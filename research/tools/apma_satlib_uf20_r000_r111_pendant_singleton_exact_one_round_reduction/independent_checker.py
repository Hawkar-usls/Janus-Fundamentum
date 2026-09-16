from __future__ import annotations

import argparse,hashlib,itertools,json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_PREREGISTRATION_REVIEW_2026-09-17.json'
DEPEND=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_DELETION_DEPENDENCY_AUDIT_RESULT_2026-09-17.json'
BOUNDARY=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17_v1.1.json'
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
SOURCES={
 'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865','cc181d11871a9907cd5024ef5f0951cb29b32c4ed378e06c48f432e20be580e6'),
 'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f','30beb0c870105dfbbf017c067298f3295fcb555130e045242fdacea9259eb97d'),
 'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1','db98a7a25397a7178df02e16e9f593fde432f9b07d3aa14b44d67dcd051069f3'),
 'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b','fd9c0c19089daf08e549ff3ab63c0c7203b61c03cce7c4bcce0778ca2fe4f3d6')}
CUBE=tuple(itertools.product((0,1),repeat=3))

def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(path):
 clauses=[];header=None
 for raw in path.read_text(encoding='utf-8').splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in {'%','0'}:continue
  if s.startswith('p '):
   p=s.split();assert p[:2]==['p','cnf'] and len(p)==4;header=(int(p[2]),int(p[3]));continue
  vals=[int(x) for x in s.split()];assert len(vals)==4 and vals[-1]==0;c=tuple(vals[:-1]);assert len({abs(x) for x in c})==3;clauses.append(c)
 assert header==(20,91) and len(clauses)==91;return clauses
def rid(c):return ''.join('0' if x>0 else '1' for x in sorted(c,key=lambda z:abs(z)))
def allowed(c):
 scope=sorted(abs(x) for x in c);out=[]
 for bits in CUBE:
  a=dict(zip(scope,bits))
  if any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in c):out.append(list(bits))
 return sorted(out)
def projected(name,clauses):
 selected=[(i,c) for i,c in enumerate(clauses,1) if rid(c) in {'000','111'}];V=sorted({abs(l) for _,c in selected for l in c});rows=[]
 for ordinal,c in selected:rows.append({'id':f'satlib_{name.lower()}_c{ordinal:03d}','scope':sorted(abs(x) for x in c),'allowed':allowed(c)})
 rows.sort(key=lambda r:(tuple(r['scope']),tuple(''.join(map(str,t)) for t in r['allowed']),r['id']))
 return {'variables':V,'constraints':rows}
def expected():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());dep=json.loads(DEPEND.read_text());bound=json.loads(BOUNDARY.read_text())
 assert pre['status']=='FROZEN_BEFORE_ANY_REDUCED_RAW_VALUE_OR_HASH_COMPUTATION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE';assert dep['verdict']=='NO_INTER_ATTACHMENT_DEPENDENCIES' and dep['edge_count']==0;assert dep['composition_theorem']['composition_argument_verified'] is True;assert bound['verdict']=='ALL_ELEVEN_UNIVERSAL' and bound['local_semantics_theorem']['symbolic_projection_equivalence_verified'] is True
 bysource={r['source']:r['attachments'] for r in bound['source_receipts']};rows=[]
 for name in ORDER:
  path,sblob,rsha=SOURCES[name];assert blob(path)==sblob;raw=projected(name,parse(path));assert csha(raw)==rsha
  aa=bysource[name];leaves=sorted(int(a['leaf_variable']) for a in aa);cids=sorted(str(a['constraint_id']) for a in aa);assert len(leaves)==len(set(leaves));leafset=set(leaves);cidset=set(cids);byid={c['id']:c for c in raw['constraints']}
  occurrence={v:[c['id'] for c in raw['constraints'] if v in c['scope']] for v in leaves};unique=all(occurrence[int(a['leaf_variable'])]==[a['constraint_id']] for a in aa);gateway=all(all(int(g) not in leafset and int(g) in raw['variables'] for g in a['gateway_order']) for a in aa);scope=all(set(byid[a['constraint_id']]['scope'])==set([int(a['leaf_variable'])]+[int(x) for x in a['gateway_order']]) for a in aa)
  retained=[c for c in raw['constraints'] if c['id'] not in cidset];no_leaf=all(not(set(c['scope'])&leafset) for c in retained);reduced={'variables':[v for v in raw['variables'] if v not in leafset],'constraints':retained}
  cert=[]
  for a in sorted(aa,key=lambda x:x['constraint_id']):
   w={str(k):int(v) for k,v in a['canonical_reconstruction_witnesses'].items()};assert set(w)=={'00','01','10','11'};cert.append({'source':name,'constraint_id':a['constraint_id'],'leaf_variable':int(a['leaf_variable']),'gateway_order':[int(x) for x in a['gateway_order']],'canonical_reconstruction_witnesses':w,'leaf_original_constraint_occurrences':occurrence[int(a['leaf_variable'])]})
  rows.append({'source':name,'original_projected_raw_sha256':rsha,'original_variable_count':len(raw['variables']),'original_constraint_count':len(raw['constraints']),'removed_leaves':leaves,'removed_constraint_ids':cids,'removed_attachment_count':len(aa),'leaf_occurrence_lists':{str(k):v for k,v in occurrence.items()},'unique_occurrence_verified':unique,'gateway_survival_verified':gateway,'target_scope_binding_verified':scope,'no_deleted_leaf_in_retained_constraint_verified':no_leaf,'retained_constraints_exact_object_equality_verified':True,'reduced_variable_count':len(reduced['variables']),'reduced_constraint_count':len(reduced['constraints']),'reduced_raw_sha256':csha(reduced),'reduced_raw':reduced,'reconstruction_entries':cert})
 return rows
def main(path):
 c=json.loads(Path(path).read_text().strip().splitlines()[-1]);rows=expected();assert c['rows']==rows,(c['rows'],rows);assert c['verdict']=='PASS_EXACT_SIMULTANEOUS_ONE_ROUND_PENDANT_REDUCTION_CERTIFIED'
 cert=c['reconstruction_certificate'];assert cert['reduction_rounds']==1 and cert['fixed_point_iterations']==0 and cert['zero_dependency_required_and_verified'] is True and cert['symbolic_equivalence_verified'] is True
 assert cert['source_entries']==[{'source':r['source'],'entries':r['reconstruction_entries']} for r in rows]
 rr=c['resource_receipt'];assert rr['target_sources']==4 and rr['target_attachments']==11 and rr['reduction_rounds']==1 and rr['fixed_point_iterations']==0 and rr['fresh_holdout_values_read']==0 and rr['global_solver_invocations']==0 and rr['component_solver_invocations']==0 and rr['portfolio_replays']==0 and rr['full_assignment_cube_enumerations']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_quotients']==0
 return {'verified':True,'candidate_imported':False,'verdict':c['verdict'],'rows':rows,'reconstruction_certificate':cert,'symbolic_equivalence_verified':True,'reduction_rounds':1,'fixed_point_iterations':0,'global_solver_invocations':0,'fresh_holdout_values_read':0,'preregistration_blob':blob(PREREG),'review_blob':blob(REVIEW),'dependency_result_blob':blob(DEPEND),'boundary_result_blob':blob(BOUNDARY)}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(a.candidate_json),sort_keys=True,separators=(',',':')))
