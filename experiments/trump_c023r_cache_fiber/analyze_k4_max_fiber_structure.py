#!/usr/bin/env python3
"""Exact revealed structural audit of the historical MAJ3-K4 max cache fiber."""
import json, sys
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'experiments'/'direct'))
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES, normalized_edges
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace

cnf,n=maj3_lifted_tseitin_cnf(4,K4_EDGES)
p=FCTracePolicy(); result,root_call=p.solve(cnf,n)
assert result.answer is False and verify_fc_trace(cnf,n,p,root_call) is False
root_state=int(p.calls[root_call]['state'])

def target(child):
    if child.get('call') is None:return None
    c=p.calls[int(child['call'])]
    if c['terminal']=='STATE':return int(c['state'])
    if c['terminal']=='CACHE_HIT':return int(c['cache_target'])
    return None

paths=defaultdict(list); paths[root_state]=[()]
# state ids follow first-creation topological order: every dependency target is later/earlier? use repeated relaxation via DFS paths.
stack=[(root_state,())]
all_paths=defaultdict(list)
while stack:
    sid,ctx=stack.pop()
    all_paths[sid].append(ctx)
    for child in p.states[sid].get('children',[]):
        t=target(child)
        if t is not None:
            stack.append((t,ctx+(int(child['literal']),)))
max_sid=max(all_paths,key=lambda s:len(all_paths[s]))
fiber=all_paths[max_sid]
assert len(fiber)==128 and max_sid==1040
varsets=[frozenset(abs(l) for l in ctx) for ctx in fiber]
same_vars=len(set(varsets))==1
common=sorted(varsets[0]) if same_vars else []

def bits(ctx):
    d={abs(l):int(l>0) for l in ctx}
    return tuple(d[v] for v in common)
vecs=[bits(c) for c in fiber] if same_vars else []
base=vecs[0] if vecs else ()
diffs=[]
for v in vecs:
    mask=0
    for i,(a,b) in enumerate(zip(base,v)):
        if a^b: mask|=1<<i
    diffs.append(mask)

def rank_and_basis(rows):
    piv={}; basis=[]
    for original in rows:
        x=original
        while x:
            p=x.bit_length()-1
            if p in piv:x^=piv[p]
            else:
                piv[p]=x; basis.append(x); break
    return len(piv),basis
rank,basis=rank_and_basis(diffs)
affine_complete=same_vars and len(set(diffs))==(1<<rank)

edges=normalized_edges(K4_EDGES)
def decode_support(mask):
    vs=[common[i] for i in range(len(common)) if (mask>>i)&1]
    return {
      'variables':vs,
      'blocks':sorted({(v-1)//3 for v in vs}),
      'block_coordinates':[(v,(v-1)//3,(v-1)%3) for v in vs]
    }
out={
 'artifact_id':'C023R-K4-MAX-FIBER-STRUCTURE-v1.0',
 'authority_class':'REVEALED_DIAGNOSTIC_ONLY',
 'target_state':max_sid,
 'fiber_size':len(fiber),
 'all_contexts_same_explicit_variable_set':same_vars,
 'explicit_variables':common,
 'context_lengths':sorted(set(map(len,fiber))),
 'affine_rank_over_context_values':rank if same_vars else None,
 'affine_subspace_complete':affine_complete,
 'affine_expected_size':(1<<rank) if same_vars else None,
 'basis_supports':[decode_support(x) for x in basis],
 'k4_sorted_edges':[list(e) for e in edges],
 'rule':'finite exact structure check only; no asymptotic inference'
}
path=Path(__file__).with_name('K4_MAX_FIBER_STRUCTURE_v1.0.json')
path.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
