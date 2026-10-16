#!/usr/bin/env python3
"""E4.10 CLEAN_ROOM N90 + THREE-HEXAGON NO-GIRTH8 CERTIFICATE.

Python standard library only; NO imports from JANUS producer.
Frozen declarative matrices only:
- parent fixed legal connected UNSAT SCL45 source,
- resulting 90x90 incidence SCL after deterministic signed 2lift,
- three simple length6 cycles of the parent whose edge bitmasks
  XOR to zero (odd number of cycles).
For any edge signing, making each of these 3 cycles double
would require 3 odd GF2 equations whose XOR gives 0=1.
Thus EVERY 2lift of THIS parent retains at least one 6-cycle.
The old source has girth6; covering cannot create shorter
cycles; hence EVERY graph 2lift has girth exactly6.

Independently reconstruct parent->new rows, check legality,
connectedness, all 128 GF2 parity words (rank83/nullity7,
#SAT=0), and two distinct exact integer ternary Y witnesses.
Checks repeated source cut ratio 2/27. Does NOT infer
any all-n polynomial SAT solver or high-girth new base.
"""
import argparse,json,hashlib
from collections import deque,Counter
from itertools import combinations
from pathlib import Path


def check_legal(rows):
    n=len(rows)
    assert n%3==0 and len(rows)==n
    degree=[0]*n
    pairs=set()
    for row in rows:
        assert len(row)==3 and len(set(row))==3
        assert all(0<=v<n for v in row)
        for v in row:degree[v]+=1
        for p in combinations(sorted(row),2):
            assert p not in pairs;pairs.add(p)
    assert all(d==3 for d in degree)


def adjacency(rows):
    n=len(rows);A=[[] for _ in range(2*n)]
    for i,row in enumerate(rows):
        for j in row:
            A[i].append(n+j);A[n+j].append(i)
    return A


def connected(A):
    seen={0};q=[0]
    while q:
        for v in A[q.pop()]:
            if v not in seen:seen.add(v);q.append(v)
    return len(seen)==len(A)


def girth(A):
    best=10**9
    for start in range(len(A)):
        dist={start:0};parent={start:None}
        todo=deque([start])
        while todo:
            u=todo.popleft()
            for v in A[u]:
                if v not in dist:
                    dist[v]=dist[u]+1;parent[v]=u;todo.append(v)
                elif parent[u]!=v and parent[v]!=u:
                    best=min(best,dist[u]+dist[v]+1)
    return best


def high_pivot_kernel(rows):
    n=len(rows)
    words=[sum(1<<v for v in row) for row in rows]
    pivots={}
    for row in words:
        x=row
        while x:
            p=x.bit_length()-1
            if p in pivots:x^=pivots[p]
            else:
                pivots[p]=x;break
    basis=[]
    for j in range(n):
        if j in pivots:continue
        x=1<<j
        for p in sorted(pivots):
            if (x&pivots[p]).bit_count()%2:x|=1<<p
        assert all((x&r).bit_count()%2==0 for r in words)
        basis.append(x)
    return len(pivots),basis


def source_sat_count(rows):
    n=len(rows)
    rank,basis=high_pivot_kernel(rows)
    d=len(basis)
    assert d<=12,("UNKNOWN_RESOURCE_LIMIT",d)
    full=(1<<n)-1
    count=0
    for mask in range(1<<d):
        v=0
        for i,b in enumerate(basis):
            if (mask>>i)&1:v^=b
        x=full^v
        if all(sum((x>>j)&1 for j in row)==1 for row in rows):
            count+=1
    return rank,d,1<<d,count


def rebuild(parent,voltage):
    n=len(parent)
    edges=[(i,j) for i,row in enumerate(parent) for j in row]
    assert len(edges)==3*n and voltage>>len(edges)==0
    lookup={edge:(voltage>>i)&1 for i,edge in enumerate(edges)}
    result=[]
    for layer in (0,1):
        for i,row in enumerate(parent):
            result.append([j+n*(layer^lookup[(i,j)]) for j in row])
    return result,edges


def verify_hexagon_relation(parent,bitmasks,edge_order):
    assert len(bitmasks)==3
    fold=0
    for mask in bitmasks:
        assert mask.bit_count()==6
        fold^=mask
        deg=Counter()
        selected=[]
        for i,(row,col) in enumerate(edge_order):
            if (mask>>i)&1:
                selected.append((row,len(parent)+col))
                deg[row]+=1;deg[len(parent)+col]+=1
        assert len(selected)==6 and len(deg)==6
        assert all(v==2 for v in deg.values())
        adjacent={v:[] for v in deg}
        for a,b in selected:
            adjacent[a].append(b);adjacent[b].append(a)
        seen={next(iter(deg))};todo=list(seen)
        while todo:
            for v in adjacent[todo.pop()]:
                if v not in seen:seen.add(v);todo.append(v)
        assert len(seen)==6
    assert fold==0
    return {"three_simple_parent_hexagons":True,
            "odd_number_cycles":3,
            "XOR_masks_zero":True,
            "all_edge_voltage_assignments_girth8_or_more_impossible":True}


def run(frozen,parent_path):
    f=json.loads(Path(frozen).read_text())
    src=json.loads(Path(parent_path).read_text())
    assert f["version"]=="R5_E410_FROZEN_N90_UNSAT_MULTIZ_1"
    parent=src["base_45_rows"]
    assert len(parent)==45
    check_legal(parent)
    rows=f["source_n90_rows"]
    check_legal(rows)
    rebuilt,E=rebuild(parent,int(f["voltage_decimal"]))
    assert rebuilt==rows
    A=adjacency(rows)
    assert connected(A)
    assert girth(A)==6
    ob=f["hexagon_odd_parity_obstruction"]
    masks=[int(x) for x in ob["original_cycle_masks_decimal"]]
    relation=verify_hexagon_relation(parent,masks,E)
    rank,d,checked,sat=source_sat_count(rows)
    assert (rank,d,checked,sat)==(83,7,128,0)
    y_data=f["two_ternary_directions"]
    zs=set()
    for entry in y_data:
        z=int(entry["base_z_decimal"])
        assert z.bit_count()==26
        y=[((z>>j)&1)+2*int(j in (1,16))
           for j in range(len(parent))]
        assert all(sum(y[j] for j in row)==2 for row in parent)
        doubled=y+y
        assert all(sum(doubled[j] for j in row)==2 for row in rows)
        zz=sum(1<<j for j,v in enumerate(doubled) if v%2)
        assert str(zz)==entry["lifted_z_decimal"]
        zs.add(zz)
    assert len(zs)==2
    # The old 4-cross-edge 72/18 bottleneck is lifted
    # to 8 crossing incidences with side sizes144/36.
    # Source n90 has incidence vertices180 total.
    boundary=0
    for i,row in enumerate(rows):
        base_row=i%45
        for j in row:
            base_var=j%45
            if (base_row<36)!=(base_var<36):boundary+=1
    assert boundary==8
    return {
        "gate":"E4_10_CLEAN_ROOM_N90_UNSAT_MULTIZ_HEXAGON_OBSTRUCTION",
        "standard_library_only":True,
        "n":len(rows),"incidence_vertices":len(A),
        "is_legal_connected":True,"girth":girth(A),
        "base_to_two_cover_reconstruction_identical":True,
        "GF2_rank":rank,"GF2_nullity":d,
        "all_parity_words_checked":checked,"SAT_count":sat,
        "explicit_distinct_lifted_Y_z":sorted(str(z) for z in zs),
        "all_integer_ternary_row_sums_checked":True,
        "hexagon_proof":relation,
        "parent_cycle_masks_decimal":[str(x) for x in masks],
        "inherited_cross_cut_edges":boundary,
        "inherited_conductance_upper_bound":"2/27",
        "girth10_target":"IMPOSSIBLE_FOR_A_SINGLE_2LIFT_OF_THIS_PARENT",
        "universal_SCL_poly":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"}


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    p.add_argument("--parent",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.fixture,a.parent),sort_keys=True,indent=2))
