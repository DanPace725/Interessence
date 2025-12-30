# Neo Noise → Unreal Engine 5 Import Guide

Import Neo Noise generated terrain into Unreal Engine 5 Landscape system.

**Tested with:** UE5.5.4, UE5.7

---

## Quick Start

```bash
# Generate export files
cd "Neo Noise/demos"
python export_for_unreal.py YOURWORLD --size 1009
```

This creates in `samples/unreal_export/YOURWORLD/`:
- `heightmap.png` - 16-bit elevation
- `splatmap.png` - RGB layer weights  
- `water_mask.png` - River/lake mask
- `metadata.json` - Import settings

---

## Step 1: Import Heightmap

1. **Create Landscape**
   - File → New Level → Empty Level
   - Activate **Landscape Mode** (Shift+3)
   - Select **New Landscape** tab

2. **Configure Import**
   - Enable "Import from File"
   - Click **...** and select `heightmap.png`
   - Verify resolution shows as 1009×1009

3. **Set Scale**
   - X/Y Scale: `100` (1 pixel = 1 meter)
   - Z Scale: `100` (adjust for terrain height)
   - Check `metadata.json` for recommended values

4. **Create**
   - Click **Create** button
   - Terrain appears in viewport

---

## Step 2: Setup Material Layers

### Import Splatmap

1. Drag `splatmap.png` into Content Browser
2. Open texture, set:
   - **sRGB**: ☐ (unchecked)
   - **Compression**: `Masks`
3. Save

### Create Landscape Material

1. Right-click → Material → name it `M_NeoLandscape`
2. Open Material Editor
3. Add nodes:

```
[Texture Sample: splatmap] 
    → R → [LandscapeLayerBlend: Ground]
    → G → [LandscapeLayerBlend: Rock]  
    → B → [LandscapeLayerBlend: Organic]
```

4. Configure each `LandscapeLayerBlend`:
   - Layer Name: `Ground`, `Rock`, `Organic`
   - Blend Type: `LB_WeightBlend`

5. Connect each blend to layer textures (grass, rock, etc.)
6. Apply material to Landscape

---

## Step 3: Water Features

### Option A: Material Mask

1. Import `water_mask.png` (sRGB off)
2. Use as water blend in material
3. Blue tint where mask is white

### Option B: Water Bodies (UE5.1+)

1. Add Water Body actors at mask locations
2. Use mask as placement guide
3. Adjust splines to match rivers

---

## Recommended Settings

| Parameter | Value | Notes |
|-----------|-------|-------|
| Landscape Size | 1009×1009 | Single component, no seams |
| Z Scale | 100 | 100m vertical range |
| Streaming | Enabled | For large worlds |

---

## Troubleshooting

**Terrain is flat/blocky**
- Check heightmap is 16-bit (not 8-bit)
- Verify Z Scale isn't 0

**Splatmap colors wrong**
- Must have sRGB disabled
- Compression must be Masks

**Scale feels off**
- At Z=100, full height range ≈ 650m
- Adjust based on your world scale (see `Neo_Noise_Scale.md`)

---

## UE5 Version Notes

| Version | Notes |
|---------|-------|
| 5.5.x | Water Bodies require plugin enable |
| 5.6.x | Landscape streaming improvements |
| 5.7.x | Full support, no special steps |

All versions support the core heightmap/splatmap workflow.
