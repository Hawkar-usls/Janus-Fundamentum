#!/usr/bin/env python3
"""Exact-One residual forest dynamic program with checkable local messages.

Works after the existing proven polynomial parity preprocessor. If the
variable/clause incidence graph has a cycle, returns OPEN_CYCLIC without
claiming a universal solution. No Rowan calls, no model-score assumptions.
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
from pathlib import Path

from exactone_parity_preprocessor import (
    preprocess, verify as verify_preprocess, validate, digest,
    solution_set,
)

SCHEMA = "janus.fundamentum.exactone_forest_certificate.v1"


def incidence(case):
    """Simple bipartite graph, preserving repeated literals inside factors."""
    n, clauses = validate(case)
    adj = {f"v:{i}": [] for i in range(1, n+1)}
    for ci, clause in enumerate(clauses):
        fac = f"c:{ci}"
        adj[fac] = []
        for var in sorted({abs(l) for l in clause}):
            key = f"v:{var}"
            adj[fac].append(key)
            adj[key].append(fac)
    parent, order, roots = {}, [], []
    cyclic = False
    for node in adj:
        if node in parent:
            continue
        parent[node] = None
        roots.append(node)
        stack = [node]
        while stack:
            u = stack.pop()
            order.append(u)
            for v in adj[u]:
                if v == parent[u]:
                    continue
                if v in parent:
                    cyclic = True
                else:
                    parent[v] = u
                    stack.append(v)
    return adj, parent, order, roots, cyclic


def truth(lit, values):
    bit = values[abs(lit)]
    return bit ^ int(lit < 0)


def factor_ok(clause, values):
    return sum(truth(lit, values) for lit in clause) == 1


def upward(case, adj, parent, order):
    """2-state messages and deterministic small-factor witness backpointers."""
    messages, choices = {}, {}
    for node in reversed(order):
        if node.startswith("v:"):
            possibilities = []
            for bit in (0, 1):
                possibilities.append(all(messages[child][bit]
                                         for child in adj[node] if parent[child] == node))
            messages[node] = possibilities
        else:
            ci = int(node.split(":")[1])
            parent_var = parent[node]
            if parent_var is None or not parent_var.startswith("v:"):
                raise ValueError("CLAUSE_ROOT_NOT_SUPPORTED")
            pvar = int(parent_var.split(":")[1])
            children = [int(v.split(":")[1]) for v in adj[node] if parent[v] == node]
            allowed = [False, False]
            for pval in (0, 1):
                for values in itertools.product((0, 1), repeat=len(children)):
                    assign = {pvar:pval, **dict(zip(children, values))}
                    if not factor_ok(case["clauses"][ci], assign):
                        continue
                    if all(messages[f"v:{v}"][assign[v]] for v in children):
                        allowed[pval] = True
                        choices[(node, pval)] = dict(zip(children, values))
                        break
            messages[node] = allowed
    return messages, choices


def lift(case, adj, parent, order, roots, messages, choices):
    assigned = {}
    for root in roots:
        if not root.startswith("v:"):
            raise ValueError("UNEXPECTED_CLAUSE_ROOT")
        options = messages[root]
        if not any(options):
            return None
        assigned[int(root.split(":")[1])] = 0 if options[0] else 1
    for node in order:
        if not node.startswith("c:"):
            continue
        parent_var = parent[node]
        if parent_var is None:
            raise ValueError("CLAUSE_WITHOUT_PARENT")
        pval = assigned[int(parent_var.split(":")[1])]
        selected = choices.get((node, pval))
        if selected is None:
            raise AssertionError("MISSING_FACTOR_WITNESS")
        for var, bit in selected.items():
            if var in assigned:
                raise AssertionError("TREE_RECONSTRUCTION_COLLISION")
            assigned[var] = bit
    if len(assigned) != case["n"]:
        raise AssertionError("RECONSTRUCTION_INCOMPLETE")
    if not all(factor_ok(c, assigned) for c in case["clauses"]):
        raise AssertionError("RECONSTRUCTED_WITNESS_INVALID")
    return assigned


def run(case):
    validate(case)
    prep = preprocess(case)
    if not verify_preprocess(case, prep):
        raise AssertionError("PREPROCESS_CERT_INVALID")
    output = {
        "schema": SCHEMA,
        "source_sha256": digest(case),
        "preprocessor": prep,
        "status": None,
        "residual_is_incidence_forest": None,
        "forest_dp_messages": None,
        "witness": None,
        "p_vs_np": "OPEN",
        "general_polynomial_sat_solver_claimed": False,
        "provider_calls": 0,
    }
    if prep["status"] == "UNSAT":
        output.update(status="UNSAT_PREPROCESS",residual_is_incidence_forest=None)
    elif prep["status"] == "SAT":
        output.update(status="SAT_PREPROCESS",residual_is_incidence_forest=None,
                      witness={str(k): v for k,v in sorted(
                          {**{v:0 for v in range(1,case["n"]+1)},
                           **{int(k):bit for k,bit in prep["assignments"].items()}}.items())})
    else:
        # Reduce to active variables; solved prep assignments do not need to
        # appear in the residual factor graph.
        residual = prep["residual_clauses"]
        active = sorted({abs(l) for c in residual for l in c})
        compressed = {v:i+1 for i,v in enumerate(active)}
        inverse = {i+1:v for i,v in enumerate(active)}
        small = {"n":max(1,len(active)), "clauses":[[
            (1 if lit>0 else -1)*compressed[abs(lit)] for lit in c]
            for c in residual]}
        adj,parent,order,roots,cyclic = incidence(small)
        if cyclic:
            output.update(status="OPEN_CYCLIC",residual_is_incidence_forest=False)
        else:
            messages,choices = upward(small,adj,parent,order)
            compact_messages = {node:values for node,values in sorted(messages.items())}
            assign_small = lift(small,adj,parent,order,roots,messages,choices)
            if assign_small is None:
                output.update(status="UNSAT_FOREST",residual_is_incidence_forest=True,
                              forest_dp_messages=compact_messages)
            else:
                full={v:0 for v in range(1,case["n"]+1)}
                full.update({int(k):bit for k,bit in prep["assignments"].items()})
                full.update({inverse[i]:bit for i,bit in assign_small.items() if i in inverse})
                if not all(factor_ok(c,full) for c in case["clauses"]):
                    raise AssertionError("LIFT_TO_ORIGINAL_FAILED")
                output.update(status="SAT_FOREST",residual_is_incidence_forest=True,
                              forest_dp_messages=compact_messages,
                              witness={str(k):v for k,v in sorted(full.items())})
    output["result_sha256"] = digest(output)
    return output


def verify(case, answer):
    """Replay original preprocessor certificate, forest DP table and witness.

    For UNSAT_FOREST, a separate recurrence checks every stated subtree
    marginal; this is a polynomial UNSAT certificate, not a brute-force claim.
    """
    try:
        validate(case)
        if answer.get("schema")!=SCHEMA or answer.get("source_sha256")!=digest(case):
            return False
        tmp=dict(answer)
        h=tmp.pop("result_sha256",None)
        if h!=digest(tmp) or answer.get("p_vs_np")!="OPEN" or answer.get("provider_calls")!=0:
            return False
        if answer.get("general_polynomial_sat_solver_claimed") is not False:
            return False
        prep=answer["preprocessor"]
        if not verify_preprocess(case,prep):
            return False
        st=answer["status"]
        if prep["status"]=="UNSAT":
            return st=="UNSAT_PREPROCESS" and answer["witness"] is None
        if prep["status"]=="SAT":
            if st!="SAT_PREPROCESS":
                return False
            return _check_witness(case,answer["witness"])
        residual=prep["residual_clauses"]
        active=sorted({abs(l) for c in residual for l in c})
        compressed={v:i+1 for i,v in enumerate(active)}
        small={"n":max(1,len(active)), "clauses":[[
            (1 if l>0 else -1)*compressed[abs(l)] for l in c]
            for c in residual]}
        adj,parent,order,roots,cyclic=incidence(small)
        if cyclic:
            return (st=="OPEN_CYCLIC" and answer["residual_is_incidence_forest"] is False
                    and answer["witness"] is None and answer["forest_dp_messages"] is None)
        if answer["residual_is_incidence_forest"] is not True or st not in ("SAT_FOREST","UNSAT_FOREST"):
            return False
        data=answer["forest_dp_messages"]
        if not isinstance(data,dict) or set(data)!=set(adj):
            return False
        # Local certificate check. Do NOT call upward()/lift().
        for node in reversed(order):
            claimed=data[node]
            if not isinstance(claimed,list) or len(claimed)!=2 or any(type(x) is not bool for x in claimed):
                return False
            if node.startswith("v:"):
                for val in (0,1):
                    expected=all(data[c][val] for c in adj[node] if parent[c]==node)
                    if claimed[val] is not expected:
                        return False
            else:
                pi=parent[node]
                if pi is None:
                    return False
                pv=int(pi.split(":")[1])
                children=[int(v.split(":")[1]) for v in adj[node] if parent[v]==node]
                ci=int(node.split(":")[1])
                for val in (0,1):
                    possible=False
                    for opts in itertools.product((0,1),repeat=len(children)):
                        local={pv:val, **dict(zip(children,opts))}
                        if factor_ok(small["clauses"][ci],local) and all(
                                data[f"v:{v}"][local[v]] for v in children):
                            possible=True
                            break
                    if claimed[val] is not possible:
                        return False
        root_feasible=all(any(data[root]) for root in roots)
        if st=="UNSAT_FOREST":
            return not root_feasible and answer["witness"] is None
        return root_feasible and _check_witness(case,answer["witness"])
    except (KeyError,TypeError,ValueError,OverflowError,AssertionError):
        return False


def _check_witness(case, witness):
    if not isinstance(witness,dict) or set(witness)!={str(i) for i in range(1,case["n"]+1)}:
        return False
    if any(type(x) is not int or x not in (0,1) for x in witness.values()):
        return False
    a={int(k):v for k,v in witness.items()}
    return all(factor_ok(c,a) for c in case["clauses"])


def self_test():
    tests=[
        {"n":3,"clauses":[[1,2,3]]},
        {"n":5,"clauses":[[1,2,3],[3,4,5]]},
        {"n":5,"clauses":[[1,2,3],[1,4,5],[2]]},
        {"n":3,"clauses":[[1],[-1]]},
        {"n":4,"clauses":[[1,2,3],[2,3,4]]},
        {"n":5,"clauses":[[1,2,3],[2,3,4],[4,5,1]]},
    ]
    rng=random.Random(20261028)
    for i in range(270):
        blocks=1+i%4
        clauses=[]
        for j in range(blocks):
            a=1 if j==0 else rng.choice(list(range(1,2*j+2)))
            b,c=2*j+2,2*j+3
            cc=[a,b,c]
            clauses.append([lit if rng.randrange(2) else -lit for lit in cc])
        n=2*blocks+1
        for _ in range(i%3):
            v=rng.randrange(1,n+1)
            clauses.append([v if rng.randrange(2) else -v])
        tests.append({"n":n,"clauses":clauses})
    statuses={}
    for case in tests:
        r=run(case)
        assert verify(case,r),("INDEPENDENT_CERTIFICATE_FAIL",case,r)
        assert case["n"]<=18
        true_count=len(solution_set(case))
        if r["status"].startswith("SAT"):
            assert true_count>0
        elif r["status"].startswith("UNSAT"):
            assert true_count==0
        else:
            assert r["status"]=="OPEN_CYCLIC"
        statuses[r["status"]]=statuses.get(r["status"],0)+1
    # Small connected forest without unit propagation: reduces 5-variable
    # two-clause Exact-One tree completely by dynamic programming.
    simple=run({"n":5,"clauses":[[1,2,3],[3,4,5]]})
    assert simple["status"]=="SAT_FOREST"
    # Reject an invalid certificate even if attacker rehashes it.
    fake=json.loads(json.dumps(simple))
    first=next(iter(fake["forest_dp_messages"]))
    fake["forest_dp_messages"][first][0]=not fake["forest_dp_messages"][first][0]
    fake.pop("result_sha256")
    fake["result_sha256"]=digest(fake)
    assert not verify({"n":5,"clauses":[[1,2,3],[3,4,5]]},fake)
    return {
        "schema":"janus.fundamentum.exactone_forest_self_test.v1",
        "status":"PASS", "cases":len(tests), "result_counts":statuses,
        "tampered_message":"REJECTED",
        "forest_dp_complexity":"O(number_of_variables+clauses+literal_occurrences) for width <=3",
        "combined_preprocess_plus_forest_bound":"O(L^5) conservative",
        "universal_polynomial_exactone_solver":False,"p_vs_np":"OPEN",
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    group=p.add_mutually_exclusive_group(required=True)
    group.add_argument("--self-test",action="store_true")
    group.add_argument("--input",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=self_test() if a.self_test else run(json.loads(a.input.read_text(encoding="utf-8")))
    if not a.self_test and not verify(json.loads(a.input.read_text(encoding="utf-8")),result):
        raise RuntimeError("FOREST_CERTIFICATE_CHECK_FAILED")
    output=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if a.output:
        a.output.write_text(output,encoding="utf-8")
    print(output)


if __name__=="__main__":
    main()
