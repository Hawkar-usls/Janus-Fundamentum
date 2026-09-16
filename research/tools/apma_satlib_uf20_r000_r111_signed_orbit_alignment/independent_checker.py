from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
SIGNED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_RESULT_2026-09-16_v1.1.json'
PORT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_RESULT_2026-09-16.json'
TRANS=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXACT_TRANSPOSITION_WITNESS_LOCALIZATION_RESULT_2026-09-16.json'
def main(candidate):
 s=json.loads(SIGNED.read_text());p=json.loads(PORT.read_text());t=json.loads(TRANS.read_text())
 sr={r['source']:r for r in s['source_receipt']};pr={r['source']:r for r in p['source_outcomes']};w=sr['UF20_01']['unique_nonidentity_witness']
 expected={
  'signed_total_nonidentity':s['total_nonidentity_exact_signed_automorphisms']==1,
  'signed_witness_source':sr['UF20_01']['nonidentity_exact_signed_automorphism_count']==1,
  'signed_witness_moves':w['sigma_moves']==[[7,10],[10,7]],
  'signed_witness_zero_epsilon':w['epsilon_flips']==[],
  'portfolio_orbit_cell':pr['UF20_01']['nontrivial_cells']==[[7,10]],
  'portfolio_closed_by_existing_orbit':pr['UF20_01']['status']=='CLOSED_BY_SEALED_ORBIT_COUNT_V1',
  'transposition_true_pair':t['passing_control']['pair']==[7,10] and t['passing_control']['predicate_result'] is True,
  'other_four_signed_identity_only':all(sr[n]['nonidentity_exact_signed_automorphism_count']==0 for n in ['UF20_02','UF20_03','UF20_04','UF20_05']),
  'other_four_portfolio_unadmitted':all(pr[n]['status']=='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO' for n in ['UF20_02','UF20_03','UF20_04','UF20_05'])
 }
 checks={'candidate_not_imported':True,'verdict':candidate.get('verdict')=='PASS_SIGNED_EXACT_WITNESS_ALIGNS_WITH_EXISTING_SEALED_ORBIT_CELL_AND_ADDS_NO_NEW_CLOSURES','checks':candidate.get('checks')==expected,'aligned_witness':candidate.get('aligned_witness')=={'source':'UF20_01','pair':[7,10],'epsilon_flips':[],'sealed_orbit_cell':[7,10]}}
 rr=candidate.get('resource_receipt',{});checks['resources']=all(rr.get(k)==0 for k in ['new_action_tests','portfolio_replays','solver_invocations','group_closure_computation','quotient_states_enumerated','new_invariants','new_solver_mechanisms','new_carrier_mechanisms','new_adapters','new_quotients']) and rr.get('budget_raise') is False
 sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('SIGNED_ALIGNMENT_IMPLIES_TRACTABILITY') is False and sf.get('SIGNED_ASYMMETRY_IMPLIES_HARDNESS') is False
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-SIGNED-VS-SEALED-ORBIT-ALIGNMENT-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_aligned_witness':{'source':'UF20_01','pair':[7,10],'epsilon_flips':[],'sealed_orbit_cell':[7,10]}}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
