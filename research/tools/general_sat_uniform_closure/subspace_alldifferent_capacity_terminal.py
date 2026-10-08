#!/usr/bin/env python3
"""Basis-invariant subspace AllDifferent capacity terminal.

Motivation
----------
The existing Binary AllDifferent terminal recognizes bit-PHP when every
difference lineral is a weight-two XOR of corresponding bit variables.
That syntax is not affine invariant.

Apply any invertible linear transform T in GL(ell,2) independently to every
object's ell-bit address.  Pairwise inequality is unchanged semantically, but
the clause linerals become dense XORs and the weight-two recognizer returns
OPEN.

This terminal works on the clause NORMAL SUBSPACES instead.

Accepted linear normal form
---------------------------
Let every native XNF clause contain ell zero-constant independent linerals and
let L_c be their ell-dimensional normal span.

We recover a complete graph K_p on the clauses if:
  * there are C(p,2) clause subspaces;
  * for two edge-subspaces sharing an object, their sum contains exactly one
    third clause subspace (the third edge of the triangle);
  * this triangle relation reconstructs exactly p star cliques, each clause
    belonging to two stars;
  * choosing one root star, its p-1 incident subspaces form a direct sum;
  * every non-root edge subspace lies inside the sum of its two root-star
    blocks and is the graph of a linear isomorphism between them;
  * these isomorphisms satisfy triangle cocycle consistency.

Then any ambient assignment induces one ell-bit label per reconstructed object
(up to invertible coordinate transport).  A clause is false exactly when the
two endpoint labels agree.  Hence all clauses require p pairwise-distinct
labels from a domain of size 2^ell.

If p>2^ell, return a polynomial UNSAT capacity certificate.

This is scoped: unmatched arrangements return OPEN.
"""

from itertools import combinations
from math import isqrt

from bit_php_open_firewall import bphp_xnf
from binary_alldifferent_capacity_terminal import detect_complete_alldifferent
from two_sided_gaussian_probe_closure import two_sided_gaussian_probe_closure
from uniform_gaussian_implication_audit import rank_vectors


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
        if y==0:
            raise ValueError("dependent basis")
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
    if y:
        return None
    return coeff


def contained(A,B):
    """span(A) <= span(B)."""
    piv=elimination_for_basis(B) if B else {}
    return all(coords_in_basis(x,B,piv) is not None for x in A)


def dim_sum(A,B):
    return len(independent_basis(tuple(A)+tuple(B)))


def infer_p(m):
    # m=p(p-1)/2
    disc=1+8*m
    s=isqrt(disc)
    if s*s!=disc:
        return None
    if (1+s)%2:
        return None
    p=(1+s)//2
    return p if p*(p-1)//2==m else None


def clause_subspaces(source):
    if not source:
        return None
    widths={len(C) for C in source}
    if len(widths)!=1:
        return None
    ell=next(iter(widths))
    if ell<2:
        return None

    lines=[]
    for C in source:
        if any(const!=0 for _,const in C):
            return None
        B=independent_basis(mask for mask,_ in C)
        if len(B)!=ell:
            return None
        lines.append(B)
    return ell,tuple(lines)


def triangle_relation(lines):
    m=len(lines)
    third={}
    adj=[set() for _ in range(m)]

    # Polynomial O(m^3 * linear algebra); deliberately explicit/certifiable.
    for i in range(m):
        for j in range(i+1,m):
            S=independent_basis(lines[i]+lines[j])
            hits=[
                k for k in range(m)
                if k not in (i,j) and contained(lines[k],S)
            ]
            if len(hits)==1:
                k=hits[0]
                third[(i,j)]=k
                third[(j,i)]=k
                adj[i].add(j); adj[j].add(i)
            elif hits:
                # More than one third edge is not the accepted K_p arrangement.
                return None,None
    return tuple(frozenset(x) for x in adj),third


def reconstruct_stars(adj,third,p):
    m=len(adj)
    stars=set()

    for e in range(m):
        N=set(adj[e])
        if len(N)!=2*(p-2):
            return None
        if not N:
            return None
        f=min(N)

        side1={f}
        for g in N-{f}:
            if g in adj[f] and third.get((f,g))!=e:
                side1.add(g)
        side2=N-side1

        if len(side1)!=p-2 or len(side2)!=p-2:
            return None

        S1=frozenset({e}|side1)
        S2=frozenset({e}|side2)

        # Both must be cliques in the recovered line graph.
        for S in (S1,S2):
            if any(v not in adj[u] for u,v in combinations(S,2)):
                return None
            stars.add(S)

    if len(stars)!=p:
        return None

    stars=tuple(sorted(stars,key=lambda S:tuple(sorted(S))))

    # Every edge belongs to exactly two stars; every star pair meets in one edge.
    for e in range(m):
        if sum(e in S for S in stars)!=2:
            return None
    for A,B in combinations(stars,2):
        if len(A&B)!=1:
            return None

    return stars


def map_from_graph_subspace(L,Si,Sj,globalB,globalP,bi,bj,ell):
    """Return linear map Si-coordinates -> Sj-coordinates for L."""
    pairs=[]
    for v in L:
        c=coords_in_basis(v,globalB,globalP)
        if c is None:
            return None
        ai=(c>>(bi*ell)) & ((1<<ell)-1)
        aj=(c>>(bj*ell)) & ((1<<ell)-1)

        # No support outside the two endpoint blocks.
        outside=c ^ (ai<<(bi*ell)) ^ (aj<<(bj*ell))
        if outside:
            return None
        pairs.append((ai,aj))

    A=[a for a,_ in pairs]
    B=[b for _,b in pairs]
    if rank_vectors(A)!=ell or rank_vectors(B)!=ell:
        return None

    Ap=elimination_for_basis(tuple(A))
    images=[]
    for r in range(ell):
        coeff=coords_in_basis(1<<r,tuple(A),Ap)
        if coeff is None:
            return None
        out=0
        for i,b in enumerate(B):
            if (coeff>>i)&1:
                out ^= b
        images.append(out)

    # Verify every basis pair.
    for a,b in pairs:
        out=0
        for r,img in enumerate(images):
            if (a>>r)&1:
                out ^= img
        if out!=b:
            return None

    return tuple(images)


def apply_map(M,x):
    out=0
    for r,img in enumerate(M):
        if (x>>r)&1:
            out ^= img
    return out


def inverse_map(M,ell):
    A=tuple(M)
    if rank_vectors(A)!=ell:
        return None
    piv=elimination_for_basis(A)
    inv=[]
    for r in range(ell):
        coeff=coords_in_basis(1<<r,A,piv)
        if coeff is None:
            return None
        inv.append(coeff)
    # coeff is preimage in standard input coordinates.
    return tuple(inv)


def compose_maps(M1,M2):
    """M2 o M1."""
    return tuple(apply_map(M2,apply_map(M1,1<<r)) for r in range(len(M1)))


def detect_subspace_alldifferent(source):
    parsed=clause_subspaces(source)
    if parsed is None:
        return {"status":"OPEN","reason":"clause_subspace_parse_fail"}
    ell,lines=parsed
    m=len(lines)
    p=infer_p(m)
    if p is None or p<5:
        return {"status":"OPEN","reason":"clause_count_not_Kp_or_p_lt_5"}

    adj,third=triangle_relation(lines)
    if adj is None:
        return {"status":"OPEN","reason":"triangle_relation_fail"}

    stars=reconstruct_stars(adj,third,p)
    if stars is None:
        return {"status":"OPEN","reason":"line_graph_Kp_recovery_fail"}

    # Edge owner pair.
    owners={}
    for e in range(m):
        ids=[i for i,S in enumerate(stars) if e in S]
        if len(ids)!=2:
            return {"status":"OPEN","reason":"edge_owner_fail"}
        owners[e]=tuple(sorted(ids))

    root=0
    other=[i for i in range(p) if i!=root]

    root_edge={}
    for i in other:
        e=next(iter(stars[root]&stars[i]))
        root_edge[i]=e

    block_bases=[]
    for i in other:
        block_bases.append(lines[root_edge[i]])

    globalB=independent_basis(tuple(v for B in block_bases for v in B))
    if len(globalB)!=ell*(p-1):
        return {"status":"OPEN","reason":"root_star_not_direct_sum"}
    globalP=elimination_for_basis(globalB)

    block_index={obj:j for j,obj in enumerate(other)}

    maps={}
    for e,(i,j) in owners.items():
        if root in (i,j):
            continue
        bi=block_index[i]; bj=block_index[j]
        M=map_from_graph_subspace(
            lines[e],
            block_bases[bi],block_bases[bj],
            globalB,globalP,bi,bj,ell
        )
        if M is None:
            return {"status":"OPEN","reason":"edge_not_graph_isomorphism"}
        maps[(i,j)]=M
        inv=inverse_map(M,ell)
        if inv is None:
            return {"status":"OPEN","reason":"edge_map_not_invertible"}
        maps[(j,i)]=inv

    # Cocycle among all non-root object triples.
    for i,j,k in combinations(other,3):
        Mij=maps[(i,j)]
        Mjk=maps[(j,k)]
        Mik=maps[(i,k)]
        if compose_maps(Mij,Mjk)!=Mik:
            return {"status":"OPEN","reason":"transport_cocycle_fail"}

    if p>1<<ell:
        return {
            "status":"UNSAT",
            "reason":"SUBSPACE_ALLDIFFERENT_CAPACITY",
            "objects":p,
            "dimension":ell,
            "domain_size":1<<ell,
            "clause_count":m,
            "normal_span_rank":len(globalB),
            "star_count":len(stars),
        }

    return {
        "status":"OPEN",
        "reason":"SUBSPACE_ALLDIFFERENT_CAPACITY_NOT_VIOLATED",
        "objects":p,
        "dimension":ell,
        "domain_size":1<<ell,
    }


def unitriangular_rows(ell):
    rows=[]
    for b in range(ell):
        if b+1<ell:
            rows.append((1<<b)|(1<<(b+1)))
        else:
            rows.append(1<<b)
    assert rank_vectors(rows)==ell
    return tuple(rows)


def scrambled_bphp_xnf(ell):
    source,n0,_,p,h=bphp_xnf(ell)
    T=unitriangular_rows(ell)

    def object_row_mask(obj,rowmask):
        out=0
        for b in range(ell):
            if (rowmask>>b)&1:
                out ^= 1<<(obj*ell+b)
        return out

    clauses=[]
    # source has clauses in pair order; reconstruct directly to avoid relying
    # on standard weight-two masks.
    for i,j in combinations(range(p),2):
        C=[]
        for row in T:
            C.append((object_row_mask(i,row)^object_row_mask(j,row),0))
        clauses.append(tuple(C))

    return tuple(clauses),n0,p,h


def verify_scrambled_family():
    receipts=[]
    for ell in range(2,5):
        source,n0,p,h=scrambled_bphp_xnf(ell)

        # Old syntax-specific detector must reject the scrambling.
        old=detect_complete_alldifferent(source)
        assert old["status"]=="OPEN"

        new=detect_subspace_alldifferent(source)
        assert new["status"]=="UNSAT"
        assert new["objects"]==p
        assert new["dimension"]==ell
        assert new["domain_size"]==h

        receipts.append({
            "ell":ell,
            "objects":p,
            "domain":h,
            "old_detector":old["status"],
            "subspace_detector":new["status"],
            "normal_rank":new["normal_span_rank"],
        })

    # Probe one nontrivial scrambled sample: coordinate change must not turn a
    # global capacity contradiction into a false SAT claim.
    source,n0,p,h=scrambled_bphp_xnf(3)
    from php_scalable_open_firewall import xnf_to_2xnf
    F,n=xnf_to_2xnf(source,n0)
    st,E,A,stats=two_sided_gaussian_probe_closure(F,n)
    assert st!="SAT_LINEAR"

    return receipts,{
        "ell":3,
        "probe_status":st,
        "probe_learned_rank":len(E or ()),
        **stats,
    }


def main():
    receipts,probe=verify_scrambled_family()

    print("SUBSPACE ALLDIFFERENT CAPACITY TERMINAL: PASS")
    for r in receipts:
        print(r)
    print("scrambled ell=3 probing:",probe)
    print("terminal is invariant under invertible basis changes of object-address differences")
    print("recognition uses clause normal subspaces + K_p line-graph recovery + linear transport cocycle")
    print("no Boolean branching")
    print("terminal remains SCOPED; unmatched high-rank residues return OPEN")
    print("GENERAL_SAT_IN_P = NOT_PROVED")
    print("P_VS_NP = OPEN")


if __name__=="__main__":
    main()
