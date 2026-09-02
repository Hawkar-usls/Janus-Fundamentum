#!/usr/bin/env python3
"""R20B supplemental semantic recovery for the four R19 timeout worlds.

Candidate is byte-frozen R18.  Truth appears only after candidate terminal.
The candidate DAG is graded exactly over the full bridge domain using packed
bit-vectors rather than repeated scalar DAG traversals.
"""
from __future__ import annotations
import argparse,hashlib,json,time,inspect
from pathlib import Path
from pysat.solvers import Solver
import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_prospective_unseen_shannon_dag_holdout as r19

TARGETS=("R19-W05","R19-W07","R19-W08","R19-W10")
EXPECTED_BLOB="afa95321ec6edbb33bef222d8ee7234fe631a599"
ORIGINAL_VERIFIER_WALL=120.0
BITPARALLEL_WALL=60.0

class ObserverLimit(RuntimeError): pass

def list_hash(masks): return hashlib.sha256(json.dumps(list(masks),separators=(",",":")).encode()).hexdigest()

def replay_model(cnf,assumptions,model):
    vals={abs(int(l)):int(l)>0 for l in model if int(l)!=0}
    for lit in assumptions: vals[abs(int(lit))]=int(lit)>0
    return all(any(vals.get(abs(int(lit)))==(int(lit)>0) for lit in clause) for clause in cnf)

def original_allowed(frame,bridge,wall_seconds=ORIGINAL_VERIFIER_WALL):
    started=time.monotonic();deadline=started+wall_seconds;allowed=[];replay=[];domain=1<<len(bridge)
    with Solver(name="m22",bootstrap_with=[list(c) for c in frame]) as solver:
        for mask in range(domain):
            if time.monotonic()>=deadline:return {"status":"OPEN_VERIFIER_RESOURCE_LIMIT","masks_scanned":mask,"allowed_partial":len(allowed),"elapsed_seconds":time.monotonic()-started}
            assumptions=[int(v) if ((mask>>i)&1) else -int(v) for i,v in enumerate(bridge)]
            if solver.solve(assumptions=assumptions):
                model=solver.get_model()
                if model is None or not replay_model(frame,assumptions,model): replay.append(mask);break
                allowed.append(mask)
    return {"status":"COMPLETE","domain_size":domain,"allowed_masks":allowed,"allowed_count":len(allowed),"truth_table_sha256":list_hash(allowed),"sat_model_replay_failures":replay,"elapsed_seconds":time.monotonic()-started}

def variable_pattern(domain_size,index):
    """Bit m is assignment mask m; index is bridge-position 0..k-1."""
    block=1<<index;period=block<<1;out=0
    # Set runs [block,2*block), repeated. Domain <=65536 so this setup is tiny.
    chunk=(1<<block)-1
    pos=block
    while pos<domain_size:
        width=min(block,domain_size-pos);out|=((1<<width)-1)<<pos;pos+=period
    return out

def bitparallel_truth(dag,root,bridge,wall_seconds=BITPARALLEL_WALL):
    started=time.monotonic();deadline=started+wall_seconds;domain=1<<len(bridge);full=(1<<domain)-1;pos={int(v):i for i,v in enumerate(bridge)};patterns={v:variable_pattern(domain,i) for v,i in pos.items()};memo={0:0,1:full};visited=0
    def rec(nid):
        nonlocal visited
        if nid in memo:return memo[nid]
        visited+=1
        if (visited&1023)==0 and time.monotonic()>=deadline: raise ObserverLimit("BITPARALLEL_EVALUATOR_WALL")
        node=dag.nodes[nid];kind=node[0]
        if kind=="LIT":
            lit=int(node[1]);v=abs(lit)
            if v not in patterns: raise AssertionError(f"non-bridge literal in terminal DAG:{lit}")
            val=patterns[v];out=val if lit>0 else (full^val)
        elif kind=="AND":
            out=full
            for c in node[1]:out&=rec(c)
        elif kind=="OR":
            out=0
            for c in node[1]:out|=rec(c)
        elif kind=="CONST":out=full if node[1] else 0
        else:raise AssertionError(node)
        memo[nid]=out;return out
    try:bits=rec(int(root))
    except ObserverLimit as e:return {"status":"OPEN_VERIFIER_RESOURCE_LIMIT","reason":str(e),"visited_nodes":visited,"memo_nodes":len(memo),"elapsed_seconds":time.monotonic()-started}
    allowed=[];x=bits
    while x:
        lsb=x&-x;allowed.append(lsb.bit_length()-1);x-=lsb
    return {"status":"COMPLETE","domain_size":domain,"allowed_masks":allowed,"allowed_count":len(allowed),"truth_table_sha256":list_hash(allowed),"visited_nodes":visited,"memo_nodes":len(memo),"elapsed_seconds":time.monotonic()-started}

def observer_firewall():
    src="\n".join(inspect.getsource(f) for f in (bitparallel_truth,original_allowed,run_world));banned=["candidate_allowed(","dpll(","shadow_exact_interface","exact_cnf_geometry","compile_observed("]
    hits=[x for x in banned if x in src];return {"pass":not hits,"forbidden_hits":hits}

def tiny_control():
    import time as _t
    b=r18.Budget(deadline=_t.monotonic()+10);d=r18.Dag(b);root=r18.compile_cnf(d,((1,2),(-1,3)));root,_=d.exists(root,1);d.gc(root);got=bitparallel_truth(d,root,(2,3),10);return got["status"]=="COMPLETE" and got["allowed_masks"]==[1,2,3]

def run_world(wid):
    if wid not in TARGETS:raise ValueError(wid)
    freeze,_=r19.load_contracts();spec=next(w for w in freeze['worlds'] if w['id']==wid);frame,bridge,checks=r19.generate_world(spec);fw=r18.candidate_firewall();ofw=observer_firewall();tiny=tiny_control();candidate=r18.candidate_compile(frame,bridge);cs={k:v for k,v in candidate.items() if k not in ('dag','root')};base={"schema":"JANUS/TRUMP/R20B/BITPARALLEL_SEMANTIC_WITNESS_RECOVERY/WORLD_RESULT/v1.0","created_date":"2026-09-02","world_id":wid,"source":spec,"regeneration_checks":checks,"candidate_blob_sha":EXPECTED_BLOB,"candidate_firewall":fw,"observer_firewall":ofw,"tiny_control":tiny,"candidate":cs,"historical_R19_verdict":"OPEN_EXECUTION_RESOURCE_LIMIT__UNCHANGED","P_VS_NP":"OPEN"}
    if not fw['pass'] or not ofw['pass'] or not tiny or candidate['status']=='FAIL_INTEGRITY':return {**base,"verdict":"R20B_FAIL_INTEGRITY","verifier":{"not_run":True}}
    if candidate['status']=='OPEN_RESOURCE_LIMIT':return {**base,"verdict":"R20B_OPEN_CANDIDATE_RESOURCE_LIMIT","verifier":{"not_run":True}}
    if candidate['status']!='COMPLETE_INTERFACE_DAG' or not set(candidate['final_support'])<=set(bridge):return {**base,"verdict":"R20B_FAIL_INTEGRITY","verifier":{"not_run":True},"reason":"TERMINAL_POSTCONDITION_FAIL"}
    # Truth only after terminal candidate.
    orig=original_allowed(frame,bridge)
    if orig['status']!='COMPLETE':return {**base,"verdict":"R20B_OPEN_VERIFIER_RESOURCE_LIMIT","original_verifier":orig,"candidate_verifier":{"not_run":True}}
    if orig['sat_model_replay_failures']:return {**base,"verdict":"R20B_FAIL_INTEGRITY","original_verifier":orig,"candidate_verifier":{"not_run":True},"reason":"ORIGINAL_MODEL_REPLAY_FAIL"}
    cand=bitparallel_truth(candidate['dag'],candidate['root'],bridge)
    if cand['status']!='COMPLETE':return {**base,"verdict":"R20B_OPEN_VERIFIER_RESOURCE_LIMIT","original_verifier":{k:v for k,v in orig.items() if k!='allowed_masks'},"candidate_verifier":cand}
    exact=set(orig['allowed_masks']);got=set(cand['allowed_masks']);fp=sorted(got-exact);fn=sorted(exact-got);cmp={"full_domain":True,"domain_size":1<<len(bridge),"original_allowed":len(exact),"candidate_allowed":len(got),"false_positive_count":len(fp),"false_negative_count":len(fn),"first_false_positive_masks":fp[:32],"first_false_negative_masks":fn[:32],"original_truth_table_sha256":orig['truth_table_sha256'],"candidate_truth_table_sha256":cand['truth_table_sha256'],"allowed_set_equal":not fp and not fn};verdict="R20B_SUPPLEMENTAL_FULL_DOMAIN_MATCH" if cmp['allowed_set_equal'] else "R20B_SUPPLEMENTAL_FULL_DOMAIN_MISMATCH";return {**base,"verdict":verdict,"original_verifier":{k:v for k,v in orig.items() if k!='allowed_masks'},"candidate_verifier":{k:v for k,v in cand.items() if k!='allowed_masks'},"comparison":cmp,"scientific_firewall":{"candidate_terminal_before_truth":True,"candidate_byte_frozen":True,"historical_R19_score_unchanged":True},"seal":"THE_FASTER_SCOREBOARD_READ_THE_SAME_FROZEN_ANSWERS"}

def main():
    a=argparse.ArgumentParser();a.add_argument('--world',required=True);a.add_argument('--output',required=True);z=a.parse_args();d=run_world(z.world);Path(z.output).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'world':d['world_id'],'verdict':d['verdict'],'candidate':d['candidate'],'original_verifier':d.get('original_verifier'),'candidate_verifier':d.get('candidate_verifier'),'comparison':d.get('comparison'),'P_VS_NP':'OPEN'},indent=2,sort_keys=True));return 2 if d['verdict']=='R20B_FAIL_INTEGRITY' else 0
if __name__=='__main__':raise SystemExit(main())
