#!/usr/bin/env python3
"""Finite exact controls for R5 E36 graph-incidence / f-factor kernel terminal.

For R equal to the 0/1 vertex-edge incidence matrix of an undirected graph H,
centered Exact-One in ker(R) is equivalent to selecting an f-factor with
    f(v)=deg_H(v)/3.

Controls:
  * triangle: non-TU incidence, degree not divisible by 3 -> UNSAT;
  * K4: non-TU incidence, cubic, perfect matching exists -> SAT;
  * a 16-vertex cubic graph with one central vertex joined by bridges to three
    subdivided-K4 gadgets: all degrees are 3 but Tutte obstruction kills every
    perfect matching -> UNSAT.

The theorem note invokes the standard polynomial f-factor algorithm; this checker
uses small exact backtracking only as a finite control.

P_VS_NP remains OPEN.
"""

from itertools import combinations


def incidence(nv,edges):
    R=[[0]*len(edges) for _ in range(nv)]
    for j,(u,v) in enumerate(edges):
        R[u][j]=1
        R[v][j]=1
    return R


def det3(M):
    a=M
    return (
        a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
        -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
        +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
    )


def degrees(nv,edges):
    d=[0]*nv
    for u,v in edges:
        d[u]+=1;d[v]+=1
    return d


def perfect_matching(nv,edges):
    adj=[set() for _ in range(nv)]
    for u,v in edges:
        adj[u].add(v);adj[v].add(u)

    def rec(rem):
        if not rem:
            return []
        u=min(rem)
        for v in sorted(adj[u] & rem):
            ans=rec(rem-{u,v})
            if ans is not None:
                return [(u,v)]+ans
        return None

    return rec(set(range(nv)))


def has_triangle_det2_minor(nv,edges):
    edge_index={tuple(sorted(e)):i for i,e in enumerate(edges)}
    R=incidence(nv,edges)
    for a,b,c in combinations(range(nv),3):
        pairs=[tuple(sorted((a,b))),tuple(sorted((b,c))),tuple(sorted((c,a)))]
        if all(p in edge_index for p in pairs):
            cs=[edge_index[p] for p in pairs]
            rs=[a,b,c]
            M=[[R[i][j] for j in cs] for i in rs]
            if abs(det3(M))==2:
                return True,M
    return False,None


def subdivided_k4_gadget(offset,subv):
    verts=[offset+i for i in range(4)]
    E=[]
    removed=tuple(sorted((verts[0],verts[1])))
    for u,v in combinations(verts,2):
        if tuple(sorted((u,v)))==removed:
            continue
        E.append((u,v))
    E.append((verts[0],subv))
    E.append((subv,verts[1]))
    return E


def cubic_tutte_obstruction():
    # Central vertex 0; three odd 5-vertex gadgets. Removing vertex 0 leaves
    # three odd components, so Tutte's condition fails: no perfect matching.
    E=[]
    starts=[1,6,11]
    subs=[5,10,15]
    for off,sub in zip(starts,subs):
        E.extend(subdivided_k4_gadget(off,sub))
        E.append((0,sub))
    return 16,E


def main():
    # Triangle: unsigned incidence has determinant -2 and deg=2, so /3 is nonintegral.
    tri=(3,[(0,1),(1,2),(2,0)])
    R=incidence(*tri)
    assert abs(det3(R))==2
    assert any(d%3 for d in degrees(*tri))
    print("triangle: non-TU, degree/3 nonintegral -> UNSAT")

    # K4: cubic and has a perfect matching.
    E4=list(combinations(range(4),2))
    ok,M=has_triangle_det2_minor(4,E4)
    assert ok
    assert degrees(4,E4)==[3]*4
    pm=perfect_matching(4,E4)
    assert pm is not None and len(pm)==2
    print(f"K4: non-TU, cubic, f=1, SAT perfect_matching={pm}")

    # Cubic graph with Tutte obstruction.
    nv,E=cubic_tutte_obstruction()
    assert degrees(nv,E)==[3]*nv
    ok,M=has_triangle_det2_minor(nv,E)
    assert ok
    pm=perfect_matching(nv,E)
    assert pm is None
    print("cubic_three_odd_components: non-TU, all degrees divisible by 3, f-factor UNSAT")

    print("R5 E36 graph f-factor kernel controls: PASS")
    print("Scientific ceiling: P_VS_NP remains OPEN.")


if __name__ == "__main__":
    main()
