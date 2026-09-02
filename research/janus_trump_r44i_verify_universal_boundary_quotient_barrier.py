#!/usr/bin/env python3
import itertools, json


def assignments(w):
    return [tuple(bits) for bits in itertools.product([False, True], repeat=w)]


def distinguisher(a, b):
    for i,(x,y) in enumerate(zip(a,b)):
        if x != y:
            # continuation literal requires xi == a[i]
            return {"var_index": i, "required_value": x}
    raise AssertionError("assignments identical")


def compatible(a, continuation):
    return a[continuation["var_index"]] == continuation["required_value"]


checks=[]
for w in range(1,11):
    A=assignments(w)
    pair_count=0
    for i in range(len(A)):
        for j in range(i+1,len(A)):
            a,b=A[i],A[j]
            c=distinguisher(a,b)
            assert compatible(a,c) is True
            assert compatible(b,c) is False
            pair_count += 1
    checks.append({
        "w":w,
        "assignments":len(A),
        "expected_equivalence_classes":2**w,
        "distinguished_pairs":pair_count
    })

print(json.dumps({
    "gate_id":"R44I_UNIVERSAL_BOUNDARY_QUOTIENT_BARRIER",
    "status":"PAIRWISE_DISTINGUISHABILITY_REPLAYED",
    "checks":checks,
    "theorem":"For exact context-independent semantics against arbitrary future continuations over a width-w Boolean boundary, every distinct pair of assignments is distinguishable by a continuation fixing one differing boundary variable. Hence all 2^w assignments lie in distinct semantic classes.",
    "generic_context_independent_state_bound":"2^w",
    "universal_assignment_quotient_polynomially_compressed":False,
    "structured_or_representation_specific_compression_still_open":True,
    "U1":"OPEN",
    "P_EQUALS_NP":"NOT_PROVED",
    "P_NE_NP":"NOT_PROVED",
    "P_VS_NP":"OPEN",
    "next_gate":"R44J_STRUCTURE_CONDITIONED_FRONTIER_COMPRESSION_OR_REPRESENTATION_SWITCH"
}, sort_keys=True))
