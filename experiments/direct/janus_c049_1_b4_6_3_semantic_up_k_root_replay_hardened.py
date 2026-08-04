#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Iterable

import janus_c049_1_b4_6_3_independent_semantic_up_k_root_replay as base

SCHEMA = "C049.1-B4.6.3-SEMANTIC-UP-K-ROOT-REPLAY-HARDENED-v1"
TERMINAL = "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def canonical_rref(rows: Iterable[int], dim: int) -> tuple[int, ...]:
    limit = 1 << dim
    table: dict[int, int] = {}
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError("vector outside ambient space")
        while x:
            pivot = x.bit_length() - 1
            if pivot in table:
                x ^= table[pivot]
                continue
            table[pivot] = x
            for other, row in list(table.items()):
                if other != pivot and ((row >> pivot) & 1):
                    table[other] = row ^ x
            break
    # The second pass is mandatory. Without it, inserting a lower pivot before
    # a higher pivot leaves an order-dependent representation, e.g.
    # rref((1,3),2)=(3,1) while rref((3,1),2)=(2,1).
    for pivot in sorted(table):
        row = table[pivot]
        for other in sorted(table, reverse=True):
            if other != pivot and ((table[other] >> pivot) & 1):
                table[other] ^= row
    return tuple(table[pivot] for pivot in sorted(table, reverse=True))


def legacy_rref(rows: Iterable[int], dim: int) -> tuple[int, ...]:
    limit = 1 << dim
    table: dict[int, int] = {}
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError("vector outside ambient space")
        while x:
            pivot = x.bit_length() - 1
            if pivot in table:
                x ^= table[pivot]
            else:
                table[pivot] = x
                for other, row in list(table.items()):
                    if other != pivot and ((row >> pivot) & 1):
                        table[other] = row ^ x
                break
    return tuple(table[pivot] for pivot in sorted(table, reverse=True))


def basis_hardening_audit() -> dict:
    legacy_left = legacy_rref((1, 3), 2)
    legacy_right = legacy_rref((3, 1), 2)
    if legacy_left == legacy_right:
        raise AssertionError("legacy order-dependence control no longer reproduces")
    if canonical_rref((1, 3), 2) != canonical_rref((3, 1), 2):
        raise AssertionError("canonical RREF still depends on row order")
    if canonical_rref((1, 3), 2) != (2, 1):
        raise AssertionError("dimension-two canonical basis drift")

    permutation_cases = 0
    for length in range(4):
        for rows in itertools.product(range(4), repeat=length):
            expected = canonical_rref(rows, 2)
            for permutation in set(itertools.permutations(rows)):
                permutation_cases += 1
                if canonical_rref(permutation, 2) != expected:
                    raise AssertionError("RREF permutation confluence failure")

    original = base.rref
    base.rref = canonical_rref
    try:
        dimension_two_subspaces = base.subspaces(2)
    finally:
        base.rref = original
    if len(dimension_two_subspaces) != 5:
        raise AssertionError("GF(2)^2 must have exactly five subspaces")

    return {
        "legacy_order_dependence_reproduced": True,
        "legacy_left": list(legacy_left),
        "legacy_right": list(legacy_right),
        "canonical_basis": list(canonical_rref((1, 3), 2)),
        "permutation_cases": permutation_cases,
        "dimension_two_subspace_count": len(dimension_two_subspaces),
        "dimension_two_subspaces": [list(item) for item in dimension_two_subspaces],
        "failures": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cycle_dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    audit = basis_hardening_audit()
    base.rref = canonical_rref
    rounds = [base.replay_round(path) for path in sorted(args.cycle_dir.glob("round-*"))]
    artifact = {
        "schema": SCHEMA,
        "source_cycle_artifact": json.loads(
            (args.cycle_dir / "artifact.json").read_text()
        )["manifest_digest"],
        "basis_hardening": audit,
        "rounds": rounds,
        "all_rounds_semantically_replayed": all(
            item["semantic_up_k_replay_complete"] for item in rounds
        ),
        "coverage_boundary": {
            "positive_cycle_boundary_dimensions": [0, 1],
            "dimension_two_basis_semantics_tested": True,
            "dimension_two_full_up_k_closure_replayed": False,
            "negative_root_engine_replay": "OPEN",
        },
        "strict_boundary": {
            "inventory_completeness": True,
            "semantic_up_k_replay_positive_cycle": True,
            "semantic_up_k_rref_hardened": True,
            "terminal_completeness_proved": False,
            "found_layout_enabled": False,
            "no_layout_at_cap_enabled": False,
            "current_global_terminal": TERMINAL,
            "p_vs_np": "OPEN",
        },
    }
    artifact["semantic_digest"] = digest(artifact)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print("JANUS_C049_1_B4_6_3_SEMANTIC_UP_K_HARDENED = PASS")
    print("RREF_PERMUTATION_CASES =", audit["permutation_cases"])
    print("GF2_DIM2_SUBSPACES =", audit["dimension_two_subspace_count"])
    print("NEGATIVE_ROOT_ENGINE_REPLAY = OPEN")
    print("TERMINAL =", TERMINAL)


if __name__ == "__main__":
    main()
