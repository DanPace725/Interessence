"""
Export for Unreal - Demo Script
Generates Neo Noise world and exports for UE5 Landscape import.

Usage:
    python export_for_unreal.py [INSCRIPTION] [--size SIZE]

Example:
    python export_for_unreal.py PANGAEA --size 1009
"""

import sys
import os
import argparse

# Add src/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import neo_noise_core as core
import neo_world as world
import neo_gco as gco
import neo_unreal_exporter as ue_export

# Default output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "samples", "unreal_export")


def generate_and_export(inscription: str, 
                        target_size: int = 1009,
                        run_gco: bool = True,
                        output_dir: str = None):
    """
    Generate a Neo Noise world and export for Unreal Engine.
    
    Args:
        inscription: World seed string (e.g., "PANGAEA")
        target_size: Target UE5 landscape size
        run_gco: Whether to run GCO for water features
        output_dir: Output directory (default: samples/unreal_export/<inscription>)
    """
    if output_dir is None:
        output_dir = os.path.join(OUTPUT_DIR, inscription)
    
    print("=" * 60)
    print(f"Neo Noise -> Unreal Engine Export")
    print(f"World: '{inscription}'")
    print(f"Target Size: {target_size}")
    print("=" * 60)
    
    # Step 1: Generate continental map
    print("\n[1/4] Generating continental elevation and climate...")
    
    # Use square aspect for UE5 landscape
    world_map = world.generate_continental_map(
        inscription, 
        width=target_size, 
        height=target_size,
        semantic_bias_strength=0.4
    )
    
    # Step 2: Create semantic layers
    print("[2/4] Deriving semantic layers...")
    layers = core.generate_semantic_layers(world_map.elevation, world_map.seed)
    layers['Vitality'] = world_map.moisture  # Override with moisture
    
    # Step 3: Run GCO for water features
    overlay = np.zeros_like(world_map.elevation)
    
    if run_gco:
        print("[3/4] Running GCO for rivers and lakes...")
        ctx = gco.ClosureContext(layers=layers, seed=world_map.seed)
        operator = gco.GlobalClosureOperator(ctx)
        result = operator.run(enable_hydraulic_erosion=False)  # Skip erosion for speed
        overlay = result.overlay
        
        # Stats
        rivers = sum(1 for f in result.committed_features if f.type == 'river')
        lakes = sum(1 for f in result.committed_features if f.type == 'lake')
        print(f"    Found {rivers} rivers, {lakes} lakes")
    else:
        print("[3/4] Skipping GCO (water features disabled)")
    
    # Step 4: Export for Unreal
    print("[4/4] Exporting for Unreal Engine...")
    
    config = ue_export.UnrealExportConfig(
        target_size=target_size,
        z_scale=100.0
    )
    
    paths = ue_export.export_all(
        elevation=world_map.elevation,
        biome_ids=world_map.biome_ids,
        overlay=overlay,
        output_dir=output_dir,
        inscription=inscription,
        seed=world_map.seed,
        config=config
    )
    
    # Print import instructions
    print("\n" + "=" * 60)
    print("UNREAL ENGINE IMPORT INSTRUCTIONS")
    print("=" * 60)
    print(f"""
1. HEIGHTMAP IMPORT:
   - Open UE5 -> Landscape Mode -> Create New
   - Enable "Import from File"
   - Select: {paths['heightmap']}
   - Set Z Scale: 100 (adjust for desired height)

2. MATERIAL LAYERS:
   - Import {paths['splatmap']}
   - Settings: sRGB = OFF, Compression = Masks
   - Create Landscape Material with LandscapeLayerBlend
   - R = Ground, G = Rock, B = Organic

3. WATER FEATURES:
   - Import {paths['water_mask']}
   - Use as mask in Water Material
   - Or spawn Water Body actors at white pixels

See: {paths['metadata']} for full settings
""")
    
    return paths


def main():
    parser = argparse.ArgumentParser(
        description="Generate Neo Noise world and export for Unreal Engine"
    )
    parser.add_argument(
        "inscription", 
        nargs="?",
        default="INTERESSENCE",
        help="World seed string (default: INTERESSENCE)"
    )
    parser.add_argument(
        "--size", 
        type=int, 
        default=1009,
        help="Target landscape size (default: 1009)"
    )
    parser.add_argument(
        "--no-water",
        action="store_true",
        help="Skip water feature generation"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    generate_and_export(
        inscription=args.inscription,
        target_size=args.size,
        run_gco=not args.no_water,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
