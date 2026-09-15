from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_component_join_carrier import component_join_carrier as v1
from research.tools.apma_component_join_carrier import component_join_carrier_v1_2 as candidate
from research.tools.apma_component_join_carrier.independent_checker import independent_global, verify_candidate_witness

ROOT = Path(__file__).resolve().parents[3]
V12_PREREG = ROOT / "research/TRUMP_BICAMERAL_COMPONENT_BOUNDARY_JOIN_CARRIER_V1_2_PREREGISTRATION_2026-09-15.json"
V1_PREREG = ROOT / "research/TRUMP_BICAMERAL_COMPONENT_BOUNDARY_JOIN_CARRIER_PREREGISTRATION_2026-09-15.json"
V1_CANDIDATE = ROOT / "research/tools/apma_component_join_carrier/component_join_carrier.py"
V12_WRAPPER = ROOT / "research/tools/apma_component_join_carrier/component_join_carrier_v1_2.py"
FIRST_FAIL = ROOT / "research/TRUMP_BICAMERAL_COMPONENT_BOUNDARY_JOIN_CARRIER_FIRST_RUN_FAILURE_2026-09-15.json"
DIAG_RESULT = ROOT / "research/TRUMP_BICAMERAL_COMPONENT_BOUNDARY_JOIN_CARRIER_V1_1_DIAGNOSTIC_RESULT_2026-09-15.json"
EXPECTED = {
    V1_PREREG: "a020a0c54995580f8d02e51d931624948060ecfa",
    V1_CANDIDATE: "89f5d591d4d553bb26489908a79f2c739f62b756",
    V12_WRAPPER: "85d8a6c826ba308f5e84dc246bdd152e2704f001",
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def run_wrapper() -> tuple[int, dict, str]:
    cp = subprocess.run([sys.executable, "-m", "research.tools.apma_component_join_carrier.component_join_carrier_v1_2"], cwd=ROOT, check=False, capture_output=True, text=True)
    if cp.returncode != 0:
        return cp.returncode, {}, cp.stderr
    lines = cp.stdout.strip().splitlines()
    return cp.returncode, json.loads(lines[-1]), cp.stderr


def main() -> None:
    prereg = json.loads(V12_PREREG.read_text(encoding="utf-8"))
    first_fail = json.loads(FIRST_FAIL.read_text(encoding="utf-8"))
    diag = json.loads(DIAG_RESULT.read_text(encoding="utf-8"))
    source = {p.name + "_blob": git_blob_sha1(p) == sha for p, sha in EXPECTED.items()}
    source.update({
        "v12_prereg_frozen": prereg.get("status") == "FROZEN_BEFORE_REPAIR_WRAPPER",
        "first_fail_preserved": first_fail.get("verdict") == "FAIL_INFRASTRUCTURE_CANDIDATE_CRASH_BEFORE_RECEIPT",
        "diagnostic_root_cause_preserved": diag.get("root_cause") == "deterministic_join_tree returns a valid singleton relation tree without tree_sha256, while component_boundary_support requires tree['tree_sha256'] for every admitted component including singleton components",
        "repair_class_exact": prereg.get("repair_class") == "PROVENANCE_RECEIPT_ONLY__SINGLETON_JOIN_TREE_CANONICAL_HASH",
    })

    rc, run, stderr = run_wrapper()
    if rc != 0:
        out = {
            "artifact_id": "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-V1-2-INDEPENDENT-CHECK-2026-09-15",
            "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
            "verdict": "FAIL_INFRASTRUCTURE_V1_2_CANDIDATE_CRASH",
            "candidate_exit_code": rc,
            "candidate_stderr": stderr,
            "source_checks": source,
            "scientific_firewall": candidate.firewall(),
        }
        print(json.dumps(out, sort_keys=True))
        raise SystemExit(1)

    pos_raw = v1.positive_multi_relation_k20()
    empty_raw = v1.empty_conditional_join_control()
    cycle_raw = v1.alpha_cycle_control()
    pos_parent = parent_mincut.explain_with_mincut(pos_raw)
    pos_support_parent = parent_support.explain_overwidth_cut(pos_raw)
    pos_ind = independent_global(pos_raw)
    empty_ind = independent_global(empty_raw)
    cycle_ind = independent_global(cycle_raw)

    pos = run["positive"]
    empty = run["negative_empty"]
    cycle = run["negative_cycle"]
    no_anchor = run["negative_no_anchor_unit"]
    hint = run["negative_hint"]
    tamper = run["negative_tamper"]
    carrier = pos.get("carrier", {})
    rr = carrier.get("resource_receipt", {})
    receipts = carrier.get("component_receipts", [])
    comp_sizes = sorted(len(c) for c in pos_ind.get("components", []))

    singleton_repaired = candidate.deterministic_join_tree_v1_2([{"id":"x","scope":[0],"allowed":[[0]]}])
    multi_probe = [
        {"id":"a","scope":[0,1],"allowed":[[0,0]]},
        {"id":"b","scope":[1,2],"allowed":[[0,0]]},
    ]
    original_multi = candidate.ORIGINAL_JOIN_TREE(multi_probe)
    repaired_multi = candidate.deterministic_join_tree_v1_2(multi_probe)

    checks = {
        **{f"P1_{k}": v for k, v in source.items()},
        "P1_singleton_receipt_has_hash": singleton_repaired.get("ok") is True and isinstance(singleton_repaired.get("tree_sha256"), str),
        "P1_multi_relation_delegation_unchanged": repaired_multi == original_multi,
        "P2_candidate_wrapper_executes": rc == 0,
        "P2_parent_overwidth": pos_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P2_parent_zero_raw_branches": pos_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") == 0,
        "P3_parent_singleton_carrier_open": pos_support_parent.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "P3_multi_relation_component_sizes": comp_sizes == [1,2],
        "P4_positive_independent_cut20": pos_ind.get("cut", {}).get("cut_size") == 20 and pos_ind.get("cut", {}).get("cut_variables") == list(range(20)),
        "P5_candidate_component_receipts_present": len(receipts) == 2 and all(isinstance(x.get("tree_sha256"), str) for x in receipts),
        "P5_independent_join_trees_verified": all(r.get("tree_ok") is True for r in pos_ind.get("component_results", [])),
        "P7_anchor_state_bounds": all(r.get("support_size", 10**9) <= r.get("anchor_input_rows", -1) for r in receipts),
        "P8_positive_support_matches_independent": carrier.get("effective_support", []) == [list(x) for x in pos_ind.get("common", [])] and carrier.get("effective_support_size") == len(pos_ind.get("common", [])) == 1,
        "P10_positive_terminal": pos.get("status") == "ADMIT_EXACT_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER",
        "P10_witness_verified": carrier.get("witness_verified") is True and verify_candidate_witness(pos_raw, pos),
        "P11_empty_independent_unsat": empty_ind.get("status") == "UNSAT" and not empty_ind.get("common", []),
        "P11_empty_terminal": empty.get("status") == "EXACT_UNSAT_BY_EMPTY_COMPONENT_BOUNDARY_SUPPORT",
        "P12_no_anchor_open": no_anchor.get("status") == "OPEN_NO_FULL_CUT_ANCHOR",
        "P13_cycle_independent_open": cycle_ind.get("status") == "OPEN_NO_VERIFIED_COMPONENT_JOIN_TREE",
        "P13_cycle_candidate_open": cycle.get("status") == "OPEN_NO_VERIFIED_COMPONENT_JOIN_TREE",
        "P14_hint_rejected": hint.get("status") == "REJECT_RAW_INPUT",
        "P14_tamper_rejected": tamper.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "P15_zero_raw_cube": rr.get("raw_cut_assignments_enumerated") == 0,
        "P15_zero_full_join": rr.get("full_join_rows_materialized") == 0,
        "P15_zero_cartesian": rr.get("cartesian_products_materialized") == 0,
        "P15_zero_backtracking": rr.get("join_tree_backtracks") == 0,
        "P15_zero_generic_transfer": rr.get("generic_transfer_calls") == 0,
        "P15_zero_external_solver": rr.get("external_solver_invocations") == 0,
        "FW_p_vs_np_open": run["scientific_firewall"].get("P_VS_NP") == "OPEN",
        "FW_general_sat_not_proved": run["scientific_firewall"].get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "FW_connected_mixed_not_solved": run["scientific_firewall"].get("CONNECTED_MIXED_CORE_SOLVED") == "NO",
        "FW_arbitrary_unseen_not_proved": run["scientific_firewall"].get("ARBITRARY_UNSEEN_INVARIANT_DISCOVERY") == "NOT_PROVED",
        "FW_general_multi_relation_not_proved": run["scientific_firewall"].get("GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION") == "NOT_PROVED",
    }
    verdict = "PASS_SCOPED_BICAMERAL_OVERWIDTH_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER_V1_2" if all(checks.values()) else "FAIL_OR_OPEN_COMPONENT_BOUNDARY_JOIN_CARRIER_V1_2"
    out = {
        "artifact_id": "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-V1-2-INDEPENDENT-CHECK-2026-09-15",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "verdict": verdict,
        "checks": checks,
        "controls": {
            "v1_failure_preserved": first_fail.get("verdict"),
            "v1_1_root_cause": diag.get("exception_message"),
            "positive_parent": pos_parent.get("status"),
            "positive_cut_size": pos_ind.get("cut", {}).get("cut_size"),
            "positive_component_sizes": comp_sizes,
            "positive_component_anchor_rows": [r.get("anchor_input_rows") for r in receipts],
            "positive_component_support_sizes": [r.get("support_size") for r in receipts],
            "positive_effective_support": [list(x) for x in pos_ind.get("common", [])],
            "positive_terminal": pos.get("status"),
            "empty_terminal": empty.get("status"),
            "cycle_terminal": cycle.get("status"),
            "no_anchor_terminal": no_anchor.get("status"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tamper.get("status"),
        },
        "repair": {
            "class": "SINGLETON_JOIN_TREE_CANONICAL_RECEIPT_ONLY",
            "frozen_v1_candidate_blob": "89f5d591d4d553bb26489908a79f2c739f62b756",
            "wrapper_blob": "85d8a6c826ba308f5e84dc246bdd152e2704f001",
            "multi_relation_delegation_unchanged": repaired_multi == original_multi,
        },
        "complexity": {
            "candidate_states": "bounded by explicit anchor relation rows",
            "raw_2_to_k_enumeration": 0,
            "full_join_materialization": 0,
            "tree_backtracking": 0,
        },
        "scientific_firewall": candidate.firewall(),
    }
    print(json.dumps(out, sort_keys=True))
    if verdict != "PASS_SCOPED_BICAMERAL_OVERWIDTH_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER_V1_2":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
