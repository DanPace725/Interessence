# Task 6: Chord-Space Clustering

K-means (K=4) on the normalized word-aware chord vectors of the 38-phrase structured natural/translation corpus, plus per-axis rankings and centroid-distance extremes.

## Corpus centroid

- action_net=-0.047, structure=+0.316, flow=+0.465, transform=+0.045

## K-means clusters (K=4)

### Cluster 0: `+d_action_net` (14 members; lang mix EN=6, LA=4, GA=3, NEO=1)
- Mean chord: action_net=+0.165, structure=+0.300, flow=+0.498, transform=+0.036
- Delta vs corpus centroid: action_net=+0.212, structure=-0.015, flow=+0.034, transform=-0.008

| Phrase | Dominant | Chord |
| :--- | :--- | :--- |
| INTERESSENCE | Gate | (+0.03, +0.31, +0.67, +0.00) |
| A SMALL KEY OPENS THE OLD LOCK | Propel | (+0.10, +0.10, +0.65, +0.14) |
| MEMORIA PORTAM ABDITAM APERIT | Gate | (+0.06, +0.34, +0.59, +0.00) |
| THE BROKEN VESSEL HOLDS LIGHT | Propel | (+0.18, +0.25, +0.57, +0.00) |
| THE SPEIR IS BLUE | Reinforce | (+0.30, +0.13, +0.57, +0.00) |
| MEMORY OPENS A HIDDEN GATE | Gate | (+0.06, +0.29, +0.55, +0.10) |
| FREEDOM OPENS THE DOOR | Gate | (+0.11, +0.35, +0.53, +0.00) |
| IS CUIMHIN LEIS AN ABHAINN | Propel | (+0.13, +0.28, +0.53, +0.06) |
| PIZZA ON TUESDAY | Gate | (+0.13, +0.31, +0.53, +0.03) |
| LIBERTAS PORTAM APERIT | Propel | (+0.26, +0.29, +0.45, +0.00) |
| LUX TENEBRAS FRANGIT | Gate | (+0.16, +0.41, +0.43, +0.00) |
| BELLUM PORTA FRANGIT | Propel | (+0.24, +0.38, +0.38, +0.00) |
| OSCLAIONN SAOIRSE AN DORAS | Propel | (+0.27, +0.35, +0.27, +0.11) |
| BRISEANN SOLAS AN DORCHADAS | Propel | (+0.27, +0.40, +0.26, +0.07) |

### Cluster 1: `-d_flow` (3 members; lang mix GA=2, EN=1)
- Mean chord: action_net=-0.099, structure=+0.468, flow=+0.225, transform=+0.208
- Delta vs corpus centroid: action_net=-0.052, structure=+0.153, flow=-0.240, transform=+0.163

| Phrase | Dominant | Chord |
| :--- | :--- | :--- |
| OSCLAIONN CUIMHNE AN GEATA | Fracture | (-0.13, +0.35, +0.25, +0.26) |
| BRISEANN COGADH AN GEATA | Gate | (-0.14, +0.46, +0.22, +0.18) |
| ORDER LEARNS TO DREAM | Anchor | (-0.02, +0.59, +0.20, +0.18) |

### Cluster 2: `-d_action_net` (14 members; lang mix EN=10, LA=3, GA=1)
- Mean chord: action_net=-0.261, structure=+0.229, flow=+0.481, transform=+0.029
- Delta vs corpus centroid: action_net=-0.214, structure=-0.087, flow=+0.017, transform=-0.016

| Phrase | Dominant | Chord |
| :--- | :--- | :--- |
| MEMORIA LAPIDEM TENET | Gate | (-0.06, +0.25, +0.69, +0.00) |
| THE NAME CHANGES THE SHAPE | Gate | (-0.09, +0.24, +0.67, +0.00) |
| COFFEE WAITS BESIDE THE WINDOW | Dampen | (-0.33, +0.04, +0.63, +0.00) |
| AIT FHRITHCHUIMILTE | Dampen | (-0.25, +0.14, +0.55, +0.07) |
| THE FOCS AND THE HOUND | Dampen | (-0.32, +0.17, +0.52, +0.00) |
| THE MAP IS NOT THE TERRITORY | Dampen | (-0.15, +0.29, +0.48, +0.08) |
| CURA FRICTIONEM AD LIBERTATEM FLECTIT | Dampen | (-0.20, +0.26, +0.48, +0.06) |
| AQUA IGNEM DOCET | Dampen | (-0.41, +0.13, +0.46, +0.00) |
| THE MARKET CLOSES AT NOON | Gate | (-0.25, +0.30, +0.45, +0.00) |
| MUSIC BENDS THE QUIET ROOM | Gate | (-0.31, +0.22, +0.43, +0.04) |
| THE CHILD DRAWS A CIRCLE | Dampen | (-0.41, +0.18, +0.41, +0.00) |
| FIRE TEACHES WATER TO TURN | Dampen | (-0.27, +0.29, +0.38, +0.07) |
| LIGHT RETURNS THROUGH THE CRACK | Gate | (-0.34, +0.36, +0.30, +0.00) |
| WAR BREAKS THE GATE | Dampen | (-0.28, +0.35, +0.29, +0.08) |

### Cluster 3: `+d_structure` (7 members; lang mix EN=6, GA=1)
- Mean chord: action_net=-0.020, structure=+0.455, flow=+0.466, transform=+0.024
- Delta vs corpus centroid: action_net=+0.027, structure=+0.139, flow=+0.001, transform=-0.021

| Phrase | Dominant | Chord |
| :--- | :--- | :--- |
| THE RIVER REMEMBERS THE STONE | Gate | (+0.00, +0.44, +0.56, +0.00) |
| STONE LISTENS UNDER THE RAIN | Gate | (+0.06, +0.40, +0.53, +0.00) |
| THE TRAIN ARRIVES AFTER SUNSET | Gate | (+0.06, +0.45, +0.49, +0.00) |
| LIGHT BREAKS THE DARKNESS | Anchor | (-0.05, +0.41, +0.44, +0.10) |
| CARE BENDS FRICTION TOWARDS FREEDOM | Dampen | (-0.08, +0.43, +0.42, +0.07) |
| SNAIDHM A IARRANN CURAM | Gate | (-0.05, +0.53, +0.42, +0.00) |
| CHAOS FINDS A NARROW DOOR | Gate | (-0.08, +0.52, +0.40, +0.00) |

## Per-axis extremes

### action_net

Lowest:
- -0.409 THE CHILD DRAWS A CIRCLE
- -0.407 AQUA IGNEM DOCET
- -0.337 LIGHT RETURNS THROUGH THE CRACK
- -0.333 COFFEE WAITS BESIDE THE WINDOW
- -0.315 THE FOCS AND THE HOUND

Highest:
- +0.303 THE SPEIR IS BLUE
- +0.273 BRISEANN SOLAS AN DORCHADAS
- +0.266 OSCLAIONN SAOIRSE AN DORAS
- +0.259 LIBERTAS PORTAM APERIT
- +0.239 BELLUM PORTA FRANGIT

### structure

Lowest:
- +0.038 COFFEE WAITS BESIDE THE WINDOW
- +0.103 A SMALL KEY OPENS THE OLD LOCK
- +0.131 THE SPEIR IS BLUE
- +0.132 AQUA IGNEM DOCET
- +0.136 AIT FHRITHCHUIMILTE

Highest:
- +0.595 ORDER LEARNS TO DREAM
- +0.528 SNAIDHM A IARRANN CURAM
- +0.524 CHAOS FINDS A NARROW DOOR
- +0.456 BRISEANN COGADH AN GEATA
- +0.447 THE TRAIN ARRIVES AFTER SUNSET

### flow

Lowest:
- +0.203 ORDER LEARNS TO DREAM
- +0.225 BRISEANN COGADH AN GEATA
- +0.248 OSCLAIONN CUIMHNE AN GEATA
- +0.256 BRISEANN SOLAS AN DORCHADAS
- +0.271 OSCLAIONN SAOIRSE AN DORAS

Highest:
- +0.686 MEMORIA LAPIDEM TENET
- +0.671 THE NAME CHANGES THE SHAPE
- +0.669 INTERESSENCE
- +0.651 A SMALL KEY OPENS THE OLD LOCK
- +0.629 COFFEE WAITS BESIDE THE WINDOW

### transform

Lowest:
- +0.000 THE RIVER REMEMBERS THE STONE
- +0.000 THE BROKEN VESSEL HOLDS LIGHT
- +0.000 STONE LISTENS UNDER THE RAIN
- +0.000 THE CHILD DRAWS A CIRCLE
- +0.000 CHAOS FINDS A NARROW DOOR

Highest:
- +0.263 OSCLAIONN CUIMHNE AN GEATA
- +0.183 ORDER LEARNS TO DREAM
- +0.177 BRISEANN COGADH AN GEATA
- +0.143 A SMALL KEY OPENS THE OLD LOCK
- +0.112 OSCLAIONN SAOIRSE AN DORAS

## Centroid distance

Phrases closest to the corpus centroid (most 'average'):

- 0.110 LIGHT BREAKS THE DARKNESS
- 0.117 THE MAP IS NOT THE TERRITORY
- 0.132 CARE BENDS FRICTION TOWARDS FREEDOM
- 0.148 MEMORY OPENS A HIDDEN GATE
- 0.163 CURA FRICTIONEM AD LIBERTATEM FLECTIT

Phrases farthest from the corpus centroid (most extreme):

- 0.434 COFFEE WAITS BESIDE THE WINDOW
- 0.411 THE SPEIR IS BLUE
- 0.408 ORDER LEARNS TO DREAM
- 0.407 AQUA IGNEM DOCET
- 0.393 THE CHILD DRAWS A CIRCLE
