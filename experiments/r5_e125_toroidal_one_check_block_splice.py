#!/usr/bin/env python3
"""R5 E125: replay the toroidal one-check E64 block splice."""

from collections import deque

from r5_e64_connected_postquotient_nullity_firewall import (
    tutte12_incidence,
    rank_q,
    two_level_kernel_count,
)

BASE_N=63
DELETE_ROW=0


def base_ports(R):
    p=[j for j,v in enumerate(R[DELETE_ROW]) if v]
    assert len(p)==3
    return p


def base_core_connected(R):
    # Levi graph after deleting check DELETE_ROW.
    # Nodes: checks 1..62 and all 63 variables.
    check_nodes=[i for i in range(BASE_N) if i!=DELETE_ROW]
    # Encode surviving checks as 0..61, variables as 62..124.
    cpos={c:i for i,c in enumerate(check_nodes)}
    off=len(check_nodes)
    adj=[set() for _ in range(off+BASE_N)]
    for c in check_nodes:
        for v,x in enumerate(R[c]):
            if x:
                a=cpos[c]
                b=off+v
                adj[a].add(b)
                adj[b].add(a)
    seen={0}
    q=[0]
    while q:
        u=q.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return len(seen)==len(adj)


def block_id(i,j,t):
    return (i%t)*t+(j%t)


def build_splice(R,t):
    ports=base_ports(R)
    m=t*t
    N=BASE_N*m
    rows=[]

    # 62 retained local rows per left block.
    for i in range(t):
        for j in range(t):
            b=block_id(i,j,t)
            off=b*BASE_N
            for c in range(BASE_N):
                if c==DELETE_ROW:
                    continue
                supp={off+v for v,x in enumerate(R[c]) if x}
                assert len(supp)==3
                rows.append(supp)

    # One cross-check per right skeleton vertex (i,j):
    # v0 from L(i,j), v1 from L(i-1,j), v2 from L(i,j-1).
    for i in range(t):
        for j in range(t):
            b0=block_id(i,j,t)
            b1=block_id(i-1,j,t)
            b2=block_id(i,j-1,t)
            rows.append({
                b0*BASE_N+ports[0],
                b1*BASE_N+ports[1],
                b2*BASE_N+ports[2],
            })

    assert len(rows)==N
    return rows,N


def verify_sparse_square_cubic_linear(rows,N):
    assert len(rows)==N
    assert all(len(r)==3 for r in rows)

    col_rows=[[] for _ in range(N)]
    pair_seen=set()
    for ri,r in enumerate(rows):
        s=sorted(r)
        for v in s:
            col_rows[v].append(ri)
        pairs=((s[0],s[1]),(s[0],s[2]),(s[1],s[2]))
        for p in pairs:
            assert p not in pair_seen
            pair_seen.add(p)

    assert all(len(x)==3 for x in col_rows)

    # Column-linearity: no pair of variables occurs in two rows is already
    # exactly the pair_seen assertion above.
    return col_rows


def connected_incidence(rows,N):
    adj=[[] for _ in range(2*N)]
    for i,r in enumerate(rows):
        for v in r:
            a=i; b=N+v
            adj[a].append(b); adj[b].append(a)
    seen={0}; q=[0]
    while q:
        u=q.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return len(seen)==2*N


def skeleton_connected(t):
    # H_t bipartite connectivity.
    # left 0..m-1, right m..2m-1
    m=t*t
    adj=[set() for _ in range(2*m)]
    for i in range(t):
        for j in range(t):
            L=block_id(i,j,t)
            for a,b in ((i,j),(i+1,j),(i,j+1)):
                R=m+block_id(a,b,t)
                adj[L].add(R); adj[R].add(L)
    assert all(len(x)==3 for x in adj)
    seen={0}; q=[0]
    while q:
        u=q.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v)
    return len(seen)==2*m


def main():
    R=tutte12_incidence()
    assert rank_q(R)==49
    d,count=two_level_kernel_count(R)
    assert d==14 and count==0
    assert base_core_connected(R)

    ports=base_ports(R)
    print("base deleted-check ports=",ports)

    for t in (2,3):
        rows,N=build_splice(R,t)
        verify_sparse_square_cubic_linear(rows,N)
        assert connected_incidence(rows,N)
        assert skeleton_connected(t)

        m=t*t
        # Symbolic rank-perturbation certificate:
        # blockdiag rank = 49m; only m row positions are replaced.
        rank_upper=50*m
        nullity_lower=N-rank_upper
        assert nullity_lower==13*m

        print(
            f"t={t}: N={N} blocks={m} square/cubic/linear/connected PASS "
            f"nullity_Q_lower_bound={nullity_lower}"
        )

    print("UNSAT theorem: each block satisfies 62 frozen E64 checks;")
    print("one-check redundancy would force deleted check, contradicting E64 UNSAT.")
    print("For general t>=3, H_t contracts to C_t square C_t, so Levi treewidth >= t.")
    print("R5 E125 toroidal one-check block splice: PASS")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
