from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_explanation.bicameral_explainer import explain_connected_mixed_core
from research.tools.apma_bicameral_pair_separator.pair_separator_explainer import (
    ARTIFACT_ID,
    explain_with_pair_separator,
    positive_prior_biconnected,
    negative_three_variable_cut_required,
    injected_hint_control,
    observation_receipt,
    redteam_pair_proposal,
)

CHECK_ARTIFACT = "JANUS-TRUMP-BICAMERAL-PAIR-SEPARATOR-EXPLANATION-INDEPENDENT-CHECK-2026-09-15-v1.0"
CANDIDATE_REL = Path("research/tools/apma_bicameral_pair_separator/pair_separator_explainer.py")
CANDIDATE_GIT_BLOB_SHA1 = "b6dc5fde585affb167e74308bc8f10c64f7d2990"
PREREG_REL = Path("research/TRUMP_BICAMERAL_PAIR_SEPARATOR_EXPLANATION_PREREGISTRATION_2026-09-15.json")
PREREG_GIT_BLOB_SHA1 = "1ad44d91f9ea23dc6b1e7891ff5631ebbe13d149"
PARENT_REL = Path("research/tools/apma_bicameral_explanation/bicameral_explainer.py")
PARENT_GIT_BLOB_SHA1 = "bc3a9e0040b255cd4c976512a619f90644434d45"
COMPOSER_REL = Path("research/tools/apma_unseen_basis/compositional_basis.py")
COMPOSER_GIT_BLOB_SHA1 = "fdc83a3368a4ad362f00d3ee8aad958f06f8d264"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_obj(obj) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def independent_graph(canonical: dict) -> dict[str, set[str]]:
    g: dict[str, set[str]] = {}
    for v in canonical["variables"]:
        g[f"v:{v}"] = set()
    for i, row in enumerate(canonical["constraints"]):
        c = f"c:{i}"
        g[c] = set()
        for v in row["scope"]:
            vn = f"v:{v}"
            g[c].add(vn)
            g[vn].add(c)
    return g


def independent_constraint_component_count(canonical: dict, removed_vars: tuple[int, ...]) -> int:
    g = independent_graph(canonical)
    removed = {f"v:{v}" for v in removed_vars}
    constraint_nodes = {n for n in g if n.startswith("c:")}
    seen: set[str] = set()
    count = 0
    for start in sorted(n for n in g if n not in removed):
        if start in seen:
            continue
        stack = [start]
        has_constraint = False
        while stack:
            n = stack.pop()
            if n in seen or n in removed:
                continue
            seen.add(n)
            if n in constraint_nodes:
                has_constraint = True
            stack.extend(x for x in g[n] if x not in seen and x not in removed)
        if has_constraint:
            count += 1
    return count


def independent_pair_separators(canonical: dict) -> list[list[int]]:
    vs = canonical["variables"]
    out = []
    for i in range(len(vs)):
        for j in range(i + 1, len(vs)):
            a, b = vs[i], vs[j]
            if independent_constraint_component_count(canonical, (a, b)) > 1:
                out.append([a, b])
    return out


def independent_restrict(canonical: dict, pair: list[int], values: list[int]) -> dict:
    assignment = {pair[0]: values[0], pair[1]: values[1]}
    constraints = []
    unsat = False
    for row in canonical["constraints"]:
        scope = list(row["scope"])
        positions = {v: scope.index(v) for v in pair if v in scope}
        if not positions:
            constraints.append({"id": row["id"], "scope": scope, "allowed": [list(t) for t in row["allowed"]]})
            continue
        survivors = []
        for raw_t in row["allowed"]:
            t = tuple(int(x) for x in raw_t)
            if all(t[pos] == assignment[v] for v, pos in positions.items()):
                survivors.append(t)
        if not survivors:
            unsat = True
            break
        keep = [idx for idx, v in enumerate(scope) if v not in assignment]
        new_scope = [scope[idx] for idx in keep]
        new_tuples = sorted({tuple(t[idx] for idx in keep) for t in survivors})
        if new_scope:
            constraints.append({"id": row["id"], "scope": new_scope, "allowed": [list(t) for t in new_tuples]})
    residual = {"variables": sorted({v for row in constraints for v in row["scope"]}), "constraints": constraints}
    body = {"assigned_variables": list(pair), "assigned_values": list(values), "branch_unsat": unsat, "residual": residual if not unsat else None}
    body["restriction_sha256"] = sha256_obj(body)
    return body


def independent_branch_admitted(restriction: dict) -> bool:
    if restriction["branch_unsat"]:
        return True
    residual = restriction["residual"]
    if not residual["constraints"]:
        return True
    return induce_compositional_basis(residual).get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO"


def permuted_positive() -> dict:
    raw = positive_prior_biconnected()
    return {
        "variables": list(raw["variables"]),
        "constraints": [
            {"id": row["id"], "scope": list(row["scope"]), "allowed": list(reversed(row["allowed"]))}
            for row in reversed(raw["constraints"])
        ],
    }


def main() -> None:
    root = repo_root()
    prereg = json.loads((root / PREREG_REL).read_text(encoding="utf-8"))
    source_checks = {
        "candidate_blob": git_blob_sha1(root / CANDIDATE_REL) == CANDIDATE_GIT_BLOB_SHA1,
        "prereg_blob": git_blob_sha1(root / PREREG_REL) == PREREG_GIT_BLOB_SHA1,
        "prereg_frozen": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "parent_single_blob": git_blob_sha1(root / PARENT_REL) == PARENT_GIT_BLOB_SHA1,
        "sealed_composer_blob": git_blob_sha1(root / COMPOSER_REL) == COMPOSER_GIT_BLOB_SHA1,
    }

    positive_raw = positive_prior_biconnected()
    positive_canonical = canonicalize_raw(positive_raw)
    parent_positive = explain_connected_mixed_core(positive_raw)
    positive = explain_with_pair_separator(positive_raw)
    independent_pairs = independent_pair_separators(positive_canonical)
    pair = [0,1]
    independent_restrictions = [independent_restrict(positive_canonical, pair, values) for values in [[0,0],[0,1],[1,0],[1,1]]]
    selected = positive.get("selected_explanation") or {}
    candidate_restrictions = [b["restriction"] for b in selected.get("branches", [])]
    independent_statuses = [independent_branch_admitted(r) for r in independent_restrictions]

    negative_raw = negative_three_variable_cut_required()
    negative_canonical = canonicalize_raw(negative_raw)
    negative = explain_with_pair_separator(negative_raw)
    negative_pairs = independent_pair_separators(negative_canonical)
    parent_negative = explain_connected_mixed_core(negative_raw)

    hint = explain_with_pair_separator(injected_hint_control())
    permuted = explain_with_pair_separator(permuted_positive())

    obs = observation_receipt(positive_canonical)
    proposal = dict(positive["proposals"][0])
    proposal["separator_variables"] = [0,2]
    tampered = redteam_pair_proposal(positive_canonical, obs, proposal)

    branch_replay_statuses = [b["replay"]["status"] for b in selected.get("branches", [])]
    checks = {
        "P1_source_guard": all(source_checks.values()),
        "P2_parent_single_variable_positive_is_open": parent_positive.get("status") == "OPEN_NO_EXACT_BICAMERAL_EXPLANATION",
        "P2_parent_single_variable_negative_is_open": parent_negative.get("status") == "OPEN_NO_EXACT_BICAMERAL_EXPLANATION",
        "P3_independent_positive_pair_is_exactly_01": independent_pairs == [[0,1]],
        "P3_candidate_positive_pair_is_exactly_01": positive.get("observation", {}).get("pair_separators") == [[0,1]],
        "P4_positive_terminal_admits": positive.get("status") == "ADMIT_EXACT_PAIR_SEPARATOR_EXPLANATION",
        "P4_selected_pair_01": selected.get("separator_variables") == [0,1],
        "P5_exactly_four_branches": [b["assignment"] for b in selected.get("branches", [])] == [[0,0],[0,1],[1,0],[1,1]],
        "P6_candidate_restrictions_match_independent": candidate_restrictions == independent_restrictions,
        "P6_branch_00_is_exact_unsat": bool(independent_restrictions) and independent_restrictions[0]["branch_unsat"] is True and branch_replay_statuses[0] == "EXACT_UNSAT_BY_EMPTY_RELATION",
        "P7_all_independent_branches_admitted": all(independent_statuses),
        "P7_all_candidate_branch_replays_admitted": all(b["replay"]["admitted"] for b in selected.get("branches", [])),
        "P8_negative_has_no_pair_separator": negative_pairs == [],
        "P8_negative_fails_closed": negative.get("status") == "OPEN_NO_EXACT_PAIR_SEPARATOR_EXPLANATION",
        "P9_hint_rejected_before_proposal": hint.get("status") == "REJECT_RAW_INPUT",
        "P10_tampered_pair_rejected": tampered.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "P11_permutation_preserves_terminal": permuted.get("status") == "ADMIT_EXACT_PAIR_SEPARATOR_EXPLANATION",
        "P11_permutation_preserves_pair": (permuted.get("selected_explanation") or {}).get("separator_variables") == [0,1],
        "P12_no_solver_execution": positive.get("metrics", {}).get("solver_invocations") == 0 and negative.get("metrics", {}).get("solver_invocations") == 0,
        "P12_no_generic_transfer": positive.get("metrics", {}).get("generic_transfer_calls") == 0 and negative.get("metrics", {}).get("generic_transfer_calls") == 0,
        "P12_no_full_variable_cube": positive.get("metrics", {}).get("full_variable_assignments_enumerated") == 0 and negative.get("metrics", {}).get("full_variable_assignments_enumerated") == 0,
        "P12_no_cartesian_products": positive.get("metrics", {}).get("cartesian_products_materialized") == 0 and negative.get("metrics", {}).get("cartesian_products_materialized") == 0,
        "P13_receipt_content_bound": bool(positive.get("provenance_receipt", {}).get("pair_separator_receipt_sha256")),
        "P14_firewall_p_vs_np_open": positive["scientific_firewall"]["P_VS_NP"] == "OPEN",
        "P14_firewall_general_sat_not_proved": positive["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "P14_firewall_connected_mixed_not_solved": positive["scientific_firewall"]["CONNECTED_MIXED_CORE_SOLVED"] == "NO",
        "P14_firewall_arbitrary_unseen_not_proved": positive["scientific_firewall"]["ARBITRARY_UNSEEN_INVARIANT_DISCOVERY"] == "NOT_PROVED",
        "P14_firewall_growing_separator_not_proved": positive["scientific_firewall"]["GROWING_SEPARATOR_DISCOVERY"] == "NOT_PROVED",
    }

    verdict = "PASS_SCOPED_BICAMERAL_TWO_VARIABLE_SEPARATOR_EXPLANATION_INDUCTION" if all(checks.values()) else "FAIL_BICAMERAL_TWO_VARIABLE_SEPARATOR_EXPLANATION_INDUCTION"
    out = {
        "artifact_id": CHECK_ARTIFACT,
        "authority": "INDEPENDENT_CHECKER__SCOPED_ONLY",
        "candidate_artifact_id": ARTIFACT_ID,
        "checks": checks,
        "source_checks": source_checks,
        "controls": {
            "positive_parent_single": parent_positive.get("status"),
            "positive_pair_separators": independent_pairs,
            "positive_terminal": positive.get("status"),
            "positive_selected_pair": selected.get("separator_variables"),
            "positive_branch_statuses": branch_replay_statuses,
            "negative_parent_single": parent_negative.get("status"),
            "negative_pair_separators": negative_pairs,
            "negative_terminal": negative.get("status"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tampered.get("status"),
            "permuted_terminal": permuted.get("status"),
        },
        "complexity": {
            "candidate_pair_count_upper_bound": "V*(V-1)/2",
            "branches_per_pair": 4,
            "claim": "POLYNOMIAL_IN_EXPLICIT_RELATION_TABLE_INPUT_FOR_FIXED_SEPARATOR_SIZE_2",
            "growing_separator_size": "NOT_CLAIMED",
            "finite_controls_are_not_asymptotic_evidence": True,
        },
        "scientific_firewall": positive["scientific_firewall"],
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
