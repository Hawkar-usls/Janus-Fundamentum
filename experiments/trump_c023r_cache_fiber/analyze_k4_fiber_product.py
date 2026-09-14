#!/usr/bin/env python3
"""Revealed follow-up: exact Cartesian-product test for K4 state 1040 fiber."""
import json,sys,itertools
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'experiments'/'direct'))
from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_tear_policy0a_fc_trace import FCTracePolicy
cnf,n=maj3_lifted_tseitin_cnf(4,K4_EDGES);p=FCTracePolicy();res,rc=p.solve(cnf,n)
root=int(p.calls[rc]['state'])
def target(ch):
 c=p.calls[int(ch['call'])] if ch.get('call') is not None else None
 return None if c is None else int(c['state'] if c['terminal']=='STATE' else c['cache_target']) if c['terminal'] in ('STATE','CACHE_HIT') else None
paths=defaultdict(list); stack=[(root,())]
while stack:
 s,ctx=stack.pop();paths[s].append(ctx)
 for ch in p.states[s].get('children',[]):
  t=target(ch)
  if t is not None:stack.append((t,ctx+(int(ch['literal']),)))
fiber=paths[1040]; assert len(fiber)==128
fixed_by_block={b:sorted({abs(l) for c in fiber for l in c if (abs(l)-1)//3==b}) for b in range(6)}
pattern_sets={}
rows=set()
for ctx in fiber:
 d={abs(l):int(l>0) for l in ctx}; row=[]
 for b in range(6):
  pat=tuple(d[v] for v in fixed_by_block[b]); pattern_sets.setdefault(b,set()).add(pat); row.append(pat)
 rows.add(tuple(row))
product_size=1
for s in pattern_sets.values():product_size*=len(s)
cartesian=set(itertools.product(*(sorted(pattern_sets[b]) for b in range(6))))
out={'fiber_size':len(rows),'fixed_variables_by_block':fixed_by_block,'patterns_by_block':{str(b):[list(x) for x in sorted(pattern_sets[b])] for b in range(6)},'pattern_counts':{str(b):len(pattern_sets[b]) for b in range(6)},'cartesian_product_size':product_size,'exact_cartesian_product':rows==cartesian,'authority':'REVEALED_DIAGNOSTIC_ONLY'}
Path(__file__).with_name('K4_FIBER_PRODUCT_v1.0.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
