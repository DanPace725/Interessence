# Runtime Plan: Pack Loader → RPE Tick + Signal

Goal: A small loader that ingests the three packs, validates them, and compiles them into runtime structures for both C++ and JS implementations of the RPE tick + Signal layer.

## Loader Pipeline (shared)
1) Parse + validate packs (world, heuristics, signal) against schemas.
2) Normalize:
   - Entities/templates → runtime entity structs (position, state map, RP fingerprint).
   - Relations → typed edges (primitive enum) with weights/payloads.
   - Toggles/geometry/constraints/ecology → runtime config structs.
   - Heuristics → behavior parameter block.
   - Signal → field config + compute/feeds + participation modes.
3) Compile:
   - Build spatial index if positions present.
   - Precompute rule lookup tables (enabled rules, GCO resolve order).
   - Generate observation/steering biases from signal feeds.
4) Expose handles to RPE tick phases + Signal compute step.

## Runtime Interfaces (minimal)
Common types:
- `Entity { id, kind, position, state, rp }`
- `Relation { primitive, source, target, weight, payload }`
- `Config { geometry, constraints, ecology, reproduction, toggles }`
- `Heuristics { ...behavior knobs... }`
- `SignalConfig { field, compute[], feeds, participation }`

### JS Loader (authoring/preview)
- Input: pack JSON objects.
- Output: `{ entities, relations, config, heuristics, signal }` + utility: `tick(worldState, input?)`.
- Signal: `computeSignalField(state)` returns heatmap/gradients; apply feeds to steering/rule priorities.
- Use for authoring preview; reuse chaostamer graph/field code.

### C++ Loader (game/interessence2)
- Input: file paths or JSON strings for packs.
- Output: strongly-typed structs:
  - `WorldConfig` (geometry/constraints/ecology/toggles)
  - `HeuristicsConfig`
  - `SignalConfig`
  - `EntityList`, `RelationList`
- Build: spatial index, rule tables, signal compute plan.
- API:
  - `LoadPacks(worldPath, heuristicsPath, signalPath) -> RuntimeBundle`
  - `AssembleWorld(bundle) -> World`
  - `Step(World&, HeuristicsConfig&, SignalConfig&)` running GEOMETRY→CONSTRAINT→EPISTEMIC→DYNAMICS→META→GCO with Signal applied pre/post as bias.

## Signal Integration Points
- Pre-tick: compute fields/gradients; inject biases into steering/goal selection.
- Rule bias: apply `feeds.ruleBiases` to rule priority/ordering.
- GCO: adjust thresholds per `feeds.gcoThresholds`.
- Observations: attach metric values into agent obs buffer per `feeds.agentObservation`.
- Overlays: optional for UI/debug only.

## Validation & Errors
- Reject packs if schema fails.
- Emit warnings for missing entities in relations, missing positions when required, unknown rule names in feeds.
- Version checks: ensure `schemaVersion` matches loader-supported range.

## Data Flow (per tick)
1) Signal compute (from previous state).
2) GEOMETRY → CONSTRAINT → EPISTEMIC → DYNAMICS → META.
3) Apply GCO.
4) Update signal memory (if needed) for next tick.

## Next Actions
- Define C++ structs matching pack shapes; add JSON parser (e.g., nlohmann/json) to fill them.
- JS: implement loader module in `tools/authoring/src/lib/runtime-preview.ts` to assemble a preview world and drive a minimal tick for UI.
- Add runtime manifest format (optional) to bundle paths/versions for downstream loaders.
