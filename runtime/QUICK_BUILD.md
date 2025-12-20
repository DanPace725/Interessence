# Runtime - Quick Build Commands

## One-Line Build & Test

### Headless Demo
```powershell
cd E:\Coding\Interessence\runtime; Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue; cmake -G "Visual Studio 18 2026" -B build; cmake --build build --config Release; .\build\Release\interessence_demo.exe ..\tools\authoring\public\samples\forest-world-pack.json ..\tools\authoring\public\samples\forest-heuristics-pack.json ..\tools\authoring\public\samples\forest-signal-pack.json
```

### With Viewer (Graphical)
```powershell
cd E:\Coding\Interessence\runtime; Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue; cmake -G "Visual Studio 18 2026" -B build -DINTERESSENCE_ENABLE_VIEWER=ON -Wno-dev; cmake --build build --config Release; cd ..; .\runtime\build\Release\interessence_viewer.exe
```

## Common Commands

```powershell
# Clean build
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

# Configure
cmake -G "Visual Studio 18 2026" -B build

# Build Debug
cmake --build build --config Debug

# Build Release
cmake --build build --config Release

# Run with samples
.\build\Release\interessence_demo.exe `
  ..\tools\authoring\public\samples\forest-world-pack.json `
  ..\tools\authoring\public\samples\forest-heuristics-pack.json `
  ..\tools\authoring\public\samples\forest-signal-pack.json
```

## Expected Output

```
Loaded entities: 6
Loaded relations: 10
Tick 1 complete.
Tick 2 complete.
Tick 3 complete.
Tick 4 complete.
Tick 5 complete.
```

## Status: ✅ All builds working

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for details.

