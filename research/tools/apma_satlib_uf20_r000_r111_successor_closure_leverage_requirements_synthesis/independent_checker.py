from __future__ import annotations

import argparse,hashlib,json
from pathlib import Path

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
def expected_statuses():
 assert all(blob(p)==s for p,s in EXPECTED.items()),{str(p):blob(p) for p in EXPECTED}
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());assert pre['status']=='FROZEN_BEFORE_ROUTE_CLASSIFICATION_SYNTHESIS_EXECUTION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE';assert tuple(pre['target_sources'])==TARGET
 matrix=json.loads(MATRIX.read_text());barrier=json.loads(BARRIER.read_text());signed=json.loads(SIGNED.read_text());portfolio=json.loads(PORTFOLIO.read_text())
 labels=set(matrix['common_label_intersection']);signed_rows={r['source']:r for r in signed['source_receipt']};portfolio_rows={r['source']:r for r in portfolio['source_outcomes']}
 all_signed=all(int(signed_rows[s]['nonidentity_exact_signed_automorphism_count'])==0 for s in TARGET);all_unadmitted=all(portfolio_rows[s]['status']=='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO' for s in TARGET)
 statuses={
 'EXPLICIT_SCHAEFER_BASIS':'NO_CURRENT_EXPLICIT_BASIS_LEVERAGE' if 'COMPOSITIONAL_OPEN_NO_SCHAEFER_BASIS' in labels else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
 'CONNECTED_COMPONENT_DECOMPOSITION':'NO_CURRENT_TOP_LEVEL_COMPONENT_LEVERAGE' if 'CONNECTED_R000_R111_CORE' in labels else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
 'LOG_ALIEN':'INAPPLICABLE_ON_CURRENT_SURFACE' if 'LOG_ALIEN_INAPPLICABLE' in labels else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
 'SEALED_ORBIT_EXCHANGEABILITY':'NO_CURRENT_SEALED_ORBIT_LEVERAGE' if 'ORBIT_NO_NONTRIVIAL_EXCHANGEABILITY' in labels and all_unadmitted else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
 'FROZEN_SIGNED_PERMUTATION_ACTION':'NO_CURRENT_FROZEN_SIGNED_ACTION_LEVERAGE' if 'SIGNED_IDENTITY_ONLY' in labels and all_signed else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
 'REFINEMENT_ONLY_ROOT_VARIABLE_PARTITION':'NO_CURRENT_REFINEMENT_ONLY_CLASS_LEVERAGE' if barrier['verdict']=='PASS_CURRENT_FOUR_SOURCE_REFINEMENT_ONLY_VARIABLE_PARTITION_UTILITY_BARRIER__NO_NON_SINGLETON_CLASS_LEVERAGE' else 'NOT_SUPPORTED_BY_FROZEN_EVIDENCE',
 'NONREFINEMENT_INSTANCE_STRUCTURAL_DECOMPOSITION':'UNTESTED_NOT_LICENSED',
 'SEMANTICS_PRESERVING_BOUNDARY_OR_REPRESENTATION_TRANSFORM':'UNTESTED_NOT_LICENSED',
 'NONPERMUTATION_ALGEBRAIC_OR_OTHER_ACTION_MODEL':'UNTESTED_NOT_LICENSED'}
 priority=list(pre['successor_route_priority_rule']['predeclared_order']);untested=[r for r in priority if statuses[r]=='UNTESTED_NOT_LICENSED'];closed=[r for r,s in statuses.items() if s!='UNTESTED_NOT_LICENSED'];first=untested[0] if untested else None
 return statuses,closed,untested,first,sorted(labels),all_signed,all_unadmitted
def main(candidate_path:Path):
 c=json.loads(candidate_path.read_text().strip().splitlines()[-1]);statuses,closed,untested,first,labels,all_signed,all_unadmitted=expected_statuses()
 assert c['route_statuses']==statuses;assert c['closed_or_inapplicable_routes']==closed;assert c['untested_routes_in_predeclared_priority_order']==untested;assert c['first_untested_route_by_predeclared_priority']==first
 verdict='PASS_EXISTING_ROUTE_ELIMINATION_SYNTHESIS__UNTESTED_ROUTE_CLASS_IDENTIFIED' if first else 'PASS_EXISTING_ROUTE_ELIMINATION_SYNTHESIS__NO_PREDECLARED_UNTESTED_ROUTE_REMAINS';assert c['verdict']==verdict
 assert c['status_receipt']['common_label_intersection']==labels and c['status_receipt']['all_four_signed_identity_only_verified']==all_signed and c['status_receipt']['all_four_current_portfolio_unadmitted_verified']==all_unadmitted
 assert c['interpretation']['first_untested_route_is_only_future_preregistration_target'] is True and c['interpretation']['first_untested_route_success_claim'] is False and c['interpretation']['fresh_holdout_values_used'] is False
 rr=c['resource_receipt'];assert rr['frozen_status_authorities_read']==4 and rr['target_sources']==4 and rr['route_classes']==9 and rr['new_source_values']==0 and rr['partition_recomputations']==0 and rr['fresh_holdout_values_read']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['new_action_semantics']==0
 assert rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'route_statuses':statuses,'closed_or_inapplicable_routes':closed,'untested_routes_in_predeclared_priority_order':untested,'first_untested_route_by_predeclared_priority':first,'fresh_holdout_values_used':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(Path(a.candidate_json)),sort_keys=True,separators=(',',':')))
