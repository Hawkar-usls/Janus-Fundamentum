from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r34_affine_xor_terminal_against_tseitin_core as r34
import janus_trump_r35b_single_literal_rup_vivification as r35b
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r45a_byte_pinned_ascent_descent_macro as r45a
import janus_trump_r47f_small_reachable_fixpoint_full_macro_falsifier as r47f
import janus_trump_r47i_r47g_one_swap_macro_dead_complement_hunt as r47i
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r47m_post_dp_full_existing_stack_closure as r47m
import janus_trump_r47n_r47m_joint_stack_closure_one_swap_falsifier as r47n

EXPECTED_HASH = "eb653802ae710e5770e21878b5b38b2871cf0db16451b04cfc5451ca2c2e7502"
EXPECTED_ROOT_CLV = (76, 203, 22)
PIVOT = 12
EXPECTED_FORCED_CLV = [78, 216, 21]
EXPECTED_FINAL_CLV = [76, 204, 20]
SOURCE = (-17, 20, 26)
REPLACEMENT = (-17, -20, -26)


def clv(formula):
    return r33.measure(r33.canonical_formula(formula))


def load_root():
    _, center = r47n.load_center_original()
    mutated = r47i.mutate_one_clause(center, SOURCE, REPLACEMENT)
    if mutated is None:
        raise AssertionError("R47U_MUTATION_RECONSTRUCTION_FAILED")
    reached = r47f.reachable_fixpoint(mutated)
    if reached is None:
        raise AssertionError("R47U_NO_REACHABLE_FIXPOINT")
    root = r33.canonical_formula(reached["formula"])
    if r42.formula_hash(root) != EXPECTED_HASH or clv(root) != EXPECTED_ROOT_CLV:
        raise AssertionError(("R47U_ROOT_DRIFT", r42.formula_hash(root), clv(root)))
    return mutated, reached, root


def literal_counter(formula):
    return Counter(int(lit) for clause in formula for lit in clause)


def variable_counter(formula):
    return Counter(abs(int(lit)) for clause in formula for lit in clause)


def counter_delta(before, after):
    keys = sorted(set(before) | set(after), key=lambda x: (abs(x), x < 0) if isinstance(x, int) else x)
    return [{"key": int(k), "before": int(before.get(k,0)), "after": int(after.get(k,0)), "delta": int(after.get(k,0)-before.get(k,0))} for k in keys if before.get(k,0) != after.get(k,0)]


def subset_relations(removed, added):
    rows=[]
    for r in removed:
        sr=set(r)
        for a in added:
            sa=set(a)
            if sa < sr:
                rows.append({"kind":"ADDED_STRICT_SUBCLAUSE_OF_REMOVED","removed":list(r),"added":list(a),"literal_delta":len(a)-len(r)})
            elif sr < sa:
                rows.append({"kind":"REMOVED_STRICT_SUBCLAUSE_OF_ADDED","removed":list(r),"added":list(a),"literal_delta":len(a)-len(r)})
    return rows


def exact_v12_decomposition(root):
    dp = r45a.exact_dp_record(root, PIVOT)
    if dp is None:
        raise AssertionError("R47U_V12_NO_DP_RECORD")
    dp_replay = r45a.independent_dp_replay(root, dp)
    if not dp_replay["pass"]:
        raise AssertionError(("R47U_DP_REPLAY_FAIL", dp_replay))
    forced = r33.canonical_formula(dp["transformed"])
    norm1 = r47j.normalize_to_certified_fixpoint(forced)
    after_norm1 = r33.canonical_formula(norm1["final_formula"])
    if norm1["terminal"] is not None:
        raise AssertionError(("R47U_UNEXPECTED_TERMINAL_AFTER_DP12", norm1["terminal"]))
    bve, bve_ledger = r42.best_sa_bve_candidate(after_norm1)
    if bve is None or int(bve["var"]) != 11:
        raise AssertionError(("R47U_EXPECTED_BVE11_MISSING", None if bve is None else bve["var"]))
    bve_replay = r42.independent_sa_bve_replay(after_norm1, bve)
    if not bve_replay["pass"]:
        raise AssertionError(("R47U_BVE11_REPLAY_FAIL", bve_replay))
    after_bve = r33.canonical_formula(bve["transformed"])
    norm2 = r47j.normalize_to_certified_fixpoint(after_bve)
    final = r33.canonical_formula(norm2["final_formula"])
    next_bve, next_bve_ledger = r42.best_sa_bve_candidate(final)
    return {
        "DP": dp,
        "forced": forced,
        "norm1": norm1,
        "after_norm1": after_norm1,
        "BVE11": bve,
        "BVE11_replay": bve_replay,
        "BVE11_ledger": bve_ledger,
        "after_BVE11": after_bve,
        "norm2": norm2,
        "final": final,
        "next_BVE": next_bve,
        "next_BVE_ledger": next_bve_ledger,
    }


def final_fixpoint_integrity(final):
    reduced = r33.simplify(final)
    after_r33 = r33.canonical_formula(reduced["final_formula"])
    affine = r34.recognize_complete_affine_cnf(after_r33)
    rup = r35b.run_candidate(after_r33)
    rup_replay = r35b.independent_certificate_replay(after_r33, rup)
    after_rup = r33.canonical_formula(rup["final_formula"])
    bve, bve_ledger = r42.best_sa_bve_candidate(after_rup)
    passed = (
        reduced["terminal"] == "STALLED_STACK_LEAN_CORE"
        and reduced["total_rule_applications"] == 0
        and after_r33 == final
        and not affine["recognized"]
        and rup["status"] == "STALLED_RUP_CORE"
        and rup["successful_strengthenings"] == 0
        and after_rup == final
        and rup_replay["pass"]
        and bve is None
    )
    return {
        "pass": bool(passed),
        "R33_terminal": reduced["terminal"],
        "R33_applications": int(reduced["total_rule_applications"]),
        "affine_recognized": bool(affine["recognized"]),
        "RUP_status": rup["status"],
        "RUP_successful_strengthenings": int(rup["successful_strengthenings"]),
        "RUP_independent_replay_pass": bool(rup_replay["pass"]),
        "BVE_candidate_present": bve is not None,
        "BVE_variables_checked": int(bve_ledger["variables_checked"]),
    }


def second_dp_profile(root, final):
    rows=[]
    for var in r33.variables(final):
        c = r47j.macro_candidate_fixpoint(final, int(var))
        if c is None:
            continue
        replay = r47j.independent_fixpoint_macro_replay(final, c)
        if not replay["pass"]:
            raise AssertionError(("R47U_SECOND_PROFILE_REPLAY_FAIL",var,replay))
        g2=r33.canonical_formula(c["normalization"]["final_formula"])
        rows.append({
            "var":int(var),
            "input_CLV":list(clv(final)),
            "forced_DP_CLV":c["DP"]["measure_after_forced_DP"],
            "final_CLV":list(clv(g2)),
            "terminal":c["normalization"]["terminal"],
            "accepted_relative_to_v12_final":bool(c["accepted"]),
            "would_descend_relative_to_R47N_root":bool(c["normalization"]["terminal"] is not None or clv(g2)<clv(root)),
            "DP_independent_replay_pass":bool(c["DP_independent_replay_pass"]),
            "polynomial_intermediate_envelope_pass":bool(c["polynomial_intermediate_envelope_pass"]),
        })
    rows.sort(key=lambda r:r["var"])
    root_descent=[r for r in rows if r["would_descend_relative_to_R47N_root"]]
    return rows, root_descent


def run():
    mutated, reached, root = load_root()
    full_candidate = r47m.macro_candidate_full_closure(root, PIVOT)
    if full_candidate is None:
        raise AssertionError("R47U_R47M_V12_MISSING")
    if full_candidate["DP"]["measure_after_forced_DP"] != EXPECTED_FORCED_CLV or full_candidate["final_CLV"] != EXPECTED_FINAL_CLV or full_candidate["accepted"]:
        raise AssertionError(("R47U_R47M_V12_DRIFT", full_candidate["DP"]["measure_after_forced_DP"], full_candidate["final_CLV"], full_candidate["accepted"]))

    d = exact_v12_decomposition(root)
    final = d["final"]
    if list(clv(final)) != EXPECTED_FINAL_CLV:
        raise AssertionError(("R47U_FINAL_CLV_DRIFT", clv(final)))

    root_set=set(root); final_set=set(final)
    removed=tuple(sorted(root_set-final_set))
    added=tuple(sorted(final_set-root_set))
    unchanged=len(root_set & final_set)
    root_lits=literal_counter(root); final_lits=literal_counter(final)
    root_vars=variable_counter(root); final_vars=variable_counter(final)
    integrity=final_fixpoint_integrity(final)
    if not integrity["pass"]:
        raise AssertionError(("R47U_FINAL_NOT_JOINT_FIXPOINT", integrity))
    profile, root_descent = second_dp_profile(root, final)

    dp=d["DP"]
    pos=dp["positive"]
    neg=dp["negative"]
    resolvents=dp["full_non_tautological_resolvents"]
    out={
        "gate":"JANUS_TRUMP_R47U_R47N_V12_ONE_LITERAL_GAP_FORENSICS",
        "verdict":"R47U_V12_ONE_LITERAL_GAP_EXACTLY_DECOMPOSED__FORENSICS_ONLY",
        "R47N_root":{
            "mutated_original_hash":r47f.formula_hash(mutated),
            "fixpoint_hash":r42.formula_hash(root),
            "CLV":list(clv(root)),
            "trajectory":reached["trajectory"],
        },
        "v12_path":{
            "forced_DP_CLV":list(clv(d["forced"])),
            "after_first_R47J_CLV":list(clv(d["after_norm1"])),
            "BVE_var":int(d["BVE11"]["var"]),
            "after_BVE11_CLV":list(clv(d["after_BVE11"])),
            "final_CLV":list(clv(final)),
            "net_delta_CLV":[clv(final)[i]-clv(root)[i] for i in range(3)],
            "final_joint_fixpoint_integrity":integrity,
        },
        "DP12_local_debt":{
            "positive_parent_count":len(pos),
            "negative_parent_count":len(neg),
            "pair_checks":int(dp["pair_checks"]),
            "distinct_non_tautological_resolvent_count":len(resolvents),
            "forced_DP_CLV":dp["measure_after_forced_DP"],
            "polynomial_envelope_pass":bool(r45a.polynomial_envelope(root,dp)["pass"]),
        },
        "root_to_final_clause_diff":{
            "unchanged_clause_count":int(unchanged),
            "removed_clause_count":len(removed),
            "added_clause_count":len(added),
            "removed_clauses":[list(c) for c in removed],
            "added_clauses":[list(c) for c in added],
            "subset_relations":subset_relations(removed,added),
            "net_clause_delta":len(final)-len(root),
            "net_literal_delta":sum(len(c) for c in final)-sum(len(c) for c in root),
            "net_variable_delta":len(r33.variables(final))-len(r33.variables(root)),
        },
        "signed_literal_occurrence_deltas":counter_delta(root_lits,final_lits),
        "variable_occurrence_deltas":counter_delta(root_vars,final_vars),
        "second_DP_profile_from_v12_joint_fixpoint_FORENSICS_ONLY":profile,
        "second_DP_rows_that_would_descend_relative_to_R47N_root":root_descent,
        "interpretation":{
            "new_rule_proposed":False,
            "one_net_extra_literal_may_be_distributed_across_many_clause_replacements":True,
            "second_DP_profile_is_forensics_not_runtime_authority":True,
            "universal_generalization_allowed":False,
        },
        "firewall":{
            "NEW_REDUCTION_RULE_AUTHORIZED":False,
            "K_EQ_2_UNIVERSAL":"NOT_PROVED",
            "UNIVERSAL_K_EXISTS":"NOT_PROVED",
            "O4_UNIVERSAL_COVERAGE":"OPEN",
            "SAT_IN_P":"NOT_PROVED",
            "P_EQ_NP":"NOT_PROVED",
            "P_NE_NP":"NOT_PROVED",
            "P_VS_NP":"OPEN",
            "TRUMP_finished":False,
        },
    }
    return out


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--output"); args=parser.parse_args()
    d=run()
    if args.output:
        p=Path(args.output); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "gate":d["gate"],"verdict":d["verdict"],"v12_path":d["v12_path"],
        "DP12_local_debt":d["DP12_local_debt"],
        "clause_diff_counts":{k:d["root_to_final_clause_diff"][k] for k in ("unchanged_clause_count","removed_clause_count","added_clause_count","net_clause_delta","net_literal_delta","net_variable_delta")},
        "second_DP_root_descent_rows":d["second_DP_rows_that_would_descend_relative_to_R47N_root"],
        "firewall":d["firewall"]},sort_keys=True))


if __name__=="__main__":
    main()
