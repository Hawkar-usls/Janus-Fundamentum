from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_PREREGISTRATION_2026-09-16.json'
SOURCES={
 'UF20_01':ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf',
 'UF20_02':ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf',
 'UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf',
 'UF20_04':ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf',
 'UF20_05':ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf'}
CUBE=tuple(itertools.product((0,1),repeat=3));LEVELS=('S0','S1','S2','S3')

def csha(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rkey(rows):return tuple(sorted(''.join(str(int(b)) for b in row) for row in rows))
def surface_order():
 xs=[]
 for f in CUBE:xs.append((rkey([r for r in CUBE if r!=f]),''.join(map(str,f))))
 xs.sort(key=lambda x:x[0]);return [x[0] for x in xs],[x[1] for x in xs]
def selected_clauses(path):return [c for c in projection_identity.parse(path) if projection_identity.rid(c) in {'000','111'}]
def feature_map(raw,clauses):
 V=raw['variables'];adj={v:set() for v in V}
 for c in raw['constraints']:
  for u,v in itertools.combinations(c['scope'],2):adj[u].add(v);adj[v].add(u)
 deg={v:len(adj[v]) for v in V};pos=Counter();neg=Counter()
 for c in clauses:
  for lit in c:(pos if lit>0 else neg)[abs(lit)]+=1
 keys,rids=surface_order();assert rids==['111','110','101','100','011','010','001','000'];idx={k:i for i,k in enumerate(keys)};inc={v:[0]*8 for v in V}
 for c in raw['constraints']:
  j=idx[rkey(c['allowed'])]
  for v in c['scope']:inc[v][j]+=1
 return {v:{'S0':(deg[v],),'S1':(deg[v],pos[v],neg[v]),'S2':(deg[v],pos[v],neg[v],tuple(inc[v])),'S3':(deg[v],pos[v],neg[v],tuple(inc[v]),tuple(sorted(deg[n] for n in adj[v])))} for v in V}
def classes(F,L):
 g=defaultdict(list)
 for v in sorted(F):g[json.dumps(F[v][L],separators=(',',':'))].append(v)
 out=[sorted(x) for x in g.values()];out.sort(key=lambda c:(c[0],len(c),c));return out
def level_row(formula,cs):
 ns=[c for c in cs if len(c)>1];edges=[];tested=0
 for c in ns:
  for u,v in itertools.combinations(c,2):
   tested+=1
   if orbit.is_exact_transposition_automorphism(formula,u,v):edges.append([u,v])
 return {'class_count':len(cs),'class_size_multiset':sorted((len(c) for c in cs),reverse=True),'max_class_size':max(map(len,cs)),'non_singleton_class_count':len(ns),'variables_in_non_singleton_classes':sum(len(c) for c in ns),'non_singleton_classes':ns,'candidate_pairs_tested':tested,'exact_transposition_count':len(edges),'exact_transposition_edges':edges}
def row(name,path,exp):
 raw,_=projection_identity.normalize_projection(name,projection_identity.parse(path));sha=csha(raw);assert sha==exp['raw_sha256'] and raw['variables']==exp['variables'];formula=orbit.validate_and_normalize(raw);F=feature_map(raw,selected_clauses(path));lv={L:level_row(formula,classes(F,L)) for L in LEVELS};first_single=next((L for L in LEVELS if lv[L]['non_singleton_class_count']==0),None);first_edge=next((L for L in LEVELS if lv[L]['exact_transposition_count']>0),None);edges=sorted({tuple(e) for L in LEVELS for e in lv[L]['exact_transposition_edges']});return {'source':name,'status':'PROFILED','raw_sha256':sha,'levels':lv,'first_all_singleton_level':first_single,'first_level_with_exact_transposition':first_edge,'all_exact_transposition_edges':[list(e) for e in edges]}
def main(candidate):
 pre=json.loads(PREREG.read_text());exp={r['source']:r for r in pre['frozen_projected_raw_identities']};rows=[row(n,p,exp[n]) for n,p in SOURCES.items()];with_edges=[r['source'] for r in rows if r['all_exact_transposition_edges']];expected='PROJECTED_ABLATION_REPLAY_LOCALIZES_CLOSED_CONTROL_EDGE' if with_edges==['UF20_01'] else 'PROJECTED_ABLATION_REPLAY_NO_EXACT_TRANSPOSITIONS_ANY_SOURCE' if not with_edges else 'PROJECTED_ABLATION_REPLAY_MULTIPLE_SOURCES_HAVE_EXACT_TRANSPOSITIONS';checks={'candidate_not_imported':True,'verdict':candidate.get('verdict')==expected,'surface_order':candidate.get('eight_relation_surface_order')==surface_order()[1],'rows':candidate.get('rows')==rows};rr=candidate.get('resource_receipt',{});checks['resources']=rr.get('pairs_outside_same_coarse_class_tested')==0 and rr.get('solver_invocations')==0 and rr.get('quotient_states_enumerated')==0 and rr.get('full_variable_cube_states_enumerated')==0 and rr.get('new_signature_features')==0 and rr.get('new_group_search_mechanisms')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_adapters')==0 and rr.get('new_quotients')==0 and rr.get('budget_raise') is False;sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('ASYMMETRY_IMPLIES_HARDNESS') is False and sf.get('SYMMETRY_IMPLIES_TRACTABILITY') is False;return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-EXISTING-SIGNATURE-ABLATION-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_rows':rows,'independent_sources_with_exact_edges':with_edges}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);o=main(c);print(json.dumps(o,sort_keys=True,separators=(',',':')));raise SystemExit(0 if o['verified'] else 1)
