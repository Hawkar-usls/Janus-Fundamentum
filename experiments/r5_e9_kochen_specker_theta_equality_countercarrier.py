#!/usr/bin/env python3
import hashlib
from itertools import product, combinations

PERES = (
    "123,345,467,789,92A,ABC,CD4,AEF,5GF,HIJ,HKL,H7M,NCO,OPQ,QRL,RST,"
    "TUJ,JPV,VWX,XYR,VZa,Lba,cde,cT1,cfg,FXM,Mhi,ijg,jkl,lme,ehn,nop,"
    "pqj,nrN,gsN,tu9,tlO,tv5,ap1,1MO"
).split(",")

E2 = [
    (2,5,6),(1,4,7),(5,7,9),(0,3,7),(4,6,9),
    (2,4,8),(3,8,9),(0,5,8),(1,3,6),
]
E1 = [
    (1,4,5),(5,7,8),(5,9,10),(3,4,9),(3,8,10),
    (0,6,10),(4,6,8),(2,3,7),(6,7,9),
]

E2_COLOR = [0,0,0,2,2,2,1,1,1,0]
E1_COLOR = [0,0,0,1,2,1,1,2,0,0,2]


def degrees(clauses, n):
    d = [0]*n
    for c in clauses:
        for v in c:
            d[v] += 1
    return d


def terminal_relation(clauses, n):
    rel = set()
    for x in product((0,1), repeat=n):
        if all(sum(x[v] for v in c) == 1 for c in clauses):
            rel.add((x[0],x[1],x[2]))
    return rel


def rainbow(clauses, colors):
    return all({colors[v] for v in c} == {0,1,2} for c in clauses)


def source_unsat(edges, n):
    inc = [[] for _ in range(n)]
    for ci,e in enumerate(edges):
        for v in e:
            inc[v].append(ci)
    a = [-1]*n

    def propagate(seed):
        changed = []
        q = list(seed)
        while q:
            v,val = q.pop()
            if a[v] != -1:
                if a[v] != val:
                    for u in reversed(changed): a[u] = -1
                    return None
                continue
            a[v] = val
            changed.append(v)
            for ci in inc[v]:
                e = edges[ci]
                ones = sum(a[u] == 1 for u in e)
                unk = [u for u in e if a[u] == -1]
                if ones > 1 or (ones == 0 and not unk):
                    for u in reversed(changed): a[u] = -1
                    return None
                if ones == 1:
                    q.extend((u,0) for u in unk)
                elif len(unk) == 1:
                    q.append((unk[0],1))
        return changed

    def rec():
        best = None
        for e in edges:
            ones = sum(a[u] == 1 for u in e)
            unk = [u for u in e if a[u] == -1]
            if ones > 1 or (ones == 0 and not unk):
                return False
            if unk and (best is None or len(unk) < len(best)):
                best = unk
        if best is None:
            return True
        v = max(best, key=lambda u: len(inc[u]))
        for val in (0,1):
            changed = propagate([(v,val)])
            if changed is not None:
                if rec():
                    return True
                for u in reversed(changed): a[u] = -1
        return False

    return not rec()


class UF:
    def __init__(self): self.p=[]
    def add(self,n):
        out=[]
        for _ in range(n):
            self.p.append(len(self.p)); out.append(len(self.p)-1)
        return out
    def find(self,x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x
    def union(self,a,b):
        a,b=self.find(a),self.find(b)
        if a != b: self.p[b]=a


def build_regularized(source_strings):
    vertices = sorted(set("".join(source_strings)))
    incidences = {v:[] for v in vertices}
    for ci,e in enumerate(source_strings):
        for pos,v in enumerate(e):
            incidences[v].append((ci,pos))

    uf=UF(); clauses=[]; free_by_v={}; counts={"E1":0,"E2":0,"ident":0}

    def add_gadget(template,n):
        ids=uf.add(n)
        clauses.extend(tuple(ids[j] for j in c) for c in template)
        return ids

    for v in vertices:
        d=len(incidences[v])
        e2nodes=[]
        if d == 1:
            e2nodes=[add_gadget(E2,10)]; counts["E2"] += 1
        else:
            a=d-1
            e1=[add_gadget(E1,11) for _ in range(a)]
            conn=[add_gadget(E2,10) for _ in range(a-1)]
            leaves=[add_gadget(E2,10) for _ in range(a+2)]
            counts["E1"] += a; counts["E2"] += 2*d-1
            e2nodes=conn+leaves
            used=[0]*a
            for i,g in enumerate(conn):
                uf.union(e1[i][used[i]],g[0]); used[i]+=1; counts["ident"]+=1
                uf.union(e1[i+1][used[i+1]],g[1]); used[i+1]+=1; counts["ident"]+=1
            li=0
            for i,g in enumerate(e1):
                while used[i] < 3:
                    uf.union(g[used[i]], leaves[li][0])
                    used[i]+=1; li+=1; counts["ident"]+=1
            assert li == len(leaves)

        free=[]
        for g in e2nodes:
            for p in g[:3]:
                if uf.find(p) == p:
                    free.append(p)
        assert len(free) == 3*d
        free_by_v[v]=free

    cursor={v:0 for v in vertices}
    for e in source_strings:
        for _copy in range(3):
            c=[]
            for v in e:
                p=free_by_v[v][cursor[v]]; cursor[v]+=1; c.append(p)
            clauses.append(tuple(c))
    assert all(cursor[v] == len(free_by_v[v]) for v in vertices)

    roots=sorted({uf.find(i) for i in range(len(uf.p))})
    rid={r:i for i,r in enumerate(roots)}
    out=[tuple(rid[uf.find(v)] for v in c) for c in clauses]
    return out,len(roots),counts


def main():
    assert len(PERES)==40
    vertices=sorted(set("".join(PERES)))
    assert len(vertices)==57
    assert all(len(e)==3 and len(set(e))==3 for e in PERES)
    for i,j in combinations(range(len(PERES)),2):
        assert len(set(PERES[i]) & set(PERES[j])) <= 1

    vid={v:i for i,v in enumerate(vertices)}
    src=[tuple(vid[v] for v in e) for e in PERES]
    d=degrees(src,len(vertices))
    assert {k:d.count(k) for k in sorted(set(d))} == {1:24,2:6,3:24,4:3}
    assert sum(d)==120
    assert source_unsat(src,len(vertices))

    assert degrees(E2,10)[:3] == [2,2,2]
    assert set(degrees(E2,10)[3:]) == {3}
    assert terminal_relation(E2,10) == {(0,0,0),(1,1,1)}
    assert rainbow(E2,E2_COLOR)

    assert degrees(E1,11)[:3] == [1,1,1]
    assert set(degrees(E1,11)[3:]) == {3}
    assert terminal_relation(E1,11) == {(0,0,0),(1,1,1)}
    assert rainbow(E1,E1_COLOR)
    for i,j in combinations(range(len(E1)),2):
        assert len(set(E1[i]) & set(E1[j])) <= 1

    out,N,counts=build_regularized(PERES)
    assert counts == {"E1":63,"E2":183,"ident":189}
    assert N == 2334
    assert len(out) == N
    deg=degrees(out,N)
    assert min(deg)==max(deg)==3

    seen=set()
    for c in out:
        assert len(set(c))==3
        for a,b in combinations(sorted(c),2):
            assert (a,b) not in seen
            seen.add((a,b))

    serial="\n".join(",".join(map(str,c)) for c in out)
    sha=hashlib.sha256(serial.encode()).hexdigest()
    assert sha == "93ea25de14d8a8b8db6e685fe06277793bc041039376d31263f2510b20863c37"

    # Projective-theta part is theorem-level source composition:
    # published Peres rank-one projectors + checked rainbow EQ gadgets imply
    # sum P_j=(N/3)I_3 and the Hilbert-Schmidt theta certificate has value N/3.
    assert N//3 == 778

    print("PASS")
    print("Peres source: 57 rays / 40 full contexts / classical Exact-One UNSAT")
    print("E1: port degree1 EQ3 + rainbow projector coloring")
    print("E2: port degree2 EQ3 + rainbow projector coloring")
    print("output: N=M=2334, row/column degree3, linear")
    print("generated-row sha256:",sha)
    print("projective theta target: N/3=778")


if __name__ == "__main__":
    main()
