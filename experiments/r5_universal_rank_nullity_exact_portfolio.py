#!/usr/bin/env python3
"""Exact rank/nullity portfolio for legal square+cubic+linear Positive Exact-One.

For an n x n incidence matrix A with every row and column of weight three,

    Exact-One(A)
    iff there is k in ker_F2(A) with |k| = 2n/3,

and the witness is x = 1 + k (Boolean complement).

This file implements two COMPLETE deterministic routes.

RANK route:
    cardinality/syndrome dynamic programming over a row-space basis,
    time O(n^2 2^r), space O(n 2^r), r = rank_F2(A).

NULLITY route:
    write k=B t and require the restriction of k to every row to be
    a nonzero even triple.  This is a 2-CNF of linear forms.  Exact
    branching on l OR m as
        l=1  OR  (l=0 AND m=1)
    gives T(d) <= T(d-1)+T(d-2), hence O*(phi^d), d=n-r.

Choosing the smaller exponential envelope gives

    O*(min(2^r, phi^(n-r))) <= O*(1.328470^n).

The solver is universal in SOUNDNESS and COMPLETENESS, but its proven
worst-case runtime is exponential.  It is NOT the requested universal
polynomial-time algorithm.  P_VS_NP remains OPEN.

The controls are independent legal instances:
  * E61 SAT12 / UNSAT12;
  * direct cubic-edge-colouring bridges for K4 / Petersen.

No numerical optimisation, timeout-to-UNSAT inference, or heuristic
status promotion occurs.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Sequence


PHI = (1.0 + math.sqrt(5.0)) / 2.0
LOG2_PHI = math.log2(PHI)


def parity(word: int) -> int:
    return word.bit_count() & 1


def validate_legal(rows: Iterable[Iterable[int]], n: int) -> tuple[tuple[int, int, int], ...]:
    """Validate exactly the square/cubic/C4-free promise."""
    if not isinstance(n, int) or n <= 0:
        raise ValueError("n must be a positive integer")
    normalized = tuple(tuple(sorted(row)) for row in rows)
    if len(normalized) != n:
        raise ValueError("square promise failed: number of rows != n")

    degrees = [0] * n
    seen_pairs: dict[tuple[int, int], int] = {}
    for i, row in enumerate(normalized):
        if len(row) != 3 or len(set(row)) != 3:
            raise ValueError(f"row {i} is not a triple of distinct variables")
        if any(v < 0 or v >= n for v in row):
            raise ValueError(f"row {i} has an out-of-range variable")
        for v in row:
            degrees[v] += 1
        for pair in combinations(row, 2):
            if pair in seen_pairs:
                raise ValueError(
                    f"linearity failed: rows {seen_pairs[pair]} and {i} "
                    f"share variables {pair}"
                )
            seen_pairs[pair] = i
    if any(d != 3 for d in degrees):
        raise ValueError("cubic column promise failed")
    return normalized


def row_masks(rows: Sequence[Sequence[int]]) -> tuple[int, ...]:
    return tuple(sum(1 << j for j in row) for row in rows)


@dataclass(frozen=True)
class GF2Data:
    rank: int
    reduced_rows: tuple[int, ...]
    null_basis: tuple[int, ...]


def gf2_rref_and_nullspace(masks: Sequence[int], n: int) -> GF2Data:
    """RREF plus a homogeneous nullspace basis, using Python integers."""
    work = list(masks)
    pivot_cols: list[int] = []
    r = 0
    for col in range(n):
        pivot = next((i for i in range(r, len(work)) if (work[i] >> col) & 1), None)
        if pivot is None:
            continue
        work[r], work[pivot] = work[pivot], work[r]
        for i in range(len(work)):
            if i != r and ((work[i] >> col) & 1):
                work[i] ^= work[r]
        pivot_cols.append(col)
        r += 1
        if r == len(work):
            break

    pivot_set = set(pivot_cols)
    basis: list[int] = []
    for free in range(n):
        if free in pivot_set:
            continue
        word = 1 << free
        for i, pivot in enumerate(pivot_cols):
            if (work[i] >> free) & 1:
                word |= 1 << pivot
        basis.append(word)

    reduced = tuple(work[:r])
    assert all(all(parity(row & word) == 0 for row in reduced) for word in basis)
    assert r + len(basis) == n
    return GF2Data(r, reduced, tuple(basis))


@dataclass
class RankDPStats:
    processed_columns: int = 0
    peak_states: int = 1


def rank_cardinality_dp(
    reduced_rows: Sequence[int], n: int, target_weight: int
) -> tuple[int | None, RankDPStats]:
    """Find a target-weight kernel word by exact syndrome DP.

    A state (q,s) means that some q chosen columns XOR to syndrome s.
    Storing one bit-mask predecessor per state gives an explicit witness.
    """
    rank = len(reduced_rows)
    column_syndromes: list[int] = []
    for j in range(n):
        syndrome = 0
        for i, row in enumerate(reduced_rows):
            if (row >> j) & 1:
                syndrome |= 1 << i
        column_syndromes.append(syndrome)

    states: dict[tuple[int, int], int] = {(0, 0): 0}
    stats = RankDPStats()
    for j, syndrome in enumerate(column_syndromes):
        additions: dict[tuple[int, int], int] = {}
        for (weight, old_syndrome), witness in tuple(states.items()):
            if weight >= target_weight:
                continue
            key = (weight + 1, old_syndrome ^ syndrome)
            if key not in states and key not in additions:
                additions[key] = witness | (1 << j)
        states.update(additions)
        stats.processed_columns = j + 1
        stats.peak_states = max(stats.peak_states, len(states))

    return states.get((target_weight, 0)), stats


@dataclass(frozen=True)
class AffineState:
    """t = origin + span(basis) inside the nullspace parameter space."""

    origin: int
    basis: tuple[int, ...]


@dataclass
class BranchStats:
    nodes: int = 0
    conflicts: int = 0
    forced_equations: int = 0
    splits: int = 0
    max_depth: int = 0


def evaluate_form(form: int, state: AffineState) -> tuple[int, int]:
    constant = parity(form & state.origin)
    coefficients = 0
    for i, direction in enumerate(state.basis):
        if parity(form & direction):
            coefficients |= 1 << i
    return constant, coefficients


def impose_form(state: AffineState, form: int, value: int) -> AffineState | None:
    """Intersect an affine state with form(t)=value."""
    constant, coefficients = evaluate_form(form, state)
    rhs = value ^ constant
    if coefficients == 0:
        return state if rhs == 0 else None

    pivot = (coefficients & -coefficients).bit_length() - 1
    pivot_direction = state.basis[pivot]
    origin = state.origin ^ (pivot_direction if rhs else 0)
    basis: list[int] = []
    for i, direction in enumerate(state.basis):
        if i == pivot:
            continue
        basis.append(direction ^ (pivot_direction if ((coefficients >> i) & 1) else 0))
    return AffineState(origin, tuple(basis))


class NullityBranchSolver:
    """Exact deterministic affine 2-Sub-SAT solver."""

    def __init__(self, rows: Sequence[Sequence[int]], n: int, null_basis: Sequence[int]):
        self.rows = tuple(tuple(row) for row in rows)
        self.n = n
        self.null_basis = tuple(null_basis)
        self.d = len(self.null_basis)
        self.stats = BranchStats()

        coordinate_forms = [0] * n
        for bit, word in enumerate(self.null_basis):
            for j in range(n):
                if (word >> j) & 1:
                    coordinate_forms[j] |= 1 << bit
        self.coordinate_forms = tuple(coordinate_forms)

        pairs: list[tuple[int, int]] = []
        for a, b, c in self.rows:
            fa, fb, fc = (
                self.coordinate_forms[a],
                self.coordinate_forms[b],
                self.coordinate_forms[c],
            )
            assert fa ^ fb ^ fc == 0
            pairs.append((fa, fb))
        self.pairs = tuple(pairs)

    def normalize(
        self, state: AffineState
    ) -> tuple[str, AffineState, int | None]:
        """Apply exact unit/tautology rules; return conflict/success/split."""
        while True:
            changed = False
            split_row: int | None = None
            for row_id, (left, right) in enumerate(self.pairs):
                lc, lv = evaluate_form(left, state)
                rc, rv = evaluate_form(right, state)

                if (lv == 0 and lc == 1) or (rv == 0 and rc == 1):
                    continue
                if lv == 0 and rv == 0:
                    if (lc | rc) == 0:
                        return "conflict", state, row_id
                    continue
                if lv == 0:
                    assert lc == 0 and rv != 0
                    nxt = impose_form(state, right, 1)
                    assert nxt is not None
                    state = nxt
                    self.stats.forced_equations += 1
                    changed = True
                    break
                if rv == 0:
                    assert rc == 0 and lv != 0
                    nxt = impose_form(state, left, 1)
                    assert nxt is not None
                    state = nxt
                    self.stats.forced_equations += 1
                    changed = True
                    break
                if lv == rv:
                    if lc != rc:
                        # Complementary affine forms: their OR is a tautology.
                        continue
                    nxt = impose_form(state, left, 1)
                    assert nxt is not None
                    state = nxt
                    self.stats.forced_equations += 1
                    changed = True
                    break

                # Over F2, two distinct nonzero coefficient vectors are independent.
                if split_row is None:
                    split_row = row_id

            if changed:
                continue
            if split_row is None:
                return "success", state, None
            return "split", state, split_row

    def search(self) -> int | None:
        sys.setrecursionlimit(max(sys.getrecursionlimit(), 4 * self.d + 100))
        initial = AffineState(0, tuple(1 << i for i in range(self.d)))
        return self._search(initial, 0)

    def _search(self, state: AffineState, depth: int) -> int | None:
        self.stats.nodes += 1
        self.stats.max_depth = max(self.stats.max_depth, depth)
        kind, state, row_id = self.normalize(state)
        if kind == "conflict":
            self.stats.conflicts += 1
            return None
        if kind == "success":
            return state.origin

        assert kind == "split" and row_id is not None
        self.stats.splits += 1
        left, right = self.pairs[row_id]

        # Satisfying assignments of left OR right partition exactly as:
        # left=1, or left=0 and right=1.
        branch_one = impose_form(state, left, 1)
        assert branch_one is not None
        answer = self._search(branch_one, depth + 1)
        if answer is not None:
            return answer

        branch_two = impose_form(state, left, 0)
        assert branch_two is not None
        branch_two = impose_form(branch_two, right, 1)
        assert branch_two is not None
        return self._search(branch_two, depth + 1)

    def parameter_to_kernel_word(self, parameter: int) -> int:
        word = 0
        for j, form in enumerate(self.coordinate_forms):
            if parity(form & parameter):
                word |= 1 << j
        return word


def exact_one_witness(rows: Sequence[Sequence[int]], n: int, kernel_word: int) -> tuple[int, ...]:
    full = (1 << n) - 1
    xword = full ^ kernel_word
    witness = tuple((xword >> j) & 1 for j in range(n))
    if not all(sum(witness[j] for j in row) == 1 for row in rows):
        raise AssertionError("internal witness verification failed")
    return witness


def solve(
    rows: Iterable[Iterable[int]], n: int, route: str = "auto"
) -> dict[str, object]:
    rows = validate_legal(rows, n)
    if n % 3:
        return {
            "status": "UNSAT",
            "reason": "CARDINALITY_N_NOT_DIVISIBLE_BY_THREE",
            "proof": "3*|x|=n for every Exact-One witness",
            "witness": None,
            "p_vs_np": "OPEN",
        }

    masks = row_masks(rows)
    data = gf2_rref_and_nullspace(masks, n)
    rank = data.rank
    nullity = len(data.null_basis)
    target_kernel_weight = 2 * n // 3

    if route not in {"auto", "rank", "nullity"}:
        raise ValueError("route must be auto, rank, or nullity")
    if route == "auto":
        route = "rank" if rank <= LOG2_PHI * nullity else "nullity"

    kernel_word: int | None
    details: dict[str, object]
    if route == "rank":
        kernel_word, stats = rank_cardinality_dp(
            data.reduced_rows, n, target_kernel_weight
        )
        details = {
            "route": "EXACT_CARDINALITY_SYNDROME_DP",
            "processed_columns": stats.processed_columns,
            "peak_states": stats.peak_states,
            "runtime_bound": "O(n^2 * 2^rank)",
        }
        unsat_reason = "EXACT_SYNDROME_STATE_EXHAUSTION"
    else:
        engine = NullityBranchSolver(rows, n, data.null_basis)
        parameter = engine.search()
        kernel_word = (
            None if parameter is None else engine.parameter_to_kernel_word(parameter)
        )
        details = {
            "route": "EXACT_AFFINE_2SUBSAT_BRANCH",
            "nodes": engine.stats.nodes,
            "conflicts": engine.stats.conflicts,
            "forced_equations": engine.stats.forced_equations,
            "splits": engine.stats.splits,
            "max_depth": engine.stats.max_depth,
            "runtime_bound": "O*(phi^nullity)",
        }
        unsat_reason = "EXACT_AFFINE_BRANCH_EXHAUSTION"

    common = {
        "n": n,
        "rank_f2": rank,
        "nullity_f2": nullity,
        "target_kernel_weight": target_kernel_weight,
        "details": details,
        "polynomial_runtime": False,
        "p_vs_np": "OPEN",
    }
    if kernel_word is None:
        return {
            "status": "UNSAT",
            "reason": unsat_reason,
            "witness": None,
            **common,
        }

    if kernel_word.bit_count() != target_kernel_weight:
        raise AssertionError("internal target-weight verification failed")
    if any(parity(mask & kernel_word) for mask in masks):
        raise AssertionError("internal kernel verification failed")
    witness = exact_one_witness(rows, n, kernel_word)
    return {
        "status": "SAT",
        "reason": "VERIFIED_EXACT_ONE_WITNESS",
        "witness": witness,
        "kernel_word_hex": hex(kernel_word),
        **common,
    }


def permutation_instance(p: Sequence[int], q: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    n = len(p)
    if sorted(p) != list(range(n)) or sorted(q) != list(range(n)):
        raise ValueError("p and q must be permutations")
    return tuple((i, p[i], q[i]) for i in range(n))


def cubic_edgecolor_bridge(
    vertex_count: int, edges: Sequence[tuple[int, int]]
) -> tuple[int, tuple[tuple[int, int, int], ...]]:
    """Direct gadget-free cubic 3-edge-colouring -> legal SCL."""
    incident = [[] for _ in range(vertex_count)]
    for e, (u, v) in enumerate(edges):
        if u == v:
            raise ValueError("loops are not allowed")
        incident[u].append(e)
        incident[v].append(e)
    if any(len(es) != 3 for es in incident):
        raise ValueError("graph is not cubic")
    if len({tuple(sorted(edge)) for edge in edges}) != len(edges):
        raise ValueError("parallel edges are not allowed")

    def variable(e: int, color: int) -> int:
        return 3 * e + color

    rows: list[tuple[int, int, int]] = []
    for e in range(len(edges)):
        rows.append(tuple(variable(e, color) for color in range(3)))
    for v in range(vertex_count):
        for color in range(3):
            rows.append(tuple(variable(e, color) for e in incident[v]))
    n = 3 * len(edges)
    assert len(rows) == n
    return n, validate_legal(rows, n)


P_SAT = (7, 6, 11, 10, 8, 4, 9, 5, 0, 3, 2, 1)
Q_SAT = (11, 8, 3, 4, 7, 9, 0, 10, 2, 1, 6, 5)
P_UNSAT = (6, 3, 7, 10, 11, 1, 4, 8, 9, 5, 2, 0)
Q_UNSAT = (3, 4, 5, 8, 7, 0, 9, 6, 2, 11, 1, 10)


def controls() -> None:
    sat12 = permutation_instance(P_SAT, Q_SAT)
    unsat12 = permutation_instance(P_UNSAT, Q_UNSAT)

    k4_edges = (
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3), (2, 3),
    )
    k4_n, k4 = cubic_edgecolor_bridge(4, k4_edges)

    petersen_edges = tuple(
        [(i, (i + 1) % 5) for i in range(5)]
        + [(5 + i, 5 + ((i + 2) % 5)) for i in range(5)]
        + [(i, 5 + i) for i in range(5)]
    )
    petersen_n, petersen = cubic_edgecolor_bridge(10, petersen_edges)

    cases = (
        ("SAT12", sat12, 12, "SAT", 10, 2),
        ("UNSAT12", unsat12, 12, "UNSAT", 11, 1),
        ("K4_DIRECT_SCL", k4, k4_n, "SAT", 12, 6),
        ("PETERSEN_DIRECT_SCL", petersen, petersen_n, "UNSAT", 33, 12),
    )
    for name, rows, n, expected, expected_rank, expected_nullity in cases:
        result = solve(rows, n)
        assert result["status"] == expected, (name, result)
        assert result["rank_f2"] == expected_rank
        assert result["nullity_f2"] == expected_nullity
        if result["status"] == "SAT":
            witness = result["witness"]
            assert witness is not None
            assert all(sum(witness[j] for j in row) == 1 for row in rows)
        print(
            f"{name}: {result['status']} rank={expected_rank} "
            f"nullity={expected_nullity} route={result['details']['route']} PASS"
        )

    # Exercise the new rank route explicitly on both opposite-status controls.
    for name, rows, expected in (
        ("SAT12_RANK", sat12, "SAT"),
        ("UNSAT12_RANK", unsat12, "UNSAT"),
    ):
        result = solve(rows, 12, route="rank")
        assert result["status"] == expected
        print(
            f"{name}: {result['status']} "
            f"peak_states={result['details']['peak_states']} PASS"
        )

    balance = LOG2_PHI / (1.0 + LOG2_PHI)
    base = 2.0 ** balance
    assert abs(base - 1.3284698786879974) < 1e-12
    print(f"ALL_INPUT_EXACT_PORTFOLIO_BOUND = O*({base:.6f}^n)")
    print("UNIVERSAL_POLYNOMIAL_RUNTIME = NOT_PROVED")
    print("P_VS_NP = OPEN")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "instance",
        nargs="?",
        help="JSON file with {'n': int, 'rows': [[a,b,c], ...]}",
    )
    parser.add_argument("--route", choices=("auto", "rank", "nullity"), default="auto")
    args = parser.parse_args()

    if args.instance is None:
        controls()
        return
    with open(args.instance, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    result = solve(payload["rows"], payload["n"], route=args.route)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
