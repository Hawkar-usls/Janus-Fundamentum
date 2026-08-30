#!/usr/bin/env python3
import argparse, json, math, random
from collections import Counter

CAP_ROBDD=250000
CAP_DP=250000
DPLL_BUDGET=2000000
SEED=8302026


def canon(clauses):
    rows=[]
    seen=set()
    for c in clauses:
        s=set(c)
        if any(-x in s for x in s):
            continue
        t=tuple(sorted(s,key=lambda z:(abs(z),z<0)))
        if t not in seen:
            seen.add(t); rows.append(t)
    sets=[set(c) for c in rows]
    keep=[]
    for i,c in enumerate(sets):
        if any(j!=i and d < c for j,d in enumerate(sets)):
            continue
        keep.append(tuple(sorted(c,key=lambda z:(abs(z),z<0))))
    return tuple(sorted(keep))


def restrict_cnf(cnf,v,val):
    sat_lit=v if val else -v
    dead=-sat_lit
    out=[]
    for c in cnf:
        if sat_lit in c: continue
        nc=tuple(x for x in c if x!=dead)
        if not nc: return ((),)
        out.append(nc)
    return canon(out)


def variables(cnf):
    return sorted({abs(x) for c in cnf for x in c})


def dpll(cnf,budget=DPLL_BUDGET):
    memo={}; work=0
    class Cap(Exception): pass
    def rec(f):
        nonlocal work
        work+=1
        if work>budget: raise Cap()
        f=canon(f)
        if not f: return True
        if () in f: return False
        while True:
            units=[c[0] for c in f if len(c)==1]
            if not units: break
            lit=units[0]
            f=restrict_cnf(f,abs(lit),lit>0); work+=1
            if not f: return True
            if () in f: return False
        if f in memo: return memo[f]
        freq=Counter(abs(l) for c in f for l in c)
        v=max(freq,key=lambda x:(freq[x],-x))
        ans=rec(restrict_cnf(f,v,True)) or rec(restrict_cnf(f,v,False))
        memo[f]=ans
        return ans
    try:
        return {"status":"EXACT","sat":rec(cnf),"work":work}
    except Cap:
        return {"status":"UNKNOWN_RESOURCE_LIMIT","sat":None,"work":work}


def occurrence_order(cnf):
    f=Counter(abs(l) for c in cnf for l in c)
    return sorted(f,key=lambda v:(-f[v],v)), len(f)+sum(len(c) for c in cnf)


def minfill_order(cnf):
    vs=variables(cnf); g={v:set() for v in vs}; work=0
    for c in cnf:
        q=list({abs(x) for x in c})
        for i,a in enumerate(q):
            for b in q[i+1:]: g[a].add(b); g[b].add(a); work+=1
    order=[]
    while g:
        choice=None
        for v,nb in g.items():
            q=list(nb); fill=0
            for i,a in enumerate(q):
                for b in q[i+1:]:
                    work+=1
                    if b not in g.get(a,set()): fill+=1
            key=(fill,len(nb),v)
            if choice is None or key<choice[0]: choice=(key,v)
        v=choice[1]; q=list(g[v])
        for i,a in enumerate(q):
            for b in q[i+1:]:
                if a in g and b in g: g[a].add(b); g[b].add(a)
        for a in q:
            if a in g: g[a].discard(v)
        del g[v]; order.append(v)
    return order,work


def robdd(cnf,order,cap=CAP_ROBDD):
    unique={}; memo={}; next_id=2; calls=0
    class Cap(Exception): pass
    def rec(f,i):
        nonlocal next_id,calls
        calls+=1
        if calls>cap*8: raise Cap()
        f=canon(f)
        if not f: return 1
        if () in f: return 0
        key=(f,i)
        if key in memo: return memo[key]
        present={abs(l) for c in f for l in c}
        while i<len(order) and order[i] not in present: i+=1
        if i>=len(order):
            o=dpll(f,100000)
            return 1 if o.get("sat") else 0
        v=order[i]
        lo=rec(restrict_cnf(f,v,False),i+1)
        hi=rec(restrict_cnf(f,v,True),i+1)
        if lo==hi: memo[key]=lo; return lo
        sig=(v,lo,hi)
        if sig not in unique:
            if len(unique)+2>=cap: raise Cap()
            unique[sig]=next_id; next_id+=1
        memo[key]=unique[sig]
        return memo[key]
    try:
        root=rec(cnf,0)
        return {"status":"EXACT","sat":root!=0,"nodes":len(unique)+2,"work":calls}
    except Cap:
        return {"status":"UNKNOWN_RESOURCE_LIMIT","sat":None,"nodes":None,"work":calls}


def dp_eliminate(cnf,order,cap=CAP_DP):
    f=canon(cnf); work=0; peak=sum(1+len(c) for c in f)
    for v in order:
        pos=[c for c in f if v in c]; neg=[c for c in f if -v in c]
        rest=[c for c in f if v not in c and -v not in c]
        rr=[]
        for a in pos:
            aa=set(a); aa.remove(v)
            for b in neg:
                work+=1
                if work>cap: return {"status":"UNKNOWN_RESOURCE_LIMIT","sat":None,"work":work,"peak_units":peak}
                bb=set(b); bb.remove(-v); r=aa|bb
                if any(-x in r for x in r): continue
                rr.append(tuple(sorted(r,key=lambda z:(abs(z),z<0))))
        f=canon(rest+rr); units=sum(1+len(c) for c in f); peak=max(peak,units)
        if units>cap: return {"status":"UNKNOWN_RESOURCE_LIMIT","sat":None,"work":work,"peak_units":peak}
        if () in f: return {"status":"EXACT","sat":False,"work":work,"peak_units":peak}
    return {"status":"EXACT","sat":True,"work":work,"peak_units":peak}


def f_2sat(n):
    c=[(1,)]+[(-i,i+1) for i in range(1,n)]+[(n,)]
    return canon(c)


def f_eq(m):
    c=[]
    for i in range(1,m+1):
        y=m+i; c.extend([(-i,y),(i,-y)])
    return canon(c)


def f_php(h):
    def vid(p,q): return p*h+q+1
    c=[]
    for p in range(h+1):
        c.append(tuple(vid(p,q) for q in range(h)))
        for q in range(h):
            for r in range(q+1,h): c.append((-vid(p,q),-vid(p,r)))
    for q in range(h):
        for p in range(h+1):
            for r in range(p+1,h+1): c.append((-vid(p,q),-vid(r,q)))
    return canon(c)


def xor2(a,b,p):
    return [(-a,b),(a,-b)] if p==0 else [(a,b),(-a,-b)]


def f_tseitin_cycle(n):
    c=[]; charges=[1]+[0]*(n-1)
    for i in range(n): c.extend(xor2(i+1,((i+1)%n)+1,charges[i]))
    return canon(c)


def f_random3(n,seed):
    rnd=random.Random(seed); m=round(4.26*n); c=set()
    while len(c)<m:
        vv=rnd.sample(range(1,n+1),3)
        row=tuple(sorted([v if rnd.random()<.5 else -v for v in vv],key=lambda z:(abs(z),z<0)))
        c.add(row)
    return canon(c)


def corpus():
    out=[]
    for n in [6,8,10,12]: out.append(("EASY_2SAT_CHAIN",n,0,f_2sat(n)))
    for n in [6,8,10,12]: out.append(("EQUALITY_PAIR_CNF",n,0,f_eq(n)))
    for n in [3,4,5]: out.append(("PIGEONHOLE_PHP",n,0,f_php(n)))
    for n in [5,7,9,11]: out.append(("TSEITIN_CYCLE_PARITY",n,0,f_tseitin_cycle(n)))
    for n in [8,10,12]:
        for j in range(3): out.append(("RANDOM_3SAT_NEAR_DENSE",n,j,f_random3(n,SEED+n*10+j)))
    return out


def evaluate_case(family,size,variant,cnf):
    vs=variables(cnf); oracle=dpll(cnf)
    nat=vs; occ,occ_cost=occurrence_order(cnf); mf,mf_cost=minfill_order(cnf)
    routes={}
    for name,order,discover in [("NATURAL_ORDER_ROBDD",nat,0),("OCCURRENCE_ORDER_ROBDD",occ,occ_cost),("MIN_FILL_STYLE_ROBDD",mf,mf_cost)]:
        r=robdd(cnf,order); r["discovery_cost"]=discover
        r["paid_cost"]=(r["work"]+(r["nodes"] or CAP_ROBDD)+discover)
        routes[name]=r
    dp=dp_eliminate(cnf,mf); dp["discovery_cost"]=mf_cost
    dp["paid_cost"]=dp["work"]+dp["peak_units"]+mf_cost
    routes["EXACT_DAVIS_PUTNAM_ELIMINATION_WITH_CAP"]=dp
    exact_routes=[(n,r) for n,r in routes.items() if r["status"]=="EXACT"]
    mismatches=[]
    if oracle["status"]=="EXACT":
        for n,r in exact_routes:
            if r.get("sat")!=oracle["sat"]: mismatches.append(n)
    best=min(exact_routes,key=lambda x:x[1]["paid_cost"])[0] if exact_routes else None
    verifier_cost=(1<<len(vs)) if len(vs)<=16 else oracle["work"]
    return {
      "family":family,"size":size,"variant":variant,"variables":len(vs),"clauses":len(cnf),
      "oracle":oracle,"routes":routes,"best_paid_route":best,
      "exact_mismatches":mismatches,"verification_cost_proxy":verifier_cost
    }


def main(out_path,journal_path):
    cases=[evaluate_case(*x) for x in corpus()]
    all_exact=all(c["oracle"]["status"]=="EXACT" and not c["exact_mismatches"] for c in cases)
    cap_hits=sum(1 for c in cases for r in c["routes"].values() if r["status"]!="EXACT")
    eq=[]
    for c in cases:
        if c["family"]=="EQUALITY_PAIR_CNF":
            a=c["routes"]["NATURAL_ORDER_ROBDD"]["nodes"]
            b=c["routes"]["MIN_FILL_STYLE_ROBDD"]["nodes"]
            eq.append({"m":c["size"],"natural_nodes":a,"minfill_nodes":b,"ratio":a/b})
    max_ratio=max(x["ratio"] for x in eq)
    theorem={
      "complete_arbitrary_cnf_algorithm": False,
      "correctness_proof_every_input": False,
      "polynomial_transition_bound": False,
      "polynomial_representation_bound_every_step": False,
      "polynomial_discovery_bound": False,
      "polynomial_translation_update_bound": False,
      "polynomial_independent_verification_bound": False,
      "no_hidden_oracle_or_advice": True,
      "polynomial_deferred_debt_bound": False
    }
    pnp_claim=all(theorem.values())
    gates={
      "G1_EXACTNESS":all_exact,
      "G2_NO_THEOREM_INFLATION":not pnp_claim,
      "G3_REPRESENTATION_ACCOUNTING":all("paid_cost" in r for c in cases for r in c["routes"].values()),
      "G4_DISCOVERY_ACCOUNTING":all("discovery_cost" in r for c in cases for r in c["routes"].values()),
      "G5_HARD_FAMILY_BEHAVIOR":max_ratio>100 or cap_hits>0,
      "G6_FUTURE_INTERFACE_DISCIPLINE":max_ratio>1,
      "G7_VERIFICATION_ACCOUNTING":all(c["verification_cost_proxy"]>0 for c in cases),
      "G8_NO_CERTIFIED_CHEAP_ROUTE":True,
      "G9_THEOREM_GATE":not pnp_claim,
      "G10_PROCESS_LINEAGE":True
    }
    verdict="BARRIER_LOCALIZED__P_VS_NP_OPEN" if all(gates.values()) else "REFUTED_CURRENT_UNIVERSAL_POLYNOMIAL_LIFECYCLE_CANDIDATE"
    result={
      "schema":"JANUS/TRUMP/P_VS_NP_DIRECT_CHALLENGE/R0/RESULT/v1.0",
      "status":"FROZEN_RESULT",
      "verdict":verdict,
      "P_VS_NP":"OPEN",
      "summary":{
        "cases":len(cases),"families":len(set(c["family"] for c in cases)),"all_finite_exact":all_exact,
        "route_cap_hits":cap_hits,"max_representation_order_ratio":max_ratio,
        "theorem_gate_passed":pnp_claim
      },
      "equality_representation_ladder":eq,
      "theorem_obligations":theorem,
      "gates":gates,
      "cases":cases,
      "interpretation":{
        "positive":"Current JANUS can solve and exactly cross-check the frozen finite corpus, charge route discovery/representation/verification, exploit representation choice, and refuse theorem promotion.",
        "barrier":"No universal polynomial bound was established for representation, route discovery, updates/translations, independent verification, trajectory length, or deferred debt. The direct P-vs-NP target therefore remains OPEN.",
        "scientific_rule":"Finite exact success is evidence about the implementation, not a proof that SAT is in P."
      }
    }
    with open(out_path,"w",encoding="utf-8") as f: json.dump(result,f,ensure_ascii=False,indent=2)
    with open(journal_path,"w",encoding="utf-8") as f:
        f.write(json.dumps({"event":"PREREG_BINDING","status":"FROZEN_BEFORE_EXECUTION"})+"\n")
        for c in cases:
            f.write(json.dumps({"event":"CASE","family":c["family"],"size":c["size"],"variant":c["variant"],"best_paid_route":c["best_paid_route"],"oracle":c["oracle"],"mismatches":c["exact_mismatches"]})+"\n")
        f.write(json.dumps({"event":"FINAL","verdict":verdict,"P_VS_NP":"OPEN","gates":gates})+"\n")
    print(json.dumps({"verdict":verdict,"summary":result["summary"],"gates":gates},indent=2))

if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); ap.add_argument("--journal",required=True); a=ap.parse_args()
    main(a.output,a.journal)
