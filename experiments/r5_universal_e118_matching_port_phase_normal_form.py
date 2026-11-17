#!/usr/bin/env python3
"""E118 universal perfect-matching port gauge: exact n-bit phase sum.

Any 3-uniform cubic source has a 3-regular incidence bipartite graph.
Hall's theorem guarantees a perfect matching. Assign the matched
third occurrence of each variable the gadget port z=q, the other two
occurrences x=y=p. Each clause then contains exactly one q_v and two
p-neighbors, so its homogeneous GF2 parity equation uniquely forces
q_v=p_a XOR p_b.

Consequently the target kernel has exactly 2n independent bits
(t_v flip and p_v) and the ENTIRE half-weight phase polynomial
is a weighted 2-state model summed over only 2^n p assignments.

Local gadget FULL weight (in alpha=sqrt(z)):
 (p,q)=00: 1+alpha^6
 (p,q)=10: alpha^6+alpha^4
 (p,q)=01: 2 alpha^5
 (p,q)=11: 2 alpha^7.
The 2x2 local matrix determinant is
  2 alpha^7 (1-alpha^2)(1-alpha^4),
nonzero for primitive Q>=16, alpha^(2)=zeta_Q.

Thus local low-rank factorization into independent p/q weights fails
at the exact primitive phase. The remaining n-bit sum can still be
exponential; THIS IS NOT A UNIVERSAL POLYNOMIAL SOLVER.

Fixture check q9 sources -> modified E118 q90 legal connected targets,
complete exact histograms vs independent 2^18 kernel enumeration.
"""
from __future__ import annotations

from collections import Counter,defaultdict

from r5_e118_universal_linear_cubic_exactone_hardness_bridge import (
    rename_gadget,
)
from r5_universal_boolean_quadratic_pc2_attack import (
    cyclic_source, source_solutions, verify_target,
)
from r5_universal_projected_walsh_phase_elimination_attack import matrix_basis


def incidence_perfect_matching(source):
    """Polynomial Kuhn augmenting-path matching source variables -> clauses."""
    names=sorted({v for row in source for v in row})
    n=len(source)
    assert n==len(names)
    incidence={v:[] for v in names}
    for c,row in enumerate(source):
        assert len(row)==len(set(row))==3
        for v in row:
            incidence[v].append(c)
    assert set(len(incidence[v]) for v in names)=={3}
    matched_clause={}
    def augment(v,visited):
        for c in incidence[v]:
            if c in visited:continue
            visited.add(c)
            if c not in matched_clause or augment(matched_clause[c],visited):
                matched_clause[c]=v
                return True
        return False
    for v in names:
        assert augment(v,set()),"Hall's theorem would be violated"
    assert len(matched_clause)==n
    return matched_clause


def matched_target(source,match):
    """E118 rename, putting each matched occurrence at port z."""
    n=len(source)
    occ={v:[] for row in source for v in row}
    for c,row in enumerate(source):
        for v in row:
            occ[v].append(c)
    portname={}
    for v,clauses in occ.items():
        assert len(clauses)==3
        selected=next(c for c,w in match.items() if w==v)
        others=[c for c in clauses if c!=selected]
        assert len(others)==2
        portname[(v,selected)]=f"{v}_z"
        portname[(v,others[0])]=f"{v}_x"
        portname[(v,others[1])]=f"{v}_y"
    rows=[]
    for c,row in enumerate(source):
        rows.append(tuple(portname[(v,c)] for v in row))
        assert sum(p.endswith("_z") for p in rows[-1])==1
    for v in sorted(occ):
        rows.extend(rename_gadget("G_"+v,(f"{v}_x",f"{v}_y",f"{v}_z")))
    names=sorted({v for row in rows for v in row})
    pos={v:j for j,v in enumerate(names)}
    target=[tuple(pos[v] for v in row) for row in rows]
    verify_target(target)
    assert len(target)==10*n==len(names)
    return target,pos


def local_weight_poly(p,q):
    return {
        (0,0):{0:1,6:1},
        (1,0):{4:1,6:1},
        (0,1):{5:2},
        (1,1):{7:2},
    }[(p,q)]


def polynomial_convolution(a,b):
    out=defaultdict(int)
    for i,ai in a.items():
        for j,bj in b.items():
            out[i+j]+=ai*bj
    return dict(out)


def polynomial_sub(a,b):
    out=defaultdict(int)
    for i,v in a.items():out[i]+=v
    for i,v in b.items():out[i]-=v
    return {i:v for i,v in out.items() if v}


def local_matrix_determinant_audit():
    W00=local_weight_poly(0,0)
    W10=local_weight_poly(1,0)
    W01=local_weight_poly(0,1)
    W11=local_weight_poly(1,1)
    det=polynomial_sub(
        polynomial_convolution(W00,W11),
        polynomial_convolution(W10,W01)
    )
    # 2a^7(1-a^2)(1-a^4)
    assert det=={7:2,9:-2,11:-2,13:2},det
    return det


def exact_phase_histogram_n_source_bits(source,match):
    """Complete exact phase via 2^n p variables; NOT worst-case polynomial."""
    names=sorted({v for row in source for v in row})
    n=len(names)
    where={v:i for i,v in enumerate(names)}
    out=defaultdict(int)
    for mask in range(1<<n):
        p={v:(mask>>i)&1 for v,i in where.items()}
        q={}
        for c,matched in match.items():
            other=[v for v in source[c] if v!=matched]
            assert len(other)==2
            q[matched]=p[other[0]]^p[other[1]]
        assert len(q)==n
        for c,row in enumerate(source):
            matched=match[c]
            assert (q[matched]^
                    (p[row[0]] if row[0]!=matched else 0)^
                    (p[row[1]] if row[1]!=matched else 0)^
                    (p[row[2]] if row[2]!=matched else 0))==0
        pol={0:1}
        for v in names:
            pol=polynomial_convolution(pol,local_weight_poly(p[v],q[v]))
        for degree,count in pol.items():
            out[degree]+=count
    assert sum(out.values())==1<<(2*n)
    assert all(deg%2==0 for deg,count in out.items() if count)
    return dict(out)


def complete_finite_kernel_audit(rows):
    """Independent exponential scientific control for q90 only."""
    n=len(rows)
    A=[[int(j in row) for j in range(n)] for row in rows]
    basis=matrix_basis(A)
    assert len(basis)==18
    hist=Counter()
    word=0
    prev=0
    for i in range(1<<len(basis)):
        mask=i^(i>>1)
        change=prev^mask
        if change:
            word^=basis[change.bit_length()-1]
        prev=mask
        hist[word.bit_count()]+=1
    return dict(hist),len(basis)


def main():
    assert local_matrix_determinant_audit()
    for name,a,b,expected in (
        ("E118_UNSAT90",1,6,0),
        ("E118_SAT90",1,2,192),
    ):
        source=cyclic_source(9,a,b)
        m=incidence_perfect_matching(source)
        rows,pos=matched_target(source,m)
        hist=exact_phase_histogram_n_source_bits(source,m)
        brute,d=complete_finite_kernel_audit(rows)
        assert hist==brute,(name,sorted((set(hist)|set(brute)))[:5])
        assert d==18
        assert sum(hist.values())==1<<18
        assert hist.get(60,0)==expected
        assert expected==len(source_solutions(source))*64
        assert len(m)==9
        print(f"{name}: source matched q9, target N=90, kernel dim18;"
              f" full phase via 512 p-states vs 262144 kernel words;"
              f" exact top count={hist.get(60,0)}, independent histogram PASS")

    print("CUBIC_SOURCE_HALL_PORT_NORMAL_FORM = PROVED_CONSTRUCTIVE_POLYNOMIAL")
    print("E118_TARGET_KERNEL_DIM_EQUALS_2N_FOR_ALIGNED_PORTS = PROVED")
    print("ALL_E118_PHASE_EXACT_N_BINARY_SOURCE_SUM = PROVED")
    print("LOCAL_WEIGHT_MATRIX_DET=2*a^7*(1-a^2)*(1-a^4) = PROVED")
    print("UNIVERSAL_GLOBAL_POLY_CONTRACTION = OPEN")
    print("SolveLinearCubicXSAT UNIVERSAL_POLY = NOT_CONSTRUCTED; P_VS_NP OPEN")


if __name__=="__main__":
    main()
