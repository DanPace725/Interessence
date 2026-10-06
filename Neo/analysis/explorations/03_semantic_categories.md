# Task 5: Semantic-Category Mapping Study

5 hand-authored categories (25 phrases total) test whether Neo signatures cluster by *meaning*. For each category we report mean chord, std-dev, within-category cosine similarity, and dominant-interaction consensus.

All phrases run with `--missing canonical`.

## Noise floor

To judge whether category cohesion is meaningful, we draw 500 random 5-phrase subsets from the structured natural/translation corpus and compute their within-subset cosine similarity. This is the *baseline* a category must beat to count as semantically cohesive in chord space.

- Random 5-subset cosine: mean **+0.803** (stdev 0.073; 5th percentile +0.678; 95th percentile +0.915)

Read the consistency table below in light of this baseline: a category with within-avg cosine close to **+0.803** is no more cohesive than a random handful of phrases.

## Cross-category centroid cosine matrix

| | breakage | containment | motion | opening | waiting |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **breakage** | +1.00 | +0.97 | +0.99 | +1.00 | +0.99 |
| **containment** | +0.97 | +1.00 | +0.99 | +0.96 | +0.97 |
| **motion** | +0.99 | +0.99 | +1.00 | +0.99 | +1.00 |
| **opening** | +1.00 | +0.96 | +0.99 | +1.00 | +0.99 |
| **waiting** | +0.99 | +0.97 | +1.00 | +0.99 | +1.00 |

If categories truly differed by meaning, this matrix would have low off-diagonal values. In practice the off-diagonal values sit in the **+0.95 to +1.00** band, showing that all five category centroids point in essentially the same direction in chord space.

## Per-category detail

### breakage

| Phrase | Dominant | Disrupt | Entropy | Chord |
| :--- | :--- | :--- | :--- | :--- |
| THE GLASS SHATTERS ON THE FLOOR | Reinforce (6) | 0 | 2.58 | (+0.22, +0.35, +0.43, +0.00) |
| THE BONE SNAPS UNDER WEIGHT | Gate (6) | 0 | 2.43 | (-0.05, +0.35, +0.60, +0.00) |
| THE BRIDGE COLLAPSES IN THE STORM | Propel (8) | 0 | 2.52 | (+0.03, +0.31, +0.65, +0.00) |
| THE ICE CRACKS BENEATH THE BOOT | Dampen (7) | 2 | 2.76 | (-0.39, +0.12, +0.45, +0.05) |
| THE WALL CRUMBLES INTO DUST | Dampen (6) | 0 | 2.49 | (-0.26, +0.21, +0.53, +0.00) |

- Mean chord: action_net=-0.088, structure=+0.268, flow=+0.534, transform=+0.010
- Std-dev:    action_net=+0.214, structure=+0.091, flow=+0.086, transform=+0.019
- Within-category avg cosine similarity: +0.814
- Dominant interaction consensus: `Dampen` (2/5)
- Dominant distribution: Dampen=2, Reinforce=1, Gate=1, Propel=1

### containment

| Phrase | Dominant | Disrupt | Entropy | Chord |
| :--- | :--- | :--- | :--- | :--- |
| THE JAR HOLDS THE HONEY | Dampen (5) | 1 | 2.50 | (-0.19, +0.26, +0.43, +0.11) |
| THE NEST CRADLES THE EGG | Gate (4) | 0 | 2.83 | (-0.23, +0.29, +0.48, +0.00) |
| THE WALL KEEPS THE GARDEN | Dampen (6) | 0 | 2.55 | (-0.25, +0.24, +0.51, +0.00) |
| THE CUP RECEIVES THE WINE | Dampen (8) | 0 | 2.38 | (-0.21, +0.15, +0.64, +0.00) |
| THE CAVE HIDES THE BEAR | Dampen (8) | 2 | 2.09 | (-0.22, +0.14, +0.54, +0.10) |

- Mean chord: action_net=-0.220, structure=+0.215, flow=+0.522, transform=+0.042
- Std-dev:    action_net=+0.021, structure=+0.060, flow=+0.069, transform=+0.052
- Within-category avg cosine similarity: +0.968
- Dominant interaction consensus: `Dampen` (4/5)
- Dominant distribution: Dampen=4, Gate=1

### motion

| Phrase | Dominant | Disrupt | Entropy | Chord |
| :--- | :--- | :--- | :--- | :--- |
| THE BIRD FLIES SOUTH | Propel (5) | 0 | 2.52 | (+0.20, +0.12, +0.67, +0.00) |
| THE RIVER RUNS TO THE SEA | Gate (5) | 1 | 2.71 | (-0.03, +0.42, +0.46, +0.09) |
| THE ARROW SEEKS THE TREE | Dampen (5) | 0 | 2.78 | (-0.24, +0.26, +0.50, +0.00) |
| THE WOLF CHASES THE DEER | Dampen (7) | 0 | 2.27 | (-0.30, +0.14, +0.55, +0.00) |
| THE WIND CARRIES THE SEED | Dampen (6) | 0 | 2.73 | (-0.29, +0.18, +0.53, +0.00) |

- Mean chord: action_net=-0.132, structure=+0.226, flow=+0.544, transform=+0.018
- Std-dev:    action_net=+0.193, structure=+0.108, flow=+0.073, transform=+0.037
- Within-category avg cosine similarity: +0.843
- Dominant interaction consensus: `Dampen` (3/5)
- Dominant distribution: Dampen=3, Propel=1, Gate=1

### opening

| Phrase | Dominant | Disrupt | Entropy | Chord |
| :--- | :--- | :--- | :--- | :--- |
| THE DOOR OPENS TO THE GARDEN | Dampen (7) | 0 | 2.40 | (-0.16, +0.35, +0.49, +0.00) |
| THE BOOK REVEALS A SECRET | Propel (6) | 2 | 2.59 | (-0.03, +0.29, +0.59, +0.09) |
| THE EYE OPENS TO THE SKY | Dampen (4) | 3 | 3.02 | (-0.07, +0.06, +0.66, +0.21) |
| THE MAP UNFOLDS THE WORLD | Dampen (4) | 0 | 2.52 | (-0.14, +0.27, +0.59, +0.00) |
| THE FLOWER OPENS AT MORNING | Gate (7) | 0 | 2.40 | (+0.08, +0.44, +0.48, +0.00) |

- Mean chord: action_net=-0.065, structure=+0.283, flow=+0.562, transform=+0.060
- Std-dev:    action_net=+0.084, structure=+0.128, flow=+0.067, transform=+0.084
- Within-category avg cosine similarity: +0.904
- Dominant interaction consensus: `Dampen` (3/5)
- Dominant distribution: Dampen=3, Propel=1, Gate=1

### waiting

| Phrase | Dominant | Disrupt | Entropy | Chord |
| :--- | :--- | :--- | :--- | :--- |
| THE OWL WAITS FOR THE NIGHT | Dampen (5) | 0 | 2.66 | (-0.33, +0.21, +0.46, +0.00) |
| THE STONE LIES ON THE PATH | Propel (7) | 0 | 2.46 | (+0.07, +0.16, +0.77, +0.00) |
| THE CANDLE REMAINS UNLIT | Gate (7) | 0 | 2.46 | (-0.15, +0.30, +0.55, +0.00) |
| THE HOUSE SLEEPS AT DAWN | Dampen (6) | 0 | 2.09 | (+0.10, +0.12, +0.78, +0.00) |
| THE LETTER RESTS ON THE TABLE | Dampen (6) | 0 | 2.53 | (-0.15, +0.30, +0.55, +0.00) |

- Mean chord: action_net=-0.093, structure=+0.221, flow=+0.621, transform=+0.000
- Std-dev:    action_net=+0.157, structure=+0.072, flow=+0.130, transform=+0.000
- Within-category avg cosine similarity: +0.895
- Dominant interaction consensus: `Dampen` (3/5)
- Dominant distribution: Dampen=3, Propel=1, Gate=1


## Consistency ranking (highest within-category cosine = most internally coherent)

| Category | Within-avg cosine | Above noise floor? | Dominant consensus | Std (action,struct,flow,transform) |
| :--- | :--- | :--- | :--- | :--- |
| containment | +0.968 | +0.165 vs baseline | `Dampen` (4/5) | (0.02, 0.06, 0.07, 0.05) |
| opening | +0.904 | +0.101 vs baseline | `Dampen` (3/5) | (0.08, 0.13, 0.07, 0.08) |
| waiting | +0.895 | +0.092 vs baseline | `Dampen` (3/5) | (0.16, 0.07, 0.13, 0.00) |
| motion | +0.843 | +0.040 vs baseline | `Dampen` (3/5) | (0.19, 0.11, 0.07, 0.04) |
| breakage | +0.814 | +0.011 vs baseline | `Dampen` (2/5) | (0.21, 0.09, 0.09, 0.02) |