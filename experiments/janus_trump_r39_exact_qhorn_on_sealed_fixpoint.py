from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

Literal = int
Clause = Tuple[int, ...]
Formula = Tuple[Clause, ...]

EXPECTED_FIXPOINT_HASH = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"
EXPECTED_FIXPOINT_CLV = [45, 105, 13]

# Exact clause sequence sealed by R38 artifact 9859591106 / result hash
# 41ed8e7ed1e3f0220e16eb3d12f683105c78b9a1787798a4b3e9ffd62ef8dee7.
FROZEN_FORMULA: Formula = (
    (-22, 24),
    (-21, -23, -24),
    (-21, -22, -23),
    (-15, -28),
    (-15, -21, -23),
    (-15, 22),
    (-15, 24),
    (-14, -18),
    (-12, 15),
    (-12, 18, 21),
    (-12, 24),
    (-8, -28),
    (-6, 8),
    (-6, 15),
    (-3, 6, -15),
    (-3, 6, -8),
    (-2, -21, 22),
    (-2, -21, 24),
    (-2, -12, -14),
    (-2, -6),
    (2, 3),
    (2, 6, -15),
    (2, 14, 23),
    (3, -28),
    (3, -23),
    (3, 18),
    (6, -15, 21),
    (6, -14, -15),
    (6, 18, 28),
    (8, -24),
    (8, -15),
    (8, 23),
    (12, -22),
    (12, -18),
    (12, -15),
    (12, 23),
    (14, -28),
    (14, 18),
    (14, 22),
    (15, -22),
    (18, -22, -23),
    (22, -24),
    (22, 28),
    (23, 24),
    (24, 28),
)

# beta2 is exactly 2*beta, so allowed values are {0,1,2}; this avoids floats.
BETA2_VALUES = (0, 1, 2)


def canonical_json_sha256(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def formula_hash(formula: Formula) -> str:
    return canonical_json_sha256([list(c) for c in formula])


def variables(formula: Formula) -> List[int]:
    return sorted({abs(lit) for clause in formula for lit in clause})


def literal_beta2(lit: Literal, assignment: Dict[int, int]) -> int:
    value = assignment[abs(lit)]
    return value if lit > 0 else 2 - value


def clause_beta2_sum(clause: Clause, assignment: Dict[int, int]) -> int:
    return sum(literal_beta2(lit, assignment) for lit in clause)


def qhorn_valuation_recheck(formula: Formula, assignment: Dict[int, int]) -> bool:
    vs = variables(formula)
    return set(assignment) == set(vs) and all(
        assignment[v] in BETA2_VALUES for v in vs
    ) and all(clause_beta2_sum(clause, assignment) <= 2 for clause in formula)


def exact_qhorn_search(formula: Formula) -> dict:
    """Exact finite q-Horn membership search.

    The search is a deterministic ternary CSP search. It is exact but is NOT
    claimed to be the general polynomial/linear q-Horn recognizer from the
    literature. Partial pruning is sound because every unassigned literal can
    contribute as little as zero to its clause.
    """
    vs = variables(formula)
    occurrence = Counter(abs(lit) for clause in formula for lit in clause)
    order = sorted(vs, key=lambda v: (-occurrence[v], v))
    by_var: Dict[int, List[int]] = defaultdict(list)
    for clause_index, clause in enumerate(formula):
        for lit in clause:
            by_var[abs(lit)].append(clause_index)

    assignment: Dict[int, int] = {}
    nodes = 0

    def partial_clause_ok(clause: Clause) -> bool:
        total = 0
        for lit in clause:
            v = abs(lit)
            if v not in assignment:
                continue
            total += assignment[v] if lit > 0 else 2 - assignment[v]
            if total > 2:
                return False
        return True

    def dfs(depth: int) -> Optional[Dict[int, int]]:
        nonlocal nodes
        nodes += 1
        if depth == len(order):
            witness = dict(assignment)
            return witness if qhorn_valuation_recheck(formula, witness) else None

        v = order[depth]
        for beta2 in BETA2_VALUES:
            assignment[v] = beta2
            if all(partial_clause_ok(formula[i]) for i in by_var[v]):
                found = dfs(depth + 1)
                if found is not None:
                    return found
        assignment.pop(v, None)
        return None

    witness = dfs(0)
    return {
        "recognized": witness is not None,
        "search_nodes": nodes,
        "variable_order": order,
        "valuation_beta2": {str(v): witness[v] for v in sorted(witness)} if witness else None,
        "valuation_recheck": qhorn_valuation_recheck(formula, witness) if witness else None,
        "method": "EXACT_TERNARY_CSP_BACKTRACKING_WITH_SOUND_PARTIAL_SUM_PRUNING",
        "general_polynomial_recognizer_claimed": False,
    }


def deletion_minimal_qhorn_unsat_core(formula: Formula) -> dict:
    """Derive a deterministic deletion-minimal core for q-Horn infeasibility."""
    core = list(range(len(formula)))
    deletion_checks = []
    for idx in list(core):
        trial_indices = [i for i in core if i != idx]
        trial_formula = tuple(formula[i] for i in trial_indices)
        trial = exact_qhorn_search(trial_formula)
        remains_unsat = not trial["recognized"]
        deletion_checks.append(
            {
                "candidate_removed_clause_index": idx,
                "remains_qhorn_infeasible": remains_unsat,
                "search_nodes": trial["search_nodes"],
            }
        )
        if remains_unsat:
            core.remove(idx)

    core_formula = tuple(formula[i] for i in core)
    minimality_witnesses = []
    for idx in core:
        trial_indices = [i for i in core if i != idx]
        trial = exact_qhorn_search(tuple(formula[i] for i in trial_indices))
        if not trial["recognized"]:
            raise AssertionError(("core not deletion-minimal", idx, core))
        minimality_witnesses.append(
            {
                "removed_clause_index": idx,
                "remaining_core_is_qhorn": True,
                "valuation_beta2": trial["valuation_beta2"],
            }
        )

    return {
        "clause_indices_zero_based": core,
        "clauses": [list(formula[i]) for i in core],
        "variables": variables(core_formula),
        "deletion_checks": deletion_checks,
        "deletion_minimal": True,
        "minimality_witnesses": minimality_witnesses,
    }


def independent_core_exhaustive_replay(core_clauses: Sequence[Sequence[int]]) -> dict:
    """Independent direct replay over all 3^k valuations of core variables."""
    core: Formula = tuple(tuple(int(lit) for lit in clause) for clause in core_clauses)
    vs = variables(core)
    total = 0
    accepted = 0
    rejection_histogram = Counter()

    for values in itertools.product(BETA2_VALUES, repeat=len(vs)):
        total += 1
        assignment = dict(zip(vs, values))
        first_bad = None
        for ci, clause in enumerate(core):
            if clause_beta2_sum(clause, assignment) > 2:
                first_bad = ci
                break
        if first_bad is None:
            accepted += 1
        else:
            rejection_histogram[first_bad] += 1

    return {
        "pass": accepted == 0,
        "variables": vs,
        "valuation_space_size": total,
        "expected_valuation_space_size": 3 ** len(vs),
        "accepted_valuations": accepted,
        "first_rejecting_core_clause_histogram": {
            str(k): v for k, v in sorted(rejection_histogram.items())
        },
        "method": "INDEPENDENT_CARTESIAN_ENUMERATION_DIRECT_CLAUSE_WEIGHT_RECHECK",
    }


def run_r39() -> dict:
    formula = FROZEN_FORMULA
    h = formula_hash(formula)
    if h != EXPECTED_FIXPOINT_HASH:
        raise AssertionError(("frozen formula hash drift", h))
    if len(formula) != EXPECTED_FIXPOINT_CLV[0]:
        raise AssertionError(("clause count drift", len(formula)))

    recognition = exact_qhorn_search(formula)

    if recognition["recognized"]:
        result = {
            "recognized": True,
            "certificate": {
                "valuation_beta2": recognition["valuation_beta2"],
                "valuation_recheck": recognition["valuation_recheck"],
            },
            "rejection_core": None,
            "independent_replay": {
                "pass": bool(recognition["valuation_recheck"]),
                "method": "DIRECT_FULL_FORMULA_QHORN_VALUATION_RECHECK",
            },
        }
        verdict = "R39_QHORN_RECOGNIZED_LOCAL_EXACT__TERMINAL_INTEGRATION_REQUIRED_SEPARATELY"
        next_gate = "R39B_PREREGISTER_STANDARD_QHORN_TERMINAL_INTEGRATION"
    else:
        core = deletion_minimal_qhorn_unsat_core(formula)
        replay = independent_core_exhaustive_replay(core["clauses"])
        if not replay["pass"]:
            raise AssertionError(("independent q-Horn rejection replay failed", replay))
        result = {
            "recognized": False,
            "certificate": None,
            "rejection_core": core,
            "independent_replay": replay,
        }
        verdict = "R39_QHORN_REJECTED_LOCAL_EXACT__RETURN_TO_UNIVERSAL_COVERAGE"
        next_gate = "R40_UNIVERSAL_FIXPOINT_COVERAGE_AND_REMAINDER_OBLIGATION"

    return {
        "schema": "JANUS_TRUMP_R39_EXACT_QHORN_RECOGNITION_RESULT",
        "version": "1.0",
        "date": "2026-09-02",
        "source_git_commit": os.environ.get("GITHUB_SHA", "LOCAL"),
        "verdict": verdict,
        "parent": {
            "R38_sealed_commit": "0b941a484143aa130bad9f7bdf9ca94fbbff79cb",
            "R38_run_id": 33663428197,
            "R38_artifact_id": 9859591106,
            "R38_result_json_sha256": "41ed8e7ed1e3f0220e16eb3d12f683105c78b9a1787798a4b3e9ffd62ef8dee7",
        },
        "frozen_fixpoint": {
            "measure_CLV": EXPECTED_FIXPOINT_CLV,
            "canonical_formula_sha256": h,
            "clause_count": len(formula),
            "variable_count": len(variables(formula)),
        },
        "q_horn_definition": {
            "exact_integer_form": "beta2(l) in {0,1,2}; beta2(not x)=2-beta2(x); FOR_EACH C: SUM beta2(l) <= 2",
            "equivalent_fractional_form": "beta(l) in {0,1/2,1}; beta(not x)=1-beta(x); FOR_EACH C: SUM beta(l) <= 1",
        },
        "primary_recognizer": recognition,
        "q_horn_membership": result,
        "complexity_firewall": {
            "this_R39_membership_decision_is_exact": True,
            "this_R39_recognizer_claimed_polynomial": False,
            "literature_has_general_linear_time_qhorn_recognition": True,
            "literature_algorithm_implemented_here": False,
            "external_SAT_solver_used": False,
            "boolean_truth_assignment_enumeration_used": False,
            "qhorn_certificate_valuation_search_used": True,
            "local_qhorn_rejection_may_be_promoted_to_global_terminal_claim": False,
        },
        "captain_verdict": {
            "law": "A WITNESS PROVES A CASE. COVERAGE PROVES THE DOMAIN. A UNIFORM POLYNOMIAL RESOLVER PROVES THE ALGORITHM.",
            "terminal_class_shopping_after_local_rejection_allowed_without_coverage_value": False,
            "next_gate": next_gate,
        },
        "proof_ladder": {
            "highest_verified_level": "L1_LOCAL_FINITE_INSTANCE_EXACTNESS_ONLY",
            "L2_UNIVERSAL_3CNF_COVERAGE": False,
            "L3_ONE_UNIFORM_TOTAL_TRUMP_RESOLVER": False,
            "L4_WORST_CASE_POLYNOMIAL_UNIFORM_TRUMP_RESOLVER": False,
        },
        "R31_obligation_impact": {"obligations_closed": 0},
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "runtime_authority": False,
    }


def self_test() -> None:
    assert formula_hash(FROZEN_FORMULA) == EXPECTED_FIXPOINT_HASH
    d = run_r39()
    assert d["frozen_fixpoint"]["measure_CLV"] == EXPECTED_FIXPOINT_CLV
    assert d["proof_ladder"]["highest_verified_level"] == "L1_LOCAL_FINITE_INSTANCE_EXACTNESS_ONLY"
    assert d["proof_ladder"]["L2_UNIVERSAL_3CNF_COVERAGE"] is False
    assert d["TRUMP_finished"] is False
    assert d["SAT_IN_P"] == "NOT_PROVED"
    assert d["P_VS_NP"] == "OPEN"
    q = d["q_horn_membership"]
    assert q["independent_replay"]["pass"] is True
    if q["recognized"]:
        assert q["certificate"]["valuation_recheck"] is True
    else:
        core = q["rejection_core"]
        assert core["deletion_minimal"] is True
        assert q["independent_replay"]["valuation_space_size"] == 3 ** len(core["variables"])
        assert q["independent_replay"]["accepted_valuations"] == 0
    print("R39_SELF_TEST_PASS", d["verdict"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    text = json.dumps(run_r39(), indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
