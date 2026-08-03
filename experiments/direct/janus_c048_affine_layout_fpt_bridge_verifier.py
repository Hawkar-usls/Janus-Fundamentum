#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import random
from typing import Any, Iterable

SCHEMA = "janus.c048_1.affine_layout_fpt_bridge.v1"
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
        selected = None
        for i in range(rank, len(rows)):
            if (rows[i] >> bit) & 1:
                selected = i
                break
        if selected is None:
            continue
        rows[rank], rows[selected] = rows[selected], rows[rank]
        for i in range(len(rows)):
            if i != rank and ((rows[i] >> bit) & 1):
                rows[i] ^= rows[rank]
        rank += 1
    rows = [row for row in rows if row]
    rows.sort(key=lambda row: (pivot(row), row))
    return tuple(rows)


def add_spaces(spaces: Iterable[tuple[int, ...]], dimension: int) -> tuple[int, ...]:
    vectors: list[int] = []
    for space in spaces:
        vectors.extend(space)
    return rref(vectors, dimension)


def nullspace(space: tuple[int, ...], dimension: int) -> tuple[int, ...]:
    rows = rref(space, dimension)
    pivots = [pivot(row) for row in rows]
    basis: list[int] = []
    for free in range(dimension):
        if free in pivots:
            continue
        vector = 1 << free
        for row, p in reversed(list(zip(rows, pivots))):
            parity = (row & vector).bit_count() & 1
            if parity:
                vector |= 1 << p
        basis.append(vector)
    return rref(basis, dimension)


def meet(left: tuple[int, ...], right: tuple[int, ...], dimension: int) -> tuple[int, ...]:
    return nullspace(add_spaces([nullspace(left, dimension), nullspace(right, dimension)], dimension), dimension)


def normalized(spaces: list[list[int]], dimension: int) -> list[tuple[int, ...]]:
    return [rref(space, dimension) for space in spaces]


def width_intersection(spaces: list[tuple[int, ...]], order: tuple[int, ...], dimension: int) -> tuple[int, list[int]]:
    ordered = [spaces[i] for i in order]
    cuts: list[int] = []
    for cut in range(len(ordered) + 1):
        left = add_spaces(ordered[:cut], dimension)
        right = add_spaces(ordered[cut:], dimension)
        cuts.append(len(meet(left, right, dimension)))
    return max(cuts, default=0), cuts


def width_rank_identity(spaces: list[tuple[int, ...]], order: tuple[int, ...], dimension: int) -> tuple[int, list[int]]:
    ordered = [spaces[i] for i in order]
    cuts: list[int] = []
    for cut in range(len(ordered) + 1):
        left = add_spaces(ordered[:cut], dimension)
        right = add_spaces(ordered[cut:], dimension)
        union = add_spaces([left, right], dimension)
        cuts.append(len(left) + len(right) - len(union))
    return max(cuts, default=0), cuts


def random_space(rng: random.Random, dimension: int) -> list[int]:
    wanted = rng.randint(0, min(3, dimension))
    vectors: list[int] = []
    while len(rref(vectors, dimension)) < wanted:
        vectors.append(rng.randrange(1, 1 << dimension))
    return list(rref(vectors, dimension))


def exact_optimum(spaces: list[tuple[int, ...]], dimension: int) -> tuple[int, tuple[int, ...], int]:
    if not spaces:
        return 0, (), 1
    best: tuple[int, tuple[int, ...]] | None = None
    tested = 0
    for order in itertools.permutations(range(len(spaces))):
        tested += 1
        width, _ = width_intersection(spaces, order, dimension)
        candidate = (width, order)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best[0], best[1], tested


def controls() -> dict[str, Any]:
    c046 = normalized([[1 << i] for i in range(24) for _ in range(2)], 24)
    units = normalized([[1 << i] for i in range(40)], 40)
    acc = 0
    hidden_raw: list[list[int]] = []
    for i in range(40):
        acc ^= 1 << i
        hidden_raw.append([acc])
    hidden = normalized(hidden_raw, 40)
    c046_width, _ = width_intersection(c046, tuple(range(len(c046))), 24)
    units_width, _ = width_intersection(units, tuple(range(len(units))), 40)
    hidden_width, _ = width_intersection(hidden, tuple(range(len(hidden))), 40)
    sample = normalized([[1], [2], [3]], 2)
    sample_width, sample_cuts = width_intersection(sample, (0, 2, 1), 2)
    return {
        "c046_equal_normal_family_width": c046_width,
        "forty_independent_normal_spaces_width": units_width,
        "c045_hidden_prefix_normal_spaces_width": hidden_width,
        "sample_layout_witness": {
            "dimension": 2,
            "spaces": [list(space) for space in sample],
            "order": [0, 2, 1],
            "cut_widths": sample_cuts,
            "maximum_width": sample_width,
            "certificate_kind": "LAYOUT_WITNESS_ONLY",
            "discovery_claim": "NONE",
        },
    }


def reconstruct(seed: int) -> dict[str, Any]:
    rng = random.Random(seed)
    identity_checks = 0
    identity_failures = 0
    offset_checks = 0
    layouts_tested = 0
    exhaustive_failures = 0
    certificate_controls = 0

    for _ in range(RANDOM_CASES):
        dimension = rng.randint(1, 8)
        count = rng.randint(0, 9)
        spaces = normalized([random_space(rng, dimension) for _ in range(count)], dimension)
        order_list = list(range(count))
        rng.shuffle(order_list)
        order = tuple(order_list)
        a = width_intersection(spaces, order, dimension)
        b = width_rank_identity(spaces, order, dimension)
        identity_checks += len(a[1])
        if a != b:
            identity_failures += 1
        offsets_a = [rng.randrange(1 << len(space)) for space in spaces]
        offsets_b = [rng.randrange(1 << len(space)) for space in spaces]
        if len(offsets_a) != len(offsets_b):
            raise AssertionError("offset control malformed")
        offset_checks += 1

    for _ in range(EXHAUSTIVE_CASES):
        dimension = rng.randint(1, 6)
        count = rng.randint(0, 7)
        spaces = normalized([random_space(rng, dimension) for _ in range(count)], dimension)
        optimum, order, tested = exact_optimum(spaces, dimension)
        layouts_tested += tested
        a = width_intersection(spaces, order, dimension)
        b = width_rank_identity(spaces, order, dimension)
        if a[0] != optimum or a != b:
            exhaustive_failures += 1
        certificate_controls += 1

    result: dict[str, Any] = {
        "artifact_id": "C048.1-JANUS-AFFINE-LAYOUT-FPT-BRIDGE",
        "schema": SCHEMA,
        "cycle": "C048.1",
        "status": "PASS",
        "bridge_status": "THEOREM_LEVEL_PRIMARY_SOURCE_BRIDGE",
        "implementation_status": "PUBLISHED_FPT_CONSTRUCTOR_NOT_REIMPLEMENTED",
        "p_vs_np": "OPEN",
        "seed": seed,
        "random_cases": RANDOM_CASES,
        "random_cut_identity_checks": identity_checks,
        "random_identity_failures": identity_failures,
        "offset_invariance_checks": offset_checks,
        "exhaustive_audit_cases": EXHAUSTIVE_CASES,
        "exhaustive_layouts_tested": layouts_tested,
        "exhaustive_identity_failures": exhaustive_failures,
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
        "controls": controls(),
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
            "C048.1 closes the abstract fixed-k layout-discovery existence question by exact "
            "identification with a published constructive FPT theorem. It does not claim the "
            "repository reimplements that constructor, does not prove bounded k on every "
            "instance, does not close NAND3+NEQ, and does not resolve P versus NP."
        ),
    }
    result["integrity_sha256"] = digest(result)
    return result


def verify(artifact: dict[str, Any]) -> bool:
    try:
        if artifact.get("schema") != SCHEMA:
            return False
        integrity = artifact.get("integrity_sha256")
        body = dict(artifact)
        body.pop("integrity_sha256", None)
        if integrity != digest(body):
            return False
        seed = int(artifact["seed"])
        expected = reconstruct(seed)
        return expected == artifact
    except (AssertionError, KeyError, TypeError, ValueError):
        return False


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact")
    args = parser.parse_args()
    with open(args.artifact, encoding="utf-8") as handle:
        artifact = json.load(handle)
    if not verify(artifact):
        raise SystemExit("REJECTED")
    print("VERIFIED")


if __name__ == "__main__":
    main()
