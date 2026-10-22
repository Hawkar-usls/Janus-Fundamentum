#!/usr/bin/env python3
"""BABEL-23C: independent exact global Fano-coupler UNSAT family replay.

Finite exact checks support but do not replace the all-n counting proof
in docs/research/BABEL23_GLOBAL_FANO_COUPLER_THEOREM_20261022.md.
"""
import hashlib
import json
from collections import Counter

COLORS=((0,0),(1,2),(5,5))  # (modified row, exported literal)


def block_rows(block):
    off=7*block
    return [tuple(sorted(off+j for j in ids))
            for ids in ((0,1,3),(1,2,4),(2,3,5),
                        (3,4,6),(0,4,5),(1,5,6),(0,2,6))]


def create(m):
    assert m>=3
    rows=[list(row) for b in range(2*m) for row in block_rows(b)]
    for left in range(m):
        for color,(ri,ex) in enumerate(COLORS):
            right=m+(left+color)%m
            ia,ib=7*left+ri,7*right+ri
            a,b=7*left+ex,7*right+ex
            assert a in rows[ia] and b in rows[ib]
            rows[ia][rows[ia].index(a)]=b
            rows[ib][rows[ib].index(b)]=a
    return [tuple(sorted(row)) for row in rows]


def validate(rows):
    n=len(rows)
    assert all(len(r)==3 and len(set(r))==3 and all(0<=j<n for j in r)
               for r in rows)
    assert Counter(j for r in rows for j in r)==Counter({j:3 for j in range(n)})
    pairs=[tuple(sorted((a,b))) for r in rows for a in r for b in r if a<b]
    assert len(set(pairs))==3*n, "linear incidence violated"
    adj=[set() for _ in range(n)]
    for row in rows:
        for j in row:adj[j].update(row)
    seen={0};stack=[0]
    while stack:
        for j in adj[stack.pop()]-seen:
            seen.add(j);stack.append(j)
    assert len(seen)==n,"disconnected incidence"
    return True


def kernel(rows):
    piv={};n=len(rows)
    for row in rows:
        x=sum(1<<j for j in row)
        while x:
            p=x.bit_length()-1
            if p in piv:x^=piv[p]
            else:piv[p]=x;break
    basis=[]
    for j in range(n):
        if j in piv:continue
        w=1<<j
        for p in sorted(piv):
            if (piv[p]&w).bit_count()%2:w^=1<<p
        assert all((w&sum(1<<k for k in row)).bit_count()%2==0
                   for row in rows)
        basis.append(w)
    return basis


def parity_enumeration(rows,basis):
    n=len(rows);v=0;count=0
    for i in range(1<<len(basis)):
        if i:v^=basis[(i&-i).bit_length()-1]
        count+=(v.bit_count()*3==2*n)
    return count


def local_port_control():
    x=[0]*7;x[0]=x[3]=1
    y=[0,1,1]
    lines=block_rows(0)
    untouched=(2,3,4,6)
    assert all(sum(x[j] for j in lines[i])==1 for i in untouched)
    for color,(ri,ex) in enumerate(COLORS):
        assert sum(x[j] for j in lines[ri] if j!=ex)+y[color]==1
    # All 3 modified rows and 4 untouched rows can be satisfied LOCALLY.
    return {"local_x_ones":[0,3],"local_import_bits":y,
            "four_untouched_exactone":True,
            "three_modified_rows_exactone_with_free_ports":True}


def main():
    local=local_port_control()
    records=[]
    for m in (3,6,9):
        rows=create(m)
        assert validate(rows)
        basis=kernel(rows)
        sat=parity_enumeration(rows,basis) if m<=6 else None
        if sat is not None:assert sat==0
        assert len(basis)=={3:10,6:19,9:28}[m],(m,len(basis))
        records.append({
            "m":m,"n":len(rows),
            "nullity_exact":len(basis),
            "parity_states":str(1<<len(basis)),
            "sat_count_by_parity_enumeration":sat,
            "sat_status_symbolic_all_n":"UNSAT_PROVED_BY_LOCAL_ONE_EXPORT_TWO_IMPORT_COUNT",
            "connected_linear_cubic_square":"EXACT_PASS",
            "rows_sha256":hashlib.sha256(json.dumps(rows,separators=(",",":")).encode()).hexdigest(),
        })
    print(json.dumps({
        "gate":"BABEL23C_GLOBAL_FANO_COUPLER",
        "local_port_feasibility":local,
        "all_n_unsat_proof":"ONE_EXPORTED_TRUE_PER_BLOCK_BUT_TWO_IMPORTED_TRUE_PER_BLOCK",
        "proof_scope":"ALL_M_GE3_AND_PROPER_THREE_COLORED_BIPARTITE_GRAPH_CONSTRUCTION",
        "uniform_fourier_degree_bound":"NOT_PROVED",
        "P_vs_NP":"OPEN",
        "cases":records,
    },indent=2,sort_keys=True))


if __name__=="__main__":
    main()
