from __future__ import annotations

import hashlib,json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[3]
PREREG=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_DELETION_DEPENDENCY_AUDIT_PREREGISTRATION_2026-09-17.json'
REVIEW=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_DELETION_DEPENDENCY_AUDIT_PREREGISTRATION_REVIEW_2026-09-17.json'
PARENT=ROOT/'research/TRUMP_SATLIB_UF20_R000_R111_PENDANT_SINGLETON_EXISTENTIAL_BOUNDARY_PROJECTION_RESULT_2026-09-17_v1.1.json'
SOURCE_ORDER={'UF20_02':0,'UF20_03':1,'UF20_04':2,'UF20_05':3}

def blob(p:Path)->str:
 d=p.read_bytes();return hashlib.sha1(f'blob {len(d)}\0'.encode()+d).hexdigest()
def node_key(n:dict[str,Any]):return (SOURCE_ORDER[n['source']],n['constraint_id'],int(n['leaf_variable']))
def node_id(n):return f"{n['source']}::{n['constraint_id']}::leaf={int(n['leaf_variable'])}"
def load_nodes(parent):
 nodes=[]
 for sr in parent['source_receipts']:
  src=sr['source']
  for a in sr['attachments']:
   nodes.append({'source':src,'constraint_id':a['constraint_id'],'leaf_variable':int(a['leaf_variable']),'gateway_order':[int(x) for x in a['gateway_order']],'leaf_projected_constraint_occurrence_count':int(a['leaf_projected_constraint_occurrence_count'])})
 nodes.sort(key=node_key);return nodes
def weak_components(ids,edges,keymap):
 adj={x:set() for x in ids}
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 unseen=set(ids);out=[]
 while unseen:
  s=min(unseen,key=lambda x:keymap[x]);unseen.remove(s);stack=[s];c={s}
  while stack:
   u=stack.pop()
   for v in sorted(adj[u],key=lambda x:keymap[x]):
    if v in unseen:unseen.remove(v);c.add(v);stack.append(v)
  out.append(sorted(c,key=lambda x:keymap[x]))
 out.sort(key=lambda c:keymap[c[0]]);return out
def cycles_canonical(ids,edges,keymap):
 adj={x:[] for x in ids}
 for a,b in edges:adj[a].append(b)
 for a in adj:adj[a].sort(key=lambda x:keymap[x])
 cycles=set()
 for start in sorted(ids,key=lambda x:keymap[x]):
  stack=[(start,[start],{start})]
  while stack:
   u,path,seen=stack.pop()
   for v in reversed(adj[u]):
    if v==start and len(path)>1:
     cyc=path[:]
     rots=[tuple(cyc[i:]+cyc[:i]) for i in range(len(cyc))]
     cycles.add(min(rots,key=lambda r:tuple(keymap[x] for x in r)))
    elif v not in seen and keymap[v]>=keymap[start]:
     stack.append((v,path+[v],seen|{v}))
 return [list(c) for c in sorted(cycles,key=lambda c:tuple(keymap[x] for x in c))]
def kahn(ids,edges,keymap):
 indeg={x:0 for x in ids};out=defaultdict(list)
 for a,b in edges:out[a].append(b);indeg[b]+=1
 for a in out:out[a].sort(key=lambda x:keymap[x])
 ready=sorted([x for x in ids if indeg[x]==0],key=lambda x:keymap[x]);order=[]
 while ready:
  u=ready.pop(0);order.append(u)
  for v in out[u]:
   indeg[v]-=1
   if indeg[v]==0:
    ready.append(v);ready.sort(key=lambda x:keymap[x])
 return order if len(order)==len(ids) else None
def main():
 pre=json.loads(PREREG.read_text());review=json.loads(REVIEW.read_text());parent=json.loads(PARENT.read_text())
 guards={'prereg_status':pre.get('status')=='FROZEN_BEFORE_ANY_INTER_ATTACHMENT_DEPENDENCY_VALUE_COMPUTATION','review_authorized':review.get('verdict')=='PASS_PREREGISTRATION_CLEAN__AUTHORIZED_TO_IMPLEMENT_AND_EXECUTE_ONCE','parent_status':parent.get('status')=='FROZEN_REPAIRED_EXECUTION_SCIENTIFIC_RESULT','parent_verdict':parent.get('verdict')=='ALL_ELEVEN_UNIVERSAL','parent_execution_verified':parent.get('execution',{}).get('conclusion')=='success' and parent.get('execution',{}).get('independent_verified') is True,'parent_theorem_verified':parent.get('local_semantics_theorem',{}).get('symbolic_projection_equivalence_verified') is True}
 if not all(guards.values()):return {'verdict':'HALT_FROZEN_AUTHORITY_BINDING_FAILURE','guards':guards}
 nodes=load_nodes(parent);assert len(nodes)==11
 ids=[node_id(n) for n in nodes];byid={node_id(n):n for n in nodes};keymap={node_id(n):node_key(n) for n in nodes};by_source_leaf=defaultdict(list)
 for n in nodes:by_source_leaf[(n['source'],n['leaf_variable'])].append(node_id(n))
 edges=[]
 for a in nodes:
  aid=node_id(a)
  for gv in a['gateway_order']:
   for bid in by_source_leaf.get((a['source'],gv),[]):
    if bid!=aid:edges.append((aid,bid))
 edges=sorted(set(edges),key=lambda e:(keymap[e[0]],keymap[e[1]]))
 indeg={x:0 for x in ids};outdeg={x:0 for x in ids}
 for a,b in edges:outdeg[a]+=1;indeg[b]+=1
 cycles=cycles_canonical(ids,edges,keymap);topo=kahn(ids,edges,keymap);acyclic=topo is not None
 per_source=[]
 for src in sorted(SOURCE_ORDER,key=lambda s:SOURCE_ORDER[s]):
  sids=[x for x in ids if byid[x]['source']==src];sedges=[list(e) for e in edges if byid[e[0]]['source']==src]
  per_source.append({'source':src,'nodes':[byid[x] | {'node_id':x,'indegree':indeg[x],'outdegree':outdeg[x]} for x in sids],'directed_edges':sedges,'edge_count':len(sedges),'weak_components':weak_components(sids,[tuple(e) for e in sedges],keymap),'directed_cycles':[c for c in cycles if c and byid[c[0]]['source']==src]})
 if not edges:verdict='NO_INTER_ATTACHMENT_DEPENDENCIES'
 elif acyclic:verdict='ACYCLIC_INTER_ATTACHMENT_DEPENDENCIES'
 else:verdict='CYCLIC_INTER_ATTACHMENT_DEPENDENCIES'
 theorem={'applicable':acyclic,'parent_single_attachment_projection_theorem_verified':True,'all_target_leaf_unique_occurrence_receipts_verified':all(n['leaf_projected_constraint_occurrence_count']==1 for n in nodes),'topological_elimination_order':topo if acyclic else None,'reverse_topological_reconstruction_order':list(reversed(topo)) if acyclic else None,'composition_argument_verified':acyclic and all(n['leaf_projected_constraint_occurrence_count']==1 for n in nodes),'deletion_applied':False,'simultaneous_deletion_applied':False}
 return {'artifact_id':'JANUS-TRUMP-SATLIB-UF20-R000-R111-PENDANT-SINGLETON-DELETION-DEPENDENCY-AUDIT-CANDIDATE-2026-09-17-v1.0','authority':'DIAGNOSTIC_FROZEN_LEAF_TO_GATEWAY_DEPENDENCY_AUDIT_ONLY__NO_DELETION_BOUNDARY_RECOMPUTATION_SOLVER_ACTION_AUTOMORPHISM_GROUP_SEARCH_CARRIER_ADAPTER_OR_QUOTIENT','verdict':verdict,'guards':guards,'preregistration_blob':blob(PREREG),'review_blob':blob(REVIEW),'parent_boundary_result_blob':blob(PARENT),'node_count':len(nodes),'edge_count':len(edges),'directed_edges':[list(e) for e in edges],'per_source':per_source,'directed_cycles':cycles,'acyclic':acyclic,'topological_elimination_order':topo if acyclic else None,'reverse_reconstruction_order':list(reversed(topo)) if acyclic else None,'composition_theorem':theorem,'resource_receipt':{'nodes':11,'boundary_relation_recomputations':0,'attachment_deletions':0,'projected_raw_modifications':0,'fresh_holdout_values_read':0,'solver_invocations':0,'component_solution_attempts':0,'action_tests':0,'automorphism_tests':0,'group_searches':0,'new_feature_definitions':0,'new_graph_statistics':0},'scientific_firewall':{'P_VS_NP':'OPEN','GENERAL_SAT_IN_P':'NOT_PROVED','CONNECTED_MIXED_CORE_SOLVED':'NO','ACYCLIC_DEPENDENCIES_IMPLY_GLOBAL_TRACTABILITY':False}}
if __name__=='__main__':print(json.dumps(main(),sort_keys=True,separators=(',',':')))
