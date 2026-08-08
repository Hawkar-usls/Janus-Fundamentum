from __future__ import annotations

import argparse
import copy
from pathlib import Path

import janus_c049_1_b5_4_corrected_discovery_phase_a_c047_handoff_verifier as base


def repair_b52(candidate: dict) -> dict:
    candidate["semantic_digest"] = base.dg(candidate["proof_payload"])
    return candidate


def repair_b54(candidate: dict) -> dict:
    candidate["semantic_digest"] = base.dg(candidate["proof_payload"])
    return candidate


def expect_reject(name: str, candidate: dict, spec: dict, b5_input: dict, phase_input: dict, b52: dict, r52: dict, r53: dict) -> None:
    try:
        base.verify(candidate, spec, b5_input, phase_input, b52, r52, r53)
    except Exception:
        print(name + " = REJECTED")
        return
    raise AssertionError(name + " survived")


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--spec",type=Path,required=True)
    p.add_argument("--base-b5-input",type=Path,required=True)
    p.add_argument("--base-phase-a-input",type=Path,required=True)
    p.add_argument("--base-b5-2b-candidate",type=Path,required=True)
    p.add_argument("--base-candidate",type=Path,required=True)
    p.add_argument("--open-b5-input",type=Path,required=True)
    p.add_argument("--open-phase-a-input",type=Path,required=True)
    p.add_argument("--open-b5-2b-candidate",type=Path,required=True)
    p.add_argument("--open-candidate",type=Path,required=True)
    p.add_argument("--b5-2b-admission",type=Path,required=True)
    p.add_argument("--b5-3-admission",type=Path,required=True)
    a=p.parse_args()

    spec=base.load(a.spec); bi=base.load(a.base_b5_input); ph=base.load(a.base_phase_a_input)
    b52=base.load(a.base_b5_2b_candidate); c=base.load(a.base_candidate)
    obi=base.load(a.open_b5_input); oph=base.load(a.open_phase_a_input); ob52=base.load(a.open_b5_2b_candidate); oc=base.load(a.open_candidate)
    r52=base.load(a.b5_2b_admission); r53=base.load(a.b5_3_admission)

    # Strengthened T08: upstream B5.2B cut-width tamper with repaired B5.2B digest.
    x=copy.deepcopy(b52)
    x["proof_payload"]["cut_certificates"][0]["width"]=999
    repair_b52(x)
    expect_reject("B5_4_T08_REPAIRED_B52_CUT_WIDTH",copy.deepcopy(c),spec,bi,ph,x,r52,r53)

    # Strengthened T09: upstream B5.2B cut-basis tamper with repaired B5.2B digest.
    x=copy.deepcopy(b52)
    x["proof_payload"]["cut_certificates"][0]["boundary_rref"]=[999]
    repair_b52(x)
    expect_reject("B5_4_T09_REPAIRED_B52_CUT_BASIS",copy.deepcopy(c),spec,bi,ph,x,r52,r53)

    # Strengthened T18: use the exact matching OPEN subject and only promote its C047 status.
    x=copy.deepcopy(oc)
    x["proof_payload"]["c047_status"]="SAT"
    repair_b54(x)
    expect_reject("B5_4_T18_MATCHED_OPEN_TO_SAT",x,spec,obi,oph,ob52,r52,r53)

    print("B5_4_SUBJECT_CORRECT_REPAIRED_DIGEST_HARDENING = PASS")
    print("STRENGTHENED_TAMPERS_REJECTED = 3/3")
    print("B5_COMPLETE = FALSE_PENDING_CONTRACT_COMPLETION_REVIEW")
    print("P_VS_NP = OPEN")

if __name__=="__main__": main()
