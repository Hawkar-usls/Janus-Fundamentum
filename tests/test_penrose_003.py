#!/usr/bin/env python3
"""Small hostile-transfer tests; the actual 56 MB proof is in separate CI job."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments" / "direct"))
from janus_penrose_002_integration import (
    REQUIRED_EDGES, STAGES, get_fixture, source_id,
)
from janus_penrose_003_transfer import (
    MAX_PROOF_BYTES, handoff_manifest, inspect_transfer, read_files,
)
from janus_penrose_003_witness import expect_rejection, run_witness


HEAD = "abcdef0123456789abcdef0123456789abcdef01"
RUN = "41298547419"


def mock_transfer():
    root, n = get_fixture("MAJ3_K4")
    proof = b'{"intentionally_incorrect_proof":true}'
    report = {
        "fixture": "MAJ3_K4",
        "stage_order": list(STAGES),
        "dependencies": [list(x) for x in REQUIRED_EDGES],
        "stage_payloads": {
            "SOURCE": {"source_sha256": source_id(root, n)},
        },
        "proof_file_sha256": sha256(proof).hexdigest(),
    }
    raw = (json.dumps(report, sort_keys=True) + "\n").encode()
    return report, raw, proof, handoff_manifest(raw, proof, head_sha=HEAD, run_id=RUN)


class WitnessTransitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report, cls.raw, cls.proof, cls.manifest = mock_transfer()

    def test_handoff_preflight_binds_same_run_and_same_bytes(self):
        self.assertEqual(
            inspect_transfer(self.manifest, self.raw, self.proof,
                             trusted_head=HEAD, trusted_run=RUN),
            self.manifest)
        self.assertEqual(self.manifest["strict_stages"], 9)
        self.assertEqual(self.manifest["strict_edges"], 14)

    def test_transfer_hash_stale_code_and_stale_run_fail_closed(self):
        for name, manifest, report, proof, sha, run in (
            ("wrong sha", self.manifest, self.raw, self.proof, "f"*40, RUN),
            ("wrong run", self.manifest, self.raw, self.proof, HEAD, "1"),
            ("stale report", self.manifest, self.raw+b" ", self.proof, HEAD, RUN),
            ("truncated proof", self.manifest, self.raw, self.proof[:-1], HEAD, RUN),
            ("wrong certificate", self.manifest, self.raw, b"bad", HEAD, RUN),
            ("different source", dict(self.manifest, source_sha256="0"*64),
             self.raw, self.proof, HEAD, RUN),
        ):
            with self.subTest(name=name):
                with self.assertRaises(ValueError):
                    inspect_transfer(manifest, report, proof,
                                     trusted_head=sha, trusted_run=run)

    def test_globally_impossible_and_missing_dependencies_rejected_before_replay(self):
        for edges in (
            list(self.report["dependencies"]) + [["FINAL_GATE", "UFR_PRODUCE"]],
            list(self.report["dependencies"])[:-1],
            list(self.report["dependencies"]) + [["FINAL_GATE", "SOURCE"]],
            list(self.report["dependencies"]) + [["ORACLE_TRUTH", "UFR_PRODUCE"]],
        ):
            mutated = deepcopy(self.report)
            mutated["dependencies"] = edges
            raw = json.dumps(mutated).encode()
            with self.assertRaises(ValueError):
                handoff_manifest(raw, self.proof, head_sha=HEAD, run_id=RUN)

    def test_same_consistent_manifest_does_not_make_bad_proof_true(self):
        # Correct transport+hashing alone is intentionally insufficient.
        self.assertEqual(
            inspect_transfer(self.manifest, self.raw, self.proof,
                             trusted_head=HEAD, trusted_run=RUN),
            self.manifest)
        with self.assertRaises((AssertionError, ValueError, KeyError, TypeError)):
            run_witness(self.manifest, self.raw, self.proof,
                        trusted_head=HEAD, trusted_run=RUN)

    def test_handshake_type_boundaries_and_disk_read(self):
        with TemporaryDirectory() as directory:
            folder = Path(directory)
            m, r, p = (folder / "manifest.json", folder / "report.json",
                       folder / "proof.json")
            m.write_text(json.dumps(self.manifest), encoding="utf-8")
            r.write_bytes(self.raw)
            p.write_bytes(self.proof)
            self.assertEqual(read_files(m, r, p)[1:], (self.raw, self.proof))
            p.unlink()
            with self.assertRaises(ValueError):
                read_files(m, r, p)
            with p.open("wb") as file:
                file.seek(MAX_PROOF_BYTES)
                file.write(b"X")
            with self.assertRaises(ValueError):
                read_files(m, r, p)

    def test_unexpected_manifest_fields_and_fixture_rejected(self):
        for obj in (
            dict(self.manifest, bonus="surprise"),
            dict(self.manifest, fixture="RENAMED_TWIN_POSITIVE_CONTROL"),
            dict(self.manifest, head_sha="wrong"),
        ):
            with self.assertRaises(ValueError):
                inspect_transfer(obj, self.raw, self.proof,
                                 trusted_head=HEAD, trusted_run=RUN)
        with self.assertRaises(ValueError):
            handoff_manifest(self.raw, self.proof,
                             head_sha="invalid", run_id=RUN)
        with self.assertRaises(ValueError):
            handoff_manifest(self.raw, self.proof,
                             head_sha=HEAD, run_id="run-abc")


if __name__ == "__main__":
    unittest.main()
