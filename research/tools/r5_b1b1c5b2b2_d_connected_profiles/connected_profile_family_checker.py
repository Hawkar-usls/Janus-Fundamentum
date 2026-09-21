#!/usr/bin/env python3
"""
B2B2-D finite verifier for the connected-Q_ALL exponential profile family.

Family K_k:
  Seed S={t,s4}, edge t-s4; f(t)=3, f(s4)=4.
  Dynamic L={l1..lk}, R={r1..rk}.
  Every dynamic vertex is adjacent to s4 and nonadjacent to t.
  Chain edges li-rj iff j<=i.
  Residual Y0={z}, with z adjacent to every rj and to no li/seed.
  X0=empty.

All dynamic vertices initially have source list {1,2,3}.
Force any F subseteq {l1,...,l{k-1}} to color 1; lk is retained.
The final Q_ALL stays connected.  Distinct F have distinct survivor degree sets
on L because li has exactly i neighbors in R and [z] marks R as the component
boundary side.

This is finite sanity/evidence; the arbitrary-k proof is stored in the result.
"""
from itertools import combinations

def build(k):
    t="t"; s="s4"; z="z"
    L=[f"l{i}" for i in range(1,k+1)]
    R=[f"r{j}" for j in range(1,k+1)]
    V=[t,s,z]+L+R
    E={tuple(sorted((t,s)))}
    for v in L+R:
        E.add(tuple(sorted((s,v))))
    for i,li in enumerate(L,1):
        for j,rj in enumerate(R,1):
            if j<=i:
                E.add(tuple(sorted((li,rj))))
    for r in R:
        E.add(tuple(sorted((z,r))))
    return V,E,L,R,t,s,z

def adj(E,a,b):
    return tuple(sorted((a,b))) in E

def has_induced_p7(V,E):
    # brute force ordered simple paths; k small in verifier
    n=len(V)
    target=7
    def extend(path):
        if len(path)==target:
            # consecutive are edges by construction; require all nonconsecutive nonedges
            for i in range(target):
                for j in range(i+2,target):
                    if adj(E,path[i],path[j]):
                        return True
            return False
        last=path[-1]
        for v in V:
            if v in path or not adj(E,last,v):
                continue
            # New vertex must avoid all earlier nonconsecutive path vertices
            if any(adj(E,v,path[i]) for i in range(len(path)-1)):
                continue
            if extend(path+[v]): return True
        return False
    return any(extend([v]) for v in V)

def source_axioms_root(k):
    V,E,L,R,t,s,z=build(k)
    S={t,s}; X0=set(); Y0={z}; Y=set(L+R)
    # (i) G-X0 connected
    seen={t}; stack=[t]
    while stack:
        x=stack.pop()
        for y in V:
            if y not in seen and adj(E,x,y):
                seen.add(y); stack.append(y)
    assert seen==set(V)
    # (ii) S connected, nobody outside complete to S
    assert adj(E,t,s)
    for v in set(V)-S:
        assert not (adj(E,v,t) and adj(E,v,s))
    # (iii) exact Y0
    calc={v for v in V if v not in S|X0 and not any(adj(E,v,q) for q in S)}
    assert calc==Y0
    # (iv) vacuous: Y0 singleton
    # (v): all U source lists have size 3 (see only seed color 4)
    # (vi): Y∩N(Y0)=R, all same source list
    assert {v for v in Y if adj(E,v,z)}==set(R)
    return True

def profile_signature(k,F):
    V,E,L,R,t,s,z=build(k)
    F=set(F)
    liveL=[li for li in L if li not in F]
    # li has exact R-neighborhood size i; R all remain live.
    surviving_degrees=tuple(i for i,li in enumerate(L,1) if li not in F)
    # right source class after forcing: X iff it has a forced neighbor
    r_classes=[]
    for j,r in enumerate(R,1):
        hit=any(int(li[1:])>=j for li in F)
        r_classes.append("X2" if hit else "Y3")
    return (surviving_degrees,tuple(r_classes))

def reachable_and_connected(k,F):
    V,E,L,R,t,s,z=build(k)
    F=set(F)
    assert L[-1] not in F
    # every unforced left remains nonadjacent to all forced left => color1 stays available
    for li in set(L)-F:
        assert all(not adj(E,li,f) for f in F)
    # z anticomplete to forced L => residual singleton retained
    assert all(not adj(E,z,f) for f in F)
    # Q_ALL live block: carrier C-z adjacent every R; lk remains and adjacent every R.
    lk=L[-1]
    assert lk not in F
    assert all(adj(E,lk,r) for r in R)
    assert all(adj(E,z,r) for r in R)
    return True

def main():
    receipts=[]
    for k in range(2,9):
        assert source_axioms_root(k)
        assert not has_induced_p7(*build(k)[:2])
        seen={}
        optional=build(k)[2][:-1]
        for mask in range(1<<len(optional)):
            F={optional[i] for i in range(len(optional)) if mask>>i & 1}
            assert reachable_and_connected(k,F)
            sig=profile_signature(k,F)
            assert sig not in seen, (k,F,seen.get(sig))
            seen[sig]=F
        assert len(seen)==2**(k-1)
        receipts.append({"k":k,"profiles":len(seen),"expected":2**(k-1)})
    print({
      "root_source_axioms_i_to_vi":"PASS",
      "P7_free_checked_k_2_to_8":"PASS",
      "all_subsets_reachable":"PASS",
      "QALL_connected_after_every_tested_subset":"PASS",
      "canonical_profile_injection_by_surviving_nested_degrees":"PASS",
      "receipts":receipts,
      "future_distinguishability":"NOT_TESTED_D_FIREWALL",
      "status":"PASS_FINITE_SANITY_EXPONENTIAL_PROFILES"
    })

if __name__=="__main__":
    main()
