#!/usr/bin/env python3
"""R19 genuinely fresh prospective holdout for byte-frozen R18 shared-DAG candidate."""
from __future__ import annotations
import argparse,json,random
from pathlib import Path
import janus_trump_p_vs_np_direct_challenge_r0 as direct
import janus_trump_r8a_unseen_natural_holdout as r8a
import janus_trump_r9_reference_frame_difference_kernel as r9
import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_truth_blind_world_selector as selector

REPO=Path(__file__).resolve().parent.parent
FREEZE=REPO/'research'/'JANUS_TRUMP_R19_FRESH_PROSPECTIVE_UNSEEN_WORLD_SET_FREEZE_2026-09-02.json'
RESOURCE=REPO/'research'/'JANUS_TRUMP_R19_EXECUTION_RESOURCE_ENVELOPE_FREEZE_2026-09-02.json'
EXPECTED_BLOB='afa95321ec6edbb33bef222d8ee7234fe631a599'

def load_contracts():
    f=json.loads(FREEZE.read_text());r=json.loads(RESOURCE.read_text());assert f['status']=='FROZEN_BEFORE_R19_CANDIDATE_EXECUTION';assert r['status']=='FROZEN_BEFORE_R19_HARNESS_IMPLEMENTATION_AND_EXECUTION';assert len(f['worlds'])==10;assert f['frozen_candidate']['blob_sha']==r['candidate']['blob_sha']==EXPECTED_BLOB;return f,r

def generate_world(spec):
    d=selector.derive_spec(spec['suite'],spec['n'],spec['rep'])
    for k in ('seed','branch_value','m','k'): assert d[k]==spec[k],(spec['id'],k,d[k],spec[k])
    sat=r8a.load_legacy_sat_core();rng=random.Random(spec['seed']);inst=sat.gen_planted(spec['n'],spec['m'],3,rng) if spec['suite']=='PLANTED' else sat.gen_unsat_core(spec['n'],spec['m'],3,rng);root=direct.canon(inst.clauses);assert r8a.digest(root)==spec['root_sha256'];order,_=direct.occurrence_order(root);assert order and int(order[0])==spec['pivot'];fd=r9.restriction_frame_delta(root,spec['pivot'],spec['branch_value']);frame=tuple(fd['frame']);bridge=tuple(fd['active_bridge_vars']);checks={'frame_sha256':fd['frame_sha256']==spec['frame_sha256'],'delta_sha256':fd['delta_sha256']==spec['delta_sha256'],'bridge':list(bridge)==spec['bridge_vars'],'frame_clauses':len(frame)==spec['frame_clause_count'],'frame_vars':len({abs(l) for c in frame for l in c})==spec['frame_variable_count'],'frame_type':r9.classify_cnf(frame)==spec['frame_type']};assert all(checks.values()),(spec['id'],checks);return frame,bridge,checks

def run_world(wid):
    freeze,_=load_contracts();spec=next(w for w in freeze['worlds'] if w['id']==wid);frame,bridge,checks=generate_world(spec);fw=r18.candidate_firewall();candidate=r18.candidate_compile(frame,bridge);cs={k:v for k,v in candidate.items() if k not in ('dag','root')};base={'schema':'JANUS/TRUMP/R19/FRESH_PROSPECTIVE_UNSEEN_SHANNON_DAG_HOLDOUT/WORLD_RESULT/v1.0','created_date':'2026-09-02','world_id':wid,'source':spec,'regeneration_checks':checks,'candidate_blob_sha':EXPECTED_BLOB,'candidate_firewall':fw,'candidate':cs,'P_VS_NP':'OPEN'}
    if not fw['pass'] or candidate['status']=='FAIL_INTEGRITY':return {**base,'verdict':'FAIL_INTEGRITY','verifier':{'not_run':True}}
    if candidate['status']=='OPEN_RESOURCE_LIMIT':return {**base,'verdict':'OPEN_CANDIDATE_RESOURCE_LIMIT','verifier':{'not_run':True},'seal':'THE_FRESH_WORLD_HIT_THE_FROZEN_DAG_RESOURCE_WALL_BEFORE_TRUTH'}
    if candidate['status']!='COMPLETE_INTERFACE_DAG' or not set(candidate['final_support'])<=set(bridge):return {**base,'verdict':'FAIL_INTEGRITY','verifier':{'not_run':True},'reason':'TERMINAL_POSTCONDITION_FAIL'}
    original=r18.independent_original_allowed(frame,bridge);got=r18.candidate_allowed(candidate,bridge);exact=set(original['allowed_masks']);cand=set(got['allowed_masks']);fp=sorted(cand-exact);fn=sorted(exact-cand);comparison={'full_domain':True,'domain_size':1<<len(bridge),'original_allowed':len(exact),'candidate_allowed':len(cand),'false_positive_count':len(fp),'false_negative_count':len(fn),'first_false_positive_masks':fp[:32],'first_false_negative_masks':fn[:32],'original_truth_table_sha256':r18.mask_hash(original['allowed_masks']),'candidate_truth_table_sha256':r18.mask_hash(got['allowed_masks']),'original_sat_model_replay_failures':original['replay_failures'],'allowed_set_equal':not fp and not fn};verdict='PASS_EXACT_FRESH_UNSEEN' if comparison['allowed_set_equal'] and not original['replay_failures'] else 'MISMATCH_FRESH_UNSEEN';return {**base,'verdict':verdict,'verifier':{'original':{k:v for k,v in original.items() if k!='allowed_masks'},'candidate_evaluation':{k:v for k,v in got.items() if k!='allowed_masks'}},'comparison':comparison,'scientific_firewall':{'world_selected_before_candidate':True,'candidate_terminal_before_truth':True,'candidate_byte_frozen':True,'full_domain':True},'seal':'THE_HERO_MET_A_TRULY_FRESH_WORLD_AND_THE_WORLD_GRADED_THE_FULL_BRIDGE'}

def main():
    a=argparse.ArgumentParser();a.add_argument('--world',required=True);a.add_argument('--output',required=True);z=a.parse_args();d=run_world(z.world);Path(z.output).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({'world':d['world_id'],'verdict':d['verdict'],'n':d['source']['n'],'suite':d['source']['suite'],'bridge':d['source']['bridge_variable_count'],'candidate':d['candidate'],'comparison':d.get('comparison'),'P_VS_NP':'OPEN'},indent=2,sort_keys=True));return 2 if d['verdict']=='FAIL_INTEGRITY' else 0
if __name__=='__main__':raise SystemExit(main())
