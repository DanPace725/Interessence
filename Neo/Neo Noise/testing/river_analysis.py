"""
River Feasibility Diagnostic
Analyzes terrain to determine if realistic river networks are possible.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import neo_noise_core as core

OUTPUT_DIR = "samples/river_analysis"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def trace_max_length_river(heightmap, start_x, start_y, max_steps=1000):
    """
    Trace a river with NO artificial constraints to find maximum possible length.
    Only stops at: edge of map, true local minima, or max_steps.
    """
    h, w = heightmap.shape
    gy, gx = np.gradient(heightmap)
    
    path = [(start_x, start_y)]
    px, py = float(start_x), float(start_y)
    vx, vy = 0.0, 0.0
    inertia = 0.8  # Higher inertia to cross flat areas
    gravity = 0.3
    
    for step in range(max_steps):
        ix, iy = int(px), int(py)
        
        if not (0 <= ix < w and 0 <= iy < h):
            break
            
        # Get gradient (downhill direction)
        dx = -gx[iy, ix]
        dy = -gy[iy, ix]
        
        mag = np.sqrt(dx*dx + dy*dy)
        
        if mag > 1e-6:
            dx /= mag
            dy /= mag
        else:
            # Flat area - try random direction or use momentum
            speed = np.sqrt(vx*vx + vy*vy)
            if speed < 0.05:
                break  # True local minimum
        
        # Update velocity and position
        vx = vx * inertia + dx * gravity
        vy = vy * inertia + dy * gravity
        px += vx
        py += vy
        
        nx, ny = int(px), int(py)
        if (nx, ny) != (ix, iy):
            if not (0 <= nx < w and 0 <= ny < h):
                break
            # Don't check for loops - allow rivers to trace freely
            path.append((nx, ny))
    
    return path


def analyze_terrain_for_rivers(inscription, size=256):
    """
    Comprehensive analysis of terrain river potential.
    """
    print(f"\n{'='*60}")
    print(f"RIVER FEASIBILITY ANALYSIS: {inscription}")
    print(f"{'='*60}")
    
    # Generate terrain
    field, seed = core.generate_field(inscription, size, size, normalize=True, octaves=4)
    
    # 1. GRADIENT ANALYSIS
    gy, gx = np.gradient(field)
    gradient_mag = np.sqrt(gx**2 + gy**2)
    
    flat_threshold = 0.001
    flat_pixels = np.sum(gradient_mag < flat_threshold)
    flat_pct = flat_pixels / (size * size) * 100
    
    print(f"\n1. GRADIENT ANALYSIS:")
    print(f"   Mean gradient magnitude: {np.mean(gradient_mag):.4f}")
    print(f"   Max gradient magnitude:  {np.max(gradient_mag):.4f}")
    print(f"   Flat pixels (<{flat_threshold}):  {flat_pct:.1f}%")
    
    # 2. ELEVATION RANGE
    print(f"\n2. ELEVATION RANGE:")
    print(f"   Min elevation: {field.min():.3f}")
    print(f"   Max elevation: {field.max():.3f}")
    print(f"   Range: {field.max() - field.min():.3f}")
    
    # 3. FIND BEST RIVER SOURCES (high points)
    # Look for local maxima
    from scipy.ndimage import maximum_filter
    local_max = maximum_filter(field, size=20)
    peaks = (field == local_max) & (field > 0.7)  # High elevation peaks
    peak_coords = np.argwhere(peaks)
    
    print(f"\n3. POTENTIAL RIVER SOURCES:")
    print(f"   Found {len(peak_coords)} high points (>0.7 elevation)")
    
    # 4. TRACE LONGEST POSSIBLE RIVERS
    print(f"\n4. TRACING UNRESTRICTED RIVERS:")
    
    river_lengths = []
    rivers = []
    
    # Sample up to 10 high points
    sample_peaks = peak_coords[:10] if len(peak_coords) > 10 else peak_coords
    
    for i, (py, px) in enumerate(sample_peaks):
        path = trace_max_length_river(field, px, py, max_steps=1000)
        river_lengths.append(len(path))
        rivers.append(path)
        
        start_h = field[py, px]
        end_y, end_x = path[-1][1], path[-1][0]
        end_h = field[end_y, end_x] if 0 <= end_y < size and 0 <= end_x < size else 0
        
        print(f"   River {i+1}: {len(path)} pixels, {start_h:.2f} -> {end_h:.2f} elevation")
    
    if river_lengths:
        print(f"\n   => LONGEST RIVER: {max(river_lengths)} pixels")
        print(f"   => AVERAGE RIVER: {np.mean(river_lengths):.0f} pixels")
    
    # 5. VISUALIZATION
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    fig.suptitle(f"River Feasibility: {inscription}", fontsize=14, color='white')
    fig.patch.set_facecolor('#0f172a')
    
    # Terrain
    ax = axes[0, 0]
    ax.imshow(field, cmap='terrain', interpolation='bicubic')
    ax.set_title('Terrain (Elevation)', color='white')
    ax.axis('off')
    
    # Gradient magnitude
    ax = axes[0, 1]
    ax.imshow(gradient_mag, cmap='viridis', interpolation='bicubic')
    ax.set_title(f'Gradient Magnitude ({flat_pct:.0f}% flat)', color='white')
    ax.axis('off')
    
    # Rivers overlaid on terrain
    ax = axes[1, 0]
    ax.imshow(field, cmap='terrain', interpolation='bicubic')
    colors = plt.cm.cool(np.linspace(0, 1, len(rivers)))
    for i, path in enumerate(rivers):
        if len(path) > 1:
            xs = [p[0] for p in path]
            ys = [p[1] for p in path]
            ax.plot(xs, ys, color=colors[i], linewidth=2, alpha=0.8)
    ax.set_title(f'Traced Rivers (max {max(river_lengths) if river_lengths else 0} px)', color='white')
    ax.axis('off')
    
    # Flow accumulation simulation (simple)
    ax = axes[1, 1]
    # Create flow accumulation by counting how many paths cross each pixel
    accumulation = np.zeros_like(field)
    for path in rivers:
        for x, y in path:
            if 0 <= y < size and 0 <= x < size:
                accumulation[y, x] += 1
    ax.imshow(np.log1p(accumulation), cmap='Blues', interpolation='nearest')
    ax.set_title('River Path Density', color='white')
    ax.axis('off')
    
    plt.tight_layout()
    filename = os.path.join(OUTPUT_DIR, f"river_analysis_{inscription}.png")
    plt.savefig(filename, facecolor=fig.get_facecolor(), dpi=120)
    plt.close()
    print(f"\nSaved: {filename}")
    
    return {
        'flat_pct': flat_pct,
        'max_river_length': max(river_lengths) if river_lengths else 0,
        'avg_river_length': np.mean(river_lengths) if river_lengths else 0,
        'num_sources': len(peak_coords)
    }


def main():
    # Test multiple inscriptions
    inscriptions = ["RIVER", "MOUNTAIN", "FIRE", "INTERESSENCE"]
    
    results = {}
    for word in inscriptions:
        results[word] = analyze_terrain_for_rivers(word)
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"{'Word':<15} {'Flat%':>8} {'MaxLen':>8} {'AvgLen':>8} {'Sources':>8}")
    print("-"*60)
    for word, r in results.items():
        print(f"{word:<15} {r['flat_pct']:>7.1f}% {r['max_river_length']:>8} {r['avg_river_length']:>8.0f} {r['num_sources']:>8}")


if __name__ == "__main__":
    main()
