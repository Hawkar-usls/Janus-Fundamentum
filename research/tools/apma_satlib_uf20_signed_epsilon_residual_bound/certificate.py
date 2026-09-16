from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_EPSILON_DETERMINATION_RESIDUAL_BOUND_PREREGISTRATION_2026-09-16.json'
PROOF=ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_EPSILON_DETERMINATION_DIRECT_PROOF_2026-09-16.md'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_RESULT_2026-09-16.json'
EXPECTED={PREREG:'c03520ad0e80341ca518348cafc99d7cbbc2b7c7',PROOF:'adfa4b1dd935109e5593fba7509d37ba5fe0400b',PARENT:'6fd65d76651492009af19db0fe4a8d97e15794d1'}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}

def blob(p:Path)->str:
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def parse(path:Path):
 out=[];decl=None
 for line in path.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   x=s.split();decl=(int(x[2]),int(x[3]));continue
  xs=[int(x) for x in s.split()];assert xs[-1]==0;cl=tuple(xs[:-1]);assert len(cl)==3 and len({abs(x) for x in cl})==3;out.append(cl)
 assert decl==(20,91) and len(out)==91
 return out

def source_receipt(path:Path):
 clauses=parse(path);adj={v:set() for v in range(1,21)};p=Counter();n=Counter()
 for cl in clauses:
  av=[abs(x) for x in cl]
  for u,v in itertools.combinations(av,2):adj[u].add(v);adj[v].add(u)
  for lit in cl:(p if lit>0 else n)[abs(lit)]+=1
 ordered={v:(p[v],n[v]) for v in range(1,21)}
 unsigned={v:(len(adj[v]),min(p[v],n[v]),max(p[v],n[v])) for v in range(1,21)}
 groups=defaultdict(list)
 for v in range(1,21):groups[unsigned[v]].append(v)
 classes=[sorted(c) for c in groups.values()];classes.sort(key=lambda c:(c[0],len(c),c))
 compatibility=True;details=[]
 for cls in classes:
  for u,v in itertools.combinations(cls,2):
   a=ordered[u];b=ordered[v];ok=b==a or b==(a[1],a[0]);compatibility &= ok;details.append({'pair':[u,v],'ordered_u':list(a),'ordered_v':list(b),'equal_or_reversed':ok})
 balanced=sorted(v for v in ordered if ordered[v][0]==ordered[v][1])
 perm_count=math.prod(math.factorial(len(c)) for c in classes)
 eps_mult=1<<len(balanced)
 return {'ordered_p_n':{str(v):list(ordered[v]) for v in sorted(ordered)},'unsigned_classes':classes,'class_size_multiset':sorted((len(c) for c in classes),reverse=True),'same_unsigned_pair_compatibility':details,'all_same_unsigned_pairs_equal_or_reversed':compatibility,'balanced_variables':balanced,'balanced_count':len(balanced),'unsigned_respecting_permutation_candidates':perm_count,'epsilon_multiplicity_per_permutation':eps_mult,'residual_signed_action_candidates':perm_count*eps_mult}

def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={name:blob(path)==sha for name,(path,sha) in SOURCES.items()}
 if not all(bindings.values()) or not all(sb.values()):return {'verdict':'SOURCE_OR_PARENT_GUARD_FAILURE','source_guard':{'ok':False,'bindings':bindings,'source_bindings':sb}}
 rows=[{'source':name,**source_receipt(path)} for name,(path,_) in SOURCES.items()]
 if not all(r['all_same_unsigned_pairs_equal_or_reversed'] for r in rows):verdict='UNSIGNED_CLASS_ORDERED_COUNT_COMPATIBILITY_FAILURE'
 else:verdict='PASS_EPSILON_DETERMINATION_AND_RESIDUAL_CANDIDATE_BOUND'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-SIGNED-EPSILON-DETERMINATION-RESIDUAL-BOUND-2026-09-16-v1.0','authority':'DIAGNOSTIC_PROOF_AND_COUNTING_CERTIFICATE_ONLY__NO_SIGNED_GROUP_SEARCH','verdict':verdict,'source_guard':{'ok':True,'bindings':bindings,'source_bindings':sb},'direct_proof':{'blob':EXPECTED[PROOF],'lemma':'SIGNED_EPSILON_DETERMINATION_FROM_ORDERED_FORBIDDEN_BIT_COUNTS'},'rows':rows,'total_residual_signed_action_candidates_across_five_sources':sum(r['residual_signed_action_candidates'] for r in rows),'resource_receipt':{'global_signed_actions_tested':0,'exact_signed_formula_transport_tests':0,'solver_invocations':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_group_search_mechanisms':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','ARBITRARY_UNSEEN_INVARIANT_DISCOVERY':'NOT_PROVED'}}

if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
