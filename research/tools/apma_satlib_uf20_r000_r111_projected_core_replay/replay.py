from __future__ import annotations
import hashlib,json
from collections import Counter
from pathlib import Path
from typing import Any
from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate
from research.tools.apma_connected_mixed_post_orbit_obstruction_census import census as reference_census

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_PREREGISTRATION_2026-09-16.json'
EXPECTED_PREREG='f06b2572b18088acfba081e6d5d2a52025f36dc3'
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
SEALED={
 ROOT/'research/tools/apma_satlib_uf20_family_sealed_portfolio_replication/replay.py':'4e4439c2e4a588cc0dd31480607bd2cab3b906bc',
 ROOT/'research/tools/apma_external_satlib_uf20_01_replay/replay.py':'67ae8bd40c58c6bb1f22f7651111d33ba6be1d0b',
 ROOT/'research/tools/apma_unseen_basis/raw_relation_basis.py':'63490c05ef3e91a4f682f75da26ff2af811839a6',
 ROOT/'research/tools/apma_connected_mixed_post_orbit_obstruction_census/census.py':'f5aa39804983d49149c976e8367a96397bad888e',
 ROOT/'research/tools/apma_unseen_basis/compositional_basis.py':'fdc83a3368a4ad362f00d3ee8aad958f06f8d264',
 ROOT/'research/tools/apma_log_alien_transfer/log_alien_transfer.py':'d20cd94fa2e0324e301f55211152c2d410099425',
 ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py':'a076cfc56d68aad0348415e313705da1f6b9cdcd',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py':'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
CLOSED_ORBIT={'ADMIT_ORBIT_COUNT_QUOTIENT_SAT','ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT'}

def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def cbytes(o:Any):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def guard():
 binds={str(PREREG.relative_to(ROOT)):blob(PREREG)==EXPECTED_PREREG};binds.update({str(p.relative_to(ROOT)):blob(p)==s for p,s in SEALED.items()});sb={n:blob(p)==s for n,(p,s) in SOURCES.items()};pre=json.loads(PREREG.read_text());return {'ok':all(binds.values()) and all(sb.values()) and pre.get('status')=='FROZEN_AFTER_PROJECTED_RAW_IDENTITY_FREEZE_AND_BEFORE_PORTFOLIO_REPLAY','bindings':binds,'source_bindings':sb,'prereg_status':pre.get('status')}
def expected_rows():return {r['source']:r for r in json.loads(PREREG.read_text())['frozen_projected_raw_identities']}
def one(name,path,exp):
 raw,ords=projection_identity.normalize_projection(name,projection_identity.parse(path));sha=hashlib.sha256(cbytes(raw)).hexdigest()
 if sha!=exp['projected_raw_sha256'] or ords!=exp['clause_ordinals'] or raw['variables']!=exp['variables']:
  return {'source':name,'status':'PROJECTED_RAW_OR_BINDING_GUARD_FAILURE','raw_sha256':sha,'ordinals':ords}
 eligibility=reference_census.eligibility(raw)
 if not eligibility.get('eligible'):
  return {'source':name,'status':'PROJECTED_RAW_OR_BINDING_GUARD_FAILURE','raw_sha256':sha,'reason':'NOT_ELIGIBLE_CONNECTED_MIXED','eligibility':eligibility}
 comp=compositional_basis.induce_compositional_basis(raw);comp_r={'status':comp.get('status'),'component_count':comp.get('component_count'),'open_component_count':comp.get('open_component_count')}
 la=reference_census.replay_log_alien(raw)
 if la.get('closed'):
  win=la.get('winning_attempt',{})
  return {'source':name,'status':'CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER','raw_sha256':sha,'eligibility':eligibility,'compositional':comp_r,'log_alien':la,'orbit':{'executed':False,'reason':'STOP_ON_FIRST_EXISTING_AUTHORITATIVE_CLOSURE'},'closure':{'mechanism':'SEALED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER','status':win.get('status')}}
 orbit=orbit_candidate.run_candidate(raw);orb={'executed':True,'status':orbit.get('status'),'solver_authority':orbit.get('solver_authority'),'raw_semantic_sha256':orbit.get('raw_semantic_sha256'),'cells':orbit.get('cells'),'nontrivial_cells':orbit.get('nontrivial_cells'),'quotient_states_Q':orbit.get('quotient_states_Q'),'certificate_type':(orbit.get('certificate') or {}).get('type'),'resource_receipt':orbit.get('resource_receipt',{})}
 if orbit.get('status') in CLOSED_ORBIT and orbit.get('solver_authority') is True:
  status='CLOSED_BY_SEALED_ORBIT_COUNT_V1';closure={'mechanism':'EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT','status':orbit.get('status')}
 else:status='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO';closure=None
 return {'source':name,'status':status,'raw_sha256':sha,'eligibility':eligibility,'compositional':comp_r,'log_alien':la,'orbit':orb,'closure':closure}
def main():
 g=guard()
 if not g['ok']:return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-SEALED-PORTFOLIO-REPLAY-2026-09-16-v1.0','authority':'DIAGNOSTIC_EXISTING_PORTFOLIO_REPLAY_ON_SOURCE_BOUND_PROJECTIONS_ONLY__NO_NEW_SOLVER_OR_MECHANISM','verdict':'PROJECTED_RAW_OR_BINDING_GUARD_FAILURE','source_guard':g,'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED'}}
 er=expected_rows();rows=[one(n,p,er[n]) for n,(p,_) in SOURCES.items()];bad=any(r['status']=='PROJECTED_RAW_OR_BINDING_GUARD_FAILURE' for r in rows)
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-SEALED-PORTFOLIO-REPLAY-2026-09-16-v1.0','authority':'DIAGNOSTIC_EXISTING_PORTFOLIO_REPLAY_ON_SOURCE_BOUND_PROJECTIONS_ONLY__NO_NEW_SOLVER_OR_MECHANISM','verdict':'PROJECTED_RAW_OR_BINDING_GUARD_FAILURE' if bad else 'PASS_DIAGNOSTIC_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY','source_guard':g,'rows':rows,'outcome_counts':dict(sorted(Counter(r['status'] for r in rows).items())),'resource_receipt':{'new_adapters':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_symmetry_mechanisms':0,'new_separator_branching':0,'full_variable_cube_enumerations':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','PROJECTED_CORE_REPLAY_IMPLIES_HARDNESS':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
