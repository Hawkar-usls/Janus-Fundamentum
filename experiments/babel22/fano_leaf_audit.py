#!/usr/bin/env python3
"""BABEL-22 independent all-n Fano-leaf falsifier control.

A connected SCL can have large GF(2) nullity and still be UNSAT for a
constant-size local reason. This experiment must not be counted as P=NP.
Standard library only, no imports from JANUS producer scripts.
"""
import json
from collections import Counter

def fano(t):
    return [tuple(sorted(7*b+j for j in (i,(i+1)%7,(i+3)%7)))
            for b in range(t) for i in range(7)]

def chain(t):
    """Attach neighboring Fano blocks by swapping exactly one row literal."""
    rows=[list(row) for row in fano(t)]
    for b in range(t-1):
        ra,rb=7*b,7*(b+1)+1
        a,c=7*b,7*(b+1)+4
        assert a in rows[ra] and c in rows[rb]
        rows[ra][rows[ra].index(a)]=c
        rows[rb][rows[rb].index(c)]=a
    return [tuple(sorted(row)) for row in rows]

def legal_connected(rows):
    n=len(rows)
    assert all(len(set(r))==3 and all(0<=j<n for j in r) for r in rows)
    degrees=Counter(j for r in rows for j in r)
    assert len(degrees)==n and set(degrees.values())=={3}
    pairs=[tuple(sorted((a,b))) for row in rows for a in row for b in row if a<b]
    assert len(set(pairs))==3*n
    adjacency=[set() for _ in range(n)]
    for row in rows:
        for a in row: adjacency[a].update(row)
    seen={0}; stack=[0]
    while stack:
        for v in adjacency[stack.pop()]-seen:
            seen.add(v);stack.append(v)
    assert len(seen)==n

def gf2_kernel(rows):
    n=len(rows)
    pivot={}
    for row in rows:
        x=sum(1<<j for j in row)
        while x:
            i=x.bit_length()-1
            if i in pivot: x^=pivot[i]
            else: pivot[i]=x;break
    basis=[]
    for j in range(n):
        if j in pivot: continue
        v=1<<j
        for p in sorted(pivot):
            if ((pivot[p]&v).bit_count()&1):v^=1<<p
        assert all(((v&sum(1<<i for i in row)).bit_count()&1)==0 for row in rows)
        basis.append(v)
    return basis

def codewords(basis):
    v=0
    for i in range(1<<len(basis)):
        if i: v^=basis[(i&-i).bit_length()-1]
        yield v

def defect(rows,v):
    return sum(all(not(v>>j&1) for j in row) for row in rows)

def prime_above(n):
    for p in range(n+1,3*n+20):
        if all(p%d for d in range(2,int(p**0.5)+1)):return p
    raise AssertionError("prime not found")

def exact_control(rows, full=True):
    legal_connected(rows)
    n=len(rows); basis=gf2_kernel(rows)
    p=prime_above(n)
    sat=0
    for v in codewords(basis):
        sat_here=(v.bit_count()*3==2*n)
        sat+=sat_here
        if full:
            d=defect(rows,v)
            assert 3*v.bit_count()==2*(n-d)
            assert sat_here==(d==0)
            assert pow(d,p-1,p)==int(d!=0)
            assert (d*pow(d,p-2,p))%p==int(d!=0)
    return {"n":n,"kernel_dim":len(basis),"parity_states":1<<len(basis),
            "sat_count":sat,"prime":p,"all_state_defect_replay":full}

def local_forcing():
    lines=fano(1)
    for omitted in range(7):
        survivors=[]
        for state in range(128):
            if all(sum(state>>j&1 for j in row)==1
                   for i,row in enumerate(lines) if i!=omitted):
                survivors.append(state)
        assert len(survivors)==1
        assert all((survivors[0]>>j)&1 for j in lines[omitted])
    return "7/7 exact 6-line Fano controls PASS"

def affine9():
    at=lambda x,y:3*x+y
    return [tuple(sorted(row)) for k in range(3) for row in (
        [at(k,y) for y in range(3)],
        [at(x,k) for x in range(3)],
        [at(x,y) for x in range(3) for y in range(3) if (x+y)%3==k]
    )]

def main():
    local=local_forcing()
    controls=[
        {"fixture":"FANO7","result":exact_control(fano(1))},
        {"fixture":"AFFINE9","result":exact_control(affine9())}
    ]
    for t in (3,6,9):
        controls.append({"fixture":f"CONNECTED_FANO_CHAIN_{7*t}",
                         "result":exact_control(chain(t),full=(t<=6))})
    assert [x["result"]["kernel_dim"] for x in controls[2:]]==[7,13,19]
    assert [x["result"]["sat_count"] for x in controls[2:]]==[0,0,0]
    assert controls[1]["result"]["sat_count"]==3
    result={
        "gate":"BABEL22_LOCAL_FANO_LEAF_FALSE_HARDNESS_FILTER",
        "local_lemma_exact_control":local,
        "all_n_proof":"Six untouched Fano lines force the missing line to 111; one external literal cannot repair the two remaining ones.",
        "controls":controls,
        "universal_degree2_completeness":"NOT_PROVED",
        "polynomial_zero_test":"NOT_PROVED",
        "P_vs_NP":"OPEN"
    }
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=="__main__":
    main()
