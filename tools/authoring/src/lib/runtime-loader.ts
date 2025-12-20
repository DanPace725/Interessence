import { validatePack } from './validation';

type Primitive = 'ONTOLOGY' | 'GEOMETRY' | 'CONSTRAINT' | 'EPISTEMIC' | 'DYNAMICS' | 'META';

export interface RuntimeEntity {
  id: string;
  kind: string;
  label?: string;
  position: { x: number; y: number; z: number };
  state: Record<string, unknown>;
  rp: {
    P1_identity: number;
    P2_dynamics: number;
    P3_geometry: number;
    P4_constraints: number;
    P5_epistemic: number;
    P6_meta: number;
  };
}

export interface RuntimeRelation {
  id?: string;
  primitive: Primitive;
  source: string;
  target: string;
  weight: number;
  payload?: unknown;
}

export interface RuntimeConfig {
  toggles?: Record<string, unknown>;
  geometry?: Record<string, unknown>;
  constraints?: Record<string, unknown>;
  ecology?: Record<string, unknown>;
  reproduction?: Record<string, unknown>;
}

export interface RuntimeHeuristics {
  parameters: Record<string, unknown>;
}

export interface RuntimeSignal {
  field?: Record<string, unknown>;
  compute?: Array<Record<string, unknown>>;
  feeds?: Record<string, unknown>;
  participation?: Record<string, unknown>;
}

export interface RuntimeBundle {
  entities: RuntimeEntity[];
  relations: RuntimeRelation[];
  config: RuntimeConfig;
  heuristics: RuntimeHeuristics;
  signal: RuntimeSignal;
}

export interface CompileResult {
  ok: boolean;
  errors: string[];
  bundle?: RuntimeBundle;
}

function parseJson(text: string) {
  try {
    return { data: JSON.parse(text), error: null as string | null };
  } catch (err) {
    return { data: null, error: (err as Error).message };
  }
}

const rpDefaults = {
  P1_identity: 0.5,
  P2_dynamics: 0.5,
  P3_geometry: 0.5,
  P4_constraints: 0.5,
  P5_epistemic: 0.5,
  P6_meta: 0.5
};

function normalizeEntities(rawEntities: any[] | undefined): RuntimeEntity[] {
  if (!Array.isArray(rawEntities)) return [];
  return rawEntities.map((e) => {
    const pos = e.position || {};
    return {
      id: String(e.id),
      kind: String(e.kind || e.type || 'entity'),
      label: e.label,
      position: {
        x: Number(pos.x) || 0,
        y: Number(pos.y) || 0,
        z: Number(pos.z) || 0
      },
      state: typeof e.state === 'object' && e.state !== null ? e.state : {},
      rp: { ...rpDefaults, ...(e.rp || {}) }
    };
  });
}

function normalizeRelations(rawRelations: any[] | undefined): RuntimeRelation[] {
  if (!Array.isArray(rawRelations)) return [];
  const primitives = new Set<Primitive>(['ONTOLOGY', 'GEOMETRY', 'CONSTRAINT', 'EPISTEMIC', 'DYNAMICS', 'META']);
  const normalized: RuntimeRelation[] = [];
  for (const r of rawRelations) {
    if (!r || !r.source || !r.target) continue;
    const prim = String(r.primitive).toUpperCase() as Primitive;
    if (!primitives.has(prim)) continue;
    normalized.push({
      id: r.id ? String(r.id) : undefined,
      primitive: prim,
      source: String(r.source),
      target: String(r.target),
      weight: typeof r.weight === 'number' ? r.weight : 1,
      payload: r.payload
    });
  }
  return normalized;
}

export function compilePacks(worldText: string, heuristicsText: string, signalText: string): CompileResult {
  const errors: string[] = [];

  const worldParsed = parseJson(worldText || '{}');
  if (worldParsed.error) errors.push(`World JSON: ${worldParsed.error}`);
  const heurParsed = parseJson(heuristicsText || '{}');
  if (heurParsed.error) errors.push(`Heuristics JSON: ${heurParsed.error}`);
  const signalParsed = parseJson(signalText || '{}');
  if (signalParsed.error) errors.push(`Signal JSON: ${signalParsed.error}`);

  if (errors.length) return { ok: false, errors };

  const worldValid = validatePack('world', worldParsed.data);
  if (!worldValid.valid) errors.push(`World schema: ${(worldValid.errors || []).map((e) => e.message).join('; ')}`);

  const heurValid = validatePack('heuristics', heurParsed.data);
  if (!heurValid.valid) errors.push(`Heuristics schema: ${(heurValid.errors || []).map((e) => e.message).join('; ')}`);

  const signalValid = validatePack('signal', signalParsed.data);
  if (!signalValid.valid) errors.push(`Signal schema: ${(signalValid.errors || []).map((e) => e.message).join('; ')}`);

  if (errors.length) return { ok: false, errors };

  const entities = normalizeEntities(worldParsed.data.entities);
  const relations = normalizeRelations(worldParsed.data.relations);
  const config: RuntimeConfig = {
    toggles: worldParsed.data.toggles,
    geometry: worldParsed.data.geometry,
    constraints: worldParsed.data.constraints,
    ecology: worldParsed.data.ecology,
    reproduction: worldParsed.data.reproduction
  };
  const heuristics: RuntimeHeuristics = {
    parameters: heurParsed.data.parameters || {}
  };
  const signal: RuntimeSignal = {
    field: signalParsed.data.field,
    compute: signalParsed.data.compute,
    feeds: signalParsed.data.feeds,
    participation: signalParsed.data.participation
  };

  return {
    ok: true,
    errors: [],
    bundle: { entities, relations, config, heuristics, signal }
  };
}
