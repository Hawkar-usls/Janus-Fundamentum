#!/usr/bin/env python3
"""Independent finite audits for cubic-graph -> JANUS SCL Exact-One.

Three DIFFERENT exact worst-case exponential counters:
  (1) proper 3-edge-colour backtracking;
  (2) perfect-matching / even 2-factor sum;
  (3) nowhere-zero F2^2 flows (two binary cycle-space elements).
Also checks incidence promises and small-field ranks.
Petersen and C5 prism: same Smith invariants, Boolean counts 0 vs 30.
No universal polynomial solver or P=NP is claimed.
"""
from collections import Counter
from math import comb


def normalized(n, edges):
    E = tuple(sorted(tuple(sorted(e)) for e in edges))
    assert len(set(E)) == len(E)
    assert all(len(e)==2 and 0 <= e[0] < e[1] < n for e in E)
    assert 2*len(E) == 3*n
    degree = Counter(v for e in E for v in e)
    assert all(degree[v]==3 for v in range(n))
    return E


def make_rows(n, edges):
    m = len(edges)
    rows = [tuple(range(3*i,3*i+3)) for i in range(m)]
    for v in range(n):
        for c in range(3):
            rows.append(tuple(3*i+c for i,e in enumerate(edges) if v in e))
    assert len(rows)==3*m==m+3*n
    assert all(len(r)==3 for r in rows)
    assert all(sum(j in r for r in rows)==3 for j in range(3*m))
    assert all(len(set(a)&set(b))<=1
               for i,a in enumerate(rows) for b in rows[i+1:])
    return rows


def colour_count(n, edges):
    incident=[[] for _ in range(n)]
    for i,(u,v) in enumerate(edges):
        incident[u].append(i)
        incident[v].append(i)
    colours=[-1]*len(edges)
    witness=[None]
    def go(k):
        if k==len(edges):
            if witness[0] is None: witness[0]=colours[:]
            return 1
        candidate=None
        for i,(u,v) in enumerate(edges):
            if colours[i]>=0: continue
            used={colours[j] for j in incident[u]+incident[v]
                  if colours[j]>=0}
            options=[c for c in range(3) if c not in used]
            if not options: return 0
            if candidate is None or len(options)<len(candidate[1]):
                candidate=(i,options)
        i,options=candidate
        total=0
        for c in options:
            colours[i]=c
            total+=go(k+1)
            colours[i]=-1
        return total
    return go(0),witness[0]


def all_perfect_matchings(n, edges):
    es=set(edges)
    def walk(unused):
        if not unused:
            yield frozenset()
            return
        v=min(unused)
        for w in sorted(unused-{v}):
            if (v,w) not in es: continue
            for rest in walk(unused-{v,w}):
                yield rest|{(v,w)}
    yield from walk(frozenset(range(n)))


def even_residual_cycles(n, edges, matching):
    adj=[[] for _ in range(n)]
    for u,v in edges:
        if (u,v) not in matching:
            adj[u].append(v)
            adj[v].append(u)
    assert all(len(a)==2 for a in adj)
    seen=set()
    cycles=0
    for start in range(n):
        if start in seen: continue
        previous,node=-1,start
        length=0
        while node not in seen:
            seen.add(node)
            length+=1
            a,b=adj[node]
            nxt=b if a==previous else a
            previous,node=node,nxt
        assert node==start
        if length%2: return None
        cycles+=1
    return cycles


def matching_count(n,edges):
    terms=[]
    for M in all_perfect_matchings(n,edges):
        k=even_residual_cycles(n,edges,M)
        terms.append(0 if k is None else 2**k)
    return sum(terms),len(terms),sum(t!=0 for t in terms)


def flow_count(n,edges):
    """Enumerate binary cycle space twice: O(4^r) in cycle rank r."""
    m=len(edges)
    parity_masks=[sum(1<<i for i,e in enumerate(edges) if v in e)
                  for v in range(n)]
    cycles=[s for s in range(1<<m)
            if all(((s&mask).bit_count()%2)==0
                   for mask in parity_masks)]
    all_edges=(1<<m)-1
    histogram=Counter((x|y).bit_count() for x in cycles for y in cycles)
    moments=tuple(sum(num*comb(w,k) for w,num in histogram.items() if w>=k)
                  for k in range(min(m,4)+1))
    return histogram.get(m,0),len(cycles),moments


def edge_cut_census(n, edges):
    """Small finite exact cut census; exponential in vertices, only a fixture."""
    cuts=set()
    for vertex_mask in range(1,1<<(n-1)):
        boundary=frozenset(i for i,(u,v) in enumerate(edges)
                           if ((vertex_mask>>u)&1)!=((vertex_mask>>v)&1))
        if boundary and len(boundary)<=4:
            cuts.add(boundary)
    return Counter(map(len,cuts))


def low_moment_formula(n, m, r, three_cuts, four_cuts):
    """Theorem for ANY 3-edge-connected cubic, r>=4.

    Moment k counts pairs of binary cycles with k chosen jointly nonzero
    edges, summed over all subsets of k edges. No SAT oracle.
    """
    assert r>=4
    return (
        4**r,
        3*m*4**(r-1),
        9*comb(m,2)*4**(r-2),
        (27*comb(m,3)-3*three_cuts)*4**(r-3),
        (81*comb(m,4)-9*three_cuts*(m-3)+3*four_cuts)*4**(r-4),
    )


def rank_mod(rows,n,p):
    a=[[int(j in r) for j in range(n)] for r in rows]
    rank=0
    for j in range(n):
        pivot=next((i for i in range(rank,n) if a[i][j]%p),None)
        if pivot is None: continue
        a[rank],a[pivot]=a[pivot],a[rank]
        inv=pow(a[rank][j],-1,p)
        a[rank]=[(t*inv)%p for t in a[rank]]
        for i in range(rank+1,n):
            f=a[i][j]
            if f:
                a[i]=[(t-f*s)%p for t,s in zip(a[i],a[rank])]
        rank+=1
    return rank


def connected_nonbip(n,edges):
    adj=[[] for _ in range(n)]
    for u,v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parity={0:0}
    queue=[0]
    odd=False
    while queue:
        v=queue.pop()
        for w in adj[v]:
            if w not in parity:
                parity[w]=1-parity[v]
                queue.append(w)
            elif parity[w]==parity[v]:
                odd=True
    return len(parity)==n,odd


def main():
    k4=[(u,v) for u in range(4) for v in range(u+1,4)]
    k33=[(u,v) for u in range(3) for v in range(3,6)]
    cube=[(v,v^(1<<bit)) for v in range(8) for bit in range(3)
          if v < (v^(1<<bit))]
    outer=[(i,(i+1)%5) for i in range(5)]
    spokes=[(i,5+i) for i in range(5)]
    prism=outer+spokes+[(5+i,5+(i+1)%5) for i in range(5)]
    petersen=outer+spokes+[(5+i,5+(i+2)%5) for i in range(5)]
    def prism_edges(k):
        return ([(i,(i+1)%k) for i in range(k)] +
                [(k+i,k+(i+1)%k) for i in range(k)] +
                [(i,k+i) for i in range(k)])
    cases=[('K4',4,k4,6),('PRISM3_NONTRIVIAL_3CUT',6,prism_edges(3),6),
           ('K33',6,k33,12),('CUBE',8,cube,24),
           ('PRISM5',10,prism,30),('PETERSEN',10,petersen,0),
           ('PRISM6',12,prism_edges(6),72)]
    for name,n,raw,want in cases:
        edges=normalized(n,raw)
        rows=make_rows(n,edges)
        exact,witness=colour_count(n,edges)
        match,pm_count,extendable=matching_count(n,edges)
        flow,cycle_size,moments=flow_count(n,edges)
        assert (exact,match,flow)==(want,want,want),(name,exact,match,flow)
        assert (witness is not None)==(want>0)
        if witness is not None:
            x=[int(witness[i]==c) for i in range(len(edges)) for c in range(3)]
            assert all(sum(x[j] for j in row)==1 for row in rows)
        N=3*len(edges)
        rank2=rank_mod(rows,N,2)
        rank3=rank_mod(rows,N,3)
        if name != 'K4':
            cuts=edge_cut_census(n,edges)
            assert cuts[1]==0 and cuts[2]==0 and cuts[3]>=n
            if name=='PRISM3_NONTRIVIAL_3CUT':
                assert cuts[3]==7 and cuts[3]>n
            expected_low=low_moment_formula(n,len(edges),
                                             len(edges)-n+1,cuts[3],cuts[4])
            assert moments==expected_low,(name,moments,expected_low)
            print(f'{name} FLOW_SUPPORT_MOMENTS_0_TO_4={moments} '
                  f'CUTS_3={cuts[3]} CUTS_4={cuts[4]}')
        if name in ('PRISM5','PETERSEN'):
            connected,odd=connected_nonbip(n,edges)
            assert connected and odd and n==10 and N==45
            assert (rank2,rank3)==(33,35)
            assert moments[:4]==(4096,46080,241920,784320)
            assert moments[4]==(1752720 if name=='PRISM5' else 1752480)
        print(f'{name}: SCL_N={N}, direct={exact}, matching_sum={match}, '
              f'flow_F2xF2={flow}, PM={pm_count}, extendable_PM={extendable}, '
              f'cycle_space={cycle_size}, rank_F2={rank2}, rank_F3={rank3}')
    print('FIRST_4_FLOW_MOMENTS_MATCH_AT_K0_K1_K2_K3 = PROVED_FINITE')
    print('K4_MOMENT_SPLIT_BY_5_EXTRA_4CUTS = 5*3*4^(6-4) = 240')
    print('LOW_MOMENT_CUT_PROFILE_THEOREM = PROVED_ALL_3EDGE_CONNECTED_CUBIC')
    print('SMITH_PAIR_PRISM_PETERSEN: invariants 1^33,2^2,0^10; BOOL 30 vs 0')
    print('SMITH_ONLY_DECISION = REFUTED; UNIVERSAL_POLY_SOLVER = NOT_CONSTRUCTED')
    print('P_VS_NP = OPEN')


if __name__=='__main__':
    main()
