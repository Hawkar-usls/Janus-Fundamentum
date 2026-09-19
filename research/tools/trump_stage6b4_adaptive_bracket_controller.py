#!/usr/bin/env python3
"""Stage6B.4 deterministic certified bracket controller.

Pure orchestration/state machine. It has no scientific authority of its own and
never inspects solver internals. The only query rule is floor((L+U)/2).

A transition is accepted only when accompanied by an externally verified
authority receipt:
  SAT  -> verified witness size s <= selected k, updates U=min(U,s)
  UNSAT-> VeriPB-verified boundary UNSAT at selected k, updates L=k

Initial L=0 authority is the frozen Stage6A CERTIFIED_NOT_QHORN result.
Initial U comes only from the frozen Stage6B.3 verified witness result.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path

TARGETS=[1,2,3,4,5,6,7,9,10,11,12,13,14]
EXPECTED_U={1:24,2:31,3:25,4:28,5:21,6:26,7:22,9:31,10:31,11:31,12:31,13:31,14:31}


def b3_row(result,index):
    return next(r for r in result["rows"] if int(r["index"])==index)


def init_state(stage6a,stage6b3,index):
    total=stage6a["verdict_summary"]["total"]
    if int(total.get("CERTIFIED_NOT_QHORN",0)) != 13:
        raise ValueError("Stage6A frozen negative authority not 13/13")
    row=b3_row(stage6b3,index)
    u=int(row["VERIFIED_DELETION_QHORN_UPPER_BOUND"])
    if u != EXPECTED_U[index]:
        raise ValueError(f"Stage6B3 U mismatch index={index}: {u}")
    if row["final_B3_verdict"]!="VERIFIED_SMALLER_DELETION_QHORN_WITNESS":
        raise ValueError("initial U lacks frozen B3 witness authority")
    ia=row["independent_authority"]
    if not (ia and ia.get("PB_MODEL_REPLAY_VERIFIED") is True and ia.get("QHORN_WITNESS_REPLAY_VERIFIED") is True):
        raise ValueError("initial U lacks dual replay")
    state={
      "schema":"janus.trump.stage6b4.certified_bracket_state.v1",
      "index":index,
      "L":0,
      "U":u,
      "lower_authority":{
        "type":"STAGE6A_CERTIFIED_NOT_QHORN",
        "result_commit":"27676d521b57c113996c482726657abe1de5f34b",
        "boundary":0
      },
      "upper_authority":{
        "type":"STAGE6B3_VERIFIED_SMALLER_DELETION_QHORN_WITNESS",
        "result_commit":"9b71c8a9df811a3a6a93cd25a547000629b44be8",
        "witness_size":u,
        "witness_sha256":ia["decoded_candidate_B_sha256"],
        "qhorn_certificate_sha256":ia["qhorn_weights_sha256"],
        "terminal_object_sha256":ia["terminal_object_sha256"],
        "PB_model_stdout_sha256":row["proof_producer"]["model_stdout_sha256"],
        "canonical_cnf_sha256":row["canonical_cnf_sha256"],
        "raw_cnf_sha256":row["raw_cnf_sha256"]
      },
      "round":0,
      "trace":[],
      "closed":False,
      "final_outcome":None
    }
    audit_invariant(state)
    if state["U"]==1:
        close_exact(state)
    return state


def audit_invariant(state):
    L=int(state["L"]); U=int(state["U"])
    if not (0 <= L < U):
        raise ValueError(f"invalid bracket {L},{U}")
    lower=state.get("lower_authority")
    upper=state.get("upper_authority")
    if not lower or not upper:
        raise ValueError("missing bracket authority")
    if L==0:
        if lower.get("type")!="STAGE6A_CERTIFIED_NOT_QHORN":
            raise ValueError("L=0 must use Stage6A authority")
    else:
        if lower.get("type")!="VERIPB_VERIFIED_BOUNDARY_UNSAT" or int(lower.get("boundary",-1))!=L:
            raise ValueError("positive L lacks matching VeriPB authority")
    if int(upper.get("witness_size",-1))!=U:
        raise ValueError("U lacks matching witness authority")
    return True


def next_k(state):
    audit_invariant(state)
    if state["U"]==state["L"]+1:
        return None
    return (int(state["L"])+int(state["U"]))//2


def close_exact(state):
    audit_invariant(state)
    if state["U"]!=state["L"]+1:
        raise ValueError("cannot close non-adjacent bracket")
    state["closed"]=True
    state["final_outcome"]="EXACT_DELETION_QHORN_DISTANCE_VERIFIED"
    state["exact_distance"]=int(state["U"])


def apply_sat(state,selected_k,receipt):
    if selected_k != next_k(state):
        raise ValueError("SAT transition k violates frozen selection rule")
    if receipt.get("PB_MODEL_REPLAY_VERIFIED") is not True:
        raise ValueError("SAT transition lacks PB model authority")
    if receipt.get("QHORN_WITNESS_REPLAY_VERIFIED") is not True:
        raise ValueError("SAT transition lacks q-Horn replay authority")
    if receipt.get("terminal_replay_verified") is not True:
        raise ValueError("SAT transition lacks polynomial terminal authority")
    s=int(receipt["decoded_B_size"])
    if s>selected_k:
        raise ValueError("verified witness exceeds selected k")
    before={"L":state["L"],"U":state["U"]}
    state["U"]=min(int(state["U"]),s)
    state["upper_authority"]={
      "type":"STAGE6B4_VERIFIED_SAT_QHORN_WITNESS",
      "round":state["round"]+1,
      "selected_k":selected_k,
      "witness_size":s,
      "witness_sha256":receipt["decoded_B_sha256"],
      "qhorn_certificate_sha256":receipt["qhorn_weights_sha256"],
      "terminal_object_sha256":receipt["terminal_object_sha256"],
      "PB_model_replay_receipt_sha256":receipt["receipt_sha256"],
      "OPB_sha256":receipt["OPB_sha256"]
    }
    state["round"]+=1
    state["trace"].append({
      "round":state["round"],"L_before":before["L"],"U_before":before["U"],
      "selected_k":selected_k,"authority":"SAT","actual_B_size":s,
      "L_after":state["L"],"U_after":state["U"],
      "authority_receipt_sha256":receipt["receipt_sha256"]
    })
    audit_invariant(state)
    if state["U"]==state["L"]+1: close_exact(state)


def apply_unsat(state,selected_k,receipt):
    if selected_k != next_k(state):
        raise ValueError("UNSAT transition k violates frozen selection rule")
    if receipt.get("VERIPB_PRIMARY_raw_proof_verified")!="YES":
        raise ValueError("UNSAT transition lacks VeriPB proof authority")
    if receipt.get("VERIPB_CHECKER_REPORTED_CONCLUSION")!="UNSAT":
        raise ValueError("UNSAT transition lacks explicit UNSAT conclusion")
    if receipt.get("VERIPB_CONCLUSION_SECTION_VALID") is not True:
        raise ValueError("UNSAT transition lacks valid conclusion section")
    before={"L":state["L"],"U":state["U"]}
    state["L"]=selected_k
    state["lower_authority"]={
      "type":"VERIPB_VERIFIED_BOUNDARY_UNSAT",
      "round":state["round"]+1,
      "boundary":selected_k,
      "OPB_sha256":receipt["OPB_sha256"],
      "raw_proof_sha256":receipt["raw_proof_sha256"],
      "VeriPB_receipt_sha256":receipt["receipt_sha256"],
      "kernel_proof_sha256":receipt.get("kernel_proof_sha256"),
      "CakePB_status":receipt.get("CakePB_status")
    }
    state["round"]+=1
    state["trace"].append({
      "round":state["round"],"L_before":before["L"],"U_before":before["U"],
      "selected_k":selected_k,"authority":"UNSAT",
      "L_after":state["L"],"U_after":state["U"],
      "authority_receipt_sha256":receipt["receipt_sha256"]
    })
    audit_invariant(state)
    if state["U"]==state["L"]+1: close_exact(state)


def stop_non_authority(state,outcome,detail=None):
    allowed={
      "TARGET_EXACTNESS_UNKNOWN_RESOURCE_LIMIT",
      "UNVERIFIED_UNSAT_NO_AUTHORITY",
      "FAIL_UNSAT_CERTIFICATE",
      "UNKNOWN_PROOF_CHECK_RESOURCE_LIMIT",
      "INFRASTRUCTURE_ERROR",
      "SCIENTIFIC_AUTHORITY_CONFLICT"
    }
    if outcome not in allowed:
        raise ValueError(outcome)
    state["closed"]=True
    state["final_outcome"]=outcome
    if detail is not None: state["stop_detail"]=detail


def main():
    ap=argparse.ArgumentParser()
    sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("init")
    p.add_argument("stage6a"); p.add_argument("stage6b3"); p.add_argument("index",type=int); p.add_argument("output")
    p=sub.add_parser("next")
    p.add_argument("state")
    p=sub.add_parser("sat")
    p.add_argument("state"); p.add_argument("k",type=int); p.add_argument("receipt"); p.add_argument("output")
    p=sub.add_parser("unsat")
    p.add_argument("state"); p.add_argument("k",type=int); p.add_argument("receipt"); p.add_argument("output")
    p=sub.add_parser("stop")
    p.add_argument("state"); p.add_argument("outcome"); p.add_argument("output"); p.add_argument("--detail")
    ns=ap.parse_args()
    if ns.cmd=="init":
        a=json.loads(Path(ns.stage6a).read_text()); b=json.loads(Path(ns.stage6b3).read_text())
        s=init_state(a,b,ns.index); Path(ns.output).write_text(json.dumps(s,indent=2,sort_keys=True)+"\n")
    elif ns.cmd=="next":
        s=json.loads(Path(ns.state).read_text()); print("CLOSED" if s.get("closed") else next_k(s))
    else:
        s=json.loads(Path(ns.state).read_text())
        if ns.cmd=="sat":
            apply_sat(s,ns.k,json.loads(Path(ns.receipt).read_text()))
        elif ns.cmd=="unsat":
            apply_unsat(s,ns.k,json.loads(Path(ns.receipt).read_text()))
        else:
            stop_non_authority(s,ns.outcome,ns.detail)
        Path(ns.output).write_text(json.dumps(s,indent=2,sort_keys=True)+"\n")
        print(json.dumps({"index":s["index"],"L":s["L"],"U":s["U"],"closed":s["closed"],"outcome":s.get("final_outcome")},sort_keys=True))


if __name__=="__main__": main()
