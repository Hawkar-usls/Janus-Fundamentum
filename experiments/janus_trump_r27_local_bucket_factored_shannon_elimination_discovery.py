#!/usr/bin/env python3
"""R27 exposed discovery: exact local-bucket factored Shannon elimination.

The candidate keeps a conjunction as a set of exact factor DAG roots in one
shared sealed-R18 DAG store.  To eliminate x it combines and rewrites only
factors whose support contains x; all unrelated factors are retained unchanged.
No global candidate conjunction is materialized.  Semantic truth is inspected
only after every retained factor is bridge-only.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import time
from pathlib import Path

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_unseen_dag_holdout as r19

HERE=Path(__file__).resolve().parent
REPO=HERE.parent
PREREG_PATH=REPO/'research'/'JANUS_TRUMP_R27_LOCAL_BUCKET_FACTORED_SHANNON_ELIMINATION_DISCOVERY_PREREGISTRATION_2026-09-02.json'
WORLD_ID='R19-W05'
EXPECTED_FRAME_SHA='cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384'
EXPECTED_R18_BLOB='afa95321ec6edbb33bef222d8ee7234fe631a599'


def load_prereg():
    d=json.loads(PREREG_PATH.read_text(encoding='utf-8'))
    assert d['status']=='FROZEN_BEFORE_R27_IMPLEMENTATION_AND_EXECUTION'
    assert d['parent_R26_result_summary_commit']=='371a2825b3e2846202daf6f93995209207b31971'
    assert d['frozen_local_boolean_machine']['git_blob_sha']==EXPECTED_R18_BLOB
    assert d['representation_contract']['global_monolithic_conjunction_forbidden'] is True
    assert d['resource_envelope']['single_global_envelope_across_entire_factor_set'] is True
    return d


def normalize_factors(roots):
    roots={int(r) for r in roots}
    if 0 in roots:
        return (0,)
    roots.discard(1)
    if not roots:
        return (1,)
    return tuple(sorted(roots))


def multi_root_gc(dag,roots):
    roots=tuple(int(r) for r in roots)
    reachable={0,1}; stack=list(roots)
    while stack:
        nid=stack.pop()
        if nid in reachable:
            continue
        if nid not in dag.nodes:
            raise AssertionError(f'MULTI_ROOT_GC_MISSING_NODE:{nid}')
        reachable.add(nid)
        node=dag.nodes[nid]
        if node[0] in ('AND','OR'):
            stack.extend(node[1])
    before=len(dag.nodes)
    dag.nodes={nid:dag.nodes[nid] for nid in reachable}
    dag.support={nid:dag.support[nid] for nid in reachable}
    dag.intern={rec:nid for nid,rec in dag.nodes.items()}
    removed=before-len(dag.nodes)
    dag.gc_calls+=1; dag.gc_removed_total+=removed
    return removed


def compile_initial_factors(dag,frame):
    roots=[]
    for clause in frame:
        root=dag.OR(*(dag.lit(int(lit)) for lit in clause))
        roots.append(root)
    factors=normalize_factors(roots)
    multi_root_gc(dag,factors)
    return factors


def factor_support_vars(dag,root,max_var):
    mask=dag.support[int(root)]
    return tuple(v for v in range(1,max_var+1) if mask & (1<<(v-1)))


def compile_factored(frame,bridge):
    started=time.monotonic(); budget=r18.Budget(deadline=started+r18.WALL_SECONDS); dag=r18.Dag(budget)
    trajectory=[]; partial=None; max_live=len(dag.nodes)
    max_var=max({abs(int(l)) for c in frame for l in c},default=0)
    try:
        factors=compile_initial_factors(dag,frame)
        max_live=max(max_live,len(dag.nodes),dag.max_nodes_seen)
        order=tuple(r18.elimination_order(frame,bridge))
        if len(order)!=len(set(order)):
            raise AssertionError('R18_ORDER_DUPLICATE')
        for step,var in enumerate(order,start=1):
            bit=1<<(int(var)-1)
            before_factors=len(factors); before_live=len(dag.nodes); created0=budget.nodes_created_total; calls0=budget.restrict_calls; hits0=dag.hashcons_hits
            bucket=tuple(r for r in factors if dag.support[r] & bit)
            rest=tuple(r for r in factors if not (dag.support[r] & bit))
            bucket_union=0
            for r in bucket: bucket_union |= dag.support[r]
            partial={'step':step,'quantified_var':int(var),'before_factors':before_factors,'before_live':before_live,'bucket_factor_count':len(bucket),'bucket_union_support_size':bucket_union.bit_count(),'created0':created0,'calls0':calls0,'hits0':hits0}
            if bucket:
                local_root=bucket[0] if len(bucket)==1 else dag.AND(*bucket)
                quantified_root,_memo=r18.Dag.exists(dag,local_root,int(var))
                factors=normalize_factors(rest+(quantified_root,))
                pre_gc=len(dag.nodes); removed=multi_root_gc(dag,factors); after_live=len(dag.nodes)
            else:
                pre_gc=len(dag.nodes); removed=0; after_live=len(dag.nodes)
            max_live=max(max_live,pre_gc,after_live,dag.max_nodes_seen)
            remaining=sum(1 for v in order[step:] if any(dag.support[r] & (1<<(v-1)) for r in factors))
            trajectory.append({
                'step':step,'quantified_var':int(var),'factor_count_before':before_factors,'bucket_factor_count':len(bucket),
                'bucket_union_support_size':bucket_union.bit_count(),'factor_count_after':len(factors),'before_live_nodes':before_live,
                'pre_gc_live_nodes':pre_gc,'after_gc_live_nodes':after_live,'new_nodes_created_step':budget.nodes_created_total-created0,
                'restrict_calls_step':budget.restrict_calls-calls0,'hashcons_hits_step':dag.hashcons_hits-hits0,'gc_removed_nodes':removed,
                'remaining_internal_variables_with_support':remaining,
            })
            partial=None
        bridge_set=set(int(v) for v in bridge)
        supports=[factor_support_vars(dag,r,max_var) for r in factors]
        bad=sorted({v for supp in supports for v in supp if v not in bridge_set})
        if bad:
            return {'status':'FAIL_INTEGRITY','reason':'FINAL_FACTOR_SUPPORT_NOT_BRIDGE_ONLY','bad_support':bad,'trajectory':trajectory},None
        return {
            'status':'COMPLETE_FACTORED_BRIDGE_INTERFACE','elapsed_seconds':time.monotonic()-started,'elimination_order':list(order),
            'completed_quantification_steps':len(trajectory),'initial_clause_count':len(frame),'final_factor_count':len(factors),
            'final_factor_roots':list(factors),'final_factor_supports':[list(x) for x in supports],'final_live_nodes':len(dag.nodes),
            'maximum_live_nodes':max(max_live,dag.max_nodes_seen),'nodes_created_total':budget.nodes_created_total,'restrict_calls_total':budget.restrict_calls,
            'hashcons_hits':dag.hashcons_hits,'gc_calls':dag.gc_calls,'gc_removed_total':dag.gc_removed_total,'trajectory':trajectory,
        },{'dag':dag,'roots':factors}
    except r18.ResourceLimit as e:
        open_partial=None
        if partial is not None:
            open_partial={
                'step':partial['step'],'quantified_var':partial['quantified_var'],'reason':e.reason,'elapsed_seconds_at_open':time.monotonic()-started,
                'factor_count_before':partial['before_factors'],'bucket_factor_count':partial['bucket_factor_count'],'bucket_union_support_size':partial['bucket_union_support_size'],
                'before_live_nodes':partial['before_live'],'active_nodes_at_open':len(dag.nodes),'partial_nodes_created_step':budget.nodes_created_total-partial['created0'],
                'partial_restrict_calls_step':budget.restrict_calls-partial['calls0'],'partial_hashcons_hits_step':dag.hashcons_hits-partial['hits0'],
            }
        return {
            'status':'OPEN_RESOURCE_LIMIT','reason':e.reason,'elapsed_seconds':time.monotonic()-started,'completed_quantification_steps':len(trajectory),
            'active_nodes_at_open':len(dag.nodes),'maximum_live_nodes':max(max_live,dag.max_nodes_seen),'nodes_created_total':budget.nodes_created_total,
            'restrict_calls_total':budget.restrict_calls,'hashcons_hits':dag.hashcons_hits,'gc_calls':dag.gc_calls,'gc_removed_total':dag.gc_removed_total,
            'partial_open_step':open_partial,'trajectory':trajectory,
        },None
    except AssertionError as e:
        return {'status':'FAIL_INTEGRITY','reason':str(e),'elapsed_seconds':time.monotonic()-started,'trajectory':trajectory},None


def candidate_firewall():
    src='\n'.join(inspect.getsource(f) for f in (normalize_factors,multi_root_gc,compile_initial_factors,factor_support_vars,compile_factored))
    forbidden=['Solver(','solve(','range(1 <<','allowed_masks','truth_table','candidate_allowed','independent_original_allowed','dpll(','resolve_on(','assumptions_for_mask']
    hits=[x for x in forbidden if x in src]
    return {'pass':not hits,'forbidden_hits':hits}


def factor_set_allowed(live,bridge):
    dag=live['dag']; roots=live['roots']; allowed=[]; started=time.monotonic()
    for mask in range(1<<len(bridge)):
        assignment={int(v):bool((mask>>i)&1) for i,v in enumerate(bridge)}
        if all(dag.evaluate(root,assignment) for root in roots):
            allowed.append(mask)
    return {'allowed_masks':allowed,'allowed_count':len(allowed),'elapsed_seconds':time.monotonic()-started}


def mask_hash(masks):
    return hashlib.sha256(json.dumps(list(masks),separators=(',',':')).encode()).hexdigest()


def tiny_factor_identity_control():
    # (x or b) AND (~x or c) AND (d) ; eliminate x locally, leave d untouched.
    frame=((1,2),(-1,3),(4,)); bridge=(2,3,4)
    candidate,live=compile_factored(frame,bridge)
    if candidate.get('status')!='COMPLETE_FACTORED_BRIDGE_INTERFACE' or live is None:
        return False
    got=factor_set_allowed(live,bridge)['allowed_masks']
    # exists x gives (b or c) AND d. Under bridge order (2,3,4), masks with d=1 and (b or c)=1.
    return got==[5,6,7]


def run():
    prereg=load_prereg(); freeze=r19.load_freeze(); spec=next(w for w in freeze['worlds'] if w['id']==WORLD_ID); world=r19.generate_frozen_world(spec)
    frame=tuple(world['frame']); bridge=tuple(world['bridge'])
    if spec['frame_sha256']!=EXPECTED_FRAME_SHA: raise AssertionError('R19-W05 frame drift')
    fw=candidate_firewall(); tiny=tiny_factor_identity_control()
    base={'schema':'JANUS/TRUMP/R27/LOCAL_BUCKET_FACTORED_SHANNON_ELIMINATION_DISCOVERY/RESULT/v1.0','created_date':'2026-09-02','scientific_role':'EXPOSED_NEW_COMPOSITION_REPRESENTATION_DISCOVERY__NOT_UNSEEN','world':{'id':WORLD_ID,'frame_sha256':EXPECTED_FRAME_SHA,'frame_clauses':len(frame),'bridge_vars':list(bridge)},'candidate_firewall':fw,'tiny_factor_identity_control':tiny,'P_VS_NP':'OPEN'}
    if not fw['pass'] or not tiny:
        return {**base,'verdict':'R27_FAIL_INTEGRITY','candidate':{'not_run':True},'verifier':{'not_run':True},'truth_accessed':False}
    candidate,live=compile_factored(frame,bridge); serial={k:v for k,v in candidate.items() if k!='trajectory'}
    if candidate['status']=='OPEN_RESOURCE_LIMIT':
        return {**base,'verdict':'R27_OPEN_RESOURCE_LIMIT__NO_SEMANTIC_VERDICT','candidate':serial,'verifier':{'not_run':True},'truth_accessed':False}
    if candidate['status']!='COMPLETE_FACTORED_BRIDGE_INTERFACE' or live is None:
        return {**base,'verdict':'R27_FAIL_INTEGRITY','candidate':serial,'verifier':{'not_run':True},'truth_accessed':False}
    verifier_started=time.monotonic(); original=r18.independent_original_allowed(frame,bridge); got=factor_set_allowed(live,bridge)
    if original.get('replay_failures'):
        return {**base,'verdict':'R27_FAIL_INTEGRITY','candidate':serial,'truth_accessed':True,'reason':'ORIGINAL_MODEL_REPLAY_FAIL'}
    exact=set(original['allowed_masks']); have=set(got['allowed_masks']); fp=sorted(have-exact); fn=sorted(exact-have); match=not fp and not fn
    comparison={'full_domain':True,'domain_size':1<<len(bridge),'allowed_set_equal':match,'original_allowed':len(exact),'candidate_allowed':len(have),'false_positive_count':len(fp),'false_negative_count':len(fn),'first_false_positive_masks':fp[:32],'first_false_negative_masks':fn[:32],'original_truth_table_sha256':mask_hash(original['allowed_masks']),'candidate_truth_table_sha256':mask_hash(got['allowed_masks']),'original_sat_model_replay_failures':original.get('replay_failures',[])}
    verdict='R27_EXPOSED_W05_FACTORED_BUCKET_FULL_DOMAIN_SEMANTIC_MATCH' if match else 'R27_EXPOSED_W05_FACTORED_BUCKET_SEMANTIC_MISMATCH'
    return {**base,'verdict':verdict,'candidate':serial,'verifier':{'started_after_candidate_terminal':True,'elapsed_seconds':time.monotonic()-verifier_started},'comparison':comparison,'truth_accessed':True,'claim_ceiling':prereg['claim_ceiling'],'seal':'THE_VARIABLE_REWROTE_ONLY_ITS_BUCKET__THE_UNRELATED_FACTORS_NEVER_MOVED','P_VS_NP':'OPEN'}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); args=ap.parse_args(); out=run(); Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'verdict':out['verdict'],'truth_accessed':out.get('truth_accessed'),'candidate':out.get('candidate'),'comparison':out.get('comparison'),'firewall':out['candidate_firewall'],'tiny':out['tiny_factor_identity_control'],'P_VS_NP':'OPEN'},indent=2,sort_keys=True))
    return 2 if out['verdict']=='R27_FAIL_INTEGRITY' else 0

if __name__=='__main__': raise SystemExit(main())
