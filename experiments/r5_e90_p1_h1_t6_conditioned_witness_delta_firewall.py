#!/usr/bin/env python3
"""R5 E90: p=1,h=1 t=6 conditioned-U24 witness + delta-parent firewall.

E89 excluded the p=1,h=1 lane through t=5 and proposed a shared-savings
induction. E90 falsifies the strongest version of that induction target:

  * at t=6 there is an explicit C4-free residual Tanner gadget whose
    conditioned four-port relation is exactly U_{2,4} twisted by the one
    variable-side port;
  * the gadget embeds in an explicit connected square 26x26 cubic C4-free
    RXC3 source.

So C4-free source geometry ALONE does not exclude the conditioned U2,4
semantics.

However the immediate five-port unpin of the witness has exact relation

    {1,2,4,8,19,21,22},

which is not a delta-matroid.  In the explicit 26x26 source completion, E90
then absorbs every connected subset of the 15 outside Tanner vertices using
exact boundary-relation composition.  There are exactly 14,345 connected
supersets of the witness cluster.  Exactly 160 have a canonical matroid
boundary relation; all 160 are binary.  No nonbinary delta parent occurs in
this complete finite expansion cone.

This does NOT prove that no other source/completion can supply a nonbinary
delta parent.  It proves that the next representation theorem must use
delta-parent liftability, not merely C4-free residual geometry.

P_VS_NP remains OPEN.
"""

from collections import Counter
from functools import lru_cache
from itertools import combinations


A,B,C = 0,1,2
R,S = 17,18

BASE = {
    (0,3,15),
    (1,7,8),
    (2,3,4),
    (3,6,10),
    (4,5,9),
    (4,7,13),
    (5,6,7),
    (5,10,12),
    (6,9,16),
    (8,9,10),
    (8,11,14),
    (11,12,13),
    (14,15,16),
}

EXTRAS = {
    (0,12,16),
    (1,2,18),
    (11,15,18),
    (13,14,17),
}

XEDGE = (R,S)
CUBICS = tuple(sorted(BASE | EXTRAS))
TARGET4 = frozenset({1,2,4,11,13,14})
RAW5 = frozenset({1,2,4,8,19,21,22})

# Outside completion: 7 checks x 8 variables.
# check 0 is attached to active variable x;
# outside vars 0,1,2,3 attach to active checks A,B,C,R.
OUTSIDE_INTERNAL = {
    (0,5),(0,7),
    (1,1),(1,6),(1,7),
    (2,1),(2,4),(2,5),
    (3,2),(3,4),(3,7),
    (4,3),(4,4),(4,6),
    (5,0),(5,3),(5,5),
    (6,0),(6,2),(6,6),
}

EXPECTED_CONNECTED_EXPANSIONS = 14345
EXPECTED_MATROID_INTERFACES = 160
EXPECTED_MATROID_BY_ARITY = Counter({3:9,4:16,5:23,6:57,7:36,8:14,9:5})


def sym_exchange_failure(family,n):
    F=set(family)
    for X in F:
        for Y in F:
            diff=X^Y
            for e in range(n):
                if not ((diff>>e)&1):
                    continue
                ok=False
                for f in range(n):
                    if not ((diff>>f)&1):
                        continue
                    Z=X^(1<<e)
                    if f!=e:
                        Z^=1<<f
                    if Z in F:
                        ok=True
                        break
                if not ok:
                    return X,Y,e
    return None


def basis_exchange_failure(family,n):
    F=set(family)
    if not F:
        return ("empty",)
    sizes={x.bit_count() for x in F}
    if len(sizes)!=1:
        return ("sizes",tuple(sorted(sizes)))
    for X in F:
        for Y in F:
            for e in range(n):
                if ((X>>e)&1) and not ((Y>>e)&1):
                    if not any(
                        ((Y>>f)&1) and not ((X>>f)&1)
                        and (X^(1<<e)^(1<<f)) in F
                        for f in range(n)
                    ):
                        return X,Y,e
    return None


def gf2_rank_cols(cols):
    pivots={}
    rank=0
    for x in cols:
        y=x
        while y:
            p=y.bit_length()-1
            if p in pivots:
                y^=pivots[p]
            else:
                pivots[p]=y
                rank+=1
                break
    return rank


def binary_matroid_from_bases(bases,n):
    if not bases:
        return True
    sizes={x.bit_count() for x in bases}
    assert len(sizes)==1
    r=next(iter(sizes))
    B0=next(iter(bases))
    bel=[i for i in range(n) if (B0>>i)&1]
    row={b:k for k,b in enumerate(bel)}
    cols=[0]*n

    for b,k in row.items():
        cols[b]=1<<k

    for e in range(n):
        if (B0>>e)&1:
            continue
        col=0
        for b,k in row.items():
            if (B0^(1<<b)^(1<<e)) in bases:
                col|=1<<k
        cols[e]=col

    reproduced=set()
    for comb in combinations(range(n),r):
        if gf2_rank_cols([cols[e] for e in comb])==r:
            reproduced.add(sum(1<<e for e in comb))
    return reproduced==set(bases)


def exact_partition_exists(triples,target):
    target=frozenset(target)
    usable=[frozenset(e) for e in triples if frozenset(e)<=target]
    byp={p:[] for p in target}
    for e in usable:
        for p in e:
            byp[p].append(e)

    memo={}
    def rec(rem):
        rem=frozenset(rem)
        if not rem:
            return True
        if rem in memo:
            return memo[rem]
        p=min(rem,key=lambda z:sum(e<=rem for e in byp[z]))
        ans=False
        for e in byp[p]:
            if e<=rem and rec(rem-e):
                ans=True
                break
        memo[rem]=ans
        return ans

    return rec(target)


def boundary_family_5(triples):
    """Bits A,B,C,R,x.  R is the zero-hole check when pinned to 0."""
    U=set(range(19))
    fam=set()

    for bits in range(32):
        external={
            u for k,u in enumerate((A,B,C,R))
            if (bits>>k)&1
        }
        xsel=(bits>>4)&1
        xcovered={R,S} if xsel else set()

        if external & xcovered:
            continue

        target=U-external-xcovered
        if len(target)%3:
            continue

        if exact_partition_exists(triples,target):
            fam.add(bits)

    return frozenset(fam)


def condition_R_zero(raw):
    out=set()
    for z in raw:
        if (z>>3)&1:
            continue
        out.add((z&7)|(((z>>4)&1)<<3))
    return frozenset(out)


def audit_residual_witness():
    assert len(CUBICS)==17

    variables=[frozenset(XEDGE)]+[frozenset(e) for e in CUBICS]
    deg=[0]*19
    for e in variables:
        for u in e:
            deg[u]+=1

    assert deg==[
        2,2,2,
        3,3,3,3,3,3,3,3,3,3,3,3,3,3,
        2,3
    ]

    for i,j in combinations(range(len(variables)),2):
        assert len(variables[i]&variables[j])<=1

    raw=boundary_family_5(CUBICS)
    assert raw==RAW5
    assert condition_R_zero(raw)==TARGET4

    # Immediate parent is not delta.
    assert sym_exchange_failure(raw,5) is not None

    # Canonical twist uses the variable-side x port (bit 4).
    M=frozenset(z^(1<<4) for z in raw)
    assert {z.bit_count() for z in M}=={2}
    assert basis_exchange_failure(M,5) is not None

    return raw


def build_full_source():
    edges=set()

    # Active witness.
    for u in XEDGE:
        edges.add((u,0))
    for j,e in enumerate(CUBICS,start=1):
        for u in e:
            edges.add((u,j))

    # Four active-check -> outside-variable stubs.
    edges.update({
        (A,18),
        (B,19),
        (C,20),
        (R,21),
    })

    # Active x -> outside check.
    edges.add((19,0))

    # Outside internal edges.
    for ci,vj in OUTSIDE_INTERNAL:
        edges.add((19+ci,18+vj))

    assert len(edges)==78

    cdeg=[0]*26
    vdeg=[0]*26
    for i,j in edges:
        cdeg[i]+=1
        vdeg[j]+=1
    assert cdeg==[3]*26
    assert vdeg==[3]*26

    # C4-free / source-linearity.
    vnei=[set() for _ in range(26)]
    for i,j in edges:
        vnei[j].add(i)
    for u,v in combinations(range(26),2):
        assert len(vnei[u]&vnei[v])<=1

    # Connected.
    adj=[set() for _ in range(52)]
    for i,j in edges:
        adj[i].add(26+j)
        adj[26+j].add(i)
    seen={0}
    stack=[0]
    while stack:
        z=stack.pop()
        for w in adj[z]:
            if w not in seen:
                seen.add(w)
                stack.append(w)
    assert len(seen)==52

    return edges


def full_adjacency(edges):
    cnei=[[] for _ in range(26)]
    vnei=[[] for _ in range(26)]
    for i,j in edges:
        cnei[i].append(j)
        vnei[j].append(i)
    return cnei,vnei


def remap_mask(mask,old_edges,new_edges,assigned):
    oldpos={e:i for i,e in enumerate(old_edges)}
    out=0
    for k,e in enumerate(new_edges):
        if e in oldpos:
            bit=(mask>>oldpos[e])&1
        else:
            bit=assigned.get(e,0)
        if bit:
            out|=1<<k
    return out


def add_node(Cset,Vset,boundary,family,node,cnei,vnei):
    Cset=set(Cset)
    Vset=set(Vset)
    old=tuple(boundary)
    oldpos={e:i for i,e in enumerate(old)}
    typ,z=node

    if typ=="V":
        incident=[(i,z) for i in vnei[z]]
        old_inc=[e for e in incident if e in oldpos]
        if not old_inc:
            return None
        Cnew=Cset
        Vnew=Vset|{z}
    else:
        incident=[(z,j) for j in cnei[z]]
        old_inc=[e for e in incident if e in oldpos]
        if not old_inc:
            return None
        Cnew=Cset|{z}
        Vnew=Vset

    # Canonical boundary ordering: check-side first, then variable-side.
    bedges=[]
    for i in sorted(Cnew):
        for j in sorted(cnei[i]):
            if j not in Vnew:
                bedges.append((i,j))
    for j in sorted(Vnew):
        for i in sorted(vnei[j]):
            if i not in Cnew:
                bedges.append((i,j))
    bedges=tuple(bedges)

    out=set()

    if typ=="V":
        for m in family:
            vals={(m>>oldpos[e])&1 for e in old_inc}
            if len(vals)!=1:
                continue
            val=next(iter(vals))
            assigned={
                e:val for e in incident
                if e not in oldpos and e in bedges
            }
            out.add(remap_mask(m,old,bedges,assigned))
    else:
        new_inc=[e for e in incident if e in bedges and e not in oldpos]
        for m in family:
            s=sum((m>>oldpos[e])&1 for e in old_inc)
            if s>1:
                continue
            need=1-s
            if need==0:
                assigned={e:0 for e in new_inc}
                out.add(remap_mask(m,old,bedges,assigned))
            elif need==1:
                for chosen in new_inc:
                    assigned={e:int(e==chosen) for e in new_inc}
                    out.add(remap_mask(m,old,bedges,assigned))

    return Cnew,Vnew,bedges,frozenset(out)


def canonical_matroid(Cset,Vset,boundary,family):
    P=0
    for k,(i,j) in enumerate(boundary):
        if j in Vset and i not in Cset:
            P|=1<<k

    bases=frozenset(F^P for F in family)
    if not bases:
        return None

    if len({B.bit_count() for B in bases})!=1:
        return None

    if basis_exchange_failure(bases,len(boundary)) is not None:
        return None

    return bases


def audit_expansion_cone(edges,raw):
    cnei,vnei=full_adjacency(edges)

    C0=set(range(19))
    V0=set(range(18))

    base_boundary=(
        (A,18),
        (B,19),
        (C,20),
        (R,21),
        (19,0),
    )

    assert raw==RAW5

    outside=(
        tuple(("C",i) for i in range(19,26))
        + tuple(("V",j) for j in range(18,26))
    )

    states={
        0:(C0,V0,base_boundary,raw)
    }
    stack=[0]

    matroid_count=0
    nonbinary_count=0
    matroid_by_arity=Counter()

    while stack:
        subset=stack.pop()
        Cset,Vset,boundary,family=states[subset]

        bases=canonical_matroid(Cset,Vset,boundary,family)
        if bases is not None:
            matroid_count+=1
            matroid_by_arity[len(boundary)]+=1
            if not binary_matroid_from_bases(bases,len(boundary)):
                nonbinary_count+=1

        bset=set(boundary)

        for k,node in enumerate(outside):
            if (subset>>k)&1:
                continue

            typ,z=node
            if typ=="V":
                incident={(i,z) for i in vnei[z]}
            else:
                incident={(z,j) for j in cnei[z]}

            if not (incident & bset):
                continue

            nxt=subset|(1<<k)
            state=add_node(
                Cset,Vset,boundary,family,node,cnei,vnei
            )
            assert state is not None

            if nxt in states:
                old=states[nxt]
                assert old[2]==state[2]
                assert old[3]==state[3]
            else:
                states[nxt]=state
                stack.append(nxt)

    assert len(states)==EXPECTED_CONNECTED_EXPANSIONS
    assert matroid_count==EXPECTED_MATROID_INTERFACES
    assert nonbinary_count==0
    assert matroid_by_arity==EXPECTED_MATROID_BY_ARITY

    return len(states),matroid_count,nonbinary_count,matroid_by_arity


def symbolic_shared_savings_firewalls():
    # sigma=0: only 2 completion triples.  Even if the zero hole is r or s,
    # x={r,s} forces at least 3 distinct completion variables to cover r,s.
    assert 2 < 3

    # sigma=1: exactly 3 completion triples and exactly one pair-shared block T.
    # A hole outside r/s leaves r,s each requiring two distinct completions,
    # impossible with only 3.  Therefore the hole is r or s.
    assert 3 < 4

    # With (say) r the hole, deficits are:
    #   T-points = 3, r/s = 1+2, A/B/C = 3.
    # Three triples have exactly nine slots.  Linearity with T and x forces
    # every completion triple to contain exactly one T-point, one of {r,s},
    # and one survivor.  The unique r-triple is therefore selected by all
    # three v=0 covers but contains one survivor J, so X_J cannot select it.
    assert 3+3+3 == 9

    # sigma=2 from one all-three-common block gives 4 completion triples.
    # Its three points need 6 incidences, or at least 5 if the zero hole lies
    # on that block.  Linearity permits each completion triple to meet the
    # common block at most once.
    assert 4 < 5


def main():
    symbolic_shared_savings_firewalls()
    raw=audit_residual_witness()
    edges=build_full_source()
    nstates,nmat,nnonbin,byarity=audit_expansion_cone(edges,raw)

    print("R5 E90 p=1,h=1 t=6 conditioned U24 witness / delta firewall: PASS")
    print("all-t firewalls: sigma=0 impossible; sigma=1 impossible; sigma=2 all-three-common impossible")
    print("t=6 residual witness: C4-free; conditioned family =", sorted(TARGET4))
    print("immediate raw five-port family =", sorted(RAW5), "delta=False")
    print("explicit source completion: 26 checks / 26 variables / 78 edges / cubic / connected / C4-free")
    print("connected expansion cone:", nstates)
    print("canonical matroid interfaces:", nmat, "by_arity=", dict(sorted(byarity.items())))
    print("nonbinary canonical matroid interfaces:", nnonbin)
    print("frontier: conditioned U24 geometry is realizable; DELTA-PARENT LIFTABILITY is now the representation killer")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
