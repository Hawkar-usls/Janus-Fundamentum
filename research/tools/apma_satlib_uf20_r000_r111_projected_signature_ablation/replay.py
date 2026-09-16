from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity
from research.tools.apma_unseen_local_invariant_orbit_count import candidate as orbit

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_PREREGISTRATION_2026-09-16.json'
EXPECTED={
 PREREG:'ce1f188d18d3bbedbebc356aeca86f7aed0e9417',
 ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SEALED_PORTFOLIO_REPLAY_RESULT_2026-09-16.json':'89958034e76e1f0f97ea28b972df2acf90786bd5',
 ROOT/'research/TRUMP_SATLIB_UF20_SIGNATURE_ABLATION_REPLICATION_PREREGISTRATION_2026-09-16.json':'ec7c43258ecb76426f114dde9b75f528ad12e480',
 ROOT/'research/TRUMP_SATLIB_UF20_SIGNATURE_ABLATION_REPLICATION_RESULT_2026-09-16.json':'bca1542226c7fe29f8d803b7473c4aa4c19d1e78',
 ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/candidate.py':'a076cfc56d68aad0348415e313705da1f6b9cdcd',
 ROOT/'research/tools/apma_unseen_local_invariant_orbit_count/independent_checker.py':'0e12304d843ef0bcce6b6c032fd2af2c68abcd14',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py':'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4',
}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
CUBE=tuple(itertools.product((0,1),repeat=3))
LEVELS=('S0','S1','S2','S3')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def relation_key_rows(rows)->tuple[str,...]:return tuple(sorted(''.join(str(int(b)) for b in row) for row in rows))
def full_surface_order():
 keys=[]
 for forbidden in CUBE:
  allowed=[r for r in CUBE if r!=forbidden];keys.append((relation_key_rows(allowed),''.join(map(str,forbidden))))
 keys.sort(key=lambda x:x[0]);return [k for k,_ in keys],[rid for _,rid in keys]

def guard():
 binds={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={n:blob(p)==s for n,(p,s) in SOURCES.items()};return {'ok':all(binds.values()) and all(sb.values()),'bindings':binds,'source_bindings':sb}
def projected_expectations():return {r['source']:r for r in json.loads(PREREG.read_text())['frozen_projected_raw_identities']}
def projected_clauses(path):
 clauses=projection_identity.parse(path);return [c for c in clauses if projection_identity.rid(c) in {'000','111'}]
def features(raw,clauses):
 variables=raw['variables'];adj={v:set() for v in variables}
 for c in raw['constraints']:
  for u,v in itertools.combinations(c['scope'],2):adj[u].add(v);adj[v].add(u)
 degree={v:len(adj[v]) for v in variables};pos=Counter();neg=Counter()
 for clause in clauses:
  for lit in clause:(pos if lit>0 else neg)[abs(lit)]+=1
 surface_keys,surface_rids=full_surface_order();assert surface_rids==['111','110','101','100','011','010','001','000']
 index={k:i for i,k in enumerate(surface_keys)};inc={v:[0]*8 for v in variables}
 for c in raw['constraints']:
  k=relation_key_rows(c['allowed']);i=index[k]
  for v in c['scope']:inc[v][i]+=1
 return {v:{'S0':(degree[v],),'S1':(degree[v],pos[v],neg[v]),'S2':(degree[v],pos[v],neg[v],tuple(inc[v])),'S3':(degree[v],pos[v],neg[v],tuple(inc[v]),tuple(sorted(degree[n] for n in adj[v])))} for v in variables}
def partition(feats,level):
 groups=defaultdict(list)
 for v in sorted(feats):groups[json.dumps(feats[v][level],separators=(',',':'))].append(v)
 out=[sorted(x) for x in groups.values()];out.sort(key=lambda c:(c[0],len(c),c));return out
def audit_level(formula,classes):
 non=[c for c in classes if len(c)>1];edges=[];tested=0
 for cls in non:
  for u,v in itertools.combinations(cls,2):
   tested+=1
   if orbit.is_exact_transposition_automorphism(formula,u,v):edges.append([u,v])
 return {'class_count':len(classes),'class_size_multiset':sorted((len(c) for c in classes),reverse=True),'max_class_size':max(map(len,classes)),'non_singleton_class_count':len(non),'variables_in_non_singleton_classes':sum(len(c) for c in non),'non_singleton_classes':non,'candidate_pairs_tested':tested,'exact_transposition_count':len(edges),'exact_transposition_edges':edges}
def one(name,path,exp):
 raw,ords=projection_identity.normalize_projection(name,projection_identity.parse(path));sha=csha(raw)
 if sha!=exp['raw_sha256'] or raw['variables']!=exp['variables']:return {'source':name,'status':'PROJECTED_RAW_OR_SEALED_BINDING_GUARD_FAILURE','observed_raw_sha256':sha}
 formula=orbit.validate_and_normalize(raw);feats=features(raw,projected_clauses(path));levels={L:audit_level(formula,partition(feats,L)) for L in LEVELS}
 first_single=next((L for L in LEVELS if levels[L]['non_singleton_class_count']==0),None);first_edge=next((L for L in LEVELS if levels[L]['exact_transposition_count']>0),None)
 all_edges=sorted({tuple(e) for L in LEVELS for e in levels[L]['exact_transposition_edges']})
 return {'source':name,'status':'PROFILED','raw_sha256':sha,'levels':levels,'first_all_singleton_level':first_single,'first_level_with_exact_transposition':first_edge,'all_exact_transposition_edges':[list(e) for e in all_edges]}
def main():
 g=guard()
 if not g['ok']:return {'verdict':'PROJECTED_RAW_OR_SEALED_BINDING_GUARD_FAILURE','source_guard':g}
 exp=projected_expectations();rows=[one(n,p,exp[n]) for n,(p,_) in SOURCES.items()]
 if any(r['status']!='PROFILED' for r in rows):verdict='PROJECTED_RAW_OR_SEALED_BINDING_GUARD_FAILURE'
 else:
  with_edges=[r['source'] for r in rows if r['all_exact_transposition_edges']]
  verdict='PROJECTED_ABLATION_REPLAY_LOCALIZES_CLOSED_CONTROL_EDGE' if with_edges==['UF20_01'] else 'PROJECTED_ABLATION_REPLAY_NO_EXACT_TRANSPOSITIONS_ANY_SOURCE' if not with_edges else 'PROJECTED_ABLATION_REPLAY_MULTIPLE_SOURCES_HAVE_EXACT_TRANSPOSITIONS'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-EXISTING-SIGNATURE-ABLATION-REPLAY-2026-09-16-v1.0','authority':'DIAGNOSTIC_REPLAY_OF_ALREADY_FROZEN_SIGNATURES_AND_EXACT_TRANSPOSITION_ONLY__NO_NEW_INVARIANT_GROUP_SEARCH_SOLVER_OR_CARRIER','verdict':verdict,'source_guard':g,'eight_relation_surface_order':full_surface_order()[1],'rows':rows,'resource_receipt':{'pairs_outside_same_coarse_class_tested':0,'solver_invocations':0,'quotient_states_enumerated':0,'full_variable_cube_states_enumerated':0,'new_signature_features':0,'new_group_search_mechanisms':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','ASYMMETRY_IMPLIES_HARDNESS':False,'SYMMETRY_IMPLIES_TRACTABILITY':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
