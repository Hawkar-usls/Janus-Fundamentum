#!/usr/bin/env python3
"""R5 E4.7 — BASE_Z_AUDIT + RATIONAL_NULLITY_FILTER.

Independent, Python-stdlib-only check on frozen SCL base. Reads
a declarative JSON fixture, never imports project research modules.

THEOREM (ALL n): Z(A)={nonzero z in ker_GF2(A):Y_z!=empty}
depends ONLY on A, not on 2-lift signs. If |Z(A)|<=1,
NO voltage assignment on any graph 2-cover has multiple
relevant nonzero XOR directions.

THEOREM (ALL n, connectedness not needed): On an UNSAT base,
if two distinct ternary y,y' solve Ay=2*1 (over integers),
rational nullity(A)>=2. Proof: y-2/3*1 ∈ ker_Q A;
all values 0,1,2 occur for each y if base is UNSAT,
and the only scalar lambda preserving the ternary alphabet
in y'=2/3*1+lambda(y-2/3*1) is lambda=1.

Finite 36-source audit:
- Independently compute integer/rational elimination rank,
  a 33x33 nonzero minor via fraction-free Bareiss,
  3 explicit rational kernel basis vectors;
- Independently compute entire GF2 kernel with low-pivot
  binary RREF, 63 nonzero physical directions;
- Compute exact residual Y_z twice using ALGORITHMICALLY
  DIFFERENT methods: uncovered-row exact-cover DFS and a
  disjoint-mask column-product dynamic program.
- For each solution reconstruct ternary y and check ALL
  original integer clause sums, check parity y mod2=z.
- Every z receives an explicit EXACT verdict, never UNKNOWN;
  the full per-direction table is emitted as JSON.
- Cross-check original frozen z_star and only allowed y.
Not a polynomial all-n SAT solver (enumerates 2^d GF2 kernel).
"""
import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path


def check_rows(rows):
    n=len(rows)
    assert n%3==0 and len(rows)==n
    assert all(len(row)==3 and len(set(row))==3 and
               all(0<=j<n for j in row) for row in rows)
    degree=[0]*n
    pairs=set()
    for row in rows:
        for j in row:degree[j]+=1
        for p in combinations(sorted(row),2):
            assert p not in pairs
            pairs.add(p)
    assert set(degree)=={3}
    return n


def low_pivot_kernel(bitin,width):
    rows=[int(v) for v in bitin]
    pivots=[]
    rank=0
    for col in range(width):
        target=next((i for i in range(rank,len(rows))
                     if (rows[i]>>col)&1),None)
        if target is None:continue
        rows[rank],rows[target]=rows[target],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=rows[rank]
        pivots.append(col)
        rank+=1
    free=sorted(set(range(width))-set(pivots))
    basis=[]
    for j in free:
        v=1<<j
        for i,k in enumerate(pivots):
            if (rows[i]>>j)&1:v|=1<<k
        assert all(((r&v).bit_count()%2)==0 for r in bitin)
        basis.append(v)
    return rank,tuple(basis)


def rational_rref(A):
    n=len(A)
    mat=[[Fraction(a) for a in row] for row in A]
    original_row_index=list(range(n))
    pivots=[]
    selected_original_rows=[]
    rank=0
    for col in range(n):
        k=next((i for i in range(rank,n) if mat[i][col]),None)
        if k is None:continue
        mat[rank],mat[k]=mat[k],mat[rank]
        original_row_index[rank],original_row_index[k]=(
            original_row_index[k],original_row_index[rank])
        selected_original_rows.append(original_row_index[rank])
        den=mat[rank][col]
        mat[rank]=[v/den for v in mat[rank]]
        for i in range(n):
            if i!=rank and mat[i][col]:
                scalar=mat[i][col]
                mat[i]=[x-scalar*y for x,y in
                        zip(mat[i],mat[rank])]
        pivots.append(col)
        rank+=1
    free=sorted(set(range(n))-set(pivots))
    basis=[]
    for j in free:
        vec=[Fraction(0)]*n
        vec[j]=Fraction(1)
        for i,p in enumerate(pivots):
            vec[p]=-mat[i][j]
        assert all(sum(Fraction(v)*vec[k] for k,v in enumerate(row))
                   ==0 for row in A)
        basis.append(vec)
    return rank,pivots,selected_original_rows,basis


def determinant_bareiss(M):
    """Integer-only fraction-free independent determinant cross-check."""
    n=len(M)
    W=[list(map(int,row)) for row in M]
    sign=1
    prev=1
    for k in range(n-1):
        if W[k][k]==0:
            swap=next((i for i in range(k+1,n) if W[i][k]),None)
            if swap is None:return 0
            W[k],W[swap]=W[swap],W[k]
            sign=-sign
        pivot=W[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                x=W[i][j]*pivot-W[i][k]*W[k][j]
                assert x%prev==0
                W[i][j]=x//prev
        for i in range(k+1,n):
            W[i][k]=0
        prev=pivot
    return sign*W[-1][-1]


def residual_two_ways(rows,z):
    n=len(rows)
    S={i for i in range(n) if ((z>>i)&1)}
    R0=[i for i,row in enumerate(rows) if not S.intersection(row)]
    R2=[i for i,row in enumerate(rows) if len(S.intersection(row))==2]
    assert len(R0)+len(R2)==n and 2*len(R2)==3*len(S)
    assert len(S)%2==0
    p=n//3-len(S)//2
    if p<0:
        assert len(R0)<0 or False  # this case impossible for legal kernel
    indexed={i:j for j,i in enumerate(R0)}
    full=(1<<len(R0))-1
    neighbor=[set(i for i,row in enumerate(rows) if v in row)
              for v in range(n)]
    r0set=set(R0)
    clean=[v for v in range(n) if v not in S and
           neighbor[v].issubset(r0set)]
    masks={v:sum(1<<indexed[i] for i in neighbor[v])
           for v in clean}
    options={i:[v for v in clean if i in neighbor[v]]
             for i in R0}
    assert all(len(opts)<=3 for opts in options.values())
    # Method A: exact cover by first uncovered row, with
    # independent integer-verification of every completed y.
    solutions=[]
    calls=0
    def dfs(uncovered,chosen):
        nonlocal calls
        calls+=1
        if not uncovered:
            assert len(chosen)==p
            selected=tuple(sorted(chosen))
            y=[int(v in S)+2*int(v in selected) for v in range(n)]
            assert all(sum(y[v] for v in row)==2 for row in rows)
            assert all((y[v]&1)==((z>>v)&1) for v in range(n))
            solutions.append(selected)
            return
        i=next(j for j in R0 if uncovered&(1<<indexed[j]))
        for v in options[i]:
            mask=masks[v]
            if uncovered&mask==mask:
                dfs(uncovered^mask,chosen+[v])
    dfs(full,[])
    assert len(solutions)==len(set(solutions))
    # Method B: polynomial-product DP over all clean columns.
    # Each column factor is (1+product of its row-indeterminates)
    # modulo row-variable squares. An exact cover equals the
    # coefficient at the full row-set monomial.
    dp={0:1}
    for v in clean:
        mask=masks[v]
        for have,coef in tuple(dp.items()):
            if have&mask==0:
                dest=have|mask
                dp[dest]=dp.get(dest,0)+coef
    assert dp.get(full,0)==len(solutions)
    return {"z_decimal":str(z),"z_weight":len(S),
            "p":p,"R0_rows":R0,"clean_cols":clean,
            "Y_count":len(solutions),
            "Y_dfs":len(solutions),
            "Y_squarefree_polynomial_DP":dp.get(full,0),
            "Y_exact_covers":[list(v) for v in solutions],
            "DFS_nodes":calls,
            "polynomial_DP_states":len(dp),
            "verdict":"EXACT"}


def replay(fixture_path):
    src=json.loads(Path(fixture_path).read_text())
    assert src["version"]=="R5_E46_FROZEN_CLEAN_ROOM_1"
    rows=tuple(tuple(row) for row in src["base_rows"])
    n=check_rows(rows)
    A=[[int(j in row) for j in range(n)] for row in rows]
    bitrows=[sum(1<<j for j in row) for row in rows]
    rank2,basis=low_pivot_kernel(bitrows,n)
    assert (n,rank2,len(basis))==(36,30,6)
    rankq,pivots,oldrows,qbasis=rational_rref(A)
    assert rankq==33 and len(qbasis)==3
    minor=[[A[i][j] for j in pivots] for i in oldrows]
    det=determinant_bareiss(minor)
    assert det!=0
    zs=[0]
    for b in basis:
        zs.extend([z^b for z in tuple(zs)])
    assert len(zs)==64 and len(set(zs))==64
    results=[]
    for z in sorted(zs):
        if z==0:continue
        assert all((z&r).bit_count()%2==0 for r in bitrows)
        results.append(residual_two_ways(rows,z))
    assert len(results)==63
    good=[r for r in results if r["Y_count"]]
    assert len(good)==1
    star=int(src["z_star_bits_decimal"])
    assert good[0]["z_decimal"]==str(star)
    assert good[0]["Y_count"]==1
    assert good[0]["Y_exact_covers"]==[[1,16]]
    orig_y=src["ternary_y"]
    assert sum(1 for v in orig_y if v==1)==20
    assert sum(1 for v in orig_y if v==2)==2
    assert sum(1 for v in orig_y if v==0)==14
    assert all(sum(orig_y[v] for v in row)==2 for row in rows)
    assert sum(1<<v for v,val in enumerate(orig_y) if val&1)==star
    hist=Counter(r["z_weight"] for r in results)
    zero=Counter(r["z_weight"] for r in results if not r["Y_count"])
    total_dfs=sum(r["DFS_nodes"] for r in results)
    biggest_dp=max(r["polynomial_DP_states"] for r in results)
    report={
        "status":"COMPLETE_BASE_Z_AUDIT_WITH_RATIONAL_NULLITY",
        "fixture_version":src["version"],
        "source_sha256":src["source_sha256"],
        "n":n,
        "GF2_rank":rank2,
        "GF2_nullity":len(basis),
        "nonzero_kernel_directions_checked":len(results),
        "rational_rank":rankq,
        "rational_nullity":len(qbasis),
        "rational_rank_33x33_minor_det_decimal":str(det),
        "rational_pivot_cols":pivots,
        "rational_minor_original_rows":oldrows,
        "rational_kernel_basis":[[str(x) for x in v] for v in qbasis],
        "weight_distribution":dict(sorted(hist.items())),
        "all_63_exact_records":results,
        "admissible_Z_A":[{"z_decimal":r["z_decimal"],
                          "z_weight":r["z_weight"],
                          "Y_z_count":r["Y_count"],
                          "y2_columns":r["Y_exact_covers"]}
                          for r in good],
        "inadmissible_directions":len(results)-len(good),
        "total_Y_count":sum(r["Y_count"] for r in results),
        "total_DFS_nodes":total_dfs,
        "max_squarefree_DP_states":biggest_dp,
        "all_r0_covers_independently_DP_checked":True,
        "ALL_2_lifts_MULTI_Z_forbidden_on_this_base":True,
        "base_only_obstruction_independent_of_voltages":True,
        "rational_nullity_one_filter_applies":False,
        "rational_nullity_two_necessary_not_sufficient":True,
        "global_SCL_polynomial_solver":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"
    }
    # Stable complete proof table fingerprint for CI and checkpoints.
    core=json.dumps(results,sort_keys=True,separators=(",",":"))
    report["all_63_table_sha256"]=hashlib.sha256(core.encode()).hexdigest()
    return report


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    a=p.parse_args()
    print(json.dumps(replay(a.fixture),indent=2,sort_keys=True))
