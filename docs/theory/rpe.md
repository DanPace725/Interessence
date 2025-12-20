
📘 **Relational Primitive Engine (RPE)
Deterministic Update Algorithm v2**
Purpose
The Relational Primitive Engine (RPE) provides a deterministic, ontology-driven, emergent simulation layer. It evaluates world state through six relational primitives (Ontology, Geometry, Constraint, Epistemic, Dynamics, Meta) and applies the Global Closure Operator (GCO) to produce a consistent, stable, and interpretable world update each tick.
The RPE is engine-agnostic and integrates cleanly with Unreal, Unity, Godot, or a custom engine.

---
1. Data Model
Entity
A discrete world participant.
Entity {  id: string,  kind: string,      // category/class/template  state: { key: value } // arbitrary properties (hp, hunger, faction, resources...)}
Relation
A typed edge connecting entities or expressing a property.
Relation {  primitive: ONTOLOGY | GEOMETRY | CONSTRAINT | EPISTEMIC | DYNAMICS | META,  source: EntityID,  target?: EntityID,  payload?: any      // radius, weight, occlusion, visibility, resource delta, rule references...}
World
World {  entities: Set<Entity>,  relations: Set<Relation>,  spatialIndex: Structure,    // quadtree/octree/BVH for GEOMETRY + EPISTEMIC  dirtyFlags: Map<EntityID, Flags> // tracks which entities changed and why}

---
2. Update Cycle (One Tick)
The RPE update cycle is strictly ordered for determinism:

---
⭐ Step 1 — GEOMETRY
(Spatial, structural, topological evaluation)
Purpose: Build a geometric snapshot for the tick.
Operations:
Compute proximity relations
Field gradients (pressure, influence, heat, mana, etc.)
Occlusion and line-of-sight
Structural connectivity
Region membership
Local curvature / manifold effects

Output:GeometryContext
This serves as the spatial foundation for all subsequent primitives.

---
⭐ Step 2 — CONSTRAINT
Purpose: Enforce physical, systemic, resource, or logical bounds.
Examples:
clamp health, energy, capacity
enforce conservation rules
apply faction laws or cultural norms
stabilize invalid states
handle collisions or blocked actions

This stage ensures the world enters Dynamics in a valid, bounded configuration.

---
⭐ Step 3 — EPISTEMIC
Purpose: Determine what each entity knows, based on Geometry and Constraints.
Derived from:
visibility
sensory ranges
occlusion
faction intelligence
memory
inference rules

Output:Knowledge graph per agent or per faction.
This grounds the simulation in local perspective — agents cannot act on information they do not have.
(It also supports stealth, misinformation, rumors, and drift.)

---
⭐ Step 4 — DYNAMICS
Purpose: Apply state changes—movement, growth, decay, combat, reproduction, trade, social action—filtered through Constraints and Epistemics.
Dynamics include:
movement or pathing
metabolic cycles
resource flows
combat resolution
AI decision-making
behavior scripts (or RP-rule behavior selectors)
ecological or systemic dynamics

This is the main “action” stage of the simulation.

---
⭐ Step 5 — META
Purpose: Rules about rules. Structural operations. System-level mutation.
META handles:
spawning / despawning entities
adding/removing relations
role changes
faction reorganization
cultural drift
rule injection (e.g., new schema when player builds a creation)
architecture changes
large-scale systemic adjustments
rewriting topologies or categories

META is how the world evolves its own laws.

---
⭐ Step 6 — GCO (Global Closure Operator)
Purpose: Ensure world consistency; resolve contradictions; finalize the tick.
Operations:
dedupe relations
remove contradictions
enforce schema-level invariants
resolve conflicts deterministically
collapse equivalences
freeze stable states
trigger RESET events where appropriate
produce a closure report for debugging and/or narrative use

After GCO completes, the world state is valid, minimal, consistent, and ready for the next tick.

---
3. Runtime Integration
For UE5 or Unity:
Run RPE.Step(world):
after physics simulation
after animation updates
before AI planning or rendering
optionally multiple times per gameplay tick (substepping)

The RPE becomes the semantic layer of the engine.

---
4. Authoring Rules
Rules are authored as:
JSON
ScriptableObjects / DataAssets
Lua fragments
Blueprint function objects
Graph-based logic

Each rule emits or modifies Relations.
META rules may mutate the ruleset itself.

---
5. Performance Notes
Use spatial indexing aggressively for GEOMETRY and EPISTEMIC.
Use change-driven evaluation (only recompute relations touching “dirty” entities).
Keep GCO simple (not a solver—just a closure pruner).
Cache perceptual fields where possible.

This keeps the simulation scalable to thousands of entities.

---
6. Debugging and Introspection
The greatest strength of RPE is transparency.
Log or visualize:
relations added this tick
relations removed
contradictions detected
closure events
epistemic states
META rewrites

This makes AI and world-sim behavior fully explainable.

---
⭐ 7. Determinism Guarantees
The RPE tick cycle is deterministic if:
input order is stable
relation evaluation order is stable
GCO resolution rules are stable

This enables:
replays
debugging
synchronization for multiplayer
predictable AI
reproducible world evolutions


