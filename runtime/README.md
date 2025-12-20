# Interessence Runtime (C++)

Minimal C++ scaffolding to load the pack schemas (world/heuristics/signal) and run a stub RPE tick.

## Structure
- `CMakeLists.txt` — builds `interessence_runtime` library.
- `include/runtime/Types.h` — structs matching pack shapes (entities, relations, configs).
- `include/runtime/Loader.h` — load packs from JSON strings or files into a `RuntimeBundle`.
- `include/runtime/Runtime.h` — stub runtime with RPE phase hooks.
- `src/Loader.cpp` — JSON parsing/normalization (uses nlohmann_json when enabled).
- `src/Runtime.cpp` — stub tick phases.

## Building

### Headless Demo
```bash
cmake -S runtime -B runtime/build -DINTERESSENCE_ENABLE_JSON=ON
cmake --build runtime/build
```

### With Graphical Viewer
```bash
cmake -S runtime -B runtime/build -DINTERESSENCE_ENABLE_JSON=ON -DINTERESSENCE_ENABLE_VIEWER=ON
cmake --build runtime/build
```

Set `INTERESSENCE_ENABLE_JSON=ON` and provide `nlohmann_json` (via package manager or FetchContent) to enable JSON parsing. 

Set `INTERESSENCE_ENABLE_VIEWER=ON` to build the graphical viewer using raylib (auto-downloaded).

## Next Steps
- Fill in RPE phase logic in `Runtime.cpp` (Geometry → Constraint → Epistemic → Dynamics → Meta → GCO).
- Add signal compute + feed application pre/post tick.
- Add tests/examples that load the sample packs from `tools/authoring/public/samples/` and run a few ticks headless.
