#!/usr/bin/env python3
import argparse, collections, copy, hashlib, itertools, json, pathlib

COLORS={1,2,3,4}

def ce(a,b): return tuple(sorted((str(a),str(b))))
def edges(P): return {ce(a,b) for a,b in P["edges"] if a in P["vertices"] and b in P["vertices"]}
def nbr(P,v):
    ee=edges(P)
    return {u for u in P["vertices"] if u!=v and ce(u,v) in ee}
def Nset(P,A):
    A=set(A)
    return (set().union(*(nbr(P,v) for v in A))-A) if A else set()
def connected(P,A):
    A=set(A)
    if not A: return False
    q=[next(iter(A))]; seen=set()
    while q:
        v=q.pop()
        if v in seen: continue
        seen.add(v)
        q.extend((nbr(P,v)&A)-seen)
    return seen==A
def proper(P,c,domain=None):
    dom=set(domain if domain is not None else c)
    for a,b in edges(P):
        if a in dom and b in dom and c.get(a)==c.get(b):
            return False,{"edge":[a,b],"color":c.get(a)}
    return True,None
def listset(P,v):
    if v in P["S"] or v in P["X0"]: return {P["f"][v]}
    return COLORS-{P["f"][s] for s in nbr(P,v)&set(P["S"])}
def digest(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def induced_path_order(P,seq):
    if len(set(seq))!=len(seq): return False
    ee=edges(P)
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            if ((ce(a,seq[j]) in ee)!=(j==i+1)): return False
    return True

def induced_p6_witness(P):
    vs=sorted(P["vertices"])
    if len(vs)<6:return None
    ee=edges(P)
    for comb in itertools.combinations(vs,6):
        sub=set(comb)
        deg={v:sum(ce(v,u) in ee for u in sub if u!=v) for v in sub}
        if sorted(deg.values())!=[1,1,2,2,2,2] or sum(deg.values())!=10: continue
        start=next(iter(sub)); seen={start}; q=collections.deque([start])
        while q:
            v=q.popleft()
            for u in sub:
                if u not in seen and ce(v,u) in ee:
                    seen.add(u);q.append(u)
        if seen==sub:
            ends=sorted(v for v,d in deg.items() if d==1)
            cur=ends[0];prev=None;order=[]
            while True:
                order.append(cur)
                nxt=sorted(u for u in sub if u!=prev and ce(cur,u) in ee)
                if not nxt:break
                if len(nxt)>1:order=[];break
                prev,cur=cur,nxt[0]
            if len(order)==6 and induced_path_order(P,order):return order
    return None

def parts(P):
    return {k:set(P[k]) for k in ["S","X0","X","Y0","Y"]}

def is_seeded(P):
    V=set(P["vertices"]); ps=parts(P)
    if set().union(*ps.values())!=V:return False,{"reason":"cover"}
    if sum(len(x) for x in ps.values())!=len(V):return False,{"reason":"overlap"}
    if set(P["f"])!=ps["S"]|ps["X0"]:return False,{"reason":"f_domain"}
    ok,bad=proper(P,P["f"],ps["S"]|ps["X0"])
    return (ok, bad if not ok else {})

def axiom(P,k):
    V=set(P["vertices"]);S=set(P["S"]);X0=set(P["X0"]);X=set(P["X"]);Y0=set(P["Y0"]);Y=set(P["Y"])
    if k=="i": return connected(P,V-X0)
    if k=="ii": return connected(P,S) and not any(S<=nbr(P,v) for v in V-S)
    if k=="iii": return Y0==V-(Nset(P,S)|X0|S)
    if k=="iv":
        y0e=[(a,b) for a,b in edges(P) if a in Y0 and b in Y0]
        for v in V-(Y0|X0):
            for a,b in y0e:
                if (a in nbr(P,v))!=(b in nbr(P,v)):return False
        return True
    if k=="v":
        for v in V-S:
            target={1:X0,2:X,3:Y,4:Y0}[len(listset(P,v))]
            if v not in target:return False
        return True
    raise KeyError(k)

def all_extensions(P):
    V=sorted(P["vertices"]);fixed=dict(P["f"]);free=[v for v in V if v not in fixed]
    out=[]
    for vals in itertools.product(range(1,5),repeat=len(free)):
        c=fixed.copy();c.update(dict(zip(free,vals)))
        ok,_=proper(P,c,V)
        if ok:out.append(tuple(c[v] for v in V))
    return out

def full_coloring_from_tuple(P,tup):
    return dict(zip(sorted(P["vertices"]),tup))

def normal_subcase(P,Pp):
    V=set(P["vertices"]);Vp=set(Pp["vertices"])
    S=set(P["S"]);Sp=set(Pp["S"]);X0=set(P["X0"]);X0p=set(Pp["X0"])
    X=set(P["X"]);Y0=set(P["Y0"]);Y=set(P["Y"])
    if not Vp<=V:return False,"graph_not_induced_subset"
    if not (V-Vp)<=Y0:return False,"deleted_vertices_not_old_Y0"
    seeded,_=is_seeded(Pp)
    if not seeded:return False,"not_seeded"
    if not connected(Pp,Sp) or not S<=Sp:return False,"seed_connected_or_inclusion"
    for v in X0p&Y0:
        if not (nbr(Pp,v)&Sp):return False,"new_X0_old_Y0_no_seed_neighbor"
    if not Sp<=S|X|Y0|Y:return False,"seed_role_containment"
    if not X0<=X0p or not X0p<=X0|X|Y0|Y:return False,"X0_role_containment"
    for v in (S|X0)&Vp:
        if Pp["f"].get(v)!=P["f"].get(v):return False,"old_color_changed"
    return True,"ok"

def type_of(P,v):return tuple(sorted(nbr(P,v)&set(P["S"])))
def fT(P,T):return {P["f"][s] for s in T}
def YT(P,T):return {v for v in P["Y"] if type_of(P,v)==tuple(T)}
def NY0(P):return Nset(P,P["Y0"])

def relevant_pairs(P):
    Ts=[];S=sorted(P["S"])
    for r in range(1,len(S)+1):
        for comb in itertools.combinations(S,r):
            if len(fT(P,comb))==1:Ts.append(tuple(comb))
    return [(T,Tp) for T in Ts for Tp in Ts if fT(P,T)!=fT(P,Tp)]

def choose_legacy_state(P,c,T,Tp):
    alpha=next(iter(fT(P,T)));beta=next(iter(fT(P,Tp)));ny0=NY0(P)
    left=sorted(YT(P,T)&ny0);right=sorted(YT(P,Tp)&ny0)
    bad=[]
    for p in left:
        for n in right:
            if ce(p,n) in edges(P):continue
            if c[p] in {alpha,beta} or c[n] in {alpha,beta}:continue
            bad.append((p,n))
    if bad:
        p,n=bad[0]
        common=sorted(z for z in P["Y0"] if z in nbr(P,p) and z in nbr(P,n))
        if not common:return {"mode":"NO_COMMON","T":list(T),"T_prime":list(Tp),"p":p,"n":n}
        return {"mode":"111","T":list(T),"T_prime":list(Tp),"p":p,"m":common[0],"n":n}
    cand=[n for n in right if c[n]!=alpha]
    if cand:return {"mode":"001","T":list(T),"T_prime":list(Tp),"n":cand[0]}
    return {"mode":"000","T":list(T),"T_prime":list(Tp)}

def build_global_Q(P,c):
    return [choose_legacy_state(P,c,T,Tp) for T,Tp in relevant_pairs(P)]

def q_state_valid(P,st):
    T=tuple(st["T"]);Tp=tuple(st["T_prime"]);m=st["mode"]
    if m=="000":return True,"ok"
    if m=="001":
        return (st["n"] in YT(P,Tp), "ok" if st["n"] in YT(P,Tp) else "001_N_wrong_type")
    if m=="111":
        p,z,n=st["p"],st["m"],st["n"]
        cond=(p in YT(P,T) and n in YT(P,Tp) and z in P["Y0"] and
              ce(z,p) in edges(P) and ce(z,n) in edges(P) and ce(p,n) not in edges(P))
        return cond,"ok" if cond else "111_membership_or_incidence"
    return False,"unknown_mode"

def local_support(st):
    if st["mode"]=="000":return set()
    if st["mode"]=="001":return {st["n"]}
    if st["mode"]=="111":return {st["p"],st["m"],st["n"]}
    return set()

def local_Z(P,st,variant="formal"):
    T=tuple(st["T"]);Tp=tuple(st["T_prime"]);ny0=NY0(P)
    if st["mode"]=="000":return YT(P,Tp)&ny0
    if st["mode"]=="001":
        base=(YT(P,Tp) if variant=="formal" else YT(P,T))&ny0
        return base-nbr(P,st["n"])
    if st["mode"]=="111":return set()
    raise ValueError(st["mode"])

def forced_color(P,st,variant="formal"):
    if st["mode"]=="000":return next(iter(fT(P,tuple(st["T"]))))
    if st["mode"]=="001":
        return next(iter(fT(P,tuple(st["T"] if variant=="formal" else st["T_prime"]))))
    return None

def Q_projections(P,Q,variant="formal"):
    A=set().union(*(local_support(st) for st in Q)) if Q else set()
    zparts=[local_Z(P,st,variant) for st in Q]
    Z=set().union(*zparts) if zparts else set()
    return A,Z,zparts

def check_admissible(P,Q,fprime,variant="formal"):
    A,Z,zparts=Q_projections(P,Q,variant)
    if set(fprime)!=A|Z:return False,{"reason":"domain","expected":sorted(A|Z),"actual":sorted(fprime)}
    for st,zs in zip(Q,zparts):
        ok,why=q_state_valid(P,st)
        if not ok:return False,{"reason":"bad_Q_state","detail":why,"state":st}
        banned=fT(P,tuple(st["T"]))|fT(P,tuple(st["T_prime"]))
        if st["mode"]=="111":
            if fprime[st["p"]] in banned or fprime[st["n"]] in banned:
                return False,{"reason":"endpoint_color","state":st}
        if st["mode"]=="001" and fprime[st["n"]] in banned:
            return False,{"reason":"endpoint_color","state":st}
        fc=forced_color(P,st,variant)
        if fc is not None:
            for v in zs:
                if fprime[v]!=fc:return False,{"reason":"forced_Z_color","vertex":v,"required":fc,"actual":fprime[v],"state":st}
    merged=dict(P["f"]);merged.update(fprime)
    ok,bad=proper(P,merged,set(P["S"])|A|set(P["X0"])|Z)
    if not ok:return False,{"reason":"properness","witness":bad}
    return True,{"A":sorted(A),"Z_FORCE":sorted(Z),"Z_overlap":sorted(A&Z)}

def literal_roles(P,Q,variant="formal"):
    A,Z,_=Q_projections(P,Q,variant)
    return {
      "S":set(P["S"])|A,
      "X0":set(P["X0"])|Z,
      "X":set(P["X"]),
      "Y0":set(P["Y0"])-(A|Nset(P,A)),
      "Y":(set(P["Y"])-(A|Z))|(Nset(P,A)&set(P["Y0"]))
    },A,Z

def normalized_constructor(P,Q,fprime,variant="formal"):
    literal,A,Z=literal_roles(P,Q,variant)
    ZX=Z-A
    out=copy.deepcopy(P)
    out["S"]=sorted(set(P["S"])|A)
    out["X0"]=sorted(set(P["X0"])|ZX)
    out["X"]=sorted(set(P["X"]))
    out["Y0"]=sorted(set(P["Y0"])-(A|Nset(P,A)))
    out["Y"]=sorted((set(P["Y"])-(A|Z))|(Nset(P,A)&set(P["Y0"])))
    nf=dict(P["f"]);nf.update(fprime);out["f"]=nf
    meta={"A":sorted(A),"Z_FORCE":sorted(Z),"Z_X0":sorted(ZX),"overlap":sorted(A&Z),
          "literal_roles":{k:sorted(v) for k,v in literal.items()}}
    return out,meta

def exact_fixed_semantics(P,A,Z,fprime,Pnorm):
    literal_fixed=set(P["S"])|set(P["X0"])|set(A)|set(Z)
    normalized_fixed=set(Pnorm["S"])|set(Pnorm["X0"])
    merged=dict(P["f"]);merged.update(fprime)
    identity=(literal_fixed==normalized_fixed and all(Pnorm["f"][v]==merged[v] for v in normalized_fixed))
    # Compare the intended literal fixed-data extension set to normalized tuple.
    tmp=copy.deepcopy(P)
    tmp["S"]=sorted(literal_fixed);tmp["X0"]=[];tmp["X"]=[];tmp["Y0"]=[];tmp["Y"]=[]
    # for extension enumeration only, keep one physical role for all unfixed vertices:
    rest=set(P["vertices"])-literal_fixed
    tmp["Y"]=sorted(rest)
    tmp["f"]={v:merged[v] for v in literal_fixed}
    lit_ext=set(all_extensions(tmp))
    norm_ext=set(all_extensions(Pnorm))
    return identity,lit_ext,norm_ext

def induced_subgraph(P,Vkeep):
    Vkeep=set(Vkeep);out=copy.deepcopy(P)
    out["vertices"]=sorted(Vkeep)
    out["edges"]=[[a,b] for a,b in P["edges"] if a in Vkeep and b in Vkeep]
    for k in ["S","X0","X","Y0","Y"]:out[k]=sorted(set(P[k])&Vkeep)
    out["f"]={v:c for v,c in P["f"].items() if v in Vkeep}
    return out

def components(P,A):
    A=set(A);res=[]
    while A:
        r=next(iter(A));stack=[r];seen=set()
        while stack:
            v=stack.pop()
            if v in seen:continue
            seen.add(v);stack.extend((nbr(P,v)&A)-seen)
        res.append(seen);A-=seen
    return res

def component_3color_witness(P,C,Apre,excluded):
    C=sorted(C);fixed={v:P["f"][v] for v in Apre}
    for vals in itertools.product(sorted(COLORS-{excluded}),repeat=len(C)):
        col=dict(fixed);col.update(dict(zip(C,vals)))
        ok,_=proper(P,col,set(C)|set(Apre))
        if ok:return {v:col[v] for v in C}
    return None

def lemma6_finite(parent,Ptilde):
    cur=copy.deepcopy(Ptilde);deleted=[]
    if not axiom(parent,"i"):return None,{"reason":"parent_i"}
    if not axiom(cur,"iii") or not axiom(cur,"iv"):return None,{"reason":"lemma6_preconditions"}
    while not axiom(cur,"i"):
        V=set(cur["vertices"]);X0=set(cur["X0"]);S=set(cur["S"])
        bad=[C for C in components(cur,V-X0) if not (C&S)]
        if not bad:return None,{"reason":"no_bad_component_but_i_false"}
        C=bad[0]
        xs=sorted(Nset(cur,C)&(X0-set(parent["X0"])))
        if not xs:return None,{"reason":"no_boundary_x","C":sorted(C)}
        x=xs[0];color=cur["f"][x]
        Apre={v for v in X0 if cur["f"][v]!=color}
        w=component_3color_witness(cur,C,Apre,color)
        if w is None:return {"empty":True},{"deleted":deleted,"reason":"no_component_extension"}
        deleted.append({"C":sorted(C),"coloring":w,"x":x,"boundary_color":color})
        cur=induced_subgraph(cur,set(cur["vertices"])-C)
    return cur,{"deleted":deleted,"empty":False}

def reconstruct_deleted(reduced_col,deleted):
    c=dict(reduced_col)
    for item in reversed(deleted):
        c.update(item["coloring"])
    return c

def lemma10_finite(parent,Pprime):
    if induced_p6_witness(parent):return None,{"reason":"not_P6_free"}
    ns,why=normal_subcase(parent,Pprime)
    if not ns:return None,{"reason":"not_normal_subcase","detail":why}
    if not axiom(Pprime,"iii"):return None,{"reason":"normalized_raw_not_iii"}
    if not all(axiom(parent,k) for k in ["ii","iii","iv"]):return None,{"reason":"lemma7_parent_hypotheses"}
    if not axiom(Pprime,"iv"):return None,{"reason":"lemma7_conclusion_failed"}
    V=set(Pprime["vertices"]);S=set(Pprime["S"]);X0=set(Pprime["X0"])
    Zi={i:set() for i in range(5)}
    for v in V-(S|X0):Zi[len(listset(Pprime,v))].add(v)
    if Zi[0]:return {"empty":True},{"lemma7":"PASS","Zi":{i:sorted(x) for i,x in Zi.items()},"reason":"Z0"}
    unique={v:next(iter(listset(Pprime,v))) for v in Zi[1]}
    Ptilde=copy.deepcopy(Pprime)
    Ptilde["X0"]=sorted(X0|Zi[1]);Ptilde["X"]=sorted(Zi[2]);Ptilde["Y0"]=sorted(Zi[4]);Ptilde["Y"]=sorted(Zi[3])
    nf=dict(Pprime["f"]);nf.update(unique);Ptilde["f"]=nf
    seeded,_=is_seeded(Ptilde)
    if not seeded:return None,{"reason":"Ptilde_not_seeded"}
    if not axiom(Ptilde,"iv"):return None,{"reason":"Ptilde_iv"}
    out,l6=lemma6_finite(parent,Ptilde)
    if out is None:return None,{"reason":"lemma6_fail","detail":l6}
    if out.get("empty"):return out,{"lemma7":"PASS","Zi":{i:sorted(x) for i,x in Zi.items()},"lemma6":l6}
    checks={k:axiom(out,k) for k in ["i","ii","iii","iv","v"]}
    if not all(checks.values()):return None,{"reason":"lemma10_conclusion","checks":checks}
    return out,{"lemma7":"PASS","Zi":{i:sorted(x) for i,x in Zi.items()},"lemma6":l6,"checks":checks}

def evaluate_full_fixture(P,variant="formal"):
    rec={"fixture_id":P["id"],"variant":variant,"graph_digest":digest(P)}
    seeded,_=is_seeded(P)
    rec["source_input"]={
      "seeded":seeded,
      "P6_free":induced_p6_witness(P) is None,
      "axioms":{k:axiom(P,k) for k in ["i","ii","iii","iv","v"]}
    }
    if not seeded or induced_p6_witness(P) is not None or not all(rec["source_input"]["axioms"].values()):
        rec["verdict"]="FAIL_SOURCE_PARITY";return rec
    c=P["c"]
    ok,_=proper(P,c,set(P["vertices"]))
    if not ok or any(c[v]!=P["f"][v] for v in set(P["S"])|set(P["X0"])):
        rec["verdict"]="FAIL_SOURCE_PARITY";rec["detail"]="c_not_extension";return rec
    Q=build_global_Q(P,c)
    if any(st["mode"]=="NO_COMMON" for st in Q):
        rec["verdict"]="FAIL_SOURCE_PARITY";rec["detail"]="P6_legacy_common_missing";return rec
    rec["Q"]=Q
    A,Z,_=Q_projections(P,Q,variant)
    fprime={v:c[v] for v in A|Z}
    adm,adetail=check_admissible(P,Q,fprime,variant)
    rec["R0_source_parity"]={"admissible":adm,"detail":adetail,"A":sorted(A),"Z_FORCE":sorted(Z)}
    if not adm:
        rec["verdict"]="QUARANTINED_SOURCE_VARIANT_NOT_ADMISSIBLE" if P.get("quarantined") else "FAIL_SOURCE_PARITY"
        return rec
    literal,_,_=literal_roles(P,Q,variant)
    lit_overlap=set(literal["S"])&set(literal["X0"])
    Pn,meta=normalized_constructor(P,Q,fprime,variant)
    rec["literal_support_Z_collision"]=sorted(A&Z)
    rec["literal_tuple_seed_X0_overlap"]=sorted(lit_overlap)
    seededn,sdetail=is_seeded(Pn)
    rec["R1_R3_normalized"]={
      "metadata":meta,
      "seeded":seededn,
      "seeded_detail":sdetail,
      "normal_subcase":normal_subcase(P,Pn),
      "axiom_iii":axiom(Pn,"iii"),
      "connected_seed":connected(Pn,Pn["S"])
    }
    if not seededn or not normal_subcase(P,Pn)[0] or not axiom(Pn,"iii"):
        rec["verdict"]="FAIL_NORMALIZED_TYPING";return rec
    identity,lit_ext,norm_ext=exact_fixed_semantics(P,A,Z,fprime,Pn)
    overlap_constraints={}
    for v in sorted(A&Z):
        overlap_constraints[v]={
          "physical_role":"SEED" if v in Pn["S"] else "OTHER",
          "semantic_Z_FORCE":v in Z,
          "color_preserved":Pn["f"][v]==fprime[v]
        }
    rec["R4_semantic_identity"]={
      "fixed_union_identity":identity,
      "literal_intended_extension_count":len(lit_ext),
      "normalized_extension_count":len(norm_ext),
      "extension_sets_equal":lit_ext==norm_ext,
      "overlap_constraints":overlap_constraints
    }
    if not identity or lit_ext!=norm_ext or any(not all(x.values()) for x in overlap_constraints.values()):
        rec["verdict"]="FAIL_EXTENSION_SEMANTICS";return rec
    # Completeness witness and raw soundness against original P.
    norm_extensions=set(all_extensions(Pn));orig_extensions=set(all_extensions(P))
    sortedV=sorted(P["vertices"]);c_tuple=tuple(c[v] for v in sortedV)
    rec["R6_raw_semantics"]={
      "fixed_extension_c_captured":c_tuple in norm_extensions,
      "normalized_extensions_subset_original":norm_extensions<=orig_extensions,
      "original_extension_count":len(orig_extensions),
      "normalized_extension_count":len(norm_extensions)
    }
    if not rec["R6_raw_semantics"]["fixed_extension_c_captured"] or not rec["R6_raw_semantics"]["normalized_extensions_subset_original"]:
        rec["verdict"]="FAIL_LEGACY_COMPLETENESS";return rec
    l10,l10rec=lemma10_finite(P,Pn)
    rec["R5_lemma7_10_replay"]=l10rec
    if l10 is None:
        rec["verdict"]="FAIL_LEMMA10_REPLAY";return rec
    if not l10.get("empty"):
        reduced_ext=all_extensions(l10)
        reconstruction_ok=True
        reconstructed=None
        if reduced_ext:
            rc=full_coloring_from_tuple(l10,reduced_ext[0])
            rc=reconstruct_deleted(rc,l10rec["lemma6"]["deleted"])
            okp,_=proper(P,rc,set(P["vertices"]))
            reconstructs_old=okp and all(rc[v]==P["f"][v] for v in set(P["S"])|set(P["X0"]))
            reconstruction_ok=reconstructs_old
            reconstructed=rc
        rec["R6_downstream_reconstruction"]={
          "reduced_has_extension":bool(reduced_ext),
          "reconstruction_ok":reconstruction_ok,
          "reconstructed_example":reconstructed
        }
        if not reconstruction_ok:
            rec["verdict"]="FAIL_LEGACY_COMPLETENESS";return rec
    rec["R7_polynomial_accounting"]={
      "Q_unchanged":True,"S_Q_unchanged":True,"Z_FORCE_unchanged":True,
      "admissibility_domain_unchanged":True,
      "extra_operation":"Z_X0 = Z_FORCE minus S(Q)",
      "asymptotic_change":"none"
    }
    rec["verdict"]="PASS_FULL_LEGACY_REPLAY"
    return rec

def sealed_regression():
    P={
      "id":"SEALED_111_PLUS_000_SUPPORT_Z_COLLISION",
      "vertices":["s1","s2","s3","v","n","z"],
      "edges":[["s1","s2"],["s2","s3"],["s1","s3"],["v","s1"],["v","z"],["z","n"],["n","s3"]],
      "S":["s1","s2","s3"],"X0":[],"X":[],"Y0":["z"],"Y":["v","n"],
      "f":{"s1":1,"s2":2,"s3":3},
      "c":{"s1":1,"s2":2,"s3":3,"v":2,"n":4,"z":1}
    }
    Q=[
      {"mode":"111","T":["s1"],"T_prime":["s3"],"p":"v","m":"z","n":"n"},
      {"mode":"000","T":["s2"],"T_prime":["s1"]}
    ]
    A,Z,_=Q_projections(P,Q,"formal");fprime={v:P["c"][v] for v in A|Z}
    adm,adet=check_admissible(P,Q,fprime,"formal")
    literal,_,_=literal_roles(P,Q,"formal")
    literal_collision=sorted(set(literal["S"])&set(literal["X0"]))
    Pn,meta=normalized_constructor(P,Q,fprime,"formal")
    seeded,_=is_seeded(Pn);ns=normal_subcase(P,Pn)
    identity,lit_ext,norm_ext=exact_fixed_semantics(P,A,Z,fprime,Pn)
    overlap=sorted(A&Z)
    return P,{
      "fixture_id":P["id"],"source_fragment_admissible":adm,"source_detail":adet,
      "literal_constructor":"FAIL_SUPPORT_Z_COLLISION" if literal_collision else "NO_COLLISION",
      "literal_collision":literal_collision,
      "normalized_constructor":"PASS_ROLE_NORMALIZATION" if seeded and ns[0] else "FAIL_NORMALIZED_TYPING",
      "metadata":meta,
      "fixed_union_identity":identity,
      "extension_sets_equal":lit_ext==norm_ext,
      "overlap_assertions":{
        v:{"physical_role":"SEED" if v in Pn["S"] else "OTHER",
           "semantic_Z_FORCE":v in Z,
           "forced_color_preserved":Pn["f"][v]==fprime[v]} for v in overlap
      },
      "P6_free":induced_p6_witness(P) is None
    }

def fixture_core():
    return {
      "id":"CORE_FULL_000_111_NO001",
      "vertices":["s1","s2","s3","v","n","z"],
      "edges":[["s1","s2"],["s2","s3"],["s1","s3"],["v","s1"],["v","z"],["z","n"],["n","s3"]],
      "S":["s1","s2","s3"],"X0":[],"X":[],"Y0":["z"],"Y":["v","n"],
      "f":{"s1":1,"s2":2,"s3":3},
      "c":{"s1":1,"s2":2,"s3":3,"v":2,"n":2,"z":1}
    }
def fixture_000():
    return {
      "id":"LEGACY_000_FORCE_ONLY",
      "vertices":["s1","s2","n","z"],
      "edges":[["s1","s2"],["s2","n"],["n","z"]],
      "S":["s1","s2"],"X0":[],"X":[],"Y0":["z"],"Y":["n"],
      "f":{"s1":1,"s2":2},
      "c":{"s1":1,"s2":2,"n":1,"z":3}
    }
def fixture_111():
    return {
      "id":"LEGACY_111_SUPPORT_ONLY",
      "vertices":["s1","s2","p","n","z"],
      "edges":[["s1","s2"],["p","s1"],["n","s2"],["p","z"],["n","z"]],
      "S":["s1","s2"],"X0":[],"X":[],"Y0":["z"],"Y":["p","n"],
      "f":{"s1":1,"s2":2},
      "c":{"s1":1,"s2":2,"p":3,"n":3,"z":4}
    }
def fixture_001():
    return {
      "id":"QUARANTINED_001_TEXT_DISCREPANCY",
      "quarantined":True,
      "vertices":["s1","s2","s3","v","z"],
      "edges":[["s1","s2"],["s2","s3"],["s1","s3"],["v","s1"],["v","z"]],
      "S":["s1","s2","s3"],"X0":[],"X":[],"Y0":["z"],"Y":["v"],
      "f":{"s1":1,"s2":2,"s3":3},
      "c":{"s1":1,"s2":2,"s3":3,"v":2,"z":1}
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);args=ap.parse_args()
    root=pathlib.Path(args.out);root.mkdir(parents=True,exist_ok=True)
    sealedP,sealed=sealed_regression()
    (root/"SEALED_111_PLUS_000_SUPPORT_Z_COLLISION.fixture.json").write_text(json.dumps(sealedP,indent=2,sort_keys=True)+"\n")
    (root/"SEALED_111_PLUS_000_SUPPORT_Z_COLLISION.receipt.json").write_text(json.dumps(sealed,indent=2,sort_keys=True)+"\n")
    authoritative=[]
    for P in [fixture_core(),fixture_000(),fixture_111()]:
        rec=evaluate_full_fixture(P,"formal");authoritative.append(rec)
        (root/(P["id"]+".fixture.json")).write_text(json.dumps(P,indent=2,sort_keys=True)+"\n")
        (root/(P["id"]+".receipt.json")).write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    qP=fixture_001();quar={}
    for variant in ["formal","completeness_text"]:
        rec=evaluate_full_fixture(qP,"formal" if variant=="formal" else "completeness")
        quar[variant]=rec
        (root/("QUARANTINED_001_"+variant+".receipt.json")).write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    (root/"QUARANTINED_001_TEXT_DISCREPANCY.fixture.json").write_text(json.dumps(qP,indent=2,sort_keys=True)+"\n")
    sealed_ok=(sealed["literal_constructor"]=="FAIL_SUPPORT_Z_COLLISION" and
               sealed["normalized_constructor"]=="PASS_ROLE_NORMALIZATION" and
               sealed["fixed_union_identity"] and sealed["extension_sets_equal"] and
               all(v["physical_role"]=="SEED" and v["semantic_Z_FORCE"] and v["forced_color_preserved"]
                   for v in sealed["overlap_assertions"].values()))
    core_ok=all(r["verdict"]=="PASS_FULL_LEGACY_REPLAY" for r in authoritative)
    # Require the pure-000 fixture to exercise nontrivial Lemma-6 deletion path.
    pure000=next(r for r in authoritative if r["fixture_id"]=="LEGACY_000_FORCE_ONLY")
    nontrivial_l6=bool(pure000.get("R5_lemma7_10_replay",{}).get("lemma6",{}).get("deleted"))
    if sealed_ok and core_ok and nontrivial_l6:
        gate="PASS_LEGACY_NORMALIZED_CONSTRUCTOR_REPLAY"
    else:
        gate="FAIL_LEGACY_NORMALIZED_CONSTRUCTOR_REPLAY"
    summary={
      "schema":"janus.trump.legacy_normalized_constructor_replay.v1",
      "authority_mode":"FINITE_SOURCE_FAITHFUL_REPLAY__NOT_UNIVERSAL_FORMAL_PROOF",
      "sealed_regression_ok":sealed_ok,
      "authoritative_core_ok":core_ok,
      "pure_000_nontrivial_lemma6_path":nontrivial_l6,
      "authoritative_receipts":authoritative,
      "quarantined_001":{
        "formal_verdict":quar["formal"]["verdict"],
        "completeness_text_verdict":quar["completeness_text"]["verdict"],
        "SOURCE_001_RESOLVED":False
      },
      "scientific_gate":gate,
      "ceiling":{
        "LEGACY_NORMALIZATION":"REPLAY_VERIFIED" if gate.startswith("PASS_") else "NOT_VERIFIED",
        "AUTHORS_INTENDED_NORMALIZATION":"NOT_CLAIMED",
        "SOURCE_001_SEMANTICS":"AMBIGUOUS",
        "RIGID_SPLIT4":"STILL_PAUSED",
        "P7_RAW_COVERAGE":"NOT_RERUN",
        "LEMMA11_P7_LIFT":"OPEN",
        "P_VS_NP":"OPEN"
      }
    }
    (root/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"scientific_gate":gate,"sealed_ok":sealed_ok,"core_ok":core_ok,
                      "lemma6_nontrivial":nontrivial_l6,
                      "q001_formal":quar["formal"]["verdict"],
                      "q001_text":quar["completeness_text"]["verdict"]},sort_keys=True))
    if gate!="PASS_LEGACY_NORMALIZED_CONSTRUCTOR_REPLAY":raise SystemExit(1)

if __name__=="__main__":main()
