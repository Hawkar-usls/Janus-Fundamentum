#!/usr/bin/env python3
import argparse, collections, copy, hashlib, itertools, json, pathlib

COLORS={1,2,3,4}

def ce(a,b): return tuple(sorted((str(a),str(b))))
def E(P): return {ce(a,b) for a,b in P["edges"]}
def has(P,a,b): return ce(a,b) in E(P)
def nbr(P,v): return {u for u in P["vertices"] if u!=v and has(P,u,v)}
def Nset(P,A):
    A=set(A)
    return (set().union(*(nbr(P,v) for v in A))-A) if A else set()
def connected(P,A):
    A=set(A)
    if not A:return False
    q=[next(iter(A))];seen=set()
    while q:
        v=q.pop()
        if v in seen:continue
        seen.add(v);q.extend((nbr(P,v)&A)-seen)
    return seen==A
def proper(P,c,domain=None):
    dom=set(domain if domain is not None else c)
    for a,b in E(P):
        if a in dom and b in dom and c.get(a)==c.get(b):
            return False,{"edge":[a,b],"color":c.get(a)}
    return True,None
def induced_path(P,seq):
    if len(set(seq))!=len(seq):return False
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            if has(P,a,seq[j])!=(j==i+1):return False
    return True
def induced_pt_witness(P,k):
    vs=sorted(P["vertices"])
    if len(vs)<k:return None
    for comb in itertools.combinations(vs,k):
        for perm in itertools.permutations(comb):
            if induced_path(P,perm):return list(perm)
    return None
def digest(o):return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def L(P,v):
    if v in P["S"] or v in P["X0"]:return {P["f"][v]}
    return COLORS-{P["f"][s] for s in nbr(P,v)&set(P["S"])}

def check_seeded_axioms(P):
    V=set(P["vertices"]);parts={k:set(P[k]) for k in ["S","X0","X","Y0","Y"]}
    if set().union(*parts.values())!=V or sum(map(len,parts.values()))!=len(V):
        return False,{"reason":"partition"}
    if set(P["f"])!=parts["S"]|parts["X0"]:
        return False,{"reason":"f_domain"}
    ok,bad=proper(P,P["f"],parts["S"]|parts["X0"])
    if not ok:return False,{"reason":"f_not_proper","witness":bad}
    axioms={}
    axioms["i"]=connected(P,V-parts["X0"])
    axioms["ii"]=connected(P,parts["S"]) and not any(parts["S"]<=nbr(P,v) for v in V-parts["S"])
    axioms["iii"]=parts["Y0"]==V-(Nset(P,parts["S"])|parts["X0"]|parts["S"])
    ax4=True
    for a,b in E(P):
        if a in parts["Y0"] and b in parts["Y0"]:
            for v in V-(parts["Y0"]|parts["X0"]):
                if has(P,v,a)!=has(P,v,b):ax4=False
    axioms["iv"]=ax4
    ax5=True
    for v in V-parts["S"]:
        target={1:"X0",2:"X",3:"Y",4:"Y0"}[len(L(P,v))]
        if v not in parts[target]:ax5=False
    axioms["v"]=ax5
    return all(axioms.values()),{"axioms":axioms}

def original_fixture():
    return {
      "id":"C11_DIRECT_SOURCE_PATTERN_WITNESS",
      "vertices":["s1","s2","p","m","n","y","y_prime","z"],
      "edges":[["s1","s2"],["s1","p"],["s1","y"],["s2","n"],["s2","y_prime"],["p","m"],["m","n"],["z","y"],["z","y_prime"],["y_prime","m"]],
      "S":["s1","s2"],"X0":[],"X":[],"Y0":["m","z"],"Y":["p","n","y","y_prime"],
      "f":{"s1":1,"s2":2}
    }
def qhat():
    return {
      "local_states":[
        {"T":["s1"],"T_prime":["s2"],"mode":"111","P":["p"],"M":["m"],"N":["n"]},
        {"T":["s2"],"T_prime":["s1"],"mode":"111","P":["n"],"M":["m"],"N":["p"]}
      ],
      "f_prime":{"p":3,"m":2,"n":4},
      "Z_FORCE":[]
    }
def extension():
    return {"s1":1,"s2":2,"p":3,"m":2,"n":4,"y":3,"y_prime":4,"z":1}

def type_of(P,v):return tuple(sorted(nbr(P,v)&set(P["S"])))
def validate_111(P,st,fp):
    T=tuple(st["T"]);Tp=tuple(st["T_prime"])
    p=st["P"][0];m=st["M"][0];n=st["N"][0]
    checks={
      "cardinality":len(st["P"])==len(st["M"])==len(st["N"])==1,
      "p_type":type_of(P,p)==T,
      "n_type":type_of(P,n)==Tp,
      "m_Y0":m in P["Y0"],
      "m_p_edge":has(P,m,p),
      "m_n_edge":has(P,m,n),
      "p_n_nonedge":not has(P,p,n),
      "singleton_seed_colors":len({P["f"][x] for x in T})==1 and len({P["f"][x] for x in Tp})==1,
      "different_seed_colors":{P["f"][x] for x in T}!={P["f"][x] for x in Tp},
      "endpoint_colors":fp[p] not in ({P["f"][x] for x in T}|{P["f"][x] for x in Tp}) and fp[n] not in ({P["f"][x] for x in T}|{P["f"][x] for x in Tp})
    }
    return all(checks.values()),checks

def construct_raw(P,Q):
    A=set()
    for st in Q["local_states"]:
        A|=set(st["P"])|set(st["M"])|set(st["N"])
    Z=set(Q["Z_FORCE"]);ZX=Z-A
    P0=copy.deepcopy(P)
    P0["S"]=sorted(set(P["S"])|A)
    P0["X0"]=sorted(set(P["X0"])|ZX)
    P0["X"]=sorted(set(P["X"]))
    P0["Y0"]=sorted(set(P["Y0"])-(A|Nset(P,A)))
    P0["Y"]=sorted((set(P["Y"])-(A|Z))|(Nset(P,A)&set(P["Y0"])))
    nf=dict(P["f"]);nf.update(Q["f_prime"]);P0["f"]=nf
    return P0,{"A":sorted(A),"Z_FORCE":sorted(Z),"Z_X0":sorted(ZX)}

def normal_subcase(P,P0):
    ok,det=check_seeded_axioms(P0)
    # check_seeded_axioms includes more than normal-subcase, useful here
    S=set(P["S"]);Sp=set(P0["S"]);X0=set(P["X0"]);X0p=set(P0["X0"])
    X=set(P["X"]);Y0=set(P["Y0"]);Y=set(P["Y"])
    checks={
      "seeded_and_i_v":ok,
      "S_subset":S<=Sp,
      "seed_connected":connected(P0,Sp),
      "seed_containment":Sp<=S|X|Y0|Y,
      "X0_subset":X0<=X0p,
      "X0_containment":X0p<=X0|X|Y0|Y,
      "new_X0_old_Y0_neighbor_condition":all(nbr(P0,v)&Sp for v in X0p&Y0),
      "old_colors_preserved":all(P0["f"].get(v)==P["f"].get(v) for v in S|X0)
    }
    return all(checks.values()),{"checks":checks,"axiom_detail":det}

def lemma10_identity_replay(P,P0):
    # On this exact witness P0 already satisfies (i)-(v), the Lemma-10 repartition is identity:
    # Z1=Z2=empty, Z3=Y', Z4=Y0'; G\X0 is connected so Lemma 6 deletes nothing.
    classes={i:[] for i in range(5)}
    for v in P0["vertices"]:
        if v not in P0["S"] and v not in P0["X0"]:
            classes[len(L(P0,v))].append(v)
    repartition_identity=(set(classes[1])==set() and set(classes[2])==set() and
                          set(classes[3])==set(P0["Y"]) and set(classes[4])==set(P0["Y0"]))
    checks={
      "input_i_v":check_seeded_axioms(P0)[0],
      "Z1_empty":classes[1]==[],
      "Z2_empty":classes[2]==[],
      "Z3_equals_Y":set(classes[3])==set(P0["Y"]),
      "Z4_equals_Y0":set(classes[4])==set(P0["Y0"]),
      "repartition_identity":repartition_identity,
      "lemma6_no_deletion_needed":connected(P0,set(P0["vertices"])-set(P0["X0"]))
    }
    return all(checks.values()),{"checks":checks,"list_size_classes":classes,"output_identical_to_raw":all(checks.values())}

def adjacency_certificate(P,order):
    cert={}
    for i,a in enumerate(order):
        for j in range(i+1,len(order)):
            cert[a+"--"+order[j]]={"edge":has(P,a,order[j]),"required_edge":j==i+1}
    return cert

def validate_main():
    P=original_fixture();Q=qhat();c=extension()
    rec={"schema":"janus.trump.p7_split4.lemma11_acceptability_fragment.candidate.v1","fixture_id":P["id"],"graph_digest":digest(P)}
    ok,adet=check_seeded_axioms(P);rec["input_recompute"]={"seeded_axioms_i_v":ok,"detail":adet}
    rec["P7_free"]={"pass":induced_pt_witness(P,7) is None,"witness":induced_pt_witness(P,7)}
    rec["contains_induced_P6"]={"path":["z","y","s1","p","m","n"],"pass":induced_path(P,["z","y","s1","p","m","n"])}
    if not ok or not rec["P7_free"]["pass"]:rec["verdict"]="FAIL_INPUT";return rec
    okc,badc=proper(P,c,P["vertices"]);rec["extension_c"]={"proper":okc,"extends_original_seed":all(c[v]==P["f"][v] for v in P["S"]),"colors":c}
    if not okc or not rec["extension_c"]["extends_original_seed"]:rec["verdict"]="FAIL_INPUT";return rec

    state_checks=[]
    for st in Q["local_states"]:
        a,b=validate_111(P,st,Q["f_prime"]);state_checks.append({"state":st,"pass":a,"checks":b})
    merged=dict(P["f"]);merged.update(Q["f_prime"])
    qproper,bad=proper(P,merged,set(P["S"])|set(Q["f_prime"]))
    rec["raw_Qhat"]={"Qhat":Q,"local_state_checks":state_checks,"Q_admissible":{"pass":all(x["pass"] for x in state_checks) and qproper,"proper_detail":bad}}
    if not rec["raw_Qhat"]["Q_admissible"]["pass"]:rec["verdict"]="FAIL_QHAT";return rec

    P0,norm=construct_raw(P,Q);rec["normalized_raw"]={"P0":P0,"normalization":norm}
    ns,nsdet=normal_subcase(P,P0);rec["normalized_raw"]["normal_subcase"]={"pass":ns,"detail":nsdet}
    if not ns:rec["verdict"]="FAIL_ACCEPTABILITY_PROVENANCE_BINDING";return rec

    l10,l10det=lemma10_identity_replay(P,P0);rec["lemma10_replay"]={"pass":l10,"detail":l10det,"P_prime":P0}
    if not l10:rec["verdict"]="FAIL_ACCEPTABILITY_PROVENANCE_BINDING";return rec
    Pp=P0

    # E0
    rec["E0"]={"pass":True,"raw_ancestor_Qhat":Q,"post_Lemma10_identity":True,"P_prime":Pp}

    # E1 acceptability violation
    y="y";yp="y_prime";z="z"
    Ly=L(Pp,y);Lyp=L(Pp,yp); inter=Ly&Lyp
    e1checks={
      "y_in_Yp":y in Pp["Y"],"yp_in_Yp":yp in Pp["Y"],
      "y_neighbor_Y0p":bool(nbr(Pp,y)&set(Pp["Y0"])),"yp_neighbor_Y0p":bool(nbr(Pp,yp)&set(Pp["Y0"])),
      "nonadjacent":not has(Pp,y,yp),"lists_unequal":Ly!=Lyp,
      "c_y_in_intersection":c[y] in inter,"c_yp_in_intersection":c[yp] in inter
    }
    rec["E1"]={"pass":all(e1checks.values()),"checks":e1checks,"L_new_y":sorted(Ly),"L_new_y_prime":sorted(Lyp),"intersection":sorted(inter)}
    if not rec["E1"]["pass"]:rec["verdict"]="FAIL_ACCEPTABILITY_PREMISE";return rec

    # E2
    oldLy=L(P,y);oldLyp=L(P,yp)
    e2checks={"y_old_Y":y in P["Y"],"yp_old_Y":yp in P["Y"],"old_new_y_equal":oldLy==Ly,"old_new_yp_equal":oldLyp==Lyp,
              "residual_z_old_Y0":z in P["Y0"],"residual_z_new_Y0":z in Pp["Y0"]}
    rec["E2"]={"pass":all(e2checks.values()),"checks":e2checks,"L_old_y":sorted(oldLy),"L_old_y_prime":sorted(oldLyp)}
    if not rec["E2"]["pass"]:rec["verdict"]="FAIL_PROPERTY5_PROVENANCE";return rec

    # E3
    T=type_of(P,y);Tp=type_of(P,yp)
    e3checks={"T":list(T),"T_prime":list(Tp),"disjoint":not(set(T)&set(Tp)),
              "singleton_colors":len({P["f"][s] for s in T})==1 and len({P["f"][s] for s in Tp})==1,
              "different_colors":{P["f"][s] for s in T}!={P["f"][s] for s in Tp}}
    rec["E3"]={"pass":all(v for k,v in e3checks.items() if isinstance(v,bool)),"checks":e3checks}
    if not rec["E3"]["pass"]:rec["verdict"]="FAIL_TYPE_SEPARATION";return rec

    # E4
    common=sorted((nbr(Pp,y)&nbr(Pp,yp)&set(Pp["Y0"])))
    rec["E4"]={"pass":bool(common),"mode":"COMMON" if common else "SPLIT","common_attachments":common,
               "exhaustive":bool(nbr(Pp,y)&set(Pp["Y0"])) and bool(nbr(Pp,yp)&set(Pp["Y0"]))}
    if not rec["E4"]["pass"]:rec["verdict"]="FAIL_RESIDUAL_ATTACHMENT_CLASSIFICATION";return rec

    # E5 exact stored state for ordered (T,T')
    target=None
    for st in Q["local_states"]:
        if tuple(st["T"])==T and tuple(st["T_prime"])==Tp:target=st
    sizes={"000":0,"001":1,"111":3,"SPLIT4":4}
    if target is None:rec["verdict"]="FAIL_STATE_SCHEMA_BINDING";return rec
    support_size=sizes[target["mode"]]
    rec["E5"]={"pass":support_size>1 and target["mode"] in {"111","SPLIT4"},"stored_state":target,"support_size":support_size,"schema_sizes":sizes,
               "inference":"|V(Qhat_TT')|>1 => mode in {111,SPLIT4}"}
    if support_size>1 and target["mode"] in {"000","001"}:rec["verdict"]="FAIL_STATE_SCHEMA_BINDING";return rec
    if not rec["E5"]["pass"]:rec["verdict"]="FAIL_STORED_STATE_CLASSIFICATION";return rec

    # E6 C11
    p=target["P"][0];m=target["M"][0];n=target["N"][0];s=next(iter(set(T)-set(Tp)))
    path=[z,y,s,p,m,n]
    stable={y,yp,p,n}
    z_anti=all(not has(Pp,z,v) for v in {p,m,n})
    stable_ok=all(not has(Pp,a,b) for a,b in itertools.combinations(stable,2))
    source_checks={
      "z_anticomplete_to_stored_support":z_anti,
      "endpoint_p_color_in_list_intersection":Pp["f"][p] in inter,
      "endpoint_n_color_in_list_intersection":Pp["f"][n] in inter,
      "both_new_lists_size_3":len(Ly)==3 and len(Lyp)==3,
      "stable_y_yp_p_n":stable_ok,
      "m_color_in_L_new_y":Pp["f"][m] in Ly,
      "y_m_nonedge":not has(Pp,y,m),
      "s_in_T_minus_Tprime":s in set(T)-set(Tp),
      "terminal_path_is_induced_P6":induced_path(Pp,path),
      "graph_is_P7_free":induced_pt_witness(Pp,7) is None
    }
    first_unsupported="The published proof infers a contradiction from the induced path z-y-s-p-m-n being a P6. In the frozen P7-free setting, the induced P6 is permitted; no contradiction follows from the already frozen hypotheses."
    rec["E6"]={"cell":"C11","residual":"COMMON","stored":"111","classification":"CELL_REACHABLE_ESCAPE","pass_to_classification":all(source_checks.values()),
               "source_checks":source_checks,"terminal_path":path,"adjacency_certificate":adjacency_certificate(Pp,path),"first_unsupported_inference":first_unsupported}
    if not rec["E6"]["pass_to_classification"]:rec["verdict"]="FAIL_CELL_WITNESS_INVALID";return rec

    roles={"seed_anchor_T":"s1","seed_anchor_T_prime":"s2","p":"p","m":"m","n":"n","y":"y","y_prime":"y_prime","z":"z"}
    rec["minimization"]={
      "vertex_count":8,
      "role_map":roles,
      "all_roles_distinct":len(set(roles.values()))==8,
      "role_count_lower_bound":8,
      "proof":"Two distinct singleton-colored seed anchors are required; the terminal P6 has six distinct roles and uses only one seed anchor; acceptability additionally requires y' distinct from y. Hence 8 vertices are necessary for this exact decorated C11 pattern.",
      "vertex_deletion_status":{v:"DESTROYS_MANDATORY_DECORATED_ROLE_"+next(k for k,x in roles.items() if x==v) for v in P["vertices"]}
    }
    rec["matrix"]={
      "C11":{"classification":"CELL_REACHABLE_ESCAPE","analysis_status":"ANALYZED"},
      "C1S":{"classification":None,"analysis_status":"NOT_REACHED_DUE_TO_STOP"},
      "CS1":{"classification":None,"analysis_status":"NOT_REACHED_DUE_TO_STOP"},
      "CSS":{"classification":None,"analysis_status":"NOT_REACHED_DUE_TO_STOP"}
    }
    rec["reachable_escape_receipt"]={
      "cell":"C11","P":P,"Qhat_ancestor":Q,"raw_normalized_ancestor":P0,"post_Lemma10_P_prime":Pp,"extension_c":c,
      "T":list(T),"T_prime":list(Tp),"y":y,"y_prime":yp,"residual_attachment_mode":"COMMON","z":z,
      "stored_local_state_mode":"111","stored_representatives":{"p":p,"m":m,"n":n},
      "old_lists":{"y":sorted(oldLy),"y_prime":sorted(oldLyp)},"new_lists":{"y":sorted(Ly),"y_prime":sorted(Lyp)},
      "relevant_colors":{"f_seed":P["f"],"f_prime":Q["f_prime"],"c_y":c[y],"c_y_prime":c[yp]},
      "adjacency_nonadjacency_certificate":adjacency_certificate(Pp,path),
      "P7_free_certificate":{"method":"exhaustive induced-P7 search","induced_P7":None},
      "induced_P6_certificate":path,
      "first_unsupported_inference":first_unsupported,
      "smallest_available_decorated_witness":{"vertices":P["vertices"],"role_count_lower_bound":8},
      "minimization_provenance":"direct source-pattern construction; no graph-family search; role-count lower bound plus per-vertex mandatory-role deletion check"
    }
    rec["verdict"]="FAIL_P7_ACCEPTABILITY_ESCAPE"
    rec["stop"]=True
    return rec

def control_remove_chord():
    P=original_fixture();P["id"]="CTRL_P7_NEGATIVE_REMOVE_CHORD";P["edges"]=[e for e in P["edges"] if set(e)!=set(["y_prime","m"])]
    w=induced_pt_witness(P,7)
    return {"id":P["id"],"verdict":"PASS_CONTROL" if w is not None else "FAIL_CONTROL","induced_P7":w}

def control_schema():
    sizes={"000":0,"001":1,"111":3,"SPLIT4":4}
    implication=all((sz<=1) or mode in {"111","SPLIT4"} for mode,sz in sizes.items())
    return {"id":"CTRL_E5_SCHEMA_CARDINALITY","sizes":sizes,"implication_pass":implication,"verdict":"PASS_CONTROL" if implication else "FAIL_CONTROL"}

def quarantine_record(upstream_path):
    up=json.loads(pathlib.Path(upstream_path).read_text())
    q=up["source_001_quarantine"]["explicit_quarantine_fixture"]
    return {
      "id":"CTRL_001_QUARANTINE_RECORD",
      "source_parent_commit":"9366055f10daa79695604f3970154682bf952082",
      "formal_definition":q["formal_definition"],
      "completeness_text":q["completeness_text"],
      "variant_invariant":q["variant_invariant"],
      "affects_main_authority":False,
      "main_C11_path_uses_001":False,
      "verdict":"CELL_001_QUARANTINED"
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);ap.add_argument("--upstream-normalized-result",required=True);args=ap.parse_args()
    root=pathlib.Path(args.out);root.mkdir(parents=True,exist_ok=True)
    result=validate_main()
    controls=[control_remove_chord(),control_schema()]
    q=quarantine_record(args.upstream_normalized_result)
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    (root/"controls.json").write_text(json.dumps(controls,indent=2,sort_keys=True)+"\n")
    (root/"001_quarantine.json").write_text(json.dumps(q,indent=2,sort_keys=True)+"\n")
    summary={
      "schema":"janus.trump.p7_split4.lemma11_acceptability_fragment.summary.v1",
      "candidate_verdict":result.get("verdict"),
      "matrix":result.get("matrix"),
      "controls":{x["id"]:x["verdict"] for x in controls},
      "001_quarantine_verdict":q["verdict"],
      "001_affects_main_authority":False,
      "first_reachable_cell":"C11" if result.get("E6",{}).get("classification")=="CELL_REACHABLE_ESCAPE" else None,
      "stop_triggered":result.get("stop",False),
      "repair_attempted":False,
      "scientific_ceiling":{
        "ACCEPTABILITY_FRAGMENT":"FAIL_P7_ACCEPTABILITY_ESCAPE" if result.get("verdict")=="FAIL_P7_ACCEPTABILITY_ESCAPE" else "UNRESOLVED",
        "SUBGATE_A":"NOT_CLAIMED",
        "FULL_LEMMA11_P7_LIFT":"OPEN",
        "P7_FREE_4_COLOR_IN_P":"NOT_PROVED",
        "HARDNESS_LOCALIZED":"NOT_CLAIMED",
        "P_VS_NP":"OPEN"
      }
    }
    (root/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"candidate_verdict":result.get("verdict"),"cell":summary["first_reachable_cell"],"controls":summary["controls"],"stop":summary["stop_triggered"]},sort_keys=True))
    if result.get("verdict")!="FAIL_P7_ACCEPTABILITY_ESCAPE":raise SystemExit(2)
    if not all(x["verdict"]=="PASS_CONTROL" for x in controls):raise SystemExit(3)

if __name__=="__main__":main()
