#!/usr/bin/env python3
"""Provider replay for C025-E2R-L1G finite mechanics."""
from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Gate:
    var: int
    left: int
    right: int
    crossing: bool = True


def eval_lit(lit, values):
    v = values[abs(lit)]
    return v if lit > 0 else not v


def evaluate_gates(root_assignment, gates):
    values = dict(root_assignment)
    for g in gates:
        values[g.var] = eval_lit(g.left, values) and eval_lit(g.right, values)
    return values


def parity_b2(n):
    if n == 1:
        return [], 1
    gates, nxt, y = [], n + 1, 1
    for x in range(2, n + 1):
        t1, t2, yp = nxt, nxt + 1, nxt + 2
        nxt += 3
        gates += [Gate(t1, y, x), Gate(t2, -y, -x), Gate(yp, -t1, -t2)]
        y = yp
    return gates, y


def exact_parity_cnf(n):
    out = set()
    for bits in product((False, True), repeat=n):
        if sum(bits) % 2:
            continue
        out.add(frozenset((-i if bits[i-1] else i) for i in range(1, n + 1)))
    return out


def crossing_monotone(gates, local_atoms):
    crossings, known = set(), set(local_atoms)
    for g in gates:
        for lit in (g.left, g.right):
            v = abs(lit)
            if v not in known and v not in crossings:
                raise ValueError("unknown/forward operand")
            if v in crossings and lit < 0:
                return False
        if g.var in known or g.var in crossings:
            raise ValueError("nonfresh gate")
        (crossings if g.crossing else known).add(g.var)
    return True


def flatten(var, gate_map, locals_):
    def rec(lit):
        v = abs(lit)
        if v in locals_:
            return [lit]
        if lit < 0:
            raise ValueError("negative crossing dependency")
        g = gate_map[v]
        return rec(g.left) + rec(g.right)
    seen, out = set(), []
    for lit in rec(var):
        if lit not in seen:
            seen.add(lit); out.append(lit)
    return tuple(out)


def expand_clause(clause, macros):
    acc = {frozenset()}
    for lit in clause:
        v = abs(lit)
        if v not in macros:
            options = [frozenset({lit})]
        elif lit > 0:
            options = [frozenset({x}) for x in macros[v]]
        else:
            options = [frozenset({-x for x in macros[v]})]
        nxt = set()
        for a in acc:
            for b in options:
                c = frozenset(a | b)
                if not any(-x in c for x in c):
                    nxt.add(c)
        acc = nxt
    return acc


def resolve(p, q, pivot):
    if pivot not in p or -pivot not in q:
        return None
    c = frozenset((p-{pivot}) | (q-{-pivot}))
    return None if any(-x in c for x in c) else c


def main():
    for n in range(2, 9):
        gates, out = parity_b2(n)
        assert len(gates) == 3*(n-1)
        for bits in product((False, True), repeat=n):
            vals = evaluate_gates({i+1: bits[i] for i in range(n)}, gates)
            assert vals[out] == (sum(bits) % 2 == 1)
        cnf = exact_parity_cnf(n)
        assert len(cnf) == 2**(n-1)
        assert all(len(c) == n for c in cnf)

    locals_ = set(range(1, 9))
    gs = [Gate(20,1,2), Gate(21,20,3), Gate(22,21,-4)]
    assert crossing_monotone(gs, locals_)
    gm = {g.var:g for g in gs}
    macros = {v: flatten(v, gm, locals_) for v in (20,21,22)}
    assert macros[20] == (1,2)
    assert macros[21] == (1,2,3)
    assert macros[22] == (1,2,3,-4)
    assert len(expand_clause((22,), macros)) == 4
    assert expand_clause((-22,), macros) == {frozenset({-1,-2,-3,4})}
    assert len(expand_clause((20,21,22), macros)) == 24
    assert len(expand_clause((20,21,22), macros)) <= (1+sum(map(len, macros.values())))**3
    assert not crossing_monotone([Gate(20,1,2), Gate(21,-20,3)], locals_)

    for r in range(2,9):
        leaves = list(range(1,r+1)); A,B=100,101
        cur = frozenset({B, *(-x for x in leaves)})
        for leaf in leaves:
            cur = resolve(frozenset({A,leaf}), cur, leaf)
            assert cur is not None
        assert cur == frozenset({A,B})

    print("C025_E2R_L1G_PARITY_LINEAR_B2_GATE_COUNT = PASS")
    print("C025_E2R_L1G_PARITY_EXACT_CNF_EXPONENTIAL = PASS")
    print("C025_E2R_L1G_GENERIC_POLY_ELIMINATION_ROUTE = REFUTED")
    print("C025_E2R_L1G_CROSSING_MONOTONE_ADMISSION = PASS")
    print("C025_E2R_L1G_MONOTONE_FLATTENING = PASS")
    print("C025_E2R_L1G_ER3_MACRO_CLAUSE_POLY_EXPANSION = PASS")
    print("C025_E2R_L1G_FLATTENED_PIVOT_CHAIN = PASS")
    print("C025_E2R_L1G_NEGATIVE_CROSSING_DEPENDENCY_REJECTION = PASS")
    print("claim_boundary = finite mechanics only; restricted asymptotic consequence uses the established NW local-functional lower bound")


if __name__ == "__main__":
    main()
