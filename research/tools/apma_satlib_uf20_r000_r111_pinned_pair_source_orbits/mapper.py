from __future__ import annotations

import hashlib,json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PINNED_PAIR_SOURCE_CLAUSE_ORBIT_CLOSURE_PROVENANCE_PREREGISTRATION_2026-09-16.json'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_TRANSPOSITION_BREAK_SOURCE_PROVENANCE_RESULT_2026-09-16.json'
EXPECTED={PREREG:'5f03f82ca902d0d4871fedca71d40698318d0636',PARENT:'d94b4a8b84ad9127fb00fd2d52ec2335acd2405a'}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f')}

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def parse(path):
 out=[];buf=[];hdr=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):x=s.split();hdr=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3 and len({abs(x) for x in buf})==3;out.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert hdr==(20,91) and len(out)==91 and not buf;return out
def rtype(c):return ''.join('0' if lit>0 else '1' for lit in sorted(c,key=lambda z:abs(z)))
def swap_scope(scope,u,v):return sorted(v if x==u else u if x==v else x for x in scope)
def source_row(spec):
 name=spec['source'];path=SOURCES[name][0];clauses=parse(path);sel=set(spec['selected_clause_ordinals']);pair=spec['pair'];u,v=pair;selected=[]
 for i,c in enumerate(clauses,1):
  if i in sel:
   r=rtype(c);assert r in {'000','111'}
   selected.append({'ordinal':i,'source_literals':list(c),'scope':sorted(abs(x) for x in c),'relation_type':r})
 index=defaultdict(list)
 for x in selected:index[(x['relation_type'],tuple(x['scope']))].append(x['ordinal'])
 incident=[]
 for x in selected:
  if u not in x['scope'] and v not in x['scope']:continue
  image=swap_scope(x['scope'],u,v);matches=sorted(index.get((x['relation_type'],tuple(image)),[]))
  if image==x['scope']:cls='FIXED_SCOPE'
  elif matches:cls='CLOSED_IMAGE'
  else:cls='UNMATCHED_TO_ABSENT_IMAGE'
  incident.append({**x,'swapped_scope':image,'image_match_ordinals':matches,'image_match_count':len(matches),'classification':cls})
 counts=Counter(x['classification'] for x in incident);unmatched=[x for x in incident if x['classification']=='UNMATCHED_TO_ABSENT_IMAGE']
 return {'source':name,'pair':pair,'role':spec['role'],'selected_clause_count':len(selected),'incident_selected_clause_count':len(incident),'classification_counts':{k:counts.get(k,0) for k in ['FIXED_SCOPE','CLOSED_IMAGE','UNMATCHED_TO_ABSENT_IMAGE']},'incident_clauses':incident,'unmatched_source_ordinals':[x['ordinal'] for x in unmatched],'unmatched_image_scopes':[x['swapped_scope'] for x in unmatched],'source_orbit_closed_on_incident_selected_clauses':len(unmatched)==0}
def main():
 binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={n:blob(p)==s for n,(p,s) in SOURCES.items()}
 if not all(binds.values()) or not all(sb.values()):return {'verdict':'SOURCE_OR_PARENT_GUARD_FAILURE','source_guard':{'ok':False,'bindings':binds,'source_bindings':sb}}
 pre=json.loads(PREREG.read_text());rows=[source_row(s) for s in pre['pinned_sources_and_pairs']];by={r['source']:r for r in rows};control=by['UF20_01'];fail=by['UF20_03']
 if not control['source_orbit_closed_on_incident_selected_clauses']:verdict='CONTROL_SOURCE_ORBIT_NOT_CLOSED'
 elif fail['source_orbit_closed_on_incident_selected_clauses']:verdict='FALSE_PAIR_SOURCE_ORBIT_FULLY_CLOSED_UNEXPECTED'
 else:verdict='PASS_CONTROL_CLOSED_AND_FALSE_PAIR_HAS_SOURCE_ORBIT_DEFICIT'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PINNED-PAIR-SOURCE-CLAUSE-ORBIT-CLOSURE-PROVENANCE-2026-09-16-v1.0','authority':'DIAGNOSTIC_EXISTING_SWAP_SOURCE_ORBIT_PROVENANCE_ONLY__NO_NEW_INVARIANT_SEARCH_SOLVER_CARRIER_ADAPTER_OR_QUOTIENT','verdict':verdict,'source_guard':{'ok':True,'bindings':binds,'source_bindings':sb},'rows':rows,'resource_receipt':{'pinned_pairs':2,'other_pairs_tested':0,'solver_invocations':0,'assignment_cube_enumerations':0,'new_signature_features':0,'new_invariants':0,'new_group_search_mechanisms':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','SOURCE_ORBIT_CLOSURE_IMPLIES_TRACTABILITY':False,'SOURCE_ORBIT_DEFICIT_IMPLIES_HARDNESS':False,'NEW_INVARIANT_LICENSED':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
