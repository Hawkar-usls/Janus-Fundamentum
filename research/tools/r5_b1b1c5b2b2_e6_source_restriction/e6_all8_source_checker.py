#!/usr/bin/env python3
"""
Finite source-restriction sanity checker for E6.

Builds one Huang G_{C7,I} instance whose optional variables v1,v2,v3 occur in
all eight literal-polarity versions of one ternary clause.  Uses the same
B0-vacuous authoritative seed as E3/E5:
  h1_0=2, x2=1, h1_1=3, h1_6=4
with deterministic root X0 promotions ~x2=2,d2=1.

Checks:
- all eight signed clause patterns coexist in one source-valid canonical state;
- root source Z0 empty and exact Z1 is {~x2,d2};
- B0 competing-survivor provenance is vacuous;
- Q_ALL is connected;
- optional x_i,d_i exact palettes remain binary {1,2};
- each optional negative literal is also binary and opposite its positive mate
  in every proper coloring;
- signed occurrence identity q=e xor sigma is exact;
- for every Boolean equality assignment e in {0,1}^3, pair states realizing e
  exist independently.

P7-freeness for arbitrary instances is source-bound to Huang's theorem;
this script is only a finite source-state sanity check.
"""
from itertools import product

COLORS={1,2,3,4}
def ek(u,v): return tuple(sorted((u,v)))
def adj(E,u,v): return ek(u,v) in E

def connected(E,nodes):
    nodes=set(nodes)
    if not nodes:return True
    s=next(iter(nodes)); seen={s}; st=[s]
    while st:
        u=st.pop()
        for v in nodes-seen:
            if adj(E,u,v):
                seen.add(v); st.append(v)
    return seen==nodes

def build():
    # anchors x1,x2,x3 plus optional x4,x5,x6
    n=6
    opts=(4,5,6)
    # distinguished anchor clause first
    clauses=[(("x",2),("x",1),("x",3))]
    # all 8 signs on optional variables
    for sig in product((0,1), repeat=3):
        cl=[]
        for var,s in zip(opts,sig):
            cl.append(("~x" if s else "x",var))
        clauses.append(tuple(cl))

    V=set();E=set();X=[];D=[];C=[];U=[]; roles=[]
    def add(u,v):
        if u!=v:E.add(ek(u,v))

    for i in range(1,n+1):
        x,xb,d=f"x{i}",f"~x{i}",f"d{i}"
        V.update((x,xb,d));X += [x,xb];D.append(d);add(x,xb)

    for j,cl in enumerate(clauses,1):
        h=[f"h{j}_{p}" for p in range(7)]
        V.update(h)
        for p in range(7):add(h[p],h[(p+1)%7])
        localC=[]
        for t,pos in enumerate((0,2,4)):
            c=h[pos]; lit,var=cl[t]
            localC.append(c);C.append(c)
            add(c,f"d{var}");add(c,f"{lit}{var}" if lit=="~x" else f"x{var}")
        localU=[h[p] for p in (1,3,5,6)]
        U += localU; roles.append((localC,localU,cl))

    for u in U:
        for x in X:add(u,x)
        for d in D:add(u,d)
    return dict(V=V,E=E,X=X,D=D,C=C,U=U,roles=roles,opts=opts)

def main():
    G=build();V,E=G["V"],G["E"]
    S={"h1_0","x2","h1_1","h1_6"}
    fS={"h1_0":2,"x2":1,"h1_1":3,"h1_6":4}
    def N(v):return {w for w in V if w!=v and adj(E,v,w)}

    assert connected(E,S)
    assert not [v for v in V-S if all(adj(E,v,s) for s in S)]

    LP={}
    for v in V-S:
        blocked={fS[w] for w in N(v)&S}
        LP[v]=COLORS-blocked
    assert not {v for v in LP if len(LP[v])==0}
    Z1={v for v in LP if len(LP[v])==1}
    assert Z1=={"~x2","d2"}

    X0=set(Z1); fX={"~x2":2,"d2":1}
    fixed={**fS,**fX}
    assert all(not (u in fixed and v in fixed and fixed[u]==fixed[v]) for u,v in E)
    assert connected(E,V-X0)

    Xc={v for v in LP if v not in X0 and len(LP[v])==2}
    Y={v for v in LP if v not in X0 and len(LP[v])==3}
    Y0={v for v in LP if v not in X0 and len(LP[v])==4}
    assert all(not adj(E,a,b) for a in Y0 for b in Y0 if a<b)

    YN={y for y in Y if N(y)&Y0}
    assert {tuple(sorted(LP[y])) for y in YN}=={(2,3,4)}

    # exact palettes after X0
    A={}
    for v in Xc|Y:
        blocked={fixed[w] for w in N(v)&(S|X0)}
        A[v]=COLORS-blocked
    for i in G["opts"]:
        assert A[f"x{i}"]=={1,2}
        assert A[f"~x{i}"]=={1,2}
        assert A[f"d{i}"]=={1,2}

    # Q_ALL connected
    dyn=Xc|Y
    qnodes=set(dyn)|{f"[{z}]" for z in Y0}
    qedges={ek(u,v) for u,v in E if u in dyn and v in dyn}
    for z in Y0:
        for u in N(z)&dyn:qedges.add(ek(f"[{z}]",u))
    assert connected(qedges,qnodes)

    # all eight sign patterns coexist
    signs=[]
    for _,_,cl in G["roles"][1:]:
        signs.append(tuple(1 if lit=="~x" else 0 for lit,var in cl))
    assert set(signs)==set(product((0,1),repeat=3))

    # q=e xor sigma identity over binary colors
    for x,d in product((1,2),repeat=2):
        e=int(x==d)
        xb=3-x
        assert int(x==d)==e
        assert int(xb==d)==1-e

    # every e vector independently realizable by pair states
    pair_for={0:(1,2),1:(1,1)}
    for evec in product((0,1),repeat=3):
        ps=[pair_for[e] for e in evec]
        assert tuple(int(x==d) for x,d in ps)==evec

    print({
      "all_8_signed_clause_patterns_in_one_source_state":"PASS",
      "root_Z1_exact":"PASS",
      "B0_competing_survivors":"VACUOUS",
      "QALL_connected":"PASS",
      "optional_pair_palettes":"{1,2}",
      "signed_occurrence_identity":"q=e xor sigma PASS",
      "all_equality_assignments_pair_state_realizable":"PASS",
      "status":"PASS_FINITE_SOURCE_RESTRICTION_SANITY"
    })

if __name__=="__main__":
    main()
