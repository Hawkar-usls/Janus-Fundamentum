#!/usr/bin/env python3
"""R25 exposed discovery: frozen R24 cutset variables are quantified first.

The Boolean representation, restriction operator, Shannon EXISTS rule and GC are
imported byte-for-byte from sealed R18.  R25 changes only the original-internal
quantification order: the eight R24 W05 structural cutset variable IDs first,
then the untouched relative order of the remaining sealed R18 elimination order.
No cutset values are assigned or enumerated.  W05 truth is inspected only if a
terminal bridge-only DAG exists.
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
PREREG_PATH=REPO/'research'/'JANUS_TRUMP_R25_CUTSET_FIRST_SYMBOLIC_SHANNON_SCHEDULE_DISCOVERY_PREREGISTRATION_2026-09-02.json'
WORLD_ID='R19-W05'
EXPECTED_FRAME_SHA='cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384'
R24_PREFIX=(35,1,32,2,37,69,59,23)
EXPECTED_R18_BLOB='afa95321ec6edbb33bef222d8ee7234fe631a599'


def load_prereg():
    d=json.loads(PREREG_PATH.read_text(encoding='utf-8'))
    assert d['status']=='FROZEN_BEFORE_R25_IMPLEMENTATION_AND_EXECUTION'
    assert d['parent_R24B_result_summary_commit']=='a92f0fdf88caf57ceb98a320038d327e76fd2501'
    assert tuple(d['quantification_schedule']['prefix'])==R24_PREFIX
    assert d['frozen_candidate_machine']['git_blob_sha']==EXPECTED_R18_BLOB
    assert d['frozen_candidate_machine']['only_allowed_candidate_change']=='ORIGINAL_INTERNAL_VARIABLE_EXISTENTIAL_QUANTIFICATION_ORDER'
    assert d['candidate_firewall']['cutset_assignment_enumeration_forbidden'] is True
    return d


def frozen_cutset_first_order(frame,bridge):
    base=tuple(r18.elimination_order(frame,bridge))
    prefix=tuple(int(v) for v in R24_PREFIX)
    if len(prefix)!=len(set(prefix)) or not set(prefix)<=set(base):
        raise ValueError('CUTSET_PREFIX_NOT_DISTINCT_INTERNAL_SUBSET')
    remainder=tuple(v for v in base if v not in set(prefix))
    order=prefix+remainder
    if len(order)!=len(base) or set(order)!=set(base):
        raise ValueError('CUTSET_FIRST_ORDER_COVERAGE_FAIL')
    return base,order


def candidate_compile_cutset_first(frame,bridge):
    started=time.monotonic(); budget=r18.Budget(deadline=started+r18.WALL_SECONDS); dag=r18.Dag(budget)
    trajectory=[]; partial=None; root=None
    try:
        root=r18.compile_cnf(dag,frame)
        dag.gc(root)
        base_order,order=frozen_cutset_first_order(frame,bridge)
        max_active=len(dag.nodes)
        for step,var in enumerate(order,start=1):
            before_nodes=len(dag.nodes); before_support=dag.support[root].bit_count()
            created_before=budget.nodes_created_total; calls_before=budget.restrict_calls; hits_before=dag.hashcons_hits
            partial={
                'step':step,'quantified_var':int(var),'before_active_nodes':before_nodes,
                'support_variables_before':before_support,'nodes_created_before_step':created_before,
                'restrict_calls_before_step':calls_before,'hashcons_hits_before_step':hits_before,
            }
            root,memo_entries=dag.exists(root,var)
            pre_gc_nodes=len(dag.nodes); removed=dag.gc(root); after_nodes=len(dag.nodes)
            max_active=max(max_active,pre_gc_nodes,after_nodes,dag.max_nodes_seen)
            trajectory.append({
                'step':step,'quantified_var':int(var),'is_R24_cutset_prefix_step':step<=len(R24_PREFIX),
                'elapsed_seconds_after_step':time.monotonic()-started,
                'before_active_nodes':before_nodes,'pre_gc_nodes':pre_gc_nodes,'after_active_nodes':after_nodes,
                'gc_removed_nodes':removed,'support_variables_before':before_support,'support_variables_after':dag.support[root].bit_count(),
                'new_nodes_created_step':budget.nodes_created_total-created_before,
                'restrict_calls_step':budget.restrict_calls-calls_before,'restrict_memo_entries_step':memo_entries,
                'hashcons_hits_step':dag.hashcons_hits-hits_before,'cumulative_nodes_created':budget.nodes_created_total,
                'cumulative_restrict_calls':budget.restrict_calls,'cumulative_hashcons_hits':dag.hashcons_hits,
            })
            partial=None
        bridge_set=set(int(v) for v in bridge)
        max_var=max({abs(int(l)) for c in frame for l in c},default=0)
        support_vars={v for v in range(1,max_var+1) if dag.support[root] & (1<<(v-1))}
        if not support_vars<=bridge_set:
            return {'status':'FAIL_INTEGRITY','reason':'FINAL_SUPPORT_NOT_BRIDGE_ONLY','support':sorted(support_vars),'trajectory':trajectory},None
        return {
            'status':'COMPLETE_INTERFACE_DAG','elapsed_seconds':time.monotonic()-started,
            'base_R18_elimination_order':list(base_order),'cutset_first_elimination_order':list(order),
            'completed_quantification_steps':len(trajectory),'trajectory':trajectory,
            'final_active_nodes':len(dag.nodes),'maximum_nodes_seen_before_gc':max(max_active,dag.max_nodes_seen),
            'nodes_created_total':budget.nodes_created_total,'restrict_calls_total':budget.restrict_calls,
            'hashcons_hits':dag.hashcons_hits,'gc_calls':dag.gc_calls,'gc_removed_total':dag.gc_removed_total,
            'final_support':sorted(support_vars),'root':root,'dag':dag,
        },{'dag':dag,'root':root}
    except r18.ResourceLimit as e:
        open_partial=None
        if partial is not None:
            open_partial={
                'step':partial['step'],'quantified_var':partial['quantified_var'],'reason':e.reason,
                'is_R24_cutset_prefix_step':partial['step']<=len(R24_PREFIX),
                'elapsed_seconds_at_open':time.monotonic()-started,'before_active_nodes':partial['before_active_nodes'],
                'active_nodes_at_open':len(dag.nodes),'support_variables_before':partial['support_variables_before'],
                'partial_nodes_created_step':budget.nodes_created_total-partial['nodes_created_before_step'],
                'partial_restrict_calls_step':budget.restrict_calls-partial['restrict_calls_before_step'],
                'partial_hashcons_hits_step':dag.hashcons_hits-partial['hashcons_hits_before_step'],
            }
        try:
            base_order,order=frozen_cutset_first_order(frame,bridge)
        except Exception:
            base_order=(); order=()
        return {
            'status':'OPEN_RESOURCE_LIMIT','reason':e.reason,'elapsed_seconds':time.monotonic()-started,
            'base_R18_elimination_order':list(base_order),'cutset_first_elimination_order':list(order),
            'completed_quantification_steps':len(trajectory),'trajectory':trajectory,'partial_open_step':open_partial,
            'active_nodes_at_open':len(dag.nodes),'maximum_nodes_seen':dag.max_nodes_seen,
            'nodes_created_total':budget.nodes_created_total,'restrict_calls_total':budget.restrict_calls,
            'hashcons_hits':dag.hashcons_hits,'gc_calls':dag.gc_calls,'gc_removed_total':dag.gc_removed_total,
        },None
    except ValueError as e:
        return {'status':'FAIL_INTEGRITY','reason':str(e),'elapsed_seconds':time.monotonic()-started,'trajectory':trajectory},None


def candidate_firewall():
    src='\n'.join(inspect.getsource(f) for f in (frozen_cutset_first_order,candidate_compile_cutset_first))
    forbidden=['Solver(','solve(','range(1 <<','allowed_masks','truth_table','candidate_allowed','independent_original_allowed','dpll(','resolve_on(']
    hits=[x for x in forbidden if x in src]
    return {'pass':not hits,'forbidden_hits':hits}


def mask_hash(masks):
    return hashlib.sha256(json.dumps(list(masks),separators=(',',':')).encode()).hexdigest()


def run():
    prereg=load_prereg(); freeze=r19.load_freeze(); spec=next(w for w in freeze['worlds'] if w['id']==WORLD_ID); world=r19.generate_frozen_world(spec)
    frame=tuple(world['frame']); bridge=tuple(world['bridge'])
    if spec['frame_sha256']!=EXPECTED_FRAME_SHA: raise AssertionError('R19-W05 frame drift')
    fw=candidate_firewall()
    base={
        'schema':'JANUS/TRUMP/R25/CUTSET_FIRST_SYMBOLIC_SHANNON_SCHEDULE_DISCOVERY/RESULT/v1.0','created_date':'2026-09-02',
        'scientific_role':'EXPOSED_SYMBOLIC_SCHEDULE_DISCOVERY__NOT_UNSEEN',
        'world':{'id':WORLD_ID,'frame_sha256':EXPECTED_FRAME_SHA,'frame_clauses':len(frame),'bridge_vars':list(bridge)},
        'R24_cutset_prefix':list(R24_PREFIX),'candidate_firewall':fw,'P_VS_NP':'OPEN',
    }
    if not fw['pass']:
        return {**base,'verdict':'R25_FAIL_INTEGRITY','candidate':{'not_run':True},'verifier':{'not_run':True},'truth_accessed':False}
    candidate,live=candidate_compile_cutset_first(frame,bridge)
    serial={k:v for k,v in candidate.items() if k not in ('dag','root')}
    if candidate['status']=='OPEN_RESOURCE_LIMIT':
        return {**base,'verdict':'R25_OPEN_RESOURCE_LIMIT__NO_SEMANTIC_VERDICT','candidate':serial,'verifier':{'not_run':True},'truth_accessed':False}
    if candidate['status']=='FAIL_INTEGRITY' or live is None:
        return {**base,'verdict':'R25_FAIL_INTEGRITY','candidate':serial,'verifier':{'not_run':True},'truth_accessed':False}
    if candidate['status']!='COMPLETE_INTERFACE_DAG':
        return {**base,'verdict':'R25_FAIL_INTEGRITY','candidate':serial,'verifier':{'not_run':True},'truth_accessed':False,'reason':'UNKNOWN_CANDIDATE_STATUS'}
    verifier_started=time.monotonic()
    original=r18.independent_original_allowed(frame,bridge)
    eval_candidate={'dag':live['dag'],'root':live['root']}
    got=r18.candidate_allowed(eval_candidate,bridge)
    if original.get('replay_failures'):
        return {**base,'verdict':'R25_FAIL_INTEGRITY','candidate':serial,'verifier':{'original':{k:v for k,v in original.items() if k!='allowed_masks'}},'truth_accessed':True,'reason':'ORIGINAL_MODEL_REPLAY_FAIL'}
    exact=set(original['allowed_masks']); have=set(got['allowed_masks']); fp=sorted(have-exact); fn=sorted(exact-have); match=not fp and not fn
    comparison={
        'full_domain':True,'domain_size':1<<len(bridge),'allowed_set_equal':match,
        'original_allowed':len(exact),'candidate_allowed':len(have),'false_positive_count':len(fp),'false_negative_count':len(fn),
        'first_false_positive_masks':fp[:32],'first_false_negative_masks':fn[:32],
        'original_truth_table_sha256':mask_hash(original['allowed_masks']),'candidate_truth_table_sha256':mask_hash(got['allowed_masks']),
        'original_sat_model_replay_failures':original.get('replay_failures',[]),
    }
    verdict='R25_EXPOSED_W05_CUTSET_FIRST_FULL_DOMAIN_SEMANTIC_MATCH' if match else 'R25_EXPOSED_W05_CUTSET_FIRST_SEMANTIC_MISMATCH'
    return {
        **base,'verdict':verdict,'candidate':serial,
        'verifier':{'started_after_candidate_terminal':True,'elapsed_seconds':time.monotonic()-verifier_started},
        'comparison':comparison,'truth_accessed':True,
        'claim_ceiling':prereg['claim_ceiling'],
        'seal':'THE_GRAPH_CHOSE_THE_FIRST_EIGHT_NAMES__THE_SAME_SYMBOLIC_EXISTS_MACHINE_DID_THE_REST',
        'P_VS_NP':'OPEN',
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); args=ap.parse_args(); out=run()
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    c=out.get('candidate',{})
    print(json.dumps({
        'verdict':out['verdict'],'truth_accessed':out.get('truth_accessed'),'comparison':out.get('comparison'),
        'candidate_summary':{k:c.get(k) for k in ('status','reason','elapsed_seconds','completed_quantification_steps','active_nodes_at_open','final_active_nodes','maximum_nodes_seen','maximum_nodes_seen_before_gc','nodes_created_total','restrict_calls_total','hashcons_hits','partial_open_step') if k in c},
        'P_VS_NP':'OPEN'
    },indent=2,sort_keys=True))
    return 2 if out['verdict']=='R25_FAIL_INTEGRITY' else 0


if __name__=='__main__': raise SystemExit(main())
