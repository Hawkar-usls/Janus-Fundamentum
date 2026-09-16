from __future__ import annotations
import argparse, hashlib, itertools, json
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
RAW=ROOT/'research/source_data/SATLIB_UF20_01_RAW_2026-09-16.json'
SOURCE=ROOT/'research/source_data/SATLIB_UF20_01_2026-09-16.cnf'
PROFILE=ROOT/'research/tools/apma_satlib_uf20_01_missing_invariant_profile/profile.py'
EXPECTED_PROFILE_BLOB='0a87b50eea9260af4b6ab90e6484477023b9ea1e'

def blob(p):
 b=p.read_bytes();return hashlib.sha1(f'blob {len(b)}\0'.encode()+b).hexdigest()
def connected(nodes,adj):
 nodes=set(nodes)
 if len(nodes)<=1:return True
 q=[next(iter(nodes))];seen={q[0]}
 while q:
  u=q.pop()
  for v in adj[u]&nodes:
   if v not in seen:seen.add(v);q.append(v)
 return seen==nodes
def cut_counts(nodes,adj):
 out={};nodes=tuple(sorted(nodes))
 for k in range(1,5):
  n=0
  for cut in itertools.combinations(nodes,k):
   rem=set(nodes)-set(cut)
   if len(rem)>1 and not connected(rem,adj):n+=1
  out[str(k)]=n
 return out
def main(candidate):
 raw=json.loads(RAW.read_text());vars=raw['variables'];adj={v:set() for v in vars}
 for c in raw['constraints']:
  for u,v in itertools.combinations(c['scope'],2):adj[u].add(v);adj[v].add(u)
 edges=sum(map(len,adj.values()))//2;deg={v:len(adj[v]) for v in vars};cuts=cut_counts(vars,adj)
 overlap=Counter();o1={c['id']:set() for c in raw['constraints']};o2={c['id']:set() for c in raw['constraints']}
 for a,b in itertools.combinations(raw['constraints'],2):
  k=len(set(a['scope'])&set(b['scope']));overlap[k]+=1
  if k>=1:o1[a['id']].add(b['id']);o1[b['id']].add(a['id'])
  if k>=2:o2[a['id']].add(b['id']);o2[b['id']].add(a['id'])
 clauses=[]
 for line in SOURCE.read_text().splitlines():
  s=line.strip()
  if s and not s.startswith('c') and not s.startswith('p '):clauses.append(tuple(map(int,s.split()[:-1])))
 pos=Counter();neg=Counter()
 for cl in clauses:
  for lit in cl:(pos if lit>0 else neg)[abs(lit)]+=1
 keys=sorted({tuple(sorted(''.join(map(str,r)) for r in c['allowed'])) for c in raw['constraints']});idx={k:i for i,k in enumerate(keys)}
 vr={v:[0]*len(keys) for v in vars}
 for c in raw['constraints']:
  i=idx[tuple(sorted(''.join(map(str,r)) for r in c['allowed']))]
  for v in c['scope']:vr[v][i]+=1
 groups=defaultdict(list)
 for v in vars:
  sig=(deg[v],pos[v],neg[v],tuple(vr[v]),tuple(sorted(deg[n] for n in adj[v])))
  h=hashlib.sha256(json.dumps(sig,separators=(',',':')).encode()).hexdigest()[:16];groups[h].append(v)
 checks={
  'profile_source_guard':candidate.get('source_guard',{}).get('ok') is True,
  'profile_blob_bound':blob(PROFILE)==EXPECTED_PROFILE_BLOB,
  'verdict':candidate.get('verdict')=='PASS_DIAGNOSTIC_PROFILE_FROZEN_OBSTRUCTION',
  'primal_edges':candidate['P1_primal']['edges']==edges,
  'degree_bounds':candidate['P1_primal']['degree_min']==min(deg.values()) and candidate['P1_primal']['degree_max']==max(deg.values()),
  'primal_cut_counts':candidate['P1_primal']['cut_counts']==cuts,
  'overlap_counts':candidate['P3_overlap']['pair_intersection_counts']=={str(k):overlap[k] for k in sorted(overlap)},
  'overlap_ge1_connectivity':candidate['P3_overlap']['graph_ge1_connected']==connected(o1,o1),
  'overlap_ge2_connectivity':candidate['P3_overlap']['graph_ge2_connected']==connected(o2,o2),
  'relation_surface_count':candidate['P4_local_mixing']['relation_surface_count']==8,
  'signature_count':candidate['P5_variable_signature']['distinct_signature_count']==len(groups),
  'signature_groups':candidate['P5_variable_signature']['signature_groups']==dict(sorted(groups.items())),
  'p_vs_np_open':candidate['scientific_firewall']['P_VS_NP']=='OPEN',
  'general_sat_not_proved':candidate['scientific_firewall']['GENERAL_SAT_IN_P']=='NOT_PROVED',
  'no_new_solver':candidate['scientific_firewall']['NEW_SOLVER_MECHANISMS']==0,
 }
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-01-MISSING-INVARIANT-PROFILE-INDEPENDENT-CHECK-2026-09-16-v1.0','authority':'INDEPENDENT_DIAGNOSTIC_CHECK_ONLY','verified':all(checks.values()),'checks':checks,'profile_imported':False,'independent_receipt':{'primal_edges':edges,'degree_min':min(deg.values()),'degree_max':max(deg.values()),'cut_counts_le4':cuts,'relation_surface_count':len(keys),'distinct_signature_count':len(groups)}}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--profile-json',required=True);a=ap.parse_args();c=json.loads(Path(a.profile_json).read_text().strip().splitlines()[-1]);print(json.dumps(main(c),sort_keys=True))
