from __future__ import annotations

"""TRUMP USF R0 Lane-B adversarial general 3CNF discovery executor.

This append-only executor runs only the already-frozen Lane-B DISCOVERY schedule.
All scientific modules are byte-pinned and unchanged. The executor supplies only
provenance/error-domain plumbing and the already-frozen incidence->BA25 factor-TD
width-domain binding required after the Lane-A V3 calibration.
"""

import argparse
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import sys
import traceback
from typing import Any

OBJECT_ID = "TRUMP_USF_R0_LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY"
EXPECTED_RECORDS = 14
EXPECTED_FAMILY = "B_HASHED_REGULAR_3CNF_D15"
EXPECTED_SIZES = (48, 72, 96, 144, 192, 288, 384)
EXPECTED_COHORTS = ("B1_BALANCED_BLIND", "B2_HASH_PLANTED_SAT")
FROZEN_SEED = "JANUS-USF-R0-LANE-B-D15"

LANE_A_V3_COMPLETION = (
    "research/TRUMP_USF_R0_LANE_A_PHASE_AND_WIDTH_SEPARATED_CALIBRATION_V3_COMPLETION_2026-09-10.json",
    "9a998aac58c415d5b6d94e9bc1992c4d33b5065a",
)
WIDTH_SUCCESSOR = (
    "research/TRUMP_USF_R0_INCIDENCE_WIDTH_VS_BA25_FACTOR_TD_WIDTH_BINDING_METHODOLOGICAL_SUCCESSOR_2026-09-10.json",
    "9b412cbbef47738ff80fa28355eed42bcd5694c6",
)
ENTRYPOINT = (
    "research/trump_usf_r0_execution_harness_frozen_entrypoint.py",
    "50e8eedd461b87de37385cc9f3d30ea6224909fb",
)
CORE = (
    "research/trump_usf_r0_execution_harness.py",
    "ed4203bac76349ab377bb97f67bf1054d837bc96",
)
SCI = {
    "GENERATOR": ("research/trump_usf_r0_frozen_generators.py", "fe33883dc08e7e1eacadf287093aa0bb1f16c19a"),
    "R37B": ("experiments/janus_trump_r37b_fixed_certified_portfolio_restart_cycle.py", "f37da1c2e1696e35695096a2c748a222af7920cc"),
    "R33": ("experiments/janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics.py", "c9234a1ef639a009cc6cb4c8a6098fd09bf9affe"),
    "R34": ("experiments/janus_trump_r34_affine_xor_terminal_against_tseitin_core.py", "7f9bec920fa47af066570d874fe9127dc4b9b968"),
    "R35": ("experiments/janus_trump_r35_nonaffine_core_freeze_structure_intake.py", "ad237e341d9659d33da0568f134815776c1f95d8"),
    "R35B": ("experiments/janus_trump_r35b_single_literal_rup_vivification.py", "259d2e38947d09b0c058963ad825a57f2e734203"),
    "R38": ("experiments/janus_trump_r38_portfolio_fixpoint_freeze_structure_intake.py", "816b53c390d78af415e580eaf358acf191796205"),
    "WIDTH_EXTENDER": ("experiments/trump_r38_fixpoint_to_ba25_factor_graph_diagnostic.py", "ea36a6b69f8c6034aa00ae4c4217bbd4d7735750"),
    "BA25": ("research/janus_trump_r50g25ba25.py", "cad9c5f837d9d3c4e1c4bd4abef40976f2bb36ff"),
}

LIFT_LAW = "BA25_FACTOR_TD_VERIFIED_WIDTH == max(INCIDENCE_TD_VERIFIED_UB, 1)"
CAUSAL_ORDER = (
    "SCHEDULED_INSTANCE_ID",
    "GENERATE",
    "CANONICALIZE",
    "FREEZE_ORIGINAL_CNF_SHA256",
    "RUN_FROZEN_REDUCER",
    "CANONICALIZE_RESIDUAL",
    "FREEZE_RESIDUAL_SHA256",
    "MEASURE_INCIDENCE_WIDTH",
    "TERMINAL_RECOGNITION",
    "CONSTRUCT_BA25_FACTOR_GRAPH_AND_TD",
    "INDEPENDENTLY_VALIDATE_FACTOR_TD_AND_MEASURE_WIDTH",
    "VERIFY_FROZEN_TD_LIFT_RELATION",
    "BA25_DIAGNOSTIC_IF_RESOURCE_GUARD_ALLOWS",
    "TRUTH_ORACLE_LAST",
)
PIPELINE_FAILURE_DOMAINS = (
    "GENERATOR_INTEGRITY_FAILURE",
    "FROZEN_BLOB_MISMATCH",
    "REDUCER_REPLAY_FAILURE",
    "INCIDENCE_WIDTH_AUTHORITY_FAILURE",
    "BA25_FACTOR_TD_BINDING_FAILURE",
    "BA25_DIAGNOSTIC_FAILURE",
    "TERMINAL_RECOGNIZER_INTEGRITY_FAILURE",
    "TRUTH_AUTHORITY_FAILURE",
    "B2_PLANTED_SAT_TRUTH_CONTRADICTION",
    "CAUSAL_FIREWALL_FAILURE",
)

class StageFailure(RuntimeError):
    def __init__(self, domain: str, stage: str, detail: Any):
        super().__init__(f"{domain}:{stage}:{detail}")
        self.domain = domain
        self.stage = stage
        self.detail = detail

def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def json_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def assert_pins(root: Path) -> dict[str, dict[str, str]]:
    pins = {
        "LANE_A_V3_COMPLETION": LANE_A_V3_COMPLETION,
        "WIDTH_SUCCESSOR": WIDTH_SUCCESSOR,
        "CANONICAL_ENTRYPOINT": ENTRYPOINT,
        "CORE_HARNESS": CORE,
        **SCI,
    }
    out = {}
    for role, (rel, expected) in pins.items():
        path = root / rel
        if not path.is_file():
            raise StageFailure("FROZEN_BLOB_MISMATCH", "PIN_ASSERTION", f"MISSING:{role}:{rel}")
        observed = git_blob_sha1(path)
        if observed != expected:
            raise StageFailure(
                "FROZEN_BLOB_MISMATCH",
                "PIN_ASSERTION",
                {"role": role, "expected": expected, "observed": observed},
            )
        out[role] = {"path": rel, "expected_git_blob": expected, "observed_git_blob": observed}
    return out

def load_modules(root: Path):
    for rel in ("research", "experiments"):
        s = str(root / rel)
        if s not in sys.path:
            sys.path.insert(0, s)
    core = importlib.import_module("trump_usf_r0_execution_harness")
    entry = importlib.import_module("trump_usf_r0_execution_harness_frozen_entrypoint")
    assertions, gen, r33, r34, r35, r35b, r38, width, ba25 = core.load_modules(root)
    return core, entry, gen, r33, r34, r35, r35b, r38, width, ba25, assertions

def frozen_lane_b_schedule(gen):
    lane_b = [r for r in gen.DISCOVERY_SCHEDULE if r.lane == "B"]
    expected = []
    for n in EXPECTED_SIZES:
        for cohort in EXPECTED_COHORTS:
            expected.append(f"USF-R0|DISCOVERY|B|{EXPECTED_FAMILY}|{cohort}|n={n}")
    actual = [r.scheduled_instance_id for r in lane_b]
    if actual != expected:
        raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "FROZEN_LANE_B_SCHEDULE", {"expected": expected, "actual": actual})
    if len(lane_b) != EXPECTED_RECORDS:
        raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "FROZEN_LANE_B_SCHEDULE", f"COUNT:{len(lane_b)}")
    for r in lane_b:
        if r.phase != "DISCOVERY" or r.family_id != EXPECTED_FAMILY or r.frozen_seed_string != FROZEN_SEED:
            raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "FROZEN_LANE_B_SCHEDULE", repr(r))
    return lane_b

def generator_preflight(gen, record) -> tuple[Any, dict]:
    try:
        generated = gen.generate(record)
    except Exception as exc:
        raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "GENERATE", f"{type(exc).__name__}:{exc}") from exc
    original = gen.canonical_formula(generated.formula)
    original_sha = gen.canonical_dimacs_sha256(original)
    c, l, v = gen.formula_counts(original)
    n = int(record.size_parameter)
    if (c, l, v) != (5 * n, 15 * n, n):
        raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "GENERATOR_COUNTS", {"observed": [c, l, v], "expected": [5 * n, 15 * n, n]})
    if any(len(clause) != 3 for clause in original):
        raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "CLAUSE_WIDTH", "NON_WIDTH_3_CLAUSE")
    degree = {x: 0 for x in range(1, n + 1)}
    for clause in original:
        seen = set()
        for lit in clause:
            x = abs(lit)
            if x in seen:
                raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "SIMPLE_TRIPLE", {"clause": clause})
            seen.add(x)
            if x not in degree:
                raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "VARIABLE_RANGE", x)
            degree[x] += 1
    if set(degree.values()) != {15}:
        raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "VARIABLE_DEGREE_15", {"degree_histogram": {str(k): list(degree.values()).count(k) for k in sorted(set(degree.values()))}})
    constructional = None
    if record.cohort == "B2_HASH_PLANTED_SAT":
        plant = {x: bool(int(gen.sha256_text(f"JANUS-B2-PLANT|{n}|{x-1}")[-1], 16) & 1) for x in range(1, n + 1)}
        bad = [i for i, clause in enumerate(original, 1) if not any(plant[abs(lit)] == (lit > 0) for lit in clause)]
        if bad:
            raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "B2_CONSTRUCTIONAL_PLANT_REPLAY", {"bad_clause_indices_1_based": bad})
        constructional = {"planted_assignment_replay_satisfies_original": True, "truth_authority": False, "role": "GENERATOR_CONSTRUCTION_INTEGRITY_ONLY"}
    return original, {
        "scheduled_instance_id": record.scheduled_instance_id,
        "cohort": record.cohort,
        "n": n,
        "frozen_seed_string": record.frozen_seed_string,
        "generator_integrity_status": generated.generator_integrity_status,
        "original_canonical_dimacs_sha256": original_sha,
        "original_CLV": [c, l, v],
        "clause_width_all_3": True,
        "variable_degree_all_15": True,
        "no_reseed": True,
        "B2_constructional_plant_replay": constructional,
    }

def factor_td_binding(core, width, ba25, width_private):
    u_i = width_private["verified_td_upper_bound"]
    orig_vars = width_private["_orig_vars"]
    clauses = width_private["_clauses"]
    inst = ba25.embed_cnf(len(orig_vars), clauses)
    factor_vertices, factor_edges = ba25.factor_graph(inst)
    factor_td = width.extend_incidence_td_to_ba25(width_private["_td"], len(orig_vars), len(clauses))
    independent = core.independent_validate_td(set(factor_vertices), set(factor_edges), factor_td.bags, factor_td.edges)
    if independent.get("pass") is not True:
        raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE", "INDEPENDENT_FACTOR_TD_VALIDATION", independent)
    u_f = independent["width"]
    lift_expected = max(u_i, 1)
    if u_f != lift_expected:
        raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE", "FROZEN_EXTENDER_LIFT_RELATION", {"measured_u_F": u_f, "u_I": u_i, "expected": lift_expected})
    native_ok, native = ba25.validate_td(factor_vertices, factor_edges, factor_td, claimed_tau=u_f)
    if not native_ok:
        raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE", "BA25_NATIVE_FACTOR_TD_VALIDATION", native)
    public = {
        "INCIDENCE_TD_VERIFIED_UB": u_i,
        "BA25_FACTOR_TD_VERIFIED_WIDTH": u_f,
        "BA25_FACTOR_TD_VALIDATION_PASS": True,
        "independent_factor_td_validation": independent,
        "ba25_native_factor_td_validation": native,
        "frozen_lift_expected_width": lift_expected,
        "frozen_lift_relation": LIFT_LAW,
        "frozen_lift_relation_pass": True,
        "claimed_tau_binding": "BA25_FACTOR_TD_VERIFIED_WIDTH",
        "bare_cross_domain_tau_used": False,
    }
    private = {"inst": inst, "factor_td": factor_td, "factor_vertices": factor_vertices, "factor_edges": factor_edges}
    return public, private

def ba25_lane_b(core, ba25, r33, residual, binding, private):
    c, _, v = r33.measure(residual)
    u_f = binding["BA25_FACTOR_TD_VERIFIED_WIDTH"]
    if u_f > core.BA25_MAX_VERIFIED_TAU or v > core.BA25_MAX_RESIDUAL_VARIABLES or c > core.BA25_MAX_RESIDUAL_CLAUSES:
        return {
            "status": "NOT_RUN_RESOURCE_GUARD",
            "resource_guard_parameter_domain": "BA25_FACTOR_TD_VERIFIED_WIDTH",
            "BA25_FACTOR_TD_VERIFIED_WIDTH": u_f,
            "limits": {"BA25_FACTOR_TD_VERIFIED_WIDTH": core.BA25_MAX_VERIFIED_TAU, "variables": core.BA25_MAX_RESIDUAL_VARIABLES, "clauses": core.BA25_MAX_RESIDUAL_CLAUSES},
            "truth_authority": False,
            "scientific_data_not_pipeline_failure": True,
        }
    try:
        dp = ba25.run_dp(private["inst"], private["factor_td"], proof=False)
        if dp.get("tau") != u_f:
            raise StageFailure("BA25_DIAGNOSTIC_FAILURE", "BA25_DP_WIDTH_DOMAIN", {"reported": dp.get("tau"), "verified": u_f})
        if dp.get("state_bound") != 2 ** (u_f + 2):
            raise StageFailure("BA25_DIAGNOSTIC_FAILURE", "BA25_STATE_BOUND_DOMAIN", {"observed": dp.get("state_bound"), "u_F": u_f})
        witness = ba25.witness_receipt(private["inst"], dp.get("witness"))
        if dp.get("sat") and witness.get("direct_verify") is not True:
            raise StageFailure("BA25_DIAGNOSTIC_FAILURE", "BA25_WITNESS_REPLAY", witness)
        return {
            "status": "BA25_DIAGNOSTIC_COMPLETE",
            "resource_guard_parameter_domain": "BA25_FACTOR_TD_VERIFIED_WIDTH",
            "BA25_FACTOR_TD_VERIFIED_WIDTH": u_f,
            "peak_table_states": dp["max_states"],
            "state_bound": dp["state_bound"],
            "sat_diagnostic": dp["sat"],
            "model_count_diagnostic": dp["count"],
            "witness_receipt": witness,
            "truth_authority": False,
            "independent_truth_oracle_replaced": False,
        }
    except StageFailure:
        raise
    except Exception as exc:
        raise StageFailure("BA25_DIAGNOSTIC_FAILURE", "BA25_DIAGNOSTIC", f"{type(exc).__name__}:{exc}") from exc

def tagged(domain: str, stage: str, fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except StageFailure:
            raise
        except Exception as exc:
            raise StageFailure(domain, stage, f"{type(exc).__name__}:{exc}") from exc
    return wrapped

def run_frozen_pipeline_with_bound_factor_width(mods, instance_id: str):
    core, entry, gen, r33, r34, r35, r35b, r38, width, ba25, assertions = mods
    old = (core.run_frozen_reducer, core.terminal_recognition, core.truth_oracle, entry.width_evidence, entry.ba25_diagnostic)
    factor_holder = {}
    def width_tag(core_arg, width_arg, formula, label):
        try:
            return old[3](core_arg, width_arg, formula, label)
        except Exception as exc:
            raise StageFailure("INCIDENCE_WIDTH_AUTHORITY_FAILURE", f"MEASURE_INCIDENCE_WIDTH:{label}", f"{type(exc).__name__}:{exc}") from exc
    def ba25_tag(core_arg, ba25_arg, width_arg, r33_arg, residual, width_private):
        binding, private = factor_td_binding(core_arg, width_arg, ba25_arg, width_private)
        factor_holder["binding"] = binding
        result = ba25_lane_b(core_arg, ba25_arg, r33_arg, residual, binding, private)
        return {"factor_td_binding": binding, **result}
    core.run_frozen_reducer = tagged("REDUCER_REPLAY_FAILURE", "RUN_FROZEN_REDUCER", old[0])
    core.terminal_recognition = tagged("TERMINAL_RECOGNIZER_INTEGRITY_FAILURE", "TERMINAL_RECOGNITION", old[1])
    core.truth_oracle = tagged("TRUTH_AUTHORITY_FAILURE", "TRUTH_ORACLE", old[2])
    entry.width_evidence = width_tag
    entry.ba25_diagnostic = ba25_tag
    try:
        record = entry.run_scheduled_instance(instance_id, Path(__file__).resolve().parents[1], execute_truth=True)
    finally:
        core.run_frozen_reducer, core.terminal_recognition, core.truth_oracle, entry.width_evidence, entry.ba25_diagnostic = old
    if "binding" not in factor_holder:
        if record.get("truth_state") == "GENERATOR_INTEGRITY_FAIL":
            raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "GENERATE", record)
        raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE", "FACTOR_TD_BINDING", "BINDING_RECEIPT_MISSING")
    return record

def reducer_replay_check(rec: dict):
    red = rec.get("reducer", {})
    bad = []
    if red.get("source_controller_blob_asserted") != SCI["R37B"][1]: bad.append("R37B_CONTROLLER_BLOB_ASSERTION_DRIFT")
    if red.get("new_reduction_rule_added") is not False: bad.append("NEW_REDUCTION_RULE_FLAG_DRIFT")
    if red.get("initial_canonical_dimacs_sha256") != rec.get("original_canonical_dimacs_sha256"): bad.append("INITIAL_HASH_OUTER_INNER_MISMATCH")
    if red.get("residual_canonical_dimacs_sha256") != rec.get("residual_canonical_dimacs_sha256"): bad.append("RESIDUAL_HASH_OUTER_INNER_MISMATCH")
    for i, item in enumerate(red.get("transformation_ledger", [])):
        status = str(item.get("certificate_replay_status", ""))
        if not status.endswith("PASS"): bad.append(f"TRANSFORMATION_CERTIFICATE_REPLAY_FAIL:{i}:{status}")
    for i, cycle in enumerate(red.get("cycles", [])):
        r34 = cycle.get("R34")
        if isinstance(r34, dict) and r34.get("recognized") is True and r34.get("certificate_replay_status") != "PASS": bad.append(f"R34_CERTIFICATE_REPLAY_FAIL:{i}")
        r35b = cycle.get("R35B")
        if isinstance(r35b, dict) and r35b.get("whole_certificate_replay", {}).get("pass") is not True: bad.append(f"R35B_WHOLE_REPLAY_FAIL:{i}")
    if bad:
        raise StageFailure("REDUCER_REPLAY_FAILURE", "REDUCER_CERTIFICATE_REPLAY", bad)

def incidence_width_check(rec: dict):
    for label in ("before", "after"):
        evidence = rec.get("width_evidence", {}).get(label, {})
        interval = evidence.get("treewidth_interval")
        if not isinstance(interval, list) or len(interval) != 2 or interval[0] > interval[1]:
            raise StageFailure("INCIDENCE_WIDTH_AUTHORITY_FAILURE", f"INCIDENCE_INTERVAL:{label}", interval)
        if evidence.get("independent_td_validation", {}).get("pass") is not True:
            raise StageFailure("INCIDENCE_WIDTH_AUTHORITY_FAILURE", f"INCIDENCE_TD_VALIDATION:{label}", evidence.get("independent_td_validation"))
        if evidence.get("independent_degeneracy_replay", {}).get("pass") is not True:
            raise StageFailure("INCIDENCE_WIDTH_AUTHORITY_FAILURE", f"DEGENERACY_REPLAY:{label}", evidence.get("independent_degeneracy_replay"))
        if evidence.get("independent_minor_min_width_replay", {}).get("pass") is not True:
            raise StageFailure("INCIDENCE_WIDTH_AUTHORITY_FAILURE", f"MMW_REPLAY:{label}", evidence.get("independent_minor_min_width_replay"))

def terminal_integrity_check(core, rec: dict):
    terminal = rec.get("terminal_recognition", {})
    classification = terminal.get("classification")
    label = terminal.get("terminal")
    if classification == "OPEN_CORE":
        if label is not None:
            raise StageFailure("TERMINAL_RECOGNIZER_INTEGRITY_FAILURE", "OPEN_CORE_LABEL", terminal)
        return
    if classification == "TERMINAL_MEMBER" and label in tuple(core.TERMINAL_CATALOGUE):
        return
    raise StageFailure("TERMINAL_RECOGNIZER_INTEGRITY_FAILURE", "TERMINAL_CLASSIFICATION", terminal)

def truth_contract_check(rec: dict, cohort: str) -> dict:
    truth = rec.get("truth_oracle", {})
    state = truth.get("truth_state")
    if state == "SAT_WITNESS_VERIFIED":
        if truth.get("direct_original_cnf_validation", {}).get("pass") is not True:
            raise StageFailure("TRUTH_AUTHORITY_FAILURE", "SAT_DIRECT_ORIGINAL_CNF_VALIDATION", truth)
        return {"truth_state": state, "scientific_data_accepted": True, "truth_authority_complete": True, "B2_independent_SAT_witness_verified": cohort == "B2_HASH_PLANTED_SAT"}
    if state == "UNSAT_PROOF_VERIFIED":
        if truth.get("proof_exists") is not True or truth.get("checker_exit_code") != 0:
            raise StageFailure("TRUTH_AUTHORITY_FAILURE", "UNSAT_LRAT_AUTHORITY", truth)
        if cohort == "B2_HASH_PLANTED_SAT":
            raise StageFailure("B2_PLANTED_SAT_TRUTH_CONTRADICTION", "TRUTH_ORACLE", {"constructional_cohort": cohort, "independent_truth_state": state, "proof_sha256": truth.get("proof_sha256")})
        return {"truth_state": state, "scientific_data_accepted": True, "truth_authority_complete": True, "B2_independent_SAT_witness_verified": None}
    if state == "UNKNOWN_RESOURCE_LIMIT":
        return {"truth_state": state, "scientific_data_accepted": True, "truth_authority_complete": False, "B2_independent_SAT_witness_verified": False if cohort == "B2_HASH_PLANTED_SAT" else None, "note": "UNKNOWN_RESOURCE_LIMIT_IS_DATA_NOT_PIPELINE_FAILURE"}
    raise StageFailure("TRUTH_AUTHORITY_FAILURE", "TRUTH_ORACLE", truth)

def causal_firewall_check(rec: dict, preflight: dict):
    if rec.get("original_canonical_dimacs_sha256") != preflight["original_canonical_dimacs_sha256"]:
        raise StageFailure("CAUSAL_FIREWALL_FAILURE", "PREFLIGHT_TO_RUNTIME_ORIGINAL_HASH", {"preflight": preflight["original_canonical_dimacs_sha256"], "runtime": rec.get("original_canonical_dimacs_sha256")})
    if rec.get("truth_may_influence_generation_reducer_width_terminal_retention_or_later_seed") is not False:
        raise StageFailure("CAUSAL_FIREWALL_FAILURE", "TRUTH_INFLUENCE_FLAG", rec)
    if rec.get("postselection_allowed") is not False or rec.get("retained") is not True:
        raise StageFailure("CAUSAL_FIREWALL_FAILURE", "RETENTION_POSTSELECTION", rec)
    if rec.get("finite_experiment_is_asymptotic_authority") is not False:
        raise StageFailure("CAUSAL_FIREWALL_FAILURE", "FINITE_ASYMPTOTIC_FIREWALL", rec)

def contract_only(root: Path) -> dict:
    pins = assert_pins(root)
    mods = load_modules(root)
    gen = mods[2]
    schedule = frozen_lane_b_schedule(gen)
    holdout_b = [r for r in gen.HOLDOUT_SCHEDULE_FROZEN_BUT_UNOPENED if r.lane == "B"]
    if len(holdout_b) != 6:
        raise StageFailure("GENERATOR_INTEGRITY_FAILURE", "B_HOLDOUT_SCHEDULE_COUNT", len(holdout_b))
    return {
        "schema": OBJECT_ID + "_INERT_CONTRACT",
        "status": "PASS",
        "pins": pins,
        "lane_b_discovery_order": [r.scheduled_instance_id for r in schedule],
        "lane_b_discovery_count": len(schedule),
        "holdout_lane_b_count_frozen_unopened": len(holdout_b),
        "holdout_instance_executed": False,
        "lane_c_instance_executed": False,
        "BA26_started": False,
        "real_lane_b_instance_executed": False,
        "width_domains_separate": True,
        "claimed_tau_binding": "BA25_FACTOR_TD_VERIFIED_WIDTH",
        "H1": "OPEN",
        "H2": "OPEN",
        "H3": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
    }

def execute(root: Path, out_dir: Path) -> dict:
    pins = assert_pins(root)
    mods = load_modules(root)
    core, entry, gen, r33, r34, r35, r35b, r38, width, ba25, core_assertions = mods
    schedule = frozen_lane_b_schedule(gen)
    out_dir.mkdir(parents=True, exist_ok=True)
    instances_dir = out_dir / "instances"
    preflight_dir = out_dir / "generator_preflight"
    instances_dir.mkdir(exist_ok=True)
    preflight_dir.mkdir(exist_ok=True)
    rows = []
    failures = []
    completed = 0
    generated_real = 0
    for index, scheduled in enumerate(schedule):
        preflight = None
        try:
            original, preflight = generator_preflight(gen, scheduled)
            pb = json_bytes(preflight)
            (preflight_dir / f"{index:03d}.json").write_bytes(pb)
            rec = run_frozen_pipeline_with_bound_factor_width(mods, scheduled.scheduled_instance_id)
            causal_firewall_check(rec, preflight)
            reducer_replay_check(rec)
            incidence_width_check(rec)
            terminal_integrity_check(core, rec)
            binding = rec.get("BA25_diagnostic", {}).get("factor_td_binding")
            if not isinstance(binding, dict):
                raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE", "FACTOR_TD_BINDING_RECEIPT", binding)
            if binding.get("BA25_FACTOR_TD_VALIDATION_PASS") is not True:
                raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE", "FACTOR_TD_VALIDATION_PASS", binding)
            u_i = binding.get("INCIDENCE_TD_VERIFIED_UB")
            u_f = binding.get("BA25_FACTOR_TD_VERIFIED_WIDTH")
            if u_f != max(u_i, 1) or binding.get("frozen_lift_relation_pass") is not True:
                raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE", "FACTOR_TD_LIFT_RELATION", binding)
            if binding.get("bare_cross_domain_tau_used") is not False:
                raise StageFailure("BA25_FACTOR_TD_BINDING_FAILURE", "AMBIGUOUS_TAU_FIREWALL", binding)
            ba25_status = rec.get("BA25_diagnostic", {}).get("status")
            if ba25_status not in ("BA25_DIAGNOSTIC_COMPLETE", "NOT_RUN_RESOURCE_GUARD"):
                raise StageFailure("BA25_DIAGNOSTIC_FAILURE", "BA25_STATUS", rec.get("BA25_diagnostic"))
            truth_status = truth_contract_check(rec, scheduled.cohort)
            before = rec["width_evidence"]["before"]
            after = rec["width_evidence"]["after"]
            metrics = rec.get("discovery_metrics_diagnostic_only", {})
            strict_drop = bool(before["treewidth_interval"][0] > after["treewidth_interval"][1])
            if strict_drop != bool(metrics.get("width_drop_certificate_condition_LBbefore_gt_UBafter")):
                raise StageFailure("INCIDENCE_WIDTH_AUTHORITY_FAILURE", "STRICT_WIDTH_DROP_DIAGNOSTIC_BINDING", {"computed": strict_drop, "recorded": metrics})
            rec["lane_b_generator_preflight"] = preflight
            rec["LANE_B_CAUSAL_ORDER"] = list(CAUSAL_ORDER)
            rec["truth_is_last_authoritative_stage"] = True
            rec["INCIDENCE_TW_LB"] = after["treewidth_interval"][0]
            rec["INCIDENCE_TD_VERIFIED_UB"] = after["treewidth_interval"][1]
            rec["INCIDENCE_TW_INTERVAL"] = after["treewidth_interval"]
            rec["BA25_FACTOR_TD_VERIFIED_WIDTH"] = u_f
            rec["BA25_FACTOR_TD_VALIDATION_PASS"] = True
            rec["rho_n"] = metrics.get("rho_n")
            rec["r_n"] = metrics.get("r_n")
            rec["CERTIFIED_STRICT_TREEWIDTH_DECREASE_ON_THIS_TRAJECTORY"] = strict_drop
            rec["truth_contract"] = truth_status
            rec["status"] = "PASS"
            rec["H1"] = "OPEN"
            rec["H2"] = "OPEN"
            rec["H3"] = "OPEN"
            rec["SAT_IN_P"] = "NOT_PROVED"
            rec["P_VS_NP"] = "OPEN"
            rec["BA26_STARTED"] = False
            rec["finite_record_proves_H1"] = False
            rec["finite_record_proves_H3"] = False
        except Exception as exc:
            if isinstance(exc, StageFailure):
                domain, stage, detail = exc.domain, exc.stage, exc.detail
            else:
                domain, stage, detail = "PIPELINE_INFRASTRUCTURE_FAILURE", "UNCLASSIFIED", f"{type(exc).__name__}:{exc}"
            rec = {
                "schema": OBJECT_ID + "_INSTANCE_FAILURE",
                "status": "FAIL",
                "scheduled_instance_id": scheduled.scheduled_instance_id,
                "family_id": scheduled.family_id,
                "cohort": scheduled.cohort,
                "n": scheduled.size_parameter,
                "frozen_seed_string": scheduled.frozen_seed_string,
                "authoritative_failure_domain": domain,
                "exact_causal_stage": stage,
                "detail": detail,
                "generator_preflight": preflight,
                "traceback": traceback.format_exc(),
                "retained": True,
                "postselection_allowed": False,
                "H1": "OPEN",
                "H2": "OPEN",
                "H3": "OPEN",
                "SAT_IN_P": "NOT_PROVED",
                "P_VS_NP": "OPEN",
                "BA26_STARTED": False,
            }
        record_bytes = json_bytes(rec)
        record_path = instances_dir / f"{index:03d}.json"
        record_path.write_bytes(record_bytes)
        row = {
            "scheduled_instance_id": scheduled.scheduled_instance_id,
            "family_id": scheduled.family_id,
            "cohort": scheduled.cohort,
            "n": scheduled.size_parameter,
            "frozen_seed_string": scheduled.frozen_seed_string,
            "status": rec["status"],
            "record_sha256": sha256_bytes(record_bytes),
        }
        if rec["status"] == "PASS":
            completed += 1
            generated_real += int(rec.get("generated_real_instance_increment", 0))
            row.update({
                "original_sha256": rec.get("original_canonical_dimacs_sha256"),
                "residual_sha256": rec.get("residual_canonical_dimacs_sha256"),
                "original_CLV": rec.get("reducer", {}).get("initial_CLV"),
                "residual_CLV": rec.get("reducer", {}).get("residual_CLV"),
                "width_interval_before": rec.get("width_evidence", {}).get("interval_before"),
                "width_interval_after": rec.get("width_evidence", {}).get("interval_after"),
                "INCIDENCE_TW_LB": rec.get("INCIDENCE_TW_LB"),
                "INCIDENCE_TD_VERIFIED_UB": rec.get("INCIDENCE_TD_VERIFIED_UB"),
                "INCIDENCE_TW_INTERVAL": rec.get("INCIDENCE_TW_INTERVAL"),
                "BA25_FACTOR_TD_VERIFIED_WIDTH": rec.get("BA25_FACTOR_TD_VERIFIED_WIDTH"),
                "BA25_FACTOR_TD_VALIDATION_PASS": rec.get("BA25_FACTOR_TD_VALIDATION_PASS"),
                "terminal_outcome": rec.get("terminal_recognition"),
                "truth_state": rec.get("truth_oracle", {}).get("truth_state"),
                "truth_contract": rec.get("truth_contract"),
                "BA25_status": rec.get("BA25_diagnostic", {}).get("status"),
                "rho_n": rec.get("rho_n"),
                "r_n": rec.get("r_n"),
                "strict_width_drop": rec.get("CERTIFIED_STRICT_TREEWIDTH_DECREASE_ON_THIS_TRAJECTORY"),
            })
        else:
            row.update({"authoritative_failure_domain": rec.get("authoritative_failure_domain"), "exact_causal_stage": rec.get("exact_causal_stage"), "detail": rec.get("detail")})
            failures.append(row)
        rows.append(row)
        if rec["status"] != "PASS":
            break
    complete = not failures and completed == EXPECTED_RECORDS and generated_real == EXPECTED_RECORDS
    result = {
        "schema": OBJECT_ID + "_RESULT",
        "version": "1.0",
        "status": "LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_COMPLETE" if complete else "LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_PIPELINE_FAILURE_STOPPED",
        "scientific_role": "RAW_LANE_B_DISCOVERY_EVIDENCE_ONLY_NO_H1_H2_H3_PROMOTION",
        "workflow_commit": os.environ.get("GITHUB_SHA"),
        "run_id": int(os.environ["GITHUB_RUN_ID"]) if os.environ.get("GITHUB_RUN_ID") else None,
        "pinned_source_assertions": pins,
        "core_source_assertions": core_assertions,
        "frozen_family": EXPECTED_FAMILY,
        "frozen_sizes": list(EXPECTED_SIZES),
        "frozen_cohort_order_per_size": list(EXPECTED_COHORTS),
        "frozen_seed": FROZEN_SEED,
        "scheduled_lane_b_discovery_count": EXPECTED_RECORDS,
        "completed_lane_b_records": completed,
        "generated_real_USF_instances_this_gate": generated_real,
        "instances": rows,
        "pipeline_failures": failures,
        "scientific_falsifiers": [],
        "OPEN_CORE_is_scientific_data_not_failure": True,
        "UNKNOWN_RESOURCE_LIMIT_is_scientific_data_not_failure": True,
        "NOT_RUN_RESOURCE_GUARD_is_scientific_data_not_failure": True,
        "strict_width_drop_statement_scope": "ONE_TRAJECTORY_ONLY_NOT_H1",
        "rho_n_definition": "LB_after / residual_variable_count when residual_variable_count>0 else null",
        "r_n_definition": "UB_after / log2(n)",
        "finite_records_prove_H1": False,
        "finite_records_prove_H3": False,
        "LANE_B_DISCOVERY_COMPLETE": complete,
        "LANE_C_EXECUTION_STARTED": False,
        "HOLDOUT_EXECUTION_STARTED": False,
        "PRIMARY_BLOCKER": "UNIVERSAL_RESIDUAL_STRUCTURAL_FUNNEL_THEOREM",
        "H1": "OPEN",
        "H2": "OPEN",
        "H3": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "BA26_STARTED": False,
        "stop": "STOP_AFTER_RAW_LANE_B_DISCOVERY_EVIDENCE_NO_INTERPRETATION_NO_LANE_C_NO_HOLDOUT_NO_BA26",
    }
    result_bytes = json_bytes(result)
    result_path = out_dir / "LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_RESULT.json"
    result_path.write_bytes(result_bytes)
    (out_dir / "LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_RESULT.sha256").write_text(sha256_bytes(result_bytes) + "  LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_RESULT.json\n", encoding="utf-8")
    manifest = {
        "schema": OBJECT_ID + "_PER_RECORD_MANIFEST",
        "records": [{"scheduled_instance_id": row["scheduled_instance_id"], "record_sha256": row["record_sha256"], "original_sha256": row.get("original_sha256"), "residual_sha256": row.get("residual_sha256")} for row in rows],
    }
    manifest_bytes = json_bytes(manifest)
    (out_dir / "LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_MANIFEST.json").write_bytes(manifest_bytes)
    (out_dir / "LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_MANIFEST.sha256").write_text(sha256_bytes(manifest_bytes) + "  LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_MANIFEST.json\n", encoding="utf-8")
    print("LANE_B_DISCOVERY_RESULT_SHA256=" + sha256_bytes(result_bytes))
    print("LANE_B_DISCOVERY_MANIFEST_SHA256=" + sha256_bytes(manifest_bytes))
    print("LANE_B_DISCOVERY_COMPLETED_RECORDS=" + str(completed))
    print("LANE_B_DISCOVERY_COMPLETE=" + str(complete).lower())
    if not complete:
        raise SystemExit(2)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--verify-contract-only", action="store_true")
    parser.add_argument("--execute-lane-b-discovery", action="store_true")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.verify_contract_only:
        print(json.dumps(contract_only(root), indent=2, sort_keys=True))
        return
    if args.execute_lane_b_discovery:
        if not args.output_dir:
            raise SystemExit("--output-dir required")
        execute(root, Path(args.output_dir).resolve())
        return
    raise SystemExit("LANE_B_EXECUTOR_INERT")

if __name__ == "__main__":
    main()
