from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v11 as v11

ROOT = Path("experiments/direct")
TMP = Path("/tmp/b54-v11")
EVIDENCE = Path("/tmp/b5-4-v11-evidence")

B51_SPEC = ROOT / "C049_1_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_SPEC_V1.json"
B51_PRODUCER = ROOT / "janus_c049_1_b5_1_generic_corrected_runtime_trace_executor.py"
B51_VERIFIER = ROOT / "janus_c049_1_b5_1_generic_corrected_runtime_trace_executor_verifier.py"
B52A_SPEC = ROOT / "C049_1_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_AMENDMENT_V1_1.json"
B52A_PRODUCER = ROOT / "janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_v11.py"
B52A_VERIFIER = ROOT / "janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier_v11.py"
B52B_SPEC = ROOT / "C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_SPEC_V1.json"
B52B_PRODUCER = ROOT / "janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction.py"
B52B_VERIFIER = ROOT / "janus_c049_1_b5_2b_generic_algorithm2_printorder_reconstruction_verifier_v11.py"
B52B_RECEIPT = ROOT / "audits/C049_1_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_RECONSTRUCTION_ADMISSION_F057B7AF.json"
B53_RECEIPT = ROOT / "audits/C049_1_B5_3_GENERIC_EMPTY_ROOT_TERMINAL_COMPOSITION_ADMISSION_E9841522.json"
B54_SPEC = ROOT / "C049_1_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_SPEC_V1.json"
B54_AMENDMENT = ROOT / "C049_1_B5_4_CORRECTED_DISCOVERY_C047_REBOUND_AMENDMENT_V1_1.json"
B54_PRODUCER = ROOT / "janus_c049_1_b5_4_corrected_discovery_c047_rebound_v11.py"
B54_VERIFIER = ROOT / "janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier_v11.py"

DEFAULT_CAPS = {
    "discovery_cap": None,
    "work_cap": None,
    "certificate_cap": None,
    "trellis_work_cap": None,
    "trellis_certificate_cap": None,
}
AFF = "janus.c049_1.c047_affine_equations.v1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def run(label: str, argv: list[str]) -> str:
    proc = subprocess.run(argv, text=True, capture_output=True)
    log = TMP / f"{label}.log"
    log.write_text(proc.stdout + ("\nSTDERR:\n" + proc.stderr if proc.stderr else ""), encoding="utf-8")
    if proc.returncode != 0:
        print(log.read_text(encoding="utf-8"))
        raise AssertionError(f"command failed: {label}")
    return proc.stdout


def py(path: Path, *args: str) -> list[str]:
    return [sys.executable, str(path), *args]


def off(equations):
    return {"schema": AFF, "equations": equations}


def write_controls() -> None:
    caps = {"max_boundary_dim": 2, "max_k": 1, "max_full_set_entries": 5000, "max_child_pairs": 100000, "max_join_paths": 500000}
    sat = {
        "ambient_dim": 2,
        "k": 0,
        "caps": caps,
        "factors": [
            {"id": "alpha", "normal_space": [1], "affine_offset": off([[1, 0]])},
            {"id": "beta", "normal_space": [2], "affine_offset": off([[2, 0]])},
        ],
        "tree": {"root": "root", "nodes": [{"id": "root", "left": "la", "right": "lb"}, {"id": "la", "factor_id": "alpha"}, {"id": "lb", "factor_id": "beta"}]},
    }
    sat_reordered = json.loads(json.dumps(sat))
    sat_reordered["factors"] = list(reversed(sat_reordered["factors"]))
    sat_reordered["tree"]["nodes"] = list(reversed(sat_reordered["tree"]["nodes"]))
    unsat = {
        "ambient_dim": 1,
        "k": 1,
        "caps": caps,
        "factors": [
            {"id": "left", "normal_space": [1], "affine_offset": off([[1, 0]])},
            {"id": "right", "normal_space": [1], "affine_offset": off([[1, 1]])},
        ],
        "tree": {"root": "r", "nodes": [{"id": "l", "factor_id": "left"}, {"id": "r", "left": "l", "right": "q"}, {"id": "q", "factor_id": "right"}]},
    }
    opaque = json.loads(json.dumps(sat))
    opaque["factors"][0]["affine_offset"] = {"opaque": "A"}
    opaque["factors"][1]["affine_offset"] = {"opaque": "B"}
    inconsistent = json.loads(json.dumps(sat))
    inconsistent["factors"][0]["affine_offset"] = off([[1, 0], [1, 1]])
    empty = json.loads(json.dumps(unsat))
    empty["k"] = 0
    opened = json.loads(json.dumps(empty))
    opened["caps"]["max_boundary_dim"] = 0
    basis = {
        "ambient_dim": 2,
        "k": 0,
        "caps": caps,
        "factors": [{"id": "gamma", "normal_space": [1, 2], "affine_offset": off([[1, 0], [2, 0]])}],
        "tree": {"root": "g", "nodes": [{"id": "g", "factor_id": "gamma"}]},
    }
    for name, value in {
        "sat": sat,
        "sat-reordered": sat_reordered,
        "unsat": unsat,
        "opaque": opaque,
        "inconsistent": inconsistent,
        "empty": empty,
        "b5-open": opened,
        "basis-order": basis,
    }.items():
        dump(TMP / f"{name}.json", value)


def build_chain(name: str) -> None:
    inp = TMP / f"{name}.json"
    b51 = TMP / f"{name}.b51.json"
    carrier = TMP / f"{name}.carrier.json"
    b52 = TMP / f"{name}.b52b.json"
    out = run(f"{name}.b51", py(B51_PRODUCER, "--spec", str(B51_SPEC), "--input", str(inp), "--output", str(b51)))
    if "CAPABILITY_STATUS = CLOSED_COMPLETE_TRACE" not in out:
        raise AssertionError(f"{name}: B5.1 not CLOSED")
    run(f"{name}.b51v", py(B51_VERIFIER, "--spec", str(B51_SPEC), "--input", str(inp), "--candidate", str(b51)))
    run(f"{name}.carrier", py(B52A_PRODUCER, "--spec", str(B52A_SPEC), "--input", str(inp), "--b5-1-artifact", str(b51), "--output", str(carrier)))
    run(f"{name}.carrierv", py(B52A_VERIFIER, "--spec", str(B52A_SPEC), "--input", str(inp), "--b5-1-artifact", str(b51), "--candidate", str(carrier)))
    run(f"{name}.b52b", py(B52B_PRODUCER, "--spec", str(B52B_SPEC), "--input", str(inp), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--output", str(b52)))
    out = run(f"{name}.b52bv", py(B52B_VERIFIER, "--spec", str(B52B_SPEC), "--input", str(inp), "--b5-1-artifact", str(b51), "--carrier", str(carrier), "--candidate", str(b52)))
    if "INDEPENDENT_VERIFIER_V1_1 = PASS" not in out:
        raise AssertionError(f"{name}: B5.2B verifier marker missing")


def build_b51_open() -> None:
    inp = TMP / "b5-open.json"
    b51 = TMP / "b5-open.b51.json"
    out = run("b5-open.b51", py(B51_PRODUCER, "--spec", str(B51_SPEC), "--input", str(inp), "--output", str(b51)))
    if "CAPABILITY_STATUS = OPEN_RUNTIME_CAPABILITY" not in out:
        raise AssertionError("B5 OPEN fixture did not open")
    run("b5-open.b51v", py(B51_VERIFIER, "--spec", str(B51_SPEC), "--input", str(inp), "--candidate", str(b51)))


def build_b54(name: str, *, raw_name: str | None = None, trellis_work_cap: int | None = None, open_b51: bool = False) -> None:
    r = raw_name or name
    inp = TMP / f"{r}.json"
    b51 = TMP / f"{r}.b51.json"
    out = TMP / f"{name}.b54.json"
    args = ["--spec", str(B54_SPEC), "--input", str(inp), "--b5-1-artifact", str(b51), "--output", str(out)]
    vargs = ["--spec", str(B54_SPEC), "--carrier-spec", str(B52A_SPEC), "--b5-2b-spec", str(B52B_SPEC), "--b5-2b-admission", str(B52B_RECEIPT), "--b5-3-admission", str(B53_RECEIPT), "--input", str(inp), "--b5-1-artifact", str(b51), "--candidate", str(out)]
    if not open_b51:
        args += ["--carrier", str(TMP / f"{r}.carrier.json"), "--b5-2b-artifact", str(TMP / f"{r}.b52b.json")]
        vargs += ["--carrier", str(TMP / f"{r}.carrier.json"), "--b5-2b-artifact", str(TMP / f"{r}.b52b.json")]
    if trellis_work_cap is not None:
        args += ["--trellis-work-cap", str(trellis_work_cap)]
        vargs += ["--trellis-work-cap", str(trellis_work_cap)]
    run(f"{name}.b54", py(B54_PRODUCER, *args))
    outlog = run(f"{name}.b54v", py(B54_VERIFIER, *vargs))
    if "INDEPENDENT_VERIFIER_V1_1 = PASS" not in outlog:
        raise AssertionError(f"{name}: B5.4 verifier marker missing")


def subject(name: str, raw_name: str | None = None, caps: dict | None = None, open_b51: bool = False):
    r = raw_name or name
    result = {
        "raw": load(TMP / f"{r}.json"),
        "b51": load(TMP / f"{r}.b51.json"),
        "candidate": load(TMP / f"{name}.b54.json"),
        "caps": caps or DEFAULT_CAPS,
    }
    if not open_b51:
        result["carrier"] = load(TMP / f"{r}.carrier.json")
        result["b52"] = load(TMP / f"{r}.b52b.json")
    return result


def check_controls() -> tuple[dict, dict]:
    p = lambda name: load(TMP / f"{name}.b54.json")["proof_payload"]
    sat, unsat, hopen, opq, inc, empty, opened, basis = [p(n) for n in ("sat", "unsat", "hist-open", "opaque", "inconsistent", "empty", "b5-open", "basis-order")]
    assert sat["c047_result"] == "SAT" and sat["historical_phase_a_verifier_pass"] is True
    assert unsat["c047_result"] == "UNSAT" and unsat["historical_phase_a_verifier_pass"] is True
    assert str(hopen["c047_result"]).startswith("OPEN_") and hopen["rebound_status"] == "PHASE_A_C047_REPLAY_OPEN"
    assert opq["rebound_status"] == "OPEN_AFFINE_REBOUND_BINDING" and opq["c047_result"] == "NOT_ESTABLISHED"
    assert inc["rebound_status"] == "OPEN_NONBIJECTIVE_AFFINE_NORMALIZATION" and inc["c047_result"] == "NOT_ESTABLISHED"
    assert empty["rebound_status"] == "NOT_APPLICABLE_NO_FOUND_LAYOUT" and empty["c047_result"] == "NOT_ESTABLISHED_DEFER_TO_B5_3"
    assert opened["rebound_status"] == "NOT_APPLICABLE_OPEN_RUNTIME" and opened["c047_result"] == "NOT_ESTABLISHED"
    assert len(unsat["phase_a_factor_bijection"]) == 2
    assert unsat["phase_a_factor_bijection"][0]["phase_a_input_position"] != unsat["phase_a_factor_bijection"][1]["phase_a_input_position"]
    rec = basis["phase_a_factor_bijection"][0]
    assert rec["semantic_normal_space_equal"] is True and rec["raw_list_byte_equal"] is False
    assert sat["authority_policy"]["b5_3_no_layout_used_as_c047_unsat_premise"] is False
    assert (TMP / "sat.b51.json").read_bytes() == (TMP / "sat-reordered.b51.json").read_bytes()
    assert (TMP / "sat.carrier.json").read_bytes() == (TMP / "sat-reordered.carrier.json").read_bytes()
    assert (TMP / "sat.b52b.json").read_bytes() == (TMP / "sat-reordered.b52b.json").read_bytes()
    assert (TMP / "sat.b54.json").read_bytes() == (TMP / "sat-reordered.b54.json").read_bytes()
    return sat, unsat


def run_tampers() -> tuple[int, int]:
    hist_caps = {**DEFAULT_CAPS, "trellis_work_cap": 0}
    subjects = {
        "sat": subject("sat"),
        "unsat": subject("unsat"),
        "hist_open": subject("hist-open", "sat", hist_caps),
        "opaque": subject("opaque"),
        "inconsistent": subject("inconsistent"),
        "empty": subject("empty"),
        "b5_open": subject("b5-open", open_b51=True),
        "basis_order": subject("basis-order"),
    }
    return v11.tamper_suite(subjects, load(B54_SPEC), load(B52A_SPEC), load(B52B_SPEC), load(B52B_RECEIPT), load(B53_RECEIPT), DEFAULT_CAPS)


def freeze_receipt(sat: dict, unsat: dict, tampers: tuple[int, int]) -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    for path in TMP.glob("*.b54.json"):
        shutil.copy2(path, EVIDENCE / path.name)
    for path in TMP.glob("*.b54v.log"):
        shutil.copy2(path, EVIDENCE / path.name)
    amendment = load(B54_AMENDMENT)
    receipt = {
        "schema": "janus.c049_1.b5_4.corrected_discovery_c047_rebound_exact_head_candidate_receipt.v1_1",
        "proof_head": os.environ["PROOF_HEAD"],
        "bindings": {
            "base_spec_git_blob": git_blob(B54_SPEC),
            "amendment_git_blob": git_blob(B54_AMENDMENT),
            "v1_failed_producer_git_blob": git_blob(ROOT / "janus_c049_1_b5_4_corrected_discovery_c047_rebound.py"),
            "v1_1_producer_git_blob": git_blob(B54_PRODUCER),
            "v1_independent_verifier_git_blob": git_blob(ROOT / "janus_c049_1_b5_4_corrected_discovery_c047_rebound_verifier.py"),
            "v1_1_independent_verifier_git_blob": git_blob(B54_VERIFIER),
            "b5_2b_admission_receipt_git_blob": git_blob(B52B_RECEIPT),
            "b5_3_admission_receipt_git_blob": git_blob(B53_RECEIPT),
        },
        "authority_correction": amendment["authority_correction"],
        "negative_provenance": amendment["negative_provenance"],
        "controls": {
            "sat": {"sha256": sha(TMP / "sat.b54.json"), "semantic_digest": load(TMP / "sat.b54.json")["semantic_digest"], "c047_result": "SAT"},
            "unsat": {"sha256": sha(TMP / "unsat.b54.json"), "semantic_digest": load(TMP / "unsat.b54.json")["semantic_digest"], "c047_result": "UNSAT"},
            "historical_open": {"sha256": sha(TMP / "hist-open.b54.json"), "semantic_digest": load(TMP / "hist-open.b54.json")["semantic_digest"], "c047_result": load(TMP / "hist-open.b54.json")["proof_payload"]["c047_result"]},
            "opaque": {"sha256": sha(TMP / "opaque.b54.json"), "status": "OPEN_AFFINE_REBOUND_BINDING"},
            "inconsistent": {"sha256": sha(TMP / "inconsistent.b54.json"), "status": "OPEN_NONBIJECTIVE_AFFINE_NORMALIZATION"},
            "empty": {"sha256": sha(TMP / "empty.b54.json"), "status": "NOT_APPLICABLE_NO_FOUND_LAYOUT"},
            "b5_open": {"sha256": sha(TMP / "b5-open.b54.json"), "status": "NOT_APPLICABLE_OPEN_RUNTIME"},
            "basis_order": {"sha256": sha(TMP / "basis-order.b54.json"), "semantic_equal": True, "raw_byte_equal": False},
        },
        "checks": {
            "b5_1_b5_2a_b5_2b_rebuild": "PASS",
            "affine_rref_rebound": "PASS",
            "factor_id_bijection": "PASS",
            "phase_a_cut_recomputation": "PASS",
            "historical_phase_a_verifier_return_required_true": "PASS",
            "sat_control": "PASS",
            "unsat_control": "PASS",
            "historical_open_propagation": "PASS",
            "opaque_open": "PASS",
            "inconsistent_open": "PASS",
            "empty_not_applicable": "PASS",
            "b5_open_not_applicable": "PASS",
            "presentation_order_byte_identity": "PASS",
            "semantic_not_byte_space_equality": "PASS",
            "tampers_rejected": f"{tampers[0]}/{tampers[1]}",
            "b5_3_used_as_c047_unsat_premise": False,
        },
        "formal_admission": "BLOCKED_PENDING_REVIEW",
        "c047_result_admitted": False,
        "affine_instance_sat_or_unsat_admitted": False,
        "all_input_termination": "NOT_ESTABLISHED",
        "polynomial_runtime": "NOT_ESTABLISHED",
        "b5_complete": False,
        "p_vs_np": "OPEN",
    }
    dump(EVIDENCE / "exact-head-receipt-v11.json", receipt)


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    write_controls()
    for name in ("sat", "sat-reordered", "unsat", "opaque", "inconsistent", "empty", "basis-order"):
        build_chain(name)
    build_b51_open()
    for name in ("sat", "sat-reordered", "unsat", "opaque", "inconsistent", "empty", "basis-order"):
        build_b54(name)
    build_b54("hist-open", raw_name="sat", trellis_work_cap=0)
    build_b54("b5-open", open_b51=True)
    sat, unsat = check_controls()
    tampers = run_tampers()
    if tampers != (25, 25):
        raise AssertionError(f"expected 25/25 repaired-digest tamper rejection, got {tampers}")
    freeze_receipt(sat, unsat, tampers)
    print("B5_4_V1_1_UPSTREAM_DISCOVERY_CHAIN_REBUILD = PASS")
    print("B5_4_V1_1_C047_SAT_CONTROL = PASS")
    print("B5_4_V1_1_C047_UNSAT_CONTROL = PASS")
    print("B5_4_V1_1_HISTORICAL_OPEN_PROPAGATION = PASS")
    print("B5_4_V1_1_OPAQUE_OFFSET_OPEN = PASS")
    print("B5_4_V1_1_INCONSISTENT_AFFINE_OPEN = PASS")
    print("B5_4_V1_1_EMPTY_ROOT_NOT_APPLICABLE = PASS")
    print("B5_4_V1_1_B5_OPEN_NOT_APPLICABLE = PASS")
    print("B5_4_V1_1_DUPLICATE_GEOMETRY_DISTINCT_POSITIONS = PASS")
    print("B5_4_V1_1_SEMANTIC_NOT_BYTE_NORMAL_SPACE_EQUALITY = PASS")
    print("B5_4_V1_1_PRESENTATION_ORDER_BYTE_IDENTITY = PASS")
    print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {tampers[0]}/{tampers[1]}")
    print("HISTORICAL_PHASE_A_VERIFIER_RETURN = REQUIRED_TRUE")
    print("C047_RESULT_ADMITTED = FALSE")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
