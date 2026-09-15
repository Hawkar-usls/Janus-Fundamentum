from __future__ import annotations

import itertools
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_pair_separator.pair_separator_explainer import explain_with_pair_separator
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as frozen_v1
from research.tools.apma_bicameral_mincut.mincut_logwidth_v1_1 import (
    ARTIFACT_ID,
    corrected_positive,
    injected_hint_control,
    explain_v1_1,
)
from research.tools.apma_bicameral_mincut.independent_checker import (
    independent_canonical_cut,
    independent_restrict,
    independent_branch_admitted,
    canonical_bytes,
    git_blob_sha1,
)

CHECK_ARTIFACT = "JANUS-TRUMP-BICAMERAL-MINCUT-LOGWIDTH-V1-1-INDEPENDENT-CHECK-2026-09-15"
WRAPPER_REL = Path("research/tools/apma_bicameral_mincut/mincut_logwidth_v1_1.py")
WRAPPER_BLOB = "c04d6b820e70f6019dffbd86038b3fe1fe5b80c5"
PREREG_REL = Path("research/TRUMP_BICAMERAL_MINCUT_LOGWIDTH_V1_1_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "16eafc01018bfb33da7992f8559e77de5f5ab129"
FROZEN_ENGINE_REL = Path("research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py")
FROZEN_ENGINE_BLOB = "c0c612676e39241b95026c15823e7af6b3da8f0d"
FROZEN_INDEPENDENT_REL = Path("research/tools/apma_bicameral_mincut/independent_checker.py")
FROZEN_INDEPENDENT_BLOB = "54e0a7b4117d59f3ad9a6e1d25c920dce8406319"
FIRST_FAILURE_REL = Path("research/TRUMP_BICAMERAL_MINCUT_LOGWIDTH_FIRST_RUN_FAILURE_2026-09-15.json")
FIRST_FAILURE_BLOB = "adfc67a7bc425e11e49d98fd282e6999b05a33b8"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def permuted_positive() -> dict:
    raw = corrected_positive()
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
    failure = json.loads((root / FIRST_FAILURE_REL).read_text(encoding="utf-8"))
    source_checks = {
        "wrapper_blob": git_blob_sha1(root / WRAPPER_REL) == WRAPPER_BLOB,
        "prereg_blob": git_blob_sha1(root / PREREG_REL) == PREREG_BLOB,
        "prereg_frozen": prereg.get("status") == "FROZEN_BEFORE_V1_1_CANDIDATE",
        "frozen_v1_engine_blob": git_blob_sha1(root / FROZEN_ENGINE_REL) == FROZEN_ENGINE_BLOB,
        "frozen_v1_independent_blob": git_blob_sha1(root / FROZEN_INDEPENDENT_REL) == FROZEN_INDEPENDENT_BLOB,
        "first_failure_blob": git_blob_sha1(root / FIRST_FAILURE_REL) == FIRST_FAILURE_BLOB,
        "first_failure_verdict_preserved": failure.get("verdict") == "FAIL_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION",
    }

    raw = corrected_positive()
    canonical = canonicalize_raw(raw)
    global_basis = induce_compositional_basis(canonical)
    parent_pair = explain_with_pair_separator(raw)
    ind_cut = independent_canonical_cut(canonical)
    candidate = explain_v1_1(raw)
    delegated = candidate.get("delegated") or {}
    candidate_cut = delegated.get("cut") or {}
    red = delegated.get("redteam") or {}
    branches = red.get("branches") or []
    L = len(canonical_bytes(canonical))
    cut = ind_cut["cut_variables"] if ind_cut else []
    independent_restrictions = [
        independent_restrict(canonical, cut, values)
        for values in itertools.product((0,1), repeat=len(cut))
    ]
    independent_admitted = [independent_branch_admitted(r) for r in independent_restrictions]
    candidate_core_restrictions = [
        {"branch_unsat": b["restriction"]["branch_unsat"], "residual": b["restriction"]["residual"]}
        for b in branches
    ]

    neg_raw = frozen_v1.negative_overwidth_cut()
    neg_can = canonicalize_raw(neg_raw)
    neg = explain_v1_1(neg_raw)
    neg_d = neg.get("delegated") or {}
    neg_red = neg_d.get("redteam") or {}
    neg_cut = independent_canonical_cut(neg_can)
    neg_L = len(canonical_bytes(neg_can))

    hint = explain_v1_1(injected_hint_control())
    hint_d = hint.get("delegated") or {}
    perm = explain_v1_1(permuted_positive())
    perm_d = perm.get("delegated") or {}

    frozen_cut = frozen_v1.canonical_min_variable_cut(canonical)
    assert frozen_cut is not None
    proposal = frozen_v1.proposal_record(canonical, frozen_cut)
    proposal["cut_receipt_sha256"] = "0" * 64
    tampered = frozen_v1.redteam_proposal(canonical, frozen_cut, proposal)

    checks = {
        "V11_P1_source_guard": all(source_checks.values()),
        "V11_P1_v1_failure_preserved": failure.get("failure_class") == "PREREGISTERED_POSITIVE_CONTROL_OUT_OF_SCOPE__NOT_MINCUT_DISCOVERY_FAILURE",
        "V11_P2_corrected_global_basis_open": global_basis.get("status") == "OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS",
        "V11_P3_parent_pair_open": parent_pair.get("status") == "OPEN_NO_EXACT_PAIR_SEPARATOR_EXPLANATION",
        "V11_P4_independent_cut_012": ind_cut is not None and ind_cut["cut_variables"] == [0,1,2] and ind_cut["cut_size"] == 3,
        "V11_P4_candidate_cut_matches_independent": ind_cut is not None and candidate_cut.get("cut_variables") == ind_cut["cut_variables"] and candidate_cut.get("cut_size") == ind_cut["cut_size"] and candidate_cut.get("maxflow_value") == ind_cut["maxflow_value"],
        "V11_P5_logwidth_budget": ind_cut is not None and (1 << ind_cut["cut_size"]) == 8 and 8 <= L,
        "V11_P6_positive_terminal": candidate.get("status") == "ADMIT_EXACT_LOGWIDTH_MINCUT_EXPLANATION",
        "V11_P6_exactly_8_branches": len(branches) == 8,
        "V11_P7_restrictions_match_independent": candidate_core_restrictions == independent_restrictions,
        "V11_P8_all_independent_branches_admit": all(independent_admitted),
        "V11_P8_all_candidate_branches_admit": len(branches) == 8 and all(b["replay"]["admitted"] for b in branches),
        "V11_P9_overwidth_independent_k20": neg_cut is not None and neg_cut["cut_size"] == 20 and neg_cut["cut_variables"] == list(range(20)),
        "V11_P9_overwidth_budget_fails": neg_cut is not None and (1 << neg_cut["cut_size"]) > neg_L,
        "V11_P9_overwidth_terminal_open": neg.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "V11_P9_overwidth_zero_branches": neg_red.get("branches") == [] and neg_red.get("resource_receipt", {}).get("branch_enumerations") == 0,
        "V11_P10_hint_rejected": hint.get("status") == "REJECT_RAW_INPUT" and hint_d.get("status") == "REJECT_RAW_INPUT",
        "V11_P10_tamper_rejected": tampered.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "V11_P12_no_solver": delegated.get("metrics", {}).get("solver_invocations") == 0 and neg_d.get("metrics", {}).get("solver_invocations") == 0,
        "V11_P12_no_generic_transfer": delegated.get("metrics", {}).get("generic_transfer_calls") == 0 and neg_d.get("metrics", {}).get("generic_transfer_calls") == 0,
        "V11_P12_no_full_cube": delegated.get("metrics", {}).get("full_variable_assignments_enumerated") == 0 and neg_d.get("metrics", {}).get("full_variable_assignments_enumerated") == 0,
        "V11_P12_no_cartesian": delegated.get("metrics", {}).get("cartesian_products_materialized") == 0 and neg_d.get("metrics", {}).get("cartesian_products_materialized") == 0,
        "V11_P13_permutation_terminal": perm.get("status") == "ADMIT_EXACT_LOGWIDTH_MINCUT_EXPLANATION",
        "V11_P13_permutation_cut": perm_d.get("cut", {}).get("cut_variables") == [0,1,2],
        "V11_firewall_p_vs_np_open": candidate["scientific_firewall"]["P_VS_NP"] == "OPEN",
        "V11_firewall_general_sat_not_proved": candidate["scientific_firewall"]["GENERAL_SAT_IN_P"] == "NOT_PROVED",
        "V11_firewall_connected_mixed_not_solved": candidate["scientific_firewall"]["CONNECTED_MIXED_CORE_SOLVED"] == "NO",
        "V11_firewall_arbitrary_unseen_not_proved": candidate["scientific_firewall"]["ARBITRARY_UNSEEN_INVARIANT_DISCOVERY"] == "NOT_PROVED",
    }

    verdict = "PASS_SCOPED_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_INDUCTION_V1_1" if all(checks.values()) else "FAIL_BICAMERAL_CANONICAL_MINCUT_LOGWIDTH_EXPLANATION_V1_1"
    out = {
        "artifact_id": CHECK_ARTIFACT,
        "authority": "INDEPENDENT_CHECKER__V1_1_SCOPED_ONLY",
        "candidate_artifact_id": ARTIFACT_ID,
        "checks": checks,
        "source_checks": source_checks,
        "controls": {
            "v1_0_failure_preserved": failure.get("verdict"),
            "positive_global_basis": global_basis.get("status"),
            "positive_parent_pair": parent_pair.get("status"),
            "positive_independent_cut": ind_cut,
            "positive_candidate_cut": candidate_cut,
            "positive_L": L,
            "positive_branch_budget": 8,
            "positive_terminal": candidate.get("status"),
            "positive_branch_count": len(branches),
            "negative_independent_cut": neg_cut,
            "negative_L": neg_L,
            "negative_branch_budget": (1 << neg_cut["cut_size"]) if neg_cut else None,
            "negative_terminal": neg.get("status"),
            "negative_branch_enumerations": neg_red.get("resource_receipt", {}).get("branch_enumerations"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tampered.get("status"),
            "permuted_terminal": perm.get("status"),
        },
        "complexity": {
            "cut_discovery": "O(C^2) polynomial max-flow calls; frozen candidate uses Edmonds-Karp and frozen independent primitive uses Dinic",
            "branch_budget": "2^k <= L checked before enumeration; at most L exact branches",
            "subset_enumeration_for_discovery": False,
            "claim": "POLYNOMIAL_IN_CANONICAL_EXPLICIT_INPUT_LENGTH_FOR_FROZEN_MINCUT_LOGWIDTH_SCOPE",
            "finite_controls_are_not_asymptotic_evidence": True,
        },
        "scientific_firewall": candidate["scientific_firewall"],
        "verdict": verdict,
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
