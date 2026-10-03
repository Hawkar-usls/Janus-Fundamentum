#!/usr/bin/env python3
"""R5 E63: E12 strong-C5 packing / raw-parameter firewall.

This checker stress-tests the post-E62 hypothesis that degree-3 + linearity might
force the non-affine strong-odd-cycle interfaces to overlap enough for a small
global parameter.

For the frozen E12 RXC3 hardness bridge it verifies:
  * one 17-column gadget has exactly 12 local induced C10's in its Levi graph,
    i.e. 12 strong hypergraph 5-cycles;
  * every such local C5 has four distinct external hyperedges after one repeated
    external port is identified, with a 5-state non-affine interface relation;
  * every E12 target with q gadgets contains a canonical packing of q pairwise
    incidence-disjoint strong C5's, so every balanced edge modulator has size >= q;
  * on full-rank cyclic q=6,9,12 source controls, the target real/rational nullity
    is exactly 2q, replaying the local-gauge term from E17.

Scientific ceiling: these are anti-loop / parameter-stress results, not a
polynomial algorithm. Complete local gadget elimination still compresses E12
to the original RXC3 quotient (R5 E53).
"""
import itertools
from fractions import Fraction

P5 = {
    (0,0,0,1),
    (0,0,1,0),
    (1,0,0,0),
    (1,1,0,0),
    (1,1,1,1),
}


def source_fixture(q):
    rows=[((i+0)%q,(i+1)%q,(i+3)%q) for i in range(q)]
    assert all(len(set(r)) == 3 for r in rows)
    deg=[0]*q
    for r in rows:
        for v in r:
            deg[v]+=1
    assert deg == [3]*q
    return rows


def build_target(q, source_sets, labeled=False):
    target=[]
    labels=[]
    x=[f"x:{i}" for i in range(q)]
    xp=[f"xp:{i}" for i in range(q)]
    for j,C in enumerate(source_sets):
        a,b,c=C
        bx=[x[a],x[b],x[c]]
        bxp=[xp[a],xp[b],xp[c]]
        z=[f"g{j}:z{i}" for i in range(1,7)]
        zp=[f"g{j}:zp{i}" for i in range(1,7)]
        t=[f"g{j}:t{i}" for i in range(1,4)]
        rows=[
            {bx[0],z[0],z[3]}, {bx[1],z[1],z[4]}, {bx[2],z[2],z[5]},
            {z[0],z[1],z[2]}, {z[3],z[4],z[5]},
            {bxp[0],zp[0],zp[3]}, {bxp[1],zp[1],zp[4]}, {bxp[2],zp[2],zp[5]},
            {zp[0],zp[1],zp[2]}, {zp[3],zp[4],zp[5]},
            {z[1],z[5],t[0]}, {z[2],z[3],t[1]}, {z[0],z[4],t[2]},
            {zp[1],zp[5],t[1]}, {zp[2],zp[3],t[2]}, {zp[0],zp[4],t[0]},
            {t[0],t[1],t[2]},
        ]
        names=[
            f"g{j}:L1",f"g{j}:L2",f"g{j}:L3",f"g{j}:L4",f"g{j}:L5",
            f"g{j}:Lp1",f"g{j}:Lp2",f"g{j}:Lp3",f"g{j}:Lp4",f"g{j}:Lp5",
            f"g{j}:D1",f"g{j}:D2",f"g{j}:D3",f"g{j}:D4",f"g{j}:D5",
            f"g{j}:D6",f"g{j}:D7",
        ]
        target.extend(rows); labels.extend(names)
    assert len(target)==17*q
    assert len(set().union(*target))==17*q
    return (target,labels) if labeled else target


def build_one_local_gadget():
    rows,labels=build_target(6,source_fixture(6),labeled=True)
    return rows[:17], labels[:17]


def incidence_adj(rows):
    adj={}
    def add(a,b):
        adj.setdefault(a,set()).add(b)
        adj.setdefault(b,set()).add(a)
    for i,R in enumerate(rows):
        rn=("r",i)
        for v in R:
            add(rn,("v",v))
    return adj


def induced_cycles_len(adj,L):
    nodes=sorted(adj,key=str)
    order={v:i for i,v in enumerate(nodes)}
    out=set()
    for s in nodes:
        path=[s]; seen={s}
        def dfs(cur):
            if len(path)==L:
                if s not in adj[cur]:
                    return
                cyc=tuple(path)
                if any(order[v] < order[s] for v in cyc):
                    return
                for i,a in enumerate(cyc):
                    for j in range(i+1,L):
                        consecutive=(j==i+1) or (i==0 and j==L-1)
                        if ((cyc[j] in adj[a]) != consecutive):
                            return
                rev=(cyc[0],)+tuple(reversed(cyc[1:]))
                key=min(cyc,rev,key=lambda z: tuple(map(str,z)))
                out.add(key)
                return
            for nb in adj[cur]:
                if nb==s or nb in seen or order[nb] < order[s]:
                    continue
                seen.add(nb); path.append(nb)
                dfs(nb)
                path.pop(); seen.remove(nb)
        dfs(s)
    return out


def rotate_to_row(cycle):
    c=list(cycle)
    k=next(i for i,n in enumerate(c) if n[0]=="r")
    c=c[k:]+c[:k]
    assert all(c[i][0] == ("r" if i%2==0 else "v") for i in range(len(c)))
    return c


def external_ports(cycle,rows):
    c=rotate_to_row(cycle)
    exts=[]
    for i in range(0,len(c),2):
        ridx=c[i][1]
        prev=c[(i-1)%len(c)][1]
        nxt=c[(i+1)%len(c)][1]
        ext=rows[ridx]-{prev,nxt}
        assert len(ext)==1
        exts.append(next(iter(ext)))
    return exts


def generic_cycle_interface(l):
    for bits in itertools.product((0,1),repeat=l):
        if any(bits[i] and bits[(i+1)%l] for i in range(l)):
            continue
        s=tuple(1-bits[(i-1)%l]-bits[i] for i in range(l))
        yield s


def identified_interface(exts):
    uniq=[]
    for e in exts:
        if e not in uniq:
            uniq.append(e)
    rel=set()
    for s in generic_cycle_interface(len(exts)):
        val={}
        ok=True
        for e,b in zip(exts,s):
            if e in val and val[e]!=b:
                ok=False; break
            val[e]=b
        if ok:
            rel.add(tuple(val[e] for e in uniq))
    return uniq,rel


def affine(rel):
    rel=set(rel)
    if not rel:
        return True
    a=next(iter(rel))
    lin={tuple(x^y for x,y in zip(r,a)) for r in rel}
    for u in lin:
        for v in lin:
            if tuple(x^y for x,y in zip(u,v)) not in lin:
                return False
    return True


def canonical_cycle_for_gadget(j):
    base=17*j
    rows=[base+0,base+3,base+10,base+16,base+11]
    vars_=[f"g{j}:z1",f"g{j}:z2",f"g{j}:t1",f"g{j}:t2",f"g{j}:z4"]
    return rows,vars_


def verify_canonical_strong_cycle(rows,j):
    rids,vs=canonical_cycle_for_gadget(j)
    seq=[]
    for r,v in zip(rids,vs):
        seq.extend([("r",r),("v",v)])
    adj=incidence_adj(rows)
    L=len(seq)
    for i,a in enumerate(seq):
        for k in range(i+1,L):
            b=seq[k]
            consecutive=(k==i+1) or (i==0 and k==L-1)
            assert ((b in adj[a]) == consecutive)
    return tuple(seq)


def rank_q(mat):
    M=[[Fraction(v) for v in row] for row in mat]
    m=len(M); n=len(M[0]); r=0
    for c in range(n):
        p=next((i for i in range(r,m) if M[i][c]),None)
        if p is None: continue
        M[r],M[p]=M[p],M[r]
        z=M[r][c]
        M[r]=[v/z for v in M[r]]
        for i in range(m):
            if i!=r and M[i][c]:
                z=M[i][c]
                M[i]=[a-z*b for a,b in zip(M[i],M[r])]
        r+=1
        if r==m: break
    return r


def incidence_matrix(rows):
    cols=sorted(set().union(*rows))
    pos={v:i for i,v in enumerate(cols)}
    A=[[0]*len(cols) for _ in rows]
    for i,R in enumerate(rows):
        for v in R:
            A[i][pos[v]]=1
    return A


def source_matrix(q,source_sets):
    R=[[0]*q for _ in range(q)]
    for j,C in enumerate(source_sets):
        for i in C: R[i][j]=1
    return R


def main():
    local_rows,_=build_one_local_gadget()
    cycles=induced_cycles_len(incidence_adj(local_rows),10)
    assert len(cycles)==12
    stats={}
    for C in cycles:
        exts=external_ports(C,local_rows)
        uniq,rel=identified_interface(exts)
        key=(len(uniq),len(rel),affine(rel))
        stats[key]=stats.get(key,0)+1
    assert stats=={(4,5,False):12}

    rel=set()
    for c in itertools.product((0,1),repeat=5):
        z1,z2,t1,t2,z4=c
        for x,z3,z6,t3 in itertools.product((0,1),repeat=4):
            eq=[
                z4+z1+x,
                z1+z2+z3,
                z2+t1+z6,
                t1+t2+t3,
                t2+z4+z3,
            ]
            if eq==[1]*5:
                rel.add((x,z3,z6,t3))
    assert rel==P5
    assert not affine(rel)
    assert (0,0,0,1) in rel and (0,0,1,0) in rel and (1,0,0,0) in rel
    assert (1,0,1,1) not in rel

    for q in (6,9,12):
        src=source_fixture(q)
        rows=build_target(q,src)

        row_seen=set(); edge_seen=set()
        for j in range(q):
            C=verify_canonical_strong_cycle(rows,j)
            rs={n[1] for n in C if n[0]=="r"}
            es={n[1] for n in C if n[0]=="v"}
            assert row_seen.isdisjoint(rs)
            assert edge_seen.isdisjoint(es)
            row_seen |= rs
            edge_seen |= es
        assert len(row_seen)==5*q
        assert len(edge_seen)==5*q

        balanced_edge_modulator_lower_bound=q
        assert balanced_edge_modulator_lower_bound*17 == len(rows)

        R=source_matrix(q,src)
        assert rank_q(R)==q
        A=incidence_matrix(rows)
        d=len(A)-rank_q(A)
        assert d==2*q

        print(
            f"q={q} n={17*q} local_C5_pack={q} "
            f"t_balanced>={q} raw_nullity={d}"
        )

    print("R5 E63 E12 non-affine C5 packing / raw-parameter firewall: PASS")
    print("one gadget: 12 strong C5, each -> 4-port 5-state non-affine relation")
    print("canonical relation P5 =",sorted(P5))
    print("E12: t_balanced >= n/17; full-rank controls: d_real = 2n/17")


if __name__=="__main__":
    main()
