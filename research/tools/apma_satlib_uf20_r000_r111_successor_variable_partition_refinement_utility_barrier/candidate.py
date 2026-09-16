from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_VARIABLE_PARTITION_REFINEMENT_UTILITY_BARRIER_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_VARIABLE_PARTITION_REFINEMENT_UTILITY_BARRIER_PREREGISTRATION_REVIEW_2026-09-17.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
PARTITIONS=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_RESULT_2026-09-17.json'
PORTFOLIO=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_RESULT_2026-09-16.json'
SIGNED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_RESULT_2026-09-16_v1.1.json'
EXPECTED={
 PREREG:'ecb5cafcb3fc59d7d938cee3927819d459c5d3e3',
 REVIEW:'8d10b0ed12628db792c37f942ef206c210b2e0e4',
 FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092',
 PARTITIONS:'971d7d98a86471e88bf33336da215171b2f8cdfe',
 PORTFOLIO:'89958034e76e1f0f97ea28b972df2acf90786bd5',
 SIGNED:'1c2b7d35f970038616fa9f1decb20d67c88965f5'}
TARGET=('UF20_02','UF20_03','UF20_04','UF20_05')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def is_discrete_receipt(receipt:dict[str,Any],stage:str)->bool:
 if stage=='S3':return receipt.get('S3_all_singleton') is True
 if stage=='L3':return receipt.get('L3_all_singleton') is True
 raise ValueError(stage)
def direct_refinement_fact_check(n:int)->dict[str,Any]:
 # Symbolic finite-set witness: D_n is the singleton partition. Any nonempty block
 # contained in a singleton is that singleton; coverage forces all n singletons.
 if n < 1:raise ValueError(n)
 discrete=[frozenset((i,)) for i in range(n)]
 each_nonempty_subset_of_discrete_block_is_singleton=all(len(b)==1 for b in discrete)
 coverage_size=len(set().union(*discrete))
 return {'ground_set_cardinality_symbolic_example':n,'discrete_block_count':len(discrete),'each_nonempty_subset_of_a_discrete_block_must_be_singleton':each_nonempty_subset_of_discrete_block_is_singleton,'discrete_partition_covers_ground_set':coverage_size==n,'claim_verified_by_direct_set_argument':each_nonempty_subset_of_discrete_block_is_singleton and coverage_size==n}
def guard()->dict[str,Any]:
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text())
 binds={str(p.relative_to(ROOT)):blob(p)==sha for p,sha in EXPECTED.items()}
 checks={'bindings':all(binds.values()),'prereg_status':pre.get('status')=='FROZEN_BEFORE_BARRIER_SYNTHESIS_EXECUTION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','target_exact':tuple(pre.get('target_sources',()))==TARGET,'fresh_holdout_values_forbidden':pre['fresh_holdout_firewall']['formula_content_may_be_used_in_this_gate'] is False and pre['fresh_holdout_firewall']['projected_values_may_be_computed_in_this_gate'] is False}
 return {'ok':all(checks.values()),'checks':checks,'bindings':binds}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','REFINEMENT_BARRIER_IMPLIES_NO_USEFUL_INVARIANT':False,'REFINEMENT_BARRIER_IMPLIES_HARDNESS':False,'REFINEMENT_BARRIER_IMPLIES_TRACTABILITY':False}
def main()->dict[str,Any]:
 g=guard()
 if not g['ok']:return {'verdict':'HALT_FROZEN_AUTHORITY_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 part=json.loads(PARTITIONS.read_text());port=json.loads(PORTFOLIO.read_text());signed=json.loads(SIGNED.read_text())
 receipts=part['key_partition_receipts'];pout={r['source']:r for r in port['source_outcomes']};sout={r['source']:r for r in signed['source_receipt']}
 pre=json.loads(PREREG.read_text());rows=[]
 for source in TARGET:
  expected_witnesses=pre['frozen_current_status_contract'][source]['existing_discrete_partition_witnesses']
  witnessed=[stage for stage in expected_witnesses if is_discrete_receipt(receipts[source],stage)]
  portfolio_ok=pout[source]['status']=='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO' and pout[source]['orbit_status']=='OPEN_NO_NONTRIVIAL_EXCHANGEABILITY'
  signed_count=int(sout[source]['nonidentity_exact_signed_automorphism_count']);signed_ok=signed_count==0
  has_discrete=bool(witnessed)
  rows.append({'source':source,'portfolio_status':pout[source]['status'],'orbit_status':pout[source]['orbit_status'],'signed_nonidentity_exact_automorphism_count':signed_count,'existing_discrete_partition_witnesses_verified':witnessed,'at_least_one_existing_partition_is_discrete':has_discrete,'refinement_of_verified_discrete_partition_can_have_non_singleton_block':False if has_discrete else None,'portfolio_unadmitted_and_no_exchangeability_verified':portfolio_ok,'signed_identity_only_verified':signed_ok})
 theorem=direct_refinement_fact_check(7)
 passed=all(r['at_least_one_existing_partition_is_discrete'] and r['portfolio_unadmitted_and_no_exchangeability_verified'] and r['signed_identity_only_verified'] and r['refinement_of_verified_discrete_partition_can_have_non_singleton_block'] is False for r in rows) and theorem['claim_verified_by_direct_set_argument']
 verdict='PASS_CURRENT_FOUR_SOURCE_REFINEMENT_ONLY_VARIABLE_PARTITION_UTILITY_BARRIER__NO_NON_SINGLETON_CLASS_LEVERAGE' if passed else 'FAIL_BARRIER_AT_LEAST_ONE_CURRENTLY_UNADMITTED_SOURCE_LACKS_A_FROZEN_DISCRETE_PARTITION_WITNESS'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-SUCCESSOR-VARIABLE-PARTITION-REFINEMENT-UTILITY-BARRIER-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_PARTITION_MONOTONICITY_AND_CURRENT_CLOSURE_RELEVANCE_AUDIT_ONLY__NO_NEW_FEATURE_GRAPH_STATISTIC_ACTION_TEST_GROUP_SEARCH_SOLVER_CARRIER_ADAPTER_OR_QUOTIENT','verdict':verdict,'source_guard':g,'rows':rows,'finite_partition_fact_receipt':theorem,'barrier_interpretation':{'blocked_candidate_class':'REFINEMENT_ONLY_VARIABLE_PARTITION_SUCCESSORS_REQUIRING_NON_SINGLETON_SAME_CLASS_LEVERAGE_ON_THE_CURRENT_FOUR_UNADMITTED_SOURCES','no_possible_useful_invariant_or_mechanism_claim':False,'fresh_holdout_011_to_015_values_used':False},'resource_receipt':{'target_sources':4,'frozen_scientific_inputs_read':3,'partition_recomputations':0,'fresh_holdout_formula_values_read':0,'fresh_holdout_partition_values_read':0,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_feature_definitions':0,'new_graph_statistics':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
