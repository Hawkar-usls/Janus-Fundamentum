from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Hashable

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_D2_D3_SINGLETON_ATTACHMENT_SCOPE_ALIGNMENT_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_D2_D3_SINGLETON_ATTACHMENT_SCOPE_ALIGNMENT_PREREGISTRATION_REVIEW_2026-09-17.json'
STRUCT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_RESULT_2026-09-17.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
EXPECTED={PREREG:'a06a3d8e2e3de7e936f1d3a2292e6245da61ac42',REVIEW:'c662eae27a57d08e5029f021c6e1905dc71a5fb2',STRUCT:'0ec3e3aec564bb08e247ec9ef1ac75d22d97e915',FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092',PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def nkey(n:Hashable):
 if isinstance(n,tuple):return (0,int(n[1])) if n[0]=='VAR' else (1,str(n[1]))
 return (2,str(n))
def comps(g:dict[Hashable,set[Hashable]],removed:set[Hashable]):
 unseen=set(g)-removed;out=[]
 while unseen:
  s=min(unseen,key=nkey);unseen.remove(s);stack=[s];comp={s}
  while stack:
   u=stack.pop()
   for v in sorted(g[u],key=nkey):
    if v not in removed and v in unseen:unseen.remove(v);comp.add(v);stack.append(v)
  out.append(comp)
 out.sort(key=lambda c:(len(c),[nkey(x) for x in sorted(c,key=nkey)]));return out
def primal(raw):
 g={int(v):set() for v in raw['variables']}
 for r in raw['constraints']:
  for a,b in itertools.combinations(r['scope'],2):a=int(a);b=int(b);g[a].add(b);g[b].add(a)
 return g
def incidence(raw):
 g={('VAR',int(v)):set() for v in raw['variables']}
 for r in raw['constraints']:
  c=('CONSTRAINT',str(r['id']));g[c]=set()
  for v in r['scope']:x=('VAR',int(v));g[x].add(c);g[c].add(x)
 return g
def singleton_variable_components_incidence(g,removed):
 return sorted(int(next(iter(c))[1]) for c in comps(g,removed) if len(c)==1 and next(iter(c))[0]=='VAR')
def singleton_variable_components_primal(g,removed):
 return sorted(int(next(iter(c))) for c in comps(g,removed) if len(c)==1)
def guard():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={n:blob(p)==sha for n,(p,sha,_) in SOURCES.items()}
 checks={'bindings':all(binds.values()),'source_bindings':all(sb.values()),'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_D2_D3_SCOPE_ALIGNMENT_VALUE_COMPUTATION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','targets_exact':tuple(pre['target_sources'])==ORDER,'no_relation_table_values':pre['alignment_contract']['no_relation_table_values_used'] is True,'fresh_holdout_values_forbidden':pre['fresh_holdout_firewall']['formula_feature_partition_structural_or_solver_values_may_be_read_or_computed'] is False}
 return {'ok':all(checks.values()),'checks':checks,'bindings':binds,'source_bindings':sb}
def source_alignment(name,path,expected_raw,frozen):
 clauses=projection_identity.parse(path);raw,_=projection_identity.normalize_projection(name,clauses);raw_sha=csha(raw)
 if raw_sha!=expected_raw:return {'source':name,'status':'HALT_PROJECTED_RAW_BINDING_FAILURE','observed_projected_raw_sha256':raw_sha}
 pg=primal(raw);ig=incidence(raw);by_id={r['id']:r for r in raw['constraints']};d2rows=frozen['D2']['articulation_rows'];d3rows=frozen['D3']['separator_rows'];frozen_d3_pairs=[tuple(r['pair']) for r in d3rows]
 d2_receipts=[]
 for row in d2rows:
  cid=row['node_name'];scope=sorted(int(v) for v in by_id[cid]['scope']);inc_singletons=singleton_variable_components_incidence(ig,{('CONSTRAINT',cid)});x=inc_singletons[0] if len(inc_singletons)==1 else None
  gateway=sorted(v for v in scope if v!=x) if x is not None and x in scope else []
  matched=[list(p) for p in frozen_d3_pairs if list(p)==gateway]
  primal_singletons=singleton_variable_components_primal(pg,set(gateway)) if len(gateway)==2 else []
  exact=(x is not None and len(scope)==3 and len(gateway)==2 and len(matched)==1 and x in primal_singletons)
  d2_receipts.append({'constraint_id':cid,'scope':scope,'incidence_singleton_variables_after_constraint_removal':inc_singletons,'singleton_variable':x,'gateway_pair':gateway,'matched_frozen_D3_pairs':matched,'primal_singleton_variables_after_gateway_pair_removal':primal_singletons,'same_singleton_exact':x is not None and x in primal_singletons,'aligned':exact})
 d3_receipts=[]
 for row in d3rows:
  pair=sorted(int(v) for v in row['pair']);ps=singleton_variable_components_primal(pg,set(pair));x=ps[0] if len(ps)==1 else None;matches=[]
  if x is not None:
   target=set(pair+[x])
   for d2 in d2_receipts:
    if set(d2['scope'])==target and d2['singleton_variable']==x and d2['aligned']:matches.append(d2['constraint_id'])
  exact=(x is not None and len(matches)==1)
  d3_receipts.append({'pair':pair,'primal_singleton_variables_after_pair_removal':ps,'singleton_variable':x,'matched_frozen_D2_constraint_ids':matches,'same_singleton_exact':exact,'aligned':exact})
 d2_matched=sum(r['aligned'] for r in d2_receipts);d3_matched=sum(r['aligned'] for r in d3_receipts);mapping={(r['constraint_id'],tuple(r['gateway_pair']),r['singleton_variable']) for r in d2_receipts if r['aligned']}
 exact_bijection=(len(d2rows)==len(d3rows)==d2_matched==d3_matched==len(mapping) and len(d2rows)>0)
 any_match=(d2_matched>0 or d3_matched>0)
 label='EXACT_D2_D3_SINGLETON_ATTACHMENT_BIJECTION' if exact_bijection else 'PARTIAL_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT' if any_match else 'NO_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT'
 return {'source':name,'status':'AUDITED','projected_raw_sha256':raw_sha,'frozen_D2_row_count':len(d2rows),'frozen_D3_row_count':len(d3rows),'D2_to_D3_receipts':d2_receipts,'D3_to_D2_receipts':d3_receipts,'D2_aligned_count':d2_matched,'D3_aligned_count':d3_matched,'unique_alignment_mapping_count':len(mapping),'per_source_alignment':label}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','GEOMETRIC_ALIGNMENT_IMPLIES_TRACTABILITY':False,'GEOMETRIC_ALIGNMENT_IMPLIES_CLOSURE':False,'GEOMETRIC_ALIGNMENT_IMPLIES_SMALL_BOUNDARY_RELATION':False}
def main():
 g=guard()
 if not g['ok']:return {'verdict':'HALT_FROZEN_AUTHORITY_OR_SOURCE_BINDING_FAILURE','source_guard':g,'scientific_firewall':firewall()}
 struct=json.loads(STRUCT.read_text());frozen={r['source']:r for r in struct['source_receipts']};rows=[]
 for name in ORDER:
  path,_,rsha=SOURCES[name];rows.append(source_alignment(name,path,rsha,frozen[name]))
 if any(r['status']!='AUDITED' for r in rows):return {'verdict':'HALT_PROJECTED_RAW_BINDING_FAILURE','source_guard':g,'rows':rows,'scientific_firewall':firewall()}
 labels=[r['per_source_alignment'] for r in rows]
 if all(x=='EXACT_D2_D3_SINGLETON_ATTACHMENT_BIJECTION' for x in labels):overall='COMMON_FOUR_EXACT_D2_D3_ALIGNMENT'
 elif any(x!='NO_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT' for x in labels):overall='PARTIAL_CROSS_SOURCE_D2_D3_ALIGNMENT'
 else:overall='NO_CROSS_SOURCE_D2_D3_ALIGNMENT'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-D2-D3-SINGLETON-ATTACHMENT-SCOPE-ALIGNMENT-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_FROZEN_STRUCTURAL_PROFILE_AND_SCOPE_ALIGNMENT_ONLY__NO_NEW_FEATURE_GRAPH_STATISTIC_BOUNDARY_RELATION_SOLVER_ACTION_AUTOMORPHISM_GROUP_SEARCH_CARRIER_ADAPTER_OR_QUOTIENT','verdict':overall,'source_guard':g,'rows':rows,'overall_alignment':overall,'resource_receipt':{'target_sources':4,'fresh_holdout_values_read':0,'new_feature_definitions':0,'new_graph_statistics':0,'relation_table_feature_reads':0,'boundary_relation_enumerations':0,'boundary_assignment_enumerations':0,'component_solution_attempts':0,'solver_invocations':0,'portfolio_replays':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'group_closure_computation':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
