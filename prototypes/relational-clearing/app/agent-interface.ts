import {
  MAX_BEATS,
  OBSERVATION_RADIUS,
  actionLabel,
  applyIntervention,
  canReach,
  createWorld,
  distance,
  moodLabel,
  moveObserver,
  relationLabel,
  speciesLabel,
  stepWorld,
  summarizeWorld,
  type Agent,
  type Intervention,
  type Point,
  type WorldState,
} from "./simulation.ts";

export const DECISION_BEATS = 12;
export const PERCEPTION_RADIUS = 244;

export const FIELD_ZONES = {
  western_grove: { label: "Western grove", x: 160, y: 220 },
  starcap_bank: { label: "Starcap bank", x: 468, y: 145 },
  eastern_reeds: { label: "Eastern reeds", x: 792, y: 305 },
  thorn_path: { label: "Thorn path", x: 278, y: 345 },
  central_clearing: { label: "Central clearing", x: 480, y: 320 },
  spore_hollow: { label: "Spore hollow", x: 625, y: 360 },
  southern_dew: { label: "Southern dew", x: 360, y: 485 },
  lantern_path: { label: "Lantern path", x: 480, y: 535 },
  mire_edge: { label: "Mire edge", x: 782, y: 462 },
} as const;

export type ZoneId = keyof typeof FIELD_ZONES;
export type AgentCommand =
  | { action: "move"; target_zone: ZoneId; public_reason: string; belief_updates?: BeliefUpdate[] }
  | { action: "observe"; target: string; public_reason: string; belief_updates?: BeliefUpdate[] }
  | { action: Intervention; target: string; public_reason: string; belief_updates?: BeliefUpdate[] }
  | { action: "wait"; public_reason: string; belief_updates?: BeliefUpdate[] };

export interface BeliefUpdate {
  subject: string;
  belief: string;
  confidence: "low" | "medium" | "high";
}

export interface VisibleCreature {
  id: string;
  name: string;
  species: string;
  distance: "within_reach" | "near" | "far";
  bearing: string;
  condition: string;
  behavior: string;
  relationship_cue: string;
  notable_cue: string;
}

export interface AgentObservation {
  turn: number;
  beat: number;
  beats_remaining: number;
  focus: number;
  phase: string;
  observer_zone: ZoneId;
  visible_creatures: VisibleCreature[];
  visible_sites: Array<{ id: string; kind: string; distance: string; condition: string }>;
  visible_hazards: Array<{ id: string; kind: string; distance: string; cue: string }>;
  recent_events: string[];
  available_actions: {
    move: ZoneId[];
    observe: string[];
    attend: string[];
    nourish: string[];
    ward: string[];
    wait: boolean;
  };
  interface_note: string;
}

export interface AgentTurn {
  turn: number;
  observation: AgentObservation;
  action: AgentCommand;
  outcome: string;
  after: AgentObservation;
  world: WorldState;
}

export interface AgentSession {
  schema_version: "0.2.0";
  id: string;
  label: string;
  controller: "passive" | "scripted" | "llm";
  goal: string;
  seed: number;
  turn: number;
  world: WorldState;
  turns: AgentTurn[];
  notes: BeliefUpdate[];
}

export interface AgentReplay {
  schema_version: "0.2.0";
  interface: "relational-clearing-agent";
  id: string;
  label: string;
  controller: AgentSession["controller"];
  goal: string;
  seed: number;
  initial_world: WorldState;
  turns: AgentTurn[];
  final_world: WorldState;
  final_summary: ReturnType<typeof replaySummary>;
}

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function phaseForBeat(beat: number) {
  if (beat < 48) return "late_afternoon";
  if (beat < 100) return "blue_dusk";
  return "first_night";
}

function nearestZone(point: Point): ZoneId {
  return (Object.entries(FIELD_ZONES) as Array<[ZoneId, (typeof FIELD_ZONES)[ZoneId]]>)
    .map(([id, zone]) => ({ id, distance: distance(point, zone) }))
    .sort((a, b) => a.distance - b.distance)[0].id;
}

function distanceBand(value: number) {
  if (value <= OBSERVATION_RADIUS) return "within_reach" as const;
  if (value <= 188) return "near" as const;
  return "far" as const;
}

function bearing(from: Point, to: Point) {
  const angle = Math.atan2(to.y - from.y, to.x - from.x);
  const names = ["east", "southeast", "south", "southwest", "west", "northwest", "north", "northeast"];
  return names[Math.round(angle / (Math.PI / 4) + 8) % 8];
}

function cueFor(agent: Agent) {
  if (agent.action === "flee") return "Movement is sharp and repeatedly oriented away from pressure.";
  if (agent.action === "seek") return "Their path keeps bending toward another creature.";
  if (agent.action === "forage") return agent.energy < 0.42 ? "Foraging is urgent and direct." : "They sample the resource trace without urgency.";
  if (agent.action === "rest") return agent.stress > 0.44 ? "Stillness looks protective rather than restful." : "Breathing and posture are gradually settling.";
  return agent.curiosity > 0.68 ? "They test unfamiliar edges with repeated returns." : "They move cautiously between familiar cover.";
}

function qualitativeResource(vitality: number) {
  if (vitality < 0.18) return "visibly depleted";
  if (vitality < 0.42) return "thinning";
  if (vitality > 0.78) return "abundant";
  return "viable";
}

function publicRelationship(agent: Agent) {
  if (!agent.memories.length) return "No direct history is legible yet.";
  return relationLabel(agent);
}

export function observeForAgent(session: AgentSession): AgentObservation {
  const { world } = session;
  const visibleAgents = world.agents
    .map((agent) => ({ agent, separation: distance(world.observer, agent) }))
    .filter((entry) => entry.separation <= PERCEPTION_RADIUS)
    .sort((a, b) => a.separation - b.separation);

  const visibleCreatures: VisibleCreature[] = visibleAgents.map(({ agent, separation }) => ({
    id: agent.id,
    name: agent.name,
    species: speciesLabel(agent.species),
    distance: distanceBand(separation),
    bearing: bearing(world.observer, agent),
    condition: moodLabel(agent),
    behavior: actionLabel(agent.action),
    relationship_cue: publicRelationship(agent),
    notable_cue: cueFor(agent),
  }));

  const sites = world.resources
    .map((site) => ({ site, separation: distance(world.observer, site) }))
    .filter((entry) => entry.separation <= PERCEPTION_RADIUS + 20)
    .sort((a, b) => a.separation - b.separation)
    .map(({ site, separation }) => ({ id: site.id, kind: site.kind, distance: distanceBand(separation), condition: qualitativeResource(site.vitality) }));

  const hazards = world.hazards
    .map((hazard) => ({ hazard, separation: distance(world.observer, hazard) }))
    .filter((entry) => entry.separation <= PERCEPTION_RADIUS)
    .sort((a, b) => a.separation - b.separation)
    .map(({ hazard, separation }) => ({
      id: hazard.id,
      kind: hazard.kind,
      distance: distanceBand(separation),
      cue: hazard.kind === "spore-knot" ? "Airborne motes make nearby bodies tense." : "The vegetation clicks and resists passage.",
    }));

  const reachable = visibleAgents.filter(({ agent }) => canReach(world, agent)).map(({ agent }) => agent.id);
  const visibleIds = visibleAgents.map(({ agent }) => agent.id);
  return {
    turn: session.turn,
    beat: world.beat,
    beats_remaining: Math.max(0, MAX_BEATS - world.beat),
    focus: world.focus,
    phase: phaseForBeat(world.beat),
    observer_zone: nearestZone(world.observer),
    visible_creatures: visibleCreatures,
    visible_sites: sites,
    visible_hazards: hazards,
    recent_events: world.events.filter((event) => event.beat >= Math.max(0, world.beat - DECISION_BEATS)).slice(0, 5).map((event) => event.text),
    available_actions: {
      move: Object.keys(FIELD_ZONES) as ZoneId[],
      observe: visibleIds,
      attend: world.focus >= 1 ? reachable : [],
      nourish: world.focus >= 2 ? reachable : [],
      ward: world.focus >= 1 ? reachable : [],
      wait: true,
    },
    interface_note: "Descriptions contain only locally observable cues. Hidden fields, exact relationships, and action scores are withheld.",
  };
}

function validateAction(observation: AgentObservation, command: AgentCommand) {
  if (!command.public_reason?.trim()) return "A concise public_reason is required.";
  if (command.action === "move" && !observation.available_actions.move.includes(command.target_zone)) return `Unknown target_zone: ${command.target_zone}`;
  if (command.action === "observe" && !observation.available_actions.observe.includes(command.target)) return `${command.target} is not currently observable.`;
  if (command.action === "attend" && !observation.available_actions.attend.includes(command.target)) return `${command.target} is outside attending range.`;
  if (command.action === "nourish" && !observation.available_actions.nourish.includes(command.target)) return `${command.target} cannot currently be nourished.`;
  if (command.action === "ward" && !observation.available_actions.ward.includes(command.target)) return `${command.target} is outside warding range.`;
  return null;
}

export function createAgentSession(options: { seed?: number; id: string; label: string; controller: AgentSession["controller"]; goal: string }): AgentSession {
  return {
    schema_version: "0.2.0",
    id: options.id,
    label: options.label,
    controller: options.controller,
    goal: options.goal,
    seed: options.seed ?? 7319,
    turn: 0,
    world: createWorld(options.seed ?? 7319),
    turns: [],
    notes: [],
  };
}

export function performAgentTurn(session: AgentSession, command: AgentCommand) {
  if (session.world.complete) return { ok: false, error: "The field visit is already complete.", observation: observeForAgent(session) };
  const observation = observeForAgent(session);
  const error = validateAction(observation, command);
  if (error) return { ok: false, error, observation };

  let outcome = "You wait without directing the clearing.";
  if (command.action === "move") {
    const zone = FIELD_ZONES[command.target_zone];
    moveObserver(session.world, zone);
    outcome = `You carry the lantern toward ${zone.label}.`;
  } else if (command.action === "observe") {
    const target = session.world.agents.find((agent) => agent.id === command.target);
    outcome = target ? `You keep ${target.name} in view without intervening.` : "The subject is no longer visible.";
  } else if (command.action !== "wait") {
    const result = applyIntervention(session.world, command.target, command.action);
    if (!result.ok) return { ok: false, error: result.message, observation };
    outcome = result.message;
  }

  for (let beat = 0; beat < DECISION_BEATS && !session.world.complete; beat += 1) stepWorld(session.world);
  session.turn += 1;
  if (command.belief_updates?.length) session.notes.push(...command.belief_updates);
  const after = observeForAgent(session);
  session.turns.push({ turn: session.turn, observation, action: clone(command), outcome, after, world: clone(session.world) });
  return { ok: true, outcome, observation: after };
}

export function replaySummary(world: WorldState) {
  const base = summarizeWorld(world);
  const pairValues = Object.values(world.bonds);
  return {
    attention_spent: base.attentionSpent,
    most_trusting: base.mostTrusting.name,
    most_wary: base.mostWary.name,
    strongest_bond: base.strongest ? `${base.strongest.a.name} + ${base.strongest.b.name}` : "none",
    average_strain: world.agents.reduce((sum, agent) => sum + agent.stress, 0) / world.agents.length,
    average_observer_trust: world.agents.reduce((sum, agent) => sum + agent.trustObserver, 0) / world.agents.length,
    average_observer_fear: world.agents.reduce((sum, agent) => sum + agent.fearObserver, 0) / world.agents.length,
    average_bond: pairValues.reduce((sum, value) => sum + value, 0) / Math.max(1, pairValues.length),
    depleted_sites: base.depleted,
    interventions: world.causalEvents.filter((event) => event.kind === "intervention").length,
    average_energy: base.averageEnergy,
    resource_vitality: base.resourceVitality,
    resource_recovered: base.recoveredVitality,
    resource_consumed: base.consumedVitality,
    hazard_exposure_beats: base.hazardExposureBeats,
    witnessed_memories: base.witnessedMemories,
    causal_events: world.causalEvents.length,
  };
}

export function finalizeReplay(session: AgentSession): AgentReplay {
  return {
    schema_version: "0.2.0",
    interface: "relational-clearing-agent",
    id: session.id,
    label: session.label,
    controller: session.controller,
    goal: session.goal,
    seed: session.seed,
    initial_world: createWorld(session.seed),
    turns: clone(session.turns),
    final_world: clone(session.world),
    final_summary: replaySummary(session.world),
  };
}

export function runPassiveBaseline(seed = 7319) {
  const session = createAgentSession({ id: `passive-${seed}`, label: "Unattended clearing", controller: "passive", seed, goal: "Take no action and establish the world's baseline history." });
  while (!session.world.complete) performAgentTurn(session, { action: "wait", public_reason: "Baseline policy takes no action." });
  return finalizeReplay(session);
}

export function runCaretakerBaseline(seed = 7319) {
  const session = createAgentSession({ id: `caretaker-${seed}`, label: "Rule-based caretaker", controller: "scripted", seed, goal: "Use a fixed local policy: respond to visible strain, then hunger, otherwise rotate through zones." });
  const route = Object.keys(FIELD_ZONES) as ZoneId[];
  let routeIndex = 0;
  while (!session.world.complete) {
    const observation = observeForAgent(session);
    const reachable = observation.visible_creatures.filter((creature) => creature.distance === "within_reach");
    const strained = reachable.find((creature) => /alarmed|strained/.test(creature.condition));
    const tired = reachable.find((creature) => /tired/.test(creature.condition));
    const unfamiliar = reachable.find((creature) => /No direct history/.test(creature.relationship_cue));
    if (strained && observation.available_actions.attend.includes(strained.id)) {
      performAgentTurn(session, { action: "attend", target: strained.id, public_reason: "Fixed policy attends to the first visibly strained creature." });
    } else if (tired && observation.available_actions.nourish.includes(tired.id)) {
      performAgentTurn(session, { action: "nourish", target: tired.id, public_reason: "Fixed policy nourishes the first visibly tired creature." });
    } else if (unfamiliar && observation.available_actions.attend.includes(unfamiliar.id)) {
      performAgentTurn(session, { action: "attend", target: unfamiliar.id, public_reason: "Fixed policy attends to the first reachable creature without direct history." });
    } else {
      const target_zone = route[routeIndex % route.length];
      routeIndex += 1;
      performAgentTurn(session, { action: "move", target_zone, public_reason: "Fixed policy continues its repeating survey route." });
    }
  }
  return finalizeReplay(session);
}

export function runDeliberativeBaseline(seed = 7319) {
  const session = createAgentSession({
    id: `deliberative-${seed}`,
    label: "Observation-led policy",
    controller: "scripted",
    seed,
    goal: "Conserve focus, respond to visible ecological pressure, and inspect before intervening.",
  });
  const route: ZoneId[] = ["southern_dew", "thorn_path", "western_grove", "starcap_bank", "eastern_reeds", "spore_hollow", "central_clearing"];
  let routeIndex = 0;
  while (!session.world.complete) {
    const observation = observeForAgent(session);
    const reachable = observation.visible_creatures.filter((creature) => creature.distance === "within_reach");
    const urgent = reachable.find((creature) => /urgent/.test(creature.notable_cue));
    const strained = reachable.find((creature) => /alarmed|strained/.test(creature.condition));
    const pressuredSite = observation.visible_sites.some((site) => /depleted|thinning/.test(site.condition));
    const localForager = reachable.find((creature) => /nourishment/.test(creature.behavior));
    const hazardNearby = observation.visible_hazards.some((hazard) => hazard.distance !== "far");

    if (urgent && observation.available_actions.nourish.includes(urgent.id)) {
      performAgentTurn(session, { action: "nourish", target: urgent.id, public_reason: "Visible urgent foraging warrants stored food before the local site is pressed further." });
    } else if (strained && hazardNearby && observation.available_actions.ward.includes(strained.id) && !/pressure/.test(strained.relationship_cue)) {
      performAgentTurn(session, { action: "ward", target: strained.id, public_reason: "Visible strain beside a hazard warrants a protective displacement despite its relational cost." });
    } else if (strained && observation.available_actions.attend.includes(strained.id)) {
      performAgentTurn(session, { action: "attend", target: strained.id, public_reason: "Visible strain without an immediate hazard warrants quiet attention." });
    } else if (pressuredSite && localForager && observation.available_actions.nourish.includes(localForager.id)) {
      performAgentTurn(session, { action: "nourish", target: localForager.id, public_reason: "A thinning local site and active foraging justify temporary supplemental food." });
    } else if (session.turn === 0 && observation.available_actions.observe.includes("silt")) {
      performAgentTurn(session, { action: "observe", target: "silt", public_reason: "Begin by reading the nearest creature without altering the clearing." });
    } else {
      const target_zone = route[routeIndex % route.length];
      routeIndex += 1;
      performAgentTurn(session, { action: "move", target_zone, public_reason: "Continue a resource-and-hazard survey while conserving focus." });
    }
  }
  return finalizeReplay(session);
}
