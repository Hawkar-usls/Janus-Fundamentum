#!/usr/bin/env python3
"""R15E2 finite post-terminal semantic control for frozen R15D candidate.

The full 2^16 shadow used by R15E was too expensive as a validator. R15E2 uses
five pre-exposed adversarial masks plus 32 precommitted hash-derived masks. The
candidate still runs first and unchanged. Only then are exact DPLL labels
computed independently on the original frame and candidate extended interface.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r10_exact_semantic_bridge_interface as r10
import janus_trump_r13_unseen_interface_generalization as r13
import janus_trump_r15b_factored_dp_extension_compiler_calibration as r15b
import janus_trump_r15d_bounded_observer_equivalent_refactor as r15d

WORLD_ID=r15b.WORLD_ID
FRAME_SHA=r15b.EXPECTED_FRAME_SHA
CANDIDATE_BLOB_SHA="e6def9fef656c8f1af1b9f245bc855081f13a586"
ADVERSARIAL=(32050,32546,32562,65328,65332)
HASH_COUNT=32


def panel_masks():
    out=list(ADVERSARIAL); seen=set(out); counter=0
    while len(out)<len(ADVERSARIAL)+HASH_COUNT:
        payload=f"{FRAME_SHA}:R15E2:{counter}".encode(); counter+=1
        value=int.from_bytes(hashlib.sha256(payload).digest()[:8],"big")%(1<<16)
        if value in seen: continue
        seen.add(value); out.append(value)
    return tuple(out)


def restrict(cnf,assignment):
    out=tuple(tuple(c) for c in cnf)
    for var,value in assignment.items(): out=direct.restrict_cnf(out,var,value)
    return out


def exact_exists(cnf,assignment):
    out=direct.dpll(restrict(cnf,assignment))
    if out["status"]!="EXACT": raise AssertionError("non-exact DPLL")
    return bool(out["sat"]),int(out.get("work",0))


def run():
    freeze=r13.load_freeze(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID); world=r13.generate_world(spec)
    if world["source"]["frame_sha256"]!=FRAME_SHA: raise AssertionError("W05 frame drift")
    bridge=tuple(world["bridge"])
    candidate=r15d.compile_observed(world["frame"],bridge)
    terminal=candidate["status"]=="COMPLETE_EXTENDED_INTERFACE" and candidate.get("checkpoint",{}).get("remaining_internal")==0
    rows=[]; mismatches=[]; original_work=0; candidate_work=0
    if terminal:
        for i,mask in enumerate(panel_masks()):
            assignment=r10.mask_assignment(bridge,mask)
            want,w1=exact_exists(world["frame"],assignment)
            got,w2=exact_exists(candidate["formula"],assignment)
            original_work+=w1; candidate_work+=w2
            row={"panel_index":i,"mask":mask,"source":"ADVERSARIAL_K4_FALSE_POSITIVE" if mask in ADVERSARIAL else "HASH_TRUTH_BLIND","original_exists":want,"candidate_exists_aux":got,"match":want==got,"original_dpll_work":w1,"candidate_dpll_work":w2}
            rows.append(row)
            if not row["match"]: mismatches.append(row)
            print(json.dumps({"R15E2_CONTROL":i+1,"mask":mask,"match":row["match"],"source":row["source"]},sort_keys=True),flush=True)
    verdict=("R15E2_CANDIDATE_NONTERMINAL" if not terminal else "R15E2_PANEL_MATCH" if not mismatches else "R15E2_PANEL_MISMATCH")
    gates={
        "G1_FRAME_FROZEN":world["source"]["frame_sha256"]==FRAME_SHA,
        "G2_PANEL_PRECOMMITTED":len(panel_masks())==37 and panel_masks()[:5]==ADVERSARIAL,
        "G3_CANDIDATE_TERMINAL_BEFORE_LABELS":terminal,
        "G4_NO_FULL_DOMAIN_CLAIM":True,
        "G5_NO_GENERALIZATION_CLAIM":True,
    }
    return {"schema":"JANUS/TRUMP/R15E2/TRUTH_BLIND_PANEL_SEMANTIC_CONTROL/RESULT/v1.0","created_date":"2026-09-02","verdict":verdict,"frozen_candidate":{"blob_sha":CANDIDATE_BLOB_SHA},"candidate":{k:v for k,v in candidate.items() if k not in ("formula","history")},"panel":{"size":len(rows),"mismatch_count":len(mismatches),"adversarial_count":len(ADVERSARIAL),"hash_truth_blind_count":HASH_COUNT,"original_dpll_work":original_work,"candidate_dpll_work":candidate_work,"rows":rows,"mismatches":mismatches},"gates":gates,"interpretation":{"match":"Finite exact panel evidence that the frozen candidate preserves W05 bridge semantics on all preregistered masks, including the five masks that defeated k4.","limit":"Not exhaustive full-domain equivalence; prospective unseen-world validation is still required."},"seal":"THE_JUDGE_DID_NOT_CHOOSE_THE_POINTS_AFTER_SEEING_THE_ANSWER","P_VS_NP":"OPEN"}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args(); d=run(); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict":d["verdict"],"panel_size":d["panel"]["size"],"mismatch_count":d["panel"]["mismatch_count"],"candidate":d["candidate"],"gates":d["gates"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True)); return 2 if d["verdict"]=="R15E2_INTEGRITY_FAIL" else 0

if __name__=="__main__": raise SystemExit(main())
