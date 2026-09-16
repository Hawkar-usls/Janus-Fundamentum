from __future__ import annotations
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_basis import compositional_basis
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit_candidate
from research.tools.apma_connected_mixed_post_orbit_obstruction_census import census as census
ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_PREREGISTRATION_2026-09-16.json'
SOURCES={'UF20_01':ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','UF20_02':ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','UF20_04':ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','UF20_05':ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf'}
CLOSED={'ADMIT_ORBIT_COUNT_QUOTIENT_SAT','ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT'}
def cb(o):return json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def replay(name,path,exp):
 raw,ords=projection_identity.normalize_projection(name,projection_identity.parse(path));sha=hashlib.sha256(cb(raw)).hexdigest();assert sha==exp['projected_raw_sha256'] and ords==exp['clause_ordinals'] and raw['variables']==exp['variables']
 elig=census.eligibility(raw);assert elig.get('eligible')
 comp=compositional_basis.induce_compositional_basis(raw);cr={'status':comp.get('status'),'component_count':comp.get('component_count'),'open_component_count':comp.get('open_component_count')}
 la=census.replay_log_alien(raw)
 if la.get('closed'):
  win=la.get('winning_attempt',{});return {'source':name,'status':'CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER','raw_sha256':sha,'eligibility':elig,'compositional':cr,'log_alien':la,'orbit':{'executed':False,'reason':'STOP_ON_FIRST_EXISTING_AUTHORITATIVE_CLOSURE'},'closure':{'mechanism':'SEALED_LOG_ALIEN_CONSTRAINT_EXACT_TRANSFER','status':win.get('status')}}
 o=orbit_candidate.run_candidate(raw);orr={'executed':True,'status':o.get('status'),'solver_authority':o.get('solver_authority'),'raw_semantic_sha256':o.get('raw_semantic_sha256'),'cells':o.get('cells'),'nontrivial_cells':o.get('nontrivial_cells'),'quotient_states_Q':o.get('quotient_states_Q'),'certificate_type':(o.get('certificate') or {}).get('type'),'resource_receipt':o.get('resource_receipt',{})}
 if o.get('status') in CLOSED and o.get('solver_authority') is True:s='CLOSED_BY_SEALED_ORBIT_COUNT_V1';cl={'mechanism':'EXACT_TRANSPOSITION_ORBIT_COUNT_QUOTIENT','status':o.get('status')}
 else:s='UNADMITTED_AFTER_CURRENT_SEALED_PORTFOLIO';cl=None
 return {'source':name,'status':s,'raw_sha256':sha,'eligibility':elig,'compositional':cr,'log_alien':la,'orbit':orr,'closure':cl}
def main(c):
 pre=json.loads(PREREG.read_text());exp={r['source']:r for r in pre['frozen_projected_raw_identities']};rows=[replay(n,p,exp[n]) for n,p in SOURCES.items()];counts=dict(sorted(Counter(r['status'] for r in rows).items()));checks={'candidate_not_imported':True,'candidate_verdict':c.get('verdict')=='PASS_DIAGNOSTIC_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY','rows':c.get('rows')==rows,'outcome_counts':c.get('outcome_counts')==counts,'resources':c.get('resource_receipt',{}).get('new_solver_mechanisms')==0 and c.get('resource_receipt',{}).get('new_carrier_mechanisms')==0 and c.get('resource_receipt',{}).get('new_adapters')==0 and c.get('resource_receipt',{}).get('budget_raise') is False,'firewall':c.get('scientific_firewall',{}).get('P_VS_NP')=='OPEN' and c.get('scientific_firewall',{}).get('GENERAL_SAT_IN_P')=='NOT_PROVED'};return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-SEALED-PORTFOLIO-REPLAY-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_rows':rows,'independent_outcome_counts':counts}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
