from __future__ import annotations

import hashlib,json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_CLOSURE_LEVERAGE_REQUIREMENTS_SYNTHESIS_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_CLOSURE_LEVERAGE_REQUIREMENTS_SYNTHESIS_PREREGISTRATION_REVIEW_2026-09-17.json'
BARRIER=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_VARIABLE_PARTITION_REFINEMENT_UTILITY_BARRIER_RESULT_2026-09-17.json'
MATRIX=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_FOUR_UNADMITTED_EXISTING_EVIDENCE_RESIDUAL_MATRIX_RESULT_2026-09-16.json'
PORTFOLIO=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_RESULT_2026-09-16.json'
SIGNED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_RESULT_2026-09-16_v1.1.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
EXPECTED={PREREG:'40fb96cc8fb54988881cb3a2186fc61f2bf45361',REVIEW:'aa71d90280a83f1c278f94e6d7e40a9db04f63c4',BARRIER:'ef78b34e32a27941aa9a11a351ebffbafe05e043',MATRIX:'f6209a9b97c8f270ff915ba5c813922b5a8e3bb3',PORTFOLIO:'89958034e76e1f0f97ea28b972df2acf90786bd5',SIGNED:'1c2b7d35f970038616fa9f1decb20d67c88965f5',FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092'}
TARGET=('UF20_02','UF20_03','UF20_04','UF20_05')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def guard():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}
 checks={'bindings':all(binds.values()),'prereg_status':pre.get('status')=='FROZEN_BEFORE_ROUTE_CLASSIFICATION_SYNTHESIS_EXECUTION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','target_exact':tuple(pre['target_sources'])==TARGET,'route_count':len(pre['route_classes'])==9,'fresh_holdout_values_forbidden':pre['fresh_holdout_firewall']['formula_feature_partition_or_solver_values_may_be_used'] is False}
 return {'ok':all(checks.values()),'checks':checks,'bindings':binds}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','UNTESTED_ROUTE_IMPLIES_PROMISE':False}
def main():
 g=guard()
 if not g['ok']:return {'verdict':'HALT_FROZEN_AUTHORITY_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 pre=json.loads(PREREG.read_text());matrix=json.loads(MATRIX.read_text());barrier=json.loads(BARRIER.read_text());signed=json.loads(SIGNED.read_text());portfolio=json.loads(PORTFOLIO.read_text())
 labels=set(matrix['common_label_intersection']);signed_rows={r['source']:r for r in signed['source_receipt']};portfolio_rows={r['source']:r for r in portfolio['source_outcomes']}
 all_signed_identity=all(int(signed_rows[s]['nonidentity_exact_signed_automorphism_count'])==0 for s in TARGET)
 all_portfolio_unadmitted=all(portfolio_rows[s]['status']=='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO' for s in TARGET)
 statuses={
  'EXPLICIT_SCHAEFER_BASIS':'NO_CURRENT_EXPLICIT_BASIS_LEVERAGE' if 'COMPOSITIONAL_OPEN_NO_SCHAEFER_BASIS' in labels else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
  'CONNECTED_COMPONENT_DECOMPOSITION':'NO_CURRENT_TOP_LEVEL_COMPONENT_LEVERAGE' if 'CONNECTED_R000_R111_CORE' in labels else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
  'LOG_ALIEN':'INAPPLICABLE_ON_CURRENT_SURFACE' if 'LOG_ALIEN_INAPPLICABLE' in labels else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
  'SEALED_ORBIT_EXCHANGEABILITY':'NO_CURRENT_SEALED_ORBIT_LEVERAGE' if 'ORBIT_NO_NONTRIVIAL_EXCHANGEABILITY' in labels and all_portfolio_unadmitted else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
  'FROZEN_SIGNED_PERMUTATION_ACTION':'NO_CURRENT_FROZEN_SIGNED_ACTION_LEVERAGE' if 'SIGNED_IDENTITY_ONLY' in labels and all_signed_identity else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
  'REFINEMENT_ONLY_ROOT_VARIABLE_PARTITION':'NO_CURRENT_REFINEMENT_ONLY_CLASS_LEVERAGE' if barrier['verdict']=='PASS_CURRENT_FOUR_SOURCE_REFINEMENT_ONLY_VARIABLE_PARTITION_UTILITY_BARRIER__NO_NON_SINGLETON_CLASS_LEVERAGE' else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
  'NONREFINEMENT_INSTANCE_STRUCTURAL_DECOMPOSITION':'UNTESTED_NOT_LICENSED',
  'SEMANTICS_PRESERVING_BOUNDARY_OR_REPRESENTATION_TRANSFORM':'UNTESTED_NOT_LICENSED',
  'NONPERMUTATION_ALGEBRAIC_OR_OTHER_ACTION_MODEL':'UNTESTED_NOT_LICENSED'}
 allowed={r['route_id']:set(r['allowed_statuses']) for r in pre['route_classes']}
 if any(statuses[r] not in allowed[r] for r in statuses):return {'verdict':'HALT_ROUTE_STATUS_OUTSIDE_PREREGISTERED_VOCABULARY','source_guard':g,'route_statuses':statuses,'scientific_firewall':firewall()}
 untested=[r for r in pre['successor_route_priority_rule']['predeclared_order'] if statuses[r]=='UNTESTED_NOT_LICENSED']
 closed=[r for r,s in statuses.items() if s!='UNTESTED_NOT_LICENSED']
 first=untested[0] if untested else None
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-SUCCESSOR-CLOSURE-LEVERAGE-REQUIREMENTS-SYNTHESIS-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_EXISTING_EVIDENCE_ROUTE_ELIMINATION_AND_REQUIREMENTS_SYNTHESIS_ONLY__NO_NEW_FEATURE_GRAPH_STATISTIC_ACTION_TEST_GROUP_SEARCH_SOLVER_CARRIER_ADAPTER_OR_QUOTIENT','verdict':'PASS_EXISTING_ROUTE_ELIMINATION_SYNTHESIS__UNTESTED_ROUTE_CLASS_IDENTIFIED' if first else 'PASS_EXISTING_ROUTE_ELIMINATION_SYNTHESIS__NO_PREDECLARED_UNTESTED_ROUTE_REMAINS','source_guard':g,'route_statuses':statuses,'closed_or_inapplicable_routes':closed,'untested_routes_in_predeclared_priority_order':untested,'first_untested_route_by_predeclared_priority':first,'status_receipt':{'common_label_intersection':sorted(labels),'all_four_signed_identity_only_verified':all_signed_identity,'all_four_current_portfolio_unadmitted_verified':all_portfolio_unadmitted,'refinement_barrier_pass_verified':barrier['verdict'].startswith('PASS_CURRENT_FOUR_SOURCE_REFINEMENT_ONLY')},'interpretation':{'first_untested_route_is_only_future_preregistration_target':True,'first_untested_route_success_claim':False,'fresh_holdout_values_used':False},'resource_receipt':{'frozen_status_authorities_read':4,'target_sources':4,'route_classes':9,'new_source_values':0,'partition_recomputations':0,'fresh_holdout_values_read':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_action_semantics':0,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
