from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_D2_D3_WITNESS_RECONSTRUCTION_RESULT_2026-09-17.json'
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}
BOUNDARY=((0,0),(0,1),(1,0),(1,1));LEAF=(0,1);CUBE=tuple(itertools.product((0,1),repeat=3))

def csha(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(path):
 clauses=[];buf=[];header=None
 for line in path.read_text(encoding='utf-8').splitlines():
  s=line.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):p=s.split();header=(int(p[2]),int(p[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3;clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert header==(20,91) and len(clauses)==91 and not buf;return clauses
def allowed(clause,scope):
 out=[]
 for bits in CUBE:
  a=dict(zip(scope,bits));sat=any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in clause)
  if sat:out.append(list(bits))
 return out
def raw(source,path):
 rows=[];variables=set()
 for i,c in enumerate(parse(path),1):
  pos=sum(x>0 for x in c)
  if pos not in {0,3}:continue
  scope=sorted(abs(x) for x in c);variables.update(scope);rows.append({'id':f'satlib_{source.lower()}_c{i:03d}','scope':scope,'allowed':allowed(c,scope)})
 rows.sort(key=lambda r:(tuple(r['scope']),tuple(''.join(map(str,t)) for t in r['allowed']),r['id']))
 return {'variables':sorted(variables),'constraints':rows}
def full(scope,leaf,gateway,b,z):
 a={leaf:z,gateway[0]:b[0],gateway[1]:b[1]};return tuple(a[v] for v in scope)
def one(r,m):
 by={c['id']:c for c in r['constraints']};cid=m['constraint_id'];assert cid in by;c=by[cid];scope=list(c['scope']);leaf=int(m['leaf_variable']);gateway=sorted(map(int,m['gateway_pair']));assert scope==list(m['actual_scope']) and set(scope)==set([leaf]+gateway)
 occ=sum(leaf in q['scope'] for q in r['constraints']);aset={tuple(t) for t in c['allowed']};checks=[];rel=[];wits={};tests=0
 for b in BOUNDARY:
  trials=[];first=None
  for z in LEAF:
   ft=full(scope,leaf,gateway,b,z);ok=ft in aset;tests+=1;trials.append({'leaf_value':z,'full_scope_tuple':list(ft),'allowed':ok})
   if ok and first is None:first=z
  accepted=first is not None;checks.append({'boundary_tuple':list(b),'trials':trials,'accepted':accepted,'canonical_leaf_witness':first})
  if accepted:rel.append(list(b));wits[''.join(map(str,b))]=first
 card=len(rel);out='UNIVERSAL_BOUNDARY_RELATION_4_OF_4' if card==4 else 'PROPER_NONEMPTY_BOUNDARY_RELATION' if card else 'EMPTY_BOUNDARY_RELATION'
 return {'constraint_id':cid,'actual_scope':scope,'leaf_variable':leaf,'gateway_pair':gateway,'leaf_projected_constraint_occurrence_count':occ,'allowed_table_sha256':csha({'scope':scope,'allowed':c['allowed']}),'boundary_checks':checks,'boundary_relation':rel,'boundary_relation_cardinality':card,'canonical_reconstruction_witnesses':wits,'membership_tests':tests,'outcome':out}
def main(path):
 c=json.loads(Path(path).read_text().strip().splitlines()[-1]);parent=json.loads(PARENT.read_text());maps={r['source']:r['mappings'] for r in parent['source_receipts']};rows=[]
 for source in ORDER:
  p,expected=SOURCES[source];r=raw(source,p);sha=csha(r);assert sha==expected,(source,sha,expected);rows.append({'source':source,'projected_raw_sha256':sha,'attachments':[one(r,m) for m in maps[source]]})
 assert c['rows']==rows,(c['rows'],rows);aa=[a for r in rows for a in r['attachments']];out=Counter(a['outcome'] for a in aa);overall='AT_LEAST_ONE_EMPTY' if out['EMPTY_BOUNDARY_RELATION'] else 'ALL_ELEVEN_UNIVERSAL' if out['UNIVERSAL_BOUNDARY_RELATION_4_OF_4']==11 else 'MIXED_OR_PROPER';assert c['verdict']==overall;counts={k:int(out.get(k,0)) for k in ('UNIVERSAL_BOUNDARY_RELATION_4_OF_4','PROPER_NONEMPTY_BOUNDARY_RELATION','EMPTY_BOUNDARY_RELATION')};assert c['outcome_counts']==counts
 unique=all(a['leaf_projected_constraint_occurrence_count']==1 for a in aa);univ=all(a['boundary_relation_cardinality']==4 for a in aa);th=overall=='ALL_ELEVEN_UNIVERSAL' and unique and univ;assert c['local_semantics_theorem']['symbolic_projection_equivalence_verified']==th and c['local_semantics_theorem']['deletion_applied'] is False
 rr=c['resource_receipt'];assert rr['attachments']==11 and rr['boundary_assignments']==44 and rr['table_membership_tests']==88 and rr['superseded_old_alignment_rows_read']==0 and rr['attachment_deletions']==0 and rr['solver_invocations']==0 and rr['fresh_holdout_values_read']==0
 return {'verified':True,'candidate_imported':False,'verdict':overall,'outcome_counts':counts,'rows':rows,'local_semantics_theorem_verified':th,'resource_receipt':rr}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--candidate-json',required=True);a=p.parse_args();print(json.dumps(main(a.candidate_json),sort_keys=True,separators=(',',':')))
