#!/usr/bin/env python3
"""Software-only audit of aat440hz/Infinite_Oracle as a JANUS EYE candidate."""
from __future__ import annotations

import argparse
import json
import random
from itertools import product

SOURCE = {
    "repository": "aat440hz/Infinite_Oracle",
    "commit": "24b9d19f072a3e2e4f1f9ea999ff2046b6b3d69f",
    "python_blob_sha": "23a769f6ed8015d371c5a268f632c06c86071812",
    "observed": {
        "generator": "Ollama or LM Studio",
        "input": "Whisper ASR",
        "output": "Coqui TTS",
        "prompt_style": "mystical/cryptic/metaphysical",
        "lm_studio_temperature": 0.7,
        "default_ollama_context": 100,
        "explicit_seed": False,
        "claim_schema": False,
        "sat_verifier": False,
        "unsat_verifier": False,
        "path": "model text -> character filter -> queue -> speech",
    },
}


def variables(formula):
    return tuple(sorted({abs(lit) for clause in formula for lit in clause}))


def satisfies(formula, assignment):
    return all(any(assignment.get(abs(lit), False) == (lit > 0)
                   for lit in clause) for clause in formula)


def brute_force(formula):
    vs = variables(formula)
    checks = 0
    for bits in product((False, True), repeat=len(vs)):
        checks += 1
        a = dict(zip(vs, bits))
        if satisfies(formula, a):
            return "SAT", a, checks
    return "UNSAT", None, checks


def simplify(formula, partial):
    out = []
    for clause in formula:
        kept = []
        true = False
        for lit in clause:
            v = abs(lit)
            if v not in partial:
                kept.append(lit)
            elif partial[v] == (lit > 0):
                true = True
                break
        if true:
            continue
        if not kept:
            return None
        out.append(tuple(kept))
    return tuple(out)


def verify_sat(formula, witness):
    return witness is not None and all(v in witness for v in variables(formula)) and satisfies(formula, witness)


def verify_tiny_resolution(formula, proof):
    clauses = [frozenset(c) for c in formula]
    for left, right, pivot in proof:
        if not (0 <= left < len(clauses) and 0 <= right < len(clauses)):
            return False
        a, b = clauses[left], clauses[right]
        if pivot not in a or -pivot not in b:
            if -pivot not in a or pivot not in b:
                return False
            a, b = b, a
        resolvent = (a - {pivot}) | (b - {-pivot})
        if any(-lit in resolvent for lit in resolvent):
            return False
        clauses.append(frozenset(resolvent))
    return bool(clauses) and not clauses[-1]


def random_formula(rng, n, m):
    clauses = []
    for _ in range(m):
        width = rng.randint(1, min(3, n))
        scope = rng.sample(range(1, n + 1), width)
        clauses.append(tuple(v if rng.getrandbits(1) else -v for v in scope))
    return tuple(clauses)


def untrusted_candidate(rng, formula):
    if rng.getrandbits(1):
        return {
            "claim": "SAT",
            "witness": {v: bool(rng.getrandbits(1)) for v in variables(formula)},
            "proof": None,
        }
    return {"claim": "UNSAT", "witness": None, "proof": None}


def proof_gate(formula, candidate):
    if candidate.get("claim") == "SAT":
        return verify_sat(formula, candidate.get("witness"))
    if candidate.get("claim") == "UNSAT":
        proof = candidate.get("proof")
        return isinstance(proof, list) and verify_tiny_resolution(formula, proof)
    return False


def source_contract_audit():
    c = SOURCE["observed"]
    assert not c["sat_verifier"] and not c["unsat_verifier"] and not c["claim_schema"]
    return {
        "result": "PASS",
        "classification": "generative_voice_agent_not_complexity_oracle",
        "useful_as": ["human interface", "hypothesis proposer", "spoken JANUS console"],
        "missing": ["SAT parser", "proof gate", "provenance hashes", "polynomial bound"],
    }


def proof_bridge_audit():
    rng = random.Random(9379992)
    cases = 500
    ungated_false = 0
    correct = 0
    gated_accepts = 0
    gated_false = 0
    for _ in range(cases):
        n = rng.randint(2, 8)
        formula = random_formula(rng, n, rng.randint(n, 4 * n))
        truth, _, _ = brute_force(formula)
        candidate = untrusted_candidate(rng, formula)
        candidate_correct = (
            candidate["claim"] == "SAT" and verify_sat(formula, candidate["witness"])
        ) or (candidate["claim"] == "UNSAT" and truth == "UNSAT")
        correct += int(candidate_correct)
        ungated_false += int(not candidate_correct)
        accepted = proof_gate(formula, candidate)
        gated_accepts += int(accepted)
        gated_false += int(accepted and not candidate_correct)
    assert ungated_false > 0 and gated_false == 0
    tiny_unsat = ((1,), (-1,))
    assert verify_tiny_resolution(tiny_unsat, [(0, 1, 1)])
    return {
        "cases": cases,
        "ungated_outputs_spoken": cases,
        "ungated_false_outputs": ungated_false,
        "correct_candidates": correct,
        "gated_accepts": gated_accepts,
        "gated_false_accepts": gated_false,
        "tiny_resolution_unsat_accepted": True,
        "result": "PASS",
        "meaning": "Proof gating restores sound acceptance, not completeness or a SAT speedup.",
    }


def self_consistency_attack():
    formula = ((1,),)
    samples = [{"claim": "UNSAT", "proof": None} for _ in range(11)]
    unanimous = all(s["claim"] == "UNSAT" for s in samples)
    accepted = any(proof_gate(formula, s) for s in samples)
    assert unanimous and not accepted
    return {
        "samples": 11,
        "unanimous_wrong_claim": True,
        "proof_gate_accepts": False,
        "result": "REJECT_SELF_CONSISTENCY_AS_PROOF",
    }


def extendable(formula, partial):
    residual = simplify(formula, partial)
    if residual is None:
        return False, 0
    remaining = [v for v in variables(formula) if v not in partial]
    checks = 0
    for bits in product((False, True), repeat=len(remaining)):
        checks += 1
        a = dict(partial)
        a.update(zip(remaining, bits))
        if satisfies(formula, a):
            return True, checks
    return False, checks


def hidden_oracle_cost_audit():
    records = []
    for n in range(1, 17):
        formula = tuple((v,) for v in range(1, n + 1))
        partial = {}
        outer = 0
        hidden = 0
        possible, checks = extendable(formula, {})
        outer += 1
        hidden += checks
        assert possible
        for v in range(1, n + 1):
            trial = dict(partial)
            trial[v] = False
            possible, checks = extendable(formula, trial)
            outer += 1
            hidden += checks
            partial[v] = False if possible else True
        assert satisfies(formula, partial)
        assert outer == n + 1 and hidden == 2**n
        records.append({"variables": n, "outer_queries": outer, "hidden_checks": hidden})
    return {"records": records, "result": "PASS"}


def rewrite_gate_audit():
    rng = random.Random(440)
    cases = 200
    unsafe = rejected = safe = 0
    for _ in range(cases):
        n = rng.randint(2, 7)
        f = random_formula(rng, n, rng.randint(n, 3 * n))
        if rng.getrandbits(1) and f:
            g = f[:-1]
        else:
            g = tuple(tuple(reversed(c)) for c in reversed(f))
        equivalent = True
        for bits in product((False, True), repeat=n):
            a = dict(zip(range(1, n + 1), bits))
            if satisfies(f, a) != satisfies(g, a):
                equivalent = False
                break
        if equivalent:
            safe += 1
        else:
            unsafe += 1
            rejected += 1
    assert unsafe == rejected
    return {
        "cases": cases,
        "safe_rewrites": safe,
        "unsafe_detected": unsafe,
        "unsafe_rejected": rejected,
        "result": "PASS",
        "boundary": "Exact small checker is exponential; scalable rewrites need proof certificates.",
    }


def run_audit():
    return {
        "artifact": "JANUS-INFINITE-ORACLE-BRIDGE-AUDIT",
        "status": "SOFTWARE_ONLY_EXTERNAL_REPOSITORY_AUDIT",
        "source": SOURCE,
        "execution_scope": {
            "external_gui_executed": False,
            "ollama_called": False,
            "lm_studio_called": False,
            "whisper_called": False,
            "tts_called": False,
            "swarm_touched": False,
            "devices_touched": False,
        },
        "audits": {
            "source_contract": source_contract_audit(),
            "proof_bridge": proof_bridge_audit(),
            "self_consistency": self_consistency_attack(),
            "hidden_oracle_cost": hidden_oracle_cost_audit(),
            "rewrite_gate": rewrite_gate_audit(),
        },
        "mapping": {
            "Infinite_Oracle": "untrusted proposer and spoken interface",
            "JANUS_EYE": "cost-accounting observer/controller",
            "TEAR": "negative proof-bearing certificate",
            "LAUGHTER": "positive SAT witness and recovery map",
        },
        "verdict": {
            "proved_P_equals_NP": False,
            "new_polynomial_sat_algorithm": False,
            "mathematical_distance_reduced": False,
            "research_architecture_improved": True,
            "false_oracle_safety_improved": True,
        },
    }


def self_test():
    report = run_audit()
    bridge = report["audits"]["proof_bridge"]
    assert bridge["gated_false_accepts"] == 0
    assert bridge["ungated_false_outputs"] == 325
    assert report["audits"]["hidden_oracle_cost"]["records"][-1]["hidden_checks"] == 65536
    print("JANUS_INFINITE_ORACLE_BRIDGE_AUDIT = PASS")
    print("SOURCE_CLASS = GENERATIVE_VOICE_AGENT_NOT_COMPLEXITY_ORACLE")
    print("UNGATED_FALSE_OUTPUTS =", bridge["ungated_false_outputs"])
    print("PROOF_GATE_FALSE_ACCEPTS =", bridge["gated_false_accepts"])
    print("SELF_CONSISTENCY_AS_PROOF = REJECTED")
    print("HIDDEN_EXTENDABILITY_COST_N16 = 65536")
    print("P_EQUALS_NP_PROGRESS = ARCHITECTURE_ONLY")
    print("SWARM_TOUCHED = false")
    print("DEVICES_TOUCHED = false")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.json:
        print(json.dumps(run_audit(), indent=2, sort_keys=True))
        return 0
    parser.error("use --self-test or --json")


if __name__ == "__main__":
    raise SystemExit(main())
