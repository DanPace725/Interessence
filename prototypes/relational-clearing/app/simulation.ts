export const WORLD_WIDTH = 960;
export const WORLD_HEIGHT = 620;
export const MAX_BEATS = 144;
export const OBSERVATION_RADIUS = 138;

export type Species = "brambleback" | "wickwing" | "mirehorn";
export type AgentAction = "forage" | "rest" | "seek" | "flee" | "explore";
export type Intervention = "attend" | "nourish" | "ward";
export type SignalOverlay = "none" | "resource" | "distress" | "bond";

export interface Point {
  x: number;
  y: number;
}

export interface MemoryNote {
  beat: number;
  kind: Intervention | "encounter" | "witnessed";
  text: string;
}

export interface CausalEvent {
  id: string;
  beat: number;
  kind: "intervention" | "social-ripple" | "resource-shift" | "hazard-contact";
  actor?: string;
  target?: string;
  parentId?: string;
  summary: string;
  effect: string;
}

export interface Agent {
  id: string;
  name: string;
  species: Species;
  epithet: string;
  description: string;
  color: string;
  accent: string;
  x: number;
  y: number;
  angle: number;
  energy: number;
  stress: number;
  trustObserver: number;
  fearObserver: number;
  curiosity: number;
  sociability: number;
  pace: number;
  sense: number;
  action: AgentAction;
  target: Point;
  actionTicks: number;
  lastReasons: string[];
  memories: MemoryNote[];
  attended: boolean;
  wardedTicks: number;
  wardHazardId: string | null;
  hazardContacts: string[];
}

export interface ResourceNode {
  id: string;
  kind: "dewbell" | "starcap" | "reedfruit";
  x: number;
  y: number;
  vitality: number;
  resilience: number;
  recovered: number;
  consumed: number;
}

export interface Hazard {
  id: string;
  kind: "spore-knot" | "thorn-murmur";
  x: number;
  y: number;
  radius: number;
  strength: number;
}

export interface Decoration {
  kind: "fern" | "grass" | "stone" | "sapling";
  x: number;
  y: number;
  scale: number;
  rotation: number;
  variant: number;
}

export interface FieldEvent {
  beat: number;
  tone: "quiet" | "warm" | "warning";
  text: string;
}

export interface WorldState {
  seed: number;
  rngState: number;
  beat: number;
  running: boolean;
  complete: boolean;
  focus: number;
  observer: Point;
  observerTarget: Point;
  agents: Agent[];
  resources: ResourceNode[];
  hazards: Hazard[];
  decorations: Decoration[];
  bonds: Record<string, number>;
  events: FieldEvent[];
  causalEvents: CausalEvent[];
  hazardExposureBeats: number;
  nextCausalId: number;
}

const speciesNames: Record<Species, string> = {
  brambleback: "Brambleback",
  wickwing: "Wickwing",
  mirehorn: "Mirehorn",
};

export function speciesLabel(species: Species) {
  return speciesNames[species];
}

function hashSeed(seed: number) {
  let value = seed | 0;
  value = Math.imul(value ^ (value >>> 16), 0x21f0aaad);
  value = Math.imul(value ^ (value >>> 15), 0x735a2d97);
  return (value ^ (value >>> 15)) >>> 0;
}

function random(world: WorldState) {
  let t = (world.rngState += 0x6d2b79f5);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

function randomFrom(seed: number, index: number) {
  let t = hashSeed(seed + index * 7919);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

function clamp(value: number, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value));
}

export function distance(a: Point, b: Point) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function bondKey(a: string, b: string) {
  return [a, b].sort().join("::");
}

export function getBond(world: WorldState, a: string, b: string) {
  return world.bonds[bondKey(a, b)] ?? 0;
}

function changeBond(world: WorldState, a: string, b: string, delta: number) {
  const key = bondKey(a, b);
  world.bonds[key] = clamp((world.bonds[key] ?? 0) + delta, -1, 1);
}

function makeAgent(agent: Omit<Agent, "action" | "target" | "actionTicks" | "lastReasons" | "memories" | "attended" | "wardedTicks" | "wardHazardId" | "hazardContacts">): Agent {
  return {
    ...agent,
    action: "explore",
    target: { x: agent.x, y: agent.y },
    actionTicks: 0,
    lastReasons: ["new surroundings"],
    memories: [],
    attended: false,
    wardedTicks: 0,
    wardHazardId: null,
    hazardContacts: [],
  };
}

export function createWorld(seed = 7319): WorldState {
  const world: WorldState = {
    seed,
    rngState: hashSeed(seed),
    beat: 0,
    running: false,
    complete: false,
    focus: 12,
    observer: { x: 480, y: 535 },
    observerTarget: { x: 480, y: 535 },
    agents: [],
    resources: [
      { id: "dew-west", kind: "dewbell", x: 164, y: 214, vitality: 0.82, resilience: 0.74, recovered: 0, consumed: 0 },
      { id: "caps-north", kind: "starcap", x: 468, y: 122, vitality: 0.72, resilience: 0.48, recovered: 0, consumed: 0 },
      { id: "reeds-east", kind: "reedfruit", x: 785, y: 318, vitality: 0.88, resilience: 0.62, recovered: 0, consumed: 0 },
      { id: "dew-south", kind: "dewbell", x: 359, y: 474, vitality: 0.58, resilience: 0.86, recovered: 0, consumed: 0 },
    ],
    hazards: [
      { id: "spore-one", kind: "spore-knot", x: 614, y: 356, radius: 62, strength: 0.75 },
      { id: "thorn-one", kind: "thorn-murmur", x: 276, y: 337, radius: 48, strength: 0.58 },
    ],
    decorations: [],
    bonds: {},
    events: [{ beat: 0, tone: "quiet", text: "The clearing settles around your lantern." }],
    causalEvents: [],
    hazardExposureBeats: 0,
    nextCausalId: 1,
  };

  world.agents = [
    makeAgent({
      id: "bracken",
      name: "Bracken",
      species: "brambleback",
      epithet: "patient seed-carrier",
      description: "A low, leaf-armored grazer. Bracken pauses often, listening through the plates along their back.",
      color: "#78915d",
      accent: "#e6b566",
      x: 205,
      y: 284,
      angle: -0.2,
      energy: 0.68,
      stress: 0.16,
      trustObserver: 0.02,
      fearObserver: 0.05,
      curiosity: 0.42,
      sociability: 0.66,
      pace: 8.2,
      sense: 190,
    }),
    makeAgent({
      id: "tilt",
      name: "Tilt",
      species: "brambleback",
      epithet: "restless path-maker",
      description: "Younger than Bracken, with copper-tipped leaves and a habit of testing every boundary.",
      color: "#8b7250",
      accent: "#d97848",
      x: 318,
      y: 436,
      angle: -1.1,
      energy: 0.51,
      stress: 0.24,
      trustObserver: -0.02,
      fearObserver: 0.09,
      curiosity: 0.82,
      sociability: 0.38,
      pace: 10.5,
      sense: 168,
    }),
    makeAgent({
      id: "luma",
      name: "Luma",
      species: "wickwing",
      epithet: "lantern-tailed scout",
      description: "A dusk flier whose chest-light brightens near familiar company and gutters under strain.",
      color: "#697fb0",
      accent: "#ffd986",
      x: 675,
      y: 170,
      angle: 2.3,
      energy: 0.74,
      stress: 0.12,
      trustObserver: 0.04,
      fearObserver: 0.04,
      curiosity: 0.74,
      sociability: 0.84,
      pace: 13.5,
      sense: 226,
    }),
    makeAgent({
      id: "vesper",
      name: "Vesper",
      species: "wickwing",
      epithet: "watchful signal-keeper",
      description: "A broad-winged elder. Vesper follows distress quickly, but remembers sudden movement for a long time.",
      color: "#7e647f",
      accent: "#b9efdc",
      x: 755,
      y: 432,
      angle: -2.8,
      energy: 0.61,
      stress: 0.2,
      trustObserver: 0,
      fearObserver: 0.1,
      curiosity: 0.34,
      sociability: 0.92,
      pace: 12.2,
      sense: 242,
    }),
    makeAgent({
      id: "silt",
      name: "Silt",
      species: "mirehorn",
      epithet: "soft-footed water finder",
      description: "A shy amphibious forager. The spiral horns collect dew and tremble near damaged ground.",
      color: "#4d8f87",
      accent: "#e2c184",
      x: 511,
      y: 416,
      angle: -1.7,
      energy: 0.57,
      stress: 0.31,
      trustObserver: -0.03,
      fearObserver: 0.16,
      curiosity: 0.51,
      sociability: 0.56,
      pace: 8.8,
      sense: 205,
    }),
  ];

  changeBond(world, "bracken", "tilt", 0.32);
  changeBond(world, "luma", "vesper", 0.47);
  changeBond(world, "luma", "silt", 0.12);
  changeBond(world, "bracken", "silt", 0.08);

  const decorationKinds: Decoration["kind"][] = ["fern", "grass", "grass", "stone", "sapling"];
  for (let index = 0; index < 74; index += 1) {
    const x = 34 + randomFrom(seed, index * 5) * (WORLD_WIDTH - 68);
    const y = 62 + randomFrom(seed, index * 5 + 1) * (WORLD_HEIGHT - 108);
    const tooClose = world.resources.some((node) => distance({ x, y }, node) < 38);
    if (tooClose) continue;
    world.decorations.push({
      kind: decorationKinds[Math.floor(randomFrom(seed, index * 5 + 2) * decorationKinds.length)],
      x,
      y,
      scale: 0.65 + randomFrom(seed, index * 5 + 3) * 0.8,
      rotation: randomFrom(seed, index * 5 + 4) * Math.PI * 2,
      variant: index % 4,
    });
  }

  return world;
}

export function signalAt(world: WorldState, point: Point, channel: Exclude<SignalOverlay, "none">) {
  if (channel === "resource") {
    return clamp(world.resources.reduce((sum, node) => sum + node.vitality * Math.exp(-distance(point, node) / 150), 0) / 1.5);
  }
  if (channel === "distress") {
    const agentSignal = world.agents.reduce((sum, agent) => sum + agent.stress * Math.exp(-distance(point, agent) / 122), 0);
    const hazardSignal = world.hazards.reduce((sum, hazard) => sum + hazard.strength * Math.exp(-distance(point, hazard) / 105), 0);
    return clamp((agentSignal + hazardSignal) / 1.8);
  }
  let total = 0;
  let count = 0;
  for (let a = 0; a < world.agents.length; a += 1) {
    for (let b = a + 1; b < world.agents.length; b += 1) {
      const bond = Math.max(0, getBond(world, world.agents[a].id, world.agents[b].id));
      const midpoint = {
        x: (world.agents[a].x + world.agents[b].x) / 2,
        y: (world.agents[a].y + world.agents[b].y) / 2,
      };
      total += bond * Math.exp(-distance(point, midpoint) / 148);
      count += 1;
    }
  }
  return clamp(total / Math.max(0.75, count * 0.18));
}

function nearestResource(agent: Agent, world: WorldState) {
  return world.resources
    .filter((node) => node.vitality > 0.08)
    .map((node) => ({ node, dist: distance(agent, node) }))
    .sort((a, b) => a.dist - b.dist)[0];
}

function nearestCompanion(agent: Agent, world: WorldState) {
  return world.agents
    .filter((other) => other.id !== agent.id)
    .map((other) => ({ other, dist: distance(agent, other), bond: getBond(world, agent.id, other.id) }))
    .sort((a, b) => (b.bond + 0.2) / (b.dist + 40) - (a.bond + 0.2) / (a.dist + 40))[0];
}

function nearestHazard(agent: Agent, world: WorldState) {
  return world.hazards
    .map((hazard) => ({ hazard, dist: distance(agent, hazard) }))
    .sort((a, b) => a.dist - b.dist)[0];
}

function chooseAction(agent: Agent, world: WorldState) {
  const resource = nearestResource(agent, world);
  const companion = nearestCompanion(agent, world);
  const observerDistance = distance(agent, world.observer);
  const resourceField = signalAt(world, agent, "resource");
  const distressField = signalAt(world, agent, "distress");
  const bondField = signalAt(world, agent, "bond");
  const candidates: Array<{ action: AgentAction; score: number; reasons: string[] }> = [
    {
      action: "forage",
      score: (1 - agent.energy) * 1.35 + resourceField * 0.5 + random(world) * 0.09,
      reasons: [agent.energy < 0.5 ? "hunger is rising" : "energy is adequate", resource ? "resource trace detected" : "no resource in reach"],
    },
    {
      action: "seek",
      score: agent.sociability * (1 - agent.stress) * 0.46 + bondField * 0.56 + random(world) * 0.09,
      reasons: [bondField > 0.25 ? "a familiar bond is nearby" : "the bond field is faint", agent.sociability > 0.7 ? "strong social tendency" : "prefers some distance"],
    },
    {
      action: "flee",
      score: agent.stress * 0.9 + distressField * 0.58 + (observerDistance < 170 ? agent.fearObserver * 1.2 : 0) + (agent.wardedTicks > 0 ? 1.4 : 0) + random(world) * 0.06,
      reasons: [distressField > 0.34 ? "distress field is elevated" : "surroundings feel quiet", observerDistance < 170 && agent.fearObserver > 0.12 ? "remembers your pressure" : "no immediate threat"],
    },
    {
      action: "rest",
      score: (1 - agent.energy) * 0.58 + agent.stress * 0.22 + random(world) * 0.06,
      reasons: [agent.energy < 0.4 ? "energy is depleted" : "energy permits movement", agent.stress > 0.5 ? "needs stillness" : "not overwhelmed"],
    },
    {
      action: "explore",
      score: agent.curiosity * (1 - agent.stress) * 0.48 + random(world) * 0.16,
      reasons: [agent.curiosity > 0.65 ? "curiosity is strong" : "curiosity is cautious", agent.stress < 0.3 ? "enough calm to wander" : "strain limits exploration"],
    },
  ];

  candidates.sort((a, b) => b.score - a.score);
  const selected = candidates[0];
  agent.action = selected.action;
  agent.actionTicks = 6 + Math.floor(random(world) * 7);
  agent.lastReasons = [...selected.reasons, `next tendency was ${candidates[1].action}`];

  if (selected.action === "forage" && resource) {
    agent.target = { x: resource.node.x, y: resource.node.y };
  } else if (selected.action === "seek" && companion) {
    agent.target = { x: companion.other.x, y: companion.other.y };
  } else if (selected.action === "flee") {
    const wardedHazard = agent.wardHazardId ? world.hazards.find((hazard) => hazard.id === agent.wardHazardId) : null;
    const pressure = wardedHazard ?? world.observer;
    let dx = agent.x - pressure.x;
    let dy = agent.y - pressure.y;
    if (Math.hypot(dx, dy) < 0.001) {
      dx = agent.id.length % 2 ? 1 : -1;
      dy = 0;
    }
    const length = Math.hypot(dx, dy) || 1;
    dx /= length;
    dy /= length;
    agent.target = { x: clamp(agent.x + dx * 210, 42, WORLD_WIDTH - 42), y: clamp(agent.y + dy * 210, 68, WORLD_HEIGHT - 42) };
  } else if (selected.action === "explore") {
    agent.target = { x: 70 + random(world) * (WORLD_WIDTH - 140), y: 92 + random(world) * (WORLD_HEIGHT - 160) };
  } else {
    agent.target = { x: agent.x, y: agent.y };
  }
}

function moveToward(agent: Agent, target: Point, speed: number) {
  const dx = target.x - agent.x;
  const dy = target.y - agent.y;
  const length = Math.hypot(dx, dy);
  if (length < 1) return;
  const step = Math.min(speed, length);
  agent.angle = Math.atan2(dy, dx);
  agent.x = clamp(agent.x + (dx / length) * step, 32, WORLD_WIDTH - 32);
  agent.y = clamp(agent.y + (dy / length) * step, 74, WORLD_HEIGHT - 30);
}

function appendEvent(world: WorldState, event: Omit<FieldEvent, "beat">) {
  world.events.unshift({ beat: world.beat, ...event });
  world.events = world.events.slice(0, 16);
}

function recordCause(world: WorldState, event: Omit<CausalEvent, "id" | "beat">) {
  const recorded: CausalEvent = { id: `cause-${world.nextCausalId}`, beat: world.beat, ...event };
  world.nextCausalId += 1;
  world.causalEvents.push(recorded);
  return recorded;
}

export function moveObserver(world: WorldState, target: Point) {
  world.observerTarget = {
    x: clamp(target.x, 24, WORLD_WIDTH - 24),
    y: clamp(target.y, 72, WORLD_HEIGHT - 24),
  };
}

export function nudgeObserver(world: WorldState, dx: number, dy: number) {
  moveObserver(world, { x: world.observer.x + dx, y: world.observer.y + dy });
  world.observer = { ...world.observerTarget };
}

export function canReach(world: WorldState, agent: Agent) {
  return distance(world.observer, agent) <= OBSERVATION_RADIUS;
}

export function applyIntervention(world: WorldState, agentId: string, intervention: Intervention) {
  const agent = world.agents.find((candidate) => candidate.id === agentId);
  if (!agent) return { ok: false, message: "That creature has moved beyond the clearing." };
  if (!canReach(world, agent)) return { ok: false, message: "Move your lantern closer first." };
  const costs: Record<Intervention, number> = { attend: 1, nourish: 2, ward: 1 };
  const cost = costs[intervention];
  if (world.focus < cost) return { ok: false, message: "Your attention is spent for this visit." };
  world.focus -= cost;

  const interventionCause = recordCause(world, {
    kind: "intervention",
    actor: "observer",
    target: agent.id,
    summary: `${intervention} directed toward ${agent.name}`,
    effect: `Spent ${cost} focus and changed ${agent.name}'s immediate state.`,
  });
  const onlookers = world.agents.filter((other) => other.id !== agent.id && distance(other, agent) < 146);

  if (intervention === "attend") {
    agent.attended = true;
    agent.trustObserver = clamp(agent.trustObserver + 0.09, -1, 1);
    agent.fearObserver = clamp(agent.fearObserver - 0.04, -1, 1);
    agent.stress = clamp(agent.stress - 0.1);
    agent.memories.unshift({ beat: world.beat, kind: intervention, text: "You stayed nearby without demanding movement." });
    onlookers.forEach((other) => {
      const bond = Math.max(0, getBond(world, agent.id, other.id));
      if (bond <= 0.04 && other.sociability < 0.7) return;
      other.stress = clamp(other.stress - (0.018 + bond * 0.026));
      other.trustObserver = clamp(other.trustObserver + 0.018 + bond * 0.02, -1, 1);
      other.memories.unshift({ beat: world.beat, kind: "witnessed", text: `They watched your quiet attention settle ${agent.name}.` });
      other.memories = other.memories.slice(0, 6);
      recordCause(world, {
        kind: "social-ripple", actor: agent.id, target: other.id, parentId: interventionCause.id,
        summary: `${other.name} witnessed ${agent.name} settle`, effect: "Nearby strain eased and observer familiarity increased.",
      });
    });
    appendEvent(world, { tone: "warm", text: `${agent.name} lets your lantern remain close.` });
  } else if (intervention === "nourish") {
    agent.attended = true;
    agent.energy = clamp(agent.energy + 0.34);
    agent.trustObserver = clamp(agent.trustObserver + 0.13, -1, 1);
    agent.stress = clamp(agent.stress - 0.045);
    agent.actionTicks = 0;
    agent.memories.unshift({ beat: world.beat, kind: intervention, text: "You offered stored dew without approaching further." });
    onlookers.forEach((other) => {
      const receptive = other.sociability > 0.65;
      changeBond(world, agent.id, other.id, receptive ? 0.035 : -0.018);
      other.trustObserver = clamp(other.trustObserver + (receptive ? 0.028 : -0.012), -1, 1);
      other.memories.unshift({ beat: world.beat, kind: "witnessed", text: `They watched you bring stored dew to ${agent.name}.` });
      other.memories = other.memories.slice(0, 6);
      recordCause(world, {
        kind: "social-ripple", actor: agent.id, target: other.id, parentId: interventionCause.id,
        summary: `${other.name} witnessed ${agent.name} being nourished`,
        effect: receptive ? "Their bond and observer familiarity strengthened." : "Their bond tightened with caution.",
      });
    });
    appendEvent(world, { tone: "warm", text: `${agent.name} takes the stored dew${onlookers.length ? " while others watch" : ""}.` });
  } else {
    const nearbyHazard = nearestHazard(agent, world);
    agent.fearObserver = clamp(agent.fearObserver + 0.22, -1, 1);
    agent.trustObserver = clamp(agent.trustObserver - 0.11, -1, 1);
    agent.stress = clamp(agent.stress + 0.16);
    agent.wardedTicks = 24;
    agent.wardHazardId = nearbyHazard?.dist < 175 ? nearbyHazard.hazard.id : null;
    agent.actionTicks = 0;
    agent.memories.unshift({ beat: world.beat, kind: intervention, text: "Your lantern flared and pressed them away from this ground." });
    onlookers.forEach((other) => {
      other.fearObserver = clamp(other.fearObserver + 0.045, -1, 1);
      other.memories.unshift({ beat: world.beat, kind: "witnessed", text: `They watched your light press ${agent.name} away.` });
      other.memories = other.memories.slice(0, 6);
      recordCause(world, {
        kind: "social-ripple", actor: agent.id, target: other.id, parentId: interventionCause.id,
        summary: `${other.name} witnessed ${agent.name} being warded`, effect: "Observer fear increased beyond the direct target.",
      });
    });
    appendEvent(world, { tone: "warning", text: `${agent.name} recoils from the warding flare.` });
  }
  agent.memories = agent.memories.slice(0, 6);
  return { ok: true, message: world.events[0].text };
}

export function stepWorld(world: WorldState) {
  if (world.complete) return;
  world.beat += 1;

  const observerDistance = distance(world.observer, world.observerTarget);
  if (observerDistance > 1) {
    const dx = world.observerTarget.x - world.observer.x;
    const dy = world.observerTarget.y - world.observer.y;
    const step = Math.min(34, observerDistance);
    world.observer.x += (dx / observerDistance) * step;
    world.observer.y += (dy / observerDistance) * step;
  }

  world.resources.forEach((node) => {
    const pressure = world.agents.filter((agent) => distance(agent, node) < 58).length;
    const recovered = (0.001 + node.resilience * 0.0032) * Math.max(0.1, 1 - pressure * 0.34);
    const before = node.vitality;
    node.vitality = clamp(node.vitality + recovered);
    node.recovered += node.vitality - before;
    if (before < 0.2 && node.vitality >= 0.2) {
      recordCause(world, {
        kind: "resource-shift", target: node.id, summary: `${node.id} returned to viable growth`,
        effect: pressure ? `Recovery continued under pressure from ${pressure} nearby creature${pressure === 1 ? "" : "s"}.` : "An undisturbed interval allowed recovery.",
      });
    }
  });

  world.agents.forEach((agent) => {
    agent.energy = clamp(agent.energy - 0.0045);
    agent.stress = clamp(agent.stress - 0.0035);
    agent.fearObserver = clamp(agent.fearObserver - 0.0008, -1, 1);
    agent.trustObserver = clamp(agent.trustObserver - 0.00025, -1, 1);
    agent.wardedTicks = Math.max(0, agent.wardedTicks - 1);
    if (agent.wardedTicks === 0) agent.wardHazardId = null;

    world.hazards.forEach((hazard) => {
      const proximity = 1 - distance(agent, hazard) / hazard.radius;
      if (proximity > 0) {
        world.hazardExposureBeats += 1;
        agent.stress = clamp(agent.stress + proximity * hazard.strength * 0.027);
        agent.energy = clamp(agent.energy - proximity * 0.008);
        if (!agent.hazardContacts.includes(hazard.id)) {
          agent.hazardContacts.push(hazard.id);
          recordCause(world, {
            kind: "hazard-contact", actor: agent.id, target: hazard.id,
            summary: `${agent.name} entered ${hazard.kind.replace("-", " ")}`,
            effect: "Strain rose and energy fell while contact continued.",
          });
        }
      }
    });

    agent.actionTicks -= 1;
    if (agent.actionTicks <= 0) chooseAction(agent, world);

    if (agent.action !== "rest") {
      const actionSpeed = agent.action === "flee" ? 1.36 : agent.action === "seek" ? 0.9 : 1;
      moveToward(agent, agent.target, agent.pace * actionSpeed);
      agent.energy = clamp(agent.energy - agent.pace * 0.00018);
    } else {
      agent.energy = clamp(agent.energy + 0.0065);
    }

    const resource = nearestResource(agent, world);
    if (agent.action === "forage" && resource && resource.dist < 27 && resource.node.vitality > 0.04) {
      const before = resource.node.vitality;
      const taken = Math.min(0.034, resource.node.vitality);
      resource.node.vitality -= taken;
      resource.node.consumed += taken;
      agent.energy = clamp(agent.energy + taken * 1.7);
      agent.stress = clamp(agent.stress - 0.008);
      if (before >= 0.2 && resource.node.vitality < 0.2) {
        recordCause(world, {
          kind: "resource-shift", actor: agent.id, target: resource.node.id,
          summary: `${agent.name}'s foraging depleted ${resource.node.id}`,
          effect: "The site's resource signal weakened below the viable threshold.",
        });
      }
    }
  });

  for (let a = 0; a < world.agents.length; a += 1) {
    for (let b = a + 1; b < world.agents.length; b += 1) {
      const first = world.agents[a];
      const second = world.agents[b];
      const separation = distance(first, second);
      if (separation < 72) {
        const calm = 1 - (first.stress + second.stress) / 2;
        changeBond(world, first.id, second.id, calm > 0.55 ? 0.0025 : -0.0012);
        first.stress = clamp(first.stress - Math.max(0, getBond(world, first.id, second.id)) * 0.0016);
        second.stress = clamp(second.stress - Math.max(0, getBond(world, first.id, second.id)) * 0.0016);
      }
      if (separation < 44 && first.action === "forage" && second.action === "forage") {
        changeBond(world, first.id, second.id, -0.0018);
      }
    }
  }

  if (world.beat === 36) appendEvent(world, { tone: "quiet", text: "Blue dusk reaches the eastern reeds." });
  if (world.beat === 76) appendEvent(world, { tone: "quiet", text: "The starcaps open. Their resource trace grows brighter." });
  if (world.beat === 112) appendEvent(world, { tone: "quiet", text: "Night gathers; the clearing begins to close." });
  if (world.beat >= MAX_BEATS) {
    world.complete = true;
    world.running = false;
    appendEvent(world, { tone: "quiet", text: "The field visit ends. Its relationships do not." });
  }
}

export function actionLabel(action: AgentAction) {
  return ({ forage: "following nourishment", rest: "settling into stillness", seek: "seeking familiar company", flee: "moving away from pressure", explore: "testing the clearing" } as const)[action];
}

export function moodLabel(agent: Agent) {
  if (agent.stress > 0.68) return "visibly alarmed";
  if (agent.stress > 0.42) return "watchful and strained";
  if (agent.energy < 0.3) return "tired and searching";
  if (agent.energy > 0.75 && agent.stress < 0.24) return "bright and well-rested";
  return "quietly attentive";
}

export function relationLabel(agent: Agent) {
  if (!agent.attended && agent.memories.length === 0) return "You have not read this relationship closely.";
  if (agent.fearObserver > 0.45) return "Your light is remembered as pressure.";
  if (agent.trustObserver > 0.42) return "They make room for your presence.";
  if (agent.trustObserver > 0.14) return "Your presence is becoming familiar.";
  if (agent.trustObserver < -0.12) return "They keep your lantern at the edge of attention.";
  return "The relationship remains unsettled.";
}

export function summarizeWorld(world: WorldState) {
  const mostTrusting = [...world.agents].sort((a, b) => b.trustObserver - a.trustObserver)[0];
  const mostWary = [...world.agents].sort((a, b) => b.fearObserver - a.fearObserver)[0];
  let strongest: { a: Agent; b: Agent; value: number } | null = null;
  for (let a = 0; a < world.agents.length; a += 1) {
    for (let b = a + 1; b < world.agents.length; b += 1) {
      const value = getBond(world, world.agents[a].id, world.agents[b].id);
      if (!strongest || value > strongest.value) strongest = { a: world.agents[a], b: world.agents[b], value };
    }
  }
  const depleted = world.resources.filter((resource) => resource.vitality < 0.2).length;
  return {
    mostTrusting,
    mostWary,
    strongest,
    depleted,
    attentionSpent: 12 - world.focus,
    resourceVitality: world.resources.reduce((sum, resource) => sum + resource.vitality, 0) / world.resources.length,
    recoveredVitality: world.resources.reduce((sum, resource) => sum + resource.recovered, 0),
    consumedVitality: world.resources.reduce((sum, resource) => sum + resource.consumed, 0),
    averageEnergy: world.agents.reduce((sum, agent) => sum + agent.energy, 0) / world.agents.length,
    witnessedMemories: world.agents.reduce((sum, agent) => sum + agent.memories.filter((memory) => memory.kind === "witnessed").length, 0),
    hazardExposureBeats: world.hazardExposureBeats,
  };
}
