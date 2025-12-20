# Neo Noise: Semantic Interference Patterns (v2)

> **Concept**: Neo Noise is a procedural generation technique that creates coherent, reproducible 2D fields not through random gradients (like Perlin) or cellular evolution (like CA), but through **Semantic Interference**. It simulates the application of a specific Inscription's particular "physics" across a field of latent potential.

## 1. The Core Algorithm

The generation of a Neo Noise field follows a 4-step process, effectively reverse-engineering the RPE logic for procedural textures.

### Step 1: Inscription as Seed
The input string (e.g., "FIRE") is hashed to create a **Deterministic Seed**.
*   This ensures that "FIRE" always produces the exact same terrain/texture.
*   Changing even one letter ("FIER") fundamentally alters the seed, and thus the physics of the world.

### Step 2: The Latent Field (Ghost Glyphs)
The algorithm treats every $(x, y)$ coordinate in the grid as containing a **Latent Glyph** (a "Ghost").
*   The type (Group) and Magnitude of this ghost are determined methodically by combining the coordinate and the Seed.
*   This creates a "white noise" of potential meaning—a field where every point *could* be a Cross or a Diagonal, but isn't realized yet.

### Step 3: Local Interaction (The Lens)
To determine the value of a pixel $(x, y)$, we do not look at the ghost glyph itself. Instead, we sample its **Neighborhood** (e.g., 3x3) and simulate **Neo Pairwise Interactions**.
*   **Cross + Diagonal** = `Crystallize` (High Intensity)
*   **Right + Left** = `Oppose` (Negative Intensity / Void)
*   **Backslash + Backslash** = `Phase Shift` (Extreme/Strange Intensity)

### Step 4: Summation & Normalization (Resolution Aware)
The final pixel value is the sum of these semantic interaction scores.
*   **Normalization**: Crucially, we normalize not against the local min/max (which causes drift at different scales), but against the **Theoretical Semantic Bounds** of the system.
*   **Result**: "FIRE" generated at 32x32 has the same average intensity as "FIRE" at 1024x1024. This allows for perfect **Level of Detail (LOD)** scaling.

---

## 2. Advanced Mechanics (v2)

### A. Temporal Evolution (Anti-Entropy)
Static noise is often dead. Neo Noise includes a **Temporal Operator** to simulate the passage of time.
*   **Diffusion**: Concepts naturally spread and blur (Laplacian smoothing).
*   **Decay**: Meaning tends to be lost over time (Entropy).
*   **Feed (Anti-Entropy)**: The "Life" term. By injecting a tiny amount of constant potential, we can create stable, self-sustaining fields that resist heat death.
    *   *Result*: A world that is "breathing" rather than just frozen static.

### B. Semantic Axes (Reading the Field)
Instead of arbitrary "Height" or "Temperature," Neo Noise naturally output 4 intrinsic properties that can be "read" by game systems:

| Axis | Derived From | Interpretation (Terrain) | Interpretation (Magic) |
| :--- | :--- | :--- | :--- |
| **DENSITY** | Mean Value | Elevation / Biomass | Mana Concentration |
| **STABILITY** | Inverse Variance | Safety / Flatness | Spell Duration |
| **FLOW** | Gradient Magnitude | Rivers / Wind / Ridges | Vector Force |
| **CONTINUITY** | Smoothness (Laplacian) | Navigability / Biome Size | Elemental Purity |

---

## 3. Theoretical Implications

### "The Physics of the Word"
In standard noise, parameters are arbitrary (Frequency, Octaves). In Neo Noise, parameters are **Semantic**.
*   **`STONE`**: High in Cross glyphs -> High interactions -> High **Density** and **Stability**.
*   **`RIVER`**: High in Diagonals -> Directed interactions -> High **Flow**.

### Reproducibility vs. Uniformity
*   **Standard Noise**: `Seed 1` and `Seed 2` look statistically identical, just shifted.
*   **Neo Noise**: "FIRE" noise looks **structurally different** from "ICE" noise. The statistical distribution of values changes based on the *composition* of the inscription.

---

## 4. Validated Use Cases
*   **Terrain Generation**: Using the Semantic Axes to determine if a region is "Walkable" (High Stability) or "Dangerous" (High Flow).
*   **VFX Textures**: Generating spell effects where the visual texture matches the spell's name.
*   **Game State**: Using the field to represent abstract "Epistemic Pressure" in a region, affecting NPC AI or magic success rates.
