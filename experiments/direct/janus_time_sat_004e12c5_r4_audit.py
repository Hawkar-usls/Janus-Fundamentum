#!/usr/bin/env python3
"""E12C5 R4: locked-source two-host audit, independent recomputation from raw.

No threshold tuning, no self-comparison to JANUS GF2 ablation,
no invented SAT completion for censored or inapplicable solvers.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from math import isclose
from statistics import median

ROOT=Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import janus_time_sat_004e12c5_r4_model as model
import janus_time_sat_004e12c5_r4_benchmark as cold

def check(hostdocs):
    if len(hostdocs)!=2:
        raise AssertionError("R4_BOTH_HOSTS_REQUIRED")
    prereg,psha=model.load_frozen()
    # The privileged auditor fits from immutable R1-R3 evidence itself.
    # A worker may not manufacture a more favorable FIT.json just by
    # replacing its SHA field in both child and parent receipts.
    independently_rebuilt_fit_sha=sha256(model.canonical(model.train())).hexdigest()
    if any(doc.get("fit_sha256")!=independently_rebuilt_fit_sha for doc in hostdocs):
        raise AssertionError("R4_CROSS_HOST_FIT_NOT_REPRODUCIBLE_FROM_PAST")
    expected=[c["id"] for c in prereg["evaluation_cohort"]]
    if expected!=cold.CASES or len(expected)!=8:
        raise AssertionError("R4_SOURCE_SET_CHANGED")
    cols={c["id"]:c for c in prereg["evaluation_cohort"]}
    artifact_manifest={}
    for host in hostdocs:
        if (host["schema"]!="JANUS-E12C5-R4-RAW-RESULT-V1"
            or host["protocol_sha256"]!=psha
            or host["protocol_blob_sha1"]!=model.FROZEN_BLOB
            or len(host["raw_cold_records"])!=120
            or set(host["source_manifest"])!=set(expected)
            or set(host["summary"])!=set(expected)
            or set(host["fit_train_original_sha256"])==set()
            or len(host["fit_train_original_sha256"])!=13
            or not host["all_censored_results_retained"]
            or not host["R4_samples_never_used_to_fit_own_selector"]
            or not host["all_source_SHA_r4_new_and_unique"]):
            raise AssertionError("R4_BAD_HOST_PROVENANCE_OR_RAW_RECEIPTS")
        original_shas=[]
        for case,item in host["source_manifest"].items():
            cohort=cols[case]
            n,rows=model.source(case)
            original_sha=model.r1.original_sha(rows,n)
            if (item["sha256"]!=original_sha or item["n"]!=n
                or item["clauses"]!=len(rows)
                or item["experimental_family"]!=cohort["kind"]
                or item["literal_occurrences"]!=sum(len(x) for x in rows)
                or item["training_original"] or
                item["sha256"] in host["fit_train_original_sha256"]):
                raise AssertionError("R4_SOURCE_RECONSTRUCTION_OR_TRAINING_LEAK")
            original_shas.append(original_sha)
        if len(set(original_shas))!=8:
            raise AssertionError("R4_DUPLICATE_R4_SOURCE_SHA")
        received=set()
        for record in host["raw_cold_records"]:
            case,arm,rep=record["case"],record["arm"],record["repeat"]
            key=(case,arm,rep)
            if (key in received or case not in cols or arm not in cold.ARMS
                or rep not in (0,1,2)):
                raise AssertionError("R4_DUPLICATE_OR_UNREGISTERED_CHILD")
            received.add(key)
            value=record["child"]
            if (not isinstance(record["parent_full_cold_wall_s"],(int,float))
                or record["parent_full_cold_wall_s"]<=0):
                raise AssertionError("R4_INVALID_COLD_DURATION")
            if value["status"]==cold.SAT:
                if (not value["original_cnf_verified"] or not value["witness_sha256"]
                    or value["original_sha256"]!=host["source_manifest"][case]["sha256"]
                    or value["fit_sha256"]!=host["fit_sha256"]
                    or value["protocol_sha256"]!=psha
                    or value["case"]!=case or value["arm"]!=arm):
                    raise AssertionError("R4_FALSE_VERIFIED_SAT_RECEIPT")
                if arm==cold.ARMS[0]:
                    if value["engine_selected"] not in (
                        "janus_gf2","cryptominisat_native_xor","cryptominisat_original_cnf"):
                        raise AssertionError("R4_UNREGISTERED_SELECTOR_ENGINE")
                    family=cols[case]["kind"]
                    if family!="LIGHTSOUT_PLANTED_SAT" and value["engine_selected"]!="cryptominisat_original_cnf":
                        raise AssertionError("R4_OUT_OF_DOMAIN_GF2_FORBIDDEN")
                    if (value["engine_selected"]=="janus_gf2"
                        and (value["predictions_prior_only"] is None
                             or value["predictions_prior_only"]["risk_lower_bound_gain"]<1.2
                             or value["predictions_prior_only"]["predicted_gain"]<1.4)):
                        raise AssertionError("R4_GF2_SELECT_WITHOUT_PAST_CONFIDENCE")
            elif value["status"]==cold.ABSTAIN:
                if arm not in ("janus_gf2_exact_ablation","cryptominisat_native_xor"):
                    raise AssertionError("R4_UNAUTHORIZED_ABSTENTION")
                if host["source_manifest"][case]["exact_xor_coverage"]:
                    raise AssertionError("R4_ABSTAINED_ON_CERTIFIED_EXACT_XOR")
            elif value["status"] not in ("UNKNOWN_WALL_CENSORED","ERROR_OR_CPU_CENSORED"):
                raise AssertionError("R4_UNKNOWN_RESULT_STATUS_NOT_REGISTERED")
        if len(received)!=120:
            raise AssertionError("R4_INCOMPLETE_CHILD_MATRIX")
        for case in expected:
            actual=host["summary"][case]
            if set(actual["arms"])!=set(cold.ARMS):
                raise AssertionError("R4_MISSING_CONTROL_ARMS")
            for arm in cold.ARMS:
                q=[x for x in host["raw_cold_records"] if x["case"]==case and x["arm"]==arm]
                full=len(q)==3 and all(x["child"]["status"]==cold.SAT for x in q)
                label=actual["arms"][arm]
                if label["verified_sat_3of3"]!=full or label["statuses"]!=[
                        x["child"]["status"] for x in q]:
                    raise AssertionError("R4_FALSIFIED_SUCCESS_CLASSIFICATION")
                if not full and label["median_full_cold_s"] is not None:
                    raise AssertionError("R4_CENSORED_BASELINE_PUBLISHED_AS_TIMING")
                if full and not isclose(label["median_full_cold_s"],
                        median(x["parent_full_cold_wall_s"] for x in q),
                        rel_tol=1e-11,abs_tol=1e-11):
                    raise AssertionError("R4_RAW_TO_MEDIAN_AUDIT_MISMATCH")
            best=[actual["arms"][arm]["median_full_cold_s"] for arm in cold.CONTROL_ARMS
                  if actual["arms"][arm]["verified_sat_3of3"]]
            pred=actual["arms"][cold.ARMS[0]]
            ratio=min(best)/pred["median_full_cold_s"] if pred["verified_sat_3of3"] and best else None
            recorded=actual["ratio_to_fastest_verified_EXTERNAL"]
            if ((ratio is None)!=(recorded is None) or (ratio is not None and
                not isclose(ratio,recorded,rel_tol=1e-11,abs_tol=1e-11))):
                raise AssertionError("R4_EXTERNAL_GAIN_REPLAY_DRIFT")
        artifact_manifest[host["host"]]=host["source_manifest"]
    if len(artifact_manifest)!=2:
        raise AssertionError("R4_TWO_DISTINCT_HOST_PLATFORM_REQUIRED")
    if not (hostdocs[0]["source_manifest"]==hostdocs[1]["source_manifest"]
       and hostdocs[0]["fit_sha256"]==hostdocs[1]["fit_sha256"]
       and hostdocs[0]["fit_train_original_sha256"]==hostdocs[1]["fit_train_original_sha256"]
       and hostdocs[0]["executing_R4_script_sha256"]==hostdocs[1]["executing_R4_script_sha256"]
       and hostdocs[0]["executing_R4_model_sha256"]==hostdocs[1]["executing_R4_model_sha256"]):
        raise AssertionError("R4_CROSS_HOST_PROVENANCE_OR_CODE_DRIFT")

    per_case={}
    passing_sizes=set()
    abstention_good=True
    all_sources_verified=True
    no_regret=True
    complete_all_controls=True
    for case in expected:
        frames=[]
        for host in hostdocs:
            s=host["summary"][case]
            selector=s["arms"][cold.ARMS[0]]
            good=selector["verified_sat_3of3"]
            all_sources_verified &= good
            gain=s["ratio_to_fastest_verified_EXTERNAL"]
            if gain is None or gain <1/1.10:
                no_regret=False
            censored=[]
            for arm in cold.CONTROL_ARMS:
                status=s["arms"][arm]
                # Native XOR on non-certified original is mathematically not applicable.
                if arm=="cryptominisat_native_xor" and not host["source_manifest"][case]["exact_xor_coverage"]:
                    if status["statuses"] != [cold.ABSTAIN]*3:
                        raise AssertionError("R4_INAPPLICABLE_NATIVE_PROOF_NOT_ABSTAINED")
                    continue
                if not status["verified_sat_3of3"]:
                    complete_all_controls=False
                    censored.append(arm)
            frames.append({"host":host["host"],"selector_all_three_verified":good,
                           "selector_engine":s["selected_engine"],"ratio_to_fastest_verified_external":gain,
                           "censored_applicable_baselines":censored})
        iswin=all(x["selector_all_three_verified"] and
                    x["ratio_to_fastest_verified_external"] is not None and
                    x["ratio_to_fastest_verified_external"]>=1.20 for x in frames)
        if iswin and cols[case]["kind"]=="LIGHTSOUT_PLANTED_SAT":
            passing_sizes.add(cols[case]["side"])
        if cols[case]["kind"]!="LIGHTSOUT_PLANTED_SAT":
            abstention_good &= all(x["selector_engine"]=="cryptominisat_original_cnf"
                                    for x in frames)
        per_case[case]={"hosts":frames,"passed_1_20_on_both":iswin}
    narrow=(len(passing_sizes)>=2 and all_sources_verified
            and no_regret and abstention_good)
    return {
        "schema":"JANUS-E12C5-R4-LOCKED-TWO-HOST-AUDIT-V1",
        "scientific_verdict":("NEW_CNF_FEATURE_CONDITIONAL_GAIN_CANDIDATE"
                    if narrow else "NO_R4_FROZEN_GENERALIZABLE_CLASS_GAIN"),
        "prereg_sha256":psha,
        "prereg_git_blob_sha1":model.FROZEN_BLOB,
        "source_manifest":hostdocs[0]["source_manifest"],
        "training_fit_sha256":hostdocs[0]["fit_sha256"],
        "source_count":8,"full_cold_children":240,
        "per_case":per_case,
        "passing_new_distinct_grid_sizes":sorted(passing_sizes),
        "all_new_selected_verified_3of3":all_sources_verified,
        "all_new_sources_no_regret_gt_10pct":no_regret,
        "non_grid_no_specialized_GF2":abstention_good,
        "strict_all_applicable_external_comparators_verified":complete_all_controls,
        "no_side_modulo_4_rule":True,
        "GF2_internal_ablation_not_external_comparator":True,
        "censored_and_inapplicable_not_counted_as_completed":True,
        "external_independent_admin":"NOT_AVAILABLE",
        "external_blind_holdout":"NOT_PERFORMED",
        "general_3SAT_speedup":"NOT_ESTABLISHED",
        "Stage5_universal":"CLOSED",
        "production_C023":"UNCHANGED",
        "E12C4_loop":"UNTOUCHED"
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--report-root",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    z=a.parse_args()
    files=sorted(z.report_root.rglob("RESULT.json"))
    if len(files)!=2:
        raise SystemExit("R4_INCOMPLETE_TWO_HOST_REPORTS "+str(len(files)))
    report=check([json.loads(q.read_text()) for q in files])
    z.out.mkdir(parents=True,exist_ok=True)
    (z.out/"AUDIT.json").write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("R4_TWO_HOST_AUDIT",json.dumps(report,sort_keys=True),flush=True)
if __name__=="__main__":
    main()
