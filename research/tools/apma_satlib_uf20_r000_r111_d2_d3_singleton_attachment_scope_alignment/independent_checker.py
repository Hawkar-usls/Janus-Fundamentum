from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Hashable

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_D2_D3_SINGLETON_ATTACHMENT_SCOPE_ALIGNMENT_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_D2_D3_SINGLETON_ATTACHMENT_SCOPE_ALIGNMENT_PREREGISTRATION_REVIEW_2026-09-17.json'
STRUCT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_RESULT_2026-09-17.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
EXPECTED={PREREG:'a06a3d8e2e3de7e936f1d3a2292e6245da61ac42',REVIEW:'c662eae27a57d08e5029f021c6e1905dc71a5fb2',STRUCT:'0ec3e3aec564bb08e247ec9ef1ac75d22d97e915',FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092'}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}
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
  vals=[int(z) for z in s.split()];assert len(vals)==4 and vals[-1]==0;c=tuple(vals[:-1]);assert len({abs(x) for x in c})==3;clauses.append(c)
 assert header==(20,91) and len(clauses)==91;return clauses
def rid(c):return ''.join('0' if x>0 else '1' for x in sorted(c,key=lambda z:abs(z)))
def allowed(c):
 scope=sorted(abs(x) for x in c);out=[]
 for bits in CUBE:
  a=dict(zip(scope,bits))
  if any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in c):out.append(list(bits))
 return sorted(out)
def raw_project(name,clauses):
 selected=[(i,c) for i,c in enumerate(clauses,1) if rid(c) in {'000','111'}];V=sorted({abs(l) for _,c in selected for l in c});rows=[]
 for ordinal,c in selected:rows.append({'id':f'satlib_{name.lower()}_c{ordinal:03d}','scope':sorted(abs(x) for x in c),'allowed':allowed(c)})
 rows.sort(key=lambda r:(tuple(r['scope']),tuple(''.join(map(str,t)) for t in r['allowed']),r['id']))
 return {'variables':V,'constraints':rows}
def nkey(n:Hashable):
 if isinstance(n,tuple):return (0,int(n[1])) if n[0]=='VAR' else (1,str(n[1]))
 return (2,str(n))
def comps(g,removed):
 unseen=set(g)-removed;out=[]
 while unseen:
  s=min(unseen,key=nkey);unseen.remove(s);stack=[s];cc={s}
  while stack:
   u=stack.pop()
   for v in sorted(g[u],key=nkey):
    if v not in removed and v in unseen:unseen.remove(v);cc.add(v);stack.append(v)
  out.append(cc)
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
def inc_singletons(g,cid):return sorted(int(next(iter(c))[1]) for c in comps(g,{('CONSTRAINT',cid)}) if len(c)==1 and next(iter(c))[0]=='VAR')
def primal_singletons(g,pair):return sorted(int(next(iter(c))) for c in comps(g,set(pair)) if len(c)==1)
def expected_rows():
 assert all(blob(p)==s for p,s in EXPECTED.items())
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());assert pre['status']=='FROZEN_BEFORE_ANY_D2_D3_SCOPE_ALIGNMENT_VALUE_COMPUTATION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 struct=json.loads(STRUCT.read_text());frozen={r['source']:r for r in struct['source_receipts']};rows=[]
 for name in ORDER:
  path,sblob,rsha=SOURCES[name];assert blob(path)==sblob;raw=raw_project(name,parse(path));assert csha(raw)==rsha
  pg=primal(raw);ig=incidence(raw);by_id={r['id']:r for r in raw['constraints']};d2rows=frozen[name]['D2']['articulation_rows'];d3rows=frozen[name]['D3']['separator_rows'];d3pairs=[tuple(r['pair']) for r in d3rows];d2out=[]
  for row in d2rows:
   cid=row['node_name'];scope=sorted(int(v) for v in by_id[cid]['scope']);incs=inc_singletons(ig,cid);x=incs[0] if len(incs)==1 else None;gateway=sorted(v for v in scope if v!=x) if x is not None and x in scope else [];matched=[list(p) for p in d3pairs if list(p)==gateway];ps=primal_singletons(pg,gateway) if len(gateway)==2 else [];exact=x is not None and len(scope)==3 and len(gateway)==2 and len(matched)==1 and x in ps
   d2out.append({'constraint_id':cid,'scope':scope,'incidence_singleton_variables_after_constraint_removal':incs,'singleton_variable':x,'gateway_pair':gateway,'matched_frozen_D3_pairs':matched,'primal_singleton_variables_after_gateway_pair_removal':ps,'same_singleton_exact':x is not None and x in ps,'aligned':exact})
  d3out=[]
  for row in d3rows:
   pair=sorted(int(v) for v in row['pair']);ps=primal_singletons(pg,pair);x=ps[0] if len(ps)==1 else None;matches=[]
   if x is not None:
    target=set(pair+[x])
    for d2 in d2out:
     if set(d2['scope'])==target and d2['singleton_variable']==x and d2['aligned']:matches.append(d2['constraint_id'])
   exact=x is not None and len(matches)==1;d3out.append({'pair':pair,'primal_singleton_variables_after_pair_removal':ps,'singleton_variable':x,'matched_frozen_D2_constraint_ids':matches,'same_singleton_exact':exact,'aligned':exact})
  dm=sum(r['aligned'] for r in d2out);gm=sum(r['aligned'] for r in d3out);mapping={(r['constraint_id'],tuple(r['gateway_pair']),r['singleton_variable']) for r in d2out if r['aligned']};exact=len(d2rows)==len(d3rows)==dm==gm==len(mapping) and len(d2rows)>0;anymatch=dm>0 or gm>0;label='EXACT_D2_D3_SINGLETON_ATTACHMENT_BIJECTION' if exact else 'PARTIAL_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT' if anymatch else 'NO_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT'
  rows.append({'source':name,'status':'AUDITED','projected_raw_sha256':rsha,'frozen_D2_row_count':len(d2rows),'frozen_D3_row_count':len(d3rows),'D2_to_D3_receipts':d2out,'D3_to_D2_receipts':d3out,'D2_aligned_count':dm,'D3_aligned_count':gm,'unique_alignment_mapping_count':len(mapping),'per_source_alignment':label})
 return rows
def main(candidate_path:Path):
 c=json.loads(candidate_path.read_text().strip().splitlines()[-1]);rows=expected_rows();assert c['rows']==rows,(c['rows'],rows);labels=[r['per_source_alignment'] for r in rows]
 overall='COMMON_FOUR_EXACT_D2_D3_ALIGNMENT' if all(x=='EXACT_D2_D3_SINGLETON_ATTACHMENT_BIJECTION' for x in labels) else 'PARTIAL_CROSS_SOURCE_D2_D3_ALIGNMENT' if any(x!='NO_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT' for x in labels) else 'NO_CROSS_SOURCE_D2_D3_ALIGNMENT'
 assert c['verdict']==overall and c['overall_alignment']==overall
 rr=c['resource_receipt'];assert rr['target_sources']==4 and rr['fresh_holdout_values_read']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['relation_table_feature_reads']==0 and rr['boundary_relation_enumerations']==0 and rr['boundary_assignment_enumerations']==0 and rr['component_solution_attempts']==0 and rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0
 sf=c['scientific_firewall'];assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO' and sf['GEOMETRIC_ALIGNMENT_IMPLIES_TRACTABILITY'] is False
 return {'verified':True,'candidate_imported':False,'verdict':overall,'rows':rows,'fresh_holdout_values_read':0,'relation_table_feature_reads':0,'boundary_relation_enumerations':0,'component_solution_attempts':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(Path(a.candidate_json)),sort_keys=True,separators=(',',':')))
