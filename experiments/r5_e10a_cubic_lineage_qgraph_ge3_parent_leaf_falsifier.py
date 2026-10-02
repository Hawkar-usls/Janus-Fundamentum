#!/usr/bin/env python3
import json

N=15
SHIFTS=(0,1,4)
M=N+1

def rank(vecs):
    B={}
    for x in vecs:
        y=x
        while y:
            p=y.bit_length()-1
            if p in B:
                y ^= B[p]
            else:
                B[p]=y
                break
    return len(B)

def basis(vecs):
    B={}
    for x in vecs:
        y=x
        while y:
            p=y.bit_length()-1
            if p in B:
                y ^= B[p]
            else:
                B[p]=y
                break
    return list(B.values())

cols=[]
for j in range(N):
    v=0
    for s in SHIFTS:
        v ^= 1 << ((j+s)%N)
    cols.append(v)
cols.append((1<<N)-1)
assert all(c.bit_count()==3 for c in cols[:-1])

rows=[]
for i in range(N):
    w=0
    for j in range(N):
        if (cols[j]>>i)&1:
            w |= 1<<j
    w |= 1<<N
    rows.append(w)
assert all(x.bit_count()==4 for x in rows)

R=rank(cols)
assert R==11 and rank(rows)==11
rb=basis(rows)

gstar=99
for a in range(1,1<<len(rb)):
    x=0
    for i,b in enumerate(rb):
        if (a>>i)&1:
            x ^= b
    if x:
        gstar=min(gstar,x.bit_count())
assert gstar==4
assert (R-2)*gstar == 36 and 2*M == 32

bad12=0
sep3=0
for mask in range(1,1<<M):
    k=mask.bit_count()
    if k>M//2:
        continue
    X=[cols[i] for i in range(M) if (mask>>i)&1]
    Y=[cols[i] for i in range(M) if not ((mask>>i)&1)]
    lam=rank(X)+rank(Y)-R
    if k>=2 and M-k>=2 and lam<2:
        bad12+=1
    if k>=3 and M-k>=3 and lam==2:
        sep3+=1
assert bad12==0 and sep3==0

base=cols[:11]
assert rank(base)==11
piv={}
for i,b in enumerate(base):
    y=b
    c=1<<i
    for p in sorted(piv,reverse=True):
        if (y>>p)&1:
            y ^= piv[p][0]
            c ^= piv[p][1]
    assert y
    piv[y.bit_length()-1]=(y,c)

def coord(x):
    y=x
    c=0
    for p in sorted(piv,reverse=True):
        if (y>>p)&1:
            y ^= piv[p][0]
            c ^= piv[p][1]
    assert y==0
    return c

cc=[coord(x) for x in cols]

def rref(vs):
    B={}
    for x in vs:
        y=x
        for p in sorted(B,reverse=True):
            if (y>>p)&1:
                y ^= B[p]
        if y:
            p=y.bit_length()-1
            for q in list(B):
                if (B[q]>>p)&1:
                    B[q] ^= y
            B[p]=y
    ps=sorted(B,reverse=True)
    for p in ps:
        for q in ps:
            if q!=p and ((B[q]>>p)&1):
                B[q] ^= B[p]
    return B

contract=(0,1,2,3,4,5,7)
delete=8
keep=(6,9,10,11,12,13,14,15)
B=rref([cc[i] for i in contract])
assert len(B)==7
free=[i for i in range(11) if i not in B]
assert len(free)==4

def qcoord(x):
    y=x
    for p in sorted(B,reverse=True):
        if (y>>p)&1:
            y ^= B[p]
    q=0
    for j,pos in enumerate(free):
        if (y>>pos)&1:
            q |= 1<<j
    return q

qvals=tuple(qcoord(cc[i]) for i in keep)
assert qvals==(1,4,8,2,7,12,9,15)
S8=(1,2,4,8,14,13,11,15)
images=(1,4,15,2)
def lin(x):
    y=0
    for i in range(4):
        if (x>>i)&1:
            y ^= images[i]
    return y
assert {lin(x) for x in S8}==set(qvals)

deletion_stats=[]
for e in range(M):
    rem=[cols[i] for i in range(M) if i!=e]
    rr=rank(rem)
    punct=[]
    for row in rb:
        lo=row & ((1<<e)-1)
        hi=row>>(e+1)
        punct.append(lo | (hi<<e))
    pb=basis(punct)
    mw=99
    for a in range(1,1<<len(pb)):
        x=0
        for i,b in enumerate(pb):
            if (a>>i)&1:
                x ^= b
        if x:
            mw=min(mw,x.bit_count())
    deletion_stats.append((rr,mw))
assert all(x==(11,3) for x in deletion_stats)

# If some deletion were graphic, simplicity plus r=11,m=15 would force
# a graph with v-c=11 and average degree <3, hence a bond of size <=2,
# contradicting deletion cogirth 3.
graft_excluded=True

def parts(n,lo=1):
    if n==0:
        yield ()
        return
    for x in range(lo,n+1):
        for rest in parts(n-x,x):
            yield (x,)+rest

triangle_free_max=0
for q in range(1,7):
    for P in parts(q):
        triangle_free_max=max(
            triangle_free_max,
            sum(((s+1)*(s+1))//4 for s in P)
        )
assert triangle_free_max==12
# Even-cut would contain a graph cycle-space of dimension >=r-1=10.
# Thus graph rank <=16-10=6. Since this cycle-space lies in C*(M)
# and g*=4, that graph is simple triangle-free. The exact componentwise
# Mantel bound above gives <=12 edges, contradicting 16.
even_cut_excluded=(M>triangle_free_max)
assert even_cut_excluded

out={
  "status":"PASS_CUBIC_LINEAGE_QGRAPH_GE3_PARENT_LEAF_FALSIFIER",
  "parent":{"n":N,"H":"I+P+P^4","f":"all_ones","rank":R,"elements":M,"cogirth":gstar},
  "q_graph_certificate":{"lhs":(R-2)*gstar,"rhs":2*M,"verdict":"q_graph>=3"},
  "connectivity":{"three_connected":True,"exact_three_separations":sep3},
  "s8_minor":{"contract":contract,"delete":delete,"keep":keep,"quotient_points":qvals,"gl4_basis_images":images},
  "terminal_controls":{
    "no_S8_terminal":True,
    "graphic_or_even_cycle_excluded_by_q_graph_ge3":True,
    "graft_excluded":graft_excluded,
    "all_single_deletions_rank_cogirth":deletion_stats,
    "even_cut_excluded":even_cut_excluded,
    "triangle_free_edge_ceiling_for_graph_rank_le6":triangle_free_max
  },
  "boundary":{"GLOBAL_SOLVER_PROMOTION":"HOLD","P_VS_NP":"OPEN","P_EQ_NP":"NOT_PROVED"}
}
print(json.dumps(out,sort_keys=True))
