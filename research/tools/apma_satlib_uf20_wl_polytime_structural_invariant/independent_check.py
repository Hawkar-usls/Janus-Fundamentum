from __future__ import annotations
import argparse,hashlib,itertools,json
from collections import Counter,defaultdict
from pathlib import Path
from typing import Any
from research.tools.apma_satlib_uf20_r000_r111_projected_core_replay import projection_identity

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_UF20_02_04_05_WL_POLYTIME_STRUCTURAL_INVARIANT_PREREGISTRATION_2026-09-17_v1.0.json';REVIEW=ROOT/'research/TRUMP_UF20_02_04_05_WL_POLYTIME_STRUCTURAL_INVARIANT_REVIEW_2026-09-17_v1.0.json';REDUCTION=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_RAW_BOUND_PENDANT_EXACT_SIMULTANEOUS_ONE_ROUND_REDUCTION_RESULT_2026-09-17_v1.1.json';PROJECTION=ROOT/'research/tools/apma_satlib_uf20_r000_r111_projected_core_replay/projection_identity.py'
EXPECTED={PREREG:'6a33cd37bddf04445500b9c94bcd806d65c95c20',REVIEW:'4d09c3fa773e9ec17c38f5388795906541eefcf3',REDUCTION:'d91cb675e3d06fed92f97d96d6b3a0733f8be5df',PROJECTION:'2ef48e73974a5f43d3f4fb4809ebd0c09c0f5be4'}
SOURCES={'UF20_02':(ROOT/'research/source_data/SATLIB_UF20_02_2026-09-16.cnf','f924caaef0d868bf62b1658e83e030ad8daee865'),'UF20_03':(ROOT/'research/source_data/SATLIB_UF20_03_2026-09-16.cnf','8f3d15154515457281f49201b843f2a7134dfa9f'),'UF20_04':(ROOT/'research/source_data/SATLIB_UF20_04_2026-09-16.cnf','34ced5c169f967b2dc44ef5e42f2ee2c924813e1'),'UF20_05':(ROOT/'research/source_data/SATLIB_UF20_05_2026-09-16.cnf','3b04eff26ee37bdd0bc21b1066486974f92a2c9b')}
ORDER=('UF20_02','UF20_03','UF20_04','UF20_05');BLOCKERS=('UF20_02','UF20_04','UF20_05');FEATURES=('WL1_MAX_VARIABLE_COLOR_CLASS_SIZE','WL1_VARIABLE_COLOR_CLASS_SIZE_MULTISET','WL1_VARIABLE_PARTITION_IS_DISCRETE','WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE','WL2_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE_MULTISET','WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE')

def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def csha(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def local(c):return f"a{len(c['scope'])}:"+'/'.join(sorted(''.join(str(int(b)) for b in r) for r in c['allowed']))
def key(n):return(n[0],str(n[1]))
def canonical(sig):
 vals=sorted(set(sig.values()),key=repr);idx={v:i for i,v in enumerate(vals)};return{k:idx[v] for k,v in sig.items()}
def make(raw):
 adj=defaultdict(set);labels={};nodes=[]
 for v in sorted(map(int,raw['variables'])):n=('v',v);nodes.append(n);labels[n]='V';adj[n]
 for c in raw['constraints']:
  n=('c',str(c['id']));nodes.append(n);labels[n]='C:'+local(c);adj[n]
  for v in sorted(set(map(int,c['scope']))):u=('v',v);adj[n].add(u);adj[u].add(n)
 return sorted(nodes,key=key),adj,labels
def refine1(nodes,adj,labels):
 colors=canonical({n:(labels[n],) for n in nodes});rounds=0
 while True:
  nxt=canonical({n:(colors[n],tuple(sorted(colors[x] for x in adj[n]))) for n in nodes});rounds+=1
  if len(set(nxt.values()))==len(set(colors.values())):return nxt,rounds
  colors=nxt
def refine2(nodes,adj,labels):
 vc=canonical({n:(labels[n],) for n in nodes});pairs=[(u,v) for u in nodes for v in nodes];colors=canonical({(u,v):(vc[u],vc[v],int(u==v),int(v in adj[u])) for u,v in pairs});rounds=0
 while True:
  nxt={}
  for u,v in pairs:nxt[(u,v)]=(colors[(u,v)],tuple(sorted((colors[(u,w)],colors[(w,v)]) for w in nodes)))
  nxt=canonical(nxt);rounds+=1
  if len(set(nxt.values()))==len(set(colors.values())):return nxt,rounds
  colors=nxt
def sizes(colors,ks):return sorted(Counter(colors[k] for k in ks).values())
def reconstruct():
 rec={r['source']:r for r in json.loads(REDUCTION.read_text())['source_receipts']};out={};guards={}
 for s in ORDER:
  p,eb=SOURCES[s];orig,_=projection_identity.normalize_projection(s,projection_identity.parse(p));r=rec[s];ids=set(r['removed_constraint_ids']);leaves=set(map(int,r['removed_leaves']));red={'variables':[int(v) for v in orig['variables'] if int(v) not in leaves],'constraints':[c for c in orig['constraints'] if c['id'] not in ids]};g={'source_blob_ok':blob(p)==eb,'original_sha_ok':csha(orig)==r['original_projected_raw']['sha256'],'reduced_sha_ok':csha(red)==r['reduced_raw']['sha256'],'variable_count_ok':len(red['variables'])==r['reduced_raw']['variables'],'constraint_count_ok':len(red['constraints'])==r['reduced_raw']['constraints']};g['all_ok']=all(g.values());assert g['all_ok'];out[s]=red;guards[s]=g
 return out,guards
def profile(raw):
 nodes,adj,labels=make(raw);vs=[x for x in nodes if x[0]=='v'];a,r1=refine1(nodes,adj,labels);b,r2=refine2(nodes,adj,labels);x=sizes(a,vs);y=sizes(b,[(v,v) for v in vs]);return{'WL1_MAX_VARIABLE_COLOR_CLASS_SIZE':max(x),'WL1_VARIABLE_COLOR_CLASS_SIZE_MULTISET':x,'WL1_VARIABLE_PARTITION_IS_DISCRETE':all(z==1 for z in x),'WL2_MAX_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE':max(y),'WL2_VARIABLE_DIAGONAL_COLOR_CLASS_SIZE_MULTISET':y,'WL2_VARIABLE_DIAGONAL_PARTITION_IS_DISCRETE':all(z==1 for z in y),'_receipt':{'incidence_vertex_count':len(nodes),'incidence_edge_count':sum(len(adj[n]) for n in nodes)//2,'wl1_rounds':r1,'wl2_rounds':r2}}
def main(path):
 cand=json.loads(path.read_text());bindings={str(p.relative_to(ROOT)):blob(p)==h for p,h in EXPECTED.items()};raws,guards=reconstruct();rows={s:profile(raws[s]) for s in ORDER};chosen=[]
 for f in FEATURES:
  x=[rows[s][f] for s in BLOCKERS]
  if x[0]==x[1]==x[2] and x[0]!=rows['UF20_03'][f]:chosen.append(f)
 chosen.sort();expected='WL_POLYTIME_COMMON_INVARIANT_CANDIDATE_SET_FOUND__BLIND_FALSIFIER_REQUIRED' if chosen else 'NO_WL_COMMON_INVARIANT_FOUND_ON_FROZEN_FIXED_DIMENSION_BASIS'
 checks={'authority_bindings':all(bindings.values()),'identity_guards':all(g['all_ok'] for g in guards.values()),'feature_rows_exact':cand.get('feature_rows')==rows,'candidate_set_exact':cand.get('candidate_invariant_set')==chosen,'verdict_exact':cand.get('verdict')==expected,'historical_controls_unread':cand.get('blindness_receipt',{}).get('historical_control_wl_values_read_or_computed')==0,'holdouts_unread':cand.get('blindness_receipt',{}).get('fresh_holdout_wl_values_read_or_computed')==0,'no_solver_or_group_search':cand.get('resource_receipt',{}).get('solver_invocations')==0 and cand.get('resource_receipt',{}).get('automorphism_or_group_searches')==0,'firewall':cand.get('scientific_firewall',{}).get('P_VS_NP')=='OPEN' and cand.get('scientific_firewall',{}).get('GENERAL_SAT_IN_P')=='NOT_PROVED'}
 return{'artifact_id':'JANUS-TRUMP-UF20-WL-POLYTIME-INVARIANT-INDEPENDENT-CHECK-2026-09-17-v1.0','verdict':'PASS_INDEPENDENT_WL_VERIFICATION' if all(checks.values()) else 'FAIL_INDEPENDENT_WL_VERIFICATION','checks':checks,'independent_feature_rows':rows,'independent_candidate_invariant_set':chosen,'expected_candidate_verdict':expected,'candidate_imported':False,'historical_control_wl_values_read_or_computed':0,'fresh_holdout_wl_values_read_or_computed':0,'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED'}}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate',required=True);a=ap.parse_args();r=main(Path(a.candidate));print(json.dumps(r,sort_keys=True,separators=(',',':')));raise SystemExit(0 if r['verdict'].startswith('PASS_') else 1)
