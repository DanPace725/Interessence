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

def generate_field(inscription, width=100, height=100, normalize=True):
    """
    Generate the full 2D noise field.
    Returns: field (numpy array), seed (int)
    """
    # Create deterministic seed from string
    if isinstance(inscription, str):
        seed = hash(inscription.upper()) & 0xFFFFFFFF
    else:
        seed = int(inscription) # Allow passing raw seed
    
    field = np.zeros((height, width))
    
    for y in range(height):
        for x in range(width):
            field[y, x] = calculate_local_intensity(seed, x, y)
    
    # FIX: Resolution-Aware Normalization
    # Previous implementation normalized strictly Min-Max locally, which shifts the semantic baseline.
    # We should normalize against GLBAL THEORETICAL BOUNDS to preserve semantic meaning across scales.
    # Min theoretical: -1.5 (Opposition) * Count
    # Max theoretical: 6.0 (Phase Shift) + 1.25 (Delta 5*0.25) ~ 7.25 * Count
    
    # Actually, calculate_local_intensity divides by count.
    # So bounds are roughly -1.5 to 7.25.
    
    THEORETICAL_MIN = -1.5
    THEORETICAL_MAX = 7.5 
    
    if normalize:
        # Scale to 0-1 based on fixed bounds, NOT local min/max
        field = (field - THEORETICAL_MIN) / (THEORETICAL_MAX - THEORETICAL_MIN)
        field = np.clip(field, 0.0, 1.0)
            
    return field, seed

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
