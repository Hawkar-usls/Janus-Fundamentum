from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter,defaultdict
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_RESIDUAL_EXACT_CERTIFICATE_PREREGISTRATION_2026-09-16.json'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_SIGNED_EPSILON_DETERMINATION_RESIDUAL_BOUND_RESULT_2026-09-16.json'
EXPECTED={PREREG:'d5e29fc5bdc98f83a8d41ed42146c182cddc8e8c',PARENT:'022463d966fa6f200a258d10e174218bf6aa4dab'}
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864',8),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865',2),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f',8),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1',8),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b',8)}

def blob(p):
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def parse(path):
 clauses=[];decl=None
 for line in path.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):x=s.split();decl=(int(x[2]),int(x[3]));continue
  xs=[int(x) for x in s.split()];assert xs[-1]==0;cl=tuple(xs[:-1]);assert len(cl)==3 and len({abs(x) for x in cl})==3;clauses.append(cl)
 assert decl==(20,91) and len(clauses)==91;return clauses

def make_raw(name,clauses):
 cons=[]
 for i,cl in enumerate(clauses,1):
  scope=sorted(abs(x) for x in cl);rows=[]
  for bits in itertools.product((0,1),repeat=3):
   a=dict(zip(scope,bits))
   if any(bool(a[abs(l)]) if l>0 else not bool(a[abs(l)]) for l in cl):rows.append(list(bits))
  cons.append({'id':f'satlib_{name.lower()}_c{i:03d}','scope':scope,'allowed':rows})
 return canonicalize_raw({'variables':list(range(1,21)),'constraints':cons})

def counts_and_classes(clauses):
 adj={v:set() for v in range(1,21)};p=Counter();n=Counter()
 for cl in clauses:
  av=[abs(x) for x in cl]
  for u,v in itertools.combinations(av,2):adj[u].add(v);adj[v].add(u)
  for lit in cl:(p if lit>0 else n)[abs(lit)]+=1
 ordered={v:(p[v],n[v]) for v in range(1,21)};unsigned={v:(len(adj[v]),min(p[v],n[v]),max(p[v],n[v])) for v in range(1,21)};g=defaultdict(list)
 for v in range(1,21):g[unsigned[v]].append(v)
 classes=[sorted(c) for c in g.values()];classes.sort(key=lambda c:(c[0],len(c),c));balanced=sorted(v for v in ordered if ordered[v][0]==ordered[v][1])
 return ordered,classes,balanced

def actions(ordered,classes,balanced):
 class_perms=[list(itertools.permutations(c)) for c in classes]
 idx=0
 for choices in itertools.product(*class_perms):
  sigma={}
  for cls,target_perm in zip(classes,choices):
   sigma.update(dict(zip(cls,target_perm)))
  fixed_eps={}
  for v in range(1,21):
   if v in balanced:continue
   w=sigma[v];a=ordered[v];b=ordered[w]
   if b==a:fixed_eps[v]=0
   elif b==(a[1],a[0]):fixed_eps[v]=1
   else:raise AssertionError(('EPSILON_GUARD',v,w,a,b))
  for bits in itertools.product((0,1),repeat=len(balanced)):
   eps=dict(fixed_eps);eps.update(dict(zip(balanced,bits)));idx+=1;yield idx,sigma,eps

def semantic_multiset(raw):
 out=Counter()
 for c in raw['constraints']:
  scope=tuple(sorted(c['scope']));pos={v:i for i,v in enumerate(c['scope'])};rows=tuple(sorted({tuple(int(r[pos[v]]) for v in scope) for r in c['allowed']}));out[(scope,rows)]+=1
 return out

def transported_multiset(raw,sigma,eps):
 out=Counter()
 for c in raw['constraints']:
  old_scope=list(c['scope']);new_scope=tuple(sorted(sigma[v] for v in old_scope));old_pos={v:i for i,v in enumerate(old_scope)};rows=set()
  for row in c['allowed']:
   moved={sigma[v]:int(row[old_pos[v]])^int(eps[v]) for v in old_scope};rows.add(tuple(moved[w] for w in new_scope))
  out[(new_scope,tuple(sorted(rows)))]+=1
 return out

def audit_source(name,path,expected_count):
 clauses=parse(path);raw=make_raw(name,clauses);original=semantic_multiset(raw);ordered,classes,balanced=counts_and_classes(clauses);rows=[];identity_passes=0;nonidentity=[]
 for ordinal,sigma,eps in actions(ordered,classes,balanced):
  is_identity=all(sigma[v]==v for v in sigma) and all(eps[v]==0 for v in eps);exact=transported_multiset(raw,sigma,eps)==original
  if is_identity and exact:identity_passes+=1
  moved=[[v,sigma[v]] for v in sorted(sigma) if sigma[v]!=v];flips=[v for v in sorted(eps) if eps[v]]
  rec={'ordinal':ordinal,'is_identity':is_identity,'sigma_moves':moved,'flip_variables':flips,'exact_signed_automorphism':exact};rows.append(rec)
  if exact and not is_identity:nonidentity.append(rec)
 if len(rows)!=expected_count:return {'source':name,'status':'COUNT_MISMATCH','expected':expected_count,'observed':len(rows),'actions':rows}
 return {'source':name,'status':'COMPLETE','candidate_count':len(rows),'identity_positive_control_pass_count':identity_passes,'nonidentity_automorphism_count':len(nonidentity),'first_nonidentity_witness':nonidentity[0] if nonidentity else None,'actions':rows}

def main():
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sb={name:blob(path)==sha for name,(path,sha,_) in SOURCES.items()}
 if not all(bindings.values()) or not all(sb.values()):return {'verdict':'SOURCE_OR_PARENT_GUARD_FAILURE','source_guard':{'ok':False,'bindings':bindings,'source_bindings':sb}}
 rows=[audit_source(name,path,n) for name,(path,_,n) in SOURCES.items()]
 if any(r['status']!='COMPLETE' for r in rows):verdict='RESIDUAL_CANDIDATE_GENERATION_COUNT_MISMATCH'
 elif any(r['identity_positive_control_pass_count']!=1 for r in rows):verdict='IDENTITY_POSITIVE_CONTROL_FAILURE'
 elif any(r['nonidentity_automorphism_count']>0 for r in rows):verdict='NONIDENTITY_SIGNED_AUTOMORPHISM_WITNESS_FOUND'
 else:verdict='PASS_SCOPED_SIGNED_GROUP_TRIVIAL_ON_ALL_FIVE'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-SIGNED-RESIDUAL-EXACT-CERTIFICATE-2026-09-16-v1.0','authority':'DIAGNOSTIC_FINITE_SOURCE_SCOPED_EXACT_ACTION_CERTIFICATE__NO_GENERAL_GROUP_SEARCH_OR_QUOTIENT','verdict':verdict,'source_guard':{'ok':True,'bindings':bindings,'source_bindings':sb},'rows':rows,'total_actions_tested':sum(r.get('candidate_count',len(r.get('actions',[]))) for r in rows),'total_nonidentity_automorphisms':sum(r.get('nonidentity_automorphism_count',0) for r in rows),'resource_receipt':{'actions_outside_frozen_residual_set_tested':0,'group_closure_computation':0,'quotient_states_enumerated':0,'solver_invocations':0,'new_solver_mechanisms':0,'new_carrier_mechanisms':0,'new_general_group_search_mechanisms':0,'budget_raise':False},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','ARBITRARY_UNSEEN_INVARIANT_DISCOVERY':'NOT_PROVED'}}

if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
