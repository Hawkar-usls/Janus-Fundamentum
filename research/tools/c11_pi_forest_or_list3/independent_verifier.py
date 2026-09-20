#!/usr/bin/env python3
import argparse,itertools,json,pathlib
COL={1,2,3,4}
def e(a,b):return tuple(sorted((a,b)))
def adj(E,a,b):return e(a,b) in E
def connected(V,E):
  V=set(V)
  if not V:return True
  seen=set();st=[next(iter(V))]
  while st:
    v=st.pop()
    if v in seen:continue
    seen.add(v);st.extend([u for u in V-seen if adj(E,v,u)])
  return seen==V
def p7(V,E):
  for S in itertools.combinations(V,7):
    SS=set(S);sub={x for x in E if x[0] in SS and x[1] in SS}
    if len(sub)!=6:continue
    deg={v:0 for v in S}
    for a,b in sub:deg[a]+=1;deg[b]+=1
    if sorted(deg.values())==[1,1,2,2,2,2,2] and connected(S,sub):return list(S)
  return None
def forest(V,E):
  V=set(V);sub={x for x in E if x[0] in V and x[1] in V}
  # count components
  rem=set(V);cc=0
  while rem:
    cc+=1;st=[next(iter(rem))];C=set()
    while st:
      v=st.pop()
      if v in C:continue
      C.add(v);st.extend([u for u in rem-C if adj(sub,v,u)])
    rem-=C
  return len(sub)==len(V)-cc
def cycle_edges(seq,E):
  return len(seq)>=4 and seq[0]==seq[-1] and len(set(seq[:-1]))==len(seq)-1 and all(adj(E,seq[i],seq[i+1]) for i in range(len(seq)-1))
def main():
  ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
  c=json.load(open(a.candidate));fr=json.load(open(a.freeze));W=fr["first_authoritative_T2_candidate"]
  V=W["vertices"];E={e(x,y) for x,y in W["exact_edges"]}
  checks={}
  checks["primary"]=c["primary_outcome"]=="T2_CYCLIC_FOUR_COLOR_RESIDUAL"
  checks["P7_free"]=p7(V,E) is None
  auth=c["authority_checks"]
  checks["old_axioms"]=all(auth["old_axioms"].values())
  checks["stored_Q"]=all(auth["stored_111_Q"].values())
  checks["post_axioms"]=all(auth["post_axioms"].values())
  checks["post_lists"]=all(auth["post_lists"].values())
  checks["answer_provenance"]=all(auth["answer_relevance_certificate"].values())
  cyc=[x for x in c["route34"]["components"] if x["classification"]=="CYCLIC_FULL_FOUR_COLOR_RESIDUAL"]
  checks["one_cyclic"]=len(cyc)>=1
  if cyc:
    C=cyc[0]
    checks["union4"]=C["union_of_lists"]==[1,2,3,4] and C["missing_colors"]==[]
    checks["connected"]=connected(C["vertices"],E)
    checks["not_forest"]=not forest(C["vertices"],E)
    checks["cycle_certificate"]=C["cycle"] is not None and cycle_edges(C["cycle"],E)
    checks["exact_C4"]=set(C["vertices"])=={"a0","a1","b2","b3"} and len(C["edges"])==4
  else:
    checks["union4"]=checks["connected"]=checks["not_forest"]=checks["cycle_certificate"]=checks["exact_C4"]=False
  fc=c["forest_positive_control"]
  checks["forest_control"]=fc["pass"] is True and fc["classification"]["classification"]=="FOREST_LIST_READY" and fc["solver"]["status"]=="COLORABLE"
  checks["forest_reconstruction"]=len(fc["solver"].get("solution",{}))==4
  cc=c["cyclic_classifier_control"]
  checks["cycle_control"]=cc["pass"] is True and cc["classification"]["cycle"] is not None
  checks["minimization"]=c["minimization"]["vertex_minimal_under_induced_deletion_for_exact_decorated_C"] is True and c["minimization"]["global_minimality_claimed"] is False
  checks["no_forbidden_tools"]=all(v is False for v in c["oracle_use"].values())
  checks["ceiling"]=c["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED" and c["scientific_ceiling"]["P_VS_NP"]=="OPEN"
  checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
  verdict="INDEPENDENT_T2_CYCLIC_FULL_FOUR_COLOR_RESIDUAL_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
  out={"schema":"janus.trump.c11_pi_forest_or_list3.independent.v1","verdict":verdict,"checks":checks,"scientific_ceiling":c["scientific_ceiling"]}
  pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
  print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v]},sort_keys=True))
  if verdict!="INDEPENDENT_T2_CYCLIC_FULL_FOUR_COLOR_RESIDUAL_VERIFIED":raise SystemExit(1)
if __name__=="__main__":main()
