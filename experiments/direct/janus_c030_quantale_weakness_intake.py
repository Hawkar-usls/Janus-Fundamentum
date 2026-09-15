#!/usr/bin/env python3
"""C030 intake audit for arXiv:2510.08814v2.

This script validates the exact claim card and separates the standard P=NP
witness-recovery upper bound from the new lower-bound obligations. It does not
validate or refute the claimed P!=NP proof.
"""
from __future__ import annotations
import hashlib
import json

CARD = {
    "artifact_id": "C030-JANUS-QUANTALE-WEAKNESS-INTAKE",
    "status": "SERIOUS_CLAIM_UNDER_REVIEW",
    "source": "arXiv:2510.08814v2",
    "revision_date": "2026-04-22",
    "claim": "P != NP",
    "model": "uniform deterministic polynomial time; polytime-capped conditional description length",
    "standard_upper_bound": "If P=NP, SAT self-reduction recovers a satisfying witness in polynomial time on satisfiable inputs.",
    "load_bearing_obligations": [
        "efficiently samplable locked SAT ensemble with the stated promise",
        "normalization of every target-relevant non-neutral evidence leaf",
        "safe-buffer leakage bound",
        "hidden-gauge rank accounting",
        "product small-success for every fixed polynomial-time observer",
        "uniform polynomial time cap in K_poly across the ensemble",
        "compression-from-success with all coding overhead charged",
        "transfer from the distributional message lower bound to the claimed contradiction",
    ],
    "first_falsification_attacks": [
        "audit quantifier order over observers, time polynomials, wrappers, and sampled instances",
        "check whether the K_poly time cap is one uniform polynomial rather than observer- or instance-dependent",
        "construct global short decoders to attack any unqualified short-program-to-locality step",
        "verify that masking and isolation preserve efficient sampling and the unique-message promise",
        "replay every normalization rewrite for termination, confluence, and semantic preservation",
        "test whether product small-success assumes independence after conditioning on shared formula structure",
    ],
    "p_vs_np": "OPEN",
}

def run() -> dict:
    assert CARD["status"] != "PROVED"
    assert CARD["p_vs_np"] == "OPEN"
    assert len(CARD["load_bearing_obligations"]) >= 8
    assert len(CARD["first_falsification_attacks"]) >= 6
    payload = json.dumps(CARD, sort_keys=True, separators=(",", ":")).encode()
    out = dict(CARD)
    out["sha256"] = hashlib.sha256(payload).hexdigest()
    return out

if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
