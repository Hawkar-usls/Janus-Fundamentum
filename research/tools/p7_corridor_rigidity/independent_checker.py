#!/usr/bin/env python3
import argparse, collections, hashlib, itertools, json, pathlib

PASS="PASS_P7_CORRIDOR_RIGIDITY"
FAIL_AXIOM="FAIL_INPUT_AXIOM"
FAIL_TYPE="FAIL_INPUT_OR_TYPE_INCONSISTENCY"
FAIL_P7="FAIL_NOT_P7_FREE"

EXPECTED={
  "POS_CANONICAL_P6_CORRIDOR":PASS,
  "NEG_ADD_Y_ZR":FAIL_AXIOM,
  "NEG_ADD_YPRIME_ZL":FAIL_AXIOM,
  "NEG_ADD_ZL_ZR":FAIL_AXIOM,
  "NEG_ONE_INTERNAL_SEED":FAIL_TYPE,
  "NEG_THREE_INTERNAL_SEED":FAIL_P7
}

def ce(a,b):
    return tuple(sorted((str(a),str(b))))

def edges(o):
    return {ce(a,b) for a,b in o["edges"]}

def nbrs(o,v):
    ee=edges(o)
    return {u for u in o["vertices"] if u!=v and ce(u,v) in ee}

def digest(o):
    return hashlib.sha256(json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def induced_order(o,seq):
    ee=edges(o)
    if len(set(seq))!=len(seq):
        return False
    for i,a in enumerate(seq):
        for j in range(i+1,len(seq)):
            if ((ce(a,seq[j]) in ee) != (j==i+1)):
                return False
    return True

def p7_witness(o):
    vs=sorted(o["vertices"])
    ee=edges(o)
    for comb in itertools.combinations(vs,7):
        ss=set(comb)
        deg={v:sum(ce(v,u) in ee for u in ss if u!=v) for v in ss}
        if sum(deg.values())//2!=6 or sorted(deg.values())!=[1,1,2,2,2,2,2]:
            continue
        st=comb[0]
        seen={st}
        q=collections.deque([st])
        while q:
            v=q.popleft()
            for u in ss:
                if u not in seen and ce(v,u) in ee:
                    seen.add(u)
                    q.append(u)
        if seen!=ss:
            continue
        cur=sorted(v for v,d in deg.items() if d==1)[0]
        prev=None
        order=[]
        while True:
            order.append(cur)
            nxt=sorted(u for u in ss if u!=prev and ce(cur,u) in ee)
            if not nxt:
                break
            if len(nxt)>1:
                order=[]
                break
            prev,cur=cur,nxt[0]
        if len(order)==7 and induced_order(o,order):
            return order
    return None

def expected_fixture(kind):
    pos={
      "id":"POS_CANONICAL_P6_CORRIDOR",
      "vertices":["zL","y","s","s_prime","y_prime","zR"],
      "edges":[["zL","y"],["y","s"],["s","s_prime"],["s_prime","y_prime"],["y_prime","zR"]],
      "S":["s","s_prime"],"X0":[],"X":["y","y_prime"],"Y0":["zL","zR"],"Y":[],
      "f":{"s":1,"s_prime":2},
      "roles":{"y":"y","y_prime":"y_prime","zL":"zL","zR":"zR"}
    }
    if kind=="POS_CANONICAL_P6_CORRIDOR":
        return pos
    if kind in {"NEG_ADD_Y_ZR","NEG_ADD_YPRIME_ZL","NEG_ADD_ZL_ZR"}:
        o=json.loads(json.dumps(pos))
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

def independently_expected(o):
    kind=o["id"]
    if o!=expected_fixture(kind):
        return "FAIL_FIXTURE_TAMPER",None
    if kind=="POS_CANONICAL_P6_CORRIDOR":
        order=["zL","y","s","s_prime","y_prime","zR"]
        return (PASS,order) if induced_order(o,order) and p7_witness(o) is None else ("FAIL_INDEPENDENT_POSITIVE",None)
    if kind in {"NEG_ADD_Y_ZR","NEG_ADD_YPRIME_ZL","NEG_ADD_ZL_ZR"}:
        return FAIL_AXIOM,None
    if kind=="NEG_ONE_INTERNAL_SEED":
        T=nbrs(o,"y")&set(o["S"])
        Tp=nbrs(o,"y_prime")&set(o["S"])
        f=o["f"]
        return (FAIL_TYPE,None) if {f[v] for v in T}=={f[v] for v in Tp} else ("FAIL_INDEPENDENT_ONE_INTERNAL",None)
    if kind=="NEG_THREE_INTERNAL_SEED":
        w=p7_witness(o)
        return (FAIL_P7,w) if w else ("FAIL_INDEPENDENT_P7_CONTROL",None)
    raise KeyError(kind)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("suite_dir")
    ap.add_argument("kernel_receipt")
    ap.add_argument("output")
    args=ap.parse_args()

    root=pathlib.Path(args.suite_dir)
    kernel=json.loads(pathlib.Path(args.kernel_receipt).read_text())
    checks={
      "kernel_replay_mode":kernel.get("mode")=="KERNEL_REPLAY",
      "kernel_replay_pass":kernel.get("verdict")=="THEOREM_KERNEL_REPLAY_PASS",
      "formal_not_claimed":kernel.get("formal_theorem_pass") is False
    }

    rows=[]
    for fid,expected in EXPECTED.items():
        o=json.loads((root/f"{fid}.fixture.json").read_text())
        rec=json.loads((root/f"{fid}.receipt.json").read_text())
        independently,w=independently_expected(o)
        row={
          "fixture_id":fid,
          "fixture_digest":digest(o),
          "preregistered_expected":expected,
          "candidate_verdict":rec.get("verdict"),
          "independent_verdict":independently,
          "candidate_matches_expected":rec.get("verdict")==expected,
          "independent_matches_expected":independently==expected,
          "graph_digest_bound":rec.get("graph_digest")==digest(o)
        }

        if fid=="POS_CANONICAL_P6_CORRIDOR":
            cc=rec.get("corridor_certificate",{})
            order=cc.get("order")
            row.update({
              "candidate_order":order,
              "independent_induced_P6":order==w and induced_order(o,order or []),
              "all_15_present":len(cc.get("all_15_pairs",[]))==15,
              "five_edges":cc.get("five_edges_verified") is True,
              "ten_nonedges":cc.get("ten_nonedges_verified") is True,
              "p7_free_independent":p7_witness(o) is None
            })

        if fid=="NEG_THREE_INTERNAL_SEED":
            candidate=(rec.get("p7_recognition") or {}).get("witness")
            row.update({
              "induced_P7_witness":w,
              "candidate_P7_witness":candidate,
              "p7_witness_matches":candidate in (w,list(reversed(w)) if w else None)
            })
        rows.append(row)

    all_rows=all(r["candidate_matches_expected"] and r["independent_matches_expected"] and r["graph_digest_bound"] for r in rows)
    positive=next(r for r in rows if r["fixture_id"]=="POS_CANONICAL_P6_CORRIDOR")
    p7row=next(r for r in rows if r["fixture_id"]=="NEG_THREE_INTERNAL_SEED")
    checks.update({
      "all_controls_match":all_rows,
      "positive_15_pair_certificate":all(positive.get(k) for k in ["independent_induced_P6","all_15_present","five_edges","ten_nonedges","p7_free_independent"]),
      "negative_p7_witness_replayed":p7row.get("p7_witness_matches") is True
    })

    verdict="INDEPENDENT_REPLAY_PASS" if all(checks.values()) else "INDEPENDENT_REPLAY_FAIL"
    out={
      "schema":"janus.trump.p7_corridor_rigidity.independent_replay.v1",
      "verdict":verdict,
      "checks":checks,
      "rows":rows
    }
    pathlib.Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
    if verdict!="INDEPENDENT_REPLAY_PASS":
        raise SystemExit(1)

if __name__=="__main__":
    main()
