# IW Language Simulator Design Notes

## Working Thesis

The early IW language should develop from survivable relations before it becomes a formal naming or inscription system.

The simulator should model:

1. an event pressure,
2. a multimodal response,
3. world feedback,
4. social selection,
5. generational drift,
6. register specialization,
7. naming reuse,
8. later proto-Neo abstraction.

This keeps the language useful for naming systems while giving each name an implied buried history.

## Core Unit

The core unit is not a word. It is a root lineage.

```text
event pressure -> sound/gesture/posture -> world response -> social memory -> drift -> descendant forms -> names -> proto-Neo mapping
```

A root lineage should preserve enough ancestry that a name can be read backward into culture, ecology, and story.

## Model Layers

### 1. World Substrate

Stable background categories:

- domains: crystals, metals, biology, language, place
- bias families: Action, Resistance, Binding, Flow, Mutation
- materials: emitters, absorbers, memory gems, conduits, volatile crystals, metals, crystalline-metal mixtures
- places: caves, gardens, rivers, borders, ruins, roads, shrines, dead zones
- roles: listener, carrier, hush-keeper, cutter, washer, root-tender, metal-sorter, rememberer

These categories should not force a meaning. They should provide recurring pressures.

### 2. Event Engine

Events create selection pressure.

Examples:

- child saved
- hunter killed
- crystal cracked
- cave answered
- fire started
- wound healed
- metal rang wrong
- burial phrase preserved
- trade misunderstanding
- purification succeeded
- portal-like accident occurred

An event should expose:

- what happened,
- where it happened,
- who carried the memory,
- which material or place responded,
- what response helped or harmed,
- what taboo or practice followed.

### 3. Multimodal Utterance

Early language is not purely spoken. A response can include:

- sound shape,
- handshape,
- body orientation,
- distance from body,
- repetition,
- sequence,
- face/gaze,
- breath or silence,
- context requirement.

This is the main bridge between early language and later Neo.

### 4. Social Selection

Forms survive because they become useful, feared, beautiful, ritualized, teachable, or institutionally preserved.

Selection factors:

- survival utility,
- danger if omitted,
- ease of child learning,
- role ownership,
- ritual prestige,
- trade usefulness,
- taboo pressure,
- specialist formalization.

### 5. Drift

Drift should be event-indexed, not arbitrary.

Possible drift channels:

- phonetic erosion,
- gesture simplification,
- posture loss,
- taboo hardening,
- metaphor expansion,
- register split,
- folk etymology,
- translation into trade speech,
- specialist compression into notation.

### 6. Naming

Names should be generated from root lineages, not syllable aesthetics alone.

Name types:

- personal names,
- place names,
- material names,
- tool names,
- ritual names,
- warning names,
- lineage or kin names.

Each generated name should carry:

- surface form,
- literal or current gloss,
- root ancestry,
- original event pressure,
- register,
- taboo/safety condition if any,
- narrative fragment,
- proto-Neo mapping.

### 7. Phonology And Register

The first phonology layer should stay light. It should constrain the flavor of generated forms without pretending the language is complete.

Current register routes are stored in `data/phonology.json`:

- first event: raw pressure response,
- daily / child speech: softened and eroded frequent-use form,
- ritual / taboo-preserved: primary bias marker preserved,
- specialist / proto-Neo facing: technical compression toward bias notation,
- place fossil: older form compacted through place memory,
- trade speech: smoother public form.

Name generation should route through these registers. For example, a place name should not be a personal-name suffix with a different label; it should preserve place-memory differently than a tool name, ritual title, or public trade name.

## Neo Bridge

The simulator should remain consistent with Neo by mapping early language features into later abstraction:

| Early Language Feature | Later Neo Feature |
|---|---|
| voice root | glyph identity or phonetic residue |
| handshape | relational operator |
| body orientation | glyph orientation |
| repetition | mark-count magnitude |
| sequence | inscription order |
| posture | activation condition |
| ritual context | substrate requirement |
| story residue | rune history |
| taboo | constraint rule |
| place memory | closure basin |

Neo should not be treated as the source of magic in the simulator. Neo is the later formalization of patterns that the world, body, and culture had already selected.

## Data First

Start with hand-authored JSON data:

- domains and bias families,
- event templates,
- root seeds,
- place/material examples,
- social roles.

Then write a small deterministic script that can:

1. combine event + context + carrier role,
2. select or evolve a root response,
3. apply simple drift rules,
4. emit descendant names,
5. write a human-readable ledger.

The first script should be deterministic by default. Randomness can be added later with explicit seeds.

## Validation Questions

A generated root or name is useful if:

- it has a concrete first context,
- its form changed for a legible reason,
- its current meaning is not identical to its original pressure,
- it can belong to at least one register,
- it can plausibly map to a later Neo bias family,
- it creates a scene possibility,
- it does not feel like generic fantasy phonotactics pasted onto the world.

## First Prototype Target

Prototype size:

- 5 domains,
- 5 bias families,
- 10 event templates,
- 8 to 12 seeded roots,
- 3 to 5 generations of drift,
- 20 to 40 generated descendants,
- 15 to 25 candidate names.

The first target reached 20 seed roots and 5 name routes, yielding 100 candidate names. The current targeted batch expands this to 28 roots and 140 candidate names so the lexicon can test SZ, TH, CHSH, and H pressure more honestly.

Root growth guidance:

- 20 roots: enough for mechanism validation and taste-testing.
- 28 roots: enough for a first targeted repair pass after lexicon review.
- 50 roots: enough for one regional ecology with less repetition.
- 100 roots: enough to start supporting broad world naming across people, places, materials, tools, rituals, offices, and technical terms.

Outputs:

- `outputs/root_ledger.md`
- `outputs/name_candidates.md`
- `outputs/proto_neo_bridge.md`

The current prototype target is implemented by `scripts/build_language_outputs.py`.

## Phase Status

Phase 1, root model stabilization, is considered provisionally complete when:

- every root has a concrete first context,
- every root has gesture and posture,
- every root has danger and world response,
- every root has at least two social carriers,
- every root has semantic drift depth,
- every root has a taboo or constraint,
- every root has a valid primary and secondary Neo bias,
- every root has at least three early-feature bridge mappings.

The generated `outputs/root_quality_report.md` checks this. The current threshold for moving into sound taste work is 8/10 per root.

Phase 2 is sound taste: tune the language's inventory, register operations, and name routes until generated forms feel like early IW rather than generic syllable output or late Neo notation.

## Proto-Word Layer

The current root entries are still meaning-bundles. To move toward a more realistic language history, the simulator now expands roots into proto-words before alphabet formation.

The model is:

```text
root bundle -> atomic proto-words -> usage drift -> semi-formal alphabet -> later Neo compression
```

Each proto-word should carry one meaning. This makes the alphabet a historical compression of repeated usage rather than an immediate collapse of broad semantic bundles.

Current generated reports:

- `outputs/proto_words.md`: atomic utterance-meaning units generated from the current root set.
- `outputs/proto_word_collapse.md`: how those units settle back toward the provisional alphabet.
- `outputs/stable_letter_names_experiment.md`: a middle-path experiment where proto-words accelerate and collapse into a learnable set of root-derived letter names.

This layer should become the main place to expand toward richer language behavior. The root set can stay relatively stable while proto-words grow, split, resist collapse, or become derived letters.

## Lexicon Layer

The dictionary should grow from the roots outward rather than being invented as a flat word list.

The first lexicon pass uses three entry types:

- root sound-events,
- adjacent proto-words split from semantic drift paths,
- phrase entries that may become standalone words if repeated use gives them social weight.

The later 15-letter alphabet can annotate each entry with mouth-family traces, but it should not linearly determine the word shape. A word can grow toward the alphabet historically without being generated from alphabet symbols.

Generated report:

- `outputs/lexicon_first_batch.md`: current dictionary pass plus thinness pressure and draft iteration rules.

The first rule set is intentionally provisional:

1. keep root ancestry visible,
2. split adjacent words only when they narrow the root bundle,
3. promote phrases only through repeated scene, role, or taboo use,
4. use alphabet traces as annotation, not source spelling,
5. expand thin mouth families through embodied roots first,
6. split overused roots before letting them dominate the lexicon.

Word-shape constraints now sit between phrase fusion and dictionary promotion:

- most words should be 3-8 characters,
- 10 characters is the common upper limit,
- 15 characters is the rare hard limit,
- identical vowels collapse at joins,
- consonant joins preserve the earlier consonant posture and drop the entering consonant cluster when no older fusion rule handles the boundary,
- no accepted headword should keep more than three consonant characters in a row.

Generated report:

- `outputs/word_combination_ruleset.md`: provisional word-combination constraints and examples.
- `outputs/lexicon_review.md`: promote/watch/ritual-only review flags and targeted root-expansion pressure.
- `outputs/lexicon_expansion_report.md`: second-pass word updates, phrase-growth examples, and emergent lexicon pressure.

The review pass should happen before adding a new root batch. New roots should answer a pressure surfaced by the dictionary, such as a thin mouth family, an overused root, a too-short adjacent form, or a long phrase that needs a shorter everyday descendant.

## Later Mouth-Family Alphabet

The later 15-letter / roughly 30-sound system is not the primitive source of IW. It is a compressed analytical alphabet created after generations of embodied speech.

The working chronology is:

```text
embodied sound-event -> repeated root -> noticed mouth family -> 15-letter compression -> script/register split -> later Neo reinterpretation
```

The core distinction is:

```text
early root = performed survival event
later letter = fossilized mouth-operation
```

The consonant layer compresses to 10 mouth families:

- `FV`: lip-teeth friction, light `f` / deep `v`
- `PB`: lip closure/release, light `p` / deep `b`
- `SZ`: ridge friction, light `s` / deep `z`
- `TH`: tongue-teeth threshold, light `th` / deep `dh`
- `DT`: tongue-up closure, light `t` / deep `d`
- `KG`: back-mouth closure, light `k` / deep `g`
- `MN`: nasal/internal binding, position contrast `m` / `n`
- `LR`: liquid routing, routing contrast `l` / `r`
- `CHSH`: release-friction scrape, duration or release contrast `ch` / `sh`
- `H`: breath gate, breath-phase contrast `h` / held or forced venting

The vowel layer compresses to 5 fields:

- `A`: open resonance
- `E`: narrow attention
- `I`: fine line / high thread
- `O`: rounded containment
- `U`: deep return / inner channel

Light/deep is only one contrast axis. It applies cleanly to `FV`, `PB`, `SZ`, `TH`, `DT`, and `KG`. `MN`, `LR`, `CHSH`, and `H` use position, routing, duration, release, or breath-phase contrasts instead.

This layer is defined in `data/later_alphabet.json` and audited by `outputs/later_alphabet_compression_audit.md`.

When revising roots, do not start by assigning letters. Start with:

- embodied root: sound, gesture, posture,
- survival function,
- mouth family,
- light/deep or other contrast state,
- vowel field,
- closure behavior,
- later compression,
- semantic drift.

## Open Design Questions

1. Should early IW have one proto-language ecology or several regional ecologies?
2. How much should phonology be constrained before the first prototype?
3. Are gesture and posture stored as symbolic tags, spatial vectors, or prose annotations at first?
4. Should the Neo bridge map to existing glyph letters immediately, or only to bias families until the language stabilizes?
5. How much should place memory affect drift compared with social carrier roles?
6. Which roots should be regional rather than shared across early IW?
7. At what point should generated forms be checked against Neo glyph/chord signatures?
