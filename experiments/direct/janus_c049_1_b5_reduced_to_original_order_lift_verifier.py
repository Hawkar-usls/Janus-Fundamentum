from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Callable

import janus_c049_1_b5_iterative_compression_preprocessing_binding_verifier as prepv
import janus_c049_1_b5_1_generic_corrected_runtime_trace_executor_verifier as b51v
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier_v11 as b52av
import janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction_verifier as b52bv

SCHEMA = "janus.c049_1.b5.reduced_to_original_order_lift_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5.reduced_to_original_order_lift_spec.v1"
BASE = Path("experiments/direct")
PREP_SPEC = BASE / "C049_1_B5_ITERATIVE_COMPRESSION_PREPROCESSING_BINDING_SPEC_V1.json"
B51_SPEC = BASE / "C049_1_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_SPEC_V1.json"
B52A_AMENDMENT = BASE / "C049_1_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_AMENDMENT_V1_1.json"
B52B_SPEC = BASE / "C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_SPEC_V1.json"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def idk(value: Any) -> str:
    return cb(value).decode("utf-8")


def rr(rows: Iterable[int], d: int) -> tuple[int, ...]:
    limit = 1 << d
    work = [int(x) for x in rows]
    if any(x < 0 or x >= limit for x in work):
        raise AssertionError("vector outside ambient")
    result: list[int] = []
    for bit in range(d - 1, -1, -1):
        pi = next((i for i, x in enumerate(work) if (x >> bit) & 1), None)
        if pi is None:
            continue
        p = work.pop(pi)
        work = [x ^ p if ((x >> bit) & 1) else x for x in work]
        result = [x ^ p if ((x >> bit) & 1) else x for x in result]
        result.append(p)
    return tuple(sorted((x for x in result if x), reverse=True))


def rank(rows: Iterable[int], d: int) -> int:
    return len(rr(rows, d))


def member(v: int, basis: Iterable[int], d: int) -> bool:
    b = list(basis)
    return rank(b, d) == rank(b + [int(v)], d)


def all_vectors(basis: tuple[int, ...]) -> Iterable[int]:
    # Used only to derive an intersection basis by linear-relation elimination,
    # never to enumerate the ambient vector space.
    n = len(basis)
    for mask in range(1 << n):
        v = 0
        for i, row in enumerate(basis):
            if (mask >> i) & 1:
                v ^= row
        yield v


def inter(left: Iterable[int], right: Iterable[int], d: int) -> tuple[int, ...]:
    a = rr(left, d)
    b = rr(right, d)
    # Enumerating combinations of the smaller *basis* is finite rank work for
    # this independent verifier; it is not an input-layout oracle.
    source, target = (a, b) if len(a) <= len(b) else (b, a)
    vectors = [v for v in all_vectors(source) if v and member(v, target, d)]
    return rr(vectors, d)


def canonical_original(raw: dict, d: int) -> list[dict]:
    factors = raw.get("factors")
    if not isinstance(factors, list):
        raise AssertionError("original factors")
    out = []
    seen = set()
    for presentation_index, f in enumerate(factors):
        key = idk(f["id"])
        if key in seen:
            raise AssertionError("duplicate factor")
        seen.add(key)
        out.append({
            "factor_id": copy.deepcopy(f["id"]),
            "presentation_index": presentation_index,
            "normal_space": list(rr(f.get("normal_space", []), d)),
            "affine_offset": copy.deepcopy(f.get("affine_offset")),
        })
    out.sort(key=lambda x: idk(x["factor_id"]))
    for i, x in enumerate(out):
        x["occurrence_index"] = i
    return out


def canonical_discovery(raw: dict, d: int) -> list[dict]:
    factors = raw.get("factors")
    if not isinstance(factors, list):
        raise AssertionError("discovery factors")
    out, seen = [], set()
    for f in factors:
        key = idk(f["id"])
        if key in seen:
            raise AssertionError("duplicate discovery factor")
        seen.add(key)
        out.append({
            "factor_id": copy.deepcopy(f["id"]),
            "normal_space": list(rr(f.get("normal_space", []), d)),
            "affine_offset": copy.deepcopy(f.get("affine_offset")),
        })
    out.sort(key=lambda x: idk(x["factor_id"]))
    for i, x in enumerate(out):
        x["occurrence_index"] = i
    return out


def cuts(catalog: list[dict], order: list[Any], d: int) -> tuple[list[dict], int]:
    by = {idk(x["factor_id"]): x for x in catalog}
    keys = [idk(x) for x in order]
    if sorted(keys) != sorted(by) or len(keys) != len(by) or len(set(keys)) != len(keys):
        raise AssertionError("order permutation")
    blocks = [tuple(by[k]["normal_space"]) for k in keys]
    out, maximum = [], 0
    for cut in range(len(order) + 1):
        left = rr((v for block in blocks[:cut] for v in block), d)
        right = rr((v for block in blocks[cut:] for v in block), d)
        boundary = inter(left, right, d)
        width = len(boundary)
        maximum = max(maximum, width)
        out.append({
            "cut": cut,
            "left_factor_ids": copy.deepcopy(order[:cut]),
            "right_factor_ids": copy.deepcopy(order[cut:]),
            "left_span_rref": list(left),
            "right_span_rref": list(right),
            "boundary_rref": list(boundary),
            "width": width,
        })
    return out, maximum


def verify(candidate: dict, spec: dict, original_raw: dict, preprocessing: dict, discovery_raw: dict, b51: dict, carrier: dict, b52b: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("spec")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("candidate schema")
    p = candidate["proof_payload"]
    if candidate.get("semantic_digest") != dg(p):
        raise AssertionError("candidate digest")

    prep_result = prepv.verify(preprocessing, load(PREP_SPEC), original_raw)
    if prep_result["branch"] not in {"PREPROCESSING_BOUND", "TRIVIAL_SINGLETON_INPUT"}:
        raise AssertionError("preprocessing obstruction")
    b51_closed = b51v.verify(b51, discovery_raw, load(B51_SPEC))
    if b51_closed is not True:
        raise AssertionError("B5.1 is not CLOSED")
    root_count = int(b51["proof_payload"]["root_entry_count_if_closed"])
    if root_count <= 0:
        raise AssertionError("positive root required")
    carrier_roots = b52av.verify_v11(carrier, discovery_raw, b51, load(B52A_AMENDMENT))
    if int(carrier_roots) != root_count:
        raise AssertionError("carrier root count")
    layout_replay = b52bv.verify(b52b, load(B52B_SPEC), discovery_raw, b51, carrier)
    if layout_replay["empty"]:
        raise AssertionError("B5.2B empty")

    prep = preprocessing["proof_payload"]
    d, k = int(prep["ambient_dim"]), int(prep["k"])
    if int(original_raw["ambient_dim"]) != d or int(original_raw["k"]) != k or int(discovery_raw["ambient_dim"]) != d or int(discovery_raw["k"]) != k:
        raise AssertionError("parameter identity")
    original = canonical_original(original_raw, d)
    discovery = canonical_discovery(discovery_raw, d)
    if original != prep["original_catalog"]:
        raise AssertionError("original catalog binding")
    expected_discovery = [{
        "factor_id": copy.deepcopy(x["factor_id"]),
        "normal_space": list(x["normal_space"]),
        "affine_offset": copy.deepcopy(x["affine_offset"]),
        "occurrence_index": int(x["occurrence_index"]),
    } for x in prep["discovery_catalog"]]
    if discovery != expected_discovery:
        raise AssertionError("discovery catalog binding")

    order = copy.deepcopy(layout_replay["order"])
    dcuts, dmax = cuts(discovery, order, d)
    ocuts, omax = cuts(original, order, d)
    if dcuts != b52b["proof_payload"]["cut_certificates"] or int(layout_replay["max_width"]) != dmax:
        raise AssertionError("independent reduced cut replay")
    if dmax > k:
        raise AssertionError("reduced width cap")
    if omax != dmax or omax > k:
        raise AssertionError("original width cap")
    equal = []
    for oc, dc in zip(ocuts, dcuts):
        if oc["boundary_rref"] != dc["boundary_rref"] or int(oc["width"]) != int(dc["width"]):
            raise AssertionError("cut boundary equality")
        equal.append({"cut": oc["cut"], "boundary_rref_equal": True, "width_equal": True, "boundary_digest": dg(oc["boundary_rref"])})

    by_o = {idk(x["factor_id"]): x for x in original}
    by_d = {idk(x["factor_id"]): x for x in discovery}
    records = []
    for pos, fid in enumerate(order):
        key = idk(fid)
        if cb(by_o[key]["affine_offset"]) != cb(by_d[key]["affine_offset"]):
            raise AssertionError("affine identity")
        records.append({
            "position": pos,
            "factor_id": copy.deepcopy(fid),
            "occurrence_index": int(by_o[key]["occurrence_index"]),
            "original_normal_space": list(by_o[key]["normal_space"]),
            "discovery_normal_space": list(by_d[key]["normal_space"]),
            "affine_offset": copy.deepcopy(by_o[key]["affine_offset"]),
            "affine_offset_identity_digest": dg(by_o[key]["affine_offset"]),
        })

    expected_subject = {
        "preprocessing_semantic_digest": preprocessing["semantic_digest"],
        "b5_1_semantic_digest": b51["semantic_digest"],
        "b5_2a_semantic_digest": carrier["semantic_digest"],
        "b5_2b_semantic_digest": b52b["semantic_digest"],
        "original_catalog_semantic_digest": prep["original_catalog_semantic_digest"],
        "discovery_catalog_semantic_digest": prep["discovery_catalog_semantic_digest"],
    }
    comparisons = {
        "gate": spec["gate"],
        "status": "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW",
        "ambient_dim": d,
        "k": k,
        "subject": expected_subject,
        "factor_order_ids": order,
        "layout_records": records,
        "discovery_cut_certificates": dcuts,
        "original_cut_certificates": ocuts,
        "cut_equality_certificates": equal,
        "discovery_maximum_cut_width": dmax,
        "original_maximum_cut_width": omax,
        "width_vectors_equal": True,
        "all_cut_boundary_subspaces_equal": True,
        "original_layout_lifted": True,
        "affine_offsets_interpreted": False,
        "phase_a_transcript_emitted": False,
        "c047_invoked": False,
        "strict_boundary": spec["strict_boundary"],
    }
    if p != comparisons:
        raise AssertionError("lift candidate differs from independent reconstruction")
    return {"factor_count": len(order), "maximum_width": omax, "cut_count": len(ocuts), "order": order}


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def tamper_suite(base: dict, spec: dict, original_raw: dict, preprocessing: dict, discovery_raw: dict, b51: dict, carrier: dict, b52b: dict) -> tuple[int, int]:
    attacks: list[tuple[str, Callable[[dict], None]]] = []
    def add(name: str, fn: Callable[[dict], None]) -> None:
        attacks.append((name, fn))
    add("T01_PREPROCESSING_DIGEST", lambda p: p["subject"].__setitem__("preprocessing_semantic_digest", "0"*64))
    add("T02_DISCOVERY_DIGEST", lambda p: p["subject"].__setitem__("discovery_catalog_semantic_digest", "0"*64))
    add("T03_ORIGINAL_DIGEST", lambda p: p["subject"].__setitem__("original_catalog_semantic_digest", "0"*64))
    add("T04_ORDER", lambda p: p["factor_order_ids"].__setitem__(-1, p["factor_order_ids"][0]))
    add("T05_DUP_OCCURRENCE", lambda p: p["layout_records"].append(copy.deepcopy(p["layout_records"][0])))
    add("T06_UNKNOWN_ID", lambda p: p["factor_order_ids"].__setitem__(0, "__unknown__"))
    add("T07_AFFINE_IDENTITY", lambda p: p["layout_records"][0].__setitem__("affine_offset", {"tamper": True}))
    add("T08_D_LEFT", lambda p: p["discovery_cut_certificates"][0].__setitem__("left_span_rref", [999]))
    add("T09_D_RIGHT", lambda p: p["discovery_cut_certificates"][0].__setitem__("right_span_rref", [999]))
    add("T10_D_BOUNDARY", lambda p: p["discovery_cut_certificates"][0].__setitem__("boundary_rref", [999]))
    add("T11_D_WIDTH", lambda p: p["discovery_cut_certificates"][0].__setitem__("width", 999))
    add("T12_O_LEFT", lambda p: p["original_cut_certificates"][0].__setitem__("left_span_rref", [999]))
    add("T13_O_RIGHT", lambda p: p["original_cut_certificates"][0].__setitem__("right_span_rref", [999]))
    add("T14_O_BOUNDARY", lambda p: p["original_cut_certificates"][0].__setitem__("boundary_rref", [999]))
    add("T15_O_WIDTH", lambda p: p["original_cut_certificates"][0].__setitem__("width", 999))
    add("T16_EQUALITY", lambda p: p["cut_equality_certificates"][0].__setitem__("boundary_rref_equal", False))
    add("T17_MAX_WIDTH", lambda p: p.__setitem__("original_maximum_cut_width", 999))
    add("T18_WIDTH_PROMOTION", lambda p: p.__setitem__("width_vectors_equal", False))
    add("T19_PHASE_A_C047", lambda p: p.update({"phase_a_transcript_emitted": True, "c047_invoked": True}))
    add("T20_GLOBAL_PROMOTION", lambda p: p["strict_boundary"].update({"iterative_compression_orchestrator": True, "phase_a_c047_from_lift": True, "all_input_termination": "ESTABLISHED", "polynomial_runtime": "ESTABLISHED", "b5_complete": True, "p_vs_np": "CLOSED"}))

    rejected = 0
    for name, mutate in attacks:
        c = copy.deepcopy(base)
        mutate(c["proof_payload"])
        repair(c)
        try:
            verify(c, spec, original_raw, preprocessing, discovery_raw, b51, carrier, b52b)
        except Exception:
            rejected += 1
            print(name + " = REJECTED")
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--original-input", type=Path, required=True)
    ap.add_argument("--preprocessing", type=Path, required=True)
    ap.add_argument("--discovery-input", type=Path, required=True)
    ap.add_argument("--b5-1-artifact", type=Path, required=True)
    ap.add_argument("--carrier", type=Path, required=True)
    ap.add_argument("--b5-2b-artifact", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--tamper-suite", action="store_true")
    a = ap.parse_args()
    spec = load(a.spec)
    args = (load(a.original_input), load(a.preprocessing), load(a.discovery_input), load(a.b5_1_artifact), load(a.carrier), load(a.b5_2b_artifact))
    candidate = load(a.candidate)
    result = verify(candidate, spec, *args)
    print("JANUS_B5_REDUCED_TO_ORIGINAL_ORDER_LIFT_INDEPENDENT_VERIFIER = PASS")
    print("FACTOR_OCCURRENCES =", result["factor_count"])
    print("CUT_COUNT =", result["cut_count"])
    print("ORIGINAL_MAXIMUM_CUT_WIDTH =", result["maximum_width"])
    print("ALL_CUT_BOUNDARY_SUBSPACES_EQUAL = TRUE")
    print("AFFINE_OFFSETS_INTERPRETED = FALSE")
    print("PHASE_A_TRANSCRIPT_EMITTED = FALSE")
    print("C047_INVOKED = FALSE")
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    if a.tamper_suite:
        rejected, total = tamper_suite(candidate, spec, *args)
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")


if __name__ == "__main__":
    main()
