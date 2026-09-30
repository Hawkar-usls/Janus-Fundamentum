#!/usr/bin/env python3
import argparse,itertools,json,pathlib,hashlib

COL={1,2,3,4}
def ek(a,b): return tuple(sorted((a,b)))
def es(edges): return {ek(a,b) for a,b in edges}
def adj(E,a,b): return ek(a,b) in E

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
        V-=C;out.append(sorted(C))
    return sorted(out,key=lambda x:(len(x),x))

def p7_witness(V,E):
    for S in itertools.combinations(V,7):
        SS=set(S); sub={x for x in E if x[0] in SS and x[1] in SS}
        if len(sub)!=6:continue
        deg={v:0 for v in S}
        for a,b in sub:deg[a]+=1;deg[b]+=1
        if sorted(deg.values())==[1,1,2,2,2,2,2] and connected(S,sub):
            return list(S)
    return None

def seed_lists(V,E,S,f):
    out={}
    for v in V:
        if v in S:continue
        used={f[s] for s in S if adj(E,v,s)}
        out[v]=sorted(COL-used)
    return out

def verify_axioms(V,E,S,X0,X,Y0,Y,f):
    L=seed_lists(V,E,S,f);ch={}
    ch["graph_connected"]=connected(V,E)
    ch["seed_connected"]=connected(S,E)
    ch["no_outside_complete_to_seed"]=all(not all(adj(E,v,s) for s in S) for v in set(V)-set(S))
    exact_y0={v for v in V if v not in S and not any(adj(E,v,s) for s in S)}
    ch["Y0_exact"]=exact_y0==set(Y0)
    Y0E=[(a,b) for a,b in E if a in Y0 and b in Y0]
    ok=True
    for v in set(V)-set(Y0)-set(X0):
        for a,b in Y0E:
            if adj(E,v,a)!=adj(E,v,b):ok=False
    ch["no_mixed_on_Y0_edge"]=ok
    ch["Y0_four_lists"]=all(set(L[v])==COL for v in Y0)
    ch["Y_three_lists"]=all(len(L[v])==3 for v in Y)
    parts=list(map(set,[S,X0,X,Y0,Y]))
    ch["partition"]=set(V)==set().union(*parts) and all(not(A&B) for A,B in itertools.combinations(parts,2))
    return ch,L

def type_set(v,E,S): return sorted([s for s in S if adj(E,v,s)])
def proper(E,c): return all(not(a in c and b in c and c[a]==c[b]) for a,b in E)

def propagate(E,lists,fixed):
    lists={v:set(L) for v,L in lists.items() if v not in fixed};fixed=dict(fixed);prov=[]
    while True:
        for a,b in E:
            if a in fixed and b in fixed and fixed[a]==fixed[b]:
                return None,fixed,{"kind":"IMPROPER_FIXED_EDGE","edge":[a,b],"color":fixed[a],"provenance":prov}
        changed=False
        for v in list(lists):
            removed=sorted({fixed[u] for u in fixed if adj(E,u,v)} & lists[v])
            if removed:
                lists[v]-=set(removed);prov.append({"op":"REMOVE_FIXED_NEIGHBOR_COLORS","vertex":v,"removed":removed});changed=True
            if not lists[v]:
                return None,fixed,{"kind":"EMPTY_LIST","vertex":v,"provenance":prov}
        singles=sorted(v for v,L in lists.items() if len(L)==1)
        if singles:
            for v in singles:
                if v not in lists:continue
                c=next(iter(lists[v]));fixed[v]=c;del lists[v]
                prov.append({"op":"FIX_SINGLETON","vertex":v,"color":c});changed=True
            continue
        if not changed:break
    return {v:sorted(L) for v,L in lists.items()},fixed,{"kind":"FIXPOINT","provenance":prov}

def comp_record(C,E,lists):
    union=sorted(set().union(*(set(lists[v]) for v in C)))
    return {"vertices":sorted(C),
            "edges":sorted([list(x) for x in E if x[0] in C and x[1] in C]),
            "lists":{v:lists[v] for v in sorted(C)},
            "union_of_lists":union,
            "missing_colors":sorted(COL-set(union)),
            "connected":connected(C,E)}

def verify_td(V,E,bags,tree_edges,width):
    B={k:set(v) for k,v in bags.items()}; T=es(tree_edges)
    checks={}
    checks["bag_size"]=all(len(x)<=width+1 for x in B.values())
    checks["vertex_coverage"]=set(V)<=set().union(*B.values()) if B else not V
    checks["edge_coverage"]=all(any(a in bag and b in bag for bag in B.values()) for a,b in E if a in V and b in V)
    checks["bag_tree_connected"]=connected(B.keys(),T)
    checks["bag_tree_edge_count"]=len(T)==max(0,len(B)-1)
    ri=True
    for v in V:
        containing=[k for k,bag in B.items() if v in bag]
        if not containing or not connected(containing,{e for e in T if e[0] in containing and e[1] in containing}):ri=False
    checks["running_intersection"]=ri
    return checks

def brute_list_color(V,E,lists):
    V=list(V); sol={}
    def rec(i):
        if i==len(V):return dict(sol)
        v=V[i]
        for c in lists[v]:
            if all(not adj(E,v,u) or sol.get(u)!=c for u in sol):
                sol[v]=c
                r=rec(i+1)
                if r:return r
                del sol[v]
        return None
    return rec(0)

def forbidden_catalog():
    K5V=[f"k{i}" for i in range(5)]
    K5E=[(a,b) for a,b in itertools.combinations(K5V,2)]
    OV=[f"o{i}" for i in range(6)]
    non={ek("o0","o1"),ek("o2","o3"),ek("o4","o5")}
    OE=[(a,b) for a,b in itertools.combinations(OV,2) if ek(a,b) not in non]
    WV=[f"v{i}" for i in range(8)]
    WE=[(f"v{i}",f"v{(i+1)%8}") for i in range(8)]+[(f"v{i}",f"v{i+4}") for i in range(4)]
    PV=[f"p{i}" for i in range(5)]+[f"q{i}" for i in range(5)]
    PE=[(f"p{i}",f"p{(i+1)%5}") for i in range(5)]+[(f"q{i}",f"q{(i+1)%5}") for i in range(5)]+[(f"p{i}",f"q{i}") for i in range(5)]
    return {"K5":(K5V,es(K5E)),"OCTAHEDRON":(OV,es(OE)),"WAGNER_V8":(WV,es(WE)),"PENTAGONAL_PRISM":(PV,es(PE))}

def verify_minor_model(CV,CE,Hname,branch_sets,cross=None):
    HV,HE=forbidden_catalog()[Hname]
    checks={}
    checks["all_H_vertices_mapped"]=set(branch_sets)==set(HV)
    sets={h:set(branch_sets[h]) for h in HV}
    checks["nonempty"]=all(sets[h] for h in HV)
    checks["inside_component"]=all(sets[h]<=set(CV) for h in HV)
    flat=[x for h in HV for x in sets[h]]
    checks["pairwise_disjoint"]=len(flat)==len(set(flat))
    checks["connected_branch_sets"]=all(connected(sets[h],CE) for h in HV)
    edge_witnesses={}
    alladj=True
    for u,v in sorted(HE):
        witnesses=[list(e) for e in CE if (e[0] in sets[u] and e[1] in sets[v]) or (e[1] in sets[u] and e[0] in sets[v])]
        if not witnesses:alladj=False
        edge_witnesses[f"{u}-{v}"]=witnesses[0] if witnesses else None
    checks["all_H_edges_realized"]=alladj
    if cross is not None:
        normalized={k:sorted(v) for k,v in cross.items()}
        checks["frozen_cross_receipt_consistent"]=all(
            sorted(edge_witnesses[k])==normalized[k] for k in normalized
        ) and len(normalized)==len(HE)
    return checks,edge_witnesses

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--tw3-terminal",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();root=pathlib.Path(a.out);root.mkdir(parents=True,exist_ok=True)
    pre=json.load(open(a.prereg));fr=json.load(open(a.freeze));tw3=json.load(open(a.tw3_terminal))
    W=fr["first_authoritative_X2_candidate"];V=W["vertices"];E=es(W["exact_edges"])
    S=W["old_precoloring"]["S"];f=W["old_precoloring"]["f"]
    old_checks,old_lists=verify_axioms(V,E,S,W["old_precoloring"]["X0"],W["old_precoloring"]["X"],W["old_precoloring"]["Y0"],W["old_precoloring"]["Y"],f)
    q={
      "P_singleton":W["stored_111"]["P"]==["p"],"M_singleton":W["stored_111"]["M"]==["m"],"N_singleton":W["stored_111"]["N"]==["n"],
      "p_type_T":type_set("p",E,S)==["s"],"n_type_Tprime":type_set("n",E,S)==["t"],"m_Y0":"m" in W["old_precoloring"]["Y0"],
      "pm":adj(E,"p","m"),"mn":adj(E,"m","n"),"pn_nonedge":not adj(E,"p","n"),
      "Q_colors":W["stored_111"]["f_prime"]["p"] not in (1,2) and W["stored_111"]["f_prime"]["n"] not in (1,2)
    }
    post=W["post_constructor"];postf={"s":1,"t":2,**W["stored_111"]["f_prime"]}
    post_checks,post_lists=verify_axioms(V,E,post["S_prime"],[],[],post["Y0_prime"],post["Y_prime"],postf)
    post_list_checks={v:post_lists[v]==L for v,L in post["lists_before_pair_fix"].items()}
    p7=p7_witness(V,E)
    y,yp=W["survivor_pair"]
    survivor={
      "yy_nonedge":not adj(E,y,yp),"common_z":adj(E,y,"z") and adj(E,yp,"z"),
      "y_type_T":type_set(y,E,S)==["s"],"yp_type_Tprime":type_set(yp,E,S)==["t"],
      "ym_nonedge":not adj(E,y,"m"),"ypm_edge":adj(E,yp,"m"),
      "lists_unequal":post_lists[y]!=post_lists[yp],
      "intersection":sorted(set(post_lists[y])&set(post_lists[yp]))
    }
    cert=W["answer_relevance_certificate"]["coloring"]
    answer={"covers_all":set(cert)==set(V),"proper":proper(E,cert),"route34":cert[y]==3 and cert[yp]==4,
            "pair_colors_allowed":cert[y] in post_lists[y] and cert[yp] in post_lists[yp]}

    fixed=dict(postf);fixed[y]=3;fixed[yp]=4
    current={v:post_lists[v] for v in V if v not in post["S_prime"]}
    route_lists,route_fixed,route_prop=propagate(E,current,fixed)
    route_comps=comps(route_lists.keys(),E)
    route_records=[comp_record(C,E,route_lists) for C in route_comps]
    expectedC=set(W["exact_after_route34_and_frozen_propagation"]["component"]["vertices"])
    target=next((r for r in route_records if set(r["vertices"])==expectedC),None)
    target_exact=target is not None and target["lists"]=={k:v for k,v in sorted(W["exact_after_route34_and_frozen_propagation"]["component"]["lists"].items())}
    target_noncontr=route_lists is not None
    not_l3=target is not None and target["missing_colors"]==[]

    # authoritative octahedron minor model
    m=W["forbidden_minor_certificate"]
    mchecks,mwitness=verify_minor_model(target["vertices"],E,m["H"],m["branch_sets"],m["cross_edge_witnesses"]) if target else ({},{})

    # positive K4 TW3 control
    PC=fr["mandatory_positive_control"];PE=es(PC["edges"]);PV=PC["vertices"]
    bags={b["id"]:b["vertices"] for b in PC["width3_decomposition"]["bags"]}
    td=verify_td(PV,PE,bags,PC["width3_decomposition"]["tree_edges"],3)
    sol=brute_list_color(PV,PE,PC["lists"])
    pc={
      "global_missing_color":sorted(COL-set().union(*(set(PC["lists"][v]) for v in PV))),
      "td_checks":td,
      "solver_status":"COLORABLE" if sol else "UNSAT",
      "reconstruction":sol,
      "proper":bool(sol and proper(PE,sol)),
      "pass":all(td.values()) and bool(sol) and proper(PE,sol)
    }

    # synthetic controls all four
    controls={}
    for h,(HV,HE) in forbidden_catalog().items():
        bs={v:[v] for v in HV}
        ch,ew=verify_minor_model(HV,HE,h,bs)
        controls[h]={"checks":ch,"pass":all(ch.values()),"edge_witnesses":ew}
    controls_pass=all(x["pass"] for x in controls.values())

    # minimization: first witness immutable; record six-vertex octahedron core and proper induced deletions of core
    core=["a0","a1","b0","b1","c0","c1"]
    core_lists={v:route_lists[v] for v in core}
    core_rec=comp_record(core,E,route_lists)
    core_mchecks,_=verify_minor_model(core,E,"OCTAHEDRON",m["branch_sets"])
    sub=[]
    for n in range(1,len(core)):
      for ss in itertools.combinations(core,n):
        if not connected(ss,E):continue
        # none can contain any 6+-vertex obstruction if <6 except K5 at 5, test all catalogs exhaustively only when possible:
        has_forbidden=False
        which=None
        if len(ss)>=5:
          # brute minor search not attempted; for <6 only possible K5 requires induced/contract with same 5 vertices -> literal K5
          if len(ss)==5 and all(adj(E,u,v) for u,v in itertools.combinations(ss,2)):
            has_forbidden=True;which="K5"
        sub.append({"vertices":list(ss),"has_verified_tw3_forbidden_minor":has_forbidden,"which":which})
    core_vertex_min=all(not x["has_verified_tw3_forbidden_minor"] for x in sub)

    input_checks={
      "prereg_binding":fr["authorization"]["prereg_blob"]=="a3efd8187bb917a2b2b058bdd6f2ae5cd2e208ba",
      "tw3_authority":tw3["status"]=="PASS_TREEWIDTH3_LIST_COLORING_POLYNOMIAL_TERMINAL"
    }
    auth_ok=all(old_checks.values()) and all(q.values()) and all(post_checks.values()) and all(post_list_checks.values()) and p7 is None and all(answer.values()) and survivor["yy_nonedge"] and survivor["common_z"] and survivor["y_type_T"] and survivor["yp_type_Tprime"] and survivor["ym_nonedge"] and survivor["ypm_edge"] and survivor["lists_unequal"] and survivor["intersection"]==[3,4]
    x2=auth_ok and target_noncontr and target_exact and not_l3 and all(mchecks.values()) and pc["pass"] and controls_pass
    outcome="X2_TW3_FORBIDDEN_MINOR_FOUR_COLOR_RESIDUAL" if x2 else "X3_GATE_UNRESOLVED"
    result={
      "schema":"janus.trump.c11_pi_tw3_or_list3.execution.v1",
      "authority_checks":{"old_axioms":old_checks,"stored_111_Q":q,"post_axioms":post_checks,"post_lists":post_list_checks,"P7_free":p7 is None,"induced_P7_witness":p7,"survivor_pair":survivor,"answer_relevance_certificate":answer},
      "route34":{"propagation":route_prop,"components":route_records,"target_exact":target_exact},
      "positive_K4_TW3_control":pc,
      "forbidden_minor_classifier_controls":controls,
      "X1":{"status":"FALSIFIED_BY_AUTHORITATIVE_X2_COMPONENT" if x2 else "NOT_ESTABLISHED"},
      "X2":{"status":"VERIFIED" if x2 else "NOT_VERIFIED","selected_forbidden_minor":"OCTAHEDRON","first_authoritative_component":target,"minor_model_checks":mchecks,"minor_edge_witnesses":mwitness,"claim":"There exists an authoritative C11 PI residual component with tw(C)>3 certified by an octahedron minor."},
      "X3":"NOT_REACHED" if x2 else "VERIFIED",
      "primary_outcome":outcome,
      "minimization":{"first_authoritative_witness_immutable":True,"six_vertex_octahdron_core":core_rec,"core_minor_checks":core_mchecks,"core_vertex_minimal_under_connected_induced_deletion_for_forbidden_minor":core_vertex_min,"proper_connected_induced_subcomponents":sub,"global_minimality_claimed":False},
      "oracle_use":{"extension_oracle_for_classification":False,"general_P7_free_4color_oracle":False,"tw4_opened":False,"backdoor_size2_search":False,"branching_search":False},
      "scientific_ceiling":{"TREEWIDTH3_LIST_TERMINAL":"VERIFIED","PREVIOUS_K4":"TW3_LIST_READY","UNIVERSAL_LIST3_OR_TW3_COLLAPSE":"FALSIFIED_BY_AUTHORITATIVE_X2_COMPONENT" if x2 else "OPEN","AUTHORITATIVE_TW3_FORBIDDEN_MINOR_RESIDUAL":"VERIFIED" if x2 else "NOT_VERIFIED","WITNESS_TREEWIDTH":">3_ONLY_FOR_THIS_WITNESS" if x2 else "UNRESOLVED","UNBOUNDED_TREEWIDTH":"NOT_CLAIMED","PI_DISCOVERY":"PARTIAL","P3_EXACT_PAIR_QUOTIENT":"NOT_ESTABLISHED","REPAIR":"NOT_STARTED","NEW_DESCRIPTOR":"NOT_DEFINED","BACKDOOR_SIZE_2":"NOT_OPENED","TW4":"NOT_OPENED","LEMMA11_P7_LIFT":"OPEN","P7_FREE_4_COLOR_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"},
      "forbidden_interpretations":["UNBOUNDED_TREEWIDTH","HARDNESS","EXPONENTIAL_COMPLEXITY","NEED_FOR_BRANCHING","NEED_FOR_BACKDOOR_SIZE_2","NEED_FOR_TW4","P3_FALSE","P_VS_NP_INFERENCE"],
      "repair_attempted":False,"successor_autoactivated":False,"stop":True,
      "input_checks":input_checks
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"outcome":outcome,"minor":result["X2"]["selected_forbidden_minor"],"P7_free":p7 is None,"positive_K4":pc["pass"],"all_classifier_controls":controls_pass},sort_keys=True))
    if not all(input_checks.values()):raise SystemExit(2)
    if outcome!="X2_TW3_FORBIDDEN_MINOR_FOUR_COLOR_RESIDUAL":raise SystemExit(3)

if __name__=="__main__":main()
