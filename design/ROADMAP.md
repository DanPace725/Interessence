# Interessence Roadmap

This roadmap anchors the new stack around a shared schema contract so authoring tools and runtimes stay aligned.

## Layers and Deliverables
- Theory/spec: RPE tick + GCO + Signal-as-bias-field (Reference/ docs stay informational).
- Authoring/visualization (EE/RM successor): tune heuristics, inspect topology/signal, export packs.
- Runtime (game): load packs, run RPE + Signal, render/play.

## Schema Contracts (v0)
- world-pack.schema.json: entities/templates, relations, initial state, rule toggles, RNG seed.
- heuristics-pack.schema.json: ~20 adaptive tunables (movement, sensing, rewards, mutation, participation forces).
- signal-pack.schema.json: which signal metrics to compute and where to surface them (biases to rules/GCO/agents/overlays).
- snapshot.schema.json (later): runtime → UI export for replay/inspection.

## Initial Milestones
1) Lock schemas: define v0 of world, heuristics, signal packs with strict versions and `additionalProperties: false`.
2) Authoring tool plan: flows for loading/editing packs, topology/signal visualizations, export pipeline.
3) Runtime plan: loader that compiles packs into RPE tick + Signal; minimal C++/JS bindings to match schema.
4) Demo slice: a small forest/predator-prey scenario that runs end-to-end (UI export → runtime load → signal overlays).
5) Training hook (optional): keep fields reserved to swap heuristic parameters with learned values later.

## Separation of Concerns
- Reference/ remains read-only guidance and theory.
- design/ holds plans and architecture notes.
- schemas/ holds the versioned contracts.
- runtime/ will house the game code that ingests packs.
- tools/ will house the authoring/visualization UI code.
- Terminology: use “stress” (not “frustration”) for arousal/load dynamics in new configs; treat energy vs chi as distinct pools (energy = metabolic/storage, chi = actionable budget converted from energy).

## Versioning Rules
- Each schema carries a `schemaVersion` string; breaking changes bump major, additive changes bump minor.
- Packs declare which schema version they target.
- Runtimes must validate packs against the declared schema before compiling them.
