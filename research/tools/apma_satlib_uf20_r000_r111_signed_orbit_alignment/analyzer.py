from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PR=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_SIGNED_VS_SEALED_ORBIT_ALIGNMENT_PREREGISTRATION_2026-09-16.json'
SIGNED=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_EXACT_CERTIFICATE_RESULT_2026-09-16_v1.1.json'
PORT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_RESULT_2026-09-16.json'
TRANS=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXACT_TRANSPOSITION_WITNESS_LOCALIZATION_RESULT_2026-09-16.json'
EXPECTED={PR:'afd8092be86bc19b7f65359357fdb3b8e509add8',SIGNED:'1c2b7d35f970038616fa9f1decb20d67c88965f5',PORT:'89958034e76e1f0f97ea28b972df2acf90786bd5',TRANS:'ad05793643bca011d9ce9cd87fff9ae2a3e06181'}
def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def main():
 guards={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}
 if not all(guards.values()):return {'verdict':'FROZEN_AUTHORITY_GUARD_FAILURE','guards':guards}
 s=json.loads(SIGNED.read_text());p=json.loads(PORT.read_text());t=json.loads(TRANS.read_text())
 sr={r['source']:r for r in s['source_receipt']};pr={r['source']:r for r in p['source_outcomes']}
 w=sr['UF20_01']['unique_nonidentity_witness']
 checks={
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
 verdict='PASS_SIGNED_EXACT_WITNESS_ALIGNS_WITH_EXISTING_SEALED_ORBIT_CELL_AND_ADDS_NO_NEW_CLOSURES' if all(checks.values()) else 'CROSS_CERTIFICATE_MISMATCH'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-SIGNED-VS-SEALED-ORBIT-ALIGNMENT-2026-09-16-v1.0','authority':'DIAGNOSTIC_CROSS_CERTIFICATE_ALIGNMENT_ONLY__NO_NEW_ACTION_TEST_GROUP_SEARCH_QUOTIENT_SOLVER_OR_CARRIER','verdict':verdict,'guards':guards,'checks':checks,'aligned_witness':{'source':'UF20_01','pair':[7,10],'epsilon_flips':[],'sealed_orbit_cell':[7,10]},'other_four':['UF20_02','UF20_03','UF20_04','UF20_05'],'resource_receipt':{'new_action_tests':0,'portfolio_replays':0,'solver_invocations':0,'group_closure_computation':0,'quotient_states_enumerated':0,'new_invariants':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','SIGNED_ALIGNMENT_IMPLIES_TRACTABILITY':False,'SIGNED_ASYMMETRY_IMPLIES_HARDNESS':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
