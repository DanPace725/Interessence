import assert from "node:assert/strict";
import test from "node:test";
import { createWorld } from "../app/simulation.ts";
import { interpolateWorld, snapshotWorld } from "../app/visual-interpolation.ts";

test("visual interpolation smooths positions without changing authoritative state", () => {
  const previous = createWorld(7319);
  const current = snapshotWorld(previous);
  current.agents[0].x += 100;
  current.observer.y -= 80;
  current.resources[0].vitality -= 0.2;

  const halfway = interpolateWorld(previous, current, 0.5);
  assert.equal(halfway.agents[0].x, previous.agents[0].x + 50);
  assert.equal(halfway.observer.y, previous.observer.y - 40);
  assert.ok(Math.abs(halfway.resources[0].vitality - (previous.resources[0].vitality - 0.1)) < 1e-9);
  assert.equal(previous.agents[0].x, 205);
  assert.equal(current.agents[0].x, 305);
});

test("visual interpolation clamps cleanly to both beat states", () => {
  const previous = createWorld(7319);
  const current = snapshotWorld(previous);
  current.agents[0].x += 42;
  assert.equal(interpolateWorld(previous, current, -1).agents[0].x, previous.agents[0].x);
  assert.equal(interpolateWorld(previous, current, 2).agents[0].x, current.agents[0].x);
});
