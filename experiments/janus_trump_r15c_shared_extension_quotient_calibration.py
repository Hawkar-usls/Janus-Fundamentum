#!/usr/bin/env python3
"""R15C: shared extension-atom quotient + minimal width3 basis calibration.

This is still exposed W05 calibration.  The candidate has no truth access.  It
reuses one canonical OR atom for identical signed-literal pairs and performs
exact clause subsumption after each original-variable elimination.
"""
from __future__ import annotations

import argparse
import inspect
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import janus_trump_r13_unseen_interface_generalization as r13
import janus_trump_r15b_factored_dp_extension_compiler_calibration as r15b

WORLD_ID=r15b.WORLD_ID
EXPECTED_FRAME_SHA=r15b.EXPECTED_FRAME_SHA
WALL_SECONDS=r15b.WALL_SECONDS
MAX_PAIR_ATTEMPTS=r15b.MAX_PAIR_ATTEMPTS
MAX_ACTIVE_CLAUSES=r15b.MAX_ACTIVE_CLAUSES
MAX_AUXILIARIES=r15b.MAX_AUXILIARIES


def canon_clause(lits):
    return r15b.canon_clause(lits)


def pair_key(a,b):
    return tuple(sorted((int(a),int(b)),key=lambda x:(abs(x),x<0)))


def minimize_width3_basis(clauses):
    cs=set()
    for c in clauses:
        cc=canon_clause(c)
        if cc is not None:
            if len(cc)>3: raise AssertionError("physical clause width >3")
            cs.add(cc)
    if () in cs: return {()}
    units={c for c in cs if len(c)==1}
    unit_lits={c[0] for c in units}
    bins=set()
    for c in cs:
        if len(c)!=2: continue
        if any(l in unit_lits for l in c): continue
        bins.add(c)
    ters=set()
    for c in cs:
        if len(c)!=3: continue
        if any(l in unit_lits for l in c): continue
        if any(pair_key(*p) in bins for p in itertools.combinations(c,2)): continue
        ters.add(c)
    return units|bins|ters


def pair_frequencies(wide):
    freq=Counter()
    for c in wide:
        for p in itertools.combinations(c,2): freq[pair_key(*p)]+=1
    return freq


def factor_batch_shared(wide,atom_cache,next_aux):
    freq=pair_frequencies(wide)
    clauses=[]; created=0; reused=0
    for c in sorted(wide,key=lambda x:(len(x),x)):
        pairs=[pair_key(*p) for p in itertools.combinations(c,2)]
        existing=[p for p in pairs if p in atom_cache]
        if existing:
            chosen=min(existing,key=lambda p:(-freq[p],tuple((abs(x),x<0) for x in p)))
            a=atom_cache[chosen]; reused+=1
        else:
            chosen=min(pairs,key=lambda p:(-freq[p],tuple((abs(x),x<0) for x in p)))
            a=next_aux; next_aux+=1; atom_cache[chosen]=a; created+=1
            l1,l2=chosen
            clauses.extend((canon_clause((-a,l1,l2)),canon_clause((a,-l1)),canon_clause((a,-l2))))
        residual=list(c)
        residual.remove(chosen[0]); residual.remove(chosen[1])
        clauses.append(canon_clause((a,residual[0],residual[1])))
    return [c for c in clauses if c is not None],next_aux,{"new_atoms":created,"reuse_hits":reused,"unique_pair_atoms_total":len(atom_cache),"wide_resolvents":len(wide)}


def choose_internal_var(formula,internal):
    return r15b.choose_internal_var(formula,internal)


def resolve_on(p,n,var):
    return r15b.resolve_on(p,n,var)


def candidate_firewall():
    funcs=[pair_key,minimize_width3_basis,pair_frequencies,factor_batch_shared,compile_shared_projection]
    src="\n".join(inspect.getsource(f) for f in funcs)
    forbidden=["dpll(","shadow_exact_interface","range(1 <<","MISSING_PRIME","FALSE_POSITIVE","exact_search_witness","robdd("]
    hits=[x for x in forbidden if x in src]
    return {"pass":not hits,"forbidden_hits":hits}


def compile_shared_projection(frame,bridge,wall_seconds=WALL_SECONDS):
    started=time.time()
    formula=minimize_width3_basis(frame)
    orig=r15b.original_vars(frame); bridge_set=set(bridge); internal=set(orig)-bridge_set
    next_aux=max(orig,default=0)+1; first_aux=next_aux
    atom_cache={}; pair_attempts=0; history=[]
    total_reuse=0; total_new_atoms=0; total_dominated=0
    while internal:
        aux_count=next_aux-first_aux
        if time.time()-started>wall_seconds or pair_attempts>MAX_PAIR_ATTEMPTS or len(formula)>MAX_ACTIVE_CLAUSES or aux_count>MAX_AUXILIARIES:
            return {"status":"OPEN_RESOURCE_LIMIT","reason":"FROZEN_RESOURCE_ENVELOPE","elapsed_seconds":time.time()-started,"pair_attempts":pair_attempts,"active_clauses":len(formula),"auxiliary_variables":aux_count,"shared_pair_atoms":len(atom_cache),"atom_reuse_hits":total_reuse,"remaining_internal":len(internal),"history":history,"max_clause_width":max(map(len,formula),default=0)}
        _,_,var,pos_count,neg_count=choose_internal_var(formula,internal)
        pos=[c for c in formula if var in c]; neg=[c for c in formula if -var in c]
        rest={c for c in formula if var not in c and -var not in c}
        direct_res=set(); wide=set(); taut=0
        for p in pos:
            for n in neg:
                pair_attempts+=1
                if pair_attempts>MAX_PAIR_ATTEMPTS:
                    return {"status":"OPEN_RESOURCE_LIMIT","reason":"PAIR_ATTEMPT_CAP","elapsed_seconds":time.time()-started,"pair_attempts":pair_attempts,"active_clauses":len(formula),"auxiliary_variables":next_aux-first_aux,"shared_pair_atoms":len(atom_cache),"atom_reuse_hits":total_reuse,"remaining_internal":len(internal),"history":history,"max_clause_width":max(map(len,formula),default=0)}
                r=resolve_on(p,n,var)
                if r is None: taut+=1; continue
                if len(r)<=3: direct_res.add(r)
                elif len(r)==4: wide.add(r)
                else: return {"status":"FAIL_INTEGRITY","reason":"RESOLVENT_WIDTH_GT4","bad_width":len(r),"history":history}
        factored,next_aux,fstats=factor_batch_shared(wide,atom_cache,next_aux)
        before_min=len(rest)+len(direct_res)+len(factored)
        formula=minimize_width3_basis(set(rest)|direct_res|set(factored))
        dominated=max(0,before_min-len(formula)); total_dominated+=dominated
        total_reuse+=fstats["reuse_hits"]; total_new_atoms+=fstats["new_atoms"]
        internal.remove(var)
        history.append({"eliminated_var":var,"before_pos":pos_count,"before_neg":neg_count,"pair_attempts_step":pos_count*neg_count,"direct_resolvents":len(direct_res),"wide_resolvents":len(wide),"new_shared_atoms":fstats["new_atoms"],"atom_reuse_hits":fstats["reuse_hits"],"dominated_or_duplicate_removed":dominated,"after_clauses":len(formula),"remaining_internal":len(internal)})
        if () in formula:
            return {"status":"COMPLETE_UNSAT_INTERFACE","reason":"EMPTY_CLAUSE_DERIVED","elapsed_seconds":time.time()-started,"pair_attempts":pair_attempts,"active_clauses":1,"auxiliary_variables":next_aux-first_aux,"shared_pair_atoms":len(atom_cache),"atom_reuse_hits":total_reuse,"dominated_removed":total_dominated,"remaining_internal":0,"formula":[[]],"history":history,"max_clause_width":0}
    maxw=max(map(len,formula),default=0)
    if any(abs(l) in (orig-bridge_set) for c in formula for l in c) or maxw>3:
        return {"status":"FAIL_INTEGRITY","reason":"POSTCONDITION_FAIL","history":history,"max_clause_width":maxw}
    return {"status":"COMPLETE_EXTENDED_INTERFACE","reason":"ALL_ORIGINAL_INTERNAL_VARIABLES_ELIMINATED","elapsed_seconds":time.time()-started,"pair_attempts":pair_attempts,"active_clauses":len(formula),"auxiliary_variables":next_aux-first_aux,"shared_pair_atoms":len(atom_cache),"atom_reuse_hits":total_reuse,"new_atom_creations":total_new_atoms,"dominated_removed":total_dominated,"remaining_internal":0,"formula":[list(c) for c in sorted(formula,key=lambda c:(len(c),c))],"history":history,"max_clause_width":maxw}


def tiny_shared_control():
    frame=((1,2,3),(-1,4,5)); bridge=(2,3,4,5)
    c=compile_shared_projection(frame,bridge,wall_seconds=30)
    if c["status"]!="COMPLETE_EXTENDED_INTERFACE": return False
    for mask in range(16):
        ba={bridge[i]:bool((mask>>i)&1) for i in range(4)}
        exact=False
        for xv in (False,True):
            a=dict(ba); a[1]=xv
            if all(any((a[abs(l)] if l>0 else not a[abs(l)]) for l in cl) for cl in frame): exact=True
        out=r15b.direct.dpll(r15b.restrict_formula(c["formula"],ba))
        if bool(out["sat"])!=exact: return False
    return True


def run():
    freeze=r13.load_freeze(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID); world=r13.generate_world(spec)
    if world["source"]["frame_sha256"]!=EXPECTED_FRAME_SHA: raise AssertionError("W05 frame drift")
    firewall=candidate_firewall(); tiny=tiny_shared_control()
    candidate=compile_shared_projection(world["frame"],tuple(world["bridge"]))
    control=r15b.post_candidate_control(candidate,world["frame"],tuple(world["bridge"])) if candidate["status"].startswith("COMPLETE") else {"not_run":True,"reason":"CANDIDATE_DID_NOT_COMPLETE"}
    if not firewall["pass"] or not tiny or candidate["status"]=="FAIL_INTEGRITY": verdict="FAIL_INTEGRITY"
    elif candidate["status"]=="OPEN_RESOURCE_LIMIT": verdict="OPEN_RESOURCE_LIMIT"
    elif control.get("mismatch_count",1)==0: verdict="CALIBRATION_PROJECTION_COMPLETE__CONTROL_MATCH"
    else: verdict="CALIBRATION_PROJECTION_COMPLETE__CONTROL_MISMATCH"
    gates={"G1_W05_FRAME_FROZEN":world["source"]["frame_sha256"]==EXPECTED_FRAME_SHA,"G2_CANDIDATE_FIREWALL":firewall["pass"],"G3_TINY_SHARED_PROJECTION_CONTROL":tiny,"G4_NO_WIDE_PHYSICAL_CLAUSES":candidate.get("max_clause_width",3)<=3,"G5_CONTROL_ONLY_AFTER_CANDIDATE":True,"G6_NO_GENERALIZATION_CLAIM":True}
    return {"schema":"JANUS/TRUMP/R15C/SHARED_EXTENSION_QUOTIENT_CALIBRATION/RESULT/v1.0","created_date":"2026-09-02","verdict":verdict,"candidate_firewall":firewall,"candidate":candidate,"post_candidate_control":control,"gates":gates,"scientific_interpretation":{"comparison_to_R15B":"Measure whether canonical shared OR atoms plus exact subsumption convert name debt into a smaller factored basis.","scope":"Exposed W05 calibration only; no unseen-world authority."},"seal":"SAME_SUBEXPRESSION__SAME_ATOM__SUPERSET_CLAUSE__NO_SECOND_STATE","P_VS_NP":"OPEN"}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args(); d=run(); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict":d["verdict"],"candidate":{k:v for k,v in d["candidate"].items() if k not in ("formula","history")},"control":{k:v for k,v in d["post_candidate_control"].items() if k!="rows"},"gates":d["gates"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True)); return 2 if d["verdict"]=="FAIL_INTEGRITY" else 0

if __name__=="__main__": raise SystemExit(main())
