from __future__ import annotations

import hashlib, json
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_SOURCE_BOUND_CORE_PROJECTION_PREREGISTRATION_2026-09-16.json'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORE_RESULT_2026-09-16.json'
EXPECTED={PREREG:'bfcbf90b47d2188b56131e954886097b0f0e42a7',PARENT:'a46c22fa2134b251f9d19ebc40cb25a2d418a13d'}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
CORE={'000','111'}

def blob(p):
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def parse(path):
 clauses=[];buf=[];hdr=None
 for raw in path.read_text().splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   x=s.split();hdr=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:
    assert len(buf)==3 and len({abs(x) for x in buf})==3
    clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert hdr==(20,91) and len(clauses)==91 and not buf
 return clauses

def rid(cl):
 return ''.join('0' if lit>0 else '1' for lit in sorted(cl,key=lambda x:abs(x)))

def components(adj):
 unseen=set(adj);out=[]
 while unseen:
  start=min(unseen,key=str);q=[start];unseen.remove(start);comp=[]
  while q:
   u=q.pop();comp.append(u)
   for v in sorted(adj[u],key=str):
    if v in unseen:unseen.remove(v);q.append(v)
  out.append(comp)
 return out

def analyze_source(path):
 clauses=parse(path);selected=[]
 for i,cl in enumerate(clauses,1):
  r=rid(cl)
  if r in CORE:selected.append({'ordinal':i,'literals':list(cl),'relation_type':r,'variables':sorted(abs(x) for x in cl)})
 counts=Counter(x['relation_type'] for x in selected);vars_=sorted({v for x in selected for v in x['variables']})
 padj={v:set() for v in vars_}
 for x in selected:
  vs=x['variables']
  for a in vs:
   for b in vs:
    if a!=b:padj[a].add(b)
 pcomps=[sorted(c) for c in components(padj)] if padj else []
 iadj=defaultdict(set)
 by_ord={x['ordinal']:x for x in selected}
 for x in selected:
  c=('c',x['ordinal']);iadj[c]
  for v in x['variables']:
   n=('v',v);iadj[c].add(n);iadj[n].add(c)
 icomps=[]
 for comp in components(dict(iadj)) if iadj else []:
  vs=sorted(n[1] for n in comp if n[0]=='v');ords=sorted(n[1] for n in comp if n[0]=='c');types=sorted({by_ord[o]['relation_type'] for o in ords});mixed=CORE.issubset(types)
  icomps.append({'variables':vs,'variable_count':len(vs),'clause_ordinals':ords,'clause_count':len(ords),'relation_types':types,'mixed_core':mixed})
 icomps.sort(key=lambda x:(x['clause_ordinals'][0] if x['clause_ordinals'] else 10**9,x['variable_count']))
 mixed=[x for x in icomps if x['mixed_core']];mixed_clause_count=sum(x['clause_count'] for x in mixed)
 return {'selected_clause_count':len(selected),'selected_clause_count_by_relation_type':{'000':counts['000'],'111':counts['111']},'selected_variables':vars_,'selected_variable_count':len(vars_),'selected_variable_coverage_fraction':len(vars_)/20,'primal_component_count':len(pcomps),'primal_components':pcomps,'incidence_component_count':len(icomps),'incidence_components':icomps,'mixed_core_component_count':len(mixed),'mixed_core_clause_count':mixed_clause_count,'mixed_core_clause_coverage_fraction':(mixed_clause_count/len(selected) if selected else 0.0),'has_connected_mixed_core':bool(mixed)}

def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sg={n:blob(p)==s for n,(p,s) in SOURCES.items()}
 if not all(bindings.values()) or not all(sg.values()):return {'verdict':'SOURCE_OR_PARENT_GUARD_FAILURE','source_guard':{'bindings':bindings,'source_bindings':sg,'ok':False}}
 rows=[{'source':n,**analyze_source(p)} for n,(p,_) in SOURCES.items()];k=sum(r['has_connected_mixed_core'] for r in rows)
 verdict='PASS_SOURCE_BOUND_R000_R111_MIXED_CORE_CONNECTED_IN_ALL_FIVE' if k==5 else 'NO_SOURCE_HAS_CONNECTED_R000_R111_MIXED_CORE' if k==0 else 'PARTIAL_SOURCE_BOUND_R000_R111_MIXED_CORE_CONNECTIVITY'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-SOURCE-BOUND-CORE-PROJECTION-2026-09-16-v1.0','authority':'DIAGNOSTIC_SOURCE_PROJECTION_AND_STRUCTURE_ONLY__NO_SAT_SOLVING_OR_NEW_MECHANISM','verdict':verdict,'source_guard':{'bindings':bindings,'source_bindings':sg,'ok':True},'sources_with_connected_mixed_core':k,'rows':rows,'resource_receipt':{'solver_invocations':0,'assignment_cube_enumerations':0,'formula_subset_enumerations':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','R000_R111_CONNECTED_COMPONENT_IMPLIES_HARDNESS':False}}

if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
