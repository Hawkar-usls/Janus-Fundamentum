from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier as liftv
import janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier_v11 as liftv11

D = Path("experiments/direct")
TMP = Path("/tmp/b5-original-order-lift")
EVIDENCE = Path("/tmp/b5-original-order-lift-evidence")

SPEC = D / "C049_1_B5_FULL_INPUT_ORIGINAL_ORDER_LIFT_C047_REBOUND_SPEC_V1.json"
AMENDMENT = D / "C049_1_B5_FULL_INPUT_ORIGINAL_ORDER_LIFT_C047_REBOUND_AMENDMENT_V1_1.json"
PRODUCER = D / "janus_c049_1_b5_full_input_original_order_lift_c047_rebound.py"
VERIFIER = D / "janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier.py"
VERIFIER_V11 = D / "janus_c049_1_b5_full_input_original_order_lift_c047_rebound_verifier_v11.py"

PRE_SPEC = D / "C049_1_B5_ITERATIVE_COMPRESSION_PREPROCESSING_BINDING_SPEC_V1.json"
PRE_PRODUCER = D / "janus_c049_1_b5_iterative_compression_preprocessing_binding.py"
PRE_VERIFIER = D / "janus_c049_1_b5_iterative_compression_preprocessing_binding_verifier.py"

B51_SPEC = D / "C049_1_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_SPEC_V1.json"
B51_PRODUCER = D / "janus_c049_1_b5_1_generic_corrected_runtime_trace_executor.py"
B51_VERIFIER = D / "janus_c049_1_b5_1_generic_corrected_runtime_trace_executor_verifier.py"

B52A_SPEC = D / "C049_1_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_AMENDMENT_V1_1.json"
B52A_PRODUCER = D / "janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_v11.py"
B52A_VERIFIER = D / "janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier_v11.py"

B52B_SPEC = D / "C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_SPEC_V1.json"
B52B_PRODUCER = D / "janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction.py"
B52B_VERIFIER = D / "janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction_verifier_v11.py"

B54_SPEC = D / "C049_1_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_SPEC_V1.json"
B54_PRODUCER = D / "janus_c049_1_b5_4_corrected_discovery_c047_rebound_v11.py"
B54_VERIFIER = D / "janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v11.py"
B52B_RECEIPT = D / "audits/C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_ADMISSION_F057B7AF.json"
B53_RECEIPT = D / "audits/C049_1_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_COMPOSITION_ADMISSION_E9841522.json"
PRE_RECEIPT = D / "audits/C049_1_B5_ITERATIVE_COMPRESSION_PREPROCESSING_BINDING_ADMISSION_8DA1F1DE.json"


def cb(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, x: Any) -> None:
    path.write_bytes(cb(x) + b"\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def run(args: list[str], log: Path | None = None) -> str:
    cp = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    if log is not None:
        log.write_text(cp.stdout, encoding="utf-8")
    return cp.stdout


def affine(equations: list[list[int]]) -> dict:
    return {"schema": "janus.c049_1.c047_affine_equations.v1", "equations": equations}


def controls() -> dict[str, dict]:
    caps = {"max_boundary_dim": 3, "max_k": 1, "max_full_set_entries": 10000, "max_child_pairs": 200000, "max_join_paths": 1000000}
    sat = {
        "ambient_dim": 2, "k": 0,
        "factors": [
            {"id": "alpha", "normal_space": [1], "affine_offset": affine([[1, 0]])},
            {"id": "beta", "normal_space": [2], "affine_offset": affine([[2, 0]])},
        ],
        "caps": caps,
    }
    sat_reordered = {"ambient_dim": 2, "k": 0, "factors": list(reversed(sat["factors"])), "caps": caps}
    unsat = {
        "ambient_dim": 1, "k": 1,
        "factors": [
            {"id": "left", "normal_space": [1], "affine_offset": affine([[1, 0]])},
            {"id": "right", "normal_space": [1], "affine_offset": affine([[1, 1]])},
        ],
        "caps": caps,
    }
    shrink = {
        "ambient_dim": 3, "k": 1,
        "factors": [
            {"id": "a", "normal_space": [1, 2, 4], "affine_offset": affine([[1, 0], [2, 0], [4, 0]])},
            {"id": "b", "normal_space": [1], "affine_offset": affine([[1, 0]])},
            {"id": "c", "normal_space": [2], "affine_offset": affine([[2, 0]])},
        ],
        "caps": caps,
    }
    opaque = {
        "ambient_dim": 2, "k": 0,
        "factors": [
            {"id": "alpha", "normal_space": [1], "affine_offset": {"opaque": "A"}},
            {"id": "beta", "normal_space": [2], "affine_offset": {"opaque": "B"}},
        ],
        "caps": caps,
    }
    return {"sat": sat, "sat-reordered": sat_reordered, "unsat": unsat, "shrink": shrink, "opaque": opaque}


def tree_for(ids: list[str]) -> dict:
    if not ids:
        raise AssertionError("positive B5 chain requires at least one factor")
    nodes: list[dict] = []
    leaf_ids = []
    for i, fid in enumerate(ids):
        nid = f"leaf_{i}"
        leaf_ids.append(nid)
        nodes.append({"id": nid, "factor_id": fid})
    root = leaf_ids[0]
    for i in range(1, len(leaf_ids)):
        parent = f"join_{i}"
        nodes.append({"id": parent, "left": root, "right": leaf_ids[i]})
        root = parent
    return {"root": root, "nodes": nodes}


def make_reduced_raw(original: dict, pre: dict) -> dict:
    p = pre["proof_payload"]
    factors = [
        {"id": str(rec["factor_id"]), "normal_space": list(rec["normal_space"]), "affine_offset": rec.get("affine_offset")}
        for rec in p["discovery_catalog"]
    ]
    ids = [x["id"] for x in factors]
    return {
        "ambient_dim": int(original["ambient_dim"]),
        "k": int(original["k"]),
        "caps": original["caps"],
        "factors": factors,
        "tree": tree_for(ids),
    }


def build_chain(name: str, original: dict) -> dict[str, Path]:
    raw = TMP / f"{name}.original.json"
    pre = TMP / f"{name}.pre.json"
    reduced = TMP / f"{name}.reduced.json"
    b51 = TMP / f"{name}.b51.json"
    carrier = TMP / f"{name}.carrier.json"
    b52 = TMP / f"{name}.b52.json"
    lift = TMP / f"{name}.lift.json"
    write(raw, original)

    run([sys.executable, str(PRE_PRODUCER), "--spec", str(PRE_SPEC), "--input", str(raw), "--output", str(pre)], TMP / f"{name}.pre.log")
    run([sys.executable, str(PRE_VERIFIER), "--spec", str(PRE_SPEC), "--input", str(raw), "--candidate", str(pre)], TMP / f"{name}.prev.log")
    pre_obj = load(pre)
    if pre_obj["proof_payload"]["preprocessing_branch"] not in {"PREPROCESSING_BOUND", "TRIVIAL_SINGLETON_INPUT"}:
        raise AssertionError(name + " did not reach positive preprocessing branch")
    write(reduced, make_reduced_raw(original, pre_obj))

    run([sys.executable, str(B51_PRODUCER), "--spec", str(B51_SPEC), "--input", str(reduced), "--output", str(b51)], TMP / f"{name}.b51.log")
    b51log = run([sys.executable, str(B51_VERIFIER), "--spec", str(B51_SPEC), "--input", str(reduced), "--candidate", str(b51)], TMP / f"{name}.b51v.log")
    if "CAPABILITY_STATUS = CLOSED_COMPLETE_TRACE" not in b51log:
        raise AssertionError(name + " B5.1 not CLOSED")

    run([sys.executable, str(B52A_PRODUCER), "--spec", str(B52A_SPEC), "--input", str(reduced), "--b5-1-artifact", str(b51), "--output", str(carrier)], TMP / f"{name}.carrier.log")
    cverify = run([sys.executable, str(B52A_VERIFIER), "--spec", str(B52A_SPEC), "--input", str(reduced), "--b5-1-artifact", str(b51), "--candidate", str(carrier)], TMP / f"{name}.carrierv.log")
    if "JANUS_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_V1_1_INDEPENDENT_VERIFIER = PASS" not in cverify:
        raise AssertionError(name + " B5.2A verify")

    run([sys.executable, str(B52B_PRODUCER), "--spec", str(B52B_SPEC), "--input", str(reduced), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--output", str(b52)], TMP / f"{name}.b52.log")
    b52verify = run([sys.executable, str(B52B_VERIFIER), "--spec", str(B52B_SPEC), "--input", str(reduced), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--candidate", str(b52)], TMP / f"{name}.b52v.log")
    if "JANUS_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_INDEPENDENT_VERIFIER_V1_1 = PASS" not in b52verify:
        raise AssertionError(name + " B5.2B verify")

    run([sys.executable, str(PRODUCER), "--spec", str(SPEC), "--original-input", str(raw), "--preprocessing", str(pre), "--reduced-input", str(reduced), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--b5-2b-artifact", str(b52), "--output", str(lift)], TMP / f"{name}.lift.log")
    lverify = run([
        sys.executable, str(VERIFIER), "--spec", str(SPEC), "--preprocessing-spec", str(PRE_SPEC), "--b5-1-spec", str(B51_SPEC), "--b5-2a-spec", str(B52A_SPEC), "--b5-2b-spec", str(B52B_SPEC),
        "--original-input", str(raw), "--preprocessing", str(pre), "--reduced-input", str(reduced), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--b5-2b-artifact", str(b52), "--candidate", str(lift)
    ], TMP / f"{name}.liftv.log")
    if "JANUS_B5_FULL_INPUT_ORIGINAL_ORDER_LIFT_C047_REBOUND_INDEPENDENT_VERIFIER = PASS" not in lverify:
        raise AssertionError(name + " lift verify")
    return {"raw": raw, "pre": pre, "reduced": reduced, "b51": b51, "carrier": carrier, "b52": b52, "lift": lift}


def direct_reduced_b54(name: str, files: dict[str, Path]) -> dict:
    out = TMP / f"{name}.direct-b54.json"
    run([sys.executable, str(B54_PRODUCER), "--spec", str(B54_SPEC), "--input", str(files["reduced"]), "--b5-1-artifact", str(files["b51"]), "--carrier", str(files["carrier"]), "--b5-2b-artifact", str(files["b52"]), "--output", str(out)], TMP / f"{name}.direct-b54.log")
    verifylog = run([
        sys.executable, str(B54_VERIFIER), "--spec", str(B54_SPEC), "--carrier-spec", str(B52A_SPEC), "--b5-2b-spec", str(B52B_SPEC), "--b5-2b-admission", str(B52B_RECEIPT), "--b5-3-admission", str(B53_RECEIPT),
        "--input", str(files["reduced"]), "--b5-1-artifact", str(files["b51"]), "--carrier", str(files["carrier"]), "--b5-2b-artifact", str(files["b52"]), "--candidate", str(out)
    ], TMP / f"{name}.direct-b54v.log")
    if "JANUS_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_INDEPENDENT_VERIFIER_V1_1 = PASS" not in verifylog:
        raise AssertionError(name + " direct reduced B5.4 verify")
    return load(out)


def build_hist_open(files: dict[str, Path]) -> Path:
    out = TMP / "hist-open.lift.json"
    run([sys.executable, str(PRODUCER), "--spec", str(SPEC), "--original-input", str(files["raw"]), "--preprocessing", str(files["pre"]), "--reduced-input", str(files["reduced"]), "--b5-1-artifact", str(files["b51"]), "--carrier", str(files["carrier"]), "--b5-2b-artifact", str(files["b52"]), "--trellis-work-cap", "0", "--output", str(out)], TMP / "hist-open.lift.log")
    log = run([
        sys.executable, str(VERIFIER), "--spec", str(SPEC), "--preprocessing-spec", str(PRE_SPEC), "--b5-1-spec", str(B51_SPEC), "--b5-2a-spec", str(B52A_SPEC), "--b5-2b-spec", str(B52B_SPEC),
        "--original-input", str(files["raw"]), "--preprocessing", str(files["pre"]), "--reduced-input", str(files["reduced"]), "--b5-1-artifact", str(files["b51"]), "--carrier", str(files["carrier"]), "--b5-2b-artifact", str(files["b52"]), "--candidate", str(out), "--trellis-work-cap", "0"
    ], TMP / "hist-open.liftv.log")
    if "JANUS_B5_FULL_INPUT_ORIGINAL_ORDER_LIFT_C047_REBOUND_INDEPENDENT_VERIFIER = PASS" not in log:
        raise AssertionError("historical OPEN verify")
    return out


def tamper_strict_shrink(files: dict[str, Path]) -> tuple[int, int]:
    subject = {
        "raw_original": load(files["raw"]), "preprocessing": load(files["pre"]), "reduced_raw": load(files["reduced"]),
        "b51": load(files["b51"]), "carrier": load(files["carrier"]), "b52": load(files["b52"]), "candidate": load(files["lift"]),
        "caps": {"discovery_cap": None, "work_cap": None, "certificate_cap": None, "trellis_work_cap": None, "trellis_certificate_cap": None},
    }
    return liftv11.tamper_suite(subject, load(SPEC), load(PRE_SPEC), load(B51_SPEC), load(B52A_SPEC), load(B52B_SPEC))


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    c = controls()
    files = {name: build_chain(name, raw) for name, raw in c.items()}
    hist_open_path = build_hist_open(files["sat"])
    direct_sat = direct_reduced_b54("sat", files["sat"])
    direct_shrink = direct_reduced_b54("shrink", files["shrink"])

    sat = load(files["sat"]["lift"])["proof_payload"]
    sat_r = load(files["sat-reordered"]["lift"])["proof_payload"]
    unsat = load(files["unsat"]["lift"])["proof_payload"]
    shrink = load(files["shrink"]["lift"])["proof_payload"]
    opaque = load(files["opaque"]["lift"])["proof_payload"]
    hopen = load(hist_open_path)["proof_payload"]

    assert sat["c047_result"] == "SAT" and sat["historical_phase_a_verifier_pass"] is True and sat["original_layout_replay"]["maximum_width"] <= 0
    assert unsat["c047_result"] == "UNSAT" and unsat["historical_phase_a_verifier_pass"] is True and len({x["phase_a_input_position"] for x in unsat["phase_a_factor_bijection"]}) == 2
    assert shrink["c047_result"] == "SAT" and shrink["historical_phase_a_verifier_pass"] is True and shrink["original_layout_replay"]["maximum_width"] <= 1
    pre_shrink = load(files["shrink"]["pre"])["proof_payload"]
    assert any(len(o["normal_space"]) > len(r["normal_space"]) for o, r in zip(pre_shrink["original_catalog"], pre_shrink["discovery_catalog"]))
    assert opaque["lift_status"] == "OPEN_AFFINE_REBOUND_BINDING" and opaque["c047_result"] == "NOT_ESTABLISHED"
    assert hopen["lift_status"] == "ORIGINAL_ORDER_LIFT_PHASE_A_C047_OPEN" and str(hopen["c047_result"]).startswith("OPEN_")
    assert direct_sat["proof_payload"]["rebound_status"] == "OPEN_AFFINE_REBOUND_BINDING" and direct_sat["proof_payload"]["c047_result"] == "NOT_ESTABLISHED"
    assert direct_shrink["proof_payload"]["rebound_status"] == "OPEN_AFFINE_REBOUND_BINDING" and direct_shrink["proof_payload"]["c047_result"] == "NOT_ESTABLISHED"
    assert sat["factor_order_ids"] == sat_r["factor_order_ids"]
    assert sat["original_layout_replay"] == sat_r["original_layout_replay"]
    assert sat["c047_result"] == sat_r["c047_result"]
    assert sat["preprocessing_semantic_digest"] != sat_r["preprocessing_semantic_digest"]
    assert all(x["semantic_boundary_equal"] is True for x in shrink["reduced_to_original_cut_bridge"])

    rejected, total = tamper_strict_shrink(files["shrink"])
    if (rejected, total) != (29, 29):
        raise AssertionError(f"expected 29/29 tamper rejection, got {rejected}/{total}")

    for name in ("sat", "unsat", "shrink", "opaque"):
        for key in ("lift",):
            (EVIDENCE / files[name][key].name).write_bytes(files[name][key].read_bytes())
        (EVIDENCE / f"{name}.liftv.log").write_bytes((TMP / f"{name}.liftv.log").read_bytes())
    (EVIDENCE / hist_open_path.name).write_bytes(hist_open_path.read_bytes())
    (EVIDENCE / "hist-open.liftv.log").write_bytes((TMP / "hist-open.liftv.log").read_bytes())
    (EVIDENCE / "sat.direct-b54.json").write_bytes((TMP / "sat.direct-b54.json").read_bytes())
    (EVIDENCE / "shrink.direct-b54.json").write_bytes((TMP / "shrink.direct-b54.json").read_bytes())

    sat_art = load(files["sat"]["lift"]); unsat_art = load(files["unsat"]["lift"]); shrink_art = load(files["shrink"]["lift"]); opaque_art = load(files["opaque"]["lift"]); hopen_art = load(hist_open_path)
    receipt = {
        "schema": "janus.c049_1.b5.full_input_original_order_lift_c047_rebound_exact_head_candidate_receipt.v1_1",
        "proof_head": os.environ.get("PROOF_HEAD", "LOCAL"),
        "bindings": {
            "spec_git_blob": git_blob(SPEC), "amendment_v1_1_git_blob": git_blob(AMENDMENT), "producer_git_blob": git_blob(PRODUCER),
            "base_independent_verifier_git_blob": git_blob(VERIFIER), "hardening_verifier_v1_1_git_blob": git_blob(VERIFIER_V11),
            "preprocessing_admission_receipt_git_blob": git_blob(PRE_RECEIPT), "b5_2b_admission_receipt_git_blob": git_blob(B52B_RECEIPT),
            "b5_3_admission_receipt_git_blob": git_blob(B53_RECEIPT),
        },
        "controls": {
            "sat": {"sha256": sha(files["sat"]["lift"]), "semantic_digest": sat_art["semantic_digest"], "c047_result": "SAT", "original_max_width": sat["original_layout_replay"]["maximum_width"]},
            "unsat": {"sha256": sha(files["unsat"]["lift"]), "semantic_digest": unsat_art["semantic_digest"], "c047_result": "UNSAT", "original_max_width": unsat["original_layout_replay"]["maximum_width"]},
            "strict_shrink": {"sha256": sha(files["shrink"]["lift"]), "semantic_digest": shrink_art["semantic_digest"], "c047_result": "SAT", "original_max_width": shrink["original_layout_replay"]["maximum_width"]},
            "opaque": {"sha256": sha(files["opaque"]["lift"]), "semantic_digest": opaque_art["semantic_digest"], "status": "OPEN_AFFINE_REBOUND_BINDING"},
            "historical_open": {"sha256": sha(hist_open_path), "semantic_digest": hopen_art["semantic_digest"], "c047_result": hopen["c047_result"]},
            "presentation_reorder": {"canonical_factor_order_equal": True, "original_layout_replay_equal": True, "c047_result_equal": True, "preprocessing_provenance_distinct": True},
            "direct_reduced_b5_4": {"sat": "OPEN_AFFINE_REBOUND_BINDING", "strict_shrink": "OPEN_AFFINE_REBOUND_BINDING"},
        },
        "checks": {
            "upstream_preprocessing_replay": "PASS", "upstream_b5_1_b5_2a_b5_2b_replay": "PASS", "original_cut_recomputation": "PASS",
            "reduced_original_cut_equivalence": "PASS", "original_affine_only": "PASS", "historical_phase_a_verifier": "PASS_OR_NOT_APPLICABLE_BY_BRANCH",
            "direct_b5_4_on_reduced_catalog": "FORBIDDEN_AND_CONTROLLED_OPEN", "historical_open_propagation": "PASS", "non_noop_repaired_digest_tampers": "29/29",
        },
        "negative_provenance": [{"classification": "BASE_T19_T20_T21_COULD_BE_NO_OP_ON_A_SAT_FIXTURE", "resolution": "V1_1_ENFORCES_CANONICAL_BYTE_CHANGE_BEFORE_EVERY_ATTACK", "semantic_replay_before_fix": False}],
        "formal_admission": "BLOCKED_PENDING_REVIEW", "iterative_compression_orchestrator": False, "all_input_termination": "NOT_ESTABLISHED",
        "polynomial_runtime": "NOT_ESTABLISHED", "b5_complete": False, "c049_1_complete": False, "p_vs_np": "OPEN",
    }
    write(EVIDENCE / "exact-head-receipt-v11.json", receipt)

    print("B5_FULL_INPUT_ORIGINAL_ORDER_LIFT_C047_REBOUND_HARNESS = PASS")
    print("SAT_CONTROL = PASS")
    print("UNSAT_CONTROL = PASS")
    print("STRICT_SHRINK_CONTROL = PASS")
    print("OPAQUE_OPEN_CONTROL = PASS")
    print("HISTORICAL_OPEN_CONTROL = PASS")
    print("PRESENTATION_REORDER_PROVENANCE_CONTROL = PASS")
    print("DIRECT_REDUCED_B5_4_CONTROL = OPEN_AS_REQUIRED")
    print("DIGEST_REPAIRED_TAMPERS_REJECTED = 29/29")
    print("ITERATIVE_COMPRESSION_ORCHESTRATOR = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
