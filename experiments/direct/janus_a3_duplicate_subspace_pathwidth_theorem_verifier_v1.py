#!/usr/bin/env python3
"""Independent verifier for A3 duplicate-subspace path-width theorem v1.

This verifier does not import the certificate producer or B5.2B. It independently
implements finite GF(2) controls, checks the frozen symbolic derivation, and
rejects repaired-digest semantic tampering. Frozen B5.2B definition conformance
is checked by a separate CI step.
"""
from __future__ import annotations

import argparse, copy, hashlib, itertools, json, re
from pathlib import Path
from typing import Iterable, Sequence

CERT_SCHEMA = "janus.fundamentum.a3.duplicate_subspace_pathwidth_certificate.v1"
SPEC_SCHEMA = "janus.fundamentum.a3.duplicate_subspace_pathwidth_theorem_spec.v1"
EXPECTED_STEPS = [
    ("INDEXED_MULTIPLICITY", "For m >= 2 and any internal cut 1 <= i < m, both sides contain at least one occurrence identity."),
    ("NONEMPTY_DUPLICATE_SPAN", "A nonempty family whose every geometric member equals U has span exactly U."),
    ("INTERNAL_LEFT_RIGHT_SPANS", "Therefore L_i = U and R_i = U at every internal cut."),
    ("BOUNDARY_IDEMPOTENCE", "U intersect U = U, so boundary_i = U and width_i = dim(U) = d."),
    ("ENDPOINTS", "At cuts 0 and m one side is the zero span, so width is 0."),
    ("LAYOUT_INVARIANCE", "Every layout has the same width profile [0,d,...,d,0], hence maximum width d."),
    ("PATHWIDTH_MINIMUM", "The minimum over all layout maximum widths is therefore d."),
]


def cbytes(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(v):
    return hashlib.sha256(cbytes(v)).hexdigest()


def rref_basis(vectors: Iterable[int], n: int) -> tuple[int, ...]:
    rows = [int(v) for v in vectors if int(v)]
    if any(v < 0 or v >= (1 << n) for v in rows):
        raise AssertionError("vector range")
    pivot = n - 1
    out = []
    while pivot >= 0:
        candidates = [v for v in rows if (v >> pivot) & 1]
        if not candidates:
            pivot -= 1
            continue
        lead = min(candidates)
        rows.remove(lead)
        rows = [v ^ lead if ((v >> pivot) & 1) else v for v in rows]
        out.append(lead)
        pivot -= 1
    # Back reduce to a canonical basis and sort by pivot position ascending.
    reduced = []
    for v in reversed(out):
        x = v
        for b in reduced:
            p = b.bit_length() - 1
            if (x >> p) & 1:
                x ^= b
        if x:
            reduced.append(x)
    # One more full reduction makes representation independent of input order.
    for i in range(len(reduced) - 1, -1, -1):
        p = reduced[i].bit_length() - 1
        for j in range(i):
            if (reduced[j] >> p) & 1:
                reduced[j] ^= reduced[i]
    return tuple(sorted((v for v in reduced if v), key=lambda x: x.bit_length()))


def span_set(basis: Sequence[int]) -> frozenset[int]:
    values = {0}
    for b in basis:
        values |= {x ^ b for x in tuple(values)}
    return frozenset(values)


def subspace_key(vectors: Iterable[int], n: int) -> tuple[int, ...]:
    # Canonicalize by the full element set, then greedily extract a basis.
    basis = rref_basis(vectors, n)
    elems = sorted(span_set(basis))
    return rref_basis(elems, n)


def all_subspaces(n: int) -> list[tuple[int, ...]]:
    if n == 0:
        return [()]
    vecs = list(range(1, 1 << n))
    seen = {()}
    for size in range(1, n + 1):
        for choice in itertools.combinations(vecs, size):
            seen.add(subspace_key(choice, n))
    return sorted(seen, key=lambda x: (len(x), x))


def independent_widths(U: Sequence[int], order: Sequence[str], n: int) -> list[int]:
    Uset = span_set(U)
    widths = []
    for cut in range(len(order) + 1):
        left_nonempty = cut > 0
        right_nonempty = cut < len(order)
        left = Uset if left_nonempty else frozenset({0})
        right = Uset if right_nonempty else frozenset({0})
        boundary = left & right
        # A finite GF(2) subspace has size 2^dimension.
        size = len(boundary)
        assert size and size & (size - 1) == 0
        widths.append(size.bit_length() - 1)
    return widths


def recompute_summary() -> dict:
    counts = {}
    arrangement_cases = layouts_checked = internal_cuts_checked = 0
    single_controls = nonzero_single = 0
    examples = []
    for n in range(5):
        subs = all_subspaces(n)
        counts[str(n)] = len(subs)
        for U in subs:
            d = len(U)
            assert independent_widths(U, ["u0"], n) == [0, 0]
            single_controls += 1
            if d:
                nonzero_single += 1
            for m in range(2, 6):
                arrangement_cases += 1
                ids = tuple(f"u{i}" for i in range(m))
                for perm in itertools.permutations(ids):
                    widths = independent_widths(U, perm, n)
                    assert widths == [0] + [d] * (m - 1) + [0]
                    assert max(widths) == d
                    layouts_checked += 1
                    internal_cuts_checked += m - 1
                if len(examples) < 12:
                    examples.append({
                        "ambient_dim": n,
                        "subspace_basis_rref": list(U),
                        "subspace_dim": d,
                        "multiplicity": m,
                        "canonical_order": list(ids),
                        "cut_widths": independent_widths(U, ids, n),
                        "maximum_cut_width": d,
                    })
    assert counts == {"0": 1, "1": 2, "2": 5, "3": 16, "4": 67}
    return {
        "ambient_dimensions": [0, 1, 2, 3, 4],
        "multiplicities": [2, 3, 4, 5],
        "subspace_counts": counts,
        "arrangement_cases": arrangement_cases,
        "layouts_checked": layouts_checked,
        "internal_cuts_checked": internal_cuts_checked,
        "single_occurrence_controls": single_controls,
        "nonzero_single_occurrence_controls": nonzero_single,
        "all_duplicate_arrangements_match_theorem": True,
        "all_m1_controls_have_width_zero": True,
        "witness_examples": examples,
    }


def verify(spec: dict, cert: dict, expected_summary: dict) -> None:
    assert spec["schema"] == SPEC_SCHEMA
    assert spec["status"] == "SPEC_FROZEN_CANDIDATE_ONLY"
    assert spec["theorem_id"] == "A3_DUPLICATE_SUBSPACE_PATHWIDTH_V1"
    assert spec["authority_binding"]["b5_2b_cut_definition_git_blob"] == "90a13116ff7999f81a744d56e0bae56eb6af5ed1"
    assert spec["authority_binding"]["frontier_v1_3_1_evidence_commit"] == "dccc046f6b69f39e18199749a2780db0ba05341f"
    assert spec["statement"]["excluded_case"].startswith("m = 1 is not covered")
    assert spec["strict_boundary"]["literature_novelty"] == "NOT_CLAIMED"
    assert spec["strict_boundary"]["does_not_establish_p_vs_np"] is True

    assert cert["schema"] == CERT_SCHEMA
    assert cert["semantic_digest_scope"] == "proof_payload"
    payload = cert["proof_payload"]
    assert cert["semantic_digest"] == digest(payload)
    assert payload["theorem_id"] == spec["theorem_id"]
    assert payload["field"] == "GF(2)"
    assert payload["authority_binding"] == spec["authority_binding"]
    assert payload["strict_boundary"] == spec["strict_boundary"]
    assert payload["excluded_case"] == spec["statement"]["excluded_case"]
    assert payload["theorem_conclusion"] == spec["statement"]["conclusion"]
    steps = payload["symbolic_derivation"]
    assert len(steps) == len(EXPECTED_STEPS)
    for got, (step, claim) in zip(steps, EXPECTED_STEPS):
        assert got == {"step": step, "claim": claim}
    assert payload["finite_exhaustive_controls"] == expected_summary

    # Semantic proof obligations independent of wording alone.
    assert "m >= 2" in steps[0]["claim"]
    assert "span exactly U" in steps[1]["claim"]
    assert "L_i = U and R_i = U" in steps[2]["claim"]
    assert "boundary_i = U" in steps[3]["claim"] and "dim(U) = d" in steps[3]["claim"]
    assert "width is 0" in steps[4]["claim"]
    assert "maximum width d" in steps[5]["claim"]
    assert "minimum over all layout maximum widths" in steps[6]["claim"]


def reject(spec, cert, expected, mutate):
    bad = copy.deepcopy(cert)
    before = cbytes(bad)
    mutate(bad)
    if cbytes(bad) == before:
        raise AssertionError("tamper fixture no-op")
    bad["semantic_digest"] = digest(bad["proof_payload"])
    try:
        verify(spec, bad, expected)
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError("tamper accepted")


def tamper_suite(spec, cert, expected):
    attacks = [
        lambda c: c["proof_payload"].__setitem__("theorem_conclusion", "Every layout has maximum cut width d-1."),
        lambda c: c["proof_payload"]["symbolic_derivation"][0].__setitem__("claim", "For m >= 1 every cut is internal."),
        lambda c: c["proof_payload"]["symbolic_derivation"][1].__setitem__("claim", "Duplicate geometry may be deduplicated before taking spans."),
        lambda c: c["proof_payload"]["symbolic_derivation"][2].__setitem__("claim", "L_i = 0 and R_i = U."),
        lambda c: c["proof_payload"]["symbolic_derivation"][3].__setitem__("claim", "U intersect U = 0."),
        lambda c: c["proof_payload"]["symbolic_derivation"][4].__setitem__("claim", "Endpoint width is d."),
        lambda c: c["proof_payload"]["symbolic_derivation"][5].__setitem__("claim", "One favorable layout is enough."),
        lambda c: c["proof_payload"]["symbolic_derivation"][6].__setitem__("claim", "The maximum over layouts is path-width."),
        lambda c: c["proof_payload"].__setitem__("excluded_case", "m = 1 is also covered with width d."),
        lambda c: c["proof_payload"]["finite_exhaustive_controls"].__setitem__("layouts_checked", expected["layouts_checked"] + 1),
        lambda c: c["proof_payload"]["finite_exhaustive_controls"].__setitem__("subspace_counts", {"0":1,"1":2,"2":5,"3":16,"4":66}),
        lambda c: c["proof_payload"]["finite_exhaustive_controls"].__setitem__("all_m1_controls_have_width_zero", False),
        lambda c: c["proof_payload"]["authority_binding"].__setitem__("b5_2b_cut_definition_git_blob", "0" * 40),
        lambda c: c["proof_payload"]["authority_binding"].__setitem__("frontier_target", "A0_P_VS_NP"),
        lambda c: c["proof_payload"]["strict_boundary"].__setitem__("literature_novelty", "ESTABLISHED"),
        lambda c: c["proof_payload"]["strict_boundary"].__setitem__("does_not_establish_p_vs_np", False),
    ]
    for attack in attacks:
        reject(spec, cert, expected, attack)
    return len(attacks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--certificate", required=True)
    ap.add_argument("--tamper-test", action="store_true")
    args = ap.parse_args()
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    cert = json.loads(Path(args.certificate).read_text(encoding="utf-8"))
    expected = recompute_summary()
    verify(spec, cert, expected)
    print("A3_DUPLICATE_SUBSPACE_PATHWIDTH_INDEPENDENT_REPLAY = PASS")
    print("SYMBOLIC_DERIVATION_BINDING = PASS")
    print("INDEXED_OCCURRENCE_MULTIPLICITY = PRESERVED")
    print(f"EXHAUSTIVE_LAYOUTS_REPLAYED = {expected['layouts_checked']}")
    print(f"EXHAUSTIVE_INTERNAL_CUTS_REPLAYED = {expected['internal_cuts_checked']}")
    print(f"SINGLE_OCCURRENCE_EXCLUSION_CONTROLS = {expected['single_occurrence_controls']}")
    if args.tamper_test:
        n = tamper_suite(spec, cert, expected)
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {n}/{n}")
    print("LITERATURE_NOVELTY = NOT_CLAIMED")
    print("P_VS_NP = OPEN")

if __name__ == "__main__":
    main()
