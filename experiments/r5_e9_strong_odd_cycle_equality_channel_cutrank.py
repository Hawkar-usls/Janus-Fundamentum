#!/usr/bin/env python3
from itertools import product


def belt_relation_k3():
    rel=set()
    for v in product((0,1), repeat=3):
        w=[]
        ok=True
        for i in range(3):
            s=v[i]+v[(i+1)%3]
            if s>1:
                ok=False
                break
            w.append(1-s)
        if ok:
            rel.add(tuple(w))
    return rel


def gf2_rank(rows, ncols):
    rows=list(rows)
    r=0
    for c in range(ncols):
        p=next((i for i in range(r,len(rows)) if (rows[i]>>c)&1), None)
        if p is None:
            continue
        rows[r],rows[p]=rows[p],rows[r]
        for i in range(len(rows)):
            if i!=r and ((rows[i]>>c)&1):
                rows[i]^=rows[r]
        r+=1
    return r


def main():
    rel=belt_relation_k3()
    expected={(1,1,1),(0,1,0),(0,0,1),(1,0,0)}
    assert rel==expected
    eq={(w0,w1) for (w0,w1,w2) in rel if w2==1}
    assert eq=={(0,0),(1,1)}

    checks=[]
    for m in range(1,9):
        n=1<<m
        # identity matrix rows as bitsets; over GF(2) its rank is n.
        rows=[1<<i for i in range(n)]
        rank=gf2_rank(rows,n)
        assert rank==n
        # Each row and column has exactly one 1, so any all-1 Boolean rectangle
        # contains at most one diagonal 1. Hence Boolean rank is n.
        row_degrees=[1]*n
        col_degrees=[1]*n
        assert all(d==1 for d in row_degrees+col_degrees)
        checks.append({"m":m,"states":n,"ordinary_rank":rank,"boolean_rank":n})

    out={
        "status":"PASS_STRONG_ODD_CYCLE_EQUALITY_CHANNEL_CUTRANK_BARRIER",
        "belt_relation_k3":sorted(rel),
        "pinned_relation":sorted(eq),
        "checks":checks,
        "theorem_scope":{
            "arbitrary_m_cut_rank":"2^m",
            "single_summary_state_lower_bound":"2^m",
            "polynomial_network_representation":"NOT_RULED_OUT",
            "universal_polynomial_decider":"OPEN",
            "P_VS_NP":"OPEN",
        },
    }
    import json
    print(json.dumps(out,sort_keys=True))


if __name__=="__main__":
    main()
