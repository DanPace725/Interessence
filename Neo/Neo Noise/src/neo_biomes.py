"""
Neo Biome Emergence System
Uses K-means clustering on semantic axes to discover emergent biomes.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class BiomeInfo:
    """Metadata for a discovered biome."""
    id: int
    name: str
    color: Tuple[float, float, float]
    centroid: np.ndarray  # [Density, Stability, Flow, Continuity]
    pixel_count: int = 0


# Default biome color palette (earthy, natural tones)
DEFAULT_BIOME_PALETTE = [
    (0.2, 0.5, 0.2),   # Forest Green
    (0.8, 0.7, 0.4),   # Desert Sand
    (0.3, 0.35, 0.3),  # Mountain Gray
    (0.4, 0.6, 0.3),   # Plains Green
    (0.25, 0.4, 0.35), # Wetland Teal
    (0.5, 0.3, 0.2),   # Badlands Brown
    (0.6, 0.55, 0.45), # Savanna Gold
    (0.15, 0.3, 0.15), # Dense Jungle
    (0.7, 0.65, 0.6),  # Tundra Gray
    (0.35, 0.25, 0.2), # Volcanic Dark
]


class BiomeClassifier:
    """
    Classifies terrain into biomes using K-means clustering on semantic axes.
    
    The 4 semantic axes are:
    - Density: Mean field value (elevation/biomass)
    - Stability: Inverse variance (safety/flatness)
    - Flow: Gradient magnitude (rivers/wind)
    - Continuity: Smoothness (navigability/biome size)
    """
    
    def __init__(self, n_biomes: int = 6, max_iterations: int = 20, seed: int = None):
        self.n_biomes = n_biomes
        self.max_iterations = max_iterations
        self.seed = seed
        self.centroids = None
        self.biome_info: List[BiomeInfo] = []
        
    def _compute_semantic_features(self, layers: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Compute per-pixel feature vectors from the 4 semantic layers.
        
        Returns:
            np.ndarray: Shape (H*W, 4) with [Density, Stability, Flow, Vitality]
        """
        structure = layers['Structure']
        flow = layers['Flow']
        constraint = layers['Constraint']
        vitality = layers['Vitality']
        
        h, w = structure.shape
        
        # Feature 1: Density = Structure height (0-1)
        density = structure.flatten()
        
        # Feature 2: Stability = Inverse of Constraint (edges = unstable)
        # Constraint layer already captures edges/roughness
        stability = (1.0 - constraint).flatten()
        
        # Feature 3: Flow = Already computed (gradient magnitude)
        flow_flat = flow.flatten()
        
        # Feature 4: Vitality = Life potential (already computed)
        vitality_flat = vitality.flatten()
        
        # Stack features
        features = np.stack([density, stability, flow_flat, vitality_flat], axis=1)
        return features
    
    def _kmeans(self, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simple K-means clustering implementation.
        
        Args:
            features: Shape (N, 4) feature vectors
            
        Returns:
            labels: Shape (N,) cluster assignments
            centroids: Shape (K, 4) cluster centers
        """
        n_samples = features.shape[0]
        
        # Initialize centroids using K-means++ style
        rng = np.random.default_rng(self.seed)
        
        # Pick first centroid randomly
        centroids = [features[rng.integers(n_samples)]]
        
        # Pick remaining centroids with probability proportional to distance squared
        for _ in range(1, self.n_biomes):
            # Compute distance to nearest centroid for each point
            dists = np.array([np.min([np.sum((f - c)**2) for c in centroids]) for f in features])
            probs = dists / dists.sum()
            idx = rng.choice(n_samples, p=probs)
            centroids.append(features[idx])
            
        centroids = np.array(centroids)
        
        # Iterate
        labels = np.zeros(n_samples, dtype=int)
        
        for iteration in range(self.max_iterations):
            # Assign points to nearest centroid
            old_labels = labels.copy()
            
            for i, point in enumerate(features):
                dists = np.sum((centroids - point) ** 2, axis=1)
                labels[i] = np.argmin(dists)
            
            # Check convergence
            if np.array_equal(labels, old_labels):
                break
                
            # Update centroids
            for k in range(self.n_biomes):
                mask = labels == k
                if np.any(mask):
                    centroids[k] = features[mask].mean(axis=0)
                    
        return labels, centroids
    
    def _infer_biome_name(self, centroid: np.ndarray) -> str:
        """
        Infer a biome name from the centroid's position in feature space.
        
        Centroid: [Density, Stability, Flow, Vitality]
        """
        density, stability, flow, vitality = centroid
        
        # Density = height (high = mountains, low = lowlands)
        # Stability = inverse constraint (high = smooth, low = rough/edges)
        # Flow = gradient magnitude (high = rivers/slopes, low = flat)
        # Vitality = life potential (high = lush, low = barren)
        
        # High altitude biomes (density > 0.6)
        if density > 0.6:
            if vitality > 0.5:
                return "Alpine Meadow"
            elif stability > 0.5:
                return "Highland Plateau"
            else:
                return "Mountain Peaks"
        
        # Mid altitude biomes (density 0.35 - 0.6)
        elif density > 0.35:
            if flow > 0.4:
                if vitality > 0.5:
                    return "River Valley"
                else:
                    return "Rocky Canyon"
            elif vitality > 0.55:
                if stability > 0.6:
                    return "Dense Forest"
                else:
                    return "Woodland"
            elif stability > 0.6:
                return "Grasslands"
            else:
                return "Scrubland"
        
        # Low altitude biomes (density < 0.35)
        else:
            if flow > 0.35:
                if vitality > 0.5:
                    return "Wetlands"
                else:
                    return "Marshes"
            elif vitality > 0.5:
                return "Fertile Plains"
            elif stability < 0.4:
                return "Badlands"
            else:
                return "Desert"
    
    def _assign_biome_color(self, biome_id: int, centroid: np.ndarray) -> Tuple[float, float, float]:
        """
        Assign a color to a biome based on its characteristics.
        
        Centroid: [Density, Stability, Flow, Vitality]
        """
        density, stability, flow, vitality = centroid
        
        # Color logic:
        # - Vitality → GREEN (high vitality = lush vegetation)
        # - Flow → BLUE (high flow = water presence)
        # - Low vitality + low flow → BROWN/TAN (dry, barren)
        # - High density → lighter tones (alpine)
        # - Low density → darker tones (lowlands)
        
        # Base GREEN from vitality (life = green)
        g = 0.15 + (vitality * 0.6)
        
        # BLUE from flow (water presence)
        b = 0.1 + (flow * 0.5)
        
        # RED: high when dry (low vitality AND low flow), forms browns/tans
        dryness = (1.0 - vitality) * (1.0 - flow)
        r = 0.2 + (dryness * 0.5) + (density * 0.15)
        
        # Elevation adjustment: higher = lighter overall
        elevation_boost = density * 0.2
        r += elevation_boost
        g += elevation_boost * 0.8  # Slightly less green boost at altitude
        b += elevation_boost * 0.6
        
        # Stability affects saturation (rough terrain = more muted)
        if stability < 0.5:
            # Pull toward gray for unstable/rough terrain
            gray = (r + g + b) / 3
            blend = 1.0 - (stability * 0.5)
            r = r * (1 - blend * 0.3) + gray * blend * 0.3
            g = g * (1 - blend * 0.3) + gray * blend * 0.3
            b = b * (1 - blend * 0.3) + gray * blend * 0.3
        
        return (np.clip(r, 0.05, 0.95), np.clip(g, 0.05, 0.95), np.clip(b, 0.05, 0.95))
    
    def fit_predict(self, layers: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Classify all pixels into biomes.
        
        Args:
            layers: Dict with 'Structure', 'Flow', 'Constraint', 'Vitality'
            
        Returns:
            np.ndarray: Shape (H, W) with biome IDs (0 to n_biomes-1)
        """
        h, w = layers['Structure'].shape
        
        # Compute features
        features = self._compute_semantic_features(layers)
        
        # Run K-means
        labels, self.centroids = self._kmeans(features)
        
        # Build biome info
        self.biome_info = []
        for k in range(self.n_biomes):
            centroid = self.centroids[k]
            name = self._infer_biome_name(centroid)
            color = self._assign_biome_color(k, centroid)
            count = np.sum(labels == k)
            
            self.biome_info.append(BiomeInfo(
                id=k,
                name=name,
                color=color,
                centroid=centroid,
                pixel_count=count
            ))
            
        # Reshape to 2D
        biome_map = labels.reshape(h, w)
        return biome_map
    
    def get_biome_color(self, biome_id: int) -> Tuple[float, float, float]:
        """Get RGB color for a biome ID."""
        if biome_id < len(self.biome_info):
            return self.biome_info[biome_id].color
        return (0.5, 0.5, 0.5)  # Gray fallback
    
    def get_biome_name(self, biome_id: int) -> str:
        """Get name for a biome ID."""
        if biome_id < len(self.biome_info):
            return self.biome_info[biome_id].name
        return "Unknown"
    
    def print_biome_summary(self):
        """Print a summary of discovered biomes."""
        print("\n=== Discovered Biomes ===")
        for info in self.biome_info:
            pct = info.pixel_count / sum(b.pixel_count for b in self.biome_info) * 100
            print(f"  [{info.id}] {info.name}: {pct:.1f}% coverage")
            print(f"      Centroid: D={info.centroid[0]:.2f}, S={info.centroid[1]:.2f}, "
                  f"F={info.centroid[2]:.2f}, C={info.centroid[3]:.2f}")
        print()


def generate_biome_texture(biome_map: np.ndarray, classifier: BiomeClassifier,
                           overlay: np.ndarray = None) -> np.ndarray:
    """
    Generate an RGB texture from a biome map.
    
    Args:
        biome_map: 2D array of biome IDs
        classifier: Fitted BiomeClassifier with color info
        overlay: Optional GCO overlay for water features
        
    Returns:
        np.ndarray: Shape (H, W, 3) RGB image
    """
    h, w = biome_map.shape
    rgb = np.zeros((h, w, 3))
    
    # Apply biome colors
    for y in range(h):
        for x in range(w):
            biome_id = biome_map[y, x]
            rgb[y, x] = classifier.get_biome_color(biome_id)
    
    # Apply GCO overlay if provided (water features override biome colors)
    if overlay is not None:
        for y in range(h):
            for x in range(w):
                feat = overlay[y, x]
                if feat >= 0.9:  # Major River
                    rgb[y, x] = [0.0, 0.7, 0.9]  # Cyan
                elif feat >= 0.7:  # Minor River
                    rgb[y, x] = [0.1, 0.5, 0.7]  # Teal
                elif feat >= 0.5:  # Lake
                    rgb[y, x] = [0.1, 0.3, 0.6]  # Deep Blue
                elif feat >= 0.2:  # Forest (blend with biome)
                    forest_col = np.array([0.1, 0.4, 0.1])
                    rgb[y, x] = rgb[y, x] * 0.5 + forest_col * 0.5
                    
    return rgb


# Quick test
if __name__ == "__main__":
    import neo_noise_core as core
    
    print("Testing Biome Classifier...")
    
    # Generate test field
    structure, seed = core.generate_field("FOREST", 128, 128, normalize=True)
    layers = core.generate_semantic_layers(structure, seed)
    
    # Classify
    classifier = BiomeClassifier(n_biomes=6, seed=42)
    biome_map = classifier.fit_predict(layers)
    
    classifier.print_biome_summary()
    
    print(f"Biome map shape: {biome_map.shape}")
    print(f"Unique biomes: {np.unique(biome_map)}")
    print("Done!")
