#!/usr/bin/env python3
"""E12C5 R2 immutable-source cross-host benchmark adjudicator.

Does NOT retune any threshold and does NOT interpret timeouts as speedups.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from hashlib import sha1,sha256
from statistics import median
from math import isclose

ROOT=Path(__file__).resolve().parents[2]
PREREG=ROOT/"experiments/time_sat_004_external/E12C5_R2_PREREG.json"
PREREG_GIT_SHA="6d31e3e716a9c09a26a83c7dceb06871e627f314"
CASES=("new_r2_grid_21","new_r2_grid_23","new_r2_grid_29","new_r2_grid_39")
ARMS=("janus_pre_solve_selector","janus_gf2","cryptominisat_native_xor",
      "cryptominisat_original_cnf","cadical195_original_cnf")
SAT="SAT_VERIFIED_ORIGINAL_CNF"

def audit(reports):
    if len(reports)!=2:
        raise AssertionError("TWO_HOSTS_REQUIRED")
    pbytes=PREREG.read_bytes()
    if sha1(b"blob "+str(len(pbytes)).encode()+bytes([0])+pbytes).hexdigest()!=PREREG_GIT_SHA:
        raise AssertionError("FROZEN_PROTOCOL_DRIFT")
    protocol=json.loads(pbytes)
    pinnedsha=sha256(pbytes).hexdigest()
    hostnames=[]
    for d in reports:
        if (d["schema"]!="JANUS-E12C5-R2-RAW-RESULT-V1"
            or d["prereg_sha256"]!=pinnedsha
            or d["protocol_git_blob_sha1"]!=PREREG_GIT_SHA
            or len(d["records"])!=60
            or set(d["source_manifest"])!=set(CASES)
            or set(d["summary"])!=set(CASES)
            or not d["censored_not_numeric_win"]
            or not d["R2_source_labels_not_used_in_training"]):
            raise AssertionError("MISSING_OR_INVALID_HOST_RECEIPT")
        hosts=d["platform"]
        hostnames.append(hosts)
        for item in protocol["new_unseen_cases"]:
            s=d["source_manifest"][item["id"]]
            if (s["n"]!=item["n"] or s["seed"]!=item["seed"]
                or s["size"]!=item["size"] or s["train_source"]
                or len(s["source_sha256"])!=64):
                raise AssertionError("SOURCE_PROVENANCE_DRIFT")
        unique_records=set()
        for r in d["records"]:
            key=(r["case"],r["arm"],r["repeat"])
            if (key in unique_records or r["case"] not in CASES or r["arm"] not in ARMS
                or r["repeat"] not in (0,1,2)):
                raise AssertionError("COLD_MATRIX_DUPLICATE_OR_DRIFT")
            unique_records.add(key)
            val=r["outcome"]
            if val["status"]==SAT:
                if (val["case"]!=r["case"] or val["arm"]!=r["arm"]
                    or not val["original_cnf_checked"]
                    or val["source_sha256"]!=d["source_manifest"][r["case"]]["source_sha256"]
                    or val["prereg_sha256"]!=pinnedsha):
                    raise AssertionError("UNVERIFIED_POSITIVE_RESULT")
                if r["arm"]=="janus_pre_solve_selector":
                    expected="cadical195_original_cnf" if r["case"]=="new_r2_grid_21" else "janus_gf2"
                    if val["engine_selected"]!=expected:
                        raise AssertionError("FORBIDDEN_TEST_TIME_SELECTION_DRIFT")
            elif val["status"] not in ("UNKNOWN_WALL_CENSORED","ERROR_OR_CPU_CENSORED"):
                raise AssertionError("UNREGISTERED_NEGATIVE_OUTCOME")
            if not isinstance(r["full_cold_child_wall_s"],(float,int)) or r["full_cold_child_wall_s"]<=0:
                raise AssertionError("INVALID_FULL_COLD_MEASUREMENT")
        if len(unique_records)!=len(CASES)*len(ARMS)*3:
            raise AssertionError("INCOMPLETE_COLD_MATRIX")
        for case in CASES:
            arms=d["summary"][case]["arms"]
            if set(arms)!=set(ARMS):
                raise AssertionError("MISSING_CONTROL")
            for arm in ARMS:
                item=arms[arm]
                actual=[r for r in d["records"] if r["case"]==case and r["arm"]==arm]
                verified=all(r["outcome"]["status"]==SAT for r in actual)
                if verified != item["verified_3_of_3"]:
                    raise AssertionError("FALSE_FULL_VERIFIED_CLAIM")
                if not verified and item["median_full_cold_s"] is not None:
                    raise AssertionError("CENSORED_NUMERIC_GAIN_FORBIDDEN")
                if verified:
                    true_median=median(r["full_cold_child_wall_s"] for r in actual)
                    if (item["median_full_cold_s"] is None or
                        not isclose(item["median_full_cold_s"],true_median,rel_tol=1e-10,abs_tol=1e-10)):
                        raise AssertionError("REPORTED_MEDIAN_NOT_REPRODUCIBLE_FROM_RAW")
            selected=arms["janus_pre_solve_selector"]
            valid_controls=[arms[arm]["median_full_cold_s"] for arm in ARMS[1:]
                if arms[arm]["verified_3_of_3"]]
            correct_ratio=(min(valid_controls)/selected["median_full_cold_s"]
                           if selected["verified_3_of_3"] and valid_controls else None)
            recorded=d["summary"][case]["ratio_fastest_verified_baseline"]
            if ((correct_ratio is None)!=(recorded is None) or
                (correct_ratio is not None and
                 not isclose(correct_ratio,recorded,rel_tol=1e-10,abs_tol=1e-10))):
                raise AssertionError("SOURCE_GAIN_NOT_REPRODUCIBLE_FROM_RAW")
    if (reports[0]["source_manifest"]!=reports[1]["source_manifest"]
       or reports[0]["r2_script_sha256"]!=reports[1]["r2_script_sha256"]):
        raise AssertionError("CROSS_HOST_SOURCE_OR_CODE_NOT_IDENTICAL")

    details={}
    winning=[]
    all_no_regret=True
    all_complete=True
    censored_cases=[]
    for case in CASES:
        host_rows=[]
        for d in reports:
            a=d["summary"][case]
            selected=a["arms"]["janus_pre_solve_selector"]
            comparison=a["ratio_fastest_verified_baseline"]
            # A trusted answer must not ever assign finite time to a censored arm.
            if comparison is not None and (
                not selected["verified_3_of_3"] or
                not any(a["arms"][arm]["verified_3_of_3"] for arm in ARMS[1:])):
                raise AssertionError("FALSE_NUMERIC_SPEEDUP")
            if comparison is None or comparison < 1/1.05:
                all_no_regret=False
            all_fully_verified=all(a["arms"][arm]["verified_3_of_3"] for arm in ARMS)
            all_complete=all_complete and all_fully_verified
            if not all_fully_verified:
                censored_cases.append({"source":case,"host":d["platform"],
                  "arms":a["censored_arms"]})
            host_rows.append({
                "host":d["platform"],
                "full_cold_ratio_to_fastest_verified_baseline":comparison,
                "selected_engine":"cadical195_original_cnf" if case=="new_r2_grid_21" else "janus_gf2",
                "selected_3_of_3_verified":selected["verified_3_of_3"],
                "censored_baselines":a["censored_arms"],
                "all_baselines_3_of_3_verified":all_fully_verified})
        good=all(x["full_cold_ratio_to_fastest_verified_baseline"] is not None
                 and x["full_cold_ratio_to_fastest_verified_baseline"]>=1.20
                 and x["selected_3_of_3_verified"] for x in host_rows)
        if good:
            winning.append(case)
        details[case]={"host_results":host_rows,"qualifies_1_20_both_hosts":good}

    narrow=(len(winning)>=2 and all_no_regret)
    verdict=("CONDITIONAL_NEW_SOURCE_CLASS_GAIN_CANDIDATE" if narrow
             else "NO_FROZEN_R2_SELECTOR_CLASS_GAIN_ESTABLISHED")
    if narrow and not all_complete:
        verdict="CONDITIONAL_NEW_SOURCE_GAIN_WITH_CENSORED_CONTROLS"
    out={"schema":"JANUS-E12C5-R2-TWO-HOST-FROZEN-AUDIT-V1",
         "verdict":verdict,"frozen_protocol_blob_sha1":PREREG_GIT_SHA,
         "prereg_sha256":pinnedsha,
         "source_manifest":reports[0]["source_manifest"],
         "host_platforms":hostnames,
         "new_source_count":len(CASES),
         "cold_children_total":sum(len(d["records"]) for d in reports),
         "selected_solvers_do_not_use_test_labels_or_run_timings":True,
         "per_case":details,"qualifying_sources":winning,
         "all_cases_within_5pct_regret":all_no_regret,
         "all_5_arms_all_cases_fully_verified":all_complete,
         "right_censored_cases":censored_cases,
         "conditional_gain_threshold":1.2,
         "any_positive_claim_scope":"same synthetic Lights-out family; not general SAT",
         "externally_sealed_blind_test":"NOT_PERFORMED",
         "external_independent_admin":"NOT_PERFORMED",
         "C023_champion_and_E12C4_loop":"UNCHANGED",
         "stage5_general_claim":"NOT_ESTABLISHED"}
    return out

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--report-root",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    z=a.parse_args()
    paths=sorted(z.report_root.rglob("RESULT.json"))
    if len(paths)!=2:
        raise SystemExit("E12C5_R2_EXPECTED_TWO_RESULT_JSON_GOT_"+str(len(paths)))
    result=audit([json.loads(p.read_text()) for p in paths])
    z.out.mkdir(parents=True,exist_ok=True)
    (z.out/"AUDIT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print("E12C5_R2_AUDIT",json.dumps(result,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
