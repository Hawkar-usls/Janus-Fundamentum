from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_PARTITION_RELATION_EXECUTION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_PARTITION_RELATION_EXECUTION_PREREGISTRATION_REVIEW_2026-09-17.json'
SOURCE_FREEZE=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_UNSEEN_SOURCE_ACQUISITION_FREEZE_RESULT_2026-09-17.json'
EXPECTED={PREREG:'3a7078d1787126df42faa183784e751cf00d2aa5',REVIEW:'c63ea31d65b4d26449fb6591077df620eef0151b',SOURCE_FREEZE:'ae26cc59e754f73476bfb903331f1c4c1d946bdc'}
ORDER=('UF20_06','UF20_07','UF20_08','UF20_09','UF20_010')
SOURCES={
 'UF20_06':ROOT/'research/source_data/SATLIB_UF20_06_2026-09-17.cnf','UF20_07':ROOT/'research/source_data/SATLIB_UF20_07_2026-09-17.cnf','UF20_08':ROOT/'research/source_data/SATLIB_UF20_08_2026-09-17.cnf','UF20_09':ROOT/'research/source_data/SATLIB_UF20_09_2026-09-17.cnf','UF20_010':ROOT/'research/source_data/SATLIB_UF20_010_2026-09-17.cnf'}
REL_ORDER=('111','110','101','100','011','010','001','000')
CUBE=tuple(itertools.product((0,1),repeat=3))

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def formula_sha(clauses):return hashlib.sha256(''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')).hexdigest()
def parse(path:Path):
 clauses=[];header=None
 for raw in path.read_text().splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in ('%','0'):continue
  if s.startswith('p '):
   x=s.split();assert x[:2]==['p','cnf'] and len(x)==4;header=(int(x[2]),int(x[3]));continue
  vals=[int(x) for x in s.split()];assert vals[-1]==0 and len(vals)==4;clause=tuple(vals[:-1]);assert len({abs(x) for x in clause})==3;clauses.append(clause)
 assert header==(20,91) and len(clauses)==91;return clauses
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
def partition(sig):
 g=defaultdict(list);canonical_map=[]
 for v in sorted(sig):
  key=json.dumps(sig[v],sort_keys=True,separators=(',',':'),ensure_ascii=False);g[key].append(v);canonical_map.append([v,sig[v]])
 classes=[sorted(x) for x in g.values()];classes.sort(key=lambda x:(x[0],len(x),x));return classes,csha(canonical_map)
def s3_signature(raw,selected):
 V=raw['variables'];adj={v:set() for v in V};pos=Counter();neg=Counter();inc={v:[0]*8 for v in V}
 for row in raw['constraints']:
  for a,b in itertools.combinations(row['scope'],2):adj[a].add(b);adj[b].add(a)
 degree={v:len(adj[v]) for v in V}
 for _,c in selected:
  r=rid(c);idx=REL_ORDER.index(r)
  for lit in c:
   (pos if lit>0 else neg)[abs(lit)]+=1;inc[abs(lit)][idx]+=1
 return {v:(degree[v],pos[v],neg[v],tuple(inc[v]),tuple(sorted(degree[u] for u in adj[v]))) for v in V}
def l3_signature(V,edges):
 nodes=[('v',v) for v in V]+[('c',i) for i in range(len(edges))];nbr={n:[] for n in nodes}
 for i,e in enumerate(edges):
  c=('c',i)
  for v in e:x=('v',v);nbr[c].append(x);nbr[x].append(c)
 color={n:(('VAR',) if n[0]=='v' else ('CORE_CONSTRAINT',)) for n in nodes}
 for _ in range(3):old=color;color={n:(old[n],tuple(sorted(old[m] for m in nbr[n]))) for n in nodes}
 return {v:color[('v',v)] for v in V}
def refines(p,q):
 qsets=[set(c) for c in q];return all(any(set(c)<=d for d in qsets) for c in p)
def compare(l3,s3):
 a=refines(l3,s3);b=refines(s3,l3)
 if a and b:lab='EQUAL'
 elif a:lab='L3_STRICTLY_FINER_THAN_S3'
 elif b:lab='S3_STRICTLY_FINER_THAN_L3'
 else:lab='INCOMPARABLE'
 return {'L3_refines_S3':a,'S3_refines_L3':b,'relation':lab}
def recompute_rows(pre):
 rows=[]
 for name in ORDER:
  path=SOURCES[name];clauses=parse(path);bound=pre['bound_sources'][name]
  assert blob(path)==bound['git_blob'] and formula_sha(clauses)==bound['canonical_formula_sha256']
  raw,selected=projected_raw(name,clauses);raw_sha=csha(raw);edges=[tuple(sorted(abs(x) for x in c)) for _,c in selected];V=raw['variables']
  s3,_=partition(s3_signature(raw,selected));l3,l3map=partition(l3_signature(V,edges));cmp=compare(l3,s3);ords=[i for i,_ in selected]
  rows.append({'source':name,'status':'AUDITED','projected_raw_sha256':raw_sha,'projected_variables':V,'projected_variable_count':len(V),'projected_constraint_count':len(selected),'selected_clause_ordinals':ords,'R000_count':sum(rid(c)=='000' for _,c in selected),'R111_count':sum(rid(c)=='111' for _,c in selected),'L3_partition':l3,'L3_partition_sha256':csha(l3),'L3_signature_map_sha256':l3map,'S3_partition':s3,'S3_partition_sha256':csha(s3),**cmp})
 return rows
def main(candidate_path:Path):
 assert all(blob(p)==s for p,s in EXPECTED.items())
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());freeze=json.loads(SOURCE_FREEZE.read_text())
 assert pre['status']=='FROZEN_BEFORE_ANY_UNSEEN_PROJECTED_L3_OR_S3_VALUE_COMPUTATION' and review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE' and freeze['verdict']=='PASS_UNSEEN_SOURCE_ACQUISITION_AND_DUAL_MIRROR_FORMULA_FREEZE'
 candidate=json.loads(candidate_path.read_text().strip().splitlines()[-1]);rows=recompute_rows(pre);assert candidate['rows']==rows,(candidate['rows'],rows)
 non_equal=[r['source'] for r in rows if r['relation']!='EQUAL'];repeat=bool(non_equal);verdict='PASS_SCOPED_UNSEEN_REPEAT_EVIDENCE_L3_VS_S3_PARTITION_DIFFERENCE' if repeat else 'PASS_UNSEEN_HOLDOUT_ALL_L3_S3_PARTITIONS_EQUAL__NO_REPEAT_EVIDENCE_ON_THIS_HOLDOUT'
 assert candidate['verdict']==verdict and candidate['non_equal_sources']==non_equal and candidate['scoped_repeat_evidence']==repeat
 rr=candidate['resource_receipt'];assert rr['sources']==5 and rr['partition_comparisons']==5 and rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['action_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0 and rr['budget_raise'] is False
 sf=candidate['scientific_firewall'];assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO'
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'non_equal_sources':non_equal,'scoped_repeat_evidence':repeat,'sources_verified':5,'rows':rows}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);args=ap.parse_args();print(json.dumps(main(Path(args.candidate_json)),sort_keys=True,separators=(',',':')))
