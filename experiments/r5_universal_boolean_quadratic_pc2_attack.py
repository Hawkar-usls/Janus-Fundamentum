#!/usr/bin/env python3
"""Universal-algorithm attack: degree-two Boolean polynomial calculus over GF(2).

The exact-one Boolean clause (a,b,c) has the equivalent field encoding
    1+a+b+c = 0,   ab+ac+bc = 0   over GF(2), with idempotent x^2=x.

Compute *all* degree <= 2 consequences of these generators (a fixed
polynomial-time Macaulay/PC2 test). A constant 1 in their linear span is
a sound UNSAT certificate. A noncontradictory span is NOT proof of SAT.

Critical E118 test: a cyclic q9 cubic source (UNSAT by complete 2^9
enumeration) embeds via the canonical equality gadget into a q90
square/cubic/linear UNSAT target that survives the full degree-2 test.
Do not infer a universal solver from its success on Tutte-12 E123.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, product

from r5_e64_connected_postquotient_nullity_firewall import tutte12_incidence
from r5_e118_universal_linear_cubic_exactone_hardness_bridge import (
    GADGET_CLAUSES, INTERNAL, PORTS,
    exact_one, rename_gadget, split_occurrences, verify_gadget,
)


def cyclic_source(n: int, a: int, b: int) -> tuple[tuple[str, str, str], ...]:
    return tuple(
        tuple("v" + str(v) for v in (i, (i + a) % n, (i + b) % n))
        for i in range(n)
    )


def source_solutions(rows: tuple[tuple[str, ...], ...]) -> list[dict[str, int]]:
    variables = sorted({v for row in rows for v in row})
    assert len(variables) <= 9  # Exhaustive, finite controls only.
    out = []
    for bits in product((0, 1), repeat=len(variables)):
        d = dict(zip(variables, bits))
        if all(sum(d[v] for v in row) == 1 for row in rows):
            out.append(d)
    return out


def e118_target(source: tuple[tuple[str, ...], ...]):
    split, ports = split_occurrences(source)
    target = list(split)
    for v, port_list in ports.items():
        target.extend(rename_gadget("G_" + v, port_list))
    variables = sorted({v for row in target for v in row})
    pos = {v: j for j, v in enumerate(variables)}
    rows = [tuple(pos[v] for v in row) for row in target]
    return rows, ports, pos


def verify_target(rows: list[tuple[int, int, int]]) -> None:
    n = len(rows)
    assert n % 3 == 0
    degree = Counter(v for row in rows for v in row)
    assert len(degree) == n and set(degree.values()) == {3}
    assert all(len(set(row)) == 3 for row in rows)
    pairs = [pair for row in rows for pair in combinations(sorted(row), 2)]
    assert len(set(pairs)) == 3 * n, "Repeated pair: violates linearity/C4-free"

    # Connected Levi graph, not a disconnected padding trick.
    adj = [set() for _ in range(2*n)]
    for i, row in enumerate(rows):
        for v in row:
            adj[i].add(n + v)
            adj[n + v].add(i)
    seen = {0}
    todo = [0]
    while todo:
        for v in adj[todo.pop()]:
            if v not in seen:
                seen.add(v)
                todo.append(v)
    assert len(seen) == 2*n


def real_witness_from_source(model, ports, target_rows, index):
    target_model = {}
    for var, triple in ports.items():
        bit = model[var]
        for port in triple:
            target_model[port] = bit
        extensions = []
        for internal_bits in product((0, 1), repeat=len(INTERNAL)):
            local = dict(zip(INTERNAL, internal_bits))
            local.update({v: bit for v in PORTS})
            if all(exact_one(c, local) for c in GADGET_CLAUSES):
                extensions.append(local)
        assert len(extensions) == (2 if bit == 0 else 1)
        for v in INTERNAL:
            target_model["G_" + var + "_" + v] = extensions[0][v]
    vals = [None] * len(index)
    for v,j in index.items():
        vals[j] = target_model[v]
    assert all(sum(vals[v] for v in row) == 1 for row in target_rows)
    return vals


def pc2_refutation(rows: list[tuple[int, int, int]]) -> tuple[int,int,int,bool]:
    """Complete degree-two polynomial calculus modulo Boolean idempotence.

    Basis: 1, x_i, x_i*x_j. Generator multiples: p_c, x_j*p_c
    for every row c and variable j; q_c. This includes every
    multiplication of a degree-one row generator to degree <= 2.
    The q_c already has degree 2, so only constant multiples apply.
    Gaussian elimination uses arbitrary-precision integer bitsets.
    """
    n = len(rows)
    mons = [()] + [(i,) for i in range(n)] + [
        (i,j) for i in range(n) for j in range(i+1,n)
    ]
    pos = {m: j for j,m in enumerate(mons)}
    def poly_product(mult, terms):
        out = 0
        for term in terms:
            m = tuple(sorted(set(mult) | set(term)))
            assert len(m) <= 2
            out ^= 1 << pos[m]
        return out

    pivot = {}
    generator_count = 0
    for row in rows:
        pterms = [()] + [(j,) for j in row]
        qterms = [tuple(sorted(pair)) for pair in combinations(row,2)]
        for mult in [()] + [(j,) for j in range(n)]:
            v = poly_product(mult, pterms)
            generator_count += 1
            while v:
                lead = v.bit_length() - 1
                if lead not in pivot:
                    pivot[lead] = v
                    break
                v ^= pivot[lead]
        v = poly_product((),qterms)
        generator_count += 1
        while v:
            lead = v.bit_length() - 1
            if lead not in pivot:
                pivot[lead] = v
                break
            v ^= pivot[lead]

    unit = 1 << pos[()]
    while unit:
        lead = unit.bit_length()-1
        if lead not in pivot:
            break
        unit ^= pivot[lead]
    return len(mons),generator_count,len(pivot),unit==0


def main() -> None:
    verify_gadget()

    # Main counterexample: 9-source -> 90-target, fully SAT preserving.
    source = cyclic_source(9,1,6)
    assert not source_solutions(source)  # exact independent 2^9 search
    target, ports, idx = e118_target(source)
    verify_target(target)
    assert len(target) == 90
    negative = pc2_refutation(target)
    assert negative == (4096, 8280, 3969, False), negative

    # SAT positive control of exactly the same shape / gadget compilation.
    source_sat = cyclic_source(9,1,2)
    models = source_solutions(source_sat)
    assert models
    sat_target, sat_ports, sat_idx = e118_target(source_sat)
    verify_target(sat_target)
    real_witness_from_source(models[0], sat_ports, sat_target, sat_idx)
    positive = pc2_refutation(sat_target)
    assert positive == (4096, 8280, 3966, False), positive

    # E123 is a stronger-but-finite UNSAT control, rejected by PC2.
    R = tutte12_incidence()
    rt = [list(c) for c in zip(*R)]
    bad63 = pc2_refutation([
        tuple(j for j, v in enumerate(row) if v) for row in R
    ])
    good63 = pc2_refutation([
        tuple(j for j, v in enumerate(row) if v) for row in rt
    ])
    assert bad63 == (2017,4095,1960,True), bad63
    assert good63 == (2017,4095,1960,False), good63

    print("UNIVERSAL PC2 ATTACK: EXACT REPLAY PASS")
    print("source cyclic q9 shifts(1,6): UNSAT by exhaustive 2^9")
    print("E118 target q90: connected cubic linear UNSAT; PC2 inconclusive",negative)
    print("source cyclic q9 shifts(1,2): SAT; E118 target q90 SAT",positive)
    print("E123 Tutte-12 q63 UNSAT PC2 refuted",bad63)
    print("E65 q63 transpose SAT PC2 not refuted",good63)
    print("PC2 contradiction => UNSAT: SOUND FOR ALL INSTANCES")
    print("PC2 inconclusive => SAT: REFUTED BY EXPLICIT Q90 INSTANCE")
    print("POLYNOMIAL UNIVERSAL SOLVER = NOT CONSTRUCTED; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
