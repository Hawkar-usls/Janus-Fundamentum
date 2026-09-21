#!/usr/bin/env python3
"""C5B T0 semantic chord census checker.

Scope: the frozen one-anchor template
    B1-C1-B2-C2-X0-C3-B3
from the inverse-Golovach clause control.

The checker classifies all 15 nonconsecutive pairs by:
- source legality of inserting that chord alone;
- tracked semantic object changed.

It is intentionally not a solver and not a general source-template generator.
"""

from itertools import combinations

ROLES=("B1","C1","B2","C2","X0","C3","B3")
TYPE={
    "B1":"B","B2":"B","B3":"B",
    "C1":"C","C2":"C","C3":"C",
    "X0":"X0",
}

# Frozen concrete roles from C5A universal witness.
CONCRETE={
    "B1":"b1",
    "C1":"z2",
    "B2":"b2",
    "C2":"z3",
    "X0":"x0c4",
    "C3":"zp3",
    "B3":"bp2",
}

# Semantic state for frozen candidate.
# B exact lists before any optional chord.
A={
    "B1":frozenset({1,4}),
    "B2":frozenset({1,4}),
    "B3":frozenset({1,4}),
}
X0_COLOR={"X0":4}
BBASE={
    "C1":frozenset({1,3,4}), # z2
    "C2":frozenset({1,3}),   # z3
    "C3":frozenset({1,2}),   # zp3
}

# Dynamic complete-neighbor sets restricted to T0 B roles.
D={
    "C1":frozenset({"B1","B2"}), # z2 sees b1,b2 (+ x2 outside T0)
    "C2":frozenset({"B2"}),      # z3 sees b2 (+ x3 outside T0)
    "C3":frozenset({"B3"}),      # zp3 sees bp2 (+ x3 outside T0)
}

# For C-C source-legality test under axiom (iv):
# each listed dynamic witness is adjacent to exactly one endpoint.
MIXED_WITNESS={
    frozenset({"C1","C2"}):"B1",
    frozenset({"C1","C3"}):"B1",
    frozenset({"C2","C3"}):"B2",
}

def classify(a,b):
    ta,tb=TYPE[a],TYPE[b]
    pair=frozenset((ta,tb))

    if ta=="C" and tb=="C":
        w=MIXED_WITNESS[frozenset((a,b))]
        return {
            "source_status":"SOURCE_FORBIDDEN",
            "reason":f"Adding {a}-{b} creates a Y0 edge mixed on by {w}, violating source axiom (iv).",
            "tracked_delta":"COMPONENT_MERGING",
        }

    if pair==frozenset({"B"}):
        return {
            "source_status":"SOURCE_OPTIONAL",
            "reason":"No seeded-precoloring axiom forces or forbids this dynamic-dynamic edge in the frozen T0 state.",
            "tracked_delta":"HARD_CORE_CHANGING",
        }

    if pair==frozenset({"B","C"}):
        B=a if ta=="B" else b
        C=b if tb=="C" else a
        assert B not in D[C]
        return {
            "source_status":"SOURCE_OPTIONAL",
            "reason":"C is singleton residual Y0, so inserting the edge is source-legal in isolation.",
            "tracked_delta":"SELECTOR_NEIGHBORHOOD_CHANGING",
            "before_D_contains":False,
            "after_D_contains":True,
        }

    if pair==frozenset({"B","X0"}):
        B=a if ta=="B" else b
        c=4
        assert c in A[B], (B,A[B])
        return {
            "source_status":"SOURCE_OPTIONAL",
            "reason":"X0 may be adjacent to dynamic vertices; the fixed X0 coloring remains proper.",
            "tracked_delta":"LIST_CHANGING",
            "before_A":sorted(A[B]),
            "after_A":sorted(A[B]-{c}),
        }

    if pair==frozenset({"C","X0"}):
        C=a if ta=="C" else b
        c=4
        assert c in BBASE[C], (C,BBASE[C])
        return {
            "source_status":"SOURCE_OPTIONAL",
            "reason":"X0-Y0 adjacency is permitted by source axioms; X0 is excluded from axiom (iv)'s outside-vertex condition.",
            "tracked_delta":"COMPONENT_BASE_LIST_CHANGING",
            "before_base":sorted(BBASE[C]),
            "after_base":sorted(BBASE[C]-{c}),
        }

    raise AssertionError((a,b,ta,tb))

def main():
    rows=[]
    counts={}
    for i,j in combinations(range(7),2):
        if j==i+1:
            continue
        a,b=ROLES[i],ROLES[j]
        out=classify(a,b)
        row={"positions":[i,j],"roles":[a,b],"concrete":[CONCRETE[a],CONCRETE[b]],**out}
        rows.append(row)
        key=(out["source_status"],out["tracked_delta"])
        counts[key]=counts.get(key,0)+1

    assert len(rows)==15
    assert sum(1 for r in rows if r["source_status"]=="SOURCE_FORBIDDEN")==3
    assert sum(1 for r in rows if r["source_status"]=="SOURCE_OPTIONAL")==12
    assert sum(1 for r in rows if r["tracked_delta"]=="HARD_CORE_CHANGING")==3
    assert sum(1 for r in rows if r["tracked_delta"]=="SELECTOR_NEIGHBORHOOD_CHANGING")==5
    assert sum(1 for r in rows if r["tracked_delta"]=="LIST_CHANGING")==3
    assert sum(1 for r in rows if r["tracked_delta"]=="COMPONENT_BASE_LIST_CHANGING")==1
    assert sum(1 for r in rows if r["tracked_delta"]=="COMPONENT_MERGING")==3

    # No nonconsecutive X0-X0 pair exists because T0 has exactly one X0 role.
    assert not any(TYPE[r["roles"][0]]=="X0" and TYPE[r["roles"][1]]=="X0" for r in rows)

    print({
        "status":"PASS_T0_CENSUS",
        "template":"B-C-B-C-X0-C-B",
        "nonconsecutive_pairs":len(rows),
        "source_optional":12,
        "source_forbidden":3,
        "semantics_neutral":0,
        "delta_counts":{
            "HARD_CORE_CHANGING":3,
            "SELECTOR_NEIGHBORHOOD_CHANGING":5,
            "LIST_CHANGING":3,
            "COMPONENT_BASE_LIST_CHANGING":1,
            "COMPONENT_MERGING":3,
        },
        "rows":rows,
    })

if __name__=="__main__":
    main()
