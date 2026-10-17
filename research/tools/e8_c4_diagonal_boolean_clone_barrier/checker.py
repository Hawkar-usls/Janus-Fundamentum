#!/usr/bin/env python3
import itertools


def edge(u,v):
    return (u,v) if u<v else (v,u)


def build_graph():
    n=16
    groups=[(1,3,5,11),(2,8,10,14),(0,4,7,13),(6,9,12,15)]
    E={edge(i,(i+1)%n) for i in range(n)}
    for g in groups:
        g=tuple(sorted(g))
        for i in range(4):
            e=edge(g[i],g[(i+1)%4])
            assert e not in E
            E.add(e)
    deg=[0]*n
    for u,v in E: deg[u]+=1;deg[v]+=1
    assert all(d==4 for d in deg)
    return n,groups,E


def colorable(n,E):
    adj=[set() for _ in range(n)]
    for u,v in E:
        adj[u].add(v);adj[v].add(u)
    order=sorted(range(n), key=lambda v:-len(adj[v]))
    col={}
    def rec(i):
        if i==n:return True
        v=order[i]
        used={col[u] for u in adj[v] if u in col}
        for c in range(3):
            if c not in used:
                col[v]=c
                if rec(i+1):return True
                del col[v]
        return False
    return rec(0)


def quotient(n,E,groups,bits):
    p=list(range(n))
    def find(x):
        while p[x]!=x:
            p[x]=p[p[x]];x=p[x]
        return x
    def union(a,b):
        a,b=find(a),find(b)
        if a!=b:p[b]=a
    for g,b in zip(groups,bits):
        g=tuple(sorted(g))
        union(g[0],g[2]) if b==0 else union(g[1],g[3])
    roots=sorted({find(i) for i in range(n)})
    idx={r:i for i,r in enumerate(roots)}
    Q=set()
    for u,v in E:
        a,b=find(u),find(v)
        if a==b:return len(roots),None
        Q.add(edge(idx[a],idx[b]))
    return len(roots),Q


def feasible_relation():
    n,groups,E=build_graph()
    R=set()
    for bits in itertools.product((0,1), repeat=4):
        qn,Q=quotient(n,E,groups,bits)
        if Q is not None and colorable(qn,Q):
            R.add(bits)
    return R


def maj(a,b,c):
    return tuple(int(a[i]+b[i]+c[i]>=2) for i in range(len(a)))

def xor3(a,b,c):
    return tuple(a[i]^b[i]^c[i] for i in range(len(a)))

def aand(a,b):return tuple(a[i]&b[i] for i in range(len(a)))
def oor(a,b):return tuple(a[i]|b[i] for i in range(len(a)))


def flip_relation(R,mask):
    return {tuple(x[i]^((mask>>i)&1) for i in range(4)) for x in R}


def closed2(R,op):
    return all(op(a,b) in R for a in R for b in R)


def main():
    R=feasible_relation()
    expected={
        (0,0,0,0),(0,1,1,0),(0,1,1,1),
        (1,0,0,0),(1,0,0,1),(1,0,1,1),
        (1,1,0,0),(1,1,0,1),(1,1,1,1),
    }
    assert R==expected

    A=(0,1,1,1); B=(1,0,1,1); C=(0,0,0,0)
    assert A in R and B in R and C in R and maj(A,B,C)==(0,0,1,1) and maj(A,B,C) not in R
    C2=(0,1,1,0)
    assert xor3(A,B,C2)==(1,0,1,0) and (1,0,1,0) not in R
    assert aand(A,B)==(0,0,1,1) and (0,0,1,1) not in R
    D=(1,1,0,0); E=(0,1,1,0)
    assert oor(D,E)==(1,1,1,0) and (1,1,1,0) not in R

    # Relabel either diagonal independently in every C4: no renaming becomes Horn or dual-Horn.
    for mask in range(16):
        Rp=flip_relation(R,mask)
        assert not closed2(Rp,aand)
        assert not closed2(Rp,oor)

    print("PASS exact 16-vertex smooth C4 diagonal-feasibility relation (9 of 16 selections)")
    print("PASS majority, XOR3, AND and OR polymorphism counterexamples")
    print("PASS all 16 independent diagonal relabellings remain non-Horn and non-dual-Horn")

if __name__=='__main__':
    main()
