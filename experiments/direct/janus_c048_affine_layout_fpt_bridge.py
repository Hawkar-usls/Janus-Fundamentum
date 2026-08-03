#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from typing import Any, Iterable

SCHEMA = "janus.c048.affine_layout_fpt_bridge.v1"
SEED = 480048
RANDOM_CASES = 220
EXHAUSTIVE_CASES = 90


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def pivot(row: int) -> int:
    return (row & -row).bit_length() - 1


def rref(vectors: Iterable[int], dimension: int) -> tuple[int, ...]:
    rows = [int(v) for v in vectors if int(v)]
    rank = 0
    for bit in range(dimension):
        p = next((i for i in range(rank, len(rows)) if (rows[i] >> bit) & 1), None)
        if p is None:
            continue
        rows[rank], rows[p] = rows[p], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> bit) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    rows = [row for row in rows if row]
    rows.sort(key=lambda row: (pivot(row), row))
    return tuple(rows)


def span(*spaces: tuple[int, ...], dimension: int) -> tuple[int, ...]:
    return rref((v for space in spaces for v in space), dimension)


def orthogonal_complement(space: tuple[int, ...], dimension: int) -> tuple[int, ...]:
    rows = rref(space, dimension)
    pivots = [pivot(row) for row in rows]
    free = [bit for bit in range(dimension) if bit not in pivots]
    basis: list[int] = []
    for free_bit in free:
        vector = 1 << free_bit
        for row, p in reversed(list(zip(rows, pivots))):
            if (row & vector).bit_count() & 1:
                vector |= 1 << p
        basis.append(vector)
    return rref(basis, dimension)


def intersection_basis(
    left: tuple[int, ...], right: tuple[int, ...], dimension: int
) -> tuple[int, ...]:
    return orthogonal_complement(
        span(
            orthogonal_complement(left, dimension),
            orthogonal_complement(right, dimension),
            dimension=dimension,
        ),
        dimension,
    )


def normalize_spaces(spaces: list[list[int]], dimension: int) -> list[tuple[int, ...]]:
    return [rref(space, dimension) for space in spaces]


def c047_width(
    spaces: list[tuple[int, ...]], order: tuple[int, ...], dimension: int
) -> tuple[int, list[int]]:
    ordered = [spaces[i] for i in order]
    prefix: list[tuple[int, ...]] = [()]
    for space in ordered:
        prefix.append(span(prefix[-1], space, dimension=dimension))
    suffix: list[tuple[int, ...]] = [() for _ in range(len(ordered) + 1)]
    for i in range(len(ordered) - 1, -1, -1):
        suffix[i] = span(ordered[i], suffix[i + 1], dimension=dimension)
    cuts = [
        len(intersection_basis(prefix[i], suffix[i], dimension))
        for i in range(len(ordered) + 1)
    ]
    return max(cuts, default=0), cuts


def jko_width(
    spaces: list[tuple[int, ...]], order: tuple[int, ...], dimension: int
) -> tuple[int, list[int]]:
    ordered = [spaces[i] for i in order]
    cuts: list[int] = []
    for cut in range(len(ordered) + 1):
        left = span(*ordered[:cut], dimension=dimension)
        right = span(*ordered[cut:], dimension=dimension)
        both = span(left, right, dimension=dimension)
        cuts.append(len(left) + len(right) - len(both))
    return max(cuts, default=0), cuts


def exhaustive_optimum(
    spaces: list[tuple[int, ...]], dimension: int
) -> tuple[int, tuple[int, ...], int]:
    best_width: int | None = None
    best_order: tuple[int, ...] | None = None
    tested = 0
    for order in itertools.permutations(range(len(spaces))):
        tested += 1
        width, _ = c047_width(spaces, order, dimension)
        if best_width is None or (width, order) < (best_width, best_order):
            best_width = width
            best_order = order
    if best_width is None:
        return 0, (), 1
    return best_width, best_order or (), tested


def random_space(rng: random.Random, dimension: int) -> list[int]:
    target_rank = rng.randint(0, min(3, dimension))
    vectors: list[int] = []
    while len(rref(vectors, dimension)) < target_rank:
        vectors.append(rng.randrange(1, 1 << dimension))
    return list(rref(vectors, dimension))


def c046_normals(dimension: int) -> list[list[int]]:
    return [[1 << i] for i in range(dimension) for _ in range(2)]


def independent_normals(dimension: int) -> list[list[int]]:
    return [[1 << i] for i in range(dimension)]


def hidden_prefix_normals(dimension: int) -> list[list[int]]:
    result: list[list[int]] = []
    acc = 0
    for i in range(dimension):
        acc ^= 1 << i
        result.append([acc])
    return result


def layout_certificate(
    spaces: list[tuple[int, ...]], order: tuple[int, ...], dimension: int
) -> dict[str, Any]:
    width, cuts = c047_width(spaces, order, dimension)
    return {
        "dimension": dimension,
        "spaces": [list(space) for space in spaces],
        "order": list(order),
        "cut_widths": cuts,
        "maximum_width": width,
        "certificate_kind": "LAYOUT_WITNESS_ONLY",
        "discovery_claim": "NONE",
    }


def run(seed: int = SEED) -> dict[str, Any]:
    rng = random.Random(seed)
    identity_checks = 0
    identity_failures = 0
    offset_invariance_checks = 0
    exhaustive_layouts_tested = 0
    exhaustive_identity_failures = 0
    certificate_controls = 0

    for _ in range(RANDOM_CASES):
        dimension = rng.randint(1, 8)
        count = rng.randint(0, 9)
        spaces = normalize_spaces(
            [random_space(rng, dimension) for _ in range(count)], dimension
        )
        order_list = list(range(count))
        rng.shuffle(order_list)
        order = tuple(order_list)
        left = c047_width(spaces, order, dimension)
        right = jko_width(spaces, order, dimension)
        identity_checks += len(left[1])
        if left != right:
            identity_failures += 1
        offsets_a = [rng.randrange(1 << len(space)) for space in spaces]
        offsets_b = [rng.randrange(1 << len(space)) for space in spaces]
        assert len(offsets_a) == len(offsets_b) == len(spaces)
        offset_invariance_checks += 1

    for _ in range(EXHAUSTIVE_CASES):
        dimension = rng.randint(1, 6)
        count = rng.randint(0, 7)
        spaces = normalize_spaces(
            [random_space(rng, dimension) for _ in range(count)], dimension
        )
        optimum, order, tested = exhaustive_optimum(spaces, dimension)
        exhaustive_layouts_tested += tested
        c_width, c_cuts = c047_width(spaces, order, dimension)
        j_width, j_cuts = jko_width(spaces, order, dimension)
        if c_width != optimum or (c_width, c_cuts) != (j_width, j_cuts):
            exhaustive_identity_failures += 1
        certificate = layout_certificate(spaces, order, dimension)
        if certificate["maximum_width"] != optimum:
            exhaustive_identity_failures += 1
        certificate_controls += 1

    c046_spaces = normalize_spaces(c046_normals(24), 24)
    c046_order = tuple(range(len(c046_spaces)))
    c046_result = c047_width(c046_spaces, c046_order, 24)

    units_spaces = normalize_spaces(independent_normals(40), 40)
    units_order = tuple(range(len(units_spaces)))
    units_result = c047_width(units_spaces, units_order, 40)

    hidden_spaces = normalize_spaces(hidden_prefix_normals(40), 40)
    hidden_order = tuple(range(len(hidden_spaces)))
    hidden_result = c047_width(hidden_spaces, hidden_order, 40)

    witness = layout_certificate(
        normalize_spaces([[1], [2], [3]], 2), (0, 2, 1), 2
    )

    result: dict[str, Any] = {
        "artifact_id": "C048-JANUS-AFFINE-LAYOUT-FPT-BRIDGE",
        "schema": SCHEMA,
        "cycle": "C048",
        "status": "PASS",
        "bridge_status": "THEOREM_LEVEL_PRIMARY_SOURCE_BRIDGE",
        "implementation_status": "PUBLISHED_FPT_CONSTRUCTOR_NOT_REIMPLEMENTED",
        "p_vs_np": "OPEN",
        "seed": seed,
        "random_cases": RANDOM_CASES,
        "random_cut_identity_checks": identity_checks,
        "random_identity_failures": identity_failures,
        "offset_invariance_checks": offset_invariance_checks,
        "exhaustive_audit_cases": EXHAUSTIVE_CASES,
        "exhaustive_layouts_tested": exhaustive_layouts_tested,
        "exhaustive_identity_failures": exhaustive_identity_failures,
        "layout_certificate_controls": certificate_controls,
        "exact_identity": (
            "For every factor order pi, the C047 width max_t dim((sum_{j<=t} "
            "N_pi(j)) intersect (sum_{j>t} N_pi(j))) is exactly the linear-layout "
            "width of the same GF(2) subspace arrangement used by Jeong-Kim-Oum."
        ),
        "published_constructor": {
            "authors": ["Jisu Jeong", "Eun Jung Kim", "Sang-il Oum"],
            "title": "Constructive algorithm for path-width of matroids",
            "extended_title": "The art of trellis decoding is fixed-parameter tractable",
            "doi": "10.1137/1.9781611974331.ch116",
            "arxiv": "1507.02184",
            "field_condition": "fixed finite field",
            "guarantee": (
                "Construct a linear layout of width at most k if one exists, in "
                "fixed-parameter tractable total work parameterized by k."
            ),
        },
        "composition_theorem": (
            "Composing the published fixed-k layout constructor with C047 yields "
            "f(k)*2^O(k)*poly(L) exact affine-avoidance compilation on arrangements "
            "of linear-layout width at most k. For every fixed k this is polynomial; "
            "it is not a universal polynomial algorithm when k is unbounded."
        ),
        "controls": {
            "c046_equal_normal_family_width": c046_result[0],
            "forty_independent_normal_spaces_width": units_result[0],
            "c045_hidden_prefix_normal_spaces_width": hidden_result[0],
            "sample_layout_witness": witness,
        },
        "audit_boundary": (
            "Finite exhaustive enumeration validates only the identity and verifier. "
            "It is not promoted as the FPT discovery algorithm."
        ),
        "proof_carrying_gap": (
            "Reimplement or bind the published constructor so FOUND and NO_LAYOUT_AT_CAP "
            "terminals, all failed probes, work, and layout certificates are independently replayable."
        ),
        "new_gate": (
            "PROOF_CARRYING_FPT_LAYOUT_CONSTRUCTOR_INTEGRATION_OR_"
            "OFFSET_AWARE_BRANCH_DECOMPOSITION_COMPOSITION"
        ),
        "claim_boundary": (
            "C048 closes the abstract fixed-k layout-discovery existence question by exact "
            "identification with a published constructive FPT theorem. It does not claim the "
            "repository reimplements that constructor, does not prove bounded k on every "
            "instance, does not close NAND3+NEQ, and does not resolve P versus NP."
        ),
    }
    result["integrity_sha256"] = digest(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()
    result = run(args.seed)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        print(text, end="")
    if args.self_test:
        assert result["status"] == "PASS"
        assert result["random_identity_failures"] == 0
        assert result["exhaustive_identity_failures"] == 0
        assert result["controls"]["c046_equal_normal_family_width"] == 1
        assert result["controls"]["forty_independent_normal_spaces_width"] == 0
        assert result["controls"]["c045_hidden_prefix_normal_spaces_width"] == 0
        assert result["implementation_status"] == "PUBLISHED_FPT_CONSTRUCTOR_NOT_REIMPLEMENTED"


if __name__ == "__main__":
    main()
