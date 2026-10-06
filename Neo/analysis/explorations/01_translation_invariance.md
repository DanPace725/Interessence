# Task 1: Translation Invariance Audit

How similar are signatures of the same concept across English (EN), Latin (LA), and Irish (GA)?

Cosine similarity is computed over the normalized word-aware chord vector `(action_net, structure, flow, transform)`. 1.0 = identical direction, 0.0 = orthogonal, negative = opposite direction.

Groups are read from `neo_phrase_corpus.csv`. Rows marked `experimental` have not been vetted by a native speaker; they are usable for orthography-driven signature analysis but should not be cited as canonical translations.

## Per-triplet summary (sorted least to most invariant by avg cosine)

| Concept | Members | Avg cosine | Avg Euclid | Distinct dominants |
| :--- | :--- | :--- | :--- | :--- |
| war breaks the gate | 3 | +0.723 | 0.400 | 3 |
| memory opens the gate | 3 | +0.828 | 0.332 | 2 |
| light breaks the darkness | 3 | +0.886 | 0.276 | 3 |
| freedom opens the door | 3 | +0.920 | 0.241 | 2 |
| water/fire teaching pair | 2 | +0.928 | 0.237 | 1 |
| care bends friction towards freedom | 2 | +0.937 | 0.215 | 1 |
| memory holds the stone / river remembers | 3 | +0.949 | 0.236 | 2 |

## Per-triplet detail

### care bends friction towards freedom

| Lang | Phrase | Dominant | Disrupt | Entropy | Chord (action,struct,flow,transform) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EN | CARE BENDS FRICTION TOWARDS FREEDOM | Dampen (7) | 2 | 2.80 | (-0.08, +0.43, +0.42, +0.07) |
| LA | CURA FRICTIONEM AD LIBERTATEM FLECTIT | Dampen (9) | 2 | 2.58 | (-0.20, +0.26, +0.48, +0.06) |

Pairs:

- EN vs LA: cosine=+0.937, euclid=0.215, dominants `Dampen`/`Dampen` (MATCH)

### freedom opens the door

| Lang | Phrase | Dominant | Disrupt | Entropy | Chord (action,struct,flow,transform) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EN | FREEDOM OPENS THE DOOR | Gate (5) | 0 | 2.55 | (+0.11, +0.35, +0.53, +0.00) |
| LA | LIBERTAS PORTAM APERIT | Propel (7) | 0 | 2.04 | (+0.26, +0.29, +0.45, +0.00) |
| GA | OSCLAIONN SAOIRSE AN DORAS | Propel (5) | 4 | 2.97 | (+0.27, +0.35, +0.27, +0.11) |

Pairs:

- EN vs LA: cosine=+0.963, euclid=0.177, dominants `Gate`/`Propel` (DIVERGE)
- EN vs GA: cosine=+0.870, euclid=0.322, dominants `Gate`/`Propel` (DIVERGE)
- LA vs GA: cosine=+0.928, euclid=0.223, dominants `Propel`/`Propel` (MATCH)

### light breaks the darkness

| Lang | Phrase | Dominant | Disrupt | Entropy | Chord (action,struct,flow,transform) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EN | LIGHT BREAKS THE DARKNESS | Anchor (4) | 2 | 2.87 | (-0.05, +0.41, +0.44, +0.10) |
| LA | LUX TENEBRAS FRANGIT | Gate (6) | 0 | 2.56 | (+0.16, +0.41, +0.43, +0.00) |
| GA | BRISEANN SOLAS AN DORCHADAS | Propel (7) | 2 | 2.62 | (+0.27, +0.40, +0.26, +0.07) |

Pairs:

- EN vs LA: cosine=+0.924, euclid=0.238, dominants `Anchor`/`Gate` (DIVERGE)
- EN vs GA: cosine=+0.796, euclid=0.376, dominants `Anchor`/`Propel` (DIVERGE)
- LA vs GA: cosine=+0.939, euclid=0.213, dominants `Gate`/`Propel` (DIVERGE)

### memory holds the stone / river remembers

| Lang | Phrase | Dominant | Disrupt | Entropy | Chord (action,struct,flow,transform) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EN | THE RIVER REMEMBERS THE STONE | Gate (10) | 0 | 2.42 | (+0.00, +0.44, +0.56, +0.00) |
| LA | MEMORIA LAPIDEM TENET | Gate (8) | 0 | 1.95 | (-0.06, +0.25, +0.69, +0.00) |
| GA | IS CUIMHIN LEIS AN ABHAINN | Propel (5) | 2 | 2.94 | (+0.13, +0.28, +0.53, +0.06) |

Pairs:

- EN vs LA: cosine=+0.948, euclid=0.234, dominants `Gate`/`Gate` (MATCH)
- EN vs GA: cosine=+0.958, euclid=0.215, dominants `Gate`/`Propel` (DIVERGE)
- LA vs GA: cosine=+0.941, euclid=0.259, dominants `Gate`/`Propel` (DIVERGE)

### memory opens the gate

| Lang | Phrase | Dominant | Disrupt | Entropy | Chord (action,struct,flow,transform) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EN | MEMORY OPENS A HIDDEN GATE | Gate (7) | 2 | 2.49 | (+0.06, +0.29, +0.55, +0.10) |
| LA | MEMORIA PORTAM ABDITAM APERIT | Gate (12) | 0 | 1.99 | (+0.06, +0.34, +0.59, +0.00) |
| GA | OSCLAIONN CUIMHNE AN GEATA | Fracture (3) | 6 | 3.22 | (-0.13, +0.35, +0.25, +0.26) |

Pairs:

- EN vs LA: cosine=+0.988, euclid=0.117, dominants `Gate`/`Gate` (MATCH)
- EN vs GA: cosine=+0.775, euclid=0.400, dominants `Gate`/`Fracture` (DIVERGE)
- LA vs GA: cosine=+0.721, euclid=0.478, dominants `Gate`/`Fracture` (DIVERGE)

### war breaks the gate

| Lang | Phrase | Dominant | Disrupt | Entropy | Chord (action,struct,flow,transform) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EN | WAR BREAKS THE GATE | Dampen (4) | 2 | 2.61 | (-0.28, +0.35, +0.29, +0.08) |
| LA | BELLUM PORTA FRANGIT | Propel (5) | 0 | 2.32 | (+0.24, +0.38, +0.38, +0.00) |
| GA | BRISEANN COGADH AN GEATA | Gate (4) | 4 | 2.95 | (-0.14, +0.46, +0.22, +0.18) |

Pairs:

- EN vs LA: cosine=+0.557, euclid=0.533, dominants `Dampen`/`Propel` (DIVERGE)
- EN vs GA: cosine=+0.927, euclid=0.210, dominants `Dampen`/`Gate` (DIVERGE)
- LA vs GA: cosine=+0.684, euclid=0.456, dominants `Propel`/`Gate` (DIVERGE)

### water/fire teaching pair

| Lang | Phrase | Dominant | Disrupt | Entropy | Chord (action,struct,flow,transform) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| EN | FIRE TEACHES WATER TO TURN | Dampen (8) | 2 | 2.52 | (-0.27, +0.29, +0.38, +0.07) |
| LA | AQUA IGNEM DOCET | Dampen (6) | 0 | 2.22 | (-0.41, +0.13, +0.46, +0.00) |

Pairs:

- EN vs LA: cosine=+0.928, euclid=0.237, dominants `Dampen`/`Dampen` (MATCH)

## Aggregate

- Triplets/pairs analyzed: 7
- Total cross-language pairs: 17
- Mean cosine across all pairs: +0.870
- Mean Euclidean distance: 0.288
- Dominant-interaction match rate: 29.4%
