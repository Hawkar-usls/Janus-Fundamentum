from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RESIDUAL_LOCAL_INVARIANT_FALSIFIER_PREREGISTRATION_2026-09-16.json'
SOURCES={
 'UF20_01':ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf',
 'UF20_02':ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf',
 'UF20_03':ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf',
 'UF20_04':ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf',
 'UF20_05':ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf',
}
CIDS=(
 'L1_ROOT_PAIR_MULTIPLICITY_MULTISET',
 'L2_ROOT_INCIDENT_HYPEREDGE_NEIGHBOR_PROFILE',
 'L3_THREE_ROUND_INCIDENCE_WL_ROOT_COLOR',
 'L4_ROOT_SIMPLE_INCIDENCE_6CYCLE_PROFILE',
)


def parse_dimacs(path:Path)->list[tuple[int,int,int]]:
 cs=[];buf=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   x=s.split();header=(int(x[2]),int(x[3]));continue
  for z in map(int,s.split()):
   if z==0:
    if len(buf)!=3 or len({abs(x) for x in buf})!=3:raise ValueError('BAD_3CNF')
    cs.append(tuple(buf));buf=[]
   else:buf.append(z)
 if header!=(20,91) or len(cs)!=91 or buf:raise ValueError('BAD_DIMACS_COUNTS')
 return cs


def relation_id(c:tuple[int,int,int])->str:
 return ''.join('0' if x>0 else '1' for x in sorted(c,key=lambda z:abs(z)))


def canonical_projected_raw(name:str,clauses:list[tuple[int,int,int]])->tuple[dict[str,Any],list[tuple[int,int,int]]]:
 selected=[(i,c) for i,c in enumerate(clauses,1) if relation_id(c) in {'000','111'}]
 V=sorted({abs(x) for _,c in selected for x in c})
 constraints=[]
 for ordinal,c in selected:
  scope=sorted(abs(x) for x in c);allowed=[]
  for bits in itertools.product((0,1),repeat=3):
   a=dict(zip(scope,bits,strict=True))
   if any((a[abs(lit)]==1) if lit>0 else (a[abs(lit)]==0) for lit in c):allowed.append(list(bits))
  constraints.append({'id':f'satlib_{name.lower()}_c{ordinal:03d}','scope':scope,'allowed':sorted(allowed)})
 constraints.sort(key=lambda r:(tuple(r['scope']),tuple(''.join(str(x) for x in t) for t in r['allowed']),r['id']))
 raw={'variables':V,'constraints':constraints}
 edges=[tuple(sorted(abs(x) for x in c)) for _,c in selected]
 return raw,edges


def sha(obj:Any)->str:
 return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def pmatrix(edges):
 p=Counter()
 for e in edges:
  for a,b in itertools.combinations(e,2):p[tuple(sorted((a,b)))]+=1
 return p


def degrees(V,edges):
 d=Counter()
 for e in edges:
  for v in e:d[v]+=1
 return {v:d[v] for v in V}


def sig_l1(V,edges):
 p=pmatrix(edges);d=degrees(V,edges);o={}
 for v in V:
  vals=[]
  for u in V:
   if u==v:continue
   x=p[tuple(sorted((v,u)))]
   if x:vals.append(x)
  o[v]=(d[v],tuple(sorted(vals)))
 return o


def sig_l2(V,edges):
 p=pmatrix(edges);d=degrees(V,edges);acc={v:[] for v in V}
 for e in edges:
  for v in e:
   q=[x for x in e if x!=v];a,b=q
   x,y=sorted((p[tuple(sorted((v,a)))],p[tuple(sorted((v,b))) ]))
   acc[v].append((x,y,p[tuple(sorted((a,b)))]))
 return {v:(d[v],tuple(sorted(acc[v]))) for v in V}


def sig_l3(V,edges):
 vars_nodes=[('v',v) for v in V];cons_nodes=[('c',i) for i in range(len(edges))]
 nbr={n:[] for n in vars_nodes+cons_nodes}
 for i,e in enumerate(edges):
  for v in e:nbr[('v',v)].append(('c',i));nbr[('c',i)].append(('v',v))
 col={n:(('VAR',) if n[0]=='v' else ('CORE_CONSTRAINT',)) for n in nbr}
 for r in range(3):
  prev=col;col={}
  for n in nbr:col[n]=(prev[n],tuple(sorted(prev[z] for z in nbr[n])))
 return {v:col[('v',v)] for v in V}


def sig_l4(V,edges):
 bypair=defaultdict(list)
 for i,e in enumerate(edges):
  for p in itertools.combinations(e,2):bypair[tuple(sorted(p))].append(i)
 tot=Counter();pairtot=Counter()
 for tri in itertools.combinations(V,3):
  a,b,c=tri
  for x in bypair.get((a,b),[]):
   for y in bypair.get((b,c),[]):
    if y==x:continue
    for z in bypair.get((a,c),[]):
     if z in (x,y):continue
     for v in tri:tot[v]+=1
     for q in itertools.combinations(tri,2):pairtot[tuple(sorted(q))]+=1
 out={}
 for v in V:
  vals=[]
  for u in V:
   if u==v:continue
   k=pairtot[tuple(sorted((v,u)))]
   if k:vals.append(k)
  out[v]=(tot[v],tuple(sorted(vals)))
 return out


def classes_and_digest(sig):
 buckets=defaultdict(list);serial=[]
 for v in sorted(sig):
  k=json.dumps(sig[v],sort_keys=True,separators=(',',':'),ensure_ascii=False);buckets[k].append(v);serial.append([v,sig[v]])
 cls=[sorted(x) for x in buckets.values()];cls.sort(key=lambda x:(x[0],len(x),x))
 return cls,sha(serial)


def recompute()->dict[str,Any]:
 pre=json.loads(PREREG.read_text())
 expected=pre['frozen_projected_raw_sha256']
 datasets={}
 for name,path in SOURCES.items():
  raw,edges=canonical_projected_raw(name,parse_dimacs(path));raw_sha=sha(raw)
  if raw_sha!=expected[name]:raise AssertionError((name,raw_sha,expected[name]))
  datasets[name]=(raw['variables'],edges,raw_sha)
 funcs={CIDS[0]:sig_l1,CIDS[1]:sig_l2,CIDS[2]:sig_l3,CIDS[3]:sig_l4}
 results=[]
 for cid in CIDS:
  rows=[];by={}
  for name,(V,edges,raw_sha) in datasets.items():
   sig=funcs[cid](V,edges);cls,dig=classes_and_digest(sig);non=[c for c in cls if len(c)>1]
   row={'source':name,'raw_sha256':raw_sha,'variable_count':len(V),'constraint_count':len(edges),'classes':cls,'nontrivial_classes':non,'max_class_size':max(map(len,cls)),'signature_map_sha256':dig}
   rows.append(row);by[name]=row
  ctrl=next(c for c in by['UF20_01']['classes'] if 7 in c);cok=ctrl==[7,10]
  pok=all(all(len(c)==1 for c in by[n]['classes']) for n in ('UF20_02','UF20_03','UF20_04','UF20_05'))
  results.append({'candidate_id':cid,'survives':cok and pok,'control_pair_class':ctrl,'control_pair_exact':cok,'panel_all_singleton':pok,'rows':rows})
 survivors=[x['candidate_id'] for x in results if x['survives']]
 verdict='PASS_SCOPED_AT_LEAST_ONE_PREREGISTERED_LOCAL_CANDIDATE_SURVIVES_FALSIFIER' if survivors else 'FAIL_NO_PREREGISTERED_LOCAL_CANDIDATE_SURVIVES_FALSIFIER'
 return {'verdict':verdict,'surviving_candidates':survivors,'candidate_results':results}


def main(candidate:dict[str,Any])->dict[str,Any]:
 ind=recompute()
 checks={
  'candidate_not_imported':True,
  'candidate_verdict':candidate.get('verdict')==ind['verdict'],
  'surviving_candidates':candidate.get('surviving_candidates')==ind['surviving_candidates'],
  'candidate_results_exact':candidate.get('candidate_results')==ind['candidate_results'],
  'candidate_count':candidate.get('resource_receipt',{}).get('candidate_count')==4,
  'no_solver':candidate.get('resource_receipt',{}).get('solver_invocations')==0,
  'no_group_search':candidate.get('resource_receipt',{}).get('group_searches')==0,
  'firewall':candidate.get('scientific_firewall',{}).get('P_VS_NP')=='OPEN' and candidate.get('scientific_firewall',{}).get('GENERAL_SAT_IN_P')=='NOT_PROVED',
 }
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-RESIDUAL-LOCAL-INVARIANT-FALSIFIER-INDEPENDENT-CHECK-2026-09-16-v1.0','candidate_imported':False,'verified':all(checks.values()),'checks':checks,'independent_verdict':ind['verdict'],'independent_surviving_candidates':ind['surviving_candidates'],'independent_candidate_results':ind['candidate_results']}


if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();cand=json.loads(Path(a.candidate_json).read_text().strip().splitlines()[-1]);out=main(cand);print(json.dumps(out,sort_keys=True,separators=(',',':')));raise SystemExit(0 if out['verified'] else 1)
