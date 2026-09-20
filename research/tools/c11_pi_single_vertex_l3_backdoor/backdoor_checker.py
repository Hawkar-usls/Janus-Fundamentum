#!/usr/bin/env python3
import argparse,itertools,json,pathlib,hashlib

COL={1,2,3,4}
def edge(a,b): return tuple(sorted((a,b)))
def eset(edges): return {edge(a,b) for a,b in edges}
def adj(E,a,b): return edge(a,b) in E

def connected(vertices,E):
    V=set(vertices)
    if not V: return True
    seen=set(); stack=[next(iter(V))]
    while stack:
        v=stack.pop()
        if v in seen: continue
        seen.add(v)
        stack.extend([u for u in V-seen if adj(E,v,u)])
    return seen==V

def induced_p7_witness(vertices,E):
    # A 7-vertex induced subgraph is P7 iff connected, has 6 edges,
    # and degree multiset [1,1,2,2,2,2,2].
    for S in itertools.combinations(vertices,7):
        SS=set(S)
        sub=[(a,b) for a,b in E if a in SS and b in SS]
        if len(sub)!=6: continue
        deg={v:0 for v in S}
        for a,b in sub:
            deg[a]+=1;deg[b]+=1
        if sorted(deg.values())!=[1,1,2,2,2,2,2]: continue
        if connected(S,set(sub)):
            return list(S)
    return None

def seed_lists(vertices,E,S,f):
    out={}
    for v in vertices:
        if v in S: continue
        used={f[s] for s in S if adj(E,v,s)}
        out[v]=sorted(COL-used)
    return out

def type_set(v,E,S):
    return sorted([s for s in S if adj(E,v,s)])

def verify_axioms_old(V,E,S,X0,X,Y0,Y,f):
    checks={}
    checks["i_graph_connected"]=connected(V,E)
    checks["ii_seed_connected"]=connected(S,E)
    checks["ii_no_outside_complete_to_seed"]=all(
        not all(adj(E,v,s) for s in S) for v in set(V)-set(S)
    )
    exact_y0={v for v in V if v not in S and not any(adj(E,v,s) for s in S)}
    checks["iii_Y0_exact"]=exact_y0==set(Y0)
    # (iv): every v outside Y0 U X0 is not mixed on any edge of G[Y0]
    ok=True
    Y0E=[(a,b) for a,b in E if a in Y0 and b in Y0]
    for v in set(V)-set(Y0)-set(X0):
        for a,b in Y0E:
            if adj(E,v,a)!=adj(E,v,b): ok=False
    checks["iv_no_mixed_Y0_edge"]=ok
    L=seed_lists(V,E,S,f)
    checks["v_Y0_four_lists"]=all(set(L[v])==COL for v in Y0)
    checks["v_Y_three_lists"]=all(len(L[v])==3 for v in Y)
    checks["partition"]=set(V)==set(S)|set(X0)|set(X)|set(Y0)|set(Y) and not any(
        A&B for A,B in itertools.combinations(map(set,[S,X0,X,Y0,Y]),2)
    )
    return checks,L

def verify_axioms_post(V,E,S,X0,X,Y0,Y,f):
    return verify_axioms_old(V,E,S,X0,X,Y0,Y,f)

def proper_coloring(E,c):
    return all(not (a in c and b in c and c[a]==c[b]) for a,b in E)

def propagate(E,current_lists,fixed):
    lists={v:set(L) for v,L in current_lists.items() if v not in fixed}
    fixed=dict(fixed)
    provenance=[]
    while True:
        # improper fixed edge
        for a,b in E:
            if a in fixed and b in fixed and fixed[a]==fixed[b]:
                return None,fixed,{"kind":"IMPROPER_FIXED_EDGE","edge":[a,b],"color":fixed[a],"provenance":provenance}
        changed=False
        for v in list(lists):
            removed=sorted({fixed[u] for u in fixed if adj(E,u,v)} & lists[v])
            if removed:
                lists[v]-=set(removed); provenance.append({"op":"REMOVE_FIXED_NEIGHBOR_COLORS","vertex":v,"removed":removed})
                changed=True
            if not lists[v]:
                return None,fixed,{"kind":"EMPTY_LIST","vertex":v,"provenance":provenance}
        singles=sorted([v for v,L in lists.items() if len(L)==1])
        if singles:
            for v in singles:
                if v not in lists: continue
                c=next(iter(lists[v]))
                fixed[v]=c; del lists[v]
                provenance.append({"op":"FIX_SINGLETON","vertex":v,"color":c})
                changed=True
            continue
        if not changed: break
    return {v:sorted(L) for v,L in lists.items()},fixed,{"kind":"FIXPOINT","provenance":provenance}

def components(E,vertices):
    V=set(vertices);out=[]
    while V:
        s=next(iter(V));stack=[s];C=set()
        while stack:
            v=stack.pop()
            if v in C: continue
            C.add(v)
            stack.extend([u for u in V-C if adj(E,v,u)])
        V-=C;out.append(sorted(C))
    return sorted(out,key=lambda x:(len(x),x))

def component_record(C,lists):
    union=sorted(set().union(*(set(lists[v]) for v in C))) if C else []
    missing=sorted(COL-set(union))
    return {
      "vertices":sorted(C),
      "lists":{v:lists[v] for v in sorted(C)},
      "union_of_lists":union,
      "missing_colors":missing,
      "L3_READY":bool(missing)
    }

def branch(E,C_lists,r,k):
    if r not in C_lists or k not in C_lists[r]:
        return {"status":"INVALID_ASSIGNMENT"}
    fixed={r:k}
    remaining={v:L for v,L in C_lists.items() if v!=r}
    lists,fixed2,prop=propagate(E,remaining,fixed)
    if lists is None:
        return {"status":"CONTRADICTION","certificate":prop,"fixed":fixed2}
    comps=components(E,lists.keys())
    recs=[component_record(C,lists) for C in comps]
    unresolved=[x for x in recs if not x["L3_READY"]]
    return {
      "status":"NOT_L3_READY" if unresolved else "L3_READY",
      "fixed":fixed2,
      "propagation":prop,
      "components":recs,
      "first_unresolved":unresolved[0] if unresolved else None
    }

def is_backdoor(E,C_lists,r):
    rec={}
    for k in sorted(C_lists[r]):
        rec[str(k)]=branch(E,C_lists,r,k)
    ok=all(x["status"] in ("CONTRADICTION","L3_READY") for x in rec.values())
    return ok,rec

def verify_answer_certificate(E,cert,post_lists,pair):
    c=cert
    y,yp=pair
    return {
      "proper":proper_coloring(E,c),
      "covers_all_vertices":True, # checked by caller
      "y_in_list":c[y] in post_lists[y],
      "yp_in_list":c[yp] in post_lists[yp],
      "pair_colors_in_intersection":c[y] in set(post_lists[y])&set(post_lists[yp]) and c[yp] in set(post_lists[y])&set(post_lists[yp])
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True);ap.add_argument("--freeze",required=True)
    ap.add_argument("--positive-control",required=True);ap.add_argument("--transfer",required=True)
    ap.add_argument("--out",required=True)
    a=ap.parse_args();root=pathlib.Path(a.out);root.mkdir(parents=True,exist_ok=True)
    pre=json.load(open(a.prereg)); fr=json.load(open(a.freeze)); pc=json.load(open(a.positive_control)); tr=json.load(open(a.transfer))
    W=fr["first_authoritative_B2_candidate"]
    V=W["vertices"]; E=eset(W["exact_edges"])
    S=W["old_precoloring"]["S"]; f=W["old_precoloring"]["f"]
    old_checks,old_lists=verify_axioms_old(V,E,S,W["old_precoloring"]["X0"],W["old_precoloring"]["X"],W["old_precoloring"]["Y0"],W["old_precoloring"]["Y"],f)

    # stored 111 / Q
    qchecks={
      "P_singleton":W["stored_111"]["P"]==["p"],
      "M_singleton":W["stored_111"]["M"]==["m"],
      "N_singleton":W["stored_111"]["N"]==["n"],
      "type_p_T":type_set("p",E,S)==["s"],
      "type_n_Tprime":type_set("n",E,S)==["t"],
      "m_in_Y0":"m" in W["old_precoloring"]["Y0"],
      "pm_edge":adj(E,"p","m"),"mn_edge":adj(E,"m","n"),"pn_nonedge":not adj(E,"p","n"),
      "endpoint_colors_avoid_1_2":W["stored_111"]["f_prime"]["p"] not in (1,2) and W["stored_111"]["f_prime"]["n"] not in (1,2)
    }

    post=W["post_constructor"]
    postf={"s":1,"t":2,**W["stored_111"]["f_prime"]}
    post_checks,post_lists_all=verify_axioms_post(V,E,post["S_prime"],[],[],post["Y0_prime"],post["Y_prime"],postf)
    post_list_checks={v:(post_lists_all[v]==L) for v,L in post["lists_before_pair_fix"].items()}

    p7=induced_p7_witness(V,E)
    pair=W["survivor_pair"]; y,yp=pair
    structural={
      "yyprime_nonedge":not adj(E,y,yp),
      "common_z":adj(E,y,"z") and adj(E,yp,"z"),
      "y_type_T":type_set(y,E,S)==["s"],
      "yp_type_Tprime":type_set(yp,E,S)==["t"],
      "ym_nonedge":not adj(E,y,"m"),
      "ypm_edge":adj(E,yp,"m"),
      "lists_unequal":post_lists_all[y]!=post_lists_all[yp],
      "list_intersection":sorted(set(post_lists_all[y])&set(post_lists_all[yp]))
    }
    cert=W["answer_relevance_certificate"]["coloring"]
    answer_checks=verify_answer_certificate(E,cert,post_lists_all,pair)
    answer_checks["covers_all_vertices"]=set(cert)==set(V)

    # Route 34 exact propagation from post-constructor lists on all unfixed vertices.
    fixed=dict(postf);fixed[y]=3;fixed[yp]=4
    current={v:post_lists_all[v] for v in V if v not in post["S_prime"]}
    route_lists,route_fixed,route_prop=propagate(E,current,fixed)
    route_components=components(E,route_lists.keys())
    route_records=[component_record(C,route_lists) for C in route_components]

    # identify frozen C
    Cset={"b3","a0","a1","b2"}
    C_lists={v:route_lists[v] for v in Cset}
    C_edges=sorted([list(e) for e in E if e[0] in Cset and e[1] in Cset])
    C_exact={
      "vertices_exact":set(C_lists)==Cset,
      "connected":connected(Cset,E),
      "edges":C_edges,
      "lists":{v:C_lists[v] for v in sorted(Cset)},
      "union_of_lists":sorted(set().union(*(set(C_lists[v]) for v in Cset)))
    }

    # Exhaustive all r, all kappa
    exhaustive={}
    backdoors=[]
    defeating={}
    for r in sorted(Cset):
        ok,rec=is_backdoor(E,C_lists,r); exhaustive[r]={"is_backdoor":ok,"branches":rec}
        if ok: backdoors.append(r)
        else:
            # lexicographically first defeating branch
            for k in sorted(C_lists[r]):
                br=rec[str(k)]
                if br["status"]=="NOT_L3_READY":
                    defeating[r]={"kappa":k,"branch":br};break

    B2=(not backdoors and set(defeating)==Cset and all(
        d["branch"]["first_unresolved"]["union_of_lists"]==[1,2,3,4]
        for d in defeating.values()
    ))

    # expected-table cross-check
    expected=W["defeating_table_expected"]
    expected_ok={}
    for r in sorted(Cset):
        exp=expected[r];got=defeating[r]
        expected_ok[r]=(
          got["kappa"]==exp["kappa"] and
          got["branch"]["first_unresolved"]["vertices"]==sorted(exp["unresolved_component"]) and
          got["branch"]["first_unresolved"]["lists"]=={k:exp["lists"][k] for k in sorted(exp["lists"])}
        )

    # negative forall control
    a0=exhaustive["a0"]["branches"]
    negative_control={
      "candidate":"a0",
      "branch_2_status":a0["2"]["status"],
      "branch_3_status":a0["3"]["status"],
      "checker_rejects_a0":exhaustive["a0"]["is_backdoor"] is False,
      "pass":a0["2"]["status"]=="L3_READY" and a0["3"]["status"]=="NOT_L3_READY" and exhaustive["a0"]["is_backdoor"] is False
    }

    # minimization under proper connected induced deletion, inherited exact lists
    minim=[]
    CV=sorted(Cset)
    for n in range(1,len(CV)):
      for sub in itertools.combinations(CV,n):
        if not connected(sub,E): continue
        sublists={v:C_lists[v] for v in sub}
        found=None
        for r in sorted(sub):
          ok,_=is_backdoor(E,sublists,r)
          if ok: found=r;break
        minim.append({"vertices":list(sub),"has_1_L3_backdoor":found is not None,"backdoor":found})
    vertex_minimal=all(x["has_1_L3_backdoor"] for x in minim)

    input_checks={
      "prereg_blob_bound":fr["authorization"]["prereg_blob"]=="76a83abc21bf1dbd24d6affd37c758f03c871698",
      "positive_control_authority":pc["status"]=="PASS_C11_FALSE_TWIN_FAMILY_SINGLE_VERTEX_L3_BACKDOOR",
      "list3_authority":tr["theorem2_external_authority"]["stronger_result_verified"]=="List 3-Coloring is polynomial-time solvable for P7-free graphs."
    }

    all_auth=all(old_checks.values()) and all(qchecks.values()) and all(post_checks.values()) and all(post_list_checks.values()) and p7 is None and all(v if not isinstance(v,list) else True for v in structural.values()) and all(answer_checks.values())
    outcome="B2_NO_SINGLE_VERTEX_BACKDOOR" if all_auth and B2 and negative_control["pass"] else "B3_GATE_UNRESOLVED"

    result={
      "schema":"janus.trump.c11_pi_single_vertex_l3_backdoor.execution.v1",
      "authority_checks":{
        "old_axioms":old_checks,"stored_111_Q":qchecks,"post_axioms":post_checks,
        "post_lists":post_list_checks,"P7_free":p7 is None,"induced_P7_witness":p7,
        "survivor_pair":structural,"answer_relevance_certificate":answer_checks
      },
      "positive_control":{
        "status":"BOUND_THEOREM_AUTHORITY",
        "theorem_status":pc["status"],
        "scope":pc["theorem"]["claim"]
      },
      "route34":{
        "propagation":route_prop,
        "components":route_records,
        "C":C_exact
      },
      "exhaustive_backdoor_audit":exhaustive,
      "defeating_table":defeating,
      "expected_table_crosscheck":expected_ok,
      "negative_quantifier_control":negative_control,
      "B1":{
        "status":"FALSIFIED_BY_AUTHORITATIVE_B2_COUNTERCOMPONENT" if outcome=="B2_NO_SINGLE_VERTEX_BACKDOOR" else "NOT_ESTABLISHED"
      },
      "B2":{
        "status":"VERIFIED" if outcome=="B2_NO_SINGLE_VERTEX_BACKDOOR" else "NOT_VERIFIED",
        "claim":"Frozen-stack bd_L3(C)>1 for the exact four-vertex residual component.",
        "scope":"Relative only to the frozen deterministic propagation plus global-missing-color/List-3 terminal stack."
      },
      "B3":"NOT_REACHED" if outcome=="B2_NO_SINGLE_VERTEX_BACKDOOR" else "VERIFIED",
      "primary_outcome":outcome,
      "minimization":{
        "first_authoritative_witness_immutable":True,
        "proper_connected_induced_subcomponents":minim,
        "vertex_minimal_under_induced_deletion_for_exact_decorated_C":vertex_minimal,
        "global_minimality_claimed":False
      },
      "oracle_use":{"extension_oracle":False,"general_P7_free_4color_oracle":False,"size2_backdoor_search":False},
      "scientific_ceiling":{
        "UNIVERSAL_C11_L3_BACKDOOR_NUMBER_LE1":"FALSIFIED_BY_THIS_COUNTERCOMPONENT" if outcome=="B2_NO_SINGLE_VERTEX_BACKDOOR" else "OPEN",
        "EXISTS_AUTHORITATIVE_C_WITH_FROZEN_STACK_bd_L3_GT1":"VERIFIED" if outcome=="B2_NO_SINGLE_VERTEX_BACKDOOR" else "NOT_VERIFIED",
        "PI_DISCOVERY":"PARTIAL",
        "P3_EXACT_PAIR_QUOTIENT":"NOT_ESTABLISHED",
        "REPAIR":"NOT_STARTED","NEW_DESCRIPTOR":"NOT_DEFINED","BACKDOOR_SIZE_2":"NOT_OPENED",
        "C1S_CS1_CSS":"NOT_REACHED","LEMMA11_P7_LIFT":"OPEN","P7_FREE_4_COLOR_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"
      },
      "forbidden_interpretations":["HARDNESS","EXPONENTIAL_LOWER_BOUND","NO_OTHER_POLYNOMIAL_ALGORITHM","P3_FALSE","P_VS_NP_INFERENCE"],
      "repair_attempted":False,"successor_autoactivated":False,"stop":True,
      "input_checks":input_checks
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"outcome":outcome,"backdoors":backdoors,"vertex_minimal":vertex_minimal,"negative_control":negative_control["pass"]},sort_keys=True))
    if not all(input_checks.values()): raise SystemExit(2)
    if outcome!="B2_NO_SINGLE_VERTEX_BACKDOOR": raise SystemExit(3)

if __name__=="__main__": main()
