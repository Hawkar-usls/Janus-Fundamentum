from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_connected_mixed_post_orbit_obstruction_census import census as reference_census
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate
from research.tools.apma_uf20_wl_historical_closed_control_falsifier import candidate as wl_ref

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_UF20_011_015_FRESH_GENERIC_PENDANT_WL_EXISTING_PORTFOLIO_REPLICATION_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW=ROOT/'research/TRUMP_UF20_011_015_FRESH_GENERIC_PENDANT_WL_EXISTING_PORTFOLIO_REPLICATION_REVIEW_2026-09-17_v1.0.json'
THEOREM=ROOT/'research/TRUMP_SOURCE_AGNOSTIC_3CNF_DEGREE1_PENDANT_ONE_ROUND_THEOREM_RESULT_2026-09-17_v1.0.json'
SOURCE_FREEZE=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
RAW_BASIS=ROOT/'research/tools/apma_unseen_basis/raw_relation_basis.py'
COMPOSITIONAL=ROOT/'research/tools/apma_unseen_basis/compositional_basis.py'
REFERENCE=ROOT/'research/tools/apma_connected_mixed_post_orbit_obstruction_census/census.py'
LOG_ALIEN=ROOT/'research/tools/apma_log_alien_transfer/log_alien_transfer.py'
ORBIT=ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py'
WL_REF=ROOT/'research/tools/apma_uf20_wl_historical_closed_control_falsifier/candidate.py'
EXPECTED={
 PREREG:'b64f7c5f3191041c2452020a28a23dd4f1e84a80',REVIEW:'5561d7b4419b4e9ba1a3acc8d61c26c7d9b8b825',THEOREM:'72f175ecd31708b09cba2fe13cfd2eeacdcf4c4b',SOURCE_FREEZE:'3ee5a11808ea04326ec5141b0138bbba4ec56092',
 PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',RAW_BASIS:'63490c05ef3e91a4f682f75da26ff2af811839a6',COMPOSITIONAL:'fdc83a3368a4ad362f00d3ee8aad958f06f8d264',REFERENCE:'f5aa39804983d49149c976e8367a96397bad888e',LOG_ALIEN:'d20cd94fa2e0324e301f55211152c2d410099425',ORBIT:'a076cfc56d68aad0348415e313705da1f6b9cdcd',WL_REF:'6b697fd8b3de4c83f8226b06399b6bad99953d4e'}
TRAINING={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','8ff66183320ed0516fb0573b0cbe76aa4c0717af8f0bf83d69813a1c837fe37f'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','cf91266425d38475c03dfae3547e809b7c8fdf1ed55ab5f4548785d5acf7b70a'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','3f26b47e41720f2acca5e6fb5444a8b17db566d650e73e911a78969f67975c27'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','f41ebed66be06fc7d22ca64a988aefee00a6d46a1831d2636dcee94e2f5036e2')}
HOLDOUT={
 'UF20_011':(ROOT/'research/source_data/SATLIB_UF20_011_2026-09-17.cnf','d693e2c019a1ceb7abe1bf1c29ffd57d25cde01b','dc043cb67fef03567bcbae82f82a66ee53c476f5d2d91bb5606aa56f9213a7e7'),
 'UF20_012':(ROOT/'research/source_data/SATLIB_UF20_012_2026-09-17.cnf','745e26942701ca6bcb3f9708e9306d7e6385ecdc','6c7750381472768e5f889be53a682316585ea09149b13d8da4070287b9dab705'),
 'UF20_013':(ROOT/'research/source_data/SATLIB_UF20_013_2026-09-17.cnf','62349f4152b5ce1576e380242e7d62bbe2099907','bf4b24d389929b0d3fe8ed25f34077283c745d9fdcc713c57827a7cec272ce42'),
 'UF20_014':(ROOT/'research/source_data/SATLIB_UF20_014_2026-09-17.cnf','9d2c03f1bd246ebcf0892722b522b82bbe07452f','2a39fdba19a928a5d950661f58dfff6a77a36eea0d94907ffc79847a7c87a8ad'),
 'UF20_015':(ROOT/'research/source_data/SATLIB_UF20_015_2026-09-17.cnf','09e4581c3281d62390731e553c2eab48c421166c','0caeb45235dda56ef74f87f9d8b0454ae68fbf8ed5e252d0695c571803c7277b')}
FEATURES=('WL1_MAX_VARIABLE_COLOR_CLASS_SIZE','WL1_VARIABLE_PARTITION_IS_DISCRETE','WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE','WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE')
BLOCK={FEATURES[0]:1,FEATURES[1]:True,FEATURES[2]:1,FEATURES[3]:True}
CLOSED_ORBIT={'ADMIT_ORBIT_COUNT_QUOTIENT_SAT','ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT'}

def blob(path:Path)->str:
 data=path.read_bytes();return hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse_and_formula_hash(path:Path):
 clauses=[];buf=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   p=s.split();header=(int(p[2]),int(p[3]));continue
  for z in map(int,s.split()):
   if z==0:
    assert len(buf)==3 and len({abs(x) for x in buf})==3;clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert header==(20,91) and len(clauses)==91 and not buf
 canonical=''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')
 return clauses,hashlib.sha256(canonical).hexdigest()
def generic_round(raw):
 degree=Counter()
 for c in raw['constraints']:
  for v in set(map(int,c['scope'])):degree[v]+=1
 D={int(v) for v in raw['variables'] if degree[int(v)]==1}
 T={str(c['id']) for c in raw['constraints'] if D & set(map(int,c['scope']))}
 reduced={'variables':[int(v) for v in raw['variables'] if int(v) not in D],'constraints':[c for c in raw['constraints'] if str(c['id']) not in T]}
 if any(D & set(map(int,c['scope'])) for c in reduced['constraints']):raise RuntimeError('REMOVED_VARIABLE_IN_REMAINING_CONSTRAINT')
 return reduced,sorted(D),sorted(T)
def projected(source,path):
 clauses,_=parse_and_formula_hash(path);return projection_identity.normalize_projection(source,clauses)[0]
def training_regression():
 rows={}
 for source,(path,expected_blob,expected_reduced) in TRAINING.items():
  source_ok=blob(path)==expected_blob
  if not source_ok:return False,{source:{'source_blob_ok':False}}
  raw=projected(source,path);reduced,D,T=generic_round(raw);sha=csha(reduced);rows[source]={'source_blob_ok':True,'projected_sha256':csha(raw),'degree1_variables':D,'target_constraints':T,'reduced_sha256':sha,'expected_reduced_sha256':expected_reduced,'match':sha==expected_reduced}
 return all(r['match'] for r in rows.values()),rows
def route_row(reduced):
 elig=reference_census.eligibility(reduced);comp=compositional_basis.induce_compositional_basis(reduced);bases=list(elig.get('global_candidate_bases') or []);basis_closed=bool(bases) or comp.get('status')=='ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO'
 out={'E1':{'global_candidate_bases':bases,'compositional_status':comp.get('status'),'closed_or_admitted':basis_closed}}
 closure=None
 if basis_closed:
  closure={'route':'EXISTING_SCHAEFER_OR_COMPOSITIONAL_BASIS','status':comp.get('status'),'solver_authority':False};out['E2']={'executed':False};out['E3']={'executed':False}
 else:
  la=reference_census.replay_log_alien(reduced);out['E2']=la
  if la.get('closed'):
   win=la.get('winning_attempt') or {};closure={'route':'SEALED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER','status':win.get('status'),'solver_authority':True};out['E3']={'executed':False}
  else:
   orb=orbit_candidate.run_candidate(reduced);out['E3']={'executed':True,'status':orb.get('status'),'solver_authority':orb.get('solver_authority'),'raw_semantic_sha256':orb.get('raw_semantic_sha256'),'cells':orb.get('cells'),'generator_edges':orb.get('generator_edges'),'quotient_states_Q':orb.get('quotient_states_Q'),'resource_receipt':orb.get('resource_receipt',{}),'certificate_type':(orb.get('certificate') or {}).get('type')}
   if orb.get('status') in CLOSED_ORBIT and orb.get('solver_authority') is True:closure={'route':'EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT','status':orb.get('status'),'solver_authority':True}
 out['closure']=closure;out['label']='PORTFOLIO_CLOSED' if closure is not None else 'PORTFOLIO_OPEN';out['signed_route']='NOT_EXECUTED_SOURCE_BOUND_IDENTITY_CONTRACT'
 return out
def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}
 if not all(bindings.values()):return {'verdict':'HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE','authority_bindings':bindings}
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());theorem=json.loads(THEOREM.read_text())
 guards={'review_authorized':review.get('review_verdict')=='PASS_CLEAN_FRESH_REPLICATION_SPEC__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','theorem_pass':theorem.get('verdict')=='PASS_SOURCE_AGNOSTIC_ONE_ROUND_DEGREE1_PENDANT_THEOREM','prereg_blind':pre.get('status')=='FROZEN_BEFORE_FIRST_HOLDOUT_FORMULA_CONTENT_READ_IN_THIS_LINEAGE'}
 if not all(guards.values()):return {'verdict':'HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE','guards':guards}
 ok,training=training_regression()
 if not ok:return {'verdict':'HALT_PREUNBLINDING_TRAINING_REGRESSION_FAILURE','training_regression':training,'holdout_formula_reads':0,'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED'}}
 rows=[]
 for source,(path,expected_blob,expected_formula_hash) in HOLDOUT.items():
  source_blob=blob(path);clauses,formula_hash=parse_and_formula_hash(path)
  if source_blob!=expected_blob or formula_hash!=expected_formula_hash:return {'verdict':'HALT_SOURCE_OR_AUTHORITY_BINDING_FAILURE','reason':source,'training_regression':training}
  raw=projection_identity.normalize_projection(source,clauses)[0];reduced,D,T=generic_round(raw);wl=wl_ref.wl_features(reduced);route=route_row(reduced)
  rows.append({'source':source,'source_git_blob':source_blob,'canonical_formula_sha256':formula_hash,'projected_raw_sha256':csha(raw),'projected_variables':len(raw['variables']),'projected_constraints':len(raw['constraints']),'degree1_variables':D,'target_constraints':T,'reduced_raw_sha256':csha(reduced),'reduced_variables':len(reduced['variables']),'reduced_constraints':len(reduced['constraints']),'wl_features':{f:wl[f] for f in FEATURES},'wl_receipt':wl['_receipt'],'existing_portfolio':route})
 scores={}
 for f in FEATURES:
  tests=[]
  for row in rows:
   blocker=row['wl_features'][f]==BLOCK[f];open_label=row['existing_portfolio']['label']=='PORTFOLIO_OPEN';tests.append({'source':row['source'],'feature_value':row['wl_features'][f],'blocker_value':BLOCK[f],'is_blocker':blocker,'route_label':row['existing_portfolio']['label'],'matches_prediction':blocker==open_label})
  scores[f]={'tests':tests,'matches':sum(t['matches_prediction'] for t in tests),'survives':all(t['matches_prediction'] for t in tests)}
 survivors=sorted(f for f in FEATURES if scores[f]['survives']);labels={r['existing_portfolio']['label'] for r in rows};both=len(labels)==2
 if len(survivors)==4:verdict='FRESH_REPLICATION_ALL_FOUR_SURVIVE_WITH_BOTH_ROUTE_CLASSES' if both else 'FRESH_REPLICATION_ALL_FOUR_SURVIVE_ONE_ROUTE_CLASS_ONLY__LIMITED'
 elif survivors:verdict='FRESH_REPLICATION_PARTIAL_FEATURE_SURVIVOR_SET'
 else:verdict='FRESH_REPLICATION_ALL_FOUR_FALSIFIED'
 return {'artifact_id':'JANUS-TRUMP-UF20-011-015-FRESH-GENERIC-PENDANT-WL-EXISTING-PORTFOLIO-REPLICATION-CANDIDATE-2026-09-17-v1.0','gate':'TRUMP_UF20_011_015_FRESH_GENERIC_PENDANT_WL_EXISTING_PORTFOLIO_REPLICATION_GATE','verdict':verdict,'authority_bindings':bindings,'training_regression':training,'holdout_rows':rows,'per_feature_scores':scores,'surviving_features':survivors,'falsified_features':sorted(set(FEATURES)-set(survivors)),'route_class_coverage':sorted(labels),'resource_receipt':{'holdout_sources_read':5,'generic_reduction_rounds_per_source':1,'iterated_peeling_rounds':0,'new_solver_mechanisms':0,'new_action_rules':0,'new_carrier_mechanisms':0,'new_routes':0,'signed_route_invocations':0,'posthoc_thresholds_or_combinations':0},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY':'NOT_PROVED'}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
