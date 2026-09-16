from __future__ import annotations
import argparse,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PORT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_RESULT_2026-09-16.json'
SIG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_RESULT_2026-09-16.json'
SOURCES=['UF20_02','UF20_03','UF20_04','UF20_05']
def main(candidate):
 p=json.loads(PORT.read_text());s=json.loads(SIG.read_text());pr={r['source']:r for r in p['source_outcomes']};sr={r['source']:r for r in s['source_summary']}
 rows=[]
 for n in SOURCES:
  labels={'CONNECTED_R000_R111_CORE','COMPOSITIONAL_OPEN_NO_SCHAEFER_BASIS','LOG_ALIEN_INAPPLICABLE','ORBIT_NO_NONTRIVIAL_EXCHANGEABILITY','SIGNED_IDENTITY_ONLY'}
  if sr[n]['first_all_singleton_level']=='S3':labels.add('S3_ALL_SINGLETON')
  if sr[n]['S3_non_singleton_classes'] and not sr[n]['all_exact_transposition_edges']:labels.add('S3_FALSE_COARSE_TWIN_WITHOUT_EXACT_TRANSPOSITION')
  rows.append({'source':n,'labels':sorted(labels),'checks':{'portfolio_unadmitted':pr[n]['status']=='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO','compositional':pr[n]['compositional']=='OPEN_COMPONENT_WITHOUT_SCHAEFER_BASIS','log_alien':pr[n]['log_alien']=='INAPPLICABLE_RELATION_SURFACE','orbit':pr[n]['orbit_status']=='OPEN_NO_NONTRIVIAL_EXCHANGEABILITY'}})
 inter=sorted(set(rows[0]['labels']).intersection(*(set(r['labels']) for r in rows[1:])))
 checks={'candidate_not_imported':True,'verdict':candidate.get('verdict')=='PASS_FOUR_UNADMITTED_EXISTING_EVIDENCE_RESIDUAL_MATRIX_COMPILED','rows':candidate.get('rows')==rows,'intersection':candidate.get('common_label_intersection')==inter}
 rr=candidate.get('resource_receipt',{});checks['resources']=all(rr.get(k)==0 for k in ['new_action_tests','portfolio_replays','solver_invocations','new_invariants','new_solver_mechanisms','new_carrier_mechanisms','new_adapters','new_quotients']) and rr.get('budget_raise') is False
 sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-FOUR-UNADMITTED-EXISTING-EVIDENCE-RESIDUAL-MATRIX-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_common_label_intersection':inter}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
