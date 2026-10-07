#!/usr/bin/env python3
"""R5 E110: exact branch-DP on the arrangement of active rank-2 check subspaces.

After E106-E109, each active forbidden check c is represented by:
  * a 2-dimensional subspace L_c <= W of dual normals;
  * one forbidden linear functional phi_c in L_c^*.

A global quotient state is a functional y in W^* avoiding
    y|L_c != phi_c
for every c.

Given a rooted binary branch decomposition of the ATOMIC subspaces L_c, define
for each node X:
    W_X = sum_{c in X} L_c
    O_X = sum_{c notin X} L_c
    B_X = W_X intersect O_X.

DP state at X:
    beta in B_X^*
that extends to some y_X in W_X^* avoiding every forbidden character in X.

Leaf:
    enumerate the four functionals on L_c, discard phi_c, project to B_X.

Join children A,B:
    beta_A and beta_B are compatible iff they agree on W_A intersect W_B.
    Compatible functionals glue uniquely on W_A+W_B.
    Their restriction to parent boundary B_X is determined by child boundary
    values because every p in B_X decomposes p=a+b with
      a in W_A intersect (W_B+O_X) <= B_A,
      b in W_B intersect (W_A+O_X) <= B_B.

Thus number of states per node <= 2^k when branch width
    k=max_X dim B_X.
A naive join costs 2^(2k) poly(n), so the solver is n*2^O(k) given the
decomposition.

The checker:
  * verifies the DP against brute force on a synthetic F2^4 arrangement;
  * replays E104's 18 active rank-2 flats with a balanced tree; ambient rank=3,
    hence width<=3, and both DP and brute force say raw8 repair exists.

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
    dot,
)


def span_basis(vecs):
    piv={}
    out=[]
    for x in vecs:
        y=x
        while y:
            p=y.bit_length()-1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p]=y
                out.append(y)
                break
    return tuple(out)


def span_set(B):
    out={0}
    for b in B:
        out |= {x^b for x in tuple(out)}
    return frozenset(out)


def intersection_basis(A,B):
    SA=span_set(A)
    SB=span_set(B)
    return span_basis(sorted(SA&SB))


def coord_map(B):
    m={0:0}
    for i,b in enumerate(B):
        for x,c in list(m.items()):
            m[x^b]=c^(1<<i)
    assert len(m)==1<<len(B)
    return m


def eval_state(state,B,x):
    coords=coord_map(B)[x]
    return (coords & state).bit_count()&1


def restriction_state(functional_on_ambient,B):
    s=0
    for i,b in enumerate(B):
        if dot(functional_on_ambient,b):
            s |= 1<<i
    return s


def all_functionals_on_subspace(B):
    # State bits on a basis enumerate every linear functional on span(B).
    return range(1<<len(B))


def eval_basis_state(state,B,x):
    return eval_state(state,B,x)


def leaves(tree):
    if isinstance(tree,int):
        return frozenset({tree})
    return leaves(tree[0])|leaves(tree[1])


def balanced_tree(indices):
    indices=tuple(indices)
    assert indices
    if len(indices)==1:
        return indices[0]
    m=len(indices)//2
    return (balanced_tree(indices[:m]),balanced_tree(indices[m:]))


class BranchDP:
    def __init__(self,d,lines,forbidden,tree):
        self.d=d
        self.lines=tuple(tuple(span_basis(L)) for L in lines)
        self.forbidden=tuple(forbidden)
        self.tree=tree
        self.all_leaves=frozenset(range(len(lines)))
        self.cache_span={}
        self.cache_boundary={}
        self.width=0

    def W(self,S):
        key=tuple(sorted(S))
        if key not in self.cache_span:
            vecs=[]
            for i in S:
                vecs.extend(self.lines[i])
            self.cache_span[key]=span_basis(vecs)
        return self.cache_span[key]

    def boundary(self,S):
        key=tuple(sorted(S))
        if key not in self.cache_boundary:
            B=intersection_basis(self.W(S),self.W(self.all_leaves-S))
            self.cache_boundary[key]=B
            self.width=max(self.width,len(B))
        return self.cache_boundary[key]

    def leaf_states(self,i):
        S=frozenset({i})
        L=self.lines[i]
        B=self.boundary(S)
        Lmap=coord_map(L)

        # forbidden[i] is a state bitmask on L basis.
        out=set()
        for f in all_functionals_on_subspace(L):
            if f==self.forbidden[i]:
                continue
            beta=0
            for j,b in enumerate(B):
                if (Lmap[b] & f).bit_count()&1:
                    beta |= 1<<j
            out.add(beta)
        return frozenset(out)

    def decompose(self,p,WA,WB):
        SB=span_set(WB)
        for a in span_set(WA):
            b=p^a
            if b in SB:
                return a,b
        raise AssertionError("no decomposition")

    def solve_node(self,node):
        if isinstance(node,int):
            return self.leaf_states(node)

        A,Bnode=node
        SA=leaves(A); SB=leaves(Bnode)
        assert SA.isdisjoint(SB)
        S=SA|SB

        statesA=self.solve_node(A)
        statesB=self.solve_node(Bnode)

        BA=self.boundary(SA)
        BB=self.boundary(SB)
        BP=self.boundary(S)

        WA=self.W(SA); WB=self.W(SB)
        I=intersection_basis(WA,WB)

        out=set()
        for astate in statesA:
            for bstate in statesB:
                if any(
                    eval_basis_state(astate,BA,g)
                    != eval_basis_state(bstate,BB,g)
                    for g in I
                ):
                    continue

                pstate=0
                for j,p in enumerate(BP):
                    x,y=self.decompose(p,WA,WB)
                    # For p in parent boundary, x lies in child-A boundary
                    # and y in child-B boundary.
                    assert x in coord_map(BA)
                    assert y in coord_map(BB)
                    val=(
                        eval_basis_state(astate,BA,x)
                        ^ eval_basis_state(bstate,BB,y)
                    )
                    if val:
                        pstate |= 1<<j
                out.add(pstate)

        return frozenset(out)

    def solve(self):
        root_states=self.solve_node(self.tree)
        assert self.boundary(self.all_leaves)==tuple()
        return bool(root_states),root_states,self.width


def flat_line_and_character(B,d):
    L=annihilator_basis(B,d)
    assert len(L)==2
    x0=next(iter(B))
    phi=0
    for i,g in enumerate(L):
        if dot(g,x0):
            phi |= 1<<i
    return L,phi


def brute_solve(d,lines,forbidden):
    for x in range(1<<d):
        ok=True
        for L,phi in zip(lines,forbidden):
            state=0
            for i,g in enumerate(L):
                if dot(g,x):
                    state |= 1<<i
            if state==phi:
                ok=False
                break
        if ok:
            return True,x
    return False,None


def verify_synthetic():
    d=4
    # Four rank-2 lines, with overlap across a balanced branch cut.
    lines=(
        (1,2),
        (2,4),
        (4,8),
        (1,8),
    )
    forbidden=(0,1,2,3)
    tree=((0,1),(2,3))

    dp=BranchDP(d,lines,forbidden,tree)
    ans,states,width=dp.solve()
    brute,x=brute_solve(d,lines,forbidden)
    assert ans==brute
    assert width<=d
    return width


def verify_e104():
    vn,support,cn,basis,words,e,flats=build_e104_flat_sets()
    d=len(basis)
    D=all_points(d)
    D2,active,unsat=propagate_explicit(D,flats)
    assert not unsat and D2==D

    lines=[]
    forbidden=[]
    for B in active:
        L,phi=flat_line_and_character(B,d)
        lines.append(L)
        forbidden.append(phi)

    tree=balanced_tree(range(len(lines)))
    dp=BranchDP(d,lines,forbidden,tree)
    ans,states,width=dp.solve()
    brute,x=brute_solve(d,lines,forbidden)

    assert ans and brute
    assert ans==brute
    assert width<=3

    avoiding=[
        x for x in D
        if all(x not in B for B in active)
    ]
    assert len(avoiding)==4

    return {
        "leaves":len(lines),
        "ambient_rank":d,
        "balanced_tree_width":width,
        "root_feasible":ans,
        "brute_avoiding_states":len(avoiding),
    }


def main():
    sw=verify_synthetic()
    stats=verify_e104()

    print("R5 E110 subspace-arrangement branch-DP: PASS")
    print("synthetic F2^4 DP agrees with brute force; width=",sw)
    print("given branch decomposition width k: state count <=2^k per edge")
    print("naive exact join runtime n*2^O(k) poly(n)")
    print("E104 replay:",stats)
    print("literature can construct such decompositions FPT for fixed k over fixed finite fields")
    print("do NOT infer polynomial construction for k=O(log n) without a stronger decomposition bound")
    print("next target: bound/construct subspace-arrangement branchwidth for the structured Tanner-derived lines")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
