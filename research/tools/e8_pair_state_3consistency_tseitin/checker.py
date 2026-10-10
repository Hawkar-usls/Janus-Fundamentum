#!/usr/bin/env python3
"""Exact regression for the E8 v4.0 pair-state / Tseitin barrier."""

from itertools import combinations, product

# Six K4 edge variables, numbered 0..5.
EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
EDGE_ID = {e: i for i, e in enumerate(EDGES)}
INCIDENT = {
    v: [i for i, e in enumerate(EDGES) if v in e]
    for v in range(4)
}
CHARGE = {0: 1, 1: 0, 2: 0, 3: 0}


def xor_relation(scope, parity):
    """Allowed assignments on one arity-3 parity scope."""
    return {
        vals for vals in product((0, 1), repeat=3)
        if (sum(vals) & 1) == parity
    }


def xor3_cnf(scope, parity):
    """Four width-3 clauses encoding xor(scope)=parity exactly.

    Literal is (var, sign), sign=True for x and False for not x.
    """
    clauses = []
    for vals in product((0, 1), repeat=3):
        if (sum(vals) & 1) != parity:
            # Clause falsified exactly by this wrong assignment.
            clause = frozenset((v, not bool(val)) for v, val in zip(scope, vals))
            clauses.append(clause)
    assert len(clauses) == 4
    return clauses


def formula():
    out = []
    for v in range(4):
        out.extend(xor3_cnf(INCIDENT[v], CHARGE[v]))
    assert len(out) == 16
    return out


def sat_clause(clause, assignment):
    return any(bool(assignment[v]) == sign for v, sign in clause)


def brute_sat(clauses):
    for bits in product((0, 1), repeat=6):
        if all(sat_clause(c, bits) for c in clauses):
            return True
    return False


def normalize_clause(lits):
    seen = {}
    for v, sign in lits:
        if v in seen and seen[v] != sign:
            return None  # tautology
        seen[v] = sign
    return frozenset(seen.items())


def resolve(c1, c2, pivot):
    pos = (pivot, True)
    neg = (pivot, False)
    if pos in c1 and neg in c2:
        raw = (c1 - {pos}) | (c2 - {neg})
    elif neg in c1 and pos in c2:
        raw = (c1 - {neg}) | (c2 - {pos})
    else:
        return None
    return normalize_clause(raw)


def width3_closure(clauses):
    S = set(clauses)
    changed = True
    while changed:
        changed = False
        current = list(S)
        additions = set()
        for i, c1 in enumerate(current):
            vars1 = {v for v, _ in c1}
            for c2 in current[i + 1:]:
                for v in vars1 & {x for x, _ in c2}:
                    r = resolve(c1, c2, v)
                    if r is not None and len(r) <= 3 and r not in S:
                        additions.add(r)
        if additions:
            S.update(additions)
            changed = True
            if frozenset() in S:
                break
    return S


def check_strong3_local_consistency():
    relations = []
    for vertex in range(4):
        scope = tuple(INCIDENT[vertex])
        relations.append((scope, xor_relation(scope, CHARGE[vertex])))

    # Every local ternary parity relation has full binary projections.
    for scope, rel in relations:
        for pair_pos in combinations(range(3), 2):
            projected = {
                (vals[pair_pos[0]], vals[pair_pos[1]])
                for vals in rel
            }
            assert projected == {(0, 0), (0, 1), (1, 0), (1, 1)}

    # Strong-3 extension check: every assignment to any two variables can be
    # extended to any third variable so that all constraints whose full scope
    # lies in that triple are satisfied.
    for x, y in combinations(range(6), 2):
        for ax, ay in product((0, 1), repeat=2):
            for z in range(6):
                if z in (x, y):
                    continue
                ok = False
                for az in (0, 1):
                    local = {x: ax, y: ay, z: az}
                    valid = True
                    for scope, rel in relations:
                        if set(scope).issubset(local):
                            tup = tuple(local[v] for v in scope)
                            if tup not in rel:
                                valid = False
                                break
                    if valid:
                        ok = True
                        break
                assert ok, (x, y, ax, ay, z)


def main():
    clauses = formula()

    # Exact global UNSAT control.
    assert not brute_sat(clauses)
    # Independent algebraic certificate: XOR of all four vertex equations.
    assert sum(CHARGE.values()) & 1 == 1
    for e in range(6):
        assert sum(e in INCIDENT[v] for v in range(4)) == 2

    # Complete width<=3 resolution saturation is silent on this K4 control.
    closure = width3_closure(clauses)
    assert frozenset() not in closure
    assert closure == set(clauses), (len(clauses), len(closure))

    # O(n^2) pair-state / strong-3 local consistency is also silent.
    check_strong3_local_consistency()

    print("PASS: K4 odd-charge Tseitin 3-CNF has 16 width-3 clauses and is UNSAT")
    print("PASS: width<=3 resolution closure adds no clause and derives no contradiction")
    print("PASS: every Boolean pair state survives strong-3 local extension consistency")


if __name__ == "__main__":
    main()
