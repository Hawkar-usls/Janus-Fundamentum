from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

import janus_c049_1_b5_iterative_compression_preprocessing_binding as prep
import janus_c049_1_b5_iterative_compression_preprocessing_binding_verifier as prepv
import janus_c049_1_b5_1_generic_corrected_runtime_trace_executor as b51
import janus_c049_1_b5_1_generic_corrected_runtime_trace_executor_verifier as b51v
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_v11 as b52a
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier_v11 as b52av
import janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction as b52b
import janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction_verifier as b52bv
import janus_c049_1_b5_reduced_to_original_order_lift as lift
import janus_c049_1_b5_reduced_to_original_order_lift_verifier as liftv

ROOT = Path("experiments/direct")
TMP = Path("/tmp/b5-order-lift")
EVIDENCE = Path("/tmp/b5-order-lift-evidence")
PREP_SPEC = ROOT / "C049_1_B5_ITERATIVE_COMPRESSION_PREPROCESSING_BINDING_SPEC_V1.json"
B51_SPEC = ROOT / "C049_1_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_SPEC_V1.json"
B52A_AMENDMENT = ROOT / "C049_1_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_AMENDMENT_V1_1.json"
B52B_SPEC = ROOT / "C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_SPEC_V1.json"
LIFT_SPEC = ROOT / "C049_1_B5_REDUCED_TO_ORIGINAL_ORDER_LIFT_SPEC_V1.json"


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def tree(ids: list[str]) -> dict:
    leaves = [{"id": f"leaf:{i}", "factor_id": fid} for i, fid in enumerate(ids)]
    if len(leaves) == 1:
        return {"root": leaves[0]["id"], "nodes": leaves}
    nodes = list(leaves)
    left = leaves[0]["id"]
    for i in range(1, len(leaves)):
        nid = f"join:{i}"
        nodes.append({"id": nid, "left": left, "right": leaves[i]["id"]})
        left = nid
    return {"root": left, "nodes": nodes}


def originals() -> dict[str, dict]:
    return {
        "zero": {
            "ambient_dim": 2,
            "k": 0,
            "factors": [
                {"id": "alpha", "normal_space": [1], "affine_offset": {"tag": "a"}},
                {"id": "beta", "normal_space": [2], "affine_offset": {"tag": "b"}},
            ],
        },
        "strict": {
            "ambient_dim": 3,
            "k": 1,
            "factors": [
                {"id": "a", "normal_space": [1, 2], "affine_offset": {"tag": "a"}},
                {"id": "b", "normal_space": [2], "affine_offset": {"tag": "b"}},
                {"id": "c", "normal_space": [5], "affine_offset": {"tag": "c"}},
            ],
        },
        "dup": {
            "ambient_dim": 1,
            "k": 1,
            "factors": [
                {"id": "left", "normal_space": [1], "affine_offset": {"side": 0}},
                {"id": "right", "normal_space": [1], "affine_offset": {"side": 1}},
            ],
        },
    }


def build_subject(name: str, original: dict, *, reverse_discovery_presentation: bool = False) -> dict:
    prep_artifact = prep.build(prep.load(PREP_SPEC), original)
    prep_result = prepv.verify(prep_artifact, prep.load(PREP_SPEC), original)
    if prep_result["branch"] not in {"PREPROCESSING_BOUND", "TRIVIAL_SINGLETON_INPUT"}:
        raise AssertionError(name + ": preprocessing obstructed")
    pp = prep_artifact["proof_payload"]
    discovery_factors = [
        {"id": x["factor_id"], "normal_space": x["normal_space"], "affine_offset": x["affine_offset"]}
        for x in pp["discovery_catalog"]
    ]
    if reverse_discovery_presentation:
        discovery_factors.reverse()
    ids = sorted((str(x["factor_id"]) for x in pp["discovery_catalog"]))
    discovery = {
        "ambient_dim": int(pp["ambient_dim"]),
        "k": int(pp["k"]),
        "factors": discovery_factors,
        "tree": tree(ids),
        "caps": {"max_boundary_dim": 3, "max_k": 2, "max_full_set_entries": 5000, "max_child_pairs": 100000, "max_join_paths": 500000},
    }
    b1 = b51.execute(discovery, b51.load(B51_SPEC))
    if b51v.verify(b1, discovery, b51.load(B51_SPEC)) is not True:
        raise AssertionError(name + ": B5.1 did not close")
    if int(b1["proof_payload"]["root_entry_count_if_closed"]) <= 0:
        raise AssertionError(name + ": B5.1 root empty")
    carrier = b52a.build(discovery, b1, b52a.load(B52A_AMENDMENT))
    roots = b52av.verify_v11(carrier, discovery, b1, b52a.load(B52A_AMENDMENT))
    if int(roots) <= 0:
        raise AssertionError(name + ": carrier empty")
    layout = b52b.build(b52b.load(B52B_SPEC), discovery, b1, carrier)
    replay = b52bv.verify(layout, b52b.load(B52B_SPEC), discovery, b1, carrier)
    if replay["empty"] or int(replay["max_width"]) > int(pp["k"]):
        raise AssertionError(name + ": no positive B5.2B layout")
    candidate = lift.build(lift.load(LIFT_SPEC), original, prep_artifact, discovery, b1, carrier, layout)
    check = liftv.verify(candidate, lift.load(LIFT_SPEC), original, prep_artifact, discovery, b1, carrier, layout)
    return {
        "original": original,
        "preprocessing": prep_artifact,
        "discovery": discovery,
        "b51": b1,
        "carrier": carrier,
        "b52b": layout,
        "candidate": candidate,
        "verification": check,
    }


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    raws = originals()
    subjects = {
        "zero": build_subject("zero", raws["zero"]),
        "strict": build_subject("strict", raws["strict"]),
        "dup": build_subject("dup", raws["dup"]),
        "strict-reordered": build_subject("strict-reordered", raws["strict"], reverse_discovery_presentation=True),
    }

    zero_prep = subjects["zero"]["preprocessing"]["proof_payload"]
    assert [x["raw_dimension"] for x in zero_prep["occurrence_records"]] == [1, 1]
    assert [x["reduced_dimension"] for x in zero_prep["occurrence_records"]] == [0, 0]
    assert subjects["zero"]["verification"]["maximum_width"] == 0

    strict_prep = subjects["strict"]["preprocessing"]["proof_payload"]
    raw_dims = [x["raw_dimension"] for x in strict_prep["occurrence_records"]]
    reduced_dims = [x["reduced_dimension"] for x in strict_prep["occurrence_records"]]
    assert raw_dims != reduced_dims and any(a > b for a, b in zip(raw_dims, reduced_dims))
    assert subjects["strict"]["candidate"]["proof_payload"]["all_cut_boundary_subspaces_equal"] is True

    dup = subjects["dup"]["candidate"]["proof_payload"]["layout_records"]
    assert len(dup) == 2 and dup[0]["factor_id"] != dup[1]["factor_id"]
    assert dup[0]["original_normal_space"] == dup[1]["original_normal_space"]

    if lift.cb(subjects["strict"]["candidate"]) != lift.cb(subjects["strict-reordered"]["candidate"]):
        raise AssertionError("discovery presentation reorder changed lift artifact")

    orders = {json.dumps(subjects[name]["candidate"]["proof_payload"]["factor_order_ids"], sort_keys=True) for name in ("zero", "strict", "dup")}
    if len(orders) < 2:
        raise AssertionError("insufficient distinct order controls")

    rejected, total = liftv.tamper_suite(
        subjects["strict"]["candidate"],
        lift.load(LIFT_SPEC),
        subjects["strict"]["original"],
        subjects["strict"]["preprocessing"],
        subjects["strict"]["discovery"],
        subjects["strict"]["b51"],
        subjects["strict"]["carrier"],
        subjects["strict"]["b52b"],
    )
    if (rejected, total) != (20, 20):
        raise AssertionError(f"expected 20/20 tamper rejection, got {rejected}/{total}")

    for name, subject in subjects.items():
        path = EVIDENCE / f"{name}.lift.json"
        lift.save(subject["candidate"], path)

    receipt = {
        "schema": "janus.c049_1.b5.reduced_to_original_order_lift_exact_head_candidate_receipt.v1",
        "proof_head": os.environ["PROOF_HEAD"],
        "bindings": {
            "spec_git_blob": blob(LIFT_SPEC),
            "producer_git_blob": blob(ROOT / "janus_c049_1_b5_reduced_to_original_order_lift.py"),
            "verifier_git_blob": blob(ROOT / "janus_c049_1_b5_reduced_to_original_order_lift_verifier.py"),
            "harness_git_blob": blob(ROOT / "janus_c049_1_b5_reduced_to_original_order_lift_ci_harness.py"),
            "preprocessing_admission_receipt_git_blob": "69a6d709900df80e263c33405ddc0b19a593b27f",
            "b5_2b_admission_receipt_git_blob": "5e60eff4a4bd4c87cbf527cd446fc6b23b013774",
        },
        "controls": {
            name: {
                "sha256": sha(EVIDENCE / f"{name}.lift.json"),
                "semantic_digest": subject["candidate"]["semantic_digest"],
                "factor_order_ids": subject["candidate"]["proof_payload"]["factor_order_ids"],
                "maximum_width": subject["verification"]["maximum_width"],
            }
            for name, subject in subjects.items()
        },
        "checks": {
            "preprocessing_independent_replay": "PASS",
            "b5_1_b5_2a_b5_2b_independent_replay": "PASS",
            "k0_raw_1_1_reduced_0_0": "PASS",
            "strict_nontrivial_reduction": "PASS",
            "all_selected_order_cut_boundaries_equal": "PASS",
            "original_width_le_k": "PASS",
            "duplicate_geometry_distinct_occurrences": "PASS",
            "discovery_presentation_order_byte_identity": "PASS",
            "distinct_order_controls": len(orders),
            "digest_repaired_tampers_rejected": f"{rejected}/{total}",
            "affine_offsets_interpreted": False,
            "phase_a_transcript_emitted": False,
            "c047_invoked": False,
        },
        "strict_boundary": lift.load(LIFT_SPEC)["strict_boundary"],
        "formal_admission": "BLOCKED_PENDING_REVIEW",
    }
    dump(EVIDENCE / "exact-head-receipt.json", receipt)

    print("B5_ORDER_LIFT_PREPROCESSING_REPLAY = PASS")
    print("B5_ORDER_LIFT_POSITIVE_CHAIN_REPLAY = PASS")
    print("B5_ORDER_LIFT_K0_RAW_1_1_REDUCED_0_0 = PASS")
    print("B5_ORDER_LIFT_STRICT_NONTRIVIAL_REDUCTION = PASS")
    print("B5_ORDER_LIFT_ALL_SELECTED_CUT_BOUNDARIES_EQUAL = PASS")
    print("B5_ORDER_LIFT_DUPLICATE_GEOMETRY_DISTINCT_OCCURRENCES = PASS")
    print("B5_ORDER_LIFT_DISCOVERY_PRESENTATION_ORDER_BYTE_IDENTITY = PASS")
    print("B5_ORDER_LIFT_DISTINCT_ORDER_CONTROLS =", len(orders))
    print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")
    print("AFFINE_OFFSETS_INTERPRETED = FALSE")
    print("PHASE_A_TRANSCRIPT_EMITTED = FALSE")
    print("C047_INVOKED = FALSE")
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
