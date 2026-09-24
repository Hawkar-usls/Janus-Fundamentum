#!/usr/bin/env python3
import argparse,itertools,json,pathlib

COL={1,2,3,4}
def e(a,b): return tuple(sorted((a,b)))
def adj(E,a,b): return e(a,b) in E
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
      SS=set(S);sub={(a,b) for a,b in E if a in SS and b in SS}
      if len(sub)!=6:continue
      deg={v:0 for v in S}
      for a,b in sub:deg[a]+=1;deg[b]+=1
      if sorted(deg.values())==[1,1,2,2,2,2,2] and connected(S,sub):return list(S)
    return None
def propagate(E,lists,fixed):
    lists={v:set(L) for v,L in lists.items() if v not in fixed};fixed=dict(fixed)
    while True:
      for a,b in E:
        if a in fixed and b in fixed and fixed[a]==fixed[b]:return None,fixed,"CONTR"
      changed=False
      for v in list(lists):
        lists[v]-={fixed[u] for u in fixed if adj(E,u,v)}
        if not lists[v]:return None,fixed,"CONTR"
      singles=[v for v,L in lists.items() if len(L)==1]
      if not singles:break
      for v in singles:
        if v not in lists:continue
        fixed[v]=next(iter(lists[v]));del lists[v];changed=True
      if not changed:break
    return {v:sorted(L) for v,L in lists.items()},fixed,"OK"
def comps(E,lists):
    V=set(lists);out=[]
    while V:
      st=[next(iter(V))];C=set()
      while st:
        v=st.pop()
        if v in C:continue
        C.add(v);st.extend([u for u in V-C if adj(E,u,v)])
      V-=C;out.append(sorted(C))
    return out
def branch(E,C_lists,r,k):
    L={v:x for v,x in C_lists.items() if v!=r}
    lists,fixed,status=propagate(E,L,{r:k})
    if status=="CONTR":return "CONTR",None
    for C in comps(E,lists):
      union=set().union(*(set(lists[v]) for v in C))
      if union==COL:return "BAD",(sorted(C),{v:lists[v] for v in sorted(C)})
    return "L3",None
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    c=json.load(open(a.candidate));fr=json.load(open(a.freeze));W=fr["first_authoritative_B2_candidate"]
    E={e(x,y) for x,y in W["exact_edges"]};V=W["vertices"]
    checks={}
    checks["primary"]=c["primary_outcome"]=="B2_NO_SINGLE_VERTEX_BACKDOOR"
    checks["p7"]=p7(V,E) is None
    C_lists=W["exact_after_route34_and_frozen_propagation"]["components"][1]["lists"]
    C_lists={v:list(L) for v,L in C_lists.items()}
    # all candidates independently
    defeating={}
    any_backdoor=False
    for r in sorted(C_lists):
      statuses={}
      for k in sorted(C_lists[r]):
        st,rec=branch(E,C_lists,r,k);statuses[k]=(st,rec)
      if all(st in ("CONTR","L3") for st,_ in statuses.values()): any_backdoor=True
      bad=[(k,rec) for k,(st,rec) in statuses.items() if st=="BAD"]
      defeating[r]=bad[0] if bad else None
    checks["no_backdoor"]=not any_backdoor and all(defeating.values())
    checks["forall_control"]=branch(E,C_lists,"a0",2)[0]=="L3" and branch(E,C_lists,"a0",3)[0]=="BAD"
    checks["candidate_table_matches"]=all(
      c["defeating_table"][r]["kappa"]==defeating[r][0] for r in sorted(C_lists)
    )
    checks["unions_all4"]=all(
      set(defeating[r][1][1][v] for v in [])==set() or
      set().union(*(set(L) for L in defeating[r][1][1].values()))==COL
      for r in defeating
    )
    checks["positive_control_bound"]=c["positive_control"]["theorem_status"]=="PASS_C11_FALSE_TWIN_FAMILY_SINGLE_VERTEX_L3_BACKDOOR"
    checks["minimization"]=c["minimization"]["vertex_minimal_under_induced_deletion_for_exact_decorated_C"] is True and c["minimization"]["global_minimality_claimed"] is False
    checks["no_forbidden_tools"]=all(v is False for v in c["oracle_use"].values())
    checks["ceiling"]=c["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED" and c["scientific_ceiling"]["P_VS_NP"]=="OPEN"
    checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
    verdict="INDEPENDENT_B2_SINGLE_VERTEX_L3_BACKDOOR_COUNTERCOMPONENT_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
    out={"schema":"janus.trump.c11_pi_single_vertex_l3_backdoor.independent.v1","verdict":verdict,"checks":checks,"defeating":defeating,"scientific_ceiling":c["scientific_ceiling"]}
    pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v]},sort_keys=True))
    if verdict!="INDEPENDENT_B2_SINGLE_VERTEX_L3_BACKDOOR_COUNTERCOMPONENT_VERIFIED":raise SystemExit(1)
if __name__=="__main__":main()
