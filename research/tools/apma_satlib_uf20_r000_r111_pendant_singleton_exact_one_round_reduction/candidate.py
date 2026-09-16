from __future__ import annotations

import hashlib,json
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_PREREGISTRATION_REVIEW_2026-09-17.json'
DEPEND=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_DELETION_DEPENDENCY_AUDIT_RESULT_2026-09-17.json'
BOUNDARY=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17_v1.1.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def cbytes(obj:Any)->bytes:return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def csha(obj:Any)->str:return hashlib.sha256(cbytes(obj)).hexdigest()
def guards():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());dep=json.loads(DEPEND.read_text());bound=json.loads(BOUNDARY.read_text())
 sb={n:blob(p)==sha for n,(p,sha,_) in SOURCES.items()}
 checks={'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_REDUCED_RAW_VALUE_OR_HASH_COMPUTATION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','dependency_verdict':dep.get('verdict')=='NO_INTER_ATTACHMENT_DEPENDENCIES','dependency_edge_count':dep.get('edge_count')==0,'dependency_composition_verified':dep.get('composition_theorem',{}).get('composition_argument_verified') is True,'boundary_verdict':bound.get('verdict')=='ALL_ELEVEN_UNIVERSAL','boundary_local_theorem':bound.get('local_semantics_theorem',{}).get('symbolic_projection_equivalence_verified') is True,'target_count':sum(len(r['attachments']) for r in bound['source_receipts'])==11,'source_bindings':all(sb.values()),'projection_blob':blob(PROJECTION)=='2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4','fresh_holdout_result_present':FRESH.exists()}
 return {'ok':all(checks.values()),'checks':checks,'source_bindings':sb,'preregistration_blob':blob(PREREG),'review_blob':blob(REVIEW),'dependency_result_blob':blob(DEPEND),'boundary_result_blob':blob(BOUNDARY)}
def reduce_source(name,path,expected_raw,attachments):
 clauses=projection_identity.parse(path);raw,_=projection_identity.normalize_projection(name,clauses);raw_sha=csha(raw)
 if raw_sha!=expected_raw:raise RuntimeError(f'PROJECTED_RAW_BINDING:{name}:{raw_sha}:{expected_raw}')
 leaves=sorted(int(a['leaf_variable']) for a in attachments);cids=sorted(str(a['constraint_id']) for a in attachments);assert len(leaves)==len(set(leaves)) and len(cids)==len(set(cids))
 leafset=set(leaves);cidset=set(cids);byid={c['id']:c for c in raw['constraints']};assert cidset<=set(byid)
 occurrence={v:[c['id'] for c in raw['constraints'] if v in c['scope']] for v in leaves}
 unique_ok=all(occurrence[v]==[next(a['constraint_id'] for a in attachments if int(a['leaf_variable'])==v)] for v in leaves)
 gateways={a['constraint_id']:[int(x) for x in a['gateway_order']] for a in attachments};gateway_survival=all(all(g not in leafset and g in raw['variables'] for g in gs) for gs in gateways.values())
 scope_binding=all(set(byid[a['constraint_id']]['scope'])==set([int(a['leaf_variable'])]+[int(x) for x in a['gateway_order']]) for a in attachments)
 retained_vars=[int(v) for v in raw['variables'] if int(v) not in leafset];retained_constraints=[c for c in raw['constraints'] if c['id'] not in cidset]
 no_deleted_leaf_in_retained=all(not (set(c['scope'])&leafset) for c in retained_constraints)
 retained_exact=all(c==byid[c['id']] for c in retained_constraints)
 reduced={'variables':retained_vars,'constraints':retained_constraints};reduced_sha=csha(reduced)
 cert=[]
 for a in sorted(attachments,key=lambda x:x['constraint_id']):
  w={str(k):int(v) for k,v in a['canonical_reconstruction_witnesses'].items()};assert set(w)=={'00','01','10','11'}
  cert.append({'source':name,'constraint_id':a['constraint_id'],'leaf_variable':int(a['leaf_variable']),'gateway_order':[int(x) for x in a['gateway_order']],'canonical_reconstruction_witnesses':w,'leaf_original_constraint_occurrences':occurrence[int(a['leaf_variable'])]})
 return {'source':name,'original_projected_raw_sha256':raw_sha,'original_variable_count':len(raw['variables']),'original_constraint_count':len(raw['constraints']),'removed_leaves':leaves,'removed_constraint_ids':cids,'removed_attachment_count':len(attachments),'leaf_occurrence_lists':{str(k):v for k,v in occurrence.items()},'unique_occurrence_verified':unique_ok,'gateway_survival_verified':gateway_survival,'target_scope_binding_verified':scope_binding,'no_deleted_leaf_in_retained_constraint_verified':no_deleted_leaf_in_retained,'retained_constraints_exact_object_equality_verified':retained_exact,'reduced_variable_count':len(retained_vars),'reduced_constraint_count':len(retained_constraints),'reduced_raw_sha256':reduced_sha,'reduced_raw':reduced,'reconstruction_entries':cert}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','EXACT_FINITE_REDUCTION_IMPLIES_TRACTABILITY':False,'EXACT_FINITE_REDUCTION_IMPLIES_HARDNESS':False}
def main():
 g=guards()
 if not g['ok']:return {'verdict':'HALT_REDUCTION_PARENT_PRECONDITION_FAILURE','guards':g,'scientific_firewall':firewall()}
 bound=json.loads(BOUNDARY.read_text());by_source={r['source']:r['attachments'] for r in bound['source_receipts']};rows=[]
 try:
  for name in ORDER:
   path,_,rsha=SOURCES[name];rows.append(reduce_source(name,path,rsha,by_source[name]))
 except RuntimeError as e:return {'verdict':'HALT_REDUCTION_SOURCE_OR_PROJECTED_RAW_BINDING_FAILURE','reason':str(e),'guards':g,'scientific_firewall':firewall()}
 retained_ok=all(r['retained_constraints_exact_object_equality_verified'] for r in rows)
 premises=all(r['unique_occurrence_verified'] and r['gateway_survival_verified'] and r['target_scope_binding_verified'] and r['no_deleted_leaf_in_retained_constraint_verified'] for r in rows)
 if not retained_ok:verdict='HALT_REDUCTION_RETAINED_CONSTRAINT_MUTATION'
 elif not premises:verdict='HALT_REDUCTION_PARENT_PRECONDITION_FAILURE'
 else:verdict='PASS_EXACT_SIMULTANEOUS_ONE_ROUND_PENDANT_REDUCTION_CERTIFIED'
 cert={'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PENDANT-SINGLETON-ONE-ROUND-RECONSTRUCTION-CERTIFICATE-2026-09-17-v1.0','reduction_rounds':1,'fixed_point_iterations':0,'source_entries':[{ 'source':r['source'],'entries':r['reconstruction_entries']} for r in rows],'forward_equivalence':'ORIGINAL_SAT_ASSIGNMENT_RESTRICTION_TO_RETAINED_VARIABLES_SATISFIES_REDUCED_RAW','reverse_equivalence':'ANY_REDUCED_SAT_ASSIGNMENT_EXTENDS_BY_INDEPENDENT_FROZEN_GATEWAY_WITNESS_LOOKUPS_TO_SATISFY_ALL_11_REMOVED_CONSTRAINTS','zero_dependency_required_and_verified':json.loads(DEPEND.read_text())['edge_count']==0,'symbolic_equivalence_verified':verdict=='PASS_EXACT_SIMULTANEOUS_ONE_ROUND_PENDANT_REDUCTION_CERTIFIED'}
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PENDANT-SINGLETON-EXACT-SIMULTANEOUS-ONE-ROUND-REDUCTION-CANDIDATE-2026-09-17-v1.0','authority':'EXACT_SEMANTICS_PRESERVING_FINITE_ONE_ROUND_REPRESENTATION_REDUCTION_ONLY__NO_SOLVER_FIXED_POINT_ACTION_AUTOMORPHISM_GROUP_SEARCH_CARRIER_OR_QUOTIENT','verdict':verdict,'guards':g,'rows':rows,'reconstruction_certificate':cert,'resource_receipt':{'target_sources':4,'target_attachments':11,'reduction_rounds':1,'fixed_point_iterations':0,'fresh_holdout_values_read':0,'global_solver_invocations':0,'component_solver_invocations':0,'portfolio_replays':0,'full_assignment_cube_enumerations':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_quotients':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
