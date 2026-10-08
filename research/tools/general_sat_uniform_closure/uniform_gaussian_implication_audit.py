#!/usr/bin/env python3
"""Uniform Gaussian implication closure audit for general 2-XNF.

Goal
----
Audit the branch-free closure suggested by the current Uniform closure review:

  * keep ALL affine/XOR dependencies over the original Boolean variables;
  * reduce linerals by Gaussian elimination;
  * build the 2-XNF implication graph;
  * learn SCC equalities and failed-lineral equations;
  * iterate to a fixed point;
  * reconstruct assignments only in the original variable space.

This is sound and polynomial, but it is NOT complete.

Frozen obstruction
------------------
Over x1,x2,x3, let a lineral (mask,const) mean
    parity(mask & x) XOR const.

The four clauses are

  C1:  x3 OR (x1 XOR x3)
  C2:  NOT x1 OR NOT(x1 XOR x2)
  C3:  (x1 XOR x2) OR NOT(x1 XOR x2 XOR x3)
  C4:  NOT x2 OR (x1 XOR x2 XOR x3)

They are UNSAT.  Their four forbidden codimension-2 affine flats are pairwise
disjoint and partition all 8 assignments of F2^3.

Nevertheless the Gaussian+implication closure reaches a fixed point with:
  * no learned affine equation;
  * all four clauses still active;
  * no SCC contradiction;
  * no failed lineral;
so it returns OPEN.

Every proper 3-clause subformula is SAT, hence the witness is irredundant.

Normal-span rescue
------------------
After closure, each active rank-2 clause depends only on two normal vectors.
Let W be the span of all active normals and r=dim(W).  The exact residual
problem factors through a 2^r quotient.  For the frozen obstruction r=3, so
8 quotient states decide it exactly without branching.

Thus a branch-free polynomial terminal is available whenever
    r <= O(log input_length).
The unresolved universal residue is the high-rank connected case.

This checker does NOT claim GENERAL_SAT_IN_P or P=NP.
"""

from collections import defaultdict
from itertools import product

# ---------- affine GF(2) utilities ----------

def rref_affine(equations, n):
    """RREF for equations mask·x = rhs. Return None on contradiction."""
    rows=[[m, rhs & 1] for m,rhs in equations]
    rank=0
    for col in range(n):
        p=next((i for i in range(rank,len(rows)) if (rows[i][0]>>col)&1), None)
        if p is None:
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        pm,pr=rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i][0]>>col)&1):
                rows[i][0]^=pm
                rows[i][1]^=pr
        rank+=1

    if any(m==0 and rhs for m,rhs in rows):
        return None

    out=[(m,rhs) for m,rhs in rows if m]
    out.sort(key=lambda row: (row[0] & -row[0]).bit_length())
    return tuple(out)


def reduce_lineral(lineral, equations):
    """Reduce affine truth function mask·x XOR const modulo RREF equations."""
    mask,const=lineral
    for rm,rhs in equations:
        pivot=(rm & -rm).bit_length()-1
        if (mask>>pivot)&1:
            mask ^= rm
            const ^= rhs
    return mask,const


def rank_vectors(vectors):
    piv={}
    for x in vectors:
        y=x
        while y:
            p=y.bit_length()-1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p]=y
                break
    return len(piv)


def eval_lineral(lineral, x):
    mask,const=lineral
    return ((mask & x).bit_count() & 1) ^ const


def neg(lineral):
    return lineral[0], lineral[1]^1


# ---------- exact formula semantics ----------

def satisfies(formula, x):
    return all(eval_lineral(a,x) or eval_lineral(b,x) for a,b in formula)


def satisfying_assignments(formula, n):
    return tuple(x for x in range(1<<n) if satisfies(formula,x))


def forbidden_points(clause, n):
    a,b=clause
    return frozenset(
        x for x in range(1<<n)
        if not eval_lineral(a,x) and not eval_lineral(b,x)
    )


# ---------- uniform Gaussian implication closure ----------

def reachability(nodes, edges):
    out={}
    for s in nodes:
        seen={s}
        stack=[s]
        while stack:
            u=stack.pop()
            for v in edges[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        out[s]=seen
    return out


def uniform_gaussian_implication_closure(formula, n):
    """Sound branch-free closure.

    Returns:
      ("SAT_LINEAR", equations, active_clauses)
      ("UNSAT", equations_or_None, active_clauses)
      ("OPEN", equations, active_clauses)
    """
    equations=tuple()

    # Every strict iteration learns at least one independent affine equation,
    # so at most n successful learning rounds are possible.
    for _round in range(n+2):
        equations=rref_affine(equations,n)
        if equations is None:
            return "UNSAT",None,tuple()

        learned=[]
        active=[]

        # Gaussian simplification of every clause.
        for a,b in formula:
            a=reduce_lineral(a,equations)
            b=reduce_lineral(b,equations)

            # true OR anything
            if a==(0,1) or b==(0,1):
                continue

            # false OR false
            if a==(0,0) and b==(0,0):
                return "UNSAT",equations,tuple(active)

            # false OR L -> L must be true.
            if a==(0,0):
                learned.append((b[0],1^b[1]))
                continue
            if b==(0,0):
                learned.append((a[0],1^a[1]))
                continue

            # L OR NOT L
            if a[0]==b[0] and (a[1]^b[1])==1:
                continue

            # L OR L -> L
            if a==b:
                learned.append((a[0],1^a[1]))
                continue

            active.append((a,b))

        if learned:
            neweq=rref_affine(tuple(equations)+tuple(learned),n)
            if neweq is None:
                return "UNSAT",None,tuple(active)
            if neweq!=equations:
                equations=neweq
                continue

        if not active:
            return "SAT_LINEAR",equations,tuple()

        # Build exact implication graph on affine linerals.
        nodes=set()
        edges=defaultdict(set)
        for a,b in active:
            nodes.update((a,neg(a),b,neg(b)))
            edges[neg(a)].add(b)
            edges[neg(b)].add(a)

        reach=reachability(nodes,edges)

        # SCC contradiction, failed linerals, SCC affine equalities.
        learned=[]

        for l in nodes:
            nl=neg(l)
            if nl in reach[l] and l in reach[nl]:
                return "UNSAT",equations,tuple(active)

            # l -> NOT l => l is false.
            if nl in reach[l]:
                learned.append((l[0],l[1]))

            # NOT l -> l => l is true.
            if l in reach[nl]:
                learned.append((l[0],1^l[1]))

        node_list=tuple(nodes)
        for i in range(len(node_list)):
            a=node_list[i]
            for j in range(i+1,len(node_list)):
                b=node_list[j]
                if b in reach[a] and a in reach[b]:
                    # Truth(a)=Truth(b).
                    learned.append((a[0]^b[0],a[1]^b[1]))

        neweq=rref_affine(tuple(equations)+tuple(learned),n)
        if neweq is None:
            return "UNSAT",None,tuple(active)
        if neweq!=equations:
            equations=neweq
            continue

        return "OPEN",equations,tuple(active)

    raise AssertionError("closure exceeded affine-rank iteration bound")


# ---------- global consistency audit ----------

def verify_independent_lineral_alias_hazard():
    # y1=x1, y2=x2, y3=x1 XOR x2.
    # The abstract Boolean vector (1,1,1) is impossible.
    target=((1,0),(2,0),(3,0))
    wanted=(1,1,1)
    assert not any(
        tuple(eval_lineral(l,x) for l in target)==wanted
        for x in range(4)
    )

    # Gaussian reconstruction catches the same inconsistency:
    # x1=1, x2=1, x1 XOR x2=1.
    assert rref_affine(((1,1),(2,1),(3,1)),2) is None


# ---------- frozen 3-variable obstruction ----------

def obstruction_formula():
    # bit 0=x1, bit 1=x2, bit 2=x3
    return (
        ((4,0),(5,0)),  # x3 OR (x1 XOR x3)
        ((1,1),(3,1)),  # NOT x1 OR NOT(x1 XOR x2)
        ((3,0),(7,1)),  # (x1 XOR x2) OR NOT(x1 XOR x2 XOR x3)
        ((2,1),(7,0)),  # NOT x2 OR (x1 XOR x2 XOR x3)
    )


def verify_obstruction():
    F=obstruction_formula()
    n=3

    # Exact semantic verdict.
    assert satisfying_assignments(F,n)==tuple()

    # Irredundant/minimal under deletion.
    for i in range(len(F)):
        sub=F[:i]+F[i+1:]
        assert satisfying_assignments(sub,n)

    # The four bad flats are 2-point affine lines and form an exact partition.
    bad=[forbidden_points(c,n) for c in F]
    assert all(len(B)==2 for B in bad)
    for i in range(4):
        for j in range(i+1,4):
            assert bad[i].isdisjoint(bad[j])
    assert frozenset().union(*bad)==frozenset(range(8))

    # Strong Gaussian+implication closure still cannot derive the contradiction.
    status,eqs,active=uniform_gaussian_implication_closure(F,n)
    assert status=="OPEN"
    assert eqs==tuple()
    assert len(active)==4

    # Normal span is rank 3.  Exact quotient enumeration is only 2^3 states.
    normals=[]
    for a,b in active:
        normals.extend((a[0],b[0]))
    r=rank_vectors(normals)
    assert r==3

    quotient_solutions=satisfying_assignments(active,n)
    assert quotient_solutions==tuple()

    return bad,r


def main():
    verify_independent_lineral_alias_hazard()
    bad,r=verify_obstruction()

    print("UNIFORM GAUSSIAN IMPLICATION CLOSURE AUDIT: PASS")
    print("independent-lineral alias hazard: Gaussian reconstruction rejects 111 for (x1,x2,x1^x2)")
    print("frozen 3-variable / 4-clause 2-XNF obstruction is exact UNSAT")
    print("every one-clause deletion is SAT")
    print("forbidden flats:", [sorted(B) for B in bad])
    print("four codim-2 flats partition all 8 assignments")
    print("UGIC fixed point: OPEN, learned affine rank 0, active clauses 4")
    print("normal-span rank:",r,"=> exact quotient has",1<<r,"states")
    print("LOW_NORMAL_RANK_QUOTIENT is branch-free exact and polynomial for r=O(log L)")
    print("HIGH_RANK_CONNECTED_RESIDUE remains OPEN")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
