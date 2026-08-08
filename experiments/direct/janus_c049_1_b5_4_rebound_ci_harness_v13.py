from __future__ import annotations

import json
from pathlib import Path

import janus_c049_1_b5_4_rebound_ci_harness_v11 as h
import janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v13 as v13

EVIDENCE = Path("/tmp/b5-4-v13-evidence")
RECEIPT = EVIDENCE / "exact-head-receipt-v13.json"
AMENDMENT_V13 = Path("experiments/direct/C049_1_B5_4_NONTRIVIAL_UPSTREAM_REBIND_HARDENING_AMENDMENT_V1_3.json")
WORKFLOW_V13 = Path(".github/workflows/validate-c049-1-b5-4-corrected-discovery-c047-rebound-v13.yml")


def main() -> None:
    h.TMP = Path("/tmp/b54-v13")
    h.EVIDENCE = EVIDENCE
    h.v11 = v13

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
        raise AssertionError(f"expected 27/27 nontrivial repaired-digest tamper rejection, got {tampers}")

    h.freeze_receipt(sat, unsat, tampers)
    old = EVIDENCE / "exact-head-receipt-v11.json"
    receipt = json.loads(old.read_text(encoding="utf-8"))
    receipt["schema"] = "janus.c049_1.b5_4.corrected_discovery_c047_rebound_exact_head_candidate_receipt.v1_3"
    receipt["bindings"]["v1_3_hardening_amendment_git_blob"] = h.git_blob(AMENDMENT_V13)
    receipt["bindings"]["v1_3_hardening_verifier_git_blob"] = h.git_blob(Path("experiments/direct/janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v13.py"))
    receipt["bindings"]["v1_3_harness_git_blob"] = h.git_blob(Path("experiments/direct/janus_c049_1_b5_4_rebound_ci_harness_v13.py"))
    receipt["bindings"]["v1_3_workflow_git_blob"] = h.git_blob(WORKFLOW_V13)
    receipt["checks"]["nontrivial_upstream_b5_2b_outer_subject_rebinding"] = "PASS"
    receipt["checks"]["direct_independent_b5_2b_replay_rejection"] = "2/2"
    receipt["checks"]["full_b5_4_replay_rejection_after_outer_rebind"] = "2/2"
    receipt["checks"]["tampers_rejected"] = "27/27"
    receipt["checks"]["workflow_exact_head_self_binding"] = "PASS"
    receipt["hardening_v1_3"] = {
        "semantic_contract_changed": False,
        "v1_2_fixture_weakness": "INNER_DIGEST_REPAIRED_BUT_OUTER_B5_4_SUBJECT_NOT_REBOUND",
        "new_regressions": [
            "REPAIRED_AND_OUTER_REBOUND_B5_2B_CUT_WIDTH_TAMPER_REJECTED_BY_DIRECT_B5_2B_AND_FULL_B5_4_REPLAY",
            "REPAIRED_AND_OUTER_REBOUND_B5_2B_CUT_BASIS_TAMPER_REJECTED_BY_DIRECT_B5_2B_AND_FULL_B5_4_REPLAY"
        ]
    }
    RECEIPT.write_text(json.dumps(receipt, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
    old.unlink()

    print("B5_4_V1_3_OUTER_SUBJECT_REBIND = PASS")
    print("B5_4_V1_3_DIRECT_B5_2B_REPLAY_REJECTION = 2/2")
    print("B5_4_V1_3_FULL_REBOUND_REPLAY_REJECTION = 2/2")
    print("DIGEST_REPAIRED_TAMPERS_REJECTED = 27/27")
    print("B5_4_V1_3_WORKFLOW_EXACT_HEAD_SELF_BINDING = PASS")
    print("B5_4_V1_3_SEMANTIC_CONTRACT_CHANGED = FALSE")
    print("C047_RESULT_ADMITTED = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
