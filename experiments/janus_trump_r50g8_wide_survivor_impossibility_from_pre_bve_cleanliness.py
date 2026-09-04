from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g_smallest_first_exact_deadcore_falsifier as r50g
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4

GATE = "JANUS_TRUMP_R50G8_WIDE_SURVIVOR_IMPOSSIBILITY_FROM_PRE_BVE_CLEANLINESS"
WIDTH_CAP = 4


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def vars_set(f):
    return set(r33.variables(canon(f)))


def pre_bve_clean(f):
    f = canon(f)
    return (
        not any(r33.is_tautology(c) for c in f)
        and not any(len(c) == 1 for c in f)
        and not r33.pure_literals(f)
        and r33.first_subsumed_clause(f) is None
        and r33.first_blocked_clause(f) is None
    )


def nonblocking_supports_for_clause(formula, clause):
    """Return one exact BCE non-blocking witness per literal of clause.

    If clause is present in an R33 fixed point, such a witness must exist for
    every literal because otherwise the clause would be blocked and BCE would
    be applicable.  Witnesses for two different literals cannot be the same:
    a clause containing both opposite literals would make either corresponding
    resolvent tautological through the other literal.
    """
    f = canon(formula)
    c = tuple(clause)
    cset = set(c)
    out = {}
    for lit in c:
        witness = None
        for other in f:
            if -lit not in other:
                continue
            resolvent = (cset - {lit}) | (set(other) - {-lit})
            if any(-x in resolvent for x in resolvent):
                continue
            witness = tuple(other)
            break
        if witness is None:
            return None
        out[int(lit)] = witness
    if len(set(out.values())) != len(out):
        raise AssertionError(("R50G8_NONBLOCKING_SUPPORT_NOT_DISTINCT", c, out))
    return out


def inspect_immediate_bve_state(formula):
    f = canon(formula)
    if max_width(f) > WIDTH_CAP:
        raise AssertionError("R50G8_INPUT_OUTSIDE_W4")
    status = r50g4.micro_r33_status(f)
    if status["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        return {"applicable": False}
    if not pre_bve_clean(f):
        raise AssertionError("R50G8_IMMEDIATE_ESCAPE_NOT_PRE_BVE_CLEAN")

    direct = r50g4.first_r33_micro_candidate(f)
    if direct["kind"] != "PROPOSAL" or direct["rule"] != "BOUNDED_VARIABLE_ELIMINATION":
        raise AssertionError(("R50G8_ESCAPE_NOT_DIRECT_BVE", direct))
    x = int(direct["var"])
    d = canon(direct["after"])
    inherited = {c for c in f if x not in c and -x not in c}
    resolvents = {tuple(c) for c in direct["resolvents"]}
    post_dp_wide = [c for c in d if len(c) > WIDTH_CAP]
    for c in post_dp_wide:
        if c in inherited:
            raise AssertionError(("R50G8_WIDE_INHERITED_FROM_W4_INPUT", c))
        if c not in resolvents:
            raise AssertionError(("R50G8_POST_DP_WIDE_NOT_CROSS_RESOLVENT", c))

    candidate = r47j.macro_candidate_fixpoint(f, x)
    if candidate is None:
        raise AssertionError("R50G8_SAME_PIVOT_R47J_MISSING")
    replay = r47j.independent_fixpoint_macro_replay(f, candidate)
    if not replay["pass"]:
        raise AssertionError(("R50G8_R47J_REPLAY_FAIL", replay))

    normalization = candidate["normalization"]
    final = canon(normalization["final_formula"])
    terminal = normalization["terminal"]
    final_wide = [c for c in final if len(c) > WIDTH_CAP]

    normalization_bve_records = []
    for reduced in normalization["R33_reconstruction_results"]:
        for record in reduced["history"]:
            if record["rule"] == "BOUNDED_VARIABLE_ELIMINATION":
                normalization_bve_records.append(record)

    wide_fixpoint_certificate = None
    if terminal is None and final_wide:
        reduced = r33.simplify(final)
        if reduced["history"] or reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            raise AssertionError(("R50G8_FINAL_WIDE_NOT_R33_FIXED", reduced))
        affine = r34.recognize_complete_affine_cnf(final)
        if affine["recognized"]:
            raise AssertionError("R50G8_FINAL_WIDE_AFFINE_SHOULD_HAVE_TERMINATED")
        rup = r35b.run_candidate(final)
        if rup["status"] != "STALLED_RUP_CORE" or canon(rup["final_formula"]) != final:
            raise AssertionError(("R50G8_FINAL_WIDE_NOT_RUP_FIXED", rup["status"]))
        if r33.bve_candidate(final) is not None:
            raise AssertionError("R50G8_FINAL_WIDE_HAS_R33_BVE")

        clause_support = []
        for c in final_wide:
            supports = nonblocking_supports_for_clause(final, c)
            if supports is None:
                raise AssertionError(("R50G8_FINAL_WIDE_CLAUSE_WO_BCE_SUPPORT", c))
            clause_support.append({
                "wide_clause": list(c),
                "distinct_nonblocking_support_count": len(supports),
                "supports": [
                    {"literal": lit, "witness_clause": list(w)}
                    for lit, w in sorted(supports.items(), key=lambda kv: r33.lit_key(kv[0]))
                ],
            })

        wide_fixpoint_certificate = {
            "kind": (
                "DIRECT_DP_WIDE_SURVIVOR_TO_FIXPOINT"
                if not normalization_bve_records
                else "NORMALIZATION_BVE_DESCENDANT_WIDE_SURVIVOR_TO_FIXPOINT"
            ),
            "final_width": max_width(final),
            "wide_clause_count": len(final_wide),
            "R33_fixed": True,
            "affine_negative": True,
            "RUP_fixed": True,
            "BVE_fixed": True,
            "wide_clause_support": clause_support,
            "normalization_BVE_count": len(normalization_bve_records),
        }

    return {
        "applicable": True,
        "pivot": x,
        "input_hash": r50g4.fhash(f),
        "input_mu": list(r50g4.mu(f)),
        "post_DP_width": max_width(d),
        "post_DP_wide_clause_count": len(post_dp_wide),
        "post_DP_all_wide_are_cross_resolvents": True,
        "normalization_BVE_count": len(normalization_bve_records),
        "terminal": terminal,
        "final_hash": r50g4.fhash(final),
        "final_width": max_width(final),
        "same_pivot_safe": bool(terminal is not None or max_width(final) <= WIDTH_CAP),
        "final_nonterminal_wide": bool(terminal is None and final_wide),
        "wide_fixpoint_certificate": wide_fixpoint_certificate,
        "independent_replay_pass": True,
    }


def replay_frozen_reachable():
    rows = []
    terminal_roots = 0
    open_roots = 0
    for worker, n in enumerate(range(6, 11)):
        for i in range(80):
            m = 3 * n + (i % (3 * n + 1))
            seed = 50_700_000 + worker * 100_000 + i
            root, _ = r50g.make_planted(seed, n, m, "3CNF")
            if len(r33.variables(root)) != n:
                continue
            state = canon(root)
            seen = set()
            bound = 8 * max(1, len(r33.variables(state))) + 4 * max(1, len(state)) + 32
            for step_index in range(bound):
                h = r50g4.fhash(state)
                if h in seen:
                    raise AssertionError(("R50G8_TRACE_CYCLE", worker, seed, h))
                seen.add(h)
                inspection = inspect_immediate_bve_state(state)
                if inspection["applicable"]:
                    rows.append({"worker": worker, "n": n, "m": m, "seed": seed, "step": step_index, **inspection})
                step = r50g4.refined_exact_step(state)
                if step["kind"] == "TERMINAL":
                    terminal_roots += 1
                    break
                if step["kind"] == "OPEN_OBSTRUCTION":
                    open_roots += 1
                    break
                state = canon(step["successor"])
            else:
                raise AssertionError(("R50G8_TRACE_BOUND", worker, seed))

    wide_rows = [r for r in rows if r["final_nonterminal_wide"]]
    return {
        "frozen_roots": 400,
        "terminal_roots": terminal_roots,
        "open_roots": open_roots,
        "immediate_BVE_states": len(rows),
        "same_pivot_safe": sum(int(r["same_pivot_safe"]) for r in rows),
        "same_pivot_terminal": sum(int(r["terminal"] is not None) for r in rows),
        "same_pivot_W4_reentry": sum(int(r["terminal"] is None and r["final_width"] <= WIDTH_CAP) for r in rows),
        "post_DP_wide_clauses_total": sum(r["post_DP_wide_clause_count"] for r in rows),
        "normalization_BVE_records_total": sum(r["normalization_BVE_count"] for r in rows),
        "final_nonterminal_wide_states": len(wide_rows),
        "first_wide_fixpoint_certificate": wide_rows[0] if wide_rows else None,
    }


def firewall(reachable_wide_found: bool):
    return {
        "HEURISTIC_AUTHORITY": False,
        "LEARNED_SELECTOR": False,
        "PROBABILISTIC_AUTHORITY": False,
        "NEW_SEMANTIC_INFERENCE_RULE": False,
        "NO_NEW_CORPUS": True,
        "FINITE_NO_FIND_IMPLIES_THEOREM": False,
        "WIDE_ANCESTRY_IMPOSSIBILITY_THEOREM": "REFUTED_ON_REACHABLE_WITNESS" if reachable_wide_found else "OPEN",
        "REACHABLE_SAME_PIVOT_W4_SAFETY": "REFUTED" if reachable_wide_found else "OPEN",
        "IMMEDIATE_BVE_CASE_ELIMINATED": False,
        "U_MU": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def run():
    reachable = replay_frozen_reachable()
    found = reachable["final_nonterminal_wide_states"] > 0
    verdict = (
        "EXPLICIT_FROZEN_REACHABLE_WIDE_FIXPOINT_ANCESTRY_CERTIFICATE_FOUND"
        if found
        else "SOURCE_LEMMAS_L1_L4_CLOSED__WIDE_SURVIVOR_REDUCED_TO_CERTIFIED_WIDE_FIXPOINT_ANCESTRY_OBSTRUCTION__UNIVERSAL_IMPOSSIBILITY_OPEN"
    )
    return {
        "gate": GATE,
        "mode": "SYMBOLIC_SOURCE_REDUCTION_WITH_FROZEN_REPLAY_CHECKER",
        "proved_from_frozen_source_definitions": [
            "L1_POST_DP_ONLY_CROSS_PIVOT_RESOLVENTS_CAN_BE_NEW_WIDE_CLAUSES",
            "L2_NON_BVE_NORMALIZATION_RULES_ARE_WIDTH_NONINCREASING",
            "L3_FINAL_WIDE_SURVIVOR_HAS_REPLAYABLE_DP_OR_BVE_ANCESTRY",
            "L4_FINAL_NONTERMINAL_STATE_IS_CERTIFIED_R33_AFFINE_RUP_FIXPOINT",
            "FIXED_WIDE_CLAUSE_REQUIRES_DISTINCT_NONBLOCKING_SUPPORT_WITNESS_PER_LITERAL",
        ],
        "critical_unproved_step": "NO_PRE_BVE_CLEAN_W4_SOURCE_CAN_GENERATE_A_WIDE_ANCESTRY_CERTIFICATE_ENDING_AT_A_NONTERMINAL_CERTIFIED_NORMALIZATION_FIXPOINT",
        "reachable_replay": reachable,
        "verdict": verdict,
        "firewall": firewall(found),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    out = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n")
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
