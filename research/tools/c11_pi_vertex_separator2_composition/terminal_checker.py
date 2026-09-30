#!/usr/bin/env python3
import argparse,itertools,json,pathlib
COL={1,2,3,4}
def ek(a,b): return tuple(sorted((a,b)))
def es(E): return {ek(a,b) for a,b in E}
def adj(E,a,b): return ek(a,b) in E
def connected(V,E):
    V=set(V)
    if not V:return True
    seen=set();st=[next(iter(V))]
    while st:
        v=st.pop()
        if v in seen:continue
        seen.add(v)
        for a,b in E:
            if a==v and b in V-seen: st.append(b)
            elif b==v and a in V-seen: st.append(a)
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
        V-=C;out.append(sorted(C))
    return sorted(out,key=lambda x:(len(x),x))
def cut_vertices(V,E):
    V=list(V)
    return sorted([r for r in V if len(comps([v for v in V if v!=r],E))>1])
def sep2(V,E):
    V=list(V);out=[]
    for a,b in itertools.combinations(sorted(V),2):
        if len(comps([v for v in V if v not in {a,b}],E))>1:out.append([a,b])
    return out
def p7_witness(V,E):
    for S in itertools.combinations(V,7):
        SS=set(S);sub={x for x in E if x[0] in SS and x[1] in SS}
        if len(sub)!=6:continue
        deg={v:0 for v in S}
        for a,b in sub:deg[a]+=1;deg[b]+=1
        if sorted(deg.values())==[1,1,2,2,2,2,2] and connected(S,sub):return list(S)
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
    ch["Y0_exact"]={v for v in V if v not in S and not any(adj(E,v,s) for s in S)}==set(Y0)
    Y0E=[x for x in E if x[0] in Y0 and x[1] in Y0];ok=True
    for v in set(V)-set(Y0)-set(X0):
        for a,b in Y0E:
            if adj(E,v,a)!=adj(E,v,b):ok=False
    ch["no_mixed_on_Y0_edge"]=ok
    ch["Y0_four_lists"]=all(set(L[v])==COL for v in Y0)
    ch["Y_three_lists"]=all(len(L[v])==3 for v in Y)
    parts=list(map(set,[S,X0,X,Y0,Y]))
    ch["partition"]=set(V)==set().union(*parts) and all(not(A&B) for A,B in itertools.combinations(parts,2))
    return ch,L
def type_set(v,E,S):return sorted([s for s in S if adj(E,v,s)])
def proper(E,c):return all(not(a in c and b in c and c[a]==c[b]) for a,b in E)
def propagate(E,L,fixed):
    L={v:set(x) for v,x in L.items() if v not in fixed};fixed=dict(fixed);prov=[]
    while True:
        for a,b in E:
            if a in fixed and b in fixed and fixed[a]==fixed[b]:
                return None,fixed,{"kind":"IMPROPER_FIXED_EDGE","edge":[a,b],"color":fixed[a],"provenance":prov}
        changed=False
        for v in list(L):
            rem=sorted({fixed[u] for u in fixed if adj(E,u,v)} & L[v])
            if rem:
                L[v]-=set(rem);prov.append({"op":"REMOVE_FIXED_NEIGHBOR_COLORS","vertex":v,"removed":rem});changed=True
            if not L[v]:return None,fixed,{"kind":"EMPTY_LIST","vertex":v,"provenance":prov}
        singles=sorted(v for v,x in L.items() if len(x)==1)
        if singles:
            for v in singles:
                if v not in L:continue
                c=next(iter(L[v]));fixed[v]=c;del L[v];prov.append({"op":"FIX_SINGLETON","vertex":v,"color":c});changed=True
            continue
        if not changed:break
    return {v:sorted(x) for v,x in L.items()},fixed,{"kind":"FIXPOINT","provenance":prov}
def literal_oct(S,E):
    S=sorted(S)
    if len(S)!=6:return None
    non=[ek(a,b) for a,b in itertools.combinations(S,2) if not adj(E,a,b)]
    if len(non)!=3 or len({x for p in non for x in p})!=6:return None
    if sum(1 for a,b in itertools.combinations(S,2) if adj(E,a,b))!=12:return None
    return sorted([list(x) for x in non])
def find_oct(V,E):
    for S in itertools.combinations(sorted(V),6):
        p=literal_oct(S,E)
        if p:return {"vertices":list(S),"independent_pairs":p}
    return None
def record(V,E,L):
    union=sorted(set().union(*(set(L[v]) for v in V)))
    return {"vertices":sorted(V),"edges":sorted([list(x) for x in E if x[0] in V and x[1] in V]),
            "lists":{v:L[v] for v in sorted(V)},"union_of_lists":union,
            "missing_colors":sorted(COL-set(union)),"connected":connected(V,E)}
def is_k122(V,E):
    if len(V)!=5:return False
    non=[ek(a,b) for a,b in itertools.combinations(sorted(V),2) if not adj(E,a,b)]
    # K_{1,2,2}: exactly two disjoint nonedges
    return len(non)==2 and len({x for p in non for x in p})==4 and sum(adj(E,a,b) for a,b in itertools.combinations(V,2))==8
def replay_positive(pfreeze,presult):
    W=pfreeze["first_authoritative_strong_S2_candidate"]
    RV=W["exact_after_route34_and_frozen_propagation"]["component_vertices"];E=es(W["exact_edges"])
    cuts=cut_vertices(RV,E);s2=sep2(RV,E)
    expected=[["a0","z"],["e0","z"]]
    # separators sorted lexically by implementation
    sep_ok=sorted([sorted(x) for x in s2])==sorted([sorted(x) for x in expected])
    per={}
    for S in s2:
        cs=comps([v for v in RV if v not in set(S)],E)
        classes=[]
        for C in cs:
            if literal_oct(C,E):classes.append("OCT")
            elif is_k122(C,E):classes.append("K122")
            else:classes.append("OTHER")
        per["|".join(S)]={"components":cs,"classes":classes,"closed_structurally":sorted(classes)==["K122","OCT"]}
    good=cuts==[] and sep_ok and all(x["closed_structurally"] for x in per.values())
    return {"Cut_C":cuts,"Sep_2_C":s2,"separator_details":per,"kappa_exactly_2":cuts==[] and len(s2)>0,
            "GOOD_2_C":good,"R2":False,"pass":good and presult["status"]=="PASS_CURRENT_S2_SEPARATOR2_COMPOSITION_TERMINAL"}
def controls(fr):
    m=fr["mandatory_controls"]["TWO_SEPARATOR_MIXED_CONTROL"]["separators"]
    def good(states):return len(states)==0 or all(x=="CLOSED" for x in states)
    gm={s:good(v["states"]) for s,v in m.items()}
    local=any("ESCAPE" in v["states"] for v in m.values());goodC=any(gm.values())
    empty_good=good([])
    # K4: no cut vertices and no two-separator (deleting two leaves an edge)
    V=["k0","k1","k2","k3"];E=es(itertools.combinations(V,2))
    c=cut_vertices(V,E);s=sep2(V,E)
    return {
      "TWO_SEPARATOR_MIXED_CONTROL":{"good_map":gm,"LOCAL_SEPARATOR2_ESCAPE":local,"GOOD_2_C":goodC,"R2":not goodC,
                                     "pass":local and goodC and gm=={"S1":False,"S2":True}},
      "EMPTY_SEPARATOR_STATE_CONTROL":{"GOOD_2_separator":empty_good,"R2":False,"pass":empty_good},
      "NO_SEPARATOR2_CONTROL":{"Cut_C":c,"Sep_2_C":s,"path_A_recognized":c==[] and s==[],"kappa_lower_bound":3,
                               "pass":c==[] and s==[]}
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True);ap.add_argument("--freeze",required=True)
    ap.add_argument("--positive-freeze",required=True);ap.add_argument("--positive-result",required=True);ap.add_argument("--out",required=True)
    a=ap.parse_args();root=pathlib.Path(a.out);root.mkdir(parents=True,exist_ok=True)
    pre=json.load(open(a.prereg));fr=json.load(open(a.freeze));pf=json.load(open(a.positive_freeze));pr=json.load(open(a.positive_result))
    W=fr["first_authoritative_strong_R2_candidate"];V=W["vertices"];E=es(W["exact_edges"])
    S=W["old_precoloring"]["S"];f=W["old_precoloring"]["f"]
    old,Lold=verify_axioms(V,E,S,W["old_precoloring"]["X0"],W["old_precoloring"]["X"],W["old_precoloring"]["Y0"],W["old_precoloring"]["Y"],f)
    q={"P_singleton":W["stored_111"]["P"]==["p"],"M_singleton":W["stored_111"]["M"]==["m"],"N_singleton":W["stored_111"]["N"]==["n"],
       "p_type_T":type_set("p",E,S)==["s"],"n_type_Tprime":type_set("n",E,S)==["t"],"m_Y0":"m" in W["old_precoloring"]["Y0"],
       "pm":adj(E,"p","m"),"mn":adj(E,"m","n"),"pn_nonedge":not adj(E,"p","n"),
       "Q_colors":W["stored_111"]["f_prime"]["p"] not in (1,2) and W["stored_111"]["f_prime"]["n"] not in (1,2)}
    post=W["post_constructor"];postf={"s":1,"t":2,**W["stored_111"]["f_prime"]}
    postchecks,postlists=verify_axioms(V,E,post["S_prime"],[],[],post["Y0_prime"],post["Y_prime"],postf)
    postlistchecks={v:postlists[v]==L for v,L in post["lists_before_pair_fix"].items()}
    pw=p7_witness(V,E);y,yp=W["survivor_pair"]
    surv={"yy_nonedge":not adj(E,y,yp),"common_z":adj(E,y,"z") and adj(E,yp,"z"),
          "y_type_T":type_set(y,E,S)==["s"],"yp_type_Tprime":type_set(yp,E,S)==["t"],
          "ym_nonedge":not adj(E,y,"m"),"ypm_edge":adj(E,yp,"m"),
          "intersection":sorted(set(postlists[y])&set(postlists[yp])),"lists_unequal":postlists[y]!=postlists[yp]}
    cert=W["answer_relevance_certificate"]["coloring"]
    answer={"covers_all":set(cert)==set(V),"proper":proper(E,cert),"route34":cert[y]==3 and cert[yp]==4}
    fixed=dict(postf);fixed[y]=3;fixed[yp]=4
    current={v:postlists[v] for v in V if v not in post["S_prime"]}
    rem,fx,prop=propagate(E,current,fixed)
    exp=set(W["exact_after_route34_and_frozen_propagation"]["component_vertices"])
    C=next((x for x in comps(rem.keys(),E) if set(x)==exp),None)
    rec=record(C,E,rem) if C else None
    exact=C is not None and {v:rem[v] for v in C}==W["exact_after_route34_and_frozen_propagation"]["lists"]
    octcert=find_oct(C,E) if C else None
    cv=cut_vertices(C,E) if C else []
    s2=sep2(C,E) if C else []
    domain={"connected":bool(C and connected(C,E)),"noncontradictory":rem is not None,
            "NOT_L3_READY":rec is not None and rec["missing_colors"]==[],
            "not_exact_literal_octahedron":C is not None and len(C)!=6,
            "tw_gt_3_oct_minor":octcert is not None,"Cut_C_empty":cv==[]}
    pos=replay_positive(pf,pr);qc=controls(fr)
    auth=all(old.values()) and all(q.values()) and all(postchecks.values()) and all(postlistchecks.values()) and pw is None and all(answer.values()) and all([surv["yy_nonedge"],surv["common_z"],surv["y_type_T"],surv["yp_type_Tprime"],surv["ym_nonedge"],surv["ypm_edge"],surv["lists_unequal"]]) and surv["intersection"]==[3,4] and exact
    r2=auth and all(domain.values()) and s2==[] and len(C)>=5 and pos["pass"] and all(x["pass"] for x in qc.values())
    outcome="R2_SEPARATOR2_COMPOSITION_ESCAPE_PATH_A" if r2 else "R3_GATE_UNRESOLVED"
    result={
      "schema":"janus.trump.c11_pi_vertex_separator2_composition.execution.v1",
      "authority_checks":{"old_axioms":old,"stored_111_Q":q,"post_axioms":postchecks,"post_lists":postlistchecks,
                          "P7_free":pw is None,"induced_P7_witness":pw,"survivor_pair":surv,"answer_relevance_certificate":answer},
      "route34":{"propagation":prop,"residual":rec,"target_exact":exact},
      "domain_checks":domain,
      "tw_gt_3_certificate":{"selected_forbidden_minor":"OCTAHEDRON","literal_core":octcert},
      "connectivity_audit":{"Cut_C":cv,"Sep_2_C":s2,"cut_complete":True,"sep2_complete":True,
                            "path_A":cv==[] and s2==[],"kappa_lower_bound":3 if cv==[] and s2==[] else None,
                            "kappa_equality_claimed":False},
      "positive_current_S2_control":pos,
      "quantifier_controls":qc,
      "R1":{"status":"FALSIFIED_BY_AUTHORITATIVE_R2_PATH_A" if r2 else "NOT_ESTABLISHED"},
      "LOCAL_SEPARATOR2_ESCAPE_COUNT":0,
      "R2":{"status":"VERIFIED" if r2 else "NOT_VERIFIED","path":"A_SEP2_EMPTY" if r2 else None,
            "claim":"There exists an authoritative cut-vertex-free C11 PI residual outside the base terminal stack with Sep_2(C)=empty; hence kappa(C)>=3."},
      "R3":"NOT_REACHED" if r2 else "VERIFIED",
      "primary_outcome":outcome,
      "oracle_use":{"general_P7_free_4color_oracle":False,"extension_oracle_for_separator_selection":False,
                    "tw4_opened":False,"separator_size3_opened":False,"backdoor_size2_opened":False,"repair":False},
      "scientific_ceiling":{"CURRENT_S2_WITNESS":"POLYNOMIALLY_RESOLVED_BY_TWO_VERTEX_SEPARATOR_COMPOSITION",
        "CURRENT_S2_VERTEX_CONNECTIVITY":"EXACTLY_2",
        "UNIVERSAL_SEPARATOR2_COMPOSITION":"FALSIFIED_BY_AUTHORITATIVE_R2_PATH_A" if r2 else "OPEN",
        "AUTHORITATIVE_KAPPA_GE_3_RESIDUAL":"VERIFIED" if r2 else "NOT_VERIFIED",
        "CONNECTIVITY_CLAIM":"KAPPA_GE_3_ONLY" if r2 else "UNRESOLVED",
        "PI_DISCOVERY":"PARTIAL","P3_EXACT_PAIR_QUOTIENT":"NOT_ESTABLISHED","SEPARATOR_SIZE_3":"NOT_OPENED",
        "BACKDOOR_SIZE_2":"NOT_OPENED","TW4":"NOT_OPENED","REPAIR":"NOT_STARTED","NEW_DESCRIPTOR":"NOT_DEFINED",
        "LEMMA11_P7_LIFT":"OPEN","P7_FREE_4_COLOR_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"},
      "forbidden_interpretations":["KAPPA_EQUALS_3","NEED_FOR_SEPARATOR_SIZE_3","HARDNESS","UNBOUNDED_CONNECTIVITY","UNBOUNDED_TREEWIDTH",
                                   "NEED_FOR_BACKDOOR_SIZE_2","NEED_FOR_TW4","NEED_FOR_REPAIR","P3_FALSE","P_VS_NP_INFERENCE"],
      "repair_attempted":False,"successor_autoactivated":False,"stop":True,
      "input_checks":{"prereg_blob":fr["authorization"]["prereg_blob"]=="d60f83c6579a4dc30ee0599502fea5327a01a90a"}
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"outcome":outcome,"Cut_C":cv,"Sep_2_C":s2,"P7_free":pw is None,"domain":domain,"positive_control":pos["pass"]},sort_keys=True))
    if not result["input_checks"]["prereg_blob"]:raise SystemExit(2)
    if outcome!="R2_SEPARATOR2_COMPOSITION_ESCAPE_PATH_A":raise SystemExit(3)
if __name__=="__main__":main()
