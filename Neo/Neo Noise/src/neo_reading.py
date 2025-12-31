"""
Neo Reading Layer
Computes glyph affinity from committed terrain structure and generates glyph overlays.

The "Reading Layer" is the inverse of inscription: realized terrain → glyph identity.
Each coordinate has a latent glyph (from get_glyph_props), and this module visualizes
that substrate as watermarks in textures.
"""

import numpy as np
from typing import Dict, Tuple

# Import from core
try:
    from . import neo_noise_core as core
except ImportError:
    import neo_noise_core as core


# Glyph group colors (RGB, 0-1)
GLYPH_GROUP_COLORS = {
    'right': (0.9, 0.4, 0.2),      # Red-orange (B-group: action)
    'left': (0.2, 0.7, 0.8),       # Cyan (H-group: resistance)
    'cross': (0.3, 0.8, 0.3),      # Green (M-group: structure)
    'diagonal': (0.3, 0.4, 0.9),   # Blue (A-group: flow)
    'backslash': (0.8, 0.3, 0.7),  # Magenta (Forfeda: transform)
}


def get_glyph_at(seed: int, x: int, y: int) -> Tuple[str, int]:
    """
    Get the latent glyph type and magnitude at a coordinate.
    Wrapper around core.get_glyph_props().
    """
    return core.get_glyph_props(seed, x, y)


def generate_glyph_color_field(seed: int, width: int, height: int) -> np.ndarray:
    """
    Generate an RGB field where each pixel is colored by its latent glyph group.
    
    Args:
        seed: Inscription seed
        width, height: Field dimensions
        
    Returns:
        np.ndarray: Shape (height, width, 3) RGB image (0-1)
    """
    field = np.zeros((height, width, 3))
    
    for y in range(height):
        for x in range(width):
            glyph_type, magnitude = get_glyph_at(seed, x, y)
            color = GLYPH_GROUP_COLORS.get(glyph_type, (0.5, 0.5, 0.5))
            
            # Modulate brightness by magnitude (1-5)
            brightness = 0.6 + (magnitude / 5.0) * 0.4  # 0.6 to 1.0
            field[y, x] = [c * brightness for c in color]
    
    return field


def draw_glyph_mark(image: np.ndarray, cx: int, cy: int, 
                    glyph_type: str, magnitude: int, 
                    cell_size: int, color: Tuple[float, float, float],
                    alpha: float = 0.15):
    """
    Draw a simple glyph mark at position (cx, cy).
    
    Marks are simplified NeOgham strokes:
    - right: horizontal lines to the right of center
    - left: horizontal lines to the left of center
    - cross: horizontal lines through center
    - diagonal: forward slash lines
    - backslash: back slash lines
    """
    h, w, _ = image.shape
    half = cell_size // 2
    mark_len = cell_size // 3
    stroke_width = max(1, cell_size // 10)
    
    # Vertical stem (subtle)
    for dy in range(-half, half):
        py = cy + dy
        if 0 <= py < h and 0 <= cx < w:
            for s in range(-stroke_width//2, stroke_width//2 + 1):
                sx = cx + s
                if 0 <= sx < w:
                    _blend_pixel(image, py, sx, color, alpha * 0.5)
    
    # Draw marks based on glyph type and magnitude
    spacing = max(3, cell_size // 6)
    
    for i in range(magnitude):
        offset_y = -half + int((i + 1) * cell_size / (magnitude + 1))
        py = cy + offset_y
        
        if 0 <= py < h:
            if glyph_type == 'right':
                # Horizontal line to the right
                for dx in range(mark_len):
                    px = cx + dx
                    if 0 <= px < w:
                        _blend_pixel(image, py, px, color, alpha)
                        
            elif glyph_type == 'left':
                # Horizontal line to the left
                for dx in range(mark_len):
                    px = cx - dx
                    if 0 <= px < w:
                        _blend_pixel(image, py, px, color, alpha)
                        
            elif glyph_type == 'cross':
                # Horizontal line through center (both sides)
                for dx in range(-mark_len, mark_len + 1):
                    px = cx + dx
                    if 0 <= px < w:
                        _blend_pixel(image, py, px, color, alpha)
                        
            elif glyph_type == 'diagonal':
                # Forward slash
                for d in range(-mark_len, mark_len + 1):
                    px = cx + d
                    dpy = py - d  # Up and right
                    if 0 <= px < w and 0 <= dpy < h:
                        _blend_pixel(image, dpy, px, color, alpha)
                        
            elif glyph_type == 'backslash':
                # Back slash
                for d in range(-mark_len, mark_len + 1):
                    px = cx + d
                    dpy = py + d  # Down and right
                    if 0 <= px < w and 0 <= dpy < h:
                        _blend_pixel(image, dpy, px, color, alpha)


def _blend_pixel(image: np.ndarray, y: int, x: int, 
                 color: Tuple[float, float, float], alpha: float):
    """Alpha-blend a color onto the image at position (y, x)."""
    for c in range(3):
        image[y, x, c] = image[y, x, c] * (1 - alpha) + color[c] * alpha


def generate_glyph_overlay(base_texture: np.ndarray, seed: int,
                           cell_size: int = 16, alpha: float = 0.12) -> np.ndarray:
    """
    Generate a glyph watermark overlay on top of a base texture.
    
    Samples the latent glyph grid at cell_size intervals and draws
    simplified glyph marks as subtle watermarks.
    
    Args:
        base_texture: RGB texture to overlay on (height, width, 3)
        seed: Inscription seed for latent glyph lookup
        cell_size: Size of each glyph cell in pixels
        alpha: Watermark opacity (0.05-0.20 recommended)
        
    Returns:
        np.ndarray: RGB image with glyph watermarks
    """
    result = base_texture.copy()
    h, w, _ = result.shape
    
    # Sample grid
    for cy in range(cell_size // 2, h, cell_size):
        for cx in range(cell_size // 2, w, cell_size):
            # Get latent glyph at this cell center
            # Map pixel coords to glyph grid (coarser sampling)
            gx = cx // 4  # Scale to match noise generation
            gy = cy // 4
            
            glyph_type, magnitude = get_glyph_at(seed, gx, gy)
            color = GLYPH_GROUP_COLORS.get(glyph_type, (0.5, 0.5, 0.5))
            
            draw_glyph_mark(result, cx, cy, glyph_type, magnitude, 
                           cell_size, color, alpha)
    
    return np.clip(result, 0.0, 1.0)


def generate_debug_glyph_grid(seed: int, width: int, height: int,
                               cell_size: int = 8) -> np.ndarray:
    """
    Generate a debug visualization showing the glyph grid.
    Each cell is colored by glyph type with magnitude as brightness.
    
    Args:
        seed: Inscription seed
        width, height: Output dimensions
        cell_size: Size of each grid cell
        
    Returns:
        np.ndarray: RGB image (height, width, 3)
    """
    result = np.zeros((height, width, 3))
    
    for cy in range(0, height, cell_size):
        for cx in range(0, width, cell_size):
            # Sample at cell center
            gx = (cx + cell_size // 2) // 4
            gy = (cy + cell_size // 2) // 4
            
            glyph_type, magnitude = get_glyph_at(seed, gx, gy)
            color = GLYPH_GROUP_COLORS.get(glyph_type, (0.5, 0.5, 0.5))
            
            # Brightness by magnitude
            brightness = 0.5 + (magnitude / 5.0) * 0.5
            
            # Fill cell
            for dy in range(min(cell_size, height - cy)):
                for dx in range(min(cell_size, width - cx)):
                    result[cy + dy, cx + dx] = [c * brightness for c in color]
    
    return result


# Quick test
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    print("Testing Neo Reading Layer...")
    
    # Generate a test biome texture first
    base_field, seed = core.generate_field("FOREST", 256, 256, normalize=True)
    
    # Create a simple color base  
    base_texture = np.zeros((256, 256, 3))
    base_texture[:, :, 0] = base_field * 0.3 + 0.2  # R
    base_texture[:, :, 1] = base_field * 0.5 + 0.3  # G
    base_texture[:, :, 2] = base_field * 0.2 + 0.1  # B
    
    # Generate glyph overlay
    print("Generating glyph overlay...")
    overlay = generate_glyph_overlay(base_texture, seed, cell_size=16, alpha=0.15)
    
    # Generate debug grid
    print("Generating debug grid...")
    debug_grid = generate_debug_glyph_grid(seed, 256, 256, cell_size=8)
    
    # Visualize
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    axes[0].imshow(base_texture)
    axes[0].set_title("Base Texture")
    axes[0].axis('off')
    
    axes[1].imshow(overlay)
    axes[1].set_title("With Glyph Watermarks")
    axes[1].axis('off')
    
    axes[2].imshow(debug_grid)
    axes[2].set_title("Debug Glyph Grid")
    axes[2].axis('off')
    
    plt.tight_layout()
    plt.savefig("../samples/glyph_reading_test.png")
    print("Saved: ../samples/glyph_reading_test.png")
