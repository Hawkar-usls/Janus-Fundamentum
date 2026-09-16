from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_PREREGISTRATION_2026-09-16.json'
PROOF=ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_AUTOMORPHISM_ADMISSIBILITY_DIRECT_PROOF_2026-09-16.md'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_S1_FULL_PERMUTATION_AUTOMORPHISM_CERTIFICATE_RESULT_2026-09-16.json'
EXPECTED={PREREG:'90ac18670617bfb29e4a52f63b4c226ed498e5b6',PROOF:'e1515e047e53535882913d3764425814290f3334',PARENT:'d804f61fde8a25bea0ad790c79cd40c9e110f646'}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}

def blob(p:Path)->str:
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def parse(path:Path):
 clauses=[];decl=None
 for line in path.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   x=s.split();decl=(int(x[2]),int(x[3]));continue
  xs=[int(x) for x in s.split()];assert xs[-1]==0
  cl=tuple(xs[:-1]);assert len(cl)==3 and len({abs(x) for x in cl})==3;clauses.append(cl)
 assert decl==(20,91) and len(clauses)==91
 return clauses

def local_signed_sanity()->dict[str,Any]:
 tests=0;sat_checks=0;forbidden_checks=0;inverse_checks=0
 cube=list(itertools.product((0,1),repeat=3))
 for forbidden in cube:
  allowed=set(cube)-{forbidden}
  for perm in itertools.permutations(range(3)):
   inv=[0]*3
   for old,new in enumerate(perm):inv[new]=old
   for eps in cube:
    transformed=set()
    for row in allowed:
     out=[0]*3
     for old,new in enumerate(perm):out[new]=row[old]^eps[old]
     transformed.add(tuple(out))
    missing=[row for row in cube if row not in transformed]
    expected=[0]*3
    for old,new in enumerate(perm):expected[new]=forbidden[old]^eps[old]
    forbidden_checks+=1
    if missing!=[tuple(expected)]:return {'ok':False,'class':'FORBIDDEN_TUPLE_RULE','witness':{'f':forbidden,'perm':perm,'eps':eps,'missing':missing,'expected':expected}}
    for a in cube:
     b=[0]*3
     for old,new in enumerate(perm):b[new]=a[old]^eps[old]
     sat_checks+=1
     if (a in allowed)!=(tuple(b) in transformed):return {'ok':False,'class':'SAT_EQUIVARIANCE','witness':{'f':forbidden,'perm':perm,'eps':eps,'a':a,'b':b}}
     recovered=[0]*3
     for new,old in enumerate(inv):recovered[old]=b[new]^eps[old]
     inverse_checks+=1
     if tuple(recovered)!=a:return {'ok':False,'class':'ASSIGNMENT_INVERSE','witness':{'perm':perm,'eps':eps,'a':a,'recovered':recovered}}
    tests+=1
 return {'ok':True,'local_action_cases':tests,'satisfaction_membership_checks':sat_checks,'forbidden_tuple_checks':forbidden_checks,'assignment_inverse_checks':inverse_checks}

def unsigned_partition(path:Path):
 clauses=parse(path);adj={v:set() for v in range(1,21)};pos=Counter();neg=Counter()
 for cl in clauses:
  av=[abs(x) for x in cl]
  for u,v in itertools.combinations(av,2):adj[u].add(v);adj[v].add(u)
  for lit in cl:(pos if lit>0 else neg)[abs(lit)]+=1
 sig={v:(len(adj[v]),min(pos[v],neg[v]),max(pos[v],neg[v])) for v in range(1,21)}
 g=defaultdict(list)
 for v in sorted(sig):g[sig[v]].append(v)
 classes=[sorted(c) for c in g.values()];classes.sort(key=lambda c:(c[0],len(c),c))
 return {'class_count':len(classes),'class_size_multiset':sorted((len(c) for c in classes),reverse=True),'non_singleton_classes':[c for c in classes if len(c)>1],'classes':classes,'signatures':{str(v):list(sig[v]) for v in sorted(sig)}}

def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};source_bindings={name:blob(path)==sha for name,(path,sha) in SOURCES.items()}
 if not all(bindings.values()) or not all(source_bindings.values()):return {'verdict':'PROOF_OR_CHECKER_FAILURE','source_guard':{'ok':False,'bindings':bindings,'source_bindings':source_bindings}}
 sanity=local_signed_sanity()
 if not sanity['ok']:
  verdict={'SAT_EQUIVARIANCE':'SIGNED_ACTION_SEMANTICS_FALSIFIED','ASSIGNMENT_INVERSE':'SIGNED_ACTION_SEMANTICS_FALSIFIED','FORBIDDEN_TUPLE_RULE':'FORBIDDEN_BIT_TRANSFORM_RULE_FALSIFIED'}.get(sanity['class'],'PROOF_OR_CHECKER_FAILURE')
 else:verdict='PASS_SIGNED_ACTION_SEMANTICS_AND_UNSIGNED_S1_NECESSARY_INVARIANT'
 rows=[{'source':name,'unsigned_S1':unsigned_partition(path)} for name,(path,_) in SOURCES.items()]
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-SIGNED-AUTOMORPHISM-ADMISSIBILITY-2026-09-16-v1.0','authority':'DIAGNOSTIC_DEFINITION_AND_PROOF_SCOPE_ONLY__NO_GROUP_SEARCH_SOLVER_OR_CARRIER','verdict':verdict,'source_guard':{'ok':all(bindings.values()) and all(source_bindings.values()),'bindings':bindings,'source_bindings':source_bindings},'direct_proof':{'blob':EXPECTED[PROOF],'signed_action_semantics_proved':True,'unsigned_S1_rule':'(degree,min(p,n),max(p,n))'},'finite_proof_sanity':sanity,'five_source_unsigned_partition_receipt':rows,'resource_receipt':{'signed_group_elements_enumerated':0,'global_signed_actions_tested':0,'solver_invocations':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_group_search_mechanisms':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','ARBITRARY_UNSEEN_INVARIANT_DISCOVERY':'NOT_PROVED'}}

if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
