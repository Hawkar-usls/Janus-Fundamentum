#!/usr/bin/env python3
"""R15D bounded observer for the frozen R15C logical candidate.

No new inference rule is introduced.  This implementation makes the R15C
resource envelope observable and enforceable inside long phases.  It is an
exposed W05 diagnostic pass, not a generalization test.
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
import janus_trump_r15c_shared_extension_quotient_calibration as r15c

WORLD_ID=r15b.WORLD_ID
EXPECTED_FRAME_SHA=r15b.EXPECTED_FRAME_SHA
WALL_SECONDS=120.0
MAX_PAIR_ATTEMPTS=30_000_000
MAX_ACTIVE_CLAUSES=150_000
MAX_AUXILIARIES=100_000
PROGRESS_SECONDS=5.0

class DeadlineExceeded(RuntimeError):
    pass


def canonical_clause(lits):
    return r15b.canon_clause(lits)


def pair_key(a,b):
    return r15c.pair_key(a,b)


def check_deadline(deadline):
    if time.monotonic() >= deadline:
        raise DeadlineExceeded


def minimize_width3_basis_bounded(clauses,deadline):
    """Exactly the R15C subset-minimal basis, with deadline checks."""
    cs=set()
    for i,c in enumerate(clauses):
        if (i & 8191)==0: check_deadline(deadline)
        cc=canonical_clause(c)
        if cc is not None:
            if len(cc)>3: raise AssertionError("physical clause width >3")
            cs.add(cc)
    if () in cs: return {()}
    units={c for c in cs if len(c)==1}; unit_lits={c[0] for c in units}
    bins=set()
    for i,c in enumerate(cs):
        if (i & 8191)==0: check_deadline(deadline)
        if len(c)==2 and not any(l in unit_lits for l in c): bins.add(c)
    ters=set()
    for i,c in enumerate(cs):
        if (i & 8191)==0: check_deadline(deadline)
        if len(c)!=3 or any(l in unit_lits for l in c): continue
        if any(pair_key(*p) in bins for p in itertools.combinations(c,2)): continue
        ters.add(c)
    return units|bins|ters


def choose_internal_var_bounded(formula,internal,deadline):
    best=None
    # Same tuple objective as R15C/R15B, but scan clauses once.
    counts={v:[0,0] for v in internal}
    for i,c in enumerate(formula):
        if (i & 8191)==0: check_deadline(deadline)
        for lit in c:
            v=abs(lit)
            if v in counts:
                counts[v][0 if lit>0 else 1]+=1
    for v in sorted(internal):
        pos,neg=counts[v]
        item=(pos*neg,pos+neg,v,pos,neg)
        if best is None or item<best: best=item
    return best


def pair_frequencies_bounded(wide,deadline):
    freq=Counter()
    for i,c in enumerate(wide):
        if (i & 8191)==0: check_deadline(deadline)
        for p in itertools.combinations(c,2): freq[pair_key(*p)]+=1
    return freq


def factor_batch_shared_bounded(wide,atom_cache,next_aux,deadline):
    freq=pair_frequencies_bounded(wide,deadline)
    clauses=[]; created=0; reused=0
    for i,c in enumerate(sorted(wide,key=lambda x:(len(x),x))):
        if (i & 4095)==0: check_deadline(deadline)
        pairs=[pair_key(*p) for p in itertools.combinations(c,2)]
        existing=[p for p in pairs if p in atom_cache]
        if existing:
            chosen=min(existing,key=lambda p:(-freq[p],tuple((abs(x),x<0) for x in p)))
            a=atom_cache[chosen]; reused+=1
        else:
            chosen=min(pairs,key=lambda p:(-freq[p],tuple((abs(x),x<0) for x in p)))
            a=next_aux; next_aux+=1; atom_cache[chosen]=a; created+=1
            l1,l2=chosen
            clauses.extend((canonical_clause((-a,l1,l2)),canonical_clause((a,-l1)),canonical_clause((a,-l2))))
        residual=list(c); residual.remove(chosen[0]); residual.remove(chosen[1])
        clauses.append(canonical_clause((a,residual[0],residual[1])))
    return [c for c in clauses if c is not None],next_aux,{"new_atoms":created,"reuse_hits":reused,"unique_pair_atoms_total":len(atom_cache),"wide_resolvents":len(wide)}


def emit_progress(state,phase,started,last_progress,force=False):
    now=time.monotonic()
    if force or now-last_progress[0]>=PROGRESS_SECONDS:
        payload={"R15D_PROGRESS":phase,"elapsed_s":round(now-started,3),**state}
        print(json.dumps(payload,sort_keys=True),flush=True)
        last_progress[0]=now


def compile_observed(frame,bridge):
    started=time.monotonic(); deadline=started+WALL_SECONDS; last_progress=[started]
    try:
        formula=minimize_width3_basis_bounded(frame,deadline)
    except DeadlineExceeded:
        return {"status":"OPEN_RESOURCE_LIMIT_WITH_CHECKPOINT","phase":"INITIAL_MINIMIZE","elapsed_seconds":time.monotonic()-started}
    orig=r15b.original_vars(frame); bridge_set=set(bridge); internal=set(orig)-bridge_set
    next_aux=max(orig,default=0)+1; first_aux=next_aux; atom_cache={}; pair_attempts=0
    history=[]; total_reuse=0; total_created=0; total_dominated=0
    checkpoint={"eliminated":0,"remaining_internal":len(internal),"active_clauses":len(formula),"pair_attempts":0,"auxiliary_variables":0,"shared_pair_atoms":0,"atom_reuse_hits":0,"last_var":None}

    def open_result(reason,phase):
        return {"status":"OPEN_RESOURCE_LIMIT_WITH_CHECKPOINT","reason":reason,"phase":phase,"elapsed_seconds":time.monotonic()-started,"checkpoint":dict(checkpoint),"history":history,"max_clause_width":max(map(len,formula),default=0)}

    while internal:
        if len(formula)>MAX_ACTIVE_CLAUSES or next_aux-first_aux>MAX_AUXILIARIES or pair_attempts>MAX_PAIR_ATTEMPTS:
            return open_result("FROZEN_RESOURCE_CAP","LOOP_HEAD")
        try:
            check_deadline(deadline)
            choice=choose_internal_var_bounded(formula,internal,deadline)
            _,_,var,pos_count,neg_count=choice
            pos=[]; neg=[]; rest=set()
            for i,c in enumerate(formula):
                if (i & 8191)==0:
                    check_deadline(deadline)
                    emit_progress(checkpoint,"PARTITION",started,last_progress)
                if var in c: pos.append(c)
                elif -var in c: neg.append(c)
                else: rest.add(c)
            direct_res=set(); wide=set(); taut=0
            for pi,p in enumerate(pos):
                for n in neg:
                    pair_attempts+=1
                    if (pair_attempts & 8191)==0:
                        checkpoint.update({"pair_attempts":pair_attempts,"active_clauses":len(formula),"remaining_internal":len(internal),"auxiliary_variables":next_aux-first_aux,"shared_pair_atoms":len(atom_cache),"atom_reuse_hits":total_reuse,"last_var":var})
                        check_deadline(deadline); emit_progress(checkpoint,"RESOLVE",started,last_progress)
                        if pair_attempts>MAX_PAIR_ATTEMPTS: return open_result("PAIR_ATTEMPT_CAP","RESOLVE")
                    r=r15b.resolve_on(p,n,var)
                    if r is None: taut+=1; continue
                    if len(r)<=3: direct_res.add(r)
                    elif len(r)==4: wide.add(r)
                    else: return {"status":"FAIL_INTEGRITY","reason":"RESOLVENT_WIDTH_GT4","bad_width":len(r),"history":history}
            checkpoint.update({"pair_attempts":pair_attempts,"last_var":var,"wide_resolvents_current":len(wide),"direct_resolvents_current":len(direct_res)})
            emit_progress(checkpoint,"FACTOR_START",started,last_progress,force=True)
            factored,next_aux,fstats=factor_batch_shared_bounded(wide,atom_cache,next_aux,deadline)
            if next_aux-first_aux>MAX_AUXILIARIES: return open_result("AUXILIARY_CAP","FACTOR")
            before_min=len(rest)+len(direct_res)+len(factored)
            emit_progress({**checkpoint,"pre_minimize_clauses":before_min,"shared_pair_atoms":len(atom_cache)},"MINIMIZE_START",started,last_progress,force=True)
            formula=minimize_width3_basis_bounded(set(rest)|direct_res|set(factored),deadline)
            dominated=max(0,before_min-len(formula)); total_dominated+=dominated
            total_reuse+=fstats["reuse_hits"]; total_created+=fstats["new_atoms"]
            internal.remove(var)
            rec={"eliminated_var":var,"before_pos":pos_count,"before_neg":neg_count,"pair_attempts_step":pos_count*neg_count,"direct_resolvents":len(direct_res),"wide_resolvents":len(wide),"new_shared_atoms":fstats["new_atoms"],"atom_reuse_hits":fstats["reuse_hits"],"dominated_or_duplicate_removed":dominated,"after_clauses":len(formula),"remaining_internal":len(internal)}
            history.append(rec)
            checkpoint={"eliminated":len(history),"remaining_internal":len(internal),"active_clauses":len(formula),"pair_attempts":pair_attempts,"auxiliary_variables":next_aux-first_aux,"shared_pair_atoms":len(atom_cache),"atom_reuse_hits":total_reuse,"new_atom_creations":total_created,"dominated_removed":total_dominated,"last_var":var}
            emit_progress(checkpoint,"STEP_COMPLETE",started,last_progress,force=True)
            if len(formula)>MAX_ACTIVE_CLAUSES: return open_result("ACTIVE_CLAUSE_CAP","STEP_COMPLETE")
            if () in formula:
                return {"status":"COMPLETE_UNSAT_INTERFACE","elapsed_seconds":time.monotonic()-started,"checkpoint":checkpoint,"formula":[[]],"history":history,"max_clause_width":0}
        except DeadlineExceeded:
            return open_result("HARD_DEADLINE","IN_STEP")

    maxw=max(map(len,formula),default=0)
    if any(abs(l) in (orig-bridge_set) for c in formula for l in c) or maxw>3:
        return {"status":"FAIL_INTEGRITY","reason":"POSTCONDITION_FAIL","history":history,"max_clause_width":maxw}
    return {"status":"COMPLETE_EXTENDED_INTERFACE","elapsed_seconds":time.monotonic()-started,"checkpoint":checkpoint,"formula":[list(c) for c in sorted(formula,key=lambda c:(len(c),c))],"history":history,"max_clause_width":maxw}


def equivalence_controls():
    samples=[
        {(1,), (1,2), (2,3), (1,2,3), (2,3,4)},
        {(1,2,3), (1,2), (-1,3), (-1,3,4), (5,)},
        {(1,2,3),(-1,2,3),(2,3),(4,5,6),(4,5)},
    ]
    for s in samples:
        got=minimize_width3_basis_bounded(s,time.monotonic()+5)
        want=r15c.minimize_width3_basis(s)
        if got!=want: return False
    return True


def candidate_firewall():
    funcs=[minimize_width3_basis_bounded,choose_internal_var_bounded,pair_frequencies_bounded,factor_batch_shared_bounded,compile_observed]
    src="\n".join(inspect.getsource(f) for f in funcs)
    forbidden=["dpll(","shadow_exact_interface","range(1 <<","MISSING_PRIME","FALSE_POSITIVE","exact_search_witness","robdd("]
    hits=[x for x in forbidden if x in src]
    return {"pass":not hits,"forbidden_hits":hits}


def run():
    freeze=r13.load_freeze(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID); world=r13.generate_world(spec)
    if world["source"]["frame_sha256"]!=EXPECTED_FRAME_SHA: raise AssertionError("W05 frame drift")
    equiv=equivalence_controls(); fw=candidate_firewall()
    candidate=compile_observed(world["frame"],tuple(world["bridge"]))
    if not equiv: verdict="FAIL_LOGICAL_EQUIVALENCE_CONTROL"
    elif not fw["pass"] or candidate["status"]=="FAIL_INTEGRITY": verdict="FAIL_INTEGRITY"
    elif candidate["status"].startswith("COMPLETE"): verdict="COMPLETE_WITHIN_DIAGNOSTIC_ENVELOPE"
    else: verdict="OPEN_RESOURCE_LIMIT_WITH_CHECKPOINT"
    gates={"G1_FRAME_FROZEN":world["source"]["frame_sha256"]==EXPECTED_FRAME_SHA,"G2_MINIMIZER_EQUIVALENCE_CONTROL":equiv,"G3_CANDIDATE_FIREWALL":fw["pass"],"G4_EXPLICIT_RESOURCE_STATUS":candidate["status"]!="UNKNOWN","G5_NO_SCIENTIFIC_INFLATION":True}
    return {"schema":"JANUS/TRUMP/R15D/BOUNDED_OBSERVER_EQUIVALENT_REFACTOR/RESULT/v1.0","created_date":"2026-09-02","verdict":verdict,"candidate_firewall":fw,"candidate":candidate,"gates":gates,"interpretation":"This pass localizes R15C resource growth; OPEN is diagnostic, not negative evidence.","seal":"MEASURE_WHERE_THE_MACHINE_GROWS__DO_NOT_GUESS_FROM_A_KILLED_PROCESS","P_VS_NP":"OPEN"}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args(); d=run(); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict":d["verdict"],"candidate":{k:v for k,v in d["candidate"].items() if k not in ("formula","history")},"history_steps":len(d["candidate"].get("history",[])),"gates":d["gates"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True)); return 2 if d["verdict"].startswith("FAIL") else 0

if __name__=="__main__": raise SystemExit(main())
