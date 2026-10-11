#!/usr/bin/env python3
"""R5 SAT/UNSAT indistinguishability through FIVE low 4-flow support moments.

Two connected cubic graphs with 20 vertices, 30 edges, 3-edge-cut count 20,
4-edge-cut count 30, full Smith invariants 1^52, 2^2, 0^20:
 * Isaacs flower J5:      Boolean UNSAT, 0 proper 3-edge colourings.
 * SAT20 fixed graph:     Boolean SAT,   72 proper 3-edge colourings.

The binomial moments H_0,...,H_4 of the TWO-BIT CYCLE-SPACE EDGE SUPPORT
are identical, while H_5 differs. Every fixed-k moment has a direct
O(sum_{j=0}^k binom(m,j) poly(n)) evaluator via graph edge-deletion ranks.
It is NOT an n^O(1) algorithm when k grows with n.
"""
from collections import Counter
from itertools import combinations
from math import comb

SAT20 = (
    (0,10),(0,14),(0,19),(1,6),(1,11),(1,19),(2,7),(2,13),
    (2,19),(3,8),(3,9),(3,16),(4,6),(4,14),(4,17),(5,9),
    (5,10),(5,17),(6,7),(7,15),(8,11),(8,18),(9,13),
    (10,11),(12,13),(12,16),(12,18),(14,15),(15,16),(17,18),
)


def flower(k):
    assert k>=5 and k%2==1
    E=set()
    def add(u,v):
        assert u!=v
        E.add(tuple(sorted((u,v))))
    for i in range(k):
        a,b,c,d=4*i,4*i+1,4*i+2,4*i+3
        for w in (b,c,d): add(a,w)
        add(b,4*((i+1)%k)+1)
    cycle=[4*i+2 for i in range(k)]+[4*i+3 for i in range(k)]
    for i in range(2*k): add(cycle[i],cycle[(i+1)%(2*k)])
    return tuple(sorted(E))


def validate(n,raw):
    E=tuple(sorted(tuple(sorted(e)) for e in raw))
    assert len(E)==len(set(E))==3*n//2
    assert all(0<=u<v<n for u,v in E)
    deg=Counter(v for u,w in E for v in (u,w))
    assert all(deg[v]==3 for v in range(n))
    return E


def edge_graph(n,E):
    adj=[[] for _ in range(n)]
    for i,(u,v) in enumerate(E):
        adj[u].append((v,i))
        adj[v].append((u,i))
    return adj


def connected_components_after_edges(n,adj,deleted_mask):
    remaining=(1<<n)-1
    c=0
    while remaining:
        root=(remaining&-remaining).bit_length()-1
        remaining^=1<<root
        stack=[root]
        c+=1
        while stack:
            v=stack.pop()
            for w,i in adj[v]:
                if (remaining & (1<<w)) and not (deleted_mask&(1<<i)):
                    remaining^=1<<w
                    stack.append(w)
    return c


def deletion_connectivity_hist(n,E,K):
    """All size<=K deletion profiles, O(sum C(m,j)*poly(n))."""
    adj=edge_graph(n,E)
    hist=[]
    for j in range(K+1):
        cnt=Counter()
        for T in combinations(range(len(E)),j):
            mask=sum(1<<i for i in T)
            cnt[connected_components_after_edges(n,adj,mask)]+=1
        assert sum(cnt.values())==comb(len(E),j)
        hist.append(cnt)
    return hist


def flow_support_binomial_moments_from_deletions(n,E,profiles):
    """Unrestricted pair of binary cycles: H_k=sum binom(|supp(f) U supp(g)|,k).
    
    Inclusion-exclusion on forced-nonzero edge subsets:
      H_k = sum_{j<=k} (-1)^j C(m-j,k-j)
             sum_{|T|=j} 4^{m-j-n+c(G-T)}.
    """
    m=len(E)
    out=[]
    for k in range(len(profiles)):
        acc=0
        for j in range(k+1):
            acc+=((-1)**j)*comb(m-j,k-j)*sum(
                count*4**(m-j-n+c) for c,count in profiles[j].items())
        out.append(acc)
    return tuple(out)


def small_exact_cut_counts(n,E,K):
    """INDEPENDENT exhaustive vertex-bipartition census; exponential."""
    masks=[0]*n
    for i,(u,v) in enumerate(E):
        masks[u]^=1<<i
        masks[v]^=1<<i
    cut=0
    gray_old=0
    count=Counter()
    # vertex 0 fixed on the complement shore => each nonempty cut counted once
    for i in range(1,1<<(n-1)):
        gray=i^(i>>1)
        flipped_vertex=(gray^gray_old).bit_length()
        cut ^= masks[flipped_vertex]
        gray_old=gray
        size=cut.bit_count()
        if size<=K:
            count[size]+=1
    return count


def three_edge_colour_count(n,E):
    """Independent exact finite matching + even 2-factor counter.
    
    Worst-case EXPONENTIAL; no polynomial guarantee.
    """
    adj=[set() for _ in range(n)]
    for u,v in E:
        adj[u].add(v);adj[v].add(u)
    mset=set(E)
    all_count=0
    mat_count=0
    extendable=0
    def match(rem, chosen):
        nonlocal all_count,mat_count,extendable
        if not rem:
            mat_count+=1
            M=set(chosen)
            rest=[[] for _ in range(n)]
            for u,v in E:
                if (u,v) not in M:
                    rest[u].append(v);rest[v].append(u)
            assert all(len(a)==2 for a in rest)
            colours=[-1]*n
            cycles=0
            for start in range(n):
                if colours[start]>=0:continue
                cycles+=1
                colours[start]=0
                todo=[start]
                while todo:
                    u=todo.pop()
                    for v in rest[u]:
                        if colours[v]<0:
                            colours[v]=1-colours[u]
                            todo.append(v)
                        elif colours[v]==colours[u]:
                            return
            extendable+=1
            all_count+=2**cycles
            return
        u=min(rem)
        for v in sorted(adj[u]&rem):
            edge=tuple(sorted((u,v)))
            assert edge in mset
            match(rem-{u,v},chosen+(edge,))
    match(set(range(n)),())
    return all_count,mat_count,extendable


def main():
    records=[]
    for name,raw,expected_count,expected_b5 in (
        ("FLOWER_J5_UNSAT",flower(5),0,61),
        ("CUBIC20_SAT",SAT20,72,68),
    ):
        n=20
        E=validate(n,raw)
        m=len(E)
        adj=edge_graph(n,E)
        assert connected_components_after_edges(n,adj,0)==1
        cuts=small_exact_cut_counts(n,E,5)
        assert all(cuts[j]==0 for j in (1,2))
        assert (cuts[3],cuts[4],cuts[5])==(20,30,expected_b5)
        colourings,matchings,good=three_edge_colour_count(n,E)
        assert colourings==expected_count
        hist=deletion_connectivity_hist(n,E,5)
        assert hist[3]==Counter({1:4040,2:20})
        assert hist[4]==Counter({1:26835,2:570})
        assert hist[5][3]==30
        assert hist[5][2] == 7770+(expected_b5-60)
        moments=flow_support_binomial_moments_from_deletions(n,E,hist)
        assert moments[:5]==(
            4194304,94371840,1026293760,7180124160,36291133440
        )
        records.append(moments)
        print(f'{name}: #3edgecolours={colourings}, '
              f'perfect_matchings={matchings}, extendable={good}, '
              f'cuts_3_4_5={(cuts[3],cuts[4],cuts[5])}, '
              f'deletion_5={dict(hist[5])}, '
              f'H0_H5={moments}',flush=True)
    sat,unsat=records[1],records[0]
    assert sat[:5]==unsat[:5]
    assert sat[5]==141091037184 and unsat[5]==141091123200
    assert unsat[5]-sat[5]==86016 == 7*3*4**6
    print('SAT_UNSAT_SAME_FIVE_FLOW_MOMENTS_K0_K4 = VERIFIED_FINITE')
    print('FIRST_DIFFERENCE_K5 = 86016')
    print('ALL_GRAPH_FIXED_K_DELETION_MOMENT_IDENTITY = PROVED')
    print('FIXED_K_EVALUATION_POLY_FOR_CONSTANT_K_ONLY')
    print('UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=="__main__":
    main()
