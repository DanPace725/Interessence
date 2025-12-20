"""
NEO Noise Core Logic
Pure Python implementation of the Neo Noise generation algorithm.
Decoupled from visualization for testing and integration.
"""

import numpy as np

# Refined Glyph Definitions (Unified Alphabet)
NEO_GLYPHS = {
    # B-Group (Right)
    'B': {'type': 'right', 'mag': 1}, 'L': {'type': 'right', 'mag': 2},
    'F': {'type': 'right', 'mag': 3}, 'S': {'type': 'right', 'mag': 4},
    'P': {'type': 'right', 'mag': 5},
    
    # H-Group (Left)
    'H': {'type': 'left', 'mag': 1}, 'D': {'type': 'left', 'mag': 2},
    'T': {'type': 'left', 'mag': 3}, 'C': {'type': 'left', 'mag': 4},
    'W': {'type': 'left', 'mag': 5},
    
    # M-Group (Cross)
    'M': {'type': 'cross', 'mag': 1}, 'G': {'type': 'cross', 'mag': 2},
    'N': {'type': 'cross', 'mag': 3}, 'Z': {'type': 'cross', 'mag': 4},
    'R': {'type': 'cross', 'mag': 5},
    
    # A-Group (Diagonal)
    'A': {'type': 'diagonal', 'mag': 1}, 'O': {'type': 'diagonal', 'mag': 2},
    'U': {'type': 'diagonal', 'mag': 3}, 'E': {'type': 'diagonal', 'mag': 4},
    'I': {'type': 'diagonal', 'mag': 5},
    
    # Forfeda (Backslash)
    'Q': {'type': 'backslash', 'mag': 1}, 'V': {'type': 'backslash', 'mag': 2},
    'X': {'type': 'backslash', 'mag': 3}, 'Y': {'type': 'backslash', 'mag': 4},
    'J': {'type': 'backslash', 'mag': 5},
}

# Interaction Logic (The "Physics")
TYPE_INTERACTIONS = {
    ('left', 'right'): -1.5,   # Opposition (Void)
    ('right', 'left'): -1.5,
    ('left', 'left'): 2.0,     # Reinforce
    ('right', 'right'): 2.0,
    ('cross', 'cross'): 3.0,   # Anchor (High Structure)
    ('cross', 'diagonal'): 4.0,# Crystallize
    ('cross', 'backslash'): 5.0, # Fracture
    ('diagonal', 'diagonal'): 1.5, # Stream
    ('diagonal', 'backslash'): 3.5, # Turbulence
    ('backslash', 'backslash'): 6.0, # Phase Shift
}

def get_glyph_props(inscription_seed, x, y):
    """
    Deterministically retrieve the latent glyph at (x,y) based on the seed.
    """
    # Complex hash to avoid simple repeating patterns
    h = (x * 374761393 ^ y * 668265263 ^ inscription_seed)
    
    # Map hash to properties
    types = ['left', 'right', 'cross', 'diagonal', 'backslash']
    g_type = types[h % 5]
    g_mag = ((h >> 8) % 5) + 1
    
    return g_type, g_mag

def calculate_local_intensity(seed, x, y):
    """
    Calculate the semantic intensity at (x,y) by observing the neighborhood.
    """
    # 3x3 Neighborhood
    neighbors = []
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            # We treat coordinates as infinite/wrapping or just procedural
            gx, gy = x + dx, y + dy
            neighbors.append(get_glyph_props(seed, gx, gy))
            
    score = 0
    count = 0
    
    # Pairwise interaction of all neighbors
    for i in range(len(neighbors)):
        for j in range(i + 1, len(neighbors)):
            t1, m1 = neighbors[i]
            t2, m2 = neighbors[j]
            
            # 1. Base Type Interaction
            base = TYPE_INTERACTIONS.get((t1, t2))
            if base is None:
                base = TYPE_INTERACTIONS.get((t2, t1), 0.5)
            
            # 2. Magnitude Modulation
            delta = abs(m1 - m2)
            
            score += base + (delta * 0.25)
            count += 1
            
    return score / count

def _bilinear_upsample(grid, target_h, target_w):
    """
    Simple bilinear upsampling for numpy grids.
    """
    h, w = grid.shape
    # If same size, return
    if h == target_h and w == target_w:
        return grid
        
    # Create coordinate grid
    x = np.linspace(0, w - 1, target_w)
    y = np.linspace(0, h - 1, target_h)
    
    # Get floor and ceil indices
    x0 = np.floor(x).astype(int)
    x1 = np.minimum(x0 + 1, w - 1)
    y0 = np.floor(y).astype(int)
    y1 = np.minimum(y0 + 1, h - 1)
    
    # Calculate weights
    wx = x - x0
    wy = y - y0
    
    # Reshape weights for broadcasting
    # We want result[r, c]
    # We can do this separately for X and Y to save memory (two passes) or broadcasting
    
    # Interpolate along X first for each Row
    # Better: Use simple loop if size is small, or broadcasting
    # Broadcast:
    # We need to construct the full 2D indices. 
    # This might be slow if we do full meshgrid.
    # Check scipy availability? No, sticking to numpy.
    
    # Optimization: 1D interpolation twice
    # 1. Resize Rows (Width)
    tmp = np.zeros((h, target_w))
    for r in range(h):
        row = grid[r, :]
        tmp[r, :] = row[x0] * (1 - wx) + row[x1] * wx
        
    # 2. Resize Cols (Height)
    result = np.zeros((target_h, target_w))
    for c in range(target_w):
        col = tmp[:, c]
        result[:, c] = col[y0] * (1 - wy) + col[y1] * wy
        
    return result

def generate_field(inscription, width=100, height=100, normalize=True, octaves=4, persistence=0.5, lacunarity=2.0):
    """
    Generate the full 2D noise field using Multi-Scale Fractal Noise.
    
    Args:
        inscription: Seed string.
        width, height: Output resolution.
        normalize: Whether to normalize output 0-1.
        octaves: Number of layers of detail.
        persistence: How much amplitude decreases per octave (0.5 = half).
        lacunarity: How much frequency increases per octave (2.0 = double).
    """
    # Create deterministic seed from string
    if isinstance(inscription, str):
        base_seed = hash(inscription.upper()) & 0xFFFFFFFF
    else:
        base_seed = int(inscription)
    
    final_field = np.zeros((height, width))
    total_amplitude = 0
    amplitude = 1.0
    
    # Determine base scale
    # We want the HIGHEST frequency octave to match the pixel grid? 
    # Or start coarse and go up.
    # Standard Perlin: Octave 0 = Coarse.
    
    # We need to determine the size of Octave 0.
    # If Octaves=4, and Octave 3 is 1:1, then:
    # Oct 3: 256x256
    # Oct 2: 128x128
    # Oct 1: 64x64
    # Oct 0: 32x32
    
    # Calculate base size
    # current_w = width // (lacunarity ** (octaves - 1))
    # current_h = height // (lacunarity ** (octaves - 1))
    
    # Floating point size? No, needs to be grid.
    if octaves < 1: octaves = 1
    
    freq = 1.0
    
    # Generate Octaves
    # We generate from Coarse to Fine
    
    # Start freq so that largest octave IS coarse?
    # Actually, let's just loop.
    # Typically, we sum: Noise(x*freq) * amp.
    # Since our 'Noise' is generating a grid of size (w,h), 
    # we simulate frequency by changing the grid size and upscaling.
    
    # Start with the smallest grid (Coarse)
    # Divider for the first octave
    divider = lacunarity ** (octaves - 1)
    
    current_w = max(4, int(width / divider))
    current_h = max(4, int(height / divider))
    
    for i in range(octaves):
        # Unique seed per octave to prevent correlation
        octave_seed = base_seed + (i * 54321)
        
        # Generate raw noise at this lower resolution
        layer = np.zeros((current_h, current_w))
        for y in range(current_h):
            for x in range(current_w):
                layer[y, x] = calculate_local_intensity(octave_seed, x, y)
                
        # Upscale to target resolution
        if current_w != width or current_h != height:
            layer = _bilinear_upsample(layer, height, width)
        
        # Accumulate
        final_field += layer * amplitude
        total_amplitude += amplitude
        
        # Prepare for next octave
        amplitude *= persistence
        current_w = int(min(width, current_w * lacunarity))
        current_h = int(min(height, current_h * lacunarity))
        
        # Correction for rounding or max cap
        if i == octaves - 2: # Ensure last one is exact
            current_w = width
            current_h = height
    
    field = final_field
    
    # FIX: Resolution-Aware Normalization
    # Bounds logic might need update for fractal sum.
    # Theoretical Min/Max scales with sum(amplitudes)
    THEORETICAL_MIN = -1.5 * total_amplitude
    THEORETICAL_MAX = 7.5 * total_amplitude
    
    if normalize:
        field = (field - THEORETICAL_MIN) / (THEORETICAL_MAX - THEORETICAL_MIN)
        field = np.clip(field, 0.0, 1.0)
            
    return field, base_seed

def evolve_field(field, steps=1, decay=0.01, diffusion=0.1, feed_rate=0.005):
    """
    Simulate temporal evolution of the field.
    Modified Gray-Scott style:
    - Diffusion: Spreads energy.
    - Decay: Consumes energy (Entropy).
    - Feed: Injects potential (Anti-Entropy) to prevent total heat death.
    """
    new_field = field.copy()
    h, w = field.shape
    
    for _ in range(steps):
        # Laplacian smoothing (Diffusion)
        padded = np.pad(new_field, 1, mode='edge')
        neighbors = (padded[:-2, 1:-1] + padded[2:, 1:-1] + 
                     padded[1:-1, :-2] + padded[1:-1, 2:])
        laplacian = neighbors - 4 * new_field
        
        # Reaction-Diffusion-Decay
        # dF/dt = (Diff * L) - Decay + Feed
        delta = (diffusion * laplacian) - decay + feed_rate
        new_field += delta
        
        # Clamp
        new_field = np.clip(new_field, 0.0, 1.0)
        
    return new_field

def get_semantic_axes(field):
    """
    Analyze the field and return values for the 4 minimal semantic axes.
    Returns dict: {Continuity, Flow, Stability, Density}
    """
    # 1. Density (Sparsity <-> Density)
    # Mean value of the field
    density = np.mean(field)
    
    # 2. Stability (Volatility <-> Stability)
    # Inverse of Variance? Or smoothness?
    # Variance measures 'spikiness' / contrast.
    # High variance = high volatility.
    stability = 1.0 - np.std(field)
    
    # 3. Flow (Resistance <-> Flow)
    # Gradient magnitude. High gradient = strong flow/currents.
    grad_y, grad_x = np.gradient(field)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    flow = np.mean(grad_mag) * 10.0 # Scale up slightly
    
    # 4. Continuity (Fragmentation <-> Continuity)
    # Measure of connected components or local correlation.
    # We can use spatial autocorrelation (Geary's C or Moran's I simplified).
    # Simple proxy: Average difference between neighbors.
    # Actually, that's just flow.
    # Let's use 'blobbiness' - threshold at 0.5, count connected components?
    # For now, let's use inverse of high-freq noise (Laplacian magnitude).
    # Continuity = Smoothness.
    laplacian = np.abs(np.gradient(grad_x, axis=1) + np.gradient(grad_y, axis=0))
    continuity = 1.0 - np.mean(laplacian)*10.0
    
    return {
        "Density": np.clip(density, 0, 1),
        "Stability": np.clip(stability, 0, 1),
        "Flow": np.clip(flow, 0, 1),
        "Continuity": np.clip(continuity, 0, 1)
    }

def normalize_field(field):
    """
    Safely normalize a field to 0-1 range.
    """
    f_min = field.min()
    f_max = field.max()
    if f_max - f_min < 1e-8:
        return np.zeros_like(field)
    return (field - f_min) / (f_max - f_min)

def generate_semantic_layers(field, seed=None):
    """
    Derive the 4 Neo Semantic Layers from the base Structure field.
    
    Args:
        field: The base Structure field (2D numpy array), usually normalized.
        seed: Optional seed for deterministic noise injections if needed.
        
    Returns:
        Dict[str, np.ndarray]: {
            'Structure': The base field,
            'Flow': Gradient magnitude (Movement potential),
            'Constraint': Laplacian magnitude (barriers/edges),
            'Vitality': Evolved life potential (Anti-Entropy)
        }
    """
    # 1. Structure (Base)
    structure = field
    
    # 2. Flow (Gradient Magnitude)
    grad_y, grad_x = np.gradient(structure)
    flow_mag = np.sqrt(grad_x**2 + grad_y**2)
    flow = normalize_field(flow_mag)
    
    # 3. Constraint (Laplacian / 2nd Derivative)
    # Measures "Edge-ness" or sudden change.
    laplacian = np.abs(np.gradient(grad_x, axis=1) + np.gradient(grad_y, axis=0))
    constraint = normalize_field(laplacian)
    
    # 4. Vitality (Anti-Entropy Evolution)
    # We evolve the field to find stable "life" pools.
    # We use a copy so we don't mutate structure
    vitality_raw = evolve_field(structure, steps=15, feed_rate=0.012, decay=0.01)
    vitality = np.clip(vitality_raw, 0, 1)
    
    return {
        "Structure": structure,
        "Flow": flow,
        "Constraint": constraint,
        "Vitality": vitality
    }
