import itertools, json, random, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from research.tools.typed_affine_open_message.typed_affine import affine_message_accepts, build_typed_affine_message

def clause_sat(c,a): return any(a[abs(l)] if l>0 else not a[abs(l)] for l in c)
def brute_profile(clauses,boundary):
    vs=sorted({abs(l) for c in clauses for l in c}); ins=[v for v in vs if v not in set(boundary)]; out=[]
    for bb in itertools.product((False,True),repeat=len(boundary)):
        base=dict(zip(boundary,bb)); ok=False
        for ib in itertools.product((False,True),repeat=len(ins)):
            a=dict(base); a.update(zip(ins,ib))
            if all(clause_sat(c,a) for c in clauses): ok=True; break
        out.append(ok)
    return tuple(out)
def msg_profile(m,b):
    return tuple(affine_message_accepts(m,dict(zip(b,bits))) for bits in itertools.product((False,True),repeat=len(b)))
def xor_gate(a,b,z): return [[a,b,-z],[a,-b,z],[-a,b,z],[-a,-b,-z]]
def force0(z,p,q): return [[-z,p,q],[-z,p,-q],[-z,-p,q],[-z,-p,-q]]
def parity_chain(n):
    xs=list(range(1,n+1)); nxt=n+1; clauses=[]; prev=None
    for i in range(1,n):
        a=xs[0] if i==1 else prev; b=xs[i]; z=nxt; nxt+=1; clauses+=xor_gate(a,b,z); prev=z
    clauses+=force0(prev,nxt,nxt+1); return clauses,xs
def cnf_eq(vs,rhs):
    out=[]
    for bits in itertools.product((False,True),repeat=len(vs)):
        if (sum(bits)&1)==rhs: continue
        out.append([(-v if bit else v) for v,bit in zip(vs,bits)])
    return out
def controls():
    c=xor_gate(1,2,3); m=build_typed_affine_message(c,[1,2])
    a={"pass":m["status"]=="AFFINE" and msg_profile(m,[1,2])==brute_profile(c,[1,2]),"message":m}
    m2=build_typed_affine_message([[1],[-1]],[])
    b={"pass":m2["status"]=="UNSAT","message":m2}
    m3=build_typed_affine_message([[1,2,3]],[1,2,3])
    d={"pass":m3["status"]=="UNRESOLVED","message":m3}
    return {"xor_projection":a,"affine_contradiction":b,"non_affine_or3_rejected":d}
def random_exact(seed=20260913,total=64):
    rng=random.Random(seed); passed=0; fail=None
    for i in range(total):
        n=rng.randint(2,7); allv=list(range(1,n+1)); boundary=sorted(rng.sample(allv,rng.randint(0,min(4,n))))
        clauses=[]; seen=set()
        for _ in range(rng.randint(1,6)):
            d=rng.randint(1,min(3,n)); sup=tuple(sorted(rng.sample(allv,d)))
            if sup in seen: continue
            seen.add(sup); clauses+=cnf_eq(sup,rng.randint(0,1))
        m=build_typed_affine_message(clauses,boundary); want=brute_profile(clauses,boundary)
        ok=m["status"] in ("AFFINE","UNSAT") and msg_profile(m,boundary)==want
        if ok: passed+=1
        elif fail is None: fail={"index":i,"clauses":clauses,"boundary":boundary,"message":m,"want":want}
    return {"passed":passed,"total":total,"seed":seed,"failure":fail}
def ladder():
    out=[]
    for n in (2,3,4,5,6,8,12,16,24,32,48,64,96,128):
        c,b=parity_chain(n); m=build_typed_affine_message(c,b)
        row={"n":n,"source_clauses":len(c),"flat_aux_free_cnf_lower_bound_clauses":2**(n-1),"status":m["status"],"message_rows":len(m.get("rows",())),"message_coefficients":m.get("message_coefficients")}
        row["pass"]=m["status"]=="AFFINE" and len(m.get("rows",()))==1 and set(m["rows"][0][0])==set(b) and m["rows"][0][1]==0 and m.get("message_coefficients")==n
        if n<=8: row["bruteforce_profile_match"]=msg_profile(m,b)==brute_profile(c,b); row["pass"]=row["pass"] and row["bruteforce_profile_match"]
        out.append(row)
    return out
def guard():
    text=Path(__file__).with_name("typed_affine.py").read_text(encoding="utf-8"); forbidden=["itertools.product","brute_profile","dpll(","solve_all_assignments","2 ** len(boundary)"]; hits=[x for x in forbidden if x in text]
    return {"pass":not hits,"hits":hits,"rule":"candidate may enumerate at most 2^3 local support points; no full live-boundary cube and no general SAT oracle"}
def main():
    c=controls(); r=random_exact(); l=ladder(); g=guard(); ok=all(x["pass"] for x in c.values()) and r["passed"]==r["total"] and all(x["pass"] for x in l) and g["pass"]
    verdict="PASS_TYPED_AFFINE_OPEN_MESSAGE__PARITY_BARRIER_COLLAPSES_TO_ONE_GF2_ROW__GENERAL_3CNF_OPEN" if ok else "FALSIFIED_TYPED_AFFINE_OPEN_MESSAGE"
    print(json.dumps({"schema":"JANUS_TRUMP_TYPED_AFFINE_OPEN_BOUNDARY_MESSAGE_GATE_V1","verdict":verdict,"controls":c,"random_exactness":r,"parity_ladder":l,"captain_obvious_guard":g,"interpretation":"The auxiliary-free CNF parity projection barrier is representation-specific: parity-chain open-boundary semantics are polynomially succinct in a typed GF(2) message.","limitation":"Only CNFs whose every support bundle is an exact affine coset are admitted; arbitrary mixed 3-CF remains unresolved.","next":"integrate typed message languages and attack affine/non-affine interactions without reifying eliminated branch choices.","scientific_status":{"SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN","Pi_negative_evidence_weight":0}},sort_keys=True))
if __name__=="__main__": main()
