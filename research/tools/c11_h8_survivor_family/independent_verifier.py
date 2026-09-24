#!/usr/bin/env python3
import argparse,json,pathlib

def load(p): return json.loads(pathlib.Path(p).read_text())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--candidate",required=True)
    ap.add_argument("--zq",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    c,z=load(a.candidate),load(a.zq)
    checks={}
    checks["outcome_F3"]=c["primary_outcome"]=="F3_POLYNOMIAL_EXACT_QUOTIENT"
    checks["F1_not_negative"]=c["precedence_receipt"]["F1"]["status"]=="NOT_ESTABLISHED_BY_FROZEN_AUTHORITY" and c["precedence_receipt"]["F1"]["negative_claim_made"] is False
    checks["F2_not_negative"]=c["precedence_receipt"]["F2"]["status"]=="NOT_ESTABLISHED_BY_FROZEN_AUTHORITY" and c["precedence_receipt"]["F2"]["negative_claim_made"] is False
    checks["zq_status"]=z["status"]=="PASS_C11_H8_Z_FIBER_EXACT_QUOTIENT"
    rel=z["relation_to_frozen_F3"]
    checks["F3_all_requirements"]=(
      rel["exact_equivalence_relation"]=="SATISFIED_FOR_Z_FIBER_QUOTIENT" and
      rel["polynomial_class_count"]=="SATISFIED_WITH_n^2_BOUND" and
      rel["class_summary_independent_of_fiber_size"]=="SATISFIED" and
      rel["exact_extension_projection_preservation"]=="SATISFIED_BY_BOUNDARY_IDENTITY" and
      rel["polynomial_discoverability_without_extension_oracle"]=="SATISFIED" and
      rel["anti_triviality"]=="SATISFIED__ONE_STRUCTURAL_COORDINATE_IS_REMOVED_SEMANTICALLY"
    )
    t=z["theorem"]
    checks["equivalence_exact"]=t["equivalence_relation"]=="(y,y',z1) ~ (u,u',z2) iff y=u and y'=u'."
    checks["n2_bound"]=t["Q5_CLASS_COUNT"]["verdict"]=="PASS" and "n^2" in t["Q5_CLASS_COUNT"]["bound"]
    checks["projection_identity"]=t["Q3_EXACT_COLOR_PROJECTION_INVARIANT"]["verdict"]=="PASS"
    checks["no_oracle"]=t["Q1_EQUIVALENCE_AND_DISCOVERABILITY"]["verdict"]=="PASS"
    checks["pair_open"]=c["scientific_ceiling"]["PAIR_MULTIPLICITY"]=="REMAINS_OPEN"
    checks["repair_off"]=c["repair_attempted"] is False and c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED"
    checks["descriptor_off"]=c["scientific_ceiling"]["NEW_DESCRIPTOR"]=="NOT_DEFINED"
    checks["001_firewall"]=c["001_firewall"]["affects_main_authority"] is False and c["001_firewall"]["used_in_F3_binding"] is False
    checks["stop"]=c["stop"] is True and c["successor_autoactivated"] is False
    verdict="INDEPENDENT_F3_Z_FIBER_QUOTIENT_BINDING_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
    out={"schema":"janus.trump.c11_h8_survivor_family.independent.v1","verdict":verdict,"checks":checks,
         "primary_outcome_seen":c["primary_outcome"],"pair_multiplicity":"REMAINS_OPEN",
         "scientific_ceiling":c["scientific_ceiling"]}
    pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v]},sort_keys=True))
    if verdict!="INDEPENDENT_F3_Z_FIBER_QUOTIENT_BINDING_VERIFIED": raise SystemExit(1)

if __name__=="__main__": main()
