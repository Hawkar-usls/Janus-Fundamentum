from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT/'research/TRUMP_SATLIB_UF20_03_CORRECTED_REDUCED_ORBIT_SAT_WITNESS_PROJECTED_RECONSTRUCTION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW = ROOT/'research/TRUMP_SATLIB_UF20_03_CORRECTED_REDUCED_ORBIT_SAT_WITNESS_PROJECTED_RECONSTRUCTION_PREREGISTRATION_REVIEW_2026-09-17_v1.0.json'
CAPTAIN = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_CORRECTED_REDUCED_EXISTING_ROUTE_CLOSURE_CAPTAIN_REVIEW_2026-09-17_v1.1.json'
ROUTE_RESULT = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_REDUCED_EXISTING_ROUTE_REEVALUATION_RESULT_2026-09-17_v1.1.json'
REDUCTION = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17_v1.1.json'
BOUNDARY = ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17.json'
SOURCE = ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf'
PROJECTION = ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
ORBIT = ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
EXPECTED = {
    PREREG:'9e05bd1e2a573e42a946ec37b0ec1558afca6d05',
    REVIEW:'3ed599ea6350114c776164570929e7d9e6c6085c',
    CAPTAIN:'3dccd091820e29148b704fb0975d290b070cad3c',
    ROUTE_RESULT:'623a88e42691e69730c7e64d8be6c0a37cea925a',
    REDUCTION:'d91cb675e3d06fed92f97d96d6b3a0733f8be5df',
    BOUNDARY:'3a9d46cb888489e769bab1e7d292e4eff459f786',
    SOURCE:'8f3d15154515457281f49201b843f2a7134dfa9f',
    PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
    ORBIT:'a076cfc56d68aad0348415e313705da1f6b9cdcd',
}


def blob(p:Path)->str:
    d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()

def csha(obj:Any)->str:
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()

def replay(raw:dict[str,Any], assignment:dict[int,int])->tuple[bool,list[str]]:
    bad=[]
    for c in raw['constraints']:
        row=tuple(int(assignment[int(v)]) for v in c['scope'])
        allowed={tuple(int(b) for b in t) for t in c['allowed']}
        if row not in allowed:bad.append(str(c['id']))
    return len(bad)==0,bad

def firewall()->dict[str,Any]:
    return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','UF20_03_FULL_CNF_SOLVED':'NOT_CLAIMED','PROJECTED_RAW_SAT_IMPLIES_FULL_CNF_SAT':False,'NEW_MECHANISM_LICENSED':False}

def main()->None:
    bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
    pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());route_result=json.loads(ROUTE_RESULT.read_text());reduction=json.loads(REDUCTION.read_text());boundary=json.loads(BOUNDARY.read_text())
    guards={
      'bindings':all(bindings.values()),
      'prereg_status':pre.get('status')=='FROZEN_BEFORE_WITNESS_MATERIALIZATION_OR_PROJECTED_RECONSTRUCTION',
      'review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE',
      'route_result_verdict':route_result.get('verdict')=='EXISTING_ROUTE_NEWLY_CLOSES_AT_LEAST_ONE_REDUCED_RAW',
      'reduction_pass':reduction.get('verdict')=='PASS_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION',
      'boundary_universal':boundary.get('verdict')=='ALL_ELEVEN_UNIVERSAL',
    }
    if not all(guards.values()):
        print(json.dumps({'verdict':'HALT_FROZEN_AUTHORITY_BINDING_FAILURE','guards':guards,'bindings':bindings,'scientific_firewall':firewall()},sort_keys=True));return
    parent={r['source']:r for r in reduction['source_receipts']}['UF20_03']
    original,_=projection_identity.normalize_projection('UF20_03',projection_identity.parse(SOURCE))
    if csha(original)!=pre['frozen_reduction_authority']['original_projected_raw_sha256']:
        print(json.dumps({'verdict':'HALT_FROZEN_AUTHORITY_BINDING_FAILURE','reason':'ORIGINAL_PROJECTED_SHA_MISMATCH','scientific_firewall':firewall()},sort_keys=True));return
    remove_ids=set(parent['removed_constraint_ids']);remove_leaves={int(v) for v in parent['removed_leaves']}
    reduced={'variables':[int(v) for v in original['variables'] if int(v) not in remove_leaves],'constraints':[c for c in original['constraints'] if c['id'] not in remove_ids]}
    reduced_sha=csha(reduced)
    if reduced_sha!=pre['parent_route_result']['reduced_raw_sha256'] or len(reduced['variables'])!=15 or len(reduced['constraints'])!=12:
        print(json.dumps({'verdict':'HALT_FROZEN_AUTHORITY_BINDING_FAILURE','reason':'REDUCED_IDENTITY_MISMATCH','reduced_sha256':reduced_sha,'scientific_firewall':firewall()},sort_keys=True));return
    orbit=orbit_candidate.run_candidate(reduced)
    if orbit.get('status')!='ADMIT_ORBIT_COUNT_QUOTIENT_SAT' or orbit.get('solver_authority') is not True or orbit.get('raw_semantic_sha256')!=pre['parent_route_result']['orbit_internal_semantic_sha256'] or orbit.get('quotient_states_Q')!=24576:
        print(json.dumps({'verdict':'FAIL_EXISTING_ORBIT_ROUTE_STATUS_DRIFT','observed_status':orbit.get('status'),'solver_authority':orbit.get('solver_authority'),'orbit_internal_semantic_sha256':orbit.get('raw_semantic_sha256'),'quotient_states_Q':orbit.get('quotient_states_Q'),'scientific_firewall':firewall()},sort_keys=True));return
    cert=orbit.get('certificate') or {}
    if cert.get('type')!='SAT' or not isinstance(cert.get('assignment'),list):
        print(json.dumps({'verdict':'FAIL_EXISTING_ORBIT_ROUTE_STATUS_DRIFT','reason':'SAT_CERTIFICATE_MISSING','scientific_firewall':firewall()},sort_keys=True));return
    reduced_assignment={int(v):int(b) for v,b in cert['assignment']}
    reduced_ok,reduced_bad=replay(reduced,reduced_assignment)
    if not reduced_ok:
        print(json.dumps({'verdict':'FAIL_REDUCED_WITNESS_REPLAY','violated_constraints':reduced_bad,'scientific_firewall':firewall()},sort_keys=True));return
    extended=dict(reduced_assignment);extension_receipts=[]
    for a in pre['frozen_extension_certificate']['attachments']:
        u,v=(int(x) for x in a['gateway']);leaf=int(a['leaf']);key=f'{extended[u]}{extended[v]}';bit=int(a['canonical_witnesses'][key]);extended[leaf]=bit
        extension_receipts.append({'constraint_id':a['constraint_id'],'gateway':[u,v],'gateway_key':key,'leaf':leaf,'selected_leaf_bit':bit})
    projected_ok,projected_bad=replay(original,extended)
    if not projected_ok:
        print(json.dumps({'verdict':'FAIL_PROJECTED_EXTENSION_REPLAY','violated_constraints':projected_bad,'extension_receipts':extension_receipts,'scientific_firewall':firewall()},sort_keys=True));return
    out={
      'artifact_id':'JANUS-TRUMP-SATLIB-UF20-03-CORRECTED-REDUCED-ORBIT-SAT-WITNESS-PROJECTED-RECONSTRUCTION-CANDIDATE-2026-09-17-v1.0',
      'authority':'CERTIFICATE_REPLAY_AND_FROZEN_RECONSTRUCTION_ONLY__NO_NEW_SOLVER_ROUTE_FEATURE_ACTION_GROUP_OR_REDUCTION',
      'verdict':'PASS_REDUCED_SAT_WITNESS_AND_PROJECTED_EXTENSION_REPLAY',
      'guards':guards,'bindings':bindings,
      'source':'UF20_03',
      'original_projected_raw_sha256':csha(original),
      'reduced_raw_sha256':reduced_sha,
      'orbit_receipt':{'status':orbit['status'],'solver_authority':True,'raw_semantic_sha256':orbit['raw_semantic_sha256'],'cells':orbit['cells'],'generator_edges':orbit['generator_edges'],'quotient_states_Q':orbit['quotient_states_Q'],'counts':cert.get('counts'),'resource_receipt':orbit.get('resource_receipt',{})},
      'reduced_sat_assignment':[[v,reduced_assignment[v]] for v in sorted(reduced_assignment)],
      'reduced_replay':{'constraints_replayed':len(reduced['constraints']),'all_true':True,'violated_constraints':[]},
      'extension_receipts':extension_receipts,
      'projected_sat_assignment':[[v,extended[v]] for v in sorted(extended)],
      'projected_replay':{'constraints_replayed':len(original['constraints']),'all_true':True,'violated_constraints':[]},
      'licensed_fact':{'statement':'THE_FROZEN_UF20_03_CORRECTED_ONE_ROUND_REDUCED_RAW_HAS_A_REPLAYED_EXISTING_ORBIT_COUNT_V1_SAT_CERTIFICATE_AND_THAT_ASSIGNMENT_EXTENDS_VIA_THE_FROZEN_CANONICAL_GATEWAY_WITNESS_TABLES_TO_A_SATISFYING_ASSIGNMENT_OF_THE_FROZEN_UF20_03_R000_R111_ORIGINAL_PROJECTED_RAW','scope':'UF20_03_FROZEN_PROJECTED_RAW_ONLY'},
      'resource_receipt':{'target_sources':1,'reduction_rounds':0,'new_reduction_targets':0,'new_solver_mechanisms':0,'new_action_families':0,'new_group_searches':0,'fresh_holdout_values_read':0,'full_cnf_equivalence_tests':0,'budget_raise':False},
      'scientific_firewall':firewall()
    }
    print(json.dumps(out,sort_keys=True,separators=(',',':')))

if __name__=='__main__':main()
