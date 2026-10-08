#!/usr/bin/env python3
"""R5 E114: signed-parallel residual-interface compression.

E113 shows that any JOINT lift of the E112 cubic normal pattern must split each
abstract normal g_e into distinct Tanner variables at its two endpoint checks,
with opposite six-witness support parity but the SAME residual normal.

For repair directions z in the post-E106 direction space U this means the two
endpoint occurrence variables of edge e have equal z-coordinate.

Take a connected cubic signed-parallel block H with q distinguished checks and
m=3q/2 abstract normals/edges.  There are 2m distinct Tanner occurrence
variables, two per edge.

Restrictions on z over those 2m variables satisfy:
  (1) m pair-equality equations, one for every signed-parallel pair;
  (2) q even-parity check equations, one for every distinguished cubic check.

After substituting the pair equalities, (2) is exactly the binary vertex-edge
incidence system of H.  For connected H its rank is q-1.  Therefore

  dim rho_H(U) <= 2m - m - (q-1)
                = m-q+1
                = q/2+1.

All remaining Tanner incidences of those occurrence variables carry the same
repair coordinates, so the ENTIRE interaction of the lifted block with the
outside world has at most 2^(q/2+1) repair patterns.

For the E112 hexagonal prism:
  q=12, m=18, 36 distinct occurrence variables,
  72 additional cubic incidences leave the distinguished checks,
  but their joint repair interface has dimension at most 7,
  hence at most 128 patterns.

Thus ANY genuine joint Tanner lift of the fixed E112 prism is an exact
constant-state interface and cannot itself be an asymptotic hard core.
The unresolved case requires a growing signed-parallel core family.

P_VS_NP remains OPEN.
"""

from itertools import combinations


def gf2_rank(rows):
    rows=[int(r) for r in rows if r]
    rank=0
    col=0
    maxbit=max((r.bit_length() for r in rows), default=0)
    while col<maxbit and rank<len(rows):
        p=next((i for i in range(rank,len(rows)) if (rows[i]>>col)&1),None)
        if p is None:
            col+=1
            continue
        rows[rank],rows[p]=rows[p],rows[rank]
        for i in range(len(rows)):
            if i!=rank and ((rows[i]>>col)&1):
                rows[i]^=rows[rank]
        rank+=1
        col+=1
    return rank


def gf2_nullity(rows,n):
    return n-gf2_rank(rows)


def connected(n,edges):
    adj=[set() for _ in range(n)]
    for u,v in edges:
        adj[u].add(v); adj[v].add(u)
    seen={0}
    stack=[0]
    while stack:
        u=stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return len(seen)==n


def check_cubic(n,edges):
    deg=[0]*n
    for u,v in edges:
        deg[u]+=1; deg[v]+=1
    assert all(d==3 for d in deg)
    assert len(edges)==3*n//2
    assert connected(n,edges)


def incidence_rows(n,edges):
    rows=[]
    for v in range(n):
        r=0
        for e,(a,b) in enumerate(edges):
            if v in (a,b):
                r |= 1<<e
        rows.append(r)
    return tuple(rows)


def occurrence_constraint_rows(n,edges):
    """Variables are two endpoint occurrences per edge.

    occurrence id 2e belongs to first endpoint edges[e][0],
    occurrence id 2e+1 belongs to second endpoint edges[e][1].

    Add pair equalities and distinguished-check parity equations.
    """
    m=len(edges)
    rows=[]

    # Same residual normal => equal repair direction coordinate.
    for e in range(m):
        rows.append((1<<(2*e)) | (1<<(2*e+1)))

    # Cubic distinguished checks.
    for v in range(n):
        r=0
        for e,(a,b) in enumerate(edges):
            if v==a:
                r |= 1<<(2*e)
            elif v==b:
                r |= 1<<(2*e+1)
        rows.append(r)
    return tuple(rows)


def verify_block(n,edges):
    edges=tuple(tuple(sorted(e)) for e in edges)
    edges=tuple(sorted(set(edges)))
    check_cubic(n,edges)
    m=len(edges)

    inc=incidence_rows(n,edges)
    assert gf2_rank(inc)==n-1
    assert gf2_nullity(inc,m)==m-n+1

    occ=occurrence_constraint_rows(n,edges)
    rank=gf2_rank(occ)
    nullity=gf2_nullity(occ,2*m)

    # Pair equations are independent, and after pair substitution the check
    # equations have connected incidence rank n-1.
    assert rank==m+n-1
    assert nullity==2*m-(m+n-1)
    assert nullity==m-n+1
    assert nullity==n//2+1

    return {
        "checks":n,
        "normals":m,
        "occurrence_variables":2*m,
        "constraint_rank":rank,
        "interface_dim":nullity,
        "interface_states":1<<nullity,
        "outside_stubs":4*m,  # each occurrence variable has 2 more cubic incidences
    }


def k4():
    return (
        (0,1),(0,2),(0,3),
        (1,2),(1,3),(2,3),
    )


def cube():
    # Q3, cubic on 8 vertices.
    E=[]
    for u in range(8):
        for bit in (1,2,4):
            v=u^bit
            if u<v:
                E.append((u,v))
    return tuple(E)


def hex_prism():
    E=set()
    for off in (0,6):
        for i in range(6):
            E.add(tuple(sorted((off+i,off+(i+1)%6))))
    for i in range(6):
        E.add((i,6+i))
    return tuple(sorted(E))


def main():
    a=verify_block(4,k4())
    b=verify_block(8,cube())
    p=verify_block(12,hex_prism())

    assert a["interface_dim"]==3
    assert b["interface_dim"]==5
    assert p["normals"]==18
    assert p["occurrence_variables"]==36
    assert p["outside_stubs"]==72
    assert p["interface_dim"]==7
    assert p["interface_states"]==128

    # General connected cubic formula q/2+1 is replayed on three independent
    # graphs rather than only the prism.
    for d in (a,b,p):
        assert d["interface_dim"]==d["checks"]//2+1

    print("R5 E114 signed-parallel residual-interface compression: PASS")
    print("K4:",a)
    print("cube:",b)
    print("hexagonal prism:",p)
    print("general connected cubic signed-parallel block: interface_dim <= q/2+1")
    print("E112 prism joint lift: 72 external Tanner incidences but <=7 repair bits / <=128 patterns")
    print("fixed prism is a constant-state exact interface, not an asymptotic hard core")
    print("next target: growing signed-parallel core family / separator theorem")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
