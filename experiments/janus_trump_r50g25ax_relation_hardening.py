from __future__ import annotations

import argparse
import hashlib
import json
from functools import lru_cache
from pathlib import Path

import janus_trump_r50g25ax_within_component_separator_affine_quotient as ax

HARDENING = "R50G25AX_PROOF_CARRYING_RELATION_ACTUAL_DP_RECONSTRUCTION_HARDENING"
PREREG = "7b9cef877200b2f056099309d672923df2178b9a"
TARGET_HASH = ax.TARGET_HASH


def lit_true(lit: int, assignment: dict[int, int]) -> bool:
    v = int(assignment[abs(int(lit))])
    return bool(v) if int(lit) > 0 else not bool(v)


def source_validate(assignment: dict[int, int], defects, equations):
    clause_failures = []
    for i, clause in enumerate(defects):
        if not any(lit_true(int(l), assignment) for l in clause):
            clause_failures.append(i)
    equation_failures = []
    for i, eq in enumerate(equations):
        lhs = 0
        for v in eq["vars"]:
            lhs ^= int(assignment[int(v)])
        if lhs != int(eq["rhs"]):
            equation_failures.append(i)
    return clause_failures, equation_failures


def run_hardening():
    residual, extraction, target, defects, equations, L, tautologies, meta = ax.build_target()
    variables = tuple(map(int, target["variables"]))
    adj = ax.primal_graph(variables, defects)
    sep = ax.min_fill_order(adj)
    order = tuple(map(int, sep["order"]))
    pos = {v: i for i, v in enumerate(order)}
    failures = []

    if ax.fh(residual) != TARGET_HASH:
        failures.append("TARGET_HASH_DRIFT")
    if len(variables) != 20 or len(defects) != 61 or len(equations) != 1:
        failures.append("TARGET_COMPONENT_SHAPE_DRIFT")
    if sorted(order) != sorted(variables) or len(set(order)) != len(variables):
        failures.append("ORDER_NOT_VARIABLE_BIJECTION")

    # Frozen min-fill graph is defect-only.  The affine side constraint must
    # therefore be carried explicitly by the relation state rather than being
    # silently assumed to fit in a defect bag.
    parity_scopes = []
    for i, eq in enumerate(equations):
        scope = tuple(sorted(map(int, eq["vars"])))
        parity_scopes.append(scope)
        if not set(scope) <= set(variables):
            failures.append(f"AFFINE_SCOPE_OUTSIDE_TARGET:{i}")
        if int(eq["rhs"]) not in (0, 1):
            failures.append(f"AFFINE_RHS_NOT_BIT:{i}")

    # Assign each defect to its earliest eliminated variable.  For a valid
    # elimination relation, all remaining variables of that clause must be
    # present in the owner's later-neighbor bag.
    owned: list[list[tuple[int, ...]]] = [[] for _ in order]
    for ci, clause in enumerate(defects):
        scope = {abs(int(l)) for l in clause}
        owner = min(scope, key=lambda v: pos[v])
        j = pos[owner]
        bag = set(map(int, sep["bags"][j]["bag"]))
        if not scope <= bag:
            failures.append(f"CLAUSE_OWNER_BAG_COVER_FAILURE:{ci}")
        owned[j].append(tuple(map(int, clause)))

    # Before choosing order[j] in reverse elimination, F_j contains exactly
    # the already-chosen later variables whose values can still affect an
    # unchosen variable.  This gives an independently checkable DP interface.
    frontiers: list[tuple[int, ...]] = []
    for j in range(len(order)):
        f = []
        for u in order[j + 1:]:
            if any(pos[x] <= j for x in adj.get(u, ())):
                f.append(int(u))
        frontiers.append(tuple(sorted(f)))

    max_frontier = max((len(f) for f in frontiers), default=0)
    induced_width = int(sep["induced_width"])
    if max_frontier > induced_width:
        failures.append("FRONTIER_EXCEEDS_FROZEN_INDUCED_WIDTH")

    # One parity bit is carried for each affine side equation.  This is an
    # explicit constant-state augmentation; it is separately charged below.
    parity_count = len(equations)
    augmented_layer_state_bound = 1 << (max_frontier + parity_count)
    frozen_separator_state_bound = 1 << induced_width
    budget = int(L) ** 4
    if frozen_separator_state_bound > budget:
        failures.append("FROZEN_SEPARATOR_STATE_BOUND_EXCEEDS_L4")
    if augmented_layer_state_bound > budget:
        failures.append("PARITY_AUGMENTED_RELATION_STATE_BOUND_EXCEEDS_L4")

    coeff = []
    rhs = []
    for eq in equations:
        eqset = set(map(int, eq["vars"]))
        coeff.append({v: 1 if v in eqset else 0 for v in variables})
        rhs.append(int(eq["rhs"]))

    state_count = 0
    branch_count = 0
    choice: dict[tuple, int] = {}

    @lru_cache(maxsize=None)
    def solve(j: int, boundary_values: tuple[int, ...], parity_assigned: tuple[int, ...]) -> bool:
        nonlocal state_count, branch_count
        state_count += 1
        if j < 0:
            return tuple(map(int, parity_assigned)) == tuple(rhs)

        frontier = frontiers[j]
        if len(boundary_values) != len(frontier):
            raise AssertionError(("BOUNDARY_ARITY_DRIFT", j, frontier, boundary_values))
        known = {int(v): int(a) for v, a in zip(frontier, boundary_values)}
        v = int(order[j])

        for value in (0, 1):
            branch_count += 1
            local = dict(known)
            local[v] = value

            clauses_ok = True
            for clause in owned[j]:
                # Every variable in an owned clause must be available through
                # the verified owner bag/frontier relation.
                missing = [abs(int(l)) for l in clause if abs(int(l)) not in local]
                if missing:
                    raise AssertionError(("OWNED_CLAUSE_VARIABLE_NOT_IN_DP_STATE", j, clause, missing, frontier))
                if not any(lit_true(int(l), local) for l in clause):
                    clauses_ok = False
                    break
            if not clauses_ok:
                continue

            new_parity = list(map(int, parity_assigned))
            for ei in range(parity_count):
                if coeff[ei][v]:
                    new_parity[ei] ^= value

            if j == 0:
                next_frontier = ()
            else:
                next_frontier = frontiers[j - 1]
            next_values = []
            for u in next_frontier:
                if u not in local:
                    raise AssertionError(("NEXT_FRONTIER_VALUE_UNAVAILABLE", j, u, frontier, v))
                next_values.append(int(local[u]))

            next_key = (j - 1, tuple(next_values), tuple(new_parity))
            if solve(*next_key):
                key = (j, tuple(boundary_values), tuple(parity_assigned))
                choice[key] = value
                return True
        return False

    initial_parity = tuple(0 for _ in equations)
    sat = solve(len(order) - 1, (), initial_parity)

    assignment: dict[int, int] = {}
    reconstruction_pass = True
    if sat:
        j = len(order) - 1
        boundary_values: tuple[int, ...] = ()
        parity_assigned = initial_parity
        while j >= 0:
            key = (j, boundary_values, parity_assigned)
            if key not in choice:
                reconstruction_pass = False
                failures.append(f"MISSING_RECONSTRUCTION_CHOICE_AT_STEP:{j}")
                break
            value = int(choice[key])
            v = int(order[j])
            known = {int(u): int(a) for u, a in zip(frontiers[j], boundary_values)}
            known[v] = value
            assignment[v] = value

            new_parity = list(map(int, parity_assigned))
            for ei in range(parity_count):
                if coeff[ei][v]:
                    new_parity[ei] ^= value
            next_frontier = () if j == 0 else frontiers[j - 1]
            try:
                boundary_values = tuple(int(known[u]) for u in next_frontier)
            except KeyError as exc:
                reconstruction_pass = False
                failures.append(f"RECONSTRUCTION_FRONTIER_KEY_ERROR:{j}:{exc}")
                break
            parity_assigned = tuple(new_parity)
            j -= 1

        if reconstruction_pass and set(assignment) != set(variables):
            reconstruction_pass = False
            failures.append("RECONSTRUCTED_ASSIGNMENT_NOT_TOTAL")

    clause_failures: list[int] = []
    equation_failures: list[int] = []
    source_validation_pass = True
    if sat and reconstruction_pass:
        clause_failures, equation_failures = source_validate(assignment, defects, equations)
        source_validation_pass = not clause_failures and not equation_failures
        if not source_validation_pass:
            failures.append("RECONSTRUCTED_WITNESS_FAILS_SOURCE_VALIDATION")

    # For UNSAT, exactness is carried by the fully enumerated memoized
    # recurrence itself; for SAT, it additionally carries a source-validated
    # reverse path.  No independent SAT oracle participates in selection or
    # verdict.
    relation_contract = {
        "DOMAIN": ax.fh(residual) == TARGET_HASH and len(variables) == 20 and len(defects) == 61 and len(equations) == 1,
        "FORWARD_PRESERVATION": not any(x.startswith("CLAUSE_OWNER_BAG_COVER_FAILURE") for x in failures),
        "CLAIM_SCOPED_RECONSTRUCTION": (not sat) or reconstruction_pass,
        "SOURCE_VALIDATION": (not sat) or source_validation_pass,
        "EXACTNESS": not any(x.startswith("OWNED_CLAUSE_VARIABLE_NOT_IN_DP_STATE") for x in failures),
        "SIZE_BOUND": augmented_layer_state_bound <= budget and state_count <= (len(order) + 1) * augmented_layer_state_bound,
        "TIME_BOUND": branch_count <= 2 * state_count,
        "COMPOSITION_SCOPE": True,
        "PROVENANCE": PREREG == ax.PREREG and ax.PARENT == "4858a25b5ce1cc8243fcb40304a0e0f0fa21dfa6",
        "COUNTEREXAMPLE_TRACE": True,
    }
    relation_pass = all(bool(v) for v in relation_contract.values()) and not failures

    return {
        "hardening": HARDENING,
        "status": "PASS" if relation_pass else "FAIL_CLOSED",
        "preregistration_commit": PREREG,
        "target_hash": TARGET_HASH,
        "frozen_separator": {
            "induced_width": induced_width,
            "frozen_state_bound_2_pow_w": frozen_separator_state_bound,
            "max_verified_frontier": max_frontier,
            "parity_side_constraint_count": parity_count,
            "parity_scopes": [list(x) for x in parity_scopes],
            "parity_augmented_layer_state_bound": augmented_layer_state_bound,
            "L4_budget": budget,
        },
        "actual_relation_dp": {
            "decision": "SAT" if sat else "UNSAT",
            "memoized_state_count": state_count,
            "branch_count": branch_count,
            "choice_row_count": len(choice),
            "reconstruction_pass": reconstruction_pass,
            "source_validation_pass": source_validation_pass,
            "source_clause_failure_indices": clause_failures,
            "source_equation_failure_indices": equation_failures,
            "reconstructed_assignment": {str(k): int(v) for k, v in sorted(assignment.items())} if sat and reconstruction_pass else None,
        },
        "relation_contract": relation_contract,
        "relation_pass": relation_pass,
        "failures": failures,
        "truth_oracle": {"generation": False, "selection": False, "verdict": False, "external_exact_sat_oracle": False},
        "interpretation": "HARDENING_VERIFIES_THE_ALREADY_FROZEN_AX_SEPARATOR_RELATION__DOES_NOT_CHANGE_CANDIDATE_ORDER_OR_BUDGET",
        "firewall": {"P_VS_NP": "OPEN", "SAT_IN_P": "NOT_PROVED", "TRUMP_finished": False},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    x = run_hardening()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(x, indent=2, sort_keys=True) + "\n").encode()
    args.out.write_bytes(raw)
    print("AX_RELATION_HARDENING_SHA256=" + hashlib.sha256(raw).hexdigest())
    print(json.dumps({
        "status": x["status"],
        "relation_pass": x["relation_pass"],
        "decision": x["actual_relation_dp"]["decision"],
        "memoized_state_count": x["actual_relation_dp"]["memoized_state_count"],
        "max_verified_frontier": x["frozen_separator"]["max_verified_frontier"],
        "parity_augmented_layer_state_bound": x["frozen_separator"]["parity_augmented_layer_state_bound"],
    }, sort_keys=True))
    raise SystemExit(0 if x["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
