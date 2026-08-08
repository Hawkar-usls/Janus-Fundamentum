from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import janus_c049_1_b5_iterative_compression_preprocessing_binding as base


def canonical_rref(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    limit = 1 << dimension
    work = [int(x) for x in rows]
    if any(x < 0 or x >= limit for x in work):
        raise ValueError("vector outside ambient space")
    result: list[int] = []
    for bit in range(dimension - 1, -1, -1):
        pivot_index = next((i for i, value in enumerate(work) if (value >> bit) & 1), None)
        if pivot_index is None:
            continue
        pivot = work.pop(pivot_index)
        work = [value ^ pivot if ((value >> bit) & 1) else value for value in work]
        result = [value ^ pivot if ((value >> bit) & 1) else value for value in result]
        result.append(pivot)
    return tuple(sorted((x for x in result if x), reverse=True))


def build(spec: dict, raw: dict) -> dict:
    old = base.xor_basis
    base.xor_basis = canonical_rref
    try:
        return base.build(spec, raw)
    finally:
        base.xor_basis = old


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    artifact = build(base.load(args.spec), base.load(args.input))
    args.output.write_bytes(base.cb(artifact) + b"\n")
    p = artifact["proof_payload"]
    print("JANUS_B5_ITERATIVE_COMPRESSION_PREPROCESSING_BINDING_V1_1 = PASS")
    print("CANONICAL_BASIS_NORMAL_FORM = FULL_RREF")
    print("PREPROCESSING_BRANCH =", p["preprocessing_branch"])
    print("FACTOR_OCCURRENCES =", len(p["original_catalog"]))
    print("THETA_2K =", p["theta"])
    print("OBSTRUCTION_OCCURRENCES =", len(p["obstruction_occurrence_indices"]))
    print("ORIGINAL_CATALOG_SEMANTIC_DIGEST =", p["original_catalog_semantic_digest"])
    print("DISCOVERY_CATALOG_SEMANTIC_DIGEST =", p["discovery_catalog_semantic_digest"])
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("C049_1_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
