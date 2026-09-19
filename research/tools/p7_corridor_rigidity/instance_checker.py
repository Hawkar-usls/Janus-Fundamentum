#!/usr/bin/env python3
import argparse, collections, hashlib, itertools, json, pathlib

PASS="PASS_P7_CORRIDOR_RIGIDITY"
FAIL_AXIOM="FAIL_INPUT_AXIOM"
FAIL_TYPE="FAIL_INPUT_OR_TYPE_INCONSISTENCY"
FAIL_P7="FAIL_NOT_P7_FREE"
FAIL_SHORTEST="FAIL_SHORTEST_PATH_CERTIFICATE"
FAIL_INDUCED="FAIL_CORRIDOR_NOT_INDUCED"
FAIL_RIGIDITY="FAIL_RIGIDITY"

def canon_edge(a,b):
    return tuple(sorted((str(a),str(b))))

def edge_set(obj):
    return {canon_edge(a,b) for a,b in obj["edges"]}

def adj(obj,v):
    E=edge_set(obj)
    return {u for u in obj["vertices"] if u!=v and canon_edge(u,v) in E}

def connected_subset(obj, subset):
    subset=set(subset)
    if not subset:
        return False
    seen=set()
    q=collections.deque([next(iter(subset))])
    while q:
        v=q.popleft()
        if v in seen:
            continue
        seen.add(v)
        for u in adj(obj,v)&subset:
            if u not in seen:
                q.append(u)
    return seen==subset

def induced_path_order(obj, seq):
    E=edge_set(obj)
    seq=list(seq)
    if len(set(seq))!=len(seq):
        return False, {"reason":"repeated_vertex"}
    bad=[]
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            b=seq[j]
            has=canon_edge(a,b) in E
            want=(j==i+1)
            if has!=want:
                bad.append({"pair":[a,b],"expected":"edge" if want else "nonedge","observed":"edge" if has else "nonedge"})
    return (not bad), {"violations":bad}

def p7_witness(obj):
    V=sorted(obj["vertices"])
    E=edge_set(obj)
    if len(V)<7:
        return None
    for comb in itertools.combinations(V,7):
        sub=set(comb)
        deg={v:sum(canon_edge(v,u) in E for u in sub if u!=v) for v in sub}
        if sum(deg.values())//2!=6 or sorted(deg.values())!=[1,1,2,2,2,2,2]:
            continue
        start=comb[0]
        seen={start}
        q=collections.deque([start])
        while q:
            v=q.popleft()
            for u in sub:
                if u not in seen and canon_edge(v,u) in E:
                    seen.add(u)
                    q.append(u)
        if seen!=sub:
            continue
        ends=sorted([v for v,d in deg.items() if d==1])
        cur=ends[0]
        prev=None
        order=[]
        while True:
            order.append(cur)
            nxt=sorted([u for u in sub if canon_edge(cur,u) in E and u!=prev])
            if not nxt:
                break
            if len(nxt)>1:
                order=[]
                break
            prev,cur=cur,nxt[0]
        if len(order)==7:
            ok,_=induced_path_order(obj,order)
            if ok:
                return order
    return None

def shortest_seed_path(obj,y,yp,S):
    allowed=set(S)|{y,yp}
    E=edge_set(obj)
    q=collections.deque([y])
    parent={y:None}
    while q:
        v=q.popleft()
        if v==yp:
            break
        for u in sorted(allowed):
            if u not in parent and canon_edge(v,u) in E:
                parent[u]=v
                q.append(u)
    if yp not in parent:
        return None
    path=[]
    v=yp
    while v is not None:
        path.append(v)
        v=parent[v]
    return list(reversed(path))

def digest_obj(obj):
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def basic_seeded_checks(obj):
    V=set(obj["vertices"])
    groups=[set(obj[k]) for k in ["S","X0","X","Y0","Y"]]
    union=set().union(*groups)
    if union!=V:
        return False,"partition_does_not_cover_vertices"
    if sum(len(g) for g in groups)!=len(union):
        return False,"partition_not_disjoint"
    f=obj["f"]
    domain=set(f)
    if domain != set(obj["S"])|set(obj["X0"]):
        return False,"f_domain_mismatch"
    E=edge_set(obj)
    for a,b in E:
        if a in domain and b in domain and f[a]==f[b]:
            return False,"f_not_proper"
    return True,None

def check_instance(obj):
    receipt={"schema":"janus.trump.p7_corridor_rigidity.instance.v1","fixture_id":obj["id"],"graph_digest":digest_obj(obj)}
    ok,why=basic_seeded_checks(obj)
    if not ok:
        receipt.update(verdict=FAIL_AXIOM,detail=why)
        return receipt

    S=set(obj["S"])
    X0=set(obj["X0"])
    Y0=set(obj["Y0"])
    V=set(obj["vertices"])
    E=edge_set(obj)
    f=obj["f"]
    R=obj["roles"]
    y,yp,zL,zR=R["y"],R["y_prime"],R["zL"],R["zR"]

    if len({y,yp,zL,zR})<4:
        receipt.update(verdict=FAIL_AXIOM,detail="roles_not_distinct")
        return receipt

    # Recompute T,T' before axiom (ii), so the preregistered one-internal-vertex
    # control is classified as an input/type inconsistency rather than theorem failure.
    T=adj(obj,y)&S
    Tp=adj(obj,yp)&S
    fT={f[v] for v in T}
    fTp={f[v] for v in Tp}
    receipt["T_recomputed"]=sorted(T)
    receipt["T_prime_recomputed"]=sorted(Tp)
    receipt["fT"]=sorted(fT)
    receipt["fT_prime"]=sorted(fTp)

    if len(fT)!=1 or len(fTp)!=1 or fT==fTp:
        receipt.update(verdict=FAIL_TYPE,detail="singleton_type_color_condition_failed")
        return receipt
    if T&Tp:
        receipt.update(verdict=FAIL_TYPE,detail="T_intersection_T_prime_nonempty",intersection=sorted(T&Tp))
        return receipt

    # Paper-II axiom (ii).
    if not connected_subset(obj,S):
        receipt.update(verdict=FAIL_AXIOM,detail="axiom_ii_seed_not_connected")
        return receipt
    for v in sorted(V-S):
        if S and S <= adj(obj,v):
            receipt.update(verdict=FAIL_AXIOM,detail="axiom_ii_outside_vertex_complete_to_seed",witness=v)
            return receipt

    # Paper-II axiom (iii): Y0 = V(G) \ (N(S) union X0 union S).
    NS=set().union(*(adj(obj,s) for s in S)) - S if S else set()
    expected_Y0=V-(NS|X0|S)
    if Y0!=expected_Y0:
        receipt.update(verdict=FAIL_AXIOM,detail="axiom_iii_Y0_mismatch",expected_Y0=sorted(expected_Y0),observed_Y0=sorted(Y0))
        return receipt

    NY0=set().union(*(adj(obj,z) for z in Y0))-Y0 if Y0 else set()
    if y not in NY0 or yp not in NY0 or y in S|X0 or yp in S|X0:
        receipt.update(verdict=FAIL_AXIOM,detail="y_typing_or_NY0_condition_failed")
        return receipt
    if zL not in Y0 or zR not in Y0:
        receipt.update(verdict=FAIL_AXIOM,detail="attachment_not_in_Y0")
        return receipt

    for a,b,label in [(zL,y,"zL-y"),(yp,zR,"yprime-zR")]:
        if canon_edge(a,b) not in E:
            receipt.update(verdict=FAIL_AXIOM,detail="required_edge_missing",witness=label)
            return receipt

    for a,b,label in [(y,yp,"y-yprime"),(zL,zR,"zL-zR"),(y,zR,"y-zR"),(yp,zL,"yprime-zL")]:
        if canon_edge(a,b) in E:
            receipt.update(verdict=FAIL_AXIOM,detail="required_nonedge_violated",witness=label)
            return receipt

    # P7-freeness is not a trusted promise.
    p7=p7_witness(obj)
    receipt["p7_recognition"]={
      "method":"exhaustive_constant_size_7_vertex_induced_subgraph_search",
      "result":"NOT_P7_FREE" if p7 else "P7_FREE",
      "witness":p7
    }
    if p7:
        receipt.update(verdict=FAIL_P7,detail="explicit_induced_P7_found")
        return receipt

    Q=shortest_seed_path(obj,y,yp,S)
    if not Q:
        receipt.update(verdict=FAIL_SHORTEST,detail="no_seed_internal_y_yprime_path")
        return receipt
    if Q[0]!=y or Q[-1]!=yp or any(v not in S for v in Q[1:-1]):
        receipt.update(verdict=FAIL_SHORTEST,detail="path_endpoint_or_interior_error",shortest_path=Q)
        return receipt

    qok,qdetail=induced_path_order(obj,Q)
    if not qok:
        receipt.update(verdict=FAIL_SHORTEST,detail="BFS_shortest_path_not_induced_unexpected",shortest_path=Q,path_check=qdetail)
        return receipt
    receipt["shortest_seed_path"]=Q
    receipt["Q_star_size"]=len(Q)-2

    corridor=[zL]+Q+[zR]
    cok,cdetail=induced_path_order(obj,corridor)
    receipt["corridor_candidate"]=corridor
    if not cok:
        receipt.update(verdict=FAIL_INDUCED,detail="corridor_has_chord_or_missing_path_edge",corridor_check=cdetail)
        return receipt

    if len(Q)-2 != 2:
        receipt.update(verdict=FAIL_RIGIDITY,detail="valid_P7_free_input_but_Q_star_size_not_2",decorated_counterexample=obj)
        return receipt

    pairs=[]
    for i,a in enumerate(corridor):
        for j in range(i+1,len(corridor)):
            b=corridor[j]
            pairs.append({"pair":[a,b],"relation":"edge" if canon_edge(a,b) in E else "nonedge","consecutive":j==i+1})
    edges=[p["pair"] for p in pairs if p["relation"]=="edge"]
    nonedges=[p["pair"] for p in pairs if p["relation"]=="nonedge"]
    receipt["corridor_certificate"]={
      "order":corridor,
      "all_15_pairs":pairs,
      "five_edges_verified":len(edges)==5,
      "ten_nonedges_verified":len(nonedges)==10,
      "induced_P6_verified":True
    }
    receipt.update(verdict=PASS)
    return receipt

def make_fixture(kind):
    if kind=="POS_CANONICAL_P6_CORRIDOR":
        return {
          "id":kind,
          "vertices":["zL","y","s","s_prime","y_prime","zR"],
          "edges":[["zL","y"],["y","s"],["s","s_prime"],["s_prime","y_prime"],["y_prime","zR"]],
          "S":["s","s_prime"],"X0":[],"X":["y","y_prime"],"Y0":["zL","zR"],"Y":[],
          "f":{"s":1,"s_prime":2},
          "roles":{"y":"y","y_prime":"y_prime","zL":"zL","zR":"zR"}
        }
    if kind in {"NEG_ADD_Y_ZR","NEG_ADD_YPRIME_ZL","NEG_ADD_ZL_ZR"}:
        o=json.loads(json.dumps(make_fixture("POS_CANONICAL_P6_CORRIDOR")))
        o["id"]=kind
        o["edges"].append({
          "NEG_ADD_Y_ZR":["y","zR"],
          "NEG_ADD_YPRIME_ZL":["y_prime","zL"],
          "NEG_ADD_ZL_ZR":["zL","zR"]
        }[kind])
        return o
    if kind=="NEG_ONE_INTERNAL_SEED":
        return {
          "id":kind,
          "vertices":["zL","y","s","y_prime","zR"],
          "edges":[["zL","y"],["y","s"],["s","y_prime"],["y_prime","zR"]],
          "S":["s"],"X0":[],"X":["y","y_prime"],"Y0":["zL","zR"],"Y":[],
          "f":{"s":1},
          "roles":{"y":"y","y_prime":"y_prime","zL":"zL","zR":"zR"}
        }
    if kind=="NEG_THREE_INTERNAL_SEED":
        return {
          "id":kind,
          "vertices":["zL","y","s1","s2","s3","y_prime","zR"],
          "edges":[["zL","y"],["y","s1"],["s1","s2"],["s2","s3"],["s3","y_prime"],["y_prime","zR"]],
          "S":["s1","s2","s3"],"X0":[],"X":["y","y_prime"],"Y0":["zL","zR"],"Y":[],
          "f":{"s1":1,"s2":3,"s3":2},
          "roles":{"y":"y","y_prime":"y_prime","zL":"zL","zR":"zR"}
        }
    raise KeyError(kind)

EXPECTED={
 "POS_CANONICAL_P6_CORRIDOR":PASS,
 "NEG_ADD_Y_ZR":FAIL_AXIOM,
 "NEG_ADD_YPRIME_ZL":FAIL_AXIOM,
 "NEG_ADD_ZL_ZR":FAIL_AXIOM,
 "NEG_ONE_INTERNAL_SEED":FAIL_TYPE,
 "NEG_THREE_INTERNAL_SEED":FAIL_P7
}

def run_suite(outdir):
    outdir=pathlib.Path(outdir)
    outdir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for fid,expected in EXPECTED.items():
        obj=make_fixture(fid)
        fp=outdir/f"{fid}.fixture.json"
        rp=outdir/f"{fid}.receipt.json"
        fp.write_text(json.dumps(obj,indent=2,sort_keys=True)+"\n")
        rec=check_instance(obj)
        rec["preregistered_expected_verdict"]=expected
        rec["matches_preregistered_expectation"]=(rec["verdict"]==expected)
        rp.write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
        rows.append(rec)
    summary={
      "schema":"janus.trump.p7_corridor_rigidity.suite.v1",
      "rows":rows,
      "all_controls_match":all(r["matches_preregistered_expectation"] for r in rows)
    }
    (outdir/"suite_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
    print(json.dumps(summary,sort_keys=True))
    if not summary["all_controls_match"]:
        raise SystemExit(1)

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--run-suite",metavar="OUTDIR")
    ap.add_argument("--check",metavar="JSON")
    args=ap.parse_args()
    if args.run_suite:
        run_suite(args.run_suite)
    elif args.check:
        obj=json.loads(pathlib.Path(args.check).read_text())
        print(json.dumps(check_instance(obj),sort_keys=True))
    else:
        ap.error("choose --run-suite or --check")
