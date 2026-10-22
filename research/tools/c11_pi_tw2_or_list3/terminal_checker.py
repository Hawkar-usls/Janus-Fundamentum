#!/usr/bin/env python3
import argparse,itertools,json,pathlib

COL={1,2,3,4}
def ek(a,b): return tuple(sorted((a,b)))
def eset(xs): return {ek(a,b) for a,b in xs}
def adj(E,a,b): return ek(a,b) in E

def connected(V,E):
    V=set(V)
    if not V:return True
    seen=set(); st=[next(iter(V))]
    while st:
        v=st.pop()
        if v in seen: continue
        seen.add(v)
        st.extend([u for u in V-seen if adj(E,v,u)])
    return seen==V

def components(V,E):
    rem=set(V); out=[]
    while rem:
        s=next(iter(rem)); C=set(); st=[s]
        while st:
            v=st.pop()
            if v in C: continue
            C.add(v); st.extend([u for u in rem-C if adj(E,v,u)])
        rem-=C; out.append(sorted(C))
    return sorted(out,key=lambda x:(len(x),x))

def p7_witness(V,E):
    for S in itertools.combinations(V,7):
        SS=set(S); sub={e for e in E if e[0] in SS and e[1] in SS}
        if len(sub)!=6: continue
        deg={v:0 for v in S}
        for a,b in sub: deg[a]+=1; deg[b]+=1
        if sorted(deg.values())!=[1,1,2,2,2,2,2]: continue
        if connected(S,sub): return list(S)
    return None

def seed_lists(V,E,S,f):
    out={}
    for v in V:
        if v in S: continue
        used={f[s] for s in S if adj(E,v,s)}
        out[v]=sorted(COL-used)
    return out

def verify_axioms(V,E,S,X0,X,Y0,Y,f):
    L=seed_lists(V,E,S,f); ch={}
    ch["i_graph_connected"]=connected(V,E)
    ch["ii_seed_connected"]=connected(S,E)
    ch["ii_no_outside_complete_to_seed"]=all(not all(adj(E,v,s) for s in S) for v in set(V)-set(S))
    exact_y0={v for v in V if v not in S and not any(adj(E,v,s) for s in S)}
    ch["iii_Y0_exact"]=exact_y0==set(Y0)
    y0_edges=[e for e in E if e[0] in Y0 and e[1] in Y0]
    ok=True
    for v in set(V)-set(Y0)-set(X0):
        for a,b in y0_edges:
            if adj(E,v,a)!=adj(E,v,b): ok=False
    ch["iv_no_mixed_Y0_edge"]=ok
    ch["v_Y0_four_lists"]=all(set(L[v])==COL for v in Y0)
    ch["v_Y_three_lists"]=all(len(L[v])==3 for v in Y)
    parts=list(map(set,[S,X0,X,Y0,Y]))
    ch["partition"]=set(V)==set().union(*parts) and all(not (A&B) for A,B in itertools.combinations(parts,2))
    return ch,L

def type_set(v,E,S): return sorted([s for s in S if adj(E,v,s)])
def proper(E,c): return all(not(a in c and b in c and c[a]==c[b]) for a,b in E)

def propagate(E,lists,fixed):
    lists={v:set(L) for v,L in lists.items() if v not in fixed}; fixed=dict(fixed); prov=[]
    while True:
        for a,b in E:
            if a in fixed and b in fixed and fixed[a]==fixed[b]:
                return None,fixed,{"kind":"IMPROPER_FIXED_EDGE","edge":[a,b],"color":fixed[a],"provenance":prov}
        changed=False
        for v in list(lists):
            rem={fixed[u] for u in fixed if adj(E,u,v)}
            gone=sorted(lists[v]&rem)
            if gone:
                lists[v]-=rem; changed=True; prov.append({"op":"REMOVE_FIXED_NEIGHBOR_COLORS","vertex":v,"removed":gone})
            if not lists[v]:
                return None,fixed,{"kind":"EMPTY_LIST","vertex":v,"provenance":prov}
        singles=sorted(v for v,L in lists.items() if len(L)==1)
        if singles:
            for v in singles:
                if v not in lists: continue
                c=next(iter(lists[v])); fixed[v]=c; del lists[v]
                prov.append({"op":"FIX_SINGLETON","vertex":v,"color":c}); changed=True
            continue
        if not changed: break
    return {v:sorted(L) for v,L in lists.items()},fixed,{"kind":"FIXPOINT","provenance":prov}

def comp_record(C,E,lists):
    union=sorted(set().union(*(set(lists[v]) for v in C)))
    return {"vertices":sorted(C),"edges":sorted([list(e) for e in E if e[0] in C and e[1] in C]),
            "lists":{v:lists[v] for v in sorted(C)},"union_of_lists":union,
            "missing_colors":sorted(COL-set(union))}

def verify_td(V,E,bags,tree_edges):
    B={b["id"]:set(b["vertices"]) for b in bags}; T=eset(tree_edges)
    checks={}
    checks["bag_size_le3"]=all(len(x)<=3 for x in B.values())
    checks["vertex_coverage"]=set(V)==set().union(*B.values())
    checks["edge_coverage"]=all(any(a in bag and b in bag for bag in B.values()) for a,b in E if a in V and b in V)
    ids=list(B)
    checks["tree_edge_count"]=len(T)==max(0,len(ids)-1)
    checks["tree_connected"]=connected(ids,T)
    ri=True
    for v in V:
        nodes=[bid for bid,bag in B.items() if v in bag]
        if nodes and not connected(nodes,{e for e in T if e[0] in nodes and e[1] in nodes}): ri=False
    checks["running_intersection"]=ri
    return checks

def td_list_dp(V,E,lists,bags,tree_edges):
    # Small exact proof-carrying control DP: enumerate bag states, then brute consistency on tree of bags.
    B={b["id"]:tuple(b["vertices"]) for b in bags}; T=eset(tree_edges); ids=list(B)
    states={}
    for bid,bag in B.items():
        arr=[]
        for vals in itertools.product(COL, repeat=len(bag)):
            c=dict(zip(bag,vals))
            if any(c[v] not in lists[v] for v in bag): continue
            if any(a in c and b in c and c[a]==c[b] for a,b in E): continue
            arr.append(c)
        states[bid]=arr
    # tree root and recursive compatibility
    root=ids[0]; parent={root:None}; order=[root]; st=[root]
    while st:
        x=st.pop()
        for y in ids:
            if y in parent or y==x: continue
            if adj(T,x,y): parent[y]=x; st.append(y); order.append(y)
    children={x:[] for x in ids}
    for x,p in parent.items():
        if p is not None: children[p].append(x)
    good={}
    witness={}
    for x in reversed(order):
        good[x]=[]
        for sx in states[x]:
            ok=True; child_pick={}
            for u in children[x]:
                compat=[]
                for su in good[u]:
                    common=set(B[x])&set(B[u])
                    if all(sx[v]==su[v] for v in common): compat.append(su)
                if not compat: ok=False; break
                child_pick[u]=compat[0]
            if ok:
                good[x].append(sx); witness[(x,tuple(sorted(sx.items())))]=child_pick
    if not good[root]: return {"status":"CONTRADICTION","states":{k:len(v) for k,v in states.items()}}
    chosen={root:good[root][0]}; stack=[root]
    while stack:
        x=stack.pop(); sx=chosen[x]
        picks=witness[(x,tuple(sorted(sx.items())))]
        for u,su in picks.items(): chosen[u]=su; stack.append(u)
    coloring={}
    for sx in chosen.values(): coloring.update(sx)
    return {"status":"COLORABLE","coloring":coloring,"proper":proper(E,coloring),
            "bag_state_counts":{k:len(v) for k,v in states.items()}}

def verify_k4_model(C,E,model):
    keys=["B1","B2","B3","B4"]; sets=[set(model[k]) for k in keys]
    checks={}
    checks["nonempty"]=all(sets)
    checks["pairwise_disjoint"]=all(not (A&B) for A,B in itertools.combinations(sets,2))
    checks["inside_C"]=all(s<=set(C) for s in sets)
    checks["connected"]=all(connected(s,{e for e in E if e[0] in s and e[1] in s}) for s in sets)
    cross={}
    ok=True
    for i,j in itertools.combinations(range(4),2):
        witnesses=[list(e) for e in E if (e[0] in sets[i] and e[1] in sets[j]) or (e[1] in sets[i] and e[0] in sets[j])]
        cross[f"B{i+1}-B{j+1}"]=witnesses[0] if witnesses else None
        if not witnesses: ok=False
    checks["all_six_cross_adjacencies"]=ok
    return checks,cross

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True);ap.add_argument("--freeze",required=True)
    ap.add_argument("--tw2-terminal",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args(); root=pathlib.Path(a.out);root.mkdir(parents=True,exist_ok=True)
    pre=json.load(open(a.prereg)); fr=json.load(open(a.freeze)); tw2=json.load(open(a.tw2_terminal))
    W=fr["first_authoritative_W2_candidate"]; V=W["vertices"]; E=eset(W["exact_edges"])
    old=W["old_precoloring"]; old_checks,old_lists=verify_axioms(V,E,old["S"],old["X0"],old["X"],old["Y0"],old["Y"],old["f"])
    q={
      "P_singleton":W["stored_111"]["P"]==["p"],"M_singleton":W["stored_111"]["M"]==["m"],"N_singleton":W["stored_111"]["N"]==["n"],
      "p_type_T":type_set("p",E,old["S"])==["s"],"n_type_Tprime":type_set("n",E,old["S"])==["t"],
      "m_in_Y0":"m" in old["Y0"],"pm":adj(E,"p","m"),"mn":adj(E,"m","n"),"pn_nonedge":not adj(E,"p","n"),
      "Q_endpoint_colors":W["stored_111"]["f_prime"]["p"] not in (1,2) and W["stored_111"]["f_prime"]["n"] not in (1,2)
    }
    post=W["post_constructor"]; postf={"s":1,"t":2,**W["stored_111"]["f_prime"]}
    post_checks,post_lists=verify_axioms(V,E,post["S_prime"],[],[],post["Y0_prime"],post["Y_prime"],postf)
    post_list_checks={v:post_lists[v]==L for v,L in post["lists_before_pair_fix"].items()}
    p7=p7_witness(V,E)
    y,yp=W["survivor_pair"]
    pair={
      "yy_nonedge":not adj(E,y,yp),"common_z":adj(E,y,"z") and adj(E,yp,"z"),
      "y_type_T":type_set(y,E,old["S"])==["s"],"yp_type_Tprime":type_set(yp,E,old["S"])==["t"],
      "ym_nonedge":not adj(E,y,"m"),"ypm_edge":adj(E,yp,"m"),
      "lists_unequal":post_lists[y]!=post_lists[yp],
      "intersection":sorted(set(post_lists[y])&set(post_lists[yp]))
    }
    cert=W["answer_relevance_certificate"]["coloring"]
    provenance={"covers_all":set(cert)==set(V),"proper":proper(E,cert),
                "route34":cert[y]==3 and cert[yp]==4,
                "colors_in_lists":cert[y] in post_lists[y] and cert[yp] in post_lists[yp]}
    fixed=dict(postf);fixed[y]=3;fixed[yp]=4
    current={v:post_lists[v] for v in V if v not in post["S_prime"]}
    route_lists,route_fixed,route_prop=propagate(E,current,fixed)
    rcomps=components(route_lists.keys(),E)
    records=[comp_record(C,E,route_lists) for C in rcomps]
    target=next((x for x in records if set(x["vertices"])=={"a0","a1","b2","b3"}),None)
    model=W["exact_after_route34_and_frozen_propagation"]["components"][1]["K4_minor_model"]
    k4_checks,k4_cross=verify_k4_model(target["vertices"] if target else [],E,model) if target else ({}, {})
    target_ok=bool(target) and target["union_of_lists"]==[1,2,3,4] and target["missing_colors"]==[] and all(k4_checks.values())

    # Positive previous C4 control
    C4=fr["mandatory_controls"]["positive_TW2_C4_control"]; C4E=eset(C4["edges"]); C4V=C4["vertices"]
    td=C4["width2_decomposition"]; td_checks=verify_td(C4V,C4E,td["bags"],td["tree_edges"])
    tdsolve=td_list_dp(C4V,C4E,C4["lists"],td["bags"],td["tree_edges"])
    c4_union=sorted(set().union(*(set(C4["lists"][v]) for v in C4V)))
    c4_model=None
    # exhaustive branch-set check for 4-vertex graph: K4 minor iff all six edges
    c4_has_k4=(len(C4E)==6)
    positive_control={
      "union_of_lists":c4_union,"missing_colors":sorted(COL-set(c4_union)),
      "td_checks":td_checks,"solver":tdsolve,"K4_minor_absent":not c4_has_k4,
      "pass":all(td_checks.values()) and tdsolve["status"]=="COLORABLE" and tdsolve["proper"] and not c4_has_k4
    }

    # Synthetic K4 negative control
    KC=fr["mandatory_controls"]["negative_K4_classifier_control"]; KCE=eset(KC["edges"])
    kc_checks,kc_cross=verify_k4_model(KC["vertices"],KCE,KC["branch_sets"])
    negative_control={"checks":kc_checks,"cross_edges":kc_cross,"pass":all(kc_checks.values())}

    # minimization: every proper connected induced subgraph of K4 has <=3 vertices, hence cannot host four nonempty branch sets
    minim=[]
    TV=target["vertices"] if target else []
    for n in range(1,len(TV)):
      for sub in itertools.combinations(TV,n):
        subE={e for e in E if e[0] in sub and e[1] in sub}
        if not connected(sub,subE): continue
        union=sorted(set().union(*(set(route_lists[v]) for v in sub)))
        minim.append({"vertices":list(sub),"connected":True,"union_of_lists":union,
                      "K4_minor_possible_by_vertex_count":len(sub)>=4,
                      "tw2_certificate_by_size":"<=2 since |V|<=3"})
    vertex_min=all(not x["K4_minor_possible_by_vertex_count"] for x in minim)

    input_checks={
      "prereg_binding":fr["authorization"]["prereg_blob"]=="d9844c3590653e85594f808167219cbca5b19207",
      "tw2_authority":tw2["status"]=="PASS_TREEWIDTH2_LIST_COLORING_POLYNOMIAL_TERMINAL"
    }
    auth_ok=all(old_checks.values()) and all(q.values()) and all(post_checks.values()) and all(post_list_checks.values()) and p7 is None and all(provenance.values())
    w2=auth_ok and target_ok and positive_control["pass"] and negative_control["pass"] and vertex_min
    outcome="W2_K4_MINOR_FOUR_COLOR_RESIDUAL" if w2 else "W3_GATE_UNRESOLVED"
    result={
      "schema":"janus.trump.c11_pi_tw2_or_list3.execution.v1",
      "authority_checks":{"old_axioms":old_checks,"stored_111_Q":q,"post_axioms":post_checks,"post_lists":post_list_checks,
                          "P7_free":p7 is None,"induced_P7_witness":p7,"survivor_pair":pair,"answer_relevance_provenance":provenance},
      "route34":{"propagation":route_prop,"components":records},
      "positive_TW2_C4_control":positive_control,
      "negative_K4_classifier_control":negative_control,
      "W1":{"status":"FALSIFIED_BY_AUTHORITATIVE_W2_COMPONENT" if w2 else "NOT_ESTABLISHED"},
      "W2":{"status":"VERIFIED" if w2 else "NOT_VERIFIED","component":target,
            "K4_minor_model":model,"K4_model_checks":k4_checks,"six_cross_adjacency_witnesses":k4_cross,
            "claim":"There exists an authoritative C11 PI residual outside the current {List-3, treewidth<=2 arbitrary-list} terminal union."},
      "W3":"NOT_REACHED" if w2 else "VERIFIED",
      "primary_outcome":outcome,
      "minimization":{"first_witness_immutable":True,"proper_connected_induced_subcomponents":minim,
                      "vertex_minimal_under_induced_deletion_for_exact_decorated_C":vertex_min,"global_minimality_claimed":False},
      "oracle_use":{"extension_oracle":False,"general_P7_free_4color_oracle":False,"branching_search":False,"backdoor_size2_search":False},
      "scientific_ceiling":{"UNIVERSAL_LIST3_OR_TW2_COLLAPSE":"FALSIFIED_BY_AUTHORITATIVE_W2_COMPONENT" if w2 else "OPEN",
                            "AUTHORITATIVE_K4_MINOR_RESIDUAL":"VERIFIED" if w2 else "NOT_VERIFIED",
                            "WITNESS_TREEWIDTH":">2_ONLY_FOR_THIS_WITNESS","UNBOUNDED_TREEWIDTH":"NOT_CLAIMED",
                            "PI_DISCOVERY":"PARTIAL","P3_EXACT_PAIR_QUOTIENT":"NOT_ESTABLISHED","REPAIR":"NOT_STARTED",
                            "NEW_DESCRIPTOR":"NOT_DEFINED","BACKDOOR_SIZE_2":"NOT_OPENED","LEMMA11_P7_LIFT":"OPEN",
                            "P7_FREE_4_COLOR_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"},
      "forbidden_interpretations":["HARDNESS","UNBOUNDED_TREEWIDTH","NEED_FOR_BRANCHING","NEED_FOR_BACKDOOR_SIZE_2","EXPONENTIAL_COMPLEXITY","P_VS_NP_INFERENCE"],
      "repair_attempted":False,"successor_autoactivated":False,"stop":True,
      "input_checks":input_checks
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"outcome":outcome,"P7_free":p7 is None,"K4_model":all(k4_checks.values()) if k4_checks else False,
                      "C4_control":positive_control["pass"],"vertex_minimal":vertex_min},sort_keys=True))
    if not all(input_checks.values()): raise SystemExit(2)
    if outcome!="W2_K4_MINOR_FOUR_COLOR_RESIDUAL": raise SystemExit(3)
if __name__=="__main__": main()
