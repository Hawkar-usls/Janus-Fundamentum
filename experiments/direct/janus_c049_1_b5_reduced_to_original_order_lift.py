from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "janus.c049_1.b5.reduced_to_original_order_lift_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.reduced_to_original_order_lift_spec.v1"
PREP_SCHEMA = "janus.c049_1.b5.iterative_compression_preprocessing_binding_candidate.v1"
B51_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"
B52A_SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier.v1_1"
B52B_SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(value: Any, path: Path) -> None:
    path.write_bytes(cb(value) + b"\n")


def id_key(value: Any) -> str:
    return cb(value).decode("utf-8")


def rref(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    limit = 1 << dimension
    for raw in rows:
        x = int(raw)
        if x < 0 or x >= limit:
            raise ValueError("vector outside ambient space")
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                for q, y in list(pivots.items()):
                    if q != p and ((y >> p) & 1):
                        pivots[q] = y ^ x
                break
    return tuple(pivots[p] for p in sorted(pivots, reverse=True))


def reduce_mod(vector: int, basis: tuple[int, ...]) -> int:
    x = int(vector)
    for b in basis:
        p = b.bit_length() - 1
        if p >= 0 and ((x >> p) & 1):
            x ^= b
    return x


def intersection(left_rows: Iterable[int], right_rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    left = rref(left_rows, dimension)
    right = rref(right_rows, dimension)
    relations: dict[int, tuple[int, int]] = {}
    kernels: list[int] = []
    for index, source in enumerate(left):
        rem = reduce_mod(source, right)
        combo = 1 << index
        while rem:
            p = rem.bit_length() - 1
            if p not in relations:
                relations[p] = (rem, combo)
                break
            old_rem, old_combo = relations[p]
            rem ^= old_rem
            combo ^= old_combo
        if rem == 0:
            kernels.append(combo)
    vectors = []
    for combo in kernels:
        value = 0
        for index, source in enumerate(left):
            if (combo >> index) & 1:
                value ^= source
        vectors.append(value)
    return rref(vectors, dimension)


def canonical_original_raw(raw: dict, dimension: int) -> list[dict]:
    factors = raw.get("factors")
    if not isinstance(factors, list):
        raise AssertionError("original factors")
    out = []
    seen = set()
    for presentation_index, item in enumerate(factors):
        key = id_key(item["id"])
        if key in seen:
            raise AssertionError("duplicate original factor id")
        seen.add(key)
        out.append({
            "factor_id": copy.deepcopy(item["id"]),
            "presentation_index": presentation_index,
            "normal_space": list(rref(item.get("normal_space", []), dimension)),
            "affine_offset": copy.deepcopy(item.get("affine_offset")),
        })
    out.sort(key=lambda x: id_key(x["factor_id"]))
    for i, item in enumerate(out):
        item["occurrence_index"] = i
    return out


def canonical_discovery_input(raw: dict, dimension: int) -> list[dict]:
    factors = raw.get("factors")
    if not isinstance(factors, list):
        raise AssertionError("discovery factors")
    out = []
    seen = set()
    for item in factors:
        key = id_key(item["id"])
        if key in seen:
            raise AssertionError("duplicate discovery factor id")
        seen.add(key)
        out.append({
            "factor_id": copy.deepcopy(item["id"]),
            "normal_space": list(rref(item.get("normal_space", []), dimension)),
            "affine_offset": copy.deepcopy(item.get("affine_offset")),
        })
    out.sort(key=lambda x: id_key(x["factor_id"]))
    for i, item in enumerate(out):
        item["occurrence_index"] = i
    return out


def exact_cuts(catalog: list[dict], order: list[Any], dimension: int) -> tuple[list[dict], int]:
    by = {id_key(item["factor_id"]): item for item in catalog}
    actual = [id_key(x) for x in order]
    if sorted(actual) != sorted(by) or len(actual) != len(by) or len(set(actual)) != len(actual):
        raise AssertionError("factor order is not an exact occurrence permutation")
    blocks = [tuple(int(v) for v in by[key]["normal_space"]) for key in actual]
    cuts = []
    maximum = 0
    for cut in range(len(order) + 1):
        left = rref((v for block in blocks[:cut] for v in block), dimension)
        right = rref((v for block in blocks[cut:] for v in block), dimension)
        boundary = intersection(left, right, dimension)
        width = len(boundary)
        maximum = max(maximum, width)
        cuts.append({
            "cut": cut,
            "left_factor_ids": copy.deepcopy(order[:cut]),
            "right_factor_ids": copy.deepcopy(order[cut:]),
            "left_span_rref": list(left),
            "right_span_rref": list(right),
            "boundary_rref": list(boundary),
            "width": width,
        })
    return cuts, maximum


def build(
    spec: dict,
    original_raw: dict,
    preprocessing: dict,
    discovery_raw: dict,
    b51: dict,
    carrier: dict,
    b52b: dict,
) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("lift spec")
    if preprocessing.get("schema") != PREP_SCHEMA:
        raise AssertionError("preprocessing schema")
    if b51.get("schema") != B51_SCHEMA or carrier.get("schema") != B52A_SCHEMA or b52b.get("schema") != B52B_SCHEMA:
        raise AssertionError("positive-chain schema")

    prep = preprocessing["proof_payload"]
    b1 = b51["proof_payload"]
    b2 = b52b["proof_payload"]
    dimension = int(prep["ambient_dim"])
    k = int(prep["k"])
    if int(original_raw["ambient_dim"]) != dimension or int(original_raw["k"]) != k:
        raise AssertionError("original parameters")
    if int(discovery_raw["ambient_dim"]) != dimension or int(discovery_raw["k"]) != k:
        raise AssertionError("discovery parameters")
    if prep["preprocessing_branch"] not in {"PREPROCESSING_BOUND", "TRIVIAL_SINGLETON_INPUT"}:
        raise AssertionError("order lift requires nonobstructed preprocessing")
    if prep["obstruction_occurrence_indices"]:
        raise AssertionError("obstructed preprocessing cannot lift positive order")
    if b1.get("capability_status") != "CLOSED_COMPLETE_TRACE" or int(b1.get("root_entry_count_if_closed", 0)) <= 0:
        raise AssertionError("positive B5.1 subject required")
    if b2.get("candidate_found_layout") is not True or b2.get("factor_order_ids") is None:
        raise AssertionError("positive B5.2B layout required")

    original = canonical_original_raw(original_raw, dimension)
    discovery = canonical_discovery_input(discovery_raw, dimension)
    if original != prep["original_catalog"]:
        raise AssertionError("original/preprocessing catalog identity")
    prep_discovery = [
        {
            "factor_id": copy.deepcopy(x["factor_id"]),
            "normal_space": list(x["normal_space"]),
            "affine_offset": copy.deepcopy(x["affine_offset"]),
            "occurrence_index": int(x["occurrence_index"]),
        }
        for x in prep["discovery_catalog"]
    ]
    if discovery != prep_discovery:
        raise AssertionError("discovery/preprocessing catalog identity")

    order = copy.deepcopy(b2["factor_order_ids"])
    reduced_cuts, reduced_max = exact_cuts(discovery, order, dimension)
    original_cuts, original_max = exact_cuts(original, order, dimension)
    if b2.get("cut_certificates") != reduced_cuts:
        raise AssertionError("B5.2B reduced cut transcript mismatch")
    if int(b2.get("maximum_cut_width")) != reduced_max or reduced_max > k:
        raise AssertionError("B5.2B reduced width cap")
    if len(original_cuts) != len(reduced_cuts):
        raise AssertionError("cut count")

    equality = []
    for oc, rc in zip(original_cuts, reduced_cuts):
        same = oc["boundary_rref"] == rc["boundary_rref"] and oc["width"] == rc["width"]
        if not same:
            raise AssertionError("original/reduced cut-boundary equality failed")
        equality.append({
            "cut": int(oc["cut"]),
            "boundary_rref_equal": True,
            "width_equal": True,
            "boundary_digest": dg(oc["boundary_rref"]),
        })
    if original_max != reduced_max or original_max > k:
        raise AssertionError("original width lift")

    orig_by = {id_key(x["factor_id"]): x for x in original}
    disc_by = {id_key(x["factor_id"]): x for x in discovery}
    layout_records = []
    for position, fid in enumerate(order):
        key = id_key(fid)
        if cb(orig_by[key]["affine_offset"]) != cb(disc_by[key]["affine_offset"]):
            raise AssertionError("affine identity changed across catalogs")
        layout_records.append({
            "position": position,
            "factor_id": copy.deepcopy(fid),
            "occurrence_index": int(orig_by[key]["occurrence_index"]),
            "original_normal_space": list(orig_by[key]["normal_space"]),
            "discovery_normal_space": list(disc_by[key]["normal_space"]),
            "affine_offset": copy.deepcopy(orig_by[key]["affine_offset"]),
            "affine_offset_identity_digest": dg(orig_by[key]["affine_offset"]),
        })

    payload = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "ambient_dim": dimension,
        "k": k,
        "subject": {
            "preprocessing_semantic_digest": preprocessing["semantic_digest"],
            "b5_1_semantic_digest": b51["semantic_digest"],
            "b5_2a_semantic_digest": carrier["semantic_digest"],
            "b5_2b_semantic_digest": b52b["semantic_digest"],
            "original_catalog_semantic_digest": prep["original_catalog_semantic_digest"],
            "discovery_catalog_semantic_digest": prep["discovery_catalog_semantic_digest"],
        },
        "factor_order_ids": order,
        "layout_records": layout_records,
        "discovery_cut_certificates": reduced_cuts,
        "original_cut_certificates": original_cuts,
        "cut_equality_certificates": equality,
        "discovery_maximum_cut_width": reduced_max,
        "original_maximum_cut_width": original_max,
        "width_vectors_equal": [x["width"] for x in reduced_cuts] == [x["width"] for x in original_cuts],
        "all_cut_boundary_subspaces_equal": all(x["boundary_rref_equal"] for x in equality),
        "original_layout_lifted": True,
        "affine_offsets_interpreted": False,
        "phase_a_transcript_emitted": False,
        "c047_invoked": False,
        "strict_boundary": copy.deepcopy(spec["strict_boundary"]),
    }
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": payload}
    artifact["semantic_digest"] = dg(payload)
    return artifact


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--original-input", type=Path, required=True)
    ap.add_argument("--preprocessing", type=Path, required=True)
    ap.add_argument("--discovery-input", type=Path, required=True)
    ap.add_argument("--b5-1-artifact", type=Path, required=True)
    ap.add_argument("--carrier", type=Path, required=True)
    ap.add_argument("--b5-2b-artifact", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    artifact = build(load(a.spec), load(a.original_input), load(a.preprocessing), load(a.discovery_input), load(a.b5_1_artifact), load(a.carrier), load(a.b5_2b_artifact))
    save(artifact, a.output)
    p = artifact["proof_payload"]
    print("JANUS_B5_REDUCED_TO_ORIGINAL_ORDER_LIFT = PASS")
    print("FACTOR_ORDER_IDS =", json.dumps(p["factor_order_ids"], sort_keys=True, separators=(",", ":")))
    print("DISCOVERY_MAXIMUM_CUT_WIDTH =", p["discovery_maximum_cut_width"])
    print("ORIGINAL_MAXIMUM_CUT_WIDTH =", p["original_maximum_cut_width"])
    print("ALL_CUT_BOUNDARY_SUBSPACES_EQUAL = TRUE")
    print("AFFINE_OFFSETS_INTERPRETED = FALSE")
    print("PHASE_A_TRANSCRIPT_EMITTED = FALSE")
    print("C047_INVOKED = FALSE")
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", artifact["semantic_digest"])


if __name__ == "__main__":
    main()
