#!/usr/bin/env python3
"""NOVIKOV-002: fair actual-cost unit-propagation vs bounded failed-literal.

Same input, branch preference, exact SAT semantics and budget for both arms.
UNKNOWN is an honest answer if resource budget is exceeded; it is never
relabeled UNSAT. Large labels are not secretly held out. Historical MAJ3
independent C023 proof is cited but never fabricated as this search's proof.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import random
import statistics

from janus_novikov_002 import search, independently_model
from janus_tachyon_001_fair_holdout import fixed_suite, exact_truth, source_sha
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES

SEED=20261101
POLICIES=("unit","lookahead","selective")


def large_planted(n,seed):
    rng=random.Random(seed)
    planted=rng.getrandbits(n)
    formula=[]
    for _ in range(3*n):
        scope=rng.sample(range(1,n+1),3)
        literals=[v if rng.randrange(2) else -v for v in scope]
        if not any(((planted>>(abs(l)-1))&1)==int(l>0) for l in literals):
            i=rng.randrange(3)
            literals[i]=-literals[i]
        formula.append(tuple(literals))
    assert independently_model(formula,n,"SAT",planted)
    return tuple(formula)


def large_unsat_embedded(n,seed):
    # A complete 4-bit blocking core is a known UNSAT construction but
    # the algorithm cannot infer it merely from this generator's promise.
    rng=random.Random(seed)
    formula=list(large_planted(n,seed))
    for mask in range(16):
        formula.append(tuple(
            (-v if (mask>>(v-1))&1 else v)
            for v in range(1,5)))
    return tuple(formula)


def suite():
    ordinary=[(id,rows,n,kind,"frozen_small")
              for id,rows,n,kind,family in fixed_suite()]
    maj,n=maj3_lifted_tseitin_cnf(4,K4_EDGES)
    extended=[("MAJ3_K4",maj,n,"SAT","benchmark_unsat_C023_source"),
              ("PLANTED_3SAT_220",large_planted(220,220173),220,"SAT","large_planted"),
              ("PLANTED_3SAT_240",large_planted(240,240271),240,"SAT","large_planted"),
              ("UNSAT_CORE_220",large_unsat_embedded(220,220113),220,"SAT","large_unsat_embedded"),
              ("UNSAT_CORE_240",large_unsat_embedded(240,240197),240,"SAT","large_unsat_embedded")]
    return ordinary,extended


def compare(case,*,repeats:int,max_nodes:int,max_visits:int,seconds:float):
    id,rows,n,kind,group=case
    measurements={}
    for policy in POLICIES:
        results=[search(rows,n,kind,policy=policy,probe_width=2,
                        max_nodes=max_nodes,max_visits=max_visits,seconds=seconds)
                 for _ in range(repeats)]
        first=results[0]
        if len({r.status for r in results})!=1:
            # Timing budgets are nondeterministic; report mixed as is, never
            # silently select the best.
            verdict="MIXED_BUDGET_RESULTS"
        else:
            verdict=first.status
        if any(r.status=="SAT" and not r.model_independently_verified for r in results):
            raise AssertionError("uncertified SAT output")
        measurements[policy]={
            "status":verdict,
            "statuses":[r.status for r in results],
            "model_independently_verified":all(
                r.model_independently_verified for r in results if r.status=="SAT"),
            "exhaustive_unsat_verified_when_applicable":all(
                r.unsat_independent_exhaustive_check
                for r in results if r.status=="UNSAT" and n<=12),
            "median_elapsed_seconds":statistics.median(
                r.elapsed_seconds for r in results),
            "wall_seconds_each":[r.elapsed_seconds for r in results],
            "median_nodes":statistics.median(r.nodes for r in results),
            "median_clause_visits":statistics.median(r.clause_visits for r in results),
            "median_failed_literal_probes":statistics.median(
                r.failed_literal_probes for r in results),
            "median_rejected_probe_branches":statistics.median(
                r.rejected_probe_branches for r in results),
            "median_probe_clause_visits":statistics.median(
                r.probe_clause_visits for r in results),
            "probe_quota_exhausted_in_any_repeat":any(
                r.probe_quota_exhausted for r in results),
            "certificate_statuses":[r.certificate_status for r in results],
        }
    # Comparison can never treat UNKNOWN as an UNSAT proof or a speed win.
    a,b,c=(measurements[v] for v in POLICIES)
    both_conclusive=(a["status"] in ("SAT","UNSAT")
                     and a["status"]==b["status"])
    selective_conclusive=(a["status"] in ("SAT","UNSAT")
                          and a["status"]==c["status"])
    return {
        "name":id,"group":group,"n":n,"constraints":len(rows),"kind":kind,
        "source_sha256":sha256(json.dumps(
            {"n":n,"kind":kind,"rows":rows},sort_keys=True,separators=(",",":")
        ).encode()).hexdigest(),
        "same_input_budget_and_order":True,
        "comparability":("SAME_CONCLUSIVE_ANSWER" if both_conclusive
                         else "INCONCLUSIVE_OR_DIFFERENT_BUDGET_OUTCOME"),
        "lookahead_over_unit_elapsed_ratio":(
            b["median_elapsed_seconds"]/a["median_elapsed_seconds"]
            if both_conclusive and a["median_elapsed_seconds"]>0 else None),
        "selective_over_unit_elapsed_ratio":(
            c["median_elapsed_seconds"]/a["median_elapsed_seconds"]
            if selective_conclusive and a["median_elapsed_seconds"]>0 else None),
        "variants":measurements,
    }


def run():
    short,large=suite()
    records=[]
    for case in short:
        row=compare(case,repeats=3,max_nodes=10000,max_visits=500000,seconds=4.0)
        ground=bool(exact_truth(case[1],case[2],case[3]))
        if any(v["status"] != ("SAT" if ground else "UNSAT")
               for v in row["variants"].values()):
            raise AssertionError("bounded full reference disagrees on "+case[0])
        records.append(row)
    for case in large:
        records.append(compare(case,repeats=1,max_nodes=140,max_visits=140000,seconds=4.0))
    small_ratios=[x["lookahead_over_unit_elapsed_ratio"] for x in records
                  if x["group"]=="frozen_small"
                  and x["lookahead_over_unit_elapsed_ratio"] is not None]
    selective_ratios=[x["selective_over_unit_elapsed_ratio"] for x in records
                  if x["group"]=="frozen_small"
                  and x["selective_over_unit_elapsed_ratio"] is not None]
    large_outcomes={r["name"]:{
        "unit":r["variants"]["unit"]["status"],
        "lookahead":r["variants"]["lookahead"]["status"],
        "selective":r["variants"]["selective"]["status"],
        "unit_nodes":r["variants"]["unit"]["median_nodes"],
        "lookahead_nodes":r["variants"]["lookahead"]["median_nodes"],
        "selective_nodes":r["variants"]["selective"]["median_nodes"],
        "unit_visits":r["variants"]["unit"]["median_clause_visits"],
        "lookahead_visits":r["variants"]["lookahead"]["median_clause_visits"],
        "selective_visits":r["variants"]["selective"]["median_clause_visits"],
        "selective_probe_visits":r["variants"]["selective"]["median_probe_clause_visits"],
        "selective_probe_quota_exhausted":r["variants"]["selective"]["probe_quota_exhausted_in_any_repeat"]
    } for r in records if r["group"]!="frozen_small"}
    return {
        "schema":"JANUS-NOVIKOV-002-PARTIAL-CONSISTENCY-COMPARISON-V1",
        "source":{"sha":os.getenv("GITHUB_SHA","local"),
                  "run_id":os.getenv("GITHUB_RUN_ID","local")},
        "status":"BOUNDED_PARTIAL_SEARCH_FALSIFICATION_NOT_PRODUCTION",
        "baseline":"Identical unit propagation, hint and variable/value selection",
        "research_variant":"Same DPLL plus 2-variable failed-literal lookahead; actual propagation charged",
        "frozen_small":{"cases":len(short),"instance_suite_sha256":
                        source_sha(fixed_suite()),
                        "median_lookahead_over_unit_wall_ratio":
                        statistics.median(small_ratios),
                        "lookahead_faster_cases":sum(
                            x<1 for x in small_ratios),
                        "lookahead_slower_cases":sum(
                            x>1 for x in small_ratios),
                        "median_selective_over_unit_wall_ratio":
                            statistics.median(selective_ratios),
                        "selective_faster_cases":sum(x<1 for x in selective_ratios),
                        "selective_slower_cases":sum(x>1 for x in selective_ratios),
                        "same_verified_answers":True,
                        "repetitions":3},
        "larger_cases":large_outcomes,
        "budgets":{"small":{"max_nodes":10000,"max_clause_visits":500000,
                            "per_repetition_seconds":4},
                   "large":{"max_nodes":140,"max_clause_visits":140000,
                            "per_repetition_seconds":4,"selective_probe_max_share":0.05}},
        "cases":records,
        "claim_ceiling":[
            "Small answers independently checked against exhaustive UFR verify_model",
            "n18 MAJ3-K4 UNSAT previously established by independent C023 proof, not by partial consistency",
            "n220/240 planted SAT constructed; the hidden model is not passed to the search",
            "n220/240 UNSAT cores are generator-known but this search emits UNKNOWN unless full search completes",
            "Any n>12 UNSAT is solver conclusion only, no portable independent certificate",
            "UNKNOWN budget exhaustion is not UNSAT and must not count as an algorithm failure of soundness",
            "This is standard failed-literal propagation, not Novikov physics or novelty",
            "Selective probing spends at most 5% of the charged clause visits and then falls back to exact unit DPLL (apart from the final charge crossing the cap by one visit)",
            "Full wall, node and clause-visit expenses of probing are counted",
            "Existing stable production C023 and existing PR #574 gate remain unchanged",
        ],
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=Path("evidence/novikov-002.json"))
    args=p.parse_args()
    result=run()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result[k] for k in (
        "schema","status","frozen_small","larger_cases","budgets","claim_ceiling"
    )},indent=2,sort_keys=True))
