#!/usr/bin/env python3
"""R5 E109: binary normal-matroid component decomposition.

After E108, the residual pure rank-2 instance is described by active dual
2-spaces L_c <= W.  Each check's three nonzero coordinate functionals are
exactly the three nonzero vectors of L_c and form a binary 3-circuit.

Let M be the represented binary matroid on the distinct nonzero normal vectors
used by the active flats.

If M has connected components E_1,...,E_s with spans W_i, then

    W = W_1 direct_sum ... direct_sum W_s.

Every active line L_c is contained in exactly one W_i (a circuit cannot cross
matroid components).  Therefore every forbidden flat depends on exactly one
component coordinate.

Consequently the avoidance problem factors exactly:
  a global avoiding state exists
  iff
  every matroid component has a local avoiding state.

Thus exact solving costs
    sum_i 2^{rank(W_i)} poly(n)
rather than 2^{rank(W)}.

Polynomial terminal:
    max_i rank(W_i) = O(log n).

The checker verifies a two-component synthetic instance and replays E104,
whose active normal matroid is one connected rank-3 component.

P_VS_NP remains OPEN.
"""

from itertools import product

from r5_e106_affine_unit_propagation_rank2_core import (
    build_e104_flat_sets,
    propagate_explicit,
    all_points,
)
from r5_e108_normal_span_quotient_solver import (
    annihilator_basis,
    span_basis,
    dot,
)


def independent_basis(vecs):
    piv={}
    B=[]
    for x in vecs:
        y=x
        while y:
            p=y.bit_length()-1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p]=y
                B.append(x)
                break
    return tuple(B)


def elimination_for_basis(B):
    """pivot -> (row_vector, coefficient mask in fixed B coordinates)."""
    piv={}
    for i,x in enumerate(B):
        y=x
        coeff=1<<i
        while y:
            p=y.bit_length()-1
            if p in piv:
                row,cm=piv[p]
                y ^= row
                coeff ^= cm
            else:
                piv[p]=(y,coeff)
                break
        assert y
    return piv


def coords_in_basis(x,B,piv=None):
    if piv is None:
        piv=elimination_for_basis(B)
    y=x
    coeff=0
    for p in sorted(piv,reverse=True):
        if (y>>p)&1:
            row,cm=piv[p]
            y ^= row
            coeff ^= cm
    assert y==0, (x,B)
    return coeff


def matroid_components(vecs):
    """Connected components of represented vector matroid on unique nonzero vecs."""
    elems=tuple(sorted(set(v for v in vecs if v)))
    if not elems:
        return tuple()

    B=independent_basis(elems)
    piv=elimination_for_basis(B)
    basis_index={v:i for i,v in enumerate(B)}

    adj={v:set() for v in elems}
    for e in elems:
        coeff=coords_in_basis(e,B,piv)
        support=[B[i] for i in range(len(B)) if (coeff>>i)&1]

        if e in basis_index and len(support)==1 and support[0]==e:
            continue

        # Fundamental circuit: e plus all basis elements in its expression.
        nodes=set(support)|{e}
        nodes=list(nodes)
        for i in range(1,len(nodes)):
            adj[nodes[0]].add(nodes[i])
            adj[nodes[i]].add(nodes[0])

    comps=[]
    seen=set()
    for s in elems:
        if s in seen:
            continue
        C=set(); stack=[s]
        while stack:
            x=stack.pop()
            if x in C:
                continue
            C.add(x); seen.add(x); stack.extend(adj[x]-C)
        comps.append(frozenset(C))

    # Component spans must form direct sum.
    ranks=[len(independent_basis(C)) for C in comps]
    assert sum(ranks)==len(independent_basis(elems))
    return tuple(comps)


def flat_normal_line(B,d):
    basis=annihilator_basis(B,d)
    assert len(basis)==2
    a,b=basis
    return frozenset({a,b,a^b})


def verify_synthetic_factorization():
    # D=F2^4 split as W1=<e0,e1>, W2=<e2,e3>.
    d=4
    D=all_points(d)

    def flat(a,b,aa,bb):
        return frozenset(
            x for x in D
            if dot(a,x)==aa and dot(b,x)==bb
        )

    flats1=(flat(1,2,0,0), flat(1,2,1,1))
    flats2=(flat(4,8,0,1),)
    flats=flats1+flats2

    lines=[flat_normal_line(B,d) for B in flats]
    vecs=[g for L in lines for g in L]
    comps=matroid_components(vecs)
    ranks=sorted(len(independent_basis(C)) for C in comps)
    assert ranks==[2,2]

    global_avoid=frozenset(
        x for x in D if all(x not in B for B in flats)
    )

    # Product criterion: each component's local constraints must leave a state.
    local_ok=[]
    for C in comps:
        relevant=[
            B for B,L in zip(flats,lines)
            if L <= C
        ]
        # Enumerate ambient points; quotient duplicates do not matter for
        # existence, so this is a simple checker.
        local_ok.append(any(all(x not in B for B in relevant) for x in D))

    assert bool(global_avoid)==all(local_ok)
    assert global_avoid


def verify_every_line_inside_one_component(lines,comps):
    owner={}
    for i,C in enumerate(comps):
        for g in C:
            owner[g]=i
    for L in lines:
        ids={owner[g] for g in L}
        assert len(ids)==1


def verify_e104_replay():
    vn,support,cn,basis,words,e,flats=build_e104_flat_sets()
    d=len(basis)
    D=all_points(d)
    D2,active,unsat=propagate_explicit(D,flats)
    assert not unsat

    lines=[flat_normal_line(B,d) for B in active]
    vecs=[g for L in lines for g in L]
    comps=matroid_components(vecs)
    verify_every_line_inside_one_component(lines,comps)

    ranks=sorted(len(independent_basis(C)) for C in comps)
    assert sum(ranks)<=d

    brute=frozenset(
        x for x in D2
        if all(x not in B for B in active)
    )
    assert len(brute)==4

    return {
        "active_flats":len(active),
        "normal_matroid_components":len(comps),
        "component_ranks":ranks,
        "avoiding_states":len(brute),
    }


def main():
    verify_synthetic_factorization()
    stats=verify_e104_replay()

    print("R5 E109 binary normal-matroid component decomposition: PASS")
    print("every active check line lies inside one represented-matroid component")
    print("normal span is direct sum of component spans")
    print("flat avoidance factors exactly across those components")
    print("max component rank O(log n) => polynomial exact solver")
    print("E104 replay:",stats)
    print("next target: attack one matroid-connected pure-rank2 block of superlogarithmic rank")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
