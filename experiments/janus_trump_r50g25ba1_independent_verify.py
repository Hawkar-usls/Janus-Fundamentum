from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

import janus_trump_r50g25ba0_target_family_expressivity_interface_capacity as ba0
import janus_trump_r50g25az_arbitrary_g_chain_composition_theorem as az

STATES=("TOP","FORCE_0","FORCE_1","BOTTOM")
VAL={
    "TOP": frozenset((0,1)),
    "FORCE_0": frozenset((0,)),
    "FORCE_1": frozenset((1,)),
    "BOTTOM": frozenset(),
}


def classify(s):
    fs=frozenset(int(x) for x in s)
    for k,v in VAL.items():
        if fs==v:
            return k
    return None


def recompute_endpoint_relation():
    Uinfo=az.source_unit()
    U=ba0.r33.canonical_formula(Uinfo["root"])
    models, counts, first=ba0.enumerate_unit_models(U)
    pairs=sorted([list(k) for k,v in counts.items() if v>0])
    return Uinfo,U,models,counts,first,pairs


def compose(rho,sigma,tau,pairs):
    out=set()
    for q in (VAL[rho] & VAL[sigma]):
        for p in (0,1):
            if [q,p] not in pairs:
                continue
            for qn in (0,1):
                if p or qn:
                    out.add(qn)
    out &= set(VAL[tau])
    return classify(out)


def direct_signature(a):
    return tuple(int(bool(VAL[a] & VAL[k])) for k in STATES)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--result", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args=ap.parse_args()
    r=json.loads(args.result.read_text())
    failures=[]

    if r.get("preregistration_commit")!="47ac7f28dfdb3b057a1a21d7c8492f37d73e57f6":
        failures.append("PREREG_DRIFT")
    if r.get("parent_BA0_source_head")!="0fbc2bf9e2ddb08e03569f8e8dcafb1d29ed83f9":
        failures.append("BA0_PARENT_DRIFT")

    Uinfo,U,models,counts,first,pairs=recompute_endpoint_relation()
    if Uinfo.get("failures"):
        failures.append(["SOURCE_UNIT_FAILURES",Uinfo.get("failures")])
    if len(models)!=60:
        failures.append(["UNIT_MODEL_COUNT",len(models)])
    exp_pairs=[[0,0],[0,1],[1,0],[1,1]]
    if pairs!=exp_pairs:
        failures.append(["ENDPOINT_RELATION",pairs])

    # Recompute local Myhill-Nerode-like signatures under allowed unary continuations.
    sig={a:list(direct_signature(a)) for a in STATES}
    if len({tuple(v) for v in sig.values()})!=4:
        failures.append(["LOCAL_EQUIVALENCE_CLASS_COUNT",sig])
    req={
        "FORCE_0_plus_K0": bool(VAL["FORCE_0"] & VAL["FORCE_0"]),
        "FORCE_1_plus_K0": bool(VAL["FORCE_1"] & VAL["FORCE_0"]),
        "FORCE_1_plus_K1": bool(VAL["FORCE_1"] & VAL["FORCE_1"]),
        "FORCE_0_plus_K1": bool(VAL["FORCE_0"] & VAL["FORCE_1"]),
    }
    if req!={"FORCE_0_plus_K0":True,"FORCE_1_plus_K0":False,"FORCE_1_plus_K1":True,"FORCE_0_plus_K1":False}:
        failures.append(["FORCE_DISTINGUISHABILITY",req])

    # Recompute the complete 64-entry algebra and exact symbolic law independently.
    table={}
    for rho in STATES:
        for sigma in STATES:
            for tau in STATES:
                got=compose(rho,sigma,tau,pairs)
                if got not in STATES:
                    failures.append(["CLOSURE",rho,sigma,tau,got])
                meet_empty=not bool(VAL[rho] & VAL[sigma])
                expected="BOTTOM" if meet_empty else tau
                if got!=expected:
                    failures.append(["COMPOSITION_LAW",rho,sigma,tau,got,expected])
                table[(rho,sigma,tau)]=got

    # Frozen neutral transport test: a full U+bridge step must preserve directional FORCE to pass BA1-A.
    neutral={a:table[(a,"TOP","TOP")] for a in STATES}
    if neutral["FORCE_0"]!=neutral["FORCE_1"]:
        failures.append(["EXPECTED_DIRECTION_ERASURE_NOT_REPRODUCED",neutral])
    if neutral["FORCE_0"]!="TOP" or neutral["FORCE_1"]!="TOP":
        failures.append(["NEUTRAL_OUTPUT_DRIFT",neutral])

    future_sig={a:[table[(a,"TOP",tau)] for tau in STATES] for a in STATES}
    if future_sig["FORCE_0"]!=future_sig["FORCE_1"]:
        failures.append(["FUTURE_SIGNATURES_FORCE_DISTINCT_UNEXPECTED",future_sig])
    directional_classes=len({tuple(future_sig[s]) for s in ("TOP","FORCE_0","FORCE_1")})
    if directional_classes!=1:
        failures.append(["DIRECTIONAL_CLASS_COUNT",directional_classes])

    # Recompute generic constructive-return prototypes: no-BOTTOM payloads are always SAT.
    required={(0,1),(1,1)}
    if not required.issubset(set(first.keys())):
        failures.append(["RECONSTRUCTION_PROTOTYPES_MISSING",sorted(required-set(first.keys()))])
    else:
        for pair in sorted(required):
            a=first[pair]
            if not ba0.eval_formula(U,a):
                failures.append(["PROTOTYPE_NOT_U_MODEL",pair])
            if (int(a[2]),int(a[30]))!=pair:
                failures.append(["PROTOTYPE_ENDPOINT_DRIFT",pair])

    # Result claims must match the independent local proof, with no finite-g ladder.
    if r.get("outcome")!="BA1-D_UNARY_PAYLOAD_TOO_WEAK":
        failures.append(["OUTCOME",r.get("outcome")])
    if r.get("finite_g_ladder_replayed") is not False:
        failures.append("FINITE_G_LADDER_REPLAYED")
    if r.get("arbitrary_CNF_coverage_started") is not False:
        failures.append("ARBITRARY_CNF_STARTED")
    if r.get("BA1_1_distinguishability",{}).get("N_local_injected_boundary")!=4:
        failures.append("LOCAL_N_RESULT_DRIFT")
    if r.get("BA1_3_generalized_pi",{}).get("status")!="FAIL_DIRECTIONAL_RESIDUAL_ERASURE":
        failures.append("PI_STATUS_DRIFT")
    if r.get("BA1_4_generic_composition",{}).get("closure") is not True:
        failures.append("COMPOSITION_CLOSURE_RESULT_DRIFT")
    if r.get("BA1_4_generic_composition",{}).get("directional_information_preserved") is not False:
        failures.append("DIRECTIONAL_PRESERVATION_RESULT_DRIFT")
    if r.get("BA1_6_unsat_capability",{}).get("nontrivial_propagated_contradiction",{}).get("exists_under_valid_single_payload_per_cut_syntax") is not False:
        failures.append("NONTRIVIAL_UNSAT_RESULT_DRIFT")
    if r.get("BA1_7_size_time",{}).get("polynomiality_for_fixed_unary_alphabet") is not True:
        failures.append("POLYNOMIALITY_RESULT_DRIFT")
    if r.get("BA1_8_information_accounting",{}).get("directional_constraint_classes_among_TOP_FORCE0_FORCE1")!=1:
        failures.append("DIRECTIONAL_CLASS_RESULT_DRIFT")
    if "F3_DIRECTIONAL_RESIDUAL_REQUIREMENT_ERASED_BY_ONE_FULL_COMPOSITION" not in r.get("falsifiers",[]):
        failures.append("F3_NOT_RECORDED")
    if "F8_NO_NONTRIVIAL_PROPAGATED_CONTRADICTION__BOTTOM_ONLY_UNSAT_CLASS" not in r.get("falsifiers",[]):
        failures.append("F8_NOT_RECORDED")
    if r.get("smallest_falsifier",{}).get("outputs")!={"FORCE_0":"TOP","FORCE_1":"TOP"}:
        failures.append(["SMALLEST_FALSIFIER_DRIFT",r.get("smallest_falsifier")])
    if r.get("AZ_modified") is not False or r.get("BA0_modified") is not False:
        failures.append("ANCESTOR_MUTATION_FLAG")
    if r.get("firewall")!={"P_VS_NP":"OPEN","SAT_IN_P":"NOT_PROVED","TRUMP_finished":False}:
        failures.append("FIREWALL_DRIFT")

    out={
        "gate":"R50G25BA1_MINIMAL_NONTRIVIAL_SEMANTIC_PAYLOAD_TRANSPORT",
        "status":"PASS" if not failures else "FAIL",
        "failure_count":len(failures),
        "failures":failures,
        "independent_endpoint_pair_counts":{str(k):int(v) for k,v in sorted(counts.items())},
        "independent_local_state_signatures":sig,
        "independent_neutral_transport":neutral,
        "independent_future_tau_signatures":future_sig,
        "independent_directional_class_count":directional_classes,
        "finite_g_ladder_replayed":False,
        "arbitrary_CNF_coverage_started":False,
        "verdict":"BA1-D_UNARY_PAYLOAD_TOO_WEAK" if not failures else "VERIFY_FAILURE"
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"failures":len(failures),"neutral":neutral,"directional_classes":directional_classes},sort_keys=True))
    if failures:
        raise SystemExit(2)

if __name__=="__main__":
    main()
