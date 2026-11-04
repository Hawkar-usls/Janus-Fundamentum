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
import janus_time_sat_004e12c5_r6_model as m
import janus_time_sat_004e12c5_r6_benchmark as b

def audit(reports):
    if len(reports)!=2:
        raise AssertionError("R6_NEED_TWO_FULL_HOST_REPORTS")
    frozen,psha=m.frozen_protocol()
    prior=m.fit_from_past()
    fit_sha=sha256(m.canonical(prior)).hexdigest()
    cases={q["id"]:q for q in frozen["new_sources"]}
    if set(cases)!=set(b.CASES):
        raise AssertionError("R6_FROZEN_COHORT_DRIFT")
    reference=None
    host_names=set()
    tested=[]
    for r in reports:
        if (r["schema"]!="JANUS-E12C5-R6-RAW-WORKER-V1"
            or r["prereg_sha256"]!=psha
            or r["pre_registered_protocol_git_blob_sha1"]!=m.PROTOCOL_BLOB_SHA
            or r["fitted_from_prior_sha256"]!=fit_sha
            or r["fit_prior_original_source_sha256"]!=prior["training_original_SHA256"]
            or len(r["raw_cold_records"])!=180
            or set(r["source_manifest"])!=set(cases)
            or set(r["summary"])!=set(cases)
            or not r["censored_not_numeric_win"]
            or not r["GF2_ablation_not_external_baseline"]
            or not r["training_cannot_see_R6_SAT_timings"]
            or not r["host_platform"]):
            raise AssertionError("R6_FALSE_OR_INCOMPLETE_HOST_RECEIPT")
        if r["host_platform"] in host_names:
            raise AssertionError("R6_DUPLICATE_HOST_PLATFORM")
        host_names.add(r["host_platform"])
        for case,src in r["source_manifest"].items():
            n,rows=m.source(case)
            h=m.r1.original_sha(rows,n)
            expected=(m.signmask_profile(rows,n)[0]["whole_original_exact_xor"])
            if (src["sha256"]!=h
                or src["n"]!=n
                or src["clauses"]!=len(rows)
                or src["source_kind"]!=cases[case]["kind"]
                or src["original_literal_count"]!=sum(len(z) for z in rows)
                or src["original_full_exact_xor"]!=expected
                or src["past_training"]
                or h in set(prior["training_original_SHA256"])):
                raise AssertionError("R6_SOURCE_REPLAY_OR_TRAINING_LEAK")
        if reference is None:
            reference={"sources":r["source_manifest"],
                       "fit":r["fitted_from_prior_sha256"],
                       "script":r["script_sha256"],
                       "model":r["model_script_sha256"]}
        elif (reference["sources"]!=r["source_manifest"]
              or reference["fit"]!=r["fitted_from_prior_sha256"]
              or reference["script"]!=r["script_sha256"]
              or reference["model"]!=r["model_script_sha256"]):
            raise AssertionError("R6_SOURCE_OR_CODE_DIFFERENT_ACROSS_HOSTS")

        actual=set()
        for rec in r["raw_cold_records"]:
            case,arm,repeat=rec["case"],rec["arm"],rec["repeat"]
            key=(case,arm,repeat)
            if key in actual or case not in cases or arm not in b.ARMS or repeat not in (0,1,2):
                raise AssertionError("R6_DUPLICATE_OR_UNKNOWN_CHILD")
            actual.add(key)
            q=rec["child"]
            if not isinstance(rec["parent_full_cold_wall_s"],(int,float)) or rec["parent_full_cold_wall_s"]<=0:
                raise AssertionError("R6_INVALID_PARENT_COLD_WALL")
            status=q["solver_status"]
            if status==b.SAT:
                if (q["schema"]!="JANUS-E12C5-R6-COLD-V1"
                    or q["case"]!=case or q["arm"]!=arm
                    or q["source_sha256"]!=r["source_manifest"][case]["sha256"]
                    or q["prior_fit_sha256"]!=fit_sha
                    or q["protocol_sha256"]!=psha
                    or not q["witness_sha256"]
                    or q["replayed_original_clause_count"]!=r["source_manifest"][case]["clauses"]):
                    raise AssertionError("R6_FALSE_POSITIVE_SAT_WITNESS")
                if arm==b.ARMS[0]:
                    n,rows=m.source(case)
                    expected_engine,proof,reason,diagnostics=m.choose(rows,n,prior)
                    if q["selected_engine"]!=expected_engine or q["reason"]!=reason:
                        raise AssertionError("R6_SELECTOR_CHANGED_AFTER_SEEING_SAT")
                    if expected_engine=="janus_gf2":
                        width=r["source_manifest"][case]["preregistered_width"]
                        minimum=1.15 if width==3 else 1.25
                        if (diagnostics.get("confidence_lower_bound_gain",0)<minimum
                            or not proof or
                            r["source_manifest"][case]["source_kind"]!="EXACT_RANDOM_XOR"):
                            raise AssertionError("R6_UNSUPPORTED_OR_UNCERTIFIED_GF2_ROUTE")
                    if r["source_manifest"][case]["source_kind"]!="EXACT_RANDOM_XOR" and expected_engine=="janus_gf2":
                        raise AssertionError("R6_MIXED_CNFS_WRONGLY_TREATED_AS_EXACT")
            elif status==b.ABSTAIN:
                if arm not in ("janus_exact_gf2_ablation","cryptominisat_native_xor") or r["source_manifest"][case]["original_full_exact_xor"]:
                    raise AssertionError("R6_INVALID_ABSTENTION")
            elif status not in ("ERROR_CPU_OR_CHILD_FAILURE","UNKNOWN_WALL_CENSORED"):
                raise AssertionError("R6_UNREGISTERED_CHILD_STATUS")
        if len(actual)!=180:
            raise AssertionError("R6_INCOMPLETE_COLD_MATRIX")
        for case in b.CASES:
            summary=r["summary"][case]
            if set(summary["arms"])!=set(b.ARMS):
                raise AssertionError("R6_MISSING_ARMS")
            for arm in b.ARMS:
                arr=[x for x in r["raw_cold_records"] if x["case"]==case and x["arm"]==arm]
                valid=len(arr)==3 and all(x["child"]["solver_status"]==b.SAT for x in arr)
                measured=summary["arms"][arm]
                expected_median=median(x["parent_full_cold_wall_s"] for x in arr) if valid else None
                if (measured["SAT_replay_3of3"]!=valid
                    or measured["median_verified_full_cold_s"]!=expected_median
                    or measured["statuses"]!=[x["child"]["solver_status"] for x in arr]):
                    raise AssertionError("R6_FALSE_VERIFIED_TIMINGS_OR_CENSOR")
            best=[summary["arms"][arm]["median_verified_full_cold_s"] for arm in b.EXTERNAL
                  if summary["arms"][arm]["SAT_replay_3of3"]]
            sel=summary["arms"][b.ARMS[0]]
            computed=min(best)/sel["median_verified_full_cold_s"] if (
                 best and sel["SAT_replay_3of3"]) else None
            recorded=summary["gain_vs_fastest_completed_external"]
            if ((computed is None)!=(recorded is None) or
                (computed is not None and not isclose(computed,recorded,rel_tol=1e-10,abs_tol=1e-10))):
                raise AssertionError("R6_FASTEST_EXTERNAL_RATIO_NOT_RECONSTRUCTIBLE")
        tested.append(r)
    all_selected_correct=True
    all_regret_within_10pct=True
    all_external_verified=True
    width3_successes=set()
    width4_success=False
    width5_success=False
    mixed4_no_regret=True
    cases_out={}
    for case in b.CASES:
        meta=cases[case]
        frames=[]
        for host in reports:
            entry=host["summary"][case]
            selected=entry["arms"][b.ARMS[0]]
            complete=selected["SAT_replay_3of3"]
            all_selected_correct &= complete
            ratio=entry["gain_vs_fastest_completed_external"]
            if ratio is None or ratio<1/1.10:
                all_regret_within_10pct=False
            if meta["kind"]=="MIXED_XOR_PLUS_CNF" and meta["width"]==4:
                mixed4_no_regret &= ratio is not None and ratio>=1/1.05
            applicable=[]
            for arm in b.EXTERNAL:
                if arm=="cryptominisat_native_xor" and not host["source_manifest"][case]["original_full_exact_xor"]:
                    if entry["arms"][arm]["statuses"]!=[b.ABSTAIN]*3:
                        raise AssertionError("R6_INAPPLICABLE_NATIVE_XOR_NOT_ABSTAINED")
                    continue
                applicable.append(arm)
                if not entry["arms"][arm]["SAT_replay_3of3"]:
                    all_external_verified=False
            frames.append({
                "host":host["host_platform"],
                "selected_engine":entry["selected_solver"],
                "all_three_SAT_verified":complete,
                "gain_vs_fastest_verified_external":ratio,
                "censored_applicable_competitors":[arm for arm in applicable
                    if not entry["arms"][arm]["SAT_replay_3of3"]]})
        minimum_gain=(1.10 if meta["kind"]=="EXACT_RANDOM_XOR" and meta["width"]==3
                      else 1.20)
        gain_pass=all(x["all_three_SAT_verified"] and
            x["gain_vs_fastest_verified_external"] is not None and
            x["gain_vs_fastest_verified_external"]>=minimum_gain for x in frames)
        if meta["kind"]=="EXACT_RANDOM_XOR" and gain_pass:
            if meta["width"]==3:width3_successes.add(case)
            if meta["width"]==4:width4_success=True
            if meta["width"]==5:width5_success=True
        if meta["kind"]!="EXACT_RANDOM_XOR" and any(
            f["selected_engine"] in ("janus_gf2","cryptominisat_native_xor") for f in frames):
            raise AssertionError("R6_UNSAFE_MIXED_GF2_OR_NATIVE_SELECTION")
        cases_out[case]={
            "source_kind":meta["kind"],
            "original_width":meta.get("width"),
            "hosts":frames,
            "all_hosts_meet_frozen_gain_requirement":gain_pass if meta["kind"]=="EXACT_RANDOM_XOR" else None}
    science=(all_selected_correct and all_regret_within_10pct and mixed4_no_regret
             and len(width3_successes)==2 and width4_success and width5_success)
    return {
        "schema":"JANUS-E12C5-R6-FROZEN-TWO-HOST-AUDIT-V1",
        "scientific_verdict":("R6_NARROW_MULTIFAMILY_CROSS_SIZE_GAIN_CANDIDATE" if science
                  else "R6_FROZEN_SCIENCE_GATE_NOT_PASSED"),
        "pre_registered_protocol_blob_sha1":m.PROTOCOL_BLOB_SHA,
        "pre_registered_protocol_sha256":psha,
        "fit_rebuilt_from_only_R5_sha256":fit_sha,
        "source_manifest":reference["sources"],
        "host_platforms":sorted(host_names),
        "total_cold_receipts":360,
        "per_case":cases_out,
        "width3_both_new_sources_over_1_10":sorted(width3_successes),
        "width4_meets_1_20":width4_success,
        "width5_meets_1_20":width5_success,
        "all_selector_SAT_3of3":all_selected_correct,
        "all_sources_at_most_10pct_regret":all_regret_within_10pct,
        "both_mixed_width4_at_most_5pct_regret":mixed4_no_regret,
        "all_applicable_external_controls_3of3":all_external_verified,
        "all_test_SAT_outcomes_replayed_original_CNF":all_selected_correct,
        "no_R6_self_training":True,
        "right_censored_controls_not_numeric":True,
        "GF2_internal_ablation_not_external_baseline":True,
        "independent_administrator":"NOT_CONNECTED",
        "external_blind_test":"NOT_PERFORMED",
        "Stage5_general_SAT":"CLOSED",
        "E12C4_epoch2":"NOT_MODIFIED",
        "C023_production":"UNCHANGED"
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--reports",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    z=a.parse_args()
    files=sorted(z.reports.rglob("RESULT.json"))
    if len(files)!=2:
        raise SystemExit("R6_TWO_HOST_ARTIFACT_JSONS_REQUIRED "+str(len(files)))
    result=audit([json.loads(p.read_text()) for p in files])
    z.out.mkdir(parents=True,exist_ok=True)
    (z.out/"AUDIT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("R6_FROZEN_SCIENCE_AUDIT",json.dumps(result,sort_keys=True),flush=True)
if __name__=="__main__":
    main()
