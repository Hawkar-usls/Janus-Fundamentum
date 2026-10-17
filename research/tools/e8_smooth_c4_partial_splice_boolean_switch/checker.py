#!/usr/bin/env python3
"""Exact replay for v8.2 partial-splice Boolean switch normal form."""

from collections import Counter, defaultdict
from itertools import combinations, permutations, product

D = range(3)
SIGNS = (1, 2)  # +1,-1 in GF(3)
PORTS = (("L",0),("L",2),("L",3),("R",0),("R",2),("R",3))
INTERNAL = ((('L',0),('R',3)), (('L',2),('R',0)), (('L',3),('R',2)))
PAIR_QS = list(product(SIGNS, repeat=2))
TRIPLE_QS = list(product(SIGNS, repeat=3))
EQ_MASK = (1<<0) | (1<<3)
IMP_AB_MASK = (1<<0) | (1<<1) | (1<<3)
IMP_BA_MASK = (1<<0) | (1<<2) | (1<<3)
FULL2 = (1<<4)-1
OR3 = (1<<8)-2       # all except (+,+,+), tuple index 0
REV_OR3 = (1<<7)-1   # all except (-,-,-), tuple index 7
NAE3 = ((1<<8)-1) ^ 1 ^ (1<<7)


def boundary(c,s,q):
    return {
        ('L',0):(c+s)%3,
        ('L',2):(c+s*q)%3,
        ('L',3):c,
        ('R',0):(c+s*q)%3,
        ('R',2):(c-s*(1+q))%3,
        ('R',3):(c+s*(q-1))%3,
    }

STATES = [(c,s,q,boundary(c,s,q)) for c in D for s in SIGNS for q in SIGNS]
QSTATES = {q:[x for x in STATES if x[2]==q] for q in SIGNS}


def mat_vec(M,x):
    return tuple(sum(M[i][j]*x[j] for j in range(3))%3 for i in range(3))

def mat_mul(A,B):
    return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(3))%3 for j in range(3)) for i in range(3))


def verify_normal_form():
    assert len(STATES)==12
    M=((0,1,0),(2,2,0),(2,1,1))
    I=((1,0,0),(0,1,0),(0,0,1))
    M2=mat_mul(M,M); M3=mat_mul(M2,M)
    assert M3==I
    patterns=Counter()
    for c,s,q,B in STATES:
        L=(B[('L',0)],B[('L',2)],B[('L',3)])
        R=(B[('R',0)],B[('R',2)],B[('R',3)])
        assert L[0]!=L[2] and L[1]!=L[2]
        assert R==mat_vec(M,L)
        # q is exactly equality-vs-disequality of L0,L2
        assert (q==1) == (L[0]==L[1])
        # canonical equality partition of the six-boundary word
        word=L+R
        ren={}; nxt=0; pat=[]
        for z in word:
            if z not in ren:
                ren[z]=nxt; nxt+=1
            pat.append(ren[z])
        patterns[tuple(pat)]+=1
    assert patterns==Counter({(0,0,1,0,0,1):6,(0,1,2,1,2,0):6})


def no_cycle(num_wires, splices):
    vertices=[(w,p) for w in range(num_wires) for p in PORTS]
    adj={v:[] for v in vertices}
    for w in range(num_wires):
        for p,r in INTERNAL:
            a=(w,p); b=(w,r); adj[a].append(b); adj[b].append(a)
    for a,b in splices:
        if a[0]==b[0]: return False
        adj[a].append(b); adj[b].append(a)
        if len(adj[a])>2 or len(adj[b])>2: return False
    seen=set()
    for v in vertices:
        if v in seen: continue
        stack=[v]; cc=[]
        while stack:
            x=stack.pop()
            if x in seen: continue
            seen.add(x); cc.append(x); stack.extend(adj[x])
        if cc and all(len(adj[x])==2 for x in cc):
            return False
    return True


def two_q_mask(edges):
    mask=0
    for i,(qa,qb) in enumerate(PAIR_QS):
        ok=False
        for A in QSTATES[qa]:
            for B in QSTATES[qb]:
                if all(A[3][pa] != B[3][pb] for pa,pb in edges):
                    ok=True; break
            if ok: break
        if ok: mask |= 1<<i
    return mask


def two_wire_classification():
    # k=1,2 are always q-universal in the complete six-port language.
    for k,expected_total,expected_open in ((1,36,36),(2,450,432)):
        rc=Counter(); total=open_count=0
        for As in combinations(PORTS,k):
            for Bs in combinations(PORTS,k):
                for perm in permutations(Bs):
                    edges=tuple(zip(As,perm)); total+=1
                    sp=tuple(((0,a),(1,b)) for a,b in edges)
                    if not no_cycle(2,sp): continue
                    open_count+=1; rc[two_q_mask(edges)]+=1
        assert (total,open_count)==(expected_total,expected_open)
        assert rc==Counter({FULL2:expected_open})

    rc=Counter(); eq_edges=[]; total=open_count=0
    for As in combinations(PORTS,3):
        for Bs in combinations(PORTS,3):
            for perm in permutations(Bs):
                edges=tuple(zip(As,perm)); total+=1
                sp=tuple(((0,a),(1,b)) for a,b in edges)
                if not no_cycle(2,sp): continue
                open_count+=1
                m=two_q_mask(edges); rc[m]+=1
                if m==EQ_MASK: eq_edges.append(edges)
    assert (total,open_count)==(2400,2112)
    assert rc==Counter({FULL2:1752,IMP_AB_MASK:168,IMP_BA_MASK:168,EQ_MASK:24})
    assert len(eq_edges)==24

    allowed_sets={frozenset((('L',0),('L',2),('R',2))),
                  frozenset((('L',0),('R',0),('R',2)))}
    used_A={frozenset(a for a,b in e) for e in eq_edges}
    used_B={frozenset(b for a,b in e) for e in eq_edges}
    assert used_A==allowed_sets and used_B==allowed_sets
    assert all(('L',0) in s and ('R',2) in s for s in allowed_sets)

    eq_w=((('L',0),('L',0)),(('L',2),('L',2)),(('R',2),('R',2)))
    imp_w=((('L',0),('L',0)),(('L',2),('L',2)),(('L',3),('R',0)))
    assert two_q_mask(eq_w)==EQ_MASK
    assert two_q_mask(imp_w)==IMP_AB_MASK


def cross_edges_three():
    out=[]
    for i,j in combinations(range(3),2):
        for p in PORTS:
            for q in PORTS:
                out.append(((i,p),(j,q)))
    return out

CROSS3=cross_edges_three()


def gen_matchings(k):
    def rec(start,chosen,used):
        if len(chosen)==k:
            yield tuple(chosen); return
        for idx in range(start,len(CROSS3)):
            a,b=CROSS3[idx]
            if a in used or b in used: continue
            yield from rec(idx+1,chosen+[CROSS3[idx]],used|{a,b})
    yield from rec(0,[],set())


def precompute_edge_masks():
    # For each q-triple there are 6^3 choices of (c,s), encoded in one Python int.
    out={}; full=(1<<216)-1
    for qi,qs in enumerate(TRIPLE_QS):
        assignments=list(product(*(QSTATES[q] for q in qs)))
        assert len(assignments)==216
        for e in CROSS3:
            a,b=e; bits=0
            for idx,ss in enumerate(assignments):
                if ss[a[0]][3][a[1]] != ss[b[0]][3][b[1]]:
                    bits |= 1<<idx
            out[(qi,e)]=bits
    return out,full


def three_mask(splices,edge_masks,full):
    mask=0
    for qi in range(8):
        bits=full
        for e in splices:
            bits &= edge_masks[(qi,e)]
            if not bits: break
        if bits: mask |= 1<<qi
    return mask


def three_wire_or_minimality():
    edge_masks,full=precompute_edge_masks()
    expected_stats={1:(108,108),2:(4590,4536),3:(99000,95328),4:(1166400,1074816)}
    for k in range(1,5):
        total=open_count=0
        for sp in gen_matchings(k):
            total+=1
            if not no_cycle(3,sp): continue
            open_count+=1
            assert three_mask(sp,edge_masks,full) not in (OR3,REV_OR3,NAE3)
        assert (total,open_count)==expected_stats[k]

    witness=(
        ((0,('L',0)),(1,('L',0))),
        ((0,('L',2)),(1,('L',3))),
        ((0,('R',0)),(2,('L',0))),
        ((1,('L',2)),(2,('L',2))),
        ((1,('R',3)),(2,('R',0))),
    )
    assert no_cycle(3,witness)
    assert three_mask(witness,edge_masks,full)==OR3
    loads=Counter(v[0] for e in witness for v in e)
    assert [loads[i] for i in range(3)]==[3,4,3]

    # Forest has 4 path components / 8 leaves.
    vertices=[(w,p) for w in range(3) for p in PORTS]
    adj={v:[] for v in vertices}
    for w in range(3):
        for p,r in INTERNAL:
            adj[(w,p)].append((w,r)); adj[(w,r)].append((w,p))
    for a,b in witness:
        adj[a].append(b); adj[b].append(a)
    leaves=sum(len(adj[v])==1 for v in vertices)
    edges=sum(len(x) for x in adj.values())//2
    assert edges==14 and leaves==8


def main():
    verify_normal_form()
    two_wire_classification()
    three_wire_or_minimality()
    print("PASS: six-boundary relation = two S3 pattern orbits, 6+6 states")
    print("PASS: boundary transfer is GF(3)-linear with M^3=I")
    print("PASS: exact (c,s,q) normal form; q is the Boolean equality switch")
    print("PASS: two-wire k=3 q-relations = EQ 24 / IMP 168+168 / FULL 1752")
    print("PASS: every direct EQ consumes critical ports L0 and R2 on both wires")
    print("PASS: no OR/reverse-OR/NAE source-open three-wire matching exists for k<=4")
    print("PASS: explicit k=5 forest realizes OR_3 with port loads 3,4,3")
    print("VERDICT: PARTIAL_SPLICE_EXPOSES_BOOLEAN_EQ_IMP_OR_BUT_DIRECT_EQ_FANOUT_IS_CAPACITY_BLOCKED")
    print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")

if __name__ == '__main__':
    main()
