from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_SIGNED_RESIDUAL_BOUND_PREREGISTRATION_2026-09-16.json'
EXPECTED={
 PREREG:'ed877e119178bd4794e84ac2975fcda0f73268e1',
 ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNED_ACTION_COMPATIBILITY_AUDIT_2026-09-16.json':'182f68377db4034c037f425849b9b8211246fbf7',
 ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_DIRECT_PROOF_2026-09-16.md':'e1515e047e53535882913d3764425814290f3334',
 ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_EPSILON_DETERMINATION_DIRECT_PROOF_2026-09-16.md':'adfa4b1dd935109e5593fba7509d37ba5fe0400b',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py':'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
CUBE=tuple(itertools.product((0,1),repeat=3))

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def canonical_sha(raw:Any)->str:return hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def frozen_rows():return {r['source']:r for r in json.loads(PREREG.read_text())['frozen_projected_raws']}
def unique_forbidden(c):
 allowed={tuple(int(x) for x in row) for row in c['allowed']}
 missing=set(CUBE)-allowed
 if len(c['scope'])!=3 or len(allowed)!=7 or len(missing)!=1:raise ValueError('NON_SINGLE_FORBIDDEN_TUPLE_RELATION_FOUND')
 return next(iter(missing))
def receipt(raw):
 V=list(raw['variables']);adj={v:set() for v in V};p=Counter();n=Counter()
 for c in raw['constraints']:
  f=unique_forbidden(c);scope=list(c['scope'])
  for u,v in itertools.combinations(scope,2):adj[u].add(v);adj[v].add(u)
  for v,b in zip(scope,f,strict=True):(p if b==0 else n)[v]+=1
 ordered={v:(p[v],n[v]) for v in V};U={v:(len(adj[v]),min(p[v],n[v]),max(p[v],n[v])) for v in V};groups=defaultdict(list)
 for v in V:groups[U[v]].append(v)
 classes=[sorted(c) for c in groups.values()];classes.sort(key=lambda c:(c[0],len(c),c));balanced=sorted(v for v in V if p[v]==n[v]);perm=math.prod(math.factorial(len(c)) for c in classes);eps=1<<len(balanced)
 compatibility=[]
 for cls in classes:
  for u,v in itertools.combinations(cls,2):
   a=ordered[u];b=ordered[v];compatibility.append({'pair':[u,v],'ordered_u':list(a),'ordered_v':list(b),'equal_or_reversed':b==a or b==(a[1],a[0])})
 return {'variables':V,'constraint_count':len(raw['constraints']),'ordered_p_n':{str(v):list(ordered[v]) for v in V},'unsigned_classes':classes,'class_size_multiset':sorted((len(c) for c in classes),reverse=True),'balanced_variables':balanced,'balanced_count':len(balanced),'same_unsigned_pair_compatibility':compatibility,'all_same_unsigned_pairs_equal_or_reversed':all(x['equal_or_reversed'] for x in compatibility),'unsigned_respecting_permutation_candidates':perm,'epsilon_multiplicity_per_permutation':eps,'residual_signed_action_candidates':perm*eps}
def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={name:blob(path)==sha for name,(path,sha) in SOURCES.items()}
 if not all(bindings.values()) or not all(sb.values()):return {'verdict':'PROJECTED_RAW_OR_PROOF_BINDING_GUARD_FAILURE','source_guard':{'ok':False,'bindings':bindings,'source_bindings':sb}}
 frozen=frozen_rows();rows=[]
 try:
  for name,(path,_) in SOURCES.items():
   raw,_=projection_identity.normalize_projection(name,projection_identity.parse(path));sha=canonical_sha(raw);exp=frozen[name]
   if sha!=exp['raw_sha256'] or raw['variables']!=exp['variables']:return {'verdict':'PROJECTED_RAW_OR_PROOF_BINDING_GUARD_FAILURE','source':name,'observed_raw_sha256':sha}
   rows.append({'source':name,'raw_sha256':sha,**receipt(raw)})
 except ValueError:
  return {'verdict':'NON_SINGLE_FORBIDDEN_TUPLE_RELATION_FOUND'}
 verdict='PASS_PROJECTED_SIGNED_RESIDUAL_BOUND_COMPUTED' if all(r['all_same_unsigned_pairs_equal_or_reversed'] for r in rows) else 'EPSILON_COUNTING_COMPATIBILITY_FAILURE'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PROJECTED-CORE-SIGNED-RESIDUAL-BOUND-2026-09-16-v1.0','authority':'DIAGNOSTIC_REPLAY_OF_ALREADY_PROVED_SIGNED_EPSILON_COUNTING_RULE_ONLY__NO_EXACT_ACTION_TEST_GROUP_SEARCH_QUOTIENT_SOLVER_OR_CARRIER','verdict':verdict,'source_guard':{'ok':True,'bindings':bindings,'source_bindings':sb},'rows':rows,'total_residual_signed_action_candidates_across_five_sources':sum(r['residual_signed_action_candidates'] for r in rows),'resource_receipt':{'global_signed_actions_tested':0,'permutation_candidates_enumerated':0,'epsilon_vectors_enumerated':0,'solver_invocations':0,'new_signature_features':0,'new_invariants':0,'new_group_search_mechanisms':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_adapters':0,'new_quotients':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','GENERAL_GT2_TRACTABILITY':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','SIGNED_RESIDUAL_COUNT_IMPLIES_TRACTABILITY':False,'SIGNED_RESIDUAL_COUNT_IMPLIES_HARDNESS':False,'NEW_INVARIANT_LICENSED':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
