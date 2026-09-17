from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Hashable

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_D2_D3_WITNESS_RECONSTRUCTION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_D2_D3_WITNESS_RECONSTRUCTION_PREREGISTRATION_REVIEW_2026-09-17.json'
FORENSIC=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_ALIGNMENT_RAW_BINDING_FORENSIC_RESULT_2026-09-17.json'
STRUCT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_RESULT_2026-09-17.json'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
EXPECTED={
 PREREG:'dff3dfe077e74a8635912dfd57fdb9ba0d8b0a5e',
 REVIEW:'e2cc765d7ab45862bb3d5a62d278eaf2772b6c2f',
 FORENSIC:'20d9fff8406bb3104563803831137812fbd89a1f',
 STRUCT:'0ec3e3aec564bb08e247ec9ef1ac75d22d97e915',
 PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b'),
}

def blob(p:Path)->str:
 d=p.read_bytes(); return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(path:Path):
 clauses=[];buf=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   p=s.split();assert p[:2]==['p','cnf'] and len(p)==4;header=(int(p[2]),int(p[3]));continue
  for z in map(int,s.split()):
   if z==0:
    assert len(buf)==3 and len({abs(x) for x in buf})==3;clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert header==(20,91) and len(clauses)==91 and not buf;return clauses
def core_clause(c):
 signs=[x>0 for x in c];return all(signs) or not any(signs)
def scope_surface(source:str,clauses):
 rows=[]
 for ordinal,c in enumerate(clauses,1):
  if core_clause(c):rows.append({'source_ordinal':ordinal,'constraint_id':f'satlib_{source.lower()}_c{ordinal:03d}','scope':sorted(abs(x) for x in c)})
 return rows

def nkey(n:Hashable):
 if isinstance(n,tuple):return (0,int(n[1])) if n[0]=='VAR' else (1,str(n[1]))
 return (2,str(n))
def components(g:dict[Hashable,set[Hashable]],removed:set[Hashable]|None=None):
 removed=removed or set();unseen=set(g)-removed;out=[]
 while unseen:
  s=min(unseen,key=nkey);unseen.remove(s);stack=[s];comp={s}
  while stack:
   u=stack.pop()
   for v in sorted(g[u],key=nkey):
    if v not in removed and v in unseen:unseen.remove(v);comp.add(v);stack.append(v)
  out.append(comp)
 out.sort(key=lambda c:(len(c),[nkey(x) for x in sorted(c,key=nkey)]));return out
def tarjan_articulations(g):
 disc={};low={};parent={};aps=set();clock=0
 def dfs(u):
  nonlocal clock
  clock+=1;disc[u]=low[u]=clock;children=0
  for v in sorted(g[u],key=nkey):
   if v not in disc:
    parent[v]=u;children+=1;dfs(v);low[u]=min(low[u],low[v])
    if parent.get(u) is None and children>1:aps.add(u)
    if parent.get(u) is not None and low[v]>=disc[u]:aps.add(u)
   elif v!=parent.get(u):low[u]=min(low[u],disc[v])
 for u in sorted(g,key=nkey):
  if u not in disc:parent[u]=None;dfs(u)
 return sorted(aps,key=nkey)
def build_incidence(surface):
 variables=sorted({v for r in surface for v in r['scope']});g={('VAR',v):set() for v in variables}
 for r in surface:
  c=('CONSTRAINT',r['constraint_id']);g[c]=set()
  for v in r['scope']:g[c].add(('VAR',v));g[('VAR',v)].add(c)
 return variables,g
def build_primal(variables,surface):
 g={v:set() for v in variables}
 for r in surface:
  for a,b in itertools.combinations(r['scope'],2):g[a].add(b);g[b].add(a)
 return g
def incidence_component_receipt(comp):
 return {'variables':sorted(int(n[1]) for n in comp if n[0]=='VAR'),'constraints':sorted(str(n[1]) for n in comp if n[0]=='CONSTRAINT'),'node_count':len(comp)}
def d2_rows(surface,ig):
 byid={r['constraint_id']:r for r in surface};rows=[]
 for node in tarjan_articulations(ig):
  if node[0]!='CONSTRAINT':continue
  cid=str(node[1]);comps=[incidence_component_receipt(c) for c in components(ig,{node})]
  singleton=[r['variables'][0] for r in comps if len(r['variables'])==1 and len(r['constraints'])==0]
  scope=list(byid[cid]['scope']);is_candidate=len(singleton)==1 and len(scope)==3 and singleton[0] in scope
  leaf=singleton[0] if is_candidate else None;gateway=sorted(v for v in scope if v!=leaf) if is_candidate else []
  rows.append({'constraint_id':cid,'source_ordinal':byid[cid]['source_ordinal'],'actual_scope':scope,'residual_components':comps,'variable_only_singletons':singleton,'singleton_attachment_candidate':is_candidate,'leaf_variable':leaf,'gateway_pair':gateway})
 return sorted(rows,key=lambda r:r['constraint_id'])
def d3_rows(pg):
 vertices=sorted(pg);base=len(components(pg,set()));rows=[]
 for u,v in itertools.combinations(vertices,2):
  if len(components(pg,{u}))>base or len(components(pg,{v}))>base:continue
  comps=components(pg,{u,v})
  if len(comps)<=base:continue
  exact=[sorted(int(x) for x in c) for c in comps];exact.sort(key=lambda c:(len(c),c));singletons=[c[0] for c in exact if len(c)==1]
  is_candidate=len(singletons)==1
  rows.append({'pair':[u,v],'residual_components':exact,'singleton_components':singletons,'singleton_attachment_candidate':is_candidate,'isolated_singleton':singletons[0] if is_candidate else None})
 return rows
def align(d2,d3):
 d2c=[r for r in d2 if r['singleton_attachment_candidate']];d3c=[r for r in d3 if r['singleton_attachment_candidate']]
 d2receipts=[]
 for r in d2c:
  matches=[q for q in d3c if q['pair']==r['gateway_pair'] and q['isolated_singleton']==r['leaf_variable']]
  d2receipts.append({'constraint_id':r['constraint_id'],'actual_scope':r['actual_scope'],'leaf_variable':r['leaf_variable'],'gateway_pair':r['gateway_pair'],'matching_D3_rows':[{'pair':q['pair'],'isolated_singleton':q['isolated_singleton']} for q in matches],'match_count':len(matches)})
 d3receipts=[]
 for q in d3c:
  matches=[r for r in d2c if r['gateway_pair']==q['pair'] and r['leaf_variable']==q['isolated_singleton']]
  d3receipts.append({'pair':q['pair'],'isolated_singleton':q['isolated_singleton'],'matching_D2_constraint_ids':[r['constraint_id'] for r in matches],'match_count':len(matches)})
 exact=bool(d2c) and bool(d3c) and all(r['match_count']==1 for r in d2receipts) and all(r['match_count']==1 for r in d3receipts) and len(d2c)==len(d3c)
 any_match=any(r['match_count'] for r in d2receipts) or any(r['match_count'] for r in d3receipts)
 label='EXACT_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_BIJECTION' if exact else 'PARTIAL_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT' if any_match else 'NO_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT'
 return {'D2_singleton_candidate_count':len(d2c),'D3_singleton_candidate_count':len(d3c),'D2_to_D3':d2receipts,'D3_to_D2':d3receipts,'per_source_alignment':label}
def firewall():return {'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','RAW_BOUND_ALIGNMENT_IMPLIES_TRACTABILITY':False,'RAW_BOUND_ALIGNMENT_IMPLIES_HARDNESS':False,'RAW_BOUND_ALIGNMENT_IMPLIES_SEMANTIC_TRANSPARENCY':False}
def main():
 binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={n:blob(p)==s for n,(p,s) in SOURCES.items()};pre=json.loads(PREREG.read_text());rev=json.loads(REVIEW.read_text());forensic=json.loads(FORENSIC.read_text());struct=json.loads(STRUCT.read_text())
 checks={'authority_bindings':all(binds.values()),'source_bindings':all(sb.values()),'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_RAW_BOUND_D2_D3_RECONSTRUCTION_VALUE_COMPUTATION','review_authorized':rev.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','forensic_verdict':forensic.get('verdict')=='STRUCTURAL_BINDING_MISMATCH_NOT_RECOVERABLE_BY_SCOPE_ONLY','old_alignment_input_forbidden':pre['target_scope']['old_alignment_mappings_may_be_used_as_input'] is False,'fresh_holdout_forbidden':pre['target_scope']['fresh_holdout_sources_may_be_read'] is False}
 guard={'ok':all(checks.values()),'checks':checks,'bindings':binds,'source_bindings':sb}
 if not guard['ok']:return {'verdict':'HALT_FROZEN_AUTHORITY_OR_SOURCE_BINDING_FAILURE','source_guard':guard,'scientific_firewall':firewall()}
 old={r['source']:r for r in struct['source_receipts']};rows=[]
 for source in ORDER:
  path,_=SOURCES[source];surface=scope_surface(source,parse(path));variables,ig=build_incidence(surface);pg=build_primal(variables,surface);D2=d2_rows(surface,ig);D3=d3_rows(pg);A=align(D2,D3)
  old_d2=int(old[source]['D2']['articulation_count']);old_d3=int(old[source]['D3']['separator_count'])
  rows.append({'source':source,'selected_source_ordinals':[r['source_ordinal'] for r in surface],'constraint_scope_surface_sha256':csha(surface),'variable_count':len(variables),'constraint_count':len(surface),'D2_rows':D2,'D3_rows':D3,'D2_articulation_count':len(D2),'D3_separator_count':len(D3),'old_structural_menu_count_comparison':{'old_D2_articulation_count':old_d2,'recomputed_D2_articulation_count':len(D2),'D2_count_equal':old_d2==len(D2),'old_D3_separator_count':old_d3,'recomputed_D3_separator_count':len(D3),'D3_count_equal':old_d3==len(D3)},'alignment':A})
 labels=[r['alignment']['per_source_alignment'] for r in rows]
 overall='COMMON_FOUR_EXACT_RAW_BOUND_ALIGNMENT' if all(x=='EXACT_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_BIJECTION' for x in labels) else 'MIXED_RAW_BOUND_ALIGNMENT' if any(x!='NO_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT' for x in labels) else 'NO_RAW_BOUND_ALIGNMENT'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-RAW-BOUND-D2-D3-WITNESS-RECONSTRUCTION-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_STRUCTURAL_RAW_BINDING_CORRECTION_ONLY__NO_RELATION_TABLE_BOUNDARY_SOLVER_ACTION_AUTOMORPHISM_GROUP_CARRIER_ADAPTER_OR_QUOTIENT','verdict':overall,'source_guard':guard,'rows':rows,'overall_alignment':overall,'resource_receipt':{'target_sources':4,'old_alignment_mappings_read':0,'allowed_table_value_reads':0,'boundary_relation_enumerations':0,'boundary_assignment_enumerations':0,'solver_invocations':0,'portfolio_replays':0,'component_solution_attempts':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'fresh_holdout_values_read':0},'scientific_firewall':firewall()}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
