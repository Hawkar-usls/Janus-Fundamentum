#!/usr/bin/env python3
"""Regression for the exposed E12C4 cycle-18 sparse CryptoMiniSat model crash.

Historical failure 41600435473 remains immutable in the state branch. This
suite replays its ORIGINAL DEVELOPMENT source exactly, not unseen holdout.
"""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
import janus_time_sat_004e12c4_autopilot_cycle as ap

FAMILY = "width4"
SEED = 202611040900
ORIGINAL_SHA = "2e5cdd19a5af97841c1bc36f2d0acd39aef751b5351202c008d33e713413a7ea"
MODEL_SHA = "f812b285bbdef01b989bb2dbbb2979764014f2e38f04979157990c6c81b66d05"
FAILED_RUN_ID = "41600435473"
DEPENDENCIES = bool(importlib.util.find_spec("pycryptosat") and importlib.util.find_spec("pysat"))

class SparseCryptoMiniSatModelTests(unittest.TestCase):
    def test_short_tuple_fills_absent_variables_and_replays_every_clause(self):
        model, missing = ap.verified_cryptominisat_model(
            (None, True, False), 5, [[1], [-2], [1, 2]])
        self.assertEqual(model, [1, -2, -3, -4, -5])
        self.assertEqual(missing, 3)

    def test_explicit_none_and_unconstrained_values(self):
        model, missing = ap.verified_cryptominisat_model(
            (None, True, None, False), 5, [[1], [-3]])
        self.assertEqual(model, [1, -2, -3, -4, -5])
        self.assertEqual(missing, 3)

    def test_rejects_extension_that_does_not_satisfy_original_cnf(self):
        # Never claim SAT merely because the solver returned True or a tuple.
        with self.assertRaisesRegex(AssertionError, "fails original CNF replay"):
            ap.verified_cryptominisat_model((None, True), 3, [[1], [2]])
        with self.assertRaisesRegex(AssertionError, "fails original CNF replay"):
            ap.verified_cryptominisat_model((None, False, True), 2, [[1], [2]])

    def test_rejects_malformed_index_and_values(self):
        bad = [(), (True, True), (None, "yes"), (None, True, False, False, True)]
        for model in bad:
            with self.subTest(model=model), self.assertRaises(AssertionError):
                ap.verified_cryptominisat_model(model, 2, [[1]])
        with self.assertRaises(AssertionError):
            ap.verified_cryptominisat_model(None, 2, [[1]])

    def test_exposed_failure_source_and_frozen_model_sha(self):
        source = ap.e.generate(FAMILY, SEED)
        self.assertEqual(source["original_sha256"], ORIGINAL_SHA)
        self.assertEqual(source["model_sha256"], MODEL_SHA)
        self.assertEqual(source["status_by_construction"], "SAT")
        self.assertNotIn((FAMILY, SEED), ap.e.HOLDOUT)
        for variant in ap.e.VARIANTS:
            transformed = ap.e.transform(source, variant)
            self.assertTrue(ap.e._model_ok(transformed["rows"], transformed["model"]))

    @unittest.skipUnless(DEPENDENCIES, "requires real pycryptosat + python-sat")
    def test_full_cold_real_solver_replay_original_failure_all_arms_variants(self):
        source = ap.e.generate(FAMILY, SEED)
        self.assertEqual(source["original_sha256"], ORIGINAL_SHA)
        self.assertEqual(source["model_sha256"], MODEL_SHA)
        fit = ap.e.fit_archived_e12c3()
        with TemporaryDirectory() as directory:
            fitpath = Path(directory) / "FIT.json"
            fitpath.write_bytes(ap.encoded(fit))
            fit_sha = ap.sha(fitpath.read_bytes())
            replay = []
            for variant in ap.e.VARIANTS:
                presentation = ap.e.transform(source, variant)
                for arm in ap.ARMS:
                    command = [
                        sys.executable, str(Path(ap.__file__).resolve()), "--child",
                        "--family", FAMILY, "--seed", str(SEED),
                        "--variant", variant, "--arm", arm,
                        "--original-sha", ORIGINAL_SHA,
                        "--variant-sha", presentation["variant_sha256"],
                        "--fit-sha", fit_sha, "--fit-path", str(fitpath)]
                    child = subprocess.run(command, capture_output=True, text=True,
                                           timeout=ap.WALL_LIMIT, check=False)
                    self.assertEqual(child.returncode, 0,
                                     (variant, arm, child.stderr[-1800:]))
                    data = json.loads(child.stdout)
                    self.assertEqual(data["status"], ap.SAT, (variant, arm))
                    self.assertEqual(data["original_sha256"], ORIGINAL_SHA)
                    self.assertEqual(data["variant_sha256"], presentation["variant_sha256"])
                    self.assertEqual(data["fit_sha256"], fit_sha)
                    self.assertLessEqual(data["cpu_s"], ap.CPU_LIMIT)
                    self.assertLessEqual(data["peak_rss_kib"] * 1024, ap.MEM_LIMIT)
                    replay.append(data)
            self.assertEqual(len(replay), 12)
            # The two variants that failed on CryptoMiniSat formerly lacked
            # a complete 30-variable output tuple. The repaired implementation
            # must actually exercise the missing-variable path.
            for variant in ("as_emitted", "global_shuffle"):
                for arm in ("raw_cms", "certified_native", "selected_dev"):
                    matched = next(d for d in replay
                                   if d["variant"] == variant and d["arm"] == arm)
                    self.assertGreater(matched["sparse_model_defaults"], 0,
                                       (variant, arm))
            selections = {d["decision"] for d in replay if d["arm"] == "selected_dev"}
            self.assertEqual(selections, {"RAW"})
            # This suite must not publish a win from the earlier failed run.
            self.assertEqual(FAILED_RUN_ID, "41600435473")

if __name__ == "__main__":
    unittest.main()
