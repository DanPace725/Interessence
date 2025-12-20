# Interessence Runtime - Build Guide

## Build Status ✅

**Last Verified**: December 15, 2025  
**Status**: Successfully builds with Visual Studio 2026 Preview  
**CMake Generator**: `"Visual Studio 18 2026"`

## Quick Build

### Standard Build (Demo Only)
```powershell
cd E:\Coding\Interessence\runtime
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
cmake -G "Visual Studio 18 2026" -B build
cmake --build build --config Release
```

### Build with Viewer (Recommended)
```powershell
cd E:\Coding\Interessence\runtime
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
cmake -G "Visual Studio 18 2026" -B build -DINTERESSENCE_ENABLE_VIEWER=ON -Wno-dev
cmake --build build --config Release
```

## Running

### Demo (Headless)
```powershell
.\build\Release\interessence_demo.exe ..\tools\authoring\public\samples\forest-world-pack.json ..\tools\authoring\public\samples\forest-heuristics-pack.json ..\tools\authoring\public\samples\forest-signal-pack.json
```

**Expected Output:**
```
Loaded entities: 6
Loaded relations: 10
Tick 1 complete.
Tick 2 complete.
Tick 3 complete.
Tick 4 complete.
Tick 5 complete.
```

### Viewer (Graphical)
```powershell
# From project root to auto-find sample packs
cd E:\Coding\Interessence
.\runtime\build\Release\interessence_viewer.exe
```

**Controls:**
- **Space**: Pause/resume simulation
- **ESC**: Exit

See [VIEWER_GUIDE.md](VIEWER_GUIDE.md) for details.

## Build Configurations

### Debug Build
```powershell
cmake --build build --config Debug
.\build\Debug\interessence_demo.exe <world> <heuristics> <signal>
```

- **Executable Size**: ~911 KB
- **Library Size**: ~14.7 MB
- **Optimizations**: Disabled
- **Debug Symbols**: Included

### Release Build
```powershell
cmake --build build --config Release
.\build\Release\interessence_demo.exe <world> <heuristics> <signal>
```

- **Executable Size**: ~195 KB
- **Library Size**: ~7.5 MB
- **Optimizations**: Enabled
- **Debug Symbols**: Minimal

## Project Structure

```
runtime/
├── CMakeLists.txt              # Build configuration
├── include/runtime/            # Public headers
│   ├── Types.h                # Pack data structures
│   ├── Loader.h               # JSON loading
│   └── Runtime.h              # RPE tick system
├── src/                       # Implementation
│   ├── Demo.cpp               # Demo executable
│   ├── Loader.cpp             # JSON parsing
│   └── Runtime.cpp            # Runtime logic
└── build/                     # Build output (generated)
    ├── Debug/
    │   ├── interessence_demo.exe
    │   └── interessence_runtime.lib
    └── Release/
        ├── interessence_demo.exe
        └── interessence_runtime.lib
```

## Build Targets

The CMake configuration creates these targets:

| Target | Type | Description |
|--------|------|-------------|
| `interessence_runtime` | Static Library | Core runtime library |
| `interessence_demo` | Executable | Demo that loads packs and runs ticks |
| `ALL_BUILD` | Meta | Builds all targets |

**Build specific target:**
```powershell
cmake --build build --config Release --target interessence_runtime
cmake --build build --config Release --target interessence_demo
```

## Dependencies

### nlohmann_json (Automatic)
The project uses **FetchContent** to automatically download and build `nlohmann_json` v3.11.3 from GitHub.

- **Source**: https://github.com/nlohmann/json/releases/download/v3.11.3/json.tar.xz
- **Build Location**: `build/_deps/nlohmann_json-src/`
- **Build Type**: Header-only (multi-header mode)

**Note**: First build will download the dependency (one-time operation).

### CMake Options

```powershell
# Enable/disable JSON support (default: ON)
cmake -G "Visual Studio 18 2026" -B build -DINTERESSENCE_ENABLE_JSON=ON

# Disable auto-fetching nlohmann_json (requires manual install)
cmake -G "Visual Studio 18 2026" -B build -DINTERESSENCE_FETCH_JSON=OFF
```

## Build Warnings

The following warning is expected and harmless:

```
CMake Warning (dev) at C:/Program Files/CMake/share/cmake-4.2/Modules/FetchContent.cmake:1383 (message):
  The DOWNLOAD_EXTRACT_TIMESTAMP option was not given and policy CMP0135 is not set.
```

**To suppress:**
```powershell
cmake -G "Visual Studio 18 2026" -B build -Wno-dev
```

## Testing the Build

### 1. Verify Files Exist
```powershell
Get-ChildItem build\Release\*.exe, build\Release\*.lib
```

### 2. Run Demo Without Arguments (Usage Message)
```powershell
.\build\Release\interessence_demo.exe
# Expected: Usage: demo <world-pack.json> <heuristics-pack.json> <signal-pack.json>
```

### 3. Run Demo With Sample Packs
```powershell
.\build\Release\interessence_demo.exe `
  ..\tools\authoring\public\samples\forest-world-pack.json `
  ..\tools\authoring\public\samples\forest-heuristics-pack.json `
  ..\tools\authoring\public\samples\forest-signal-pack.json
```

## Common Issues

### Issue: "Generator does not match"
**Solution:** Clean the build directory:
```powershell
Remove-Item -Recurse -Force build
```

### Issue: nlohmann_json download fails
**Solution:** Check internet connection or manually provide the library:
```powershell
# Option 1: Use vcpkg
vcpkg install nlohmann-json
cmake -G "Visual Studio 18 2026" -B build -DINTERESSENCE_FETCH_JSON=OFF

# Option 2: Point to existing installation
cmake -G "Visual Studio 18 2026" -B build -Dnlohmann_json_DIR="C:/path/to/nlohmann_jsonConfig.cmake"
```

### Issue: Executable won't run
**Solution:** Check that you're using the correct path:
```powershell
# From runtime/ directory
.\build\Release\interessence_demo.exe

# Or use absolute path
E:\Coding\Interessence\runtime\build\Release\interessence_demo.exe
```

## Integration with Other Projects

### Using the Runtime Library

**In your CMakeLists.txt:**
```cmake
add_subdirectory(runtime)
target_link_libraries(your_target PRIVATE Interessence::runtime)
```

**Or with find_package (after installation):**
```cmake
find_package(interessence_runtime CONFIG REQUIRED)
target_link_libraries(your_target PRIVATE Interessence::runtime)
```

## Development Workflow

**Typical development cycle:**
```powershell
# 1. Edit source files
code .\src\Runtime.cpp

# 2. Rebuild
cmake --build build --config Debug

# 3. Test
.\build\Debug\interessence_demo.exe <test-packs>

# 4. If tests pass, build release
cmake --build build --config Release
```

## Next Steps

As documented in the README, the runtime is currently a stub. Next development tasks:

1. **Fill in RPE phase logic** in `Runtime.cpp`:
   - Geometry phase
   - Constraint phase
   - Epistemic phase
   - Dynamics phase
   - Meta phase
   - GCO (Garbage Collection/Optimization)

2. **Add signal computation**: Pre/post tick signal field processing

3. **Add comprehensive tests**: Unit tests for each RPE phase

4. **Performance profiling**: Optimize hot paths identified through profiling

## Related Documentation

- [README.md](README.md) - Project overview and structure
- [AI Build Guide](../Reference/game/docs/AI_BUILD_GUIDE.md) - General VS/CMake guide
- [System Setup](../Reference/VS_CMAKE_SYSTEM_SETUP.md) - Environment configuration

## Build Statistics

**Clean build time** (including dependency download):
- First build: ~10-15 seconds
- Incremental builds: ~2-5 seconds

**Build output sizes**:
- Debug: ~15 MB total (exe + lib)
- Release: ~7.6 MB total (exe + lib)

---

**Build Verified**: ✅ All configurations build without errors  
**Runtime Tested**: ✅ Successfully loads and processes sample packs  
**Last Test**: December 15, 2025

