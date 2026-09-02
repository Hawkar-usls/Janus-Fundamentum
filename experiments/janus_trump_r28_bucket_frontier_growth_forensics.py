#!/usr/bin/env python3
"""R28 replay-only observer for frozen R27 bucket-frontier growth.

No candidate logic is implemented here.  The observer calls byte-frozen
r27.compile_factored once on the same exposed W05 frame and serializes/analyzes
the trajectory that R27 already produced internally.  Semantic truth is absent.
"""
from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path

import janus_trump_r19_fresh_unseen_dag_holdout as r19
import janus_trump_r27_local_bucket_factored_shannon_elimination_discovery as r27

HERE=Path(__file__).resolve().parent
REPO=HERE.parent
PREREG_PATH=REPO/'research'/'JANUS_TRUMP_R28_BUCKET_FRONTIER_GROWTH_FORENSICS_PREREGISTRATION_2026-09-02.json'
WORLD_ID='R19-W05'
EXPECTED_FRAME_SHA='cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384'
EXPECTED_R27_BLOB='ff1139a4da7e9eaf43945995db95a6d22fb45dbe'


def load_prereg():
    d=json.loads(PREREG_PATH.read_text(encoding='utf-8'))
    assert d['status']=='FROZEN_BEFORE_R28_OBSERVER_IMPLEMENTATION_AND_REPLAY'
    assert d['parent_R27_result_summary_commit']=='55c18e317d7a8081dc5ce6c20ee11e7d59f71cb8'
    assert d['frozen_R27_candidate']['git_blob_sha']==EXPECTED_R27_BLOB
    assert d['observer_contract']['candidate_mutation'] is False
    return d


def deterministic_summary(candidate):
    p=candidate.get('partial_open_step') or {}
    return {
        'status':candidate.get('status'),'reason':candidate.get('reason'),'completed_quantification_steps':candidate.get('completed_quantification_steps'),
        'active_nodes_at_open':candidate.get('active_nodes_at_open'),'maximum_live_nodes':candidate.get('maximum_live_nodes'),
        'nodes_created_total':candidate.get('nodes_created_total'),'restrict_calls_total':candidate.get('restrict_calls_total'),
        'hashcons_hits':candidate.get('hashcons_hits'),'gc_calls':candidate.get('gc_calls'),'gc_removed_total':candidate.get('gc_removed_total'),
        'partial_open_step':{
            'step':p.get('step'),'quantified_var':p.get('quantified_var'),'factor_count_before':p.get('factor_count_before'),'bucket_factor_count':p.get('bucket_factor_count'),
            'bucket_union_support_size':p.get('bucket_union_support_size'),'before_live_nodes':p.get('before_live_nodes'),'active_nodes_at_open':p.get('active_nodes_at_open'),
            'partial_nodes_created_step':p.get('partial_nodes_created_step'),'partial_restrict_calls_step':p.get('partial_restrict_calls_step'),'partial_hashcons_hits_step':p.get('partial_hashcons_hits_step'),
        }
    }


def equivalence_check(candidate,prereg):
    got=deterministic_summary(candidate); ref=prereg['R27_equivalence_reference']
    checks={}
    for k,v in ref.items():
        if k!='partial_open_step': checks[k]=got.get(k)==v
    for k,v in ref['partial_open_step'].items(): checks['partial_open_step.'+k]=got['partial_open_step'].get(k)==v
    return {'pass':all(checks.values()),'checks':checks,'expected':ref,'observed':got}


def first_crossing(traj,field,threshold):
    row=next((r for r in traj if int(r[field])>=threshold),None)
    return None if row is None else {'step':row['step'],'quantified_var':row['quantified_var'],'value':row[field]}


def analyze_trajectory(candidate):
    traj=list(candidate.get('trajectory',[]))
    enriched=[]
    for r in traj:
        before=max(1,int(r['before_live_nodes'])); after=int(r['after_gc_live_nodes']); pre=int(r['pre_gc_live_nodes'])
        enriched.append({**r,'after_gc_live_delta':after-before,'after_gc_live_growth_factor':after/before,'temporary_live_growth_factor':pre/before,'gc_survival_fraction':after/pre if pre else 0.0})
    max_delta=max(enriched,key=lambda r:r['after_gc_live_delta'],default=None)
    max_factor=max(enriched,key=lambda r:r['after_gc_live_growth_factor'],default=None)
    max_created=max(enriched,key=lambda r:r['new_nodes_created_step'],default=None)
    max_restrict=max(enriched,key=lambda r:r['restrict_calls_step'],default=None)
    return {
        'trajectory':enriched,
        'bucket_support_crossings':{str(t):first_crossing(enriched,'bucket_union_support_size',t) for t in (20,30,40)},
        'after_gc_live_crossings':{str(t):first_crossing(enriched,'after_gc_live_nodes',t) for t in (10000,50000,100000,250000,500000)},
        'maximum_completed_step_live_growth_delta':None if max_delta is None else {'step':max_delta['step'],'quantified_var':max_delta['quantified_var'],'value':max_delta['after_gc_live_delta'],'bucket_support':max_delta['bucket_union_support_size'],'bucket_factors':max_delta['bucket_factor_count']},
        'maximum_completed_step_live_growth_factor':None if max_factor is None else {'step':max_factor['step'],'quantified_var':max_factor['quantified_var'],'value':max_factor['after_gc_live_growth_factor'],'bucket_support':max_factor['bucket_union_support_size'],'bucket_factors':max_factor['bucket_factor_count']},
        'maximum_completed_step_nodes_created':None if max_created is None else {'step':max_created['step'],'quantified_var':max_created['quantified_var'],'value':max_created['new_nodes_created_step'],'bucket_support':max_created['bucket_union_support_size'],'bucket_factors':max_created['bucket_factor_count']},
        'maximum_completed_step_restrict_calls':None if max_restrict is None else {'step':max_restrict['step'],'quantified_var':max_restrict['quantified_var'],'value':max_restrict['restrict_calls_step'],'bucket_support':max_restrict['bucket_union_support_size'],'bucket_factors':max_restrict['bucket_factor_count']},
        'partial_open_step':candidate.get('partial_open_step'),
    }


def observer_firewall():
    src='\n'.join(inspect.getsource(f) for f in (deterministic_summary,equivalence_check,first_crossing,analyze_trajectory,run))
    forbidden=['Solver(','solve(','allowed_masks','truth_table','candidate_allowed','independent_original_allowed','range(1 <<','dpll(','resolve_on(']
    hits=[x for x in forbidden if x in src]
    return {'pass':not hits,'forbidden_hits':hits}


def run():
    prereg=load_prereg(); freeze=r19.load_freeze(); spec=next(w for w in freeze['worlds'] if w['id']==WORLD_ID); world=r19.generate_frozen_world(spec)
    frame=tuple(world['frame']); bridge=tuple(world['bridge'])
    if spec['frame_sha256']!=EXPECTED_FRAME_SHA: raise AssertionError('R19-W05 frame drift')
    fw=observer_firewall(); candidate,_live=r27.compile_factored(frame,bridge); eq=equivalence_check(candidate,prereg)
    analysis=analyze_trajectory(candidate) if eq['pass'] and fw['pass'] else None
    verdict='R28_BUCKET_FRONTIER_TRAJECTORY_CAPTURED' if eq['pass'] and fw['pass'] else 'R28_FAIL_OBSERVER_EQUIVALENCE'
    return {
        'schema':'JANUS/TRUMP/R28/BUCKET_FRONTIER_GROWTH_FORENSICS/RESULT/v1.0','created_date':'2026-09-02','scientific_role':'REPLAY_ONLY_RESOURCE_FORENSICS__NO_SEMANTIC_TRUTH',
        'world_id':WORLD_ID,'frame_sha256':EXPECTED_FRAME_SHA,'frozen_R27_blob':EXPECTED_R27_BLOB,'verdict':verdict,'observer_firewall':fw,'R27_observer_equivalence':eq,
        'analysis':analysis,'truth_accessed':False,'semantic_verifier_ran':False,'claim_ceiling':prereg['claim_ceiling'],'seal':'THE_CAMERA_RECORDED_THE_FROZEN_BUCKET_MACHINE_WITHOUT_TOUCHING_IT','P_VS_NP':'OPEN'
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True); args=ap.parse_args(); out=run(); Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    a=out.get('analysis') or {}; print(json.dumps({'verdict':out['verdict'],'equivalence':out['R27_observer_equivalence']['pass'],'bucket_support_crossings':a.get('bucket_support_crossings'),'after_gc_live_crossings':a.get('after_gc_live_crossings'),'max_live_delta':a.get('maximum_completed_step_live_growth_delta'),'partial_open_step':a.get('partial_open_step'),'P_VS_NP':'OPEN'},indent=2,sort_keys=True)); return 2 if out['verdict'].startswith('R28_FAIL') else 0

if __name__=='__main__': raise SystemExit(main())
