from __future__ import annotations
import hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any
from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_UF20_02_04_05_WL_POLYTIME_STRUCTURAL_INVARIANT_PREREGISTRATION_2026-09-17_v1.0.json'
REVIEW=ROOT/'research/TRUMP_UF20_02_04_05_WL_POLYTIME_STRUCTURAL_INVARIANT_REVIEW_2026-09-17_v1.0.json'
REDUCTION=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17_v1.1.json'
PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
EXPECTED={PREREG:'6a33cd37bddf04445500b9c94bcd806d65c95c20',REVIEW:'4d09c3fa773e9ec17c38f5388795906541eefcf3',REDUCTION:'d91cb675e3d06fed92f97d96d6b3a0733f8be5df',PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
SOURCES={
'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),
'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),
'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),
'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05');BLOCKERS=('UF20_02','UF20_04','UF20_05');CONTROL='UF20_03'
FEATURES=('WL1_MAX_VARIABLE_COLOR_CLASS_SIZE','WL1_VARIABLE_COLOR_CLASS_SIZE_MULTISET','WL1_VARIABLE_PARTITION_IS_DISCRETE','WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE','WL2_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE_MULTISET','WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE')

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(o:Any)->str:return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def rsig(c):
 rows=sorted(''.join(str(int(b)) for b in row) for row in c['allowed']);return f"a{len(c['scope'])}:"+'/'.join(rows)
def nkey(x):return (x[0],str(x[1]))
def rank(signatures):
 uniq=sorted(set(signatures.values()),key=repr);m={s:i for i,s in enumerate(uniq)};return {k:m[v] for k,v in signatures.items()}
def structure(raw):
 nodes=[];adj=defaultdict(set);labels={}
 for v in sorted(int(x) for x in raw['variables']):
  n=('v',v);nodes.append(n);labels[n]='V';adj[n]
 for c in raw['constraints']:
  n=('c',str(c['id']));nodes.append(n);labels[n]='C:'+rsig(c);adj[n]
  for v in sorted({int(x) for x in c['scope']}):
   u=('v',v);adj[n].add(u);adj[u].add(n)
 nodes=sorted(nodes,key=nkey);return nodes,adj,labels
def wl1(nodes,adj,labels):
 colors=rank({n:(labels[n],) for n in nodes});rounds=0
 while True:
  sig={n:(colors[n],tuple(sorted(colors[x] for x in adj[n]))) for n in nodes};new=rank(sig);rounds+=1
  if len(set(new.values()))==len(set(colors.values())):return new,rounds
  colors=new
def wl2(nodes,adj,labels):
 vcolors=rank({n:(labels[n],) for n in nodes});pairs=list(itertools.product(nodes,nodes))
 init={(u,v):(vcolors[u],vcolors[v],int(u==v),int(v in adj[u])) for u,v in pairs};colors=rank(init);rounds=0
 while True:
  sig={}
  for u,v in pairs:
   mult=tuple(sorted((colors[(u,w)],colors[(w,v)]) for w in nodes))
   sig[(u,v)]=(colors[(u,v)],mult)
  new=rank(sig);rounds+=1
  if len(set(new.values()))==len(set(colors.values())):return new,rounds
  colors=new
def class_sizes(color_map,keys):
 c=Counter(color_map[k] for k in keys);return sorted(c.values())
def reconstruct():
 result=json.loads(REDUCTION.read_text());receipts={r['source']:r for r in result['source_receipts']};raws={};guards={}
 for s in ORDER:
  path,eb=SOURCES[s];orig,_=projection_identity.normalize_projection(s,projection_identity.parse(path));r=receipts[s]
  rmids=set(r['removed_constraint_ids']);rmv={int(x) for x in r['removed_leaves']};red={'variables':[int(v) for v in orig['variables'] if int(v) not in rmv],'constraints':[c for c in orig['constraints'] if c['id'] not in rmids]}
  g={'source_blob_ok':blob(path)==eb,'original_sha_ok':csha(orig)==r['original_projected_raw']['sha256'],'reduced_sha_ok':csha(red)==r['reduced_raw']['sha256'],'variable_count_ok':len(red['variables'])==r['reduced_raw']['variables'],'constraint_count_ok':len(red['constraints'])==r['reduced_raw']['constraints']};g['all_ok']=all(g.values())
  if not g['all_ok']:raise RuntimeError((s,g));raws[s]=red;guards[s]=g
  raws[s]=red;guards[s]=g
 return raws,guards
def profile(raw):
 nodes,adj,labels=structure(raw);vars=[n for n in nodes if n[0]=='v'];c1,r1=wl1(nodes,adj,labels);c2,r2=wl2(nodes,adj,labels);s1=class_sizes(c1,vars);s2=class_sizes(c2,[(v,v) for v in vars])
 return {'WL1_VARIABLE_COLOR_CLASS_SIZE_MULTISET':s1,'WL1_VARIABLE_PARTITION_IS_DISCRETE':all(x==1 for x in s1),'WL1_MAX_VARIABLE_COLOR_CLASS_SIZE':max(s1),'WL2_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE_MULTISET':s2,'WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE':all(x==1 for x in s2),'WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE':max(s2),'_receipt':{'incidence_vertex_count':len(nodes),'incidence_edge_count':sum(len(adj[n]) for n in nodes)//2,'wl1_rounds':r1,'wl2_rounds':r2}}
def main():
 binds={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()}
 if not all(binds.values()):return {'verdict':'FAIL_AUTHORITY_BINDING','authority_bindings':binds}
 if json.loads(REVIEW.read_text()).get('review_verdict')!='PASS_CLEAN_WL_SPECIFICATION__AUTHORIZED_TO_IMPLEMENT_ONCE':return {'verdict':'FAIL_REVIEW_NOT_AUTHORIZED'}
 raws,guards=reconstruct();rows={s:profile(raws[s]) for s in ORDER};cand=[]
 for f in FEATURES:
  vals=[rows[s][f] for s in BLOCKERS]
  if vals[0]==vals[1]==vals[2] and vals[0]!=rows[CONTROL][f]:cand.append(f)
 cand.sort();verdict='WL_POLYTIME_COMMON_INVARIANT_CANDIDATE_SET_FOUND__BLIND_FALSIFIER_REQUIRED' if cand else 'NO_WL_COMMON_INVARIANT_FOUND_ON_FROZEN_FIXED_DIMENSION_BASIS'
 return {'artifact_id':'JANUS-TRUMP-UF20-02-04-05-WL-POLYTIME-STRUCTURAL-INVARIANT-CANDIDATE-2026-09-17-v1.0','verdict':verdict,'authority_bindings':binds,'identity_guards':guards,'feature_rows':rows,'candidate_invariant_set':cand,'frozen_feature_names':list(FEATURES),'blindness_receipt':{'historical_control_wl_values_read_or_computed':0,'fresh_holdout_wl_values_read_or_computed':0,'posthoc_thresholds_tested':0,'feature_combinations_tested':0},'resource_receipt':{'solver_invocations':0,'automorphism_or_group_searches':0,'new_solver_rules':0,'new_action_rules':0,'new_carrier_mechanisms':0,'new_reduction_mechanisms':0},'complexity_receipt':{'wl1':'POLYNOMIAL_FIXED_COLOR_REFINEMENT','wl2':'POLYNOMIAL_FIXED_DIMENSION_2_WL'},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY':'NOT_PROVED'}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
