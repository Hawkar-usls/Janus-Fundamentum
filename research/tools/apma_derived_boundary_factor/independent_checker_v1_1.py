from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_component_join_carrier import component_join_carrier_v1_3 as old_join
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as v1
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor_v1_1 as candidate
from research.tools.apma_derived_boundary_factor import independent_checker as independent

ROOT = Path(__file__).resolve().parents[3]
FILES = {
    ROOT / "research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_PREREGISTRATION_2026-09-15.json": "4c3af40842188d2489df8df7ed66c0e3dc8e711e",
    ROOT / "research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1_1_PREREGISTRATION_2026-09-15.json": "b0a784b2fa1dd9380ccee7eec676bb24bf35772a",
    ROOT / "research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_FIRST_RUN_FAILURE_2026-09-15.json": "8aa328fe71d6391491996b5ad8530f52d7cbfc38",
    ROOT / "research/tools/apma_derived_boundary_factor/derived_two_relation_factor.py": "1047351df47ed5f326eef2650da0c9f5ee0f2fda",
    ROOT / "research/tools/apma_derived_boundary_factor/derived_two_relation_factor_v1_1.py": "2332b09a897cbc85e1f5d2e562bc93e170ff5b1c",
    ROOT / "registry/TRUMP_CURRENT_STATE_2026-09-15_v2.9.json": "80bf1fb61ee3a773733f85f4305356d815dd3532",
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> None:
    v11_prereg = json.loads((ROOT / "research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1_1_PREREGISTRATION_2026-09-15.json").read_text(encoding="utf-8"))
    first_fail = json.loads((ROOT / "research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_FIRST_RUN_FAILURE_2026-09-15.json").read_text(encoding="utf-8"))
    source = {p.name + "_blob": git_blob_sha1(p) == sha for p, sha in FILES.items()}
    source["v11_prereg_frozen"] = v11_prereg.get("status") == "FROZEN_BEFORE_V1_1_REPAIR"
    source["repair_class_exact"] = v11_prereg.get("repair_class") == "JSON_SAFE_PROVENANCE_SERIALIZATION_ONLY"
    source["v1_failure_preserved"] = first_fail.get("verdict") == "FAIL_INFRASTRUCTURE_SERIALIZATION_BEFORE_RECEIPT"

    pos_raw = v1.positive_no_anchor_k20()
    pos = candidate.explain(pos_raw)
    pos_ind = independent.independent_global(pos_raw)
    pos_can = canonicalize_raw(pos_raw)
    pos_parent = parent_mincut.explain_with_mincut(pos_raw)
    pos_small = parent_support.explain_overwidth_cut(pos_raw)
    pos_old = old_join.explain_overwidth_component_join(pos_raw)
    B = list(pos_parent.get("cut", {}).get("cut_variables", []))
    comps = parent_support.constraint_components_after_cut(pos_can, B) if B else []
    pair_comp = next((c for c in comps if len(c) == 2), [])
    pair_rels = [pos_can["constraints"][i] for i in pair_comp]
    no_full_anchor = bool(pair_rels) and all(not set(B).issubset(set(r["scope"])) for r in pair_rels)
    union_covers = bool(pair_rels) and set(B).issubset(set().union(*(set(r["scope"]) for r in pair_rels)))
    cand_support = [tuple(x) for x in pos.get("carrier", {}).get("effective_support", [])]
    internal_support_maps = [r.get("support", {}) for r in pos.get("carrier", {}).get("component_results", [])]
    tuple_keys_preserved = all(all(isinstance(k, tuple) for k in support.keys()) for support in internal_support_maps)

    empty_raw = v1.empty_pair_support_control()
    empty = candidate.explain(empty_raw)
    empty_ind = independent.independent_global(empty_raw)

    three = candidate.explain(v1.three_relation_no_anchor_control())
    unit_can, unit_comp, unit_cut = v1.incomplete_cover_unit_control()
    unit_cand = v1.component_support(unit_can, unit_comp, unit_cut)
    unit_ind = independent._indexed_component_support(unit_can, unit_comp, unit_cut)
    hint = candidate.explain(v1.injected_hint_control())
    tamper = candidate.tampered_control()

    carrier = pos.get("carrier", {})
    rr = carrier.get("resource_receipt", {})
    pair_receipts = [r.get("receipt", {}) for r in carrier.get("component_results", []) if r.get("receipt", {}).get("kind") == "DERIVED_TWO_RELATION_NATURAL_JOIN_PROJECT_B"]
    repair = pos.get("v1_1_repair", {})

    checks = {
        **{f"P1_{k}": v for k, v in source.items()},
        "P1_wrapper_repair_exact": repair.get("class") == "JSON_SAFE_PROVENANCE_SERIALIZATION_ONLY",
        "P1_frozen_v1_declared": repair.get("frozen_v1_candidate_blob") == "1047351df47ed5f326eef2650da0c9f5ee0f2fda",
        "P1_tuple_support_keys_preserved_in_memory": tuple_keys_preserved,
        "P2_parent_overwidth": pos_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P2_cut20": B == list(range(20)),
        "P2_zero_raw_branches": pos_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") == 0,
        "P3_singleton_support_parent_open": pos_small.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "P4_old_join_no_anchor": pos_old.get("status") == "OPEN_NO_FULL_CUT_ANCHOR",
        "P5_components_1_and_2": sorted(len(c) for c in comps) == [1, 2],
        "P5_pair_no_raw_full_anchor": no_full_anchor,
        "P6_pair_union_covers_B": union_covers,
        "P7_positive_terminal": pos.get("status") == "ADMIT_EXACT_DERIVED_TWO_RELATION_BOUNDARY_FACTOR",
        "P8_independent_terminal": pos_ind.get("status") == "ADMIT_EXACT_DERIVED_TWO_RELATION_BOUNDARY_FACTOR",
        "P8_support_matches_hash_indexed_join": sorted(cand_support) == sorted(pos_ind.get("support", [])),
        "P8_support_one": len(cand_support) == 1,
        "P9_support_bounded_by_row_product": bool(pair_receipts) and all(r.get("support_size", 10**9) <= r.get("row_pair_product_bound", -1) for r in pair_receipts),
        "P11_witness_verified": carrier.get("witness_verified") is True,
        "P12_empty_candidate_unsat": empty.get("status") == "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
        "P12_empty_independent_unsat": empty_ind.get("status") == "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
        "P13_three_relation_open": three.get("status") == "OPEN_COMPONENT_RELATION_COUNT_GT_2",
        "P14_incomplete_candidate_open": unit_cand.get("status") == "OPEN_INCOMPLETE_TWO_RELATION_CUT_COVER",
        "P14_incomplete_independent_open": unit_ind.get("status") == "OPEN_INCOMPLETE_TWO_RELATION_CUT_COVER",
        "P15_zero_raw_cube": rr.get("raw_cut_assignments_enumerated") == 0,
        "P15_zero_join_chain": rr.get("unbounded_join_chains") == 0,
        "P15_zero_cross_component_cartesian": rr.get("cartesian_products_across_components") == 0,
        "P15_zero_generic_transfer": rr.get("generic_transfer_calls") == 0,
        "P15_zero_external_solver": rr.get("external_solver_invocations") == 0,
        "P16_hint_rejected": hint.get("status") == "REJECT_RAW_INPUT",
        "P16_tamper_rejected": tamper.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "FW_p_vs_np_open": pos.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
        "FW_general_sat_not_proved": pos.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "FW_connected_mixed_not_solved": pos.get("scientific_firewall", {}).get("CONNECTED_MIXED_CORE_SOLVED") == "NO",
        "FW_general_boundary_not_proved": pos.get("scientific_firewall", {}).get("GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION") == "NOT_PROVED",
    }
    verdict = "PASS_SCOPED_BICAMERAL_OVERWIDTH_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1_1" if all(checks.values()) else "FAIL_OR_OPEN_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1_1"
    out = {
        "artifact_id": "JANUS-TRUMP-BICAMERAL-DERIVED-TWO-RELATION-BOUNDARY-FACTOR-V1-1-INDEPENDENT-CHECK-2026-09-15",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "verdict": verdict,
        "checks": checks,
        "controls": {
            "first_failure_preserved": first_fail.get("verdict"),
            "positive_parent": pos_parent.get("status"),
            "positive_cut": B,
            "positive_components": comps,
            "positive_old_join": pos_old.get("status"),
            "positive_terminal": pos.get("status"),
            "positive_support": [list(x) for x in cand_support],
            "empty_terminal": empty.get("status"),
            "three_terminal": three.get("status"),
            "incomplete_unit_terminal": unit_cand.get("status"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tamper.get("status"),
        },
        "complexity": {
            "row_pair_comparisons": rr.get("row_pair_comparisons"),
            "max_component_row_pair_product_bound": rr.get("max_component_row_pair_product_bound"),
            "raw_2_to_k_enumeration": rr.get("raw_cut_assignments_enumerated"),
            "unbounded_join_chains": rr.get("unbounded_join_chains"),
            "claim": "FIXED_POLYNOMIAL_SINGLE_JOIN_PER_TWO_RELATION_COMPONENT",
        },
        "repair": repair,
        "scientific_firewall": v1.firewall(),
    }
    print(json.dumps(candidate._json_safe_keys(out), sort_keys=True))
    if verdict.startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
