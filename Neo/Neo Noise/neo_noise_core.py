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

# ============================================================================
# SEQUENTIAL FIELD PROPAGATION (Multiglyph Composition)
# ============================================================================
# This module implements left-fold composition for multi-glyph inscriptions.
# Each glyph modifies a 4D field vector: [Action, Structure, Modulation, Transform]

def glyph_to_field_vector(glyph):
    """
    Convert a glyph dict to a 4D field vector.
    
    Returns:
        np.ndarray: [action, structure, modulation, transform]
    """
    vector = np.zeros(4)  # [action, structure, modulation, transform]
    
    glyph_type = glyph['type']
    magnitude = glyph['mag']
    
    if glyph_type == 'left':
        vector[0] = -magnitude  # Negative action
    elif glyph_type == 'right':
        vector[0] = magnitude   # Positive action
    elif glyph_type == 'cross':
        vector[1] = magnitude   # Structure
    elif glyph_type == 'diagonal':
        vector[2] = magnitude   # Modulation
    elif glyph_type == 'backslash':
        vector[3] = magnitude   # Transform
    
    return vector

def pairwise_interference(state, glyph):
    """
    Calculate interference between accumulated state and new glyph.
    
    Args:
        state: Current 4D state vector (or glyph dict for initial)
        glyph: New glyph dict to incorporate
        
    Returns:
        np.ndarray: New 4D field state
    """
    # If state is a glyph dict, convert to field vector first
    if isinstance(state, dict):
        state = glyph_to_field_vector(state)
    
    # Convert new glyph to field contribution
    g_vector = glyph_to_field_vector(glyph)
    
    # Determine interaction modifier based on dominant dimensions
    dominant_dim = np.argmax(np.abs(state)) if np.any(state != 0) else 0
    
    interaction_modifier = 1.0
    
    # Check if they reinforce or oppose based on dominant dimensions
    if dominant_dim == np.argmax(np.abs(g_vector)):
        interaction_modifier = 1.5  # Reinforce same dimension
    elif np.abs(state[dominant_dim]) > 0 and np.sign(state[dominant_dim]) != np.sign(g_vector[dominant_dim]):
        interaction_modifier = 0.5  # Opposition
    
    # Combine: decay old state, add new contribution with modifier
    new_state = state * 0.7 + g_vector * interaction_modifier
    
    return new_state

def sequential_composition(inscription):
    """
    Compose glyphs sequentially using left fold.
    
    S₀ = G₁
    S₁ = pairwise_interference(S₀, G₂)
    S₂ = pairwise_interference(S₁, G₃)
    ...
    
    Args:
        inscription: The inscription string
        
    Returns:
        tuple: (final_state, history) where final_state is 4D vector
               and history is list of (glyph, state) tuples
    """
    inscription = inscription.upper()
    glyphs = [NEO_GLYPHS.get(char) for char in inscription if char in NEO_GLYPHS]
    
    if not glyphs:
        return np.zeros(4), []
    
    # Initialize with first glyph
    state = glyph_to_field_vector(glyphs[0])
    history = [(glyphs[0], state.copy())]
    
    # Sequentially fold remaining glyphs
    for glyph in glyphs[1:]:
        state = pairwise_interference(state, glyph)
        history.append((glyph, state.copy()))
    
    return state, history

def get_inscription_bias(inscription):
    """
    Compute semantic bias weights from sequential composition.
    
    Returns a dict of normalized weights (0-1) for each dimension.
    These can be used to modulate TYPE_INTERACTIONS.
    
    Args:
        inscription: The inscription string
        
    Returns:
        dict: {
            'action': float,      # Absolute normalized action bias
            'structure': float,   # Normalized structure bias  
            'modulation': float,  # Normalized modulation bias
            'transform': float,   # Normalized transform bias
            'raw_vector': np.ndarray,  # The raw 4D state vector
            'magnitude': float    # Overall magnitude (word "power")
        }
    """
    final_state, _ = sequential_composition(inscription)
    
    # Compute magnitude
    magnitude = np.linalg.norm(final_state)
    
    # Normalize to get relative contributions
    abs_state = np.abs(final_state)
    total = np.sum(abs_state)
    
    if total < 1e-8:
        # No valid glyphs, return neutral bias
        return {
            'action': 0.25,
            'structure': 0.25,
            'modulation': 0.25,
            'transform': 0.25,
            'raw_vector': final_state,
            'magnitude': 0.0
        }
    
    normalized = abs_state / total
    
    return {
        'action': float(normalized[0]),
        'structure': float(normalized[1]),
        'modulation': float(normalized[2]),
        'transform': float(normalized[3]),
        'raw_vector': final_state,
        'magnitude': float(magnitude)
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

def calculate_local_intensity(seed, x, y, bias=None):
    """
    Calculate the semantic intensity at (x,y) by observing the neighborhood.
    
    Args:
        seed: The inscription seed
        x, y: Coordinates
        bias: Optional dict from get_inscription_bias() to modulate interactions
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
    
    # Compute bias modifiers if provided
    # Map glyph types to bias dimensions
    type_to_bias_key = {
        'left': 'action',
        'right': 'action', 
        'cross': 'structure',
        'diagonal': 'modulation',
        'backslash': 'transform'
    }
    
    # Pairwise interaction of all neighbors
    for i in range(len(neighbors)):
        for j in range(i + 1, len(neighbors)):
            t1, m1 = neighbors[i]
            t2, m2 = neighbors[j]
            
            # 1. Base Type Interaction
            base = TYPE_INTERACTIONS.get((t1, t2))
            if base is None:
                base = TYPE_INTERACTIONS.get((t2, t1), 0.5)
            
            # 2. Apply semantic bias modulation if provided
            if bias is not None:
                # Average the bias weights for both types involved
                b1 = bias.get(type_to_bias_key.get(t1, 'action'), 0.25)
                b2 = bias.get(type_to_bias_key.get(t2, 'action'), 0.25)
                # Bias modifies the interaction strength
                # Higher bias for these types = stronger contribution
                bias_factor = (b1 + b2) / 0.5  # Normalize so 0.25+0.25=1.0 is neutral
                base *= bias_factor
            
            # 3. Magnitude Modulation
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

def generate_field(inscription, width=100, height=100, normalize=True, octaves=4, persistence=0.5, lacunarity=2.0, semantic_bias_strength=0.3):
    """
    Generate the full 2D noise field using Multi-Scale Fractal Noise.
    
    Args:
        inscription: Seed string.
        width, height: Output resolution.
        normalize: Whether to normalize output 0-1.
        octaves: Number of layers of detail.
        persistence: How much amplitude decreases per octave (0.5 = half).
        lacunarity: How much frequency increases per octave (2.0 = double).
        semantic_bias_strength: How strongly the sequential glyph composition
                               affects the field (0.0 = none, 1.0 = full).
                               Default 0.3 for moderate influence.
    """
    # Create deterministic seed from string
    if isinstance(inscription, str):
        base_seed = hash(inscription.upper()) & 0xFFFFFFFF
        # Compute semantic bias from sequential glyph composition
        raw_bias = get_inscription_bias(inscription)
    else:
        base_seed = int(inscription)
        raw_bias = None
    
    # Apply bias strength scaling
    # semantic_bias_strength of 0.0 means no bias (all weights = 0.25)
    # semantic_bias_strength of 1.0 means full bias as computed
    if raw_bias is not None and semantic_bias_strength > 0:
        scaled_bias = {
            'action': 0.25 + (raw_bias['action'] - 0.25) * semantic_bias_strength,
            'structure': 0.25 + (raw_bias['structure'] - 0.25) * semantic_bias_strength,
            'modulation': 0.25 + (raw_bias['modulation'] - 0.25) * semantic_bias_strength,
            'transform': 0.25 + (raw_bias['transform'] - 0.25) * semantic_bias_strength,
        }
    else:
        scaled_bias = None
    
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
                layer[y, x] = calculate_local_intensity(octave_seed, x, y, scaled_bias)
                
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
    
    # ACTUAL BOUNDS NORMALIZATION
    # Use observed field range instead of theoretical bounds.
    # This is the "honest" approach - rare extreme values will map to extremes,
    # and the natural signal distribution is preserved.
    if normalize:
        field_min = field.min()
        field_max = field.max()
        if field_max - field_min > 1e-8:
            field = (field - field_min) / (field_max - field_min)
        else:
            field = np.full_like(field, 0.5)
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
