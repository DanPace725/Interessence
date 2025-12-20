# Interessence Viewer Guide

## Overview

The **Interessence Viewer** is a real-time graphical visualizer for the runtime simulation. It uses **raylib** for rendering and displays entities as they move, interact, and evolve according to the RPE (Relational Primitives Engine) rules.

## Quick Start

### Build with Viewer Enabled

```powershell
cd E:\Coding\Interessence\runtime
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
cmake -G "Visual Studio 18 2026" -B build -DINTERESSENCE_ENABLE_JSON=ON -DINTERESSENCE_ENABLE_VIEWER=ON -Wno-dev
cmake --build build --config Release
```

### Run the Viewer

**From project root** (to use default sample packs):
```powershell
cd E:\Coding\Interessence
.\runtime\build\Release\interessence_viewer.exe
```

**Or with custom pack files**:
```powershell
.\runtime\build\Release\interessence_viewer.exe `
  path\to\world-pack.json `
  path\to\heuristics-pack.json `
  path\to\signal-pack.json
```

## Controls

| Key | Action |
|-----|--------|
| **Space** | Pause/Resume simulation |
| **ESC** or **Close Window** | Exit viewer |

## Visual Elements

### Entity Rendering

**Agents** (blue circles):
- **Size**: 8 pixels radius
- **Color**: Blue (RGB: 79, 106, 243)
- **Chi Bar**: Yellow bar above entity (max 20px)
- **Energy Bar**: Green bar below chi bar (max 20px)

**Resources** (green circles):
- **Size**: 6 pixels radius
- **Color**: Green (RGB: 76, 217, 100)
- No status bars

### Screen Layout

- **Background**: Dark blue (RGB: 14, 19, 29)
- **Resolution**: 1000x700 pixels
- **Camera**: Centered at screen center (500, 350)
- **Frame Rate**: 60 FPS

### Status Bars

Agents display two status bars:
1. **Chi (Yellow)**: Represents agent "chi" or internal energy
   - Maximum visual length: 20 pixels
   - Scale: chi * 0.2
2. **Energy (Green)**: Represents metabolic energy
   - Maximum visual length: 20 pixels
   - Scale: energy * 0.2

## How It Works

### Initialization
1. Loads pack files (world, heuristics, signal)
2. Creates Runtime instance with loaded entities and rules
3. Opens 1000x700 window titled "Interessence Viewer"
4. Sets target frame rate to 60 FPS

### Main Loop
Every frame:
1. If **running** (not paused), executes one `Runtime::Tick()`
2. Clears screen with dark background
3. For each entity:
   - Calculates screen position (entity.position + screen center)
   - Draws entity circle (blue for agents, green for resources)
   - For agents: draws chi and energy status bars
4. Displays control hint: "Space: pause/resume"

### Default Sample Packs

When run without arguments, the viewer searches for:
- `tools/authoring/public/samples/forest-world-pack.json`
- `tools/authoring/public/samples/forest-heuristics-pack.json`
- `tools/authoring/public/samples/forest-signal-pack.json`

Relative to the current working directory.

## Build Details

### Dependencies

**raylib 5.5** (auto-downloaded via FetchContent):
- Repository: https://github.com/raysan5/raylib.git
- Tag: 5.5
- Graphics API: OpenGL 3.3
- Platform: Windows Desktop
- Audio Backend: miniaudio

**nlohmann_json** (also required):
- For loading pack files

### CMake Options

```cmake
-DINTERESSENCE_ENABLE_VIEWER=ON   # Enable viewer build (default: ON)
-DINTERESSENCE_FETCH_RAYLIB=ON    # Auto-fetch raylib (default: ON)
```

### Build Targets

```powershell
# Build only the viewer
cmake --build build --config Release --target interessence_viewer

# Build everything (runtime lib, demo, viewer)
cmake --build build --config Release
```

## Troubleshooting

### Issue: "Failed to load packs"
**Cause**: Sample files not found
**Solution**: Run from project root:
```powershell
cd E:\Coding\Interessence
.\runtime\build\Release\interessence_viewer.exe
```

### Issue: Black window or no entities visible
**Cause**: Entities outside visible area
**Solution**: 
- Check entity positions in pack files
- Screen center is (500, 350)
- Entities at (0, 0) appear at screen center
- Visible range: approximately ±500 pixels from center

### Issue: Window closes immediately
**Cause**: Error during pack loading or initialization
**Solution**: Run from command line to see error messages:
```powershell
cd E:\Coding\Interessence
.\runtime\build\Release\interessence_viewer.exe
# Check for error messages before window opens
```

### Issue: Build fails with raylib errors
**Cause**: CMake version incompatibility or network issues
**Solution**: 
```powershell
# Clear build and try again
Remove-Item -Recurse -Force runtime/build
cmake -G "Visual Studio 18 2026" -B runtime/build -DINTERESSENCE_ENABLE_VIEWER=ON -Wno-dev
```

## Performance Notes

- **Target Frame Rate**: 60 FPS
- **Tick Rate**: 60 ticks/second (when unpaused)
- **Rendering**: Simple 2D circles (very fast)
- **Bottleneck**: Runtime simulation logic, not rendering

**Tips for better performance:**
- Reduce entity count in pack files
- Simplify heuristics rules
- Use Release build (10-20% faster than Debug)

## Source Code

**Main file**: `runtime/src/Viewer.cpp`

Key functions:
- `ResolveSample()` - Locates sample pack files
- `DrawBars()` - Renders chi and energy status bars
- `main()` - Window loop and entity rendering

## Extending the Viewer

### Adding New Visual Elements

Edit `runtime/src/Viewer.cpp`:

```cpp
// In the main loop, after drawing entities:
for (const auto& e : runtime.GetEntities()) {
    float x = cx + static_cast<float>(e.position.x);
    float y = cy + static_cast<float>(e.position.y);
    
    // Your custom rendering here
    // Example: Draw velocity vector
    DrawLine(x, y, 
             x + e.velocity.x * 10, 
             y + e.velocity.y * 10, 
             RED);
}
```

### Adding New Controls

```cpp
// In the main loop:
if (IsKeyPressed(KEY_R)) {
    // Reset simulation
    runtime = Runtime(originalBundle);
}

if (IsKeyPressed(KEY_S)) {
    // Single step
    runtime.Tick();
}
```

### Customizing Colors

```cpp
// Agent color
Color agentColor = Color{79, 106, 243, 255};  // Blue

// Resource color
Color resourceColor = Color{76, 217, 100, 255};  // Green

// Background
Color bgColor = Color{14, 19, 29, 255};  // Dark blue
```

## Related Files

- **Runtime Implementation**: `runtime/src/Runtime.cpp`
- **Pack Loading**: `runtime/src/Loader.cpp`
- **Type Definitions**: `runtime/include/runtime/Types.h`
- **Sample Packs**: `tools/authoring/public/samples/`

## Build Statistics

- **Viewer Executable Size**: ~693 KB (Release)
- **raylib Library Size**: ~7 MB (static link included)
- **First Build Time**: ~30-60 seconds (includes raylib download)
- **Incremental Build Time**: ~5-10 seconds

## Known Limitations

1. **No camera pan/zoom**: Fixed viewport centered on (0, 0)
2. **No entity selection**: Can't click on entities
3. **Limited status info**: Only chi and energy displayed
4. **No graph view**: No relationship visualization
5. **Single window**: Can't open multiple simulations

## Future Enhancements

Potential additions:
- [ ] Interactive camera (pan, zoom)
- [ ] Entity selection and inspection
- [ ] Relationship edge rendering
- [ ] Performance statistics overlay
- [ ] Screenshot/recording capability
- [ ] Configuration hot-reload

---

**Status**: ✅ Working  
**Last Updated**: December 15, 2025  
**Tested On**: Windows 10.0.26200, Visual Studio 2026 Preview

