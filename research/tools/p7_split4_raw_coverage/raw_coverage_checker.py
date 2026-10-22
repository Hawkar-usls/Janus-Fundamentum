#!/usr/bin/env python3
import argparse, collections, hashlib, importlib.util, itertools, json, pathlib, sys

PASS_LOCAL="PASS_RAW_COVERAGE_LOCAL"
FAIL_INPUT="FAIL_INPUT_AXIOM"
FAIL_P7="FAIL_NOT_P7_FREE"
FAIL_LOCAL="FAIL_LOCAL_BRANCH_COVERAGE"
FAIL_SPLIT="FAIL_SPLIT4_LOCAL_SCHEMA"
FAIL_RIGIDITY="FAIL_RIGIDITY_BINDING"
FAIL_ROLE="FAIL_GLOBAL_ROLE_COLLISION"
FAIL_SZ="FAIL_SUPPORT_Z_COLLISION"
FAIL_TYPING="FAIL_GLOBAL_TYPING"
FAIL_CONN="FAIL_GLOBAL_CONNECTIVITY"
FAIL_COLOR="FAIL_GLOBAL_COLOR_CONSISTENCY"
FAIL_POLY="FAIL_POLY_ENUMERATION"

def ce(a,b): return tuple(sorted((str(a),str(b))))
def E(o): return {ce(a,b) for a,b in o["edges"]}
def nbr(o,v):
    ee=E(o)
    return {u for u in o["vertices"] if u!=v and ce(u,v) in ee}
def Nset(o,A):
    A=set(A)
    return set().union(*(nbr(o,v) for v in A)) - A if A else set()
def digest(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def connected(o,A):
    A=set(A)
    if not A: return False
    q=collections.deque([next(iter(A))]); seen=set()
    while q:
        v=q.popleft()
        if v in seen: continue
        seen.add(v)
        for u in nbr(o,v)&A:
            if u not in seen:q.append(u)
    return seen==A

def induced_path(o,seq):
    ee=E(o); seq=list(seq)
    if len(set(seq))!=len(seq): return False
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            if ((ce(a,seq[j]) in ee) != (j==i+1)): return False
    return True

def p7_witness(o):
    vs=sorted(o["vertices"])
    for comb in itertools.combinations(vs,7):
        for perm in itertools.permutations(comb):
            if induced_path(o,perm): return list(perm)
    return None

def proper(o,col,domain=None):
    dom=set(domain if domain is not None else col)
    ee=E(o)
    for a,b in ee:
        if a in dom and b in dom and col.get(a)==col.get(b):
            return False,(a,b,col.get(a))
    return True,None

def list_colors(o,v):
    if v in o["S"] or v in o["X0"]: return {o["f"][v]}
    used={o["f"][s] for s in nbr(o,v)&set(o["S"])}
    return {1,2,3,4}-used

def check_input(o):
    V=set(o["vertices"])
    parts={k:set(o[k]) for k in ["S","X0","X","Y0","Y"]}
    union=set().union(*parts.values())
    if union!=V: return FAIL_INPUT,{"reason":"partition_does_not_cover","missing":sorted(V-union),"extra":sorted(union-V)}
    names=list(parts)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            inter=parts[a]&parts[b]
            if inter:return FAIL_INPUT,{"reason":"input_partition_overlap","sets":[a,b],"vertices":sorted(inter)}
    if set(o["f"]) != parts["S"]|parts["X0"]:
        return FAIL_INPUT,{"reason":"f_domain_mismatch"}
    ok,bad=proper(o,o["f"],parts["S"]|parts["X0"])
    if not ok:return FAIL_INPUT,{"reason":"input_precoloring_not_proper","witness":bad}
    if not connected(o,V-parts["X0"]):return FAIL_INPUT,{"reason":"axiom_i"}
    if not connected(o,parts["S"]):return FAIL_INPUT,{"reason":"axiom_ii_seed_not_connected"}
    for v in V-parts["S"]:
        if parts["S"] and parts["S"] <= nbr(o,v):
            return FAIL_INPUT,{"reason":"axiom_ii_complete_to_seed","vertex":v}
    expected_y0=V-(Nset(o,parts["S"])|parts["X0"]|parts["S"])
    if parts["Y0"]!=expected_y0:
        return FAIL_INPUT,{"reason":"axiom_iii","expected":sorted(expected_y0),"actual":sorted(parts["Y0"])}
    # axiom iv
    y0edges=[(a,b) for a,b in E(o) if a in parts["Y0"] and b in parts["Y0"]]
    for v in V-(parts["Y0"]|parts["X0"]):
        for a,b in y0edges:
            if (a in nbr(o,v)) != (b in nbr(o,v)):
                return FAIL_INPUT,{"reason":"axiom_iv","vertex":v,"edge":[a,b]}
    # axiom v
    for v in V-parts["S"]:
        l=len(list_colors(o,v))
        target={1:"X0",2:"X",3:"Y",4:"Y0"}[l]
        if v not in parts[target]:
            return FAIL_INPUT,{"reason":"axiom_v","vertex":v,"list_size":l,"expected_part":target}
    pw=p7_witness(o)
    if pw:return FAIL_P7,{"ordered_induced_P7":pw}
    c=o["c"]
    if set(c)!=V:return FAIL_INPUT,{"reason":"extension_domain"}
    ok,bad=proper(o,c,V)
    if not ok:return FAIL_INPUT,{"reason":"c_not_proper","witness":bad}
    for v in parts["S"]|parts["X0"]:
        if c[v]!=o["f"][v]:return FAIL_INPUT,{"reason":"c_not_extension","vertex":v}
    return "PASS_INPUT",{}

def all_types(o):
    S=sorted(o["S"]); f=o["f"]
    out=[]
    for r in range(len(S)+1):
        for comb in itertools.combinations(S,r):
            colors={f[v] for v in comb}
            if len(colors)==1: out.append(tuple(comb))
    return sorted(out)

def fT(o,T):
    return frozenset(o["f"][v] for v in T)

def type_of(o,v):
    return tuple(sorted(nbr(o,v)&set(o["S"])))

def YT(o,T):
    return {v for v in o["Y"] if type_of(o,v)==tuple(T)}

def NY0(o):
    return Nset(o,o["Y0"])

def relevant_pairs(o):
    ts=all_types(o)
    return [(T,Tp) for T in ts for Tp in ts if fT(o,T)!=fT(o,Tp)]

def load_parent(path):
    spec=importlib.util.spec_from_file_location("rigidity_parent",path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def state_key(st):
    return json.dumps(st,sort_keys=True,separators=(",",":"))

def rigidity_receipt(o,T,Tp,p,n,a,b,parent):
    x=json.loads(json.dumps(o))
    x["roles"]={"y":p,"y_prime":n,"zL":a,"zR":b}
    rec=parent.check_instance(x)
    return rec

def enumerate_local_states_no_c(o,T,Tp,parent):
    ys=sorted(YT(o,T)); yn=sorted(YT(o,Tp)); y0=sorted(o["Y0"]); ny0=NY0(o)
    states=[{"mode":"000","T":list(T),"T_prime":list(Tp)}]
    for n in yn:
        states.append({"mode":"001","T":list(T),"T_prime":list(Tp),"n":n})
    for p in ys:
        for n in yn:
            if ce(p,n) in E(o): continue
            for z in y0:
                if ce(p,z) in E(o) and ce(n,z) in E(o):
                    states.append({"mode":"111","T":list(T),"T_prime":list(Tp),"p":p,"z":z,"n":n})
    for p in sorted(set(ys)&ny0):
        for n in sorted(set(yn)&ny0):
            if ce(p,n) in E(o): continue
            commons=[z for z in y0 if ce(p,z) in E(o) and ce(n,z) in E(o)]
            if commons: continue
            for a in y0:
                if ce(p,a) not in E(o): continue
                for b in y0:
                    if ce(n,b) not in E(o): continue
                    if len({p,n,a,b})<4: continue
                    if any(ce(x,y) in E(o) for x,y in [(p,b),(a,n),(a,b)]): continue
                    rec=rigidity_receipt(o,T,Tp,p,n,a,b,parent)
                    if rec.get("verdict")=="PASS_P7_CORRIDOR_RIGIDITY":
                        states.append({"mode":"SPLIT4","T":list(T),"T_prime":list(Tp),"p":p,"a":a,"b":b,"n":n,
                                       "corridor":rec["corridor_certificate"]["order"]})
    return states

def select_local(o,T,Tp,parent):
    c=o["c"]; ny0=NY0(o); alpha=next(iter(fT(o,T))); beta=next(iter(fT(o,Tp)))
    left=sorted(set(YT(o,T))&ny0); right=sorted(set(YT(o,Tp))&ny0)
    bad=[]
    for p in left:
        for n in right:
            if ce(p,n) in E(o):continue
            if c[p] in {alpha,beta} or c[n] in {alpha,beta}:continue
            bad.append((p,n))
    if bad:
        p,n=bad[0]
        common=sorted([z for z in o["Y0"] if ce(p,z) in E(o) and ce(n,z) in E(o)])
        if common:
            z=common[0]
            return {"mode":"111","T":list(T),"T_prime":list(Tp),"p":p,"z":z,"n":n}, {"branch":"A1"}
        As=sorted([z for z in o["Y0"] if ce(p,z) in E(o)])
        Bs=sorted([z for z in o["Y0"] if ce(n,z) in E(o)])
        if not As or not Bs:
            return None,{"branch":"A2","failure":"missing_attachment"}
        a,b=As[0],Bs[0]
        rel={"p-b":ce(p,b) not in E(o),"a-n":ce(a,n) not in E(o),"a-b":ce(a,b) not in E(o),"p-n":ce(p,n) not in E(o)}
        if not all(rel.values()):
            return None,{"branch":"A2","failure":"derived_nonedge","relations":rel,"vertices":[p,a,b,n]}
        rec=rigidity_receipt(o,T,Tp,p,n,a,b,parent)
        if rec.get("verdict")!="PASS_P7_CORRIDOR_RIGIDITY":
            return None,{"branch":"A2","failure":"rigidity","receipt":rec}
        return {"mode":"SPLIT4","T":list(T),"T_prime":list(Tp),"p":p,"a":a,"b":b,"n":n,
                "corridor":rec["corridor_certificate"]["order"]},{"branch":"A2","rigidity":rec}
    cand=[n for n in right if c[n]!=alpha]
    if cand:
        n=cand[0]
        return {"mode":"001","T":list(T),"T_prime":list(Tp),"n":n},{"branch":"B"}
    # C: theorem proof requires all right-side Y0-neighbors colored alpha
    if any(c[n]!=alpha for n in right):
        return None,{"branch":"C","failure":"C_color_fact"}
    return {"mode":"000","T":list(T),"T_prime":list(Tp)},{"branch":"C"}

def local_support(st):
    m=st["mode"]
    if m=="000":return set()
    if m=="001":return {st["n"]}
    if m=="111":return {st["p"],st["z"],st["n"]}
    if m=="SPLIT4":return {st["p"],st["a"],st["b"],st["n"]}
    raise KeyError(m)

def local_Z(o,st):
    T=tuple(st["T"]); Tp=tuple(st["T_prime"]); ny0=NY0(o)
    m=st["mode"]
    if m=="000":
        return set(YT(o,Tp))&ny0
    if m=="001":
        n=st["n"]
        return (set(YT(o,T))&ny0)-nbr(o,n)
    if m in {"111","SPLIT4"}:
        return set()
    raise KeyError(m)

def forced_z_color(o,st):
    if st["mode"]=="000":return next(iter(fT(o,tuple(st["T"]))))
    if st["mode"]=="001":return next(iter(fT(o,tuple(st["T_prime"]))))
    return None

def pairwise_partition(parts):
    names=list(parts)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            inter=set(parts[a])&set(parts[b])
            if inter:return False,{"sets":[a,b],"vertices":sorted(inter)}
    return True,None

def check_global(o,states):
    support=set().union(*(local_support(st) for st in states)) if states else set()
    zsets=[local_Z(o,st) for st in states]
    Z=set().union(*zsets) if zsets else set()
    roles=collections.defaultdict(list)
    for st in states:
        for fld in ["p","z","n","a","b"]:
            if fld in st: roles[st[fld]].append({"mode":st["mode"],"role":fld,"T":st["T"],"T_prime":st["T_prime"]})
    sx0=support&(set(o["X0"])|Z)
    if sx0:
        return FAIL_SZ,{"support":sorted(support),"Z":sorted(Z),"collision":sorted(sx0),"roles":{v:roles[v] for v in sorted(sx0)}},None
    fp={}
    # selected support values are inherited from c in completeness witness
    for v in support: fp[v]=o["c"][v]
    for st,zs in zip(states,zsets):
        fc=forced_z_color(o,st)
        if fc is not None:
            for v in zs:
                if v in fp and fp[v]!=fc:
                    return FAIL_COLOR,{"vertex":v,"support_color":fp[v],"forced_Z_color":fc,"state":st},None
                fp[v]=fc
                if o["c"][v]!=fc:
                    return FAIL_COLOR,{"vertex":v,"c":o["c"][v],"forced_Z_color":fc,"state":st},None
    Snew=set(o["S"])|support
    X0new=set(o["X0"])|Z
    Xnew=set(o["X"])
    Y0new=set(o["Y0"])-(support|Nset(o,support))
    Ynew=(set(o["Y"])-(support|Z)) | (Nset(o,support)&set(o["Y0"]))
    parts={"S":Snew,"X0":X0new,"X":Xnew,"Y0":Y0new,"Y":Ynew}
    ok,why=pairwise_partition(parts)
    if not ok:return FAIL_TYPING,{"reason":"output_partition_overlap","detail":why,"parts":{k:sorted(v) for k,v in parts.items()}},None
    if set().union(*parts.values())!=set(o["vertices"]):
        return FAIL_TYPING,{"reason":"output_partition_cover","parts":{k:sorted(v) for k,v in parts.items()}},None
    if not connected(o,Snew):
        return FAIL_CONN,{"seed":sorted(Snew)},None
    fnew=dict(o["f"]); fnew.update(fp)
    ok,bad=proper(o,fnew,Snew|X0new)
    if not ok:return FAIL_COLOR,{"reason":"f_union_fprime_not_proper","witness":bad},None
    # normal-subcase literal conditions
    if not set(o["S"])<=Snew:
        return FAIL_TYPING,{"reason":"old_seed_not_subset"},None
    if not Snew <= set(o["S"])|set(o["X"])|set(o["Y0"])|set(o["Y"]):
        return FAIL_TYPING,{"reason":"seed_outside_allowed"},None
    if not set(o["X0"])<=X0new:
        return FAIL_TYPING,{"reason":"old_X0_not_subset"},None
    if not X0new <= set(o["X0"])|set(o["X"])|set(o["Y0"])|set(o["Y"]):
        return FAIL_TYPING,{"reason":"X0_outside_allowed"},None
    for v in X0new&set(o["Y0"]):
        if not (nbr(o,v)&Snew):
            return FAIL_TYPING,{"reason":"promoted_Y0_precolored_without_seed_neighbor","vertex":v},None
    return "PASS_GLOBAL_ASSEMBLY",{
      "support":sorted(support),"Z":sorted(Z),"parts":{k:sorted(v) for k,v in parts.items()},
      "f_prime":dict(sorted(fp.items())),"roles":dict(roles)
    },{"parts":parts,"fnew":fnew}

def target_branch_check(o,states,branches):
    target=o.get("target_pair")
    exp=o.get("expected_target_branch")
    if not target or not exp:return True,None
    T=tuple(target[0]); Tp=tuple(target[1])
    key=(T,Tp)
    obs=branches.get(str(key))
    if obs!=exp:return False,{"target_pair":target,"expected":exp,"observed":obs}
    return True,None

def evaluate_fixture(o,parent):
    receipt={"fixture_id":o["id"],"graph_digest":digest(o)}
    iv,detail=check_input(o)
    receipt["input_verdict"]=iv
    if iv!="PASS_INPUT":
        receipt.update(verdict=iv,detail=detail);return receipt
    pairs=relevant_pairs(o); states=[]; branchmap={}; local_receipts=[]
    for T,Tp in pairs:
        st,meta=select_local(o,T,Tp,parent)
        k=str((T,Tp)); branchmap[k]=meta.get("branch")
        if st is None:
            fail=FAIL_RIGIDITY if meta.get("failure")=="rigidity" else (FAIL_SPLIT if meta.get("branch")=="A2" else FAIL_LOCAL)
            receipt.update(verdict=fail,first_failed_pair=[list(T),list(Tp)],failure=meta);return receipt
        family=enumerate_local_states_no_c(o,T,Tp,parent)
        if state_key(st) not in {state_key(x) for x in family}:
            receipt.update(verdict=FAIL_POLY,first_failed_pair=[list(T),list(Tp)],selected_state=st,
                           detail="existentially selected state absent from c-free local family");return receipt
        states.append(st)
        local_receipts.append({"T":list(T),"T_prime":list(Tp),"branch":meta["branch"],"state":st,"c_free_family_size":len(family)})
    ok,why=target_branch_check(o,states,branchmap)
    if not ok:
        receipt.update(verdict=FAIL_LOCAL,detail=why);return receipt
    receipt["local_states"]=local_receipts
    receipt["coverage_local"]=PASS_LOCAL
    gv,gdetail,built=check_global(o,states)
    receipt["global_assembly"]={"verdict":gv,"detail":gdetail}
    if gv!="PASS_GLOBAL_ASSEMBLY":
        receipt.update(verdict=gv,witness={"P":{k:o[k] for k in ["vertices","edges","S","X0","X","Y0","Y","f"]},
                                          "c":o["c"],"local_states":states,"first_failing_inference":gv,
                                          "detail":gdetail})
        return receipt
    n=len(o["vertices"]); s=len(o["S"]); t=len(pairs)
    bound=(4*(n**4))**t
    receipt["poly_constructible"]={
      "uses_c_for_enumeration":False,
      "selected_states_found_in_c_free_families":True,
      "t":t,"n":n,"s":s,"global_symbolic_upper_bound":str(bound),
      "frozen_n_exponent_bound":14*(2**(2*s))
    }
    receipt["raw_soundness"]="PASS_RAW_SOUNDNESS_BY_LITERAL_NORMAL_SUBCASE"
    # witness-level completeness: c extends constructed tuple because fnew is its restriction.
    parts=built["parts"]; fnew=built["fnew"]
    complete=all(o["c"][v]==fnew[v] for v in set(parts["S"])|set(parts["X0"]))
    receipt["raw_completeness_witness"]="PASS_RAW_COMPLETENESS_WITNESS" if complete else "FAIL_RAW_COMPLETENESS"
    if not complete:
        receipt.update(verdict="FAIL_RAW_COMPLETENESS");return receipt
    receipt["verdict"]="RAW_EQUIVALENCE_WITNESS_PASS"
    return receipt

def fixture_A2():
    return {
      "id":"CTRL_A2_CANONICAL_SPLIT4",
      "vertices":["a","p","s1","s2","n","b"],
      "edges":[["a","p"],["p","s1"],["s1","s2"],["s2","n"],["n","b"]],
      "S":["s1","s2"],"X0":[],"X":[],"Y0":["a","b"],"Y":["p","n"],
      "f":{"s1":1,"s2":2},"c":{"s1":1,"s2":2,"p":3,"n":4,"a":1,"b":1},
      "target_pair":[["s1"],["s2"]],"expected_target_branch":"A2"
    }
def fixture_A1():
    return {
      "id":"CTRL_A1_COMMON111",
      "vertices":["p","s1","s2","n","z"],
      "edges":[["p","s1"],["s1","s2"],["s2","n"],["p","z"],["n","z"]],
      "S":["s1","s2"],"X0":[],"X":[],"Y0":["z"],"Y":["p","n"],
      "f":{"s1":1,"s2":2},"c":{"s1":1,"s2":2,"p":3,"n":4,"z":1},
      "target_pair":[["s1"],["s2"]],"expected_target_branch":"A1"
    }
def fixture_B():
    return {
      "id":"CTRL_B_001",
      "vertices":["s1","s2","n","z"],
      "edges":[["s1","s2"],["s2","n"],["n","z"]],
      "S":["s1","s2"],"X0":[],"X":[],"Y0":["z"],"Y":["n"],
      "f":{"s1":1,"s2":2},"c":{"s1":1,"s2":2,"n":3,"z":1},
      "target_pair":[["s1"],["s2"]],"expected_target_branch":"B"
    }
def fixture_C():
    return {
      "id":"CTRL_C_000",
      "vertices":["s1","s2","n","z"],
      "edges":[["s1","s2"],["s2","n"],["n","z"]],
      "S":["s1","s2"],"X0":[],"X":[],"Y0":["z"],"Y":["n"],
      "f":{"s1":1,"s2":2},"c":{"s1":1,"s2":2,"n":1,"z":3},
      "target_pair":[["s1"],["s2"]],"expected_target_branch":"C"
    }
def fixture_interaction():
    return {
      "id":"PROBE_GLOBAL_INTERACTION_3TYPE",
      "vertices":["s1","s2","s3","v","n","z"],
      "edges":[["s1","s2"],["s2","s3"],["s1","s3"],["v","s1"],["v","z"],["z","n"],["n","s3"]],
      "S":["s1","s2","s3"],"X0":[],"X":[],"Y0":["z"],"Y":["v","n"],
      "f":{"s1":1,"s2":2,"s3":3},
      "c":{"s1":1,"s2":2,"s3":3,"v":2,"n":4,"z":1}
    }

def minimize_by_vertex_deletion(o,parent,fail_code):
    # Preserve fixed roles only implicitly; for the global probe test all induced deletions.
    best=o
    changed=True
    while changed:
        changed=False
        for v in list(best["vertices"]):
            cand=json.loads(json.dumps(best))
            cand["vertices"]=[x for x in cand["vertices"] if x!=v]
            cand["edges"]=[[a,b] for a,b in cand["edges"] if a!=v and b!=v]
            for k in ["S","X0","X","Y0","Y"]:
                cand[k]=[x for x in cand[k] if x!=v]
            cand["f"].pop(v,None); cand["c"].pop(v,None)
            if not cand["S"]: continue
            r=evaluate_fixture(cand,parent)
            if r.get("verdict")==fail_code:
                best=cand; changed=True; break
    return best

def run(outdir,parent_path):
    parent=load_parent(parent_path)
    out=pathlib.Path(outdir);out.mkdir(parents=True,exist_ok=True)
    fixtures=[fixture_A2(),fixture_A1(),fixture_B(),fixture_C(),fixture_interaction()]
    rows=[]
    for o in fixtures:
        rec=evaluate_fixture(o,parent)
        if o["id"]=="PROBE_GLOBAL_INTERACTION_3TYPE" and rec.get("verdict","").startswith("FAIL_"):
            mini=minimize_by_vertex_deletion(o,parent,rec["verdict"])
            rec["minimized_induced_subgraph_witness"]=mini
            rec["vertex_minimized_under_induced_deletion"]=(len(mini["vertices"])==len(o["vertices"]))
        (out/(o["id"]+".fixture.json")).write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
        (out/(o["id"]+".receipt.json")).write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
        rows.append(rec)
    controls={r["fixture_id"]:r["verdict"] for r in rows[:4]}
    expected={
      "CTRL_A2_CANONICAL_SPLIT4":"RAW_EQUIVALENCE_WITNESS_PASS",
      "CTRL_A1_COMMON111":"RAW_EQUIVALENCE_WITNESS_PASS",
      "CTRL_B_001":"RAW_EQUIVALENCE_WITNESS_PASS",
      "CTRL_C_000":"RAW_EQUIVALENCE_WITNESS_PASS"
    }
    controls_ok=controls==expected
    probe=rows[4]
    if not controls_ok:
        scientific="FAIL_CONTROL"
    elif probe["verdict"]!="RAW_EQUIVALENCE_WITNESS_PASS":
        scientific="FAIL_RAW_REPRESENTATIVE_COVERAGE"
    else:
        scientific="FINITE_REPLAY_PASS__UNIVERSAL_AUTHORITY_NOT_ESTABLISHED"
    summary={
      "schema":"janus.trump.p7_split4.raw_coverage_execution.v1",
      "control_verdicts":controls,"controls_expected":expected,"controls_ok":controls_ok,
      "probe_verdict":probe["verdict"],
      "scientific_gate":scientific,
      "raw_equivalence_universal":False,
      "subgate_A":"OPEN",
      "lemma7_transfer":"NOT_STARTED",
      "lemma10_transfer":"NOT_STARTED",
      "break_B":"NOT_STARTED",
      "rows":rows
    }
    (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"controls_ok":controls_ok,"probe_verdict":probe["verdict"],"scientific_gate":scientific},sort_keys=True))
    # A witness-carrying falsifier is a scientifically successful run; only harness/control failure exits nonzero.
    if not controls_ok: raise SystemExit(2)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    ap.add_argument("--rigidity-parent",required=True)
    args=ap.parse_args()
    run(args.out,args.rigidity_parent)
