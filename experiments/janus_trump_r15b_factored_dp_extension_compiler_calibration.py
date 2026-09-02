#!/usr/bin/env python3
"""R15B: direct-from-frame factored Davis-Putnam extension compiler calibration.

Candidate lane never sees the exact W05 interface. Original internal variables
are eliminated exactly. Every width-4 resolvent is replaced by a fresh
projection-equivalent width<=3 extension encoding; fresh auxiliaries remain
existential and are never eliminated. The output is K(B,A), not a same-variable
CNF interface. Resource exhaustion returns OPEN.
"""
from __future__ import annotations

import argparse
import inspect
import json
import time
from pathlib import Path

import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r10_exact_semantic_bridge_interface as r10
import janus_trump_r13_unseen_interface_generalization as r13

WORLD_ID="R13-W05"
EXPECTED_FRAME_SHA="84fa0fbdd127b1c73f3c8ef6820a0d0cdf154093750ed9c600289fce4b6aae88"
EXPECTED_TRUTH_SHA="acf8828272994c0ad05a44590aa4335e1828d5b7d3e3d4f438b0d497cfcad92f"
FROZEN_OLD_FALSE_POSITIVES=(32050,32546,32562,65328,65332)
WALL_SECONDS=600
MAX_PAIR_ATTEMPTS=30_000_000
MAX_ACTIVE_CLAUSES=150_000
MAX_AUXILIARIES=100_000


def canon_clause(lits):
    s=set(int(x) for x in lits)
    if 0 in s: raise ValueError("literal zero")
    if any(-x in s for x in s): return None
    return tuple(sorted(s,key=lambda x:(abs(x),x<0)))


def resolve_on(p,n,var):
    if var not in p or -var not in n: raise ValueError("bad pivot orientation")
    return canon_clause([x for x in p if x!=var]+[x for x in n if x!=-var])


def factor_width4(clause,next_aux):
    c=canon_clause(clause)
    if c is None or len(c)!=4: raise ValueError("factor_width4 requires one non-tautological width4 clause")
    a=int(next_aux)
    l1,l2,l3,l4=c
    # a <-> (l1 OR l2), then assert (a OR l3 OR l4).
    enc=(
        canon_clause((-a,l1,l2)),
        canon_clause((a,-l1)),
        canon_clause((a,-l2)),
        canon_clause((a,l3,l4)),
    )
    assert all(x is not None and len(x)<=3 for x in enc)
    return enc,a,next_aux+1


def normalize_formula(clauses):
    out=set()
    for c in clauses:
        cc=canon_clause(c)
        if cc is not None: out.add(cc)
    return out


def original_vars(frame):
    return {abs(l) for c in frame for l in c}


def choose_internal_var(formula,internal):
    best=None
    for v in sorted(internal):
        pos=sum(1 for c in formula if v in c)
        neg=sum(1 for c in formula if -v in c)
        score=pos*neg
        item=(score,pos+neg,v,pos,neg)
        if best is None or item<best: best=item
    return best


def candidate_firewall():
    funcs=[canon_clause,resolve_on,factor_width4,normalize_formula,choose_internal_var,compile_factored_projection]
    src="\n".join(inspect.getsource(f) for f in funcs)
    forbidden=["dpll(","shadow_exact_interface","range(1 <<","exact_search_witness","robdd(","MISSING_PRIME","FALSE_POSITIVE"]
    hits=[x for x in forbidden if x in src]
    return {"pass":not hits,"forbidden_hits":hits}


def compile_factored_projection(frame,bridge):
    started=time.time()
    formula=normalize_formula(frame)
    orig=original_vars(frame)
    bridge_set=set(bridge)
    internal=set(orig)-bridge_set
    next_aux=max(orig,default=0)+1
    first_aux=next_aux
    pair_attempts=0
    history=[]
    integrity=True

    if max((len(c) for c in formula),default=0)>3:
        return {"status":"FAIL_INTEGRITY","reason":"INPUT_WIDTH_GT3","history":history}

    while internal:
        elapsed=time.time()-started
        aux_count=next_aux-first_aux
        if elapsed>WALL_SECONDS or pair_attempts>MAX_PAIR_ATTEMPTS or len(formula)>MAX_ACTIVE_CLAUSES or aux_count>MAX_AUXILIARIES:
            return {"status":"OPEN_RESOURCE_LIMIT","reason":"FROZEN_RESOURCE_ENVELOPE","elapsed_seconds":elapsed,"pair_attempts":pair_attempts,"active_clauses":len(formula),"auxiliary_variables":aux_count,"remaining_internal":len(internal),"history":history}

        choice=choose_internal_var(formula,internal)
        _,_,var,pos_count,neg_count=choice
        pos=[c for c in formula if var in c]
        neg=[c for c in formula if -var in c]
        rest={c for c in formula if var not in c and -var not in c}
        direct_res=set(); wide=set(); taut=0
        for p in pos:
            for n in neg:
                pair_attempts+=1
                if pair_attempts>MAX_PAIR_ATTEMPTS:
                    return {"status":"OPEN_RESOURCE_LIMIT","reason":"PAIR_ATTEMPT_CAP","elapsed_seconds":time.time()-started,"pair_attempts":pair_attempts,"active_clauses":len(formula),"auxiliary_variables":next_aux-first_aux,"remaining_internal":len(internal),"history":history}
                r=resolve_on(p,n,var)
                if r is None:
                    taut+=1; continue
                if len(r)<=3: direct_res.add(r)
                elif len(r)==4: wide.add(r)
                else:
                    integrity=False
                    return {"status":"FAIL_INTEGRITY","reason":"RESOLVENT_WIDTH_GT4_FROM_WIDTH3_PARENTS","bad_width":len(r),"history":history}
        new_formula=set(rest)|direct_res
        aux_before=next_aux
        for r in sorted(wide,key=lambda c:(len(c),c)):
            enc,_,next_aux=factor_width4(r,next_aux)
            new_formula.update(enc)
            if next_aux-first_aux>MAX_AUXILIARIES:
                return {"status":"OPEN_RESOURCE_LIMIT","reason":"AUXILIARY_CAP","elapsed_seconds":time.time()-started,"pair_attempts":pair_attempts,"active_clauses":len(new_formula),"auxiliary_variables":next_aux-first_aux,"remaining_internal":len(internal),"history":history}
        formula=normalize_formula(new_formula)
        internal.remove(var)
        history.append({
            "eliminated_var":var,"before_pos":pos_count,"before_neg":neg_count,
            "pair_attempts_step":pos_count*neg_count,"tautologies":taut,
            "direct_resolvents":len(direct_res),"factored_width4_resolvents":len(wide),
            "aux_created":next_aux-aux_before,"after_clauses":len(formula),
            "remaining_internal":len(internal)
        })
        if () in formula:
            return {"status":"COMPLETE_UNSAT_INTERFACE","reason":"EMPTY_CLAUSE_DERIVED","elapsed_seconds":time.time()-started,"pair_attempts":pair_attempts,"active_clauses":1,"auxiliary_variables":next_aux-first_aux,"remaining_internal":0,"formula":[[]],"history":history,"max_clause_width":0}

    if any(abs(l) in (orig-bridge_set) for c in formula for l in c):
        integrity=False
    maxw=max((len(c) for c in formula),default=0)
    status="COMPLETE_EXTENDED_INTERFACE" if integrity and maxw<=3 else "FAIL_INTEGRITY"
    return {"status":status,"reason":"ALL_ORIGINAL_INTERNAL_VARIABLES_ELIMINATED" if status.startswith("COMPLETE") else "POSTCONDITION_FAIL","elapsed_seconds":time.time()-started,"pair_attempts":pair_attempts,"active_clauses":len(formula),"auxiliary_variables":next_aux-first_aux,"remaining_internal":0,"formula":[list(c) for c in sorted(formula,key=lambda c:(len(c),c))],"history":history,"max_clause_width":maxw}


def restrict_formula(formula,assign):
    cnf=tuple(tuple(c) for c in formula)
    for var,value in assign.items():
        cnf=direct.restrict_cnf(cnf,var,value)
    return cnf


def post_candidate_control(candidate,frame,bridge):
    shadow=r10.shadow_exact_interface(frame,bridge)
    if shadow["truth_table_sha256"]!=EXPECTED_TRUTH_SHA: raise AssertionError("W05 truth drift")
    exact=set(shadow["allowed_masks"])
    disallowed=[m for m in range(1<<len(bridge)) if m not in exact and m not in FROZEN_OLD_FALSE_POSITIVES]
    panel=list(FROZEN_OLD_FALSE_POSITIVES)+sorted(exact)[:16]+disallowed[:16]
    rows=[]; mismatches=[]; total_work=0
    for mask in panel:
        assignment=r10.mask_assignment(bridge,mask)
        restricted=restrict_formula(candidate["formula"],assignment)
        out=direct.dpll(restricted)
        total_work+=int(out.get("work",0))
        if out["status"]!="EXACT": raise AssertionError("control DPLL non-exact")
        got=bool(out["sat"]); want=mask in exact
        row={"mask":mask,"expected":want,"candidate_exists_aux":got,"match":got==want,"work":int(out.get("work",0))}
        rows.append(row)
        if not row["match"]: mismatches.append(row)
    return {"truth_table_sha256":shadow["truth_table_sha256"],"panel_size":len(panel),"mismatch_count":len(mismatches),"mismatches":mismatches,"rows":rows,"dpll_work":total_work}


def tiny_projection_control():
    # F=(x OR b1 OR b2) AND (~x OR b3 OR b4); eliminate x creates width4.
    frame=((1,2,3),(-1,4,5)); bridge=(2,3,4,5)
    c=compile_factored_projection(frame,bridge)
    if c["status"]!="COMPLETE_EXTENDED_INTERFACE" or c["max_clause_width"]>3: return False
    for mask in range(16):
        ba={bridge[i]:bool((mask>>i)&1) for i in range(4)}
        # exact existential x
        exact=False
        for xv in (False,True):
            a=dict(ba); a[1]=xv
            if all(any((a[abs(l)] if l>0 else not a[abs(l)]) for l in cl) for cl in frame): exact=True
        out=direct.dpll(restrict_formula(c["formula"],ba))
        if bool(out["sat"])!=exact: return False
    return True


def run():
    freeze=r13.load_freeze(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID)
    world=r13.generate_world(spec)
    if world["source"]["frame_sha256"]!=EXPECTED_FRAME_SHA: raise AssertionError("W05 frame drift")
    firewall=candidate_firewall(); tiny=tiny_projection_control()
    candidate=compile_factored_projection(world["frame"],tuple(world["bridge"]))
    if candidate["status"].startswith("COMPLETE"):
        control=post_candidate_control(candidate,world["frame"],tuple(world["bridge"]))
    else:
        control={"not_run":True,"reason":"CANDIDATE_DID_NOT_COMPLETE"}
    if not firewall["pass"] or not tiny or candidate["status"]=="FAIL_INTEGRITY": verdict="FAIL_INTEGRITY"
    elif candidate["status"]=="OPEN_RESOURCE_LIMIT": verdict="OPEN_RESOURCE_LIMIT"
    elif control.get("mismatch_count",1)==0: verdict="CALIBRATION_PROJECTION_COMPLETE__CONTROL_MATCH"
    else: verdict="CALIBRATION_PROJECTION_COMPLETE__CONTROL_MISMATCH"
    gates={
        "G1_W05_FRAME_FROZEN":world["source"]["frame_sha256"]==EXPECTED_FRAME_SHA,
        "G2_CANDIDATE_FIREWALL":firewall["pass"],
        "G3_TINY_PROJECTION_CONTROL":tiny,
        "G4_NO_WIDE_PHYSICAL_CLAUSES":candidate.get("max_clause_width",3)<=3,
        "G5_CONTROL_ONLY_AFTER_CANDIDATE":True,
        "G6_NO_GENERALIZATION_CLAIM":True,
    }
    return {"schema":"JANUS/TRUMP/R15B/FACTORED_DP_EXTENSION_COMPILER_CALIBRATION/RESULT/v1.0","created_date":"2026-09-02","verdict":verdict,"candidate_firewall":firewall,"candidate":candidate,"post_candidate_control":control,"gates":gates,"scientific_interpretation":{"scope":"Exposed W05 calibration only.","if_complete":"A direct-from-frame exact projection can in principle carry widened resolvents through fresh existential extension atoms while keeping physical clause width<=3; scaling/auxiliary growth remain the next wall.","if_open":"Resource growth, not semantic width, is the observed wall for this candidate under the frozen envelope."},"seal":"FACTOR_THE_WIDE_CONSEQUENCE__ELIMINATE_THE_OLD_VARIABLE__NEVER_CALL_THE_FACTOR_A_PROOF_OF_SPEED","P_VS_NP":"OPEN"}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args()
    d=run(); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict":d["verdict"],"candidate":{k:v for k,v in d["candidate"].items() if k not in ("formula","history")},"control":{k:v for k,v in d["post_candidate_control"].items() if k not in ("rows",)},"gates":d["gates"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True))
    return 2 if d["verdict"]=="FAIL_INTEGRITY" else 0

if __name__=="__main__": raise SystemExit(main())
