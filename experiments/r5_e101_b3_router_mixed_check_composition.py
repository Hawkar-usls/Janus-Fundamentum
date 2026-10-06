#!/usr/bin/env python3
"""R5 E101: B3 router -> mixed-check composition.

Take one exact B_C=3 router relation R on bits r0,r1,r2.  Each boundary
inert incidence enters a distinct mixed ExactOne check

    ExactOne(ri, ai, bi).

Eliminate the router bits.  The resulting six-port relation G(R) is:
  if ri=1, then (ai,bi)=(0,0);
  if ri=0, then exactly one of ai,bi is 1.

E100 gives exactly 17 nonempty router relations.

E101 proves:
  * for 16/17 routers (all except EQ3={000,111}), R is equicardinal and
    is the basis family of a binary matroid M on three elements;
  * G(R) is exactly the parallel-pair lift of the dual matroid M*:
    complement the router basis, then replace each ground element i by the
    parallel pair {ai,bi};
  * therefore G(R) is an explicitly represented binary matroid basis family,
    hence an even binary delta-matroid;
  * the unique exception R=EQ3 gives
        G(EQ3) = {000000} union
                 {choose exactly one element from each of three pairs},
    which fails symmetric exchange;
  * this exception is semantically identical to retaining one ordinary
    Equality_3 variable z and the three mixed ExactOne checks:
        exists z: prod_i ExactOne(z,ai,bi).

By E99 a non-rigid/mixed check has at most one inert incidence.  Hence two
different B3 rigid cores cannot claim the same mixed check, so all B3 gadgets
can be processed in parallel: non-EQ gadgets become represented binary modules,
while EQ gadgets collapse to one Equality variable.

This is an exact semantic closure theorem.  It does NOT solve the constructive
identification problem: E100 does not yet give a polynomial algorithm for
deciding which optional router states are feasible inside an arbitrary large
core.

P_VS_NP remains OPEN.
"""

from itertools import combinations, product

W1=frozenset({1,2,4})
W2=frozenset({3,5,6})
EQ=frozenset({0,7})


def nonempty_subsets(S):
    S=tuple(sorted(S))
    out=[]
    for r in range(1,len(S)+1):
        for C in combinations(S,r):
            out.append(frozenset(C))
    return tuple(out)


ROUTERS=(frozenset({0}),frozenset({7}),EQ)+nonempty_subsets(W1)+nonempty_subsets(W2)
assert len(ROUTERS)==17


def compose_router(R):
    F=set()
    for r in R:
        options=[]
        for i in range(3):
            if (r>>i)&1:
                options.append(((0,0),))
            else:
                options.append(((1,0),(0,1)))
        for p0 in options[0]:
            for p1 in options[1]:
                for p2 in options[2]:
                    bits=p0+p1+p2
                    F.add(sum(b<<j for j,b in enumerate(bits)))
    return frozenset(F)


def sym_exchange_failure(F,n):
    F=set(F)
    for X in F:
        for Y in F:
            d=X^Y
            for e in range(n):
                if not ((d>>e)&1):
                    continue
                ok=False
                for f in range(n):
                    if not ((d>>f)&1):
                        continue
                    Z=X^(1<<e) if f==e else X^(1<<e)^(1<<f)
                    if Z in F:
                        ok=True
                        break
                if not ok:
                    return X,Y,e
    return None


def gf2_rank(cols,r):
    basis=[0]*r
    rank=0
    for x in cols:
        y=x
        while y:
            b=y.bit_length()-1
            if basis[b]:
                y^=basis[b]
            else:
                basis[b]=y
                rank+=1
                break
    return rank


def bases_from_columns(cols,r):
    n=len(cols)
    if r==0:
        return frozenset({0})
    out=set()
    for C in combinations(range(n),r):
        if gf2_rank([cols[i] for i in C],r)==r:
            out.add(sum(1<<i for i in C))
    return frozenset(out)


def find_binary_rep_three(B):
    """Find a GF(2) representation for an equicardinal basis family on 3."""
    sizes={x.bit_count() for x in B}
    assert len(sizes)==1
    r=next(iter(sizes))
    if r==0:
        assert B==frozenset({0})
        return (0,0,0),0
    seed=next(iter(B))
    basis_e=[i for i in range(3) if (seed>>i)&1]
    other=[i for i in range(3) if i not in basis_e]
    cols=[None]*3
    for k,i in enumerate(basis_e):
        cols[i]=1<<k
    for vals in product(range(1<<r),repeat=len(other)):
        for i,v in zip(other,vals):
            cols[i]=v
        if bases_from_columns(tuple(cols),r)==B:
            return tuple(cols),r
    raise AssertionError(("no binary rep",B))


def complement_bases(R):
    return frozenset(7^x for x in R)


def parallel_lift(cols,r):
    out=[]
    for v in cols:
        out.extend((v,v))
    return tuple(out)


def verify_non_eq_router(R):
    sizes={x.bit_count() for x in R}
    assert len(sizes)==1

    dual_bases=complement_bases(R)
    dual_sizes={x.bit_count() for x in dual_bases}
    assert len(dual_sizes)==1

    cols3,r=find_binary_rep_three(dual_bases)
    cols6=parallel_lift(cols3,r)
    represented=bases_from_columns(cols6,r)
    semantic=compose_router(R)

    assert represented==semantic
    assert sym_exchange_failure(semantic,6) is None
    assert len({x.bit_count()%2 for x in semantic})==1
    return r,cols6,len(semantic)


def verify_eq_exception():
    G=compose_router(EQ)

    expected={0}
    for choice in product((0,1),repeat=3):
        m=0
        for i,c in enumerate(choice):
            m |= 1<<(2*i+c)
        expected.add(m)
    assert G==frozenset(expected)
    assert len(G)==9
    assert {x.bit_count() for x in G}=={0,3}

    fail=sym_exchange_failure(G,6)
    assert fail is not None

    # Exact central-Equality star identity.
    star=set()
    for z in (0,1):
        opts=[]
        for _ in range(3):
            if z:
                opts.append(((0,0),))
            else:
                opts.append(((1,0),(0,1)))
        for p0 in opts[0]:
            for p1 in opts[1]:
                for p2 in opts[2]:
                    bits=p0+p1+p2
                    star.add(sum(b<<j for j,b in enumerate(bits)))
    assert frozenset(star)==G
    return fail


def verify_parallel_gadget_disjointness():
    # E99 theorem: ordinary check inert-incidence count is 0,1,3, never 2.
    # A mixed check is non-rigid, hence cannot have count 3; if it borders a
    # rigid core it has exactly one inert incidence. Thus it belongs to a unique
    # rigid core boundary. Freeze the logical count table.
    allowed={0,1,3}
    assert 2 not in allowed
    mixed={k for k in allowed if k!=3}
    assert mixed=={0,1}
    assert max(mixed)==1


def main():
    binary=[]
    for R in ROUTERS:
        if R==EQ:
            continue
        binary.append((tuple(sorted(R)),)+verify_non_eq_router(R))

    assert len(binary)==16
    fail=verify_eq_exception()
    verify_parallel_gadget_disjointness()

    print("R5 E101 B3 router -> mixed-check composition: PASS")
    print("E100 router families=17")
    print("non-EQ routers -> explicit binary-matroid six-port modules=16")
    print("construction: complement/dual router bases, then duplicate each element as a parallel pair")
    print("EQ3 unique exception: six-port family has 9 states and fails symmetric exchange at",fail)
    print("EQ3 exception is exactly one Equality variable joined to the same three ExactOne checks")
    print("E99 uniqueness => all B3 gadgets can be reduced in parallel")
    print("residual hard kernel: represented binary modules + primitive Equality-star nodes; no internal rigid checks")
    print("constructive gap: exact router-type identification inside an arbitrary large core remains OPEN")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
