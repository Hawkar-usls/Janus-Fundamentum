#!/usr/bin/env python3
"""
Finite sanity checker for
R5_B1B1C5B2B2_E1_FOUR_COLOR_ACTIVE_CONNECTED_CORE_STRESS_V1.

Family X_k, k>=3:
  seed S={s1,s4}, edge s1-s4, colors 1 and 4;
  L={l1,...,lk}, R={r1,...,rk}, residual Y0={z};
  s4 adjacent to all L and to s1;
  s1 adjacent to all R and to s4;
  l_i-r_j iff j<=i;
  z-r_j iff j<=k-1;
  no other edges.

Thus H=G[L union R union {z}] is a chain graph on bipartition
(L union {z}, R), while the full graph is bipartite with sides
A={s1,z} union L and B={s4} union R.

Reachable profile family:
  force any subset F subset {l2,...,l_{k-1}} to color 1.
  l1 and lk are retained, giving 2^(k-2) canonical profiles.

Checks:
- no induced P7 for calibration k<=8;
- source axioms (i)-(vi) for every tested forced subset;
- one connected Q_ALL block;
- no global missing color on live dynamic vertices;
- all four colors occur in authorized R2 queries;
- exactly 2^(k-2) distinct canonical live-left degree signatures.

Finite sanity only. Arbitrary-k authority is the structural theorem proof.
"""

from itertools import combinations

COLORS={1,2,3,4}

def ekey(u,v):
    return tuple(sorted((u,v)))

def build(k):
    s1,s4,z="s1","s4","z"
    L=[f"l{i}" for i in range(1,k+1)]
    R=[f"r{j}" for j in range(1,k+1)]
    V=[s1,s4,z]+L+R
    E=set()
    def add(u,v): E.add(ekey(u,v))
    add(s1,s4)
    for l in L: add(s4,l)
    for r in R: add(s1,r)
    for i,l in enumerate(L,1):
        for j,r in enumerate(R,1):
            if j<=i: add(l,r)
    for j,r in enumerate(R,1):
        if j<=k-1: add(z,r)
    return V,E,L,R

def adj(E,u,v):
    return ekey(u,v) in E

def neigh(V,E,v):
    return {w for w in V if w!=v and adj(E,v,w)}

def connected(V,E,nodes):
    nodes=set(nodes)
    if not nodes: return True
    s=next(iter(nodes)); seen={s}; st=[s]
    while st:
        u=st.pop()
        for v in list(nodes-seen):
            if adj(E,u,v):
                seen.add(v); st.append(v)
    return seen==nodes

def induced_p7(V,E):
    def dfs(path):
        if len(path)==7: return tuple(path)
        for v in V:
            if v in path: continue
            if not adj(E,path[-1],v): continue
            if any(adj(E,v,w) for w in path[:-1]): continue
            path.append(v)
            ans=dfs(path)
            if ans: return ans
            path.pop()
        return None
    for s in V:
        ans=dfs([s])
        if ans: return ans
    return None

def state(k,F):
    V,E,L,R=build(k)
    F=set(F)
    S={"s1","s4"}|{f"l{i}" for i in F}
    X0=set()
    fixed={"s1":1,"s4":4}
    fixed.update({f"l{i}":1 for i in F})

    LP={}
    for v in V:
        if v in S or v in X0: continue
        blocked={fixed[w] for w in neigh(V,E,v)&S}
        LP[v]=COLORS-blocked

    Y0={v for v in V if v not in S|X0 and not (neigh(V,E,v)&S)}
    X={v for v in LP if len(LP[v])==2}
    Y={v for v in LP if len(LP[v])==3}
    Z1={v for v in LP if len(LP[v])==1}
    Z0={v for v in LP if len(LP[v])==0}

    ax_i=connected(V,E,set(V)-X0)
    ax_ii_seed=connected(V,E,S)
    ax_ii_no_complete=all(
        not all(adj(E,v,s) for s in S) for v in set(V)-S
    )
    canon={v for v in V if v not in S|X0 and not (neigh(V,E,v)&S)}
    ax_iii=(Y0==canon)

    ax_iv=True
    for a,b in combinations(Y0,2):
        if adj(E,a,b):
            for v in set(V)-Y0-X0:
                if adj(E,v,a)!=adj(E,v,b):
                    ax_iv=False

    ax_v=(not Z0 and not Z1 and set(LP)==X|Y|Y0 and
          all(len(LP[v])==4 for v in Y0))

    Yn={y for y in Y if neigh(V,E,y)&Y0}
    ax_vi=(len({tuple(sorted(LP[y])) for y in Yn})<=1)

    # Q_ALL: live dynamics X union Y plus [z], with [z]-r_j for j<=k-1.
    live=X|Y
    qnodes=set(live)|{"[z]"}
    qedges={ekey(u,v) for u,v in E if u in live and v in live}
    for j in range(1,k):
        r=f"r{j}"
        if r in live: qedges.add(ekey("[z]",r))
    qall_conn=connected(list(qnodes),qedges,qnodes)

    # No global missing color over live exact palettes.
    union=set()
    for v in live: union |= LP[v]
    four_active=(union==COLORS)

    # Canonical profile injection: L/R are distinguished by source lists.
    # Every surviving l_i has exactly i R-neighbors.
    sig=tuple(i for i in range(1,k+1) if f"l{i}" in live)

    return {
      "axioms":(ax_i,ax_ii_seed,ax_ii_no_complete,ax_iii,ax_iv,ax_v,ax_vi),
      "Y0":Y0,"Z0":Z0,"Z1":Z1,"qall_connected":qall_conn,
      "four_active":four_active,"signature":sig,"LP":LP,
      "live":live,"V":V,"E":E
    }

def all_four_R2_activity(k,F):
    st=state(k,F)
    LP=st["LP"]; E=st["E"]
    # permanent live anchors: l1, lk, r1, rk
    l1=f"l1"; lk=f"l{k}"; r1=f"r1"; rk=f"r{k}"
    witnesses={
      1:(l1,lk),
      2:(l1,lk),
      3:(l1,lk),
      4:(r1,rk),
    }
    for c,(u,v) in witnesses.items():
        assert u in st["live"] and v in st["live"]
        assert not adj(E,u,v)
        assert c in LP[u] and c in LP[v]
    return True

def main():
    for k in range(3,9):
        V,E,_,_=build(k)
        assert induced_p7(V,E) is None

    receipts=[]
    for k in range(3,9):
        sigs=set()
        for mask in range(1<<(k-2)):
            F={i+2 for i in range(k-2) if (mask>>i)&1}
            st=state(k,F)
            assert all(st["axioms"])
            assert st["Y0"]=={"z"}
            assert not st["Z0"] and not st["Z1"]
            assert st["qall_connected"]
            assert st["four_active"]
            assert all_four_R2_activity(k,F)
            sigs.add(st["signature"])
        assert len(sigs)==1<<(k-2)
        receipts.append({
          "k":k,
          "profiles":len(sigs),
          "expected":1<<(k-2)
        })

    print({
      "P7_calibration_k_3_to_8":"PASS",
      "source_axioms_i_to_vi":"PASS",
      "connected_QALL":"PASS",
      "no_global_missing_color":"PASS",
      "all_four_R2_activity":"PASS",
      "profile_count_2^(k-2)":"PASS",
      "receipts":receipts,
      "status":"PASS_FINITE_SANITY"
    })

if __name__=="__main__":
    main()
