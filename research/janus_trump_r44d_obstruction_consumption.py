#!/usr/bin/env python3
import itertools, json
from janus_trump_r44_exact_representation_switchboard import dispatch, norm, clause_forbid_assignment


def complete_cube_unsat(cnf):
    cnf = norm(cnf)
    if not cnf:
        return None
    vs = sorted({abs(l) for c in cnf for l in c})
    k = len(vs)
    m = len(cnf)
    # Critical cost firewall: never enumerate 2^k unless the explicit input already has at least that many clauses.
    if k >= 63 or (1 << k) > m:
        return None
    if m != (1 << k):
        return None
    if any(len(c) != k or {abs(l) for l in c} != set(vs) for c in cnf):
        return None
    got = {tuple(c) for c in cnf}
    if len(got) != m:
        return None
    expected = {clause_forbid_assignment(tuple(vs), bits) for bits in itertools.product([False, True], repeat=k)}
    if got != expected:
        return None
    return {
        "decision": "UNSAT",
        "verified": True,
        "certificate": {
            "kind": "COMPLETE_ASSIGNMENT_BLOCKING_CUBE",
            "variables": vs,
            "assignment_count": 1 << k,
            "clause_count": m
        }
    }


def dispatch_r44d(cnf):
    route, res, ledger = dispatch(norm(cnf))
    if route is not None:
        return route, res, ledger
    r = complete_cube_unsat(cnf)
    if r is not None:
        ledger = dict(ledger)
        ledger["route_checks"] += 1
        ledger["complete_cube_explicit_patterns"] = len(cnf)
        return "COMPLETE_ASSIGNMENT_BLOCKING_CUBE_UNSAT_V1", r, ledger
    return None, {"status":"OPEN_OUTSIDE_SWITCHBOARD","decision_authority":False}, ledger


def cube(k):
    vs = tuple(range(1,k+1))
    return [list(clause_forbid_assignment(vs,b)) for b in itertools.product([False,True],repeat=k)]

# Consume the exact R44C witness, and also verify that the rule is a family rather than a one-off 3-variable patch.
consumed=[]
for k in (1,2,3,4):
    cnf=cube(k)
    route,res,ledger=dispatch_r44d(cnf)
    assert res["decision"] == "UNSAT"
    assert res["verified"] is True
    consumed.append({"k":k,"clauses":len(cnf),"route":route,"decision":res["decision"],"ledger":ledger})

# Fresh residual: a small mixed-sign 3-CNF chosen outside the explicit complete cube. It is only a search seed;
# its role is to prove the enlarged finite switchboard still has an OPEN frontier, not to make a complexity claim.
fresh = [
    [1,2,3], [1,-2,-3], [-1,2,-3], [-1,-2,3],
    [1,2,-4], [-1,3,4], [2,-3,4], [-2,3,-4],
    [1,-3,4], [-1,-2,-4]
]
route,res,ledger=dispatch_r44d(fresh)

print(json.dumps({
    "gate_id":"R44D_OBSTRUCTION_CONSUMPTION_AND_FRESH_RESIDUAL_SEARCH",
    "consumed_family":consumed,
    "r44c_obstruction_consumed": any(x["k"]==3 and x["decision"]=="UNSAT" for x in consumed),
    "fresh_probe":{"cnf":fresh,"route":route,"status":"CERTIFIED_ROUTE" if route else "OPEN_OUTSIDE_SWITCHBOARD","ledger":ledger},
    "universal_totality_proved":False,
    "U1":"OPEN",
    "P_VS_NP":"OPEN",
    "next_gate":"R44E_FRESH_RESIDUAL_MINIMIZATION_AND_MACHINE_INVARIANT_MINING"
}, sort_keys=True))
