#!/usr/bin/env python3
"""Provider replay for the frozen heuristic-free Policy-0B.1 baseline.

Finite mechanics only: exhaustive CNFs on <=3 variables and <=3 clauses are
cross-checked against brute force.  No polynomial-total-runtime claim follows.
"""
from __future__ import annotations

from itertools import combinations, product
from typing import Iterable, Mapping

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def lit_key(lit: int):
    return (abs(lit), lit < 0)


def canonical_clause(clause: Iterable[int]) -> Clause | None:
    s = set(clause)
    if any(-lit in s for lit in s):
        return None
    return tuple(sorted(s, key=lit_key))


def canonical_cnf(clauses: Iterable[Iterable[int]]) -> CNF:
    out: set[Clause] = set()
    for clause in clauses:
        c = canonical_clause(clause)
        if c is not None:
            out.add(c)
    return tuple(sorted(out, key=lambda c: (len(c), c)))


def subsumption_reduce(cnf: CNF) -> CNF:
    frozen = canonical_cnf(cnf)
    sets = [set(c) for c in frozen]
    return canonical_cnf(
        c
        for i, c in enumerate(frozen)
        if not any(j != i and sets[j] < sets[i] for j in range(len(frozen)))
    )


def restrict_cnf(cnf: CNF, rho: Mapping[int, int]) -> CNF:
    out: list[Clause] = []
    for clause in cnf:
        residual: list[int] = []
        satisfied = False
        for lit in clause:
            var = abs(lit)
            if var in rho:
                value = rho[var] if lit > 0 else 1 - rho[var]
                if value:
                    satisfied = True
                    break
            else:
                residual.append(lit)
        if not satisfied:
            out.append(tuple(residual))
    return subsumption_reduce(canonical_cnf(out))


def fair_strengthen(cnf: CNF):
    frozen = subsumption_reduce(canonical_cnf(cnf))
    pos: dict[int, list[Clause]] = {}
    neg: dict[int, list[Clause]] = {}
    for clause in frozen:
        for lit in clause:
            (pos if lit > 0 else neg).setdefault(abs(lit), []).append(clause)

    fsets = {c: set(c) for c in frozen}
    best: dict[Clause, Clause | None] = {c: None for c in frozen}
    units: set[int] = set()
    attempts = 0

    for pivot in sorted(set(pos) & set(neg)):
        for left in pos[pivot]:
            for right in neg[pivot]:
                attempts += 1
                candidate = canonical_clause(
                    (set(left) - {pivot}) | (set(right) - {-pivot})
                )
                if candidate is None:
                    continue
                if not candidate:
                    return True, (), frozen, attempts, False
                if len(candidate) == 1:
                    units.add(candidate[0])
                    continue
                sc = set(candidate)
                for old in frozen:
                    if sc < fsets[old]:
                        previous = best[old]
                        if previous is None or (len(candidate), candidate) < (
                            len(previous),
                            previous,
                        ):
                            best[old] = candidate

    replacement: list[Clause] = []
    changed = False
    for old in frozen:
        candidate = best[old]
        if candidate is None:
            replacement.append(old)
        else:
            replacement.append(candidate)
            changed = True
    new = subsumption_reduce(canonical_cnf(replacement))
    if changed:
        assert sum(map(len, new)) < sum(map(len, frozen))

    L = sum(map(len, frozen))
    assert 4 * attempts <= L * L
    return False, tuple(sorted(units, key=lit_key)), new, attempts, changed


def preprocess(cnf: CNF, rho0: Mapping[int, int]):
    rho = dict(rho0)
    active = restrict_cnf(cnf, rho)
    scans = attempts = strengthenings = units_assigned = 0
    while True:
        if () in active:
            return True, active, rho, (scans, attempts, strengthenings, units_assigned)
        units = sorted({c[0] for c in active if len(c) == 1}, key=lit_key)
        if units:
            lit = units[0]
            var, value = abs(lit), int(lit > 0)
            if var in rho and rho[var] != value:
                return True, ((),), rho, (scans, attempts, strengthenings, units_assigned)
            if var not in rho:
                rho[var] = value
                units_assigned += 1
            active = restrict_cnf(active, rho)
            continue
        conflict, derived_units, new, local_attempts, changed = fair_strengthen(active)
        scans += 1
        attempts += local_attempts
        if conflict:
            return True, ((),), rho, (scans, attempts, strengthenings, units_assigned)
        if derived_units:
            lit = derived_units[0]
            var, value = abs(lit), int(lit > 0)
            if var in rho and rho[var] != value:
                return True, ((),), rho, (scans, attempts, strengthenings, units_assigned)
            if var not in rho:
                rho[var] = value
                units_assigned += 1
            active = restrict_cnf(active, rho)
            continue
        if changed:
            strengthenings += 1
            active = new
            continue
        return False, active, rho, (scans, attempts, strengthenings, units_assigned)


def solve(cnf: CNF):
    root = canonical_cnf(cnf)
    root_vars = sorted({abs(l) for c in root for l in c})
    stats = {"nodes": 0, "max_depth": 0, "branches": 0, "attempts": 0}

    def rec(active: CNF, rho: dict[int, int], depth: int):
        stats["nodes"] += 1
        stats["max_depth"] = max(stats["max_depth"], depth)
        conflict, residual, propagated, pstats = preprocess(active, rho)
        stats["attempts"] += pstats[1]
        if conflict:
            return False, None
        if not residual:
            witness = dict(propagated)
            for var in root_vars:
                witness.setdefault(var, 0)
            return True, witness
        remaining = sorted(
            {
                abs(l)
                for c in residual
                for l in c
                if abs(l) not in propagated
            }
        )
        assert remaining
        var = remaining[0]
        stats["branches"] += 1
        rho0 = dict(propagated)
        rho0[var] = 0
        sat, witness = rec(residual, rho0, depth + 1)
        if sat:
            return True, witness
        rho1 = dict(propagated)
        rho1[var] = 1
        return rec(residual, rho1, depth + 1)

    sat, witness = rec(root, {}, 0)
    return sat, witness, stats


def brute_sat(cnf: CNF):
    root = canonical_cnf(cnf)
    variables = sorted({abs(l) for c in root for l in c})
    for bits in product((0, 1), repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        if all(
            any(
                assignment[abs(l)] if l > 0 else 1 - assignment[abs(l)]
                for l in clause
            )
            for clause in root
        ):
            return True
    return False


def verify_witness(cnf: CNF, witness: Mapping[int, int]):
    return all(
        any(witness[abs(l)] if l > 0 else 1 - witness[abs(l)] for l in clause)
        for clause in canonical_cnf(cnf)
    )


def all_clauses(n: int):
    out: list[Clause] = []
    for pattern in product((-1, 0, 1), repeat=n):
        if all(x == 0 for x in pattern):
            continue
        clause = []
        for var, sign in enumerate(pattern, 1):
            if sign > 0:
                clause.append(var)
            elif sign < 0:
                clause.append(-var)
        c = canonical_clause(clause)
        assert c is not None
        out.append(c)
    return sorted(set(out), key=lambda c: (len(c), c))


def main():
    # Exact strengthening fixture.
    base = canonical_cnf(((1, 2), (-1, 2, 3)))
    before = sum(map(len, base))
    conflict, units, strengthened, attempts, changed = fair_strengthen(base)
    assert not conflict and not units and changed and attempts == 1
    assert strengthened == canonical_cnf(((1, 2), (2, 3)))
    assert sum(map(len, strengthened)) < before

    clauses = all_clauses(3)
    checked = 0
    for clause_count in range(4):
        for chosen in combinations(clauses, clause_count):
            cnf = canonical_cnf(chosen)
            sat, witness, stats = solve(cnf)
            assert sat == brute_sat(cnf)
            assert stats["max_depth"] <= 3
            if sat:
                assert witness is not None and verify_witness(cnf, witness)
            sat2, witness2, stats2 = solve(cnf)
            assert sat2 == sat and witness2 == witness and stats2 == stats
            checked += 1

    print("C025_POLICY0B1_TOTAL_MACHINE_PROVIDER_REPLAY = PASS")
    print("C025_POLICY0B1_DETERMINISM = PASS")
    print("C025_POLICY0B1_FAIR_STRENGTHENING_POTENTIAL = PASS")
    print(f"C025_POLICY0B1_EXHAUSTIVE_CNFS_CHECKED = {checked}")
    print("C025_POLICY0B1_AUTOMATIC_EXTENSIONS = NONE")
    print("C025_POLICY0B1_BRANCH_RULE = MIN_ROOT_ID_FALSE_FIRST")
    print("C025_POLICY0B1_TOTAL_BOUND = 2^N * N^O(1)")
    print("C025_POLICY0B1_POLYTIME = NOT_ESTABLISHED")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
