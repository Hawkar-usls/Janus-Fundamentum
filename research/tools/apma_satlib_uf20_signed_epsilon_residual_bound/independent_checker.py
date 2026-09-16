from __future__ import annotations

import argparse,hashlib,itertools,json,math
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
SOURCES={
 'UF20_01':(ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf','8330041b292e0501f8d74c1b1d32ca96c4498864'),
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}

def blob(p):
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()

def parse(path):
 out=[];decl=None
 for line in path.read_text().splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):x=s.split();decl=(int(x[2]),int(x[3]));continue
  xs=[int(x) for x in s.split()];assert xs[-1]==0;out.append(tuple(xs[:-1]))
 assert decl==(20,91) and len(out)==91;return out

def receipt(path):
 adj={v:set() for v in range(1,21)};p=Counter();n=Counter()
 for cl in parse(path):
  av=[abs(x) for x in cl]
  for u,v in itertools.combinations(av,2):adj[u].add(v);adj[v].add(u)
  for lit in cl:(p if lit>0 else n)[abs(lit)]+=1
 ordered={v:(p[v],n[v]) for v in range(1,21)};u={v:(len(adj[v]),min(p[v],n[v]),max(p[v],n[v])) for v in range(1,21)};g=defaultdict(list)
 for v in range(1,21):g[u[v]].append(v)
 classes=[sorted(c) for c in g.values()];classes.sort(key=lambda c:(c[0],len(c),c));pairs=[];ok=True
 for c in classes:
  for a,b in itertools.combinations(c,2):
   x,y=ordered[a],ordered[b];q=y==x or y==(x[1],x[0]);ok&=q;pairs.append({'pair':[a,b],'ordered_u':list(x),'ordered_v':list(y),'equal_or_reversed':q})
 bal=sorted(v for v in ordered if ordered[v][0]==ordered[v][1]);pc=math.prod(math.factorial(len(c)) for c in classes);em=2**len(bal)
 return {'ordered_p_n':{str(v):list(ordered[v]) for v in ordered},'unsigned_classes':classes,'class_size_multiset':sorted((len(c) for c in classes),reverse=True),'same_unsigned_pair_compatibility':pairs,'all_same_unsigned_pairs_equal_or_reversed':ok,'balanced_variables':bal,'balanced_count':len(bal),'unsigned_respecting_permutation_candidates':pc,'epsilon_multiplicity_per_permutation':em,'residual_signed_action_candidates':pc*em}

def main(c):
 rows={r['source']:{k:v for k,v in r.items() if k!='source'} for r in c.get('rows',[])};ind={name:receipt(path) for name,(path,_) in SOURCES.items()};checks={'candidate_not_imported':True,'verdict':c.get('verdict')=='PASS_EPSILON_DETERMINATION_AND_RESIDUAL_CANDIDATE_BOUND','sources':set(rows)==set(SOURCES)}
 for name,(path,sha) in SOURCES.items():checks[f'{name}_blob']=blob(path)==sha;checks[f'{name}_receipt']=rows.get(name)==ind[name]
 checks['total']=c.get('total_residual_signed_action_candidates_across_five_sources')==sum(r['residual_signed_action_candidates'] for r in ind.values())
 rr=c.get('resource_receipt',{});checks['resources']=rr.get('global_signed_actions_tested')==0 and rr.get('exact_signed_formula_transport_tests')==0 and rr.get('solver_invocations')==0 and rr.get('new_solver_mechanisms')==0 and rr.get('new_carrier_mechanisms')==0 and rr.get('new_group_search_mechanisms')==0 and rr.get('budget_raise') is False
 sf=c.get('scientific_firewall',{});checks['firewall']=sf.get('P_VS_NP')=='OPEN' and sf.get('GENERAL_SAT_IN_P')=='NOT_PROVED'
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-SIGNED-EPSILON-RESIDUAL-BOUND-INDEPENDENT-CHECK-2026-09-16-v1.0','verified':all(checks.values()),'certificate_imported':False,'checks':checks,'independent_rows':ind}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();c=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);print(json.dumps(main(c),sort_keys=True,separators=(',',':')))
