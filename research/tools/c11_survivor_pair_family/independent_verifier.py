#!/usr/bin/env python3
import argparse,json,pathlib

def load(p): return json.loads(pathlib.Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True)
    ap.add_argument("--counter",required=True)
    ap.add_argument("--relation",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    c,counter,rel=load(a.candidate),load(a.counter),load(a.relation)
    checks={}
    checks["P1_authority"]=c["P1"]=="FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY" and counter["gate_implications"]["P1"]=="FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY"
    checks["P2_authority"]=c["P2"]=="FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY" and counter["gate_implications"]["P2"]=="FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY"
    checks["relation_authority"]=rel["status"]=="PASS_C11_SURVIVOR_PAIR_RELATION_REPRESENTATION"
    b=c["baseline"]
    checks["baseline_verified"]=b["status"]=="VERIFIED_SUPPORTING_REDUCTION"
    checks["baseline_full_decorated_key"]=all(b["definition"].values())
    checks["baseline_R_proof"]="R_C11_preservation" in b["proof"]
    checks["baseline_Pi_bijection"]="Pi_preservation" in b["proof"] and any("bijection" in x for x in b["proof"]["Pi_preservation"])
    checks["baseline_polynomial"]="polynomial_discovery" in b["proof"]
    checks["baseline_not_promoted"]=c["P3"]["audit"]["baseline_not_sufficient"] is True
    checks["anti_cheat_identity"]=c["P3"]["audit"]["identity_classes_rejected"] is True
    checks["anti_cheat_sigma"]=c["P3"]["audit"]["equal_Sigma_rejected"] is True
    checks["anti_cheat_rows"]=c["P3"]["audit"]["equal_matrix_rows_columns_rejected"] is True
    checks["anti_cheat_n2"]=c["P3"]["audit"]["n2_listing_rejected"] is True
    checks["P3_not_established"]=c["P3"]["status"]=="NOT_ESTABLISHED_BY_FROZEN_AUTHORITY" and c["P3"]["negative_claim"] is False
    checks["P4_exact"]=c["primary_outcome"]=="P4_PAIR_STRUCTURE_UNRESOLVED" and c["P4"]["status"]=="VERIFIED_AS_FROZEN_FALLBACK_OUTCOME"
    checks["no_forbidden_inference"]=set(c["forbidden_interpretations"])=={"P3_FALSE","NO_QUOTIENT_EXISTS","HARDNESS","EXPONENTIAL_LOWER_BOUND"}
    sc=c["scientific_ceiling"]
    checks["ceiling"]=(
      sc["PAIR_STRUCTURE"]=="UNRESOLVED" and sc["REPAIR"]=="NOT_STARTED" and
      sc["NEW_DESCRIPTOR"]=="NOT_DEFINED" and sc["LEMMA11_P7_LIFT"]=="OPEN" and
      sc["P7_FREE_4_COLOR_IN_P"]=="NOT_PROVED" and sc["HARDNESS_LOCALIZED"]=="NOT_CLAIMED" and
      sc["P_VS_NP"]=="OPEN"
    )
    checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
    verdict="INDEPENDENT_P4_PAIR_STRUCTURE_UNRESOLVED_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
    out={
      "schema":"janus.trump.c11_survivor_pair_family.independent.v1",
      "verdict":verdict,
      "checks":checks,
      "primary_outcome":c["primary_outcome"],
      "baseline_status":b["status"],
      "P3_status":c["P3"]["status"],
      "scientific_ceiling":sc
    }
    pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v]},sort_keys=True))
    if verdict!="INDEPENDENT_P4_PAIR_STRUCTURE_UNRESOLVED_VERIFIED": raise SystemExit(1)

if __name__=="__main__": main()
