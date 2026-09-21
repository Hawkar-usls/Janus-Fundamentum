#!/usr/bin/env python3
"""
R5_B1B1C5B2B2_D finite sanity checker.

Family G_k:
  seed S={s4,s1}, edge s4-s1, colors f(s4)=4,f(s1)=1;
  L={l_1,...,l_k}, R={r_1,...,r_k}, residual Y0={z};
  s4 adjacent to every L,R; s1 adjacent only to s4;
  z adjacent to every R;
  L,R are stable;
  l_i-r_j iff j<=i.

Authorized descendants force any subset F subset {l_1,...,l_{k-1}}
to color 1.  l_k is deliberately never forced, so the Q_ALL block
remains connected.

Checks:
- no induced P7 on finite calibration sizes;
- exact source axioms (i)-(vi) on every forced subset;
- no Z0/Z1 promotion and no residual-component deletion;
- connected Q_ALL;
- 2^(k-1) pairwise distinct canonical structural signatures, witnessed
  by the set of degrees of live non-D_C vertices into D_C=R.

This script is finite sanity evidence only.  Arbitrary-k authority is the
structural proof stored in the D result/seal.
"""

from itertools import combinations

COLORS={1,2,3,4}

def ekey(u,v):
    return tuple(sorted((u,v)))

def build(k):
    s4,s1,z="s4","s1","z"
    L=[f"l{i}" for i in range(1,k+1)]
    R=[f"r{j}" for j in range(1,k+1)]
    V=[s4,s1,z]+L+R
    E=set()
    def add(u,v): E.add(ekey(u,v))
    add(s4,s1)
    for x in L+R:
        add(s4,x)
    for r in R:
        add(z,r)
    for i,l in enumerate(L,1):
        for j,r in enumerate(R,1):
            if j<=i:
                add(l,r)
    return V,E,L,R

def adj(E,u,v):
    return ekey(u,v) in E

def neighbors(V,E,v):
    return {w for w in V if w!=v and adj(E,v,w)}

def connected(V,E,nodes):
    nodes=set(nodes)
    if not nodes: return True
    s=next(iter(nodes)); seen={s}; st=[s]
    while st:
        u=st.pop()
        for v in nodes-seen:
            if adj(E,u,v):
                seen.add(v); st.append(v)
    return seen==nodes

def induced_p7(V,E):
    target=7
    def dfs(path):
        if len(path)==target:
            return tuple(path)
        for v in V:
            if v in path: continue
            if not adj(E,path[-1],v): continue
            if any(adj(E,v,w) for w in path[:-1]):
                continue
            path.append(v)
            ans=dfs(path)
            if ans: return ans
            path.pop()
        return None
    for s in V:
        ans=dfs([s])
        if ans: return ans
    return None

def forced_state(k,F):
    V,E,L,R=build(k)
    F=set(F)
    S={"s4","s1"} | {f"l{i}" for i in F}
    X0=set()
    fixed={"s4":4,"s1":1}
    fixed.update({f"l{i}":1 for i in F})

    LP={}
    for v in V:
        if v in S or v in X0: continue
        blocked={fixed[w] for w in neighbors(V,E,v)&S}
        LP[v]=COLORS-blocked

    Y0={v for v in V if v not in S|X0 and not (neighbors(V,E,v)&S)}
    X={v for v in LP if len(LP[v])==2}
    Y={v for v in LP if len(LP[v])==3}
    Z1={v for v in LP if len(LP[v])==1}
    Z0={v for v in LP if len(LP[v])==0}

    ax_i=connected(V,E,set(V)-X0)
    ax_ii_seed=connected(V,E,S)
    ax_ii_no_complete=all(
        not all(adj(E,v,s) for s in S) for v in set(V)-S
    )
    canon={v for v in V if v not in S|X0 and not (neighbors(V,E,v)&S)}
    ax_iii=(Y0==canon)

    ax_iv=True
    for a,b in combinations(Y0,2):
        if adj(E,a,b):
            for v in set(V)-Y0-X0:
                if adj(E,v,a)!=adj(E,v,b):
                    ax_iv=False

    ax_v=(
        not Z0 and not Z1 and
        set(LP)==X|Y|Y0 and
        all(len(LP[v])==4 for v in Y0)
    )
    Yn={y for y in Y if neighbors(V,E,y)&Y0}
    ax_vi=len({tuple(sorted(LP[y])) for y in Yn})<=1

    live=set(V)-S-X0-Y0
    # Q_ALL has live dynamic vertices plus one carrier [z].
    # [z] adjacent exactly to R.
    qnodes=set(live)|{"[z]"}
    qedges={ekey(u,v) for u,v in E if u in live and v in live}
    for r in R:
        if r in live:
            qedges.add(ekey("[z]",r))
    qconn=connected(list(qnodes),qedges,qnodes)

    liveL=[f"l{i}" for i in range(1,k+1) if i not in F]
    signature=tuple(sorted(
        sum(1 for r in R if adj(E,l,r)) for l in liveL
    ))

    return {
      "axioms":(ax_i,ax_ii_seed,ax_ii_no_complete,ax_iii,ax_iv,ax_v,ax_vi),
      "Z0":Z0,"Z1":Z1,"Y0":Y0,"X":X,"Y":Y,
      "qall_connected":qconn,
      "signature":signature
    }

def main():
    # finite P7 calibration
    for k in range(1,8):
        V,E,_,_=build(k)
        assert induced_p7(V,E) is None

    receipts=[]
    for k in range(2,8):
        sigs=set()
        for mask in range(1<<(k-1)):
            F={i+1 for i in range(k-1) if (mask>>i)&1}
            st=forced_state(k,F)
            assert all(st["axioms"])
            assert not st["Z0"] and not st["Z1"]
            assert st["Y0"]=={"z"}
            assert st["qall_connected"]
            sigs.add(st["signature"])
        assert len(sigs)==1<<(k-1)
        receipts.append({
          "k":k,
          "reachable_forced_subsets":1<<(k-1),
          "distinct_canonical_signatures":len(sigs)
        })

    print({
      "P7_calibration_k_le_7":"PASS",
      "all_forced_subsets_source_axioms_i_to_vi":"PASS",
      "no_Z0_Z1":"PASS",
      "residual_component_z_retained":"PASS",
      "Q_ALL_connected_for_all_tested_descendants":"PASS",
      "profile_count_matches_2^(k-1)":"PASS",
      "receipts":receipts,
      "status":"PASS_FINITE_SANITY"
    })

if __name__=="__main__":
    main()
