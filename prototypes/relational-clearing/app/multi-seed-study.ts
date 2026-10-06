import {
  runCaretakerBaseline,
  runDeliberativeBaseline,
  runPassiveBaseline,
  type AgentReplay,
} from "./agent-interface.ts";

export const STUDY_SEEDS = [7319, 15238, 29011, 41047, 88421] as const;

type NumericSummaryKey =
  | "interventions"
  | "resource_vitality"
  | "average_energy"
  | "hazard_exposure_beats"
  | "witnessed_memories"
  | "average_observer_trust"
  | "average_observer_fear"
  | "average_bond";

export interface MultiSeedControllerResult {
  id: "passive" | "caretaker" | "deliberative";
  label: string;
  runs: Array<{ seed: number; summary: AgentReplay["final_summary"] }>;
  mean: Record<NumericSummaryKey, number>;
  range: Record<NumericSummaryKey, { min: number; max: number }>;
}

export interface MultiSeedStudy {
  schema_version: "0.2.0";
  seeds: number[];
  decision_windows: 12;
  note: string;
  controllers: MultiSeedControllerResult[];
}

const numericKeys: NumericSummaryKey[] = [
  "interventions", "resource_vitality", "average_energy", "hazard_exposure_beats",
  "witnessed_memories", "average_observer_trust", "average_observer_fear", "average_bond",
];

function aggregate(id: MultiSeedControllerResult["id"], label: string, replays: AgentReplay[]): MultiSeedControllerResult {
  const runs = replays.map((replay) => ({ seed: replay.seed, summary: replay.final_summary }));
  const mean = {} as Record<NumericSummaryKey, number>;
  const range = {} as Record<NumericSummaryKey, { min: number; max: number }>;
  numericKeys.forEach((key) => {
    const values = runs.map((run) => run.summary[key]);
    mean[key] = values.reduce((sum, value) => sum + value, 0) / values.length;
    range[key] = { min: Math.min(...values), max: Math.max(...values) };
  });
  return { id, label, runs, mean, range };
}

export function runMultiSeedStudy(seeds: readonly number[] = STUDY_SEEDS): MultiSeedStudy {
  return {
    schema_version: "0.2.0",
    seeds: [...seeds],
    decision_windows: 12,
    note: "Five deterministic mechanics trials. The observation-led controller is a fixed public-cue policy, not five independent LLM conversations.",
    controllers: [
      aggregate("passive", "No action", seeds.map((seed) => runPassiveBaseline(seed))),
      aggregate("caretaker", "Reactive caretaker", seeds.map((seed) => runCaretakerBaseline(seed))),
      aggregate("deliberative", "Observation-led policy", seeds.map((seed) => runDeliberativeBaseline(seed))),
    ],
  };
}
