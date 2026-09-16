from __future__ import annotations

import hashlib,json
from pathlib import Path
from typing import Any

from research.tools.apma_mixed_carrier_barrier.check_schaefer_barrier import is_0_valid,is_1_valid,is_horn,is_dual_horn,is_bijunctive,is_affine
from research.tools.apma_satlib_uf20_r000_r111_nonrefinement_structural_decomposition_menu import candidate as structural

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_ONE_ROUND_REDUCED_RAW_EXISTING_ROUTE_REEVALUATION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_ONE_ROUND_REDUCED_RAW_EXISTING_ROUTE_REEVALUATION_PREREGISTRATION_REVIEW_2026-09-17.json'
REDUCTION=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17.json'
ORIG_STRUCT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_RESULT_2026-09-17.json'
ORIG_MATRIX=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_FOUR_UNADMITTED_EXISTING_EVIDENCE_RESIDUAL_MATRIX_RESULT_2026-09-16.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
SCHAEFER=ROOT/'research/tools/apma_mixed_carrier_barrier/check_schaefer_barrier.py'
STRUCT_IMPL=ROOT/'research/tools/apma_satlib_uf20_r000_r111_nonrefinement_structural_decomposition_menu/candidate.py'
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
DIDS=('D1_PRIMAL_ARTICULATION_BLOCK_PROFILE','D2_INCIDENCE_ARTICULATION_BLOCK_PROFILE','D3_PRIMAL_MINIMAL_TWO_VERTEX_SEPARATOR_PROFILE')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def language(raw):
 seen={}
 for c in raw['constraints']:
  rel=frozenset(tuple(int(x) for x in t) for t in c['allowed']);seen[(len(c['scope']),tuple(sorted(rel)))]=set(rel)
 return [seen[k] for k in sorted(seen,key=lambda x:(x[0],x[1]))]
def fingerprint(rels):
 return {'ZERO_VALID':is_0_valid(rels),'ONE_VALID':is_1_valid(rels),'HORN':is_horn(rels),'DUAL_HORN':is_dual_horn(rels),'BIJUNCTIVE':is_bijunctive(rels),'AFFINE':is_affine(rels)}
def inc_profiles(comps):
 out=[]
 for cc in comps:
  nv=sum(isinstance(n,tuple) and n[0]=='VAR' for n in cc);nc=sum(isinstance(n,tuple) and n[0]=='CONSTRAINT' for n in cc);out.append([nv,nc,nv+nc])
 return sorted(out)
def main():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());red=json.loads(REDUCTION.read_text());orig=json.loads(ORIG_STRUCT.read_text());matrix=json.loads(ORIG_MATRIX.read_text())
 guards={'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_REDUCED_ROUTE_REEVALUATION_VALUE_COMPUTATION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','reduction_pass':red.get('verdict')=='PASS_EXACT_SIMULTANEOUS_ONE_ROUND_PENDANT_REDUCTION_CERTIFIED','reduction_rounds':red.get('resource_receipt',{}).get('reduction_rounds')==1 and red.get('resource_receipt',{}).get('fixed_point_iterations')==0,'schaefer_blob':blob(SCHAEFER)=='11fcacd5f0c550543f96648a7965734308509d22','structural_blob':blob(STRUCT_IMPL)=='1eedfc1fb381171411b200d5dbfaa661c4523a27','original_structural_counts':orig['diagnostic_summary'][DIDS[0]]['presence_count']==0 and orig['diagnostic_summary'][DIDS[1]]['presence_count']==4 and orig['diagnostic_summary'][DIDS[2]]['presence_count']==4,'original_labels':all(x in matrix['common_label_intersection'] for x in ('COMPOSITIONAL_OPEN_NO_SCHAEFER_BASIS','CONNECTED_R000_R111_CORE'))}
 if not all(guards.values()):return {'verdict':'HALT_FROZEN_AUTHORITY_BINDING_FAILURE','guards':guards}
 rec={r['source']:r for r in red['reduced_source_receipts']};rows=[]
 for src in ORDER:
  rr=rec[src];p=ROOT/rr['reduced_raw_path'];raw=json.loads(p.read_text());assert blob(p)==rr['reduced_raw_git_blob'] and csha(raw)==rr['reduced_raw_sha256']
  pg=structural.primal_graph(raw);ig=structural.incidence_graph(raw);pc=structural.components(pg,set());ic=structural.components(ig,set())
  p_sizes=sorted(len(c) for c in pc);i_prof=inc_profiles(ic);connected=len(pc)==1 and len(ic)==1
  rels=language(raw);fp=fingerprint(rels);admit=any(fp.values());basis_label='ADMIT_AT_LEAST_ONE_FROZEN_SCHAEFER_BASIS' if admit else 'OPEN_NO_SCHAEFER_BASIS'
  d={DIDS[0]:structural.d1(pg),DIDS[1]:structural.d2(ig),DIDS[2]:structural.d3(pg)}
  rows.append({'source':src,'reduced_raw_path':rr['reduced_raw_path'],'reduced_raw_git_blob':rr['reduced_raw_git_blob'],'reduced_raw_sha256':rr['reduced_raw_sha256'],'reduced_variable_count':len(raw['variables']),'reduced_constraint_count':len(raw['constraints']),'connected_component_status':{'primal_component_count':len(pc),'primal_component_sizes':p_sizes,'incidence_component_count':len(ic),'incidence_component_profiles':i_prof,'label':'STILL_CONNECTED' if connected else 'BECAME_DISCONNECTED'},'explicit_relation_language':{'unique_relation_count':len(rels),'schaefer_fingerprint':fp,'label':basis_label},'structural_diagnostics':d})
 presence={did:sum(r['structural_diagnostics'][did]['decomposition_present'] for r in rows) for did in DIDS};route_changed=any(r['connected_component_status']['label']=='BECAME_DISCONNECTED' or r['explicit_relation_language']['label']=='ADMIT_AT_LEAST_ONE_FROZEN_SCHAEFER_BASIS' for r in rows);struct_changed=presence!={DIDS[0]:0,DIDS[1]:4,DIDS[2]:4}
 if route_changed:verdict='EXISTING_ROUTE_APPLICABILITY_CHANGED_ON_AT_LEAST_ONE_SOURCE'
 elif struct_changed:verdict='NO_EXISTING_BASIS_OR_COMPONENT_ROUTE_CHANGE__STRUCTURAL_STATUS_CHANGED'
 else:verdict='NO_TESTED_ROUTE_STATUS_CHANGE_AFTER_ONE_ROUND_REDUCTION'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PENDANT-ONE-ROUND-REDUCED-RAW-EXISTING-ROUTE-REEVALUATION-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_EXISTING_ROUTE_REEVALUATION_ON_EXACT_REDUCED_RAWS_ONLY__NO_SOLVER_PORTFOLIO_REPLAY_NEW_FEATURE_ACTION_AUTOMORPHISM_GROUP_SEARCH_CARRIER_ADAPTER_OR_QUOTIENT','verdict':verdict,'guards':guards,'preregistration_blob':blob(PREREG),'review_blob':blob(REVIEW),'reduction_result_blob':blob(REDUCTION),'rows':rows,'reduced_structural_presence_counts':presence,'route_applicability_changed':route_changed,'structural_status_changed':struct_changed,'resource_receipt':{'reduced_sources':4,'fresh_holdout_values_read':0,'solver_invocations':0,'portfolio_replays':0,'additional_reduction_rounds':0,'fixed_point_iterations':0,'new_feature_definitions':0,'new_graph_statistics':0,'action_tests':0,'automorphism_tests':0,'group_searches':0},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','ROUTE_STATUS_CHANGE_IMPLIES_TRACTABILITY':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
