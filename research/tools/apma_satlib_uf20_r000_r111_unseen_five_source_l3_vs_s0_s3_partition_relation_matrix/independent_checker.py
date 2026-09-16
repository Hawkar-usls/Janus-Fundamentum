from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_UNSEEN_FIVE_SOURCE_L3_VS_S0_S3_PARTITION_RELATION_MATRIX_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_UNSEEN_FIVE_SOURCE_L3_VS_S0_S3_PARTITION_RELATION_MATRIX_PREREGISTRATION_REVIEW_2026-09-17.json'
LOCALIZATION=ROOT/'research/TRUMP_SATLIB_UF20_06_L3_COLLISION_EXISTING_S0_S3_COMPONENT_LOCALIZATION_RESULT_2026-09-17.json'
BLIND=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_PARTITION_RELATION_RESULT_2026-09-17.json'
EXPECTED={PREREG:'49183b8530f34e1eb84483f797e4760e5a9f85cd',REVIEW:'d3fe6839f430011ea5db96e3fdc9617aefd78891',LOCALIZATION:'2189b85416a1495d090e90768a55e1fcb1746a25',BLIND:'222d227e491df0a4ff03257d3f52a6e8be3cb6d9'}
ORDER=('UF20_06','UF20_07','UF20_08','UF20_09','UF20_010')
STAGES=('S0','S1','S2','S3')
REL_ORDER=('111','110','101','100','011','010','001','000')
CUBE=tuple(itertools.product((0,1),repeat=3))
SOURCES={
 'UF20_06':ROOT/'research/source_data/SATLIB_UF20_06_2026-09-17.cnf',
 'UF20_07':ROOT/'research/source_data/SATLIB_UF20_07_2026-09-17.cnf',
 'UF20_08':ROOT/'research/source_data/SATLIB_UF20_08_2026-09-17.cnf',
 'UF20_09':ROOT/'research/source_data/SATLIB_UF20_09_2026-09-17.cnf',
 'UF20_010':ROOT/'research/source_data/SATLIB_UF20_010_2026-09-17.cnf'}

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(path:Path):
 clauses=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   x=s.split();assert x[:2]==['p','cnf'] and len(x)==4;header=(int(x[2]),int(x[3]));continue
  vals=[int(x) for x in s.split()];assert len(vals)==4 and vals[-1]==0;clause=tuple(vals[:-1]);assert len({abs(x) for x in clause})==3;clauses.append(clause)
 assert header==(20,91) and len(clauses)==91;return clauses
def formula_sha(clauses):return hashlib.sha256(''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')).hexdigest()
def rid(clause):return ''.join('0' if lit>0 else '1' for lit in sorted(clause,key=lambda x:abs(x)))
def allowed_for_clause(clause):
 scope=sorted(abs(x) for x in clause);out=[]
 for bits in CUBE:
  a=dict(zip(scope,bits))
  if any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in clause):out.append(list(bits))
 return out
def projected_raw(name,clauses):
 selected=[(i,c) for i,c in enumerate(clauses,1) if rid(c) in {'000','111'}];V=sorted({abs(l) for _,c in selected for l in c});rows=[]
 for ordinal,c in selected:rows.append({'id':f'satlib_{name.lower()}_c{ordinal:03d}','scope':sorted(abs(x) for x in c),'allowed':sorted(allowed_for_clause(c))})
 rows.sort(key=lambda r:(tuple(r['scope']),tuple(''.join(map(str,t)) for t in r['allowed']),r['id']))
 return {'variables':V,'constraints':rows},selected
def existing_signatures(raw,selected):
 V=raw['variables'];adj={v:set() for v in V};pos=Counter();neg=Counter();inc={v:[0]*8 for v in V}
 for row in raw['constraints']:
  for a,b in itertools.combinations(row['scope'],2):adj[a].add(b);adj[b].add(a)
 degree={v:len(adj[v]) for v in V}
 for _,clause in selected:
  idx=REL_ORDER.index(rid(clause))
  for lit in clause:
   (pos if lit>0 else neg)[abs(lit)]+=1;inc[abs(lit)][idx]+=1
 return {v:{'S0':(degree[v],),'S1':(degree[v],pos[v],neg[v]),'S2':(degree[v],pos[v],neg[v],tuple(inc[v])),'S3':(degree[v],pos[v],neg[v],tuple(inc[v]),tuple(sorted(degree[n] for n in adj[v])))} for v in V}
def l3_signature(V,selected):
 edges=[tuple(sorted(abs(x) for x in clause)) for _,clause in selected];nodes=[('v',v) for v in V]+[('c',i) for i in range(len(edges))];nbr={n:[] for n in nodes}
 for i,e in enumerate(edges):
  c=('c',i)
  for v in e:x=('v',v);nbr[c].append(x);nbr[x].append(c)
 color={n:(('VAR',) if n[0]=='v' else ('CORE_CONSTRAINT',)) for n in nodes}
 for _ in range(3):old=color;color={n:(old[n],tuple(sorted(old[m] for m in nbr[n]))) for n in nodes}
 return {v:color[('v',v)] for v in V}
def partition(sig):
 groups=defaultdict(list)
 for v in sorted(sig):groups[json.dumps(sig[v],sort_keys=True,separators=(',',':'),ensure_ascii=False)].append(v)
 out=[sorted(x) for x in groups.values()];out.sort(key=lambda x:(x[0],len(x),x));return out
def refines(p,q):
 qsets=[set(c) for c in q];return all(any(set(c)<=d for d in qsets) for c in p)
def compare(l3,sk):
 a=refines(l3,sk);b=refines(sk,l3)
 if a and b:lab='EQUAL'
 elif a:lab='L3_STRICTLY_FINER_THAN_Sk'
 elif b:lab='Sk_STRICTLY_FINER_THAN_L3'
 else:lab='INCOMPARABLE'
 return {'L3_refines_stage':a,'stage_refines_L3':b,'relation':lab}
def recompute_rows(pre):
 rows=[]
 for name in ORDER:
  path=SOURCES[name];clauses=parse(path);bound=pre['bound_sources'][name]
  assert blob(path)==bound['git_blob'];assert formula_sha(clauses)==bound['canonical_formula_sha256']
  raw,selected=projected_raw(name,clauses);assert csha(raw)==bound['projected_raw_sha256']
  feats=existing_signatures(raw,selected);stage_parts={s:partition({v:feats[v][s] for v in raw['variables']}) for s in STAGES};l3=partition(l3_signature(raw['variables'],selected));rels={s:compare(l3,stage_parts[s]) for s in STAGES}
  rows.append({'source':name,'status':'AUDITED','projected_raw_sha256':csha(raw),'projected_variable_count':len(raw['variables']),'projected_constraint_count':len(raw['constraints']),'L3_partition':l3,'L3_partition_sha256':csha(l3),'stage_partitions':stage_parts,'stage_partition_sha256':{s:csha(stage_parts[s]) for s in STAGES},'relations':rels})
 return rows
def main(candidate_path:Path):
 assert all(blob(p)==sha for p,sha in EXPECTED.items())
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());assert pre['status']=='FROZEN_BEFORE_ANY_UNSEEN_S0_S1_S2_PARTITION_RELATION_VALUE_COMPUTATION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 candidate=json.loads(candidate_path.read_text().strip().splitlines()[-1]);rows=recompute_rows(pre);assert candidate['rows']==rows,(candidate['rows'],rows)
 additional=[r['source'] for r in rows if r['relations']['S3']['relation'] in {'L3_STRICTLY_FINER_THAN_Sk','INCOMPARABLE'}];verdict='PASS_SCOPED_UNSEEN_L3_ADDITIONAL_DISCRIMINATION_BEYOND_S3_PRESENT' if additional else 'PASS_UNSEEN_HOLDOUT_NO_L3_ADDITIONAL_DISCRIMINATION_BEYOND_S3'
 assert candidate['verdict']==verdict and candidate['s3_additional_discrimination_sources']==additional
 rr=candidate['resource_receipt'];assert rr['sources']==5 and rr['existing_stages']==4 and rr['partition_comparisons']==20;assert rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0 and rr['budget_raise'] is False
 sf=candidate['scientific_firewall'];assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO'
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'s3_additional_discrimination_sources':additional,'rows':rows,'partition_comparisons_verified':20}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);args=ap.parse_args();print(json.dumps(main(Path(args.candidate_json)),sort_keys=True,separators=(',',':')))
