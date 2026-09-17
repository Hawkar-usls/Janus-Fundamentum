from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
STRUCT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_RESULT_2026-09-17.json'
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf',
 'UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf',
 'UF20_04':ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf',
 'UF20_05':ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf',
}

def csha(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(path):
 out=[];buf=[];header=None
 for line in path.read_text(encoding='utf-8').splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):p=s.split();header=(int(p[2]),int(p[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3;out.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert header==(20,91) and len(out)==91 and not buf;return out
def surface(source,path):
 rows=[]
 for i,c in enumerate(parse(path),1):
  pos=sum(x>0 for x in c)
  if pos in {0,3}:rows.append({'source_ordinal':i,'constraint_id':f'satlib_{source.lower()}_c{i:03d}','scope':sorted(abs(x) for x in c)})
 return rows
def ikey(n):return (0,n[1]) if n[0]=='VAR' else (1,n[1])
def icomponents(g,removed=frozenset()):
 unseen=set(g)-set(removed);out=[]
 while unseen:
  s=min(unseen,key=ikey);unseen.remove(s);stack=[s];comp={s}
  while stack:
   u=stack.pop()
   for v in g[u]:
    if v not in removed and v in unseen:unseen.remove(v);comp.add(v);stack.append(v)
  out.append(comp)
 out.sort(key=lambda c:(len(c),[ikey(x) for x in sorted(c,key=ikey)]));return out
def pcomponents(g,removed=frozenset()):
 unseen=set(g)-set(removed);out=[]
 while unseen:
  s=min(unseen);unseen.remove(s);stack=[s];comp={s}
  while stack:
   u=stack.pop()
   for v in g[u]:
    if v not in removed and v in unseen:unseen.remove(v);comp.add(v);stack.append(v)
  out.append(comp)
 out.sort(key=lambda c:(len(c),sorted(c)));return out
def graphs(surf):
 variables=sorted({v for r in surf for v in r['scope']});ig={('VAR',v):set() for v in variables};pg={v:set() for v in variables}
 for r in surf:
  c=('CONSTRAINT',r['constraint_id']);ig[c]=set()
  for v in r['scope']:ig[c].add(('VAR',v));ig[('VAR',v)].add(c)
  for a,b in itertools.combinations(r['scope'],2):pg[a].add(b);pg[b].add(a)
 return variables,ig,pg
def comp_receipt(comp):return {'variables':sorted(n[1] for n in comp if n[0]=='VAR'),'constraints':sorted(n[1] for n in comp if n[0]=='CONSTRAINT'),'node_count':len(comp)}
def D2(surf,ig):
 byid={r['constraint_id']:r for r in surf};base=len(icomponents(ig));rows=[]
 for cid in sorted(byid):
  node=('CONSTRAINT',cid);cs=icomponents(ig,{node})
  if len(cs)<=base:continue
  receipts=[comp_receipt(c) for c in cs];single=[r['variables'][0] for r in receipts if len(r['variables'])==1 and len(r['constraints'])==0];scope=list(byid[cid]['scope']);cand=len(single)==1 and len(scope)==3 and single[0] in scope;leaf=single[0] if cand else None;gateway=sorted(v for v in scope if v!=leaf) if cand else []
  rows.append({'constraint_id':cid,'source_ordinal':byid[cid]['source_ordinal'],'actual_scope':scope,'residual_components':receipts,'variable_only_singletons':single,'singleton_attachment_candidate':cand,'leaf_variable':leaf,'gateway_pair':gateway})
 return rows
def D3(pg):
 vertices=sorted(pg);base=len(pcomponents(pg));rows=[]
 for u,v in itertools.combinations(vertices,2):
  if len(pcomponents(pg,{u}))>base or len(pcomponents(pg,{v}))>base:continue
  cs=pcomponents(pg,{u,v})
  if len(cs)<=base:continue
  exact=[sorted(c) for c in cs];exact.sort(key=lambda c:(len(c),c));single=[c[0] for c in exact if len(c)==1];cand=len(single)==1
  rows.append({'pair':[u,v],'residual_components':exact,'singleton_components':single,'singleton_attachment_candidate':cand,'isolated_singleton':single[0] if cand else None})
 return rows
def alignment(d2,d3):
 a=[r for r in d2 if r['singleton_attachment_candidate']];b=[r for r in d3 if r['singleton_attachment_candidate']];r2=[];r3=[]
 for r in a:
  m=[q for q in b if q['pair']==r['gateway_pair'] and q['isolated_singleton']==r['leaf_variable']]
  r2.append({'constraint_id':r['constraint_id'],'actual_scope':r['actual_scope'],'leaf_variable':r['leaf_variable'],'gateway_pair':r['gateway_pair'],'matching_D3_rows':[{'pair':q['pair'],'isolated_singleton':q['isolated_singleton']} for q in m],'match_count':len(m)})
 for q in b:
  m=[r for r in a if r['gateway_pair']==q['pair'] and r['leaf_variable']==q['isolated_singleton']]
  r3.append({'pair':q['pair'],'isolated_singleton':q['isolated_singleton'],'matching_D2_constraint_ids':[r['constraint_id'] for r in m],'match_count':len(m)})
 exact=bool(a) and bool(b) and len(a)==len(b) and all(x['match_count']==1 for x in r2) and all(x['match_count']==1 for x in r3);anym=any(x['match_count'] for x in r2) or any(x['match_count'] for x in r3);label='EXACT_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_BIJECTION' if exact else 'PARTIAL_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT' if anym else 'NO_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT'
 return {'D2_singleton_candidate_count':len(a),'D3_singleton_candidate_count':len(b),'D2_to_D3':r2,'D3_to_D2':r3,'per_source_alignment':label}
def expected_rows():
 old={r['source']:r for r in json.loads(STRUCT.read_text())['source_receipts']};rows=[]
 for source in ORDER:
  s=surface(source,SOURCES[source]);vars_,ig,pg=graphs(s);d2=D2(s,ig);d3=D3(pg);al=alignment(d2,d3);od2=int(old[source]['D2']['articulation_count']);od3=int(old[source]['D3']['separator_count'])
  rows.append({'source':source,'selected_source_ordinals':[r['source_ordinal'] for r in s],'constraint_scope_surface_sha256':csha(s),'variable_count':len(vars_),'constraint_count':len(s),'D2_rows':d2,'D3_rows':d3,'D2_articulation_count':len(d2),'D3_separator_count':len(d3),'old_structural_menu_count_comparison':{'old_D2_articulation_count':od2,'recomputed_D2_articulation_count':len(d2),'D2_count_equal':od2==len(d2),'old_D3_separator_count':od3,'recomputed_D3_separator_count':len(d3),'D3_count_equal':od3==len(d3)},'alignment':al})
 return rows
def main(path):
 c=json.loads(Path(path).read_text().strip().splitlines()[-1]);rows=expected_rows();assert c['rows']==rows,(c['rows'],rows);labels=[r['alignment']['per_source_alignment'] for r in rows];overall='COMMON_FOUR_EXACT_RAW_BOUND_ALIGNMENT' if all(x=='EXACT_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_BIJECTION' for x in labels) else 'MIXED_RAW_BOUND_ALIGNMENT' if any(x!='NO_RAW_BOUND_D2_D3_SINGLETON_ATTACHMENT_ALIGNMENT' for x in labels) else 'NO_RAW_BOUND_ALIGNMENT';assert c['verdict']==overall and c['overall_alignment']==overall;rr=c['resource_receipt'];assert rr['old_alignment_mappings_read']==0 and rr['allowed_table_value_reads']==0 and rr['boundary_relation_enumerations']==0 and rr['solver_invocations']==0 and rr['fresh_holdout_values_read']==0
 return {'verified':True,'candidate_imported':False,'verdict':overall,'rows':rows,'resource_receipt':rr}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--candidate-json',required=True);a=p.parse_args();print(json.dumps(main(a.candidate_json),sort_keys=True,separators=(',',':')))
