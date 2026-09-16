from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
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

def sanity():
 cube=list(itertools.product((0,1),repeat=3));cases=sat=forb=invchecks=0
 for f in cube:
  R=set(cube)-{f}
  for perm in itertools.permutations(range(3)):
   inv=[0]*3
   for old,new in enumerate(perm):inv[new]=old
   for eps in cube:
    Rp=set()
    for r in R:
     y=[0]*3
     for old,new in enumerate(perm):y[new]=r[old]^eps[old]
     Rp.add(tuple(y))
    expected=[0]*3
    for old,new in enumerate(perm):expected[new]=f[old]^eps[old]
    missing=[x for x in cube if x not in Rp];forb+=1
    if missing!=[tuple(expected)]:return {'ok':False,'class':'FORBIDDEN'}
    for a in cube:
     y=[0]*3
     for old,new in enumerate(perm):y[new]=a[old]^eps[old]
     sat+=1
     if (a in R)!=(tuple(y) in Rp):return {'ok':False,'class':'SAT'}
     back=[0]*3
     for new,old in enumerate(inv):back[old]=y[new]^eps[old]
     invchecks+=1
     if tuple(back)!=a:return {'ok':False,'class':'INVERSE'}
    cases+=1
 return {'ok':True,'local_action_cases':cases,'satisfaction_membership_checks':sat,'forbidden_tuple_checks':forb,'assignment_inverse_checks':invchecks}

def unsigned(path:Path):
 clauses=parse(path);adj={v:set() for v in range(1,21)};p=Counter();n=Counter()
 for cl in clauses:
  av=[abs(x) for x in cl]
  for u,v in itertools.combinations(av,2):adj[u].add(v);adj[v].add(u)
  for lit in cl:(p if lit>0 else n)[abs(lit)]+=1
 sig={v:(len(adj[v]),min(p[v],n[v]),max(p[v],n[v])) for v in range(1,21)};g=defaultdict(list)
 for v in sorted(sig):g[sig[v]].append(v)
 classes=[sorted(c) for c in g.values()];classes.sort(key=lambda c:(c[0],len(c),c))
 return {'class_count':len(classes),'class_size_multiset':sorted((len(c) for c in classes),reverse=True),'non_singleton_classes':[c for c in classes if len(c)>1],'classes':classes,'signatures':{str(v):list(sig[v]) for v in sorted(sig)}}

def main(candidate):
 s=sanity();rows={r['source']:r['unsigned_S1'] for r in candidate.get('five_source_unsigned_partition_receipt',[])};ind={name:unsigned(path) for name,(path,_) in SOURCES.items()}
 checks={'implementation_not_imported':True,'expected_verdict':candidate.get('verdict')=='PASS_SIGNED_ACTION_SEMANTICS_AND_UNSIGNED_S1_NECESSARY_INVARIANT','sanity_match':candidate.get('finite_proof_sanity')==s,'source_set':set(rows)==set(SOURCES)}
 for name,(path,sha) in SOURCES.items():
  checks[f'{name}_source_blob']=blob(path)==sha
  checks[f'{name}_unsigned_partition']=rows.get(name)==ind[name]
 rr=candidate.get('resource_receipt',{});checks['resources']=rr.get('signed_group_elements_enumerated')==0 and rr.get('global_signed_actions_tested')==0 and rr.get('solver_invocations')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_group_search_mechanisms')==0 and rr.get('budget_raise') is False
 sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED' and sf.get('CONNECTED_MIXED_CORE_SOLVED')=='NO'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-SIGNED-AUTOMORPHISM-ADMISSIBILITY-INDEPENDENT-CHECK-2026-09-16-v1.0','authority':'INDEPENDENT_DIAGNOSTIC_CHECK_ONLY','verified':all(checks.values()),'implementation_imported':False,'checks':checks,'independent_sanity':s,'independent_unsigned_partitions':ind}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);print(json.dumps(main(c),sort_keys=True,separators=(',',':')))
