from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Hashable

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_PREREGISTRATION_REVIEW_2026-09-17.json'
ROUTE=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SUCCESSOR_CLOSURE_LEVERAGE_REQUIREMENTS_SYNTHESIS_RESULT_2026-09-17.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
EXPECTED={PREREG:'cb82240f1b7183f6875cf20a658eca3270baad52',REVIEW:'38e8d7fb6a91f3aa66d36a742ef210ed47483b02',ROUTE:'c5e2e7b6e7612cea498045611d6173d8aa14ffe4',FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092'}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}
DIDS=('D1_PRIMAL_ARTICULATION_BLOCK_PROFILE','D2_INCIDENCE_ARTICULATION_BLOCK_PROFILE','D3_PRIMAL_MINIMAL_TWO_VERTEX_SEPARATOR_PROFILE')
CUBE=tuple(itertools.product((0,1),repeat=3))

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(path:Path):
 clauses=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   x=s.split();assert x[:2]==['p','cnf'] and len(x)==4;header=(int(x[2]),int(x[3]));continue
  vals=[int(z) for z in s.split()];assert len(vals)==4 and vals[-1]==0;clause=tuple(vals[:-1]);assert len({abs(x) for x in clause})==3;clauses.append(clause)
 assert header==(20,91) and len(clauses)==91;return clauses
def rid(clause):return ''.join('0' if lit>0 else '1' for lit in sorted(clause,key=lambda x:abs(x)))
def allowed(clause):
 scope=sorted(abs(x) for x in clause);out=[]
 for bits in CUBE:
  a=dict(zip(scope,bits))
  if any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in clause):out.append(list(bits))
 return sorted(out)
def independent_raw(name:str,clauses):
 selected=[(i,c) for i,c in enumerate(clauses,1) if rid(c) in {'000','111'}];V=sorted({abs(l) for _,c in selected for l in c});rows=[]
 for ordinal,c in selected:
  rows.append({'id':f'satlib_{name.lower()}_c{ordinal:03d}','scope':sorted(abs(x) for x in c),'allowed':allowed(c)})
 rows.sort(key=lambda r:(tuple(r['scope']),tuple(''.join(map(str,t)) for t in r['allowed']),r['id']))
 return {'variables':V,'constraints':rows}
def nkey(n:Hashable):
 if isinstance(n,tuple):return (0,int(n[1])) if n[0]=='VAR' else (1,str(n[1]))
 return (2,str(n))
def comps(g:dict[Hashable,set[Hashable]],removed:set[Hashable]|None=None):
 removed=removed or set();unseen=set(g)-removed;out=[]
 while unseen:
  start=min(unseen,key=nkey);unseen.remove(start);stack=[start];comp={start}
  while stack:
   u=stack.pop()
   for v in sorted(g[u],key=nkey):
    if v not in removed and v in unseen:unseen.remove(v);comp.add(v);stack.append(v)
  out.append(comp)
 out.sort(key=lambda c:(len(c),[nkey(x) for x in sorted(c,key=nkey)]));return out
def is_connected(g,removed=None):return len(comps(g,removed))<=1
def brute_articulations(g):
 base=len(comps(g));return [u for u in sorted(g,key=nkey) if len(comps(g,{u}))>base]
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
def D1(g):
 rows=[]
 for v in brute_articulations(g):rows.append({'variable':int(v),'residual_component_sizes':sorted(len(c) for c in comps(g,{v}) if c)})
 return {'articulation_rows':rows,'articulation_count':len(rows),'decomposition_present':any(len(r['residual_component_sizes'])>=2 for r in rows)}
def D2(g):
 rows=[]
 for a in brute_articulations(g):
  prof=[]
  for c in comps(g,{a}):
   nv=sum(x[0]=='VAR' for x in c);nc=sum(x[0]=='CONSTRAINT' for x in c);prof.append([nv,nc,nv+nc])
  prof.sort();rows.append({'node_type':a[0],'node_name':('v'+str(a[1])) if a[0]=='VAR' else str(a[1]),'residual_component_profiles':prof})
 rows.sort(key=lambda r:(r['node_type'],r['node_name']))
 return {'articulation_rows':rows,'articulation_count':len(rows),'decomposition_present':any(len(r['residual_component_profiles'])>=2 for r in rows)}
def D3(g):
 rows=[];base=is_connected(g);V=sorted(g)
 if base:
  for u,v in itertools.combinations(V,2):
   if not is_connected(g,{u}) or not is_connected(g,{v}):continue
   cs=[c for c in comps(g,{u,v}) if c]
   if len(cs)>=2:rows.append({'pair':[u,v],'residual_component_sizes':sorted(len(c) for c in cs)})
 return {'separator_rows':rows,'separator_count':len(rows),'decomposition_present':bool(rows),'base_primal_graph_connected':base}
def outcome(n):
 return 'COMMON_FOUR_SOURCE_STRUCTURAL_DIAGNOSTIC' if n==4 else 'PARTIAL_STRUCTURAL_DIAGNOSTIC' if 1<=n<=3 else 'NO_STRUCTURAL_DIAGNOSTIC'
def expected_rows():
 assert all(blob(p)==s for p,s in EXPECTED.items())
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());assert pre['status']=='FROZEN_BEFORE_ANY_STRUCTURAL_DECOMPOSITION_VALUE_COMPUTATION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE';assert tuple(pre['discovery_scope']['primary_execution_targets'])==ORDER
 rows=[]
 for name in ORDER:
  path,sblob,rsha=SOURCES[name];assert blob(path)==sblob;raw=independent_raw(name,parse(path));assert csha(raw)==rsha
  pg=primal(raw);ig=incidence(raw);receipt={'primal_vertex_count':len(pg),'primal_edge_count':sum(map(len,pg.values()))//2,'incidence_variable_node_count':len(raw['variables']),'incidence_constraint_node_count':len(raw['constraints']),'incidence_edge_count':sum(map(len,ig.values()))//2}
  rows.append({'source':name,'projected_raw_sha256':rsha,'graph_receipt':receipt,'diagnostics':{DIDS[0]:D1(pg),DIDS[1]:D2(ig),DIDS[2]:D3(pg)}})
 return rows
def main(candidate_path:Path):
 c=json.loads(candidate_path.read_text().strip().splitlines()[-1]);rows=expected_rows();assert c['rows']==rows,(c['rows'],rows)
 summary={}
 for did in DIDS:
  n=sum(r['diagnostics'][did]['decomposition_present'] for r in rows);summary[did]={'presence_count':n,'outcome':outcome(n),'sources_present':[r['source'] for r in rows if r['diagnostics'][did]['decomposition_present']],'sources_absent':[r['source'] for r in rows if not r['diagnostics'][did]['decomposition_present']]}
 if any(x['outcome']=='COMMON_FOUR_SOURCE_STRUCTURAL_DIAGNOSTIC' for x in summary.values()):overall='COMMON_FOUR_SOURCE_STRUCTURAL_LEVERAGE_PRESENT'
 elif any(x['outcome']=='PARTIAL_STRUCTURAL_DIAGNOSTIC' for x in summary.values()):overall='PARTIAL_STRUCTURAL_LEVERAGE_ONLY'
 else:overall='NO_TESTED_STRUCTURAL_DECOMPOSITION_LEVERAGE'
 assert c['diagnostic_summary']==summary and c['overall_outcome']==overall and c['verdict']==overall
 rr=c['resource_receipt'];assert rr['target_sources']==4 and rr['diagnostics']==3 and rr['fresh_holdout_values_read']==0 and rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['boundary_relation_enumerations']==0 and rr['component_solution_attempts']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0 and rr['budget_raise'] is False
 sf=c['scientific_firewall'];assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO' and sf['STRUCTURAL_SEPARATOR_IMPLIES_TRACTABILITY'] is False
 return {'verified':True,'candidate_imported':False,'verdict':overall,'diagnostic_summary':summary,'rows':rows,'fresh_holdout_values_read':0,'boundary_relation_enumerations':0,'component_solution_attempts':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(Path(a.candidate_json)),sort_keys=True,separators=(',',':')))
