# Neo Corpora

`neo_phrase_corpus.csv` is the structured source of truth for batch signature runs.

Use `sample_phrases.txt` as a small legacy/starter list, but prefer the CSV when
you care about language, concept group, provenance, or experiment type.

## Columns

- `corpus_id`: stable row identifier.
- `collection`: broad source set, such as `seed`, `expanded`, `translation_added`,
  `semantic_category`, `forfeda_probe`, `controlled_syntax`, or `minimal_pair`.
- `item_type`: `phrase`, `word`, or `probe`.
- `concept_id`: machine-friendly concept grouping.
- `concept`: human-readable concept grouping.
- `language`: language/register code, currently `EN`, `LA`, `GA`, or `NEO`.
- `phrase`: text sent through the Neo analyzer.
- `provenance`: where the row came from.
- `status`: `working`, `control`, `experimental`, or `synthetic`.
- `notes`: freeform caution or description.

## Experiment Collections

- `controlled_syntax`: repeated English frames such as `THE X OPENS THE Y`,
  `THE X HOLDS THE Y`, `THE X BREAKS THE Y`, and `THE X WAITS NEAR THE Y`.
  These are designed to separate verb/frame effects from noun-pair effects.
- `minimal_pair`: word families such as `GATE/FATE/LATE/MATE/RATE` and
  `LIGHT/NIGHT/RIGHT/SIGHT`. These are designed to measure how sharply small
  orthographic changes move a Neo signature.

## Run

```powershell
python Neo\neo_batch_signatures.py `
  --input Neo\corpora\neo_phrase_corpus.csv `
  --phrase-column phrase `
  --out-dir Neo\analysis\signature_exports\unified_corpus_sensitivity `
  --label "unified phrase corpus sensitivity" `
  --missing sensitivity
```

## Current Reference Transliteration

The Neo alphabet is still 25 glyphs, so non-native Latin letters are handled in
the analyzer's transliteration layer:

- `K -> C`
- `Q -> CW`
- `V -> F`
- `J -> G`
- `X -> CS`
- `Y -> EA`

These substitutions are recorded in the export metadata instead of being hidden.
