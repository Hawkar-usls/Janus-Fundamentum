from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r50g25y_minimal_w_policy_counterexample_forensics as y
import janus_trump_r50g25ap_interleaved_r33_rup_combined_potential as ap

GATE = "JANUS_TRUMP_R50G25AQ_OUTER_DP_PHASE_COUNT_OR_GLOBAL_AMORTIZED_POTENTIAL_COUNTEREXAMPLE"
PREREG_COMMIT = "a57380d38b78fe013d131f3d26e54c3e9620dd18"
PARENT_AP_SYNC_HEAD = "ce0a7684dae0991caec78a976fc1805f347b4af5"
SUCCESS_WITH_SCALAR_CEX = "OUTER_DP_PHASE_COUNT_STRUCTURALLY_BOUNDED_BY_V0__GLOBAL_SCALAR_COUNTEREXAMPLE_FOUND"
SUCCESS_SCALAR_SURVIVES = "OUTER_DP_PHASE_COUNT_STRUCTURALLY_BOUNDED_BY_V0__GLOBAL_SCALAR_SURVIVES_FROZEN_AUDIT"
CONTRACT_COUNTEREXAMPLE = "OUTER_DP_PHASE_COUNT_OR_OPERATOR_CONTRACT_COUNTEREXAMPLE_FOUND"


def canonical(formula):
    return r33.canonical_formula(formula)


def vars_set(formula):
    return set(map(int, r33.variables(canonical(formula))))


def clv(formula):
    return tuple(map(int, r33.measure(canonical(formula))))


def bipolar_vars(formula):
    f = canonical(formula)
    out = []
    for v in r33.variables(f):
        pos = any(v in c for c in f)
        neg = any(-v in c for c in f)
        if pos and neg:
            out.append(int(v))
    return out


def exact_dp_contract(formula, pivot, context):
    before = canonical(formula)
    before_vars = vars_set(before)
    rec = y.exact_dp_record(before, int(pivot))
    if rec is None:
        return None, [{"kind": "REPLAY_OR_IMPLEMENTATION_FAILURE", "context": context, "detail": "requested pivot is not bipolar"}]
    after = canonical(rec["transformed"])
    after_vars = vars_set(after)
    failures = []
    if not rec.get("replay_pass"):
        failures.append({"kind": "REPLAY_OR_IMPLEMENTATION_FAILURE", "context": context, "detail": "exact DP independent replay failed"})
    if int(pivot) in after_vars:
        failures.append({"kind": "EXACT_DP_PIVOT_REINTRODUCTION", "context": context, "pivot": int(pivot), "after_vars": sorted(after_vars)})
    allowed = before_vars - {int(pivot)}
    if not after_vars <= allowed:
        failures.append({"kind": "EXACT_DP_NEW_VARIABLE_INTRODUCTION", "context": context, "pivot": int(pivot), "new_vars": sorted(after_vars - allowed)})
    if len(after_vars) > len(before_vars) - 1:
        failures.append({"kind": "EXACT_DP_VARIABLE_DESCENT_FAILURE", "context": context, "before_V": len(before_vars), "after_V": len(after_vars), "pivot": int(pivot)})
    return {
        "context": context,
        "pivot": int(pivot),
        "before_CLV": list(clv(before)),
        "after_CLV": list(clv(after)),
        "before_vars": sorted(before_vars),
        "after_vars": sorted(after_vars),
        "pair_checks": int(rec.get("pair_checks", 0)),
        "relation": rec.get("relation"),
        "replay_pass": bool(rec.get("replay_pass")),
        "transformed": after,
    }, failures


def dp_explosion_gadget(k=8, shared=8):
    pivot = 1
    pos_shared = list(range(2, 2 + shared))
    neg_shared = list(range(2 + shared, 2 + 2 * shared))
    pos_markers = list(range(2 + 2 * shared, 2 + 2 * shared + k))
    neg_markers = list(range(2 + 2 * shared + k, 2 + 2 * shared + 2 * k))
    clauses = []
    for m in pos_markers:
        clauses.append(tuple([pivot] + pos_shared + [m]))
    for m in neg_markers:
        clauses.append(tuple([-pivot] + neg_shared + [m]))
    return canonical(clauses), pivot


def gamma(formula, M):
    _C, L, V = clv(formula)
    return int(L + int(M) * V)


def audit_scalar_candidate():
    formula, pivot = dp_explosion_gadget()
    C0, L0, V0 = clv(formula)
    M = C0 * V0 + 1
    rec, failures = exact_dp_contract(formula, pivot, "FROZEN_DP_EXPLOSION_GADGET")
    if rec is None:
        return {"technical_failure": failures[0] if failures else {"kind": "REPLAY_OR_IMPLEMENTATION_FAILURE"}}
    after = rec["transformed"]
    gb = gamma(formula, M)
    ga = gamma(after, M)
    return {
        "technical_failure": failures[0] if failures else None,
        "pivot": pivot,
        "root_CLV": [C0, L0, V0],
        "after_CLV": list(clv(after)),
        "M": M,
        "Gamma_before": gb,
        "Gamma_after": ga,
        "Gamma_delta": ga - gb,
        "strict_global_scalar_descent": ga < gb,
        "exact_DP_contract": {k: v for k, v in rec.items() if k != "transformed"},
    }


def deterministic_corpus():
    corpus = []
    for seed in range(52000, 52016):
        n = 8 if seed % 2 == 0 else 10
        ratio = (2.5, 3.0, 3.5)[seed % 3]
        corpus.append((f"RANDOM_{seed}_n{n}_r{ratio}", r33.deterministic_random_3cnf(seed, n=n, ratio=ratio)))
    for n in (8, 12):
        corpus.append((f"PRISM_{n}", r33.prism_tseitin(n)))
    gadget, _ = dp_explosion_gadget()
    corpus.append(("FROZEN_DP_EXPLOSION_GADGET", gadget))
    return corpus


def audit_dp_chains():
    all_rows = []
    formula_rows = []
    failures = []
    max_phases = 0
    max_initial_V = 0
    for name, formula in deterministic_corpus():
        state = canonical(formula)
        initial_V = len(vars_set(state))
        max_initial_V = max(max_initial_V, initial_V)
        phases = 0
        local_rows = []
        while True:
            b = bipolar_vars(state)
            if not b:
                break
            pivot = min(b)
            rec, fs = exact_dp_contract(state, pivot, f"{name}:DP{phases}")
            failures.extend(fs)
            if rec is None:
                break
            phases += 1
            local_rows.append({k: v for k, v in rec.items() if k != "transformed"})
            all_rows.append({"formula": name, **{k: v for k, v in rec.items() if k != "transformed"}})
            state = rec["transformed"]
            if phases > initial_V:
                failures.append({"kind": "OUTER_DP_PHASE_COUNT_BOUND_FAILURE", "formula": name, "initial_V": initial_V, "observed_DP_phases": phases})
                break
        max_phases = max(max_phases, phases)
        formula_rows.append({
            "formula": name,
            "initial_CLV": list(clv(formula)),
            "initial_V": initial_V,
            "DP_phase_count": phases,
            "bound": initial_V,
            "final_CLV": list(clv(state)),
            "final_bipolar_var_count": len(bipolar_vars(state)),
            "rows": local_rows,
        })
    return {
        "formula_count": len(formula_rows),
        "transition_count": len(all_rows),
        "max_observed_DP_phase_count": max_phases,
        "max_initial_V": max_initial_V,
        "formula_rows": formula_rows,
        "transition_rows": all_rows,
        "failures": failures,
    }


def audit_ap_phase_ranking():
    # AP had a transparent compatibility runner for a historical r33.simpl typo.
    # AQ applies the same alias without changing any scientific definition.
    if not hasattr(r33, "simpl"):
        r33.simpl = r33.simplify
    out = ap.audit_an_interleaving()
    if out.get("technical_failure") is not None:
        return {"technical_failure": out["technical_failure"]}
    failures = list(out.get("failures", []))
    for row in out.get("rows", []):
        before = tuple(map(int, row.get("before_CLV", [])))
        after = tuple(map(int, row.get("after_CLV", [])))
        if len(before) == 3 and len(after) == 3 and after[2] > before[2]:
            failures.append({"kind": "NON_DP_VARIABLE_INTRODUCTION", "transition": row.get("transition"), "round": row.get("round"), "before_CLV": list(before), "after_CLV": list(after)})
        if int(row.get("Phi_drop", 0)) <= 0:
            failures.append({"kind": "AP_PHASE_RANKING_REPLAY_FAILURE", "transition": row.get("transition"), "round": row.get("round"), "Phi_drop": row.get("Phi_drop")})
    return {
        "technical_failure": None,
        "root_CLV": out.get("root_CLV"),
        "root_constants": out.get("root_constants"),
        "R33_steps": out.get("R33_steps"),
        "RUP_steps": out.get("RUP_steps"),
        "successful_combined_steps": out.get("successful_combined_steps"),
        "minimum_observed_Phi_drop": out.get("minimum_observed_Phi_drop"),
        "reentry": out.get("reentry"),
        "failures": failures,
    }


def run():
    scalar = audit_scalar_candidate()
    chains = audit_dp_chains()
    phase = audit_ap_phase_ranking()

    failures = []
    if scalar.get("technical_failure") is not None:
        failures.append(scalar["technical_failure"])
    failures.extend(chains.get("failures", []))
    if phase.get("technical_failure") is not None:
        failures.append({"kind": "AP_PHASE_RANKING_REPLAY_FAILURE", "detail": phase["technical_failure"]})
    failures.extend(phase.get("failures", []))

    if failures:
        verdict = CONTRACT_COUNTEREXAMPLE
    elif scalar["strict_global_scalar_descent"]:
        verdict = SUCCESS_SCALAR_SURVIVES
    else:
        verdict = SUCCESS_WITH_SCALAR_CEX

    structural_certificate = {
        "exact_DP": "Every resolvent is formed only from literals already present in positive/negative parent clauses after removing pivot x/-x; canonicalization/subsumption only delete. Therefore Vars(after) subset Vars(before)-{x} and V strictly decreases on every accepted exact-DP transition.",
        "RUP": "RUP replaces one existing clause by a proper subclause; it introduces no variable.",
        "R33": "TAUTOLOGY/UNIT/PURE/SUBSUMPTION/BCE only delete clauses/literals; BVE forms resolvents from existing parent literals after removing its pivot. No R33 rule introduces a new variable.",
        "phase_count_consequence": "Along any route composed only of exact-DP, R33 and RUP, exact-DP transitions <= V_initial and R33/RUP phase segments <= V_initial+1.",
        "hierarchical_ranking": "Use V as the outer rank. Inside each fixed-root phase use AP Phi_phase. Exact-DP may reset Phi_phase but strictly decreases V; within a phase AP Phi_phase strictly decreases.",
    }

    return {
        "gate": GATE,
        "preregistration_commit": PREREG_COMMIT,
        "parent_AP_sync_head": PARENT_AP_SYNC_HEAD,
        "verdict": verdict,
        "structural_certificate": structural_certificate,
        "frozen_global_scalar_attack": scalar,
        "finite_exact_DP_chain_audit": chains,
        "historical_AN_phase_ranking_replay": phase,
        "falsifier_count": len(failures),
        "falsifiers": failures,
        "scientific_scope": {
            "outer_exact_DP_transition_count": "STRUCTURALLY_BOUNDED_BY_INITIAL_V_FOR_THE_IMPLEMENTED_OPERATOR SET",
            "phase_segment_count": "AT_MOST_INITIAL_V_PLUS_ONE",
            "hierarchical_ranking_well_foundedness": "STRUCTURAL_PLUS_AP_PHASE_CERTIFICATE",
            "simple_global_AP_scalar_across_DP": "FALSIFIED_IF_RECORDED_COUNTEREXAMPLE_IS_PRESENT",
            "global_phase_root_size_bound": "OPEN",
            "end_to_end_polynomial_runtime": "OPEN",
            "reason_runtime_remains_open": "The number of phases is bounded, but exact-DP can increase explicit C,L. A polynomial bound on every phase-root state size in terms of the original input is still required before composing per-phase polynomial ledgers into an end-to-end polynomial runtime theorem."
        },
        "recommended_next_gate": "R50G25AR_GLOBAL_PHASE_ROOT_STATE_SIZE_ENVELOPE_OR_EXPLICIT_DP_BLOWUP_OBSTRUCTION",
        "firewalls": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
            "phase_count_bound_is_not_state_size_bound": True,
            "finite_replay_is_not_universal_proof": True,
            "end_to_end_polynomial_runtime_not_claimed": True,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="research/R50G25AQ_RESULT.json")
    args = parser.parse_args()
    result = run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "verdict": result["verdict"],
        "falsifier_count": result["falsifier_count"],
        "dp_transition_count": result["finite_exact_DP_chain_audit"]["transition_count"],
        "max_DP_phases": result["finite_exact_DP_chain_audit"]["max_observed_DP_phase_count"],
        "scalar_Gamma_delta": result["frozen_global_scalar_attack"].get("Gamma_delta"),
        "AP_min_Phi_drop": result["historical_AN_phase_ranking_replay"].get("minimum_observed_Phi_drop"),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
