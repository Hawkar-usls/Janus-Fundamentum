#!/usr/bin/env python3
import argparse, collections, copy, hashlib, importlib.util, itertools, json, pathlib

COLORS={1,2,3,4}
PASS="P7_SPLIT4_NORMALIZED_RAW_EQUIVALENCE_AUTHORITATIVE_CORE_VERIFIED"
FULL_OPEN="OPEN_DUE_TO_001_AMBIGUITY"

def ce(a,b): return tuple(sorted((str(a),str(b))))
def E(P): return {ce(a,b) for a,b in P["edges"]}
def has(P,a,b): return ce(a,b) in E(P)
def nbr(P,v): return {u for u in P["vertices"] if u!=v and has(P,u,v)}
def Nset(P,A):
    A=set(A)
    return (set().union(*(nbr(P,v) for v in A))-A) if A else set()
def connected(P,A):
    A=set(A)
    if not A: return False
    todo=[next(iter(A))]; seen=set()
    while todo:
        v=todo.pop()
        if v in seen: continue
        seen.add(v); todo.extend((nbr(P,v)&A)-seen)
    return seen==A
def proper(P,c,domain=None):
    dom=set(domain if domain is not None else c)
    for a,b in E(P):
        if a in dom and b in dom and c.get(a)==c.get(b):
            return False,{"edge":[a,b],"color":c.get(a)}
    return True,None
def induced_path(P,seq):
    if len(set(seq))!=len(seq): return False
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            if has(P,a,seq[j]) != (j==i+1): return False
    return True
def induced_pt_witness(P,k):
    vs=sorted(P["vertices"])
    if len(vs)<k:return None
    for comb in itertools.combinations(vs,k):
        for perm in itertools.permutations(comb):
            if induced_path(P,perm): return list(perm)
    return None
def digest(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def list_colors(P,v):
    if v in P["S"] or v in P["X0"]: return {P["f"][v]}
    used={P["f"][s] for s in nbr(P,v)&set(P["S"])}
    return COLORS-used

def check_input(P,require_p7=True):
    V=set(P["vertices"]); ps={k:set(P[k]) for k in ["S","X0","X","Y0","Y"]}
    if set().union(*ps.values())!=V or sum(map(len,ps.values()))!=len(V):
        return "FAIL_INPUT_AXIOM",{"reason":"partition"}
    if set(P["f"])!=ps["S"]|ps["X0"]:
        return "FAIL_INPUT_AXIOM",{"reason":"f_domain"}
    ok,bad=proper(P,P["f"],ps["S"]|ps["X0"])
    if not ok:return "FAIL_INPUT_AXIOM",{"reason":"f_not_proper","witness":bad}
    if not connected(P,V-ps["X0"]):return "FAIL_INPUT_AXIOM",{"reason":"axiom_i"}
    if not connected(P,ps["S"]):return "FAIL_INPUT_AXIOM",{"reason":"axiom_ii_seed"}
    if any(ps["S"] <= nbr(P,v) for v in V-ps["S"]):return "FAIL_INPUT_AXIOM",{"reason":"axiom_ii_complete_to_seed"}
    expected_y0=V-(Nset(P,ps["S"])|ps["X0"]|ps["S"])
    if ps["Y0"]!=expected_y0:return "FAIL_INPUT_AXIOM",{"reason":"axiom_iii","expected":sorted(expected_y0),"actual":sorted(ps["Y0"])}
    y0edges=[(a,b) for a,b in E(P) if a in ps["Y0"] and b in ps["Y0"]]
    for v in V-(ps["Y0"]|ps["X0"]):
        for a,b in y0edges:
            if (a in nbr(P,v))!=(b in nbr(P,v)):
                return "FAIL_INPUT_AXIOM",{"reason":"axiom_iv","vertex":v,"edge":[a,b]}
    for v in V-ps["S"]:
        l=len(list_colors(P,v)); target={1:"X0",2:"X",3:"Y",4:"Y0"}[l]
        if v not in ps[target]:return "FAIL_INPUT_AXIOM",{"reason":"axiom_v","vertex":v,"list_size":l,"expected":target}
    if require_p7:
        pw=induced_pt_witness(P,7)
        if pw:return "FAIL_NOT_P7_FREE",{"ordered_induced_P7":pw}
    return "PASS_INPUT",{}

def fT(P,T): return frozenset(P["f"][v] for v in T)
def type_of(P,v): return tuple(sorted(nbr(P,v)&set(P["S"])))
def YT(P,T): return {v for v in P["Y"] if type_of(P,v)==tuple(T)}
def NY0(P): return Nset(P,P["Y0"])
def relevant_pairs(P):
    S=sorted(P["S"]); Ts=[]
    for r in range(1,len(S)+1):
        for T in itertools.combinations(S,r):
            if len(fT(P,T))==1: Ts.append(tuple(T))
    return [(T,Tp) for T in Ts for Tp in Ts if fT(P,T)!=fT(P,Tp)]

def load_parent(path):
    spec=importlib.util.spec_from_file_location("rigidity_parent",path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod

def rigidity_receipt(P,T,Tp,p,n,a,b,parent):
    x=copy.deepcopy(P); x["roles"]={"y":p,"y_prime":n,"zL":a,"zR":b}
    return parent.check_instance(x)

def select_local(P,c,T,Tp,parent):
    alpha=next(iter(fT(P,T))); beta=next(iter(fT(P,Tp))); ny0=NY0(P)
    left=sorted(YT(P,T)&ny0); right=sorted(YT(P,Tp)&ny0)
    bad=[]
    for p in left:
        for n in right:
            if has(P,p,n): continue
            if c[p] in {alpha,beta} or c[n] in {alpha,beta}: continue
            bad.append((p,n))
    if bad:
        p,n=bad[0]
        common=sorted(z for z in P["Y0"] if has(P,p,z) and has(P,n,z))
        if common:
            z=common[0]
            return {"mode":"111","T":list(T),"T_prime":list(Tp),"p":p,"m":z,"n":n},{"branch":"A1_111"}
        As=sorted(z for z in P["Y0"] if has(P,p,z)); Bs=sorted(z for z in P["Y0"] if has(P,n,z))
        if not As or not Bs:return None,{"branch":"A2_SPLIT4","failure":"missing_attachment"}
        a,b=As[0],Bs[0]
        rel={"p-b":not has(P,p,b),"a-n":not has(P,a,n),"a-b":not has(P,a,b),"p-n":not has(P,p,n)}
        if not all(rel.values()):return None,{"branch":"A2_SPLIT4","failure":"derived_nonedge","relations":rel}
        rec=rigidity_receipt(P,T,Tp,p,n,a,b,parent)
        if rec.get("verdict")!="PASS_P7_CORRIDOR_RIGIDITY":
            return None,{"branch":"A2_SPLIT4","failure":"rigidity","receipt":rec}
        return {"mode":"SPLIT4","T":list(T),"T_prime":list(Tp),"p":p,"a":a,"b":b,"n":n,
                "corridor":rec["corridor_certificate"]["order"]},{"branch":"A2_SPLIT4","rigidity":rec}
    cand=[n for n in right if c[n]!=alpha]
    if cand:return {"mode":"001","T":list(T),"T_prime":list(Tp),"n":cand[0]},{"branch":"B_001"}
    if any(c[n]!=alpha for n in right):return None,{"branch":"C_000","failure":"C_color_fact"}
    return {"mode":"000","T":list(T),"T_prime":list(Tp)},{"branch":"C_000"}

def q_state_valid(P,st,parent=None):
    T=tuple(st["T"]);Tp=tuple(st["T_prime"]);m=st["mode"]
    if m=="000":return True,"ok"
    if m=="001":return (st["n"] in YT(P,Tp),"ok" if st["n"] in YT(P,Tp) else "001_N_wrong_type")
    if m=="111":
        p,z,n=st["p"],st["m"],st["n"]
        ok=p in YT(P,T) and n in YT(P,Tp) and z in P["Y0"] and has(P,z,p) and has(P,z,n) and not has(P,p,n)
        return ok,"ok" if ok else "111_membership"
    if m=="SPLIT4":
        p,a,b,n=st["p"],st["a"],st["b"],st["n"]
        ok=(p in YT(P,T)&NY0(P) and n in YT(P,Tp)&NY0(P) and a in P["Y0"] and b in P["Y0"] and
            has(P,p,a) and has(P,b,n) and not has(P,p,n) and not has(P,p,b) and not has(P,a,n) and not has(P,a,b))
        if not ok:return False,"split_membership"
        if parent is not None:
            rec=rigidity_receipt(P,T,Tp,p,n,a,b,parent)
            if rec.get("verdict")!="PASS_P7_CORRIDOR_RIGIDITY":return False,"rigidity"
        return True,"ok"
    return False,"unknown_mode"

def local_support(st):
    m=st["mode"]
    if m=="000":return set()
    if m=="001":return {st["n"]}
    if m=="111":return {st["p"],st["m"],st["n"]}
    if m=="SPLIT4":return {st["p"],st["a"],st["b"],st["n"]}
    raise KeyError(m)

def local_Z(P,st,variant):
    T=tuple(st["T"]);Tp=tuple(st["T_prime"]);ny0=NY0(P);m=st["mode"]
    if m=="000":return YT(P,Tp)&ny0
    if m=="001":
        base=YT(P,Tp) if variant=="FORMAL_DEFINITION" else YT(P,T)
        return (base&ny0)-nbr(P,st["n"])
    if m in {"111","SPLIT4"}:return set()
    raise KeyError(m)

def local_forcing(P,st,variant):
    if st["mode"]=="000":return next(iter(fT(P,tuple(st["T"]))))
    if st["mode"]=="001":
        return next(iter(fT(P,tuple(st["T"] if variant=="FORMAL_DEFINITION" else st["T_prime"]))))
    return None

def q_projections(P,Q,variant):
    A=set().union(*(local_support(st) for st in Q)) if Q else set()
    zparts=[local_Z(P,st,variant) for st in Q]
    Z=set().union(*zparts) if zparts else set()
    return A,Z,zparts

def forcing_map(P,Q,variant):
    fmap=collections.defaultdict(list)
    for st in Q:
        fc=local_forcing(P,st,variant)
        if fc is None:continue
        for v in local_Z(P,st,variant):fmap[v].append({"color":fc,"state":st})
    return dict(fmap)

def check_admissible(P,Q,fprime,variant,parent=None):
    A,Z,zparts=q_projections(P,Q,variant)
    if set(fprime)!=A|Z:return False,{"reason":"domain","A":sorted(A),"Z_FORCE":sorted(Z)}
    fmap=forcing_map(P,Q,variant)
    conflicts={v:items for v,items in fmap.items() if len({x["color"] for x in items})>1}
    if conflicts:return False,{"reason":"FAIL_Z_FORCE_COLOR_CONFLICT","conflicts":conflicts}
    for st,zs in zip(Q,zparts):
        ok,why=q_state_valid(P,st,parent)
        if not ok:return False,{"reason":"state_invalid","detail":why,"state":st}
        banned=fT(P,tuple(st["T"]))|fT(P,tuple(st["T_prime"]))
        if st["mode"] in {"001","111","SPLIT4"}:
            ep=[st[x] for x in (["n"] if st["mode"]=="001" else ["p","n"])]
            if any(fprime[v] in banned for v in ep):return False,{"reason":"endpoint_color","state":st}
        fc=local_forcing(P,st,variant)
        if fc is not None:
            for v in zs:
                if fprime[v]!=fc:return False,{"reason":"forced_Z_color","vertex":v,"required":fc,"actual":fprime[v],"state":st}
    merged=dict(P["f"]);merged.update(fprime)
    ok,bad=proper(P,merged,set(P["S"])|A|set(P["X0"])|Z)
    if not ok:return False,{"reason":"global_color_consistency","witness":bad}
    return True,{"A":sorted(A),"Z_FORCE":sorted(Z),"overlap":sorted(A&Z),"forcing_map":fmap}

def normalized_constructor(P,Q,fprime,variant):
    A,Z,_=q_projections(P,Q,variant); ZX=Z-A
    out=copy.deepcopy(P)
    out["S"]=sorted(set(P["S"])|A)
    out["X0"]=sorted(set(P["X0"])|ZX)
    out["X"]=sorted(set(P["X"]))
    out["Y0"]=sorted(set(P["Y0"])-(A|Nset(P,A)))
    out["Y"]=sorted((set(P["Y"])-(A|Z))|(Nset(P,A)&set(P["Y0"])))
    nf=dict(P["f"]);nf.update(fprime);out["f"]=nf
    return out,{"A":sorted(A),"Z_FORCE":sorted(Z),"Z_X0":sorted(ZX),"overlap":sorted(A&Z),"forcing_map":forcing_map(P,Q,variant)}

def seeded_typing(P):
    V=set(P["vertices"]); ps={k:set(P[k]) for k in ["S","X0","X","Y0","Y"]}
    if set().union(*ps.values())!=V:return False,{"reason":"cover"}
    if sum(map(len,ps.values()))!=len(V):return False,{"reason":"overlap","parts":{k:sorted(v) for k,v in ps.items()}}
    if set(P["f"])!=ps["S"]|ps["X0"]:return False,{"reason":"f_domain"}
    ok,bad=proper(P,P["f"],ps["S"]|ps["X0"])
    if not ok:return False,{"reason":"proper","witness":bad}
    return True,{}

def normal_subcase(P,Pp):
    ok,det=seeded_typing(Pp)
    if not ok:return False,{"reason":"typing","detail":det}
    S=set(P["S"]);Sp=set(Pp["S"]);X0=set(P["X0"]);X0p=set(Pp["X0"])
    X=set(P["X"]);Y0=set(P["Y0"]);Y=set(P["Y"])
    if not connected(Pp,Sp) or not S<=Sp:return False,{"reason":"seed_connectivity"}
    for v in X0p&Y0:
        if not (nbr(Pp,v)&Sp):return False,{"reason":"new_X0_old_Y0_no_seed_neighbor","vertex":v}
    if not Sp<=S|X|Y0|Y:return False,{"reason":"seed_containment"}
    if not X0<=X0p or not X0p<=X0|X|Y0|Y:return False,{"reason":"X0_containment"}
    for v in (S|X0):
        if Pp["f"].get(v)!=P["f"].get(v):return False,{"reason":"old_color_changed","vertex":v}
    return True,{}

def all_extensions(P):
    V=sorted(P["vertices"]); fixed=dict(P["f"]); free=[v for v in V if v not in fixed];out=[]
    for vals in itertools.product(range(1,5),repeat=len(free)):
        c=fixed.copy();c.update(dict(zip(free,vals)))
        ok,_=proper(P,c,V)
        if ok:out.append(c)
    return out

def ckey(c): return tuple(sorted(c.items()))

def enumerate_local_family(P,T,Tp,parent,include_001=True):
    states=[{"mode":"000","T":list(T),"T_prime":list(Tp)}]
    if include_001:
        for n in sorted(YT(P,Tp)):
            states.append({"mode":"001","T":list(T),"T_prime":list(Tp),"n":n})
    for p in sorted(YT(P,T)):
        for n in sorted(YT(P,Tp)):
            if has(P,p,n):continue
            for z in sorted(P["Y0"]):
                if has(P,p,z) and has(P,n,z):
                    states.append({"mode":"111","T":list(T),"T_prime":list(Tp),"p":p,"m":z,"n":n})
    for p in sorted(YT(P,T)&NY0(P)):
        for n in sorted(YT(P,Tp)&NY0(P)):
            if has(P,p,n):continue
            if any(has(P,p,z) and has(P,n,z) for z in P["Y0"]):continue
            for a in sorted(P["Y0"]):
                if not has(P,p,a):continue
                for b in sorted(P["Y0"]):
                    if not has(P,n,b):continue
                    if len({p,n,a,b})<4:continue
                    if has(P,p,b) or has(P,a,n) or has(P,a,b):continue
                    rec=rigidity_receipt(P,T,Tp,p,n,a,b,parent)
                    if rec.get("verdict")=="PASS_P7_CORRIDOR_RIGIDITY":
                        states.append({"mode":"SPLIT4","T":list(T),"T_prime":list(Tp),"p":p,"a":a,"b":b,"n":n,"corridor":rec["corridor_certificate"]["order"]})
    seen=set();out=[]
    for st in states:
        k=json.dumps(st,sort_keys=True,separators=(",",":"))
        if k not in seen:seen.add(k);out.append(st)
    return out

def state_semantic_key(st):
    x={k:v for k,v in st.items() if k!="corridor"}
    return json.dumps(x,sort_keys=True,separators=(",",":"))

def extension_variant_record(P,c,parent,variant):
    Q=[]; branches=[]; family_ok=True
    for T,Tp in relevant_pairs(P):
        st,meta=select_local(P,c,T,Tp,parent)
        if st is None:
            return {"state":None,"Z_FORCE":None,"admissibility":False,"extension_semantics":None,"verdict":"FAIL_LOCAL_BRANCH_COVERAGE","failure":meta}
        fam=enumerate_local_family(P,T,Tp,parent,include_001=True)
        if state_semantic_key(st) not in {state_semantic_key(x) for x in fam}:family_ok=False
        Q.append(st);branches.append({"T":list(T),"T_prime":list(Tp),"branch":meta["branch"],"state":st})
    A,Z,_=q_projections(P,Q,variant);fprime={v:c[v] for v in A|Z}
    adm,adet=check_admissible(P,Q,fprime,variant,parent)
    if not adm:
        return {"state":branches,"Z_FORCE":sorted(Z),"admissibility":{"pass":False,"detail":adet},"extension_semantics":{"c_captured":False},"poly_family_contains_selected":family_ok,"verdict":adet.get("reason","FAIL_ADMISSIBILITY")}
    Pn,meta=normalized_constructor(P,Q,fprime,variant)
    typed,td=seeded_typing(Pn);ns,nd=normal_subcase(P,Pn)
    if not typed or not ns:
        return {"state":branches,"Z_FORCE":sorted(Z),"admissibility":{"pass":True,"detail":adet},"extension_semantics":{"c_captured":False},"poly_family_contains_selected":family_ok,"normalized":meta,"verdict":"FAIL_NORMALIZED_GLOBAL_TYPING","typing":td,"normal_subcase":nd}
    for v in A&Z:
        if v not in Pn["S"] or v in Pn["X0"] or fprime[v]!=c[v]:
            return {"state":branches,"Z_FORCE":sorted(Z),"admissibility":{"pass":True,"detail":adet},"extension_semantics":{"c_captured":False},"poly_family_contains_selected":family_ok,"normalized":meta,"verdict":"FAIL_SPLIT4_GLOBAL_ROLE_INTERACTION","vertex":v}
    if not connected(Pn,Pn["S"]):
        return {"state":branches,"Z_FORCE":sorted(Z),"admissibility":{"pass":True,"detail":adet},"extension_semantics":{"c_captured":False},"poly_family_contains_selected":family_ok,"normalized":meta,"verdict":"FAIL_GLOBAL_CONNECTIVITY"}
    c_captured=all(c[v]==Pn["f"][v] for v in set(Pn["S"])|set(Pn["X0"]))
    orig_ext={ckey(x) for x in all_extensions(P)}; sub_ext={ckey(x) for x in all_extensions(Pn)}
    sound=sub_ext<=orig_ext
    return {"state":branches,"Z_FORCE":sorted(Z),"admissibility":{"pass":True,"detail":adet},
            "extension_semantics":{"c_captured":c_captured,"sub_extensions":len(sub_ext),"original_extensions":len(orig_ext),"sound_subset":sound},
            "poly_family_contains_selected":family_ok,"normalized":meta,
            "verdict":"PASS_VARIANT" if c_captured and sound and family_ok else ("FAIL_POLY_ENUMERATION" if not family_ok else ("FAIL_RAW_SOUNDNESS" if not sound else "FAIL_RAW_COMPLETENESS"))}

def variant_invariant(a,b):
    return (a.get("Z_FORCE")==b.get("Z_FORCE") and
            a.get("admissibility")==b.get("admissibility") and
            a.get("extension_semantics")==b.get("extension_semantics") and
            a.get("verdict")==b.get("verdict") and
            a.get("state")==b.get("state"))

def classify_extension(P,c,parent):
    a=extension_variant_record(P,c,parent,"FORMAL_DEFINITION")
    b=extension_variant_record(P,c,parent,"COMPLETENESS_TEXT")
    any001=any(x.get("branch")=="B_001" for x in (a.get("state") or [])) or any(x.get("branch")=="B_001" for x in (b.get("state") or []))
    inv=variant_invariant(a,b)
    authoritative=(not any001) or inv
    return {"formal_definition":a,"completeness_text":b,"variant_invariant":inv,"affects_main_authority":False if not authoritative else True,"authoritative":authoritative}

def all_authoritative_global_states(P,parent):
    pairs=relevant_pairs(P); families=[]
    for T,Tp in pairs:
        fam=[st for st in enumerate_local_family(P,T,Tp,parent,include_001=False)]
        families.append(fam)
    for combo in itertools.product(*families):
        yield list(combo)

def admissible_functions(P,Q,variant="FORMAL_DEFINITION"):
    A,Z,_=q_projections(P,Q,variant); fmap=forcing_map(P,Q,variant)
    if any(len({x["color"] for x in items})>1 for items in fmap.values()):return []
    forced={v:items[0]["color"] for v,items in fmap.items()}
    out=[]
    for vals in itertools.product(range(1,5),repeat=len(A)):
        fp=dict(zip(sorted(A),vals));bad=False
        for v,color in forced.items():
            if v in fp and fp[v]!=color:bad=True;break
            fp[v]=color
        if bad:continue
        if set(fp)!=A|Z:continue
        ok,_=check_admissible(P,Q,fp,variant,parent=None)
        if ok:out.append(fp)
    return out

def exhaustive_authoritative_soundness(P,parent,limit_states=100000):
    orig={ckey(c) for c in all_extensions(P)}; checked_Q=0; checked_adm=0
    first_fail=None
    for Q in all_authoritative_global_states(P,parent):
        checked_Q+=1
        if checked_Q>limit_states:return {"pass":False,"verdict":"FAIL_POLY_ENUMERATION","reason":"finite_harness_limit","checked_Q":checked_Q}
        for fp in admissible_functions(P,Q):
            checked_adm+=1
            Pn,meta=normalized_constructor(P,Q,fp,"FORMAL_DEFINITION")
            typed,td=seeded_typing(Pn);ns,nd=normal_subcase(P,Pn)
            if not typed or not ns:
                first_fail={"verdict":"FAIL_NORMALIZED_GLOBAL_TYPING","Q":Q,"fprime":fp,"typing":td,"normal_subcase":nd,"normalized":meta};break
            sub={ckey(c) for c in all_extensions(Pn)}
            if not sub<=orig:
                first_fail={"verdict":"FAIL_RAW_SOUNDNESS","Q":Q,"fprime":fp,"extra_extensions":[list(x) for x in sorted(sub-orig)[:3]],"normalized":meta};break
        if first_fail:break
    return {"pass":first_fail is None,"checked_global_Q":checked_Q,"checked_admissible_functions":checked_adm,"first_fail":first_fail}

def auth_overlap_fixture():
    return {
      "id":"AUTH_SPLIT4_SUPPORT_LEGACY_ZFORCE_OVERLAP",
      "vertices":["s1","s2","s3","p","n","w","a","b"],
      "edges":[["s1","s2"],["s2","s3"],["s1","s3"],["p","s1"],["p","a"],["p","w"],["n","s2"],["n","b"],["w","s3"],["w","b"]],
      "S":["s1","s2","s3"],"X0":[],"X":[],"Y0":["a","b"],"Y":["p","n","w"],
      "f":{"s1":1,"s2":2,"s3":3},
      "c":{"s1":1,"s2":2,"s3":3,"p":3,"n":4,"w":1,"a":1,"b":2}
    }
def fixture_a2():
    return {"id":"AUTH_A2_CANONICAL_SPLIT4","vertices":["a","p","s1","s2","n","b"],"edges":[["a","p"],["p","s1"],["s1","s2"],["s2","n"],["n","b"]],"S":["s1","s2"],"X0":[],"X":[],"Y0":["a","b"],"Y":["p","n"],"f":{"s1":1,"s2":2},"c":{"s1":1,"s2":2,"p":3,"n":4,"a":1,"b":1}}
def fixture_a1():
    return {"id":"AUTH_A1_COMMON111","vertices":["p","s1","s2","n","z"],"edges":[["p","s1"],["s1","s2"],["s2","n"],["p","z"],["n","z"]],"S":["s1","s2"],"X0":[],"X":[],"Y0":["z"],"Y":["p","n"],"f":{"s1":1,"s2":2},"c":{"s1":1,"s2":2,"p":3,"n":4,"z":1}}
def fixture_c000():
    return {"id":"AUTH_C_000","vertices":["s1","s2","n","z"],"edges":[["s1","s2"],["s2","n"],["n","z"]],"S":["s1","s2"],"X0":[],"X":[],"Y0":["z"],"Y":["n"],"f":{"s1":1,"s2":2},"c":{"s1":1,"s2":2,"n":1,"z":3}}
def fixture_q001():
    return {"id":"QUARANTINED_001_TEXT_DISCREPANCY","vertices":["s1","s2","s3","v","z"],"edges":[["s1","s2"],["s2","s3"],["s1","s3"],["v","s1"],["v","z"]],"S":["s1","s2","s3"],"X0":[],"X":[],"Y0":["z"],"Y":["v"],"f":{"s1":1,"s2":2,"s3":3},"c":{"s1":1,"s2":2,"s3":3,"v":2,"z":1}}
def legacy_collision_fixture():
    return {"id":"LEGACY_111_PLUS_000_NORMALIZED_REGRESSION","vertices":["s1","s2","s3","v","n","z"],"edges":[["s1","s2"],["s2","s3"],["s1","s3"],["v","s1"],["v","z"],["z","n"],["n","s3"]],"S":["s1","s2","s3"],"X0":[],"X":[],"Y0":["z"],"Y":["v","n"],"f":{"s1":1,"s2":2,"s3":3},"c":{"s1":1,"s2":2,"s3":3,"v":2,"n":4,"z":1}}

def selected_receipt(P,parent):
    iv,det=check_input(P)
    if iv!="PASS_INPUT":return {"fixture_id":P["id"],"verdict":iv,"detail":det}
    c=P["c"]
    ok,bad=proper(P,c,P["vertices"])
    if not ok:return {"fixture_id":P["id"],"verdict":"FAIL_INPUT_AXIOM","detail":{"reason":"c_not_proper","witness":bad}}
    cls=classify_extension(P,c,parent)
    return {"fixture_id":P["id"],"verdict":"PASS_SELECTED_EXTENSION" if cls["authoritative"] and cls["formal_definition"]["verdict"]=="PASS_VARIANT" else ("QUARANTINED_001" if not cls["authoritative"] else cls["formal_definition"]["verdict"]),"classification":cls}

def mandatory_overlap_assertions(P,receipt):
    r=receipt["classification"]["formal_definition"]
    states=r["state"] or []
    branchmap={str((tuple(x["T"]),tuple(x["T_prime"]))):x["branch"] for x in states}
    expected={
      str((("s1",),("s2",))):"A2_SPLIT4",
      str((("s2",),("s1",))):"A2_SPLIT4",
      str((("s1",),("s3",))):"C_000",
      str((("s3",),("s1",))):"C_000",
      str((("s2",),("s3",))):"A1_111",
      str((("s3",),("s2",))):"A1_111"
    }
    meta=r.get("normalized",{}); fmap=(r.get("admissibility",{}).get("detail",{}) or {}).get("forcing_map",{})
    forcing_colors={v:sorted({x["color"] for x in items}) for v,items in fmap.items()}
    return {
      "decision_tree_exact":branchmap==expected,
      "A_exact":set(meta.get("A",[]))=={"p","n","w","a","b"},
      "Z_FORCE_exact":set(meta.get("Z_FORCE",[]))=={"p","w"},
      "overlap_exact":set(meta.get("overlap",[]))=={"p","w"},
      "forcing_p":forcing_colors.get("p")==[3],
      "forcing_w":forcing_colors.get("w")==[1],
      "normalized_variant_pass":r.get("verdict")=="PASS_VARIANT",
      "no_001_in_selected_c":all(x["branch"]!="B_001" for x in states)
    }

def legacy_normalization_regression(P):
    Q=[{"mode":"111","T":["s1"],"T_prime":["s3"],"p":"v","m":"z","n":"n"},{"mode":"000","T":["s2"],"T_prime":["s1"]}]
    A,Z,_=q_projections(P,Q,"FORMAL_DEFINITION");fp={v:P["c"][v] for v in A|Z}
    literal_seed=set(P["S"])|A;literal_X0=set(P["X0"])|Z;collision=literal_seed&literal_X0
    adm,adet=check_admissible(P,Q,fp,"FORMAL_DEFINITION")
    Pn,meta=normalized_constructor(P,Q,fp,"FORMAL_DEFINITION");typed,td=seeded_typing(Pn);ns,nd=normal_subcase(P,Pn)
    return {"fixture_id":P["id"],"literal_collision":sorted(collision),"expected_old_verdict":"FAIL_SUPPORT_Z_COLLISION" if collision else "NO_COLLISION","admissible":adm,"admissibility":adet,"normalized_typed":typed,"normal_subcase":ns,"typing_detail":td,"normal_detail":nd,"normalized":meta,
            "overlap_force_preserved":all(v in Pn["S"] and v not in Pn["X0"] and fp[v]==Pn["f"][v] for v in A&Z),
            "verdict":"PASS_LEGACY_NORMALIZATION_REGRESSION" if collision and adm and typed and ns else "FAIL_NORMALIZED_GLOBAL_TYPING"}

def negative_force_conflict(P):
    Q=[{"mode":"000","T":["s1"],"T_prime":["s3"]},{"mode":"000","T":["s2"],"T_prime":["s3"]}]
    A,Z,_=q_projections(P,Q,"FORMAL_DEFINITION");fp={v:P["c"].get(v,1) for v in A|Z}
    adm,det=check_admissible(P,Q,fp,"FORMAL_DEFINITION")
    return {"id":"NEG_Z_FORCE_COLOR_CONFLICT","admissible":adm,"detail":det,"verdict":"PASS_NEGATIVE_CONTROL" if (not adm and det.get("reason")=="FAIL_Z_FORCE_COLOR_CONFLICT") else "FAIL_NEGATIVE_CONTROL"}

def run(outdir,parent_path):
    parent=load_parent(parent_path);root=pathlib.Path(outdir);root.mkdir(parents=True,exist_ok=True)
    main=auth_overlap_fixture();controls=[main,fixture_a2(),fixture_a1(),fixture_c000()]
    receipts=[]
    for P in controls:
        rec=selected_receipt(P,parent);receipts.append(rec)
        (root/(P["id"]+".fixture.json")).write_text(json.dumps(P,indent=2,sort_keys=True)+"\n")
        (root/(P["id"]+".receipt.json")).write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
    mainrec=receipts[0];overlap_checks=mandatory_overlap_assertions(main,mainrec)

    ext_records=[];authoritative_pass=True;quarantine=[];authoritative_count=0
    first_fail=None
    for c in all_extensions(main):
        cls=classify_extension(main,c,parent)
        item={"c":c,"variant_invariant":cls["variant_invariant"],"authoritative":cls["authoritative"],
              "formal_definition":cls["formal_definition"],"completeness_text":cls["completeness_text"],
              "affects_main_authority":cls["authoritative"]}
        if cls["authoritative"]:
            authoritative_count+=1
            if cls["formal_definition"]["verdict"]!="PASS_VARIANT":
                authoritative_pass=False
                if first_fail is None:first_fail={"verdict":cls["formal_definition"]["verdict"],"witness":item,"first_failing_inference":"AUTHORITATIVE_EXTENSION_COMPLETENESS"}
        else:
            item["affects_main_authority"]=False;quarantine.append(item)
        ext_records.append(item)
    (root/"main_all_extensions.json").write_text(json.dumps(ext_records,indent=2,sort_keys=True)+"\n")

    sound=exhaustive_authoritative_soundness(main,parent)
    if not sound["pass"] and first_fail is None:
        first_fail={"verdict":sound["first_fail"]["verdict"] if sound.get("first_fail") else sound.get("verdict","FAIL_RAW_SOUNDNESS"),"witness":sound.get("first_fail"),"first_failing_inference":"AUTHORITATIVE_CANDIDATE_SOUNDNESS"}
        authoritative_pass=False

    legP=legacy_collision_fixture();leg=legacy_normalization_regression(legP)
    (root/(legP["id"]+".fixture.json")).write_text(json.dumps(legP,indent=2,sort_keys=True)+"\n")
    (root/(legP["id"]+".receipt.json")).write_text(json.dumps(leg,indent=2,sort_keys=True)+"\n")

    qP=fixture_q001();qcls=classify_extension(qP,qP["c"],parent)
    qrec={"fixture_id":qP["id"],"001_quarantine":{
      "formal_definition":qcls["formal_definition"],"completeness_text":qcls["completeness_text"],
      "variant_invariant":qcls["variant_invariant"],"affects_main_authority":False},
      "verdict":"QUARANTINED_001_RECORDED"}
    (root/(qP["id"]+".fixture.json")).write_text(json.dumps(qP,indent=2,sort_keys=True)+"\n")
    (root/(qP["id"]+".receipt.json")).write_text(json.dumps(qrec,indent=2,sort_keys=True)+"\n")

    neg=negative_force_conflict(main);(root/"NEG_Z_FORCE_COLOR_CONFLICT.receipt.json").write_text(json.dumps(neg,indent=2,sort_keys=True)+"\n")

    selected_controls_ok=(all(r["verdict"]=="PASS_SELECTED_EXTENSION" for r in receipts) and all(overlap_checks.values()))
    regression_ok=(leg["verdict"]=="PASS_LEGACY_NORMALIZATION_REGRESSION")
    negative_ok=(neg["verdict"]=="PASS_NEGATIVE_CONTROL")
    poly={"n":len(main["vertices"]),"s":len(main["S"]),"t":len(relevant_pairs(main)),
          "local_state_upper_bound":"<=4*n^4 per ordered pair",
          "global_state_upper_bound":"<=(4*n^4)^t",
          "support_bound":"<=4t","normalization_extra_cost":"one set difference Z_FORCE\\A",
          "uses_extension_oracle_for_enumeration":False}

    if not selected_controls_ok and first_fail is None:
        first_fail={"verdict":"FAIL_SPLIT4_GLOBAL_ROLE_INTERACTION","witness":{"control_receipts":receipts,"overlap_checks":overlap_checks},"first_failing_inference":"MANDATORY_REGRESSION"}
        authoritative_pass=False
    if not regression_ok and first_fail is None:
        first_fail={"verdict":"FAIL_NORMALIZED_GLOBAL_TYPING","witness":leg,"first_failing_inference":"LEGACY_NORMALIZATION_REGRESSION"};authoritative_pass=False
    if not negative_ok and first_fail is None:
        first_fail={"verdict":"FAIL_Z_FORCE_COLOR_CONFLICT","witness":neg,"first_failing_inference":"NEGATIVE_CONTROL"};authoritative_pass=False

    core_pass=authoritative_pass and selected_controls_ok and regression_ok and negative_ok and sound["pass"]
    scientific=PASS if core_pass else first_fail["verdict"]
    full_status=("FULL_SOURCE_DOMAIN_CONDITIONS_SATISFIED" if not quarantine else FULL_OPEN)
    summary={
      "schema":"janus.trump.p7_split4.normalized_raw_rerun.v1",
      "scientific_gate":scientific,
      "authoritative_core_verified":core_pass,
      "authority_mode":"FROZEN_GATE_PROOF_CARRYING_FINITE_EXECUTION__UNIVERSAL_P7_THEOREM_NOT_CLAIMED",
      "mandatory_overlap_checks":overlap_checks,
      "selected_control_verdicts":{r["fixture_id"]:r["verdict"] for r in receipts},
      "legacy_normalization_regression":leg["verdict"],
      "negative_force_conflict_control":neg["verdict"],
      "exhaustive_main_extensions":{"total":len(ext_records),"authoritative":authoritative_count,"quarantined_001":len(quarantine),"all_authoritative_pass":authoritative_pass},
      "authoritative_candidate_soundness":sound,
      "poly_constructibility":poly,
      "001_quarantine":{"cases":quarantine,"count":len(quarantine),"explicit_fixture":qrec,"SOURCE_001_RESOLVED":False},
      "full_source_domain":full_status,
      "first_failure":first_fail,
      "ceiling":{
        "SUBGATE_A":"OPEN","LEMMA7_P7_TRANSFER":"NOT_STARTED","LEMMA10_P7_TRANSFER":"NOT_STARTED","BREAK_B":"NOT_STARTED","SUBGATE_B":"NOT_STARTED","LEMMA11_P7_LIFT":"OPEN","P7_FREE_4_COLOR_IN_P":"NOT_PROVED","HARDNESS_LOCALIZED":"NOT_CLAIMED","P_VS_NP":"OPEN"
      },
      "successor_autoactivated":False
    }
    (root/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"scientific_gate":scientific,"authoritative_extensions":authoritative_count,"quarantined_001":len(quarantine),"soundness_Q":sound.get("checked_global_Q"),"soundness_admissible":sound.get("checked_admissible_functions"),"full_source_domain":full_status},sort_keys=True))

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--out",required=True);ap.add_argument("--rigidity-parent",required=True);args=ap.parse_args();run(args.out,args.rigidity_parent)
