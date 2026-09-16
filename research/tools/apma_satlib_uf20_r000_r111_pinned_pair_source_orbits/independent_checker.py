from __future__ import annotations
import argparse,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PINNED_PAIR_SOURCE_CLAUSE_ORBIT_CLOSURE_PROVENANCE_PREREGISTRATION_2026-09-16.json'
SOURCES={'UF20_01':ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf'}
def parse(path):
 out=[];buf=[];hdr=None
 for raw in path.read_text().splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):x=s.split();hdr=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3 and len({abs(x) for x in buf})==3;out.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert hdr==(20,91) and len(out)==91 and not buf;return out
def rt(c):return ''.join('0' if x>0 else '1' for x in sorted(c,key=lambda z:abs(z)))
def sw(scope,u,v):return sorted(v if x==u else u if x==v else x for x in scope)
def make(spec):
 clauses=parse(SOURCES[spec['source']]);sel=set(spec['selected_clause_ordinals']);u,v=spec['pair'];selected=[]
 for i,c in enumerate(clauses,1):
  if i in sel:selected.append({'ordinal':i,'source_literals':list(c),'scope':sorted(abs(x) for x in c),'relation_type':rt(c)})
 idx=defaultdict(list)
 for x in selected:idx[(x['relation_type'],tuple(x['scope']))].append(x['ordinal'])
 inc=[]
 for x in selected:
  if u not in x['scope'] and v not in x['scope']:continue
  image=sw(x['scope'],u,v);m=sorted(idx.get((x['relation_type'],tuple(image)),[]));cl='FIXED_SCOPE' if image==x['scope'] else 'CLOSED_IMAGE' if m else 'UNMATCHED_TO_ABSENT_IMAGE';inc.append({**x,'swapped_scope':image,'image_match_ordinals':m,'image_match_count':len(m),'classification':cl})
 cnt=Counter(x['classification'] for x in inc);bad=[x for x in inc if x['classification']=='UNMATCHED_TO_ABSENT_IMAGE']
 return {'source':spec['source'],'pair':spec['pair'],'role':spec['role'],'selected_clause_count':len(selected),'incident_selected_clause_count':len(inc),'classification_counts':{k:cnt.get(k,0) for k in ['FIXED_SCOPE','CLOSED_IMAGE','UNMATCHED_TO_ABSENT_IMAGE']},'incident_clauses':inc,'unmatched_source_ordinals':[x['ordinal'] for x in bad],'unmatched_image_scopes':[x['swapped_scope'] for x in bad],'source_orbit_closed_on_incident_selected_clauses':not bad}
def main(c):
 pre=json.loads(PREREG.read_text());rows=[make(s) for s in pre['pinned_sources_and_pairs']];by={r['source']:r for r in rows};expected='CONTROL_SOURCE_ORBIT_NOT_CLOSED' if not by['UF20_01']['source_orbit_closed_on_incident_selected_clauses'] else 'FALSE_PAIR_SOURCE_ORBIT_FULLY_CLOSED_UNEXPECTED' if by['UF20_03']['source_orbit_closed_on_incident_selected_clauses'] else 'PASS_CONTROL_CLOSED_AND_FALSE_PAIR_HAS_SOURCE_ORBIT_DEFICIT';checks={'candidate_not_imported':True,'verdict':c.get('verdict')==expected,'rows':c.get('rows')==rows};rr=c.get('resource_receipt',{});checks['resources']=rr.get('pinned_pairs')==2 and rr.get('other_pairs_tested')==0 and rr.get('solver_invocations')==0 and rr.get('assignment_cube_enumerations')==0 and rr.get('new_signature_features')==0 and rr.get('new_invariants')==0 and rr.get('new_group_search_mechanisms')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_adapters')==0 and rr.get('new_quotients')==0 and rr.get('budget_raise') is False;sf=c.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('NEW_INVARIANT_LICENSED') is False;return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PINNED-PAIR-SOURCE-ORBIT-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_rows':rows,'independent_expected_verdict':expected}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
