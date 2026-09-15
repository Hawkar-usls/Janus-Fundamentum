from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, induce_basis
from research.tools.apma_unseen_basis.compositional_basis import (
    induce_compositional_basis,
    disconnected_mixed,
    connected_mixed,
    bridged_mixed,
    many_components,
    permuted,
)

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_RAW_COMPOSITIONAL_BASIS_INDUCTION_PREREGISTRATION_2026-09-15.json"
CANDIDATE = ROOT / "research/tools/apma_unseen_basis/compositional_basis.py"
PARENT = ROOT / "research/tools/apma_unseen_basis/raw_relation_basis.py"
PREREG_SHA1 = "212eeb78a08b8a558248873f50a776bed61a7748"
CANDIDATE_SHA1 = "fdc83a3368a4ad362f00d3ee8aad958f06f8d264"
PARENT_SHA1 = "63490c05ef3e91a4f682f75da26ff2af811839a6"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def independent_components(raw: dict) -> list[list[int]]:
    canonical = canonicalize_raw(raw)
    rows = canonical["constraints"]
    var_to_rows: dict[int, set[int]] = {}
    for i, row in enumerate(rows):
        for v in row["scope"]:
            var_to_rows.setdefault(v, set()).add(i)
    adj = {i: set() for i in range(len(rows))}
    for indices in var_to_rows.values():
        ids = sorted(indices)
        for i in ids:
            adj[i].update(j for j in ids if j != i)
    unseen = set(adj)
    components = []
    while unseen:
        start = min(unseen)
        stack = [start]
        seen = set()
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            unseen.discard(x)
            stack.extend(sorted(adj[x] - seen, reverse=True))
        components.append(sorted(seen))

    def key(indices: list[int]):
        variables = sorted({v for i in indices for v in rows[i]["scope"]})
        semantic_rows = sorted((tuple(rows[i]["scope"]), tuple("".join(str(int(x)) for x in t) for t in rows[i]["allowed"])) for i in indices)
        return variables, semantic_rows

    return sorted(components, key=key)


def component_varsets(raw: dict, components: list[list[int]]) -> list[set[int]]:
    rows = canonicalize_raw(raw)["constraints"]
    return [{v for i in comp for v in rows[i]["scope"]} for comp in components]


def validate_partition(raw: dict, partition: list[list[int]]) -> bool:
    canonical = canonicalize_raw(raw)
    n = len(canonical["constraints"])
    flat = [i for comp in partition for i in comp]
    if sorted(flat) != list(range(n)) or len(flat) != len(set(flat)):
        return False
    varsets = component_varsets(raw, partition)
    for i in range(len(varsets)):
        for j in range(i + 1, len(varsets)):
            if varsets[i] & varsets[j]:
                return False
    return sorted(sorted(c) for c in partition) == sorted(sorted(c) for c in independent_components(raw))


def selected_bases(result: dict) -> list[str | None]:
    return [c["local_basis_certificate"].get("selected_basis") for c in result.get("portfolio", [])]


def main() -> None:
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    source = CANDIDATE.read_text(encoding="utf-8")

    d_raw = disconnected_mixed()
    c_raw = connected_mixed()
    b_raw = bridged_mixed()
    m_raw = many_components()

    global_d = induce_basis(d_raw)
    d = induce_compositional_basis(d_raw)
    c = induce_compositional_basis(c_raw)
    b = induce_compositional_basis(b_raw)
    m = induce_compositional_basis(m_raw)
    dp = induce_compositional_basis(permuted(d_raw))

    d_ind = independent_components(d_raw)
    c_ind = independent_components(c_raw)
    b_ind = independent_components(b_raw)
    m_ind = independent_components(m_raw)

    fake_connected_split = [[0], [1]]
    metrics = [x.get("metrics", {}) for x in (d, c, b, m)]

    checks = {
        "P1_prereg_blob": git_blob_sha1(PREREG) == PREREG_SHA1,
        "P1_candidate_blob": git_blob_sha1(CANDIDATE) == CANDIDATE_SHA1,
        "P1_parent_blob": git_blob_sha1(PARENT) == PARENT_SHA1,
        "P1_prereg_frozen": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "P2_disconnected_components_independent": d.get("component_count") == len(d_ind) == 2,
        "P2_connected_component_independent": c.get("component_count") == len(c_ind) == 1,
        "P2_bridge_component_independent": b.get("component_count") == len(b_ind) == 1,
        "P2_many_components_independent": m.get("component_count") == len(m_ind) == 8,
        "P2_disjoint_component_variables_reported": all(x.get("exact_decomposition_certificate", {}).get("pairwise_disjoint_component_variables") is True for x in (d, c, b, m)),
        "P3_global_single_basis_rejects_disconnected_mixed_language": global_d.get("status") == "OPEN_NO_SCHAEFER_BASIS",
        "P3_compositional_admits_disconnected_mixed": d.get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO",
        "P3_disconnected_bases_exact": selected_bases(d) == ["BIJUNCTIVE", "AFFINE"],
        "P3_many_all_local_admitted": m.get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO" and m.get("open_component_count") == 0,
        "P3_many_expected_alternating_basis_multiset": sorted(selected_bases(m)) == sorted(["BIJUNCTIVE", "AFFINE"] * 4),
        "P4_component_coverage_exact_disconnected": d.get("exact_decomposition_certificate", {}).get("covered_constraint_count") == len(d_raw["constraints"]),
        "P4_component_coverage_exact_many": m.get("exact_decomposition_certificate", {}).get("covered_constraint_count") == len(m_raw["constraints"]),
        "P5_zero_cartesian_products": all(x.get("cartesian_products_materialized") == 0 for x in metrics),
        "P5_additive_portfolio_records": m.get("metrics", {}).get("portfolio_records") == m.get("component_count") == 8,
        "P6_connected_mixed_open": c.get("status") == "OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS" and c.get("open_component_count") == 1,
        "P6_bridge_merges_and_open": b.get("status") == "OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS" and b.get("component_count") == 1,
        "P6_connected_local_basis_is_open": c["portfolio"][0]["local_basis_certificate"].get("status") == "OPEN_NO_SCHAEFER_BASIS",
        "P7_permutation_same_semantic_portfolio_hash": d.get("semantic_portfolio_sha256") == dp.get("semantic_portfolio_sha256"),
        "P7_permutation_same_basis_sequence": selected_bases(d) == selected_bases(dp),
        "P8_fake_split_rejected": validate_partition(c_raw, fake_connected_split) is False,
        "P8_true_partition_accepted": validate_partition(d_raw, d_ind) is True,
        "P8_candidate_no_itertools": "import itertools" not in source,
        "P8_candidate_no_full_cube_pattern": "range(1 <<" not in source and "product(" not in source,
        "P8_zero_full_variable_cube": all(x.get("full_variable_assignments_enumerated") == 0 for x in metrics),
        "P8_zero_solver_invocations": all(x.get("solver_invocations") == 0 for x in metrics),
        "P9_firewall_p_vs_np_open": d.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
        "P9_firewall_general_sat_not_proved": d.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "P9_connected_mixed_not_solved": d.get("scientific_firewall", {}).get("CONNECTED_MIXED_CORE_SOLVED") == "NO",
        "P9_arbitrary_discovery_not_proved": d.get("scientific_firewall", {}).get("ARBITRARY_UNSEEN_INVARIANT_DISCOVERY") == "NOT_PROVED",
    }

    verdict = "PASS_SCOPED_RAW_COMPOSITIONAL_BASIS_INDUCTION" if all(checks.values()) else "FAIL_OR_OPEN_RAW_COMPOSITIONAL_BASIS_INDUCTION"
    out = {
        "artifact_id": "JANUS-TRUMP-RAW-COMPOSITIONAL-BASIS-INDUCTION-INDEPENDENT-CHECK-2026-09-15-v1.0",
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "checks": checks,
        "controls": {
            "disconnected_global_single_basis": global_d.get("status"),
            "disconnected_compositional": d.get("status"),
            "disconnected_bases": selected_bases(d),
            "connected_mixed": c.get("status"),
            "bridged_mixed": b.get("status"),
            "many_components": m.get("component_count"),
            "many_bases": selected_bases(m),
            "cartesian_products_materialized": m.get("metrics", {}).get("cartesian_products_materialized"),
        },
        "theorem": "For variable-disjoint incidence components, conjunction semantics factor exactly by component. Canonical incidence decomposition plus the sealed label-blind local basis induction yields an additive exact basis portfolio in polynomial time over the explicit raw object. Connected mixed components outside the local library fail closed.",
        "complexity": {
            "component_discovery": "O(scope-incidence * alpha(constraints)) in candidate; independent checker uses polynomial graph traversal",
            "local_basis_induction": "sum over components O(sum_R s_R^3 a_R)",
            "portfolio_storage": "additive in component certificates",
            "cartesian_product": 0,
            "full_variable_cube": 0,
            "solver_execution": 0
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW"
        },
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
