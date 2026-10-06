import assert from "node:assert/strict";
import test from "node:test";
import {
  applyIntervention,
  createWorld,
  getBond,
  stepWorld,
} from "../app/simulation.ts";

function evidenceSnapshot(seed: number, beats: number) {
  const world = createWorld(seed);
  for (let beat = 0; beat < beats; beat += 1) stepWorld(world);
  return {
    beat: world.beat,
    rngState: world.rngState,
    agents: world.agents.map((agent) => ({
      id: agent.id,
      x: agent.x,
      y: agent.y,
      energy: agent.energy,
      stress: agent.stress,
      action: agent.action,
      target: agent.target,
    })),
    resources: world.resources,
    bonds: world.bonds,
  };
}

test("the same seed produces the same unattended history", () => {
  assert.deepEqual(evidenceSnapshot(7319, 80), evidenceSnapshot(7319, 80));
  assert.notDeepEqual(evidenceSnapshot(7319, 80), evidenceSnapshot(15238, 80));
});

test("an intervention persists as relational memory without becoming a score", () => {
  const world = createWorld(7319);
  const bracken = world.agents.find((agent) => agent.id === "bracken");
  assert.ok(bracken);
  world.observer = { x: bracken.x, y: bracken.y };

  const beforeTrust = bracken.trustObserver;
  const attended = applyIntervention(world, bracken.id, "attend");
  assert.equal(attended.ok, true);
  assert.equal(world.focus, 11);
  assert.ok(bracken.trustObserver > beforeTrust);
  assert.equal(bracken.memories[0].kind, "attend");

  const warded = applyIntervention(world, bracken.id, "ward");
  assert.equal(warded.ok, true);
  assert.equal(world.focus, 10);
  assert.equal(bracken.memories[0].kind, "ward");
  assert.ok(bracken.wardedTicks > 0);
});

test("creature bonds and resources remain material simulation state", () => {
  const world = createWorld(7319);
  const initialBond = getBond(world, "bracken", "tilt");
  const initialResources = world.resources.length;
  for (let beat = 0; beat < 40; beat += 1) stepWorld(world);
  assert.equal(world.resources.length, initialResources);
  assert.equal(world.agents.length, 5);
  assert.ok(getBond(world, "bracken", "tilt") >= -1);
  assert.equal(initialBond, 0.32);
});

test("nearby creatures remember witnessed care and the causal ledger links the ripple", () => {
  const world = createWorld(7319);
  const silt = world.agents.find((agent) => agent.id === "silt");
  const luma = world.agents.find((agent) => agent.id === "luma");
  assert.ok(silt && luma);
  world.observer = { x: silt.x, y: silt.y };
  luma.x = silt.x + 30;
  luma.y = silt.y;
  const beforeTrust = luma.trustObserver;

  assert.equal(applyIntervention(world, silt.id, "attend").ok, true);
  assert.ok(luma.trustObserver > beforeTrust);
  assert.equal(luma.memories[0].kind, "witnessed");
  const intervention = world.causalEvents.find((event) => event.kind === "intervention");
  const ripple = world.causalEvents.find((event) => event.kind === "social-ripple");
  assert.ok(intervention && ripple);
  assert.equal(ripple.parentId, intervention.id);
});

test("resource recovery slows under local creature pressure", () => {
  const quiet = createWorld(7319);
  const pressured = createWorld(7319);
  const quietSite = quiet.resources[0];
  const pressuredSite = pressured.resources[0];
  quiet.agents.forEach((agent) => { agent.x = 800; agent.y = 500; agent.action = "rest"; agent.actionTicks = 99; });
  pressured.agents.forEach((agent) => { agent.x = pressuredSite.x; agent.y = pressuredSite.y; agent.action = "rest"; agent.actionTicks = 99; });
  const quietBefore = quietSite.vitality;
  const pressuredBefore = pressuredSite.vitality;
  stepWorld(quiet);
  stepWorld(pressured);
  assert.ok(quietSite.vitality - quietBefore > pressuredSite.vitality - pressuredBefore);
});

test("warding can reduce hazard exposure while increasing observer fear", () => {
  const unattended = createWorld(7319);
  const warded = createWorld(7319);
  for (const world of [unattended, warded]) {
    const silt = world.agents.find((agent) => agent.id === "silt");
    const hazard = world.hazards[0];
    assert.ok(silt);
    silt.x = hazard.x;
    silt.y = hazard.y;
    silt.action = "rest";
    silt.actionTicks = 99;
    world.observer = { x: silt.x, y: silt.y };
  }
  const wardedSilt = warded.agents.find((agent) => agent.id === "silt");
  assert.ok(wardedSilt);
  const beforeFear = wardedSilt.fearObserver;
  assert.equal(applyIntervention(warded, "silt", "ward").ok, true);
  for (let beat = 0; beat < 12; beat += 1) { stepWorld(unattended); stepWorld(warded); }
  assert.ok(warded.hazardExposureBeats < unattended.hazardExposureBeats);
  assert.ok(wardedSilt.fearObserver > beforeFear);
});
