import assert from "node:assert/strict";
import test from "node:test";
import {
  createAgentSession,
  observeForAgent,
  performAgentTurn,
  runCaretakerBaseline,
  runPassiveBaseline,
} from "../app/agent-interface.ts";
import { runMultiSeedStudy } from "../app/multi-seed-study.ts";

test("agent observations expose local cues without leaking hidden simulation values", () => {
  const session = createAgentSession({ id: "test", label: "test", controller: "llm", goal: "test", seed: 7319 });
  const observation = observeForAgent(session);
  const encoded = JSON.stringify(observation);
  assert.match(encoded, /visible_creatures/);
  assert.match(encoded, /available_actions/);
  assert.doesNotMatch(encoded, /trustObserver|fearObserver|rngState|lastReasons|sociability|energy|stress/);
  assert.equal(observation.visible_creatures[0].id, "silt");
});

test("invalid or omniscient actions are rejected without advancing the world", () => {
  const session = createAgentSession({ id: "test", label: "test", controller: "llm", goal: "test", seed: 7319 });
  const result = performAgentTurn(session, { action: "nourish", target: "luma", public_reason: "Attempt an unavailable remote action." });
  assert.equal(result.ok, false);
  assert.equal(session.world.beat, 0);
  assert.equal(session.turns.length, 0);
});

test("the same structured action trace is deterministic", () => {
  const first = createAgentSession({ id: "a", label: "a", controller: "llm", goal: "test", seed: 7319 });
  const second = createAgentSession({ id: "b", label: "b", controller: "llm", goal: "test", seed: 7319 });
  const actions = [
    { action: "observe", target: "silt", public_reason: "Gather evidence first." } as const,
    { action: "move", target_zone: "central_clearing", public_reason: "Survey the center." } as const,
    { action: "wait", public_reason: "Allow consequences to develop." } as const,
  ];
  actions.forEach((action) => { assert.equal(performAgentTurn(first, action).ok, true); assert.equal(performAgentTurn(second, action).ok, true); });
  assert.deepEqual(first.world, second.world);
});

test("baseline controllers complete equal-length visits through the public contract", () => {
  const passive = runPassiveBaseline(7319);
  const caretaker = runCaretakerBaseline(7319);
  assert.equal(passive.turns.length, 12);
  assert.equal(caretaker.turns.length, 12);
  assert.equal(passive.final_world.complete, true);
  assert.equal(caretaker.final_world.complete, true);
  assert.ok(caretaker.final_summary.interventions > passive.final_summary.interventions);
  assert.ok(caretaker.final_summary.average_observer_trust > passive.final_summary.average_observer_trust);
  assert.ok(caretaker.final_summary.witnessed_memories > passive.final_summary.witnessed_memories);
});

test("the fixed multi-seed study is deterministic and exposes policy differences", () => {
  const first = runMultiSeedStudy([7319, 15238]);
  const second = runMultiSeedStudy([7319, 15238]);
  assert.deepEqual(first, second);
  const passive = first.controllers.find((controller) => controller.id === "passive");
  const caretaker = first.controllers.find((controller) => controller.id === "caretaker");
  const deliberative = first.controllers.find((controller) => controller.id === "deliberative");
  assert.ok(passive && caretaker && deliberative);
  assert.ok(caretaker.mean.average_observer_trust > passive.mean.average_observer_trust);
  assert.ok(deliberative.mean.resource_vitality > passive.mean.resource_vitality);
  assert.ok(deliberative.mean.average_energy > passive.mean.average_energy);
});
