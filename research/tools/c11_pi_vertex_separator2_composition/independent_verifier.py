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
    seen.add(v)
    for a,b in E:
      if a==v and b in V-seen:st.append(b)
      elif b==v and a in V-seen:st.append(a)
  return seen==V
def comps(V,E):
  V=set(V);out=[]
  while V:
    s=next(iter(V));C=set();st=[s]
    while st:
      v=st.pop()
      if v in C:continue
      C.add(v)
      for a,b in E:
        if a==v and b in V-C:st.append(b)
        elif b==v and a in V-C:st.append(a)
    V-=C;out.append(C)
  return out
def cuts(V,E):return sorted([r for r in V if len(comps([v for v in V if v!=r],E))>1])
def sep2(V,E):
  out=[]
  for a,b in itertools.combinations(sorted(V),2):
    if len(comps([v for v in V if v not in {a,b}],E))>1:out.append([a,b])
  return out
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
  c=json.load(open(a.candidate));fr=json.load(open(a.freeze));W=fr["first_authoritative_strong_R2_candidate"]
  V=W["vertices"];E=es(W["exact_edges"]);R=c["route34"]["residual"];RV=R["vertices"];checks={}
  cv=cuts(RV,E);s2=sep2(RV,E)
  checks["primary"]=c["primary_outcome"]=="R2_SEPARATOR2_COMPOSITION_ESCAPE_PATH_A"
  checks["P7_free"]=p7(V,E) is None
  checks["authority_axioms"]=all(c["authority_checks"]["old_axioms"].values()) and all(c["authority_checks"]["stored_111_Q"].values()) and all(c["authority_checks"]["post_axioms"].values()) and all(c["authority_checks"]["post_lists"].values())
  checks["answer_provenance"]=all(c["authority_checks"]["answer_relevance_certificate"].values())
  checks["connected"]=connected(RV,E) and len(RV)>4
  checks["domain_no_missing"]=R["missing_colors"]==[] and c["domain_checks"]["NOT_L3_READY"] is True
  checks["not_exact_oct"]=len(RV)!=6 and c["domain_checks"]["not_exact_literal_octahedron"] is True
  checks["tw_gt3_literal_oct"]=find_oct(RV,E) is not None and c["tw_gt_3_certificate"]["selected_forbidden_minor"]=="OCTAHEDRON"
  checks["Cut_empty"]=cv==[] and c["connectivity_audit"]["Cut_C"]==[]
  checks["Sep2_empty"]=s2==[] and c["connectivity_audit"]["Sep_2_C"]==[]
  checks["kappa_claim_only_lower_bound"]=c["connectivity_audit"]["kappa_lower_bound"]==3 and c["connectivity_audit"]["kappa_equality_claimed"] is False and c["scientific_ceiling"]["CONNECTIVITY_CLAIM"]=="KAPPA_GE_3_ONLY"
  checks["positive_control"]=c["positive_current_S2_control"]["pass"] is True and c["positive_current_S2_control"]["kappa_exactly_2"] is True and c["positive_current_S2_control"]["GOOD_2_C"] is True
  checks["mixed_control"]=c["quantifier_controls"]["TWO_SEPARATOR_MIXED_CONTROL"]["pass"] is True and c["quantifier_controls"]["TWO_SEPARATOR_MIXED_CONTROL"]["GOOD_2_C"] is True
  checks["empty_control"]=c["quantifier_controls"]["EMPTY_SEPARATOR_STATE_CONTROL"]["pass"] is True and c["quantifier_controls"]["EMPTY_SEPARATOR_STATE_CONTROL"]["GOOD_2_separator"] is True
  checks["no_sep_control"]=c["quantifier_controls"]["NO_SEPARATOR2_CONTROL"]["pass"] is True and c["quantifier_controls"]["NO_SEPARATOR2_CONTROL"]["path_A_recognized"] is True
  checks["no_forbidden_tools"]=all(v is False for v in c["oracle_use"].values())
  checks["ceiling"]=c["scientific_ceiling"]["SEPARATOR_SIZE_3"]=="NOT_OPENED" and c["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and c["scientific_ceiling"]["TW4"]=="NOT_OPENED" and c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED" and c["scientific_ceiling"]["P_VS_NP"]=="OPEN"
  checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
  verdict="INDEPENDENT_R2_KAPPA_GE3_AUTHORITATIVE_RESIDUAL_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
  out={"schema":"janus.trump.c11_pi_vertex_separator2_composition.independent.v1","verdict":verdict,"checks":checks,
       "recomputed_Cut_C":cv,"recomputed_Sep_2_C":s2,"scientific_ceiling":c["scientific_ceiling"]}
  pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
  print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v],"Cut_C":cv,"Sep_2_C":s2},sort_keys=True))
  if verdict!="INDEPENDENT_R2_KAPPA_GE3_AUTHORITATIVE_RESIDUAL_VERIFIED":raise SystemExit(1)
if __name__=="__main__":main()
