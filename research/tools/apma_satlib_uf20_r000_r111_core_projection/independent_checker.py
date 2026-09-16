from __future__ import annotations

import argparse, hashlib, json
from collections import Counter, defaultdict
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
  if s.startswith('p '):x=s.split();hdr=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3 and len({abs(x) for x in buf})==3;clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert hdr==(20,91) and len(clauses)==91 and not buf;return clauses

def rel(cl):return ''.join('0' if lit>0 else '1' for lit in sorted(cl,key=lambda x:abs(x)))

def comps(adj):
 unseen=set(adj);out=[]
 while unseen:
  start=min(unseen,key=str);stack=[start];unseen.remove(start);cc=[]
  while stack:
   u=stack.pop();cc.append(u)
   for v in sorted(adj[u],key=str):
    if v in unseen:unseen.remove(v);stack.append(v)
  out.append(cc)
 return out

def project(path):
 selected=[]
 for idx,cl in enumerate(parse(path),1):
  r=rel(cl)
  if r in CORE:selected.append((idx,cl,r,sorted(abs(x) for x in cl)))
 cnt=Counter(x[2] for x in selected);vs=sorted({v for x in selected for v in x[3]})
 p={v:set() for v in vs}
 for _,_,_,xs in selected:
  for u in xs:
   p[u].update(v for v in xs if v!=u)
 pcc=[sorted(c) for c in comps(p)] if p else []
 ia=defaultdict(set);by={x[0]:x for x in selected}
 for idx,_,_,xs in selected:
  c=('c',idx);ia[c]
  for v in xs:ia[c].add(('v',v));ia[('v',v)].add(c)
 ic=[]
 for cc in comps(dict(ia)) if ia else []:
  cv=sorted(n[1] for n in cc if n[0]=='v');co=sorted(n[1] for n in cc if n[0]=='c');rt=sorted({by[o][2] for o in co});mixed=CORE.issubset(rt)
  ic.append({'variables':cv,'variable_count':len(cv),'clause_ordinals':co,'clause_count':len(co),'relation_types':rt,'mixed_core':mixed})
 ic.sort(key=lambda x:(x['clause_ordinals'][0] if x['clause_ordinals'] else 10**9,x['variable_count']))
 mixed=[x for x in ic if x['mixed_core']];m=sum(x['clause_count'] for x in mixed)
 return {'selected_clause_count':len(selected),'selected_clause_count_by_relation_type':{'000':cnt['000'],'111':cnt['111']},'selected_variables':vs,'selected_variable_count':len(vs),'selected_variable_coverage_fraction':len(vs)/20,'primal_component_count':len(pcc),'primal_components':pcc,'incidence_component_count':len(ic),'incidence_components':ic,'mixed_core_component_count':len(mixed),'mixed_core_clause_count':m,'mixed_core_clause_coverage_fraction':(m/len(selected) if selected else 0.0),'has_connected_mixed_core':bool(mixed)}

def main(candidate):
 binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sg={n:blob(p)==s for n,(p,s) in SOURCES.items()};rows=[{'source':n,**project(p)} for n,(p,_) in SOURCES.items()];k=sum(r['has_connected_mixed_core'] for r in rows);expected_verdict='PASS_SOURCE_BOUND_R000_R111_MIXED_CORE_CONNECTED_IN_ALL_FIVE' if k==5 else 'NO_SOURCE_HAS_CONNECTED_R000_R111_MIXED_CORE' if k==0 else 'PARTIAL_SOURCE_BOUND_R000_R111_MIXED_CORE_CONNECTIVITY';checks={'candidate_not_imported':True,'guards':all(binds.values()) and all(sg.values()),'verdict':candidate.get('verdict')==expected_verdict,'source_count':candidate.get('sources_with_connected_mixed_core')==k,'rows':candidate.get('rows')==rows};rr=candidate.get('resource_receipt',{});checks['resources']=rr.get('solver_invocations')==0 and rr.get('assignment_cube_enumerations')==0 and rr.get('formula_subset_enumerations')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_adapters')==0 and rr.get('new_quotients')==0 and rr.get('budget_raise') is False;sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('R000_R111_CONNECTED_COMPONENT_IMPLIES_HARDNESS') is False;return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-SOURCE-BOUND-CORE-PROJECTION-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_sources_with_connected_mixed_core':k,'independent_rows':rows}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
