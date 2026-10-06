import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Novel.language_sim.scripts import build_language_outputs as builder


class LanguageOutputTests(unittest.TestCase):
    def test_seed_roots_validate_and_hit_first_target(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")

        self.assertEqual(len(roots), 28)
        self.assertEqual(len(phonology["name_routes"]), 5)
        self.assertEqual(builder.validate_roots(roots), [])
        self.assertNotIn("ash", {root["proto_sound"] for root in roots})
        self.assertNotIn("dor", {root["proto_sound"] for root in roots})
        self.assertNotIn("kor", {root["proto_sound"] for root in roots})
        self.assertNotIn("wai", {root["proto_sound"] for root in roots})
        self.assertIn("thae", {root["proto_sound"] for root in roots})
        self.assertIn("zai", {root["proto_sound"] for root in roots})
        self.assertIn("dhae", {root["proto_sound"] for root in roots})
        self.assertIn("cha", {root["proto_sound"] for root in roots})
        self.assertIn("hu", {root["proto_sound"] for root in roots})

    def test_reports_are_generated(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(builder, "OUTPUT_DIR", Path(tmp)):
                builder.build_outputs()

            manifest = json.loads((Path(tmp) / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["root_count"], 28)
            self.assertEqual(manifest["proto_word_count"], 66)
            self.assertEqual(manifest["name_candidate_count"], 140)
            self.assertEqual(manifest["name_route_count"], 5)
            self.assertEqual(manifest["phrase_probe_count"], 23)
            self.assertGreaterEqual(manifest["alphabet_attractor_count"], 5)
            self.assertGreaterEqual(manifest["provisional_letter_count"], 25)
            self.assertGreaterEqual(manifest["stable_letter_name_count"], 20)
            self.assertLessEqual(manifest["stable_letter_name_count"], 40)
            self.assertGreaterEqual(manifest["vowel_grid_onset_count"], 10)
            self.assertEqual(manifest["vowel_grid_probe_count"], manifest["vowel_grid_onset_count"] * 25)
            self.assertEqual(manifest["phonetic_function_onset_count"], manifest["vowel_grid_onset_count"])
            self.assertEqual(manifest["phonetic_analogy_count"], 8)
            self.assertEqual(manifest["later_consonant_family_count"], 10)
            self.assertEqual(manifest["later_vowel_family_count"], 5)
            self.assertEqual(manifest["complete_later_alphabet_letter_count"], 15)
            self.assertGreaterEqual(manifest["lexicon_first_batch_entry_count"], 89)
            self.assertIn("promote", manifest["lexicon_review_status_counts"])
            self.assertIn("watch", manifest["lexicon_review_status_counts"])
            self.assertEqual(manifest["later_missing_consonant_families"], [])
            self.assertEqual(manifest["later_missing_vowel_families"], [])
            self.assertTrue((Path(tmp) / "root_ledger.md").exists())
            self.assertTrue((Path(tmp) / "name_candidates.md").exists())
            self.assertTrue((Path(tmp) / "proto_neo_bridge.md").exists())
            self.assertTrue((Path(tmp) / "root_quality_report.md").exists())
            self.assertTrue((Path(tmp) / "sound_taste_report.md").exists())
            self.assertTrue((Path(tmp) / "phrase_samples.md").exists())
            self.assertTrue((Path(tmp) / "evolution_fastforward.md").exists())
            self.assertTrue((Path(tmp) / "provisional_alphabet.md").exists())
            self.assertTrue((Path(tmp) / "proto_words.md").exists())
            self.assertTrue((Path(tmp) / "proto_word_collapse.md").exists())
            self.assertTrue((Path(tmp) / "stable_letter_names_experiment.md").exists())
            self.assertTrue((Path(tmp) / "vowel_combination_grid.md").exists())
            self.assertTrue((Path(tmp) / "phonetic_function_matrix.md").exists())
            self.assertTrue((Path(tmp) / "neo_phonetic_analogy_matrix.md").exists())
            self.assertTrue((Path(tmp) / "later_alphabet_compression_audit.md").exists())
            self.assertTrue((Path(tmp) / "complete_later_alphabet.md").exists())
            self.assertTrue((Path(tmp) / "word_combination_ruleset.md").exists())
            self.assertTrue((Path(tmp) / "lexicon_first_batch.md").exists())
            self.assertTrue((Path(tmp) / "lexicon_review.md").exists())
            self.assertTrue((Path(tmp) / "lexicon_expansion_report.md").exists())

    def test_root_quality_scores_are_stable_enough_for_sound_taste(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        scores = [builder.assess_root_quality(root)["score"] for root in roots]

        self.assertTrue(all(score >= 8 for score in scores))

    def test_phrase_probes_reference_existing_roots_and_registers(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        phrase_probes = builder.load_json(builder.DATA_DIR / "phrase_probes.json")
        root_sounds = {root["proto_sound"] for root in roots}
        register_ids = set(phonology["registers"])

        for probe in phrase_probes["probes"]:
            self.assertIn(probe["register_id"], register_ids)
            self.assertTrue(set(probe["roots"]).issubset(root_sounds))

    def test_phrase_fusion_changes_blocky_samples(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        phrase_probes = builder.load_json(builder.DATA_DIR / "phrase_probes.json")
        lookup = builder.roots_by_sound(roots)
        probes = {probe["id"]: probe for probe in phrase_probes["probes"]}

        self.assertEqual(builder.phrase_underlying(probes["healer_command"], lookup, phonology), "om + nu")
        self.assertEqual(builder.phrase_surface(probes["healer_command"], lookup, phonology), "omnu")
        self.assertEqual(builder.phrase_underlying(probes["carry_memory"], lookup, phonology), "kelm + morm")
        self.assertEqual(builder.phrase_surface(probes["carry_memory"], lookup, phonology), "kelmorm")

    def test_root_inventory_covers_current_phonology(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        inventory_parts = []
        for root in roots:
            inventory_parts.extend(
                [
                    root["proto_sound"],
                    root["phonogestural_contour"]["vowel_movement"],
                    root["phonogestural_contour"]["consonant_transition"],
                ]
            )
        inventory_text = " ".join(inventory_parts)

        for consonant in phonology["sound_inventory"]["common_consonants"]:
            self.assertIn(consonant, inventory_text)

        for vowel in phonology["sound_inventory"]["vowels"]:
            self.assertIn(vowel, inventory_text)

        for vowel in phonology["sound_inventory"]["resonant_vowels"]:
            self.assertIn(vowel, inventory_text)

    def test_evolution_clusters_roots_into_attractors(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        clusters = builder.alphabet_clusters(roots)

        self.assertEqual(sum(len(group) for group in clusters.values()), len(roots))
        self.assertTrue(all(builder.alphabet_attractor_form(key, group, phonology) for key, group in clusters.items()))

    def test_provisional_alphabet_is_root_derived_and_learnable(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        entries = builder.provisional_alphabet_entries(roots, phonology)
        base_entries = [entry for entry in entries if entry["kind"] == "base"]

        self.assertEqual(len(base_entries), len(roots))
        self.assertGreaterEqual(len(entries), 25)
        self.assertTrue(all("-" not in entry["letter"] for entry in entries))
        self.assertTrue(all(entry["letter"] == entry["phoneme"] for entry in entries))

    def test_attractor_pronunciation_marks_vowel_duration(self):
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")

        keam = builder.pronunciation_for_form("keam", "binding", phonology)
        moam = builder.pronunciation_for_form("moam", "binding", phonology)
        taoa = builder.pronunciation_for_form("taoa", "action", phonology)

        self.assertEqual(keam["reading_ascii"], "ke-aam")
        self.assertEqual(keam["duration_pattern"], "short-long")
        self.assertEqual(keam["marked_form"], "kĕām")
        self.assertEqual(moam["reading_ascii"], "mo-aam")
        self.assertEqual(moam["marked_form"], "mŏām")
        self.assertEqual(taoa["duration_pattern"], "short-long-short")


    def test_proto_words_expand_root_meanings_before_collapse(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        proto_words = builder.generate_proto_words(roots, phonology)
        grouped = builder.proto_words_by_root(proto_words)

        self.assertEqual(len(proto_words), 66)
        self.assertEqual(set(grouped), {root["proto_sound"] for root in roots})
        self.assertTrue(all(";" not in item["meaning"] for item in proto_words))
        self.assertEqual(len({item["utterance"] for item in proto_words}), len(proto_words))

    def test_stable_letter_names_are_learnable_length(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        proto_words = builder.generate_proto_words(roots, phonology)
        entries = builder.stable_letter_name_entries(roots, proto_words, phonology)

        self.assertGreaterEqual(len(entries), 20)
        self.assertLessEqual(len(entries), 40)
        self.assertTrue(all(3 <= len(entry["stable_name"]) <= 6 for entry in entries))
        self.assertEqual(len({entry["stable_name"] for entry in entries}), len(entries))

    def test_vowel_combination_grid_uses_current_root_onsets(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        onsets = builder.current_beginning_consonants(roots)
        combos = builder.vowel_combinations(phonology)

        self.assertIn("br", onsets)
        self.assertIn("dr", onsets)
        self.assertIn("sh", onsets)
        self.assertIn("th", onsets)
        self.assertIn("dh", onsets)
        self.assertIn("ch", onsets)
        self.assertIn("z", onsets)
        self.assertNotIn("w", onsets)
        self.assertEqual(len(combos), 25)

    def test_phonetic_function_matrix_maps_clusters_through_neo_logic(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        entries = {entry["onset"]: entry for entry in builder.sound_function_entries(roots)}

        self.assertEqual(entries["br"]["glyphs"], ["B", "R"])
        self.assertEqual(entries["br"]["pair"]["matrix"], "Anchor")
        self.assertEqual(entries["br"]["dominant"], "structure")
        self.assertEqual(entries["dr"]["glyphs"], ["D", "R"])
        self.assertEqual(entries["dr"]["pair"]["intensity"], "Dominance")
        self.assertEqual(entries["th"]["glyphs"], ["T", "H"])
        self.assertEqual(entries["th"]["pair"]["matrix"], "Reinforce")
        self.assertEqual(entries["dh"]["glyphs"], ["D", "H"])
        self.assertEqual(entries["ch"]["glyphs"], ["T", "S"])
        self.assertEqual(entries["z"]["glyphs"], ["Z"])
        self.assertNotIn("w", entries)

    def test_phonetic_analogy_matrix_treats_manners_as_interaction_patterns(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        entries = {entry["id"]: entry for entry in builder.phonetic_analogy_entries(roots)}

        self.assertIn("Propel", entries["plosive"]["neo_analogy"])
        self.assertIn("Fracture", entries["plosive"]["neo_analogy"])
        self.assertIn("Turbulence", entries["fricative"]["neo_analogy"])
        self.assertIn("th", entries["threshold"]["current_onsets"])
        self.assertIn("ch", entries["affricate"]["current_onsets"])
        self.assertIn("m", entries["nasal"]["current_onsets"])
        self.assertEqual(entries["approximant"]["current_onsets"], [])

    def test_later_alphabet_compression_audits_roots_as_mouth_actions(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        later_alphabet = builder.load_json(builder.DATA_DIR / "later_alphabet.json")
        coverage = builder.later_alphabet_coverage(roots, later_alphabet)
        profiles = {profile["root"]: profile for profile in coverage["profiles"]}

        self.assertEqual(len(later_alphabet["consonant_families"]), 10)
        self.assertEqual(len(later_alphabet["vowel_families"]), 5)
        self.assertEqual(profiles["ha"]["compressed_form"], "H+A")
        self.assertEqual(profiles["thae"]["compressed_form"], "TH+A+E")
        self.assertEqual(profiles["dhae"]["compressed_form"], "TH+A+E")
        self.assertEqual(profiles["cha"]["compressed_form"], "CHSH+A")
        self.assertEqual(profiles["zai"]["compressed_form"], "SZ+A+I")
        self.assertEqual(profiles["hu"]["compressed_form"], "H+U")
        self.assertIn("PB", profiles["bri"]["consonant_families"])
        self.assertIn("LR", profiles["bri"]["consonant_families"])
        self.assertIn("CHSH", profiles["sha"]["consonant_families"])
        self.assertEqual(coverage["missing_consonants"], [])
        self.assertEqual(coverage["missing_vowels"], [])

    def test_complete_later_alphabet_has_names_phonetics_gestures_and_meanings(self):
        later_alphabet = builder.load_json(builder.DATA_DIR / "later_alphabet.json")
        entries = builder.complete_alphabet_entries(later_alphabet)

        self.assertEqual(len(entries), 15)
        self.assertEqual(entries[0]["name"], "Fáevá")
        self.assertEqual(entries[0]["letter"], "FV")
        self.assertIn("f / v", entries[0]["dual_phonetics"])
        self.assertEqual(entries[1]["name"], "Píeb")
        self.assertEqual(entries[4]["name"], "Detrá")
        self.assertTrue(all(entry["gesture"] for entry in entries))
        self.assertTrue(all(entry["brief_meaning"] for entry in entries))
        self.assertEqual(entries[-1]["name"], "Urá")

    def test_lexicon_first_batch_grows_from_roots_proto_words_and_phrases(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        phrase_probes = builder.load_json(builder.DATA_DIR / "phrase_probes.json")
        later_alphabet = builder.load_json(builder.DATA_DIR / "later_alphabet.json")
        proto_words = builder.generate_proto_words(roots, phonology)
        entries = builder.lexicon_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
        kinds = {entry["kind"] for entry in entries}
        headwords = {entry["headword"] for entry in entries}

        self.assertGreaterEqual(len(entries), 60)
        self.assertIn("root sound-event", kinds)
        self.assertIn("adjacent proto-word", kinds)
        self.assertIn("warning phrase", kinds)
        self.assertIn("thae", headwords)
        self.assertIn("haisilh", headwords)
        self.assertIn("zunheah", headwords)
        self.assertIn("dhaehpaem", headwords)
        self.assertTrue(all(entry["length"] <= builder.WORD_COMBINATION_RULES["rare_hard_max"] for entry in entries))
        self.assertTrue(any(entry["shape_status"] == "compressed-from-overlong" for entry in entries))

    def test_word_combination_rules_enforce_vowel_and_length_constraints(self):
        self.assertEqual(builder.combine_words_for_lexicon(["ta", "ari"]), "tari")
        self.assertEqual(builder.combine_words_for_lexicon(["om", "nu"]), "omnu")
        self.assertEqual(builder.combine_words_for_lexicon(["kelm", "morm"]), "kelmorm")
        constrained = builder.constrained_lexicon_headword(["fairafa", "vekfaba", "paemara"], ["fai", "vek", "pae"])

        self.assertLessEqual(constrained["length"], builder.WORD_COMBINATION_RULES["rare_hard_max"])
        self.assertEqual(constrained["shape_status"], "compressed-from-overlong")

    def test_lexicon_review_flags_words_for_next_root_expansion(self):
        roots = builder.load_json(builder.DATA_DIR / "roots.seed.json")["roots"]
        phonology = builder.load_json(builder.DATA_DIR / "phonology.json")
        phrase_probes = builder.load_json(builder.DATA_DIR / "phrase_probes.json")
        later_alphabet = builder.load_json(builder.DATA_DIR / "later_alphabet.json")
        proto_words = builder.generate_proto_words(roots, phonology)
        entries = builder.lexicon_review_entries(roots, proto_words, phonology, phrase_probes, later_alphabet)
        statuses = {entry["review_status"] for entry in entries}
        targets = builder.root_expansion_targets(entries, later_alphabet)

        self.assertIn("promote", statuses)
        self.assertIn("watch", statuses)
        self.assertIn("ritual-only", statuses)
        self.assertTrue(any(target["family"] == "PB" for target in targets))
        self.assertTrue(any(target["family"] == "CHSH" for target in targets))


if __name__ == "__main__":
    unittest.main()
