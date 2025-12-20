# AI Agent Build Guide - Visual Studio & CMake

## Overview
This guide is specifically for AI agents working on this codebase. It documents the exact environment configuration and build commands that work for this project.

## Environment Details

### Software Installed
- **CMake**: Version 4.2.1
  - Location: `C:\Program Files\CMake\bin`
  - Already in PATH ✓
- **Visual Studio**: Community 2026 (Preview)
  - Installation Path: `E:\Visual Studio\Visual Studio`
  - MSVC Compiler: `E:/Visual Studio/Visual Studio/VC/Tools/MSVC/14.50.35717/bin/Hostx64/x64/cl.exe`
  - Version: 19.50.35720.0
- **Windows SDK**: 10.0.26100.0
- **Target**: Windows 10.0.26200

### Important Notes
- Do NOT add `E:\Visual Studio\VC\vcpkg\scripts\cmake` to PATH (not needed)
- Do NOT add `E:\Visual Studio` to PATH (not needed)
- CMake auto-detects Visual Studio using `vswhere.exe`

## Project Structure

```
Reference/game/
├── CMakeLists.txt          # Main CMake configuration
├── include/                # Header files
│   ├── core/              # Core engine headers
│   ├── primitives/        # Entity templates
│   ├── rules/             # Game rules
│   ├── spatial/           # Spatial indexing
│   └── utils/             # Utilities
├── src/                    # Source files
│   ├── core/
│   ├── primitives/
│   ├── spatial/
│   └── utils/
├── examples/              # Example programs
└── build/                 # Build output (generated)
```

## Build Commands

### Method 1: Visual Studio Generator (Recommended for Development)

**Initial Configuration:**
```powershell
cd E:\Coding\Interessence\Reference\game
cmake -G "Visual Studio 18 2026" -B build
```

**Build the Project:**
```powershell
cmake --build build --config Release
```

**Or for Debug:**
```powershell
cmake --build build --config Debug
```

**Clean and Reconfigure:**
```powershell
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
cmake -G "Visual Studio 18 2026" -B build
```

### Method 2: Ninja Generator (Faster Builds)

**Prerequisites:**
First, initialize the Visual Studio environment:
```powershell
&"E:\Visual Studio\Visual Studio\Common7\Tools\Launch-VsDevShell.ps1" -Arch amd64
```

**Then Build:**
```powershell
cd E:\Coding\Interessence\Reference\game
cmake -G Ninja -B build
cmake --build build
```

### Method 3: Using Developer Command Prompt

**Launch VS Developer Environment:**
```powershell
&"E:\Visual Studio\Visual Studio\Common7\Tools\Launch-VsDevShell.ps1" -Arch amd64
cd E:\Coding\Interessence\Reference\game
```

**Then use any generator:**
```powershell
cmake -G "NMake Makefiles" -B build
cmake --build build
```

## Build Targets

The CMakeLists.txt defines these targets:

1. **rpe_core** - Static library containing the core engine
2. **ecosystem_demo** - Example executable

**Build specific target:**
```powershell
cmake --build build --target rpe_core
cmake --build build --target ecosystem_demo
```

## Running the Built Executable

**After building:**
```powershell
.\build\Release\ecosystem_demo.exe
# or
.\build\Debug\ecosystem_demo.exe
```

## Common Issues and Solutions

### Issue: "Generator Visual Studio 17 2022 could not find any instance"
**Solution:** Use the correct generator: `"Visual Studio 18 2026"`

### Issue: "Generator does not match the generator used previously"
**Solution:** Clean the build directory first:
```powershell
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
```

### Issue: CMake not found
**Solution:** CMake should be in PATH at `C:\Program Files\CMake\bin`. Verify:
```powershell
cmake --version
```

### Issue: Compiler not found
**Solution:** CMake auto-detects VS. Verify VS is installed:
```powershell
&"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath
```

## Automated Build Script

**For CI/CD or automated builds, use this PowerShell script:**

```powershell
# automated-build.ps1
$ErrorActionPreference = "Stop"

$PROJECT_DIR = "E:\Coding\Interessence\Reference\game"
$BUILD_TYPE = "Release"

Write-Host "=== Starting Automated Build ==="

# Navigate to project
Set-Location $PROJECT_DIR

# Clean previous build
Write-Host "Cleaning previous build..."
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue

# Configure with CMake
Write-Host "Configuring with CMake..."
cmake -G "Visual Studio 18 2026" -B build

if ($LASTEXITCODE -ne 0) {
    Write-Error "CMake configuration failed!"
    exit 1
}

# Build
Write-Host "Building project..."
cmake --build build --config $BUILD_TYPE

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed!"
    exit 1
}

Write-Host "=== Build Completed Successfully ==="
Write-Host "Executable location: $PROJECT_DIR\build\$BUILD_TYPE\ecosystem_demo.exe"
```

**Run the script:**
```powershell
.\automated-build.ps1
```

## Verifying the Build

**Check if files were created:**
```powershell
Get-ChildItem -Recurse build\Release\*.exe
Get-ChildItem -Recurse build\Release\*.lib
```

**Expected output files:**
- `build\Release\ecosystem_demo.exe`
- `build\Release\rpe_core.lib`

## CMake Configuration Options

**View available generators:**
```powershell
cmake --help
```

**List available configurations:**
```powershell
cmake --build build --config ?
# Available: Debug, Release, MinSizeRel, RelWithDebInfo
```

**Enable verbose output:**
```powershell
cmake --build build --config Release --verbose
```

## Integration with Other Tools

### Using with vcpkg (if needed later)
```powershell
$env:CMAKE_TOOLCHAIN_FILE = "E:\Visual Studio\VC\vcpkg\scripts\buildsystems\vcpkg.cmake"
cmake -G "Visual Studio 18 2026" -B build
```

### Using with MSBuild directly
```powershell
msbuild build\RPGameSim.sln /p:Configuration=Release
```

## Tips for AI Agents

1. **Always clean before major changes**: `Remove-Item -Recurse -Force build`
2. **Use absolute paths** when possible to avoid confusion
3. **Check exit codes**: `$LASTEXITCODE` in PowerShell, `$?` in bash
4. **The generator name must be exact**: `"Visual Studio 18 2026"` (not 17, not 2022)
5. **CMake auto-detects VS**: No need to manually specify compiler paths
6. **Windows paths use backslashes** but CMake accepts forward slashes too

## Quick Reference Commands

```powershell
# Full rebuild from scratch
cd E:\Coding\Interessence\Reference\game
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
cmake -G "Visual Studio 18 2026" -B build
cmake --build build --config Release

# Check what's installed
cmake --version                     # CMake version
where cmake                          # CMake location
&"C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property displayName

# Troubleshooting
Get-ChildItem build\               # List build directory
cmake --build build --config Release --verbose  # Verbose build
```

## Last Updated
December 15, 2025

---

**Note for AI Agents**: This guide is based on the actual environment configuration found on this system. Always verify paths and versions match before executing commands.

