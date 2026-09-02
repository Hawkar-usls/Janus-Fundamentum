#!/usr/bin/env python3
"""R26 truth-blind Shannon existential-order sensitivity forensics.

The exact sealed R18 DAG machine is reused. Only the complete order of original
internal existential quantification changes among eight preregistered,
structure-only orders. No SAT solver, semantic verifier, bridge assignment scan,
or cutset assignment scan is called by R26.
"""
from __future__ import annotations

import argparse
import inspect
import json
import time
from pathlib import Path

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_unseen_dag_holdout as r19
import janus_trump_r23_primal_graph_decomposition_forensics as r23

HERE=Path(__file__).resolve().parent
REPO=HERE.parent
PREREG_PATH=REPO/'research'/'JANUS_TRUMP_R26_SHANNON_EXISTENTIAL_ORDER_SENSITIVITY_FORENSICS_PREREGISTRATION_2026-09-02.json'
WORLD_ID='R19-W05'
EXPECTED_FRAME_SHA='cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384'
R24_PREFIX=(35,1,32,2,37,69,59,23)
EXPECTED_R18_BLOB='afa95321ec6edbb33bef222d8ee7234fe631a599'
ORDER_IDS=(
    'ORIGINAL_R18_OCCURRENCE',
    'R24_CUTSET_FIRST',
    'R24_CUTSET_LAST',
    'R23_MIN_FILL_INTERNAL',
    'R23_MIN_DEGREE_INTERNAL',
    'R23_MIN_FILL_REVERSED',
    'R23_MIN_DEGREE_REVERSED',
    'PRIMAL_DEGREE_DESCENDING',
)


def load_prereg():
    d=json.loads(PREREG_PATH.read_text(encoding='utf-8'))
    assert d['status']=='FROZEN_BEFORE_R26_IMPLEMENTATION_AND_EXECUTION'
    assert d['parent_R25_result_summary_commit']=='c7515c59171326225c5046a0deef8fd6b7e3e5b6'
    assert d['frozen_machine']['git_blob_sha']==EXPECTED_R18_BLOB
    assert tuple(x['id'] for x in d['frozen_order_family'])==ORDER_IDS
    assert d['firewall']['semantic_verifier_forbidden'] is True
    return d


def validate_order(order,frame,bridge):
    internal={abs(int(l)) for c in frame for l in c}-set(int(v) for v in bridge)
    order=tuple(int(v) for v in order)
    if len(order)!=len(internal) or len(set(order))!=len(order) or set(order)!=internal:
        raise ValueError('ORDER_COVERAGE_FAIL')
    return order


def frozen_orders(frame,bridge):
    original=validate_order(r18.elimination_order(frame,bridge),frame,bridge)
    prefix=tuple(int(v) for v in R24_PREFIX)
    if not set(prefix)<=set(original) or len(set(prefix))!=len(prefix):
        raise ValueError('R24_PREFIX_INVALID')
    pset=set(prefix)
    remainder=tuple(v for v in original if v not in pset)
    adj=r23.primal_graph(frame)
    min_fill=tuple(r23.eliminate_internal(adj,frame,bridge,'MIN_FILL_INTERNAL')['elimination_order'])
    min_degree=tuple(r23.eliminate_internal(adj,frame,bridge,'MIN_DEGREE_INTERNAL')['elimination_order'])
    internal=set(original)
    degree_desc=tuple(sorted(internal,key=lambda v:(-len(adj[v]),v)))
    orders={
        'ORIGINAL_R18_OCCURRENCE':original,
        'R24_CUTSET_FIRST':prefix+remainder,
        'R24_CUTSET_LAST':remainder+prefix,
        'R23_MIN_FILL_INTERNAL':min_fill,
        'R23_MIN_DEGREE_INTERNAL':min_degree,
        'R23_MIN_FILL_REVERSED':tuple(reversed(min_fill)),
        'R23_MIN_DEGREE_REVERSED':tuple(reversed(min_degree)),
        'PRIMAL_DEGREE_DESCENDING':degree_desc,
    }
    return {k:validate_order(v,frame,bridge) for k,v in orders.items()}


def compile_with_order(frame,bridge,order):
    started=time.monotonic(); budget=r18.Budget(deadline=started+r18.WALL_SECONDS); dag=r18.Dag(budget)
    trajectory=[]; partial=None; max_active=len(dag.nodes)
    try:
        root=r18.compile_cnf(dag,frame); dag.gc(root); max_active=max(max_active,len(dag.nodes),dag.max_nodes_seen)
        for step,var in enumerate(order,start=1):
            before=len(dag.nodes); support_before=dag.support[root].bit_count(); created0=budget.nodes_created_total; calls0=budget.restrict_calls; hits0=dag.hashcons_hits
            partial={'step':step,'quantified_var':int(var),'before_active_nodes':before,'support_variables_before':support_before,'created0':created0,'calls0':calls0,'hits0':hits0}
            root,memo_entries=dag.exists(root,var)
            pre_gc=len(dag.nodes); removed=dag.gc(root); after=len(dag.nodes); max_active=max(max_active,pre_gc,after,dag.max_nodes_seen)
            trajectory.append({
                'step':step,'quantified_var':int(var),'before_active_nodes':before,'pre_gc_nodes':pre_gc,'after_active_nodes':after,
                'gc_removed_nodes':removed,'support_variables_before':support_before,'support_variables_after':dag.support[root].bit_count(),
                'new_nodes_created_step':budget.nodes_created_total-created0,'restrict_calls_step':budget.restrict_calls-calls0,
                'restrict_memo_entries_step':memo_entries,'hashcons_hits_step':dag.hashcons_hits-hits0,
            })
            partial=None
        bridge_set=set(int(v) for v in bridge); max_var=max({abs(int(l)) for c in frame for l in c},default=0)
        support={v for v in range(1,max_var+1) if dag.support[root] & (1<<(v-1))}
        if not support<=bridge_set:
            return {'status':'FAIL_INTEGRITY','reason':'FINAL_SUPPORT_NOT_BRIDGE_ONLY','final_support':sorted(support),'trajectory':trajectory}
        return {
            'status':'COMPLETE_INTERFACE_DAG','reason':None,'elapsed_seconds':time.monotonic()-started,
            'completed_quantification_steps':len(trajectory),'final_active_nodes':len(dag.nodes),'maximum_nodes_seen_before_gc':max(max_active,dag.max_nodes_seen),
            'nodes_created_total':budget.nodes_created_total,'restrict_calls_total':budget.restrict_calls,'hashcons_hits':dag.hashcons_hits,
            'gc_calls':dag.gc_calls,'gc_removed_total':dag.gc_removed_total,'final_support':sorted(support),'trajectory':trajectory,
        }
    except r18.ResourceLimit as e:
        open_partial=None
        if partial is not None:
            open_partial={
                'step':partial['step'],'quantified_var':partial['quantified_var'],'reason':e.reason,'elapsed_seconds_at_open':time.monotonic()-started,
                'before_active_nodes':partial['before_active_nodes'],'active_nodes_at_open':len(dag.nodes),'support_variables_before':partial['support_variables_before'],
                'partial_nodes_created_step':budget.nodes_created_total-partial['created0'],'partial_restrict_calls_step':budget.restrict_calls-partial['calls0'],
                'partial_hashcons_hits_step':dag.hashcons_hits-partial['hits0'],
            }
        return {
            'status':'OPEN_RESOURCE_LIMIT','reason':e.reason,'elapsed_seconds':time.monotonic()-started,
            'completed_quantification_steps':len(trajectory),'active_nodes_at_open':len(dag.nodes),'maximum_nodes_seen':max(max_active,dag.max_nodes_seen),
            'nodes_created_total':budget.nodes_created_total,'restrict_calls_total':budget.restrict_calls,'hashcons_hits':dag.hashcons_hits,
            'gc_calls':dag.gc_calls,'gc_removed_total':dag.gc_removed_total,'partial_open_step':open_partial,'trajectory':trajectory,
        }


def candidate_firewall():
    src='\n'.join(inspect.getsource(f) for f in (validate_order,frozen_orders,compile_with_order,run_order,aggregate_directory))
    forbidden=['Solver(','solve(','allowed_masks','truth_table','candidate_allowed','independent_original_allowed','range(1 <<','dpll(','resolve_on(','assumptions_for_mask']
    hits=[x for x in forbidden if x in src]
    return {'pass':not hits,'forbidden_hits':hits}


def run_order(order_id):
    prereg=load_prereg(); freeze=r19.load_freeze(); spec=next(w for w in freeze['worlds'] if w['id']==WORLD_ID); world=r19.generate_frozen_world(spec)
    frame=tuple(world['frame']); bridge=tuple(world['bridge'])
    if spec['frame_sha256']!=EXPECTED_FRAME_SHA: raise AssertionError('R19-W05 frame drift')
    orders=frozen_orders(frame,bridge); fw=candidate_firewall()
    if order_id not in orders: raise ValueError(order_id)
    if not fw['pass']:
        return {'schema':'JANUS/TRUMP/R26/SHANNON_EXISTENTIAL_ORDER_SENSITIVITY_FORENSICS/ORDER_RESULT/v1.0','order_id':order_id,'verdict':'R26_FAIL_INTEGRITY','candidate_firewall':fw,'truth_accessed':False,'P_VS_NP':'OPEN'}
    result=compile_with_order(frame,bridge,orders[order_id])
    serial={k:v for k,v in result.items() if k!='trajectory'}
    survivor=(result.get('status')=='COMPLETE_INTERFACE_DAG' and result.get('completed_quantification_steps')==len(orders[order_id]) and set(result.get('final_support',[]))<=set(bridge))
    if result.get('status')=='FAIL_INTEGRITY': verdict='R26_FAIL_INTEGRITY'
    elif survivor: verdict='R26_TERMINAL_ORDER_SURVIVOR'
    else: verdict='R26_ORDER_RESOURCE_OPEN'
    return {
        'schema':'JANUS/TRUMP/R26/SHANNON_EXISTENTIAL_ORDER_SENSITIVITY_FORENSICS/ORDER_RESULT/v1.0','created_date':'2026-09-02',
        'scientific_role':'EXPOSED_RESOURCE_ORDER_SENSITIVITY_ONLY__NO_SEMANTIC_TRUTH','world_id':WORLD_ID,'frame_sha256':EXPECTED_FRAME_SHA,
        'order_id':order_id,'quantification_order':list(orders[order_id]),'candidate_firewall':fw,'candidate':serial,'terminal_survivor':survivor,
        'truth_accessed':False,'semantic_verifier_ran':False,'verdict':verdict,'P_VS_NP':'OPEN',
    }


def aggregate_directory(directory:Path):
    prereg=load_prereg(); rows=[]
    for p in sorted(directory.glob('*.json')):
        d=json.loads(p.read_text(encoding='utf-8'))
        if d.get('schema')=='JANUS/TRUMP/R26/SHANNON_EXISTENTIAL_ORDER_SENSITIVITY_FORENSICS/ORDER_RESULT/v1.0': rows.append(d)
    by={r['order_id']:r for r in rows}; missing=[x for x in ORDER_IDS if x not in by]; ordered=[by[x] for x in ORDER_IDS if x in by]
    integrity=(not missing and len(ordered)==8 and all(r.get('candidate_firewall',{}).get('pass') and r.get('truth_accessed') is False and r.get('semantic_verifier_ran') is False and r.get('verdict')!='R26_FAIL_INTEGRITY' for r in ordered))
    survivors=[r for r in ordered if r.get('terminal_survivor')]
    def rank(r):
        c=r['candidate']; return (int(c['maximum_nodes_seen_before_gc']),int(c['nodes_created_total']),int(c['restrict_calls_total']),r['order_id'])
    ranked=sorted(survivors,key=rank)
    if not integrity: verdict='R26_FAIL_INTEGRITY'
    elif ranked: verdict='R26_SHANNON_ORDER_SENSITIVITY_CONFIRMED__TERMINAL_ORDER_SURVIVOR_EXISTS'
    else: verdict='R26_NO_TERMINAL_ORDER_SURVIVOR_IN_FROZEN_FAMILY__STOP_ORDER_FISHING'
    compact=[]
    for r in ordered:
        c=r['candidate']; compact.append({
            'order_id':r['order_id'],'verdict':r['verdict'],'terminal_survivor':r['terminal_survivor'],'status':c.get('status'),'reason':c.get('reason'),
            'completed_quantification_steps':c.get('completed_quantification_steps'),'active_nodes_at_open':c.get('active_nodes_at_open'),'final_active_nodes':c.get('final_active_nodes'),
            'maximum_nodes_seen':c.get('maximum_nodes_seen',c.get('maximum_nodes_seen_before_gc')),'nodes_created_total':c.get('nodes_created_total'),
            'restrict_calls_total':c.get('restrict_calls_total'),'hashcons_hits':c.get('hashcons_hits'),'partial_open_step':c.get('partial_open_step'),
        })
    return {
        'schema':'JANUS/TRUMP/R26/SHANNON_EXISTENTIAL_ORDER_SENSITIVITY_FORENSICS/AGGREGATE_RESULT/v1.0','created_date':'2026-09-02',
        'verdict':verdict,'order_count':len(ordered),'missing_orders':missing,'integrity_pass':integrity,'terminal_survivor_count':len(ranked),
        'terminal_survivor_order_ids':[r['order_id'] for r in ranked],'resource_selected_best_survivor':ranked[0]['order_id'] if ranked else None,
        'orders':compact,'truth_accessed':False,'semantic_verifier_ran':False,
        'interpretation':'Eight preregistered structure-only Shannon existential orders were tested with the exact frozen R18 machine and resource envelope. R26 has no semantic authority.',
        'claim_ceiling':prereg['claim_ceiling'],'seal':'NO_NINTH_ORDER_AFTER_THE_CLOCK_STOPS','P_VS_NP':'OPEN',
    }


def main():
    ap=argparse.ArgumentParser(); g=ap.add_mutually_exclusive_group(required=True); g.add_argument('--order',choices=ORDER_IDS); g.add_argument('--aggregate-dir'); ap.add_argument('--output',required=True); args=ap.parse_args()
    out=run_order(args.order) if args.order else aggregate_directory(Path(args.aggregate_dir))
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:out.get(k) for k in ('order_id','verdict','terminal_survivor','terminal_survivor_count','terminal_survivor_order_ids','resource_selected_best_survivor','P_VS_NP') if k in out},indent=2,sort_keys=True))
    return 2 if str(out.get('verdict','')).startswith('R26_FAIL') else 0


if __name__=='__main__': raise SystemExit(main())
