#!/usr/bin/env python3
"""R5 E112: cubic cycle-space exact-cover firewall.

E105-E111 reduce NO-RAW8 to a structured rank-2 affine cover.
E112 shows that the generic algebraic ingredients accumulated so far still
admit exact NO-RAW8 covers, even with defect multiplicity divisible by 3.

General construction:
  Let H be a connected cubic graph with n vertices and no bridges/2-edge cuts
  (3-edge-connected is sufficient).  Let U be its GF(2) cycle space.
  For each edge e, g_e in U* is the coordinate functional.
  At each cubic vertex v, the three incident g_e satisfy
      g_e1 + g_e2 + g_e3 = 0
  and, under 3-edge-connectivity, are three distinct nonzero vectors spanning
  a rank-2 line L_v.

  If n is divisible by 4 then |E|=3n/2 is even.  A standard parity-orientation
  argument gives an orientation in which every vertex has even indegree.
  Define forbidden character phi_v on L_v by phi_v(g_e)=1 iff e enters v.
  Even indegree makes phi_v linear on L_v.

  On each edge uv, phi_u(g_e) xor phi_v(g_e)=1.

For any global y in U:
  z_{v,e}=y_e xor phi_v(g_e).
At a vertex, z_v has even parity.  If y avoids the forbidden character there,
z_v is a nonzero even 3-bit vector, hence has exactly one ZERO half-edge.
If y violates the vertex, z_v=000, hence has three zero half-edges.

Along each edge, endpoint z bits are opposite, so exactly one endpoint is zero.

If delta(y) is the number of violated vertices:
    n + 2 delta(y) = |E| = 3n/2,
hence
    delta(y) = n/4
for EVERY y.

Thus the n forbidden codim-2 flats form an exact (n/4)-fold affine cover.
For n divisible by 12, defect multiplicity is automatically 0 mod 3, matching
E107 exactly.

The checker instantiates n=12 using the hexagonal prism:
  cycle-space dimension 7,
  12 rank-2 vertex lines,
  18 distinct nonzero edge normals,
  explicit even-indegree orientation,
  every one of 128 cycle-space points lies in exactly 3 forbidden flats.

Therefore the E105-E111 generic flat/normal/branchwidth language alone cannot
prove raw8.  The next theorem must use additional five-port TARGET6 witness
semantics not captured by this abstract cycle-space construction.

P_VS_NP remains OPEN.
"""

from collections import Counter


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


def rank_vecs(vecs):
    piv={}
    for x in vecs:
        y=x
        while y:
            p=y.bit_length()-1
            if p in piv:
                y ^= piv[p]
            else:
                piv[p]=y
                break
    return len(piv)


def hex_prism():
    E=set()
    for off in (0,6):
        for i in range(6):
            E.add(tuple(sorted((off+i,off+(i+1)%6))))
    for i in range(6):
        E.add((i,6+i))
    return tuple(sorted(E))


def incidence_rows(edges,nv):
    rows=[]
    for v in range(nv):
        m=0
        for i,(a,b) in enumerate(edges):
            if v in (a,b):
                m |= 1<<i
        rows.append(m)
    return tuple(rows)


def edge_normals_from_cycle_basis(cycle_basis,ne):
    # g_e is column e of a generator matrix whose rows are cycle_basis.
    out=[]
    for e in range(ne):
        g=0
        for i,row in enumerate(cycle_basis):
            if (row>>e)&1:
                g |= 1<<i
        out.append(g)
    return tuple(out)


def find_even_orientation(edges,nv):
    # brute force only for frozen 18-edge prism control
    for bits in range(1<<len(edges)):
        indeg=[0]*nv
        for i,(u,v) in enumerate(edges):
            # bit=0: u->v ; bit=1: v->u
            if (bits>>i)&1:
                indeg[u]+=1
            else:
                indeg[v]+=1
        if all(x%2==0 for x in indeg):
            return bits,tuple(indeg)
    raise AssertionError("no even orientation")


def head_bit(bits,i,vertex,edge):
    u,v=edge
    if (bits>>i)&1:
        # v -> u, head u
        return int(vertex==u)
    else:
        # u -> v, head v
        return int(vertex==v)


def dot(a,b):
    return (a&b).bit_count()&1


def main():
    edges=hex_prism()
    nv=12
    ne=len(edges)
    assert ne==18
    rows=incidence_rows(edges,nv)
    assert all(r.bit_count()==3 for r in rows)

    cycles=gf2_nullspace(rows,ne)
    assert len(cycles)==7

    normals=edge_normals_from_cycle_basis(cycles,ne)
    assert all(normals)
    assert len(set(normals))==ne  # prism has no 1/2-edge cut
    assert rank_vecs(normals)==7

    orient,indeg=find_even_orientation(edges,nv)
    assert all(d in (0,2) for d in indeg)
    assert sum(indeg)==ne

    vertex_lines=[]
    forbidden=[]
    for v in range(nv):
        idx=[i for i,e in enumerate(edges) if v in e]
        assert len(idx)==3
        gs=[normals[i] for i in idx]
        assert gs[0]^gs[1]^gs[2]==0
        assert rank_vecs(gs)==2

        vals=tuple(head_bit(orient,i,v,edges[i]) for i in idx)
        assert sum(vals)%2==0
        vertex_lines.append(tuple(idx))
        forbidden.append(vals)

    # Opposite endpoint marks on every edge.
    for i,(u,v) in enumerate(edges):
        assert head_bit(orient,i,u,edges[i]) ^ head_bit(orient,i,v,edges[i]) == 1

    multiplicity=[]
    for y in range(1<<len(cycles)):
        bad=0
        zero_halfedges=0
        for v,idx in enumerate(vertex_lines):
            vals=tuple(dot(y,normals[i]) for i in idx)
            z=tuple(a^b for a,b in zip(vals,forbidden[v]))
            assert sum(z)%2==0
            if z==(0,0,0):
                bad+=1
                zero_halfedges+=3
            else:
                assert sum(z)==2
                zero_halfedges+=1

        # Each graph edge has exactly one zero endpoint because marks are opposite.
        assert zero_halfedges==ne
        assert bad==nv//4==3
        multiplicity.append(bad)

    assert Counter(multiplicity)==Counter({3:1<<7})

    # Explicit flat cover count from forbidden local characters.
    cover_count=[0]*(1<<len(cycles))
    for v,idx in enumerate(vertex_lines):
        for y in range(1<<len(cycles)):
            vals=tuple(dot(y,normals[i]) for i in idx)
            if vals==forbidden[v]:
                cover_count[y]+=1
    assert set(cover_count)=={3}

    print("R5 E112 cubic cycle-space affine-cover firewall: PASS")
    print("hexagonal prism: vertices=12 edges=18 cycle-rank=7")
    print("edge normals: 18 distinct nonzero vectors")
    print("12 vertex lines are rank2")
    print("even-indegree orientation:",indeg)
    print("all 128 global states have defect multiplicity exactly 3")
    print("12 forbidden flats form an exact 3-fold affine cover")
    print("generic E105-E111 algebraic structure does NOT force raw8")
    print("next target: use five-port TARGET6 witness-support semantics beyond the abstract flat cover")
    print("P_VS_NP remains OPEN")


if __name__=="__main__":
    main()
