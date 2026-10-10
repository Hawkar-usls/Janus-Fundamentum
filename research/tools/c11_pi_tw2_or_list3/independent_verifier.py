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
def verify_model(C,E,M):
  sets=[set(M[k]) for k in ["B1","B2","B3","B4"]]
  ch={}
  ch["nonempty"]=all(sets)
  ch["disjoint"]=all(not(A&B) for A,B in itertools.combinations(sets,2))
  ch["inside"]=all(s<=set(C) for s in sets)
  ch["connected"]=all(connected(s,{x for x in E if x[0] in s and x[1] in s}) for s in sets)
  cross={}
  ok=True
  for i,j in itertools.combinations(range(4),2):
    xs=[x for x in E if (x[0] in sets[i] and x[1] in sets[j]) or (x[1] in sets[i] and x[0] in sets[j])]
    cross[f"{i+1}-{j+1}"]=list(xs[0]) if xs else None
    if not xs:ok=False
  ch["six_cross"]=ok
  return ch,cross
def main():
  ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
  c=json.load(open(a.candidate));fr=json.load(open(a.freeze));W=fr["first_authoritative_W2_candidate"]
  V=W["vertices"];E={e(x,y) for x,y in W["exact_edges"]};checks={}
  checks["primary"]=c["primary_outcome"]=="W2_K4_MINOR_FOUR_COLOR_RESIDUAL"
  checks["P7_free"]=p7(V,E) is None
  auth=c["authority_checks"]
  checks["old_axioms"]=all(auth["old_axioms"].values())
  checks["stored_Q"]=all(auth["stored_111_Q"].values())
  checks["post_axioms"]=all(auth["post_axioms"].values())
  checks["post_lists"]=all(auth["post_lists"].values())
  checks["provenance"]=all(auth["answer_relevance_provenance"].values())
  W2=c["W2"];C=W2["component"]
  checks["component_exact"]=set(C["vertices"])=={"a0","a1","b2","b3"} and len(C["edges"])==6
  checks["union4"]=C["union_of_lists"]==[1,2,3,4] and C["missing_colors"]==[]
  mch,cross=verify_model(C["vertices"],E,W2["K4_minor_model"])
  checks["K4_model"]=all(mch.values()) and len([v for v in cross.values() if v])==6
  pc=c["positive_TW2_C4_control"]
  checks["C4_positive"]=pc["pass"] is True and all(pc["td_checks"].values()) and pc["solver"]["status"]=="COLORABLE" and pc["solver"]["proper"] is True and pc["K4_minor_absent"] is True
  nc=c["negative_K4_classifier_control"]
  checks["K4_negative_control"]=nc["pass"] is True and all(nc["checks"].values())
  checks["minimization"]=c["minimization"]["vertex_minimal_under_induced_deletion_for_exact_decorated_C"] is True and c["minimization"]["global_minimality_claimed"] is False
  checks["no_forbidden_tools"]=all(v is False for v in c["oracle_use"].values())
  checks["ceiling"]=c["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED" and c["scientific_ceiling"]["UNBOUNDED_TREEWIDTH"]=="NOT_CLAIMED" and c["scientific_ceiling"]["P_VS_NP"]=="OPEN"
  checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
  verdict="INDEPENDENT_W2_K4_MINOR_FOUR_COLOR_RESIDUAL_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
  out={"schema":"janus.trump.c11_pi_tw2_or_list3.independent.v1","verdict":verdict,"checks":checks,"recomputed_cross_edges":cross,"scientific_ceiling":c["scientific_ceiling"]}
  pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
  print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v]},sort_keys=True))
  if verdict!="INDEPENDENT_W2_K4_MINOR_FOUR_COLOR_RESIDUAL_VERIFIED":raise SystemExit(1)
if __name__=="__main__":main()
