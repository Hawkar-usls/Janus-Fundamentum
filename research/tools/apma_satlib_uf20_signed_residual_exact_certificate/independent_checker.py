from __future__ import annotations

import argparse,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864',8),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865',2),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f',8),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1',8),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b',8)}

def blob(p):
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def parse(path):
 out=[];decl=None
 for line in path.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):x=s.split();decl=(int(x[2]),int(x[3]));continue
  xs=[int(x) for x in s.split()];assert xs[-1]==0;cl=tuple(xs[:-1]);assert len(cl)==3 and len({abs(x) for x in cl})==3;out.append(cl)
 assert decl==(20,91) and len(out)==91;return out

def counts_classes(clauses):
 adj={v:set() for v in range(1,21)};p=Counter();n=Counter()
 for cl in clauses:
  av=[abs(x) for x in cl]
  for u,v in itertools.combinations(av,2):adj[u].add(v);adj[v].add(u)
  for lit in cl:(p if lit>0 else n)[abs(lit)]+=1
 ordered={v:(p[v],n[v]) for v in range(1,21)};u={v:(len(adj[v]),min(p[v],n[v]),max(p[v],n[v])) for v in range(1,21)};g=defaultdict(list)
 for v in range(1,21):g[u[v]].append(v)
 classes=[sorted(c) for c in g.values()];classes.sort(key=lambda c:(c[0],len(c),c));balanced=sorted(v for v in ordered if ordered[v][0]==ordered[v][1]);return ordered,classes,balanced

def generated_actions(ordered,classes,balanced):
 cps=[list(itertools.permutations(c)) for c in classes];idx=0
 for choices in itertools.product(*cps):
  sigma={}
  for cls,t in zip(classes,choices):sigma.update(dict(zip(cls,t)))
  fixed={}
  for v in range(1,21):
   if v in balanced:continue
   a=ordered[v];b=ordered[sigma[v]]
   if b==a:fixed[v]=0
   elif b==(a[1],a[0]):fixed[v]=1
   else:raise AssertionError('EPSILON_COMPAT')
  for bits in itertools.product((0,1),repeat=len(balanced)):
   eps=dict(fixed);eps.update(dict(zip(balanced,bits)));idx+=1;yield idx,sigma,eps

def forbidden_multiset(clauses):
 out=Counter()
 for cl in clauses:
  scope=tuple(sorted(abs(x) for x in cl));lit={abs(x):x for x in cl};forbidden=tuple(0 if lit[v]>0 else 1 for v in scope);out[(scope,forbidden)]+=1
 return out

def transported_forbidden_multiset(clauses,sigma,eps):
 out=Counter()
 for cl in clauses:
  old_scope=tuple(sorted(abs(x) for x in cl));lit={abs(x):x for x in cl};old_forbidden={v:(0 if lit[v]>0 else 1) for v in old_scope};new_scope=tuple(sorted(sigma[v] for v in old_scope));moved={sigma[v]:old_forbidden[v]^eps[v] for v in old_scope};new_forbidden=tuple(moved[w] for w in new_scope);out[(new_scope,new_forbidden)]+=1
 return out

def row(name,path,expected_count):
 clauses=parse(path);original=forbidden_multiset(clauses);ordered,classes,balanced=counts_classes(clauses);actions=[]
 for ordinal,sigma,eps in generated_actions(ordered,classes,balanced):
  ident=all(sigma[v]==v for v in sigma) and all(eps[v]==0 for v in eps);exact=transported_forbidden_multiset(clauses,sigma,eps)==original
  actions.append({'ordinal':ordinal,'is_identity':ident,'sigma_moves':[[v,sigma[v]] for v in sorted(sigma) if sigma[v]!=v],'flip_variables':[v for v in sorted(eps) if eps[v]],'exact_signed_automorphism':exact})
 return {'source':name,'candidate_count':len(actions),'expected_count':expected_count,'identity_passes':sum(a['is_identity'] and a['exact_signed_automorphism'] for a in actions),'nonidentity_count':sum((not a['is_identity']) and a['exact_signed_automorphism'] for a in actions),'actions':actions}

def main(candidate):
 cand={r['source']:r for r in candidate.get('rows',[])};ind={name:row(name,path,n) for name,(path,_,n) in SOURCES.items()};checks={'candidate_not_imported':True,'source_set':set(cand)==set(SOURCES)}
 for name,(path,sha,n) in SOURCES.items():
  checks[f'{name}_blob']=blob(path)==sha
  c=cand.get(name,{});r=ind[name]
  checks[f'{name}_count']=c.get('candidate_count')==r['candidate_count']==n
  checks[f'{name}_identity']=c.get('identity_positive_control_pass_count')==r['identity_passes']==1
  checks[f'{name}_nonidentity']=c.get('nonidentity_automorphism_count')==r['nonidentity_count']
  checks[f'{name}_actions']=c.get('actions')==r['actions']
 total=sum(r['candidate_count'] for r in ind.values());non=sum(r['nonidentity_count'] for r in ind.values());checks['totals']=candidate.get('total_actions_tested')==total==34 and candidate.get('total_nonidentity_automorphisms')==non
 expected_verdict='NONIDENTITY_SIGNED_AUTOMORPHISM_WITNESS_FOUND' if non else 'PASS_SCOPED_SIGNED_GROUP_TRIVIAL_ON_ALL_FIVE';checks['verdict']=candidate.get('verdict')==expected_verdict
 rr=candidate.get('resource_receipt',{});checks['resources']=rr.get('actions_outside_frozen_residual_set_tested')==0 and rr.get('group_closure_computation')==0 and rr.get('quotient_states_enumerated')==0 and rr.get('solver_invocations')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_general_group_search_mechanisms')==0 and rr.get('budget_raise') is False
 sf=candidate.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-SIGNED-RESIDUAL-EXACT-CERTIFICATE-INDEPENDENT-CHECK-2026-09-16-v1.0','verified':all(checks.values()),'candidate_imported':False,'comparison_model':'UNIQUE_FORBIDDEN_TUPLE_MULTISET_EQUIVALENT_TO_EXPLICIT_SEVEN_ROW_RELATION_IN_FROZEN_3CNF_DOMAIN','checks':checks,'independent_rows':ind}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);print(json.dumps(main(c),sort_keys=True,separators=(',',':')))
