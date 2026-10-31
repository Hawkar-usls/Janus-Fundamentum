#!/usr/bin/env python3
from itertools import product, combinations


def allowed(r,qmod):
    out=set()
    for y in product((0,1), repeat=3):
        a=sum(y[:r]); b=sum(y[r:])
        if (qmod+a-b)%3==0:
            out.add(y)
    return out


def delta(rel):
    sets={frozenset(i for i,b in enumerate(t) if b) for t in rel}
    if not sets: return False
    for X in sets:
        for Y in sets:
            D=X^Y
            for e in D:
                ok=False
                for f in D:
                    toggle={e} if e==f else {e,f}
                    if X^toggle in sets:
                        ok=True; break
                if not ok: return False
    return True

expected={
 (0,0):{'000','111'}, (0,1):{'001','010','100'}, (0,2):{'011','101','110'},
 (1,0):{'000','101','110'}, (1,1):{'001','010','111'}, (1,2):{'011','100'},
 (2,0):{'000','011','101'}, (2,1):{'001','110'}, (2,2):{'010','100','111'},
 (3,0):{'000','111'}, (3,1):{'011','101','110'}, (3,2):{'001','010','100'},
}

for r in range(4):
    for q in range(3):
        R=allowed(r,q)
        S={''.join(map(str,t)) for t in R}
        assert S==expected[(r,q)]
        if len(R)==3:
            assert len({sum(t)%2 for t in R})==1
            assert all(sum(a!=b for a,b in zip(x,y))==2 for x,y in combinations(R,2))
            L=list(R)
            for mask in range(1,1<<len(L)):
                Q={L[i] for i in range(len(L)) if mask>>i & 1}
                assert delta(Q)
                assert len({sum(t)%2 for t in Q})==1
        else:
            assert len(R)==2
            x,y=tuple(R)
            assert all(a!=b for a,b in zip(x,y))
            assert not delta(R)
            assert delta({x}) and delta({y})

print({
 'status':'PASS_THREE_EDGE_CUT_BOUNDARY_ALGEBRA',
 'cases':12,
 'ambient_classes':'3-state even-delta or 2-state complementary',
 'interface_state_explosion':'CLOSED_FOR_SIZE_3',
 'hard_core':'THREE_CUT_IRREDUCIBLE_OPEN',
 'E8_D1':'EMPTY',
 'P_VS_NP':'OPEN',
})
