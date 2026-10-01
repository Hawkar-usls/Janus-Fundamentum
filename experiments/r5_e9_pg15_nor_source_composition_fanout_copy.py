#!/usr/bin/env python3
"""Exact PG15 NOR source-composition checker.

Proves finite local facts used by the source-preserving composition theorem:
- canonical PG15 has exactly four Boolean models and terminals (o,a,b) form NOR;
- deleting the fixed four port rows leaves exactly the same four models;
- every fixed output/input port switch is exactly an equality wire;
- exhaustive one-switch serial census has 36 exact hits;
- exhaustive natural two-switch fanout-2 class has 216 exact source-valid hits;
- tied-input NOT has 54 semantic hits, of which exactly 36 preserve linearity;
- every pair of source-valid NOT templates composes to exact COPY (1296/1296);
- direct output pin0 and derived output pin1 gadgets are exact and source-valid.
"""
from itertools import product, combinations
from functools import lru_cache

ROWS1 = [
    (1,2,3),(1,10,11),(1,12,13),(2,9,11),(2,12,14),
    (3,4,7),(3,5,6),(4,9,13),(4,10,14),(5,8,13),
    (5,10,15),(6,8,14),(6,9,15),(7,8,15),(7,11,12),
]
ROWS = [tuple(x-1 for x in r) for r in ROWS1]
N = 15
TERMS = (11,12,13)  # output, input0, input1
NOR = {(0,1,1),(1,0,0),(0,1,0),(0,0,1)}


def enumerate_models(skip=()):
    skip=set(skip)
    out=[]
    for bits in product((0,1), repeat=N):
        if all(sum(bits[j] for j in row)==1
               for i,row in enumerate(ROWS) if i not in skip):
            out.append(bits)
    return tuple(out)


FULL = enumerate_models()
assert len(FULL) == 4
assert {tuple(m[j] for j in TERMS) for m in FULL} == NOR
assert len({tuple(m[j] for j in TERMS) for m in FULL}) == len(FULL)


@lru_cache(None)
def open_models(skip_tuple):
    return enumerate_models(skip_tuple)


def make_copies(k):
    out=[]
    for c in range(k):
        off=c*N
        out.extend([list(off+j for j in row) for row in ROWS])
    return out


def swap_occ(src,c1,r1,v1,c2,r2,v2):
    i1=c1*15+r1; i2=c2*15+r2
    gv1=c1*N+v1; gv2=c2*N+v2
    assert gv1 in src[i1] and gv2 in src[i2]
    src[i1][src[i1].index(gv1)] = gv2
    src[i2][src[i2].index(gv2)] = gv1


def source_props(src,k):
    assert len(src)==15*k
    rows3=all(len(r)==3 and len(set(r))==3 for r in src)
    deg=[0]*(N*k)
    for r in src:
        for v in r:
            deg[v]+=1
    cubic=all(d==3 for d in deg)

    paircount={}
    linear=True
    for r in src:
        for a,b in combinations(sorted(r),2):
            paircount[(a,b)]=paircount.get((a,b),0)+1
            if paircount[(a,b)]>1:
                linear=False

    R=len(src); V=N*k
    adj=[[] for _ in range(R+V)]
    for i,r in enumerate(src):
        for v in r:
            adj[i].append(R+v)
            adj[R+v].append(i)
    seen={0}; stack=[0]
    while stack:
        u=stack.pop()
        for w in adj[u]:
            if w not in seen:
                seen.add(w); stack.append(w)
    connected=(len(seen)==len(adj))
    return (rows3,cubic,linear,connected)


def network_relation(k,swaps):
    """Exact projected relation after incidence switches.

    Each swap is (copy1,row1,var1,copy2,row2,var2).
    Completeness comes from enumerating every assignment satisfying all
    unchanged rows of every copy, then checking every modified row exactly.
    """
    src=make_copies(k)
    mods=[set() for _ in range(k)]
    for c1,r1,v1,c2,r2,v2 in swaps:
        swap_occ(src,c1,r1,v1,c2,r2,v2)
        mods[c1].add(r1); mods[c2].add(r2)

    choices=[open_models(tuple(sorted(s))) for s in mods]
    rel=set()
    for ass in product(*choices):
        good=True
        for c in range(k):
            for r in mods[c]:
                total=0
                for gv in src[c*15+r]:
                    cc,lv=divmod(gv,N)
                    total += ass[cc][lv]
                if total != 1:
                    good=False
                    break
            if not good:
                break
        if good:
            rel.add(tuple(bit for c in range(k)
                          for bit in (ass[c][j] for j in TERMS)))
    return rel, source_props(src,k), tuple(len(x) for x in choices)


# Exact port-row redundancy.
PORT_ROWS=(2,4,7,11)
assert set(open_models(PORT_ROWS)) == set(FULL)
for r in range(15):
    assert set(open_models((r,))) == set(FULL)

# Fixed port normal form.
OUT_PORTS=((2,11),(4,11))
IN_PORTS=((7,12),(11,13))
for ro,vo in OUT_PORTS:
    for ri,vi in IN_PORTS:
        rel,props,_ = network_relation(2,[(0,ro,vo,1,ri,vi)])
        idx=TERMS.index(vi)
        target={a+b for a in NOR for b in NOR if a[0]==b[idx]}
        assert rel==target
        assert props==(True,True,True,True)

# Exhaustive all-incidence serial equality census.
inc=[(r,v) for r,row in enumerate(ROWS) for v in row]
serial_hits=[]
for rp,vp in inc:
    for rc,vc in inc:
        for input_var in (12,13):
            rel,props,_=network_relation(2,[(0,rp,vp,1,rc,vc)])
            idx=TERMS.index(input_var)
            target={a+b for a in NOR for b in NOR if a[0]==b[idx]}
            if rel==target:
                serial_hits.append((rp,vp,rc,vc,input_var,props))
assert len(serial_hits)==36
assert all(h[-1]==(True,True,True,True) for h in serial_hits)

# Natural fanout-2 class: two distinct occurrences of producer output 11,
# each wired to one chosen consumer input occurrence.
out_rows=[r for r,row in enumerate(ROWS) if 11 in row]
in_occ={v:[r for r,row in enumerate(ROWS) if v in row] for v in (12,13)}
assert out_rows==[2,4,14]
assert in_occ=={12:[2,7,9],13:[4,8,11]}

fanout_hits=0
for pair in combinations(out_rows,2):
    for prows in (pair,pair[::-1]):
        for v1 in (12,13):
            for r1 in in_occ[v1]:
                for v2 in (12,13):
                    for r2 in in_occ[v2]:
                        swaps=[
                            (0,prows[0],11,1,r1,v1),
                            (0,prows[1],11,2,r2,v2),
                        ]
                        rel,props,_=network_relation(3,swaps)
                        i1=TERMS.index(v1); i2=TERMS.index(v2)
                        target={
                            p+c1+c2
                            for p in NOR for c1 in NOR for c2 in NOR
                            if p[0]==c1[i1] and p[0]==c2[i2]
                        }
                        if rel==target and props==(True,True,True,True):
                            fanout_hits += 1
assert fanout_hits==216

# Tied-input NOT: producer output -> both inputs of one consumer.
not_semantic=0
not_templates=[]
for pair in combinations(out_rows,2):
    for prows in (pair,pair[::-1]):
        for r12 in in_occ[12]:
            for r13 in in_occ[13]:
                swaps=[
                    (0,prows[0],11,1,r12,12),
                    (0,prows[1],11,1,r13,13),
                ]
                rel,props,_=network_relation(2,swaps)
                target={
                    p+c for p in NOR for c in NOR
                    if c[1]==p[0] and c[2]==p[0]
                }
                if rel==target:
                    not_semantic += 1
                    if props==(True,True,True,True):
                        not_templates.append((prows,r12,r13))
assert not_semantic==54
assert len(not_templates)==36

# Exact COPY = NOT composed with NOT.
copy_hits=0
target_copy={
    p+n1+n2
    for p in NOR for n1 in NOR for n2 in NOR
    if n1[1]==p[0] and n1[2]==p[0]
    and n2[1]==n1[0] and n2[2]==n1[0]
}
assert len(target_copy)==4
for prows1,r12_1,r13_1 in not_templates:
    for prows2,r12_2,r13_2 in not_templates:
        swaps=[
            (0,prows1[0],11,1,r12_1,12),
            (0,prows1[1],11,1,r13_1,13),
            (1,prows2[0],11,2,r12_2,12),
            (1,prows2[1],11,2,r13_2,13),
        ]
        rel,props,_=network_relation(3,swaps)
        if rel==target_copy and props==(True,True,True,True):
            copy_hits += 1
assert copy_hits==36*36==1296

# Direct source-valid output pin0 using the unique PG15 constant-zero
# coordinate 3 of a helper copy.
assert {m[3] for m in FULL}=={0}
pin0=[(0,14,11,1,5,3)]
rel0,props0,_=network_relation(2,pin0)
assert props0==(True,True,True,True)
assert {t[0] for t in rel0}=={0}

# Output pin1: tied-input NOT on fixed safe ports, then pin the inverter
# output to zero by the same constant-zero helper.
pin1=[
    (0,2,11,1,7,12),
    (0,4,11,1,11,13),
    (1,14,11,2,5,3),
]
rel1,props1,_=network_relation(3,pin1)
assert props1==(True,True,True,True)
assert {t[0] for t in rel1}=={1}
assert len(rel1)==4

print("PASS_PG15_NOR_SOURCE_COMPOSITION_FANOUT_NOT_COPY")
print("pg15_boolean_models=4")
print("terminal_relation=NOR(output,input0,input1)")
print("fixed_port_rows_zero_based=2,4,7,11")
print("fixed_port_skeleton_models=4")
print("serial_one_switch_exact_hits=36")
print("fanout2_exact_source_valid_hits=216_of_216")
print("tied_not_semantic_hits=54")
print("tied_not_source_linear_hits=36")
print("copy_exact_source_valid_hits=1296_of_1296")
print("pin0=PASS")
print("pin1_via_not_then_pin0=PASS")
print("ARBITRARY_DAG_COMPOSITION_PROOF=THEOREM_SIDE")
print("UNIVERSAL_SOLVER=NOT_CLAIMED")
print("E8_D1=EMPTY P_VS_NP=OPEN")
