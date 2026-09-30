#!/usr/bin/env python3
import argparse,itertools,json,pathlib
COL={1,2,3,4}
def e(a,b):return tuple(sorted((a,b)))
def es(edges):return {e(a,b) for a,b in edges}
def adj(E,a,b):return e(a,b) in E
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
        SS=set(S);sub={x for x in E if x[0] in SS and x[1] in SS}
        if len(sub)!=6:continue
        deg={v:0 for v in S}
        for a,b in sub:deg[a]+=1;deg[b]+=1
        if sorted(deg.values())==[1,1,2,2,2,2,2] and connected(S,sub):return list(S)
    return None
def oct_parts(S,E):
    S=sorted(S)
    if len(S)!=6:return None
    non=[e(a,b) for a,b in itertools.combinations(S,2) if not adj(E,a,b)]
    if len(non)!=3:return None
    flat=[x for z in non for x in z]
    if len(set(flat))!=6:return None
    if sum(1 for a,b in itertools.combinations(S,2) if adj(E,a,b))!=12:return None
    return sorted([list(x) for x in non])
def enumerate_octs(V,E):
    return {tuple(S):oct_parts(S,E) for S in itertools.combinations(sorted(V),6) if oct_parts(S,E) is not None}
def proper_cols(H,E,L):
    H=list(H);out=[]
    for vals in itertools.product([1,2,3,4],repeat=6):
        phi=dict(zip(H,vals))
        if any(phi[v] not in L[v] for v in H):continue
        if any(phi[a]==phi[b] for a,b in E if a in phi and b in phi):continue
        out.append(phi)
    return out
def propagate(E,L,fixed):
    L={v:set(x) for v,x in L.items() if v not in fixed};fixed=dict(fixed)
    while True:
        for a,b in E:
            if a in fixed and b in fixed and fixed[a]==fixed[b]:return None,fixed
        changed=False
        for v in list(L):
            L[v]-={fixed[u] for u in fixed if adj(E,u,v)}
            if not L[v]:return None,fixed
        singles=[v for v,x in L.items() if len(x)==1]
        if singles:
            for v in singles:
                if v not in L:continue
                fixed[v]=next(iter(L[v]));del L[v];changed=True
            continue
        if not changed:break
    return {v:sorted(x) for v,x in L.items()},fixed
def comps(V,E):
    V=set(V);out=[]
    while V:
        st=[next(iter(V))];C=set()
        while st:
            v=st.pop()
            if v in C:continue
            C.add(v);st.extend([u for u in V-C if adj(E,v,u)])
        V-=C;out.append(C)
    return out
def has_literal_oct(C,E):
    o=enumerate_octs(C,E)
    return next(iter(o.items())) if o else None
def escape_exists(H,CV,E,L):
    for phi in proper_cols(H,E,L):
        rem,fixed=propagate(E,L,phi)
        if rem is None:continue
        for D in comps(rem.keys(),E):
            union=set().union(*(set(rem[v]) for v in D))
            if union!=COL:continue
            octw=has_literal_oct(D,E)
            if octw:return phi,sorted(D),octw
    return None
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--candidate",required=True);ap.add_argument("--freeze",required=True);ap.add_argument("--out",required=True);a=ap.parse_args()
    c=json.load(open(a.candidate));fr=json.load(open(a.freeze));W=fr["first_authoritative_strong_O2_candidate"]
    V=W["vertices"];E=es(W["exact_edges"]);checks={}
    checks["primary"]=c["primary_outcome"]=="O2_OCTAHEDRON_ATTACHMENT_ESCAPE"
    checks["P7_free"]=p7(V,E) is None
    checks["authority_axioms"]=all(c["authority_checks"]["old_axioms"].values()) and all(c["authority_checks"]["stored_111_Q"].values()) and all(c["authority_checks"]["post_axioms"].values()) and all(c["authority_checks"]["post_lists"].values())
    checks["answer_provenance"]=all(c["authority_checks"]["answer_relevance_certificate"].values())
    residual=c["route34"]["residual"];CV=residual["vertices"];L=residual["lists"]
    octs=enumerate_octs(CV,E)
    checks["Oct_C_count"]=len(octs)==6
    candidate_cores={tuple(x["vertices"]) for x in c["Oct_C_complete_audit"]["cores"]}
    checks["Oct_C_complete"]=set(octs)==candidate_cores and c["Oct_C_complete_audit"]["complete_set_matches_freeze"] is True and c["Oct_C_complete_audit"]["every_core_accounted_once"] is True
    recomputed={}
    for H,parts in octs.items():
        cols=proper_cols(H,E,L)
        esc=escape_exists(H,CV,E,L)
        recomputed["|".join(H)]={"count":len(cols),"escape":esc is not None,"escape_phi":esc[0] if esc else None,"D":esc[1] if esc else None,"minor_core":list(esc[2][0]) if esc else None}
    checks["every_core_nonempty"]=all(x["count"]>0 for x in recomputed.values())
    checks["forall_H_exists_escape"]=all(x["escape"] for x in recomputed.values())
    checks["candidate_local_escape_count"]=c["LOCAL_CORE_ESCAPE_COUNT"]==6
    checks["GOOD_C_false"]=c["O2"]["GOOD_C"] is False and c["O2"]["status"]=="VERIFIED"
    qc=c["quantifier_controls"]
    checks["mixed_control"]=qc["TWO_CORE_MIXED_CONTROL"]["pass"] is True and qc["TWO_CORE_MIXED_CONTROL"]["GOOD_C"] is True and qc["TWO_CORE_MIXED_CONTROL"]["strong_O2"] is False
    checks["empty_control"]=qc["EMPTY_CORE_COLORING_CONTROL"]["pass"] is True and qc["EMPTY_CORE_COLORING_CONTROL"]["CORE_UNSAT_GOOD_MODULATOR"] is True
    checks["current_X2_control"]=c["current_authoritative_X2_control"]["pass"] is True and c["current_authoritative_X2_control"]["proper_core_colorings"]==30
    checks["no_forbidden_tools"]=all(v is False for v in c["oracle_use"].values())
    checks["ceiling"]=c["scientific_ceiling"]["TW4"]=="NOT_OPENED" and c["scientific_ceiling"]["BACKDOOR_SIZE_2"]=="NOT_OPENED" and c["scientific_ceiling"]["REPAIR"]=="NOT_STARTED" and c["scientific_ceiling"]["P_VS_NP"]=="OPEN"
    checks["stop"]=c["repair_attempted"] is False and c["successor_autoactivated"] is False and c["stop"] is True
    verdict="INDEPENDENT_STRONG_O2_FORALL_LITERAL_OCTAHEDRA_ESCAPE_VERIFIED" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
    out={"schema":"janus.trump.c11_pi_octahedron_core_modulator.independent.v1","verdict":verdict,"checks":checks,"recomputed_complete_Oct_C":recomputed,"scientific_ceiling":c["scientific_ceiling"]}
    pathlib.Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"verdict":verdict,"failed":[k for k,v in checks.items() if not v],"Oct_C":len(octs)},sort_keys=True))
    if verdict!="INDEPENDENT_STRONG_O2_FORALL_LITERAL_OCTAHEDRA_ESCAPE_VERIFIED":raise SystemExit(1)
if __name__=="__main__":main()
