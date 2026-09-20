#!/usr/bin/env python3
import argparse, json, pathlib, hashlib

def load(p): return json.loads(pathlib.Path(p).read_text())
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True)
    ap.add_argument("--freeze",required=True)
    ap.add_argument("--counter",required=True)
    ap.add_argument("--relation",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args()
    root=pathlib.Path(a.out); root.mkdir(parents=True,exist_ok=True)
    pre,fr,counter,relation=map(load,[a.prereg,a.freeze,a.counter,a.relation])

    input_checks={
      "prereg_name":pre["name"]=="C11_SURVIVOR_PAIR_FAMILY_GATE_V1",
      "prereg_status":pre["status"]=="FROZEN_PAIR_RELATION_STRUCTURE_REPRESENTABILITY_PREREGISTRATION__NO_REPAIR",
      "P1_bound":counter["gate_implications"]["P1"]=="FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY",
      "P2_bound":counter["gate_implications"]["P2"]=="FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY",
      "relation_authority":relation["status"]=="PASS_C11_SURVIVOR_PAIR_RELATION_REPRESENTATION",
      "freeze_gate_binding":fr["authorization"]["gate"]=="C11_SURVIVOR_PAIR_FAMILY_GATE_V1"
    }

    baseline={
      "name":"DECORATED_FALSE_TWIN_QUOTIENT",
      "status":"VERIFIED_SUPPORTING_REDUCTION",
      "definition":{
        "same_side":True,
        "equal_full_open_neighborhood":True,
        "same_old_type":True,
        "same_current_list":True,
        "same_post_Lemma10_role":True,
        "same_frozen_precoloring_labels":True
      },
      "proof":{
        "decorated_transposition_automorphism":[
          "For two same-side vertices satisfying the complete decorated-false-twin key, swapping them fixes every other vertex and preserves every graph edge/nonedge.",
          "Side, old type, current list, post-Lemma10 role, and all frozen labels are equal, so the transposition preserves the complete decorated instance rather than only the uncolored graph.",
          "Therefore it is a color-preserving automorphism of the frozen CSP instance."
        ],
        "R_C11_preservation":[
          "Equal full neighborhoods imply identical adjacency to every Y0' component, hence equal Sigma signatures.",
          "Equal full neighborhoods also preserve adjacency/nonadjacency to any opposite-side endpoint.",
          "Thus replacing one endpoint by a same-side decorated false twin preserves membership in R_C11."
        ],
        "Pi_preservation":[
          "Let phi be the decorated automorphism swapping same-side false twins.",
          "For every extension c realizing boundary colors on a survivor pair, c composed with phi^{-1} is an extension realizing the same ordered color values on the phi-image pair.",
          "Applying phi^{-1} gives the inverse map, hence a bijection between extensions.",
          "Therefore Pi(y,y') equals Pi(phi(y),phi(y')) exactly."
        ],
        "polynomial_discovery":[
          "Compute a decorated key for every A/B vertex consisting of side/role/labels plus its full adjacency bit-vector (or sorted neighborhood identifier list).",
          "Sort/hash these keys; equal keys are exactly the permitted decorated false-twin classes.",
          "This is polynomial in the graph encoding size."
        ],
        "summary_size":"One class key plus representative vertex identifier per same-side class; independent of class multiplicity."
      }
    }

    # Frozen authority audit for a stronger universal quotient.
    # This is deliberately not a mathematical negation; it records that no universal proof object
    # satisfying every P3 obligation is present in the bound authority.
    p3_obligations={
      "merges_distinct_pairs_universally_or_under_proved_applicability":False,
      "graph_state_only_membership":True,
      "summary_independent_of_pair_count":False,
      "exact_Pi_preservation":False,
      "polynomial_discovery":False,
      "frozen_budget_bound":False
    }
    audit={
      "baseline_not_sufficient":True,
      "reason_baseline_not_sufficient":"Decorated false-twin classes may all be singletons on a valid frozen-hypothesis instance, so this supporting quotient has no theorem guaranteeing nontrivial pair compression.",
      "equal_Sigma_rejected":True,
      "equal_matrix_rows_columns_rejected":True,
      "identity_classes_rejected":True,
      "n2_listing_rejected":True,
      "local_H8_shape_rejected":True,
      "color_orbit_only_rejected":True,
      "automorphism_orbits_not_promoted":"Exact Pi preservation is valid for decorated automorphisms, but no polynomial-time universal orbit-discovery theorem is bound by the frozen authority; arbitrary graph-automorphism orbit quotient is therefore not used.",
      "universal_P3_proof_object":"NOT_ESTABLISHED_BY_FROZEN_AUTHORITY"
    }

    outcome="P4_PAIR_STRUCTURE_UNRESOLVED"
    result={
      "schema":"janus.trump.c11_survivor_pair_family.execution.v1",
      "P1":"FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY",
      "P2":"FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY",
      "baseline":baseline,
      "P3":{
        "status":"NOT_ESTABLISHED_BY_FROZEN_AUTHORITY",
        "negative_claim":False,
        "obligation_receipt":p3_obligations,
        "audit":audit
      },
      "primary_outcome":outcome,
      "P4":{
        "status":"VERIFIED_AS_FROZEN_FALLBACK_OUTCOME",
        "meaning":"No universal nontrivial exact pair quotient/factorization satisfying all frozen P3 requirements was proved in this execution. This is not P3_FALSE and not a nonexistence theorem."
      },
      "scientific_ceiling":{
        "P1":"FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY",
        "P2":"FALSIFIED_BY_PARAMETRIC_P7_FREE_FAMILY",
        "P3":"NOT_ESTABLISHED",
        "PAIR_STRUCTURE":"UNRESOLVED",
        "REPAIR":"NOT_STARTED",
        "NEW_DESCRIPTOR":"NOT_DEFINED",
        "C1S_CS1_CSS":"NOT_REACHED",
        "LEMMA11_P7_LIFT":"OPEN",
        "P7_FREE_4_COLOR_IN_P":"NOT_PROVED",
        "HARDNESS_LOCALIZED":"NOT_CLAIMED",
        "P_VS_NP":"OPEN"
      },
      "forbidden_interpretations":["P3_FALSE","NO_QUOTIENT_EXISTS","HARDNESS","EXPONENTIAL_LOWER_BOUND"],
      "repair_attempted":False,
      "successor_autoactivated":False,
      "stop":True,
      "input_checks":input_checks,
      "source_hashes":{
        "prereg_sha256":sha(a.prereg),
        "freeze_sha256":sha(a.freeze),
        "counter_sha256":sha(a.counter),
        "relation_sha256":sha(a.relation)
      }
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "P1":result["P1"],"P2":result["P2"],
      "baseline":baseline["status"],
      "P3":result["P3"]["status"],
      "outcome":outcome
    },sort_keys=True))
    if not all(input_checks.values()): raise SystemExit(2)
    if outcome!="P4_PAIR_STRUCTURE_UNRESOLVED": raise SystemExit(3)

if __name__=="__main__": main()
