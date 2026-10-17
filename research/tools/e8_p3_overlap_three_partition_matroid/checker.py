#!/usr/bin/env python3
"""Exact regression for the P3-overlap three-partition-matroid carrier.

The universal equivalence is proved symbolically in the companion JSON theorem.
This checker independently verifies:
  * the local mixed-degree-3 relation and its unique symmetric-exchange defect;
  * all three one-state local repairs become delta-matroids;
  * exhaustive SAT <-> common-independent witness equivalence for every
    2/3-CNF on three variables with at most three clauses and occurrence<=3;
  * one frozen bounded-occurrence UNSAT control and one SAT control.
"""

from itertools import combinations, combinations_with_replacement, product


def powerset(items):
    items = tuple(items)
    out = []
    for mask in range(1 << len(items)):
        out.append(frozenset(items[i] for i in range(len(items)) if mask >> i & 1))
    return out


def delta_failures(feasible):
    feasible = set(feasible)
    failures = []
    for X in feasible:
        for Y in feasible:
            D = X ^ Y
            for u in D:
                ok = False
                for v in D:
                    toggle = {u} if u == v else {u, v}
                    if frozenset(X ^ toggle) in feasible:
                        ok = True
                        break
                if not ok:
                    failures.append((X, Y, u))
    return failures


def local_delta_checks():
    E = ("L", "M", "R")
    feasible = {
        frozenset(),
        frozenset({"L"}),
        frozenset({"M"}),
        frozenset({"R"}),
        frozenset({"L", "R"}),
    }
    missing = [S for S in powerset(E) if S not in feasible]
    assert set(missing) == {
        frozenset({"L", "M"}),
        frozenset({"M", "R"}),
        frozenset({"L", "M", "R"}),
    }

    failures = delta_failures(feasible)
    assert len(failures) == 1
    X, Y, u = failures[0]
    assert X == frozenset({"L", "R"})
    assert Y == frozenset({"M"})
    assert u == "M"

    for repair in missing:
        assert not delta_failures(feasible | {repair})

    return len(failures), len(missing)


def clause_catalog():
    clauses = []
    vars_ = (1, 2, 3)
    for k in (2, 3):
        for support in combinations(vars_, k):
            for signs in product((1, -1), repeat=k):
                clauses.append(tuple(s * v for s, v in zip(signs, support)))
    assert len(clauses) == 20
    return clauses


def occurrence_count_ok_general(formula):
    counts = {}
    for C in formula:
        for lit in C:
            counts[abs(lit)] = counts.get(abs(lit), 0) + 1
    return all(v <= 3 for v in counts.values())


def occurrence_count_ok(formula):
    return occurrence_count_ok_general(formula)


def sat_bruteforce_general(formula):
    n = max((abs(lit) for C in formula for lit in C), default=0)
    for bits in product((False, True), repeat=n):
        ok = True
        for C in formula:
            clause_ok = False
            for lit in C:
                val = bits[abs(lit) - 1]
                clause_ok |= val if lit > 0 else (not val)
            if not clause_ok:
                ok = False
                break
        if ok:
            return True
    return False


def sat_bruteforce(formula):
    return sat_bruteforce_general(formula)


def conflict_pairs(formula):
    """Return the nontrivial capacity-1 blocks for M_L and M_R.

    Occurrence ids are (clause_index, position_index).
    """
    occ = {}
    for ci, C in enumerate(formula):
        for pi, lit in enumerate(C):
            occ.setdefault(abs(lit), []).append(((ci, pi), 1 if lit > 0 else -1))

    left_blocks = []
    right_blocks = []

    for entries in occ.values():
        if len(entries) <= 1:
            continue
        signs = [s for _, s in entries]
        if len(entries) == 2:
            if signs[0] != signs[1]:
                left_blocks.append(frozenset((entries[0][0], entries[1][0])))
            continue

        assert len(entries) == 3
        plus = [oid for oid, s in entries if s == 1]
        minus = [oid for oid, s in entries if s == -1]
        if not plus or not minus:
            continue

        majority = plus if len(plus) == 2 else minus
        minority = minus[0] if len(minus) == 1 else plus[0]
        L, R = majority
        M = minority
        left_blocks.append(frozenset((L, M)))
        right_blocks.append(frozenset((R, M)))

    return left_blocks, right_blocks


def common_independent_witness_exists(formula):
    left_blocks, right_blocks = conflict_pairs(formula)

    # M_C independence + cardinality=#clauses means exactly one occurrence
    # is chosen from each clause, so enumerate only that product.
    choices = [tuple((ci, pi) for pi in range(len(C))) for ci, C in enumerate(formula)]
    for picked_tuple in product(*choices):
        picked = set(picked_tuple)
        if any(block <= picked for block in left_blocks):
            continue
        if any(block <= picked for block in right_blocks):
            continue
        return True
    return False


def common_independent_witness_exists_general(formula):
    return common_independent_witness_exists(formula)


def overlap_shape_ok(formula):
    left_blocks, right_blocks = conflict_pairs(formula)
    edges = [tuple(block) for block in left_blocks + right_blocks]

    deg = {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    assert max(deg.values(), default=0) <= 2

    adj = {}
    for a, b in edges:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen = set()
    for root in adj:
        if root in seen:
            continue
        stack = [root]
        comp = set()
        edge_twice = 0
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            comp.add(u)
            edge_twice += len(adj[u])
            stack.extend(adj[u] - seen)
        assert len(comp) in (2, 3)
        assert edge_twice // 2 in (1, 2)
        if len(comp) == 3:
            assert sorted(len(adj[u]) for u in comp) == [1, 1, 2]
    return True


def overlap_shape_ok_general(formula):
    return overlap_shape_ok(formula)


def exhaustive_small_regression():
    clauses = clause_catalog()
    tested = 0
    sat_count = 0
    unsat_count = 0

    for m in (1, 2, 3):
        for idxs in combinations_with_replacement(range(len(clauses)), m):
            formula = tuple(clauses[i] for i in idxs)
            if not occurrence_count_ok(formula):
                continue
            overlap_shape_ok(formula)
            sat = sat_bruteforce(formula)
            carrier = common_independent_witness_exists(formula)
            assert sat == carrier, (formula, sat, carrier)
            tested += 1
            sat_count += int(sat)
            unsat_count += int(not sat)

    assert tested > 0
    assert sat_count > 0
    return tested, sat_count, unsat_count


def frozen_controls():
    # Exact UNSAT control already used by the v1.9 syndrome barrier.
    unsat_formula = (
        (1, 2),
        (1, -2),
        (-1, 3),
        (-3, 4),
        (-3, -4),
    )
    assert occurrence_count_ok_general(unsat_formula)
    assert not sat_bruteforce_general(unsat_formula)
    assert not common_independent_witness_exists_general(unsat_formula)
    overlap_shape_ok_general(unsat_formula)

    sat_formula = (
        (1, 2),
        (-1, 3),
        (-2, 4),
        (-3, -4),
    )
    assert occurrence_count_ok_general(sat_formula)
    assert sat_bruteforce_general(sat_formula)
    assert common_independent_witness_exists_general(sat_formula)
    overlap_shape_ok_general(sat_formula)
    return 1, 1


def main():
    local_failures, repairs = local_delta_checks()
    tested, sat_count, unsat_count = exhaustive_small_regression()
    unsat_controls, sat_extra_controls = frozen_controls()

    print("PASS_P3_OVERLAP_THREE_PARTITION_MATROID_CARRIER")
    print(f"local_delta_failures={local_failures}")
    print(f"one_state_delta_repairs={repairs}")
    print(f"small_normalized_formulas_tested={tested}")
    print(f"sat_controls={sat_count}")
    print(f"small_unsat_controls={unsat_count}")
    print(f"frozen_unsat_controls={unsat_controls}")
    print(f"frozen_sat_extra_controls={sat_extra_controls}")
    print("pair_block_overlap=DISJOINT_P3_K2")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
