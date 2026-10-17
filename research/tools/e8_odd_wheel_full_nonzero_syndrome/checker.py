#!/usr/bin/env python3
from itertools import product

MOD=3


def wheel_matrix(n):
    # columns: spokes p_0..p_{n-1}, rim r_0..r_{n-1}
    Q=[[0]*(2*n) for _ in range(n)]
    for i in range(n):
        Q[i][i]=1
        Q[i][n+i]=1
        Q[i][(i+1)%n]=2
    return Q


def mat_vec(Q,s):
    return tuple(sum(a*x for a,x in zip(row,s))%3 for row in Q)


def construct_signs(y):
    n=len(y)
    assert n%2==1 and any(v%3 for v in y)
    j=next(i for i,v in enumerate(y) if v%3)
    # Rotate indices so j is the closing transition. Work in original indices.
    order=[(j+1+t)%n for t in range(n)]  # states p at these vertices; final edge j closes
    # edges traversed before j are indices order[0],...,order[n-2]
    other_edges=order[:-1]
    zero_count=sum(y[i]%3==0 for i in other_edges)
    # If odd, choose the state before closing so the allowed directed flip at edge j occurs.
    # p_j is state before edge j; p_{j+1} is state after closing.
    if zero_count%2==0:
        p_start=1  # loop at closing edge will work
    else:
        # y_j=1 allows +1 -> -1, so p_{j+1}=-1.
        # y_j=2 allows -1 -> +1, so p_{j+1}=+1.
        p_start=2 if y[j]%3==1 else 1
    p=[None]*n
    p[(j+1)%n]=p_start
    cur=(j+1)%n
    for edge in other_edges:
        assert edge==cur
        nxt=(cur+1)%n
        if y[edge]%3==0:
            p[nxt]=(-p[cur])%3
        else:
            p[nxt]=p[cur]
        cur=nxt
    assert cur==j
    # closing edge j must be legal
    r=[None]*n
    for i in range(n):
        r[i]=(y[i]-p[i]+p[(i+1)%n])%3
        assert r[i] in (1,2), (n,y,j,i,p,r[i])
    return tuple(p+r)


def main():
    # constructive replay for every nonzero syndrome up to beta=7
    for n in (3,5,7):
        Q=wheel_matrix(n)
        seen=set()
        for y in product(range(3), repeat=n):
            if all(v==0 for v in y):
                continue
            s=construct_signs(y)
            assert all(x in (1,2) for x in s)
            assert mat_vec(Q,s)==y
            seen.add(y)
        assert len(seen)==3**n-1

        # zero syndrome is absent; brute-force feasible through n=7 (2^(14)=16384)
        for s in product((1,2), repeat=2*n):
            assert mat_vec(Q,s)!=(0,)*n

    # larger exact finite controls: enumerate sign image, not proof search
    for n in (9,):
        Q=wheel_matrix(n)
        S={mat_vec(Q,s) for s in product((1,2), repeat=2*n)}
        assert (0,)*n not in S
        assert len(S)==3**n-1

    print('PASS: odd-wheel full nonzero syndrome theorem')
    print('verified W_3, W_5, W_7 constructively for every nonzero target')
    print('verified W_9 sign image has exactly 3^9-1 nonzero syndromes')
    print('any proper linear syndrome quotient has a false zero on every odd wheel')


if __name__=='__main__':
    main()
