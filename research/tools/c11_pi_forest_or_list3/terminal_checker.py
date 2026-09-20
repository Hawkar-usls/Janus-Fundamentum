#!/usr/bin/env python3
import argparse,itertools,json,pathlib,hashlib

COL={1,2,3,4}
def ek(a,b): return tuple(sorted((a,b)))
def edgeset(edges): return {ek(a,b) for a,b in edges}
def adj(E,a,b): return ek(a,b) in E

def connected(V,E):
    V=set(V)
    if not V:return True
    seen=set();stack=[next(iter(V))]
    while stack:
        v=stack.pop()
        if v in seen:continue
        seen.add(v)
        stack.extend([u for u in V-seen if adj(E,v,u)])
    return seen==V

def components(E,V):
    V=set(V);out=[]
    while V:
        s=next(iter(V));C=set();stack=[s]
        while stack:
            v=stack.pop()
            if v in C:continue
            C.add(v)
            stack.extend([u for u in V-C if adj(E,v,u)])
        V-=C;out.append(sorted(C))
    return sorted(out,key=lambda x:(len(x),x))

def p7_witness(V,E):
    for S in itertools.combinations(V,7):
        SS=set(S); sub={e for e in E if e[0] in SS and e[1] in SS}
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
    ch["i_graph_connected"]=connected(V,E)
    ch["ii_seed_connected"]=connected(S,E)
    ch["ii_no_outside_complete_to_seed"]=all(not all(adj(E,v,s) for s in S) for v in set(V)-set(S))
    exact_y0={v for v in V if v not in S and not any(adj(E,v,s) for s in S)}
    ch["iii_Y0_exact"]=exact_y0==set(Y0)
    Y0E=[(a,b) for a,b in E if a in Y0 and b in Y0]
    ok=True
    for v in set(V)-set(Y0)-set(X0):
        for a,b in Y0E:
            if adj(E,v,a)!=adj(E,v,b):ok=False
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

def forest_info(V,E):
    V=set(V); sub={e for e in E if e[0] in V and e[1] in V}
    comps=components(sub,V)
    isforest=(len(sub)==len(V)-len(comps))
    return isforest,sorted([list(e) for e in sub]),comps

def simple_cycle(V,E):
    V=set(V)
    # DFS with parent; return cycle closed with first vertex repeated.
    nbr={v:sorted([u for u in V if u!=v and adj(E,v,u)]) for v in V}
    seen=set()
    for start in sorted(V):
      if start in seen: continue
      parent={start:None};stack=[(start,iter(nbr[start]))];seen.add(start)
      while stack:
        v,it=stack[-1]
        try:u=next(it)
        except StopIteration:
          stack.pop();continue
        if u==parent.get(v):continue
        if u not in seen:
          seen.add(u);parent[u]=v;stack.append((u,iter(nbr[u])));continue
        # back/cross edge in undirected DFS; reconstruct v -> lca and u -> lca
        pv=[];x=v
        while x is not None:pv.append(x);x=parent.get(x)
        pu=[];x=u
        while x is not None:pu.append(x);x=parent.get(x)
        common=next((x for x in pv if x in set(pu)),None)
        if common is None:continue
        pathv=pv[:pv.index(common)+1]
        pathu=pu[:pu.index(common)+1]
        cyc=pathv + list(reversed(pathu[:-1]))
        if len(cyc)>=3:
          cyc_closed=cyc+[cyc[0]]
          if all(adj(E,cyc_closed[i],cyc_closed[i+1]) for i in range(len(cyc_closed)-1)):
            return cyc_closed
    return None

def classify_component(C,E,lists):
    union=sorted(set().union(*(set(lists[v]) for v in C)))
    missing=sorted(COL-set(union))
    forest,subedges,cc=forest_info(C,E)
    cyc=None if forest else simple_cycle(C,E)
    return {
      "vertices":sorted(C),
      "edges":subedges,
      "lists":{v:lists[v] for v in sorted(C)},
      "union_of_lists":union,
      "missing_colors":missing,
      "L3_READY":bool(missing),
      "forest":forest,
      "cycle":cyc,
      "classification":"L3_READY" if missing else ("FOREST_LIST_READY" if forest else "CYCLIC_FULL_FOUR_COLOR_RESIDUAL")
    }

def forest_list_dp(V,E,lists):
    forest,_,comps=forest_info(V,E)
    if not forest:return {"status":"NOT_FOREST"}
    # exact singleton propagation first
    plists,pfixed,prop=propagate(E,lists,{})
    if plists is None:return {"status":"CONTRADICTION","certificate":prop}
    # fixed singleton vertices were removed; residual remains forest. Solve residual by rooted DP.
    residual=set(plists)
    solution=dict(pfixed)
    for comp in components(E,residual):
        if not comp:continue
        root=comp[0];parent={root:None};order=[root];stack=[root]
        while stack:
            v=stack.pop()
            for u in sorted(comp):
                if u==parent.get(v) or u in parent:continue
                if adj(E,v,u):
                    parent[u]=v;stack.append(u);order.append(u)
        children={v:[] for v in comp}
        for v,p in parent.items():
            if p is not None:children[p].append(v)
        F={}
        for v in reversed(order):
            good=[]
            for c in plists[v]:
                ok=True
                for u in children[v]:
                    if not any(d!=c for d in F[u]):
                        ok=False;break
                if ok:good.append(c)
            F[v]=good
            if not good:return {"status":"CONTRADICTION","certificate":{"kind":"EMPTY_DP_STATE","vertex":v,"states":F}}
        # reconstruct
        solution[root]=F[root][0]
        for v in order[1:]:
            p=parent[v]
            solution[v]=next(d for d in F[v] if d!=solution[p])
    # incorporate check against propagated fixed vertices
    if not proper(E,solution):
        return {"status":"INTERNAL_RECONSTRUCTION_FAIL","solution":solution}
    return {"status":"COLORABLE","solution":solution,"propagation":prop}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True);ap.add_argument("--freeze",required=True)
    ap.add_argument("--forest-terminal",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();root=pathlib.Path(a.out);root.mkdir(parents=True,exist_ok=True)
    pre=json.load(open(a.prereg));fr=json.load(open(a.freeze));forest_auth=json.load(open(a.forest_terminal))
    W=fr["first_authoritative_T2_candidate"];V=W["vertices"];E=edgeset(W["exact_edges"])
    S=W["old_precoloring"]["S"];f=W["old_precoloring"]["f"]
    old_checks,old_lists=verify_axioms(V,E,S,W["old_precoloring"]["X0"],W["old_precoloring"]["X"],W["old_precoloring"]["Y0"],W["old_precoloring"]["Y"],f)
    qchecks={
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
    structural={
      "yy_nonedge":not adj(E,y,yp),"common_z":adj(E,y,"z") and adj(E,yp,"z"),
      "y_type_T":type_set(y,E,S)==["s"],"yp_type_Tprime":type_set(yp,E,S)==["t"],
      "ym_nonedge":not adj(E,y,"m"),"ypm_edge":adj(E,yp,"m"),
      "lists":[post_lists[y],post_lists[yp]],"intersection":sorted(set(post_lists[y])&set(post_lists[yp]))
    }
    cert=W["answer_relevance_certificate"]["coloring"]
    answer={
      "covers_all_vertices":set(cert)==set(V),"proper":proper(E,cert),
      "route34":cert[y]==3 and cert[yp]==4,
      "selected_colors_in_lists":cert[y] in post_lists[y] and cert[yp] in post_lists[yp]
    }
    fixed=dict(postf);fixed[y]=3;fixed[yp]=4
    current={v:post_lists[v] for v in V if v not in post["S_prime"]}
    route_lists,route_fixed,route_prop=propagate(E,current,fixed)
    route_comps=components(E,route_lists.keys())
    classified=[classify_component(C,E,route_lists) for C in route_comps]
    cyclic=[x for x in classified if x["classification"]=="CYCLIC_FULL_FOUR_COLOR_RESIDUAL"]
    l3=[x for x in classified if x["classification"]=="L3_READY"]

    # positive forest control and exact solver
    FC=fr["mandatory_controls"]["forest_positive_control"];FE=edgeset(FC["edges"])
    fclass=classify_component(FC["vertices"],FE,FC["lists"])
    fsolve=forest_list_dp(FC["vertices"],FE,FC["lists"])
    forest_control={
      "classification":fclass,
      "solver":fsolve,
      "pass":(not fclass["L3_READY"] and fclass["forest"] and fclass["classification"]=="FOREST_LIST_READY" and fsolve["status"]=="COLORABLE")
    }
    # cyclic synthetic control
    CC=fr["mandatory_controls"]["cyclic_classifier_control"];CE=edgeset(CC["edges"])
    cclass=classify_component(CC["vertices"],CE,CC["lists"])
    cycle_control={"classification":cclass,"pass":(not cclass["forest"] and cclass["cycle"] is not None and cclass["union_of_lists"]==[1,2,3,4])}

    # minimization of authoritative C4
    target=cyclic[0] if cyclic else None
    minim=[]
    vertex_min=False
    if target:
      TV=target["vertices"]
      for n in range(1,len(TV)):
        for sub in itertools.combinations(TV,n):
          subE={e for e in E if e[0] in sub and e[1] in sub}
          if not connected(sub,subE):continue
          rec=classify_component(sub,E,{v:route_lists[v] for v in sub})
          minim.append({"vertices":list(sub),"classification":rec["classification"],"forest":rec["forest"],"missing_colors":rec["missing_colors"]})
      vertex_min=all(x["classification"]!="CYCLIC_FULL_FOUR_COLOR_RESIDUAL" for x in minim)

    input_checks={
      "prereg_binding":fr["authorization"]["prereg_blob"]=="41e515511b5b3a4dd2d9a20ed787a2667947999e",
      "forest_authority":forest_auth["status"]=="PASS_FOREST_LIST_COLORING_POLYNOMIAL_TERMINAL"
    }
    auth_ok=all(old_checks.values()) and all(qchecks.values()) and all(post_checks.values()) and all(post_list_checks.values()) and p7 is None and all(answer.values())
    t2_ok=(auth_ok and len(cyclic)>=1 and forest_control["pass"] and cycle_control["pass"] and vertex_min)
    outcome="T2_CYCLIC_FOUR_COLOR_RESIDUAL" if t2_ok else "T3_GATE_UNRESOLVED"
    result={
      "schema":"janus.trump.c11_pi_forest_or_list3.execution.v1",
      "authority_checks":{"old_axioms":old_checks,"stored_111_Q":qchecks,"post_axioms":post_checks,"post_lists":post_list_checks,"P7_free":p7 is None,"induced_P7_witness":p7,"survivor_pair":structural,"answer_relevance_certificate":answer},
      "route34":{"propagation":route_prop,"components":classified},
      "forest_positive_control":forest_control,
      "cyclic_classifier_control":cycle_control,
      "T1":{"status":"FALSIFIED_BY_AUTHORITATIVE_T2_COMPONENT" if t2_ok else "NOT_ESTABLISHED"},
      "T2":{
        "status":"VERIFIED" if t2_ok else "NOT_VERIFIED",
        "first_authoritative_component":target,
        "claim":"There exists an authoritative C11 PI residual component outside the current {List-3, Forest-List} terminal union."
      },
      "T3":"NOT_REACHED" if t2_ok else "VERIFIED",
      "primary_outcome":outcome,
      "minimization":{"first_witness_immutable":True,"proper_connected_induced_subcomponents":minim,"vertex_minimal_under_induced_deletion_for_exact_decorated_C":vertex_min,"global_minimality_claimed":False},
      "oracle_use":{"extension_oracle":False,"general_P7_free_4color_oracle":False,"branching_search":False,"backdoor_size2_search":False},
      "scientific_ceiling":{"UNIVERSAL_FOREST_OR_L3_COLLAPSE":"FALSIFIED_BY_AUTHORITATIVE_T2_COMPONENT" if t2_ok else "OPEN","CYCLIC_FULL_FOUR_COLOR_RESIDUAL":"VERIFIED" if t2_ok else "NOT_VERIFIED","PI_DISCOVERY":"PARTIAL","P3_EXACT_PAIR_QUOTIENT":"NOT_ESTABLISHED","REPAIR":"NOT_STARTED","NEW_DESCRIPTOR":"NOT_DEFINED","BACKDOOR_SIZE_2":"NOT_OPENED","LEMMA11_P7_LIFT":"OPEN","P7_FREE_4_COLOR_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"},
      "forbidden_interpretations":["HARDNESS","NEED_FOR_BRANCHING","NEED_FOR_BACKDOOR_SIZE_2","UNBOUNDED_TREEWIDTH","EXPONENTIAL_COMPLEXITY","P_VS_NP_INFERENCE"],
      "repair_attempted":False,"successor_autoactivated":False,"stop":True,
      "input_checks":input_checks
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"outcome":outcome,"cyclic_components":len(cyclic),"forest_control":forest_control["pass"],"cycle_control":cycle_control["pass"],"vertex_minimal":vertex_min},sort_keys=True))
    if not all(input_checks.values()):raise SystemExit(2)
    if outcome!="T2_CYCLIC_FOUR_COLOR_RESIDUAL":raise SystemExit(3)
if __name__=="__main__":main()
