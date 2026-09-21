#!/usr/bin/env python3
"""
Finite sanity checker for authoritative E3 candidate
HUANG_ALLTRIPLES_B0_VACUOUS_Hk_V2.

Same all-positive Huang G_{C7,I_k} family as the preliminary candidate, but
the distinguished seed colors are:
  c*=2, x2=1, u1=3, u6=4.

Root source singletons ~x2 and d2 are deterministically promoted to X0 with
colors 2 and 1.  Optional forcing v_i=1 similarly promotes ~v_i=2.

Checks for k=3,4:
- root/descendant fixed set is proper;
- source Z0 empty and canonical Z1 exactly the declared X0 promotions;
- G-X0 connected;
- Y0 stable;
- every Y vertex meeting Y0 has the single source list {2,3,4}, so B0
  competing-survivor provenance is vacuous;
- explicit total coloring extends every forced subset and X0 promotion;
- Q_ALL connected;
- exact live palettes use all four colors globally;
- exactly 2^k distinct structural signatures;
- all four colors have permanent R2 witnesses under the explicit coloring;
- all-triples optional dependency primal graph is K_k.

P7-freeness is source-bound to Huang's theorem because the underlying graph is
exactly G_{C7,I_k}; no graph edge is added.
"""
from itertools import combinations

COLORS={1,2,3,4}
def ek(u,v): return tuple(sorted((u,v)))
def adj(E,u,v): return ek(u,v) in E

def connected(E,nodes):
    nodes=set(nodes)
    if not nodes: return True
    s=next(iter(nodes)); seen={s}; stack=[s]
    while stack:
        u=stack.pop()
        for v in nodes-seen:
            if adj(E,u,v):
                seen.add(v); stack.append(v)
    return seen==nodes

def build(k):
    n=3+k
    opts=list(range(4,4+k))
    clauses=[(2,1,3)]
    clauses += list(combinations(opts,3))
    for idx,v in enumerate(opts,1):
        clauses += [(1,3,v)]*(k*k+idx)

    V=set(); E=set(); X=[]; D=[]; C=[]; U=[]; clause_roles=[]
    def add(u,v):
        if u!=v: E.add(ek(u,v))

    for i in range(1,n+1):
        x,xb,d=f"x{i}",f"~x{i}",f"d{i}"
        V.update((x,xb,d)); X += [x,xb]; D.append(d); add(x,xb)

    for j,cl in enumerate(clauses,1):
        h=[f"h{j}_{p}" for p in range(7)]
        V.update(h)
        for p in range(7): add(h[p],h[(p+1)%7])
        localC=[]
        for t,pos in enumerate((0,2,4)):
            c=h[pos]; var=cl[t]
            localC.append(c); C.append(c)
            add(c,f"d{var}"); add(c,f"x{var}")
        localU=[h[p] for p in (1,3,5,6)]
        U += localU
        clause_roles.append((localC,localU,cl))

    for u in U:
        for x in X: add(u,x)
        for d in D: add(u,d)

    return dict(n=n,opts=opts,clauses=clauses,V=V,E=E,X=X,D=D,C=C,U=U,clause_roles=clause_roles)

def canonical_state(k,Fidx):
    G=build(k); V,E,opts=G["V"],G["E"],G["opts"]
    Fvars={opts[i-1] for i in Fidx}

    S={"h1_0","x2","h1_1","h1_6"} | {f"x{v}" for v in Fvars}
    fS={"h1_0":2,"x2":1,"h1_1":3,"h1_6":4}
    fS.update({f"x{v}":1 for v in Fvars})

    def N(v): return {w for w in V if w!=v and adj(E,v,w)}

    LP={}
    for v in V-S:
        blocked={fS[w] for w in N(v)&S}
        LP[v]=COLORS-blocked

    assert not {v for v in LP if len(LP[v])==0}
    Z1={v for v in LP if len(LP[v])==1}
    expected_Z1={"~x2","d2"} | {f"~x{v}" for v in Fvars}
    assert Z1==expected_Z1

    X0=set(Z1)
    fX={v:next(iter(LP[v])) for v in X0}
    assert fX["~x2"]==2 and fX["d2"]==1
    for v in Fvars: assert fX[f"~x{v}"]==2

    fixed={**fS,**fX}
    assert all(not (u in fixed and v in fixed and fixed[u]==fixed[v]) for u,v in E)
    assert connected(E,set(V)-X0)

    Xc={v for v in LP if v not in X0 and len(LP[v])==2}
    Y={v for v in LP if v not in X0 and len(LP[v])==3}
    Y0={v for v in LP if v not in X0 and len(LP[v])==4}
    assert all(not adj(E,a,b) for a,b in combinations(Y0,2))

    YN={y for y in Y if N(y)&Y0}
    vi_lists={tuple(sorted(LP[y])) for y in YN}
    assert vi_lists=={(2,3,4)}

    # exact palettes after X0 effects
    A={}
    for v in Xc|Y:
        blocked={fixed[w] for w in N(v)&(S|X0)}
        A[v]=COLORS-blocked

    # Explicit extension.
    col={}
    for i in range(1,G["n"]+1):
        col[f"d{i}"]=1; col[f"x{i}"]=1; col[f"~x{i}"]=2
    for j in range(1,len(G["clauses"])+1):
        col[f"h{j}_0"]=2; col[f"h{j}_2"]=2; col[f"h{j}_4"]=2
        col[f"h{j}_1"]=3; col[f"h{j}_3"]=3; col[f"h{j}_5"]=3; col[f"h{j}_6"]=4
    assert all(col[v]==c for v,c in fixed.items())
    assert all(col[u]!=col[v] for u,v in E)

    dyn=Xc|Y
    qnodes=set(dyn)|{f"[{z}]" for z in Y0}
    qedges={ek(u,v) for u,v in E if u in dyn and v in dyn}
    for z in Y0:
        for u in N(z)&dyn: qedges.add(ek(f"[{z}]",u))
    assert connected(qedges,qnodes)

    # 2^k structural profile injection.
    sig=[]
    for idx,v in enumerate(opts,1):
        d=f"d{v}"
        residual=sum(1 for z in Y0 if adj(E,d,z))
        dynamicC=sum(1 for c in G["C"] if c in dyn and adj(E,d,c))
        sig.append((idx,residual,dynamicC))

    # C1 fails on exact palettes in every state.
    ordinary_u=G["clause_roles"][1][1][0]
    assert A["d1"]=={1,2}
    assert A[ordinary_u]=={3,4}
    assert A["d1"]|A[ordinary_u]==COLORS

    # Permanent explicit R2 witnesses in the stored full coloring.
    assert col["d1"]==col["d3"]==1 and not adj(E,"d1","d3")
    assert col["~x1"]==col["~x3"]==2 and not adj(E,"~x1","~x3")
    u3a=G["clause_roles"][1][1][0]; u3b=G["clause_roles"][2][1][0]
    assert col[u3a]==col[u3b]==3 and not adj(E,u3a,u3b)
    u4a=G["clause_roles"][1][1][3]; u4b=G["clause_roles"][2][1][3]
    assert col[u4a]==col[u4b]==4 and not adj(E,u4a,u4b)

    return G,tuple(sig),len(V),len(G["clauses"])

def main():
    receipts=[]
    for k in (3,4):
        sigs=set()
        for mask in range(1<<k):
            F={i+1 for i in range(k) if (mask>>i)&1}
            G,sig,n,m=canonical_state(k,F)
            sigs.add(sig)
        assert len(sigs)==1<<k

        opts=G["opts"]
        core=[set(c) for c in G["clauses"] if set(c)<=set(opts)]
        primal={tuple(sorted((a,b))) for C in core for a,b in combinations(C,2)}
        assert len(primal)==k*(k-1)//2

        receipts.append({
          "k":k,
          "vertices":n,
          "clauses":m,
          "profiles":len(sigs),
          "expected_profiles":1<<k,
          "optional_primal":"K_k"
        })

    print({
      "root_and_descendant_singleton_promotion":"PASS",
      "B0_competing_survivor_provenance":"VACUOUS",
      "explicit_extension_all_subsets":"PASS",
      "QALL_connected":"PASS",
      "exact_four_color_activity":"PASS",
      "profile_injection_2^k":"PASS",
      "optional_dependency_primal":"K_k",
      "status":"PASS_FINITE_SANITY"
    })

if __name__=="__main__":
    main()
