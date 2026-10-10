#!/usr/bin/env python3
import argparse, itertools, json, pathlib, hashlib
from collections import Counter

COLORS={1,2,3,4}

def ek(a,b): return tuple(sorted((a,b)))
def eset(edges): return {ek(a,b) for a,b in edges}
def adjacent(E,a,b): return ek(a,b) in E

def connected(vertices,E):
    V=set(vertices)
    if not V: return True
    seen=set(); stack=[next(iter(V))]
    while stack:
        v=stack.pop()
        if v in seen: continue
        seen.add(v)
        for a,b in E:
            if a==v and b in V-seen: stack.append(b)
            elif b==v and a in V-seen: stack.append(a)
    return seen==V

def seed_lists(V,E,S,f):
    out={}
    for v in V:
        if v in S: continue
        used={f[s] for s in S if adjacent(E,v,s)}
        out[v]=sorted(COLORS-used)
    return out

def verify_axioms(V,E,S,X0,X,Y0,Y,f):
    L=seed_lists(V,E,S,f); ch={}
    ch["graph_connected"]=connected(V,E)
    ch["seed_connected"]=connected(S,E)
    ch["no_outside_complete_to_seed"]=all(not all(adjacent(E,v,s) for s in S) for v in set(V)-set(S))
    ch["Y0_exact"]={v for v in V if v not in S and not any(adjacent(E,v,s) for s in S)}==set(Y0)
    y0edges=[x for x in E if x[0] in Y0 and x[1] in Y0]
    ok=True
    for v in set(V)-set(Y0)-set(X0):
        for a,b in y0edges:
            if adjacent(E,v,a)!=adjacent(E,v,b): ok=False
    ch["no_mixed_on_Y0_edge"]=ok
    ch["Y0_four_lists"]=all(set(L[v])==COLORS for v in Y0)
    ch["Y_three_lists"]=all(len(L[v])==3 for v in Y)
    parts=list(map(set,[S,X0,X,Y0,Y]))
    ch["partition"]=set(V)==set().union(*parts) and all(not(A&B) for A,B in itertools.combinations(parts,2))
    return ch,L

def type_set(v,E,S): return sorted([s for s in S if adjacent(E,v,s)])

def proper(E,c):
    return all(not(a in c and b in c and c[a]==c[b]) for a,b in E)

def propagate(E,L,fixed):
    L={v:set(x) for v,x in L.items() if v not in fixed}
    fixed=dict(fixed)
    while True:
        for a,b in E:
            if a in fixed and b in fixed and fixed[a]==fixed[b]:
                return None,fixed
        changed=False
        for v in list(L):
            remove={fixed[u] for u in fixed if adjacent(E,u,v)}
            old=set(L[v]); L[v]-=remove
            if L[v]!=old: changed=True
            if not L[v]: return None,fixed
        singles=sorted(v for v,x in L.items() if len(x)==1)
        if singles:
            for v in singles:
                if v not in L: continue
                fixed[v]=next(iter(L[v])); del L[v]; changed=True
            continue
        if not changed: break
    return {v:sorted(x) for v,x in L.items()},fixed

def path7(vertices, Esub):
    deg={v:0 for v in vertices}
    for a,b in Esub:
        deg[a]+=1; deg[b]+=1
    return len(Esub)==6 and sorted(deg.values())==[1,1,2,2,2,2,2] and connected(vertices,Esub)

def compile_p7_patterns(V,baseE,port_edges):
    patterns=[]
    pkeys=[ek(a,b) for a,b in port_edges]
    for S in itertools.combinations(V,7):
        SS=set(S)
        fixed=[e for e in baseE if e[0] in SS and e[1] in SS]
        local=[(i,pkeys[i]) for i in range(len(pkeys)) if pkeys[i][0] in SS and pkeys[i][1] in SS]
        need=6-len(fixed)
        if need<0 or need>len(local): continue
        for comb in itertools.combinations(local,need):
            selected=[edge for _,edge in comb]
            Esub=set(fixed)|set(selected)
            if not path7(S,Esub): continue
            req=sum(1<<i for i,_ in comb)
            localmask=sum(1<<i for i,_ in local)
            patterns.append((tuple(S),req,localmask))
    patterns=sorted(set(patterns), key=lambda x:(x[0],x[1],x[2]))
    return patterns

def first_p7_from_patterns(mask,patterns):
    for S,req,localmask in patterns:
        if (mask & localmask)==req:
            return list(S)
    return None

def selected_indices(mask,n=16):
    return [i for i in range(n) if (mask>>i)&1]

def channel_metrics(mask, port_edges, PA, PD):
    idxs=selected_indices(mask,len(port_edges))
    deg={v:0 for v in PA+PD}
    for i in idxs:
        u,v=port_edges[i]; deg[u]+=1; deg[v]+=1
    delta=max(deg.values()) if deg else 0
    canonical=[]
    nu=0
    for k in range(min(4,len(idxs)),-1,-1):
        found=None
        for comb in itertools.combinations(idxs,k):
            left=set(); right=set(); ok=True
            for i in comb:
                u,v=port_edges[i]
                if u in left or v in right:
                    ok=False; break
                left.add(u); right.add(v)
            if ok:
                found=list(comb); break
        if found is not None:
            nu=k; canonical=found; break
    return {
      "degree_sequence_left":[deg[v] for v in PA],
      "degree_sequence_right":[deg[v] for v in PD],
      "Delta_X":delta,
      "nu_X":nu,
      "canonical_maximum_matching_edge_indices":canonical
    }

def invariant_authority(fr):
    F=fr["frame"]; V=F["vertices"]; E=eset(F["base_non_port_edges"])
    old=F["old_precoloring"]; S=old["S"]; f=old["f"]
    oldchecks,_=verify_axioms(V,E,S,old["X0"],old["X"],old["Y0"],old["Y"],f)
    q=F["stored_111"]
    qchecks={
      "P_singleton":q["P"]==["p"],
      "M_singleton":q["M"]==["m"],
      "N_singleton":q["N"]==["n"],
      "p_type_T":type_set("p",E,S)==["s"],
      "n_type_Tprime":type_set("n",E,S)==["t"],
      "m_Y0":"m" in old["Y0"],
      "pm":adjacent(E,"p","m"),
      "mn":adjacent(E,"m","n"),
      "pn_nonedge":not adjacent(E,"p","n"),
      "Q_colors":q["f_prime"]["p"] not in (1,2) and q["f_prime"]["n"] not in (1,2)
    }
    post=F["post_constructor"]; postf={"s":1,"t":2,**q["f_prime"]}
    postchecks,postlists=verify_axioms(V,E,post["S_prime"],[],[],post["Y0_prime"],post["Y_prime"],postf)
    postlistchecks={v:postlists[v]==L for v,L in post["lists_before_pair_fix"].items()}
    y,yp=F["survivor_pair"]
    survivor={
      "yy_nonedge":not adjacent(E,y,yp),
      "common_z":adjacent(E,y,"z") and adjacent(E,yp,"z"),
      "y_type_T":type_set(y,E,S)==["s"],
      "yp_type_Tprime":type_set(yp,E,S)==["t"],
      "ym_nonedge":not adjacent(E,y,"m"),
      "ypm_edge":adjacent(E,yp,"m"),
      "intersection":sorted(set(postlists[y])&set(postlists[yp]))==[3,4],
      "lists_unequal":postlists[y]!=postlists[yp]
    }
    prov=F["frozen_provenance_coloring"]
    provenance_base={"covers_all":set(prov)==set(V),"proper_on_base":proper(E,prov),"route34":prov[y]==3 and prov[yp]==4}
    fixed=dict(postf); fixed[y]=3; fixed[yp]=4
    current={v:postlists[v] for v in V if v not in post["S_prime"]}
    route_lists,route_fixed=propagate(E,current,fixed)
    route_ok=route_lists is not None and set(route_lists)==set(F["expected_route34_component_vertices"]) and all(route_lists[v]==F["expected_route34_lists"][v] for v in route_lists)
    return {
      "old_axioms":oldchecks,
      "stored_111_Q":qchecks,
      "post_axioms":postchecks,
      "post_lists":postlistchecks,
      "survivor_pair":survivor,
      "provenance_base":provenance_base,
      "route34_base_exact":route_ok
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--prereg",required=True); ap.add_argument("--freeze",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); root=pathlib.Path(a.out); root.mkdir(parents=True,exist_ok=True)
    pre=json.load(open(a.prereg)); fr=json.load(open(a.freeze)); F=fr["frame"]
    invariant=invariant_authority(fr)
    invariant_ok=all(all(x.values()) if isinstance(x,dict) else bool(x) for x in invariant.values())
    if not invariant_ok:
        raise SystemExit("FRAME_INVARIANT_AUTHORITY_FAIL")

    V=F["vertices"]; baseE=eset(F["base_non_port_edges"]); ports=[tuple(x) for x in F["port_edge_order"]]
    PA=F["left_ports"]; PD=F["right_ports"]; prov=F["frozen_provenance_coloring"]
    incompatible=[i for i,(u,v) in enumerate(ports) if prov[u]==prov[v]]
    incompatible_mask=sum(1<<i for i in incompatible)
    patterns=compile_p7_patterns(V,baseE,ports)

    current_edges={ek(a,b) for a,b in fr["controls"]["current_Q2"]["port_edges"]}
    current_mask=sum(1<<i for i,e in enumerate(ports) if ek(*e) in current_edges)
    synth_c2_edges={ek(a,b) for a,b in fr["controls"]["synthetic_C2"]["port_edges"]}
    synth_c2_mask=sum(1<<i for i,e in enumerate(ports) if ek(*e) in synth_c2_edges)
    synth_m2_edges={ek(a,b) for a,b in fr["controls"]["synthetic_M2"]["port_edges"]}
    synth_m2_mask=sum(1<<i for i,e in enumerate(ports) if ek(*e) in synth_m2_edges)

    controls={
      "current_Q2":channel_metrics(current_mask,ports,PA,PD),
      "synthetic_C2":channel_metrics(synth_c2_mask,ports,PA,PD),
      "synthetic_M2":channel_metrics(synth_m2_mask,ports,PA,PD)
    }
    controls["current_Q2"]["pass"]=controls["current_Q2"]["Delta_X"]==1 and controls["current_Q2"]["nu_X"]==3
    controls["synthetic_C2"]["pass"]=controls["synthetic_C2"]["nu_X"]==4
    controls["synthetic_M2"]["pass"]=controls["synthetic_M2"]["Delta_X"]>=2
    if not all(v["pass"] for v in controls.values()):
        raise SystemExit("CLASSIFIER_CONTROL_FAIL")

    counts=Counter(); admissible=0
    current_Q2_row=None
    max_delta=-1; max_nu=-1
    first_M2=None; first_C2=None
    all_admissible_delta_le1=True; all_admissible_nu_le3=True
    table=root/"all_masks.ndjson"
    h=hashlib.sha256()
    with table.open("w",encoding="utf-8") as fh:
        for mask in range(65536):
            row={"mask":mask,"mask_hex":f"{mask:04x}","selected_port_edge_indices":selected_indices(mask)}
            conflicts=selected_indices(mask & incompatible_mask)
            if conflicts:
                row.update({"status":"FRAME_INADMISSIBLE","reason":"PROVENANCE_IMPROPER_PORT_EDGE","conflicting_edge_indices":conflicts})
                counts["PROVENANCE_IMPROPER_PORT_EDGE"]+=1
            else:
                p7=first_p7_from_patterns(mask,patterns)
                if p7 is not None:
                    row.update({"status":"FRAME_INADMISSIBLE","reason":"INDUCED_P7_PRESENT","p7_vertices":p7})
                    counts["INDUCED_P7_PRESENT"]+=1
                else:
                    met=channel_metrics(mask,ports,PA,PD)
                    row.update({"status":"FRAME_ADMISSIBLE","reason":"ADMISSIBLE",**met})
                    counts["ADMISSIBLE"]+=1; admissible+=1
                    max_delta=max(max_delta,met["Delta_X"]); max_nu=max(max_nu,met["nu_X"])
                    if met["Delta_X"]>=2:
                        all_admissible_delta_le1=False
                        if first_M2 is None: first_M2={"mask":mask,"selected_port_edge_indices":row["selected_port_edge_indices"],**met}
                    if met["nu_X"]==4:
                        all_admissible_nu_le3=False
                        if first_C2 is None: first_C2={"mask":mask,"selected_port_edge_indices":row["selected_port_edge_indices"],**met}
            if mask==current_mask:
                current_Q2_row=dict(row)
            line=json.dumps(row,sort_keys=True,separators=(",",":"))+"\n"
            fh.write(line); h.update(line.encode())

    if sum(counts.values())!=65536:
        raise SystemExit("MASK_ACCOUNTING_FAIL")
    if not current_Q2_row or current_Q2_row.get("status")!="FRAME_ADMISSIBLE":
        raise SystemExit("CURRENT_Q2_AUTHORITATIVE_CONTROL_NOT_ADMISSIBLE")
    if current_Q2_row.get("Delta_X")!=1 or current_Q2_row.get("nu_X")!=3:
        raise SystemExit("CURRENT_Q2_AUTHORITATIVE_CONTROL_METRIC_FAIL")
    controls["current_Q2_enumeration"]={
      "mask":current_mask,
      "status":current_Q2_row["status"],
      "Delta_X":current_Q2_row["Delta_X"],
      "nu_X":current_Q2_row["nu_X"],
      "canonical_maximum_matching_edge_indices":current_Q2_row["canonical_maximum_matching_edge_indices"],
      "pass":True
    }

    M_verdict="M1_PORT_CHANNEL_MATCHING_STRUCTURE_UNIVERSAL" if all_admissible_delta_le1 else "M2_NONMATCHING_PORT_CHANNEL_WITNESS"
    C_verdict="C1_DIRECT_CHANNEL_MATCHING_NUMBER_LE3_UNIVERSAL" if all_admissible_nu_le3 else "C2_FOURTH_INDEPENDENT_DIRECT_CHANNEL_WITNESS"

    def edge_names(idxs):
        return [list(ports[i]) for i in idxs]

    if first_M2:
        first_M2["selected_port_edges"]=edge_names(first_M2["selected_port_edge_indices"])
        degs=first_M2["degree_sequence_left"]+first_M2["degree_sequence_right"]
        labels=PA+PD
        v=max(range(len(degs)),key=lambda i:degs[i])
        first_M2["degree_ge2_vertex"]=labels[v]
        first_M2["incident_edges"]=[list(ports[i]) for i in first_M2["selected_port_edge_indices"] if labels[v] in ports[i]]
    if first_C2:
        first_C2["selected_port_edges"]=edge_names(first_C2["selected_port_edge_indices"])
        first_C2["perfect_matching"]=edge_names(first_C2["canonical_maximum_matching_edge_indices"])
        paths=[F["hub_path"]]+[[F["left_anchor"],u,v,F["right_anchor"]] for u,v in first_C2["perfect_matching"]]
        first_C2["five_explicit_paths"]=paths

    result={
      "schema":"janus.trump.c11_two_octahedron_channel_structure.execution.v1",
      "frame_authority":invariant,
      "enumeration":{
        "raw_masks_expected":65536,
        "raw_masks_accounted":sum(counts.values()),
        "literal_mask_loop":"0..65535",
        "symmetry_pruning":False,
        "per_mask_table":"all_masks.ndjson",
        "per_mask_table_sha256":h.hexdigest(),
        "reason_histogram":dict(sorted(counts.items())),
        "admissible_count":admissible,
        "rejected_count":65536-admissible,
        "compiled_induced_P7_pattern_count":len(patterns),
        "provenance_incompatible_port_edge_indices":incompatible,
        "max_Delta_over_admissible":max_delta,
        "max_nu_over_admissible":max_nu
      },
      "controls":controls,
      "M_axis":{
        "verdict":M_verdict,
        "universal_relative_to_frozen_frame":M_verdict.startswith("M1_"),
        "first_authoritative_witness":first_M2
      },
      "C_axis":{
        "verdict":C_verdict,
        "universal_relative_to_frozen_frame":C_verdict.startswith("C1_"),
        "first_authoritative_witness":first_C2
      },
      "combined_verdict":M_verdict+"__AND__"+C_verdict,
      "both_axes_completed":True,
      "early_stop_used":False,
      "oracle_use":{"extension_oracle":False,"general_P7_free_4color_oracle":False,"separator4_universal_gate":False,"tw4":False,"backdoor2":False,"repair":False},
      "scientific_ceiling":{
        "FRAME_SCOPE":"ONLY_FROZEN_TWO_OCTAHEDRON_PORT_FRAME",
        "M_AXIS":M_verdict,
        "C_AXIS":C_verdict,
        "GLOBAL_KAPPA_FROM_CHANNELS":"NOT_INFERRED",
        "UNIVERSAL_CHANNEL_BOUND_ALL_C11":"NOT_CLAIMED",
        "UNIVERSAL_SEPARATOR4_COMPOSITION":"NOT_OPENED",
        "SEPARATOR_SIZE_5":"NOT_OPENED",
        "TW4":"NOT_OPENED","BACKDOOR_SIZE_2":"NOT_OPENED","REPAIR":"NOT_STARTED",
        "LEMMA11_P7_LIFT":"OPEN","P7_FREE_4_COLOR_IN_P":"NOT_PROVED","P_VS_NP":"OPEN"
      },
      "stop":True
    }
    (root/"candidate_result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "combined_verdict":result["combined_verdict"],
      "admissible":admissible,
      "histogram":dict(counts),
      "max_Delta":max_delta,
      "max_nu":max_nu,
      "table_sha256":h.hexdigest()
    },sort_keys=True))

if __name__=="__main__": main()
