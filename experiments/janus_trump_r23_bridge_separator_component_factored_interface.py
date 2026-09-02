#!/usr/bin/env python3
"""R23 exposed discovery: keep bridge-separated internal components independent.

Candidate lane uses only frozen CNF structure plus the sealed R18 Boolean DAG
operators.  The frozen bridge B is the only separator.  Internal connected
components after removing B are compiled and existentially quantified locally;
the resulting bridge-only factors are never materialized into one global DAG.
Semantic truth is available only after a terminal factor set exists.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import time
from dataclasses import dataclass
from pathlib import Path

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_unseen_dag_holdout as r19

HERE=Path(__file__).resolve().parent
REPO=HERE.parent
PREREG_PATH=REPO/'research'/'JANUS_TRUMP_R23_BRIDGE_SEPARATOR_COMPONENT_FACTORED_INTERFACE_PREREGISTRATION_2026-09-02.json'
WORLD_ID='R19-W05'
EXPECTED_FRAME_SHA='cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384'
WALL_SECONDS=120.0
MAX_TOTAL_LIVE=1_000_000
MAX_TOTAL_CREATED=5_000_000
MAX_TOTAL_RESTRICT=20_000_000
MAX_COMPONENTS=1_000


def load_prereg():
    d=json.loads(PREREG_PATH.read_text(encoding='utf-8'))
    assert d['status']=='FROZEN_BEFORE_R23_IMPLEMENTATION_AND_EXECUTION'
    assert d['parent_R22_result_summary_commit']=='fc46806c93346ee088fc94847e1d0f2296bffc8c'
    assert d['representation_contract']['separator']=='THE_FROZEN_R19_W05_BRIDGE_VARIABLE_SET_B_ONLY'
    assert d['resource_envelope']['wall_seconds_total']==120
    assert d['candidate_firewall']['global_monolithic_BDD_or_DAG_build_forbidden'] is True
    return d


def internal_components(frame,bridge):
    bridge_set=set(int(v) for v in bridge)
    internal=sorted({abs(int(l)) for c in frame for l in c}-bridge_set)
    adj={v:set() for v in internal}
    for clause in frame:
        vs=sorted({abs(int(l)) for l in clause if abs(int(l)) not in bridge_set})
        for i,a in enumerate(vs):
            for b in vs[i+1:]:
                adj[a].add(b); adj[b].add(a)
    unseen=set(internal); comps=[]
    while unseen:
        start=min(unseen); unseen.remove(start); stack=[start]; comp=[]
        while stack:
            v=stack.pop(); comp.append(v)
            for w in sorted(adj[v],reverse=True):
                if w in unseen:
                    unseen.remove(w); stack.append(w)
        comps.append(tuple(sorted(comp)))
    comps.sort()
    return tuple(comps)


def partition_clauses(frame,bridge,components):
    bridge_set=set(int(v) for v in bridge)
    owner={v:i for i,c in enumerate(components) for v in c}
    buckets=[[] for _ in components]; bridge_only=[]
    for clause in frame:
        ivars=sorted({abs(int(l)) for l in clause if abs(int(l)) not in bridge_set})
        if not ivars:
            bridge_only.append(tuple(clause)); continue
        ids={owner.get(v) for v in ivars}
        if None in ids or len(ids)!=1:
            raise ValueError(f'PRIMAL_COMPONENT_PARTITION_INTEGRITY_FAIL:{clause}:{ids}')
        buckets[next(iter(ids))].append(tuple(clause))
    return tuple(tuple(x) for x in buckets),tuple(bridge_only)


def local_bridge_support(clauses,bridge):
    present={abs(int(l)) for c in clauses for l in c}
    return tuple(v for v in bridge if int(v) in present)


class GlobalBudget(r18.Budget):
    def check(self):
        super().check()
        if self.restrict_calls>MAX_TOTAL_RESTRICT:
            raise r18.ResourceLimit('GLOBAL_RESTRICT_CALL_CAP')
        if self.nodes_created_total>MAX_TOTAL_CREATED:
            raise r18.ResourceLimit('GLOBAL_NODE_CREATION_CAP')


class FactorDag(r18.Dag):
    def __init__(self,budget,retained_live,max_global_live):
        self._retained_live=retained_live
        self._max_global_live=max_global_live
        super().__init__(budget)
        self._observe_global_live()
    def _observe_global_live(self):
        cur=self._retained_live[0]+len(self.nodes)
        self._max_global_live[0]=max(self._max_global_live[0],cur)
        if cur>MAX_TOTAL_LIVE:
            raise r18.ResourceLimit('GLOBAL_LIVE_NODE_CAP')
    def _check_nodes(self):
        self.budget.check()
        if len(self.nodes)>=r18.MAX_NODES:
            raise r18.ResourceLimit('NODE_CAP')
        if self._retained_live[0]+len(self.nodes)>=MAX_TOTAL_LIVE:
            raise r18.ResourceLimit('GLOBAL_LIVE_NODE_CAP')
        self._observe_global_live()
    def gc(self,root):
        removed=super().gc(root)
        self._observe_global_live()
        return removed


def support_vars(dag,root,max_var):
    return tuple(v for v in range(1,max_var+1) if dag.support[root] & (1<<(v-1)))


def compile_one_factor(label,clauses,bridge,budget,retained_live,max_global_live):
    dag=FactorDag(budget,retained_live,max_global_live)
    started=time.monotonic(); created_before=budget.nodes_created_total; restrict_before=budget.restrict_calls
    root=r18.compile_cnf(dag,clauses)
    dag.gc(root)
    order=r18.elimination_order(clauses,bridge)
    trajectory=[]
    for step,var in enumerate(order,start=1):
        before=len(dag.nodes); calls0=budget.restrict_calls; created0=budget.nodes_created_total; hits0=dag.hashcons_hits
        root,memo_entries=dag.exists(root,var)
        pre_gc=len(dag.nodes); removed=dag.gc(root); after=len(dag.nodes)
        trajectory.append({
            'step':step,'quantified_var':int(var),'before_active_nodes':before,'pre_gc_nodes':pre_gc,'after_active_nodes':after,
            'gc_removed_nodes':removed,'new_nodes_created_step':budget.nodes_created_total-created0,
            'restrict_calls_step':budget.restrict_calls-calls0,'restrict_memo_entries_step':memo_entries,
            'hashcons_hits_step':dag.hashcons_hits-hits0,
        })
    max_var=max({abs(int(l)) for c in clauses for l in c},default=0)
    final_support=support_vars(dag,root,max_var)
    bridge_set=set(int(v) for v in bridge)
    if not set(final_support)<=bridge_set:
        raise ValueError(f'LOCAL_FACTOR_SUPPORT_NOT_BRIDGE_ONLY:{label}:{final_support}')
    summary={
        'label':label,'clause_count':len(clauses),'local_bridge_support':list(bridge),'elimination_order':list(order),
        'quantified_internal_count':len(order),'elapsed_seconds':time.monotonic()-started,
        'final_active_nodes':len(dag.nodes),'maximum_nodes_seen':dag.max_nodes_seen,
        'nodes_created_factor':budget.nodes_created_total-created_before,'restrict_calls_factor':budget.restrict_calls-restrict_before,
        'hashcons_hits':dag.hashcons_hits,'gc_calls':dag.gc_calls,'gc_removed_total':dag.gc_removed_total,
        'final_support':list(final_support),'trajectory':trajectory,
    }
    retained_live[0]+=len(dag.nodes)
    max_global_live[0]=max(max_global_live[0],retained_live[0])
    if retained_live[0]>MAX_TOTAL_LIVE:
        raise r18.ResourceLimit('GLOBAL_LIVE_NODE_CAP')
    return {'dag':dag,'root':root,'summary':summary}


def candidate_compile_factored(frame,bridge):
    started=time.monotonic(); comps=internal_components(frame,bridge)
    if len(comps)>MAX_COMPONENTS:
        return {'status':'OPEN_RESOURCE_LIMIT','reason':'COMPONENT_COUNT_CAP','components':len(comps),'elapsed_seconds':time.monotonic()-started},[]
    buckets,bridge_only=partition_clauses(frame,bridge,comps)
    structural={
        'internal_component_count':len(comps),
        'internal_components':[list(c) for c in comps],
        'component_sizes':[len(c) for c in comps],
        'component_clause_counts':[len(b) for b in buckets],
        'bridge_only_clause_count':len(bridge_only),
        'largest_internal_component':max((len(c) for c in comps),default=0),
        'largest_component_clause_count':max((len(b) for b in buckets),default=0),
    }
    if len(comps)<2:
        return {'status':'NO_BRIDGE_SEPARATOR_DECOMPOSITION','reason':'INTERNAL_GRAPH_CONNECTED_AFTER_BRIDGE_REMOVAL','structural':structural,'elapsed_seconds':time.monotonic()-started},[]
    budget=GlobalBudget(deadline=started+WALL_SECONDS)
    retained_live=[0]; max_global_live=[0]; factors=[]; summaries=[]
    try:
        if bridge_only:
            f=compile_one_factor('BRIDGE_ONLY',bridge_only,tuple(bridge),budget,retained_live,max_global_live)
            factors.append(f); summaries.append(f['summary'])
        for i,(comp,clauses) in enumerate(zip(comps,buckets),start=1):
            if not clauses:
                raise ValueError(f'EMPTY_COMPONENT_CLAUSE_BUCKET:{i}:{comp}')
            local_bridge=local_bridge_support(clauses,bridge)
            f=compile_one_factor(f'COMPONENT_{i:03d}',clauses,local_bridge,budget,retained_live,max_global_live)
            factors.append(f); summaries.append(f['summary'])
        all_internal={v for c in comps for v in c}
        expected_internal={abs(int(l)) for c in frame for l in c}-set(int(v) for v in bridge)
        if all_internal!=expected_internal:
            raise ValueError('INTERNAL_COMPONENT_COVERAGE_FAIL')
        return {
            'status':'COMPLETE_FACTORED_BRIDGE_INTERFACE','elapsed_seconds':time.monotonic()-started,'structural':structural,
            'factor_count':len(factors),'factors':summaries,'total_retained_live_nodes':retained_live[0],
            'maximum_global_live_nodes':max_global_live[0],'total_nodes_created':budget.nodes_created_total,
            'total_restrict_calls':budget.restrict_calls,
        },factors
    except r18.ResourceLimit as e:
        return {
            'status':'OPEN_RESOURCE_LIMIT','reason':e.reason,'elapsed_seconds':time.monotonic()-started,'structural':structural,
            'completed_factor_count':len(factors),'completed_factors':summaries,'total_retained_live_nodes':retained_live[0],
            'maximum_global_live_nodes':max_global_live[0],'total_nodes_created':budget.nodes_created_total,
            'total_restrict_calls':budget.restrict_calls,
        },factors
    except ValueError as e:
        return {'status':'FAIL_INTEGRITY','reason':str(e),'elapsed_seconds':time.monotonic()-started,'structural':structural},factors


def candidate_firewall():
    funcs=[internal_components,partition_clauses,local_bridge_support,GlobalBudget,FactorDag,support_vars,compile_one_factor,candidate_compile_factored]
    src='\n'.join(inspect.getsource(f) for f in funcs)
    forbidden=['Solver(','solve(','range(1 <<','allowed_masks','truth_table','independent_original_allowed','candidate_allowed','dpll(','resolve_on(']
    hits=[x for x in forbidden if x in src]
    return {'pass':not hits,'forbidden_hits':hits}


def factor_allowed(factors,bridge):
    allowed=[]; started=time.monotonic()
    for mask in range(1<<len(bridge)):
        assignment={int(v):bool((mask>>i)&1) for i,v in enumerate(bridge)}
        if all(f['dag'].evaluate(f['root'],assignment) for f in factors):
            allowed.append(mask)
    return {'allowed_masks':allowed,'allowed_count':len(allowed),'elapsed_seconds':time.monotonic()-started}


def mask_hash(masks):
    return hashlib.sha256(json.dumps(list(masks),separators=(',',':')).encode()).hexdigest()


def tiny_structural_control():
    # B={10}; internal components {1,2} and {3,4}; no clause couples the components except through B.
    frame=((1,2,10),(-1,2),(3,4,-10),(-3,4),(10,))
    comps=internal_components(frame,(10,))
    buckets,bo=partition_clauses(frame,(10,),comps)
    return comps==((1,2),(3,4)) and tuple(map(len,buckets))==(2,2) and len(bo)==1


def run():
    prereg=load_prereg(); freeze=r19.load_freeze(); spec=next(w for w in freeze['worlds'] if w['id']==WORLD_ID); world=r19.generate_frozen_world(spec)
    if spec['frame_sha256']!=EXPECTED_FRAME_SHA: raise AssertionError('R19-W05 frame drift')
    frame=tuple(world['frame']); bridge=tuple(world['bridge']); fw=candidate_firewall(); tiny=tiny_structural_control()
    base={
        'schema':'JANUS/TRUMP/R23/BRIDGE_SEPARATOR_COMPONENT_FACTORED_INTERFACE/RESULT/v1.0','created_date':'2026-09-02',
        'world':{'id':WORLD_ID,'frame_sha256':EXPECTED_FRAME_SHA,'frame_clauses':len(frame),'bridge_vars':list(bridge)},
        'candidate_firewall':fw,'tiny_structural_control':tiny,'P_VS_NP':'OPEN',
    }
    if not fw['pass'] or not tiny:
        return {**base,'verdict':'R23_FAIL_INTEGRITY','candidate':{'not_run':True},'verifier':{'not_run':True}}
    candidate,factors=candidate_compile_factored(frame,bridge)
    if candidate['status']=='NO_BRIDGE_SEPARATOR_DECOMPOSITION':
        return {**base,'verdict':'R23_NO_BRIDGE_SEPARATOR_DECOMPOSITION','candidate':candidate,'verifier':{'not_run':True},'truth_accessed':False}
    if candidate['status']=='OPEN_RESOURCE_LIMIT':
        return {**base,'verdict':'R23_OPEN_RESOURCE_LIMIT__NO_SEMANTIC_VERDICT','candidate':candidate,'verifier':{'not_run':True},'truth_accessed':False}
    if candidate['status']=='FAIL_INTEGRITY':
        return {**base,'verdict':'R23_FAIL_INTEGRITY','candidate':candidate,'verifier':{'not_run':True},'truth_accessed':False}
    if candidate['status']!='COMPLETE_FACTORED_BRIDGE_INTERFACE':
        return {**base,'verdict':'R23_FAIL_INTEGRITY','candidate':candidate,'verifier':{'not_run':True},'truth_accessed':False}
    verifier_started=time.monotonic()
    original=r18.independent_original_allowed(frame,bridge)
    got=factor_allowed(factors,bridge)
    if original.get('replay_failures'):
        return {**base,'verdict':'R23_FAIL_INTEGRITY','candidate':candidate,'verifier':{'original':{k:v for k,v in original.items() if k!='allowed_masks'}},'truth_accessed':True,'reason':'ORIGINAL_MODEL_REPLAY_FAIL'}
    exact=set(original['allowed_masks']); have=set(got['allowed_masks']); fp=sorted(have-exact); fn=sorted(exact-have); match=not fp and not fn
    comparison={
        'full_domain':True,'domain_size':1<<len(bridge),'allowed_set_equal':match,
        'original_allowed':len(exact),'candidate_allowed':len(have),'false_positive_count':len(fp),'false_negative_count':len(fn),
        'first_false_positive_masks':fp[:32],'first_false_negative_masks':fn[:32],
        'original_truth_table_sha256':mask_hash(original['allowed_masks']),'candidate_truth_table_sha256':mask_hash(got['allowed_masks']),
        'original_sat_model_replay_failures':original.get('replay_failures',[]),
    }
    verdict='R23_EXPOSED_W05_FACTORED_INTERFACE_FULL_DOMAIN_MATCH' if match else 'R23_EXPOSED_W05_FACTORED_INTERFACE_SEMANTIC_MISMATCH'
    return {
        **base,'verdict':verdict,'candidate':candidate,
        'verifier':{'started_after_candidate_terminal':True,'elapsed_seconds':time.monotonic()-verifier_started},
        'comparison':comparison,'truth_accessed':True,
        'claim_ceiling':prereg['claim_ceiling'],
        'seal':'THE_INTERNAL_ROOMS_STAYED_SEPARATE__ONLY_THE_FROZEN_BRIDGE_CONNECTED_THEIR_ANSWERS',
        'P_VS_NP':'OPEN',
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); args=ap.parse_args(); out=run();
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'verdict':out['verdict'],'candidate':{k:v for k,v in out.get('candidate',{}).items() if k not in ('factors','completed_factors')},'comparison':out.get('comparison'),'truth_accessed':out.get('truth_accessed'),'P_VS_NP':'OPEN'},indent=2,sort_keys=True))
    return 2 if out['verdict']=='R23_FAIL_INTEGRITY' else 0


if __name__=='__main__': raise SystemExit(main())
