#!/usr/bin/env python3
"""BABEL41 independent end-to-end positive/negative proof and tamper tests.

Includes legal connected non-U SCL9, connected unique SCL27, connected
balanced signed-flux SCL54, and genuine UNSAT DAG proof for 21-row system.
This does NOT estimate an unproved global polynomial runtime.
"""
import copy,itertools,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

from experiments.babel41.universal_exact_one import (
  ExactDecision,solve,affine9,fano,triple_fano
)
from experiments.babel41.verify_universal_proof import validate_result
from experiments.babel37.fourport_majority_falsifier import U,PORTS as POS
from experiments.babel40.signed_flux_arc_adversary import NEGATIVE_PORTS
from experiments.babel39.generic_scl_component_compiler import join_certificate


def expectation(rows,result,ground_truth):
    n=len(rows)
    if ground_truth:
        assert result["status"]=="SAT"
        assert result["witness"] in ground_truth
    else:
        assert result["status"]=="UNSAT"
    checked=validate_result(rows,result)
    if result["status"]=="SAT":
        assert checked["status"]=="SAT_CERTIFIED"
        assert result["witness"].bit_count()==n//3
    else:
        assert checked["status"].startswith("UNSAT_CERTIFIED")
    return checked


def assert_invalid(rows,bad):
    try:
        validate_result(rows,bad)
    except (AssertionError,ValueError,KeyError,TypeError):
        return
    raise AssertionError("Tampered fake proof was wrongly accepted")


def main():
    cases=[]
    # Exact semantics guard: never reinterpret malformed fractional/string/
    # boolean literals as integer variable indices.
    for invalid in (0.5,"0",True):
        broken=[list(row) for row in affine9()]
        broken[0][0]=invalid
        try:
            solve(broken)
        except (ValueError,TypeError):
            pass
        else:
            raise AssertionError(("lossy noninteger input accepted",invalid))
    a=affine9()
    assert len(a)==9
    oracle9={truth for truth in range(1<<9)
             if all(sum((truth>>v)&1 for v in row)==1 for row in a)}
    assert len(oracle9)==3
    sat9=solve(a)
    ack=expectation(a,sat9,oracle9)
    cases.append({"case":"CONNECTED_AFFINE9",
                  "answer":sat9["status"],"independent_models":len(oracle9),
                  "independent_proof":ack["status"],
                  "expanded_nodes":sat9.get("states_examined")})
    fake=copy.deepcopy(sat9)
    fake["witness"]^=1
    assert_invalid(a,fake)

    f=fano()
    fresult=solve(f)
    ack=expectation(f,fresult,set())
    assert fresult["certificate"]["type"]=="DIVISIBILITY"
    cases.append({"case":"FANO7_DIVISIBILITY_UNSAT",
                  "answer":"UNSAT","independent_proof":ack["status"]})

    u=U
    from experiments.babel32.rational_kernel_gate import solve_rational
    rational=solve_rational(u)
    assert rational["status"]=="SAT" and rational["exact_sat_count"]==1
    model=sum(1<<j for j in rational["witness_ones"])
    us=solve(u)
    ack=expectation(u,us,{model})
    cases.append({"case":"CONNECTED_U27_UNIQUE_SAT",
                  "answer":"SAT","independent_model_count":1,
                  "independent_proof":ack["status"],
                  "expanded_nodes":us.get("states_examined")})

    signed={"components":[{"rows":U,"ports":POS},
                          {"rows":U,"ports":NEGATIVE_PORTS}],
            "edges":[(0,j,1,j) for j in range(4)]}
    signedrows,_=join_certificate(signed["components"],signed["edges"])
    expected=sum(1<<j for j in (0,2,3,7,9,13,17,19,23,24,
                                  30,34,36,40,44,46,50,51))
    signedres=solve(signedrows)
    ack=expectation(signedrows,signedres,{expected})
    cases.append({"case":"CONNECTED_SIGNED_FLUX_SCL54",
                  "answer":"SAT","exact_original_witness":True,
                  "expanded_nodes":signedres.get("states_examined"),
                  "independent_proof":ack["status"]})

    # Unlike Fano7, 3 disjoint Fano blocks have n=21 DIVISIBLE BY THREE:
    # divisibility alone cannot certify UNSAT; full proof DAG is mandatory.
    bad=triple_fano()
    unsat=solve(bad)
    ack=expectation(bad,unsat,set())
    assert unsat["certificate"]["type"]=="COMPLETE_EXACT_ONE_REFUTATION"
    assert ack["complete_verified_states"]>0
    cases.append({"case":"TRIPLE_FANO21_DIVISIBLE_BY3_UNSAT",
                  "answer":"UNSAT","independent_proof":ack["status"],
                  "complete_exhaustive_DAG_states":ack["complete_verified_states"],
                  "branch_states":ack["branch_states"],
                  "conflict_states":ack["contradiction_states"]})
    fake=copy.deepcopy(unsat)
    fake["certificate"]["rows_sha256"]="0"*64
    assert_invalid(bad,fake)
    fake=copy.deepcopy(unsat)
    branch=next((k for k,v in fake["certificate"]["nodes"].items()
                 if v["type"]=="BRANCH"),None)
    assert branch is not None
    fake["certificate"]["nodes"][branch]["children"].pop()
    assert_invalid(bad,fake)
    fake=copy.deepcopy(unsat)
    leaf=next(k for k,v in fake["certificate"]["nodes"].items()
              if v["type"]=="CONFLICT")
    fake["certificate"]["nodes"][leaf]={"type":"BRANCH","row":0,"children":[]}
    assert_invalid(bad,fake)

    # FALSIFIER of polynomial time for THIS DPLL search strategy:
    # t disjoint satisfiable affine9 components (3 models each) before an
    # impossible 21-row triple-Fano tail. n=9t+21 is always divisible by3.
    # On this ordered disconnected family, exhaustive refutation must visit
    # distinct states corresponding to all 3^t affine prefix models.
    # This is NOT a lower bound for all algorithms or CONNECTED SCL.
    growth=[]
    for t in (1,2,3):
        prefix=tuple(tuple(9*b+j for j in row)
                     for b in range(t) for row in a)
        tail=tuple(tuple(9*t+j for j in row) for row in bad)
        composite=prefix+tail
        total=solve(composite)
        audited=expectation(composite,total,set())
        assert total["certificate"]["type"]=="COMPLETE_EXACT_ONE_REFUTATION"
        exact_expected=(3**(t+2)-1)//2
        assert audited["complete_verified_states"]==exact_expected,(
            t,audited["complete_verified_states"],exact_expected)
        growth.append({"affine9_sat_prefix_blocks":t,
                       "n":len(composite),
                       "at_least_exhaustive_states":3**t,
                       "actual_exhaustive_proof_nodes":
                          audited["complete_verified_states"],
                       "independent_unsat_receipt":"PASS"})
    cases.extend({"case":"EXPONENTIAL_ORDERED_DISJOINT_LOWER_BOUND",
                  **entry} for entry in growth)

    print(json.dumps({
      "gate":"BABEL41_UNIVERSAL_TOTAL_SCL_EXACT_SAT_UNSAT",
      "ALL_LEGAL_SCL": "SAT_OR_UNSAT_NEVER_UNKNOWN",
      "unsat_certificate":"COMPLETE_EXACT_ROW_BRANCH_DAG",
      "independent_refutation_checker":"PASS",
      "independent_actual_SAT_witness_checker":"PASS",
      "tampered_unsat_and_sat_certificates_rejected":"PASS",
      "worst_case_time_bound":"poly(n) * 3^(n/3)",
      "polynomial_runtime_for_ALL_SCL":"NOT_PROVED",
      "P_vs_NP":"OPEN",
      "controls":cases
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
