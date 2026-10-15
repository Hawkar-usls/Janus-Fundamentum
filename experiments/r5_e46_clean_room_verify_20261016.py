#!/usr/bin/env python3
"""E4.6 CLEAN_ROOM_VERIFY: import-free independent GF(2), 2-lift and cycle replay.

Usage: python3 this_script.py --fixture frozen_fixture.json
It imports ONLY Python's standard library. Input is a declarative
frozen instance, not Python modules or a source-reconstruction script.

Independently validates:
* legal cubic linear base SCL, rank30/nullity6 and full base UNSAT;
* own RREF left/right kernel, Phi rank26 and 71-dimensional gauge;
* 11 quotient generators genuinely span kerPhi modulo gauge;
* same 6x6 obstruction H of rank5 and 1-dimensional kerH;
* physical z_star of weight20 and residual Y_z=1 by pairs of columns;
* G_z has 20 nodes,30 edges,11 cycles; Psi rank5;
* 2^11 predicted SAT voltage codes (64) vs GF2 EXACT 128-word
  integer Exact-One oracle for EVERY lift (0 disagreements);
* all SAT lifts have exactly2 witnesses, UNSAT lifts exactly0.

Independent algorithmic implementation: LOW-pivot RREF, not JANUS
high-pivot GF2 routines. Full 2048*128 enumeration is a finite
proof check, not general polynomial-time SAT solving.
"""
import argparse
import json
from collections import Counter, deque
from itertools import combinations
from pathlib import Path


def parity(x):
    return x.bit_count()&1


def rref(raw,width):
    """Reduced row echelon over GF2, earliest (LOW) pivot columns."""
    rows=[int(v) for v in raw]
    p=[]
    lead=0
    for j in range(width):
        pivot=next((i for i in range(lead,len(rows))
                    if ((rows[i]>>j)&1)),None)
        if pivot is None:
            continue
        rows[lead],rows[pivot]=rows[pivot],rows[lead]
        for k in range(len(rows)):
            if k!=lead and ((rows[k]>>j)&1):
                rows[k]^=rows[lead]
        p.append(j)
        lead+=1
        if lead==len(rows):
            break
    assert not any(rows[i] for i in range(lead,len(rows)))
    return tuple(rows[:lead]),tuple(p)


def rank(rows,width):
    return len(rref(rows,width)[1])


def kernel(rows,width):
    reduced,pivots=rref(rows,width)
    free=sorted(set(range(width))-set(pivots))
    ans=[]
    for j in free:
        v=1<<j
        for equation,pivot in zip(reduced,pivots):
            if (equation>>j)&1:
                v|=1<<pivot
        assert all(not parity(v&row) for row in rows)
        ans.append(v)
    return tuple(ans)


def source(rows):
    n=len(rows)
    assert n%3==0
    assert all(len(row)==3 and len(set(row))==3
               and all(0<=j<n for j in row) for row in rows)
    occur=[0]*n
    pairs=set()
    for row in rows:
        for j in row:occur[j]+=1
        for a,b in combinations(sorted(row),2):
            assert (a,b) not in pairs
            pairs.add((a,b))
    assert all(v==3 for v in occur)
    return tuple(sum(1<<j for j in row) for row in rows)


def edges_of(rows):
    return tuple((i,j) for i,row in enumerate(rows) for j in row)


def left_kernel(bitrows,n):
    columns=[sum(1<<i for i,row in enumerate(bitrows)
                 if (row>>j)&1) for j in range(n)]
    return kernel(columns,n)


def phi_images(right,left,edges):
    d=len(right)
    images=[]
    for i,j in edges:
        matrix=0
        for a,l in enumerate(left):
            if (l>>i)&1:
                for b,k in enumerate(right):
                    if (k>>j)&1: matrix^=1<<(a*d+b)
        images.append(matrix)
    return tuple(images)


def image_of(mask,images):
    total=0
    while mask:
        single=mask&-mask
        total^=images[single.bit_length()-1]
        mask^=single
    return total


def matrix_rank_from_phi(image,d):
    return rank([(image>>(i*d))&((1<<d)-1)
                 for i in range(d)],d)


def build_2lift(rows,voltage,edges):
    n=len(rows)
    bits={(i,j):(voltage>>q)&1
          for q,(i,j) in enumerate(edges)}
    lifted=[]
    for layer in (0,1):
        for i,row in enumerate(rows):
            lifted.append(tuple(
                j+n*(layer ^ bits[(i,j)]) for j in row))
    source(lifted)
    return tuple(lifted)


def affine_exact_oracle(rows,limit=1<<8):
    """Complete exact SAT count via low-pivot binary kernel enumeration."""
    n=len(rows)
    bitrows=source(rows)
    null=kernel(bitrows,n)
    if len(null)>8 or (1<<len(null))>limit:
        return {"verdict":"UNKNOWN_RESOURCE_LIMIT","d":len(null)}
    full=(1<<n)-1
    count=0
    tested=0
    for word in range(1<<len(null)):
        v=0
        for j,b in enumerate(null):
            if (word>>j)&1:v^=b
        x=full^v
        assert all(parity(x&row)==1 for row in bitrows)
        if all(sum((x>>j)&1 for j in row)==1 for row in rows):
            count+=1
        tested+=1
    return {"verdict":"EXACT","d":len(null),
            "count":count,"words_checked":tested}


def residual_count_by_pairs(rows,z):
    n=len(rows)
    S={j for j in range(n) if (z>>j)&1}
    r0=tuple(i for i,row in enumerate(rows)
             if not any(j in S for j in row))
    r2=tuple(i for i,row in enumerate(rows)
             if sum(j in S for j in row)==2)
    assert len(r0)+len(r2)==n
    assert len(r2)*2==3*len(S)
    clean=[]
    for j in range(n):
        if j in S:continue
        containing={i for i,row in enumerate(rows) if j in row}
        if containing.issubset(set(r0)):clean.append(j)
    assert len(r0)==6 and len(S)==20
    solutions=[]
    for a,b in combinations(clean,2):
        y=[int(j in S)+2*int(j in (a,b)) for j in range(n)]
        if all(sum(y[j] for j in row)==2 for row in rows):
            solutions.append(((a,b),y))
    return {"r0":r0,"r2":r2,"clean":clean,
            "solutions":solutions}


def cycle_constraints(rows,z,edges,voltage,generators):
    n=len(rows)
    lookup={(i,j):k for k,(i,j) in enumerate(edges)}
    S=[j for j in range(n) if (z>>j)&1]
    g={j:[] for j in S}
    links=[]
    for i,row in enumerate(rows):
        both=[j for j in row if (z>>j)&1]
        assert len(both) in (0,2)
        if not both:continue
        a,b=both
        mask=(1<<lookup[(i,a)])|(1<<lookup[(i,b)])
        idx=len(links)
        links.append((a,b,i,mask))
        g[a].append((b,idx));g[b].append((a,idx))
    assert len(S)==20 and len(links)==30
    assert all(len(g[j])==3 for j in S)
    parents={}
    parentedge={}
    depth={}
    spanning=set()
    components=0
    for root in S:
        if root in parents:continue
        components+=1
        parents[root]=None
        depth[root]=0
        q=deque([root])
        while q:
            u=q.popleft()
            for v,e in g[u]:
                if v in parents:continue
                parents[v]=u
                parentedge[v]=e
                depth[v]=depth[u]+1
                spanning.add(e)
                q.append(v)
    def tree_path(a,b):
        path=[]
        while depth[a]>depth[b]:
            path.append(parentedge[a]);a=parents[a]
        while depth[b]>depth[a]:
            path.append(parentedge[b]);b=parents[b]
        while a!=b:
            path += [parentedge[a],parentedge[b]]
            a=parents[a];b=parents[b]
        return path
    cycle_rows=[]
    constants=[]
    for e,(a,b,i,mask) in enumerate(links):
        if e in spanning:continue
        cyc=[e]+tree_path(a,b)
        q=0
        for j in cyc:q^=links[j][3]
        constant=(len(cyc)&1)^parity(q&voltage)
        cycle_rows.append(sum(1<<k for k,delta in enumerate(generators)
                              if parity(delta&q)))
        constants.append(constant)
    assert components==1 and len(cycle_rows)==11
    assert all(c==0 for c in constants)  # original SAT sign
    return {"components":components,"nodes":len(S),"links":len(links),
            "cycles":len(cycle_rows),"psi":cycle_rows,
            "constants":constants,
            "rank":rank(cycle_rows,len(generators))}


def run(path):
    data=json.loads(Path(path).read_text())
    assert data["version"]=="R5_E46_FROZEN_CLEAN_ROOM_1"
    rows=tuple(tuple(x) for x in data["base_rows"])
    bitrows=source(rows)
    n=len(rows)
    assert n==36
    rights=kernel(bitrows,n)
    lefts=left_kernel(bitrows,n)
    assert len(rights)==len(lefts)==6
    assert rank(bitrows,n)==30
    oracle_source=affine_exact_oracle(rows)
    assert oracle_source=={"verdict":"EXACT","d":6,
                           "count":0,"words_checked":64}
    edges=edges_of(rows)
    assert len(edges)==3*n
    voltage=int(data["sat_voltage_bits_decimal"])
    generators=tuple(int(q) for q in data["quotient_generator_bits_decimal"])
    assert len(generators)==11
    images=phi_images(rights,lefts,edges)
    assert rank(images,36)==26
    gauge=[]
    for i in range(n):
        gauge.append(sum(1<<k for k,(row,j) in enumerate(edges) if row==i))
    for j in range(n):
        gauge.append(sum(1<<k for k,(row,v) in enumerate(edges) if v==j))
    assert rank(gauge,len(edges))==71
    assert all(image_of(x,images)==0 for x in gauge)
    assert all(image_of(x,images)==0 for x in generators)
    assert rank(gauge+list(generators),len(edges))==82
    assert 108-26==82
    H=image_of(voltage,images)
    assert matrix_rank_from_phi(H,6)==5
    hrows=[(H>>(i*6))&63 for i in range(6)]
    hnull=kernel(hrows,6)
    assert len(hnull)==1
    z=0
    for j,b in enumerate(rights):
        if (hnull[0]>>j)&1:z^=b
    assert z==int(data["z_star_bits_decimal"])
    assert z.bit_count()==20
    remainder=residual_count_by_pairs(rows,z)
    assert len(remainder["solutions"])==1
    ((two_columns,y),)=remainder["solutions"]
    assert y==data["ternary_y"]
    cycle=cycle_constraints(rows,z,edges,voltage,generators)
    assert cycle["rank"]==5
    assert 1<<(11-cycle["rank"])==64
    original_cover=build_2lift(rows,voltage,edges)
    original_exact=affine_exact_oracle(original_cover)
    assert original_exact["count"]==2
    witness=int(data["sat_witness_decimal"])
    assert all(sum((witness>>j)&1 for j in row)==1
               for row in original_cover)
    result=Counter()
    disagreements=0
    histogram=Counter()
    for orbit in range(1<<11):
        delta=0
        for j,g in enumerate(generators):
            if (orbit>>j)&1: delta^=g
        predicted=all(parity(row&orbit)==c
                      for row,c in zip(cycle["psi"],cycle["constants"]))
        lifted=build_2lift(rows,voltage^delta,edges)
        oracle=affine_exact_oracle(lifted)
        assert oracle["verdict"]=="EXACT"
        assert oracle["d"]==7 and oracle["words_checked"]==128
        if (oracle["count"]>0)!=predicted:disagreements+=1
        result["SAT" if oracle["count"] else "UNSAT"]+=1
        histogram[str(oracle["count"])]+=1
    assert disagreements==0
    assert result==Counter({"SAT":64,"UNSAT":1984})
    assert histogram==Counter({"2":64,"0":1984})
    return {
        "gate":"E4_6_CLEAN_ROOM_VERIFY",
        "standard_library_only":True,
        "source_rows":n,"base_rank":30,"base_GF2_UNSAT_words":64,
        "left_right_nullity":6,"Phi_rank":26,
        "gauge_rank":71,"nongauge_dim":11,
        "rank_H":5,"z_weight":z.bit_count(),
        "residual_R0_rows":list(remainder["r0"]),
        "residual_clean_columns":list(remainder["clean"]),
        "residual_selected_two_columns":list(two_columns),
        "direct_residual_Y_z_count":len(remainder["solutions"]),
        "G_z_components":cycle["components"],
        "G_z_nodes":cycle["nodes"],
        "G_z_edges":cycle["links"],
        "G_z_fundamental_cycles":cycle["cycles"],
        "Psi_rank":cycle["rank"],
        "predicted_SAT_classes":64,
        "actual_class_counts":dict(result),
        "exact_sat_counts_distribution":dict(histogram),
        "independent_oracle_disagreements":disagreements,
        "all_2048_cases_replayed":True,
        "all_n_polynomial_SCL":"NOT_CONSTRUCTED",
        "P_vs_NP":"OPEN"
    }


if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--fixture",required=True)
    args=p.parse_args()
    print(json.dumps(run(args.fixture),sort_keys=True,indent=2))
