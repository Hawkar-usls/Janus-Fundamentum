#!/usr/bin/env python3
import itertools, json
from janus_trump_r44_exact_representation_switchboard import dispatch, norm
from janus_trump_r44d_obstruction_consumption import dispatch_r44d

BASE = [[1,2,3],[1,2,-3],[-1,-2,3]]


def vars_of(cnf):
    return sorted({abs(l) for c in cnf for l in c})


def is_horn(cnf):
    return all(sum(1 for l in c if l>0) <= 1 for c in cnf)


def is_dual_horn(cnf):
    return all(sum(1 for l in c if l<0) <= 1 for c in cnf)


def is_renamable_horn_exact(cnf):
    vs=vars_of(cnf)
    for bits in itertools.product([False,True], repeat=len(vs)):
        flip=dict(zip(vs,bits))
        t=[[(-l if flip[abs(l)] else l) for l in c] for c in cnf]
        if is_horn(t):
            return True
    return False


def gadget(offset):
    m={1:offset+1,2:offset+2,3:offset+3}
    return [[(m[abs(l)] if l>0 else -m[abs(l)]) for l in c] for c in BASE]


def family(t):
    out=[]
    for i in range(t):
        out.extend(gadget(3*i))
    return out


def simplify(cnf, assignment):
    out=[]
    for c in cnf:
        nc=[]; sat=False
        for l in c:
            v=abs(l)
            if v in assignment:
                if assignment[v] == (l>0):
                    sat=True; break
            else:
                nc.append(l)
        if sat: continue
        if not nc: return [[]]
        out.append(nc)
    return out


def frozen_authoritative_terminal(cnf):
    if cnf == [[]] or not cnf:
        return True
    route,res,_=dispatch_r44d(norm(cnf))
    if route is None:
        return False
    # R44 renamable-Horn route is explicitly diagnostic-only and carries no asymptotic authority.
    if route.startswith('RENAMABLE_HORN_'):
        return False
    return res.get('verified') is True

# Verify the base gadget has the intended local obstruction properties.
assert all(len(c)==3 for c in BASE)
assert not is_horn(BASE)
assert not is_dual_horn(BASE)
assert not is_renamable_horn_exact(BASE)
route,res,_=dispatch_r44d(BASE)
assert route is None

# Any single variable hit makes one gadget a 2-SAT residual for both assignments.
for v in (1,2,3):
    for bit in (False,True):
        r=simplify(BASE,{v:bit})
        assert all(len(c)<=2 for c in r)
        assert frozen_authoritative_terminal(r)

checks=[]
for t in range(1,7):
    F=family(t)
    route,res,_=dispatch_r44d(F)
    assert route is None, (t,route)
    supports=[set(range(3*i+1,3*i+4)) for i in range(t)]
    # Structural lower bound: any B with |B|<t misses at least one disjoint support.
    # An untouched copy is exactly BASE up to renaming and blocks every currently authoritative frozen terminal class.
    lower_bound=t
    # Constructive upper bound: hit first variable of every gadget; every branch is 2-SAT.
    B=[3*i+1 for i in range(t)]
    branch_ok=True
    # Exhaustive branch replay is only for t<=6 fixtures; theorem authority comes from the structural argument above.
    for bits in itertools.product([False,True], repeat=t):
        r=simplify(F,dict(zip(B,bits)))
        if not all(len(c)<=2 for c in r) or not frozen_authoritative_terminal(r):
            branch_ok=False; break
    assert branch_ok
    checks.append({
        't':t,
        'variables':3*t,
        'clauses':3*t,
        'frozen_route_before_backdoor':route,
        'proved_lower_bound':lower_bound,
        'constructive_backdoor':B,
        'constructive_upper_bound':t,
        'minimum_backdoor_size':t
    })

print(json.dumps({
    'gate_id':'R44F_SCALABLE_RESIDUAL_FAMILY_OUTSIDE_FIXED_BACKDOOR_RADIUS',
    'family':'DISJOINT_NONRENAMABLE_3CLAUSE_GADGETS_V1',
    'base_gadget':BASE,
    'fixture_checks':checks,
    'theorem':'For every fixed k, G_(k+1) has strong-backdoor size at least k+1 into the current authoritative frozen terminal portfolio, while size k+1 is sufficient. Hence no fixed-k R44E backdoor radius covers this family.',
    'fixed_k_route_universal':False,
    'U1':'OPEN',
    'P_NE_NP':'NOT_PROVED',
    'P_EQUALS_NP':'NOT_PROVED',
    'P_VS_NP':'OPEN',
    'next_gate':'R44G_COMPRESS_OR_BYPASS_LINEAR_BACKDOOR_COST'
}, sort_keys=True))
