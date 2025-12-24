# Neo Noise Scale Reference

> How to interpret pixel measurements in real-world game terms.

## The Core Question

**How big is a pixel?**

The answer depends on your game's **world scale** - you define it. This document provides reference mappings.

---

## Scale Presets

| Scale | 1 Pixel = | 256px Map = | 670px River = | Use Case |
|-------|-----------|-------------|---------------|----------|
| **Micro** | 1 meter | 256m (small arena) | 670m (short stream) | Dungeon, arena, small scene |
| **Local** | 10 meters | 2.5 km (village area) | 6.7 km (creek) | Town, local region |
| **Regional** | 100 meters | 25 km (county) | 67 km (small river) | Overworld exploration |
| **Continental** | 1 km | 256 km (small country) | 670 km (major river) | World map |

---

## Real-World River Comparisons

| River | Length | At Regional Scale (100m/px) |
|-------|--------|-----------------------------|
| Thames (London section) | 55 km | 550 pixels |
| Hudson River | 507 km | 5,070 pixels |
| Danube | 2,850 km | 28,500 pixels |
| Amazon | 6,400 km | 64,000 pixels |
| **Neo Noise Max (670px)** | **67 km** | Small/medium river ✓ |

**Conclusion**: At regional scale, 670 pixels = 67 km, which is realistic for a small-to-medium river like a county's main waterway.

---

## Recommended Multi-Scale Approach

### 1. Continental Map (512x256)
- **Scale**: 1 pixel = 2-4 km
- **Total Size**: 1,000-2,000 km across
- **Rivers**: Major arteries only (simplified paths)

### 2. Regional Tiles (256x256)  
- **Scale**: 1 pixel = 100 meters
- **Total Size**: 25.6 km × 25.6 km per tile
- **Rivers**: Full detail, tributaries, streams

### 3. Local Detail (256x256)
- **Scale**: 1 pixel = 10 meters
- **Total Size**: 2.56 km × 2.56 km
- **Rivers**: Banks, fords, bridges rendered

---

## Height Scale

The elevation range (0.0 to 1.0) maps to vertical height:

| Height Scale | 0.0-1.0 Range = | Example |
|--------------|-----------------|---------|
| Gentle | 100m | Rolling hills |
| Standard | 500m | Mountainous terrain |
| Dramatic | 2,000m | Alpine peaks |

**Current mesh exporter default**: `height_scale=40.0` in mesh units.

---

## Summary

**For a typical overworld game:**
- Use **Regional Scale** (1px = 100m)
- 256×256 tile = 25km × 25km playable area
- 670px river = 67km river (realistic for a region)
- Generate multiple tiles for larger worlds

**For world map / fast travel:**
- Use **Continental Scale** (1px = 2km)
- 512×256 map = 1024km × 512km world
- Rivers are schematic (show major paths only)
