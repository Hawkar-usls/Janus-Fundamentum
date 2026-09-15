from __future__ import annotations

import copy
import hashlib
import json

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, induce_basis
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_explanation.bicameral_explainer import (
    ARTIFACT_ID,
    explain_connected_mixed_core,
    positive_connected_articulation,
    negative_biconnected_mixed,
    injected_hint_control,
    redteam_proposal,
)

VERDICT = "PASS_SCOPED_BICAMERAL_SINGLE_VARIABLE_SEPARATOR_EXPLANATION_INDUCTION"


def sha256_obj(obj) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha256(data).hexdigest()


def independent_incidence(canonical: dict) -> tuple[dict[str, set[str]], list[int]]:
    graph: dict[str, set[str]] = {}
    for v in canonical["variables"]:
        graph[f"V{v}"] = set()
    for i, row in enumerate(canonical["constraints"]):
        c = f"C{i}"
        graph[c] = set()
        for v in row["scope"]:
            n = f"V{v}"
            graph[c].add(n)
            graph[n].add(c)

    def constraint_component_count(removed: str | None) -> int:
        seen: set[str] = set()
        count = 0
        for start in sorted(graph):
            if start == removed or start in seen or not start.startswith("C"):
                continue
            count += 1
            queue = [start]
            while queue:
                node = queue.pop(0)
                if node in seen or node == removed:
                    continue
                seen.add(node)
                for nxt in graph[node]:
                    if nxt != removed and nxt not in seen:
                        queue.append(nxt)
        return count

    arts = [v for v in canonical["variables"] if constraint_component_count(f"V{v}") > 1]
    return graph, arts


def independent_restrict(canonical: dict, variable: int, value: int) -> dict:
    residual = []
    for row in canonical["constraints"]:
        scope = list(row["scope"])
        tuples = [tuple(t) for t in row["allowed"]]
        if variable not in scope:
            residual.append({"id": row["id"], "scope": scope, "allowed": [list(t) for t in tuples]})
            continue
        p = scope.index(variable)
        kept = sorted({t[:p] + t[p + 1 :] for t in tuples if t[p] == value})
        if not kept:
            return {"unsat": True, "raw": None}
        new_scope = scope[:p] + scope[p + 1 :]
        if not new_scope:
            continue
        residual.append({"id": row["id"], "scope": new_scope, "allowed": [list(t) for t in kept]})
    vars_ = sorted({v for row in residual for v in row["scope"]})
    return {"unsat": False, "raw": {"variables": vars_, "constraints": residual}}


def permuted_positive() -> dict:
    raw = positive_connected_articulation()
    return {
        "variables": list(raw["variables"]),
        "constraints": [
            {"id": "renamed_b", "scope": list(raw["constraints"][1]["scope"]), "allowed": list(reversed(raw["constraints"][1]["allowed"]))},
            {"id": "renamed_a", "scope": list(raw["constraints"][0]["scope"]), "allowed": list(reversed(raw["constraints"][0]["allowed"]))},
        ],
    }


def main() -> None:
    pos_raw = positive_connected_articulation()
    pos_can = canonicalize_raw(pos_raw)
    neg_raw = negative_biconnected_mixed()
    neg_can = canonicalize_raw(neg_raw)

    pos_parent_global = induce_basis(pos_raw)
    pos_parent_composed = induce_compositional_basis(pos_raw)
    pos = explain_connected_mixed_core(pos_raw)
    neg = explain_connected_mixed_core(neg_raw)
    hint = explain_connected_mixed_core(injected_hint_control())
    perm = explain_connected_mixed_core(permuted_positive())

    _, pos_arts = independent_incidence(pos_can)
    _, neg_arts = independent_incidence(neg_can)

    selected = pos.get("selected_explanation") or {}
    branches = selected.get("branches") or []
    independent_branch_ok = True
    independent_branch_statuses = []
    for value in (0, 1):
        ref = independent_restrict(pos_can, 1, value)
        if ref["unsat"]:
            independent_branch_statuses.append("UNSAT")
            continue
        if not ref["raw"]["constraints"]:
            independent_branch_statuses.append("TRIVIAL")
            continue
        cert = induce_compositional_basis(ref["raw"])
        independent_branch_statuses.append(cert.get("status"))
        independent_branch_ok = independent_branch_ok and cert.get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO"

    # Candidate restriction receipts must match an independently reconstructed restriction hash surface.
    branch_restriction_match = True
    for row in branches:
        value = row["value"]
        independent = independent_restrict(pos_can, 1, value)
        candidate_restriction = row["restriction"]
        if independent["unsat"] != candidate_restriction["branch_unsat"]:
            branch_restriction_match = False
        if not independent["unsat"] and independent["raw"] != candidate_restriction["residual"]:
            branch_restriction_match = False

    tampered = copy.deepcopy(pos["proposals"][0])
    tampered["separator_variables"] = [0]
    tamper_result = redteam_proposal(pos_can, tampered)

    perm_selected = (perm.get("selected_explanation") or {}).get("separator_variables")

    checks = {
        "artifact_identity": pos.get("artifact_id") == ARTIFACT_ID,
        "source_guard": bool((pos.get("source_guard") or {}).get("ok")),
        "parent_global_mixed_is_open": pos_parent_global.get("status") == "OPEN_NO_SCHAEFER_BASIS",
        "parent_connected_composition_is_open": pos_parent_composed.get("status") == "OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS",
        "independent_positive_articulation_is_exactly_1": pos_arts == [1],
        "positive_terminal_admits_explanation": pos.get("status") == "ADMIT_EXACT_STRUCTURAL_EXPLANATION",
        "positive_selected_separator_is_1": selected.get("separator_variables") == [1],
        "positive_exactly_two_branches": [x.get("value") for x in branches] == [0, 1],
        "positive_all_branch_replays_admit": len(branches) == 2 and all((x.get("replay") or {}).get("admitted") for x in branches),
        "independent_branch_replay_admits": independent_branch_ok,
        "candidate_restrictions_match_independent": branch_restriction_match,
        "receipt_content_bound": bool((pos.get("provenance_receipt") or {}).get("bicameral_receipt_sha256")),
        "no_solver_execution": (pos.get("metrics") or {}).get("solver_invocations") == 0,
        "no_generic_transfer": (pos.get("metrics") or {}).get("generic_transfer_calls") == 0,
        "no_full_variable_cube": (pos.get("metrics") or {}).get("full_variable_assignments_enumerated") == 0,
        "negative_has_no_single_variable_articulation": neg_arts == [],
        "negative_biconnected_fails_closed": neg.get("status") == "OPEN_NO_EXACT_BICAMERAL_EXPLANATION" and not neg.get("proposals"),
        "injected_hint_rejected_before_proposal": hint.get("status") == "REJECT_RAW_INPUT" and (hint.get("metrics") or {}).get("solver_invocations") == 0,
        "tampered_proposal_rejected": tamper_result.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "permutation_preserves_terminal": perm.get("status") == "ADMIT_EXACT_STRUCTURAL_EXPLANATION",
        "permutation_preserves_discovered_separator": perm_selected == [1],
        "permutation_still_zero_solver": (perm.get("metrics") or {}).get("solver_invocations") == 0,
        "scientific_firewall_p_vs_np_open": (pos.get("scientific_firewall") or {}).get("P_VS_NP") == "OPEN",
        "scientific_firewall_general_sat_not_proved": (pos.get("scientific_firewall") or {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "scientific_firewall_arbitrary_unseen_not_proved": (pos.get("scientific_firewall") or {}).get("ARBITRARY_UNSEEN_INVARIANT_DISCOVERY") == "NOT_PROVED",
    }

    verdict = VERDICT if all(checks.values()) else "FAIL_BICAMERAL_CONNECTED_CORE_EXPLANATION_GATE"
    out = {
        "verdict": verdict,
        "checks": checks,
        "controls": {
            "positive_raw_sha256": sha256_obj(pos_can),
            "positive_independent_articulations": pos_arts,
            "positive_terminal": pos.get("status"),
            "positive_separator": selected.get("separator_variables"),
            "positive_independent_branch_statuses": independent_branch_statuses,
            "negative_independent_articulations": neg_arts,
            "negative_terminal": neg.get("status"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tamper_result.get("status"),
            "permuted_terminal": perm.get("status"),
        },
        "complexity": {
            "proposal_library": "ALL_SINGLE_VARIABLE_INCIDENCE_ARTICULATIONS",
            "proposal_count_upper_bound": "V",
            "branches_per_proposal": 2,
            "claim": "POLYNOMIAL_IN_EXPLICIT_RELATION_TABLE_INPUT_FOR_THIS_FROZEN_SCOPE",
            "finite_controls_are_not_asymptotic_evidence": True,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        },
    }
    print(json.dumps(out, sort_keys=True))
    if verdict != VERDICT:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
