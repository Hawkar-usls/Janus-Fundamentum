from __future__ import annotations

import argparse,hashlib,itertools,json
from collections import defaultdict
from pathlib import Path
from typing import Any,Hashable

from research.tools.apma_mixed_carrier_barrier.check_schaefer_barrier import is_0_valid,is_1_valid,is_horn,is_dual_horn,is_bijunctive,is_affine

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_ONE_ROUND_REDUCED_RAW_EXISTING_ROUTE_REEVALUATION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_ONE_ROUND_REDUCED_RAW_EXISTING_ROUTE_REEVALUATION_PREREGISTRATION_REVIEW_2026-09-17.json'
REDUCTION=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17.json'
ORIG_STRUCT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_NONREFINEMENT_STRUCTURAL_DECOMPOSITION_MENU_RESULT_2026-09-17.json'
ORIG_MATRIX=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_FOUR_UNADMITTED_EXISTING_EVIDENCE_RESIDUAL_MATRIX_RESULT_2026-09-16.json'
SCHAEFER=ROOT/'research/tools/apma_mixed_carrier_barrier/check_schaefer_barrier.py'
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05')
DIDS=('D1_PRIMAL_ARTICULATION_BLOCK_PROFILE','D2_INCIDENCE_ARTICULATION_BLOCK_PROFILE','D3_PRIMAL_MINIMAL_TWO_VERTEX_SEPARATOR_PROFILE')

def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(o:Any):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def nk(n:Hashable):
 if isinstance(n,tuple):return (0,int(n[1])) if n[0]=='VAR' else (1,str(n[1]))
 return (2,str(n))
def comps(g,removed=None):
 removed=removed or set();unseen=set(g)-removed;out=[]
 while unseen:
  s=min(unseen,key=nk);unseen.remove(s);stack=[s];cc={s}
  while stack:
   u=stack.pop()
   for v in sorted(g[u],key=nk):
    if v not in removed and v in unseen:unseen.remove(v);cc.add(v);stack.append(v)
  out.append(cc)
 out.sort(key=lambda c:(len(c),[nk(x) for x in sorted(c,key=nk)]));return out
def primal(raw):
 g={int(v):set() for v in raw['variables']}
 for r in raw['constraints']:
  for a,b in itertools.combinations(r['scope'],2):a=int(a);b=int(b);g[a].add(b);g[b].add(a)
 return g
def incidence(raw):
 g={('VAR',int(v)):set() for v in raw['variables']}
 for r in raw['constraints']:
  c=('CONSTRAINT',str(r['id']));g[c]=set()
  for v in r['scope']:x=('VAR',int(v));g[x].add(c);g[c].add(x)
 return g
def articulations(g):
 base=len(comps(g));return [u for u in sorted(g,key=nk) if len(comps(g,{u}))>base]
def d1(g):
 rows=[]
 for v in articulations(g):rows.append({'variable':int(v),'residual_component_sizes':sorted(len(c) for c in comps(g,{v}) if c)})
 return {'articulation_rows':rows,'articulation_count':len(rows),'decomposition_present':any(len(r['residual_component_sizes'])>=2 for r in rows)}
def d2(g):
 rows=[]
 for a in articulations(g):
  prof=[]
  for c in comps(g,{a}):
   nv=sum(x[0]=='VAR' for x in c);nc=sum(x[0]=='CONSTRAINT' for x in c);prof.append([nv,nc,nv+nc])
  prof.sort();rows.append({'node_type':a[0],'node_name':('v'+str(a[1])) if a[0]=='VAR' else str(a[1]),'residual_component_profiles':prof})
 rows.sort(key=lambda r:(r['node_type'],r['node_name']))
 return {'articulation_rows':rows,'articulation_count':len(rows),'decomposition_present':any(len(r['residual_component_profiles'])>=2 for r in rows)}
def connected(g,removed=None):return len(comps(g,removed))<=1
def d3(g):
 rows=[];base=connected(g);V=sorted(g)
 if base:
  for u,v in itertools.combinations(V,2):
   if not connected(g,{u}) or not connected(g,{v}):continue
   cs=[c for c in comps(g,{u,v}) if c]
   if len(cs)>=2:rows.append({'pair':[u,v],'residual_component_sizes':sorted(len(c) for c in cs)})
 return {'separator_rows':rows,'separator_count':len(rows),'decomposition_present':bool(rows),'base_primal_graph_connected':base}
def language(raw):
 unique={}
 for c in raw['constraints']:
  r=frozenset(tuple(int(x) for x in t) for t in c['allowed']);unique[(len(c['scope']),tuple(sorted(r)))]=set(r)
 return [unique[k] for k in sorted(unique,key=lambda x:(x[0],x[1]))]
def fp(rels):return {'ZERO_VALID':is_0_valid(rels),'ONE_VALID':is_1_valid(rels),'HORN':is_horn(rels),'DUAL_HORN':is_dual_horn(rels),'BIJUNCTIVE':is_bijunctive(rels),'AFFINE':is_affine(rels)}
def expected_rows():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());red=json.loads(REDUCTION.read_text());orig=json.loads(ORIG_STRUCT.read_text());matrix=json.loads(ORIG_MATRIX.read_text())
 assert pre['status']=='FROZEN_BEFORE_ANY_REDUCED_ROUTE_REEVALUATION_VALUE_COMPUTATION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE';assert red['verdict']=='PASS_EXACT_SIMULTANEOUS_ONE_ROUND_PENDANT_REDUCTION_CERTIFIED';assert blob(SCHAEFER)=='11fcacd5f0c550543f96648a7965734308509d22';assert all(x in matrix['common_label_intersection'] for x in ('COMPOSITIONAL_OPEN_NO_SCHAEFER_BASIS','CONNECTED_R000_R111_CORE'));assert [orig['diagnostic_summary'][d]['presence_count'] for d in DIDS]==[0,4,4]
 rec={r['source']:r for r in red['reduced_source_receipts']};rows=[]
 for src in ORDER:
  rr=rec[src];p=ROOT/rr['reduced_raw_path'];raw=json.loads(p.read_text());assert blob(p)==rr['reduced_raw_git_blob'] and csha(raw)==rr['reduced_raw_sha256']
  pg=primal(raw);ig=incidence(raw);pc=comps(pg);ic=comps(ig);profiles=[]
  for cc in ic:
   nv=sum(n[0]=='VAR' for n in cc);nc=sum(n[0]=='CONSTRAINT' for n in cc);profiles.append([nv,nc,nv+nc])
  profiles.sort();connected_label='STILL_CONNECTED' if len(pc)==1 and len(ic)==1 else 'BECAME_DISCONNECTED';rels=language(raw);f=fp(rels);basis='ADMIT_AT_LEAST_ONE_FROZEN_SCHAEFER_BASIS' if any(f.values()) else 'OPEN_NO_SCHAEFER_BASIS';dd={DIDS[0]:d1(pg),DIDS[1]:d2(ig),DIDS[2]:d3(pg)}
  rows.append({'source':src,'reduced_raw_path':rr['reduced_raw_path'],'reduced_raw_git_blob':rr['reduced_raw_git_blob'],'reduced_raw_sha256':rr['reduced_raw_sha256'],'reduced_variable_count':len(raw['variables']),'reduced_constraint_count':len(raw['constraints']),'connected_component_status':{'primal_component_count':len(pc),'primal_component_sizes':sorted(len(c) for c in pc),'incidence_component_count':len(ic),'incidence_component_profiles':profiles,'label':connected_label},'explicit_relation_language':{'unique_relation_count':len(rels),'schaefer_fingerprint':f,'label':basis},'structural_diagnostics':dd})
 return rows
def main(path):
 c=json.loads(Path(path).read_text().strip().splitlines()[-1]);rows=expected_rows();assert c['rows']==rows,(c['rows'],rows);presence={d:sum(r['structural_diagnostics'][d]['decomposition_present'] for r in rows) for d in DIDS};route=any(r['connected_component_status']['label']=='BECAME_DISCONNECTED' or r['explicit_relation_language']['label']=='ADMIT_AT_LEAST_ONE_FROZEN_SCHAEFER_BASIS' for r in rows);struct=presence!={DIDS[0]:0,DIDS[1]:4,DIDS[2]:4}
 verdict='EXISTING_ROUTE_APPLICABILITY_CHANGED_ON_AT_LEAST_ONE_SOURCE' if route else 'NO_EXISTING_BASIS_OR_COMPONENT_ROUTE_CHANGE__STRUCTURAL_STATUS_CHANGED' if struct else 'NO_TESTED_ROUTE_STATUS_CHANGE_AFTER_ONE_ROUND_REDUCTION';assert c['verdict']==verdict and c['reduced_structural_presence_counts']==presence and c['route_applicability_changed']==route and c['structural_status_changed']==struct
 rr=c['resource_receipt'];assert rr['reduced_sources']==4 and rr['fresh_holdout_values_read']==0 and rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['additional_reduction_rounds']==0 and rr['fixed_point_iterations']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'rows':rows,'reduced_structural_presence_counts':presence,'route_applicability_changed':route,'structural_status_changed':struct,'fresh_holdout_values_read':0,'solver_invocations':0,'portfolio_replays':0,'additional_reduction_rounds':0,'preregistration_blob':blob(PREREG),'review_blob':blob(REVIEW),'reduction_result_blob':blob(REDUCTION)}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(a.candidate_json),sort_keys=True,separators=(',',':')))
