#!/usr/bin/env python3
"""Universal SUPPORT coefficient attack: E118 amplification and cancellation.

Purpose: test a *global* coefficient-extraction proposal for every square/
cubic/linear Exact-One instance. The coefficient identity is exact, but NO
polynomial coefficient-extraction algorithm is supplied or claimed.

The E118 cubic occurrence-splitting gadget amplifies the number of solutions
by 2^(2n/3); in particular ordinary characteristic-2 counts cannot serve as
Boolean support bits even on arbitrarily large SAT members of the target class.

This is a direct audit of a universal algorithm candidate, not a new terminal.
"""
from __future__ import annotations

from collections import Counter
from itertools import product

from r5_e118_universal_linear_cubic_exactone_hardness_bridge import (
    GADGET_CLAUSES, INTERNAL, PORTS, exact_one,
    rename_gadget, split_occurrences,
)


def equal3_extensions(port_value: int) -> list[dict[str, int]]:
    extensions = []
    for bits in product((0, 1), repeat=len(INTERNAL)):
        local = dict(zip(INTERNAL, bits))
        local.update({port: port_value for port in PORTS})
        if all(exact_one(clause, local) for clause in GADGET_CLAUSES):
            extensions.append(local)
    assert len(extensions) == (2 if port_value == 0 else 1)
    return extensions


def frozen_source(k: int):
    """k independent cubic positive Exact-One triples, n=3k."""
    assert 1 <= k <= 2
    rows = []
    blocks = []
    for b in range(k):
        tri = tuple(f"block{b}_v{j}" for j in range(3))
        blocks.append(tri)
        rows.extend((tri, tri, tri))
    return tuple(rows), blocks


def build_reduction(source):
    split, port_map = split_occurrences(source)
    target = list(split)
    for v, ports in port_map.items():
        target.extend(rename_gadget(f"G_{v}", ports))
    variables = {v for row in target for v in row}
    assert len(target) == len(variables) == 10 * len(source)
    assert all(len(row) == len(set(row)) == 3 for row in target)
    degree = Counter(v for row in target for v in row)
    assert set(degree.values()) == {3}
    assert all(
        len(set(target[i]).intersection(target[j])) <= 1
        for i in range(len(target))
        for j in range(i)
    )
    return target, port_map


def verify_toy(k: int) -> None:
    source, blocks = frozen_source(k)
    rows, ports = build_reduction(source)
    n_source = len(source)
    assert n_source == 3*k

    e0 = equal3_extensions(0)
    e1 = equal3_extensions(1)

    # Every source satisfying assignment chooses one variable per block.
    assignments = []
    for selected_by_block in product(range(3), repeat=k):
        source_bits = {
            v: int(j == selected_by_block[b])
            for b, tri in enumerate(blocks)
            for j, v in enumerate(tri)
        }
        assert all(sum(source_bits[v] for v in row) == 1 for row in source)

        local_options = [
            e1 if source_bits[v] else e0
            for v in ports
        ]
        variables = list(ports)
        for choices in product(*local_options):
            target_bits = {}
            for var, choice in zip(variables, choices):
                for j, p in zip(PORTS, ports[var]):
                    target_bits[p] = choice[j]
                for name in INTERNAL:
                    target_bits[f"G_{var}_{name}"] = choice[name]
            assert len(target_bits) == 10 * n_source
            assert all(sum(target_bits[v] for v in row) == 1 for row in rows)
            assignments.append(target_bits)

    count = len(assignments)
    expected = (3 ** k) * (2 ** (2*k))
    assert count == expected == 12 ** k
    per_port_counts = [
        tuple(sum(sol[v] for sol in assignments) for v in row)
        for row in rows
    ]
    assert set(per_port_counts) == {(4 * 12**(k-1),)*3}
    assert all(all(c > 0 and c % 2 == 0 for c in triple)
               for triple in per_port_counts)

    # Every check has true SUPPORT=111 but all mod-2 counts vanish.
    assert all(sum(ct) == count for ct in per_port_counts)
    print(
        f"source_n={n_source} target_n={len(rows)} "
        f"source_sat={3**k} target_sat={count} "
        f"each_port_count={4 * 12**(k-1)} "
        f"true_mask=111 mod2_mask=000: PASS"
    )


def main():
    verify_toy(1)
    verify_toy(2)
    print("General E118 exact amplification: Z_target=2^(2n/3)*Z_source")
    print("General target one-port counts divisible by 2^(2n/3-1)")
    print("Global coefficient extraction in polynomial time: NOT ESTABLISHED")
    print("Universal SolveLinearCubicXSAT: NOT CONSTRUCTED; P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
