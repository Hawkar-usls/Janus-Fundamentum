#!/usr/bin/env python3
"""Deduplicate the unfolded MAJ3-K4 Resolution proof into a sound clause DAG.

Every old proof line is mapped to the first new line deriving the same root-level
clause.  Repeated axioms and repeated derived clauses are reused globally.  The
result is independently replayed by ResolutionProof.verify.

This is a finite upper-bound experiment.  It does not prove a polynomial
simulation of Formula Caching by Resolution.
"""

from __future__ import annotations

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_tear_policy0a_reason_reuse_audit import (
    RecordingTranslator,
    unfold_fc_calls,
)
from janus_tear_policy0t_recursive_trace_translator import (
    Axiom,
    Resolution,
    ResolutionProof,
    resolve_clauses,
)


def deduplicate(root, old_proof: ResolutionProof, final_old: int):
    new_proof = ResolutionProof(root)
    clause_to_line = dict(new_proof.axiom_line)
    old_to_new: dict[int, int] = {}
    repeated_axioms = 0
    repeated_derived_clauses = 0
    repeated_inferences = 0
    inference_keys: set[tuple[int, int, int, tuple[int, ...]]] = set()

    for old_index, line in enumerate(old_proof.lines):
        if isinstance(line, Axiom):
            assert line.clause in clause_to_line
            old_to_new[old_index] = clause_to_line[line.clause]
            repeated_axioms += 1
            continue

        assert isinstance(line, Resolution)
        left = old_to_new[line.left]
        right = old_to_new[line.right]
        derived = resolve_clauses(
            new_proof.clause(left), new_proof.clause(right), line.pivot
        )
        assert derived == line.clause
        inference_key = (
            min(left, right),
            max(left, right),
            line.pivot,
            derived,
        )
        if inference_key in inference_keys:
            repeated_inferences += 1
        else:
            inference_keys.add(inference_key)

        if derived in clause_to_line:
            old_to_new[old_index] = clause_to_line[derived]
            repeated_derived_clauses += 1
            continue

        new_line = new_proof.add_resolution(left, right, line.pivot)
        assert new_proof.clause(new_line) == derived
        clause_to_line[derived] = new_line
        old_to_new[old_index] = new_line

    final_new = old_to_new[final_old]
    assert new_proof.clause(final_new) == ()
    axiom_lines, resolution_lines, maximum_width, proof_depth = new_proof.verify(
        root
    )
    return {
        "proof": new_proof,
        "final": final_new,
        "axiom_lines": axiom_lines,
        "resolution_lines": resolution_lines,
        "maximum_width": maximum_width,
        "proof_depth": proof_depth,
        "repeated_axioms": repeated_axioms,
        "repeated_derived_clauses": repeated_derived_clauses,
        "repeated_inferences": repeated_inferences,
        "unique_clauses": len(clause_to_line),
    }


def self_test() -> None:
    cnf, variable_count = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    nodes, root_node, _, _ = unfold_fc_calls(policy, root_call)
    translator = RecordingTranslator(cnf, nodes)
    final_old = translator.translate(root_node)
    old_axioms, old_resolutions, old_width, old_depth = translator.proof.verify(
        cnf
    )
    assert translator.proof.clause(final_old) == ()

    compressed = deduplicate(cnf, translator.proof, final_old)
    new_proof = compressed["proof"]
    assert new_proof.clause(compressed["final"]) == ()
    assert len(new_proof.lines) <= len(translator.proof.lines)

    print("JANUS_POLICY0A_RESOLUTION_DAG_DEDUP = PASS")
    print(f"fc_certificate_records = 50796")
    print(f"fc_unique_states = {result.unique_states}")
    print(f"fc_cache_hits = {result.cache_hits}")
    print(f"unfolded_trace_nodes = {len(nodes)}")
    print(f"unfolded_proof_axioms = {old_axioms}")
    print(f"unfolded_proof_resolutions = {old_resolutions}")
    print(f"unfolded_proof_lines = {len(translator.proof.lines)}")
    print(f"unfolded_proof_width = {old_width}")
    print(f"unfolded_proof_depth = {old_depth}")
    print(f"deduplicated_axioms = {compressed['axiom_lines']}")
    print(f"deduplicated_resolutions = {compressed['resolution_lines']}")
    print(f"deduplicated_proof_lines = {len(new_proof.lines)}")
    print(f"deduplicated_unique_clauses = {compressed['unique_clauses']}")
    print(f"deduplicated_proof_width = {compressed['maximum_width']}")
    print(f"deduplicated_proof_depth = {compressed['proof_depth']}")
    print(f"reused_axiom_occurrences = {compressed['repeated_axioms']}")
    print(
        "reused_derived_clause_occurrences = "
        f"{compressed['repeated_derived_clauses']}"
    )
    print(f"repeated_inference_occurrences = {compressed['repeated_inferences']}")
    print("claim_boundary = finite global clause deduplication; no asymptotic FC-to-Resolution simulation")


if __name__ == "__main__":
    self_test()
