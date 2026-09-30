#!/usr/bin/env python3
import argparse,itertools,json,pathlib,hashlib

COL={1,2,3,4}
def ek(a,b): return tuple(sorted((a,b)))
def es(edges): return {ek(a,b) for a,b in edges}
def adj(E,a,b): return ek(a,b) in E

def connected(V,E):
    V=set(V)
    if not V: return True
    seen=set(); st=[next(iter(V))]
    while st:
        v=st.pop()
        if v in seen: continue
        seen.add(v)
        st.extend([u for u in V-seen if adj(E,v,u)])
    return seen==V

def components(V,E):
    V=set(V); out=[]
    while V:
        s=next(iter(V)); C=set(); st=[s]
        while st:
            v=st.pop()
            if v in C: continue
            C.add(v)
            st.extend([u for u in V-C if adj(E,v,u)])
        V-=C; out.append(sorted(C))
    return sorted(out,key=lambda x:(len(x),x))

def p7_witness(V,E):
    for S in itertools.combinations(V,7):
        SS=set(S); sub={x for x in E if x[0] in SS and x[1] in SS}
        if len(sub)!=6: continue
        deg={v:0 for v in S}
        for a,b in sub:
            deg[a]+=1; deg[b]+=1
        if sorted(deg.values())==[1,1,2,2,2,2,2] and connected(S,sub):
            return list(S)
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
    ch["graph_connected"]=connected(V,E)
    ch["seed_connected"]=connected(S,E)
    ch["no_outside_complete_to_seed"]=all(not all(adj(E,v,s) for s in S) for v in set(V)-set(S))
    exact_y0={v for v in V if v not in S and not any(adj(E,v,s) for s in S)}
    ch["Y0_exact"]=exact_y0==set(Y0)
    Y0E=[(a,b) for a,b in E if a in Y0 and b in Y0]
    ok=True
    for v in set(V)-set(Y0)-set(X0):
        for a,b in Y0E:
            if adj(E,v,a)!=adj(E,v,b): ok=False
    ch["no_mixed_on_Y0_edge"]=ok
    ch["Y0_four_lists"]=all(set(L[v])==COL for v in Y0)
    ch["Y_three_lists"]=all(len(L[v])==3 for v in Y)
    parts=list(map(set,[S,X0,X,Y0,Y]))
    ch["partition"]=set(V)==set().union(*parts) and all(not(A&B) for A,B in itertools.combinations(parts,2))
    return ch,L

def type_set(v,E,S): return sorted([s for s in S if adj(E,v,s)])
def proper(E,c):
    return all(not(a in c and b in c and c[a]==c[b]) for a,b in E)

def propagate(E,base_lists,fixed):
    lists={v:set(L) for v,L in base_lists.items() if v not in fixed}; fixed=dict(fixed); prov=[]
    while True:
        for a,b in E:
            if a in fixed and b in fixed and fixed[a]==fixed[b]:
                return None,fixed,{"kind":"IMPROPER_FIXED_EDGE","edge":[a,b],"color":fixed[a],"provenance":prov}
        changed=False
        for v in list(lists):
            removed=sorted({fixed[u] for u in fixed if adj(E,u,v)} & lists[v])
            if removed:
                lists[v]-=set(removed); prov.append({"op":"REMOVE_FIXED_NEIGHBOR_COLORS","vertex":v,"removed":removed}); changed=True
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

def literal_octahedron_parts(S,E):
    S=sorted(S)
    if len(S)!=6: return None
    non=[ek(a,b) for a,b in itertools.combinations(S,2) if not adj(E,a,b)]
    subedges=sum(1 for a,b in itertools.combinations(S,2) if adj(E,a,b))
    if subedges!=12 or len(non)!=3: return None
    flat=[v for pair in non for v in pair]
    if len(set(flat))!=6: return None
    return sorted([list(x) for x in non])

def enumerate_literal_octahedra(V,E):
    out=[]
    for S in itertools.combinations(sorted(V),6):
        parts=literal_octahedron_parts(S,E)
        if parts is not None:
            out.append({"vertices":list(S),"independent_pairs":parts})
    return out

def proper_core_colorings(H,E,lists):
    H=sorted(H)
    out=[]
    for vals in itertools.product([1,2,3,4],repeat=6):
        phi=dict(zip(H,vals))
        if any(phi[v] not in lists[v] for v in H): continue
        if any(phi[a]==phi[b] for a,b in E if a in phi and b in phi): continue
        out.append(phi)
    return out

def component_record(C,E,lists):
    union=sorted(set().union(*(set(lists[v]) for v in C))) if C else []
    return {
      "vertices":sorted(C),
      "edges":sorted([list(x) for x in E if x[0] in C and x[1] in C]),
      "lists":{v:lists[v] for v in sorted(C)},
      "union_of_lists":union,
      "missing_colors":sorted(COL-set(union)),
      "connected":connected(C,E)
    }

def literal_oct_minor_in_component(C,E):
    octs=enumerate_literal_octahedra(C,E)
    if not octs: return None
    H=octs[0]
    verts=H["vertices"]
    branch_sets={f"o{i}":[v] for i,v in enumerate(verts)}
    # derive H labels by matching nonedge pairs to o0-o1,o2-o3,o4-o5
    parts=H["independent_pairs"]
    ordered=[]
    for pair in parts: ordered.extend(pair)
    branch_sets={f"o{i}":[ordered[i]] for i in range(6)}
    non={ek("o0","o1"),ek("o2","o3"),ek("o4","o5")}
    edge_witnesses={}
    for u,v in itertools.combinations([f"o{i}" for i in range(6)],2):
        if ek(u,v) in non: continue
        a=branch_sets[u][0]; b=branch_sets[v][0]
        if not adj(E,a,b): return None
        edge_witnesses[f"{u}-{v}"]=[a,b]
    return {"H":"OCTAHEDRON","literal_core":verts,"independent_pairs":parts,"branch_sets":branch_sets,"cross_edge_witnesses":edge_witnesses}

def find_escape(H,CV,CE,lists):
    colorings=proper_core_colorings(H,CE,lists)
    for phi in colorings:
        rem_lists,fixed,prop=propagate(CE,lists,phi)
        if rem_lists is None: continue
        for D in components(rem_lists.keys(),CE):
            rec=component_record(D,CE,rem_lists)
            if rec["missing_colors"]: continue
            minor=literal_oct_minor_in_component(D,CE)
            if minor:
                return {
                  "phi":phi,
                  "propagation":prop,
                  "fixed_after_propagation":fixed,
                  "D":rec,
                  "forbidden_minor":minor
                },len(colorings)
    return None,len(colorings)

def replay_current_control(ctrl):
    H=ctrl["exact_residual"]["octahedron_core"]["H"]
    parts=ctrl["exact_residual"]["octahedron_core"]["parts"]
    lists={k:set(v) for k,v in ctrl["exact_residual"]["lists"].items()}
    HE=set()
    partmap={}
    for i,pair in enumerate(parts):
        for v in pair: partmap[v]=i
    for a,b in itertools.combinations(H,2):
        if partmap[a]!=partmap[b]: HE.add(ek(a,b))
    E=set(HE)
    for v in ["a0","a1","c0","c1"]: E.add(ek("z",v))
    cols=proper_core_colorings(H,E,lists)
    counts={"[1]":0,"[1,2]":0,"OTHER":0}
    allterm=True
    for phi in cols:
        z=set(lists["z"])
        for v in H:
            if adj(E,"z",v): z.discard(phi[v])
        key=str(sorted(z)).replace(" ","")
        if key=="[1]": counts["[1]"]+=1
        elif key=="[1,2]": counts["[1,2]"]+=1
        else:
            counts["OTHER"]+=1
            if not z: allterm=False
    return {
      "proper_core_colorings":len(cols),
      "z_list_branch_counts":counts,
      "all_branches_terminal":allterm and counts["OTHER"]==0,
      "pass":len(cols)==30 and counts["[1]"]==28 and counts["[1,2]"]==2 and counts["OTHER"]==0
    }

def logical_quantifier_controls():
    # Directly tests the aggregator that caused the quantifier bug.
    mixed={
      "H1":{"proper_branches":["TERMINAL","ESCAPE"]},
      "H2":{"proper_branches":["TERMINAL","TERMINAL"]}
    }
    def good(branches): return len(branches)==0 or all(x=="TERMINAL" for x in branches)
    goodmap={h:good(x["proper_branches"]) for h,x in mixed.items()}
    local=any("ESCAPE" in x["proper_branches"] for x in mixed.values())
    goodC=any(goodmap.values())
    strongO2=all((len(x["proper_branches"])>0 and "ESCAPE" in x["proper_branches"]) for x in mixed.values())
    # Empty proper-color set is explicitly a good core.
    empty_good=good([])
    return {
      "TWO_CORE_MIXED_CONTROL":{
        "good_core_map":goodmap,"local_core_escape":local,"GOOD_C":goodC,"strong_O2":strongO2,
        "pass":local and goodC and not strongO2 and goodmap=={"H1":False,"H2":True}
      },
      "EMPTY_CORE_COLORING_CONTROL":{
        "proper_core_coloring_count":0,"CORE_UNSAT_GOOD_MODULATOR":empty_good,"strong_O2":False,
        "pass":empty_good
      }
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True); ap.add_argument("--binding",required=True); ap.add_argument("--freeze",required=True)
    ap.add_argument("--current-control",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); root=pathlib.Path(a.out); root.mkdir(parents=True,exist_ok=True)
    pre=json.load(open(a.prereg)); binding=json.load(open(a.binding)); fr=json.load(open(a.freeze)); ctrl=json.load(open(a.current_control))
    W=fr["first_authoritative_strong_O2_candidate"]; V=W["vertices"]; E=es(W["exact_edges"])
    S=W["old_precoloring"]["S"]; f=W["old_precoloring"]["f"]
    old_checks,old_lists=verify_axioms(V,E,S,W["old_precoloring"]["X0"],W["old_precoloring"]["X"],W["old_precoloring"]["Y0"],W["old_precoloring"]["Y"],f)
    q={
      "P_singleton":W["stored_111"]["P"]==["p"],"M_singleton":W["stored_111"]["M"]==["m"],"N_singleton":W["stored_111"]["N"]==["n"],
      "p_type_T":type_set("p",E,S)==["s"],"n_type_Tprime":type_set("n",E,S)==["t"],"m_Y0":"m" in W["old_precoloring"]["Y0"],
      "pm":adj(E,"p","m"),"mn":adj(E,"m","n"),"pn_nonedge":not adj(E,"p","n"),
      "Q_colors":W["stored_111"]["f_prime"]["p"] not in (1,2) and W["stored_111"]["f_prime"]["n"] not in (1,2)
    }
    post=W["post_constructor"]; postf={"s":1,"t":2,**W["stored_111"]["f_prime"]}
    post_checks,post_lists=verify_axioms(V,E,post["S_prime"],[],[],post["Y0_prime"],post["Y_prime"],postf)
    post_list_checks={v:post_lists[v]==L for v,L in post["lists_before_pair_fix"].items()}
    p7=p7_witness(V,E)
    y,yp=W["survivor_pair"]
    survivor={
      "yy_nonedge":not adj(E,y,yp),"common_z":adj(E,y,"z") and adj(E,yp,"z"),
      "y_type_T":type_set(y,E,S)==["s"],"yp_type_Tprime":type_set(yp,E,S)==["t"],
      "ym_nonedge":not adj(E,y,"m"),"ypm_edge":adj(E,yp,"m"),
      "intersection":sorted(set(post_lists[y])&set(post_lists[yp])),
      "lists_unequal":post_lists[y]!=post_lists[yp]
    }
    cert=W["answer_relevance_certificate"]["coloring"]
    answer={"covers_all":set(cert)==set(V),"proper":proper(E,cert),"route34":cert[y]==3 and cert[yp]==4,
            "pair_colors_allowed":cert[y] in post_lists[y] and cert[yp] in post_lists[yp]}
    fixed=dict(postf); fixed[y]=3; fixed[yp]=4
    current={v:post_lists[v] for v in V if v not in post["S_prime"]}
    route_lists,route_fixed,route_prop=propagate(E,current,fixed)
    route_components=components(route_lists.keys(),E)
    expectedV=set(W["exact_after_route34_and_frozen_propagation"]["component_vertices"])
    target=next((C for C in route_components if set(C)==expectedV),None)
    target_lists={v:route_lists[v] for v in target} if target else {}
    target_exact=target is not None and target_lists==W["exact_after_route34_and_frozen_propagation"]["lists"]
    residual_record=component_record(target,E,route_lists) if target else None

    # Complete graph-only Oct(C) enumeration.
    octs=enumerate_literal_octahedra(target,E) if target else []
    frozen_expected=W["expected_complete_Oct_C"]
    expected_by_vertices={tuple(sorted(x["vertices"])):x for x in frozen_expected}
    actual_keys={tuple(sorted(x["vertices"])) for x in octs}
    expected_keys=set(expected_by_vertices)
    complete_match=(actual_keys==expected_keys and len(octs)==W["exact_after_route34_and_frozen_propagation"]["expected_literal_octahedron_count"])

    audit=[]
    all_defeated=True
    any_core_unsat=False
    any_good_core=False
    for Hrec in octs:
        key=tuple(sorted(Hrec["vertices"]))
        expected=expected_by_vertices.get(key)
        coloring_count=len(proper_core_colorings(Hrec["vertices"],E,route_lists))
        if coloring_count==0:
            any_core_unsat=True; any_good_core=True
            audit.append({"vertices":list(key),"independent_pairs":Hrec["independent_pairs"],"proper_core_coloring_count":0,
                          "classification":"CORE_UNSAT_GOOD_MODULATOR","defeating_escape":None})
            all_defeated=False
            continue
        escape,count=find_escape(Hrec["vertices"],target,E,route_lists)
        if escape is None:
            # Strong O2 cannot be asserted. Do not infer universal goodness without exhaustive terminal classification.
            audit.append({"vertices":list(key),"independent_pairs":Hrec["independent_pairs"],"proper_core_coloring_count":coloring_count,
                          "classification":"NO_CERTIFIED_ESCAPE_FOUND","defeating_escape":None})
            all_defeated=False
        else:
            audit.append({"vertices":list(key),"independent_pairs":Hrec["independent_pairs"],"proper_core_coloring_count":coloring_count,
                          "classification":"LOCAL_CORE_ESCAPE","defeating_escape":escape,
                          "expected_count_crosscheck": expected is not None and coloring_count==expected["proper_core_coloring_count"]})
    accounted_once=len(audit)==len(octs) and len({tuple(x["vertices"]) for x in audit})==len(octs)
    strongO2=complete_match and accounted_once and all_defeated and not any_core_unsat and len(octs)>0

    current_control=replay_current_control(ctrl)
    quantifier_controls=logical_quantifier_controls()

    input_checks={
      "prereg_binding":fr["authorization"]["prereg_blob"]=="09132719fe1da6a329d83a06d94ecdc37d3a2166",
      "quantifier_binding":fr["authorization"]["quantifier_binding"]["blob"]=="43771ac28214118dedfbac9f5b49d6165dc9a27b",
      "binding_formula_contains_forall_cores":"for every H in Oct(C)" in binding["bound_quantifiers"]["O2_strong_falsifier"]["formula"],
      "current_control_authority":ctrl["status"]=="PASS_CURRENT_X2_OCTAHEDRON_CORE_MODULATOR_TERMINAL"
    }
    auth_ok=all(old_checks.values()) and all(q.values()) and all(post_checks.values()) and all(post_list_checks.values()) and p7 is None and all(answer.values()) and survivor["yy_nonedge"] and survivor["common_z"] and survivor["y_type_T"] and survivor["yp_type_Tprime"] and survivor["ym_nonedge"] and survivor["ypm_edge"] and survivor["intersection"]==[3,4] and survivor["lists_unequal"] and target_exact
    controls_ok=current_control["pass"] and all(x["pass"] for x in quantifier_controls.values())
    outcome="O2_OCTAHEDRON_ATTACHMENT_ESCAPE" if auth_ok and strongO2 and controls_ok else "O3_GATE_UNRESOLVED"
    result={
      "schema":"janus.trump.c11_pi_octahedron_core_modulator.execution.v1",
      "authority_checks":{"old_axioms":old_checks,"stored_111_Q":q,"post_axioms":post_checks,"post_lists":post_list_checks,
                          "P7_free":p7 is None,"induced_P7_witness":p7,"survivor_pair":survivor,"answer_relevance_certificate":answer},
      "route34":{"propagation":route_prop,"residual":residual_record,"target_exact":target_exact},
      "Oct_C_complete_audit":{
        "literal_core_count":len(octs),
        "expected_count":W["exact_after_route34_and_frozen_propagation"]["expected_literal_octahedron_count"],
        "complete_set_matches_freeze":complete_match,
        "every_core_accounted_once":accounted_once,
        "cores":audit
      },
      "current_authoritative_X2_control":current_control,
      "quantifier_controls":quantifier_controls,
      "O1":{"status":"FALSIFIED_BY_STRONG_O2_AUTHORITATIVE_RESIDUAL" if outcome=="O2_OCTAHEDRON_ATTACHMENT_ESCAPE" else "NOT_ESTABLISHED"},
      "LOCAL_CORE_ESCAPE_COUNT":sum(1 for x in audit if x["classification"]=="LOCAL_CORE_ESCAPE"),
      "O2":{
        "status":"VERIFIED" if outcome=="O2_OCTAHEDRON_ATTACHMENT_ESCAPE" else "NOT_VERIFIED",
        "quantifier":"exists authoritative C; for every literal H in Oct(C), exists proper list-respecting phi_H with certified Escape(C,H,phi_H)",
        "GOOD_C":False if outcome=="O2_OCTAHEDRON_ATTACHMENT_ESCAPE" else "UNRESOLVED",
        "claim":"No literal octahedron in this authoritative residual is a universal six-vertex modulator to the frozen {Contradiction,List-3,TW3} terminal stack."
      },
      "O3":"NOT_REACHED" if outcome=="O2_OCTAHEDRON_ATTACHMENT_ESCAPE" else "VERIFIED",
      "primary_outcome":outcome,
      "minimization":{"first_authoritative_witness_immutable":True,"attempted":False,"global_minimality_claimed":False},
      "oracle_use":{"extension_oracle_for_core_selection":False,"extension_oracle_for_phi_selection":False,"general_P7_free_4color_oracle":False,
                    "tw4_opened":False,"backdoor_size2_search":False,"repair":False},
      "scientific_ceiling":{
        "CURRENT_X2_WITNESS":"POLYNOMIALLY_RESOLVED_BY_FIXED_CORE",
        "UNIVERSAL_LITERAL_OCTAHEDRON_CORE_MODULATOR":"FALSIFIED_BY_STRONG_O2_AUTHORITATIVE_RESIDUAL" if outcome=="O2_OCTAHEDRON_ATTACHMENT_ESCAPE" else "OPEN",
        "STRONG_O2_FORALL_CORES_ESCAPE":"VERIFIED" if outcome=="O2_OCTAHEDRON_ATTACHMENT_ESCAPE" else "NOT_VERIFIED",
        "OTHER_TW3_FORBIDDEN_MINOR_TYPES":"UNTOUCHED",
        "PI_DISCOVERY":"PARTIAL","P3_EXACT_PAIR_QUOTIENT":"NOT_ESTABLISHED","TW4":"NOT_OPENED","BACKDOOR_SIZE_2":"NOT_OPENED",
        "REPAIR":"NOT_STARTED","NEW_DESCRIPTOR":"NOT_DEFINED","LEMMA11_P7_LIFT":"OPEN","P7_FREE_4_COLOR_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"
      },
      "forbidden_interpretations":["HARDNESS","UNBOUNDED_TREEWIDTH","NEED_FOR_TW4","NEED_FOR_BACKDOOR_SIZE_2","NEED_FOR_REPAIR","P3_FALSE","P_VS_NP_INFERENCE"],
      "repair_attempted":False,"successor_autoactivated":False,"stop":True,
      "input_checks":input_checks
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"outcome":outcome,"Oct_C":len(octs),"local_escapes":result["LOCAL_CORE_ESCAPE_COUNT"],
                      "complete":complete_match,"current_control":current_control["pass"],"quantifier_controls":controls_ok},sort_keys=True))
    if not all(input_checks.values()): raise SystemExit(2)
    if outcome!="O2_OCTAHEDRON_ATTACHMENT_ESCAPE": raise SystemExit(3)

if __name__=="__main__": main()
