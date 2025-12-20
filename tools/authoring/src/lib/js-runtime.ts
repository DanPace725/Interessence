import { compilePacks } from './runtime-loader';

type Value = number | boolean | string;

interface Entity {
  id: string;
  kind: string;
  position: { x: number; y: number; z: number };
  state: Record<string, Value>;
}

interface Relation {
  primitive: string;
  source: string;
  target: string;
  weight: number;
}

interface RuntimeState {
  entities: Entity[];
  relations: Relation[];
  config: any;
  heuristics: any;
  signal: any;
}

function getNumber(state: Record<string, Value>, key: string, fallback = 0): number {
  const v = state[key];
  if (typeof v === 'number') return v;
  if (typeof v === 'boolean') return v ? 1 : 0;
  return fallback;
}

function getBool(state: Record<string, Value>, key: string, fallback = false): boolean {
  const v = state[key];
  if (typeof v === 'boolean') return v;
  if (typeof v === 'number') return v !== 0;
  return fallback;
}

function setNumber(state: Record<string, Value>, key: string, v: number) {
  state[key] = v;
}

function dist2(a: { x: number; y: number }, b: { x: number; y: number }) {
  const dx = a.x - b.x;
  const dy = a.y - b.y;
  return dx * dx + dy * dy;
}

function sampleMetric(e: Entity, metric: string): number {
  if (metric === 'visibleResources') return getNumber(e.state, 'visibleResources', 0);
  if (metric === 'nearestResourceDist2') {
    const d2 = getNumber(e.state, 'nearestResourceDist2', Number.POSITIVE_INFINITY);
    if (!isFinite(d2)) return 0;
    return 1 / (1 + d2);
  }
  return getNumber(e.state, metric, 0);
}

export function initRuntime(worldText: string, heuristicsText: string, signalText: string): RuntimeState | null {
  const res = compilePacks(worldText, heuristicsText, signalText);
  if (!res.ok || !res.bundle) return null;
  const entities: Entity[] = res.bundle.entities.map((e) => ({
    id: e.id,
    kind: e.kind,
    position: { ...e.position },
    state: { ...e.state }
  }));
  const relations: Relation[] = res.bundle.relations.map((r) => ({
    primitive: r.primitive,
    source: r.source,
    target: r.target,
    weight: r.weight
  }));
  return {
    entities,
    relations,
    config: res.bundle.config,
    heuristics: res.bundle.heuristics,
    signal: res.bundle.signal
  };
}

export function tickRuntime(rt: RuntimeState) {
  const geom = rt.config.geometry || {};
  const neighborR2 = geom.wallAvoidMargin ? geom.wallAvoidMargin * geom.wallAvoidMargin : 100 * 100;
  const resourceRadius = geom.resourceRadius ?? 10;
  const worldHalf = geom.worldHalfSize ?? 500;
  const params = rt.heuristics.parameters || {};

  // Geometry
  for (const e of rt.entities) {
    let count = 0;
    let nearestResource = Number.POSITIVE_INFINITY;
    for (const other of rt.entities) {
      if (e.id === other.id) continue;
      if (dist2(e.position, other.position) <= neighborR2) count++;
      if (other.kind === 'resource') {
        const d2 = dist2(e.position, other.position);
        if (d2 < nearestResource) nearestResource = d2;
      }
    }
    setNumber(e.state, 'neighbors', count);
    if (isFinite(nearestResource)) setNumber(e.state, 'nearestResourceDist2', nearestResource);
  }

  // Constraint: max agents
  const maxAgents = Math.max(0, Math.floor(rt.config.constraints?.maxAgents ?? rt.entities.length + 1000));
  if (rt.entities.length > maxAgents) rt.entities.length = maxAgents;

  // Epistemic: sensing resources
  const senseBase = params.aiSensoryRangeBase ?? 0;
  const senseMax = params.aiSensoryRangeMax ?? senseBase;
  const sensePerChi = params.aiSenseRangePerChi ?? 0;
  for (const e of rt.entities) {
    const chi = getNumber(e.state, 'chi', 0);
    const radius = Math.min(senseMax, senseBase + chi * sensePerChi);
    const r2 = radius * radius;
    let visible = 0;
    for (const other of rt.entities) {
      if (other.kind !== 'resource') continue;
      if (dist2(e.position, other.position) <= r2) visible++;
    }
    setNumber(e.state, 'visibleResources', visible);
  }

  // Dynamics
  const chiLeak = params.chiLeakPerSec ?? 0;
  const chiMoveCost = params.chiMoveCostPerSec ?? 0;
  const energyLeak = params.energyLeakPerSec ?? 0;
  const energyGainPerFood = params.energyGainPerFood ?? 0;
  const chiRegenRate = params.chiRegenRateFromEnergy ?? 0;
  const chiRegenThreshold = params.chiRegenThresholdEnergy ?? 0;
  const maxSpeed = params.maxSpeed ?? 0;
  const mitosisThreshold = params.mitosisThreshold ?? Number.POSITIVE_INFINITY;
  const mitosisCost = params.mitosisCost ?? 0;
  const childStartChi = params.childStartChi ?? 0;
  const mitosisCooldown = params.mitosisCooldown ?? 0;
  const spawnOffset = params.spawnOffset ?? 10;
  const inheritHeading = params.inheritHeading ?? false;
  const carryCapMult = rt.config.constraints?.carryingCapacityMultiplier ?? 1.0;
  const respectCap = !!rt.config.constraints?.respectCarryingCapacity;
  const steeringFeeds = rt.signal.steeringFeeds || [];
  const ruleBiases = rt.signal.ruleBiases || [];

  const resourceCount = rt.entities.filter((e) => e.kind === 'resource').length;

  for (const e of rt.entities) {
    let chi = getNumber(e.state, 'chi', 0);
    let energy = getNumber(e.state, 'energy', 0);

    chi -= chiLeak + chiMoveCost;
    energy -= energyLeak;

    const vis = getNumber(e.state, 'visibleResources', 0);
    if (vis > 0 && energyGainPerFood > 0) {
      energy += energyGainPerFood * Math.min(vis, 1);
    }

    if (energy > chiRegenThreshold && chiRegenRate > 0) {
      const delta = Math.min(chiRegenRate, energy - chiRegenThreshold);
      chi += delta;
      energy -= delta;
    }

    let steerBias = 0;
    for (const sf of steeringFeeds) {
      steerBias += sampleMetric(e, sf.metric) * (sf.weight ?? 0);
    }
    for (const rb of ruleBiases) {
      if (rb.rule === 'seek_resource') steerBias += rb.weight ?? 0;
      if (rb.rule === 'avoid_distress') steerBias -= rb.weight ?? 0;
    }
    setNumber(e.state, 'steeringBias', steerBias);

    if (chi < 0) chi = 0;
    if (energy < 0) energy = 0;
    setNumber(e.state, 'chi', chi);
    setNumber(e.state, 'energy', energy);
  }

  // Movement, resource consumption, reproduction
  const newEntities: Entity[] = [];
  const resourceConsumed = new Set<string>();
  for (const e of rt.entities) {
    if (maxSpeed > 0) {
      let dx = (Math.random() * 2 - 1);
      let dy = (Math.random() * 2 - 1);
      const bias = getNumber(e.state, 'steeringBias', 0);
      if (bias !== 0) {
        let dirX = 0;
        let dirY = 0;
        let best = Number.POSITIVE_INFINITY;
        for (const r of rt.entities) {
          if (r.kind !== 'resource') continue;
          const d2 = dist2(e.position, r.position);
          if (d2 < best) {
            best = d2;
            dirX = r.position.x - e.position.x;
            dirY = r.position.y - e.position.y;
          }
        }
        const len = Math.hypot(dirX, dirY);
        if (len > 1e-6) {
          dirX /= len;
          dirY /= len;
        }
        dx += dirX * bias;
        dy += dirY * bias;
      }
      const stepLen = Math.hypot(dx, dy);
      if (stepLen > 1e-6) {
        const scale = Math.min(maxSpeed, stepLen);
        dx = (dx / stepLen) * scale;
        dy = (dy / stepLen) * scale;
      }
      e.position.x = Math.min(Math.max(e.position.x + dx, -worldHalf), worldHalf);
      e.position.y = Math.min(Math.max(e.position.y + dy, -worldHalf), worldHalf);
    }

    // consume resource
    for (const res of rt.entities) {
      if (res.kind !== 'resource') continue;
      if (resourceConsumed.has(res.id)) continue;
      if (dist2(e.position, res.position) <= resourceRadius * resourceRadius) {
        let energy = getNumber(e.state, 'energy', 0);
        energy += energyGainPerFood;
        setNumber(e.state, 'energy', energy);
        resourceConsumed.add(res.id);
        break;
      }
    }

    // reproduction
    let cooldown = getNumber(e.state, 'mitosisCooldown', 0);
    if (cooldown > 0) {
      cooldown -= 1;
      setNumber(e.state, 'mitosisCooldown', cooldown);
    }
    const chi = getNumber(e.state, 'chi', 0);
    const capacity = respectCap ? resourceCount * carryCapMult : maxAgents;
    if (chi > mitosisThreshold && cooldown <= 0 && rt.entities.length + newEntities.length < maxAgents && rt.entities.length + newEntities.length < capacity) {
      const child: Entity = {
        id: e.id + '_child_' + Math.floor(Math.random() * 1e6),
        kind: e.kind,
        position: {
          x: e.position.x + (Math.random() * 2 - 1) * spawnOffset,
          y: e.position.y + (Math.random() * 2 - 1) * spawnOffset,
          z: e.position.z
        },
        state: { ...e.state }
      };
      setNumber(child.state, 'chi', childStartChi);
      setNumber(child.state, 'energy', getNumber(e.state, 'energy', 0) * 0.5);
      if (!inheritHeading) {
        delete child.state.steeringBias;
      }
      setNumber(e.state, 'chi', chi - mitosisCost);
      setNumber(e.state, 'mitosisCooldown', mitosisCooldown);
      newEntities.push(child);
    }
  }

  // remove consumed resources and dead
  rt.entities = rt.entities.filter((e) => {
    if (e.kind === 'resource' && resourceConsumed.has(e.id)) return false;
    if (getNumber(e.state, 'chi', 0) <= 0) return false;
    return true;
  });
  rt.entities.push(...newEntities);

  // GCO: dedupe relations and apply thresholds
  const seen = new Set<string>();
  const deduped: Relation[] = [];
  for (const r of rt.relations) {
    const key = `${r.primitive}:${r.source}:${r.target}`;
    if (!seen.has(key)) {
      seen.add(key);
      deduped.push(r);
    }
  }
  rt.relations = deduped;
  if (rt.signal.gcoThresholds && rt.signal.gcoThresholds.length) {
    rt.relations = rt.relations.filter((r) => {
      const target = rt.entities.find((e) => e.id === r.target);
      if (!target) return false;
      for (const th of rt.signal.gcoThresholds) {
        if (th.target === '' || th.target === r.target) {
          const val = sampleMetric(target, th.metric);
          if (val < (th.threshold ?? 0)) return false;
        }
      }
      return true;
    });
  }
}
