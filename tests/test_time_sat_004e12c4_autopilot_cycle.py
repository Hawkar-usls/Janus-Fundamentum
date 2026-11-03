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
