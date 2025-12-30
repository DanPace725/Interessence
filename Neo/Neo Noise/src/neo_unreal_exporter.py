"""
Neo Unreal Exporter
Exports Neo Noise world data in formats compatible with Unreal Engine 5 Landscape.

Supports UE5.x (tested with 5.5.4 and 5.7)

Output Formats:
- Heightmap: 16-bit grayscale PNG
- Splatmap: 8-bit RGB PNG (layer weights)
- Water Mask: 8-bit grayscale PNG
- Metadata: JSON with import settings
"""

import numpy as np
from PIL import Image
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict

# UE5 recommended landscape sizes (single component)
# These avoid stretching and component alignment issues
UE5_VALID_SIZES = [127, 253, 505, 1009, 2017, 4033]


@dataclass
class UnrealExportConfig:
    """Configuration for Unreal export."""
    target_size: int = 1009  # Default to 1009x1009
    z_scale: float = 100.0   # Vertical scale multiplier in UE5
    
    # Layer mapping: which biome IDs map to which splatmap channel
    # R, G, B, A (if using RGBA splatmap)
    layer_mapping: Dict[str, List[int]] = None
    
    def __post_init__(self):
        if self.layer_mapping is None:
            # Default: Group 12 biomes into 3 channels
            # R = Ground (Ocean, Coast, Grassland, Savanna)
            # G = Rock (Alpine, Snow Peaks, Tundra, Taiga)
            # B = Organic (Forest, Rainforest, Desert, Deep Ocean)
            self.layer_mapping = {
                "Ground": [1, 2, 4, 5],      # Ocean, Coast, Savanna, Grassland
                "Rock": [9, 10, 11, 8],       # Tundra, Alpine, Snow, Taiga
                "Organic": [3, 6, 7, 0]       # Desert, Forest, Rainforest, Deep Ocean
            }


def get_nearest_valid_size(size: int) -> int:
    """Find the nearest UE5-valid landscape size."""
    return min(UE5_VALID_SIZES, key=lambda x: abs(x - size))


def export_heightmap(elevation: np.ndarray, 
                     output_path: str, 
                     target_size: int = 1009) -> str:
    """
    Export elevation data as 16-bit PNG heightmap for UE5 Landscape.
    
    Args:
        elevation: 2D numpy array with values 0.0-1.0
        output_path: Output file path (should end in .png)
        target_size: Target resolution (will use nearest valid UE5 size)
        
    Returns:
        Path to exported file
    """
    # Validate and adjust target size
    valid_size = get_nearest_valid_size(target_size)
    if valid_size != target_size:
        print(f"  Adjusted size {target_size} → {valid_size} (UE5 compatible)")
    
    # Resize if needed using PIL for high-quality interpolation
    h, w = elevation.shape
    if h != valid_size or w != valid_size:
        # Convert to PIL Image for resizing
        # First normalize to 0-65535 for 16-bit
        img_data = (np.clip(elevation, 0, 1) * 65535).astype(np.uint16)
        img = Image.fromarray(img_data, mode='I;16')
        img = img.resize((valid_size, valid_size), Image.Resampling.BICUBIC)
        img_data = np.array(img)
    else:
        img_data = (np.clip(elevation, 0, 1) * 65535).astype(np.uint16)
    
    # Save as 16-bit PNG
    img = Image.fromarray(img_data, mode='I;16')
    img.save(output_path, format='PNG')
    
    print(f"  Heightmap: {output_path} ({valid_size}x{valid_size}, 16-bit)")
    return output_path


def export_splatmap(biome_ids: np.ndarray,
                    output_path: str,
                    config: UnrealExportConfig = None) -> str:
    """
    Export biome weights as RGB splatmap for UE5 landscape layers.
    
    Each channel (R, G, B) represents weight for a layer group.
    Values are normalized so R+G+B ≈ 255 at each pixel.
    
    Args:
        biome_ids: 2D numpy array of biome IDs (0-11)
        output_path: Output file path
        config: Export configuration with layer mapping
        
    Returns:
        Path to exported file
    """
    if config is None:
        config = UnrealExportConfig()
    
    h, w = biome_ids.shape
    target_size = get_nearest_valid_size(config.target_size)
    
    # Create RGB splatmap
    splatmap = np.zeros((h, w, 3), dtype=np.uint8)
    
    # Map biomes to channels
    mapping = config.layer_mapping
    for channel_idx, (layer_name, biome_list) in enumerate(mapping.items()):
        if channel_idx >= 3:
            break  # RGB only
        for biome_id in biome_list:
            mask = biome_ids == biome_id
            splatmap[mask, channel_idx] = 255
    
    # Resize if needed
    if h != target_size or w != target_size:
        img = Image.fromarray(splatmap, mode='RGB')
        img = img.resize((target_size, target_size), Image.Resampling.NEAREST)
        splatmap = np.array(img)
    
    # Save
    img = Image.fromarray(splatmap, mode='RGB')
    img.save(output_path, format='PNG')
    
    print(f"  Splatmap: {output_path} ({target_size}x{target_size}, RGB)")
    print(f"    Layers: R={list(mapping.keys())[0]}, G={list(mapping.keys())[1]}, B={list(mapping.keys())[2]}")
    return output_path


def export_water_mask(overlay: np.ndarray,
                      output_path: str,
                      target_size: int = 1009,
                      river_threshold: float = 0.7,
                      lake_threshold: float = 0.5) -> str:
    """
    Export rivers and lakes as binary mask.
    
    Args:
        overlay: GCO overlay from ClosureResult
        output_path: Output file path
        target_size: Target resolution
        river_threshold: Overlay value threshold for rivers
        lake_threshold: Overlay value threshold for lakes
        
    Returns:
        Path to exported file
    """
    valid_size = get_nearest_valid_size(target_size)
    h, w = overlay.shape
    
    # Create binary mask
    # Rivers = overlay > 0.7, Lakes = 0.5-0.7
    water_mask = np.zeros((h, w), dtype=np.uint8)
    is_river = overlay > river_threshold
    is_lake = (overlay > lake_threshold) & (overlay <= river_threshold)
    
    water_mask[is_river] = 255  # Full white for rivers
    water_mask[is_lake] = 200   # Slightly dimmer for lakes (can differentiate)
    
    # Resize if needed
    if h != valid_size or w != valid_size:
        img = Image.fromarray(water_mask, mode='L')
        img = img.resize((valid_size, valid_size), Image.Resampling.NEAREST)
        water_mask = np.array(img)
    
    # Save
    img = Image.fromarray(water_mask, mode='L')
    img.save(output_path, format='PNG')
    
    river_pixels = np.sum(water_mask == 255)
    lake_pixels = np.sum(water_mask == 200)
    print(f"  Water Mask: {output_path} ({valid_size}x{valid_size})")
    print(f"    Rivers: {river_pixels} px, Lakes: {lake_pixels} px")
    return output_path


def export_metadata(inscription: str,
                    output_path: str,
                    config: UnrealExportConfig,
                    seed: int = 0,
                    additional_data: Dict = None) -> str:
    """
    Export JSON metadata for import reference.
    
    Args:
        inscription: World seed string
        output_path: Output JSON file path
        config: Export configuration
        seed: Numeric seed
        additional_data: Any extra data to include
        
    Returns:
        Path to exported file
    """
    valid_size = get_nearest_valid_size(config.target_size)
    
    metadata = {
        "neo_noise_export": {
            "version": "1.0",
            "inscription": inscription,
            "seed": seed,
        },
        "unreal_settings": {
            "heightmap_size": valid_size,
            "z_scale_recommended": config.z_scale,
            "compatible_ue_versions": ["5.5", "5.6", "5.7"],
        },
        "layer_mapping": {
            "splatmap_format": "RGB",
            "channels": {
                "R": list(config.layer_mapping.keys())[0],
                "G": list(config.layer_mapping.keys())[1],
                "B": list(config.layer_mapping.keys())[2],
            },
            "import_settings": {
                "sRGB": False,
                "Compression": "Masks"
            }
        },
        "files": {
            "heightmap": "heightmap.png",
            "splatmap": "splatmap.png",
            "water_mask": "water_mask.png"
        }
    }
    
    if additional_data:
        metadata["custom"] = additional_data
    
    with open(output_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"  Metadata: {output_path}")
    return output_path


def export_all(elevation: np.ndarray,
               biome_ids: np.ndarray,
               overlay: np.ndarray,
               output_dir: str,
               inscription: str = "WORLD",
               seed: int = 0,
               config: UnrealExportConfig = None) -> Dict[str, str]:
    """
    Export all assets needed for UE5 import.
    
    Args:
        elevation: Heightmap data (0-1)
        biome_ids: Biome classification array
        overlay: GCO water overlay
        output_dir: Directory to write files
        inscription: World name
        seed: World seed
        config: Export configuration
        
    Returns:
        Dict mapping asset type to file path
    """
    if config is None:
        config = UnrealExportConfig()
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\nExporting Neo Noise world '{inscription}' for Unreal Engine...")
    print(f"Output: {output_dir}")
    print("-" * 50)
    
    paths = {}
    
    # Export each asset
    paths['heightmap'] = export_heightmap(
        elevation, 
        os.path.join(output_dir, "heightmap.png"),
        config.target_size
    )
    
    paths['splatmap'] = export_splatmap(
        biome_ids,
        os.path.join(output_dir, "splatmap.png"),
        config
    )
    
    paths['water_mask'] = export_water_mask(
        overlay,
        os.path.join(output_dir, "water_mask.png"),
        config.target_size
    )
    
    paths['metadata'] = export_metadata(
        inscription,
        os.path.join(output_dir, "metadata.json"),
        config,
        seed
    )
    
    print("-" * 50)
    print(f"Export complete! {len(paths)} files written.")
    print("\nNext: Open UE5, create Landscape from heightmap.png")
    
    return paths


# Quick test when run directly
if __name__ == "__main__":
    print("Neo Unreal Exporter - Test Mode")
    print("=" * 50)
    
    # Create test data
    size = 256
    test_elevation = np.random.rand(size, size) * 0.5 + 0.25
    test_biome_ids = np.random.randint(0, 12, (size, size))
    test_overlay = np.zeros((size, size))
    test_overlay[100:150, 50:200] = 0.8  # Fake river
    
    # Export
    config = UnrealExportConfig(target_size=505)  # Smaller for test
    export_all(
        test_elevation,
        test_biome_ids,
        test_overlay,
        output_dir="samples/unreal_test",
        inscription="TEST",
        config=config
    )
