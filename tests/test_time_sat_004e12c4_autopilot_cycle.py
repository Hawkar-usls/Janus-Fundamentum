#!/usr/bin/env python3
"""E12C4 autonomous development state-machine safety tests, no timed solver."""
import json
import os
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
import janus_time_sat_004e12c4_autopilot_cycle as cycle


class E12C4AutopilotTests(unittest.TestCase):
    def make_state(self, path, **override):
        state = {"schema": cycle.SOURCE_STATE_SCHEMA, "mode": "DEVELOPMENT_ONLY",
                 "next_cycle": 0, "history": [], "completed_run_ids": []}
        state.update(override)
        path.write_text(json.dumps(state) + "\n")

    def test_frozen_holdout_never_used_as_development_seed(self):
        seen = set()
        holdout = set(cycle.e.HOLDOUT)
        for index in range(cycle.MAX_CYCLES):
            family, seed = cycle.source_for_cycle(index)
            self.assertNotIn((family, seed), holdout)
            self.assertNotIn((family, seed), seen)
            seen.add((family, seed))
        with self.assertRaises(ValueError):
            cycle.source_for_cycle(cycle.MAX_CYCLES)

    def test_incremental_calibration_trains_on_every_completed_prior_only(self):
        first = cycle.e.generate("coverage_0.6", 202611040000)
        second = cycle.e.generate("coverage_0.67", 202611040100)
        failed = cycle.e.generate("width4", 202611040900)
        current = cycle.e.generate("coverage_0.699", 202611040200)
        feat1 = {"n": 30, "m": 640, "lits": 3072, "eq": 12,
                 "width6": 12, "coverage": 0.6, "residual": 256}
        feat2 = {"n": 30, "m": 573, "lits": 2871, "eq": 12,
                 "width6": 12, "coverage": 0.670157, "residual": 189}
        def item(src, features, state, ratio=0.85):
            return {"original_sha256": src["original_sha256"],
                    "features": features, "cycle_status": state,
                    "paired_full_cold": [{"raw_status": "VERIFIED",
                        "xor_status": "VERIFIED", "raw_s": ratio,
                        "xor_s": 1.0}] * len(cycle.e.VARIANTS)}
        r1 = item(first, feat1, "COMPLETE")
        r2 = item(second, feat2, "COMPLETE")
        bad = item(failed, feat1, "PAUSED_SAFETY_FAILURE")
        baseline = {"schema": cycle.SOURCE_STATE_SCHEMA,
                    "history": []}
        fit0 = cycle.trained_from_past(baseline)
        self.assertEqual(len(fit0["profiles"]), 8)
        state1 = {**baseline, "history": [r1]}
        fit1 = cycle.trained_from_past(state1)
        provenance1 = cycle.calibration_lineage(
            state1, fit1, second["original_sha256"])
        self.assertEqual(provenance1["prior_complete_original_count"], 1)
        self.assertEqual(provenance1["total_profile_count"], 9)
        state2 = {**baseline, "history": [r1, bad, r2]}
        fit2 = cycle.trained_from_past(state2)
        evidence = cycle.calibration_lineage(
            state2, fit2, current["original_sha256"])
        self.assertEqual(evidence["prior_complete_original_count"], 2)
        self.assertEqual(evidence["total_profile_count"], 10)
        self.assertEqual(evidence["excluded_failed_history_count"], 1)
        self.assertNotIn(bad["original_sha256"],
                         {p["original_sha256"] for p in fit2["profiles"]})
        self.assertNotIn(current["original_sha256"],
                         {p["original_sha256"] for p in fit2["profiles"]})
        self.assertNotEqual(cycle.sha(cycle.encoded(fit1)),
                            cycle.sha(cycle.encoded(fit2)))
        tampered = dict(fit2)
        tampered["profiles"] = [p for p in fit2["profiles"]
                                if p["original_sha256"] != r2["original_sha256"]]
        with self.assertRaisesRegex(AssertionError, "DROPPED_VERIFIED_HISTORY"):
            cycle.calibration_lineage(
                state2, tampered, current["original_sha256"])
        tampered = dict(fit2)
        tampered["profiles"] = fit2["profiles"] + [
            {"original_sha256": current["original_sha256"],
             "features": feat1, "censored": False, "gain": 100.0}]
        with self.assertRaisesRegex(AssertionError, "SELF_TRAINING"):
            cycle.calibration_lineage(
                state2, tampered, current["original_sha256"])
        tampered = dict(fit2)
        tampered["profiles"] = fit2["profiles"] + [
            {"original_sha256": bad["original_sha256"],
             "features": feat1, "censored": False, "gain": 100.0}]
        with self.assertRaises(AssertionError):
            cycle.calibration_lineage(
                state2, tampered, current["original_sha256"])

    def test_past_training_is_not_cosmetic_model_selection_changes_on_good_evidence(self):
        s = cycle.e.generate("coverage_0.75", 202611049301)
        i = cycle.e.c1.source_index_all_widths(s["rows"], s["n"])
        f = cycle.e.features(s["rows"], s["n"], [
            eq for eq in i["equations"] if eq["width"] in (5, 6)])
        def pair(gain):
            return [{"raw_status": "VERIFIED", "xor_status": "VERIFIED",
                     "raw_s": gain, "xor_s": 1.0}] * 3
        history = []
        for x in ("a"*64, "b"*64):
            history.append({"original_sha256": x, "features": f,
                            "cycle_status": "COMPLETE",
                            "paired_full_cold": pair(2.0)})
        strong = cycle.e.fit_development(history)
        self.assertEqual(cycle.e.choose(s["rows"], s["n"], strong)["decision"],
                         "XOR_INTERNAL_DEVELOPMENT")
        weak = [{**r, "paired_full_cold": pair(0.9)} for r in history]
        slow = cycle.e.fit_development(weak)
        self.assertEqual(cycle.e.choose(s["rows"], s["n"], slow)["decision"], "RAW")

    def test_skip_replayed_run_no_new_cold_trials(self):
        with TemporaryDirectory() as d:
            f, out = Path(d)/"STATE.json", Path(d)/"out"
            self.make_state(f, completed_run_ids=["44"])
            with patch.dict(os.environ, {"GITHUB_RUN_ID": "44"}):
                cycle.loop(SimpleNamespace(state=f, out=out))
            self.assertEqual(json.loads((out/"REPORT.json").read_text())["cycle_status"],
                             "SKIPPED_DUPLICATE_RUN")
            self.assertFalse((out/"FIT.json").exists())

    def test_paused_state_remains_paused_without_compute(self):
        with TemporaryDirectory() as d:
            f, out = Path(d)/"STATE.json", Path(d)/"out"
            self.make_state(f, mode="PAUSED_SAFETY_FAILURE")
            with patch.dict(os.environ, {"GITHUB_RUN_ID": "45"}):
                cycle.loop(SimpleNamespace(state=f, out=out))
            self.assertEqual(json.loads((out/"REPORT.json").read_text())["cycle_status"],
                             "SKIPPED_PAUSED")

    def test_successful_cycle_advances_only_with_one_original_and_12_cold_receipts(self):
        with TemporaryDirectory() as d:
            f, out = Path(d)/"STATE.json", Path(d)/"out"
            self.make_state(f)
            model = {"schema": cycle.e.SCHEMA + "-DEV-FIT", "profiles": [],
                     "min_gain":1.5, "min_matching_originals":2}
            def fake_child(command, **kwargs):
                args = dict(zip(command[3::2], command[4::2]))
                return SimpleNamespace(returncode=0,
                    stdout=json.dumps({"arm": args["--arm"],
                        "variant":args["--variant"],
                        "original_sha256":args["--original-sha"],
                        "variant_sha256":args["--variant-sha"],
                        "status":cycle.SAT,
                        "decision":"RAW" if args["--arm"] == "selected_dev" else "CONTROL"}),
                    stderr="")
            with patch.object(cycle, "trained_from_past", return_value=model), (
                 patch.object(cycle.subprocess, "run", side_effect=fake_child)), (
                 patch.dict(os.environ, {"GITHUB_RUN_ID": "46"})):
                cycle.loop(SimpleNamespace(state=f, out=out))
            j = json.loads((out/"REPORT.json").read_text())
            self.assertEqual(j["cycle_status"], "COMPLETE")
            self.assertEqual(len(j["records"]), 12)
            self.assertEqual(len(j["paired_full_cold"]), 3)
            self.assertEqual(j["heldout_sources_timed"], 0)
            self.assertEqual(j["promotion"], "PROHIBITED")

if __name__ == "__main__":
    unittest.main()
