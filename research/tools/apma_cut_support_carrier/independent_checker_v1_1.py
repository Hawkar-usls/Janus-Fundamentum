from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as candidate
from research.tools.apma_cut_support_carrier.independent_checker import independent_carrier

ROOT = Path(__file__).resolve().parents[3]
V11_PREREG = ROOT / "research/TRUMP_BICAMERAL_CUT_SUPPORT_CARRIER_V1_1_PREREGISTRATION_2026-09-15.json"
V1_PREREG = ROOT / "research/TRUMP_BICAMERAL_CUT_SUPPORT_CARRIER_PREREGISTRATION_2026-09-15.json"
V1_CANDIDATE = ROOT / "research/tools/apma_cut_support_carrier/cut_support_carrier.py"
V1_CHECKER = ROOT / "research/tools/apma_cut_support_carrier/independent_checker.py"
FIRST_FAIL = ROOT / "research/TRUMP_BICAMERAL_CUT_SUPPORT_CARRIER_FIRST_RUN_FAILURE_2026-09-15.json"
PARENT_STATE = ROOT / "registry/TRUMP_CURRENT_STATE_2026-09-15_v2.7.json"
OLD_QUOTIENT = ROOT / "research/tools/apma_interface_quotient/exact_quotient.py"
OLD_QUOTIENT_CHECKER = ROOT / "research/tools/apma_interface_quotient/independent_checker.py"
EXPECTED = {
    V11_PREREG: "2226e7243c4578933e76ac542b655748a25e3230",
    V1_PREREG: "b4eaaf90fe45b2c45867114928e93726132ebaf5",
    V1_CANDIDATE: "012aa1acf52fa12de26bb64df303b2208d396ea9",
    V1_CHECKER: "77a25a8a6cc8a2b8687a4af63f9f765bdcca5680",
    FIRST_FAIL: "7a48329b64a9d92d095e2b382ec65e205bec6ae9",
    PARENT_STATE: "deb9b4b1d32b7dba24b945d80ef933f10044de2a",
    OLD_QUOTIENT: "cc331245bd71b6c83ab6c43b86f961fe53ed31c8",
    OLD_QUOTIENT_CHECKER: "fb5fe1773bbc5cc91a78e13eb1129449b84d3820",
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def run_module(module: str) -> tuple[int, dict]:
    cp = subprocess.run([sys.executable, "-m", module], cwd=ROOT, check=False, capture_output=True, text=True)
    last = cp.stdout.strip().splitlines()[-1] if cp.stdout.strip() else "{}"
    return cp.returncode, json.loads(last)


def shared_variables(canonical: dict, relation_index: int) -> set[int]:
    relation_scope = set(canonical["constraints"][relation_index]["scope"])
    out: set[int] = set()
    for v in relation_scope:
        hits = sum(1 for row in canonical["constraints"] if v in row["scope"])
        if hits > 1:
            out.add(v)
    return out


def main() -> None:
    prereg = json.loads(V11_PREREG.read_text(encoding="utf-8"))
    first_fail = json.loads(FIRST_FAIL.read_text(encoding="utf-8"))
    source = {p.name + "_blob": git_blob_sha1(p) == sha for p, sha in EXPECTED.items()}
    source["v11_prereg_frozen"] = prereg.get("status") == "FROZEN_BEFORE_V1_1_CHECKER"
    source["v11_candidate_frozen_unchanged"] = prereg.get("frozen_v1_candidate", {}).get("blob_sha") == "012aa1acf52fa12de26bb64df303b2208d396ea9"
    source["first_fail_verdict_preserved"] = first_fail.get("verdict") == "FAIL_OR_OPEN_BICAMERAL_CUT_SUPPORT_CARRIER"

    v1_rc, v1_out = run_module("research.tools.apma_cut_support_carrier.independent_checker")
    cand_rc, run = run_module("research.tools.apma_cut_support_carrier.cut_support_carrier")

    pos_raw = candidate.positive_overwidth()
    pos_can = canonicalize_raw(pos_raw)
    pos_parent = parent_mincut.explain_with_mincut(pos_raw)
    pos_ind = independent_carrier(pos_raw)
    pos = run["positive"]
    B = list(pos_ind["cut"]["cut_variables"])
    singleton_components = pos_ind.get("components") == [[0], [1]]
    direct_full_visibility = singleton_components and all(set(B).issubset(set(row["scope"])) for row in pos_can["constraints"])
    shared_sets = [shared_variables(pos_can, i) for i in range(len(pos_can["constraints"]))]
    derived_visibility_condition = singleton_components and all(set(B).issubset(s) for s in shared_sets)

    empty_raw = candidate.empty_intersection_control()
    empty_parent = parent_mincut.explain_with_mincut(empty_raw)
    empty_ind = independent_carrier(empty_raw)
    empty = run["negative_empty"]

    multi_raw = candidate.multi_relation_component_control()
    multi_parent = parent_mincut.explain_with_mincut(multi_raw)
    multi_ind = independent_carrier(multi_raw)
    multi = run["negative_multi_relation_component"]

    support_sizes = sorted(pos_ind.get("support_sizes", []))
    carrier = pos.get("carrier", {})
    rr = carrier.get("resource_receipt", {})

    checks = {
        **{f"V11_P1_{k}": v for k, v in source.items()},
        "V11_P1_old_checker_still_fails": v1_rc != 0 and v1_out.get("verdict") == "FAIL_OR_OPEN_BICAMERAL_CUT_SUPPORT_CARRIER",
        "V11_P1_candidate_main_executes": cand_rc == 0,
        "V11_P2_parent_overwidth": pos_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "V11_P2_parent_zero_branches": pos_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") == 0,
        "V11_P3_independent_cut20": pos_ind.get("cut", {}).get("cut_size") == 20 and B == list(range(20)),
        "V11_P3_candidate_cut_matches": pos.get("parent_cut", {}).get("cut_variables") == B,
        "V11_P4_single_relation_components": singleton_components,
        "V11_P5_direct_full_cut_visibility": direct_full_visibility,
        "V11_P5_all_shared_variables_on_singletons_are_in_cut": all(s.issubset(set(B)) for s in shared_sets),
        "V11_P5_derived_full_visibility_condition": derived_visibility_condition,
        "V11_P6_support_size_multiset": support_sizes == [3, 4],
        "V11_P7_effective_support_one": len(pos_ind.get("common", [])) == 1 and carrier.get("effective_support_size") == 1,
        "V11_P7_carrier_bounded_by_support": carrier.get("effective_support_size", 999) <= carrier.get("support_size_bound", -1),
        "V11_P7_carrier_bounded_by_rows": carrier.get("effective_support_size", 999) <= pos_ind.get("rows", -1),
        "V11_P8_positive_terminal": pos.get("status") == "ADMIT_EXACT_CUT_SUPPORT_INTERSECTION_CARRIER",
        "V11_P8_witness_verified": carrier.get("witness_verified") is True,
        "V11_P9_empty_parent_overwidth": empty_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "V11_P9_empty_independent_unsat": empty_ind.get("status") == "UNSAT" and not empty_ind.get("common"),
        "V11_P9_empty_exact_unsat": empty.get("status") == "EXACT_UNSAT_BY_EMPTY_CUT_SUPPORT_INTERSECTION",
        "V11_P10_multi_parent_overwidth": multi_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "V11_P10_multi_detected": multi_ind.get("status") == "OPEN_COMPONENT_COUNT" and any(len(c) > 1 for c in multi_ind.get("components", [])),
        "V11_P10_multi_open": multi.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "V11_P11_hint_rejected": run["negative_hint"].get("status") == "REJECT_RAW_INPUT",
        "V11_P11_tamper_rejected": run["negative_tamper"].get("status") == "REJECT_TAMPERED_PROVENANCE",
        "V11_P12_zero_raw_cube": rr.get("raw_cut_assignments_enumerated") == 0,
        "V11_P12_zero_cartesian": rr.get("cartesian_products_materialized") == 0,
        "V11_P12_zero_solver": rr.get("solver_invocations") == 0,
        "V11_P12_zero_generic_transfer": rr.get("generic_transfer_calls") == 0,
        "V11_P14_rows_scanned_match": carrier.get("total_input_rows_scanned") == pos_ind.get("rows"),
        "FW_p_vs_np_open": run["scientific_firewall"].get("P_VS_NP") == "OPEN",
        "FW_general_sat_not_proved": run["scientific_firewall"].get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "FW_connected_mixed_not_solved": run["scientific_firewall"].get("CONNECTED_MIXED_CORE_SOLVED") == "NO",
        "FW_arbitrary_unseen_not_proved": run["scientific_firewall"].get("ARBITRARY_UNSEEN_INVARIANT_DISCOVERY") == "NOT_PROVED",
    }

    verdict = "PASS_SCOPED_BICAMERAL_OVERWIDTH_CUT_SUPPORT_INTERSECTION_CARRIER_V1_1" if all(checks.values()) else "FAIL_OR_OPEN_BICAMERAL_CUT_SUPPORT_CARRIER_V1_1"
    out = {
        "artifact_id": "JANUS-TRUMP-BICAMERAL-CUT-SUPPORT-CARRIER-V1-1-INDEPENDENT-CHECK-2026-09-15",
        "authority": "INDEPENDENT_CHECKER__V1_1_SCOPED_ONLY",
        "verdict": verdict,
        "checks": checks,
        "controls": {
            "v1_failure_preserved": v1_out.get("verdict"),
            "positive_parent": pos_parent.get("status"),
            "positive_k": pos_ind.get("cut", {}).get("cut_size"),
            "positive_raw_branch_budget": pos_parent.get("redteam", {}).get("branch_budget"),
            "positive_parent_branch_enumerations": pos_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations"),
            "positive_support_size_multiset": support_sizes,
            "positive_effective_support": [list(x) for x in pos_ind.get("common", [])],
            "positive_terminal": pos.get("status"),
            "empty_terminal": empty.get("status"),
            "multi_terminal": multi.get("status"),
            "hint_terminal": run["negative_hint"].get("status"),
            "tamper_terminal": run["negative_tamper"].get("status"),
        },
        "structural_lemma": {
            "name": "GLOBAL_MINCUT_SINGLETON_COMPONENT_FULL_CUT_VISIBILITY",
            "positive_direct_check": direct_full_visibility,
            "logic": "If a singleton relation omitted a cut variable, its shared variables would be a strict subset of B; variables outside B are private by singleton-after-cut, so deleting the shared subset gives a smaller pairwise variable cut, contradicting global minimum |B|.",
        },
        "complexity": {
            "parent_cut_discovery": "frozen polynomial max-flow",
            "support_projection": "linear in explicit tuple cells",
            "support_intersection": "polynomial and non-expanding",
            "carrier_size": "<= minimum input projected-support size <= explicit input rows",
            "raw_2_to_k_enumeration": 0,
            "cartesian_products": 0,
        },
        "scientific_firewall": candidate.firewall(),
    }
    print(json.dumps(out, sort_keys=True))
    if verdict.startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
