#!/usr/bin/env python3
"""Independent original-source audit: Petersen 6-pole Boolean <=1 gate.

Petersen fragment (three disjoint severed cycle edges) boundary predicate
T_i = [same colour at corresponding cut ends].
Exact boundary relation {000,100,010,001}; no 111 since this would
recolour the original Petersen snark. Contrary to naïve expectation,
it is NOT a stand-alone reusable exact-one gate: glued to C6 XOR
all six ports are consumed, though internal signals become one-hot.

The glued simple cubic graph is SCL72 SAT with exactly 36 proper
edge-colourings, independently verified against every ORIGINAL row.
"""
from collections import Counter, defaultdict
from itertools import product


def petersen():
    e=set()
    def add(a,b):e.add(tuple(sorted((a,b))))
    for i in range(5):
        add(i,(i+1)%5)
        add(i,5+i)
        add(5+i,5+(i+2)%5)
    return sorted(e)


CUT = ((0,1),(2,3),(5,8))


def enumerate_degree2_ports(nv, edges, port_vertices):
    edges=tuple(tuple(sorted(e)) for e in edges)
    incidence={v:[] for v in range(nv)}
    for j,(a,b) in enumerate(edges):
        incidence[a].append(j);incidence[b].append(j)
    assert all(len(incidence[v])==(2 if v in port_vertices else 3)
               for v in range(nv))
    colour=[-1]*len(edges)
    def rec(i):
        if i==len(edges):
            ports=tuple(3-sum(colour[j] for j in incidence[v]) for v in port_vertices)
            yield ports,dict(zip(edges,colour))
            return
        u,v=edges[i]
        for c in range(3):
            if all(colour[j]!=c for w in (u,v) for j in incidence[w] if j<i):
                colour[i]=c
                yield from rec(i+1)
                colour[i]=-1
    yield from rec(0)


def enumerate_sixcycle():
    for es in product(range(3),repeat=6):
        if any(es[i]==es[(i-1)%6] for i in range(6)):continue
        ports=tuple(3-es[(i-1)%6]-es[i] for i in range(6))
        edges={tuple(sorted((i,(i+1)%6))):es[i] for i in range(6)}
        yield ports,edges


def legal_scl_and_witness(edges, nv, colouring):
    e=tuple(sorted(tuple(sorted(a)) for a in edges))
    assert len(e)==len(set(e))
    assert all(sum(v in pair for pair in e)==3 for v in range(nv))
    rows=[frozenset((edge,c) for c in range(3)) for edge in e]
    for v in range(nv):
        for c in range(3):
            rows.append(frozenset((edge,c) for edge in e if v in edge))
    assert len(rows)==3*len(e)==3*24==72
    assert all(len(r)==3 for r in rows)
    vars_=set().union(*rows)
    assert len(vars_)==len(rows)
    assert all(sum(x in row for row in rows)==3 for x in vars_)
    assert all(len(a&b)<=1 for i,a in enumerate(rows) for b in rows[i+1:])
    witness={(edge,colouring[edge]) for edge in e}
    assert all(len(row&witness)==1 for row in rows)


def main():
    pe=petersen()
    assert len(pe)==15 and set(CUT)<=set(pe)
    remain=[e for e in pe if e not in CUT]
    ports_vertices=tuple(CUT[i][side] for side in (0,1) for i in range(3))
    ps=defaultdict(list)
    for p,assigned in enumerate_degree2_ports(10,remain,ports_vertices):
        bits=tuple(int(p[i]==p[i+3]) for i in range(3))
        assert bits!=(1,1,1), ("incorrect Petersen 3-edge-coloring",p)
        ps[p].append(assigned)
    bitcounts=Counter()
    for p, assignments in ps.items():
        bitcounts[tuple(int(p[i]==p[i+3]) for i in range(3))] += len(assignments)
    assert set(bitcounts)=={(0,0,0),(1,0,0),(0,1,0),(0,0,1)}
    assert len(ps)==84 and sum(len(v) for v in ps.values())==108
    assert bitcounts[(0,0,0)]==36
    assert all(bitcounts[x]==24 for x in ((1,0,0),(0,1,0),(0,0,1)))
    print("PETERSEN_6POLE: 108 internal colourings,84 boundary colour signatures,")
    print("  exact Boolean relation {000,100,010,001}; 111 excluded PASS")

    cs=defaultdict(list)
    for p,assigned in enumerate_sixcycle():
        cs[p].append(assigned)
    assert sum(len(v) for v in cs.values())==66 and len(cs)==63
    total=0
    bits=Counter()
    for signature in sorted(set(cs)&set(ps)):
        t=tuple(int(signature[i]==signature[i+3]) for i in range(3))
        assert sum(t)==1
        for ce in cs[signature]:
            for q in ps[signature]:
                col=dict(ce)
                col.update({(a+6,b+6):v for (a,b),v in q.items()})
                for i,v in enumerate(ports_vertices):
                    edge=tuple(sorted((i,6+v)))
                    col[edge]=signature[i]
                legal_scl_and_witness(col,16,col)
                total+=1
                bits[t]+=1
    assert total==36 and set(bits)=={(1,0,0),(0,1,0),(0,0,1)}
    print("C6_PLUS_PETERSEN_CLOSED: 16 cubic vertices,24 edges, native SCL72;")
    print(f"  {total} complete independently source-replayed 3-edge colourings PASS")
    print("INTERNAL_BOOLEAN_ONEHOT: intersection of XOR odd and at-most-one")
    print("  forces exactly one TRUE among three CLOSED bits, not an exposed 3-port gate")
    print("UNBOUNDED_NATIVE_PC_DEGREE=OPEN; GLOBAL_CSP_BACKSIM=OPEN; P_VS_NP=OPEN")


if __name__=="__main__":
    main()
