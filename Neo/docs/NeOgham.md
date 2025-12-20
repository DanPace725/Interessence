# NeOgham Technical Specification

## Overview
NeOgham is the fundamental character set and geometric logic system for Interessence. It extends the historical Ogham alphabet into a structurally complete 5x5 grid designed for 3D/edge-based inscription.

## 1. Structural Architecture

### The Central Stem (The Edge)
Unlike 2D scripts, NeOgham is defined by a central axis—physically, the edge of a volumetric object (pillar, stone, blade).
-   **Face A (Left)**
-   **Face B (Right)**
-   **Cross** (Traversing both faces)
-   **Diagonal** (Vector through the edge)

### The 5x5 Matrix
The system consists of 25 glyphs, organized by spatial orientation and magnitude (mark count).

| Group (Aicme) | Orientation | Geometric Property | Relational Bias |
| :--- | :--- | :--- | :--- |
| **B-Group** | Right Face (Vertical) | Unilateral, Face A | Local, Direct |
| **H-Group** | Left Face (Vertical) | Unilateral, Face B | Inverse, Complementary |
| **M-Group** | Cross (Horizontal) | Bilateral, Perpendicular | Binding, Locking |
| **A-Group** | Diagonal (Forward) | Vector, Through-Edge | Transitive, Flow |
| **Forfeda** | Diagonal (Back) | Vector, Counter-Flow | Inversion, Mutation |

*Note: Group names (B, H, M, A) are historical references but distinct in function.*

## 2. Relational Primitive (RP) Mapping

Each glyph acts as a parameter for the Relational Primitive Engine (RPE).

-   **Ontology**: Defined by the stem itself. The edge effectively "is" the entity boundary.
-   **Geometry**: Encoded by Orientation. Left/Right defines approach vectors; Cross defines bonding; Diagonals define flow direction.
-   **Constraint**: Encoded by Mark Count (1-5). Higher magnitude = stronger bias/stiffer constraint.
-   **Epistemic**: Defined by Visibility. A glyph on the Right Face is invisible to an observer on the Left, creating inherent information asymmetry.

## 3. Game System Applications

### Dimensional Spellcasting
Spells are geometric structures built from NeOgham.
-   **Mechanic**: Players must position their camera/character to align visible glyph segments into valid logic circuits.
-   **Occlusion**: Complex spells span multiple faces, requiring multiple players (or rapid movement) to "hold" the spell in working memory (Signal persistence).

### Geometric Crafting
Crafting is the assembly of geometric logic gates.
-   **Partial Glyphs**: Components (hilts, guards, pommels) contain fragment glyphs.
-   **Assembly**: Joining components physically aligns fragments.
-   **Completion**: If fragments form a valid NeOgham glyph, the item gains that glyph's RP bias (e.g., "Fire" property, or "Durability" constraint).

### Inscription-Based Generation (Genetics)
Objects are procedurally generated from their NeOgham names.
-   **Process**: `String Name` -> `Glyph Sequence` -> `Parametric Curves` -> `3D Mesh`.
-   **Identity**: Changing the name (inscription) alters the physical mesh.
-   **Mutation**: "Genetic" drift occurs when inscriptions are imperfectly copied or damaged, physically warping the entity's form.