from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_06_L3_COLLISION_EXISTING_S0_S3_COMPONENT_LOCALIZATION_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_06_L3_COLLISION_EXISTING_S0_S3_COMPONENT_LOCALIZATION_PREREGISTRATION_REVIEW_2026-09-17.json'
UNSEEN=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_L3_WL3_UNSEEN_PARTITION_RELATION_RESULT_2026-09-17.json'
SOURCE=ROOT/'research/source_data/SATLIB_UF20_06_2026-09-17.cnf'
EXPECTED={PREREG:'21d3f7ceb52caff3ba0b5a3378942c811ddd9c86',REVIEW:'0e1a98ff1a469f1b62b99b2caf9e35b9e936279d',UNSEEN:'222d227e491df0a4ff03257d3f52a6e8be3cb6d9',SOURCE:'42d6feffa98dc1a213e019f28cf6bc7ddf94c0bf'}
CUBE=tuple(itertools.product((0,1),repeat=3))
REL_ORDER=('111','110','101','100','011','010','001','000')
LEVELS=('S0','S1','S2','S3')
COMPONENTS=('degree','positive_literal_count','negative_literal_count','eight_relation_incidence_vector','sorted_neighbor_degrees')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(obj:Any)->str:return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(path:Path):
 clauses=[];header=None
 for raw in path.read_text().splitlines():
  s=raw.strip()
  if not s or s.startswith('c') or s in ('%','0'):continue
  if s.startswith('p '):
   x=s.split();assert x[:2]==['p','cnf'] and len(x)==4;header=(int(x[2]),int(x[3]));continue
  vals=[int(x) for x in s.split()];assert vals[-1]==0 and len(vals)==4;clause=tuple(vals[:-1]);assert len({abs(x) for x in clause})==3;clauses.append(clause)
 assert header==(20,91) and len(clauses)==91;return clauses
def formula_sha(clauses):return hashlib.sha256(''.join(' '.join(map(str,c))+' 0\n' for c in clauses).encode('ascii')).hexdigest()
def rid(clause):return ''.join('0' if lit>0 else '1' for lit in sorted(clause,key=lambda x:abs(x)))
def allowed_for_clause(clause):
 scope=sorted(abs(x) for x in clause);out=[]
 for bits in CUBE:
  a=dict(zip(scope,bits))
  if any((a[abs(l)]==1) if l>0 else (a[abs(l)]==0) for l in clause):out.append(list(bits))
 return out
def projected_raw(clauses):
 selected=[(i,c) for i,c in enumerate(clauses,1) if rid(c) in {'000','111'}];V=sorted({abs(l) for _,c in selected for l in c});rows=[]
 for ordinal,c in selected:rows.append({'id':f'satlib_uf20_06_c{ordinal:03d}','scope':sorted(abs(x) for x in c),'allowed':sorted(allowed_for_clause(c))})
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
def l3_partition(V,selected):
 edges=[tuple(sorted(abs(x) for x in clause)) for _,clause in selected];nodes=[('v',v) for v in V]+[('c',i) for i in range(len(edges))];nbr={n:[] for n in nodes}
 for i,e in enumerate(edges):
  c=('c',i)
  for v in e:x=('v',v);nbr[c].append(x);nbr[x].append(c)
 color={n:(('VAR',) if n[0]=='v' else ('CORE_CONSTRAINT',)) for n in nodes}
 for _ in range(3):old=color;color={n:(old[n],tuple(sorted(old[m] for m in nbr[n]))) for n in nodes}
 sig={v:color[('v',v)] for v in V};groups=defaultdict(list)
 for v in sorted(sig):groups[json.dumps(sig[v],sort_keys=True,separators=(',',':'))].append(v)
 out=[sorted(x) for x in groups.values()];out.sort(key=lambda x:(x[0],len(x),x));return out
def serialize(value):
 if isinstance(value,tuple):return [serialize(x) for x in value]
 return value
def components(s3):return {'degree':s3[0],'positive_literal_count':s3[1],'negative_literal_count':s3[2],'eight_relation_incidence_vector':list(s3[3]),'sorted_neighbor_degrees':list(s3[4])}
def first_split(values):
 for level in LEVELS:
  if values['12'][level]!=values['16'][level]:return level
 return None
def expected_payload():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());unseen=json.loads(UNSEEN.read_text());assert pre['status']=='FROZEN_BEFORE_ANY_TARGET_SIGNATURE_VALUE_RECOMPUTATION';assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 clauses=parse(SOURCE);assert formula_sha(clauses)==pre['pinned_authorities']['UF20_06_source']['canonical_formula_sha256'];raw,selected=projected_raw(clauses);assert csha(raw)==pre['pinned_authorities']['UF20_06_projected_raw_sha256'];receipt=next(r for r in unseen['source_receipts'] if r['source']=='UF20_06');assert receipt['L3_partition']==[[1],[3],[4],[5],[6],[7],[8],[9],[10],[11],[12,16],[13],[14],[15],[17],[18],[19],[20]] and receipt['relation']=='S3_STRICTLY_FINER_THAN_L3'
 feats=existing_signatures(raw,selected);values={str(v):{level:serialize(feats[v][level]) for level in LEVELS} for v in (12,16)};l3=l3_partition(raw['variables'],selected);assert next(c for c in l3 if 12 in c)==[12,16] and next(c for c in l3 if 16 in c)==[12,16]
 comp={str(v):components(feats[v]['S3']) for v in (12,16)};eq={name:comp['12'][name]==comp['16'][name] for name in COMPONENTS};split=first_split(values);assert split is not None
 stage_components={'S0':['degree'],'S1':['degree','positive_literal_count','negative_literal_count'],'S2':['degree','positive_literal_count','negative_literal_count','eight_relation_incidence_vector'],'S3':list(COMPONENTS)}[split]
 prev=[] if split=='S0' else {'S1':['degree'],'S2':['degree','positive_literal_count','negative_literal_count'],'S3':['degree','positive_literal_count','negative_literal_count','eight_relation_incidence_vector']}[split]
 diff=[name for name in stage_components if not eq[name] and name not in prev] or [name for name in stage_components if not eq[name]]
 verdict={'S0':'FIRST_SPLIT_AT_S0_EXISTING_DEGREE_COMPONENT','S1':'FIRST_SPLIT_AT_S1_EXISTING_SIGN_COUNT_COMPONENTS','S2':'FIRST_SPLIT_AT_S2_EXISTING_RELATION_INCIDENCE_COMPONENT','S3':'FIRST_SPLIT_AT_S3_EXISTING_NEIGHBOR_DEGREE_COMPONENT'}[split]
 return raw,values,comp,eq,split,diff,verdict
def main(candidate_path:Path):
 assert all(blob(p)==sha for p,sha in EXPECTED.items()),{str(p):blob(p) for p in EXPECTED};candidate=json.loads(candidate_path.read_text().strip().splitlines()[-1]);raw,values,comp,eq,split,diff,verdict=expected_payload()
 assert candidate['projected_raw_sha256']==csha(raw);assert candidate['target_variables']==[12,16] and candidate['frozen_L3_class_verified']==[12,16];assert candidate['signature_values']==values;assert candidate['component_values']==comp;assert candidate['component_equalities']==eq;assert candidate['first_split_stage']==split;assert candidate['first_split_differing_existing_components']==diff;assert candidate['verdict']==verdict
 rr=candidate['resource_receipt'];assert rr['sources']==1 and rr['target_variables']==2 and rr['existing_signature_stages']==4 and rr['solver_invocations']==0 and rr['portfolio_replays']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['group_closure_computation']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0 and rr['new_solver_mechanisms']==0 and rr['new_carrier_mechanisms']==0 and rr['new_adapters']==0 and rr['new_quotients']==0 and rr['budget_raise'] is False
 sf=candidate['scientific_firewall'];assert sf['P_VS_NP']=='OPEN' and sf['GENERAL_SAT_IN_P']=='NOT_PROVED' and sf['CONNECTED_MIXED_CORE_SOLVED']=='NO' and sf['PAIR_12_16_AUTOMORPHISM_STATUS']=='NOT_TESTED_AND_NOT_AUTHORIZED_HERE'
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'first_split_stage':split,'first_split_differing_existing_components':diff,'signature_values':values,'component_values':comp,'component_equalities':eq}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);args=ap.parse_args();print(json.dumps(main(Path(args.candidate_json)),sort_keys=True,separators=(',',':')))
