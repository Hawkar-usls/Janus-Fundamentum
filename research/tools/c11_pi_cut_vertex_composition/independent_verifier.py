#!/usr/bin/env python3
import argparse,itertools,json,pathlib
def e(a,b):return tuple(sorted((a,b)))
def es(E):return {e(a,b) for a,b in E}
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
def comps(V,E):
  V=set(V);out=[]
  while V:
    s=next(iter(V));C=set();st=[s]
    while st:
      v=st.pop()
      if v in C:continue
      C.add(v);st.extend([u for u in V-C if adj(E,v,u)])
    V-=C;out.append(C)
  return out
def cuts(V,E):
  V=list(V);return sorted([r for r in V if len(comps([v for v in V if v!=r],E))>1])
def p7(V,E):
  for S in itertools.combinations(V,7):
    SS=set(S);sub={x for x in E if x[0] in SS and x[1] in SS}
    if len(sub)!=6:continue
    deg={v:0 for v in S}
    for a,b in sub:deg[a]+=1;deg[b]+=1
    if sorted(deg.values())==[1,1,2,2,2,2,2] and connected(S,sub):return list(S)
  return None
def literal_oct(S,E):
  S=sorted(S)
  if len(S)!=6:return False
  non=[e(a,b) for a,b in itertools.combinations(S,2) if not adj(E,a,b)]
  return len(non)==3 and len({x for p in non for x in p})==6 and sum(adj(E,a,b) for a,b in itertools.combinations(S,2))==12
def find_oct(V,E):
  return next((list(S) for S in itertools.combinations(sorted(V),6) if literal_oct(S,E)),None)
def main():
  ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
  c=json.load(open(a.candidate));fr=json.load(open(a.freeze));W=fr["first_authoritative_strong_S2_candidate"]
  V=W["vertices"];E=es(W["exact_edges"]);checks={}
  checks["primary"]=c["primary_outcome"]=="S2_CUT_VERTEX_COMPOSITION_ESCAPE_PATH_A"
  checks["P7_free"]=p7(V,E) is None
  checks["authority_axioms"]=all(c["authority_checks"]["old_axioms"].values()) and all(c["authority_checks"]["stored_111_Q"].values()) and all(c["authority_checks"]["post_axioms"].values()) and all(c["authority_checks"]["post_lists"].values())
  checks["answer_provenance"]=all(c["authority_checks"]["answer_relevance_certificate"].values())
  R=c["route34"]["residual"];RV=R["vertices"]
  cv=cuts(RV,E)
  checks["cut_set_empty"]=cv==[] and c["cut_vertex_audit"]["Cut_C"]==[]
  checks["connected"]=connected(RV,E) and len(RV)>=3
  checks["domain_no_missing"]=R["missing_colors"]==[] and c["domain_checks"]["NOT_L3_READY"] is True
  checks["not_exact_oct"]=len(RV)!=6 and c["domain_checks"]["not_exact_literal_octahedron"] is True
  checks["tw_gt3_literal_oct"]=find_oct(RV,E) is not None and c["tw_gt_3_certificate"]["selected_forbidden_minor"]=="OCTAHEDRON"
  checks["positive_control"]=c["positive_current_strong_O2_control"]["pass"] is True and c["positive_current_strong_O2_control"]["GOOD_cut_C"] is True and c["positive_current_strong_O2_control"]["S2"] is False
  checks["mixed_control"]=c["quantifier_controls"]["TWO_CUT_MIXED_CONTROL"]["pass"] is True and c["quantifier_controls"]["TWO_CUT_MIXED_CONTROL"]["GOOD_cut_C"] is True and c["quantifier_controls"]["TWO_CUT_MIXED_CONTROL"]["S2"] is False
  checks["no_cut_control"]=c["quantifier_controls"]["NO_CUT_CONTROL"]["pass"] is True and c["quantifier_controls"]["NO_CUT_CONTROL"]["path_A_recognized"] is True
  checks["no_forbidden_tools"]=all(v is False for v in c["oracle_use"].values())
  checks["ceiling"]=c["scientific_ceiling"]["TW4"]=="NOT_OPENED" and c["scientific_ceiling"]["SEPARATOR_SIZE_2"]=="NOT_OPENED" and c["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED" and c["scientific_ceiling"]["P_VS_NP"]=="OPEN"
  checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
  verdict="INDEPENDENT_S2_CUT_VERTEX_FREE_AUTHORITATIVE_RESIDUAL_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
  out={"schema":"janus.trump.c11_pi_cut_vertex_composition.independent.v1","verdict":verdict,"checks":checks,"recomputed_Cut_C":cv,"scientific_ceiling":c["scientific_ceiling"]}
  pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
  print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v],"Cut_C":cv},sort_keys=True))
  if verdict!="INDEPENDENT_S2_CUT_VERTEX_FREE_AUTHORITATIVE_RESIDUAL_VERIFIED":raise SystemExit(1)
if __name__=="__main__":main()
