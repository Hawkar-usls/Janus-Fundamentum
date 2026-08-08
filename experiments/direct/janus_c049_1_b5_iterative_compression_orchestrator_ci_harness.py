from __future__ import annotations

import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import subprocess

import janus_c049_1_b5_iterative_compression_orchestrator as prod
import janus_c049_1_b5_iterative_compression_orchestrator_verifier as ver
from janus_c049_1_b3_expand_join_shrink_core import subspace_intersection, xor_basis

ROOT = Path("experiments/direct")
SPEC_PATH = ROOT / "C049_1_B5_ITERATIVE_COMPRESSION_ORCHESTRATOR_SPEC_V1.json"
TMP = Path("/tmp/b5-orchestrator")
EVIDENCE = Path("/tmp/b5-orchestrator-evidence")
AFF = "janus.c049_1.c047_affine_equations.v1"


def off(equations):
    return {"schema": AFF, "equations": equations}


def caps(max_boundary_dim=3):
    return {"max_boundary_dim": max_boundary_dim, "max_k": 2, "max_full_set_entries": 5000, "max_child_pairs": 100000, "max_join_paths": 500000}


def controls() -> dict[str, dict]:
    sat_factors = [
        {"id": "a", "normal_space": [1], "affine_offset": off([[1, 0]])},
        {"id": "b", "normal_space": [3], "affine_offset": off([[3, 0]])},
        {"id": "c", "normal_space": [2], "affine_offset": off([[2, 1]])},
    ]
    unsat_factors = [
        {"id": "a", "normal_space": [1], "affine_offset": off([[1, 0]])},
        {"id": "b", "normal_space": [3], "affine_offset": off([[3, 0]])},
        {"id": "c", "normal_space": [2], "affine_offset": off([[2, 0]])},
    ]
    common = {"ambient_dim": 3, "k": 1, "runtime_caps": caps(), "phase_a_caps": {}}
    sat = {**common, "factors": sat_factors, "input_order": ["a", "b", "c"]}
    sat_reordered = {**common, "factors": list(reversed(sat_factors)), "input_order": ["a", "b", "c"]}
    unsat = {**common, "factors": unsat_factors, "input_order": ["a", "b", "c"]}
    prefixneg = {
        "ambient_dim": 3, "k": 1, "runtime_caps": caps(), "phase_a_caps": {},
        "factors": [
            {"id": "a", "normal_space": [1], "affine_offset": {"opaque": "a"}},
            {"id": "b", "normal_space": [2, 4], "affine_offset": {"opaque": "b"}},
            {"id": "c", "normal_space": [3, 4], "affine_offset": {"opaque": "c"}},
            {"id": "d", "normal_space": [1], "affine_offset": {"opaque": "d"}},
        ],
        "input_order": ["a", "b", "c", "d"],
    }
    local2k = {
        "ambient_dim": 2, "k": 0, "runtime_caps": caps(2), "phase_a_caps": {},
        "factors": [
            {"id": "a", "normal_space": [1], "affine_offset": {"opaque": "a"}},
            {"id": "b", "normal_space": [2], "affine_offset": {"opaque": "b"}},
        ],
        "input_order": ["a", "b"],
    }
    b5open = {**sat, "runtime_caps": caps(0)}
    affineopen = {
        **common,
        "factors": [
            {"id": "a", "normal_space": [1], "affine_offset": {"opaque": "a"}},
            {"id": "b", "normal_space": [3], "affine_offset": {"opaque": "b"}},
            {"id": "c", "normal_space": [2], "affine_offset": {"opaque": "c"}},
        ],
        "input_order": ["a", "b", "c"],
    }
    roundcap = {**sat, "max_rounds": 2}
    dup = {
        "ambient_dim": 1, "k": 1, "runtime_caps": caps(1), "phase_a_caps": {},
        "factors": [
            {"id": "left", "normal_space": [1], "affine_offset": off([[1, 0]])},
            {"id": "right", "normal_space": [1], "affine_offset": off([[1, 1]])},
        ],
        "input_order": ["left", "right"],
    }
    return {"sat": sat, "sat-reordered": sat_reordered, "unsat": unsat, "prefixneg": prefixneg, "local2k": local2k, "b5open": b5open, "affineopen": affineopen, "roundcap": roundcap, "dup": dup}


def save(path: Path, value) -> None:
    path.write_text(json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blob(path: Path) -> str:
    return subprocess.check_output(["git", "hash-object", str(path)], text=True).strip()


def cut_width(spaces: dict[str, tuple[int, ...]], order: tuple[str, ...], d: int) -> int:
    maximum = 0
    for cut in range(len(order) + 1):
        left = xor_basis([v for fid in order[:cut] for v in spaces[fid]], d)
        right = xor_basis([v for fid in order[cut:] for v in spaces[fid]], d)
        maximum = max(maximum, len(subspace_intersection(left, right, d)))
    return maximum


def monotonicity_falsifier(raw: dict) -> int:
    d = int(raw["ambient_dim"])
    full_ids = tuple(raw["input_order"])
    prefix = full_ids[:3]
    spaces = {str(f["id"]): tuple(xor_basis(f["normal_space"], d)) for f in raw["factors"]}
    checked = 0
    for full_order in itertools.permutations(full_ids):
        induced = tuple(fid for fid in full_order if fid in set(prefix))
        if cut_width(spaces, induced, d) > cut_width(spaces, full_order, d):
            raise AssertionError("deletion monotonicity falsified")
        checked += 1
    return checked


def main() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    spec = prod.load(SPEC_PATH)
    raw_controls = controls()
    subjects: dict[str, tuple[dict, dict]] = {}
    results: dict[str, dict] = {}

    for name, raw in raw_controls.items():
        input_path = TMP / f"{name}.input.json"
        candidate_path = TMP / f"{name}.candidate.json"
        save(input_path, raw)
        candidate = prod.execute(raw, spec)
        prod.save(candidate, candidate_path)
        replay = ver.verify(candidate, raw, spec)
        subjects[name] = (candidate, raw)
        results[name] = replay
        shutil.copy2(candidate_path, EVIDENCE / candidate_path.name)
        print(name, "=", replay["terminal_class"], replay.get("c047_result"))

    assert results["sat"] == {"terminal_class": "FULL_INPUT_C047_SAT", "round_count": 3, "c047_result": "SAT", "full_discovery_no_layout_at_cap": False}
    assert results["unsat"] == {"terminal_class": "FULL_INPUT_C047_UNSAT", "round_count": 3, "c047_result": "UNSAT", "full_discovery_no_layout_at_cap": False}
    assert results["prefixneg"]["terminal_class"] == "STRICT_PREFIX_NO_LAYOUT_AT_CAP_WITH_DELETION_MONOTONICITY"
    assert results["prefixneg"]["round_count"] == 3 and results["prefixneg"]["full_discovery_no_layout_at_cap"] is True and results["prefixneg"]["c047_result"] == "NOT_ESTABLISHED"
    assert results["local2k"]["terminal_class"] == "OPEN_LOCAL_2K_CERTIFICATE_REQUIRED" and results["local2k"]["full_discovery_no_layout_at_cap"] is False
    assert results["b5open"]["terminal_class"] == "OPEN_B5_1_RUNTIME_CAPABILITY"
    assert results["affineopen"]["terminal_class"] == "OPEN_AFFINE_REBOUND_BINDING"
    assert results["roundcap"]["terminal_class"] == "OPEN_ORCHESTRATOR_ROUND_CAP" and results["roundcap"]["round_count"] == 2
    assert results["dup"]["terminal_class"] in {"FULL_INPUT_C047_SAT", "FULL_INPUT_C047_UNSAT"}
    dup_catalog = subjects["dup"][0]["proof_payload"]["canonical_factor_catalog"]
    assert len(dup_catalog) == 2 and dup_catalog[0]["normal_space"] == dup_catalog[1]["normal_space"] and dup_catalog[0]["id"] != dup_catalog[1]["id"]

    sat_bytes = (TMP / "sat.candidate.json").read_bytes()
    reordered_bytes = (TMP / "sat-reordered.candidate.json").read_bytes()
    if sat_bytes != reordered_bytes:
        raise AssertionError("catalog presentation order changed orchestrator artifact")

    checked = monotonicity_falsifier(raw_controls["prefixneg"])
    if checked != 24:
        raise AssertionError("unexpected monotonicity falsifier coverage")

    rejected, total = ver.tamper_suite(subjects, spec)
    if (rejected, total) != (27, 27):
        raise AssertionError(f"expected 27/27 tamper rejection, got {rejected}/{total}")

    receipt = {
        "schema": "janus.c049_1.b5.iterative_compression_orchestrator_exact_head_candidate_receipt.v1",
        "proof_head": os.environ["PROOF_HEAD"],
        "bindings": {
            "spec_git_blob": blob(SPEC_PATH),
            "producer_git_blob": blob(ROOT / "janus_c049_1_b5_iterative_compression_orchestrator.py"),
            "verifier_git_blob": blob(ROOT / "janus_c049_1_b5_iterative_compression_orchestrator_verifier.py"),
            "harness_git_blob": blob(ROOT / "janus_c049_1_b5_iterative_compression_orchestrator_ci_harness.py"),
        },
        "controls": {
            name: {"terminal_class": result["terminal_class"], "c047_result": result.get("c047_result"), "sha256": sha(TMP / f"{name}.candidate.json"), "semantic_digest": subjects[name][0]["semantic_digest"]}
            for name, result in results.items()
        },
        "checks": {
            "three_round_sat": "PASS",
            "three_round_unsat": "PASS",
            "strict_prefix_negative_monotonicity": "PASS",
            "bounded_full_order_monotonicity_falsifier": f"{checked}/24",
            "local_2k_without_certificate_is_open": "PASS",
            "b5_runtime_open_preserved": "PASS",
            "final_affine_open_preserved": "PASS",
            "round_cap_open_preserves_completed_rounds": "PASS",
            "catalog_presentation_order_byte_identity": "PASS",
            "duplicate_geometry_distinct_occurrences": "PASS",
            "anti_promotion_tampers_rejected": f"{rejected}/{total}",
            "b5_3_used_as_c047_unsat_premise": False,
        },
        "strict_boundary": spec["strict_boundary"],
        "formal_admission": "BLOCKED_PENDING_REVIEW",
    }
    save(EVIDENCE / "exact-head-receipt.json", receipt)

    print("B5_ORCHESTRATOR_THREE_ROUND_SAT = PASS")
    print("B5_ORCHESTRATOR_THREE_ROUND_UNSAT = PASS")
    print("B5_ORCHESTRATOR_STRICT_PREFIX_NEGATIVE = PASS")
    print("DELETION_MONOTONICITY_BOUNDED_FALSIFIER = 24/24")
    print("OPEN_LOCAL_2K_CERTIFICATE_REQUIRED = PASS")
    print("OPEN_B5_RUNTIME_PRESERVED = PASS")
    print("OPEN_FINAL_AFFINE_REBOUND_PRESERVED = PASS")
    print("OPEN_ROUND_CAP_PRESERVES_COMPLETED_EVIDENCE = PASS")
    print("CATALOG_PRESENTATION_ORDER_BYTE_IDENTITY = PASS")
    print("DUPLICATE_GEOMETRY_DISTINCT_OCCURRENCES = PASS")
    print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")
    print("B5_3_NO_LAYOUT_USED_AS_C047_UNSAT_PREMISE = FALSE")
    print("ALL_INPUT_TERMINATION = NOT_ESTABLISHED")
    print("POLYNOMIAL_RUNTIME = NOT_ESTABLISHED")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    main()
