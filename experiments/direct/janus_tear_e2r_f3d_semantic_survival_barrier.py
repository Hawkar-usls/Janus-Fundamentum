#!/usr/bin/env python3
"""Finite replay for C025-E2R-L1G-F3-D semantic survival barrier.

Validates small explicit instances only; not an asymptotic proof.
"""
from __future__ import annotations

from itertools import product
from typing import Dict, List, Sequence, Set, Tuple

Literal = Tuple[str, str, bool]
Gate = Tuple[str, Literal, Literal]


def root(name: str, neg: bool = False) -> Literal:
    return ("root", name, neg)


def ext(name: str, neg: bool = False) -> Literal:
    return ("ext", name, neg)


def build(B: int, D: int) -> Tuple[Set[str], List[Gate], str]:
    if B < 2 or D < 1:
        raise ValueError("require B>=2,D>=1")
    roots: Set[str] = {"z"}
    gates: List[Gate] = []
    tops: List[str] = []
    for j in range(1, B + 1):
        y = f"y{j}"
        roots.add(y)
        name = f"g{j}_1"
        gates.append((name, root("z"), root(y)))
        prev = name
        for t in range(2, D + 1):
            name = f"g{j}_{t}"
            gates.append((name, root("z"), ext(prev, True)))
            prev = name
        tops.append(prev)
    agg = "A2"
    gates.append((agg, ext(tops[0], True), ext(tops[1], True)))
    for j in range(3, B + 1):
        nxt = f"A{j}"
        gates.append((nxt, ext(agg), ext(tops[j - 1], True)))
        agg = nxt
    return roots, gates, agg


def supports(roots: Set[str], gates: Sequence[Gate]) -> Dict[str, Set[str]]:
    out: Dict[str, Set[str]] = {r: {r} for r in roots}
    for name, a, b in gates:
        out[name] = set(out[a[1]]) | set(out[b[1]])
    return out


def metrics(roots: Set[str], gates: Sequence[Gate]) -> Tuple[int, int]:
    # Abstract locality hypergraph with singleton neighborhoods. Therefore
    # every extension depending on z and at least one y_j is crossing.
    neighborhoods = [{r} for r in roots]
    supp = supports(roots, gates)
    crossing = {
        name: not any(supp[name] <= hood for hood in neighborhoods)
        for name, _, _ in gates
    }
    gate_map = {name: (a, b) for name, a, b in gates}

    depth: Dict[str, int] = {}
    for name, a, b in gates:
        candidates = [0]
        for op in (a, b):
            if op[0] == "ext":
                child = op[1]
                candidates.append(
                    depth[child] + int(op[2] and crossing[child] and crossing[name])
                )
        depth[name] = max(candidates)

    memo: Dict[str, Set[Tuple[str, str]]] = {}

    def frontier(name: str) -> Set[Tuple[str, str]]:
        if name in memo:
            return set(memo[name])
        found: Set[Tuple[str, str]] = set()
        for op in gate_map[name]:
            if op[0] != "ext" or not crossing.get(op[1], False):
                continue
            child = op[1]
            if op[2]:
                found.add((child, name))
            else:
                found.update(frontier(child))
        memo[name] = set(found)
        return found

    b = max(len(frontier(name)) for name, _, _ in gates)
    d = max(depth.values())
    return b, d


def residual_tables(roots: Set[str], gates: Sequence[Gate], rho: Dict[str, int]):
    free = sorted(roots - set(rho))
    tables = {name: [] for name, _, _ in gates}
    for bits in product((0, 1), repeat=len(free)):
        assignment = dict(rho)
        assignment.update(dict(zip(free, bits)))
        values: Dict[str, int] = {}

        def value(op: Literal) -> int:
            kind, name, neg = op
            raw = assignment[name] if kind == "root" else values[name]
            return 1 - raw if neg else raw

        for name, a, b in gates:
            values[name] = value(a) & value(b)
            tables[name].append(values[name])
    return {name: tuple(vs) for name, vs in tables.items()}


def replay(B: int, D: int) -> None:
    roots, gates, final = build(B, D)
    b, d = metrics(roots, gates)
    assert b >= B, (B, D, b, d)
    assert d >= D, (B, D, b, d)
    assert len(gates) == B * D + (B - 1)

    tables = residual_tables(roots, gates, {"z": 0})
    assert all(table and all(v == table[0] for v in table) for table in tables.values())
    assert set(tables[final]) == {1}


def main() -> None:
    cases = 0
    for B in range(2, 7):
        for D in range(1, 7):
            replay(B, D)
            cases += 1
    assert cases == 30
    print("C025_E2R_F3D_D0_COUNTERFAMILY_FINITE_REPLAY = PASS")
    print("C025_E2R_F3D_D0_PRE_B_GE_TARGET = PASS")
    print("C025_E2R_F3D_D0_PRE_D_GE_TARGET = PASS")
    print("C025_E2R_F3D_D0_ONE_ROOT_BIT_COLLAPSES_ALL_TESTED_MACROS = PASS")
    print("C025_E2R_F3D_CLAIM_CEILING = FINITE_MECHANICS_ONLY")
    print("C025_E2R_F3D_NEXT = EXACT_SELF_REDUCTION_SEMANTIC_SURVIVAL")


if __name__ == "__main__":
    main()
