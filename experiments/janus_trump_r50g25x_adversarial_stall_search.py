from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import janus_trump_r33_certified_safe_reduction_stack_lean_core_forensics as r33
import janus_trump_r42_subsumption_aware_bve_successor as r42
import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r50g25r_outer_counterexample_search as r50g25r
import janus_trump_r50g25s_max_rup_minimization_structured_escalation as r50g25s
import janus_trump_r50g25w_sa_bve_policy_lift_outer_replay as r50g25w
import janus_trump_r50g25g_micro_rup_restart_replay_source_lift_family as r50g25g

GATE = "JANUS_TRUMP_R50G25X_UNIVERSAL_COMPLETENESS_OBLIGATION_AND_ADVERSARIAL_STALL_SEARCH"
W_RUN = 34044471849
W_JOURNAL_COMMIT = "83d4a1f306a059ad40a6b6543f2277bb36292b64"
X_PREREG_COMMIT = "558a528863e33ff5bf3cef28af03257158fe753f"
EXPECTED_R47_HASH = "c379fb11374c4259a736545f6652a417b6d98d016e9dcaed62d44d3740b71adb"


def canonical_hash(formula):
    return r42.formula_hash(r33.canonical_formula(formula))


def route_score(result):
    # Truth-blind adversarial score. Residual is always ranked hardest.
    residual = int(result.get("semantic_sat") is None)
    rounds = int(result.get("round_count", 0))
    rup = int(result.get("ledger", {}).get("RUP_successful_strengthenings", 0))
    sa = int(result.get("ledger", {}).get("SA_BVE_applications", 0))
    checks = int(result.get("ledger", {}).get("R33_check_operation_upper_ledger", 0))
    return (residual, rounds, rup + sa, checks)


def replay_to_policy_fixpoint(initial, r50g23, r35b, r33m, r47jm):
    r34 = r50g23.r34
    r42m = r50g23.r42
    state = r33m.canonical_formula(initial)
    height_bound = r47jm.restart_height_bound(state)
    route = []
    for round_index in range(height_bound + 1):
        before = state
        reduced = r33m.simplify(before)
        after_r33 = r33m.canonical_formula(reduced["final_formula"])
        row = {
            "round": round_index,
            "before_CLV": list(r33m.measure(before)),
            "after_R33_CLV": list(r33m.measure(after_r33)),
            "R33_terminal": str(reduced["terminal"]),
        }
        if reduced["terminal"] != "STALLED_STACK_LEAN_CORE":
            row["stop"] = "DECLARED_TERMINAL"
            route.append(row)
            return {"kind":"TERMINAL","state":after_r33,"route":route}
        affine = r34.recognize_complete_affine_cnf(after_r33)
        if affine["recognized"]:
            row["stop"] = "AFFINE"
            route.append(row)
            return {"kind":"AFFINE","state":after_r33,"route":route}
        proposal, rup_ledger = r35b.first_rup_strengthening(after_r33)
        row["RUP_scan_ledger"] = rup_ledger
        if proposal is not None:
            if not r35b.independent_up_conflict_checker(after_r33, proposal["assumptions"]):
                raise AssertionError(("X_RUP_REPLAY_FAIL", round_index, proposal))
            state = r35b.replace_clause_with_subclause(after_r33, tuple(proposal["source_clause"]), tuple(proposal["strengthened_clause"]))
            row["door"] = "RUP"
            row["after_door_CLV"] = list(r33m.measure(state))
            route.append(row)
            continue
        candidate, bve_ledger = r42m.best_sa_bve_candidate(after_r33)
        row["SA_BVE_scan_ledger"] = bve_ledger
        if candidate is not None:
            replay = r42m.independent_sa_bve_replay(after_r33, candidate)
            if not replay["pass"]:
                raise AssertionError(("X_SA_BVE_REPLAY_FAIL", round_index, replay))
            state = r33m.canonical_formula(candidate["transformed"])
            row["door"] = "SA_BVE"
            row["SA_BVE_var"] = int(candidate["var"])
            row["SA_BVE_replay_pass"] = True
            row["after_door_CLV"] = list(r33m.measure(state))
            route.append(row)
            continue
        row["stop"] = "NO_RUP_NO_SA_BVE"
        route.append(row)
        return {"kind":"RESIDUAL","state":after_r33,"route":route,"RUP_scan_ledger":rup_ledger,"SA_BVE_scan_ledger":bve_ledger}
    raise AssertionError(("X_HEIGHT_BOUND_EXHAUSTED", height_bound))


def historical_candidates():
    out = []
    for spec in r42.HOLDOUTS:
        f = r33.deterministic_random_3cnf(spec["seed"], n=spec["n"], ratio=spec["ratio"])
        out.append({"family":"HISTORICAL_R42_HOLDOUT","formula":f,"meta":dict(spec)})
    sealed, f47 = r47j.load_counterexample()
    if canonical_hash(f47) != EXPECTED_R47_HASH:
        raise AssertionError(("X_R47_HASH_DRIFT", canonical_hash(f47)))
    out.append({"family":"HISTORICAL_R47_COUNTEREXAMPLE","formula":f47,"meta":{"expected_hash":EXPECTED_R47_HASH,"CLV":list(r33.measure(f47))}})
    return out


def new_candidates():
    out = []
    # New deterministic random threshold ladder, one seed per density/size.
    for n in (36, 40, 48, 56, 64):
        for density in (4.20, 4.26, 4.30):
            m = int(round(density * n))
            seed = 50000000 + 100000 * n + int(round(density * 100))
            out.append({"family":"NEW_RANDOM_THRESHOLD","formula":r50g25r.random_3cnf(r33,n,m,seed),"meta":{"n":n,"m":m,"density":density,"seed":seed}})

    # R33-stall targeted states, one per chosen size. Selection never inspects truth.
    for n in (36, 48, 64):
        m = int(round(4.26 * n))
        selected = None
        scanned = 0
        for i in range(1500):
            seed = 53000000 + 100000 * n + i
            f = r50g25r.random_3cnf(r33,n,m,seed)
            scanned += 1
            try:
                b = r33.simplify(f)
                stalled = str(b.get("terminal")) == "STALLED_STACK_LEAN_CORE"
            except AssertionError:
                stalled = True
            if stalled:
                selected = (f, seed)
                break
        if selected is not None:
            f, seed = selected
            out.append({"family":"NEW_R33_STALL_TARGET","formula":f,"meta":{"n":n,"m":m,"seed":seed,"scanned":scanned}})

    # Structured controls. XOR sizes are direct variables; prism uses 3k edge variables.
    for n in (36, 48, 60):
        for pattern in ("ZERO","ALT"):
            out.append({"family":"NEW_XOR_CYCLE","formula":r50g25r.xor_cycle_formula(r33,n,pattern),"meta":{"n":n,"pattern":pattern}})
    for k in (12, 16, 20):
        for pattern in ("ZERO","SINGLE"):
            f, meta = r50g25s.tseitin_prism_formula(r33,k,pattern)
            out.append({"family":"NEW_TSEITIN_PRISM","formula":f,"meta":meta})
    return out


def mutate_clause_truth_blind(formula, n, seed):
    # Replace one clause deterministically with a new syntactic 3-clause. No truth query.
    f = list(r33.canonical_formula(formula))
    if not f:
        return tuple(f)
    import random
    rng = random.Random(int(seed))
    idx = rng.randrange(len(f))
    for _ in range(100):
        vs = sorted(rng.sample(range(1, n+1), 3))
        c = tuple(r33.canonical_clause([v if rng.getrandbits(1) else -v for v in vs]))
        if c not in f:
            f[idx] = c
            return r33.canonical_formula(f)
    return r33.canonical_formula(f)


def behavior_guided_mutations(base_rows, r50g23, r35b, r33m, r47jm):
    # Choose three hardest NEW_RANDOM_THRESHOLD parents by W route score, then make
    # six one-clause mutations each. Selection is solver-behavior-only.
    parents = sorted(
        [r for r in base_rows if r["item"]["family"] == "NEW_RANDOM_THRESHOLD"],
        key=lambda r: (r["score"], r["hash"]), reverse=True
    )[:3]
    out = []
    for pi, parent in enumerate(parents):
        formula = parent["item"]["formula"]
        n = int(parent["item"]["meta"]["n"])
        for j in range(6):
            seed = 57000000 + 1000*pi + j
            mutated = mutate_clause_truth_blind(formula,n,seed)
            out.append({"family":"BEHAVIOR_GUIDED_MUTATION","formula":mutated,"meta":{"parent_hash":parent["hash"],"n":n,"seed":seed,"parent_score":list(parent["score"])}})
    return out


def audit_item(item, r50g23, r35b, r33m, r47jm):
    f = r33m.canonical_formula(item["formula"])
    h = canonical_hash(f)
    try:
        result = r50g25w.micro_with_sa_bve(f,r50g23,r35b,r33m,r47jm)
        error = None
    except AssertionError as exc:
        result = None
        error = repr(exc)
    if result is None:
        return {"item":item,"hash":h,"CLV":list(r33m.measure(f)),"error":error,"score":(1,10**9,10**9,10**9),"residual":False,"terminal":None,"semantic_sat":None,"reconstruction_pass":False,"SA_BVE":None,"RUP":None,"rounds":None}
    residual = result.get("semantic_sat") is None
    return {
        "item":item,"hash":h,"CLV":list(r33m.measure(f)),"error":None,
        "score":route_score(result),"residual":residual,"terminal":result.get("terminal"),
        "semantic_sat":result.get("semantic_sat"),
        "reconstruction_pass":bool(result.get("SAT_reconstruction",{}).get("pass",True)),
        "SA_BVE":int(result.get("ledger",{}).get("SA_BVE_applications",0)),
        "RUP":int(result.get("ledger",{}).get("RUP_successful_strengthenings",0)),
        "rounds":int(result.get("round_count",0)),
        "R33_checks":int(result.get("ledger",{}).get("R33_check_operation_upper_ledger",0)),
    }


def run():
    _b, r50g23, r35b, r33m, r47jm = r50g25g._chain()
    initial = historical_candidates() + new_candidates()
    seen = {}
    for item in initial:
        f = r33m.canonical_formula(item["formula"])
        seen.setdefault(tuple(f), {**item,"formula":f})
    initial = list(seen.values())
    initial_rows = [audit_item(x,r50g23,r35b,r33m,r47jm) for x in initial]
    mutations = behavior_guided_mutations(initial_rows,r50g23,r35b,r33m,r47jm)
    all_items = initial[:]
    for x in mutations:
        f = r33m.canonical_formula(x["formula"])
        if tuple(f) not in seen:
            seen[tuple(f)] = {**x,"formula":f}
            all_items.append(seen[tuple(f)])
    # Reuse initial audits and only audit genuinely new mutation items.
    row_by_hash = {r["hash"]:r for r in initial_rows}
    rows = initial_rows[:]
    for item in all_items[len(initial):]:
        rows.append(audit_item(item,r50g23,r35b,r33m,r47jm))

    residuals = []
    assertions = []
    reconstruction_failures = []
    terminal_hist = Counter()
    family_hist = Counter()
    max_route = None
    for r in rows:
        family_hist[r["item"]["family"]] += 1
        if r["error"] is not None:
            assertions.append({k:v for k,v in r.items() if k != "item"} | {"family":r["item"]["family"],"meta":r["item"]["meta"]})
            continue
        terminal_hist[str(r["terminal"] if r["terminal"] is not None else "RESIDUAL_FIXPOINT")] += 1
        if not r["reconstruction_pass"]:
            reconstruction_failures.append(r["hash"])
        if r["residual"]:
            core = replay_to_policy_fixpoint(r["item"]["formula"],r50g23,r35b,r33m,r47jm)
            if core["kind"] != "RESIDUAL":
                raise AssertionError(("X_RESIDUAL_REPLAY_DISAGREEMENT",r["hash"],core["kind"]))
            residuals.append({
                "source_hash":r["hash"],"source_CLV":r["CLV"],"family":r["item"]["family"],"meta":r["item"]["meta"],
                "source_rounds":r["rounds"],"source_RUP":r["RUP"],"source_SA_BVE":r["SA_BVE"],
                "residual_hash":canonical_hash(core["state"]),"residual_CLV":list(r33m.measure(core["state"])),
                "residual_formula":[list(c) for c in core["state"]],
                "RUP_scan_ledger":core.get("RUP_scan_ledger"),"SA_BVE_scan_ledger":core.get("SA_BVE_scan_ledger"),
                "route_tail":core["route"][-8:],
            })
        if max_route is None or (r["score"],r["hash"]) > (max_route["score"],max_route["hash"]):
            max_route = r

    counterexample = bool(residuals or assertions or reconstruction_failures)
    verdict = "W_POLICY_COUNTEREXAMPLE_FOUND" if counterexample else "NO_W_POLICY_COUNTEREXAMPLE_IN_PREREGISTERED_X_DOMAIN"
    next_gate = "R50G25Y_MINIMAL_W_POLICY_COUNTEREXAMPLE_FORENSICS" if counterexample else "R50G25Y_LOCAL_DOOR_COMPLETENESS_LEMMA_OR_SYMBOLIC_COUNTEREXAMPLE"

    return {
        "gate":GATE,"parent_W_run":W_RUN,"parent_W_journal_commit":W_JOURNAL_COMMIT,"X_preregistration_commit":X_PREREG_COMMIT,
        "universal_obligation_status":"OPEN_CONJECTURE_NOT_PROVED",
        "generation_contract":{"truth_used_for_generation_or_selection":False,"exact_truth_authority":False,"behavior_guided_mutation_is_adversarial_search_only":True,"initial_candidate_count":len(initial),"mutation_candidate_count":len(all_items)-len(initial),"total_unique_count":len(rows)},
        "family_partition":dict(sorted(family_hist.items())),"terminal_partition":dict(sorted(terminal_hist.items())),
        "assertion_failure_count":len(assertions),"reconstruction_failure_count":len(reconstruction_failures),"residual_fixpoint_count":len(residuals),
        "assertion_examples":assertions[:10],"residuals":residuals,
        "max_route_case":None if max_route is None else {"hash":max_route["hash"],"family":max_route["item"]["family"],"meta":max_route["item"]["meta"],"CLV":max_route["CLV"],"score":list(max_route["score"]),"rounds":max_route["rounds"],"RUP":max_route["RUP"],"SA_BVE":max_route["SA_BVE"],"R33_checks":max_route.get("R33_checks"),"terminal":max_route["terminal"]},
        "verdict":verdict,"next_gate":next_gate,
        "interpretation_contract":{"finite_pass_is_not_universal_completeness_proof":True,"counterexample_if_found_refutes_current_W_policy_not_P_equals_NP":True,"historical_holdouts_used_unchanged":True},
        "firewall":{"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); args=ap.parse_args()
    out=run(); p=Path(args.out); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=='__main__': main()
