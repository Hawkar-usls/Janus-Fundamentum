#!/usr/bin/env python3
"""BABEL41 independent exhaustive UNSAT DAG verifier over ORIGINAL rows.

This checker does NOT call producer search, unit closure or branch heuristic.
Each UNSAT branch must include EVERY legal choice in some unsatisfied row,
and every leaf must have an independently verified local contradiction.
SAT is certified by direct ORIGINAL row replay, irrespective of discovery.
Time O(poly(n) * proof_size), which can be EXPONENTIAL IN ORIGINAL n.
"""
import hashlib
import json
from collections import Counter


def independently_validate(rows):
    n=len(rows)
    assert n>0
    assert all(len(r)==3 and len(set(r))==3
               and all(isinstance(v,int) and 0<=v<n for v in r)
               for r in rows)
    assert Counter(v for r in rows for v in r)==Counter({j:3 for j in range(n)})
    paircount=Counter(tuple(sorted((a,b)))
                      for r in rows for a in r for b in r if a<b)
    assert len(paircount)==3*n
    assert max(paircount.values())==1
    return tuple(tuple(r) for r in rows)


def digest(rows):
    return hashlib.sha256(json.dumps(
        [list(r) for r in rows],separators=(",",":")).encode()).hexdigest()


def examine(rows,initial_true):
    """Independent row-set fixed-point evaluation; no bitset producer use."""
    n=len(rows)
    t={v for v in range(n) if (initial_true>>v)&1}
    while True:
        forbidden=set()
        open_rows=[]
        for i,row in enumerate(rows):
            hits=t.intersection(row)
            if len(hits)>1:
                return "CONFLICT",t,[],{}
            if len(hits)==1:
                forbidden.update(set(row)-hits)
        if t&forbidden:
            return "CONFLICT",t,[],{}
        forced=set()
        for i,row in enumerate(rows):
            if t.intersection(row):continue
            options=[v for v in row if v not in forbidden]
            if not options:
                return "CONFLICT",t,[],{}
            if len(options)==1:
                forced.add(options[0])
            else:
                open_rows.append((i,tuple(sorted(options))))
        if forced-t:
            t|=forced
            continue
        if not open_rows:
            assert all(sum(v in t for v in row)==1 for row in rows)
            return "SAT",t,[],{}
        return "OPEN",t,open_rows,{i:choices for i,choices in open_rows}


def _key(mask,n):
    assert isinstance(mask,int) and 0<=mask<(1<<n)
    return format(mask,"x")


def validate_result(rows,result):
    rows=independently_validate(rows)
    n=len(rows)
    assert result["n"]==n
    if result["status"]=="SAT":
        truth=result["witness"]
        assert isinstance(truth,int) and 0<=truth<(1<<n)
        assert truth.bit_count()==n//3
        assert n%3==0
        assert all(sum((truth>>v)&1 for v in row)==1 for row in rows)
        assert result.get("rows_sha256")==digest(rows)
        return {"status":"SAT_CERTIFIED","physical_rows_verified":n}
    assert result["status"]=="UNSAT"
    proof=result["certificate"]
    assert proof["format"]=="BABEL41/EXACT-UNSAT-DAG/v1"
    assert proof["n"]==n and proof["rows_sha256"]==digest(rows)
    if proof["type"]=="DIVISIBILITY":
        assert n%3!=0
        return {"status":"UNSAT_CERTIFIED_DIVISIBILITY","original_rows":n}

    assert proof["type"]=="COMPLETE_EXACT_ONE_REFUTATION"
    assert n%3==0 and proof["root"]=="0"
    nodes=proof["nodes"]
    assert isinstance(nodes,dict) and "0" in nodes
    visited=set()
    stack=set()
    conflicts=[0]
    branches=[0]
    def verify_node(key):
        assert isinstance(key,str)
        before=int(key,16)
        assert _key(before,n)==key
        if key in visited:return
        assert key not in stack,"invalid cyclic refutation"
        assert key in nodes,"missing branch of claimed UNSAT decision tree"
        stack.add(key)
        kind,true,open_rows,available=examine(rows,before)
        node=nodes[key]
        if kind=="CONFLICT":
            assert node=={"type":"CONFLICT"},(key,kind,node)
            conflicts[0]+=1
        else:
            assert kind=="OPEN",("SAT point was omitted from claimed UNSAT DAG",key)
            assert node["type"]=="BRANCH"
            row=node["row"]
            assert isinstance(row,int) and row in available
            candidates=available[row]
            assert 2<=len(candidates)<=3
            true_mask=sum(1<<v for v in true)
            expected=[_key(true_mask|(1<<v),n) for v in candidates]
            assert node["children"]==expected,(row,candidates,node["children"],expected)
            branches[0]+=1
            for child in expected:
                verify_node(child)
        stack.remove(key)
        visited.add(key)
    verify_node("0")
    assert visited==set(nodes),"extraneous or unreachable unsound proof entries"
    return {"status":"UNSAT_CERTIFIED_EXHAUSTIVE_BRANCH_DAG",
            "physical_rows":n,
            "complete_verified_states":len(visited),
            "branch_states":branches[0],
            "contradiction_states":conflicts[0]}


def main():
    print("BABEL41 independent verifier: validate_result(original_rows,result)")
    print("UNSAT DAG verification polynomial in certificate size, not necessarily input size.")


if __name__=="__main__":
    main()
