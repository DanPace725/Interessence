# Quick Build Reference

## TL;DR - Build the Project

```powershell
cd E:\Coding\Interessence\Reference\game
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
cmake -G "Visual Studio 18 2026" -B build
cmake --build build --config Release
.\build\Release\ecosystem_demo.exe
```

## Environment
- **CMake**: 4.2.1
- **Visual Studio**: Community 2026 (Preview)
- **Generator**: `"Visual Studio 18 2026"` ⚠️ Must be exact!

## Common Commands

| Task | Command |
|------|---------|
| Configure | `cmake -G "Visual Studio 18 2026" -B build` |
| Build Release | `cmake --build build --config Release` |
| Build Debug | `cmake --build build --config Debug` |
| Clean | `Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue` |
| Run | `.\build\Release\ecosystem_demo.exe` |

## Why "Visual Studio 18 2026"?

This system has **Visual Studio 2026 Preview** installed, not VS 2022. CMake auto-detects it at:
- `E:\Visual Studio\Visual Studio`

## Troubleshooting

**Error: "Generator does not match"**
→ Clean first: `Remove-Item -Recurse -Force build`

**Error: "Could not find any instance of Visual Studio"**
→ Check you're using `"Visual Studio 18 2026"` (not 17 2022)

**CMake not found**
→ Should be at: `C:\Program Files\CMake\bin`

## Full Guide

See [AI_BUILD_GUIDE.md](docs/AI_BUILD_GUIDE.md) for complete documentation.

