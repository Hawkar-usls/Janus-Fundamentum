#!/usr/bin/env python3
"""BABEL38: complete linear-time 4-port U macro SAT/#SAT through global flux.

NO construction metadata passed to solve_admitted: original physical row
incidences plus the fixed-U block ROW and VARIABLE alignment only. Extract
all reciprocal crossing incidences, certify the complete macro template,
then use both independent global port2 forcing and DSU equality/pin count.
The input class is STRICT; arbitrary legal SCL is NOT claimed tractable.
"""
import hashlib
import itertools
import json
import random
from collections import Counter,deque

U=(
(0,1,2),(0,3,6),(0,5,7),(3,5,20),(1,7,11),
(3,8,12),(6,7,8),(2,5,8),(2,10,14),
(9,10,11),(9,12,15),(9,14,22),
(12,13,14),(10,13,16),(1,6,17),(15,16,17),
(4,17,20),(11,13,21),(4,18,19),(15,18,24),
(18,23,25),(19,21,26),(24,25,26),
(4,23,26),(20,22,24))
U_SHA="9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed"
PORTS=((0,0),(1,3),(2,7),(26,20))
R4=(
 (0,0,0,1,0,0,1,0), # state A=0
 (0,1,1,0,0,1,1,0), # state B=1
 (1,1,1,0,0,0,0,0)  # state C=2 (globally excluded)
)
TRUES=(
 (2,6,11,12,16,18,20,22,26),
 (2,3,7,9,13,17,19,23,24),
 (0,2,3,7,9,13,17,19,23,24)
)
LOCAL_MASKS=tuple(sum(1<<v for v in ones) for ones in TRUES)


def exact_one(rows,truth):
    return all(sum((truth>>v)&1 for v in r)==1 for r in rows)


def original_local_certificate():
    assert hashlib.sha256(json.dumps(U,separators=(",",":")).encode()).hexdigest()==U_SHA
    assert len(U)==27
    kept=[r for i,r in enumerate(U) if i not in {q for q,v in PORTS}]
    for index,(bits,ones) in enumerate(zip(LOCAL_MASKS,TRUES)):
        assert tuple(i for i in range(27) if bits>>i&1)==ones
        assert exact_one(kept,bits)
        out=tuple((bits>>v)&1 for _,v in PORTS)
        need=tuple(1-sum((bits>>v)&1 for v in U[ri] if v!=own)
                   for ri,own in PORTS)
        assert out+need==R4[index]
    assert [(sum(s[:4])-sum(s[4:])) for s in R4]==[0,0,3]
    return True


def link_relation(i,j):
    """All 16 exact two-state allowed-pair relations derived from R4 bits."""
    assert 0<=i<4 and 0<=j<4
    return frozenset((s,t) for s in range(2) for t in range(2)
        if R4[s][i]==R4[t][4+j] and R4[t][j]==R4[s][4+i])


def all_link_table():
    return {(i,j):link_relation(i,j) for i in range(4) for j in range(4)}


class DSU:
    def __init__(self,n):
        self.parent=list(range(n))
        self.size=[1]*n
        self.pin=[None]*n
        self.conflict=False

    def find(self,a):
        while a!=self.parent[a]:
            self.parent[a]=self.parent[self.parent[a]]
            a=self.parent[a]
        return a

    def union(self,a,b):
        a=self.find(a);b=self.find(b)
        if a==b:return
        if self.size[a]<self.size[b]:a,b=b,a
        self.parent[b]=a;self.size[a]+=self.size[b]
        if self.pin[b] is not None:
            self.force(a,self.pin[b])

    def force(self,a,value):
        a=self.find(a)
        if self.pin[a] is not None and self.pin[a]!=value:
            self.conflict=True
        else:self.pin[a]=value

    def finish(self):
        if self.conflict:return None,0
        representatives={self.find(i) for i in range(len(self.parent))}
        free=[r for r in representatives if self.pin[r] is None]
        chosen={r:self.pin[r] if self.pin[r] is not None else 0
                for r in representatives}
        result=[chosen[self.find(i)] for i in range(len(self.parent))]
        return result,1<<len(free)


def solve_dsu(edges,t):
    """DSU is an INDEPENDENT decision/count audit of direct port2 forcing."""
    d=DSU(t)
    table=all_link_table()
    for u,i,v,j in edges:
        p=table[(i,j)]
        if not p:return None,0,"IMPOSSIBLE_PORT_PAIR"
        if len(p)==4:continue
        if p==frozenset({(0,0),(1,1)}):
            d.union(u,v)
            continue
        # Other 14-entry types are unit pins: inspect projections.
        au={x for x,y in p};bv={y for x,y in p}
        if len(au)==1:d.force(u,next(iter(au)))
        if len(bv)==1:d.force(v,next(iter(bv)))
        # Explicit full verification below prevents false acceptance in
        # case some future local relation contains a non-rectangular pair.
        if p and len(au)>1 and len(bv)>1:
            raise AssertionError(("non-DSU relation",i,j,p))
    states,count=d.finish()
    if count==0:return None,0,"PIN_CONTRADICTION"
    assert states is not None
    assert all((states[u],states[v]) in table[(i,j)]
               for u,i,v,j in edges)
    return states,count,"COMPLETE_EQUIVALENCE_PIN_DSU"


def verify_extract_raw(original_rows):
    """Extract every edge and every port WITHOUT construction history."""
    n=len(original_rows)
    assert n and n%27==0
    t=n//27
    assert all(len(r)==3 and len(set(r))==3 and
               all(0<=v<n for v in r) for r in original_rows)
    assert Counter(v for r in original_rows for v in r)==Counter({v:3 for v in range(n)})
    pairs=[tuple(sorted(x)) for r in original_rows for x in itertools.combinations(r,2)]
    assert len(set(pairs))==3*n
    cross={}
    for block in range(t):
        for ri,original in enumerate(U):
            row=set(original_rows[27*block+ri])
            expected={27*block+v for v in original}
            retained={v for v in row if v//27==block}
            deleted=expected-retained
            imported=row-retained
            hasport=any(ri==k for k,v in PORTS)
            if not hasport:
                assert row==expected
                continue
            port_index=next(i for i,(k,v) in enumerate(PORTS) if k==ri)
            assert deleted=={27*block+PORTS[port_index][1]}
            assert len(imported)==1
            value=next(iter(imported))
            assert value//27!=block
            cross[(block,port_index)]=value
    assert len(cross)==4*t
    edges=[]
    seen=set()
    adj={i:set() for i in range(t)}
    for (block,pi),foreign in cross.items():
        neighbor=foreign//27
        endpoint_var=foreign%27
        matches=[j for j,(_,v) in enumerate(PORTS) if v==endpoint_var]
        assert len(matches)==1
        pj=matches[0]
        reverse=cross[(neighbor,pj)]
        assert reverse==27*block+PORTS[pi][1]
        if (block,pi) in seen:continue
        seen.add((block,pi));seen.add((neighbor,pj))
        if block<neighbor:edges.append((block,pi,neighbor,pj))
        else:edges.append((neighbor,pj,block,pi))
        adj[block].add(neighbor);adj[neighbor].add(block)
    edges.sort()
    assert len(seen)==4*t and len(edges)==2*t
    assert all(len(adj[v])==4 for v in adj)
    assert len({(u,v) for u,i,v,j in edges})==2*t # simple macro
    viewed={0};q=deque([0])
    while q:
        for w in adj[q.popleft()]-viewed:
            viewed.add(w);q.append(w)
    assert len(viewed)==t
    return edges,t


def solve_admitted(original_rows):
    original_local_certificate()
    edges,t=verify_extract_raw(original_rows)
    # All-n exact flux identity rules out state C; within A/B,
    # every node's edge incident to port2 forces its state!
    forces={}
    table=all_link_table()
    for u,i,v,j in edges:
        # A port2--port2 edge forces BOTH endpoints, not only one.
        for target,own_port,other_port in ((u,i,j),(v,j,i)):
            if own_port!=2:continue
            required={0:None,1:1,2:1,3:0}[other_port]
            assert target not in forces
            forces[target]=required
    assert len(forces)==t
    if any(value is None for value in forces.values()):
        direct_states=None;direct_count=0
        direct_reason="PORT2_TO_PORT0_IMPOSSIBLE"
    else:
        direct_states=[forces[i] for i in range(t)]
        conflicts=[(u,i,v,j) for u,i,v,j in edges
                   if (direct_states[u],direct_states[v]) not in table[(i,j)]]
        if conflicts:
            direct_states=None;direct_count=0
            direct_reason="FORCED_STATE_EDGE_CONTRADICTION"
        else:
            direct_count=1
            direct_reason="ALL_BLOCK_STATES_FORCED_AND_COMPATIBLE"
    dsu_states,dsu_count,dsu_reason=solve_dsu(edges,t)
    assert (direct_count==0)==(dsu_count==0),(
        "independent direct/DSU disagreement",direct_reason,dsu_reason)
    assert dsu_count in (0,1),("all block port2 bits must be forced",dsu_count)
    if direct_count:
        assert direct_states==dsu_states
        model=0
        for block,st in enumerate(direct_states):
            model|=LOCAL_MASKS[st]<<(27*block)
        assert exact_one(original_rows,model)
        status="SAT"
    else:
        model=None;status="UNSAT"
    return {
        "status":status,"n":len(original_rows),"macro_blocks":t,
        "exact_sat_count":direct_count,
        "original_2SAT_nonbijunctive_local_R4":"TRUE",
        "all_n_net_flux_excludes_C":True,
        "direct_port2_gate":direct_reason,
        "independent_equivalence_pin_DSU":dsu_reason,
        "macro_edges":len(edges),
        "verified_recovered_original_incidence_links":len(edges),
        "physical_SAT_witness":model,
        "physical_SAT_witness_true_count":model.bit_count() if model is not None else None,
        "full_original_rows_replayed":model is not None,
        "selector_states":direct_states
    }


def macro_graph(kind,n=8):
    if kind=="K5":
        return 5,tuple(itertools.combinations(range(5),2))
    if kind=="K44":
        return 8,tuple((i,4+j) for i in range(4) for j in range(4))
    assert kind=="CIRCULANT" and n>=7
    edges=set()
    for i in range(n):
        for step in (1,2):
            edges.add(tuple(sorted((i,(i+step)%n))))
            edges.add(tuple(sorted((i,(i-step)%n))))
    return n,tuple(sorted(edges))


def compile_fixture(kind,n=8,seed=0,special=False):
    t,edges=macro_graph(kind,n)
    neighbors={i:set() for i in range(t)}
    for a,b in edges:
        neighbors[a].add(b);neighbors[b].add(a)
    assert all(len(v)==4 for v in neighbors.values())
    ports={}
    rng=random.Random(seed)
    for vertex in range(t):
        choices=sorted(neighbors[vertex])
        if kind=="K44" and special:
            ports[vertex]={neighbor:(vertex+(neighbor-4))%4
                         if vertex<4 else ((neighbor)+(vertex-4))%4
                         for neighbor in choices}
        elif kind=="CIRCULANT" and special in ("ALL_A","ALL_B"):
            offsets={1:2,-1:3,2:0,-2:1} if special=="ALL_A" else {
                1:1,-1:2,2:0,-2:3}
            ports[vertex]={((vertex+offset)%t):port
                           for offset,port in offsets.items()}
        else:
            rng.shuffle(choices)
            ports[vertex]={neighbor:i for i,neighbor in enumerate(choices)}
    assert all(set(ports[v].values())=={0,1,2,3} for v in ports)
    rows=[list(27*block+v for v in row) for block in range(t) for row in U]
    for a,b in edges:
        ra,va=PORTS[ports[a][b]]
        rb,vb=PORTS[ports[b][a]]
        la=27*a+ra;lb=27*b+rb
        va+=27*a;vb+=27*b
        assert va in rows[la] and vb in rows[lb], (
            "invalid source port during independent fixture assembly",
            kind,n,seed,special,(a,b),ra,va,rb,vb,rows[la],rows[lb],
            ports[a],ports[b])
        rows[la][rows[la].index(va)]=vb
        rows[lb][rows[lb].index(vb)]=va
    return tuple(tuple(sorted(r)) for r in rows)


def finite_macro_three_state_truth_oracle(original_rows):
    """Original 3-state relation, complete Cartesian enumeration t<=8."""
    edges,t=verify_extract_raw(original_rows)
    assert t<=8
    valid=[]
    for states in itertools.product(range(3),repeat=t):
        if all(R4[states[u]][i]==R4[states[v]][4+j] and
               R4[states[v]][j]==R4[states[u]][4+i]
               for u,i,v,j in edges):
            physical=sum(LOCAL_MASKS[st]<<(27*b) for b,st in enumerate(states))
            assert exact_one(original_rows,physical)
            valid.append((states,physical))
    assert len({m for states,m in valid})==len(valid)
    assert all(2 not in states for states,mask in valid)
    return valid


def main():
    cases=[
        ("K5_UNSAT",compile_fixture("K5",seed=38)),
        ("K44_EDGE_COLORED_SAT",compile_fixture("K44",special=True)),
    ]
    for n in (7,8):
        for seed in range(6):
            cases.append((f"FULL_RANDOM_PORTS_CIRCULANT_t{n}_s{seed}",
                          compile_fixture("CIRCULANT",n=n,seed=seed)))
    for n in (12,20,40):
        for kind in ("ALL_A","ALL_B"):
            cases.append((f"FULL_SAT_CIRCULANT_{kind}_t{n}",
                          compile_fixture("CIRCULANT",n=n,special=kind)))
        for seed in (0,1,7):
            cases.append((f"LARGE_CONNECTED_CIRCULANT_t{n}_s{seed}",
                          compile_fixture("CIRCULANT",n=n,seed=seed)))
    checked=[]
    for label,rows in cases:
        output=solve_admitted(rows)
        if len(rows)//27<=8:
            oracle=finite_macro_three_state_truth_oracle(rows)
            assert len(oracle)==output["exact_sat_count"],(label,len(oracle),output)
            if oracle:
                assert output["physical_SAT_witness"]==oracle[0][1]
        if label=="K5_UNSAT":assert output["status"]=="UNSAT"
        if label=="K44_EDGE_COLORED_SAT":assert output["exact_sat_count"]==1
        if "FULL_SAT_CIRCULANT" in label:assert output["exact_sat_count"]==1
        checked.append({
            "case":label,"n":len(rows),
            "macros":output["macro_blocks"],
            "exact_sat_count":output["exact_sat_count"],
            "result":output["status"],
            "direct_port2_reason":output["direct_port2_gate"],
            "independent_DSU_reason":output["independent_equivalence_pin_DSU"],
            "complete_3_pow_t_oracle":len(rows)//27<=8,
            "original_row_witness_rechecked":output["full_original_rows_replayed"]
        })
    print(json.dumps({
        "gate":"BABEL38_CLOSED_FOURPORT_U_MACRO_GLOBAL_BALANCE",
        "all_n_global_conservation":"EXACT_THEOREM",
        "state_C_elimination":"EXACT_ALL_N",
        "all_n_port2_forces_every_block":"EXACT_THEOREM",
        "all_n_exact_sat_count":"0_OR_1",
        "direct_force_and_independent_DSU_agree":"PASS",
        "finite_full_three_state_macro_oracles":"PASS",
        "generic_unrestricted_SCL":"NOT_SOLVED",
        "P_vs_NP":"OPEN",
        "cases":checked
    },sort_keys=True,indent=2))


if __name__=="__main__":
    main()
