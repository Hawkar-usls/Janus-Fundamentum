#!/usr/bin/env python3
import itertools, json


def norm(cnf):
    return [tuple(int(x) for x in c) for c in cnf]


def vars_of(cnf):
    return sorted({abs(x) for c in cnf for x in c})


def eval_clause(clause, a):
    return any(a[abs(l)] == (l > 0) for l in clause)


def verify_assignment(cnf, a):
    return all(eval_clause(c, a) for c in cnf)


def lit_index(lit, idx):
    base = 2 * idx[abs(lit)]
    return base if lit > 0 else base + 1


def neg_index(node):
    return node ^ 1


def two_sat(cnf):
    if not all(len(c) <= 2 for c in cnf):
        return None
    vs = vars_of(cnf)
    idx = {v:i for i,v in enumerate(vs)}
    n = 2 * len(vs)
    g = [[] for _ in range(n)]
    rg = [[] for _ in range(n)]

    def add_edge(u, v):
        g[u].append(v)
        rg[v].append(u)

    for c in cnf:
        if len(c) == 0:
            return {"decision":"UNSAT","certificate":{"kind":"EMPTY_CLAUSE"},"verified":True,"algorithm":"SCC_2SAT_V1"}
        if len(c) == 1:
            a = lit_index(c[0], idx)
            add_edge(neg_index(a), a)
        elif len(c) == 2:
            a = lit_index(c[0], idx)
            b = lit_index(c[1], idx)
            add_edge(neg_index(a), b)
            add_edge(neg_index(b), a)

    seen = [False] * n
    order = []
    for s in range(n):
        if seen[s]:
            continue
        stack = [(s, 0)]
        seen[s] = True
        while stack:
            u, i = stack[-1]
            if i < len(g[u]):
                v = g[u][i]
                stack[-1] = (u, i + 1)
                if not seen[v]:
                    seen[v] = True
                    stack.append((v, 0))
            else:
                order.append(u)
                stack.pop()

    comp = [-1] * n
    cid = 0
    for s in reversed(order):
        if comp[s] != -1:
            continue
        stack = [s]
        comp[s] = cid
        while stack:
            u = stack.pop()
            for v in rg[u]:
                if comp[v] == -1:
                    comp[v] = cid
                    stack.append(v)
        cid += 1

    conflicts = []
    for v in vs:
        p = lit_index(v, idx)
        q = neg_index(p)
        if comp[p] == comp[q]:
            conflicts.append(v)
    if conflicts:
        return {
            "decision":"UNSAT",
            "certificate":{"kind":"SCC_CONTRADICTION","variables":conflicts},
            "verified":True,
            "algorithm":"SCC_2SAT_V1",
            "complexity":"O(V+E) implication graph"
        }

    a = {}
    for v in vs:
        p = lit_index(v, idx)
        q = neg_index(p)
        a[v] = comp[p] > comp[q]
    assert verify_assignment(cnf, a)
    return {
        "decision":"SAT",
        "witness":a,
        "verified":True,
        "algorithm":"SCC_2SAT_V1",
        "complexity":"O(V+E) implication graph"
    }


def is_horn(cnf):
    return all(sum(1 for l in c if l > 0) <= 1 for c in cnf)


def horn_solve(cnf):
    if not is_horn(cnf):
        return None
    true = set()
    changed = True
    while changed:
        changed = False
        for c in cnf:
            pos = [l for l in c if l > 0]
            neg = [-l for l in c if l < 0]
            if all(v in true for v in neg):
                if not pos:
                    return {"decision":"UNSAT", "certificate":{"violated_negative_clause":list(c),"true_atoms":sorted(true)}, "verified":True}
                v = pos[0]
                if v not in true:
                    true.add(v); changed = True
    a = {v:(v in true) for v in vars_of(cnf)}
    assert verify_assignment(cnf, a)
    return {"decision":"SAT", "witness":a, "verified":True}


def dual_horn_solve(cnf):
    if not all(sum(1 for l in c if l < 0) <= 1 for c in cnf):
        return None
    transformed = [[-l for l in c] for c in cnf]
    r = horn_solve(transformed)
    if r is None: return None
    if r["decision"] == "SAT":
        a = {v:not val for v,val in r["witness"].items()}
        assert verify_assignment(cnf,a)
        return {"decision":"SAT","witness":a,"verified":True}
    return {"decision":"UNSAT","certificate":{"dual_of":r["certificate"]},"verified":True}


def renamable_horn_small(cnf):
    # Diagnostic recognition only, explicitly excluded from asymptotic algorithm authority.
    vs = vars_of(cnf)
    if len(vs) > 12:
        return None
    for bits in itertools.product([False,True], repeat=len(vs)):
        flip = dict(zip(vs,bits))
        t = [[(-l if flip[abs(l)] else l) for l in c] for c in cnf]
        if is_horn(t):
            return {"flip":flip, "transformed":t}
    return None


def clause_forbid_assignment(triple, assn):
    return tuple((-v if bit else v) for v,bit in zip(triple,assn))


def xor_detect(cnf):
    if not cnf or not all(len(c)==3 and len({abs(x) for x in c})==3 for c in cnf):
        return None
    groups = {}
    for c in cnf:
        k = tuple(sorted(abs(x) for x in c))
        groups.setdefault(k, []).append(tuple(c))
    equations=[]
    for k, clauses in groups.items():
        if len(clauses)!=4: return None
        forbidden=[]
        canonical=set(tuple(c) for c in clauses)
        for bits in itertools.product([False,True], repeat=3):
            if clause_forbid_assignment(k,bits) in canonical:
                forbidden.append(bits)
        if len(forbidden)!=4: return None
        parities={sum(b)%2 for b in forbidden}
        if len(parities)!=1: return None
        allowed_rhs = 1-next(iter(parities))
        equations.append((k,allowed_rhs))
    return equations


def gf2_solve(eqs):
    vs=sorted({v for k,_ in eqs for v in k}); idx={v:i for i,v in enumerate(vs)}
    rows=[]
    for k,rhs in eqs:
        mask=0
        for v in k: mask ^= 1<<idx[v]
        rows.append([mask,rhs])
    pivot=0
    for col in range(len(vs)):
        q=next((i for i in range(pivot,len(rows)) if (rows[i][0]>>col)&1),None)
        if q is None: continue
        rows[pivot],rows[q]=rows[q],rows[pivot]
        for i in range(len(rows)):
            if i!=pivot and ((rows[i][0]>>col)&1):
                rows[i][0]^=rows[pivot][0]; rows[i][1]^=rows[pivot][1]
        pivot+=1
    if any(mask==0 and rhs for mask,rhs in rows):
        return {"decision":"UNSAT","certificate":{"row":"0=1"},"verified":True}
    a={v:False for v in vs}
    for mask,rhs in reversed(rows):
        if not mask: continue
        p=(mask & -mask).bit_length()-1
        s=rhs
        for j,v in enumerate(vs):
            if j!=p and ((mask>>j)&1) and a[v]: s^=1
        a[vs[p]]=bool(s)
    return {"decision":"SAT","witness":a,"verified":True}


def dispatch(cnf):
    ledger={"route_checks":0,"literal_visits":sum(map(len,cnf)),"xor_bundle_checks":0,"certificate_checks":0}
    ledger["route_checks"]+=1
    r=two_sat(cnf)
    if r is not None: return "TWO_SAT_SCC_V1",r,ledger
    ledger["route_checks"]+=1
    r=horn_solve(cnf)
    if r is not None: return "HORN",r,ledger
    ledger["route_checks"]+=1
    r=dual_horn_solve(cnf)
    if r is not None: return "DUAL_HORN",r,ledger
    ledger["route_checks"]+=1
    rh=renamable_horn_small(cnf)
    if rh is not None:
        hr=horn_solve(rh["transformed"])
        if hr["decision"]=="SAT":
            a={v:(not val if rh["flip"][v] else val) for v,val in hr["witness"].items()}
            assert verify_assignment(cnf,a)
            hr={"decision":"SAT","witness":a,"verified":True,"diagnostic_only":True}
        return "RENAMABLE_HORN_EXACT_BRUTE_FORCE_OVER_POLARITY_VECTOR_FOR_SMALL_FIXTURES_ONLY",hr,ledger
    ledger["route_checks"]+=1; ledger["xor_bundle_checks"]+=len(cnf)
    eq=xor_detect(cnf)
    if eq is not None:
        gr=gf2_solve(eq)
        if gr["decision"]=="SAT": assert verify_assignment(cnf,gr["witness"])
        return "EXACT_WIDTH3_XOR_BUNDLE_TO_GF2_V1",gr,ledger
    return None,{"status":"OPEN_OUTSIDE_SWITCHBOARD","decision_authority":False},ledger


def xor_bundle(triple,rhs):
    return [list(clause_forbid_assignment(triple,b)) for b in itertools.product([False,True],repeat=3) if sum(b)%2 != rhs]

fixtures={
 "TWO_SAT_SAT": [[1,2],[-1,2]],
 "TWO_SAT_UNSAT": [[1],[-1]],
 "HORN_UNSAT": [[1],[2],[-1,-2,3],[-3]],
 "DUAL_HORN_SAT": [[1,2,-3]],
 "XOR3_SAT": xor_bundle((1,2,3),0),
 "ADVERSARIAL_OPEN_3CNF": [list(clause_forbid_assignment((1,2,3),b)) for b in itertools.product([False,True],repeat=3)]
}
expected={
 "TWO_SAT_SAT":("TWO_SAT_SCC_V1","CERTIFIED_ROUTE"),
 "TWO_SAT_UNSAT":("TWO_SAT_SCC_V1","CERTIFIED_ROUTE"),
 "HORN_UNSAT":("HORN","CERTIFIED_ROUTE"),
 "DUAL_HORN_SAT":("DUAL_HORN","CERTIFIED_ROUTE"),
 "XOR3_SAT":("EXACT_WIDTH3_XOR_BUNDLE_TO_GF2_V1","CERTIFIED_ROUTE"),
 "ADVERSARIAL_OPEN_3CNF":(None,"OPEN_OUTSIDE_SWITCHBOARD")
}


def replay():
    out=[]
    for tid,cnf in fixtures.items():
        route,res,ledger=dispatch(norm(cnf))
        status="CERTIFIED_ROUTE" if route is not None else "OPEN_OUTSIDE_SWITCHBOARD"
        er,es=expected[tid]
        assert route==er,(tid,route,er)
        assert status==es,(tid,status,es)
        if route is not None:
            assert res.get("verified") is True
            authority = route != "RENAMABLE_HORN_EXACT_BRUTE_FORCE_OVER_POLARITY_VECTOR_FOR_SMALL_FIXTURES_ONLY"
        else:
            authority=False
        out.append({"id":tid,"route":route,"status":status,"decision":res.get("decision"),"decision_authority":authority,"ledger":ledger})
    return {
      "gate_id":"R44_EXACT_REPRESENTATION_SWITCHBOARD_COVERAGE_OR_COUNTEREXAMPLE",
      "status":"FROZEN_EXPECTATIONS_REPRODUCED_WITH_SCC_2SAT",
      "tests":out,
      "two_sat_algorithm":"SCC_2SAT_V1",
      "two_sat_asymptotic_cost":"O(V+E)",
      "counterexample_to_frozen_switchboard":"ADVERSARIAL_OPEN_3CNF",
      "universal_coverage_proved":False,
      "proof_authority_delta":0,
      "TRUMP_finished":False,
      "SAT_IN_P":"NOT_PROVED",
      "P_VS_NP":"OPEN",
      "next_question":"What exact invariant shared by OPEN residuals enables a new polynomial representation switch without hidden exponential compilation?"
    }


if __name__ == "__main__":
    print(json.dumps(replay(),sort_keys=True))
