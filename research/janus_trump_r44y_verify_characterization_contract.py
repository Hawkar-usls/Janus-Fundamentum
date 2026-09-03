#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ARTIFACT = ROOT / "JANUS_TRUMP_R44Y_LEGEND_EQUIVALENCE_AND_COOK_RECKHOW_SPLIT_2026-09-03.json"
PROOF = ROOT / "JANUS_TRUMP_R44Y_LEGEND_EQUIVALENCE_PROOF_2026-09-03.md"


def main() -> None:
    obj = json.loads(ARTIFACT.read_text())
    proof = PROOF.read_text()

    assert obj["status"] == "MATHEMATICAL_CHARACTERIZATION_PROVED_IN_SCOPE"
    assert obj["theorem_1"]["name"] == "LEGEND_CHARACTERIZATION"
    assert obj["theorem_1"]["P_equals_NP_proved"] is False
    assert obj["theorem_2"]["name"] == "UNSAT_CERTIFICATE_SUBFRONT"
    assert obj["theorem_2"]["critical_firewall"] == "POLYNOMIAL_CERTIFICATE_EXISTENCE != DETERMINISTIC_POLYNOMIAL_CERTIFICATE_DISCOVERY"
    assert obj["next_direct_attack"]["obligation"] == "L3_POLYNOMIAL_DISCOVERY_AND_LOCAL_WORK"
    assert obj["TRUMP_finished"] is False
    assert obj["SAT_IN_P"] == "NOT_PROVED"
    assert obj["P_EQUALS_NP"] == "NOT_PROVED"
    assert obj["P_NE_NP"] == "NOT_PROVED"
    assert obj["P_VS_NP"] == "OPEN"

    required_phrases = [
        "LEGEND <=> 3SAT in P <=> P = NP",
        "POLYNOMIAL CERTIFICATE EXISTENCE != DETERMINISTIC POLYNOMIAL CERTIFICATE DISCOVERY",
        "10.2307/2273702",
        "P_VS_NP = OPEN",
    ]
    for phrase in required_phrases:
        assert phrase in proof, phrase

    out = {
        "gate_id": "R44Y_LEGEND_EQUIVALENCE_AND_COOK_RECKHOW_SPLIT",
        "artifact_loaded": str(ARTIFACT.name),
        "proof_loaded": str(PROOF.name),
        "contract_consistency": "PASS",
        "theorem_authority_source": "MATHEMATICAL_ARGUMENT_NOT_CI",
        "CI_role": "STRUCTURAL_FIREWALL_ONLY",
        "P_VS_NP": "OPEN",
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
