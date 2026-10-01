from collections import deque
from itertools import combinations, product

REPS = ((1,0),(0,1),(1,1),(1,2))


def add2(a,b):
    return ((a[0]+b[0])%3,(a[1]+b[1])%3)


def scale2(c,a):
    return ((c*a[0])%3,(c*a[1])%3)


def sign_image_columns(cols):
    image = {(0,0)}
    for col in cols:
        image = {add2(x, scale2(s,col)) for x in image for s in (1,2)}
    return image


def predicted_zero_free(counts):
    occupied = [c for c in counts if c]
    if len(occupied) < 2:
        return False  # rank-two classification scope excludes these
    if len(occupied) == 2:
        return min(occupied) == 1
    if len(occupied) == 4:
        return all(c == 1 for c in occupied)
    return False


def check_abstract_classification():
    tested = 0
    for counts in product(range(4), repeat=4):
        occupied = sum(c>0 for c in counts)
        if occupied < 2:
            continue
        cols = []
        for rep, count in zip(REPS, counts):
            cols.extend([rep]*count)
        zero_free = (0,0) not in sign_image_columns(cols)
        assert zero_free == predicted_zero_free(counts), (counts, zero_free)
        tested += 1
    assert tested == 256 - 1 - 12  # remove all-zero and 12 one-direction patterns
    return tested


def undirected(e):
    u,v=e
    return (u,v) if u<v else (v,u)


def cycle_edges(c):
    return [(c[i],c[(i+1)%len(c)]) for i in range(len(c))]


def spanning_tree(n, edges):
    adj=[[] for _ in range(n)]
    for e in edges:
        u,v=e; adj[u].append((v,e)); adj[v].append((u,e))
    seen={0}; q=deque([0]); tree=set()
    while q:
        u=q.popleft()
        for v,e in adj[u]:
            if v not in seen:
                seen.add(v); q.append(v); tree.add(e)
    assert len(seen)==n
    return tree


def tree_path(tree,n,s,t):
    adj=[[] for _ in range(n)]
    for u,v in tree:
        adj[u].append(v); adj[v].append(u)
    prev={s:None}; q=deque([s])
    while q:
        u=q.popleft()
        if u==t: break
        for v in adj[u]:
            if v not in prev:
                prev[v]=u; q.append(v)
    out=[]; cur=t
    while prev[cur] is not None:
        p=prev[cur]; out.append((p,cur)); cur=p
    return list(reversed(out))


def fundamental_cycle_matrix(n, edges):
    edges=sorted(undirected(e) for e in edges)
    idx={e:i for i,e in enumerate(edges)}
    tree=spanning_tree(n,edges)
    rows=[]
    for chord in edges:
        if chord in tree: continue
        u,v=chord
        row=[0]*len(edges); row[idx[chord]]=1
        for a,b in tree_path(tree,n,v,u):
            e=undirected((a,b)); row[idx[e]]=1 if e==(a,b) else 2
        rows.append(tuple(row))
    return rows


def combine(lam,Q):
    return tuple(sum(lam[i]*Q[i][j] for i in range(len(Q)))%3 for j in range(len(Q[0])))


def independent(a,b):
    if not any(a) or not any(b): return False
    return b != a and b != tuple((2*x)%3 for x in a)


def projected_zero_exists(lam1,lam2,Q):
    r1=combine(lam1,Q); r2=combine(lam2,Q)
    cols=list(zip(r1,r2))
    return (0,0) in sign_image_columns(cols)


def graph_from_cycles(H,Fs):
    edges=set()
    for cyc in [H]+Fs:
        for e in cycle_edges(cyc):
            ue=undirected(e); assert ue not in edges; edges.add(ue)
    return edges


def check_k4_exhaustive():
    edges={(i,j) for i in range(4) for j in range(i+1,4)}
    Q=fundamental_cycle_matrix(4,edges)
    assert len(Q)==3
    vectors=[v for v in product(range(3), repeat=3) if any(v)]
    checked=0
    for a in vectors:
        for b in vectors:
            if independent(a,b):
                assert projected_zero_exists(a,b,Q)
                checked+=1
    assert checked == 26*24
    return checked


def check_eight_vertex_samples():
    H=list(range(8))
    controls=[
        graph_from_cycles(H,[[0,3,1,5],[2,6,4,7]]),
        graph_from_cycles(H,[[0,3,1,6],[2,4,7,5]]),
    ]
    total=0
    for edges in controls:
        Q=fundamental_cycle_matrix(8,edges)
        assert len(Q)==9
        lambdas=[]
        for i in range(9):
            e=[0]*9; e[i]=1; lambdas.append(tuple(e))
        for i in range(9):
            e=[0]*9; e[i]=1; e[(i+1)%9]=1; lambdas.append(tuple(e))
        for a,b in combinations(lambdas,2):
            if independent(a,b):
                assert projected_zero_exists(a,b,Q)
                total+=1
    return total


def cycle_rank_of_edge_set(n, edge_set):
    vertices=set()
    adj={}
    for u,v in edge_set:
        vertices.update((u,v)); adj.setdefault(u,[]).append(v); adj.setdefault(v,[]).append(u)
    seen=set(); components=0
    for s in vertices:
        if s in seen: continue
        components+=1; q=[s]; seen.add(s)
        while q:
            u=q.pop()
            for v in adj.get(u,[]):
                if v not in seen: seen.add(v); q.append(v)
    return len(edge_set)-len(vertices)+components if vertices else 0


def check_simple_four_edge_cycle_rank():
    all_edges=[(i,j) for i in range(5) for j in range(i+1,5)]
    for r in range(5):
        for subset in combinations(all_edges,r):
            assert cycle_rank_of_edge_set(5,subset) <= 1


def main():
    abstract=check_abstract_classification()
    k4=check_k4_exhaustive()
    samples=check_eight_vertex_samples()
    check_simple_four_edge_cycle_rank()
    print(f'PASS: rank2 classification patterns={abstract}; K4 projections={k4}; 8-vertex sampled projections={samples}; zero always present for tested simple graphic projections.')


if __name__=='__main__':
    main()
