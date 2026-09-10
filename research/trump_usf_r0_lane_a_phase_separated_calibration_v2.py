from __future__ import annotations

"""Lane-A calibration V2 execution wrapper for the sealed USF-R0 harness.

This file changes calibration assertion semantics only.  It does not implement
or modify a generator, reducer, terminal recognizer, width method, BA25 method,
truth oracle, canonical serialization, schedule, holdout policy, or H1/H2/H3
condition.  All scientific computation is delegated to byte-pinned R0 sources.

For A1-A4 the source-class predicate is evaluated on a deterministically
regenerated original canonical CNF before the canonical frozen entrypoint is
allowed to execute the scheduled instance.  The preflight original SHA-256 is
then required to equal the original SHA-256 recorded by the frozen entrypoint.
This preserves the sole canonical runtime entrypoint while placing source-class
recognition before reducer/truth information.
"""

import argparse
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

OBJECT_ID = "TRUMP_USF_R0_LANE_A_PHASE_SEPARATED_CALIBRATION_V2"
EXPECTED_LANE_A_RECORDS = 36
EXPECTED_NEW_GENERATED_REAL_INSTANCES = 35

METHODOLOGY_PATH = "research/TRUMP_USF_R0_LANE_A_INPUT_CLASS_VS_POST_REDUCER_TERMINAL_METHODOLOGICAL_SUCCESSOR_2026-09-10.json"
METHODOLOGY_BLOB = "6d8db87c7c0bc36e3e8c08d5df691714aa2448ff"
OLD_FAILURE_PATH = "research/TRUMP_USF_R0_LANE_A_CALIBRATION_DISCOVERY_FAILURE_2026-09-10.json"
OLD_FAILURE_BLOB = "97b454cefb2be61b6f0ccd021980b06831cab66d"
OLD_FAILURE_COMMIT = "8e139b1eb26a628ff8477d5cf1e984e7f7a86310"
OLD_FAILED_RUN_ID = 34502250623

ENTRYPOINT_PATH = "research/trump_usf_r0_execution_harness_frozen_entrypoint.py"
ENTRYPOINT_BLOB = "50e8eedd461b87de37385cc9f3d30ea6224909fb"
CORE_PATH = "research/trump_usf_r0_execution_harness.py"
CORE_BLOB = "ed4203bac76349ab377bb97f67bf1054d837bc96"

PINNED_SCIENTIFIC_BLOBS = {
    "GENERATOR": ("research/trump_usf_r0_frozen_generators.py", "fe33883dc08e7e1eacadf287093aa0bb1f16c19a"),
    "R37B_CONTROLLER": ("experiments/janus_trump_r37b_fixed_certified_portfolio_restart_cycle.py", "f37da1c2e1696e35695096a2c748a222af7920cc"),
    "R33": ("experiments/janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics.py", "c9234a1ef639a009cc6cb4c8a6098fd09bf9affe"),
    "R34": ("experiments/janus_trump_r34_affine_xor_terminal_against_tseitin_core.py", "7f9bec920fa47af066570d874fe9127dc4b9b968"),
    "R35": ("experiments/janus_trump_r35_nonaffine_core_freeze_structure_intake.py", "ad237e341d9659d33da0568f134815776c1f95d8"),
    "R35B": ("experiments/janus_trump_r35b_single_literal_rup_vivification.py", "259d2e38947d09b0c058963ad825a57f2e734203"),
    "R38": ("experiments/janus_trump_r38_portfolio_fixpoint_freeze_structure_intake.py", "816b53c390d78af415e580eaf358acf191796205"),
    "WIDTH": ("experiments/trump_r38_fixpoint_to_ba25_factor_graph_diagnostic.py", "ea36a6b69f8c6034aa00ae4c4217bbd4d7735750"),
    "BA25": ("research/janus_trump_r50g25ba25.py", "cad9c5f837d9d3c4e1c4bd4abef40976f2bb36ff"),
}

CADICAL_SHA256 = "d258dc72e4ec52d434a29f3b2c44dcfd800c10f898cce783f2bf6755b711fb39"
LRAT_CHECK_SHA256 = "35caa09cb09bc24178ccbddafaedac1f5774190e3ac3d8c9f03cf11e133dee8c"

SOURCE_EXPECTATIONS = {
    "A1_2SAT_EQUIVALENCE_RING": ("2CNF", "R33_IS_2CNF_ON_ORIGINAL_CANONICAL_CNF"),
    "A2_HORN_FORWARD_CHAIN": ("HORN", "R33_IS_HORN_ON_ORIGINAL_CANONICAL_CNF"),
    "A3_RENAMABLE_HORN_FLIPPED_WIDTH3": ("RENAMABLE_HORN", "R38_GENERAL_RENAMABLE_HORN_RECOGNIZER_ON_ORIGINAL_CANONICAL_CNF"),
    "A4_AFFINE_TSEITIN_CIRCULAR_LADDER": ("AFFINE_XOR_COMPLETE_CNF_BUNDLE", "R34_COMPLETE_AFFINE_CNF_RECOGNITION_ON_ORIGINAL_CANONICAL_CNF"),
}
A5_FAMILY = "A5_HISTORICAL_R38"
A5_SOURCE_COMMIT = "0b941a484143aa130bad9f7bdf9ca94fbbff79cb"
A5_EXPECTED_INTERNAL_RESIDUAL_SHA256 = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"
A5_EXPECTED_WIDTH_BEFORE = [12, 19]
A5_EXPECTED_WIDTH_AFTER = [6, 8]

PHASE_SEPARATION_LAW = "SOURCE_MEMBERSHIP_PERP_POST_REDUCTION_TERMINAL_LABEL_SUBJECT_TO_EXACT_TRANSFORMATION_SOUNDNESS"
SOURCE_CLASS_LABEL_EQUALS_POST_REDUCER_TERMINAL_LABEL_REQUIRED = False

V2_CAUSAL_TRACE = [
    "SCHEDULED_INSTANCE_ID",
    "GENERATE_ORIGINAL_FOR_SOURCE_PHASE_WITH_FROZEN_GENERATOR",
    "CANONICALIZE_ORIGINAL_WITH_FROZEN_SERIALIZATION",
    "FREEZE_ORIGINAL_CNF_SHA256_FOR_SOURCE_PHASE",
    "SOURCE_CLASS_CHECK_ORIGINAL_CNF_NO_TRUTH",
    "RUN_CANONICAL_FROZEN_ENTRYPOINT_AND_ASSERT_IDENTICAL_ORIGINAL_SHA256",
    "RUN_FROZEN_REDUCER",
    "FREEZE_RESIDUAL_SHA256",
    "WIDTH_POST_TERMINAL_BA25_DIAGNOSTICS",
    "TRUTH_ORACLE_LAST_INSIDE_FROZEN_ENTRYPOINT",
]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")


def assert_all_pins(root: Path) -> dict[str, dict[str, str]]:
    pins = {
        "METHODOLOGICAL_SUCCESSOR": (METHODOLOGY_PATH, METHODOLOGY_BLOB),
        "OLD_FAILED_R0_RECEIPT": (OLD_FAILURE_PATH, OLD_FAILURE_BLOB),
        "CANONICAL_ENTRYPOINT": (ENTRYPOINT_PATH, ENTRYPOINT_BLOB),
        "CORE_HARNESS": (CORE_PATH, CORE_BLOB),
        **PINNED_SCIENTIFIC_BLOBS,
    }
    out = {}
    for role, (rel, expected) in pins.items():
        observed = git_blob_sha1(root / rel)
        if observed != expected:
            raise RuntimeError(f"PINNED_BLOB_DRIFT:{role}:expected={expected}:observed={observed}")
        out[role] = {"path": rel, "expected_git_blob": expected, "observed_git_blob": observed}
    return out


def load_frozen_modules(root: Path):
    for rel in ("research", "experiments"):
        p = str(root / rel)
        if p not in sys.path:
            sys.path.insert(0, p)
    core = importlib.import_module("trump_usf_r0_execution_harness")
    if core.git_blob_sha1(root / CORE_PATH) != CORE_BLOB:
        raise RuntimeError("CORE_BLOB_DRIFT_AFTER_IMPORT")
    assertions, gen, r33, r34, _r35, _r35b, r38, _width, _ba25 = core.load_modules(root)
    return core, gen, r33, r34, r38, assertions


def source_class_check(gen, r33, r34, r38, schedule_record, out_dir: Path, index: int) -> dict:
    family = schedule_record.family_id
    if family == A5_FAMILY:
        return {
            "applicable": False,
            "family_id": family,
            "reason": "A5_SEALED_HISTORICAL_REPLAY_NOT_A_SOURCE_CLASS_POSITIVE_CONTROL",
            "SOURCE_CLASS_EXPECTATION_PASS": None,
            "truth_or_solver_output_consumed": False,
        }
    if family not in SOURCE_EXPECTATIONS:
        raise RuntimeError(f"UNEXPECTED_LANE_A_FAMILY_FOR_SOURCE_CHECK:{family}")

    generated = gen.generate(schedule_record)
    original = gen.canonical_formula(generated.formula)
    original_sha = gen.canonical_dimacs_sha256(original)
    c, l, v = gen.formula_counts(original)
    expected_class, authority = SOURCE_EXPECTATIONS[family]

    if family == "A1_2SAT_EQUIVALENCE_RING":
        full = {"recognized": bool(r33.is_2cnf(original)), "predicate": "r33.is_2cnf"}
    elif family == "A2_HORN_FORWARD_CHAIN":
        full = {"recognized": bool(r33.is_horn(original)), "predicate": "r33.is_horn"}
    elif family == "A3_RENAMABLE_HORN_FLIPPED_WIDTH3":
        full = r38.renamable_horn_recognition(original)
    elif family == "A4_AFFINE_TSEITIN_CIRCULAR_LADDER":
        full = r34.recognize_complete_affine_cnf(original)
    else:
        raise AssertionError("unreachable")

    recognized = bool(full.get("recognized"))
    full_blob = json_bytes(full)
    full_path = out_dir / "source_class_receipts" / f"{index:03d}.json"
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_bytes(full_blob)

    receipt = {
        "applicable": True,
        "scheduled_instance_id": schedule_record.scheduled_instance_id,
        "family_id": family,
        "SOURCE_CLASS": expected_class,
        "recognizer_authority": authority,
        "evaluation_phase": "ORIGINAL_CANONICAL_CNF_BEFORE_FROZEN_REDUCER",
        "original_canonical_dimacs_sha256_frozen_before_recognizer": original_sha,
        "original_CLV": [c, l, v],
        "recognizer_receipt_sha256": sha256_bytes(full_blob),
        "recognized": recognized,
        "SOURCE_CLASS_EXPECTATION_PASS": recognized,
        "truth_or_solver_output_consumed": False,
        "exclusive_membership_required": False,
    }
    phase_path = out_dir / "source_phase" / f"{index:03d}.json"
    phase_path.parent.mkdir(parents=True, exist_ok=True)
    phase_path.write_bytes(json_bytes(receipt))
    return receipt


def width_authority_pass(rec: dict) -> tuple[bool, list[str]]:
    reasons = []
    width = rec.get("width_evidence", {})
    for label in ("before", "after"):
        w = width.get(label, {})
        interval = w.get("treewidth_interval")
        if not isinstance(interval, list) or len(interval) != 2 or interval[0] > interval[1]:
            reasons.append(f"INVALID_TREEWIDTH_INTERVAL:{label}")
        if not w.get("independent_td_validation", {}).get("pass"):
            reasons.append(f"TD_VALIDATION_FAIL:{label}")
        if not w.get("independent_degeneracy_replay", {}).get("pass"):
            reasons.append(f"DEGENERACY_REPLAY_FAIL:{label}")
        if not w.get("independent_minor_min_width_replay", {}).get("pass"):
            reasons.append(f"MINOR_MIN_WIDTH_REPLAY_FAIL:{label}")
        if w.get("exact_treewidth") is not None and isinstance(interval, list) and len(interval) == 2 and interval[0] != interval[1]:
            reasons.append(f"EXACT_TREEWIDTH_WITHOUT_LB_EQ_UB:{label}")
    return not reasons, reasons


def reducer_replay_pass(rec: dict, expected_original_sha: str | None) -> tuple[bool, list[str]]:
    reasons = []
    red = rec.get("reducer", {})
    if red.get("source_controller_blob_asserted") != PINNED_SCIENTIFIC_BLOBS["R37B_CONTROLLER"][1]:
        reasons.append("R37B_CONTROLLER_ASSERTION_DRIFT")
    if red.get("new_reduction_rule_added") is not False:
        reasons.append("NEW_REDUCTION_RULE_FLAG_DRIFT")
    if red.get("residual_canonical_dimacs_sha256") != rec.get("residual_canonical_dimacs_sha256"):
        reasons.append("RESIDUAL_HASH_OUTER_INNER_MISMATCH")
    if expected_original_sha is not None:
        if red.get("initial_canonical_dimacs_sha256") != expected_original_sha:
            reasons.append("REDUCER_INITIAL_HASH_DIFFERS_FROM_SOURCE_PHASE")
        if rec.get("original_canonical_dimacs_sha256") != expected_original_sha:
            reasons.append("ENTRYPOINT_ORIGINAL_HASH_DIFFERS_FROM_SOURCE_PHASE")
    ledger = red.get("transformation_ledger")
    if not isinstance(ledger, list):
        reasons.append("TRANSFORMATION_LEDGER_MISSING")
    else:
        for i, row in enumerate(ledger):
            status = str(row.get("certificate_replay_status", ""))
            if not status.endswith("PASS"):
                reasons.append(f"TRANSFORMATION_CERTIFICATE_REPLAY_FAIL:{i}:{status}")
    for i, cycle in enumerate(red.get("cycles", [])):
        r34 = cycle.get("R34")
        if isinstance(r34, dict) and r34.get("recognized") is True and r34.get("certificate_replay_status") != "PASS":
            reasons.append(f"R34_CERTIFICATE_REPLAY_FAIL:cycle={i}")
    return not reasons, reasons


def post_terminal_sound(core, rec: dict, family: str) -> tuple[bool, list[str]]:
    terminal = rec.get("terminal_recognition", {})
    classification = terminal.get("classification")
    label = terminal.get("terminal")
    if family == A5_FAMILY:
        if classification != "OPEN_CORE":
            return False, ["A5_HISTORICAL_POST_REDUCER_CLASSIFICATION_DRIFT"]
        return True, []
    if classification != "TERMINAL_MEMBER":
        return False, [f"RESIDUAL_NOT_SOUND_FROZEN_TERMINAL_MEMBER:{classification}"]
    if label not in tuple(core.TERMINAL_CATALOGUE):
        return False, [f"TERMINAL_NOT_IN_FROZEN_C_USF_R0:{label}"]
    return True, []


def truth_authority_pass(rec: dict) -> tuple[bool, list[str]]:
    truth = rec.get("truth_oracle", {})
    state = truth.get("truth_state")
    if state == "SAT_WITNESS_VERIFIED":
        if truth.get("direct_original_cnf_validation", {}).get("pass") is not True:
            return False, ["SAT_STATE_WITHOUT_DIRECT_ORIGINAL_CNF_VALIDATION"]
        return True, []
    if state == "UNSAT_PROOF_VERIFIED":
        if truth.get("checker_exit_code") != 0 or truth.get("proof_exists") is not True:
            return False, ["UNSAT_STATE_WITHOUT_SUCCESSFUL_PINNED_LRAT_CHECK"]
        return True, []
    return False, [f"NONAUTHORITATIVE_TRUTH_STATE:{state}"]


def causal_firewall_pass(core, rec: dict, source: dict) -> tuple[bool, list[str]]:
    reasons = []
    if rec.get("canonical_entrypoint") != "trump_usf_r0_execution_harness_frozen_entrypoint.py":
        reasons.append("CANONICAL_ENTRYPOINT_DRIFT")
    if rec.get("causal_order") != list(core.CAUSAL_ORDER):
        reasons.append("FROZEN_ENTRYPOINT_CAUSAL_ORDER_DRIFT")
    if rec.get("truth_may_influence_generation_reducer_width_terminal_retention_or_later_seed") is not False:
        reasons.append("TRUTH_INFLUENCE_FIREWALL_DRIFT")
    if rec.get("postselection_allowed") is not False or rec.get("retained") is not True:
        reasons.append("RETENTION_OR_POSTSELECTION_FIREWALL_DRIFT")
    if source.get("truth_or_solver_output_consumed") is not False:
        reasons.append("SOURCE_CLASS_CHECK_CONSUMED_TRUTH")
    if source.get("applicable"):
        if source.get("original_canonical_dimacs_sha256_frozen_before_recognizer") != rec.get("original_canonical_dimacs_sha256"):
            reasons.append("SOURCE_PREFLIGHT_AND_ENTRYPOINT_ORIGINAL_HASH_MISMATCH")
    if rec.get("finite_experiment_is_asymptotic_authority") is not False:
        reasons.append("FINITE_TO_ASYMPTOTIC_FIREWALL_DRIFT")
    return not reasons, reasons


def a5_historical_pass(rec: dict) -> tuple[bool, list[str]]:
    reasons = []
    red = rec.get("reducer", {})
    if red.get("A5_source_commit") != A5_SOURCE_COMMIT:
        reasons.append("A5_SOURCE_COMMIT_DRIFT")
    if red.get("A5_historical_internal_residual_hash") != A5_EXPECTED_INTERNAL_RESIDUAL_SHA256:
        reasons.append("A5_INTERNAL_RESIDUAL_HASH_DRIFT")
    if rec.get("generated_real_instance_increment") != 0:
        reasons.append("A5_COUNTED_AS_NEW_REAL_GENERATION")
    if rec.get("width_evidence", {}).get("interval_before") != A5_EXPECTED_WIDTH_BEFORE:
        reasons.append("A5_WIDTH_BEFORE_DRIFT")
    if rec.get("width_evidence", {}).get("interval_after") != A5_EXPECTED_WIDTH_AFTER:
        reasons.append("A5_WIDTH_AFTER_DRIFT")
    return not reasons, reasons


def run_entrypoint(root: Path, instance_id: str, output_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / ENTRYPOINT_PATH), "--run-scheduled", instance_id, "--output", str(output_path)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def classify_successful_entrypoint_record(core, rec: dict, source: dict) -> tuple[dict, list[str]]:
    family = rec.get("instance_identity_frozen_before_solver_output", {}).get("family_id")
    expected_sha = source.get("original_canonical_dimacs_sha256_frozen_before_recognizer") if source.get("applicable") else None
    reducer_ok, reducer_reasons = reducer_replay_pass(rec, expected_sha)
    width_ok, width_reasons = width_authority_pass(rec)
    post_ok, post_reasons = post_terminal_sound(core, rec, family)
    truth_ok, truth_reasons = truth_authority_pass(rec)
    causal_ok, causal_reasons = causal_firewall_pass(core, rec, source)
    a5_ok, a5_reasons = (a5_historical_pass(rec) if family == A5_FAMILY else (True, []))

    flags = {
        "SOURCE_CLASS_EXPECTATION_PASS": source.get("SOURCE_CLASS_EXPECTATION_PASS") if source.get("applicable") else None,
        "REDUCER_CERTIFICATE_REPLAY_PASS": reducer_ok,
        "TRUTH_AUTHORITY_PASS": truth_ok,
        "WIDTH_AUTHORITY_PASS": width_ok,
        "CAUSAL_FIREWALL_PASS": causal_ok,
        "POST_REDUCER_TERMINAL_SOUND": post_ok,
        "A5_HISTORICAL_REPLAY_PASS": a5_ok if family == A5_FAMILY else None,
        "SOURCE_CLASS_LABEL_EQUALS_POST_REDUCER_TERMINAL_LABEL_REQUIRED": False,
    }
    failure_domains = []
    if source.get("applicable") and source.get("SOURCE_CLASS_EXPECTATION_PASS") is not True:
        failure_domains.append({"domain": "SOURCE_CLASS_CALIBRATION_FAILURE", "detail": ["SOURCE_CLASS_EXPECTATION_FALSE"]})
    if not reducer_ok:
        failure_domains.append({"domain": "REDUCER_REPLAY_FAILURE", "detail": reducer_reasons})
    if not post_ok:
        failure_domains.append({"domain": "POST_REDUCER_TERMINAL_CALIBRATION_FAILURE", "detail": post_reasons})
    if not truth_ok:
        failure_domains.append({"domain": "TRUTH_AUTHORITY_FAILURE", "detail": truth_reasons})
    if not width_ok:
        failure_domains.append({"domain": "WIDTH_AUTHORITY_FAILURE", "detail": width_reasons})
    if not causal_ok:
        failure_domains.append({"domain": "CAUSAL_FIREWALL_FAILURE", "detail": causal_reasons})
    if not a5_ok:
        failure_domains.append({"domain": "A5_HISTORICAL_REPLAY_FAILURE", "detail": a5_reasons})
    return flags, failure_domains


def execute_lane_a_v2(root: Path, out_dir: Path) -> dict:
    pins = assert_all_pins(root)
    core, gen, r33, r34, r38, core_assertions = load_frozen_modules(root)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "instances").mkdir(exist_ok=True)

    schedule_cp = subprocess.run(
        [sys.executable, str(root / ENTRYPOINT_PATH), "--print-schedule", "--output", str(out_dir / "FROZEN_SCHEDULE.json")],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if schedule_cp.returncode != 0:
        raise RuntimeError("FROZEN_SCHEDULE_ENTRYPOINT_FAILURE:" + schedule_cp.stderr[-2000:])
    schedule = json.loads((out_dir / "FROZEN_SCHEDULE.json").read_text(encoding="utf-8"))
    lane_a = [x for x in schedule["discovery_order"] if x.startswith("USF-R0|DISCOVERY|A|")]
    if len(lane_a) != EXPECTED_LANE_A_RECORDS:
        raise RuntimeError(f"FROZEN_LANE_A_SCHEDULE_COUNT_DRIFT:{len(lane_a)}")
    if any("|B|" in x or "|C|" in x or "|HOLDOUT|" in x for x in lane_a):
        raise RuntimeError("LANE_SCOPE_OR_HOLDOUT_VIOLATION")

    compact = []
    failures = []
    completed = 0
    generated_real = 0

    for index, instance_id in enumerate(lane_a):
        schedule_record = gen.scheduled_instance(instance_id, allow_holdout=False)
        source = source_class_check(gen, r33, r34, r38, schedule_record, out_dir, index)

        if source.get("applicable") and source.get("SOURCE_CLASS_EXPECTATION_PASS") is not True:
            failure = {
                "scheduled_instance_id": instance_id,
                "failure_domains": [{"domain": "SOURCE_CLASS_CALIBRATION_FAILURE", "detail": ["ORIGINAL_CANONICAL_CNF_NOT_IN_PREREGISTERED_SOURCE_CLASS"]}],
                "source_class": source,
                "stop_before_reducer": True,
            }
            failures.append(failure)
            compact.append(failure)
            break

        raw_path = out_dir / "instances" / f"{index:03d}.json"
        cp = run_entrypoint(root, instance_id, raw_path)
        if cp.returncode != 0:
            stderr_path = out_dir / "instances" / f"{index:03d}.stderr.txt"
            stderr_path.write_text(cp.stderr, encoding="utf-8")
            failure = {
                "scheduled_instance_id": instance_id,
                "failure_domains": [{"domain": "REDUCER_REPLAY_FAILURE", "detail": ["CANONICAL_ENTRYPOINT_NONZERO_BEFORE_ACCEPTED_RECORD", f"returncode={cp.returncode}", cp.stderr[-3000:]]}],
                "source_class": source,
                "raw_record_created": raw_path.exists(),
            }
            failures.append(failure)
            compact.append(failure)
            break

        rec = json.loads(raw_path.read_text(encoding="utf-8"))
        completed += 1
        generated_real += int(rec.get("generated_real_instance_increment", 0))
        identity = rec.get("instance_identity_frozen_before_solver_output", {})
        family = identity.get("family_id")
        if identity.get("scheduled_instance_id") != instance_id or identity.get("lane") != "A":
            failures.append({"scheduled_instance_id": instance_id, "failure_domains": [{"domain": "CAUSAL_FIREWALL_FAILURE", "detail": ["INSTANCE_IDENTITY_OR_LANE_DRIFT"]}]})
            break

        flags, failure_domains = classify_successful_entrypoint_record(core, rec, source)
        raw_hash = sha256_bytes(raw_path.read_bytes())
        compact_row = {
            "scheduled_instance_id": instance_id,
            "family_id": family,
            "cohort": identity.get("cohort"),
            "variant": identity.get("variant"),
            "frozen_size_parameter": identity.get("frozen_size_parameter"),
            "frozen_seed_string": identity.get("frozen_seed_string"),
            "SOURCE_CLASS": source,
            "REDUCTION_OUTCOME": {
                "initial_canonical_dimacs_sha256": rec.get("reducer", {}).get("initial_canonical_dimacs_sha256"),
                "residual_canonical_dimacs_sha256": rec.get("residual_canonical_dimacs_sha256"),
                "initial_CLV": rec.get("reducer", {}).get("initial_CLV"),
                "residual_CLV": rec.get("reducer", {}).get("residual_CLV"),
                "terminal_status_from_reducer": rec.get("reducer", {}).get("terminal_status_from_reducer"),
                "cycle_count": rec.get("reducer", {}).get("cycle_count"),
                "transformation_count": len(rec.get("reducer", {}).get("transformation_ledger", [])),
            },
            "POST_REDUCER_TERMINAL_CLASS": rec.get("terminal_recognition"),
            "width_interval_before": rec.get("width_evidence", {}).get("interval_before"),
            "width_interval_after": rec.get("width_evidence", {}).get("interval_after"),
            "BA25_status": rec.get("BA25_diagnostic", {}).get("status"),
            "truth_state": rec.get("truth_oracle", {}).get("truth_state"),
            "truth_authority_receipt": {
                "direct_original_cnf_validation": rec.get("truth_oracle", {}).get("direct_original_cnf_validation"),
                "proof_exists": rec.get("truth_oracle", {}).get("proof_exists"),
                "proof_sha256": rec.get("truth_oracle", {}).get("proof_sha256"),
                "checker_exit_code": rec.get("truth_oracle", {}).get("checker_exit_code"),
            },
            "pass_flags": flags,
            "failure_domains": failure_domains,
            "raw_instance_record_sha256": raw_hash,
            "finite_experiment_is_asymptotic_authority": False,
        }
        compact.append(compact_row)
        if failure_domains:
            failures.append({"scheduled_instance_id": instance_id, "failure_domains": failure_domains, "raw_instance_record_sha256": raw_hash})
            break

    passed = (
        not failures
        and completed == EXPECTED_LANE_A_RECORDS
        and generated_real == EXPECTED_NEW_GENERATED_REAL_INSTANCES
        and sum(1 for row in compact if row.get("family_id") == A5_FAMILY) == 1
    )

    summary = {
        "schema": OBJECT_ID + "_RESULT",
        "version": "2.0",
        "status": "LANE_A_PHASE_SEPARATED_CALIBRATION_V2_PASSED" if passed else "LANE_A_PHASE_SEPARATED_CALIBRATION_V2_FAILURE_STOPPED",
        "scientific_role": "REAL_EXPERIMENT_PIPELINE_CALIBRATION_ONLY_NOT_STRUCTURAL_FUNNEL_UNIVERSAL_EVIDENCE",
        "methodological_successor_blob": METHODOLOGY_BLOB,
        "phase_separation_law": PHASE_SEPARATION_LAW,
        "source_post_terminal_label_equality_required": False,
        "old_failed_execution_preserved": {
            "run_id": OLD_FAILED_RUN_ID,
            "receipt_commit": OLD_FAILURE_COMMIT,
            "receipt_blob": OLD_FAILURE_BLOB,
            "status_remains": "FAILED_UNDER_ORIGINAL_CONTRACT",
            "classification": "METHODOLOGICAL_CALIBRATION_ASSERTION_SCOPE_FAILURE",
            "retroactive_reinterpretation": False,
        },
        "workflow_commit": os.environ.get("GITHUB_SHA"),
        "run_id": int(os.environ["GITHUB_RUN_ID"]) if os.environ.get("GITHUB_RUN_ID") else None,
        "pinned_source_assertions": pins,
        "core_source_assertions": core_assertions,
        "canonical_entrypoint_blob": ENTRYPOINT_BLOB,
        "causal_trace_v2": V2_CAUSAL_TRACE,
        "scheduled_lane_a_discovery_count": EXPECTED_LANE_A_RECORDS,
        "completed_lane_a_records": completed,
        "generated_real_USF_instances_this_v2_gate": generated_real,
        "A5_historical_replay_count": sum(1 for row in compact if row.get("family_id") == A5_FAMILY),
        "instances": compact,
        "failures": failures,
        "LANE_A_PHASE_SEPARATED_CALIBRATION_V2_PASSED": passed,
        "LANE_A_EXECUTION_COMPLETE": passed,
        "LANE_B_EXECUTION_STARTED": False,
        "LANE_C_EXECUTION_STARTED": False,
        "HOLDOUT_EXECUTION_STARTED": False,
        "PRIMARY_BLOCKER": "UNIVERSAL_RESIDUAL_STRUCTURAL_FUNNEL_THEOREM",
        "H1": "OPEN",
        "H2": "OPEN",
        "H3": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "BA26_STARTED": False,
        "successful_scope_if_passed": "REAL_EXPERIMENT_PIPELINE_CALIBRATED",
        "universal_structural_funnel_supported_by_this_gate": False,
        "stop": "STOP_AFTER_LANE_A_PHASE_SEPARATED_CALIBRATION_V2_NO_LANE_B_NO_LANE_C_NO_HOLDOUT_NO_BA26",
    }
    result_bytes = json_bytes(summary)
    (out_dir / "LANE_A_PHASE_SEPARATED_CALIBRATION_V2_RESULT.json").write_bytes(result_bytes)
    (out_dir / "LANE_A_PHASE_SEPARATED_CALIBRATION_V2_RESULT.sha256").write_text(
        sha256_bytes(result_bytes) + "  LANE_A_PHASE_SEPARATED_CALIBRATION_V2_RESULT.json\n", encoding="utf-8"
    )
    print("LANE_A_PHASE_SEPARATED_CALIBRATION_V2_RESULT_SHA256=" + sha256_bytes(result_bytes))
    print("LANE_A_V2_COMPLETED_RECORDS=" + str(completed))
    print("LANE_A_V2_GENERATED_REAL_INSTANCES=" + str(generated_real))
    print("LANE_A_PHASE_SEPARATED_CALIBRATION_V2_PASSED=" + str(passed).lower())
    return summary


def verify_contract_only(root: Path) -> dict:
    pins = assert_all_pins(root)
    return {
        "object_id": OBJECT_ID,
        "pins_pass": True,
        "pins": pins,
        "phase_separation_law": PHASE_SEPARATION_LAW,
        "source_post_terminal_label_equality_required": SOURCE_CLASS_LABEL_EQUALS_POST_REDUCER_TERMINAL_LABEL_REQUIRED,
        "expected_lane_a_records": EXPECTED_LANE_A_RECORDS,
        "lane_b_authorized": False,
        "lane_c_authorized": False,
        "holdout_authorized": False,
        "BA26_authorized": False,
        "real_instance_executed": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output-dir")
    parser.add_argument("--verify-contract-only", action="store_true")
    parser.add_argument("--execute-lane-a-v2", action="store_true")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.verify_contract_only:
        print(json.dumps(verify_contract_only(root), indent=2, sort_keys=True))
        return
    if not args.execute_lane_a_v2:
        raise SystemExit("INERT: choose --verify-contract-only or explicitly --execute-lane-a-v2")
    if not args.output_dir:
        raise SystemExit("--output-dir is required for execution")
    execute_lane_a_v2(root, Path(args.output_dir).resolve())


if __name__ == "__main__":
    main()
