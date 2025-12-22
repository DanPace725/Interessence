# Neo Noise: Layer Role Definitions

> **Strategy**: We do not create "River Noise" or "Mountain Noise." We use the **Same Algorithm** (Neo Noise) but interpret its outputs through 4 distinct **Functional Layers**. This prevents parameter bloat and ensures semantic coherence (e.g., a "FIRE" world has Fire-structured rivers, not generic Simplex rivers).

## The 4 Functional Layers

Every Neo-Generated World is composed of these four signal channels.

| Layer Role | Function | Neo Source | Terrain Manifestation |
| :--- | :--- | :--- | :--- |
| **1. STRUCTURE** | **Large-Scale Shape** | Low-Frequency Sample | **The Heightmap**. Continents, Oceans, Mountain Ranges. |
| **2. FLOW** | **Movement Bias** | Gradient Vectors | **Erosion & Transport**. Rivers, Wind tunnels, Ley Lines. |
| **3. CONSTRAINT** | **Blocking / Resistance** | Variance / Edge Detect | **Navigability**. Cliffs, Dense Forests, Magic Barriers. |
| **4. VITALITY** | **Growth Potential** | Anti-Entropy Feed | **Biomass**. Vegetation, Civilization spawn points, Loot density. |

---

## 1. Structure Layer (The Stage)
*   **Purpose**: Defines the "Stage" where reality happens.
*   **Derivation**: Sample the Neo Field at **Low Resolution** (e.g., 64x64 stretched to 1024x1024).
*   **Logic**:
    *   High Value -> Elevation / Matter.
    *   Low Value -> Depression / Void.

## 2. Flow Layer (The Current)
*   **Purpose**: Defines how things move across the stage.
*   **Derivation**: Calculate the **Gradient Field** ($\nabla F$) of the Structure Layer + a high-frequency "Turbulence" Neo Field.
*   **Logic**:
    *   River/Erosion simulations follow these vectors.
    *   NPC migration paths follow the "path of least resistance" defined here.

## 3. Constraint Layer (The Walls)
*   **Purpose**: Defines where things *cannot* go.
*   **Derivation**: The **Laplacian** (2nd Derivative) or Local Variance of the Structure Layer.
*   **Logic**:
    *   High Constraint -> "Hard" terrain (Bedrock, Fortress Walls, Rifts).
    *   Low Constraint -> "Soft" terrain (Soil, Sand, Open Air).
    *   *Note*: A high-elevation area (Mountain) can have Low Constraint (Plateau) or High Constraint (Jagged Peaks) depending on this layer.

## 4. Vitality Layer (The Life)
*   **Purpose**: Defines where things *grow* and *persist*.
*   **Derivation**: Run the **Anti-Entropy Evolution** step. Regions that stabilize > 0 are "Vital."
*   **Logic**:
    *   High Vitality -> Spawns resources, NPCs, vegetation.
    *   Zero Vitality -> Barren wasteland (even if Structure is high).
    *   *Example*: A High-Structure, Zero-Vitality zone is a "Dead Peak." A Low-Structure, High-Vitality zone is a "Swamp."

---

## Summary of Interaction

1.  **Structure** creates the land.
2.  **Flow** erodes the land (carving valleys).
3.  **Constraint** blocks the flow (creating lakes).
4.  **Vitality** populates the result (forests grow where Flow + Structure meet).

**All 4 layers use the exact same Inscription Seed ("FIRE").** containing coherent semantic DNA across all 4 functions.
