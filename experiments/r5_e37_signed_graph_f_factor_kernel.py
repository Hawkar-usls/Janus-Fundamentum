#!/usr/bin/env python3
"""Finite exact controls for R5 E37 signed-graph / f-factor kernel terminal.

A signed graph column has two endpoint entries in {+1,-1}.  The theorem transforms
R(3x-1)=0 exactly into an ordinary graph f-factor instance by complementing --
edges and replacing mixed-sign edges with degree-one selector vertices.

This checker brute-forces both the original signed Boolean system and the transformed
small f-factor instance and verifies exact equivalence on several controls.

P_VS_NP remains OPEN.
"""

from itertools import product


def signed_matrix(nv,edges):
    # edge = (u,su,v,sv), signs su,sv in {-1,+1}
    R=[[0]*len(edges) for _ in range(nv)]
    for j,(u,su,v,sv) in enumerate(edges):
        assert u != v and su in (-1,1) and sv in (-1,1)
        R[u][j]=su
        R[v][j]=sv
    return R


def matvec(R,x):
    return [sum(a*b for a,b in zip(row,x)) for row in R]


def brute_original(nv,edges):
    R=signed_matrix(nv,edges)
    n=len(edges)
    for x in product((0,1),repeat=n):
        y=[3*x[j]-1 for j in range(n)]
        if matvec(R,y)==[0]*nv:
            return True,x
    return False,None


def transform_to_factor(nv,edges):
    R=signed_matrix(nv,edges)
    row_sum=matvec(R,[1]*len(edges))
    if any(s % 3 for s in row_sum):
        return None

    negdeg=[0]*nv
    for u,su,v,sv in edges:
        if su < 0: negdeg[u]+=1
        if sv < 0: negdeg[v]+=1

    f=[row_sum[v]//3 + negdeg[v] for v in range(nv)]
    Fedges=[]
    decode=[]
    nextv=nv

    for eid,(u,su,v,sv) in enumerate(edges):
        if su==1 and sv==1:
            # direct selected state x=1
            Fedges.append((u,v,(eid,1)))
        elif su==-1 and sv==-1:
            # direct selected state z=1-x=1 => x=0
            Fedges.append((u,v,(eid,0)))
        else:
            s=nextv; nextv+=1
            f.append(1)
            # Selector chooses exactly one endpoint.
            if su==1:
                Fedges.append((s,u,(eid,1)))
                Fedges.append((s,v,(eid,0)))
            else:
                Fedges.append((s,u,(eid,0)))
                Fedges.append((s,v,(eid,1)))

    return nextv,Fedges,f


def brute_factor(num_vertices,Fedges,f,orig_m):
    m=len(Fedges)
    for take in product((0,1),repeat=m):
        deg=[0]*num_vertices
        for j,on in enumerate(take):
            if on:
                u,v,_=Fedges[j]
                deg[u]+=1;deg[v]+=1
        if deg != f:
            continue

        x=[None]*orig_m
        ok=True
        for j,on in enumerate(take):
            if not on:
                continue
            _,_,(eid,val)=Fedges[j]
            if x[eid] is not None and x[eid] != val:
                ok=False;break
            x[eid]=val
        if not ok:
            continue

        # ++ / -- direct edges not selected determine the complementary state.
        for eid in range(orig_m):
            if x[eid] is None:
                # Find edge representations for this eid.
                reps=[(j,meta) for j,(_,_,meta) in enumerate(Fedges) if meta[0]==eid]
                vals={meta[1] for _,meta in reps}
                if len(reps)==1:
                    # Direct ++ has tagged val 1, so absent =>0; direct -- tagged 0,
                    # so absent =>1.
                    tagged=next(iter(vals))
                    x[eid]=1-tagged
                else:
                    # Mixed selector must choose one representative when f(selector)=1.
                    ok=False;break
        if ok:
            return True,tuple(x)
    return False,None


def check(name,nv,edges):
    sat0,w0=brute_original(nv,edges)
    T=transform_to_factor(nv,edges)
    if T is None:
        sat1=False;w1=None
    else:
        nv2,Fedges,f=T
        sat1,w1=brute_factor(nv2,Fedges,f,len(edges))
    assert sat0==sat1
    if sat1:
        R=signed_matrix(nv,edges)
        y=[3*z-1 for z in w1]
        assert matvec(R,y)==[0]*nv
    print(f"{name}: SAT={sat0}, original_witness={w0}, factor_witness={w1}")


def main():
    # Pure directed 3-cycle (+ at tail, - at head): flow special case.
    check("directed_triangle",3,[
        (0,1,1,-1),
        (1,1,2,-1),
        (2,1,0,-1),
    ])

    # Pure unsigned K4 (++): f-factor/perfect-matching special case.
    edges=[]
    for u in range(4):
        for v in range(u+1,4):
            edges.append((u,1,v,1))
    check("unsigned_K4",4,edges)

    # Mixed signs with both selector and direct-edge behavior.
    check("mixed_square",4,[
        (0,1,1,-1),
        (1,1,2,1),
        (2,-1,3,-1),
        (3,1,0,-1),
        (0,1,2,1),
        (1,-1,3,1),
    ])

    # Mod-3 impossible signed imbalance.
    check("signed_star_impossible",4,[
        (0,1,1,1),
        (0,1,2,-1),
        (0,1,3,-1),
    ])

    print("R5 E37 signed-graph f-factor controls: PASS")
    print("Scientific ceiling: P_VS_NP remains OPEN.")


if __name__ == "__main__":
    main()
