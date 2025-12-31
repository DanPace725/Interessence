"""
Neo Landscape Blender Exporter v2
Generates comprehensive 3D landscape for Blender validation.

Exports:
- Terrain OBJ with GCO-eroded heightmap
- River mesh (carved geometry following river paths)
- Water plane at sea level (separate mesh)
- Biome diffuse texture with water overlay
- Water mask for material mixing

Versioning: Each export gets a unique version number for iteration tracking.
"""

import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import time

# Add src/ to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import neo_noise_core as core
import neo_gco as gco
import neo_biomes as biomes
import neo_reading as reading

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "samples", "3d", "blender")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Version tracking file
VERSION_FILE = os.path.join(OUTPUT_DIR, ".version_counter")


def get_next_version():
    """Get and increment the global version counter."""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as f:
            version = int(f.read().strip())
    else:
        version = 0
    
    with open(VERSION_FILE, 'w') as f:
        f.write(str(version + 1))
    
    return version + 1


def generate_river_mesh(overlay: np.ndarray, structure: np.ndarray, 
                        height_scale: float, river_depth: float = 2.0) -> tuple:
    """
    Generate river channel geometry from the GCO overlay.
    
    Args:
        overlay: GCO overlay with river/lake markers
        structure: Heightmap for base elevation
        height_scale: Vertical scaling
        river_depth: How deep to carve rivers (world units)
        
    Returns:
        vertices: List of (x, y, z) tuples
        faces: List of vertex index tuples (quads)
        uvs: List of (u, v) tuples
    """
    h, w = overlay.shape
    vertices = []
    faces = []
    uvs = []
    
    # Find river pixels (overlay > 0.7)
    river_mask = overlay > 0.7
    
    # For each river pixel, create a small quad depressed into terrain
    river_pixels = np.argwhere(river_mask)
    
    if len(river_pixels) == 0:
        return vertices, faces, uvs
    
    # Create vertex grid for river areas only (lower resolution)
    step = 2  # Sample every 2 pixels for efficiency
    
    for y in range(0, h - 1, step):
        for x in range(0, w - 1, step):
            # Check if any of the 4 corners are river
            is_river = (
                river_mask[y, x] or 
                river_mask[min(y + step, h-1), x] or
                river_mask[y, min(x + step, w-1)] or
                river_mask[min(y + step, h-1), min(x + step, w-1)]
            )
            
            if not is_river:
                continue
            
            # Get vertex indices for this quad
            base_idx = len(vertices)
            
            # Add 4 vertices for the quad
            for dy, dx in [(0, 0), (0, step), (step, 0), (step, step)]:
                py = min(y + dy, h - 1)
                px = min(x + dx, w - 1)
                
                # Position
                world_x = px - w / 2
                world_z = py - h / 2
                
                # Height: if river, carve down; otherwise use terrain height
                base_height = structure[py, px] * height_scale
                if river_mask[py, px]:
                    # Carve river channel
                    world_y = base_height - river_depth
                else:
                    # Bank edge - slightly below terrain for blending
                    world_y = base_height - river_depth * 0.3
                
                vertices.append((world_x, world_y, world_z))
                uvs.append((px / (w - 1), 1.0 - py / (h - 1)))
            
            # Add two triangular faces (quad split)
            # Vertices: 0=bottom-left, 1=bottom-right, 2=top-left, 3=top-right
            faces.append((base_idx + 0, base_idx + 2, base_idx + 3, base_idx + 1))
    
    return vertices, faces, uvs


def generate_landscape(inscription: str,
                       size: int = 256,
                       height_scale: float = 40.0,
                       sea_level: float = 0.25,
                       include_water_plane: bool = True,
                       include_river_mesh: bool = True,
                       include_glyph_overlay: bool = True,
                       river_depth: float = 2.0,
                       glyph_cell_size: int = 12,
                       glyph_alpha: float = 0.12,
                       octaves: int = 4,
                       persistence: float = 0.5,
                       lacunarity: float = 2.0,
                       version: int = None):
    """
    Generate a full landscape for Blender validation.
    
    Args:
        inscription: World seed string (e.g., "FOREST", "ARCHIPELAGO")
        size: Resolution (256, 512, or 1024 recommended)
        height_scale: Vertical exaggeration for the mesh
        sea_level: 0.0-1.0, elevation for ocean/water plane
        include_water_plane: Export separate water mesh
        include_river_mesh: Export carved river geometry
        river_depth: Depth of river channels in world units
        octaves: Noise detail level
        persistence: Noise amplitude falloff
        lacunarity: Noise frequency multiplier
        version: Optional version override (auto-increments if None)
        
    Returns:
        Dict with paths to all exported files
    """
    # Get version number
    if version is None:
        version = get_next_version()
    
    print(f"\n{'='*60}")
    print(f"Generating Landscape: '{inscription}' v{version} ({size}x{size})")
    print(f"{'='*60}")
    
    # =========================================================================
    # Step 1: Generate Base Terrain
    # =========================================================================
    print("\n[1/6] Generating base terrain...")
    base_structure, seed = core.generate_field(
        inscription, size, size, normalize=True,
        octaves=octaves, persistence=persistence, lacunarity=lacunarity
    )
    layers = core.generate_semantic_layers(base_structure, seed)
    
    # =========================================================================
    # Step 2: Run GCO Pipeline (Erosion + Feature Detection)
    # =========================================================================
    print("[2/6] Running GCO pipeline (erosion + hydrology)...")
    context = gco.ClosureContext(layers=layers, seed=seed)
    operator = gco.GlobalClosureOperator(context)
    result = operator.run(enable_hydraulic_erosion=True)
    
    # Get eroded terrain and features
    structure = layers['Structure']  # Now eroded by GCO
    overlay = result.overlay
    
    # Clamp structure for mesh generation
    structure = np.clip(structure, 0.0, 1.0)
    
    # Count features
    rivers = sum(1 for f in result.committed_features if f.type == 'river')
    lakes = sum(1 for f in result.committed_features if f.type == 'lake')
    forests = sum(1 for f in result.committed_features if f.type == 'forest')
    print(f"      Committed: {rivers} rivers, {lakes} lakes, {forests} forests")
    
    # =========================================================================
    # Step 3: Generate Biome Classification
    # =========================================================================
    print("[3/6] Classifying biomes...")
    classifier = biomes.BiomeClassifier(n_biomes=6, seed=seed)
    biome_map = classifier.fit_predict(layers)
    classifier.print_biome_summary()
    
    # =========================================================================
    # Step 4: Export Terrain Mesh
    # =========================================================================
    print("[4/6] Exporting terrain mesh...")
    
    # Versioned base name
    base_name = f"landscape_{inscription}_v{version}"
    obj_path = os.path.join(OUTPUT_DIR, f"{base_name}.obj")
    mtl_filename = f"{base_name}.mtl"
    diffuse_filename = f"{base_name}_diffuse.png"
    water_mask_filename = f"{base_name}_water_mask.png"
    
    with open(obj_path, 'w') as f:
        f.write(f"# Neo Noise Landscape: {inscription} v{version}\n")
        f.write(f"# Size: {size}x{size}, Height Scale: {height_scale}\n")
        f.write(f"# Seed: {seed}\n")
        f.write(f"mtllib {mtl_filename}\n")
        f.write(f"o terrain_{inscription}\n")
        
        # Vertices and UVs
        for y in range(size):
            for x in range(size):
                h = structure[y, x] * height_scale
                px = x - size / 2
                pz = y - size / 2
                f.write(f"v {px:.4f} {h:.4f} {pz:.4f}\n")
                
                u = x / (size - 1)
                v = 1.0 - (y / (size - 1))
                f.write(f"vt {u:.4f} {v:.4f}\n")
        
        # Faces
        f.write(f"usemtl terrain_material\n")
        for y in range(size - 1):
            for x in range(size - 1):
                i00 = (y * size) + x + 1
                i10 = (y * size) + (x + 1) + 1
                i01 = ((y + 1) * size) + x + 1
                i11 = ((y + 1) * size) + (x + 1) + 1
                f.write(f"f {i00}/{i00} {i01}/{i01} {i11}/{i11} {i10}/{i10}\n")
    
    print(f"      Saved: {obj_path}")
    
    # =========================================================================
    # Step 4b: Export River Mesh (NEW)
    # =========================================================================
    river_obj_path = None
    if include_river_mesh:
        print("[4b/6] Generating river geometry...")
        river_verts, river_faces, river_uvs = generate_river_mesh(
            overlay, structure, height_scale, river_depth
        )
        
        if len(river_verts) > 0:
            river_obj_path = os.path.join(OUTPUT_DIR, f"{base_name}_rivers.obj")
            
            with open(river_obj_path, 'w') as f:
                f.write(f"# Neo Noise River Mesh: {inscription} v{version}\n")
                f.write(f"# River vertices: {len(river_verts)}, faces: {len(river_faces)}\n")
                f.write(f"mtllib {mtl_filename}\n")
                f.write(f"o rivers_{inscription}\n")
                
                # Write vertices
                for vx, vy, vz in river_verts:
                    f.write(f"v {vx:.4f} {vy:.4f} {vz:.4f}\n")
                
                # Write UVs
                for u, v in river_uvs:
                    f.write(f"vt {u:.4f} {v:.4f}\n")
                
                # Write faces
                f.write("usemtl river_material\n")
                for face in river_faces:
                    indices = " ".join(f"{i+1}/{i+1}" for i in face)
                    f.write(f"f {indices}\n")
            
            print(f"      Saved: {river_obj_path} ({len(river_verts)} verts, {len(river_faces)} faces)")
        else:
            print("      No river geometry generated (no rivers detected)")
    
    # =========================================================================
    # Step 4c: Export Water Plane (optional)
    # =========================================================================
    water_obj_path = None
    if include_water_plane:
        water_obj_path = os.path.join(OUTPUT_DIR, f"{base_name}_water.obj")
        water_height = sea_level * height_scale
        half_size = size / 2
        
        with open(water_obj_path, 'w') as f:
            f.write(f"# Neo Noise Water Plane: {inscription} v{version}\n")
            f.write(f"# Sea Level: {sea_level} -> Height: {water_height}\n")
            f.write(f"mtllib {mtl_filename}\n")
            f.write(f"o water_{inscription}\n")
            
            # Simple quad at sea level
            f.write(f"v {-half_size:.4f} {water_height:.4f} {-half_size:.4f}\n")
            f.write(f"v {half_size:.4f} {water_height:.4f} {-half_size:.4f}\n")
            f.write(f"v {half_size:.4f} {water_height:.4f} {half_size:.4f}\n")
            f.write(f"v {-half_size:.4f} {water_height:.4f} {half_size:.4f}\n")
            
            f.write("vt 0.0 0.0\n")
            f.write("vt 1.0 0.0\n")
            f.write("vt 1.0 1.0\n")
            f.write("vt 0.0 1.0\n")
            
            f.write("usemtl water_material\n")
            f.write("f 1/1 2/2 3/3 4/4\n")
        
        print(f"      Saved: {water_obj_path}")
    
    # =========================================================================
    # Step 5: Export Textures and Materials
    # =========================================================================
    print("[5/6] Generating textures...")
    
    # Generate biome texture with water overlay
    rgb = biomes.generate_biome_texture(biome_map, classifier, overlay)
    
    diffuse_path = os.path.join(OUTPUT_DIR, diffuse_filename)
    plt.imsave(diffuse_path, rgb)
    print(f"      Saved: {diffuse_path}")
    
    # Generate water mask (grayscale)
    # Rivers = 1.0, Lakes = 0.75, Everything else = 0.0
    water_mask = np.zeros_like(overlay)
    water_mask[overlay > 0.7] = 1.0  # Rivers
    water_mask[(overlay > 0.5) & (overlay <= 0.7)] = 0.75  # Lakes
    
    water_mask_path = os.path.join(OUTPUT_DIR, water_mask_filename)
    plt.imsave(water_mask_path, water_mask, cmap='gray')
    print(f"      Saved: {water_mask_path}")
    
    # Generate glyph overlay texture (NEW)
    glyph_overlay_path = None
    if include_glyph_overlay:
        glyph_overlay_filename = f"{base_name}_glyph.png"
        
        # Apply glyph watermarks on top of biome texture
        glyph_rgb = reading.generate_glyph_overlay(
            rgb, seed, cell_size=glyph_cell_size, alpha=glyph_alpha
        )
        
        glyph_overlay_path = os.path.join(OUTPUT_DIR, glyph_overlay_filename)
        plt.imsave(glyph_overlay_path, glyph_rgb)
        print(f"      Saved: {glyph_overlay_path} (glyph watermarks)")
    
    # Generate MTL file (updated with river material)
    mtl_path = os.path.join(OUTPUT_DIR, mtl_filename)
    with open(mtl_path, 'w') as f:
        f.write("# Neo Noise Landscape Materials\n\n")
        
        # Terrain material
        f.write("newmtl terrain_material\n")
        f.write("Ka 0.2 0.2 0.2\n")       # Ambient
        f.write("Kd 1.0 1.0 1.0\n")       # Diffuse (white, texture provides color)
        f.write("Ks 0.1 0.1 0.1\n")       # Low specular
        f.write("Ns 10.0\n")              # Low shininess
        f.write(f"map_Kd {diffuse_filename}\n")
        f.write("\n")
        
        # River channel material (darker, wet look)
        f.write("newmtl river_material\n")
        f.write("Ka 0.05 0.08 0.1\n")
        f.write("Kd 0.15 0.25 0.35\n")    # Dark blue-gray (wet rock/mud)
        f.write("Ks 0.4 0.4 0.4\n")       # Moderate specular (wet)
        f.write("Ns 50.0\n")              # Medium shininess
        f.write("\n")
        
        # Water plane material
        f.write("newmtl water_material\n")
        f.write("Ka 0.0 0.1 0.2\n")
        f.write("Kd 0.1 0.3 0.6\n")       # Blue diffuse
        f.write("Ks 0.8 0.8 0.8\n")       # High specular (reflective)
        f.write("Ns 100.0\n")             # Sharp highlights
        f.write("d 0.7\n")                # Transparency
        f.write("illum 2\n")
    
    print(f"      Saved: {mtl_path}")
    
    # =========================================================================
    # Step 6: Summary
    # =========================================================================
    print(f"\n[6/6] Export complete!")
    print(f"\n{'='*60}")
    print(f"EXPORT COMPLETE: {inscription} v{version}")
    print(f"{'='*60}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"\nFiles:")
    print(f"  - {base_name}.obj (terrain mesh)")
    print(f"  - {base_name}.mtl (materials)")
    if river_obj_path:
        print(f"  - {base_name}_rivers.obj (river geometry)")
    if include_water_plane:
        print(f"  - {base_name}_water.obj (water plane)")
    print(f"  - {diffuse_filename} (biome texture)")
    print(f"  - {water_mask_filename} (water mask)")
    print(f"\nTo import in Blender:")
    print(f"  File -> Import -> Wavefront (.obj)")
    print(f"  Select: {obj_path}")
    
    return {
        'terrain_obj': obj_path,
        'mtl': mtl_path,
        'river_obj': river_obj_path,
        'water_obj': water_obj_path,
        'diffuse': diffuse_path,
        'water_mask': water_mask_path,
        'seed': seed,
        'version': version
    }


def main():
    """Generate test landscapes for Blender validation."""
    
    # Get shared version for this batch
    version = get_next_version()
    
    # Test inscriptions - different terrain characters
    test_cases = [
        ("ARCHIPELAGO", 256, 0.30),   # Islands - higher sea level
        ("MOUNTAIN", 256, 0.20),      # Peaks - low sea level
        ("FOREST", 256, 0.25),        # Lush - moderate water
    ]
    
    for inscription, size, sea_level in test_cases:
        generate_landscape(
            inscription=inscription,
            size=size,
            height_scale=40.0,
            sea_level=sea_level,
            include_water_plane=True,
            include_river_mesh=True,
            river_depth=2.5,
            version=version  # Same version for batch
        )
    
    print("\n" + "="*60)
    print(f"ALL LANDSCAPES GENERATED! (Version {version})")
    print("="*60)


if __name__ == "__main__":
    main()
