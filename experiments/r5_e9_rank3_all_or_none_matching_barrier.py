#!/usr/bin/env python3

R={(0,0,0),(1,1,1)}

def as_set(t):
    return {i for i,b in enumerate(t) if b}

def is_delta_matroid(R):
    F=[as_set(t) for t in R]
    table={frozenset(S) for S in F}
    witnesses=[]
    for X in F:
        for Y in F:
            diff=X^Y
            for e in diff:
                ok=False
                for f in diff:
                    toggled = X ^ ({e} if e==f else {e,f})
                    if frozenset(toggled) in table:
                        ok=True
                        break
                if not ok:
                    witnesses.append((frozenset(X),frozenset(Y),e,frozenset(diff)))
                    return False,witnesses[0]
    return True,None

def main():
    ok,w=is_delta_matroid(R)
    assert not ok
    X,Y,e,diff=w
    assert X==frozenset()
    assert Y==frozenset({0,1,2})
    assert e in diff

    parities={sum(t)&1 for t in R}
    assert parities=={0,1}

    print("R_ALL_OR_NONE = {000,111}")
    print("DELTA_MATROID = FALSE")
    print("SYMMETRIC_EXCHANGE_WITNESS = X=empty, Y={0,1,2}")
    print("SUPPORT_PARITIES = {EVEN,ODD}")
    print("PURE_MATCHGATE_FIXED_PARITY = FAIL")
    print("D1 = EMPTY")
    print("P_VS_NP = OPEN")

if __name__=="__main__":
    main()
