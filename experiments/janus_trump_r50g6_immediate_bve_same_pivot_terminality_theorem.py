from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g5_immediate_bve_exact_descent_algebraic_reduction as r50g5

GATE = "JANUS_TRUMP_R50G6_IMMEDIATE_BVE_SAME_PIVOT_TERMINALITY_THEOREM"
WIDTH_CAP = 4
MIN_N = 6
MAX_N = 10
ROOTS_PER_WORKER = 80


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def fhash(f):
    return r50g4.fhash(canon(f))


def shift_formula(formula, offset: int):
    out = []
    for clause in canon(formula):
        out.append(tuple((abs(l) + offset) if l > 0 else -(abs(l) + offset) for l in clause))
    return canon(out)


def frozen_root(worker: int, i: int):
    n = MIN_N + int(worker)
    m = 3 * n + (i % (3 * n + 1))
    seed = 50_700_000 + worker * 100_000 + i
    root, _ = r50g.make_planted(seed, n, m, "3CNF")
    return canon(root), {"worker": worker, "index": i, "seed": seed, "n": n, "m": m}


def iter_frozen_reachable_states():
    for worker in range(5):
        for i in range(ROOTS_PER_WORKER):
            root, provenance = frozen_root(worker, i)
            n = MIN_N + worker
            if len(r33.variables(root)) != n:
                continue
            state = root
            seen = set()
            bound = 8 * max(1, len(r33.variables(state))) + 4 * max(1, len(state)) + 32
            for step_index in range(bound):
                h = fhash(state)
                if h in seen:
                    raise AssertionError(("R50G6_REACHABLE_CYCLE", provenance, h))
                seen.add(h)
                yield canon(state), {**provenance, "step": step_index, "hash": h}
                step = r50g4.refined_exact_step(state)
                if step["kind"] in ("TERMINAL", "OPEN_OBSTRUCTION"):
                    break
                state = canon(step["successor"])
            else:
                raise AssertionError(("R50G6_REACHABLE_TRACE_BOUND", provenance))


def first_frozen_immediate_bve_state():
    for state, provenance in iter_frozen_reachable_states():
        status = r50g4.micro_r33_status(state)
        if status["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
            continue
        proof = r50g5.prove_immediate_bve_same_pivot(state)
        if not proof["applicable"]:
            raise AssertionError("R50G6_R50G5_APPLICABILITY_DRIFT")
        return state, provenance, proof
    raise AssertionError("R50G6_NO_FROZEN_IMMEDIATE_BVE_WITNESS")


def certify_nonterminal_component():
    sealed, core = r47j.load_counterexample()
    core = canon(core)
    if max_width(core) > WIDTH_CAP:
        raise AssertionError(("R50G6_CORE_NOT_W4", max_width(core)))
    norm = r47j.normalize_to_certified_fixpoint(core)
    final = canon(norm["final_formula"])
    return {
        "core": core,
        "core_hash": r50g4.fhash(core),
        "core_CLV": list(r33.measure(core)),
        "core_max_width": max_width(core),
        "normalization_terminal": norm["terminal"],
        "normalization_final_hash": r50g4.fhash(final),
        "normalization_final_CLV": list(r33.measure(final)),
        "normalization_unchanged": final == core,
        "normalization_nonterminal": norm["terminal"] is None,
        "sealed_fixpoint_hash": sealed["genuine_residual_fixpoint"]["hash"],
    }


def exact_disjoint_composition_test():
    a, provenance, a_proof = first_frozen_immediate_bve_state()
    direct = r50g4.first_r33_micro_candidate(a)
    if direct["rule"] != "BOUNDED_VARIABLE_ELIMINATION":
        raise AssertionError("R50G6_A_NOT_IMMEDIATE_BVE")
    x = int(direct["var"])
    if not a_proof["same_pivot_terminal"]:
        raise AssertionError("R50G6_FROZEN_A_NOT_SAME_PIVOT_TERMINAL")

    core_cert = certify_nonterminal_component()
    core = core_cert.pop("core")
    preconditions = bool(core_cert["normalization_nonterminal"] and core_cert["normalization_unchanged"])
    if not preconditions:
        return {
            "preconditions_pass": False,
            "reason": "FROZEN_R47I_CORE_IS_NOT_AN_R47J_NORMALIZATION_FIXED_NONTERMINAL",
            "A": {"provenance": provenance, "hash": fhash(a), "pivot": x, "R50G5": a_proof},
            "B": core_cert,
            "reachability_of_composite": "NOT_ESTABLISHED",
        }

    offset = max(r33.variables(a), default=0) + 100
    b = shift_formula(core, offset)
    if set(r33.variables(a)) & set(r33.variables(b)):
        raise AssertionError("R50G6_COMPONENTS_NOT_DISJOINT")
    composite = canon(list(a) + list(b))
    if max_width(composite) > WIDTH_CAP:
        raise AssertionError(("R50G6_COMPOSITE_NOT_W4", max_width(composite)))

    status = r50g4.micro_r33_status(composite)
    if status["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        raise AssertionError(("R50G6_COMPOSITE_LOST_IMMEDIATE_BVE", status))
    c_direct = r50g4.first_r33_micro_candidate(composite)
    if int(c_direct["var"]) != x:
        raise AssertionError(("R50G6_COMPOSITE_PIVOT_DRIFT", x, c_direct.get("var")))

    c_proof = r50g5.prove_immediate_bve_same_pivot(composite)
    if not c_proof["applicable"]:
        raise AssertionError("R50G6_COMPOSITE_R50G5_NOT_APPLICABLE")

    candidate = r47j.macro_candidate_fixpoint(composite, x)
    if candidate is None:
        raise AssertionError("R50G6_COMPOSITE_SAME_PIVOT_CANDIDATE_MISSING")
    replay = r47j.independent_fixpoint_macro_replay(composite, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G6_COMPOSITE_REPLAY_FAIL", replay))
    final = canon(candidate["normalization"]["final_formula"])
    terminal = candidate["normalization"]["terminal"]

    # If component factorization behaves as the source lemmas predict, B survives
    # modulo its deterministic variable shift.  Equality is a stronger check than
    # merely observing nonterminality.
    b_survives_exactly = final == b
    local_terminality_refuted = terminal is None

    return {
        "preconditions_pass": True,
        "A": {
            "provenance": provenance,
            "hash": fhash(a),
            "CLV": list(r33.measure(a)),
            "max_width": max_width(a),
            "pivot": x,
            "same_pivot_terminal": bool(a_proof["same_pivot_terminal"]),
            "terminal": a_proof["terminal"],
        },
        "B": {**core_cert, "shift_offset": offset, "shifted_hash": fhash(b)},
        "composite": {
            "hash": fhash(composite),
            "CLV": list(r33.measure(composite)),
            "max_width": max_width(composite),
            "micro_status": status["status"],
            "pivot": int(c_direct["var"]),
            "same_pivot_terminal": terminal is not None,
            "terminal": terminal,
            "final_hash": fhash(final),
            "final_CLV": list(r33.measure(final)),
            "final_max_width": max_width(final),
            "B_survives_exactly": b_survives_exactly,
            "same_pivot_machine_safe": bool(c_proof["same_pivot_R47J_machine_safe"]),
            "independent_replay_pass": bool(replay["pass"]),
        },
        "local_terminality_refuted": local_terminality_refuted,
        "reachability_of_composite": "NOT_ESTABLISHED",
    }


def frozen_reachable_terminality_replay():
    rows = []
    for state, provenance in iter_frozen_reachable_states():
        if r50g4.micro_r33_status(state)["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
            continue
        proof = r50g5.prove_immediate_bve_same_pivot(state)
        rows.append({
            "provenance": provenance,
            "hash": fhash(state),
            "pivot": proof["pivot"],
            "terminal": proof["terminal"],
            "same_pivot_terminal": bool(proof["same_pivot_terminal"]),
            "same_pivot_machine_safe": bool(proof["same_pivot_R47J_machine_safe"]),
            "final_width": int(proof["final_width"]),
        })
    return rows


def firewall(local_refuted: bool, reachable_counterexample_count: int):
    return {
        "HEURISTIC_AUTHORITY": False,
        "LEARNED_SELECTOR": False,
        "PROBABILISTIC_AUTHORITY": False,
        "NEW_SEMANTIC_INFERENCE_RULE": False,
        "STRONG_LOCAL_TERMINALITY_THEOREM": "REFUTED" if local_refuted else "OPEN",
        "REACHABLE_TERMINALITY_THEOREM": "REFUTED" if reachable_counterexample_count else "OPEN",
        "IMMEDIATE_BVE_CASE_ELIMINATED": False,
        "FINITE_REPLAY_IMPLIES_UNIVERSAL_THEOREM": False,
        "U_MU": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def run():
    composition = exact_disjoint_composition_test()
    reachable = frozen_reachable_terminality_replay()
    reachable_counterexamples = [r for r in reachable if not r["same_pivot_terminal"]]
    terminal_hist = dict(sorted(Counter(str(r["terminal"]) for r in reachable).items()))
    local_refuted = bool(composition.get("local_terminality_refuted", False))

    if reachable_counterexamples:
        verdict = "REACHABLE_SAME_PIVOT_TERMINALITY_COUNTEREXAMPLE_FOUND__CANDIDATE_THEOREM_REFUTED"
    elif local_refuted:
        verdict = "STRONG_LOCAL_TERMINALITY_THEOREM_REFUTED_BY_EXACT_DISJOINT_COMPONENT_WITNESS__REACHABLE_TERMINALITY_REQUIRES_REACHABILITY_SPECIFIC_INVARIANT"
    elif not composition.get("preconditions_pass", False):
        verdict = "FROZEN_COMPOSITION_PRECONDITION_FAILED__TERMINALITY_THEOREMS_REMAIN_OPEN"
    else:
        verdict = "NO_TERMINALITY_COUNTEREXAMPLE_IN_FROZEN_TESTS__NO_UNIVERSAL_PROOF"

    return {
        "gate": GATE,
        "mode": "THEOREM_OR_COUNTEREXAMPLE",
        "source_lemmas": [
            "DP_X_FACTORIZES_OVER_DISJOINT_CONJUNCTION_COMPONENTS",
            "PRE_BVE_R33_RULE_APPLICABILITY_IS_COMPONENT_LOCAL_FOR_DISJOINT_VARIABLE_SETS",
            "LOCAL_BVE_GEOMETRY_CANNOT_BY_ITSELF_DELETE_AN_INDEPENDENT_NORMALIZATION_FIXED_COMPONENT",
        ],
        "composition": composition,
        "reachable_replay": {
            "frozen_roots": 400,
            "immediate_BVE_states": len(reachable),
            "same_pivot_terminal_count": sum(int(r["same_pivot_terminal"]) for r in reachable),
            "same_pivot_nonterminal_count": len(reachable_counterexamples),
            "terminal_histogram": terminal_hist,
            "first_reachable_counterexample": reachable_counterexamples[0] if reachable_counterexamples else None,
        },
        "critical_next_obligation": (
            "REACHABILITY_SPECIFIC_TERMINALITY_INVARIANT_OR_REFOCUS_ON_UNIVERSAL_SAME_PIVOT_W4_SAFETY"
            if local_refuted and not reachable_counterexamples
            else "PRESERVE_AND_MINIMIZE_REACHABLE_TERMINALITY_COUNTEREXAMPLE"
            if reachable_counterexamples
            else "TERMINALITY_REMAINS_OPEN"
        ),
        "verdict": verdict,
        "firewall": firewall(local_refuted, len(reachable_counterexamples)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
