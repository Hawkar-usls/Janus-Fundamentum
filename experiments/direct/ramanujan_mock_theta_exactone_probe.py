#!/usr/bin/env python3
"""Exact finite-size controls for FARADAY–RAMANUJAN–EXACTONE.

Only Python standard library; no quantum, electromagnetic or mock-modular
solver is claimed. All energy coefficients are found by 2**n enumeration.
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from math import isqrt


FIXTURES = (
    ("n09_unsat", 9, (0, 1, 3), 0),
    ("n12_unsat", 12, (0, 1, 3), 0),
    ("n12_sat", 12, (0, 1, 5), 3),
    ("n15_unsat_rank_deficient", 15, (0, 1, 4), 0),
    ("n15_sat", 15, (0, 1, 5), 3),
)


def circulant_rows(n: int, shifts: tuple[int, int, int]) -> tuple[int, ...]:
    if n <= 0 or len(set(shifts)) != 3:
        raise ValueError("Need n > 0 and three distinct shifts")
    return tuple(sum(1 << ((i + shift) % n) for shift in shifts)
                 for i in range(n))


def validate_square_cubic_linear(rows: tuple[int, ...], n: int) -> None:
    if len(rows) != n or n % 3:
        raise ValueError("Square carrier with n divisible by 3 required")
    if any(r.bit_count() != 3 for r in rows):
        raise ValueError("Every check must have degree three")
    if any(sum(bool((r >> j) & 1) for r in rows) != 3 for j in range(n)):
        raise ValueError("Every variable must have degree three")
    if any((a & b).bit_count() > 1 for a, b in combinations(rows, 2)):
        raise ValueError("Linearity violated: pair of checks shares two variables")


def energy(bits: int, rows: tuple[int, ...]) -> int:
    return sum(((bits & row).bit_count() - 1) ** 2 for row in rows)


def exact_partition(rows: tuple[int, ...], n: int) -> tuple[list[int], list[int]]:
    # Exponential reference oracle; intentionally NOT a scalable solver.
    coefficients = [0] * (4 * len(rows) + 1)
    solutions = []
    for bits in range(1 << n):
        e = energy(bits, rows)
        coefficients[e] += 1
        if e == 0:
            solutions.append(bits)
    return coefficients, solutions


def independent_sat_count(rows: tuple[int, ...], n: int) -> int:
    # Independent recursive exact-one propagation, not based on "energy".
    check_vars = [tuple(j for j in range(n) if (row >> j) & 1) for row in rows]
    by_var = [[] for _ in range(n)]
    for i, triple in enumerate(check_vars):
        for j in triple:
            by_var[j].append(i)
    used = [0] * len(rows)
    remaining = [3] * len(rows)

    def visit(j: int) -> int:
        if j == n:
            return int(all(v == 1 for v in used))
        total = 0
        for value in (0, 1):
            allowed = True
            for i in by_var[j]:
                used[i] += value
                remaining[i] -= 1
                if used[i] > 1 or used[i] + remaining[i] < 1:
                    allowed = False
            if allowed:
                total += visit(j + 1)
            for i in by_var[j]:
                used[i] -= value
                remaining[i] += 1
        return total

    return visit(0)


def gf2_rank_and_consistency(rows: tuple[int, ...], n: int) -> tuple[int, bool]:
    # RREF of A x = 1 over GF(2).
    extended = [row | (1 << n) for row in rows]
    rank = 0
    for col in range(n):
        piv = next((i for i in range(rank, len(extended))
                    if (extended[i] >> col) & 1), None)
        if piv is None:
            continue
        extended[rank], extended[piv] = extended[piv], extended[rank]
        for i in range(len(extended)):
            if i != rank and ((extended[i] >> col) & 1):
                extended[i] ^= extended[rank]
        rank += 1
    consistent = all(row != (1 << n) for row in extended[rank:])
    return rank, consistent


def selected_port_support(rows: tuple[int, ...], solutions: list[int]) -> int:
    # A three-bit SUPPORT_c relative to check c=0's sorted port order.
    ports = [j for j in range(max(rows).bit_length()) if (rows[0] >> j) & 1]
    if len(ports) != 3:
        raise ValueError("Expected exactly three ports")
    return sum((1 << k) for k, j in enumerate(ports)
               if any((bits >> j) & 1 for bits in solutions))


def mock_theta_f_prefix(degree: int) -> list[int]:
    """Formal coefficients of Ramanujan's third-order f(q).

    f(q)=sum_{r>=0} q^(r*r) / prod_{k=1}^r (1+q^k)^2.
    Uses (1+u)^(-2) = sum_{j>=0} (-1)^j (j+1) u^j.
    """
    coefficients = [0] * (degree + 1)
    for r in range(isqrt(degree) + 1):
        inverse = [1] + [0] * degree
        for k in range(1, r + 1):
            updated = [0] * (degree + 1)
            for exp, value in enumerate(inverse):
                if value:
                    for j in range((degree - exp) // k + 1):
                        updated[exp + k * j] += value * (-1 if j & 1 else 1) * (j + 1)
            inverse = updated
        for exp in range(degree - r*r + 1):
            coefficients[r*r + exp] += inverse[exp]
    return coefficients


def discrete_faraday_identity() -> bool:
    # The boundary of a boundary vanishes: curl(grad(phi)) = 0
    # on an oriented triangle (0->1, 1->2, 2->0).
    for phi in ((0, 0, 0), (2, -3, 7), (11, 2, -8)):
        e = (phi[1]-phi[0], phi[2]-phi[1], phi[0]-phi[2])
        if sum(e) != 0:
            return False
    return True


def run() -> dict:
    controls = []
    for name, n, shifts, expected_sat in FIXTURES:
        rows = circulant_rows(n, shifts)
        validate_square_cubic_linear(rows, n)
        coefficients, solutions = exact_partition(rows, n)
        rank, gf2_consistent = gf2_rank_and_consistency(rows, n)
        assert coefficients[0] == expected_sat
        assert independent_sat_count(rows, n) == expected_sat
        assert sum(coefficients) == 1 << n  # Z(1) = 2^n
        assert sum(i*c for i, c in enumerate(coefficients)) == n*(1 << n)  # Z'(1)
        assert gf2_consistent  # all-ones assignment always solves A x = 1 mod 2
        # For degree-three square incidence, incidence-graph V=2n E=3n.
        # All these fixed-shift circulant bipartite graphs are connected.
        # Cycle rank is n+1, verified by an explicit connectedness BFS.
        adjacency = [[] for _ in range(2*n)]
        for i, row in enumerate(rows):
            for j in range(n):
                if (row >> j) & 1:
                    adjacency[i].append(n+j)
                    adjacency[n+j].append(i)
        visited = {0}
        frontier = [0]
        while frontier:
            for v in adjacency[frontier.pop()]:
                if v not in visited:
                    visited.add(v)
                    frontier.append(v)
        assert len(visited) == 2*n
        controls.append({
            "name": name,
            "n": n,
            "shifts": list(shifts),
            "sat_count": len(solutions),
            "support_c0_mask": selected_port_support(rows, solutions),
            "gf2_rank": rank,
            "gf2_consistent": gf2_consistent,
            "cycle_rank": n+1,
            "coefficients_first_10": coefficients[:10],
            "min_energy": next(i for i, x in enumerate(coefficients) if x),
            "states_charged": 1 << n,
            "partition_at_one": sum(coefficients),
            "first_moment": sum(i*c for i, c in enumerate(coefficients)),
        })
    mock = mock_theta_f_prefix(12)
    assert mock[:6] == [1, 1, -2, 3, -3, 3]
    assert discrete_faraday_identity()
    assert controls[1]["cycle_rank"] == controls[2]["cycle_rank"]
    assert controls[1]["sat_count"] != controls[2]["sat_count"]
    assert controls[3]["gf2_rank"] < controls[3]["n"]  # UNSAT despite nontrivial kernel
    return {
        "status": "FINITE_EXACT_CONTROLS_ONLY",
        "claim_boundary": "No general polynomial solver; no modularity proven; no physical speedup.",
        "mock_theta_f_coefficients_degree_0_to_12": mock,
        "mock_theta_f_has_negative_coefficients": any(x < 0 for x in mock),
        "discrete_curl_gradient_identity": True,
        "fixtures": controls,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        for fixture in result["fixtures"]:
            print(f'{fixture["name"]}: sat={fixture["sat_count"]}, '
                  f'gf2_rank={fixture["gf2_rank"]}, '
                  f'cycle_rank={fixture["cycle_rank"]}, '
                  f'SUPPORT_c0={fixture["support_c0_mask"]:03b}')
        print("mock f(q) prefix:", result["mock_theta_f_coefficients_degree_0_to_12"])
        print("PASS: exact finite controls only, not polynomial solver")


if __name__ == "__main__":
    main()
