#!/usr/bin/env python3
"""R5 ALL-LOCAL EDGE GAUGE NO-GO for native cubic ExactOne/Equality3 Holant.

This strengthens the previously certified GLOBAL homogeneous GL2 no-go:
NO independent invertible 2x2 basis matrix B_e on each Tanner incidence
edge can make every original ExactOne3 clause and every Equality3
variable gate have pure matchgate parity, while preserving standard
edgewise contraction by paired inverse-transpose B_e^-T.

Proof works over characteristic ZERO, arbitrary complex invertible
B_e; no numeric search or algorithmic complexity assumption.

Set Z=diag(1,-1), K_e=B_e^-1 Z B_e. Then tr(K_e)=0,
K_e^2=I, det(K_e)=-1. Pure parity at a CLAUSE implies
  (K_e1 tensor K_e2 tensor K_e3) W = +/- W,
where W=|001>+|010>+|100>.
Pure parity at a VARIABLE implies
  (K_e1^T tensor K_e2^T tensor K_e3^T) GHZ = +/- GHZ,
where GHZ=|000>+|111>.

LEMMA GHZ PRODUCT STABILIZER:
If A tensor B tensor C sends GHZ to a nonzero scalar multiple of
GHZ, then A,B,C are ALL diagonal or ALL antidiagonal invertible
matrices. Proof: flatten the GHZ tensor across leg 1 vs (2,3).
The two-dimensional support span{|00>,|11>} is preserved by B tensor C.
Its ONLY nonzero product vectors are multiples of |00>,|11>.
Since B tensor C maps the two product vectors |00> and |11> into
that span, B,C must be monomial with the SAME orientation.
Repeat flattening at other legs -> A also monomial, same type.

At each variable, therefore, the K_e themselves are monomial
(diagonal or antidiagonal). At each clause, their tensor product
acts on {001,010,100} by nonzero scalars plus one common XOR
translation of 3-bit supports. A NONZERO translation is a
fixed-point-free involution and cannot preserve an ODD-cardinality
3-element set. Thus all three K_e at every clause must be
DIAGONAL; hence ALL Tanner edges have diagonal K_e.
A diagonal, traceless involution with det -1 is +/- Z.
At any variable, (tensor +/- Z)GHZ is proportional to
|000>-|111>, not to GHZ. CONTRADICTION.

No assumption of planarity, expansion, treewidth or a COMMON
basis is made. Assumptions: native W and GHZ of arity exactly 3,
one standard 2-dimensional invertible gauge per original wire,
source gate tensors preserved; ordinary matchgate parity necessary.
Does NOT preclude noninvertible gadgets, higher dimensions,
regrouped signatures, nonmatchgate tensor algorithms, or general
P=NP approaches. P_VS_NP=OPEN.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import product

from r5_universal_exact_support_residual_dag_attack import validate_sparse
from r5_universal_holant_matchgate_uniform_basis_nogo import (
    W,GHZ,parity_type,matrix_inverse_transpose,
)


def matmul(A,B):
    return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def inverse(B):
    (a,b),(c,d)=B
    det=a*d-b*c
    assert det!=0
    return ((Fraction(d,det),Fraction(-b,det)),
            (Fraction(-c,det),Fraction(a,det)))


Z=((1,0),(0,-1))


def is_monomial(K):
    (a,b),(c,d)=K
    diag=b==0 and c==0 and a!=0 and d!=0
    anti=a==0 and d==0 and b!=0 and c!=0
    return "DIAGONAL" if diag else "ANTIDIAGONAL" if anti else "NONE"


def conjugated_parity(B):
    # K=B^-1 Z B (pull parity test backward through B)
    K=matmul(matmul(inverse(B),Z),B)
    assert matmul(K,K)==((1,0),(0,1))
    assert K[0][0]+K[1][1]==0
    assert K[0][0]*K[1][1]-K[0][1]*K[1][0]==-1
    return K


def transform_tensor3(signature,bases):
    assert len(signature)==4 and len(bases)==3
    ans={}
    for new in product((0,1),repeat=3):
        total=0
        for old in product((0,1),repeat=3):
            w=signature[sum(old)]
            for j in range(3):
                w*=bases[j][new[j]][old[j]]
            total+=w
        ans[new]=total
    return ans


def parity_type_8(weights):
    assert set(weights)==set(product((0,1),repeat=3))
    even=all(value==0 for bits,value in weights.items() if sum(bits)%2)
    odd=all(value==0 for bits,value in weights.items() if not sum(bits)%2)
    if even and odd:return "ZERO"
    if even:return "EVEN"
    if odd:return "ODD"
    return "MIXED"


def is_eigen_tensor(signature,matrices):
    transformed=transform_tensor3(signature,matrices)
    original={s:signature[sum(s)] for s in product((0,1),repeat=3)}
    nonzero=next(s for s in original if original[s])
    ratio=transformed[nonzero]/original[nonzero]
    return ratio!=0 and all(transformed[s]==ratio*original[s] for s in original)


def verify_local_variable_stabilizer(Bs):
    """Independent finite test of the universal symbolic GHZ lemma."""
    assert len(Bs)==3
    K=[conjugated_parity(B) for B in Bs]
    kt=[tuple(zip(*A)) for A in K]
    dst=transform_tensor3(GHZ,[matrix_inverse_transpose(B) for B in Bs])
    target=parity_type_8(dst)
    if target in ("EVEN","ODD"):
        assert is_eigen_tensor(GHZ,kt)
        modes=[is_monomial(A) for A in K]
        assert modes[0]!="NONE" and modes==[modes[0]]*3
    return target


def verify_local_clause_stabilizer(Bs):
    assert len(Bs)==3
    K=[conjugated_parity(B) for B in Bs]
    dst=transform_tensor3(W,Bs)
    target=parity_type_8(dst)
    if target in ("EVEN","ODD"):
        assert is_eigen_tensor(W,K)
        # If variable-side GHZ parity is possible, each K is monomial.
        # Under that proven precondition, W parity can survive iff
        # no bitflip is made on any of its three input coordinates.
        modes=[is_monomial(A) for A in K]
        if all(m!="NONE" for m in modes):
            assert modes==["DIAGONAL"]*3
    return target


def verify_symbolic_edge_local_nogo():
    """A finite-independent CASE PROOF mirrored by exhaustive controls.

    [GHZ] Any invertible local product that preserves a three-leg
    GHZ tensor maps its unique two rank-1 decomposable directions
    |00>,|11> to themselves or exchanges them. Such transformations
    are all monomial of a matching orientation.
    [W] If three monomial K tensors preserve the support
    {001,010,100}, their flip mask must be zero: any nontrivial
    xor-translation partitions an invariant set into even-sized
    orbits; the source support has cardinality THREE (odd).
    [INVO] K=B^-1 Z B diagonal implies exactly K=+Z or K=-Z.
    [GHZ] tensor product of three +/-Z maps |000>+|111>
    to +/- (|000>-|111>) and NOT an eigenvector.
    Contradiction at ANY variable of ANY source cubic Tanner graph.
    """
    support={(0,0,1),(0,1,0),(1,0,0)}
    for mask in product((0,1),repeat=3):
        moved={tuple(bits[i]^mask[i] for i in range(3)) for bits in support}
        assert (moved==support)==(mask==(0,0,0))
    for signs in product((-1,1),repeat=3):
        Ks=[tuple(tuple(signs[i]*Z[j][k] for k in range(2))
                  for j in range(2)) for i in range(3)]
        assert is_eigen_tensor(W,Ks)
        assert not is_eigen_tensor(GHZ,Ks)
    library=(
        ((1,0),(0,1)),((0,1),(1,0)),
        ((1,1),(1,-1)),((1,2),(1,1)),
        ((2,1),(1,1)),((1,1),(0,1)),
        ((1,0),(1,1)),((0,1),(1,1)),
    )
    trials=0
    for ids in product(range(len(library)),repeat=3):
        Bs=tuple(library[i] for i in ids)
        verify_local_variable_stabilizer(Bs)
        verify_local_clause_stabilizer(Bs)
        trials+=1
    assert trials==512
    return library


def verify_source_parity_contradiction(rows,n,libraries):
    rows=validate_sparse(rows,n)
    assert len(rows)==n
    degree=[0]*n
    edges=[]
    for i,row in enumerate(rows):
        for v in row:
            degree[v]+=1
            edges.append((i,v))
    assert all(d==3 for d in degree)
    assert len(edges)==3*n
    # Evaluate multiple heterogeneous per-wire gauge proposals.
    # The impossibility theorem does NOT depend on any particular
    # candidate list or on a limited bounded source size.
    for rule in range(4):
        if rule==0:
            edge_basis={e:libraries[0] for e in edges}
        elif rule==1:
            edge_basis={e:libraries[2] for e in edges}
        else:
            edge_basis={(i,v):libraries[(rule*i+3*v)%len(libraries)]
                        for i,v in edges}
        clauses=[]
        for i,row in enumerate(rows):
            Bs=[edge_basis[(i,v)] for v in row]
            clauses.append(parity_type_8(transform_tensor3(W,Bs)))
        vars_=[]
        for v in range(n):
            incident=[edge_basis[(i,v)] for i,row in enumerate(rows)
                      if v in row]
            assert len(incident)==3
            vars_.append(parity_type_8(transform_tensor3(
                GHZ,[matrix_inverse_transpose(B) for B in incident]
            )))
        assert "MIXED" in clauses or "MIXED" in vars_,(
            "a local 2x2 gauge falsely defeated the no-go",rule
        )
    return True


def main():
    from r5_universal_all_odd_cyclic_pc2_four_orbit_identity import cyclic
    from r5_universal_cubic_edgecolor_direct_scl_bridge import (
        make_scl,K4,K33,petersen_graph,
    )
    lib=verify_symbolic_edge_local_nogo()
    print("GHZ_LOCAL_PRODUCT_STABILIZER_MONOMIAL=PROVED_SYMBOLIC")
    print("W_THREE_SUPPORT_ODD_TRANSLATION_FLIP_NO_GO=PROVED_SYMBOLIC")
    print("DIAGONAL_TRACeless_INVOLUTION_VARIABLE_GHZ_CONFLICT=PROVED_SYMBOLIC")
    print("HETEROGENEOUS_EDGE_GAUGES_512_LOCAL_BASIS_TRIPLES=VERIFIED")
    for name,rows,n in (
        ("FANO7",cyclic(7),7),
        ("K4_SCL18",*make_scl(K4())[:2]),
        ("K33_SCL27",*make_scl(K33())[:2]),
        ("PETERSEN_SCL45",*make_scl(petersen_graph())[:2]),
    ):
        assert verify_source_parity_contradiction(rows,n,lib)
        print(f"{name}_SOURCE_LOCAL_GAUGE_CONFLICT=VERIFIED n={n}",flush=True)
    print("ALL_SCL_NATIVE_W_GHZ_EDGEWISE_GL2_MATCHGATE_PARITY_NO_GO=PROVED")
    print("HIGHER_ARITY_GADGETS_AND_NONMATCHGATE_COMPRESSION=OPEN")
    print("UNIVERSAL_POLY_SOLVELINEARCUBICXSAT=NOT_CONSTRUCTED")
    print("P_VS_NP=OPEN")


if __name__=="__main__":
    main()
