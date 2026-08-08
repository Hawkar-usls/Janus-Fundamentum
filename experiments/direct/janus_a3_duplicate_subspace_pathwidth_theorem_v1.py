#!/usr/bin/env python3
"""Certificate producer for A3 duplicate-subspace path-width theorem v1.

The mathematical theorem is symbolic and general. Finite exhaustive controls
cover every subspace of GF(2)^n for n <= 4, multiplicities 2..5, and every
permutation of indexed occurrence identities. The certificate does not claim
literature novelty or any complexity-class separation.
"""
from __future__ import annotations

import argparse, hashlib, itertools, json
from pathlib import Path
from typing import Iterable, Sequence

SCHEMA = "janus.fundamentum.a3.duplicate_subspace_pathwidth_certificate.v1"
SPEC_SCHEMA = "janus.fundamentum.a3.duplicate_subspace_pathwidth_theorem_spec.v1"


def cbytes(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(v):
    return hashlib.sha256(cbytes(v)).hexdigest()


def xor_basis(rows: Iterable[int], n: int) -> tuple[int, ...]:
    basis = [0] * n
    for value in rows:
        x = int(value)
        if x < 0 or x >= (1 << n):
            raise AssertionError("vector outside ambient space")
        while x:
            p = x.bit_length() - 1
            if basis[p]:
                x ^= basis[p]
            else:
                basis[p] = x
                for q in range(p):
                    if basis[q] and ((basis[p] >> q) & 1):
                        basis[p] ^= basis[q]
                for q in range(p + 1, n):
                    if basis[q] and ((basis[q] >> p) & 1):
                        basis[q] ^= basis[p]
                break
    return tuple(v for v in basis if v)


def span_elements(basis: Sequence[int]) -> frozenset[int]:
    out = {0}
    for v in basis:
        out |= {x ^ v for x in tuple(out)}
    return frozenset(out)


def intersection_basis(a: Sequence[int], b: Sequence[int], n: int) -> tuple[int, ...]:
    common = span_elements(a) & span_elements(b)
    return xor_basis(sorted(common), n)


def enumerate_subspaces(n: int) -> list[tuple[int, ...]]:
    if n == 0:
        return [()]
    nonzero = list(range(1, 1 << n))
    seen = {()}
    for r in range(1, n + 1):
        for rows in itertools.combinations(nonzero, r):
            seen.add(xor_basis(rows, n))
    return sorted(seen, key=lambda b: (len(b), b))


def exact_cut_widths(normal_space: Sequence[int], order: Sequence[str], n: int) -> list[int]:
    by_id = {occ: tuple(normal_space) for occ in order}
    widths = []
    for cut in range(len(order) + 1):
        left = xor_basis((v for occ in order[:cut] for v in by_id[occ]), n)
        right = xor_basis((v for occ in order[cut:] for v in by_id[occ]), n)
        boundary = intersection_basis(left, right, n)
        widths.append(len(boundary))
    return widths


def exhaustive_summary() -> dict:
    subspace_counts = {}
    arrangement_cases = 0
    layouts_checked = 0
    internal_cuts_checked = 0
    single_occurrence_controls = 0
    nonzero_single_occurrence_controls = 0
    witness_examples = []

    for n in range(5):
        subs = enumerate_subspaces(n)
        subspace_counts[str(n)] = len(subs)
        for basis in subs:
            d = len(basis)
            single = exact_cut_widths(basis, ["u0"], n)
            assert single == [0, 0]
            single_occurrence_controls += 1
            if d > 0:
                nonzero_single_occurrence_controls += 1

            for m in range(2, 6):
                arrangement_cases += 1
                ids = tuple(f"u{i}" for i in range(m))
                for order in itertools.permutations(ids):
                    widths = exact_cut_widths(basis, order, n)
                    assert widths[0] == 0 and widths[-1] == 0
                    assert widths[1:-1] == [d] * (m - 1)
                    assert max(widths) == d
                    layouts_checked += 1
                    internal_cuts_checked += m - 1
                if len(witness_examples) < 12:
                    witness_examples.append({
                        "ambient_dim": n,
                        "subspace_basis_rref": list(basis),
                        "subspace_dim": d,
                        "multiplicity": m,
                        "canonical_order": list(ids),
                        "cut_widths": exact_cut_widths(basis, ids, n),
                        "maximum_cut_width": d,
                    })

    assert subspace_counts == {"0": 1, "1": 2, "2": 5, "3": 16, "4": 67}
    return {
        "ambient_dimensions": [0, 1, 2, 3, 4],
        "multiplicities": [2, 3, 4, 5],
        "subspace_counts": subspace_counts,
        "arrangement_cases": arrangement_cases,
        "layouts_checked": layouts_checked,
        "internal_cuts_checked": internal_cuts_checked,
        "single_occurrence_controls": single_occurrence_controls,
        "nonzero_single_occurrence_controls": nonzero_single_occurrence_controls,
        "all_duplicate_arrangements_match_theorem": True,
        "all_m1_controls_have_width_zero": True,
        "witness_examples": witness_examples,
    }


def build(spec: dict) -> dict:
    assert spec["schema"] == SPEC_SCHEMA
    assert spec["status"] == "SPEC_FROZEN_CANDIDATE_ONLY"
    statement = spec["statement"]
    proof = {
        "theorem_id": spec["theorem_id"],
        "field": "GF(2)",
        "symbolic_derivation": [
            {
                "step": "INDEXED_MULTIPLICITY",
                "claim": "For m >= 2 and any internal cut 1 <= i < m, both sides contain at least one occurrence identity.",
            },
            {
                "step": "NONEMPTY_DUPLICATE_SPAN",
                "claim": "A nonempty family whose every geometric member equals U has span exactly U.",
            },
            {
                "step": "INTERNAL_LEFT_RIGHT_SPANS",
                "claim": "Therefore L_i = U and R_i = U at every internal cut.",
            },
            {
                "step": "BOUNDARY_IDEMPOTENCE",
                "claim": "U intersect U = U, so boundary_i = U and width_i = dim(U) = d.",
            },
            {
                "step": "ENDPOINTS",
                "claim": "At cuts 0 and m one side is the zero span, so width is 0.",
            },
            {
                "step": "LAYOUT_INVARIANCE",
                "claim": "Every layout has the same width profile [0,d,...,d,0], hence maximum width d.",
            },
            {
                "step": "PATHWIDTH_MINIMUM",
                "claim": "The minimum over all layout maximum widths is therefore d.",
            },
        ],
        "excluded_case": statement["excluded_case"],
        "theorem_conclusion": statement["conclusion"],
        "finite_exhaustive_controls": exhaustive_summary(),
        "authority_binding": spec["authority_binding"],
        "strict_boundary": spec["strict_boundary"],
    }
    cert = {
        "schema": SCHEMA,
        "semantic_digest_scope": "proof_payload",
        "proof_payload": proof,
    }
    cert["semantic_digest"] = digest(proof)
    return cert


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", default="research_targets/A3_DUPLICATE_SUBSPACE_PATHWIDTH_THEOREM_SPEC_V1.json")
    ap.add_argument("--output", default="artifacts/a3_duplicate_subspace_pathwidth_theorem_v1.json")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    cert = build(spec)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(cert, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    s = cert["proof_payload"]["finite_exhaustive_controls"]
    print("A3_DUPLICATE_SUBSPACE_PATHWIDTH_SYMBOLIC_DERIVATION = BUILT")
    print(f"SUBSPACE_COUNTS = {s['subspace_counts']}")
    print(f"ARRANGEMENT_CASES = {s['arrangement_cases']}")
    print(f"LAYOUTS_CHECKED = {s['layouts_checked']}")
    print(f"INTERNAL_CUTS_CHECKED = {s['internal_cuts_checked']}")
    print(f"SINGLE_OCCURRENCE_CONTROLS = {s['single_occurrence_controls']}")
    print(f"CERTIFICATE_SEMANTIC_DIGEST = {cert['semantic_digest']}")
    print("THEOREM_STATUS = CANDIDATE_PENDING_INDEPENDENT_REPLAY_AND_REVIEW")

if __name__ == "__main__":
    main()
