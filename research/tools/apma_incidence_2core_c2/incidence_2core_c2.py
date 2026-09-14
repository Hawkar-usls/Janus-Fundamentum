from research.tools.apma_incidence_2core.incidence_2core import (
    UNSAT,
    normalize_source,
    encoding_size,
    eval_source,
    canonical_two_core_variables,
    _simplify,
    solve_incidence_forest,
)

FROZEN_C = 2


def compile_incidence_2core_c2(source, n):
    norm = normalize_source(source)
    L = encoding_size(norm, n)
    polynomial_branch_bound = L ** FROZEN_C

    if any(len(c) == 0 for c in norm):
        return {
            "status": "CERTIFIED_UNSAT_INCIDENCE_2CORE_C2",
            "core_width": 0,
            "encoding_size": L,
            "frozen_c": FROZEN_C,
            "polynomial_branch_bound": polynomial_branch_bound,
            "enumerated_assignments": 0,
            "reason": "EMPTY_CLAUSE",
        }

    core_vars = canonical_two_core_variables(norm)
    k = len(core_vars)
    branch_count = 1 << k

    if branch_count > polynomial_branch_bound:
        return {
            "status": "OPEN_INCIDENCE_2CORE_C2_WIDTH",
            "core_width": k,
            "encoding_size": L,
            "frozen_c": FROZEN_C,
            "branch_count": branch_count,
            "polynomial_branch_bound": polynomial_branch_bound,
            "enumerated_assignments": 0,
        }

    tried = 0
    for mask in range(branch_count):
        tried += 1
        core_assignment = {v: bool((mask >> i) & 1) for i, v in enumerate(core_vars)}
        residual = _simplify(norm, core_assignment)
        if residual is UNSAT:
            continue
        solved = solve_incidence_forest(residual, n)
        if solved["status"] == "RESIDUAL_CYCLE":
            return {
                "status": "FAIL_INTERNAL_C2_RESIDUAL_CYCLE",
                "core_width": k,
                "encoding_size": L,
                "frozen_c": FROZEN_C,
                "enumerated_assignments": tried,
            }
        if solved["status"].startswith("FAIL_"):
            return {
                "status": solved["status"],
                "core_width": k,
                "encoding_size": L,
                "frozen_c": FROZEN_C,
                "enumerated_assignments": tried,
            }
        if solved["status"] == "SAT":
            witness = dict(solved["witness"])
            witness.update(core_assignment)
            witness = {i: bool(witness.get(i, False)) for i in range(1, int(n) + 1)}
            if not eval_source(source, witness):
                return {
                    "status": "FAIL_SOURCE_WITNESS_REPLAY_C2",
                    "core_width": k,
                    "encoding_size": L,
                    "frozen_c": FROZEN_C,
                    "enumerated_assignments": tried,
                }
            return {
                "status": "CERTIFIED_SAT_INCIDENCE_2CORE_C2",
                "witness": witness,
                "core_width": k,
                "encoding_size": L,
                "frozen_c": FROZEN_C,
                "branch_count": branch_count,
                "polynomial_branch_bound": polynomial_branch_bound,
                "enumerated_assignments": tried,
                "certificate": {
                    "kind": "CANONICAL_INCIDENCE_2CORE_FIXED_C2_PLUS_EXACT_FOREST_MESSAGES",
                    "core_variables": core_vars,
                    "bound": "2^k <= L^2",
                },
            }

    return {
        "status": "CERTIFIED_UNSAT_INCIDENCE_2CORE_C2",
        "core_width": k,
        "encoding_size": L,
        "frozen_c": FROZEN_C,
        "branch_count": branch_count,
        "polynomial_branch_bound": polynomial_branch_bound,
        "enumerated_assignments": tried,
        "certificate": {
            "kind": "ALL_FIXED_C2_CORE_ASSIGNMENTS_EXHAUSTED_WITH_EXACT_FOREST_MESSAGES",
            "core_variables": core_vars,
            "bound": "2^k <= L^2",
        },
    }
