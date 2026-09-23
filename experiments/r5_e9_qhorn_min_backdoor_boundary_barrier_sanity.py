#!/usr/bin/env python3
"""Sanity witnesses for the q-Horn minimum-backdoor boundary semantics barrier.

For small k this script brute-forces q-Horn certificates, deletion backdoors,
and all boundary assignments.
"""

from itertools import product, combinations


def vars_of(clauses):
    return sorted({v for c in clauses for v, _ in c})


def qhorn(clauses):
    vs = vars_of(clauses)
    pos = {v:i for i,v in enumerate(vs)}
    # Store 2*beta in {0,1,2}.
    for beta in product((0,1,2), repeat=len(vs)):
        ok = True
        for c in clauses:
            s = 0
            for v, positive in c:
                b = beta[pos[v]]
                s += b if positive else 2-b
            if s > 2:
                ok = False
                break
        if ok:
            return True
    return False


def delete_vars(clauses, deleted):
    deleted = set(deleted)
    return [tuple(l for l in c if l[0] not in deleted) for c in clauses]


def simplify(clauses, assignment):
    out = []
    for c in clauses:
        residual = []
        satisfied = False
        for v, positive in c:
            if v in assignment:
                val = assignment[v]
                if val if positive else not val:
                    satisfied = True
                    break
            else:
                residual.append((v, positive))
        if not satisfied:
            out.append(tuple(residual))
    return out


def sat_bruteforce(clauses):
    vs = vars_of(clauses)
    for bits in product((False, True), repeat=len(vs)):
        a = dict(zip(vs, bits))
        if all(any(a[v] if p else not a[v] for v,p in c) for c in clauses):
            return True
    return False


def build(G, B):
    k = len(B)
    t = k + 1
    F = list(G)
    for b in B:
        for j in range(t):
            u = f"u_{b}_{j}"
            v = f"v_{b}_{j}"
            F.append(((b,True),(u,True),(v,True)))
            F.append(((b,False),(u,False),(v,False)))
    return F


def eval_formula(G, assignment):
    return all(any(assignment[v] if p else not assignment[v] for v,p in c)
               for c in G)


def main():
    # central gadget is non-q-Horn; deleting any one variable makes it Krom/q-Horn
    Q = [
        (("b",True),("u",True),("v",True)),
        (("b",False),("u",False),("v",False)),
    ]
    assert not qhorn(Q)
    for x in ("b","u","v"):
        assert qhorn(delete_vars(Q,{x}))

    # Small arbitrary boundary relation: XOR on two B variables.
    B = ["b0","b1"]
    G = [
        (("b0",True),("b1",True)),
        (("b0",False),("b1",False)),
    ]
    F = build(G,B)
    k = len(B)

    small_backdoors = []
    allvars = vars_of(F)
    for r in range(k+1):
        for S in combinations(allvars,r):
            if qhorn(delete_vars(F,S)):
                small_backdoors.append(set(S))

    assert small_backdoors == [set(B)]

    for bits in product((False,True), repeat=k):
        a = dict(zip(B,bits))
        assert sat_bruteforce(simplify(F,a)) == eval_formula(G,a)

    print("R5 E9 q-Horn minimum-backdoor boundary barrier sanity: PASS")


if __name__ == "__main__":
    main()
