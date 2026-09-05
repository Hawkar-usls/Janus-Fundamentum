from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g4_prefix_closure_microstep_authority as r50g4
import janus_trump_r50g5_immediate_bve_exact_descent_algebraic_reduction as r50g5

GATE = "JANUS_TRUMP_R50G9_EXPLICIT_WIDE_FIXPOINT_ANCESTRY_COUNTEREXAMPLE"
PIVOT = 1
POS_PARENT = (1, -2, -5, -9)
NEG_PARENT = (-1, 24, -30)
WIDE = (-2, -5, -9, 24, -30)
WIDTH_CAP = 4
EXPECTED_CORE_HASH = "c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb"


def canon(f):
    return r33.canonical_formula(f)


def max_width(f):
    return max((len(c) for c in canon(f)), default=0)


def nontaut_resolvent(a, b, lit):
    r = (set(a) - {lit}) | (set(b) - {-lit})
    if any(-x in r for x in r):
        return None
    return r33.canonical_clause(r)


def support_certificate(final_formula, wide_clause):
    f = canon(final_formula)
    c = r33.canonical_clause(wide_clause)
    rows = []
    used = set()
    for lit in c:
        witnesses = []
        for d in f:
            if -lit not in d:
                continue
            r = nontaut_resolvent(c, d, lit)
            if r is None:
                continue
            external = [x for x in d if x != -lit and x not in set(c) - {lit}]
            witnesses.append((d, r, external))
        if not witnesses:
            raise AssertionError(("R50G9_MISSING_NONBLOCKING_SUPPORT", lit, c))
        witnesses.sort(key=lambda x: x[0])
        d, r, external = witnesses[0]
        if not external:
            raise AssertionError(("R50G9_SUPPORT_HAS_NO_RUP_ESCAPE_LITERAL", lit, d))
        if d in used:
            raise AssertionError(("R50G9_SUPPORT_NOT_DISTINCT", lit, d))
        used.add(d)
        rows.append({
            "literal": int(lit),
            "support_clause": list(d),
            "nontaut_resolvent": list(r),
            "external_escape_literals": [int(x) for x in external],
        })
    return rows


def run():
    _sealed, core = r47j.load_counterexample()
    core = canon(core)
    if r50g4.fhash(core) != EXPECTED_CORE_HASH:
        raise AssertionError("R50G9_CORE_HASH_DRIFT")
    if r47j.normalize_to_certified_fixpoint(core)["final_formula_hash"] != EXPECTED_CORE_HASH:
        raise AssertionError("R50G9_CORE_NOT_FIXPOINT")

    source = canon(list(core) + [POS_PARENT, NEG_PARENT])
    if max_width(source) > WIDTH_CAP:
        raise AssertionError("R50G9_SOURCE_LEFT_W4")
    micro = r50g4.micro_r33_status(source)
    if micro["status"] != "IMMEDIATE_BVE_W4_ESCAPE":
        raise AssertionError(("R50G9_SOURCE_NOT_IMMEDIATE_ESCAPE", micro))
    direct = r50g4.first_r33_micro_candidate(source)
    if direct.get("rule") != "BOUNDED_VARIABLE_ELIMINATION" or int(direct.get("var", -1)) != PIVOT:
        raise AssertionError(("R50G9_FIRST_BVE_NOT_PIVOT1", direct))
    if tuple(WIDE) not in {tuple(c) for c in direct["resolvents"]}:
        raise AssertionError(("R50G9_PREDICTED_WIDE_RESOLVENT_MISSING", direct["resolvents"]))

    proof = r50g5.prove_immediate_bve_same_pivot(source)
    if not proof["applicable"]:
        raise AssertionError("R50G9_R50G5_PROOF_NOT_APPLICABLE")

    cand = r47j.macro_candidate_fixpoint(source, PIVOT)
    if cand is None:
        raise AssertionError("R50G9_SAME_PIVOT_CANDIDATE_MISSING")
    replay = r47j.independent_fixpoint_macro_replay(source, cand)
    if not replay["pass"]:
        raise AssertionError(("R50G9_INDEPENDENT_REPLAY_FAIL", replay))
    final = canon(cand["normalization"]["final_formula"])
    terminal = cand["normalization"]["terminal"]
    wide_present = tuple(WIDE) in set(final)
    local_witness = bool(terminal is None and max_width(final) > WIDTH_CAP and wide_present)

    support = []
    fixed_checks = None
    if local_witness:
        simp = r33.simplify(final)
        affine = r34.recognize_complete_affine_cnf(final)
        rup = r35b.run_candidate(final)
        if simp["history"] or simp["terminal"] != "STALLED_STACK_LEAN_CORE":
            raise AssertionError(("R50G9_FINAL_NOT_R33_FIXED", simp["terminal"], simp["history"][:1]))
        if affine["recognized"]:
            raise AssertionError("R50G9_FINAL_AFFINE_TERMINAL")
        if rup["status"] != "STALLED_RUP_CORE" or rup.get("history"):
            raise AssertionError(("R50G9_FINAL_NOT_RUP_FIXED", rup["status"], rup.get("history", [])[:1]))
        support = support_certificate(final, WIDE)
        fixed_checks = {
            "R33_fixed": True,
            "affine_negative": True,
            "RUP_fixed": True,
            "wide_clause_present": True,
            "support_witness_count": len(support),
            "support_witnesses_distinct": len({tuple(x["support_clause"]) for x in support}) == len(WIDE),
            "all_supports_have_external_escape": all(bool(x["external_escape_literals"]) for x in support),
        }

    no_alt = bool(local_witness and not proof["existing_certified_door_exists"])
    if local_witness and no_alt:
        verdict = "EXPLICIT_LOCAL_IMMEDIATE_BVE_GUARDED_OBSTRUCTION_FOUND__REACHABILITY_NOT_ESTABLISHED"
    elif local_witness:
        verdict = "LOCAL_WIDE_ANCESTRY_IMPOSSIBILITY_REFUTED__SAME_PIVOT_W4_SAFETY_REFUTED__ALTERNATE_CERTIFIED_DOOR_EXISTS"
    else:
        verdict = "CANDIDATE_DID_NOT_SURVIVE_AS_WIDE_CERTIFIED_FIXPOINT__R50G8_REMAINS_OPEN"

    return {
        "gate": GATE,
        "mode": "EXPLICIT_THEOREM_OR_COUNTEREXAMPLE",
        "source": {
            "hash": r50g4.fhash(source),
            "CLV": list(r33.measure(source)),
            "max_width": max_width(source),
            "pivot": PIVOT,
            "positive_parent": list(POS_PARENT),
            "negative_parent": list(NEG_PARENT),
            "predicted_wide_resolvent": list(WIDE),
            "R33_micro_status": micro["status"],
        },
        "same_pivot": proof,
        "final": {
            "hash": r50g4.fhash(final),
            "CLV": list(r33.measure(final)),
            "max_width": max_width(final),
            "terminal": terminal,
            "wide_clause_present": wide_present,
            "local_wide_fixpoint_witness": local_witness,
            "fixed_checks": fixed_checks,
            "support_certificate": support,
        },
        "interpretation": {
            "local_wide_ancestry_impossibility": "REFUTED" if local_witness else "OPEN",
            "local_same_pivot_W4_safety": "REFUTED" if local_witness else "OPEN",
            "local_existing_door_implication": "REFUTED" if no_alt else "NOT_REFUTED_BY_THIS_WITNESS",
            "witness_reachability_under_U_mu": "NOT_ESTABLISHED",
            "reachable_same_pivot_W4_safety": "OPEN",
            "immediate_BVE_case_eliminated": False,
        },
        "critical_next_obligation": (
            "REACHABILITY_SPECIFIC_EXCLUSION_OR_EXISTING_ALTERNATE_DOOR_THEOREM_FOR_WIDE_FIXPOINT_ANCESTRY_STATES"
            if local_witness else
            "CONTINUE_WIDE_ANCESTRY_IMPOSSIBILITY_ATTACK"
        ),
        "verdict": verdict,
        "firewall": {
            "HEURISTIC_AUTHORITY": False,
            "NEW_SEMANTIC_INFERENCE_RULE": False,
            "FINITE_SEARCH_IMPLIES_REACHABILITY": False,
            "U_MU": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "P_EQ_NP": "NOT_PROVED",
            "P_NE_NP": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False,
        },
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
