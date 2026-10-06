import type { WorldState } from "./simulation";

export const SIMULATION_TICK_MS = 430;

export function snapshotWorld(world: WorldState): WorldState {
  return structuredClone(world);
}

function lerp(from: number, to: number, amount: number) {
  return from + (to - from) * amount;
}

function lerpAngle(from: number, to: number, amount: number) {
  const delta = ((to - from + Math.PI * 3) % (Math.PI * 2)) - Math.PI;
  return from + delta * amount;
}

export function smoothProgress(value: number) {
  const clamped = Math.min(1, Math.max(0, value));
  return clamped * clamped * (3 - 2 * clamped);
}

export function interpolateWorld(previous: WorldState, current: WorldState, progress: number): WorldState {
  const amount = smoothProgress(progress);
  const previousAgents = new Map(previous.agents.map((agent) => [agent.id, agent]));
  const previousResources = new Map(previous.resources.map((resource) => [resource.id, resource]));
  return {
    ...current,
    observer: {
      x: lerp(previous.observer.x, current.observer.x, amount),
      y: lerp(previous.observer.y, current.observer.y, amount),
    },
    agents: current.agents.map((agent) => {
      const before = previousAgents.get(agent.id) ?? agent;
      return {
        ...agent,
        x: lerp(before.x, agent.x, amount),
        y: lerp(before.y, agent.y, amount),
        angle: lerpAngle(before.angle, agent.angle, amount),
      };
    }),
    resources: current.resources.map((resource) => {
      const before = previousResources.get(resource.id) ?? resource;
      return { ...resource, vitality: lerp(before.vitality, resource.vitality, amount) };
    }),
  };
}
