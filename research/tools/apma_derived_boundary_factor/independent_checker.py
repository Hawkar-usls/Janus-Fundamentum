from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_component_join_carrier import component_join_carrier_v1_3 as old_join
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as candidate

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_BICAMERAL_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_PREREGISTRATION_2026-09-15.json"
CANDIDATE = ROOT / "research/tools/apma_derived_boundary_factor/derived_two_relation_factor.py"
PARENT_STATE = ROOT / "registry/TRUMP_CURRENT_STATE_2026-09-15_v2.9.json"
EXPECTED = {
    PREREG: "4c3af40842188d2489df8df7ed66c0e3dc8e711e",
    CANDIDATE: "1047351df47ed5f326eef2650da0c9f5ee0f2fda",
    PARENT_STATE: "80bf1fb61ee3a773733f85f4305356d815dd3532",
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def _row_tuple(row) -> tuple[int, ...]:
    return tuple(int(x) for x in row)


def _indexed_component_support(canonical: dict, component: list[int], cut: list[int]) -> dict:
    B = set(cut)
    if len(component) == 1:
        gi = component[0]
        rel = canonical["constraints"][gi]
        scope = list(rel["scope"])
        if not B.issubset(set(scope)):
            return {"status": "OPEN_SINGLETON_WITHOUT_FULL_CUT_VISIBILITY", "support": {}}
        pos = {v: i for i, v in enumerate(scope)}
        support = {}
        for raw in rel["allowed"]:
            row = _row_tuple(raw)
            sigma = tuple(row[pos[v]] for v in cut)
            support.setdefault(sigma, {"rows": [(gi, row)]})
        return {"status": "ADMIT_DIRECT_SINGLETON_SUPPORT", "support": support}
    if len(component) != 2:
        return {"status": "OPEN_COMPONENT_RELATION_COUNT_GT_2", "support": {}}
    g0, g1 = component
    r0, r1 = canonical["constraints"][g0], canonical["constraints"][g1]
    s0, s1 = list(r0["scope"]), list(r1["scope"])
    if not B.issubset(set(s0) | set(s1)):
        return {"status": "OPEN_INCOMPLETE_TWO_RELATION_CUT_COVER", "support": {}}
    shared = sorted(set(s0) & set(s1))
    p0 = {v: i for i, v in enumerate(s0)}
    p1 = {v: i for i, v in enumerate(s1)}
    index = {}
    for raw1 in r1["allowed"]:
        row1 = _row_tuple(raw1)
        key = tuple(row1[p1[v]] for v in shared)
        index.setdefault(key, []).append(row1)
    support = {}
    matches = 0
    for raw0 in r0["allowed"]:
        row0 = _row_tuple(raw0)
        key = tuple(row0[p0[v]] for v in shared)
        for row1 in index.get(key, []):
            matches += 1
            merged = {v: row0[i] for i, v in enumerate(s0)}
            for i, v in enumerate(s1):
                bit = row1[i]
                if v in merged and merged[v] != bit:
                    raise AssertionError("INDEXED_JOIN_KEY_INCONSISTENT")
                merged[v] = bit
            sigma = tuple(merged[v] for v in cut)
            support.setdefault(sigma, {"rows": [(g0, row0), (g1, row1)]})
    return {
        "status": "ADMIT_DERIVED_TWO_RELATION_SUPPORT" if support else "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
        "support": support,
        "matches": matches,
        "product_bound": len(r0["allowed"]) * len(r1["allowed"]),
    }


def independent_global(raw: dict) -> dict:
    canonical = canonicalize_raw(raw)
    parent = parent_mincut.explain_with_mincut(raw)
    if parent.get("status") != "OPEN_MINCUT_BRANCH_BUDGET":
        return {"status": "OUT_OF_SCOPE_PARENT_NOT_OVERWIDTH"}
    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    results = [_indexed_component_support(canonical, c, cut) for c in components]
    for r in results:
        if r["status"].startswith("OPEN_"):
            return {"status": r["status"], "cut": cut, "components": components, "results": results}
        if r["status"] == "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT":
            return {"status": r["status"], "cut": cut, "components": components, "results": results, "support": []}
    supports = [set(r["support"]) for r in results]
    common = sorted(set.intersection(*supports) if supports else set())
    return {
        "status": "ADMIT_EXACT_DERIVED_TWO_RELATION_BOUNDARY_FACTOR" if common else "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
        "cut": cut,
        "components": components,
        "results": results,
        "support": common,
    }


def main() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    source = {p.name + "_blob": git_blob_sha1(p) == sha for p, sha in EXPECTED.items()}
    source["prereg_frozen"] = prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION"

    pos_raw = candidate.positive_no_anchor_k20()
    pos = candidate.explain(pos_raw)
    pos_ind = independent_global(pos_raw)
    pos_can = canonicalize_raw(pos_raw)
    pos_parent = parent_mincut.explain_with_mincut(pos_raw)
    pos_support_parent = parent_support.explain_overwidth_cut(pos_raw)
    pos_old = old_join.explain_overwidth_component_join(pos_raw)
    B = list(pos_parent.get("cut", {}).get("cut_variables", []))
    comps = parent_support.constraint_components_after_cut(pos_can, B) if B else []
    pair_comp = next((c for c in comps if len(c) == 2), [])
    pair_rels = [pos_can["constraints"][i] for i in pair_comp]
    no_full_anchor = bool(pair_rels) and all(not set(B).issubset(set(r["scope"])) for r in pair_rels)
    union_covers = bool(pair_rels) and set(B).issubset(set().union(*(set(r["scope"]) for r in pair_rels)))
    cand_support = [tuple(x) for x in pos.get("carrier", {}).get("effective_support", [])]

    empty_raw = candidate.empty_pair_support_control()
    empty = candidate.explain(empty_raw)
    empty_ind = independent_global(empty_raw)

    three_raw = candidate.three_relation_no_anchor_control()
    three = candidate.explain(three_raw)

    unit_can, unit_comp, unit_cut = candidate.incomplete_cover_unit_control()
    unit_cand = candidate.component_support(unit_can, unit_comp, unit_cut)
    unit_ind = _indexed_component_support(unit_can, unit_comp, unit_cut)

    hint = candidate.explain(candidate.injected_hint_control())
    tamper = candidate.tampered_control()
    rr = pos.get("carrier", {}).get("resource_receipt", {})
    pair_receipts = [r.get("receipt", {}) for r in pos.get("carrier", {}).get("component_results", []) if r.get("receipt", {}).get("kind") == "DERIVED_TWO_RELATION_NATURAL_JOIN_PROJECT_B"]

    checks = {
        **{f"P1_{k}": v for k, v in source.items()},
        "P2_parent_overwidth": pos_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P2_cut20": pos_parent.get("cut", {}).get("cut_size") == 20 and B == list(range(20)),
        "P2_zero_raw_branches": pos_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") == 0,
        "P3_singleton_support_parent_open": pos_support_parent.get("status") == "OPEN_UNSUPPORTED_CUT_SUPPORT_CARRIER",
        "P4_old_join_no_anchor": pos_old.get("status") == "OPEN_NO_FULL_CUT_ANCHOR",
        "P5_component_sizes": sorted(len(c) for c in comps) == [1, 2],
        "P5_pair_has_no_raw_full_anchor": no_full_anchor,
        "P6_pair_union_covers_B": union_covers,
        "P7_positive_terminal": pos.get("status") == "ADMIT_EXACT_DERIVED_TWO_RELATION_BOUNDARY_FACTOR",
        "P8_independent_terminal": pos_ind.get("status") == "ADMIT_EXACT_DERIVED_TWO_RELATION_BOUNDARY_FACTOR",
        "P8_support_matches_indexed_join": sorted(cand_support) == sorted(pos_ind.get("support", [])),
        "P8_effective_support_one": len(cand_support) == 1,
        "P9_pair_support_bounded_by_product": bool(pair_receipts) and all(r.get("support_size", 10**9) <= r.get("row_pair_product_bound", -1) for r in pair_receipts),
        "P11_witness_verified": pos.get("carrier", {}).get("witness_verified") is True,
        "P12_empty_candidate_unsat": empty.get("status") == "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
        "P12_empty_independent_unsat": empty_ind.get("status") == "EXACT_UNSAT_BY_EMPTY_DERIVED_COMPONENT_SUPPORT",
        "P13_three_relation_open": three.get("status") == "OPEN_COMPONENT_RELATION_COUNT_GT_2",
        "P14_incomplete_cover_candidate_open": unit_cand.get("status") == "OPEN_INCOMPLETE_TWO_RELATION_CUT_COVER",
        "P14_incomplete_cover_independent_open": unit_ind.get("status") == "OPEN_INCOMPLETE_TWO_RELATION_CUT_COVER",
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
        "FW_arbitrary_unseen_not_proved": pos.get("scientific_firewall", {}).get("ARBITRARY_UNSEEN_INVARIANT_DISCOVERY") == "NOT_PROVED",
        "FW_general_boundary_compression_not_proved": pos.get("scientific_firewall", {}).get("GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION") == "NOT_PROVED",
    }
    verdict = "PASS_SCOPED_BICAMERAL_OVERWIDTH_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1" if all(checks.values()) else "FAIL_OR_OPEN_DERIVED_TWO_RELATION_BOUNDARY_FACTOR_V1"
    out = {
        "artifact_id": "JANUS-TRUMP-BICAMERAL-DERIVED-TWO-RELATION-BOUNDARY-FACTOR-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "verdict": verdict,
        "checks": checks,
        "controls": {
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
            "raw_2_to_k_enumeration": rr.get("raw_cut_assignments_enumerated"),
            "row_pair_comparisons": rr.get("row_pair_comparisons"),
            "max_component_row_pair_product_bound": rr.get("max_component_row_pair_product_bound"),
            "unbounded_join_chains": rr.get("unbounded_join_chains"),
            "claim": "FIXED_POLYNOMIAL_SINGLE_JOIN_PER_TWO_RELATION_COMPONENT",
        },
        "scientific_firewall": candidate.firewall(),
    }
    print(json.dumps(out, sort_keys=True))
    if verdict.startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
