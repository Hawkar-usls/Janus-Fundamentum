#!/usr/bin/env python3
"""R5 E105: NO-RAW8 <=> affine-flat cover of the full zero-boundary kernel.

Fix six TARGET6 witnesses and let e be the E95 even-occurrence parity
candidate for boundary raw8.

Let K0 be the GF(2) zero-boundary kernel:
  * parity zero at every internal/check-side row, including A,B,C,E;
  * special variable-side boundary variable x fixed to zero.

For any z in K0, e xor z has the SAME raw8 boundary parity.

At every ordinary cubic check c:
  * z restricted to its three incident variables has even parity, so it is one
    of 000,110,101,011;
  * e restricted there has odd parity, so it has weight 1 or 3;
  * exactly ONE even z-pattern makes e xor z = 111, namely
        f_c = 111 xor e|_c.

Therefore define the forbidden flat
    B_c = { z in K0 : z|_c = f_c }.
It is empty or an affine subspace/coset of K0 with codimension at most 2.

Boundary rows cannot create an integer defect:
  * A,B,C have internal degree 2, so odd parity means exactly one;
  * E has x=0 and the zero-boundary kernel forces the other internal neighbour
    unchanged as well;
  * V is fixed by z_x=0.

Hence the universal exact equivalence is

    raw8 feasible
      <=> exists z in K0 outside union_c B_c,

    NO_RAW8
      <=> K0 = union_c B_c.

Choose a basis t in GF(2)^d for K0.  For each nonempty rank-2 local image,
B_c is the simultaneous solution of two affine linear equations
    l_c1(t)=alpha_c, l_c2(t)=beta_c.
Avoiding B_c is one OR-clause of affine parity predicates:
    (l_c1 != alpha_c) OR (l_c2 != beta_c),
equivalently one rank-one quadratic equation over GF(2).
Ranks 0/1 are degenerate constant/unit-clause cases.

E104 replay:
  zero-boundary kernel dimension d=3;
  exactly 8 raw8-parity words exist;
  4 are exact raw8 witnesses and 4 are defective;
  the four exact witnesses are NOT contained in the E102 constant-phase span.
This freezes that full-kernel repair is genuinely stronger than h1/h2 holonomy
repair.

P_VS_NP remains OPEN.
"""

from itertools import product

from r5_e104_pairwise_minimal_phase_clash_firewall import (
    TARGETS,
    build_combined,
    check_neighbors,
    verify_target_witnesses,
    enumerate_boundary_witnesses,
)


def gf2_rank(rows,n):
    rows=list(rows)
    rank=0
    for col in range(n):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=rows[rank]
        rank+=1
        if rank==len(rows):
            break
    return rank


def gf2_nullspace(rows,n):
    rows=[r for r in rows if r]
    rank=0
    piv=[]
    for col in range(n):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=rows[rank]
        piv.append(col)
        rank+=1

    free=[c for c in range(n) if c not in set(piv)]
    basis=[]
    for f in free:
        x=1<<f
        for i,p in enumerate(piv):
            if (rows[i]>>f)&1:
                x |= 1<<p
        basis.append(x)
    return tuple(basis)


def set_to_mask(S):
    m=0
    for x in S:
        m |= 1<<x
    return m


def mask_to_set(m,n):
    return frozenset(i for i in range(n) if (m>>i)&1)


def kernel_words(basis):
    out=[]
    for coeff in product((0,1),repeat=len(basis)):
        z=0
        for a,b in zip(coeff,basis):
            if a:
                z ^= b
        out.append((coeff,z))
    return tuple(out)


def e95_candidate(support):
    return frozenset(
        v for v,S in enumerate(support)
        if len(S)%2==0
    )


def local_bits(S,N):
    return tuple(int(v in S) for v in sorted(N))


def xor_bits(a,b):
    return tuple(x^y for x,y in zip(a,b))


def defect_checks(cn,e,zset):
    out=[]
    for q,N in enumerate(cn):
        if q in (0,1,2,17):
            continue
        eb=local_bits(e,N)
        zb=local_bits(zset,N)
        final=xor_bits(eb,zb)
        assert sum(final) in (1,3)
        if sum(final)==3:
            out.append(q)
    return tuple(out)


def verify_universal_local_truth_table():
    even=((0,0,0),(1,1,0),(1,0,1),(0,1,1))
    odd=tuple(x for x in product((0,1),repeat=3) if sum(x)%2==1)

    for e in odd:
        bad=[]
        for z in even:
            w=xor_bits(e,z)
            if sum(w)==3:
                bad.append(z)
            else:
                assert sum(w)==1
        assert bad==[tuple(1^x for x in e)]


def local_image_rank(basis,N):
    coords=tuple(sorted(N))
    vecs=[]
    for b in basis:
        pattern=tuple((b>>v)&1 for v in coords)
        # store first two coordinates; third is their xor because K0 has
        # even parity on the check.
        vecs.append(pattern[:2])

    rows=[]
    for j in range(2):
        row=0
        for i,v in enumerate(vecs):
            if v[j]:
                row |= 1<<i
        rows.append(row)
    return gf2_rank(rows,len(basis))


def verify_e104_replay():
    vn,support=build_combined()
    cn=check_neighbors(vn)
    labelled=verify_target_witnesses(cn,support)

    n=len(vn)
    # Full zero-boundary parity kernel: all check rows plus V-variable x=17.
    rows=[]
    for N in cn:
        rows.append(set_to_mask(N))
    rows.append(1<<17)

    basis=gf2_nullspace(rows,n)
    assert len(basis)==3
    assert len(kernel_words(basis))==8

    e=e95_candidate(support)
    em=set_to_mask(e)

    # h1/h2 from the chosen six witnesses, as in E96/E102.
    D1=frozenset({0,1,4,5})
    D2=frozenset({0,2,3,5})
    h1=frozenset(v for v,S in enumerate(support) if len(S&D1)%2)
    h2=frozenset(v for v,S in enumerate(support) if len(S&D2)%2)
    hspan={
        0,
        set_to_mask(h1),
        set_to_mask(h2),
        set_to_mask(h1)^set_to_mask(h2),
    }
    assert len(hspan)<8

    # Exact raw8 fiber from independent exact-cover enumeration.
    exact8=set(map(set_to_mask,enumerate_boundary_witnesses(vn,8)))
    assert len(exact8)==4

    avoided=[]
    covered=[]
    flat_sizes=[]
    ranks=[]

    # Precompute forbidden local patterns f_c = 111 xor e_c.
    ordinary=[q for q in range(len(cn)) if q not in (0,1,2,17)]
    forbidden={}
    for q in ordinary:
        N=tuple(sorted(cn[q]))
        eb=local_bits(e,N)
        assert sum(eb) in (1,3)
        forbidden[q]=tuple(1^x for x in eb)
        ranks.append(local_image_rank(basis,cn[q]))

    # Every z in K0 is covered by a forbidden flat iff e xor z is defective.
    for coeff,z in kernel_words(basis):
        zset=mask_to_set(z,n)
        bad=defect_checks(cn,e,zset)

        flat_hits=[]
        for q in ordinary:
            if local_bits(zset,cn[q])==forbidden[q]:
                flat_hits.append(q)
        assert tuple(flat_hits)==bad

        candidate=em^z
        if bad:
            covered.append(z)
            assert candidate not in exact8
        else:
            avoided.append(z)
            assert candidate in exact8

    assert len(avoided)==4
    assert len(covered)==4
    assert {em^z for z in avoided}==exact8

    # The exact raw8 witnesses require full-kernel directions beyond h1/h2.
    assert all(z not in hspan for z in avoided)

    # Local images have rank at most two, exactly as the theorem states.
    assert all(r in (0,1,2) for r in ranks)

    return {
        "dim_K0":len(basis),
        "parity_words":len(kernel_words(basis)),
        "exact_raw8":len(exact8),
        "defective_raw8_parity":len(covered),
        "hspan_size":len(hspan),
        "local_rank_counts":{r:ranks.count(r) for r in (0,1,2)},
    }


def main():
    verify_universal_local_truth_table()
    stats=verify_e104_replay()

    print("R5 E105 NO-RAW8 affine-flat kernel-cover normal form: PASS")
    print("universal local truth table: each ordinary check forbids exactly one even kernel pattern")
    print("NO_RAW8 iff forbidden check preimages cover the full zero-boundary kernel")
    print("basis form: avoid one affine codim<=2 flat per ordinary check")
    print("equivalently: conjunction of ORs of affine parity predicates / rank-one quadratic constraints")
    print("E104 replay:",stats)
    print("all four E104 exact raw8 repairs lie outside the E102 constant-phase h-span")
    print("next target: exploit C4-free/cubic structure of this affine-flat cover; generic flat avoidance alone is not enough")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
