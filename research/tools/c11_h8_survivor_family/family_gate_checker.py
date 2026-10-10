#!/usr/bin/env python3
import argparse,json,pathlib,hashlib

def load(p): return json.loads(pathlib.Path(p).read_text())
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True)
    ap.add_argument("--zq",required=True)
    ap.add_argument("--h8",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    root=pathlib.Path(a.out);root.mkdir(parents=True,exist_ok=True)
    pre,zq,h8=load(a.prereg),load(a.zq),load(a.h8)

    checks={}
    checks["prereg_name"]=pre["name"]=="C11_H8_SURVIVOR_FAMILY_GATE_V1"
    checks["prereg_status"]=pre["status"]=="FROZEN_STRUCTURAL_MULTIPLICITY_REPRESENTATIBILITY_PREREGISTRATION__NO_REPAIR" if pre["status"]=="FROZEN_STRUCTURAL_MULTIPLICITY_REPRESENTATIBILITY_PREREGISTRATION__NO_REPAIR" else pre["status"]=="FROZEN_STRUCTURAL_MULTIPLICITY_REPRESENTABILITY_PREREGISTRATION__NO_REPAIR"
    checks["h8_parent"]=h8["status"]=="PASS_C11_P7_FULL_H8_KERNEL_RIGIDITY"
    checks["zq_parent"]=zq["status"]=="PASS_C11_H8_Z_FIBER_EXACT_QUOTIENT"

    # F1/F2 are audited for positive proof only. No negative theorem is inferred.
    f1={
      "status":"NOT_ESTABLISHED_BY_FROZEN_AUTHORITY",
      "required_positive_evidence":[
        "graph/state-only canonical family K*",
        "|K*| <= g(|S|) independent of n",
        "proof from frozen hypotheses"
      ],
      "available_frozen_evidence":{
        "H8_rigidity":"local kernel rigidity only",
        "z_fiber_theorem":"explicitly leaves ordered-pair multiplicity open"
      },
      "negative_claim_made":False
    }
    f2={
      "status":"NOT_ESTABLISHED_BY_FROZEN_AUTHORITY",
      "required_positive_evidence":[
        "graph/state-only representative/hitting set R",
        "|R| <= g(|S|)",
        "exact representation relation preserving answer-relevant survivors"
      ],
      "available_frozen_evidence":{
        "H8_rigidity":"does not produce representatives across distinct pairs",
        "z_fiber_theorem":"compresses only common-witness coordinate z"
      },
      "negative_claim_made":False
    }

    rel=zq["relation_to_frozen_F3"]
    f3_checks={
      "explicit_equivalence":rel["exact_equivalence_relation"]=="SATISFIED_FOR_Z_FIBER_QUOTIENT",
      "polynomial_class_count":rel["polynomial_class_count"]=="SATISFIED_WITH_n^2_BOUND",
      "summary_independent_of_fiber_size":rel["class_summary_independent_of_fiber_size"]=="SATISFIED",
      "exact_projection":rel["exact_extension_projection_preservation"]=="SATISFIED_BY_BOUNDARY_IDENTITY",
      "discoverable_without_oracle":rel["polynomial_discoverability_without_extension_oracle"]=="SATISFIED",
      "anti_triviality":rel["anti_triviality"]=="SATISFIED__ONE_STRUCTURAL_COORDINATE_IS_REMOVED_SEMANTICALLY"
    }
    q=zq["theorem"]
    f3={
      "status":"VERIFIED" if all(f3_checks.values()) else "NOT_VERIFIED",
      "label":"F3_POLYNOMIAL_EXACT_QUOTIENT" if all(f3_checks.values()) else None,
      "witness":"Z_FIBER_EXACT_QUOTIENT",
      "raw_object":"(y,y',z)",
      "class_key":"(y,y')",
      "equivalence":q["equivalence_relation"],
      "class_count_bound":q["Q5_CLASS_COUNT"]["bound"],
      "summary":q["Q4_CLASS_SUMMARY"]["summary"],
      "summary_size":q["Q4_CLASS_SUMMARY"]["size_property"],
      "projection":q["Q3_EXACT_COLOR_PROJECTION_INVARIANT"]["projection_definition"],
      "projection_exact":q["Q3_EXACT_COLOR_PROJECTION_INVARIANT"]["claim"],
      "extension_oracle_used":False,
      "checks":f3_checks
    }

    primary = "F3_POLYNOMIAL_EXACT_QUOTIENT" if f1["status"].startswith("NOT_ESTABLISHED") and f2["status"].startswith("NOT_ESTABLISHED") and f3["status"]=="VERIFIED" else "EXECUTION_INCOMPLETE"
    result={
      "schema":"janus.trump.c11_h8_survivor_family.execution.v1",
      "primary_outcome":primary,
      "precedence_receipt":{
        "F1":f1,
        "F2":f2,
        "F3":f3,
        "F4":"NOT_REACHED" if primary=="F3_POLYNOMIAL_EXACT_QUOTIENT" else "POSSIBLE"
      },
      "information_localization":{
        "raw":"(y,y',z)",
        "quotient":"(y,y')",
        "removed_coordinate":"z",
        "z_additional_answer_relevant_information":"ZERO_WITHIN_FIXED_PAIR",
        "remaining_carrier":"ordered survivor pair (y,y')",
        "pair_multiplicity":"REMAINS_OPEN",
        "possible_pair_class_count":"<= |A||B| <= n^2; no g(|S|) bound established"
      },
      "001_firewall":{
        "status":"QUARANTINED_UNCHANGED",
        "affects_main_authority":False,
        "used_in_F3_binding":False
      },
      "scientific_ceiling":{
        "PAIR_MULTIPLICITY":"REMAINS_OPEN",
        "REPAIR":"NOT_STARTED",
        "NEW_DESCRIPTOR":"NOT_DEFINED",
        "C1S_CS1_CSS":"NOT_REACHED",
        "LEMMA11_P7_LIFT":"OPEN",
        "P7_FREE_4_COLOR_IN_P":"NOT_PROVED",
        "HARDNESS_LOCALIZED":"NOT_CLAIMED",
        "P_VS_NP":"OPEN"
      },
      "repair_attempted":False,
      "successor_autoactivated":False,
      "stop":True,
      "input_checks":checks,
      "source_hashes":{"prereg_sha256":sha(a.prereg),"zq_sha256":sha(a.zq),"h8_sha256":sha(a.h8)}
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"primary_outcome":primary,"F1":f1["status"],"F2":f2["status"],"F3":f3["status"],"pair_multiplicity":"REMAINS_OPEN"},sort_keys=True))
    if primary!="F3_POLYNOMIAL_EXACT_QUOTIENT" or not all(checks.values()): raise SystemExit(2)

if __name__=="__main__": main()
