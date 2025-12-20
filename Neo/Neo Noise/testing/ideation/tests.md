
## CATEGORY 1: INVARIANCE & IDENTITY TESTS

*(“Is this thing actually itself?”)*

These test whether Neo Noise has a stable identity independent of trivial changes.

### 1. Resolution Invariance Test

**Goal:** Does meaning survive scale?

**Test:**

* Generate Neo Noise for the same inscription at:

  * 32×32
  * 64×64
  * 128×128
  * 256×256
* Normalize outputs and compare:

  * global μ, σ
  * histogram shape
  * spatial autocorrelation

**Pass condition:**

* Statistical identity remains similar
* Local detail increases, but *behavioral character* persists

**Failure modes to watch:**

* Identity only exists at one resolution
* High-res collapses into mush or noise
* Low-res loses all structure

---

### 2. Coordinate Rotation / Reflection Test

**Goal:** Is meaning tied to orientation accidentally?

**Test:**

* Rotate coordinate space by 90°, 180°
* Mirror X and Y axes
* Regenerate fields using transformed coordinates

**Pass condition:**

* Field *changes*, but retains the same **interaction affordances**
* No catastrophic semantic flip unless glyph orientation is explicitly directional

**Failure mode:**

* FIRE becomes WATER just by rotating the grid → bad coupling

---

### 3. Seed Sensitivity Envelope Test

**Goal:** Does the system have controlled variability?

**Test:**

* For a single inscription, generate 100+ seeds
* Measure:

  * μ distribution
  * variance bounds
  * frequency of extreme zones (void/singularity)

**Pass condition:**

* Variability within a bounded envelope
* Outliers exist but are rare and explainable

**Failure mode:**

* Seeds dominate meaning
* Some seeds “break” the inscription identity

---

## CATEGORY 2: COMPOSITION & ORDER TESTS

*(“Does structure really matter?”)*

These directly probe whether Neo is truly compositional.

### 4. Permutation Sensitivity Test

**Goal:** Does order matter in a principled way?

**Test:**

* Compare:

  * FIRE
  * FIER
  * RIFE
  * REEF
* Quantify:

  * cross-correlation
  * gradient alignment
  * zone clustering

**Pass condition:**

* Not identical
* Not random
* Differences are *systematic*, not chaotic

**Failure mode:**

* Either all permutations look the same
* Or permutations are completely unrelated

---

### 5. Subtractive Glyph Test

**Goal:** Does removing a glyph create a coherent loss?

**Test:**

* Compare:

  * TREE
  * TRE
  * TEE
  * REE
* Analyze what disappears or weakens

**Pass condition:**

* Loss of structure is *directional*
* Removed glyph corresponds to reduced constraints, not arbitrary noise

**Failure mode:**

* Removal causes unrelated effects
* Meaning collapses instead of attenuates

---

### 6. Additive Saturation Test

**Goal:** Is there graceful overload?

**Test:**

* Compare:

  * FIRE
  * FIREFIRE
  * FIRE×4
* Observe:

  * Does intensity saturate?
  * Does structure fracture?
  * Does noise blow up?

**Pass condition:**

* Diminishing returns or crystallization
* Not linear runaway

**Failure mode:**

* Exponential blow-up
* Total flattening

---

## CATEGORY 3: SEMANTIC FIELD TESTS

*(“Does color map to behavior, not labels?”)*

These ensure you’re not accidentally building vibes.

### 7. Blind Label Test (Very Important)

**Goal:** Can meaning be inferred without names?

**Test:**

* Generate multiple fields
* Strip labels entirely
* Have Gemini cluster fields purely by statistics
* Then compare clusters to inscription families

**Pass condition:**

* FIRE-like things cluster together
* ORDER-like things cluster together

**Failure mode:**

* Clusters do not correspond to inscriptions
* Labels are doing all the work

---

### 8. Threshold Boundary Test

**Goal:** Are transitions smooth or brittle?

**Test:**

* Slowly interpolate between two inscriptions:

  * FIRE → WATER (e.g., glyph weighting)
* Visualize transition frames

**Pass condition:**

* Gradual phase shift
* No sudden semantic snapping

**Failure mode:**

* Abrupt identity flip at arbitrary thresholds

---

## CATEGORY 4: TEMPORAL / EVOLUTION TESTS

*(“Can this survive time?”)*

This is where your system either becomes profound or collapses.

### 9. Time-Step Integration Test

**Goal:** Does headless evolution preserve identity?

**Test:**

* Take a Neo Noise field
* Apply evolution rules over:

  * Δt = small
  * Δt = medium
  * Δt = large
* Compare end states

**Pass condition:**

* Larger Δt ≈ multiple small Δt steps
* Evolution directionally consistent

**Failure mode:**

* Time step size changes outcomes qualitatively
* Non-associative time integration

---

### 10. Entropy Drift Test

**Goal:** Does the world tend toward something?

**Test:**

* Run long headless evolution
* Track:

  * variance decay
  * structure persistence
  * zone migration

**Pass condition:**

* Drift toward stable attractors *or* controlled decay
* Not total homogenization

**Failure mode:**

* Everything becomes gray mush
* Or everything collapses into singularities

---

## CATEGORY 5: GAME-RELEVANT BREAK TESTS

*(“Would this hurt a player?”)*

These tests anticipate UX pain early.

### 11. Locality Shock Test

**Goal:** Are local changes local?

**Test:**

* Perturb a small region heavily
* Observe propagation radius

**Pass condition:**

* Effects propagate predictably
* No global ripples from small changes

**Failure mode:**

* Butterfly-effect chaos everywhere

---

### 12. Stability Anchor Test

**Goal:** Can stable regions exist?

**Test:**

* Intentionally generate:

  * village candidate zones
  * flat / low variance areas
* Run time evolution

**Pass condition:**

* Stability persists longer than volatility zones

**Failure mode:**

* No place is safe long enough to matter

---

## HOW TO FRAME THIS FOR GEMINI

You can literally say something like:

> “Treat Neo Noise as a generative ontology, not a graphics algorithm. Design and run stress tests to probe invariance, compositional identity, temporal evolution, and failure modes. Explicitly identify where the system breaks or becomes incoherent.”



---

