from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXISTENTIAL_BOUNDARY_PROJECTION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXISTENTIAL_BOUNDARY_PROJECTION_PREREGISTRATION_REVIEW_2026-09-17.json'
ALIGN=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_D2_D3_SINGLETON_ATTACHMENT_SCOPE_ALIGNMENT_RESULT_2026-09-17.json'
FRESH=ROOT/'research/TRUMP_SATLIB_UF20_SUCCESSOR_LOCAL_INVARIANT_FRESH_BLIND_SOURCE_ACQUISITION_RESULT_2026-09-17.json'
EXPECTED={PREREG:'1b1e2959bc238f18fa8f951876072f9f4c8f917f',REVIEW:'f44771b6f32c0837aea18bc4f03d2f74cf703c4b',ALIGN:'9442fca30db3e623c56a33d8fda6c3a1e3c1f624',FRESH:'3ee5a11808ea04326ec5141b0138bbba4ec56092'}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}
CUBE=tuple(itertools.product((0,1),repeat=3));BOUNDARY=((0,0),(0,1),(1,0),(1,1));LEAF_VALUES=(0,1)

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
  vals=[int(z) for z in s.split()];assert len(vals)==4 and vals[-1]==0;c=tuple(vals[:-1]);assert len({abs(x) for x in c})==3;clauses.append(c)
 assert header==(20,91) and len(clauses)==91;return clauses
def rid(c):return ''.join('0' if lit>0 else '1' for lit in sorted(c,key=lambda x:abs(x)))
def allowed(c):
 scope=sorted(abs(x) for x in c);out=[]
 for bits in CUBE:
  a=dict(zip(scope,bits))
  if any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in c):out.append(list(bits))
 return sorted(out)
def raw_project(name,clauses):
 selected=[(i,c) for i,c in enumerate(clauses,1) if rid(c) in {'000','111'}];V=sorted({abs(l) for _,c in selected for l in c});rows=[]
 for ordinal,c in selected:rows.append({'id':f'satlib_{name.lower()}_c{ordinal:03d}','scope':sorted(abs(x) for x in c),'allowed':allowed(c)})
 rows.sort(key=lambda r:(tuple(r['scope']),tuple(''.join(map(str,t)) for t in r['allowed']),r['id']))
 return {'variables':V,'constraints':rows}
def coord_map(scope,leaf,gateway):
 roles={leaf:'LEAF',gateway[0]:'GATEWAY_0',gateway[1]:'GATEWAY_1'};return [{'scope_index':i,'variable':int(v),'role':roles[int(v)]} for i,v in enumerate(scope)]
def full_tuple(scope,leaf,gateway,b,z):
 a={leaf:z,gateway[0]:b[0],gateway[1]:b[1]};return tuple(a[int(v)] for v in scope)
def attachment(raw,mapping):
 by_id={r['id']:r for r in raw['constraints']};cid=mapping['constraint_id'];c=by_id[cid];scope=[int(v) for v in c['scope']];leaf=int(mapping['singleton_variable']);gateway=sorted(int(v) for v in mapping['gateway_pair']);assert scope==mapping['scope'] and set(scope)==set([leaf]+gateway)
 occurrence=sum(leaf in r['scope'] for r in raw['constraints']);aset={tuple(int(x) for x in t) for t in c['allowed']};checks=[];boundary=[];witnesses={};tests=0
 for b in BOUNDARY:
  trials=[];w=None
  for z in LEAF_VALUES:
   ft=full_tuple(scope,leaf,gateway,b,z);ok=ft in aset;tests+=1;trials.append({'leaf_value':z,'full_scope_tuple':list(ft),'allowed':ok})
   if ok and w is None:w=z
  accepted=w is not None;checks.append({'boundary_tuple':list(b),'tested_leaf_values':trials,'accepted':accepted,'canonical_leaf_witness':w})
  if accepted:boundary.append(list(b));witnesses[''.join(map(str,b))]=w
 card=len(boundary);outcome='UNIVERSAL_BOUNDARY_RELATION_4_OF_4' if card==4 else 'PROPER_NONEMPTY_BOUNDARY_RELATION' if card>0 else 'EMPTY_BOUNDARY_RELATION'
 return {'constraint_id':cid,'scope':scope,'allowed_table_sha256':csha({'scope':scope,'allowed':c['allowed']}),'leaf_variable':leaf,'leaf_projected_constraint_occurrence_count':occurrence,'gateway_order':gateway,'scope_coordinate_map':coord_map(scope,leaf,gateway),'boundary_checks':checks,'boundary_relation':boundary,'boundary_relation_cardinality':card,'canonical_reconstruction_witnesses':witnesses,'membership_tests':tests,'outcome':outcome}
def expected_rows():
 assert all(blob(p)==s for p,s in EXPECTED.items());pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());assert pre['status']=='FROZEN_BEFORE_ANY_EXISTENTIAL_BOUNDARY_RELATION_VALUE_COMPUTATION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 align=json.loads(ALIGN.read_text());maps={r['source']:r['mappings'] for r in align['source_receipts']};assert sum(map(len,maps.values()))==11;rows=[]
 for name in ORDER:
  path,sblob,rsha=SOURCES[name];assert blob(path)==sblob;raw=raw_project(name,parse(path));assert csha(raw)==rsha;rows.append({'source':name,'projected_raw_sha256':rsha,'attachments':[attachment(raw,m) for m in maps[name]]})
 return rows
def main(candidate_path:Path):
 c=json.loads(candidate_path.read_text().strip().splitlines()[-1]);rows=expected_rows();assert c['rows']==rows,(c['rows'],rows);aa=[a for r in rows for a in r['attachments']];out=Counter(a['outcome'] for a in aa)
 overall='AT_LEAST_ONE_EMPTY' if out['EMPTY_BOUNDARY_RELATION'] else 'ALL_ELEVEN_UNIVERSAL' if out['UNIVERSAL_BOUNDARY_RELATION_4_OF_4']==11 else 'MIXED_OR_PROPER';assert c['verdict']==overall and c['overall_outcome']==overall
 expected_counts={k:int(out.get(k,0)) for k in ('UNIVERSAL_BOUNDARY_RELATION_4_OF_4','PROPER_NONEMPTY_BOUNDARY_RELATION','EMPTY_BOUNDARY_RELATION')};assert c['outcome_counts']==expected_counts
 unique=all(a['leaf_projected_constraint_occurrence_count']==1 for a in aa);univ=all(a['boundary_relation_cardinality']==4 for a in aa);theorem=overall=='ALL_ELEVEN_UNIVERSAL' and unique and univ
 assert c['local_semantics_theorem']['applicable']==(overall=='ALL_ELEVEN_UNIVERSAL');assert c['local_semantics_theorem']['all_leaf_unique_occurrence_premises_verified']==unique;assert c['local_semantics_theorem']['all_boundary_relations_universal_verified']==univ;assert c['local_semantics_theorem']['symbolic_projection_equivalence_verified']==theorem;assert c['local_semantics_theorem']['deletion_applied'] is False
 rr=c['resource_receipt'];assert rr['attachments']==11 and rr['boundary_assignments']==44 and rr['table_membership_tests']==88 and rr['maximum_table_membership_tests']==88 and rr['attachment_deletions']==0 and rr['projected_raw_modifications']==0 and rr['fresh_holdout_values_read']==0 and rr['global_solver_invocations']==0 and rr['portfolio_replays']==0 and rr['component_solution_attempts']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0
 return {'verified':True,'candidate_imported':False,'verdict':overall,'outcome_counts':expected_counts,'rows':rows,'local_semantics_theorem_verified':theorem,'table_membership_tests':88,'deletion_applied':False,'fresh_holdout_values_read':0}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(Path(a.candidate_json)),sort_keys=True,separators=(',',':')))
