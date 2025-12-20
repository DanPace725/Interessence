# Multi-Glyph Dynamics: The "Chord" Logic

> **Principle**: When 3+ glyphs combine, they do not merely sum; they form a **Relational Chord**. This chord is defined by the *Structural Role* of each glyph modulated by its *Position* in the temporal sequence.

## 1. The Core Problem
Pairwise logic works on direct interference (Delta). Multi-glyph logic must solve for:
1.  **Sequence Sensitivity**: `A -> B -> C` should feel different from `C -> B -> A`.
2.  **Emergent Complexity**: The result should be a "field state" (Chord), not just a winner-takes-all label.
3.  **Non-Associativity**: Interaction order matters.

## 2. The Solution: Structural Role + Positional Weight
We adopt a **Vector Integration** approach. Each glyph contributes to four fundamental field dimensions based on its Aicme (Group) and Magnitude, scaled by its position in the inscription.

### A. Structural Roles (The 4 Dimensions)
Every glyph maps to one of four primary vectors based on its geometry.

| Aicme (Group) | Structural Role | Vector Component | Effect |
| :--- | :--- | :--- | :--- |
| **B-Group (Right)** | **Action** | `(+X)` | Initiation, Drive, Force, Projection. |
| **H-Group (Left)** | **Action (Inv)** | `(-X)` | Resistance, Containment, Filtering, Grounding. |
| **M-Group (Cross)** | **Structure** | `(Y)` | Anchoring, Binding, Crystalization, Stability. |
| **A-Group (Diag)** | **Modulation** | `(Z)` | Flow, Drift, Color, Directionality. |
| **Forfeda (Back)** | **Transform** | `(W)` | Phase-Shift, Inversion, Mutation, warping. |

*Note: Right and Left are opposite polarities of the "Action" dimension.*

### B. Positional Weights (The Temporal Decay)
The influence of a glyph depends on *when* it appears. 
*   **Onset**: Sets the initial conditions (State).
*   **Nucleus**: The core mass of the spell/inscription.
*   **Coda**: The final expression or release.

**Standard Weighting Curve:**
1.  **Position 1 (Onset)**: `1.0` (Defines the "Key" of the chord).
2.  **Position 2 (Nucleus)**: `0.8` (Strong modification).
3.  **Position 3+ (Extension)**: `0.6` ( decaying support).
4.  **Final Glyph (Coda)**: `0.9` (Terminal output function).

### C. The Algorithm: Vector Summation
To determine the nature of an inscription (e.g., "FIRE"):

1.  **Initialize** a zero vector: `[Action: 0, Structure: 0, Modulation: 0, Transform: 0]`
2.  **Iterate** through the glyphs.
3.  **Calculate Contribution**: `GlyphMagnitude * PositionalWeight`.
4.  **Add** to the corresponding Dimension.
5.  **Result**: The final vector describes the **Field Topology**.

#### Example: FIRE vs RIFE

**Sequence: FIRE (Fearn, Idad, Ruis, Eadhadh)**
*   **F (Fearn)**: Right, Mag 3. Role: **Action (+)**. Pos: 1 (`1.0`). -> `+3.0 Action`
*   **I (Idad)**: Diag, Mag 5. Role: **Modulation**. Pos: 2 (`0.8`). -> `+4.0 Modulation`
*   **R (Ruis)**: Cross, Mag 5. Role: **Structure**. Pos: 3 (`0.6`). -> `+3.0 Structure`
*   **E (Eadhadh)**: Diag, Mag 4. Role: **Modulation**. Pos: 4 (`0.9`). -> `+3.6 Modulation`

**Total Vector**:
*   **Action**: 3.0
*   **Structure**: 3.0
*   **Modulation**: 7.6 (Dominant)
*   **Transform**: 0.0

**Interpretation**: "A highly modulated flow field (7.6), initiated by moderate force (3.0) and stabilized by a structural core (3.0)." 
*Result: A directed, stable stream.*

---

**Sequence: RIFE (Ruis, Idad, Fearn, Eadhadh)**
*   **R (Ruis)**: Cross, Mag 5. Role: **Structure**. Pos: 1 (`1.0`). -> `+5.0 Structure`
*   **I (Idad)**: Diag, Mag 5. Role: **Modulation**. Pos: 2 (`0.8`). -> `+4.0 Modulation`
*   **F (Fearn)**: Right, Mag 3. Role: **Action**. Pos: 3 (`0.6`). -> `+1.8 Action`
*   **E (Eadhadh)**: Diag, Mag 4. Role: **Modulation**. Pos: 4 (`0.9`). -> `+3.6 Modulation`

**Total Vector**:
*   **Action**: 1.8
*   **Structure**: 5.0 (Strong Base)
*   **Modulation**: 7.6 (Dominant)
*   **Transform**: 0.0

**Interpretation**: "A structural stronghold (5.0) emitting a high-intensity frequency (7.6), with weak projection (1.8)."
*Result: A vibrating obelisk/beacon (Stationary).*

## 3. Implementation in Game Logic
This system allows the RPE to process **any length string** and produce a consistent, deterministic Signal Profile.

*   **Dominance**: The highest dimension determines the "Subject" of the spell (e.g., A Projectile vs A Wall).
*   **Ratios**: The ratios between dimensions determine the "Adjectives" (e.g., "Unstable" if Transformation > Structure).
*   **Thresholds**: Specific vector magnitudes can unlock "Tiered Effects" (e.g., Structure > 10 creates permanent geometry).
