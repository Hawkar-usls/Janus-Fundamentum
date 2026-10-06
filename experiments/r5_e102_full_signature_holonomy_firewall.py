#!/usr/bin/env python3
"""R5 E102: full four-candidate local-signature + holonomy firewall.

This experiment audits the E96 global extrapolation before using it for the
rigid-free rectangle-holonomy step.

Six TARGET6 labels:
  0=XA, 1=XB, 2=XC, 3=QAB, 4=QAC, 5=QBC.

The E95 base state8 parity candidate selects a variable iff its support across
the six witnesses has even cardinality.

The two target-derived zero-boundary kernel corrections are
  h1 = parity on D1={0,1,4,5}
  h2 = parity on D2={0,2,3,5}.

For EVERY ordinary check, its three variable supports partition the six
labels.  There are 122 unlabeled 3-bin partitions (empty bins allowed).

For each partition P define Good(P) subset GF(2)^2:
  k=(a,b) is Good iff the corrected E95 assignment e+a*h1+b*h2 selects
  exactly one of the three incident variables.

Complete exhaustive classification gives exactly 12 local signature sets:

  rigid base defects:
    empty                                      : 5

  base defects:
    {k != 0}                                  : 8
    H_a^1={k: k.a=1}, three directions         : 6 each

  base-good checks:
    GF(2)^2                                   : 28
    H_a^0={k: k.a=0}, three directions         : 9 each
    GF(2)^2 \ {q}, q nonzero, three choices   : 12 each

Thus the E96 LOCAL defect classification remains correct:
  31 all-even partitions = 5 + 18 + 8.

But its earlier GLOBAL extrapolation is invalid:
a correction that repairs every base defect can create a new defect on a
base-good check.  In particular H_a^0 and H_a^1 are disjoint, so two locally
legal non-rigid checks can already eliminate all four GLOBAL corrections
without requiring all three E96 proper-conflict types.

Holonomy localization:
For fixed six TARGET6 witnesses, color every variable by
    c(v)=(h1(v),h2(v)) in GF(2)^2.
At every check the xor of the three colors is 00.  Since both h1,h2 have zero
boundary syndrome, every connected component of nonzero-color variables
supports independent restricted kernel corrections
    z_C,k(v)=k.c(v), k in GF(2)^2.
All nonzero variables of any check lie in one such component.

If a check has all colors zero and the E95 base candidate is defective, then
all three supports are even and h=00; this forces all three supports to be
unions of opposite atoms, hence the check is exactly an E96 rigid defect.

Therefore, in a rigid-free TARGET6 geometry, raw state8 follows whenever each
nonzero-color component C has
    intersection_{checks touching C} Good(P_check) != empty.
A no-state8 counterexample must contain a BAD HOLONOMY COMPONENT with empty
intersection.

At pure signature level (excluding the rigid empty signature), the 11 possible
nonempty Good-sets have exactly:
  3 minimal empty-intersection families of size 2,
  22 of size 3,
  1 of size 4.
The three size-2 obstructions are precisely H_a^0 versus H_a^1.

E102-C constructive router identification:
E100's B3 allowed boundary layer has size at most 3, and the three canonical
atom covers reveal a nonempty subset of that layer.  Therefore at most TWO
additional boundary-membership queries determine the exact router relation.
Once known, E101 constructs the constant-size representation immediately.
Those membership queries are not yet known to be polynomial-time.

P_VS_NP remains OPEN.
"""

from itertools import product, combinations
from collections import Counter

U=frozenset(range(6))
D1=frozenset({0,1,4,5})
D2=frozenset({0,2,3,5})
OPPOSITE=(
    frozenset({0,5}),
    frozenset({1,4}),
    frozenset({2,3}),
)
K=((0,0),(1,0),(0,1),(1,1))
NZ=((1,0),(0,1),(1,1))
TARGET_MASKS=(1,2,4,19,21,22)


def dot(x,y):
    return (x[0]*y[0] + x[1]*y[1]) & 1


def canonical_partition(blocks):
    return tuple(sorted(tuple(sorted(b)) for b in blocks))


def all_partitions():
    out=set()
    for assignment in product(range(3), repeat=6):
        blocks=[
            frozenset(i for i,x in enumerate(assignment) if x==k)
            for k in range(3)
        ]
        out.add(canonical_partition(blocks))
    return tuple(sorted(out))


def hcolor(S):
    S=frozenset(S)
    return (
        len(S & D1) & 1,
        len(S & D2) & 1,
    )


def base_bit(S):
    return 1 if len(S)%2==0 else 0


def corrected_bit(S,k):
    c=hcolor(S)
    return base_bit(S) ^ dot(k,c)


def good_set(partition):
    out=[]
    for k in K:
        if sum(corrected_bit(S,k) for S in partition)==1:
            out.append(k)
    return frozenset(out)


def inert(S):
    S=frozenset(S)
    return all(len(S&A) in (0,2) for A in OPPOSITE)


def classify_expected_sets():
    H0={a:frozenset(k for k in K if dot(k,a)==0) for a in NZ}
    H1={a:frozenset(k for k in K if dot(k,a)==1) for a in NZ}
    N0=frozenset(NZ)
    Nq={q:frozenset(k for k in K if k!=q) for q in NZ}
    return H0,H1,N0,Nq


def verify_full_local_table():
    parts=all_partitions()
    assert len(parts)==122

    counts=Counter(good_set(p) for p in parts)
    H0,H1,N0,Nq=classify_expected_sets()
    EMPTY=frozenset()
    FULL=frozenset(K)

    assert counts[EMPTY]==5
    assert counts[N0]==8
    assert counts[FULL]==28
    for a in NZ:
        assert counts[H1[a]]==6
        assert counts[H0[a]]==9
    for q in NZ:
        assert counts[Nq[q]]==12
    assert sum(counts.values())==122
    assert len(counts)==12

    # E96's local base-defect classification remains exact.
    base_defects=[
        p for p in parts
        if sum(base_bit(S) for S in p)==3
    ]
    assert len(base_defects)==31
    assert Counter(good_set(p) for p in base_defects)[EMPTY]==5
    assert sum(1 for p in base_defects if good_set(p)==N0)==8
    assert sum(1 for p in base_defects if good_set(p) in set(H1.values()))==18

    # The five empty signatures are exactly rigid opposite-atom coarsenings.
    rigid=[p for p in parts if good_set(p)==EMPTY]
    assert len(rigid)==5
    for p in rigid:
        assert all(inert(S) for S in p)
        assert all(len(S)%2==0 for S in p)

    # Every local partition has h-color xor zero.
    for p in parts:
        x=(0,0)
        for S in p:
            c=hcolor(S)
            x=(x[0]^c[0],x[1]^c[1])
        assert x==(0,0)

    return parts,counts,H0,H1,N0,Nq


def verify_e96_global_extrapolation_firewall(parts,H0,H1):
    # Find an explicit same-direction anti-conflict/conflict pair:
    # one base-good H_a^0 check and one base-defect H_a^1 check.
    for a in NZ:
        p0=next(p for p in parts if good_set(p)==H0[a])
        p1=next(p for p in parts if good_set(p)==H1[a])
        assert good_set(p0) & good_set(p1) == frozenset()
        assert sum(base_bit(S) for S in p0)==1
        assert sum(base_bit(S) for S in p1)==3
        # Neither is rigid.
        assert good_set(p0)
        assert good_set(p1)
    return True


def verify_zero_color_even_implies_inert():
    # If h(S)=00 then the three opposite-pair parities are equal.
    # Even |S| then forces that common parity to zero, hence S is a union of
    # whole opposite atoms.
    for mask in range(64):
        S=frozenset(i for i in range(6) if (mask>>i)&1)
        if hcolor(S)!=(0,0) or len(S)%2:
            continue
        assert inert(S)


def verify_minimal_signature_obstructions(counts):
    sigs=tuple(sorted(
        (G for G in counts if G),
        key=lambda G:(len(G),tuple(sorted(G)))
    ))
    assert len(sigs)==11

    minimal=[]
    for r in range(2,5):
        for fam in combinations(range(len(sigs)),r):
            inter=set(K)
            for i in fam:
                inter &= set(sigs[i])
            if inter:
                continue
            ok=True
            for j in fam:
                inter2=set(K)
                for i in fam:
                    if i!=j:
                        inter2 &= set(sigs[i])
                if not inter2:
                    ok=False
                    break
            if ok:
                minimal.append(fam)

    sizes=Counter(len(f) for f in minimal)
    assert sizes==Counter({3:22,2:3,4:1})

    H0,H1,_,_=classify_expected_sets()
    pair_obstructions=[]
    for fam in minimal:
        if len(fam)!=2:
            continue
        A,B=(sigs[i] for i in fam)
        pair_obstructions.append(frozenset((A,B)))
    expected={
        frozenset((H0[a],H1[a]))
        for a in NZ
    }
    assert set(pair_obstructions)==expected
    return sizes


def verify_boundary_zero_syndrome():
    # D1,D2 are the four-state XOR dependencies used for h1,h2.
    x1=0
    for i in D1:
        x1 ^= TARGET_MASKS[i]
    x2=0
    for i in D2:
        x2 ^= TARGET_MASKS[i]
    assert x1==0
    assert x2==0


def verify_router_query_bound():
    # Residue-0 E100 layer has 2 states; rank-1/rank-2 layers have 3.
    # Three canonical atom covers always reveal >=1 distinct feasible state.
    # Query every still-unseen layer state: at most 2 binary membership queries.
    max_queries=0
    for layer_size in (2,3):
        for image_size in range(1, min(3,layer_size)+1):
            max_queries=max(max_queries,layer_size-image_size)
    assert max_queries==2
    return max_queries


def main():
    parts,counts,H0,H1,N0,Nq=verify_full_local_table()
    verify_e96_global_extrapolation_firewall(parts,H0,H1)
    verify_zero_color_even_implies_inert()
    sizes=verify_minimal_signature_obstructions(counts)
    verify_boundary_zero_syndrome()
    q=verify_router_query_bound()

    print("R5 E102 full local-signature / holonomy firewall: PASS")
    print("all ordinary six-witness support partitions=122")
    print("complete Good-set signature types=12")
    print("E96 base-defect local classification preserved: 31=5 rigid+18 proper+8 all-repair")
    print("E96 global three-conflict extrapolation SUPERSEDED: base-good checks can create anti-conflict restrictions")
    print("minimal non-rigid signature obstruction sizes:",dict(sizes))
    print("size-2 holonomy obstructions=3, exactly H_a^0 versus H_a^1")
    print("rigid-free no-state8 parent => at least one bad nonzero-color holonomy component")
    print("E102-C exact B3 router identification needs at most",q,"additional boundary-membership queries")
    print("polynomial implementation of those membership queries remains OPEN")
    print("next target: geometry-kill bad holonomy components, starting with the 2-check signed phase clash")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
