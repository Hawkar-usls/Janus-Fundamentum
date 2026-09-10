from __future__ import annotations
import argparse, hashlib, json, math
from pathlib import Path

EXPECTED_SIZES=(48,72,96,144,192,288,384)
EXPECTED_COHORTS=("B1_BALANCED_BLIND","B2_HASH_PLANTED_SAT")
ALLOWED_TERMINALS={"EMPTY_CNF_SAT","EMPTY_CLAUSE_UNSAT","2CNF","HORN","AFFINE_XOR_COMPLETE_CNF_BUNDLE","RENAMABLE_HORN","DUAL_HORN","BETA_ACYCLIC"}

def sha256(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def verify(out:Path)->dict:
    rp=out/"LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_RESULT.json"
    mp=out/"LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_MANIFEST.json"
    cp=out/"LANE_B_INERT_CONTRACT.json"
    for p in (rp,mp,cp):
        if not p.is_file(): raise AssertionError(f"MISSING:{p.name}")
    d=json.loads(rp.read_text()); m=json.loads(mp.read_text()); c=json.loads(cp.read_text())
    assert c["status"]=="PASS" and c["real_lane_b_instance_executed"] is False
    assert c["lane_b_discovery_count"]==14 and c["holdout_lane_b_count_frozen_unopened"]==6
    assert d["LANE_B_DISCOVERY_COMPLETE"] is True, d["pipeline_failures"]
    assert d["completed_lane_b_records"]==14 and d["generated_real_USF_instances_this_gate"]==14
    assert len(d["instances"])==14 and len(m["records"])==14 and not d["pipeline_failures"]
    expected=[(n,cohort) for n in EXPECTED_SIZES for cohort in EXPECTED_COHORTS]
    assert [(x["n"],x["cohort"]) for x in d["instances"]]==expected
    record_hashes=[]
    originals=[]
    residuals=[]
    for i,row in enumerate(d["instances"]):
        assert row["status"]=="PASS"
        n=row["n"]
        assert row["original_CLV"]==[5*n,15*n,n]
        assert row["BA25_FACTOR_TD_VALIDATION_PASS"] is True
        assert row["BA25_FACTOR_TD_VERIFIED_WIDTH"]==max(row["INCIDENCE_TD_VERIFIED_UB"],1)
        assert row["BA25_status"] in {"BA25_DIAGNOSTIC_COMPLETE","NOT_RUN_RESOURCE_GUARD"}
        term=row["terminal_outcome"]
        assert (term["classification"]=="OPEN_CORE" and term["terminal"] is None) or (term["classification"]=="TERMINAL_MEMBER" and term["terminal"] in ALLOWED_TERMINALS)
        ts=row["truth_state"]
        assert ts in {"SAT_WITNESS_VERIFIED","UNSAT_PROOF_VERIFIED","UNKNOWN_RESOURCE_LIMIT"}
        if row["cohort"]=="B2_HASH_PLANTED_SAT":
            assert ts!="UNSAT_PROOF_VERIFIED"
            if ts=="SAT_WITNESS_VERIFIED":
                assert row["truth_contract"]["B2_independent_SAT_witness_verified"] is True
        assert row["INCIDENCE_TW_INTERVAL"]==row["width_interval_after"]
        assert row["strict_width_drop"]==(row["width_interval_before"][0] > row["width_interval_after"][1])
        if row["r_n"] is not None:
            assert abs(row["r_n"]-row["INCIDENCE_TD_VERIFIED_UB"]/math.log2(n))<1e-12
        raw=out/"instances"/f"{i:03d}.json"
        assert raw.is_file()
        rh=sha256(raw)
        assert rh==row["record_sha256"]
        rec=json.loads(raw.read_text())
        pre=rec["lane_b_generator_preflight"]
        assert pre["original_canonical_dimacs_sha256"]==row["original_sha256"]
        assert pre["original_CLV"]==[5*n,15*n,n]
        assert pre["clause_width_all_3"] is True and pre["variable_degree_all_15"] is True and pre["no_reseed"] is True
        if row["cohort"]=="B2_HASH_PLANTED_SAT":
            assert pre["B2_constructional_plant_replay"]["planted_assignment_replay_satisfies_original"] is True
            assert pre["B2_constructional_plant_replay"]["truth_authority"] is False
        bind=rec["BA25_diagnostic"]["factor_td_binding"]
        iv=bind["independent_factor_td_validation"]
        assert iv["pass"] is True and iv["tree"] is True and iv["vertex_coverage"] is True and iv["edge_coverage"] is True and iv["running_intersection"] is True
        assert bind["BA25_FACTOR_TD_VERIFIED_WIDTH"]==iv["width"]
        assert bind["frozen_lift_relation_pass"] is True
        assert bind["bare_cross_domain_tau_used"] is False
        assert rec["truth_is_last_authoritative_stage"] is True
        assert rec["postselection_allowed"] is False and rec["retained"] is True
        assert rec["H1"]==rec["H2"]==rec["H3"]=="OPEN"
        assert rec["SAT_IN_P"]=="NOT_PROVED" and rec["P_VS_NP"]=="OPEN" and rec["BA26_STARTED"] is False
        mr=m["records"][i]
        assert mr["scheduled_instance_id"]==row["scheduled_instance_id"]
        assert mr["record_sha256"]==rh
        assert mr["original_sha256"]==row["original_sha256"]
        assert mr["residual_sha256"]==row["residual_sha256"]
        record_hashes.append(rh); originals.append(row["original_sha256"]); residuals.append(row["residual_sha256"])
    assert d["OPEN_CORE_is_scientific_data_not_failure"] is True
    assert d["UNKNOWN_RESOURCE_LIMIT_is_scientific_data_not_failure"] is True
    assert d["NOT_RUN_RESOURCE_GUARD_is_scientific_data_not_failure"] is True
    assert d["finite_records_prove_H1"] is False and d["finite_records_prove_H3"] is False
    assert d["LANE_C_EXECUTION_STARTED"] is False and d["HOLDOUT_EXECUTION_STARTED"] is False
    assert d["H1"]==d["H2"]==d["H3"]=="OPEN"
    assert d["SAT_IN_P"]=="NOT_PROVED" and d["P_VS_NP"]=="OPEN" and d["BA26_STARTED"] is False
    return {
        "schema":"TRUMP_USF_R0_LANE_B_ADVERSARIAL_GENERAL_3CNF_DISCOVERY_INDEPENDENT_RAW_EVIDENCE_VERIFICATION",
        "status":"PASS",
        "records_verified":14,
        "result_sha256":sha256(rp),
        "manifest_sha256":sha256(mp),
        "record_hashes":record_hashes,
        "original_hashes":originals,
        "residual_hashes":residuals,
        "lane_c_executed":False,
        "holdout_executed":False,
        "BA26_started":False,
        "H1":"OPEN","H2":"OPEN","H3":"OPEN","SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN",
        "interpretation_performed":False,
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",required=True); ap.add_argument("--receipt")
    a=ap.parse_args(); out=verify(Path(a.output_dir).resolve())
    text=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if a.receipt: Path(a.receipt).write_text(text,encoding="utf-8")
    else: print(text,end="")
if __name__=="__main__": main()
