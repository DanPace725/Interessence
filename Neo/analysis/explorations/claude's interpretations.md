All four investigations are wired into a single reproducible script (`Neo/analysis/explorations/run_explorations.py`) that writes a synthesis report plus per-task `.md` + `.csv` files. Here are the headline results.

## What the script does

`Neo/analysis/explorations/run_explorations.py` calls `analyze_phrase` from `neo_batch_signatures` directly, so re-running it always produces fresh outputs in `Neo/analysis/explorations/`:

- `REPORT.md` — synthesis across all four tasks
- `01_translation_invariance.{md,csv}` — Task 1
- `02_phase_turbulence.{md,csv}` — Task 2
- `03_semantic_categories.{md,csv}` + centroids CSV — Task 5
- `04_chord_clusters.{md,csv}` + neighbors CSV — Task 6

Run it with `python Neo\analysis\explorations\run_explorations.py`.

## Headlines per task

### Task 1 — Translation invariance is real but uneven

7 cross-language groups (EN/LA/GA where available, marked `corpus` vs `added`). Across 17 cross-language pairs:

- Mean cosine in chord space: **+0.865** (well above orthogonality)
- Dominant-interaction match rate: **29%**

So the *vector direction* is preserved across languages but the *peak interaction cell* gets relabeled by orthography most of the time. Most invariant: `memory holds the stone / river remembers` (cos +0.949). Least invariant: `war breaks the gate` (cos +0.723).

The clean takeaway is that you can't rely on the dominant-interaction label as a translation-invariant feature. Cosine similarity in `(action_net, structure, flow, transform)` space is a far better invariant.

### Task 2 — Phase Shift and Turbulence are reachable, just not from prose

Across 15 synthetic probes:

- **22 Phase Shift events** fired (was 0 in the natural corpus)
- **11 Turbulence events** fired (was 2 in the natural corpus)

Clean Phase-Shift probes like `AEUI`, `AEAEAE`, `UIEAIO` collapse to chord vector `(0, 0, 0, 1)` — pure transform. So the matrix cells are sound. The reason they don't appear in natural corpora is that Forfeda digraphs (`AE/OI/UI/EA/IO`) are sparse in real text and almost never adjacent. **The Forfeda axis is currently a binary "ritual register"** — present or absent, not a graded signal. That's actually a useful design property: those cells naturally distinguish *intentional* Forfeda-heavy inscription from organic transliteration.

### Task 5 — Semantic categories barely beat random

5 categories × 5 phrases (motion, containment, breakage, waiting, opening). I added a noise-floor calibration: 500 random 5-phrase subsets of the original 33-phrase corpus.

| Category | Within cosine | vs random baseline | Dominant consensus |
| :--- | :--- | :--- | :--- |
| containment | +0.978 | +0.183 | `Dampen` 4/5 |
| opening | +0.912 | +0.117 | `Dampen` 3/5 |
| waiting | +0.895 | +0.101 | `Dampen` 3/5 |
| motion | +0.843 | +0.049 | `Dampen` 3/5 |
| breakage | +0.814 | +0.020 | `Dampen` 2/5 |

Random 5-subset baseline: **mean +0.795, 95th percentile +0.900**.

**Two findings buried in this**: (a) the entire corpus already lives in a 0.8-cosine ball — chord space is currently *one big neighborhood*, not five separable categories; (b) only `containment` exceeds the 95th-percentile noise floor decisively. `breakage` is statistically indistinguishable from a random subset, despite having the most semantically unified meaning of any category I picked. The cross-category centroid cosine matrix is uniformly +0.95 to +1.00, confirming that all five "categories" point in essentially the same direction.

The reason `containment` looks tight is probably lexical: `JAR HOLDS HONEY`, `WALL KEEPS GARDEN`, `CUP RECEIVES WINE`, `CAVE HIDES BEAR` share verb-shape and letter mix. The reason `breakage` looks loose is that `SHATTERS / SNAPS / COLLAPSES / CRACKS / CRUMBLES` are lexically diverse — even though semantically they're a tight category. So **chord-space cohesion currently tracks lexical similarity, not semantic category**.

### Task 6 — Clusters track *language*, not just meaning

K-means K=4 over the 33-phrase corpus, labeled by deviation from the corpus centroid (so the cluster names are informative rather than all `+flow`):

| Cluster | Label | Size | Lang mix | Character |
| :--- | :--- | :--- | :--- | :--- |
| 0 | `+d_flow` | 6 | EN=5, LA=1 | The "pure conduit" cluster — `INTERESSENCE`, `THE NAME CHANGES THE SHAPE`, `MEMORY OPENS A HIDDEN GATE`, `MEMORIA LAPIDEM TENET`, `A SMALL KEY OPENS THE OLD LOCK`, `PIZZA ON TUESDAY`. The Neo project's *thesis phrases land here together* — they're flow-dominant gates with near-zero transform. |
| 1 | `+d_action_net` | 7 | EN=3, LA=2, GA=2 | The "Propel" cluster — `BELLUM PORTA FRANGIT`, `LIBERTAS PORTAM APERIT`, `BRISEANN SOLAS AN DORCHADAS`, `IS CUIMHIN LEIS AN ABHAINN`, `THE SPEIR IS BLUE`, `STONE LISTENS UNDER THE RAIN`, `THE BROKEN VESSEL HOLDS LIGHT`. Latin and Irish *forward-action mantras* dominate here. |
| 2 | `-d_action_net` | 12 | EN=9, LA=2, GA=1 | The "Dampen prose" cluster — most English phrases that didn't make it into another cluster. `COFFEE WAITS`, `MAP/TERRITORY`, `FOCS/HOUND`, `WAR BREAKS GATE`, `AQUA IGNEM DOCET`, etc. The default-mode English corpus. |
| 3 | `+d_structure` | 8 | EN=5, GA=3 | The "Anchor / Fracture" cluster — `ORDER LEARNS TO DREAM`, `OSCLAIONN CUIMHNE AN GEATA`, `BRISEANN COGADH AN GEATA`, `SNAIDHM A IARRANN CURAM`, `CHAOS FINDS A NARROW DOOR`. Irish phrases concentrate here, alongside structurally-rich English ones. |

The genuine cross-cutting finding is that **the chord vector currently carries a language fingerprint as its primary signal**. Latin clusters as positive-action, Irish as high-structure, English as negative-action. Concept identity is a secondary, weaker layer on top.

The most "average" phrases (closest to centroid) are `THE MAP IS NOT THE TERRITORY`, `CURA FRICTIONEM AD LIBERTATEM FLECTIT`, and `CARE BENDS FRICTION TOWARDS FREEDOM`. The most extreme are `ORDER LEARNS TO DREAM`, `THE SPEIR IS BLUE`, and `BRISEANN SOLAS AN DORCHADAS`.

## The big picture

The four investigations together produce one coherent story for the **Name = Form** thesis: **Neo currently encodes orthography first and semantics second.** Cross-language cosine of +0.87 says some semantic signal does survive, but cluster geometry, semantic-category cohesion, and dominant-interaction lookups all reveal that letter statistics are the dominant carrier. This is consistent with two readings:

1. *Intended*: "the same idea in a different language is genuinely a different inscription, and that's a feature."
2. *Bug*: "we want translations to cluster, so we need a phoneme-level or lemma-level normalization layer above the raw glyph sequence."

The audit doesn't pick between those — it makes the trade-off visible and quantifies it. Picking is a design decision, but now it's a decision with numbers attached.

If you want to pursue any thread further from here, I'd suggest:
- A 2D scatter visualization (in `Neo_viewer.html` or a new tool) of `flow` vs `action_net` colored by language — the language separation should jump out.
- A second semantic study with **lexically-controlled** phrases (same verb structure, different domains) to test whether chord cohesion is genuinely orthography or partially semantic.
- A phoneme-normalization experiment: transliterate via a phonemic intermediate (CMU-style for English, Latin's regular sound system, Irish broad/slender consonants) before glyph-mapping, then re-run the translation invariance audit — if cosine jumps from +0.87 to +0.95+, that's a strong signal that orthography is the contaminant.