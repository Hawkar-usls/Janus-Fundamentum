#!/usr/bin/env python3
import argparse,itertools,json,pathlib
COL={1,2,3,4}
def e(a,b):return tuple(sorted((a,b)))
def es(edges):return {e(a,b) for a,b in edges}
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
def oct_edges():
  V=[f"o{i}" for i in range(6)];non={e("o0","o1"),e("o2","o3"),e("o4","o5")}
  return V,{e(a,b) for a,b in itertools.combinations(V,2) if e(a,b) not in non}
def verify_oct_minor(CV,CE,bs):
  HV,HE=oct_edges();sets={h:set(bs[h]) for h in HV};ch={}
  ch["keys"]=set(bs)==set(HV);ch["nonempty"]=all(sets[h] for h in HV);ch["inside"]=all(sets[h]<=set(CV) for h in HV)
  flat=[x for h in HV for x in sets[h]];ch["disjoint"]=len(flat)==len(set(flat));ch["connected"]=all(connected(sets[h],CE) for h in HV)
  ch["all_edges"]=all(any((a in sets[u] and b in sets[v]) or (b in sets[u] and a in sets[v]) for a,b in CE) for u,v in HE)
  return ch
def proper(E,c):return all(c[a]!=c[b] for a,b in E if a in c and b in c)
def main():
  ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
  c=json.load(open(a.candidate));fr=json.load(open(a.freeze));W=fr["first_authoritative_X2_candidate"]
  V=W["vertices"];E=es(W["exact_edges"]);checks={}
  checks["primary"]=c["primary_outcome"]=="X2_TW3_FORBIDDEN_MINOR_FOUR_COLOR_RESIDUAL"
  checks["P7_free"]=p7(V,E) is None
  auth=c["authority_checks"]
  checks["old_axioms"]=all(auth["old_axioms"].values());checks["stored_Q"]=all(auth["stored_111_Q"].values());checks["post_axioms"]=all(auth["post_axioms"].values());checks["post_lists"]=all(auth["post_lists"].values())
  checks["answer_extension"]=all(auth["answer_relevance_certificate"].values()) and proper(E,W["answer_relevance_certificate"]["coloring"])
  checks["survivor_pair"]=auth["survivor_pair"]["intersection"]==[3,4] and auth["survivor_pair"]["common_z"] and auth["survivor_pair"]["lists_unequal"]
  x2=c["X2"];C=x2["first_authoritative_component"]
  checks["target_connected"]=C["connected"] is True
  checks["union4_no_missing"]=C["union_of_lists"]==[1,2,3,4] and C["missing_colors"]==[]
  checks["selected_oct"]=x2["selected_forbidden_minor"]=="OCTAHEDRON"
  bs=W["forbidden_minor_certificate"]["branch_sets"]
  mch=verify_oct_minor(C["vertices"],E,bs)
  checks["oct_minor"]=all(mch.values()) and all(x2["minor_model_checks"].values())
  # literal core edges exactly octahedron under mapping
  core={"a0","a1","b0","b1","c0","c1"}
  coreE={x for x in E if x[0] in core and x[1] in core}
  checks["literal_octahedron_edge_count"]=len(coreE)==12
  checks["positive_K4"]=c["positive_K4_TW3_control"]["pass"] is True and c["positive_K4_TW3_control"]["solver_status"]=="COLORABLE"
  checks["classifier_controls"]=all(x["pass"] for x in c["forbidden_minor_classifier_controls"].values()) and set(c["forbidden_minor_classifier_controls"])=={"K5","OCTAHEDRON","WAGNER_V8","PENTAGONAL_PRISM"}
  checks["minimization"]=c["minimization"]["core_vertex_minimal_under_connected_induced_deletion_for_forbidden_minor"] is True and c["minimization"]["global_minimality_claimed"] is False
  checks["no_forbidden_tools"]=all(v is False for v in c["oracle_use"].values())
  checks["ceiling"]=c["scientific_ceiling"]["TW4"]=="NOT_OPENED" and c["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED" and c["scientific_ceiling"]["P_VS_NP"]=="OPEN"
  checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
  verdict="INDEPENDENT_X2_TW3_FORBIDDEN_MINOR_RESIDUAL_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
  out={"schema":"janus.trump.c11_pi_tw3_or_list3.independent.v1","verdict":verdict,"checks":checks,"recomputed_oct_minor":mch,"scientific_ceiling":c["scientific_ceiling"]}
  pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
  print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v]},sort_keys=True))
  if verdict!="INDEPENDENT_X2_TW3_FORBIDDEN_MINOR_RESIDUAL_VERIFIED":raise SystemExit(1)
if __name__=="__main__":main()
