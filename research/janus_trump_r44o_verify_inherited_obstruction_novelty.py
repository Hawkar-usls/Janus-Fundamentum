#!/usr/bin/env python3
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / "JANUS_TRUMP_R44O_INHERITED_OBSTRUCTION_REPLAY_AND_NOVELTY_TEST_2026-09-03.json"

with CONTRACT.open("r", encoding="utf-8") as f:
    contract = json.load(f)

fingerprints = contract["frozen_obstruction_fingerprints"]


def normalize(candidate):
    return {
        "failed_premise": candidate.get("failed_premise"),
        "structural_trigger": candidate.get("structural_trigger"),
        "cost_failure_mode": candidate.get("cost_failure_mode"),
        "required_successor_escape": candidate.get("required_successor_escape"),
    }


def exact_match(candidate, fp):
    c = normalize(candidate)
    f = normalize(fp)
    # Only compare fields actually frozen by the inherited fingerprint.
    compared = 0
    for key, value in f.items():
        if value is None:
            continue
        compared += 1
        if c.get(key) != value:
            return False
    return compared > 0


def classify(candidate):
    matches = [fp for fp in fingerprints if exact_match(candidate, fp)]
    if matches:
        return {
            "verdict": "NOT_NOVEL",
            "matched_source_gates": [m["source_gate"] for m in matches],
            "matched_machine_ids": [m["machine_id"] for m in matches],
            "theorem_authority_delta": 0,
        }
    return {
        "verdict": "NOVELTY_OPEN",
        "matched_source_gates": [],
        "matched_machine_ids": [],
        "theorem_authority_delta": 0,
    }


# Adversarial replay: the same machines under renamed prose must still be detected.
replays = [
    {
        "name": "renamed_fixed_portfolio_gap",
        "failed_premise": "fixed_small_portfolio_is_universal",
        "structural_trigger": "explicit_residual_outside_all_frozen_routes",
        "required_successor_escape": "new_exact_route_or_general_coverage_theorem",
        "expected": "R44C",
    },
    {
        "name": "renamed_fixed_backdoor_gap",
        "failed_premise": "fixed_k_backdoor_radius_is_universal",
        "structural_trigger": "scalable_family_with_minimum_backdoor_size_growing",
        "required_successor_escape": "unbounded_structure_with_polynomial_compression_or_different_representation",
        "expected": "R44F",
    },
    {
        "name": "renamed_boundary_quotient_gap",
        "failed_premise": "arbitrary_boundary_assignments_have_polynomial_universal_quotient",
        "structural_trigger": "pairwise_distinguishable_boundary_assignments",
        "cost_failure_mode": "2^w_states",
        "required_successor_escape": "structure_conditioned_or_symbolic_representation",
        "expected": "R44I",
    },
]

replay_results = []
for candidate in replays:
    result = classify(candidate)
    assert result["verdict"] == "NOT_NOVEL", (candidate, result)
    assert candidate["expected"] in result["matched_source_gates"], (candidate, result)
    replay_results.append({"name": candidate["name"], **result})

# A syntactically new candidate with no exact inherited machine match must remain OPEN,
# never be promoted to certified novelty merely because no match was found.
unknown_candidate = {
    "name": "unknown_cross_language_compile_barrier",
    "failed_premise": "all_exact_language_switches_have_polynomial_compile_size",
    "structural_trigger": "candidate_cross_language_blowup_family",
    "cost_failure_mode": "unknown_compile_blowup",
    "required_successor_escape": "prove_polynomial_compile_or_find_new_representation",
}
unknown_result = classify(unknown_candidate)
assert unknown_result["verdict"] == "NOVELTY_OPEN"
assert unknown_result["theorem_authority_delta"] == 0

required_laws = {
    "NEW_WORDS != NEW_MACHINE",
    "MATCHED_INHERITED_MACHINE => NOT_NOVEL",
    "NO_MATCH_FOUND != PROVED_NOVEL",
    "FAILURE_IS_HERITABLE",
    "THEOREM_AUTHORITY_DELTA=0",
}
assert required_laws.issubset(set(contract["core_laws"]))
assert contract["P_EQUALS_NP"] == "NOT_PROVED"
assert contract["P_NE_NP"] == "NOT_PROVED"
assert contract["P_VS_NP"] == "OPEN"

print(json.dumps({
    "gate_id": contract["id"],
    "verdict": "INHERITED_OBSTRUCTION_REPLAY_AND_CONSERVATIVE_NOVELTY_TEST_PASS",
    "replayed_inherited_machines": replay_results,
    "unknown_candidate": unknown_result,
    "firewall": "NO_MATCH_FOUND != PROVED_NOVEL",
    "theorem_authority_delta": 0,
    "P_VS_NP": "OPEN",
    "next_gate": contract["next_gate"],
}, sort_keys=True))
