from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from typing import Any
from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate
ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_03_CORRECTED_REDUCED_ORBIT_SAT_WITNESS_PROJECTED_RECONSTRUCTION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_03_CORRECTED_REDUCED_ORBIT_SAT_WITNESS_PROJECTED_RECONSTRUCTION_PREREGISTRATION_REVIEW_2026-09-17_v1.0.json'
CAND=ROOT/'research/tools/apma_satlib_uf20_03_reduced_orbit_sat_witness_projected_reconstruction/candidate.py'
REDUCTION=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17_v1.1.json'
SOURCE=ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
ORBIT=ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
EXPECTED={PREREG:'9e05bd1e2a573e42a946ec37b0ec1558afca6d05',REVIEW:'3ed599ea6350114c776164570929e7d9e6c6085c',CAND:'05c3684f66f7c02d55c7b4367e210c5bfe122f63',REDUCTION:'d91cb675e3d06fed92f97d96d6b3a0733f8be5df',SOURCE:'8f3d15154515457281f49201b843f2a7134dfa9f',PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',ORBIT:'a076cfc56d68aad0348415e313705da1f6b9cdcd'}
def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(o:Any)->str:return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def replay(raw,a):
 bad=[]
 for c in raw['constraints']:
  row=tuple(int(a[int(v)]) for v in c['scope']);allowed={tuple(int(b) for b in t) for t in c['allowed']}
  if row not in allowed:bad.append(str(c['id']))
 return not bad,bad
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);args=ap.parse_args();cand=json.loads(Path(args.candidate_json).read_text().strip().splitlines()[-1])
 binds={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()};pre=json.loads(PREREG.read_text());rev=json.loads(REVIEW.read_text());red=json.loads(REDUCTION.read_text())
 if not all(binds.values()) or rev.get('verdict')!='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE':
  print(json.dumps({'verified':False,'candidate_imported':False,'reason':'FROZEN_BINDING_FAILURE','bindings':binds},sort_keys=True));return
 parent={r['source']:r for r in red['source_receipts']}['UF20_03'];original,_=projection_identity.normalize_projection('UF20_03',projection_identity.parse(SOURCE));remove_ids=set(parent['removed_constraint_ids']);remove_leaves={int(v) for v in parent['removed_leaves']};reduced={'variables':[int(v) for v in original['variables'] if int(v) not in remove_leaves],'constraints':[c for c in original['constraints'] if c['id'] not in remove_ids]}
 orbit=orbit_candidate.run_candidate(reduced);cert=orbit.get('certificate') or {};ra={int(v):int(b) for v,b in cert.get('assignment',[])};rok,rbad=replay(reduced,ra) if ra else (False,['NO_ASSIGNMENT']);extended=dict(ra);ext=[]
 if rok:
  for x in pre['frozen_extension_certificate']['attachments']:
   u,v=map(int,x['gateway']);leaf=int(x['leaf']);key=f'{extended[u]}{extended[v]}';bit=int(x['canonical_witnesses'][key]);extended[leaf]=bit;ext.append({'constraint_id':x['constraint_id'],'gateway':[u,v],'gateway_key':key,'leaf':leaf,'selected_leaf_bit':bit})
 pok,pbad=replay(original,extended) if rok else (False,['REDUCED_REPLAY_FAILED'])
 expected={'verdict':'PASS_REDUCED_SAT_WITNESS_AND_PROJECTED_EXTENSION_REPLAY','source':'UF20_03','original_projected_raw_sha256':csha(original),'reduced_raw_sha256':csha(reduced),'orbit_status':orbit.get('status'),'solver_authority':orbit.get('solver_authority'),'orbit_semantic_sha256':orbit.get('raw_semantic_sha256'),'Q':orbit.get('quotient_states_Q'),'reduced_assignment':[[v,ra[v]] for v in sorted(ra)],'extension_receipts':ext,'projected_assignment':[[v,extended[v]] for v in sorted(extended)],'reduced_ok':rok,'projected_ok':pok}
 checks={'candidate_verdict':cand.get('verdict')==expected['verdict'],'source':cand.get('source')=='UF20_03','original_sha':cand.get('original_projected_raw_sha256')==expected['original_projected_raw_sha256']=='30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d','reduced_sha':cand.get('reduced_raw_sha256')==expected['reduced_raw_sha256']=='cf91266425d38475c03dfae3547e809b7c8fdf1ed55ab5f4548785d5acf7b70a','route_status':expected['orbit_status']=='ADMIT_ORBIT_COUNT_QUOTIENT_SAT' and expected['solver_authority'] is True and expected['orbit_semantic_sha256']=='7f8f35aada56b3f174ebd86b095f20b1d32e21701839687a8e2a4a3f09ed01af' and expected['Q']==24576,'reduced_replay':rok and cand.get('reduced_replay',{}).get('all_true') is True and cand.get('reduced_sat_assignment')==expected['reduced_assignment'],'extension':cand.get('extension_receipts')==ext,'projected_replay':pok and cand.get('projected_replay',{}).get('all_true') is True and cand.get('projected_sat_assignment')==expected['projected_assignment'],'no_full_cnf':cand.get('resource_receipt',{}).get('full_cnf_equivalence_tests')==0,'holdout_zero':cand.get('resource_receipt',{}).get('fresh_holdout_values_read')==0}
 print(json.dumps({'verified':all(checks.values()),'candidate_imported':False,'verdict':expected['verdict'],'checks':checks,'reduced_sat_assignment':expected['reduced_assignment'],'extension_receipts':ext,'projected_sat_assignment':expected['projected_assignment'],'reduced_violations':rbad,'projected_violations':pbad,'bindings':binds},sort_keys=True,separators=(',',':')))
if __name__=='__main__':main()
