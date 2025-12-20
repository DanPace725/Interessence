# Visual Studio & CMake System Setup

## System Configuration

This document describes the **exact Visual Studio and CMake configuration** on this system. Use this as a reference when troubleshooting build issues.

## Installed Software

### CMake
- **Version**: 4.2.1
- **Installation Path**: `C:\Program Files\CMake`
- **Binary Path**: `C:\Program Files\CMake\bin\cmake.exe`
- **In PATH**: ✓ Yes (system-wide)

### Visual Studio
- **Version**: Community 2026 (Preview)
- **Product Name**: Visual Studio Community 2026 Preview
- **Installation Path**: `E:\Visual Studio\Visual Studio`
- **MSVC Compiler**: `E:/Visual Studio/Visual Studio/VC/Tools/MSVC/14.50.35717/bin/Hostx64/x64/cl.exe`
- **Compiler Version**: 19.50.35720.0
- **CMake Generator Name**: `"Visual Studio 18 2026"`

### Windows SDK
- **Version**: 10.0.26100.0
- **Target OS**: Windows 10.0.26200

## Environment Variables

### DO NOT ADD to PATH
❌ `E:\Visual Studio\VC\vcpkg\scripts\cmake` - Not needed
❌ `E:\Visual Studio` - Not needed

CMake uses `vswhere.exe` to automatically locate Visual Studio installations. Manual PATH entries for Visual Studio are unnecessary and can cause conflicts.

### What IS in PATH
✓ `C:\Program Files\CMake\bin` - CMake tools

## How CMake Finds Visual Studio

CMake automatically detects Visual Studio using:
```powershell
&"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
```

**Output**: `E:\Visual Studio\Visual Studio`

This happens automatically when you specify a Visual Studio generator.

## CMake Generator Names

### Correct Generator for This System
```powershell
cmake -G "Visual Studio 18 2026" -B build
```

### Why This Specific Generator?
- **VS 2026** → Generator version **18**
- **VS 2022** → Generator version **17**
- **VS 2019** → Generator version **16**

The version number in the generator name corresponds to the Visual Studio version, not the MSVC compiler version.

### Available Generators on This System
Run to see all:
```powershell
cmake --help
```

Key generators available:
- `Visual Studio 18 2026` ✓ **Use this**
- `Ninja`
- `NMake Makefiles`
- `Unix Makefiles` (requires MinGW/Cygwin)

## Build Workflows

### Standard CMake + VS Workflow
```powershell
# 1. Configure (generate VS solution files)
cmake -G "Visual Studio 18 2026" -B build

# 2. Build (compile the project)
cmake --build build --config Release

# 3. Run
.\build\Release\your-executable.exe
```

### Alternative: Use MSBuild Directly
```powershell
# After cmake configure step:
msbuild build\YourProject.sln /p:Configuration=Release
```

### Alternative: Ninja Build (Faster)
```powershell
# Initialize VS environment first
&"E:\Visual Studio\Visual Studio\Common7\Tools\Launch-VsDevShell.ps1" -Arch amd64

# Then use Ninja
cmake -G Ninja -B build
cmake --build build
```

## Verification Commands

### Check CMake Installation
```powershell
cmake --version
# Expected: cmake version 4.2.1

where cmake
# Expected: C:\Program Files\CMake\bin\cmake.exe
```

### Check Visual Studio Installation
```powershell
&"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
# Expected: E:\Visual Studio\Visual Studio

&"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property displayName
# Expected: Visual Studio Community 2026 Preview
```

### Check Compiler
```powershell
&"E:\Visual Studio\Visual Studio\Common7\Tools\Launch-VsDevShell.ps1" -Arch amd64
cl
# Should show: Microsoft (R) C/C++ Optimizing Compiler Version 19.50.35720.0
```

## Common Issues

### Issue 1: "Could not find any instance of Visual Studio"
**Cause**: Wrong generator name specified
**Solution**: Use `"Visual Studio 18 2026"` (not 17 2022)

### Issue 2: "Generator does not match the generator used previously"
**Cause**: CMakeCache.txt has old generator name
**Solution**: Clean build directory:
```powershell
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
```

### Issue 3: CMake doesn't recognize Visual Studio
**Cause**: Unusual installation path
**Solution**: CMake should auto-detect via vswhere. If not, manually specify:
```powershell
cmake -G "Visual Studio 18 2026" -T "host=x64" -A x64 -B build
```

### Issue 4: Wrong MSVC version selected
**Cause**: Multiple MSVC toolsets installed
**Solution**: Specify toolset:
```powershell
cmake -G "Visual Studio 18 2026" -T "v145" -B build
```

## Developer Command Prompt Alternative

Instead of using CMake generators, you can use the VS Developer environment:

```powershell
# Launch VS developer environment
&"E:\Visual Studio\Visual Studio\Common7\Tools\Launch-VsDevShell.ps1" -Arch amd64

# Now cl, link, nmake, etc. are available
cd E:\Coding\Interessence\Reference\game
cmake -G "NMake Makefiles" -B build
cmake --build build
```

## vcpkg Integration (Optional)

If you need vcpkg package manager:
```powershell
$env:CMAKE_TOOLCHAIN_FILE = "E:\Visual Studio\VC\vcpkg\scripts\buildsystems\vcpkg.cmake"
cmake -G "Visual Studio 18 2026" -B build
```

## Best Practices for AI Agents

1. **Always verify the generator name** - It must match the installed VS version
2. **Clean before reconfiguring** - Avoid generator mismatch errors
3. **Use absolute paths** - Especially important on Windows
4. **Check exit codes** - `$LASTEXITCODE` in PowerShell
5. **Don't manually modify PATH for VS** - Let CMake auto-detect
6. **Prefer `cmake --build`** over direct `msbuild` - More portable

## Directory Structure

```
E:\Coding\Interessence\
└── Reference\
    ├── game\                  # C++ game project
    │   ├── CMakeLists.txt    # Main build config
    │   ├── include\          # Headers
    │   ├── src\              # Sources
    │   └── build\            # Build output (generated)
    ├── chaostamer\           # TypeScript reference
    └── EmergenceEngine\      # JavaScript reference
```

## Related Documentation

- [AI Build Guide](game/docs/AI_BUILD_GUIDE.md) - Detailed build instructions
- [Quick Reference](game/BUILD_QUICK_REFERENCE.md) - Fast command reference
- [CMakeLists.txt](game/CMakeLists.txt) - Build configuration

## System Snapshot Date
December 15, 2025

---

**Note**: This document describes the system as configured on the date above. If VS or CMake are updated, generator names or paths may change.

