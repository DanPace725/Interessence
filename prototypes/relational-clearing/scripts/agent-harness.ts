import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import {
  createAgentSession,
  finalizeReplay,
  observeForAgent,
  performAgentTurn,
  runCaretakerBaseline,
  runPassiveBaseline,
  type AgentCommand,
  type AgentReplay,
  type AgentSession,
} from "../app/agent-interface.ts";
import { runMultiSeedStudy } from "../app/multi-seed-study.ts";

function flags(argv: string[]) {
  const parsed: Record<string, string> = {};
  for (let index = 0; index < argv.length; index += 1) {
    if (!argv[index].startsWith("--")) continue;
    parsed[argv[index].slice(2)] = argv[index + 1] ?? "true";
    index += 1;
  }
  return parsed;
}

async function loadSession(path: string) {
  return JSON.parse(await readFile(resolve(path), "utf8")) as AgentSession;
}

async function saveJson(path: string, value: unknown) {
  const absolute = resolve(path);
  await mkdir(dirname(absolute), { recursive: true });
  await writeFile(absolute, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

const [command, ...rest] = process.argv.slice(2);
const options = flags(rest);

if (command === "reset") {
  if (!options.state) throw new Error("reset requires --state");
  const seed = Number(options.seed ?? 7319);
  const session = createAgentSession({
    id: options.id ?? `llm-${seed}`,
    label: options.label ?? "LLM field run",
    controller: "llm",
    seed,
    goal: options.goal ?? "Observe carefully, intervene only when warranted, and keep the clearing materially viable.",
  });
  await saveJson(options.state, session);
  process.stdout.write(`${JSON.stringify(observeForAgent(session), null, 2)}\n`);
} else if (command === "observe") {
  if (!options.state) throw new Error("observe requires --state");
  process.stdout.write(`${JSON.stringify(observeForAgent(await loadSession(options.state)), null, 2)}\n`);
} else if (command === "act") {
  if (!options.state || (!options.json && !options.action)) throw new Error("act requires --state and either --json or --action");
  const session = await loadSession(options.state);
  const belief_updates = options.belief
    ? [{ subject: options["belief-subject"] ?? "world", belief: options.belief, confidence: (options.confidence ?? "low") as "low" | "medium" | "high" }]
    : undefined;
  const action = options.json
    ? JSON.parse(options.json) as AgentCommand
    : ({
        action: options.action,
        ...(options.target ? { target: options.target } : {}),
        ...(options.zone ? { target_zone: options.zone } : {}),
        public_reason: options.reason ?? "No public reason supplied.",
        ...(belief_updates ? { belief_updates } : {}),
      } as AgentCommand);
  const result = performAgentTurn(session, action);
  if (result.ok) await saveJson(options.state, session);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (!result.ok) process.exitCode = 2;
} else if (command === "finish") {
  if (!options.state || !options.out) throw new Error("finish requires --state and --out");
  const session = await loadSession(options.state);
  if (options.label) session.label = options.label;
  await saveJson(options.out, finalizeReplay(session));
  process.stdout.write(`${JSON.stringify(finalizeReplay(session).final_summary, null, 2)}\n`);
} else if (command === "baselines") {
  const outDir = options["out-dir"] ?? options.out_dir;
  if (!outDir) throw new Error("baselines requires --out-dir");
  const seed = Number(options.seed ?? 7319);
  await saveJson(`${outDir}/passive-${seed}.json`, runPassiveBaseline(seed));
  await saveJson(`${outDir}/caretaker-${seed}.json`, runCaretakerBaseline(seed));
  process.stdout.write(`Wrote passive and caretaker baselines for seed ${seed}.\n`);
} else if (command === "replay") {
  if (!options.source || !options.out) throw new Error("replay requires --source and --out");
  const source = JSON.parse(await readFile(resolve(options.source), "utf8")) as AgentReplay;
  const session = createAgentSession({
    id: options.id ?? source.id,
    label: options.label ?? `${source.label} · mechanics v0.2`,
    controller: source.controller,
    seed: source.seed,
    goal: source.goal,
  });
  for (const turn of source.turns) {
    const result = performAgentTurn(session, turn.action);
    if (!result.ok) throw new Error(`Recorded action ${turn.turn} is no longer valid: ${result.error}`);
  }
  const replay = finalizeReplay(session);
  await saveJson(options.out, replay);
  process.stdout.write(`${JSON.stringify(replay.final_summary, null, 2)}\n`);
} else if (command === "study") {
  if (!options.out) throw new Error("study requires --out");
  const seeds = options.seeds?.split(",").map(Number).filter(Number.isFinite);
  const study = runMultiSeedStudy(seeds?.length ? seeds : undefined);
  await saveJson(options.out, study);
  process.stdout.write(`${JSON.stringify(study, null, 2)}\n`);
} else {
  process.stderr.write("Usage: agent-harness.ts reset|observe|act|finish|baselines|replay|study [flags]\n");
  process.exitCode = 1;
}
