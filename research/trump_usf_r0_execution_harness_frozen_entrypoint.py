from __future__ import annotations

"""Final pre-execution binding for the JANUS/TRUMP USF R0 harness freeze.

This append-only entrypoint composes the already-created core harness with two
pre-seal, pre-result edge-case bindings: (1) the empty incidence graph uses the
standard treewidth convention -1, avoiding an invalid [0,-1] interval from the
historical diagnostic helper; (2) preregistered A5 is a sealed historical R38
replay, not a generated family instance.  No reduction rule, family, seed,
schedule, terminal, or scientific claim is changed here.

Import is inert.  The freeze gate may invoke only --synthetic-self-test and
--print-schedule.  --run-scheduled is reserved for a later explicit gate.
"""

import argparse
import json
import math
from pathlib import Path
import sys

CORE_HARNESS_PATH = "research/trump_usf_r0_execution_harness.py"
CORE_HARNESS_BLOB = "ed4203bac76349ab377bb97f67bf1054d837bc96"
GENERATOR_PATH = "research/trump_usf_r0_frozen_generators.py"
GENERATOR_BLOB = "fe33883dc08e7e1eacadf287093aa0bb1f16c19a"
A5_SOURCE_COMMIT = "0b941a484143aa130bad9f7bdf9ca94fbbff79cb"
A5_EXPECTED_INITIAL_CLV = [118, 354, 28]
A5_EXPECTED_INTERNAL_RESIDUAL_SHA256 = "3361190b3fe683457061662dd9244cd37ca79283828139666d35b01b11d2fe95"

IMPLEMENTATION_BINDINGS = {
    "empty_incidence_graph_treewidth": {
        "convention": -1,
        "reason": "Historical width helper initializes finite nonempty-graph lower bounds at 0; empty graph is bound here before USF results so LB/UB remains a valid exact interval.",
        "changes_frozen_measurement_source_bytes": False,
    },
    "A5_HISTORICAL_R38": {
        "preregistered_role": "NO_GENERATION_SEALED_HISTORICAL_REPLAY",
        "source_commit": A5_SOURCE_COMMIT,
        "expected_initial_CLV": A5_EXPECTED_INITIAL_CLV,
        "expected_internal_residual_sha256": A5_EXPECTED_INTERNAL_RESIDUAL_SHA256,
        "counts_as_generated_real_USF_instance": False,
    },
    "scientific_scope": "PREEXECUTION_IMPLEMENTATION_BINDING_ONLY_BEFORE_ANY_SCHEDULED_RESULT",
}


def _import_core(root: Path):
    research = str(root / "research")
    if research not in sys.path:
        sys.path.insert(0, research)
    import trump_usf_r0_execution_harness as core
    if core.git_blob_sha1(root / CORE_HARNESS_PATH) != CORE_HARNESS_BLOB:
        raise core.HarnessIntegrityError("CORE_HARNESS_BLOB_MISMATCH")
    if core.git_blob_sha1(root / GENERATOR_PATH) != GENERATOR_BLOB:
        raise core.HarnessIntegrityError("GENERATOR_BLOB_MISMATCH")
    return core


def width_evidence(core, width_module, formula, label: str) -> tuple[dict, dict]:
    vertices, edges = core._incidence_graph(formula)
    if not vertices:
        out = {
            "label": label,
            "C_L_V": [0, 0, 0],
            "variable_count": 0,
            "clause_count": 0,
            "incidence_vertex_count": 0,
            "incidence_edge_count": 0,
            "verified_td_upper_bound": -1,
            "treewidth_lower_bound": -1,
            "lower_bound_components": {"empty_graph_convention": -1},
            "treewidth_interval": [-1, -1],
            "exact_treewidth": -1,
            "exact_treewidth_certified": True,
            "candidate_order_method": "EMPTY_GRAPH_NO_HEURISTIC",
            "candidate_order_is_exact_treewidth_authority": False,
            "independent_td_validation": {
                "pass": True,
                "tree": True,
                "vertex_coverage": True,
                "edge_coverage": True,
                "running_intersection": True,
                "width": -1,
            },
            "independent_degeneracy_replay": {
                "pass": True, "lower_bound": -1, "empty_graph": True
            },
            "independent_minor_min_width_replay": {
                "pass": True, "lower_bound": -1, "empty_graph": True
            },
        }
        private = {
            **out,
            "_td": {"bags": {}, "edges": (), "order": (), "width": -1},
            "_clauses": [],
            "_orig_vars": [],
        }
        return out, private
    return core.width_evidence(width_module, formula, label)


def ba25_diagnostic(core, ba25, width_module, r33, residual, width_private) -> dict:
    c, _, v = r33.measure(residual)
    if c == 0 and v == 0:
        return {
            "status": "NOT_RUN_EMPTY_RESIDUAL",
            "verified_tau": -1,
            "truth_authority": False,
            "independent_truth_oracle_replaced": False,
        }
    return core.ba25_diagnostic(ba25, width_module, r33, residual, width_private)


def run_scheduled_instance(instance_id: str, root: Path, *, execute_truth: bool = True) -> dict:
    core = _import_core(root)
    assertions, gen, r33, r34, r35, r35b, r38, width, ba25 = core.load_modules(root)
    record = gen.scheduled_instance(instance_id, allow_holdout=False)

    if record.family_id == "A5_HISTORICAL_R38":
        original = r33.canonical_formula(
            r33.deterministic_random_3cnf(36001, n=28, ratio=4.2)
        )
        if list(r33.measure(original)) != A5_EXPECTED_INITIAL_CLV:
            raise core.HarnessIntegrityError("A5_HISTORICAL_R37B_SOURCE_CLV_DRIFT")
        generator_status = "SEALED_HISTORICAL_SOURCE_RECONSTRUCTION_PASS"
        generator_spec_version = "A5_SEALED_R37B_REPLAY"
        generated_real_instance_increment = 0
    else:
        try:
            generated = gen.generate(record)
        except gen.GeneratorIntegrityError as exc:
            return {
                "schema": "TRUMP_USF_R0_INSTANCE_RESULT",
                "scheduled_instance_id": instance_id,
                "truth_state": "GENERATOR_INTEGRITY_FAIL",
                "generator_error": str(exc),
                "retained": True,
                "finite_experiment_is_asymptotic_authority": False,
                "H1": "OPEN", "H2": "OPEN", "H3": "OPEN",
                "SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN",
                "BA26_STARTED": False,
            }
        original = gen.canonical_formula(generated.formula)
        generator_status = generated.generator_integrity_status
        generator_spec_version = generated.generator_spec_version
        generated_real_instance_increment = 1

    identity = core.instance_identity(gen, record, original)
    reducer = core.run_frozen_reducer(gen, r33, r34, r35, r35b, original)
    residual = gen.canonical_formula(reducer.pop("residual_formula"))

    if record.family_id == "A5_HISTORICAL_R38":
        historical_internal_hash = r35.canonical_json_sha256([list(c) for c in residual])
        if historical_internal_hash != A5_EXPECTED_INTERNAL_RESIDUAL_SHA256:
            raise core.HarnessIntegrityError("A5_HISTORICAL_R38_RESIDUAL_HASH_DRIFT")
        reducer["A5_historical_internal_residual_hash"] = historical_internal_hash
        reducer["A5_source_commit"] = A5_SOURCE_COMMIT

    residual_sha = gen.canonical_dimacs_sha256(residual)
    if residual_sha != reducer["residual_canonical_dimacs_sha256"]:
        raise core.HarnessIntegrityError("RESIDUAL_CANONICAL_HASH_DRIFT")

    before_width, _before_private = width_evidence(core, width, original, "ORIGINAL")
    after_width, after_private = width_evidence(core, width, residual, "RESIDUAL")
    terminal = core.terminal_recognition(r33, r34, r38, residual)
    ba25_result = ba25_diagnostic(core, ba25, width, r33, residual, after_private)

    truth = core.truth_oracle(gen, original) if execute_truth else {"truth_state": "OPEN_UNVERIFIED"}
    if truth["truth_state"] not in core.TRUTH_STATES:
        raise core.HarnessIntegrityError("UNKNOWN_TRUTH_STATE")

    lb_before, ub_before = before_width["treewidth_interval"]
    lb_after, ub_after = after_width["treewidth_interval"]
    residual_v = after_width["variable_count"]
    n = record.size_parameter
    metrics = {
        "rho_n": (lb_after / residual_v) if residual_v > 0 else None,
        "r_n": (ub_after / math.log2(n)) if n is not None and n > 1 else None,
        "width_drop_certificate_condition_LBbefore_gt_UBafter": lb_before > ub_after,
        "width_drop_certificate_scope": "ONE_TRAJECTORY_ONLY_NOT_H1",
    }

    return {
        "schema": "TRUMP_USF_R0_INSTANCE_RESULT",
        "version": "1.0",
        "canonical_entrypoint": "trump_usf_r0_execution_harness_frozen_entrypoint.py",
        "causal_order": list(core.CAUSAL_ORDER),
        "instance_identity_frozen_before_solver_output": identity,
        "generator_integrity_status": generator_status,
        "generator_spec_version": generator_spec_version,
        "generated_real_instance_increment": generated_real_instance_increment,
        "source_blob_assertions": assertions,
        "original_canonical_dimacs_sha256": identity["canonical_DIMACS_bytes_SHA256"],
        "reducer": reducer,
        "residual_canonical_dimacs_sha256": residual_sha,
        "width_evidence": {
            "before": before_width,
            "after": after_width,
            "interval_before": [lb_before, ub_before],
            "interval_after": [lb_after, ub_after],
        },
        "terminal_recognition": terminal,
        "BA25_diagnostic": ba25_result,
        "truth_oracle": truth,
        "discovery_metrics_diagnostic_only": metrics,
        "retained": True,
        "postselection_allowed": False,
        "truth_may_influence_generation_reducer_width_terminal_retention_or_later_seed": False,
        "finite_experiment_is_asymptotic_authority": False,
        "finite_execution_allowed_roles": [
            "DISCOVER_CANDIDATE_FAMILY_THEOREM",
            "DISCOVER_CANDIDATE_HARD_CORE_FAMILY",
            "FALSIFY_INCORRECTLY_SPECIFIED_FINITE_IMPLEMENTATION_CLAIM",
        ],
        "H1": "OPEN", "H2": "OPEN", "H3": "OPEN",
        "SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "BA26_STARTED": False,
    }


def synthetic_self_test(root: Path) -> dict:
    core = _import_core(root)
    old_width = core.width_evidence
    old_ba25 = core.ba25_diagnostic
    try:
        core.width_evidence = lambda width_module, formula, label: width_evidence(
            core, width_module, formula, label
        )
        core.ba25_diagnostic = lambda ba25, width_module, r33, residual, width_private: ba25_diagnostic(
            core, ba25, width_module, r33, residual, width_private
        )
        result = core.synthetic_self_test(root)
    finally:
        core.width_evidence = old_width
        core.ba25_diagnostic = old_ba25

    if result["generated_real_USF_instances"] != 0:
        raise AssertionError("SYNTHETIC_SELF_TEST_GENERATED_REAL_USF_INSTANCE")
    if result["discovery_execution_started"]:
        raise AssertionError("SYNTHETIC_SELF_TEST_STARTED_DISCOVERY")
    result["canonical_entrypoint"] = "trump_usf_r0_execution_harness_frozen_entrypoint.py"
    result["implementation_bindings"] = IMPLEMENTATION_BINDINGS
    result["generated_real_USF_instances"] = 0
    result["discovery_execution_started"] = False
    result["holdout_execution_started"] = False
    return result


def print_schedule(root: Path) -> dict:
    core = _import_core(root)
    _, gen, *_ = core.load_modules(root)
    return {
        "canonical_entrypoint": "trump_usf_r0_execution_harness_frozen_entrypoint.py",
        "discovery_order": [x.scheduled_instance_id for x in gen.DISCOVERY_SCHEDULE],
        "holdout_order_frozen_but_unopened": [
            x.scheduled_instance_id for x in gen.HOLDOUT_SCHEDULE_FROZEN_BUT_UNOPENED
        ],
        "generated_real_USF_instances": 0,
        "discovery_execution_started": False,
        "holdout_execution_started": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--synthetic-self-test", action="store_true")
    parser.add_argument("--print-schedule", action="store_true")
    parser.add_argument("--run-scheduled")
    parser.add_argument("--output")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.synthetic_self_test:
        out = synthetic_self_test(root)
    elif args.print_schedule:
        out = print_schedule(root)
    elif args.run_scheduled:
        out = run_scheduled_instance(args.run_scheduled, root, execute_truth=True)
    else:
        raise SystemExit(
            "FREEZE_INERT: choose --synthetic-self-test, --print-schedule, or later --run-scheduled"
        )

    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
