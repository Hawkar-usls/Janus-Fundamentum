#!/usr/bin/env python3
import json
from janus_trump_r44f_scalable_backdoor_obstruction import family, BASE
from janus_trump_r44d_obstruction_consumption import dispatch_r44d
from janus_trump_r44_exact_representation_switchboard import norm


def vars_of_clause(c):
    return {abs(l) for l in c}


def component_partition(cnf):
    # Clause components induced by variable co-occurrence. Two clauses are linked if they share a variable,
    # transitively. This is exact decomposition for conjunction over disjoint variable sets.
    n=len(cnf)
    var_to_clauses={}
    for i,c in enumerate(cnf):
        for v in vars_of_clause(c):
            var_to_clauses.setdefault(v,[]).append(i)
    seen=set(); comps=[]
    for s in range(n):
        if s in seen: continue
        stack=[s]; seen.add(s); ids=[]
        while stack:
            i=stack.pop(); ids.append(i)
            for v in vars_of_clause(cnf[i]):
                for j in var_to_clauses.get(v,[]):
                    if j not in seen:
                        seen.add(j); stack.append(j)
        comps.append([cnf[i] for i in sorted(ids)])
    return comps


def local_exact_solve(cnf):
    route,res,ledger=dispatch_r44d(norm(cnf))
    if route is not None and res.get('verified') is True:
        return {'route':route,'decision':res.get('decision'),'verified':True,'ledger':ledger}
    # R44F BASE is constant-size and intentionally outside the frozen switchboard. For R44G we add a
    # preregistered exact finite local truth-table certificate for this one 3-variable component type.
    vs=sorted({abs(l) for c in cnf for l in c})
    if len(vs) > 3:
        return None
    sat_witness=None
    for mask in range(1<<len(vs)):
        a={v:bool((mask>>i)&1) for i,v in enumerate(vs)}
        ok=all(any(a[abs(l)]==(l>0) for l in c) for c in cnf)
        if ok:
            sat_witness=a; break
    return {
        'route':'LOCAL_EXACT_TRUTH_TABLE_K_LE_3_V1',
        'decision':'SAT' if sat_witness is not None else 'UNSAT',
        'verified':True,
        'witness':sat_witness,
        'authority_scope':'component variable count <= 3 only'
    }


def solve_by_components(cnf):
    comps=component_partition(cnf)
    solved=[]
    merged_witness={}
    for comp in comps:
        r=local_exact_solve(comp)
        if r is None:
            return {'status':'OPEN_COMPONENT','decision_authority':False,'components':solved}
        solved.append({'vars':sorted({abs(l) for c in comp for l in c}),'clauses':comp,'result':r})
        if r['decision']=='UNSAT':
            return {'status':'CERTIFIED','decision':'UNSAT','verified':True,'components':solved}
        if r.get('witness'):
            overlap=set(merged_witness).intersection(r['witness'])
            assert not overlap
            merged_witness.update(r['witness'])
    assert all(any(merged_witness[abs(l)]==(l>0) for l in c) for c in cnf)
    return {'status':'CERTIFIED','decision':'SAT','verified':True,'witness':merged_witness,'components':solved}

checks=[]
for t in range(1,13):
    F=family(t)
    comps=component_partition(F)
    assert len(comps)==t
    assert all(len({abs(l) for c in comp for l in c})==3 for comp in comps)
    r=solve_by_components(F)
    assert r['status']=='CERTIFIED' and r['verified'] is True
    checks.append({
        't':t,
        'variables':3*t,
        'clauses':3*t,
        'components':len(comps),
        'naive_backdoor_branches':2**t,
        'factorized_local_solves':len(comps),
        'decision':r['decision']
    })

print(json.dumps({
    'gate_id':'R44G_COMPRESS_OR_BYPASS_LINEAR_BACKDOOR_COST',
    'route':'VARIABLE_DISJOINT_COMPONENT_FACTOR_V1',
    'base_gadget':BASE,
    'checks':checks,
    'r44f_family_consumed_without_global_branch_product':True,
    'theorem':'For pairwise variable-disjoint CNF components F_i, SAT(AND_i F_i) iff every F_i is SAT. Therefore independent component decisions compose without enumerating the Cartesian product of local backdoor assignments.',
    'complexity_for_r44f_family':'O(t) component decompositions and t constant-size exact local solves; no 2^t enumeration.',
    'general_connected_3sat_solved':False,
    'U1':'OPEN',
    'P_EQUALS_NP':'NOT_PROVED',
    'P_VS_NP':'OPEN',
    'next_gate':'R44H_CONNECTED_GADGET_COUPLING_OBSTRUCTION'
}, sort_keys=True))
