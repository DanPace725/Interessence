# Scripts

Future simulator scripts will live here.

The first script should:

1. load `../data/domains.json`, `../data/events.json`, `../data/roots.seed.json`, and `../data/phonology.json`,
2. validate root entries against `../schemas/root_entry.schema.json`,
3. apply deterministic drift rules,
4. emit reports into `../outputs/`.

Run it from the repository root:

```powershell
python .\Novel\language_sim\scripts\build_language_outputs.py
```
