# Neo Explorations: Synthesis Report

Generated: 2026-05-06T13:52:00

Seven investigations driven by the structured corpus in `neo_phrase_corpus.csv`. Detailed results live in the per-task files alongside this report. A visual scatterplot companion is available in `05_chord_visualizations.html`.

## 1. Translation Invariance (`01_translation_invariance.md`)

- Triplets/pairs analyzed: **7**
- Mean cosine across all cross-language pairs: **+0.870**
- Mean Euclidean distance: **0.288**
- Dominant-interaction match rate across pairs: **29.4%**

Most-invariant concept (highest avg cosine):
  - `memory holds the stone / river remembers` (cos=+0.949)
  - `care bends friction towards freedom` (cos=+0.937)
Least-invariant concept (lowest avg cosine):
  - `memory opens the gate` (cos=+0.828)
  - `war breaks the gate` (cos=+0.723)

## 2. Phase Shift / Turbulence Reachability (`02_phase_turbulence.md`)

- Phase Shift events fired across probes: **22**
- Turbulence events fired across probes: **11**
- Probes run: 15

Conclusion: both rare cells are reachable. They simply do not appear in natural Latin-alphabet prose because the Forfeda digraphs (AE/OI/UI/EA/IO) only arise from Irish orthography or transliteration, and almost never adjacent. They are available as a 'ritual register' for deliberate Forfeda-heavy inscription.

## 3. Semantic Category Consistency (`03_semantic_categories.md`)

| Category | Within-avg cosine | vs random baseline | Dominant consensus |
| :--- | :--- | :--- | :--- |
| containment | +0.968 | +0.165 | `Dampen` (4/5) |
| opening | +0.904 | +0.101 | `Dampen` (3/5) |
| waiting | +0.895 | +0.092 | `Dampen` (3/5) |
| motion | +0.843 | +0.040 | `Dampen` (3/5) |
| breakage | +0.814 | +0.011 | `Dampen` (2/5) |

Random-subset noise floor (500 random 5-phrase subsets of the 38-phrase structured natural/translation corpus): mean cosine **+0.803**, 95th percentile **+0.915**.

Most consistent semantic category: **containment** (within-cosine +0.968)
Least consistent: **breakage** (within-cosine +0.814)

## 4. Chord-Space Clusters (`04_chord_clusters.md`)

- Corpus rows clustered: **38**
- Corpus centroid: action_net=-0.047, structure=+0.316, flow=+0.465, transform=+0.045

K-means K=4 cluster summary (label = largest deviation from corpus centroid):

| Cluster | Label | Size | Lang mix |
| :--- | :--- | :--- | :--- |
| 0 | `+d_action_net` | 14 | EN=6, LA=4, GA=3, NEO=1 |
| 1 | `-d_flow` | 3 | GA=2, EN=1 |
| 2 | `-d_action_net` | 14 | EN=10, LA=3, GA=1 |
| 3 | `+d_structure` | 7 | EN=6, GA=1 |

Most-average phrases (closest to centroid):
- 0.110 LIGHT BREAKS THE DARKNESS
- 0.117 THE MAP IS NOT THE TERRITORY
- 0.132 CARE BENDS FRICTION TOWARDS FREEDOM

Most-extreme phrases (farthest from centroid):
- 0.434 COFFEE WAITS BESIDE THE WINDOW
- 0.411 THE SPEIR IS BLUE
- 0.408 ORDER LEARNS TO DREAM

## 5. Chord Visualizations (`05_chord_visualizations.html`)

The visualization report plots flow/action, flow/structure, structure/transform, and a two-axis PCA projection of the chord vectors. Points are colored by language so the language fingerprint can be inspected visually rather than only inferred from tables.

## 6. Controlled Syntax (`06_controlled_syntax.md`)

Controlled syntax rows hold the noun pairs steady while swapping the frame: `opens`, `holds`, `breaks`, and `waits_near`.

| Frame | Within-avg cosine | Dominant consensus |
| :--- | :--- | :--- |
| waits_near | +0.942 | `Dampen` (5/5) |
| opens | +0.909 | `Dampen` (3/5) |
| breaks | +0.897 | `Dampen` (4/5) |
| holds | +0.885 | `Dampen` (4/5) |

## 7. Minimal Pairs (`07_minimal_pairs.md`)

Mean Euclidean movement for one-edit word pairs: **0.357**

| Family | Avg pair cosine | Avg pair Euclid | Most moved from base |
| :--- | :--- | :--- | :--- |
| gate_family | +0.810 | 0.456 | FATE (0.556) |
| light_family | +0.801 | 0.389 | RIGHT (0.423) |
| stone_family | +0.823 | 0.347 | STORM (0.546) |
| break_family | +0.842 | 0.330 | BREATHE (0.373) |
| care_family | +0.991 | 0.078 | CIRCE (0.109) |

## Cross-cutting observations

**Translation invariance is real but uneven.** Mean cross-language cosine sits at **+0.870**, well above orthogonality. Same-concept phrases *do* point in similar directions in chord space. But the dominant-interaction label only matches **29%** of the time. So the *vector* is preserved across languages while the *peak interaction cell* gets relabeled by orthography. The most stable concept is `memory holds the stone / river remembers` (cos +0.949), the least is `war breaks the gate` (+0.723).

**Forfeda is a 'ritual register'.** Phase Shift and Turbulence are sparse in natural prose but trivially producible once Forfeda digraphs are clustered intentionally. The pure Phase-Shift probes `AEUI`, `AEAEAE`, `UIEAIO` all collapse to chord vector `(0, 0, 0, 1)` - pure transform. This means the Forfeda axis is currently a *binary* indicator (present / absent) rather than a continuous signal in observed text. It functions as an opt-in 'magic register'.

**Semantic categories barely beat random.** Random 5-phrase subsets of the 38-phrase structured natural/translation corpus already average **+0.803** within-cosine - meaning the entire corpus lives in a single tight chord neighborhood. The most cohesive category (`containment`) beats the noise floor by only **+0.165**, the least by **+0.011**. The cross-category centroid cosine matrix is uniformly +0.95 to +1.00. Translation: chord-space clustering currently captures English-prose letter statistics, not semantic content.

**Controlled frames are the next stress test.** The most internally stable frame is `waits_near` (+0.942); the loosest is `holds` (+0.885). If these values stay high while cross-frame centroids remain close, Neo is mostly hearing the shared sentence shell. If the frame centroids pull apart, the verb/action field is measurable.

**Minimal pairs expose the instrument's gain.** The most sensitive family in this run is `gate_family` (avg Euclid 0.456); one-edit pairs move by 0.357 on average. This gives us a concrete scale for deciding whether a phrase-level difference is large or just normal orthographic jitter.

**Clusters track *language*, not just *meaning*.** Once K-means clusters are relabeled by deviation from the corpus centroid, the four groups have distinct linguistic tilts:

- Cluster 0 `+d_action_net` over-represents Latin (LA=4, GA=3, EN=6)
- Cluster 1 `-d_flow` over-represents Irish (GA=2, LA=0, EN=1)
- Cluster 3 `+d_structure` over-represents English (EN=6, LA=0, GA=1)

The chord vector currently carries a **language fingerprint** as its primary signal. Latin currently over-represents in the positive-action cluster, Irish in the low-flow / high-transform pocket, and English in the high-structure and negative-action clusters. Concept identity is a secondary, weaker layer on top.

**Implication for the Name = Form thesis.** Two genuine outcomes are compatible with these results: (a) Neo correctly captures that 'the same idea expressed in different languages is a different inscription' - meaningful and intended, or (b) Neo currently confuses orthography with meaning and a phoneme-level or lemma-level normalization layer is needed before chord vectors. This audit doesn't pick between the two; it simply makes the trade-off visible and quantifies it.
