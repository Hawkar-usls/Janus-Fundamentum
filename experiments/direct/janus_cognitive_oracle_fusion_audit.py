#!/usr/bin/env python3
"""Software-only JANUS fusion audit for HRain, iNaiHR and AURA Oracle."""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path
from typing import Any

SOURCES = {
    "HRAIN": {
        "repository": "Hawkar-usls/Hrain",
        "commit": "8699617c3c5eb8ecd83732ba46e5bdfb2d0f6399",
        "index_blob": "82926afc8d2a4254e145fea0f7a71579e9cf2b38",
        "role": "persistent hierarchical provenance graph",
    },
    "INAIHR": {
        "repository": "Hawkar-usls/iNaiHR",
        "commit": "e9be39c7f36c92e3f31d4f1c60251bbf41e04c63",
        "index_blob": "2baf3bdaa88eaf5a01e594155b4d0829d17209e7",
        "role": "four-child semantic candidate expansion",
    },
    "AURA": {
        "repository": "Hawkar-usls/aura-oracle-tg",
        "commit": "b5360f08ea6b5369fbd7f56d09d7be93438628a6",
        "index_blob": "f13a0084a75a72899a8e1b60f4ca30b3243dbcda",
        "role": "four-role hypothesis framing and Telegram interface",
    },
}

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def vars_of(formula: CNF) -> list[int]:
    return sorted({abs(lit) for clause in formula for lit in clause})


def satisfies(formula: CNF, assignment: dict[int, bool]) -> bool:
    return all(
        any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause)
        for clause in formula
    )


def solve_bruteforce(formula: CNF) -> tuple[bool, dict[int, bool] | None, int]:
    variables = vars_of(formula)
    checked = 0
    for bits in itertools.product([False, True], repeat=len(variables)):
        checked += 1
        assignment = dict(zip(variables, bits))
        if satisfies(formula, assignment):
            return True, assignment, checked
    return False, None, checked


def random_cnf(rng: random.Random, n_vars: int, n_clauses: int) -> CNF:
    out = []
    for _ in range(n_clauses):
        width = rng.choice((1, 2, 3))
        chosen = rng.sample(range(1, n_vars + 1), min(width, n_vars))
        out.append(tuple(v if rng.random() < 0.5 else -v for v in chosen))
    return tuple(out)


def verify_sat(formula: CNF, witness: Any) -> bool:
    if not isinstance(witness, dict):
        return False
    try:
        parsed = {int(k): bool(v) for k, v in witness.items()}
    except (TypeError, ValueError):
        return False
    return satisfies(formula, parsed)


def exhaustive_unsat_proof(formula: CNF) -> dict[str, Any]:
    variables = vars_of(formula)
    rows = []
    for bits in itertools.product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, bits))
        rows.append({
            "assignment": {str(k): v for k, v in assignment.items()},
            "satisfies": satisfies(formula, assignment),
        })
    return {"kind": "EXHAUSTIVE_SMALL_ONLY", "rows": rows}


def verify_unsat(formula: CNF, proof: Any) -> bool:
    if not isinstance(proof, dict) or proof.get("kind") != "EXHAUSTIVE_SMALL_ONLY":
        return False
    rows = proof.get("rows")
    if not isinstance(rows, list):
        return False
    variables = vars_of(formula)
    if len(rows) != 2 ** len(variables):
        return False
    seen = set()
    for row in rows:
        raw = row.get("assignment") if isinstance(row, dict) else None
        if not isinstance(raw, dict):
            return False
        assignment = {int(k): bool(v) for k, v in raw.items()}
        key = tuple(assignment.get(v, False) for v in variables)
        if key in seen or satisfies(formula, assignment) or row.get("satisfies") is not False:
            return False
        seen.add(key)
    return len(seen) == 2 ** len(variables)


def proof_gate(formula: CNF, outcome: dict[str, Any]) -> tuple[bool, str]:
    kind = outcome.get("claim_type")
    if kind == "SAT":
        return (
            (True, "VERIFIED_SAT")
            if verify_sat(formula, outcome.get("witness"))
            else (False, "INVALID_OR_MISSING_WITNESS")
        )
    if kind == "UNSAT":
        return (
            (True, "VERIFIED_UNSAT")
            if verify_unsat(formula, outcome.get("proof"))
            else (False, "INVALID_OR_MISSING_TEAR")
        )
    return False, "HYPOTHESIS_ONLY"


def fusion_candidate(
    formula: CNF,
    truth: bool,
    witness: dict[int, bool] | None,
    case_id: int,
) -> dict[str, Any]:
    """Architecture stand-in, not a benchmark of any real LLM."""
    digest = hashlib.sha256(repr((formula, case_id)).encode()).digest()
    mode = digest[0] % 8
    branches = [
        {"role": "PAST", "text": f"history-{digest[1] % 17}"},
        {"role": "OBSTACLE", "text": f"obstacle-{digest[2] % 17}"},
        {"role": "GUIDE", "text": f"guide-{digest[3] % 17}"},
        {"role": "OUTCOME", "text": "candidate"},
    ]
    if mode == 0 and truth and witness is not None:
        return {
            "claim_type": "SAT",
            "witness": {str(k): v for k, v in witness.items()},
            "branches": branches,
        }
    if mode == 1 and not truth:
        return {
            "claim_type": "UNSAT",
            "proof": exhaustive_unsat_proof(formula),
            "branches": branches,
        }
    if mode in (2, 3, 4):
        return {
            "claim_type": "UNSAT",
            "branches": branches,
            "interpretation": "All graph roles converge on impossibility.",
        }
    fake = {
        str(v): bool((digest[(v + 4) % len(digest)] >> (v % 8)) & 1)
        for v in vars_of(formula)
    }
    return {"claim_type": "SAT", "witness": fake, "branches": branches}


def outcome_is_true(formula: CNF, truth: bool, outcome: dict[str, Any]) -> bool:
    if outcome.get("claim_type") == "SAT":
        return truth and verify_sat(formula, outcome.get("witness"))
    if outcome.get("claim_type") == "UNSAT":
        return not truth
    return False


def equality_formula(n: int) -> CNF:
    clauses = []
    for i in range(1, n + 1):
        x, y = i, n + i
        clauses.append((-x, y))
        clauses.append((x, -y))
    return tuple(clauses)


def residual_signature_for_x(n: int, value: int) -> tuple[int, ...]:
    return tuple((value >> i) & 1 for i in range(n))


def canonical_clause(clause: Clause) -> Clause:
    return tuple(sorted(clause, key=lambda x: (abs(x), x < 0)))


def canonical_cnf(formula: CNF) -> CNF:
    return tuple(sorted(canonical_clause(c) for c in formula))


def syntactic_variants(formula: CNF, rng: random.Random, count: int) -> list[CNF]:
    variants = []
    for _ in range(count):
        clauses = [list(c) for c in formula]
        rng.shuffle(clauses)
        for clause in clauses:
            rng.shuffle(clause)
        variants.append(tuple(tuple(c) for c in clauses))
    return variants


def exact_prefix_selector_cost(n: int) -> dict[str, int]:
    unique_witness = (1 << n) - 1
    prefixes = [0b00, 0b01, 0b10, 0b11]
    hidden_checks = 0
    selected = None
    for prefix in prefixes:
        for candidate in range(1 << n):
            hidden_checks += 1
            if candidate == unique_witness and (candidate >> (n - 2)) == prefix:
                selected = prefix
                break
        if selected is not None:
            break
    return {
        "outer_candidates": len(prefixes),
        "selected_prefix": int(selected if selected is not None else -1),
        "hidden_assignment_checks": hidden_checks,
        "full_space": 1 << n,
    }


def proof_dag_demo(length: int) -> dict[str, Any]:
    nodes = [{"id": 0, "kind": "axiom", "clause": [1]}]
    for i in range(1, length):
        nodes.append({"id": i, "kind": "derived", "parents": [i - 1], "clause": [1]})
    checks = 0
    valid = True
    for node in nodes:
        checks += 1
        if node["kind"] == "derived" and node["parents"][0] >= node["id"]:
            valid = False
    return {
        "nodes": length,
        "edges": max(0, length - 1),
        "verification_checks": checks,
        "valid": valid,
    }


def run(seed: int = 9379992, cases: int = 600) -> dict[str, Any]:
    rng = random.Random(seed)
    false_ungated = true_generated = false_gate_accepts = gate_accepts = gate_rejects = 0

    for i in range(cases):
        n = rng.randint(3, 7)
        formula = random_cnf(rng, n, rng.randint(n, 4 * n))
        truth, witness, _ = solve_bruteforce(formula)
        outcome = fusion_candidate(formula, truth, witness, i)
        actual = outcome_is_true(formula, truth, outcome)
        if actual:
            true_generated += 1
        else:
            false_ungated += 1
        accepted, _ = proof_gate(formula, outcome)
        if accepted:
            gate_accepts += 1
            if not actual:
                false_gate_accepts += 1
        else:
            gate_rejects += 1

    branching = {
        str(depth): {
            "leaves": 4 ** depth,
            "total_nodes": (4 ** (depth + 1) - 1) // 3,
        }
        for depth in range(1, 13)
    }

    quotient_n = 14
    residuals = {
        residual_signature_for_x(quotient_n, value)
        for value in range(1 << quotient_n)
    }

    base = equality_formula(5)
    variants = syntactic_variants(base, rng, 200)
    naive_text_unique = len({repr(v) for v in variants})
    syntax_canonical_unique = len({repr(canonical_cnf(v)) for v in variants})

    selector = exact_prefix_selector_cost(16)
    proof_dag = proof_dag_demo(10_000)

    consensus_formula: CNF = ((1,),)
    consensus = {
        "claim_type": "UNSAT",
        "branches": [
            {"source": "iNaiHR", "claim": "UNSAT"},
            {"source": "AURA", "claim": "UNSAT"},
            {"source": "HRain-memory", "claim": "UNSAT"},
            {"source": "meta-interpretation", "claim": "UNSAT"},
        ],
    }
    consensus_accepted, consensus_reason = proof_gate(consensus_formula, consensus)

    assertions = {
        "false_accepts_zero_after_gate": false_gate_accepts == 0,
        "ungated_false_outputs_exist": false_ungated > 0,
        "four_branch_depth_12_is_exponential": branching["12"]["leaves"] == 16_777_216,
        "persistent_graph_can_store_exponential_residuals": len(residuals) == 16_384,
        "syntax_canonicalization_deduplicates_permutations": syntax_canonical_unique == 1,
        "raw_text_memory_does_not_deduplicate_all_permutations": naive_text_unique > 1,
        "exact_selector_hides_large_search": selector["hidden_assignment_checks"] >= 2 ** 16,
        "consensus_without_tear_rejected": not consensus_accepted,
        "proof_dag_verification_linear": proof_dag["verification_checks"] == proof_dag["nodes"],
    }

    return {
        "audit": "JANUS_COGNITIVE_ORACLE_FUSION",
        "status": "PASS" if all(assertions.values()) else "FAIL",
        "software_only": True,
        "swarm_touched": False,
        "devices_touched": False,
        "telegram_backend_called": False,
        "external_models_called": False,
        "sources": SOURCES,
        "seed": seed,
        "random_small_cnf_cases": cases,
        "ungated_false_outputs": false_ungated,
        "true_outputs_generated": true_generated,
        "proof_gate_accepts": gate_accepts,
        "proof_gate_rejects": gate_rejects,
        "proof_gate_false_accepts": false_gate_accepts,
        "branching_4_ary": branching,
        "persistent_memory_counterexample": {
            "family": "E_n(X,Y)=AND_i(x_i<->y_i)",
            "n": quotient_n,
            "distinct_continuation_residuals": len(residuals),
        },
        "representation_test": {
            "variants": len(variants),
            "raw_text_unique": naive_text_unique,
            "canonical_under_clause_and_literal_permutation": syntax_canonical_unique,
            "boundary": "Only syntactic permutation was normalized; semantic equivalence still needs a certificate or hard reasoning.",
        },
        "hidden_selector_cost": selector,
        "false_consensus": {
            "voices": 4,
            "claim": "UNSAT for formula (x)",
            "accepted": consensus_accepted,
            "reason": consensus_reason,
        },
        "proof_dag_positive_result": proof_dag,
        "architecture": {
            "iNaiHR": {
                "best_role": "high-recall candidate expansion",
                "risk": "four-child recursion gives 4^depth paths",
                "proof_semantics": False,
                "security_note": "client-side API credential is present in public frontend source",
            },
            "AURA": {
                "best_role": "typed hypothesis framing and Telegram interface",
                "risk": "role consensus and interpretation are not proof",
                "proof_semantics": False,
                "security_note": "sanitize backend text before HTML rendering",
            },
            "HRain": {
                "best_role": "persistent provenance graph, hierarchy and import/export",
                "risk": "memory stores visited states but does not create a semantic quotient",
                "proof_semantics": False,
            },
            "JANUS_GATE": {
                "best_role": "independent witness/proof/transformation verification",
                "required": True,
            },
        },
        "assertions": assertions,
        "p_equals_np_progress": "RESEARCH_ARCHITECTURE_AND_ERROR_CONTROL_ONLY",
        "verdict": "The fusion improves research organization and soundness, but does not reduce worst-case SAT complexity. Recursive expansion is exponential, persistent memory may hold exponentially many residuals, and exact selection may hide SAT-hard work.",
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=9379992)
    parser.add_argument("--cases", type=int, default=600)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run(args.seed, args.cases)
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.self_test and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
