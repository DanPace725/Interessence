# Neo Research Snapshot

Generated: 2026-05-06

This document summarizes the Neo analysis work done so far across Codex and
Claude Opus, synthesizes the emerging interpretation, and proposes next steps.

## 1. Current State Of The Work

Neo started as a NeOgham-derived inscription system: Latin letters and selected
digraphs map into a 5x5 glyph matrix organized by orientation and mark count.
Orientation supplies the glyph's structural role, while mark count supplies
magnitude. Adjacent glyphs then produce pairwise interactions such as `Gate`,
`Dampen`, `Propel`, `Anchor`, `Fracture`, `Invert`, `Turbulence`, and
`Phase Shift`.

The original workflow generated individual HTML interpretation pages for one
phrase at a time. Those pages were visually rich and interesting, but they made
larger analysis difficult. We have now moved from one-off readings toward a
repeatable corpus pipeline.

## 2. What Codex Added

### Batch Signature Pipeline

Codex added `Neo/neo_batch_signatures.py`, a batch analyzer that reads text,
CSV, JSON, or JSONL inputs and exports:

- `signatures.json`: full structured signatures.
- `signatures.jsonl`: one signature per line.
- `signatures.csv`: phrase-level table for spreadsheet analysis.
- `pair_events.csv`: every adjacent glyph interaction.
- `summary.md`: aggregate corpus overview.

Each signature includes:

- original phrase and Neo-normalized phrase
- glyph sequence
- glyph counts and group counts
- adjacent pair interactions
- dominant interaction
- disruptive event count
- interaction entropy
- word-aware chord vector
- transliteration substitutions
- sensitivity results for ambiguous substitutions

### Transliteration Layer

The initial analyzer only understood the core Neo alphabet. We added a
transliteration layer so unsupported letters can be normalized while preserving
metadata about the substitution.

The current reference map is:

| Source | Neo normalization |
| :--- | :--- |
| `K` | `C` |
| `V` | `F` |
| `J` | `G` |
| `Y` | `EA` |
| `Q` | `CW` |
| `X` | `CS` |

This matters because these are not neutral substitutions. `Y -> EA`, for
example, moves Y-bearing phrases into the Forfeda / transform register. That
significantly changes the field behavior compared with the earlier provisional
`Y -> I` mapping.

### Corpus Upgrade

The original `sample_phrases.txt` remains as a small starter list, but Codex
added `Neo/corpora/neo_phrase_corpus.csv` as a structured source of truth. It
contains metadata columns for:

- `corpus_id`
- `collection`
- `item_type`
- `concept_id`
- `concept`
- `language`
- `phrase`
- `provenance`
- `status`
- `notes`

This lets us group phrases by concept, language, source, and experimental role.
It also lets future analyses distinguish seed phrases, expansion phrases,
translation-audit phrases, semantic-category probes, and synthetic Forfeda
probes.

### Current Export Runs

Important generated output folders include:

- `Neo/analysis/signature_exports/sample`
- `Neo/analysis/signature_exports/expanded_sensitivity_qv`
- `Neo/analysis/signature_exports/expanded_reference_map`
- `Neo/analysis/signature_exports/unified_corpus_sensitivity`
- `Neo/analysis/signature_exports/unified_corpus_reference_map`

The most current run is `unified_corpus_reference_map`, using the structured
CSV corpus and the reference transliteration map.

That run now analyzes 118 items after adding controlled syntax and minimal-pair
collections. It produced:

- 1885 glyphs
- 1767 adjacent pair events
- 0 skipped unsupported characters
- 45 transliteration substitutions

The top interactions in that run were:

1. `Dampen`: 420
2. `Gate`: 348
3. `Propel`: 283
4. `Reinforce`: 199
5. `Anchor`: 157

The top structural groups were:

1. Diagonal / Flow: 634
2. Left / Resistance: 543
3. Cross / Structure: 323
4. Right / Action: 304
5. Backslash / Transform: 81

## 3. What Claude Added

Claude added a reproducible exploration script, and Codex then updated it to
load its analysis groups from the structured corpus CSV instead of keeping
translation groups, semantic categories, probes, and clustering inputs embedded
directly in Python:

`Neo/analysis/explorations/run_explorations.py`

It runs four investigations:

1. Translation invariance audit
2. Phase Shift / Turbulence reachability probes
3. Semantic-category consistency study
4. Chord-space clustering

It writes:

- `REPORT.md`
- `01_translation_invariance.md` and `.csv`
- `02_phase_turbulence.md` and `.csv`
- `03_semantic_categories.md` and `.csv`
- `03_semantic_categories_centroids.csv`
- `04_chord_clusters.md` and `.csv`
- `04_chord_neighbors.csv`

Claude's main summary is also captured in:

`Neo/analysis/explorations/claude's interpretations.md`

## 4. Claude's Main Findings

### Translation Invariance Is Real But Uneven

Across 7 cross-language concept groups and 17 cross-language pairs:

- Mean chord cosine similarity: about `+0.865`
- Dominant-interaction match rate: about `29%`

This means translated phrases often point in similar directions in chord space,
but they do not usually share the same dominant interaction label.

The key distinction:

- Chord vectors are comparatively translation-tolerant.
- Dominant interaction labels are orthography-sensitive.

### Forfeda Is Reachable But Rare In Natural Prose

The ordinary phrase corpus rarely produced `Phase Shift` or `Turbulence`, but
synthetic Forfeda-heavy probes produced them easily.

Examples such as `AEUI`, `AEAEAE`, and `UIEAIO` collapse into near-pure
transform space. This suggests that Forfeda is currently behaving like an
opt-in register rather than a continuously distributed feature of ordinary
phrases.

Claude described this as a "ritual register": present when deliberately invoked
or when specific orthographies create it, mostly absent otherwise.

### Semantic Categories Barely Beat Random

Claude tested categories such as motion, containment, breakage, waiting, and
opening. The result was sobering:

- The entire corpus already lives in a high-similarity chord neighborhood.
- Random subsets have high within-cosine similarity.
- Semantic categories only weakly separate from that baseline.

The strongest category was containment. Breakage, despite being semantically
coherent, did not strongly cluster. This suggests the current system tracks
letter shape, word form, and orthographic pattern more strongly than semantic
category.

### Clusters Track Language

K-means clustering over the current 38-phrase natural/translation corpus
suggests that chord vectors carry a language fingerprint:

- Latin tends to lean positive-action / Propel.
- Irish or Gaelic-looking text tends to lean structure / transform.
- English often leans negative-action / Dampen.

Concept identity appears to be present, but weaker than the orthographic and
language-shape signal.

## 5. Synthesized Interpretation

The strongest current interpretation is:

Neo is not yet a semantic translator. It is an inscription-physics instrument.

It measures the structure of a written form: the glyph geometry implied by its
letters, the flow/resistance/structure/transform balance created by that form,
and the local interactions produced by adjacent glyphs.

This means the system is currently orthographic first and semantic second.

That is not necessarily a flaw. It depends on the design goal.

If the thesis is "the same idea should produce the same field across languages,"
then the current system needs a phonemic, lemma-level, or semantic normalization
layer above raw spelling.

If the thesis is "the same idea in different languages is genuinely a different
inscription-body," then the current behavior is a feature. A translation is not
an equivalent signal. It is a sibling body shaped by a different language's
history, phonotactics, and orthography.

The second interpretation currently feels more native to Neo. The system seems
to reveal how meaning is embodied by inscription rather than abstracting meaning
away from inscription.

## 6. Emerging Patterns

### Flow Is The Default Gravity

Most phrases are flow-heavy because vowels map to diagonal / flow glyphs. This
creates a strong corpus-wide attractor.

Result: many phrases look similar in chord space even when their meanings differ.

### Gate And Dampen Are The Main Surface Weather

Across the current corpora, `Gate` and `Dampen` dominate. This reflects the
large number of diagonal-flow glyphs interacting with cross-structure and
left-resistance glyphs.

`Gate` often appears when flow meets structure.
`Dampen` often appears when flow meets resistance.

### Forfeda Carries Transform And Disruption

Forfeda glyphs strongly increase:

- `Fracture`
- `Invert`
- `Turbulence`
- `Phase Shift`
- `Transform` chord weight

The reference `Y -> EA` mapping makes Y-bearing phrases more transform-active
than the earlier provisional `Y -> I` mapping. This is important and should be
treated as a major design decision.

### Dominant Interaction Is A Local Label, Not A Deep Identity

Dominant interaction is useful, but not stable enough to be the main comparison
feature across languages.

Better comparison features:

- normalized chord vector
- group ratios
- transform load
- disruptive event density
- pair-event distributions
- distance from corpus centroid

### Language Shape Is A Primary Signal

Neo currently encodes language fingerprints strongly. That means cross-language
translation studies should always record language and provenance.

## 7. Current Caveats

1. Many translation entries are experimental and not vetted by native speakers.
2. The corpus is small.
3. The semantic-category study is not lexically controlled.
4. The current chord vector has a strong flow baseline.
5. Dominant interaction labels can overstate differences.
6. The transliteration layer is now more principled, but still interpretive.
7. `Y -> EA` should be re-run through the exploration reports because it changes
   transform behavior materially.

## 8. Recommended Next Steps

### 1. Re-run Claude's Exploration Script Against The Reference Map - Done

Claude's reports were generated before the final `Y -> EA`, `J -> G`, and
`X -> CS` reference mapping. This has now been re-run:

```powershell
python Neo\analysis\explorations\run_explorations.py
```

Current results in `REPORT.md`:

- Mean cross-language cosine: `+0.870`
- Dominant-interaction match rate: `29.4%`
- Phase Shift probe hits: `22`
- Turbulence probe hits: `11`
- Structured natural/translation corpus clustered: `38` phrases

Transform and disruptive counts rose where the reference map introduces
Forfeda, especially through `Y -> EA`.

### 2. Point Exploration Scripts At `neo_phrase_corpus.csv` - Done

`run_explorations.py` now reads translation groups, semantic categories,
Forfeda probes, and cluster inputs from `neo_phrase_corpus.csv`.

Goal achieved: the CSV is now the source of truth for these explorations.

### 3. Add Visualizations - Initial Version Done

`run_explorations.py` now generates:

- `05_chord_visualizations.html`
- `05_chord_visualizations.csv`

The first visualization report includes:

- `flow` vs `action_net`
- `flow` vs `structure`
- `structure` vs `transform`
- PCA over chord vectors

The current HTML colors points by language and provides hover labels for phrase,
dominant interaction, and coordinates.

Still useful future additions:

- collection
- dominant interaction
- concept group
- transform/disruption density

Those additional color modes would make the Forfeda register and concept-group
structure easier to compare visually.

### 4. Build Lexically Controlled Tests - Initial Version Done

The current semantic categories are too lexically variable, so Codex added an
initial controlled syntax collection to `neo_phrase_corpus.csv`:

- `THE X OPENS THE Y`
- `THE X HOLDS THE Y`
- `THE X BREAKS THE Y`
- `THE X WAITS NEAR THE Y`

Each frame uses the same five noun pairs. `run_explorations.py` now generates:

- `06_controlled_syntax.md`
- `06_controlled_syntax.csv`
- `06_controlled_syntax_centroids.csv`
- `06_controlled_syntax_noun_pairs.csv`

Current first-pass result:

- `waits_near`: within-cosine `+0.942`
- `opens`: within-cosine `+0.909`
- `breaks`: within-cosine `+0.897`
- `holds`: within-cosine `+0.885`

The frame centroids remain close. This suggests the shared sentence shell is
still very strong, though the `opens` and `waits_near` centroids begin to pull
apart enough to be worth testing with larger controlled sets.

### 5. Add Minimal Pair Studies - Initial Version Done

Codex added an initial `minimal_pair` collection:

- `GATE`, `FATE`, `LATE`, `MATE`, `RATE`
- `STONE`, `STORE`, `STORM`, `STERN`
- `CARE`, `CURE`, `CORE`, `CIRCE`
- `BREAK`, `BREAD`, `BREATHE`
- `LIGHT`, `NIGHT`, `RIGHT`, `SIGHT`

`run_explorations.py` now generates:

- `07_minimal_pairs.md`
- `07_minimal_pairs.csv`
- `07_minimal_pair_distances.csv`

Current first-pass result:

- Mean Euclidean movement for one-edit word pairs: `0.357`
- Most sensitive family: `gate_family`, avg pair Euclid `0.456`
- Least sensitive family: `care_family`, avg pair Euclid `0.078`

These results give us a practical scale for distinguishing meaningful
phrase-level movement from normal one-letter orthographic jitter.

### 6. Test Orthographic vs Phonetic Neo

Create a parallel experimental analyzer mode:

- raw orthographic Neo
- reference transliteration Neo
- phonetic-lite Neo
- possibly phoneme-based Neo later

Then ask:

- Do translations cluster more tightly under phonetic normalization?
- Does the language fingerprint weaken?
- Does semantic category signal strengthen?

### 7. Develop A Register Taxonomy

Potential registers:

- ordinary prose
- control/mundane
- translation
- ritual / Forfeda-heavy
- project thesis phrases
- synthetic probes

Each register may have its own expected field profile.

### 8. Add Attribution Reports

For each phrase, show which glyphs and pairs contribute most to:

- flow
- resistance
- structure
- transform
- disruptive event count

This will make interpretations less impressionistic.

## 9. Short Thesis Statement

Neo currently behaves like a geometry of written names.

It does not erase language differences to reveal a pure semantic essence.
Instead, it makes language differences measurable. The same concept, expressed
through different orthographies, becomes a different body with a related but
non-identical field.

That may be the most interesting version of the Name = Form thesis:

Meaning is not merely encoded by the name. Meaning is refracted through the
material structure of the name.


Updated chat response: 
Yes. It clarifies the picture quite a bit.

My updated read is:

Neo is **more form-sensitive than I previously appreciated**, but not in a trivial way. The controlled syntax and minimal pair tests suggest the system is not just “random orthographic noise”; it has a fairly consistent geometry. But that geometry is mostly responding to **inscriptional structure**, not semantic category.

The controlled syntax test is the big clue. All four frames stay high-cosine:

- `waits_near`: `+0.942`
- `opens`: `+0.909`
- `breaks`: `+0.897`
- `holds`: `+0.885`

That means the repeated shell `THE X ___ THE Y` is exerting a very strong field. The verb matters, but the sentence-body matters more. So I’d soften any earlier claim like “Neo may be detecting semantic categories” and restate it as: Neo may detect **stable phrase-forms that often correlate with semantic roles**, but it does not yet separate semantic content cleanly from syntax and orthography.

The minimal pairs add another important correction. A one-letter change can move a word a lot: average Euclid `0.357`, with `GATE/FATE/LATE/RATE` especially volatile. But `CARE/CURE/CORE/CIRCE` barely moves by comparison. So Neo’s sensitivity is **not uniformly high**. Some glyph neighborhoods are flexible and preserve identity; others are hinge points where a single letter reorients the field.

That makes the “Name = Form” thesis stronger, actually. Not because Neo proves meanings are preserved across names, but because it shows names have measurable local physics. A word is not a bag of letters; it has pressure points.

So my updated synthesis would be:

Neo is currently best understood as an **inscriptional dynamics system**. It measures how written forms generate fields. Meaning can show up indirectly when it is stabilized by repeated syntax, shared roots, language habits, or ritual/Forfeda choices. But meaning is not the primary layer yet.

The most interesting new distinction is:

- **Phrase-level tests** show strong shell/syntax gravity.
- **Word-level tests** show local glyph sensitivity and hinge letters.
- **Translation tests** show related-but-nonidentical language bodies.
- **Forfeda tests** show an intentional transform register.

That feels cleaner than where we were before. Neo is less like a semantic decoder, more like a way to study the geometry of inscription.