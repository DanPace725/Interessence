# IW Language Simulator

This directory is a working area for developing the early IW language simulator.

The goal is not to generate a finished conlang from the top down. The goal is to model a language ecology: events, places, materials, bodies, sounds, gestures, taboos, and repeated use gradually produce roots, names, drift paths, semantic fossils, and later proto-Neo mappings.

## Source Documents

- `../early_iw_language_and_crystal_culture_seed.md`
- `../iw_core_grammar_five_domains.md`
- `../iw_character_braid_narrative_structure.md`
- `../../Neo/docs/Neo.md`
- `../../Neo/docs/NeOgham.md`
- `../../Neo/analysis/explorations/NEO_RESEARCH_SNAPSHOT.md`

## Directory Layout

- `DESIGN_NOTES.md`: programmatic approach and modeling assumptions.
- `data/`: hand-authored JSON seed data for domains, events, roles, places, and root examples.
- `data/phonology.json`: first-pass sound inventory, register rules, name routes, and root growth plan.
- `data/later_alphabet.json`: later 15-letter mouth-family compression used to audit root evolution toward the alphabet concept.
- `data/phrase_probes.json`: editable phrase probes for hearing roots in short utterances.
- `schemas/`: machine-readable schemas for root entries and later generated artifacts.
- `scripts/`: future simulator scripts.
- `outputs/`: generated ledgers, name lists, drift reports, and Neo bridge reports.
- `tests/`: future validation checks for consistency and reproducibility.

## First Milestone

The first useful milestone is a deterministic prototype that takes a small set of world events and seeded roots, then produces:

- a root ledger with ancestry,
- descendant forms across a few generations,
- candidate personal/place/material names,
- taboo and register notes,
- a proto-Neo mapping for each root family.

## Run

```powershell
python .\Novel\language_sim\scripts\build_language_outputs.py
```

This writes the first generated reports into `outputs/`.

Generated reports:

- `root_ledger.md`
- `name_candidates.md`
- `proto_neo_bridge.md`
- `root_quality_report.md`
- `sound_taste_report.md`
- `phrase_samples.md`
- `evolution_fastforward.md`
- `provisional_alphabet.md`
- `proto_words.md`
- `proto_word_collapse.md`
- `stable_letter_names_experiment.md`
- `vowel_combination_grid.md`
- `phonetic_function_matrix.md`
- `neo_phonetic_analogy_matrix.md`
- `later_alphabet_compression_audit.md`
- `complete_later_alphabet.md`
- `word_combination_ruleset.md`
- `lexicon_first_batch.md`
- `lexicon_review.md`
- `lexicon_expansion_report.md`

## Root Count

The current 28-root set is enough to prove the mechanism and begin answering thin-family pressure from the lexicon review: event ancestry, drift, register routes, generated names, mouth-family coverage, and Neo bridge mappings.

It is not enough for the full world. A good next target is roughly 50 roots for one regional language ecology, then roughly 100 roots once the system needs broad personal, place, material, ritual, technical, and lineage naming without repeating the same root ancestors too often.

The prototype should stay inspectable. Prefer plain data files and readable reports before building a larger engine.
