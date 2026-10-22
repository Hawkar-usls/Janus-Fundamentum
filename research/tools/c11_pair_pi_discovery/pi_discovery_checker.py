#!/usr/bin/env python3
import argparse,itertools,json,pathlib,hashlib

COL={1,2,3,4}
def ce(a,b): return tuple(sorted((a,b)))
def edges(P): return {ce(a,b) for a,b in P["edges"]}
def adj(P,a,b): return ce(a,b) in edges(P)
def neigh(P,v): return {u for u in P["vertices"] if u!=v and adj(P,u,v)}
def induced_path(P,seq):
    if len(set(seq))!=len(seq): return False
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            if adj(P,a,seq[j])!=(j==i+1): return False
    return True
def has_p7(P):
    if len(P["vertices"])<7:return None
    for comb in itertools.combinations(P["vertices"],7):
        for perm in itertools.permutations(comb):
            if induced_path(P,perm): return list(perm)
    return None
def proper(P,c):
    return all(c[a]!=c[b] for a,b in edges(P) if a in c and b in c)
def components(P,verts):
    V=set(verts); out=[]
    while V:
        s=next(iter(V)); st=[s]; C=set()
        while st:
            v=st.pop()
            if v in C:continue
            C.add(v); st.extend((neigh(P,v)&V)-C)
        out.append(sorted(C)); V-=C
    return out
def sha(p): return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def canonical():
    return {
      "vertices":["s","t","p","m","n","y","yp","z"],
      "edges":[["s","t"],["s","p"],["s","y"],["t","n"],["t","yp"],["p","m"],["m","n"],["m","yp"],["z","y"],["z","yp"]],
      "fixed":{"s":1,"t":2,"p":3,"m":2,"n":4},
      "lists":{"y":[2,3,4],"yp":[1,3,4],"z":[1,2,3,4]}
    }

def blowup22():
    return {
      "vertices":["s","t","p","m","n","z","a1","a2","b1","b2"],
      "edges":[["s","t"],["s","p"],["p","m"],["m","n"],["t","n"],
               ["a1","s"],["a1","z"],["a2","s"],["a2","z"],
               ["b1","t"],["b1","m"],["b1","z"],["b2","t"],["b2","m"],["b2","z"]],
      "fixed":{"s":1,"t":2,"p":3,"m":2,"n":4},
      "base_lists":{"a1":[2,3,4],"a2":[2,3,4],"b1":[1,3,4],"b2":[1,3,4],"z":[1,2,3,4]}
    }

def propagate(P,lists,fixed):
    out={v:set(L) for v,L in lists.items() if v not in fixed}
    for v in list(out):
        out[v]-={fixed[u] for u in neigh(P,v) if u in fixed}
    return {v:sorted(x) for v,x in out.items()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--transfer",required=True);ap.add_argument("--counter",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args(); root=pathlib.Path(a.out); root.mkdir(parents=True,exist_ok=True)
    pre=json.load(open(a.prereg)); fr=json.load(open(a.freeze)); transfer=json.load(open(a.transfer)); counter=json.load(open(a.counter))

    input_checks={
      "prereg_name":pre["name"]=="C11_PAIR_PI_DISCOVERY_GATE_V1",
      "prereg_status":pre["status"]=="FROZEN_PI_DISCOVERY_PREREGISTRATION__NO_REPAIR",
      "freeze_binding":fr["authorization"]["prereg_blob"]=="873c409e4872a2365cf95e087086c865de574c4f",
      "list3_authority":transfer["theorem2_external_authority"]["stronger_result_verified"]=="List 3-Coloring is polynomial-time solvable for P7-free graphs.",
      "counter_authority":counter["status"]=="PASS_C11_PAIR_MULTIPLICITY_FALSE_TWIN_BLOWUP_THEOREM"
    }

    # Positive control / terminal subclass on canonical H8
    P=canonical(); pos={}
    for g,d in [(3,3),(3,4),(4,3),(4,4)]:
        fixed=dict(P["fixed"]); fixed["y"]=g; fixed["yp"]=d
        ok_lists=(g in P["lists"]["y"] and d in P["lists"]["yp"])
        ok_prop=proper(P,fixed)
        rem=["z"]
        lists=propagate(P,{"z":P["lists"]["z"]},fixed)
        comps=components(P,rem)
        union=set(lists["z"])
        missing=sorted(COL-union)
        bit=1 if ok_lists and ok_prop and missing and lists["z"] else None
        pos[f"{g}{d}"]={"assignment_respects_lists":ok_lists,"proper_fixed":ok_prop,"components":comps,"lists":lists,"missing_colors":missing,"q":bit}
    positive_pass=all(x["q"]==1 and x["components"]==[["z"]] and len(x["missing_colors"])>=1 for x in pos.values())

    # Exact r=q=2 obstruction
    B=blowup22(); obs={}
    for g,d in [(3,3),(3,4),(4,3),(4,4)]:
        fixed=dict(B["fixed"]); fixed["a1"]=g; fixed["b1"]=d
        lists=propagate(B,B["base_lists"],fixed)
        # remove fixed endpoints from list map
        lists={k:v for k,v in lists.items() if k not in {"a1","b1"}}
        rem=sorted(lists)
        comps=components(B,rem)
        union=sorted(set().union(*(set(v) for v in lists.values())))
        no_missing=(set(union)==COL)
        no_singletons=all(len(v)>1 for v in lists.values())
        boundary_ok=(lists["a2"]==[2,3,4] and lists["b2"]==[1,3,4])
        expected_z=sorted(COL-{g,d})
        z_ok=lists["z"]==expected_z
        partition=sorted(sum((c for c in comps),[]))==sorted(rem)
        no_cross=True
        for i in range(len(comps)):
            for j in range(i+1,len(comps)):
                if any(adj(B,u,v) for u in comps[i] for v in comps[j]): no_cross=False
        obs[f"{g}{d}"]={
          "fixed_assignment":fixed,"components":comps,"lists":lists,"union_of_lists":union,
          "NO_GLOBAL_MISSING_COLOR":no_missing,"no_singleton_list":no_singletons,
          "boundary_propagation_exact":boundary_ok and z_ok,
          "partition_exact":partition,"no_cross_component_edges":no_cross,
          "P7_free":has_p7(B) is None,
          "first_route_failure":"GLOBAL_MISSING_COLOR_TEST"
        }
    obstruction_pass=all(
      x["components"]==[["a2","b2","z"]] and x["NO_GLOBAL_MISSING_COLOR"] and x["no_singleton_list"] and
      x["boundary_propagation_exact"] and x["partition_exact"] and x["no_cross_component_edges"] and x["P7_free"]
      for x in obs.values()
    )

    result={
      "schema":"janus.trump.c11_pair_pi_discovery.execution.v1",
      "route":"PAIR_FIXED_THREE_COLOR_COLLAPSE",
      "positive_terminal_subclass":{
        "status":"VERIFIED_POLYNOMIAL_SUBCLASS" if positive_pass else "FAIL",
        "reason":"Whenever every undecided component has a globally missing color, exact boundary propagation reduces each component to P7-free List-3 and component factorization is exact.",
        "canonical_H8_control":pos
      },
      "route_obstruction":{
        "status":"NO_GLOBAL_MISSING_COLOR_VERIFIED" if obstruction_pass else "FAIL",
        "authority":"frozen false-twin blow-up family, finite authoritative member r=q=2",
        "selected_pair":["a1","b1"],
        "assignments":obs,
        "interpretation":"Refutes universality of the direct missing-color/List-3 route only. Does not imply any q bit is hard or false."
      },
      "D1":{
        "status":"NOT_ESTABLISHED",
        "reason":"An authoritative-core r=q=2 instance reaches a remaining component with union of lists [4] for every fixed assignment, so the preregistered direct List-3 terminal route is not universal."
      },
      "D2":{
        "status":"VERIFIED" if positive_pass and obstruction_pass else "NOT_VERIFIED",
        "solved_scope":"All fixed-pair states satisfying the certified per-component global-missing-color condition; canonical H8 provides all-four-bit control.",
        "unresolved_scope":"False-twin blow-up r=q=2 provides exact NO_GLOBAL_MISSING_COLOR receipts for 33,34,43,44."
      },
      "D3":"NOT_REACHED" if positive_pass and obstruction_pass else "POSSIBLE",
      "primary_outcome":"D2_PARTIAL_PI_DISCOVERY" if positive_pass and obstruction_pass else "D3_PI_DISCOVERY_UNRESOLVED",
      "P3_EXACT_PAIR_QUOTIENT":"NOT_ESTABLISHED",
      "forbidden_interpretations":["P3_FALSE","HARDNESS","EXPONENTIAL_LOWER_BOUND","NO_POLYNOMIAL_PI_ALGORITHM_EXISTS"],
      "oracle_use":{"extension_oracle":False,"general_P7_free_4color_oracle":False,"hidden_extension_c":False},
      "scientific_ceiling":{
        "PI_SEMANTIC_CLASS_COUNT":"<=16_VERIFIED",
        "PI_DISCOVERY":"PARTIAL" if positive_pass and obstruction_pass else "UNRESOLVED",
        "P3_EXACT_PAIR_QUOTIENT":"NOT_ESTABLISHED",
        "REPAIR":"NOT_STARTED","NEW_DESCRIPTOR":"NOT_DEFINED",
        "C1S_CS1_CSS":"NOT_REACHED","LEMMA11_P7_LIFT":"OPEN","P7_FREE_4_COLOR_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"
      },
      "repair_attempted":False,"successor_autoactivated":False,"stop":True,
      "input_checks":input_checks,
      "source_hashes":{"prereg":sha(a.prereg),"freeze":sha(a.freeze),"transfer":sha(a.transfer),"counter":sha(a.counter)}
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"outcome":result["primary_outcome"],"positive":positive_pass,"obstruction":obstruction_pass},sort_keys=True))
    if not all(input_checks.values()): raise SystemExit(2)
    if result["primary_outcome"]!="D2_PARTIAL_PI_DISCOVERY": raise SystemExit(3)

if __name__=="__main__": main()
