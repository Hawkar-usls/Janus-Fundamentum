from __future__ import annotations

"""Independent static verifier for Lane-A phase-separated calibration V2.

This verifier does not import or execute the V2 executor, generator, reducer,
width machinery, BA25, or truth oracle.  It parses the V2 executor as source and
checks frozen Git blob identities plus the anti-post-hoc phase-separation
contract before any V2 real instance may be accepted as evidence.
"""

import ast
import hashlib
import json
from pathlib import Path

RUNNER_PATH = "research/trump_usf_r0_lane_a_phase_separated_calibration_v2.py"
RUNNER_BLOB = "4a1cb6460c8c5ef21e3f7bd658e08a30d9522348"
METHODOLOGY_PATH = "research/TRUMP_USF_R0_LANE_A_INPUT_CLASS_VS_POST_REDUCER_TERMINAL_METHODOLOGICAL_SUCCESSOR_2026-09-10.json"
METHODOLOGY_BLOB = "6d8db87c7c0bc36e3e8c08d5df691714aa2448ff"
OLD_FAILURE_PATH = "research/TRUMP_USF_R0_LANE_A_CALIBRATION_DISCOVERY_FAILURE_2026-09-10.json"
OLD_FAILURE_BLOB = "97b454cefb2be61b6f0ccd021980b06831cab66d"
OLD_FAILED_RUN_ID = 34502250623

PINNED_BLOBS = {
    "GENERATOR": ("research/trump_usf_r0_frozen_generators.py", "fe33883dc08e7e1eacadf287093aa0bb1f16c19a"),
    "ENTRYPOINT": ("research/trump_usf_r0_execution_harness_frozen_entrypoint.py", "50e8eedd461b87de37385cc9f3d30ea6224909fb"),
    "CORE": ("research/trump_usf_r0_execution_harness.py", "ed4203bac76349ab377bb97f67bf1054d837bc96"),
    "R37B": ("experiments/janus_trump_r37b_fixed_certified_portfolio_restart_cycle.py", "f37da1c2e1696e35695096a2c748a222af7920cc"),
    "R33": ("experiments/janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics.py", "c9234a1ef639a009cc6cb4c8a6098fd09bf9affe"),
    "R34": ("experiments/janus_trump_r34_affine_xor_terminal_against_tseitin_core.py", "7f9bec920fa47af066570d874fe9127dc4b9b968"),
    "R35": ("experiments/janus_trump_r35_nonaffine_core_freeze_structure_intake.py", "ad237e341d9659d33da0568f134815776c1f95d8"),
    "R35B": ("experiments/janus_trump_r35b_single_literal_rup_vivification.py", "259d2e38947d09b0c058963ad825a57f2e734203"),
    "R38": ("experiments/janus_trump_r38_portfolio_fixpoint_freeze_structure_intake.py", "816b53c390d78af415e580eaf358acf191796205"),
    "WIDTH": ("experiments/trump_r38_fixpoint_to_ba25_factor_graph_diagnostic.py", "ea36a6b69f8c6034aa00ae4c4217bbd4d7735750"),
    "BA25": ("research/janus_trump_r50g25ba25.py", "cad9c5f837d9d3c4e1c4bd4abef40976f2bb36ff"),
}

EXPECTED_SOURCE_CALLS = {
    "A1_2SAT_EQUIVALENCE_RING": "r33.is_2cnf",
    "A2_HORN_FORWARD_CHAIN": "r33.is_horn",
    "A3_RENAMABLE_HORN_FLIPPED_WIDTH3": "r38.renamable_horn_recognition",
    "A4_AFFINE_TSEITIN_CIRCULAR_LADDER": "r34.recognize_complete_affine_cnf",
}
FORBIDDEN_POST_TERMINAL_FAMILY_MARKERS = tuple(EXPECTED_SOURCE_CALLS)
FORBIDDEN_POST_TERMINAL_SOURCE_LABELS = (
    "2CNF",
    "HORN",
    "RENAMABLE_HORN",
    "AFFINE_XOR_COMPLETE_CNF_BUNDLE",
    "EMPTY_CNF_SAT",
    "EMPTY_CLAUSE_UNSAT",
)


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def assigned_literal(tree: ast.AST, name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
                return ast.literal_eval(node.value)
    raise AssertionError(f"ASSIGNMENT_NOT_FOUND:{name}")


def function_node(tree: ast.Module, name: str) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"FUNCTION_NOT_FOUND:{name}")


def dotted_call_names(node: ast.AST) -> set[str]:
    out: set[str] = set()
    for item in ast.walk(node):
        if not isinstance(item, ast.Call):
            continue
        f = item.func
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            out.add(f.value.id + "." + f.attr)
        elif isinstance(f, ast.Name):
            out.add(f.id)
    return out


def verify(root: Path) -> dict:
    observations = {}

    all_pins = {
        "V2_EXECUTOR": (RUNNER_PATH, RUNNER_BLOB),
        "METHODOLOGICAL_SUCCESSOR": (METHODOLOGY_PATH, METHODOLOGY_BLOB),
        "OLD_FAILED_R0_RECEIPT": (OLD_FAILURE_PATH, OLD_FAILURE_BLOB),
        **PINNED_BLOBS,
    }
    pin_results = {}
    for role, (rel, expected) in all_pins.items():
        observed = git_blob_sha1(root / rel)
        if observed != expected:
            raise AssertionError(f"PINNED_BLOB_MISMATCH:{role}:expected={expected}:observed={observed}")
        pin_results[role] = {"path": rel, "expected": expected, "observed": observed, "pass": True}
    observations["all_frozen_blob_assertions_pass"] = True

    methodology = json.loads((root / METHODOLOGY_PATH).read_text(encoding="utf-8"))
    assert methodology["methodological_law"]["phase_separation"] == "SOURCE_MEMBERSHIP_PERP_POST_REDUCTION_TERMINAL_LABEL_SUBJECT_TO_EXACT_TRANSFORMATION_SOUNDNESS"
    assert methodology["future_lane_a_pass_contract"]["explicitly_not_required"] == "SOURCE_CLASS_LABEL_EQUALS_POST_REDUCER_TERMINAL_LABEL"
    assert methodology["anti_post_hoc_firewall"]["observed_A1_terminal_added_as_special_exception"] is False
    assert methodology["anti_post_hoc_firewall"]["generic_for_all_A1_A4_source_classes"] is True
    observations["methodological_successor_phase_separation_replayed"] = True

    old = json.loads((root / OLD_FAILURE_PATH).read_text(encoding="utf-8"))
    assert old["workflow"]["run_id"] == OLD_FAILED_RUN_ID
    assert old["workflow"]["conclusion"] == "failure"
    assert old["calibration_failure"]["exact_reason"] == "A1_REQUIRED_2CNF_RECOGNIZER_MISMATCH"
    observations["old_failed_run_preserved_as_failure"] = True

    source = (root / RUNNER_PATH).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=RUNNER_PATH)
    assert assigned_literal(tree, "EXPECTED_LANE_A_RECORDS") == 36
    assert assigned_literal(tree, "EXPECTED_NEW_GENERATED_REAL_INSTANCES") == 35
    assert assigned_literal(tree, "SOURCE_CLASS_LABEL_EQUALS_POST_REDUCER_TERMINAL_LABEL_REQUIRED") is False
    assert assigned_literal(tree, "OLD_FAILED_RUN_ID") == OLD_FAILED_RUN_ID
    observations["literal_source_post_terminal_label_equality_requirement_absent"] = True

    source_check = function_node(tree, "source_class_check")
    source_calls = dotted_call_names(source_check)
    for family, required_call in EXPECTED_SOURCE_CALLS.items():
        if family not in ast.get_source_segment(source, source_check):
            raise AssertionError(f"SOURCE_FAMILY_BINDING_MISSING:{family}")
        if required_call not in source_calls:
            raise AssertionError(f"SOURCE_RECOGNIZER_CALL_MISSING:{family}:{required_call}")
    source_check_text = ast.get_source_segment(source, source_check) or ""
    assert "original_canonical_dimacs_sha256_frozen_before_recognizer" in source_check_text
    assert '"truth_or_solver_output_consumed": False' in source_check_text
    assert "A5_SEALED_HISTORICAL_REPLAY_NOT_A_SOURCE_CLASS_POSITIVE_CONTROL" in source_check_text
    observations["A1_A4_source_predicates_bound_to_original_phase"] = True
    observations["A5_excluded_from_source_positive_control_schema"] = True

    post = function_node(tree, "post_terminal_sound")
    post_text = ast.get_source_segment(source, post) or ""
    for marker in FORBIDDEN_POST_TERMINAL_FAMILY_MARKERS:
        if marker in post_text:
            raise AssertionError(f"POST_TERMINAL_FAMILY_SPECIAL_CASE_FORBIDDEN:{marker}")
    for label in FORBIDDEN_POST_TERMINAL_SOURCE_LABELS:
        if ('"' + label + '"') in post_text or ("'" + label + "'") in post_text:
            raise AssertionError(f"POST_TERMINAL_SOURCE_LABEL_SPECIAL_CASE_FORBIDDEN:{label}")
    assert "core.TERMINAL_CATALOGUE" in post_text
    assert "A5_FAMILY" in post_text
    observations["post_terminal_A1_A4_rule_is_generic_frozen_catalogue_membership"] = True

    execute = function_node(tree, "execute_lane_a_v2")
    execute_text = ast.get_source_segment(source, execute) or ""
    source_pos = execute_text.find("source_class_check(")
    entry_pos = execute_text.find("run_entrypoint(")
    if not (source_pos >= 0 and entry_pos >= 0 and source_pos < entry_pos):
        raise AssertionError("SOURCE_CLASS_CHECK_NOT_BEFORE_CANONICAL_ENTRYPOINT_EXECUTION")
    assert 'startswith("USF-R0|DISCOVERY|A|")' in execute_text
    assert '"|B|" in x' in execute_text
    assert '"|C|" in x' in execute_text
    assert '"|HOLDOUT|" in x' in execute_text
    observations["source_phase_precedes_reducer_truth_entrypoint"] = True
    observations["lane_scope_static_firewall_present"] = True

    causal = function_node(tree, "causal_firewall_pass")
    causal_text = ast.get_source_segment(source, causal) or ""
    assert "SOURCE_PREFLIGHT_AND_ENTRYPOINT_ORIGINAL_HASH_MISMATCH" in causal_text
    assert "truth_may_influence_generation_reducer_width_terminal_retention_or_later_seed" in causal_text
    assert "postselection_allowed" in causal_text
    observations["preflight_original_hash_must_equal_entrypoint_original_hash"] = True
    observations["truth_and_postselection_firewalls_present"] = True

    classifier = function_node(tree, "classify_successful_entrypoint_record")
    classifier_text = ast.get_source_segment(source, classifier) or ""
    for field in (
        "SOURCE_CLASS_EXPECTATION_PASS",
        "REDUCER_CERTIFICATE_REPLAY_PASS",
        "TRUTH_AUTHORITY_PASS",
        "WIDTH_AUTHORITY_PASS",
        "CAUSAL_FIREWALL_PASS",
        "POST_REDUCER_TERMINAL_SOUND",
    ):
        assert field in classifier_text
    for failure in (
        "SOURCE_CLASS_CALIBRATION_FAILURE",
        "REDUCER_REPLAY_FAILURE",
        "POST_REDUCER_TERMINAL_CALIBRATION_FAILURE",
        "TRUTH_AUTHORITY_FAILURE",
        "WIDTH_AUTHORITY_FAILURE",
        "CAUSAL_FIREWALL_FAILURE",
    ):
        assert failure in classifier_text
    observations["six_phase_separated_pass_flags_present"] = True
    observations["six_disjoint_failure_domains_present"] = True

    # A family-specific source expectation is allowed only in the source phase.
    # A1-A4 family markers must not occur in post_terminal_sound, whose only
    # family-specific exception is the separately frozen A5 historical replay.
    observations["anti_post_hoc_A1_EMPTY_CNF_special_case_absent"] = (
        "A1_2SAT_EQUIVALENCE_RING" not in post_text and "EMPTY_CNF_SAT" not in post_text
    )
    assert observations["anti_post_hoc_A1_EMPTY_CNF_special_case_absent"] is True

    result = {
        "schema": "TRUMP_USF_R0_LANE_A_PHASE_SEPARATED_CALIBRATION_V2_INDEPENDENT_STATIC_VERIFICATION",
        "version": "1.0",
        "ANTI_POST_HOC_MECHANICAL_VERIFICATION_PASS": True,
        "real_instance_executed_by_verifier": False,
        "executor_imported_by_verifier": False,
        "scientific_modules_imported_by_verifier": False,
        "expected_lane_a_records": 36,
        "expected_new_generated_real_instances": 35,
        "lane_b_authorized": False,
        "lane_c_authorized": False,
        "holdout_authorized": False,
        "BA26_authorized": False,
        "pin_results": pin_results,
        "observations": observations,
        "scientific_state": {
            "PRIMARY_BLOCKER": "UNIVERSAL_RESIDUAL_STRUCTURAL_FUNNEL_THEOREM",
            "H1": "OPEN",
            "H2": "OPEN",
            "H3": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "BA26_STARTED": False,
        },
    }
    return result


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    result = verify(root)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
