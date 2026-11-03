#!/usr/bin/env python3
"""Independent R5 receipt replayer. No model tuning, no censored wins.

Read two independent runner RESULT.json; independently regenerate every R5
original SHA, retrain ONLY R4 history, replay medians from all 360 child
records, check frozen scientific criterion. Same GitHub admin != external.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from math import isclose
from pathlib import Path
from statistics import median
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import janus_time_sat_004e12c5_r5_model as m
import janus_time_sat_004e12c5_r5_benchmark as b

def audit(reports):
    if len(reports)!=2:
        raise AssertionError("R5_NEED_TWO_FULL_HOST_REPORTS")
    frozen,psha=m.frozen()
    prior=m.fit_from_prior()
    fit_sha=sha256(m.canonical(prior)).hexdigest()
    cases={q["id"]:q for q in frozen["cohort"]}
    if set(cases)!=set(b.CASES):
        raise AssertionError("R5_FROZEN_COHORT_DRIFT")
    reference=None
    host_names=set()
    tested=[]
    for r in reports:
        if (r["schema"]!="JANUS-E12C5-R5-RAW-WORKER-V1"
            or r["prereg_sha256"]!=psha
            or r["pre_registered_protocol_git_blob_sha1"]!=m.FROZEN_BLOB
            or r["fitted_from_prior_sha256"]!=fit_sha
            or r["fit_prior_original_source_sha256"]!=prior["R4_source_original_sha256"]
            or len(r["raw_cold_records"])!=180
            or set(r["source_manifest"])!=set(cases)
            or set(r["summary"])!=set(cases)
            or not r["censored_not_numeric_win"]
            or not r["GF2_ablation_not_external_baseline"]
            or not r["training_cannot_see_R5_SAT_timings"]
            or not r["host_platform"]):
            raise AssertionError("R5_FALSE_OR_INCOMPLETE_HOST_RECEIPT")
        if r["host_platform"] in host_names:
            raise AssertionError("R5_DUPLICATE_HOST_PLATFORM")
        host_names.add(r["host_platform"])
        for case,src in r["source_manifest"].items():
            n,rows=m.source(case)
            h=m.r1.original_sha(rows,n)
            expected=(m.feature_profile(rows,n)[0]["exact_original_xor_cover"])
            if (src["sha256"]!=h
                or src["n"]!=n
                or src["clauses"]!=len(rows)
                or src["source_kind"]!=cases[case]["kind"]
                or src["original_literal_count"]!=sum(len(z) for z in rows)
                or src["original_full_exact_xor"]!=expected
                or src["past_training"]
                or h in set(prior["R4_source_original_sha256"].values())):
                raise AssertionError("R5_SOURCE_REPLAY_OR_TRAINING_LEAK")
        if reference is None:
            reference={"sources":r["source_manifest"],
                       "fit":r["fitted_from_prior_sha256"],
                       "script":r["script_sha256"],
                       "model":r["model_script_sha256"]}
        elif (reference["sources"]!=r["source_manifest"]
              or reference["fit"]!=r["fitted_from_prior_sha256"]
              or reference["script"]!=r["script_sha256"]
              or reference["model"]!=r["model_script_sha256"]):
            raise AssertionError("R5_SOURCE_OR_CODE_DIFFERENT_ACROSS_HOSTS")

        actual=set()
        for rec in r["raw_cold_records"]:
            case,arm,repeat=rec["case"],rec["arm"],rec["repeat"]
            key=(case,arm,repeat)
            if key in actual or case not in cases or arm not in b.ARMS or repeat not in (0,1,2):
                raise AssertionError("R5_DUPLICATE_OR_UNKNOWN_CHILD")
            actual.add(key)
            q=rec["child"]
            if not isinstance(rec["parent_full_cold_wall_s"],(int,float)) or rec["parent_full_cold_wall_s"]<=0:
                raise AssertionError("R5_INVALID_PARENT_COLD_WALL")
            status=q["solver_status"]
            if status==b.SAT:
                if (q["schema"]!="JANUS-E12C5-R5-COLD-V1"
                    or q["case"]!=case or q["arm"]!=arm
                    or q["source_sha256"]!=r["source_manifest"][case]["sha256"]
                    or q["prior_fit_sha256"]!=fit_sha
                    or q["protocol_sha256"]!=psha
                    or not q["witness_sha256"]
                    or q["replayed_original_clause_count"]!=r["source_manifest"][case]["clauses"]):
                    raise AssertionError("R5_FALSE_POSITIVE_SAT_WITNESS")
                if arm==b.ARMS[0]:
                    n,rows=m.source(case)
                    expected_engine,proof,reason,diagnostics=m.choose(rows,n,prior)
                    if q["selected_engine"]!=expected_engine or q["reason"]!=reason:
                        raise AssertionError("R5_SELECTOR_CHANGED_AFTER_SEEING_SAT")
                    if expected_engine=="janus_gf2":
                        if (not diagnostics["estimated_gain_lower_bound"]
                            or diagnostics["estimated_gain_lower_bound"]<1.25
                            or not proof
                            or r["source_manifest"][case]["source_kind"]!="EXACT_RANDOM_XOR"):
                            raise AssertionError("R5_UNSUPPORTED_GPU_OR_GF2_ROUTE")
                    if r["source_manifest"][case]["source_kind"]!="EXACT_RANDOM_XOR" and expected_engine=="janus_gf2":
                        raise AssertionError("R5_MIXED_CNFS_WRONGLY_TREATED_AS_EXACT")
            elif status==b.ABSTAIN:
                if arm not in ("janus_exact_gf2_ablation","cryptominisat_native_xor") or r["source_manifest"][case]["original_full_exact_xor"]:
                    raise AssertionError("R5_INVALID_ABSTENTION")
            elif status not in ("ERROR_CPU_OR_CHILD_FAILURE","UNKNOWN_WALL_CENSORED"):
                raise AssertionError("R5_UNREGISTERED_CHILD_STATUS")
        if len(actual)!=180:
            raise AssertionError("R5_INCOMPLETE_COLD_MATRIX")
        for case in b.CASES:
            summary=r["summary"][case]
            if set(summary["arms"])!=set(b.ARMS):
                raise AssertionError("R5_MISSING_ARMS")
            for arm in b.ARMS:
                arr=[x for x in r["raw_cold_records"] if x["case"]==case and x["arm"]==arm]
                valid=len(arr)==3 and all(x["child"]["solver_status"]==b.SAT for x in arr)
                measured=summary["arms"][arm]
                expected_median=median(x["parent_full_cold_wall_s"] for x in arr) if valid else None
                if (measured["SAT_replay_3of3"]!=valid
                    or measured["median_verified_full_cold_s"]!=expected_median
                    or measured["statuses"]!=[x["child"]["solver_status"] for x in arr]):
                    raise AssertionError("R5_FALSE_VERIFIED_TIMINGS_OR_CENSOR")
            best=[summary["arms"][arm]["median_verified_full_cold_s"] for arm in b.EXTERNAL
                  if summary["arms"][arm]["SAT_replay_3of3"]]
            sel=summary["arms"][b.ARMS[0]]
            computed=min(best)/sel["median_verified_full_cold_s"] if (
                 best and sel["SAT_replay_3of3"]) else None
            recorded=summary["gain_vs_fastest_completed_external"]
            if ((computed is None)!=(recorded is None) or
                (computed is not None and not isclose(computed,recorded,rel_tol=1e-10,abs_tol=1e-10))):
                raise AssertionError("R5_FASTEST_EXTERNAL_RATIO_NOT_RECONSTRUCTIBLE")
        tested.append(r)
    passing_widths=set()
    correct_all=True
    no_regret_exact=True
    no_regret_inexact=True
    all_applicable_verified=True
    cases_out={}
    for case in b.CASES:
        meta=cases[case]
        frames=[]
        for r in reports:
            item=r["summary"][case]
            sel=item["arms"][b.ARMS[0]]
            correct_all&=sel["SAT_replay_3of3"]
            ratio=item["gain_vs_fastest_completed_external"]
            if ratio is None or ratio<1/1.10:
                if meta["kind"]=="EXACT_RANDOM_XOR":no_regret_exact=False
                else:no_regret_inexact=False
            applicable=[]
            for arm in b.EXTERNAL:
                if (arm=="cryptominisat_native_xor" and
                    not r["source_manifest"][case]["original_full_exact_xor"]):
                    if item["arms"][arm]["statuses"]!=[b.ABSTAIN]*3:
                        raise AssertionError("R5_NATIVE_XOR_INAPPLICABILITY_NOT_RECORDED")
                    continue
                applicable.append(arm)
                if not item["arms"][arm]["SAT_replay_3of3"]:
                    all_applicable_verified=False
            frames.append({
                "host":r["host_platform"],"selected":item["selected_solver"],
                "fully_verified":sel["SAT_replay_3of3"],
                "gain_vs_fastest_verified_external":ratio,
                "all_applicable_external_verified":all(item["arms"][arm]["SAT_replay_3of3"] for arm in applicable),
                "censored_external_controls":[arm for arm in applicable if not item["arms"][arm]["SAT_replay_3of3"]]})
        qualifies=all(x["fully_verified"] and x["gain_vs_fastest_verified_external"] is not None
                      and x["gain_vs_fastest_verified_external"]>=1.2 for x in frames)
        if qualifies and meta["kind"]=="EXACT_RANDOM_XOR" and meta["width"] in (4,5):
            passing_widths.add(meta["width"])
        cases_out[case]={"case_kind":meta["kind"],"width":meta.get("width"),
                         "hosts":frames,"gain_over_1_2_on_both_hosts":qualifies}
    narrow=(correct_all and passing_widths=={4,5} and no_regret_exact and no_regret_inexact)
    return {
        "schema":"JANUS-E12C5-R5-FROZEN-TWO-HOST-SCIENCE-AUDIT-V1",
        "frozen_scientific_verdict":("R5_NARROW_CROSS_FAMILY_GAIN_CANDIDATE"
             if narrow else "R5_NO_PREREGISTERED_GENERALIZED_GAIN"),
        "frozen_prereg_sha256":psha,
        "frozen_prereg_blob_sha1":m.FROZEN_BLOB,
        "fit_regenerated_from_prior_sha256":fit_sha,
        "source_manifest":reference["sources"],
        "worker_host_platforms":sorted(host_names),
        "children_validated":360,
        "per_case":cases_out,
        "distinct_non_grid_XOR_widths_over_1_2_both_hosts":sorted(passing_widths),
        "all_selected_SAT_3of3_verified":correct_all,
        "no_regret_exact_XOR":no_regret_exact,
        "no_regret_incomplete_mixed_CNFS":no_regret_inexact,
        "strict_all_applicable_baselines_verified":all_applicable_verified,
        "incomplete_or_mixed_never_selected_own_GF2":all(x["hosts"][0]["selected"]!="janus_gf2" and
            x["hosts"][1]["selected"]!="janus_gf2" for x in cases_out.values() if x["case_kind"]!="EXACT_RANDOM_XOR"),
        "no_Future_R5_timing_used_during_fit":True,
        "same_GitHub_trust_domain":"YES",
        "independent_external_custodian":"NOT_CONNECTED",
        "sealed_external_CNF":"NOT_PERFORMED",
        "generic_SAT_speedup":"NOT_ESTABLISHED",
        "Stage5_universal":"CLOSED",
        "C023":"UNCHANGED","E12C4":"UNTOUCHED"
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--reports",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    z=a.parse_args()
    files=sorted(z.reports.rglob("RESULT.json"))
    if len(files)!=2:
        raise SystemExit("R5_TWO_HOST_ARTIFACT_JSONS_REQUIRED "+str(len(files)))
    result=audit([json.loads(p.read_text()) for p in files])
    z.out.mkdir(parents=True,exist_ok=True)
    (z.out/"AUDIT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("R5_FROZEN_SCIENCE_AUDIT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    main()
