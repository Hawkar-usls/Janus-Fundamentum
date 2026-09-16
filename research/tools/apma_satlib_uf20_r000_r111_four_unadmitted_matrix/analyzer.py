from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PR=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_FOUR_UNADMITTED_EXISTING_EVIDENCE_RESIDUAL_MATRIX_PREREGISTRATION_2026-09-16.json'
SRC=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SOURCE_BOUND_CORE_PROJECTION_RESULT_2026-09-16.json'
PORT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_RESULT_2026-09-16.json'
SIG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_RESULT_2026-09-16.json'
ALIGN=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_SIGNED_VS_SEALED_ORBIT_ALIGNMENT_RESULT_2026-09-16.json'
EXPECTED={PR:'537d8d9a0955426f6263dd36ae6d28772dc67275',SRC:'3a1e13a72183490a33e879d3f0c033f7c805b7e5',PORT:'89958034e76e1f0f97ea28b972df2acf90786bd5',SIG:'b7ba5bd772c3092e0436dde8bd717dc28985983c',ALIGN:'d20150284fef9926d828f9903a6b9f5c56c10b01'}
SOURCES=['UF20_02','UF20_03','UF20_04','UF20_05']
def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def main():
 guards={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()}
 if not all(guards.values()):return {'verdict':'FROZEN_AUTHORITY_GUARD_FAILURE','guards':guards}
 src=json.loads(SRC.read_text());port=json.loads(PORT.read_text());sig=json.loads(SIG.read_text());align=json.loads(ALIGN.read_text())
 port_rows={r['source']:r for r in port['source_outcomes']};sig_rows={r['source']:r for r in sig['source_summary']}
 rows=[]
 for n in SOURCES:
  labels={'CONNECTED_R000_R111_CORE','COMPOSITIONAL_OPEN_NO_SCHAEFER_BASIS','LOG_ALIEN_INAPPLICABLE','ORBIT_NO_NONTRIVIAL_EXCHANGEABILITY','SIGNED_IDENTITY_ONLY'}
  s=sig_rows[n]
  if s['first_all_singleton_level']=='S3':labels.add('S3_ALL_SINGLETON')
  if s['S3_non_singleton_classes'] and not s['all_exact_transposition_edges']:labels.add('S3_FALSE_COARSE_TWIN_WITHOUT_EXACT_TRANSPOSITION')
  p=port_rows[n]
  checks={'portfolio_unadmitted':p['status']=='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO','compositional':p['compositional']=='OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS','log_alien':p['log_alien']=='INAPPLICABLE_RELATION_SURFACE','orbit':p['orbit_status']=='OPEN_NO_NONTRIVIAL_EXCHANGEABILITY'}
  rows.append({'source':n,'labels':sorted(labels),'checks':checks})
 intersection=sorted(set(rows[0]['labels']).intersection(*(set(r['labels']) for r in rows[1:])))
 verdict='PASS_FOUR_UNADMITTED_EXISTING_EVIDENCE_RESIDUAL_MATRIX_COMPILED' if all(all(r['checks'].values()) for r in rows) else 'CROSS_RESULT_MATRIX_MISMATCH'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-FOUR-UNADMITTED-EXISTING-EVIDENCE-RESIDUAL-MATRIX-2026-09-16-v1.0','authority':'DIAGNOSTIC_CROSS_RESULT_RESIDUAL_OBLIGATION_MATRIX_ONLY__NO_NEW_INVARIANT_ACTION_TEST_SOLVER_CARRIER_ADAPTER_QUOTIENT_OR_SEARCH','verdict':verdict,'guards':guards,'rows':rows,'common_label_intersection':intersection,'resource_receipt':{'new_action_tests':0,'portfolio_replays':0,'solver_invocations':0,'new_invariants':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO'}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
