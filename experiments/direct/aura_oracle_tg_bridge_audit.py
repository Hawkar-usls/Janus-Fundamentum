#!/usr/bin/env python3
"""
JANUS software-only audit of Hawkar-usls/aura-oracle-tg.

This is an architectural audit pinned to the public frontend revision:
  repository: Hawkar-usls/aura-oracle-tg
  commit: b5360f08ea6b5369fbd7f56d09d7be93438628a6
  index.html blob: f13a0084a75a72899a8e1b60f4ca30b3243dbcda

No Telegram bot, ngrok backend, model server, swarm node, device, NAS,
miner, biological sample, or physical junction is contacted.

The test asks whether AURA's fixed four-card graph can serve as a
proof-carrying JANUS Observer for SAT / P versus NP research.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SOURCE = {
    "repository": "Hawkar-usls/aura-oracle-tg",
    "commit": "b5360f08ea6b5369fbd7f56d09d7be93438628a6",
    "index_blob": "f13a0084a75a72899a8e1b60f4ca30b3243dbcda",
    "frontend_only": True,
    "observed_endpoints": [
        "/api/get_user_state",
        "/api/get_invoice?app=aura",
        "/api/generate_cards",
        "/api/interpret",
    ],
    "observed_contract": {
        "card_limit": 4,
        "roles": ["PAST", "OBSTACLE", "GUIDE", "OUTCOME"],
        "request_uses_selected_node_label": True,
        "existing_graph_is_reset_before_recast": True,
        "selected_node_is_not_reset_in_same_block": True,
        "new_links_use_selected_node_id": True,
        "interpretation_is_inserted_as_innerHTML": True,
        "claim_schema_present": False,
        "proof_schema_present": False,
        "cost_accounting_present": False,
    },
}

Clause = tuple[int, ...]
CNF = tuple[Clause, ...]


def variables(formula: CNF) -> list[int]:
    return sorted({abs(lit) for clause in formula for lit in clause})


def satisfies(formula: CNF, assignment: dict[int, bool]) -> bool:
    for clause in formula:
        if not any(assignment.get(abs(lit), False) == (lit > 0) for lit in clause):
            return False
    return True


def brute_force_truth(formula: CNF) -> tuple[bool, dict[int, bool] | None, int]:
    vars_ = variables(formula)
    checked = 0
    for bits in itertools.product([False, True], repeat=len(vars_)):
        checked += 1
        assignment = dict(zip(vars_, bits))
        if satisfies(formula, assignment):
            return True, assignment, checked
    return False, None, checked


def exhaustive_unsat_certificate(formula: CNF) -> dict[str, Any]:
    vars_ = variables(formula)
    rows = []
    for bits in itertools.product([False, True], repeat=len(vars_)):
        assignment = dict(zip(vars_, bits))
        rows.append({
            "assignment": {str(k): v for k, v in assignment.items()},
            "satisfies": satisfies(formula, assignment),
        })
    return {"kind": "EXHAUSTIVE_SMALL_ONLY", "rows": rows}


def verify_unsat_certificate(formula: CNF, certificate: Any) -> bool:
    if not isinstance(certificate, dict):
        return False
    if certificate.get("kind") != "EXHAUSTIVE_SMALL_ONLY":
        return False
    rows = certificate.get("rows")
    if not isinstance(rows, list):
        return False
    vars_ = variables(formula)
    expected = 1 << len(vars_)
    if len(rows) != expected:
        return False
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            return False
        raw = row.get("assignment")
        if not isinstance(raw, dict):
            return False
        try:
            assignment = {int(k): bool(v) for k, v in raw.items()}
        except (TypeError, ValueError):
            return False
        key = tuple(assignment.get(v, False) for v in vars_)
        if key in seen:
            return False
        seen.add(key)
        if satisfies(formula, assignment):
            return False
        if row.get("satisfies") is not False:
            return False
    return len(seen) == expected


def verify_claim(formula: CNF, claim: dict[str, Any]) -> tuple[bool, str]:
    claim_type = claim.get("claim_type")
    if claim_type == "SAT":
        raw = claim.get("witness")
        if not isinstance(raw, dict):
            return False, "SAT_WITHOUT_WITNESS"
        try:
            witness = {int(k): bool(v) for k, v in raw.items()}
        except (TypeError, ValueError):
            return False, "MALFORMED_WITNESS"
        return (
            (True, "VERIFIED_SAT")
            if satisfies(formula, witness)
            else (False, "INVALID_SAT_WITNESS")
        )

    if claim_type == "UNSAT":
        ok = verify_unsat_certificate(formula, claim.get("certificate"))
        return (True, "VERIFIED_UNSAT") if ok else (False, "UNSAT_WITHOUT_VALID_PROOF")

    return False, "HYPOTHESIS_ONLY"


@dataclass
class AuraGraphState:
    root_id: int = 1
    selected_id: int = 1
    node_ids: tuple[int, ...] = (1,)

    def recast(self, card_count: int = 4) -> dict[str, Any]:
        request_source_id = self.selected_id
        nodes = [self.root_id] if len(self.node_ids) > 1 else list(self.node_ids)
        new_ids = list(range(1000, 1000 + min(card_count, 4)))
        links = [(request_source_id, nid) for nid in new_ids]
        resulting_nodes = tuple(nodes + new_ids)
        detached_links = [
            (src, dst) for src, dst in links
            if src not in resulting_nodes or dst not in resulting_nodes
        ]
        return {
            "request_source_id": request_source_id,
            "resulting_nodes": resulting_nodes,
            "links": links,
            "detached_links": detached_links,
        }


def random_cnf(rng: random.Random, n_vars: int, n_clauses: int) -> CNF:
    clauses: list[Clause] = []
    for _ in range(n_clauses):
        width = rng.choice([1, 2, 3])
        chosen = rng.sample(range(1, n_vars + 1), k=min(width, n_vars))
        clause = tuple(v if rng.random() < 0.5 else -v for v in chosen)
        clauses.append(clause)
    return tuple(clauses)


def deterministic_bad_or_mixed_claim(
    formula: CNF,
    truth: bool,
    witness: dict[int, bool] | None,
    index: int,
) -> dict[str, Any]:
    digest = hashlib.sha256(repr((formula, index)).encode()).digest()
    mode = digest[0] % 6

    if mode == 0 and truth and witness is not None:
        return {
            "claim_type": "SAT",
            "witness": {str(k): v for k, v in witness.items()},
            "cards": ["PAST", "OBSTACLE", "GUIDE", "OUTCOME"],
        }
    if mode == 1 and not truth:
        return {
            "claim_type": "UNSAT",
            "certificate": exhaustive_unsat_certificate(formula),
            "cards": ["PAST", "OBSTACLE", "GUIDE", "OUTCOME"],
        }
    if mode in (2, 3):
        return {
            "claim_type": "UNSAT",
            "cards": ["PAST", "OBSTACLE", "GUIDE", "OUTCOME"],
            "interpretation": "All four roles agree.",
        }

    vars_ = variables(formula)
    fake = {str(v): bool((digest[v % len(digest)] >> (v % 8)) & 1) for v in vars_}
    return {
        "claim_type": "SAT",
        "witness": fake,
        "cards": ["PAST", "OBSTACLE", "GUIDE", "OUTCOME"],
    }


def claim_is_true(formula: CNF, claim: dict[str, Any], truth: bool) -> bool:
    if claim.get("claim_type") == "SAT":
        raw = claim.get("witness")
        if not isinstance(raw, dict):
            return False
        try:
            witness = {int(k): bool(v) for k, v in raw.items()}
        except (TypeError, ValueError):
            return False
        return truth and satisfies(formula, witness)
    if claim.get("claim_type") == "UNSAT":
        return not truth
    return False


def run_audit(seed: int = 9379992, cases: int = 500) -> dict[str, Any]:
    rng = random.Random(seed)

    ungated_false = 0
    gated_false_accepts = 0
    gated_accepts = 0
    gated_rejects = 0
    true_claims_generated = 0

    for i in range(cases):
        n_vars = rng.randint(3, 7)
        n_clauses = rng.randint(n_vars, n_vars * 4)
        formula = random_cnf(rng, n_vars, n_clauses)
        truth, witness, _ = brute_force_truth(formula)
        claim = deterministic_bad_or_mixed_claim(formula, truth, witness, i)
        actually_true = claim_is_true(formula, claim, truth)
        if actually_true:
            true_claims_generated += 1
        else:
            ungated_false += 1

        accepted, _ = verify_claim(formula, claim)
        if accepted:
            gated_accepts += 1
            if not actually_true:
                gated_false_accepts += 1
        else:
            gated_rejects += 1

    simple_sat: CNF = ((1,),)
    false_consensus = {
        "claim_type": "UNSAT",
        "cards": [
            {"role": "PAST", "claim": "UNSAT"},
            {"role": "OBSTACLE", "claim": "UNSAT"},
            {"role": "GUIDE", "claim": "UNSAT"},
            {"role": "OUTCOME", "claim": "UNSAT"},
        ],
        "interpretation": "UNSAT",
    }
    consensus_gate, consensus_reason = verify_claim(simple_sat, false_consensus)

    graph_state = AuraGraphState(root_id=1, selected_id=102, node_ids=(1, 100, 101, 102, 103))
    recast = graph_state.recast(4)
    branch_growth = {str(depth): 4 ** depth for depth in range(1, 13)}

    janus_role_map = {
        "ROOT": "original formula and formula_hash",
        "PAST": "known tractable structures and prior verified transformations",
        "OBSTACLE": "exact failed invariant, counterexample, or lower-bound witness",
        "GUIDE": "candidate order, module decomposition, proof language, or backdoor",
        "OUTCOME": "SAT witness, UNSAT Tear, or explicitly labelled OPEN hypothesis",
    }

    findings = {
        "source_class": "STRUCTURED_GENERATIVE_TELEGRAM_FRONTEND_NOT_COMPLEXITY_ORACLE",
        "backend_source_present_in_audited_repository": False,
        "frontend_accepts_cards_without_proof_schema": True,
        "frontend_accepts_interpretation_without_verification": True,
        "four_role_consensus_is_proof": False,
        "fixed_four_cards_guarantee_polynomial_total_work": False,
        "recursive_selected_child_recast_has_detached_source_risk": bool(recast["detached_links"]),
        "innerHTML_backend_rendering_is_safe_for_untrusted_proof_text": False,
        "useful_as_candidate_decomposition_and_provenance_ui": True,
        "p_equals_np_progress": "ARCHITECTURE_ONLY",
    }

    assertions = {
        "proof_gate_false_accepts_zero": gated_false_accepts == 0,
        "ungated_path_accepts_false_outputs": ungated_false > 0,
        "false_four_role_consensus_rejected": not consensus_gate,
        "detached_source_risk_reproduced": bool(recast["detached_links"]),
        "four_power_growth_is_exponential": branch_growth["12"] == 16_777_216,
    }
    passed = all(assertions.values())

    return {
        "audit": "JANUS_AURA_ORACLE_TG_BRIDGE",
        "status": "PASS" if passed else "FAIL",
        "software_only": True,
        "swarm_touched": False,
        "devices_touched": False,
        "network_backend_called": False,
        "source": SOURCE,
        "seed": seed,
        "random_small_cnf_cases": cases,
        "ungated_false_outputs": ungated_false,
        "true_claims_generated": true_claims_generated,
        "proof_gate_accepts": gated_accepts,
        "proof_gate_rejects": gated_rejects,
        "proof_gate_false_accepts": gated_false_accepts,
        "false_consensus_test": {
            "formula": [[1]],
            "roles_agree": 4,
            "claim": "UNSAT",
            "accepted_by_proof_gate": consensus_gate,
            "reason": consensus_reason,
        },
        "recursive_recast_test": recast,
        "branch_growth_4_pow_depth": branch_growth,
        "janus_role_map": janus_role_map,
        "findings": findings,
        "assertions": assertions,
        "verdict": (
            "AURA improves the JANUS research interface by providing a bounded four-role "
            "candidate graph and a human-in-the-loop Telegram surface. It does not supply "
            "a SAT oracle, a proof system, polynomial total-work accounting, or backend "
            "transparency. It becomes useful only after every OUTCOME is typed and verified: "
            "SAT requires a witness, UNSAT requires a Tear, transformations require a "
            "checkable equivalence/equisatisfiability certificate, and all other outputs "
            "remain HYPOTHESIS."
        ),
    }


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=9379992)
    parser.add_argument("--cases", type=int, default=500)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = run_audit(seed=args.seed, cases=args.cases)
    if args.output:
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.self_test and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
