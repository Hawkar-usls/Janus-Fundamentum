from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_component_join_carrier import component_join_carrier as v1
from research.tools.apma_component_join_carrier import component_join_carrier_v1_2 as v12
from research.tools.apma_component_join_carrier import component_join_carrier_v1_3 as candidate
from research.tools.apma_component_join_carrier.independent_checker import independent_global, verify_candidate_witness

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_BICAMERAL_COMPONENT_BOUNDARY_JOIN_CARRIER_V1_3_PREREGISTRATION_2026-09-15.json"
V1_CANDIDATE = ROOT / "research/tools/apma_component_join_carrier/component_join_carrier.py"
V12_WRAPPER = ROOT / "research/tools/apma_component_join_carrier/component_join_carrier_v1_2.py"
V13_WRAPPER = ROOT / "research/tools/apma_component_join_carrier/component_join_carrier_v1_3.py"
V12_FAILURE = ROOT / "research/TRUMP_BICAMERAL_COMPONENT_BOUNDARY_JOIN_CARRIER_V1_2_FAILURE_2026-09-15.json"
EXPECTED = {
    V1_CANDIDATE: "89f5d591d4d553bb26489908a79f2c739f62b756",
    V12_WRAPPER: "85d8a6c826ba308f5e84dc246bdd152e2704f001",
    V13_WRAPPER: "acfa7d0f82f4a0b70074661a6f558831b73c9362",
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def run_candidate() -> tuple[int, dict, str]:
    cp = subprocess.run([sys.executable, "-m", "research.tools.apma_component_join_carrier.component_join_carrier_v1_3"], cwd=ROOT, check=False, capture_output=True, text=True)
    if cp.returncode:
        return cp.returncode, {}, cp.stderr
    return 0, json.loads(cp.stdout.strip().splitlines()[-1]), cp.stderr


def main() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    v12_fail = json.loads(V12_FAILURE.read_text(encoding="utf-8"))
    source = {p.name + "_blob": git_blob_sha1(p) == sha for p, sha in EXPECTED.items()}
    source["prereg_frozen"] = prereg.get("status") == "FROZEN_BEFORE_V1_3_WRAPPER"
    source["repair_class_exact"] = prereg.get("repair_class") == "NEGATIVE_CONTROL_SCOPE_ONLY__HOSTILE_ALPHA_CYCLE_MUST_SURVIVE_PARENT_OVERWIDTH_ADMISSION"
    source["v12_failure_preserved"] = v12_fail.get("verdict") == "FAIL_OR_OPEN_COMPONENT_BOUNDARY_JOIN_CARRIER_V1_2"

    rc, run, stderr = run_candidate()
    if rc:
        print(json.dumps({
            "artifact_id": "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-V1-3-INDEPENDENT-CHECK-2026-09-15",
            "verdict": "FAIL_INFRASTRUCTURE_V1_3_CANDIDATE_CRASH",
            "candidate_stderr": stderr,
            "source_checks": source,
            "scientific_firewall": v1.firewall(),
        }, sort_keys=True))
        raise SystemExit(1)

    pos_raw = v1.positive_multi_relation_k20()
    empty_raw = v1.empty_conditional_join_control()
    cycle_raw = candidate.alpha_cycle_control_v1_3()

    pos_parent = parent_mincut.explain_with_mincut(pos_raw)
    pos_support_parent = parent_support.explain_overwidth_cut(pos_raw)
    pos_ind = independent_global(pos_raw)
    empty_ind = independent_global(empty_raw)

    cycle_parent = parent_mincut.explain_with_mincut(cycle_raw)
    cycle_support_parent = parent_support.explain_overwidth_cut(cycle_raw)
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

    multi_probe = [
        {"id":"a","scope":[0,1],"allowed":[[0,0]]},
        {"id":"b","scope":[1,2],"allowed":[[0,0]]},
    ]
    original_multi = v12.ORIGINAL_JOIN_TREE(multi_probe)
    repaired_multi = v12.deterministic_join_tree_v1_2(multi_probe)

    checks = {
        **{f"P1_{k}": v for k, v in source.items()},
        "P1_v1_multi_relation_semantics_unchanged": repaired_multi == original_multi,
        "P2_candidate_executes": rc == 0,
        "P2_positive_parent_overwidth": pos_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P2_positive_parent_zero_branches": pos_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") == 0,
        "P3_positive_parent_singleton_open": pos_support_parent.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "P4_positive_cut20": pos_ind.get("cut", {}).get("cut_size") == 20 and pos_ind.get("cut", {}).get("cut_variables") == list(range(20)),
        "P5_positive_join_trees_verified": all(r.get("tree_ok") is True for r in pos_ind.get("component_results", [])),
        "P7_anchor_bounds": all(r.get("support_size", 10**9) <= r.get("anchor_input_rows", -1) for r in receipts),
        "P8_positive_support_one_and_matches": carrier.get("effective_support_size") == len(pos_ind.get("common", [])) == 1 and carrier.get("effective_support") == [list(x) for x in pos_ind.get("common", [])],
        "P10_positive_terminal": pos.get("status") == "ADMIT_EXACT_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER",
        "P10_witness_verified": carrier.get("witness_verified") is True and verify_candidate_witness(pos_raw, pos),
        "P11_empty_unsat": empty_ind.get("status") == "UNSAT" and empty.get("status") == "EXACT_UNSAT_BY_EMPTY_COMPONENT_BOUNDARY_SUPPORT",
        "P12_no_anchor_open": no_anchor.get("status") == "OPEN_NO_FULL_CUT_ANCHOR",
        "P13_cycle_parent_overwidth": cycle_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P13_cycle_parent_zero_branches": cycle_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") == 0,
        "P13_cycle_cut20": cycle_ind.get("cut", {}).get("cut_size") == 20 and cycle_ind.get("cut", {}).get("cut_variables") == list(range(20)),
        "P13_cycle_parent_singleton_open": cycle_support_parent.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "P13_cycle_components_1_and_3": sorted(len(c) for c in cycle_ind.get("components", [])) == [1,3],
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
    verdict = "PASS_SCOPED_BICAMERAL_OVERWIDTH_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER_V1_3" if all(checks.values()) else "FAIL_OR_OPEN_COMPONENT_BOUNDARY_JOIN_CARRIER_V1_3"
    out = {
        "artifact_id": "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-V1-3-INDEPENDENT-CHECK-2026-09-15",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "verdict": verdict,
        "checks": checks,
        "controls": {
            "positive_terminal": pos.get("status"),
            "positive_cut_size": pos_ind.get("cut", {}).get("cut_size"),
            "positive_effective_support": [list(x) for x in pos_ind.get("common", [])],
            "empty_terminal": empty.get("status"),
            "cycle_parent": cycle_parent.get("status"),
            "cycle_parent_cut": cycle_parent.get("cut", {}).get("cut_variables"),
            "cycle_parent_branch_enumerations": cycle_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations"),
            "cycle_component_sizes": sorted(len(c) for c in cycle_ind.get("components", [])),
            "cycle_independent_terminal": cycle_ind.get("status"),
            "cycle_candidate_terminal": cycle.get("status"),
            "no_anchor_terminal": no_anchor.get("status"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tamper.get("status"),
            "v1_2_failure_preserved": v12_fail.get("verdict"),
        },
        "complexity": {
            "candidate_states": "bounded by explicit anchor rows",
            "raw_2_to_k_enumeration": 0,
            "full_join_materialization": 0,
            "join_tree_backtracking": 0,
        },
        "scientific_firewall": v1.firewall(),
    }
    print(json.dumps(out, sort_keys=True))
    if verdict != "PASS_SCOPED_BICAMERAL_OVERWIDTH_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER_V1_3":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
