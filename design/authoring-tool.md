# Authoring Tool Plan

Goal: A schema-driven editor for world/heuristics/signal packs with topology and signal visualization, plus reliable export.

## Core Flows
- Load packs: pick `world/heuristics/signal` JSON; validate against schemas; show inline errors.
- Edit packs:
  - Form view auto-generated from schema (types/ranges, booleans, enums).
  - JSON view with live validation and error surfacing.
  - Group energy/chi/stress and reproduction knobs coherently.
- Topology view:
  - Render RP graph from `entities`/`relations`, filter by primitive, show positions if present.
  - Edit nodes/edges; highlight constraints and META toggles.
- Signal view:
  - Display field settings (cell size, decay/diffuse) and channel settings.
  - Visualize computed metrics (gradient heatmap, coherence overlay).
  - Participation radii per mode; edit feeds (rule biases, GCO thresholds, steering couplings) via sliders.
- Preview (optional stub):
  - Run a tiny local sim against current packs for sanity checks.
  - Stream snapshots back to topology/signal views.
- Export:
  - Validate all packs; block export on errors.
  - Save individual packs + combined “scenario bundle” (paths or inline).
  - Stamp schema versions; warn on mismatch.

## UI Layout
- Left: pack navigator (world / heuristics / signal).
- Right: tabbed editor (Form, JSON).
- Bottom/side: graph canvas + signal overlay toggles; console for validation/logs.
- Controls: Import, Export, Validate, Preview Run, Snapshot (when preview is active).

## Data & Validation
- Use the JSON Schemas to:
  - Generate form controls.
  - Validate on edit; show per-field errors.
  - Enforce `additionalProperties: false`.
- Keep dirty state per pack; show diff badges.

## Visualizations
- Topology: force or spatial layout; color by primitive; size by RP fingerprint; selectable nodes/edges with detail pane.
- Signal: grid heatmap for a chosen channel; vectors for gradients; overlays for participation radii; metric readouts.

## Export Pipeline
- Step 1: Validate each pack.
- Step 2: Bundle (references or inline) with schemaVersion stamps and timestamp.
- Step 3: Save to disk; optionally emit a minimal manifest for runtime loaders.

## Implementation Notes
- Form generation: derive from schemas; add custom widgets for RP fingerprints and relation editor.
- Graph rendering: reuse chaostamer-style rendering; add per-node position support if present.
- Signal rendering: simple canvas grid; sampling hooks for preview mode.
- Keep an extensibility hook for future AI training fields (heuristics pack) without breaking core schemas.
