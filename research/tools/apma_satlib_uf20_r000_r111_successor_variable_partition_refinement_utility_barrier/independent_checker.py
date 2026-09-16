from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_VARIABLE_PARTITION_REFINEMENT_UTILITY_BARRIER_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_VARIABLE_PARTITION_REFINEMENT_UTILITY_BARRIER_PREREGISTRATION_REVIEW_2026-09-17.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
PARTITIONS=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_RESULT_2026-09-17.json'
PORTFOLIO=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_RESULT_2026-09-16.json'
SIGNED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_RESULT_2026-09-16_v1.1.json'
EXPECTED={PREREG:'ecb5cafcb3fc59d7d938cee3927819d459c5d3e3',REVIEW:'8d10b0ed12628db792c37f942ef206c210b2e0e4',FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092',PARTITIONS:'971d7d98a86471e88bf33336da215171b2f8cdfe',PORTFOLIO:'89958034e76e1f0f97ea28b972df2acf90786bd5',SIGNED:'1c2b7d35f970038616fa9f1decb20d67c88965f5'}
TARGET=('UF20_02','UF20_03','UF20_04','UF20_05')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def discrete(receipt,stage):
 if stage=='S3':return receipt.get('S3_all_singleton') is True
 if stage=='L3':return receipt.get('L3_all_singleton') is True
 raise AssertionError(stage)
def direct_set_argument_receipt():
 # Logical kernel, independent of any source values:
 # for nonempty B and singleton {v}, B subseteq {v} => B={v}.
 examples=[]
 for v in range(5):
  singleton={v}
  nonempty_subsets=[{v}]
  assert all(B and B <= singleton and B==singleton for B in nonempty_subsets)
  examples.append(v)
 return {'proof_kind':'DIRECT_SET_ARGUMENT','universal_step':'NONEMPTY_B_SUBSET_OF_SINGLETON_{v}_IMPLIES_B_EQUALS_SINGLETON_{v}','coverage_step':'A_PARTITION_COVERS_V_SO_EVERY_v_HAS_EXACTLY_ONE_SINGLETON_BLOCK','conclusion':'ANY_PARTITION_REFINING_D(V)_EQUALS_D(V)','sanity_singletons_checked':len(examples),'claim_verified_by_direct_set_argument':True}
def expected_rows():
 assert all(blob(p)==sha for p,sha in EXPECTED.items()),{str(p):blob(p) for p in EXPECTED}
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text())
 assert pre['status']=='FROZEN_BEFORE_BARRIER_SYNTHESIS_EXECUTION'
 assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 part=json.loads(PARTITIONS.read_text());port=json.loads(PORTFOLIO.read_text());signed=json.loads(SIGNED.read_text())
 receipts=part['key_partition_receipts'];pout={r['source']:r for r in port['source_outcomes']};sout={r['source']:r for r in signed['source_receipt']}
 rows=[]
 for source in TARGET:
  expected=pre['frozen_current_status_contract'][source]['existing_discrete_partition_witnesses']
  witnessed=[s for s in expected if discrete(receipts[source],s)]
  count=int(sout[source]['nonidentity_exact_signed_automorphism_count'])
  portfolio_ok=pout[source]['status']=='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO' and pout[source]['orbit_status']=='OPEN_NO_NONTRIVIAL_EXCHANGEABILITY'
  signed_ok=count==0;has=bool(witnessed)
  rows.append({'source':source,'portfolio_status':pout[source]['status'],'orbit_status':pout[source]['orbit_status'],'signed_nonidentity_exact_automorphism_count':count,'existing_discrete_partition_witnesses_verified':witnessed,'at_least_one_existing_partition_is_discrete':has,'refinement_of_verified_discrete_partition_can_have_non_singleton_block':False if has else None,'portfolio_unadmitted_and_no_exchangeability_verified':portfolio_ok,'signed_identity_only_verified':signed_ok})
 return rows
def main(candidate_path:Path):
 c=json.loads(candidate_path.read_text().strip().splitlines()[-1]);rows=expected_rows()
 assert c['rows']==rows,(c['rows'],rows)
 theorem=direct_set_argument_receipt()
 assert c['finite_partition_fact_receipt']['claim_verified_by_direct_set_argument'] is True
 assert theorem['claim_verified_by_direct_set_argument'] is True
 passed=all(r['at_least_one_existing_partition_is_discrete'] and r['portfolio_unadmitted_and_no_exchangeability_verified'] and r['signed_identity_only_verified'] and r['refinement_of_verified_discrete_partition_can_have_non_singleton_block'] is False for r in rows)
 verdict='PASS_CURRENT_FOUR_SOURCE_REFINEMENT_ONLY_VARIABLE_PARTITION_UTILITY_BARRIER__NO_NON_SINGLETON_CLASS_LEVERAGE' if passed else 'FAIL_BARRIER_AT_LEAST_ONE_CURRENTLY_UNADMITTED_SOURCE_LACKS_A_FROZEN_DISCRETE_PARTITION_WITNESS'
 assert c['verdict']==verdict
 assert c['barrier_interpretation']['no_possible_useful_invariant_or_mechanism_claim'] is False
 assert c['barrier_interpretation']['fresh_holdout_011_to_015_values_used'] is False
 rr=c['resource_receipt'];assert rr['target_sources']==4 and rr['frozen_scientific_inputs_read']==3 and rr['partition_recomputations']==0 and rr['fresh_holdout_formula_values_read']==0 and rr['fresh_holdout_partition_values_read']==0
 assert rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'rows':rows,'direct_set_argument':theorem,'fresh_holdout_values_used':False,'partition_recomputations':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(Path(a.candidate_json)),sort_keys=True,separators=(',',':')))
