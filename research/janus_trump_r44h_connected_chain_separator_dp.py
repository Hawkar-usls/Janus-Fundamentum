#!/usr/bin/env python3
import json

BASE = [[1,2,3],[1,2,-3],[-1,-2,3]]


def sat_clause(c, a):
    return any(a[abs(l)] == (l > 0) for l in c)


def gadget_clauses(si, ai, sj):
    m={1:si,2:ai,3:sj}
    return [[m[abs(l)] if l>0 else -m[abs(l)] for l in c] for c in BASE]


def chain(t):
    # separators s_0..s_t are 1..t+1; local a_i are t+2..2t+1
    clauses=[]
    gadgets=[]
    for i in range(t):
        si=i+1
        sj=i+2
        ai=t+2+i
        g=gadget_clauses(si,ai,sj)
        clauses.extend(g)
        gadgets.append((si,ai,sj,g))
    return clauses,gadgets


def primal_connected(cnf):
    vs=sorted({abs(l) for c in cnf for l in c})
    adj={v:set() for v in vs}
    for c in cnf:
        cv=sorted({abs(l) for l in c})
        for i,u in enumerate(cv):
            for v in cv[i+1:]:
                adj[u].add(v); adj[v].add(u)
    seen=set()
    stack=[vs[0]] if vs else []
    while stack:
        u=stack.pop()
        if u in seen: continue
        seen.add(u); stack.extend(adj[u]-seen)
    return len(seen)==len(vs)


def dp_solve(t):
    cnf,gadgets=chain(t)
    # map frontier value to one exact witness for processed prefix
    states={False:{1:False}, True:{1:True}}
    max_states=len(states)
    for si,ai,sj,g in gadgets:
        nxt={}
        for svi,w in states.items():
            assert w[si] == svi
            for aval in (False,True):
                for sjval in (False,True):
                    a=dict(w); a[ai]=aval; a[sj]=sjval
                    if all(sat_clause(c,a) for c in g):
                        nxt.setdefault(sjval,a)
        states=nxt
        max_states=max(max_states,len(states))
        if not states:
            return {"decision":"UNSAT","verified":True,"max_frontier_states":max_states,"cnf":cnf}
    witness=next(iter(states.values()))
    assert all(sat_clause(c,witness) for c in cnf)
    return {"decision":"SAT","verified":True,"witness":witness,"max_frontier_states":max_states,"cnf":cnf}

checks=[]
for t in range(1,65):
    cnf,_=chain(t)
    assert primal_connected(cnf)
    r=dp_solve(t)
    assert r['verified'] is True
    assert r['max_frontier_states'] <= 2
    checks.append({
        't':t,
        'variables':2*t+1,
        'clauses':3*t,
        'primal_connected':True,
        'max_frontier_states':r['max_frontier_states'],
        'decision':r['decision']
    })

print(json.dumps({
    'gate_id':'R44H_CONNECTED_CHAIN_SEPARATOR_DP',
    'family':'CONNECTED_OVERLAPPING_GADGET_CHAIN_V1',
    'route':'CONSTANT_SEPARATOR_FRONTIER_DP_V1',
    'checks':checks,
    'connected_family_consumed_without_global_branch_product':True,
    'state_bound':2,
    'complexity':'O(t) local transitions with at most 2 frontier states and 4 constant local extensions per incoming state',
    'proof_idea':'Inductively, states after gadget i are exactly the values of separator s_(i+1) extendible to a satisfying assignment of the processed prefix.',
    'general_connected_3sat_solved':False,
    'U1':'OPEN',
    'P_EQUALS_NP':'NOT_PROVED',
    'P_VS_NP':'OPEN',
    'next_gate':'R44I_GROWING_SEPARATOR_WIDTH_OR_SEMANTIC_STATE_COMPRESSION'
}, sort_keys=True))
