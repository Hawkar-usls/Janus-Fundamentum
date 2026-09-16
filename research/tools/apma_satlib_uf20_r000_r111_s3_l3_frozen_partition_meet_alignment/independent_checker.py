from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_FROZEN_PARTITION_MEET_ALIGNMENT_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_S3_L3_FROZEN_PARTITION_MEET_ALIGNMENT_PREREGISTRATION_REVIEW_2026-09-17.json'
EQUIV_RESULT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_EXISTING_SIGNATURE_EQUIVALENCE_AUDIT_RESULT_2026-09-17.json'
EXPECTED={
 PREREG:'01b7a1f2da7956c5bab2734c39cda2f9703fac07',REVIEW:'9980a3da4f5634d681f2394b032ac840ef13aac9',EQUIV_RESULT:'971d7d98a86471e88bf33336da215171b2f8cdfe',
 ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PROJECTED_CORE_EXISTING_SIGNATURE_ABLATION_REPLAY_RESULT_2026-09-16.json':'b7ba5bd772c3092e0436dde8bd717dc28985983c',
 ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RESIDUAL_LOCAL_INVARIANT_FALSIFIER_RESULT_2026-09-16.json':'954893935bee1d46a77c5f635086e0e278b05fac',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_signature_ablation/replay.py':'2edad57e6017cb34bf797313e4451c1ce014900b',
 ROOT/'research/tools/apma_satlib_uf20_r000_r111_residual_local_invariant_falsifier/candidate.py':'4ec02d6d42e6cad7d91f16b1acfdcbe51dbd65df',
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
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def relation_key_rows(rows):return tuple(sorted(''.join(str(int(b)) for b in row) for row in rows))
def full_surface_order():
 keys=[]
 for forbidden in CUBE:
  allowed=[r for r in CUBE if r!=forbidden];keys.append((relation_key_rows(allowed),''.join(map(str,forbidden))))
 keys.sort(key=lambda x:x[0]);return [k for k,_ in keys],[rid for _,rid in keys]
def selected(path):return [c for c in projection_identity.parse(path) if projection_identity.rid(c) in {'000','111'}]

def s3_partition(raw,clauses):
 V=raw['variables'];adj={v:set() for v in V}
 for c in raw['constraints']:
  for u,v in itertools.combinations(c['scope'],2):adj[u].add(v);adj[v].add(u)
 degree={v:len(adj[v]) for v in V};pos=Counter();neg=Counter()
 for clause in clauses:
  for lit in clause:(pos if lit>0 else neg)[abs(lit)]+=1
 keys,rids=full_surface_order();assert rids==['111','110','101','100','011','010','001','000'];idx={k:i for i,k in enumerate(keys)};inc={v:[0]*8 for v in V}
 for c in raw['constraints']:
  i=idx[relation_key_rows(c['allowed'])]
  for v in c['scope']:inc[v][i]+=1
 sig={v:(degree[v],pos[v],neg[v],tuple(inc[v]),tuple(sorted(degree[n] for n in adj[v]))) for v in V};return partition(sig)[0]

def l3_partition(V,edges):
 nodes=[('v',v) for v in V]+[('c',i) for i in range(len(edges))];nbr={n:[] for n in nodes}
 for i,e in enumerate(edges):
  c=('c',i)
  for v in e:x=('v',v);nbr[c].append(x);nbr[x].append(c)
 color={n:(('VAR',) if n[0]=='v' else ('CORE_CONSTRAINT',)) for n in nodes}
 for _ in range(3):old=color;color={n:(old[n],tuple(sorted(old[m] for m in nbr[n]))) for n in nodes}
 sig={v:color[('v',v)] for v in V};return partition(sig)[0]

def partition(sig):
 groups=defaultdict(list)
 for v in sorted(sig):groups[json.dumps(sig[v],sort_keys=True,separators=(',',':'),ensure_ascii=False)].append(v)
 out=[sorted(x) for x in groups.values()];out.sort(key=lambda c:(c[0],len(c),c));return out,csha([[v,sig[v]] for v in sorted(sig)])
def meet(p,q):
 out=[]
 for a in p:
  sa=set(a)
  for b in q:
   x=sorted(sa.intersection(b))
   if x:out.append(x)
 out.sort(key=lambda c:(c[0],len(c),c));return out
def nontriv(p):return [c for c in p if len(c)>1]

def recompute(pre):
 rows=[]
 for name,(path,_) in SOURCES.items():
  clauses=projection_identity.parse(path);raw,_=projection_identity.normalize_projection(name,clauses);raw_sha=csha(raw);assert raw_sha==pre['frozen_projected_raw_sha256'][name]
  sel=[c for c in clauses if projection_identity.rid(c) in {'000','111'}];edges=[tuple(sorted(abs(x) for x in c)) for c in sel];V=sorted({v for e in edges for v in e});assert V==raw['variables']
  s3=s3_partition(raw,sel);l3=l3_partition(V,edges);m=meet(s3,l3)
  rows.append({'source':name,'status':'AUDITED','raw_sha256':raw_sha,'S3_partition':s3,'S3_non_singleton_classes':nontriv(s3),'L3_partition':l3,'L3_non_singleton_classes':nontriv(l3),'meet_partition':m,'meet_partition_sha256':csha(m),'meet_non_singleton_classes':nontriv(m),'meet_all_singleton':all(len(c)==1 for c in m)})
 return rows

def main(candidate_path:Path):
 bindings={str(p.relative_to(ROOT)):blob(p)==s for p,s in EXPECTED.items()};sources={n:blob(p)==s for n,(p,s) in SOURCES.items()};assert all(bindings.values()) and all(sources.values()),(bindings,sources)
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());eq=json.loads(EQUIV_RESULT.read_text());assert pre['status']=='FROZEN_BEFORE_ANY_PARTITION_MEET_EXECUTION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 candidate=json.loads(candidate_path.read_text().strip().splitlines()[-1]);rows=recompute(pre);by={r['source']:r for r in rows};key=eq['key_partition_receipts']
 assert by['UF20_01']['L3_non_singleton_classes']==key['UF20_01']['L3_non_singleton_classes'];assert by['UF20_01']['S3_non_singleton_classes']==key['UF20_01']['S3_non_singleton_classes'];assert by['UF20_03']['S3_non_singleton_classes']==key['UF20_03']['S3_non_singleton_classes'];assert by['UF20_03']['L3_non_singleton_classes']==[]
 for n in ('UF20_02','UF20_04','UF20_05'):assert by[n]['S3_non_singleton_classes']==[] and by[n]['L3_non_singleton_classes']==[]
 rule=pre['a_priori_alignment_test'];control=by['UF20_01']['meet_non_singleton_classes']==[rule['UF20_01_expected_only_non_singleton_meet_class']];panel=all(by[n]['meet_all_singleton'] for n in ('UF20_02','UF20_03','UF20_04','UF20_05'));verdict=rule['pass_verdict'] if control and panel else rule['fail_verdict']
 assert candidate['verdict']==verdict;assert candidate['rows']==rows;assert candidate['control_alignment_pass']==control and candidate['panel_alignment_pass']==panel and candidate['frozen_partition_receipts_verified'] is True
 rr=candidate['resource_receipt'];assert rr['partition_meets']==5 and rr['solver_invocations']==0 and rr['group_searches']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0 and rr['budget_raise'] is False
 sf=candidate['scientific_firewall'];assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO'
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'control_meet_non_singleton_classes':by['UF20_01']['meet_non_singleton_classes'],'panel_all_singleton':panel,'partition_meets_verified':5}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);args=ap.parse_args();print(json.dumps(main(Path(args.candidate_json)),sort_keys=True,separators=(',',':')))
