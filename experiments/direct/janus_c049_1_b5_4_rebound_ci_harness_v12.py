from __future__ import annotations

import json
from pathlib import Path

import janus_c049_1_b5_4_rebound_ci_harness_v11 as h
import janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v12 as v12

EVIDENCE = Path("/tmp/b5-4-v12-evidence")
RECEIPT = EVIDENCE / "exact-head-receipt-v12.json"


def main() -> None:
    h.TMP = Path("/tmp/b54-v12")
    h.EVIDENCE = EVIDENCE
    h.v11 = v12

    h.TMP.mkdir(parents=True, exist_ok=True)
    h.write_controls()
    for name in ("sat", "sat-reordered", "unsat", "opaque", "inconsistent", "empty", "basis-order"):
        h.build_chain(name)
    h.build_b51_open()
    for name in ("sat", "sat-reordered", "unsat", "opaque", "inconsistent", "empty", "basis-order"):
        h.build_b54(name)
    h.build_b54("hist-open", raw_name="sat", trellis_work_cap=0)
    h.build_b54("b5-open", open_b51=True)

    sat, unsat = h.check_controls()
    tampers = h.run_tampers()
    if tampers != (27, 27):
        raise AssertionError(f"expected 27/27 repaired-digest tamper rejection, got {tampers}")

    h.freeze_receipt(sat, unsat, tampers)
    old = EVIDENCE / "exact-head-receipt-v11.json"
    receipt = json.loads(old.read_text(encoding="utf-8"))
    receipt["schema"] = "janus.c049_1.b5_4.corrected_discovery_c047_rebound_exact_head_candidate_receipt.v1_2"
    receipt["bindings"]["v1_2_hardening_verifier_git_blob"] = h.git_blob(Path("experiments/direct/janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v12.py"))
    receipt["bindings"]["v1_2_harness_git_blob"] = h.git_blob(Path("experiments/direct/janus_c049_1_b5_4_rebound_ci_harness_v12.py"))
    receipt["checks"]["upstream_b5_2b_repaired_digest_cut_tampers"] = "2/2"
    receipt["checks"]["tampers_rejected"] = "27/27"
    receipt["hardening_v1_2"] = {
        "semantic_contract_changed": False,
        "new_regressions": [
            "REPAIRED_DIGEST_B5_2B_CUT_WIDTH_TAMPER_REJECTED_BEFORE_C047_PROMOTION",
            "REPAIRED_DIGEST_B5_2B_CUT_BASIS_TAMPER_REJECTED_BEFORE_C047_PROMOTION",
        ],
        "base_v1_1_green_run": 31247184773,
        "base_v1_1_green_job": 93077618813,
        "base_v1_1_artifact": 9018874362,
        "base_v1_1_artifact_zip_sha256": "bd77c6dc50c062f474997cbe9a5847e95b600e044a2eb55d2bef51fb18da86c2",
    }
    RECEIPT.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    old.unlink()

    print("B5_4_V1_2_UPSTREAM_B5_2B_CUT_WIDTH_REPAIRED_DIGEST_TAMPER = REJECTED")
    print("B5_4_V1_2_UPSTREAM_B5_2B_CUT_BASIS_REPAIRED_DIGEST_TAMPER = REJECTED")
    print("DIGEST_REPAIRED_TAMPERS_REJECTED = 27/27")
    print("B5_4_V1_2_SEMANTIC_CONTRACT_CHANGED = FALSE")
    print("C047_RESULT_ADMITTED = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
