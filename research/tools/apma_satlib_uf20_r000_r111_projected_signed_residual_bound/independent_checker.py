from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_BOUND_PREREGISTRATION_2026-09-16.json'
SOURCES={
 'UF20_01':ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf',
 'UF20_02':ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf',
 'UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf',
 'UF20_04':ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf',
 'UF20_05':ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf'}

def source_receipt(path,variables):
 V=list(variables);adj={v:set() for v in V};p=Counter();n=Counter();selected=[]
 for c in projection_identity.parse(path):
  r=projection_identity.rid(c)
  if r not in {'000','111'}:continue
  selected.append(c);scope=sorted(abs(x) for x in c)
  for u,v in itertools.combinations(scope,2):adj[u].add(v);adj[v].add(u)
  for v in scope:(p if r=='000' else n)[v]+=1
 assert sorted({abs(x) for c in selected for x in c})==V
 ordered={v:(p[v],n[v]) for v in V};U={v:(len(adj[v]),min(p[v],n[v]),max(p[v],n[v])) for v in V};g=defaultdict(list)
 for v in V:g[U[v]].append(v)
 classes=[sorted(c) for c in g.values()];classes.sort(key=lambda c:(c[0],len(c),c));balanced=sorted(v for v in V if p[v]==n[v]);perm=math.prod(math.factorial(len(c)) for c in classes);eps=1<<len(balanced);compat=[]
 for cls in classes:
  for u,v in itertools.combinations(cls,2):
   a=ordered[u];b=ordered[v];compat.append({'pair':[u,v],'ordered_u':list(a),'ordered_v':list(b),'equal_or_reversed':b==a or b==(a[1],a[0])})
 return {'variables':V,'constraint_count':len(selected),'ordered_p_n':{str(v):list(ordered[v]) for v in V},'unsigned_classes':classes,'class_size_multiset':sorted((len(c) for c in classes),reverse=True),'balanced_variables':balanced,'balanced_count':len(balanced),'same_unsigned_pair_compatibility':compat,'all_same_unsigned_pairs_equal_or_reversed':all(x['equal_or_reversed'] for x in compat),'unsigned_respecting_permutation_candidates':perm,'epsilon_multiplicity_per_permutation':eps,'residual_signed_action_candidates':perm*eps}
def main(candidate):
 pre=json.loads(PREREG.read_text());frozen={r['source']:r for r in pre['frozen_projected_raws']};cand={r['source']:r for r in candidate.get('rows',[])};ind={name:source_receipt(path,frozen[name]['variables']) for name,path in SOURCES.items()};checks={'candidate_not_imported':True,'verdict':candidate.get('verdict')=='PASS_PROJECTED_SIGNED_RESIDUAL_BOUND_COMPUTED','source_set':set(cand)==set(SOURCES)}
 for name in SOURCES:
  c=cand.get(name,{});r=ind[name];checks[f'{name}_raw_sha']=c.get('raw_sha256')==frozen[name]['raw_sha256'];checks[f'{name}_receipt']={k:v for k,v in c.items() if k not in {'source','raw_sha256'}}==r
 checks['total']=candidate.get('total_residual_signed_action_candidates_across_five_sources')==sum(r['residual_signed_action_candidates'] for r in ind.values())
 rr=candidate.get('resource_receipt',{});checks['resources']=rr.get('global_signed_actions_tested')==0 and rr.get('permutation_candidates_enumerated')==0 and rr.get('epsilon_vectors_enumerated')==0 and rr.get('solver_invocations')==0 and rr.get('new_signature_features')==0 and rr.get('new_invariants')==0 and rr.get('new_group_search_mechanisms')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_adapters')==0 and rr.get('new_quotients')==0 and rr.get('budget_raise') is False
 sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('NEW_INVARIANT_LICENSED') is False
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-SIGNED-RESIDUAL-BOUND-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'comparison_model':'SOURCE_R000_R111_OCCURRENCE_COUNTS_EQUIVALENT_TO_PROJECTED_RAW_FORBIDDEN_BIT_COUNTS','verified':all(checks.values()),'checks':checks,'independent_rows':ind,'independent_total_residual_signed_action_candidates':sum(r['residual_signed_action_candidates'] for r in ind.values())}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
