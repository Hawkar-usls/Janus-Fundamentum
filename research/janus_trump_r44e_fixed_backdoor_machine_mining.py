#!/usr/bin/env python3
import itertools, json
from janus_trump_r44_exact_representation_switchboard import dispatch, norm
from janus_trump_r44d_obstruction_consumption import dispatch_r44d

FRESH = [
    [1,2,3], [1,-2,-3], [-1,2,-3], [-1,-2,3],
    [1,2,-4], [-1,3,4], [2,-3,4], [-2,3,-4],
    [1,-3,4], [-1,-2,-4]
]


def simplify(cnf, assignment):
    out=[]
    for c in cnf:
        satisfied=False
        nc=[]
        for l in c:
            v=abs(l)
            if v in assignment:
                if assignment[v] == (l>0):
                    satisfied=True
                    break
            else:
                nc.append(l)
        if satisfied:
            continue
        if not nc:
            return [[]]
        out.append(nc)
    return out


def vars_of(cnf):
    return sorted({abs(l) for c in cnf for l in c})


def certified_terminal(cnf):
    if cnf == [[]]:
        return {"route":"EMPTY_CLAUSE","decision":"UNSAT","verified":True}
    if not cnf:
        return {"route":"EMPTY_FORMULA","decision":"SAT","verified":True,"witness":{}}
    route,res,ledger=dispatch_r44d(norm(cnf))
    if route is None:
        return None
    if res.get("verified") is not True:
        return None
    return {"route":route,"decision":res.get("decision"),"verified":True,"ledger":ledger}


def find_strong_backdoor(cnf, kmax=2):
    vs=vars_of(cnf)
    for k in range(1, min(kmax,len(vs))+1):
        for B in itertools.combinations(vs,k):
            branches=[]
            ok=True
            for bits in itertools.product([False,True], repeat=k):
                a=dict(zip(B,bits))
                rcnf=simplify(cnf,a)
                cert=certified_terminal(rcnf)
                if cert is None:
                    ok=False
                    break
                branches.append({"assignment":{str(v):a[v] for v in B},"residual":rcnf,"terminal":cert})
            if ok:
                return {"backdoor":list(B),"k":k,"branches":branches}
    return None


def exact_decision_from_backdoor(cnf, cert):
    sat_branches=[b for b in cert["branches"] if b["terminal"]["decision"]=="SAT"]
    if sat_branches:
        # This gate establishes exact decision composition; full original-input witness lifting is left explicit for U6.
        return {"decision":"SAT","composition_verified":True,"sat_branch_count":len(sat_branches)}
    return {"decision":"UNSAT","composition_verified":True,"unsat_branch_count":len(cert["branches"])}

backdoor=find_strong_backdoor(FRESH,2)
result={
    "gate_id":"R44E_FIXED_BACKDOOR_MACHINE_MINING",
    "fresh_input":FRESH,
    "fixed_k_max":2,
    "machine_found":backdoor is not None,
    "certificate":backdoor,
    "U1":"OPEN",
    "P_VS_NP":"OPEN"
}
if backdoor is not None:
    result["exact_composed_decision"]=exact_decision_from_backdoor(FRESH,backdoor)
    result["interpretation"]="The R44D residual is not a durable obstruction: a fixed-size strong backdoor exposes frozen tractable structure on every branch. This is a polynomial exact family mechanism for fixed k, not universal coverage."
    result["next_gate"]="R44F_SCALABLE_RESIDUAL_FAMILY_OUTSIDE_FIXED_BACKDOOR_RADIUS"
else:
    result["interpretation"]="The frozen k<=2 backdoor machine does not consume this residual; preserve as candidate obstruction to this route."
    result["next_gate"]="R44F_MINIMIZE_AND_SCALE_THIS_BACKDOOR_OBSTRUCTION"
print(json.dumps(result, sort_keys=True))
