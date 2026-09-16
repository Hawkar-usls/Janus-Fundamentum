from __future__ import annotations

import argparse,hashlib,json
from collections import defaultdict,deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_DELETION_DEPENDENCY_AUDIT_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_DELETION_DEPENDENCY_AUDIT_PREREGISTRATION_REVIEW_2026-09-17.json'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17_v1.1.json'
SOURCE_ORDER={'UF20_02':0,'UF20_03':1,'UF20_04':2,'UF20_05':3}

def blob(p):
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def key(n):return (SOURCE_ORDER[n['source']],n['constraint_id'],int(n['leaf_variable']))
def nid(n):return f"{n['source']}::{n['constraint_id']}::leaf={int(n['leaf_variable'])}"
def nodes_from_parent(p):
 out=[]
 for sr in p['source_receipts']:
  for a in sr['attachments']:
   out.append({'source':sr['source'],'constraint_id':a['constraint_id'],'leaf_variable':int(a['leaf_variable']),'gateway_order':[int(x) for x in a['gateway_order']],'leaf_projected_constraint_occurrence_count':int(a['leaf_projected_constraint_occurrence_count'])})
 return sorted(out,key=key)
def build_edges(nodes):
 idx=defaultdict(list)
 for n in nodes:idx[(n['source'],n['leaf_variable'])].append(nid(n))
 byid={nid(n):n for n in nodes};order={nid(n):key(n) for n in nodes};edges=set()
 for a in nodes:
  for g in a['gateway_order']:
   for b in idx.get((a['source'],g),[]):
    if b!=nid(a):edges.add((nid(a),b))
 return sorted(edges,key=lambda e:(order[e[0]],order[e[1]])),byid,order
def weak(ids,edges,order):
 g={x:set() for x in ids}
 for a,b in edges:g[a].add(b);g[b].add(a)
 unseen=set(ids);ans=[]
 while unseen:
  s=min(unseen,key=lambda x:order[x]);q=[s];unseen.remove(s);c=[]
  while q:
   u=q.pop(0);c.append(u)
   for v in sorted(g[u],key=lambda x:order[x]):
    if v in unseen:unseen.remove(v);q.append(v)
  ans.append(sorted(c,key=lambda x:order[x]))
 return sorted(ans,key=lambda c:order[c[0]])
def topo(ids,edges,order):
 g=defaultdict(list);ind={x:0 for x in ids}
 for a,b in edges:g[a].append(b);ind[b]+=1
 ready=sorted([x for x in ids if ind[x]==0],key=lambda x:order[x]);out=[]
 while ready:
  u=ready.pop(0);out.append(u)
  for v in sorted(g[u],key=lambda x:order[x]):
   ind[v]-=1
   if ind[v]==0:ready.append(v);ready.sort(key=lambda x:order[x])
 return out if len(out)==len(ids) else None
def has_path(start,target,g):
 q=deque([start]);seen={start}
 while q:
  u=q.popleft()
  for v in g[u]:
   if v==target:return True
   if v not in seen:seen.add(v);q.append(v)
 return False
def cycle_receipts(ids,edges,order):
 g={x:[] for x in ids}
 for a,b in edges:g[a].append(b)
 for u in g:g[u].sort(key=lambda x:order[x])
 # independent cycle certificate: each edge a->b is cyclic iff b reaches a; return cyclic edges only.
 cyclic_edges=[]
 for a,b in edges:
  if has_path(b,a,g):cyclic_edges.append([a,b])
 return cyclic_edges
def main(path):
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());parent=json.loads(PARENT.read_text())
 assert pre['status']=='FROZEN_BEFORE_ANY_INTER_ATTACHMENT_DEPENDENCY_VALUE_COMPUTATION'
 assert review['verdict']=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE'
 assert parent['status']=='FROZEN_REPAIRED_EXECUTION_SCIENTIFIC_RESULT' and parent['verdict']=='ALL_ELEVEN_UNIVERSAL'
 assert parent['execution']['conclusion']=='success' and parent['execution']['independent_verified'] is True
 cand=json.loads(Path(path).read_text().strip().splitlines()[-1]);nodes=nodes_from_parent(parent);assert len(nodes)==11
 edges,byid,order=build_edges(nodes);ids=[nid(n) for n in nodes];ind={x:0 for x in ids};outd={x:0 for x in ids}
 for a,b in edges:outd[a]+=1;ind[b]+=1
 t=topo(ids,edges,order);acyclic=t is not None;cyclic_edges=cycle_receipts(ids,edges,order)
 if not edges:verdict='NO_INTER_ATTACHMENT_DEPENDENCIES'
 elif acyclic:verdict='ACYCLIC_INTER_ATTACHMENT_DEPENDENCIES'
 else:verdict='CYCLIC_INTER_ATTACHMENT_DEPENDENCIES'
 assert cand['verdict']==verdict;assert cand['node_count']==11;assert cand['edge_count']==len(edges);assert cand['directed_edges']==[list(e) for e in edges];assert cand['acyclic']==acyclic
 assert cand['topological_elimination_order']==(t if acyclic else None);assert cand['reverse_reconstruction_order']==(list(reversed(t)) if acyclic else None)
 # verify per-source graph receipts independently
 for row in cand['per_source']:
  src=row['source'];sids=[x for x in ids if byid[x]['source']==src];sedges=[e for e in edges if byid[e[0]]['source']==src]
  assert row['directed_edges']==[list(e) for e in sedges];assert row['edge_count']==len(sedges);assert row['weak_components']==weak(sids,sedges,order)
  for nr in row['nodes']:
   x=nr['node_id'];assert nr['indegree']==ind[x] and nr['outdegree']==outd[x]
 # candidate may enumerate explicit simple cycles; independently require exact cycle presence/absence consistency.
 assert bool(cand['directed_cycles'])==bool(cyclic_edges)
 theorem=cand['composition_theorem'];unique=all(n['leaf_projected_constraint_occurrence_count']==1 for n in nodes)
 assert theorem['applicable']==acyclic and theorem['parent_single_attachment_projection_theorem_verified'] is True and theorem['all_target_leaf_unique_occurrence_receipts_verified']==unique and theorem['composition_argument_verified']==(acyclic and unique)
 assert theorem['deletion_applied'] is False and theorem['simultaneous_deletion_applied'] is False
 rr=cand['resource_receipt'];assert rr['nodes']==11 and rr['boundary_relation_recomputations']==0 and rr['attachment_deletions']==0 and rr['projected_raw_modifications']==0 and rr['fresh_holdout_values_read']==0 and rr['solver_invocations']==0 and rr['component_solution_attempts']==0 and rr['action_tests']==0 and rr['automorphism_tests']==0 and rr['group_searches']==0 and rr['new_feature_definitions']==0 and rr['new_graph_statistics']==0
 return {'verified':True,'candidate_imported':False,'verdict':verdict,'node_count':11,'edge_count':len(edges),'directed_edges':[list(e) for e in edges],'acyclic':acyclic,'topological_elimination_order':t if acyclic else None,'reverse_reconstruction_order':list(reversed(t)) if acyclic else None,'cyclic_edge_certificate':cyclic_edges,'unique_leaf_occurrence_verified':unique,'preregistration_blob':blob(PREREG),'review_blob':blob(REVIEW),'parent_boundary_result_blob':blob(PARENT),'fresh_holdout_values_read':0,'boundary_relation_recomputations':0,'deletion_applied':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--candidate-json',required=True);a=ap.parse_args();print(json.dumps(main(a.candidate_json),sort_keys=True,separators=(',',':')))
