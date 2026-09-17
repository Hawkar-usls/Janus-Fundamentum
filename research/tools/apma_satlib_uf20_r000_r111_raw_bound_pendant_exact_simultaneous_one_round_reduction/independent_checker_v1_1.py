from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_PREREGISTRATION_2026-09-17.json'
BOUNDARY=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17.json'
DEPENDENCY=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_SIMULTANEOUS_DEPENDENCY_AUDIT_RESULT_2026-09-17.json'
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}
CUBE=tuple(itertools.product((0,1),repeat=3))

def csha(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(path):
 clauses=[];buf=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):p=s.split();header=(int(p[2]),int(p[3]));continue
  for z in map(int,s.split()):
   if z==0:assert len(buf)==3 and len({abs(x) for x in buf})==3;clauses.append(tuple(buf));buf=[]
   else:buf.append(z)
 assert header==(20,91) and len(clauses)==91 and not buf;return clauses
def allowed(clause,scope):
 out=[]
 for bits in CUBE:
  a=dict(zip(scope,bits))
  if any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in clause):out.append(list(bits))
 return sorted(out)
def raw(source,path):
 rows=[];vars_=set()
 for i,c in enumerate(parse(path),1):
  positives=sum(x>0 for x in c)
  if positives not in {0,3}:continue
  scope=sorted(abs(x) for x in c);vars_.update(scope);rows.append({'id':f'satlib_{source.lower()}_c{i:03d}','scope':scope,'allowed':allowed(c,scope)})
 rows.sort(key=lambda r:(tuple(r['scope']),tuple(''.join(map(str,t)) for t in r['allowed']),r['id']))
 return {'variables':sorted(vars_),'constraints':rows}
def chash(c):return csha({'id':c['id'],'scope':c['scope'],'allowed':c['allowed']})
def expected_rows():
 pre=json.loads(PREREG.read_text());bound=json.loads(BOUNDARY.read_text());dep=json.loads(DEPENDENCY.read_text());assert bound['verdict']=='ALL_ELEVEN_UNIVERSAL' and dep['verdict']=='ZERO_CROSS_ATTACHMENT_DEPENDENCY';bsource={r['source']:r['attachments'] for r in bound['source_receipts']};rows=[]
 for source in ORDER:
  path,expected_sha=SOURCES[source];original=raw(source,path);orig_sha=csha(original);assert orig_sha==expected_sha,(source,orig_sha,expected_sha);target=pre['frozen_per_source_targets'][source];remove_ids=set(target['remove_constraints']);remove_leaves=set(map(int,target['remove_leaves']));byid={c['id']:c for c in original['constraints']};bmap={a['constraint_id']:a for a in bsource[source]};ids_exist=remove_ids.issubset(set(byid));leaves_exist=remove_leaves.issubset(set(original['variables']));targets_match=remove_ids==set(bmap) and remove_leaves==set(int(a['leaf']) for a in bsource[source]);pre_occ={str(leaf):[c['id'] for c in original['constraints'] if leaf in c['scope']] for leaf in sorted(remove_leaves)};pre_clean=all(len(v)==1 and v[0] in remove_ids for v in pre_occ.values());remain_c=[c for c in original['constraints'] if c['id'] not in remove_ids];remain_v=[v for v in original['variables'] if v not in remove_leaves];reduced={'variables':remain_v,'constraints':remain_c};leaf_absent=all(not(remove_leaves & set(c['scope'])) for c in remain_c);gateways=sorted({int(v) for a in bsource[source] for v in a['gateway']});gateways_remain=all(v in set(remain_v) for v in gateways);orig_nt={c['id']:chash(c) for c in original['constraints'] if c['id'] not in remove_ids};redmap={c['id']:chash(c) for c in reduced['constraints']};unchanged=orig_nt==redmap;no_extra=set(original['variables'])-set(remain_v)==remove_leaves;cert=[]
  for a in bsource[source]:
   w=a['canonical_witnesses'];cert.append({'source':source,'removed_constraint_id':a['constraint_id'],'removed_leaf':int(a['leaf']),'gateway_pair':[int(v) for v in a['gateway']],'canonical_witness_table_00_01_10_11':{k:int(w[k]) for k in ('00','01','10','11')}})
  cert.sort(key=lambda r:r['removed_constraint_id']);wcomplete=all(set(r['canonical_witness_table_00_01_10_11'])=={'00','01','10','11'} for r in cert);structural=all([ids_exist,leaves_exist,targets_match,pre_clean,leaf_absent,gateways_remain,unchanged,no_extra,wcomplete]);sem={'forward_projection_verified_symbolically':structural,'reverse_extension_verified_from_frozen_universal_boundary_and_zero_dependency':structural,'projection_solution_set_equality_verified_symbolically':structural,'sat_equivalence_verified_symbolically':structural,'global_assignment_enumeration_used':False}
  rows.append({'source':source,'original_projected_raw_sha256':orig_sha,'original_variable_count':len(original['variables']),'original_constraint_count':len(original['constraints']),'removed_constraint_ids':sorted(remove_ids),'removed_leaves':sorted(remove_leaves),'pre_transform_leaf_occurrences':pre_occ,'reduced_raw':reduced,'reduced_raw_sha256':csha(reduced),'reduced_variable_count':len(reduced['variables']),'reduced_constraint_count':len(reduced['constraints']),'remaining_constraint_fingerprints':redmap,'all_target_constraints_exist':ids_exist,'all_target_leaves_exist':leaves_exist,'targets_match_frozen_boundary_receipts':targets_match,'each_removed_leaf_occurs_only_in_own_target_constraint':pre_clean,'no_removed_leaf_in_remaining_scope':leaf_absent,'all_gateways_remain':gateways_remain,'all_nontarget_constraints_unchanged':unchanged,'no_nontarget_variable_removed':no_extra,'reconstruction_certificate':cert,'semantics_certificate':sem,'source_pass':structural and all(sem[k] for k in ('forward_projection_verified_symbolically','reverse_extension_verified_from_frozen_universal_boundary_and_zero_dependency','projection_solution_set_equality_verified_symbolically','sat_equivalence_verified_symbolically'))})
 return rows
def main(path):
 c=json.loads(Path(path).read_text().strip().splitlines()[-1]);rows=expected_rows();assert c['rows']==rows,(c['rows'],rows);expected='PASS_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION' if all(r['source_pass'] for r in rows) else 'FAIL_SEMANTICS_CERTIFICATE';assert c['verdict']==expected;rr=c['resource_receipt'];assert rr['reduction_rounds']==1 and rr['target_constraints']==11 and rr['target_leaves']==11 and rr['post_round_target_discoveries']==0 and rr['new_relations_added']==0 and rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['global_assignment_enumerations']==0 and rr['fresh_holdout_values_read']==0
 return {'verified':True,'candidate_imported':False,'checker_repair':'JSON_OBJECT_KEY_CANONICALIZATION_ONLY','verdict':expected,'rows':rows,'resource_receipt':rr}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(a.candidate_json),sort_keys=True,separators=(',',':')))
