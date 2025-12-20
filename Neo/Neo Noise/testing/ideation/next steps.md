
---

## Priority 1: Stabilize the substrate before expanding it

### 1. Add **resolution-aware normalization** (must-do)

This is the only thing that genuinely blocks world gen readiness right now.

**Problem revealed**

* Mean intensity drifts downward with higher resolution.
* That will cause the same “world” to mean different things at different scales.

**Why this matters for world gen**

* Biomes, rivers, forests, villages must not depend on chunk size.
* LOD (level of detail) will *absolutely* break without this.

**What to do**

* Normalize after aggregation, not before.
* Or normalize per-octave / per-layer before composition.
* Alternatively: introduce a reference scale (e.g. “world-meter”) and scale weights relative to it.

This is not cosmetic. This is foundational.

> **Do this before adding a single new semantic layer.**

---

### 2. Introduce a **controlled anti-entropy term** (must-do)

Your entropy test didn’t reveal a bug — it revealed physics.

But for world gen, **pure entropy means eventual dead maps**.

You need a *dial*, not a rewrite.

**Options (you only need one at first):**

* A weak attractor field (baseline pressure that never goes to zero)
* Periodic regeneration (seasonal pulse, environmental breathing)
* Boundary injection (edges feed structure inward)
* Life-coupled regeneration (only stabilizes where “activity” exists)

**Why now**

* Terrain generation will rely on long-term stability.
* Rivers, forests, settlements need persistence across time skips.

This turns Neo Noise from “cosmic fog” into “habitable substrate.”

---

## Priority 2: Clarify semantic intent (without over-defining meaning)

You are doing something subtle and correct already:
**meaning is emergent, not symbolic**.

But world gen needs *operational semantics*, not lore semantics.

### 3. Define a **minimal semantic axis set**

Not “fire = hot” or “water = wet” — that’s the trap.

Instead, define things like:

* continuity ↔ fragmentation
* flow ↔ resistance
* stability ↔ volatility
* density ↔ sparsity

These are *physicalizable*.

**Why this matters**

* Terrain features map naturally to these axes.
* AI, ecology, and magic can all read the same signals differently.
* You avoid hardcoding “biomes” too early.

Think of this as:

> “What kinds of forces exist?”
> not
> “What things exist?”

---

### 4. Lock in **layer roles**, not layer meanings

Before adding layers, decide what *types* of layers exist.

Example:

* Structural layer (large-scale shape)
* Flow layer (movement bias)
* Constraint layer (blocking, resistance)
* Vitality layer (growth potential)

You can generate all of these from Neo Noise **without changing the core algorithm**, just by:

* sampling at different frequencies
* using different aggregation weights
* interpreting gradients differently

This avoids Minecraft’s “17 parameters bolted on over a decade” problem.

---

## Priority 3: Prepare for terrain specifically

### 5. Build a **gray-box terrain extractor** (next practical step)

Don’t add new noise yet.
Instead, answer this question:

> “Given the current Neo field, can I reliably say:
>
> * this is walkable
> * this holds water
> * this supports growth
> * this resists change?”

That means:

* thresholding
* slope detection
* gradient direction
* local variance checks

No meshes. No textures. Just flags.

If you can’t do this cleanly, adding more layers will only hide the problem.

---

### 6. Test **biome emergence**, not biome assignment

Don’t define “forest,” “desert,” etc. yet.

Instead:

* Generate maps
* Cluster regions based on Neo-derived metrics
* See if *recurring terrain personalities* appear

If they do, you’re done.
If they don’t, *then* you adjust layer interactions.

This is exactly where Minecraft’s biome complexity came from — but you get to do it consciously.

---

## What NOT to do yet (important)

❌ Don’t add dozens of layers
❌ Don’t lock in specific biomes
❌ Don’t over-semanticize glyphs
❌ Don’t optimize performance prematurely
❌ Don’t switch engines or tools

You are still shaping the physics, not the content.

---

