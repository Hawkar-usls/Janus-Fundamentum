#!/usr/bin/env python3
"""Independent Stage6A q-Horn certificate checker and polynomial terminal replay.

This module never imports or calls the external proposer. Positive authority is
obtained only by replaying the integer q-Horn certificate against the frozen CNF
and then executing the published Horn-minimum-model -> residual 2-SAT route.

Negative authority is proof-carrying: on an external UNSAT proposal result, the
checker deterministically constructs the Boros quadratic cover F2, finds a
violating triple if one exists, emits six directed paths, and replays every edge
of those paths before issuing CERTIFIED_NOT_QHORN. External UNSAT alone is never
scientific authority.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, time
from pathlib import Path

PRIMARY={2,9,10,11,12,13,14}
CONTROLS={1,3,4,5,6,7}
ALLOWED=PRIMARY|CONTROLS


def sha_bytes(b:bytes)->str:
    return hashlib.sha256(b).hexdigest()


def file_sha256(p:Path)->str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for ch in iter(lambda:f.read(1<<20),b""):
            h.update(ch)
    return h.hexdigest()


def formula_sequence_bytes(clauses):
    return json.dumps(clauses,ensure_ascii=False,separators=(",",":")).encode("utf-8")


def formula_sequence_sha256(clauses):
    return sha_bytes(formula_sequence_bytes(clauses))


def cert_size(obj):
    return len((json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode())


def lit_value(lit:int, model:dict[int,bool])->bool:
    val=model[abs(lit)]
    return val if lit>0 else not val


def verify_original_model(clauses,model):
    failed=[]
    for ci,c in enumerate(clauses):
        if not any(lit_value(l,model) for l in c):
            failed.append(ci)
    return failed


def verify_weights(clauses, cert):
    vars_=sorted({abs(l) for c in clauses for l in c})
    expected={str(v) for v in vars_}|{str(-v) for v in vars_}
    if not isinstance(cert,dict) or set(cert)!=expected:
        return False,{"reason":"LITERAL_KEY_SET_MISMATCH",
                     "missing":sorted(expected-set(cert) if isinstance(cert,dict) else expected),
                     "extra":sorted(set(cert)-expected) if isinstance(cert,dict) else []}
    w={}
    for k,v in cert.items():
        if isinstance(v,bool) or not isinstance(v,int) or v not in (0,1,2):
            return False,{"reason":"WEIGHT_DOMAIN_FAIL","literal":k,"value":v}
        w[int(k)]=v
    for v in vars_:
        if w[v]+w[-v]!=2:
            return False,{"reason":"COMPLEMENT_SUM_FAIL","variable":v,
                          "positive":w[v],"negative":w[-v]}
    for ci,c in enumerate(clauses):
        total=sum(w[l] for l in c)
        if total>2:
            return False,{"reason":"CLAUSE_WEIGHT_SUM_FAIL",
                          "clause_index":ci,"sum":total,"clause":c}
    return True,{"weights":w,"variables":vars_}


def horn_minimum_model(horn_clauses, hvars):
    true=set()
    deriv=[]
    changed=True
    while changed:
        changed=False
        for hc in horn_clauses:
            lits=hc["literals"]
            pos=[l for l in lits if l>0]
            neg=[-l for l in lits if l<0]
            if len(pos)>1:
                raise AssertionError(("NOT_HORN_AFTER_VERIFIED_QHORN",hc))
            if pos and pos[0] in neg:
                continue
            if all(v in true for v in neg):
                if not pos:
                    return {
                      "status":"UNSAT",
                      "true_variables":sorted(true),
                      "derivation":deriv,
                      "contradiction":{
                        "original_clause_index":hc["original_clause_index"],
                        "antecedents":neg,
                        "literals":lits
                      }
                    }
                head=pos[0]
                if head not in true:
                    true.add(head)
                    changed=True
                    deriv.append({
                      "derived_true":head,
                      "original_clause_index":hc["original_clause_index"],
                      "antecedents":neg
                    })
    return {
      "status":"SAT",
      "true_variables":sorted(true),
      "false_variables":sorted(set(hvars)-true),
      "derivation":deriv
    }


def implication_from_2sat(residual):
    adj=collections.defaultdict(set)
    edge_sources=collections.defaultdict(list)
    vars_=set()

    def add(a,b,src):
        adj[a].add(b)
        adj[b]
        edge_sources[(a,b)].append(src)

    for rc in residual:
        c=rc["q_literals"]
        src=rc["original_clause_index"]
        for l in c:
            vars_.add(abs(l))
            adj[l]
            adj[-l]
        if len(c)==0:
            return None,None,None,{"empty_clause_from_original":src}
        if len(c)==1:
            a=c[0]
            add(-a,a,src)
        elif len(c)==2:
            a,b=c
            add(-a,b,src)
            add(-b,a,src)
        else:
            raise AssertionError(("RESIDUAL_NOT_2SAT",rc))
    for v in vars_:
        adj[v]
        adj[-v]
    return adj,edge_sources,vars_,None


def kosaraju_int(adj):
    nodes=sorted(adj)
    seen=set()
    order=[]

    def dfs(u):
        seen.add(u)
        for v in sorted(adj[u]):
            if v not in seen:
                dfs(v)
        order.append(u)

    for u in nodes:
        if u not in seen:
            dfs(u)

    radj={u:set() for u in nodes}
    for u in nodes:
        for v in adj[u]:
            radj.setdefault(v,set()).add(u)
            radj.setdefault(u,set())

    comp={}
    cid=0

    def rdfs(u):
        comp[u]=cid
        for v in sorted(radj[u]):
            if v not in comp:
                rdfs(v)

    for u in reversed(order):
        if u not in comp:
            rdfs(u)
            cid+=1
    return comp


def bfs_path(adj,start,goal):
    q=collections.deque([start])
    prev={start:None}
    while q:
        u=q.popleft()
        if u==goal:
            break
        for v in sorted(adj[u],key=str):
            if v not in prev:
                prev[v]=u
                q.append(v)
    if goal not in prev:
        return None
    out=[]
    x=goal
    while x is not None:
        out.append(x)
        x=prev[x]
    return list(reversed(out))


def solve_2sat(residual):
    adj,edge_sources,vars_,empty=implication_from_2sat(residual)
    if empty is not None:
        return {"status":"UNSAT","reason":"EMPTY_RESIDUAL_CLAUSE","evidence":empty}

    comp=kosaraju_int(adj)
    for v in sorted(vars_):
        if comp[v]==comp[-v]:
            p1=bfs_path(adj,v,-v)
            p2=bfs_path(adj,-v,v)
            return {
              "status":"UNSAT",
              "reason":"SCC_COMPLEMENT_CONTRADICTION",
              "variable":v,
              "path_v_to_not_v":p1,
              "path_not_v_to_v":p2,
              "path_edge_sources":{
                "v_to_not_v":[edge_sources[(a,b)] for a,b in zip(p1,p1[1:])],
                "not_v_to_v":[edge_sources[(a,b)] for a,b in zip(p2,p2[1:])]
              }
            }

    assignment={v:(comp[v]>comp[-v]) for v in sorted(vars_)}
    bad=[]
    for rc in residual:
        if not any((assignment[abs(l)] if l>0 else not assignment[abs(l)])
                   for l in rc["q_literals"]):
            bad.append(rc["original_clause_index"])
    if bad:
        return {
          "status":"INTERNAL_ERROR",
          "reason":"2SAT_MODEL_REPLAY_FAIL",
          "failed_original_clauses":bad
        }
    return {
      "status":"SAT",
      "assignment":{str(k):v for k,v in assignment.items()}
    }


def qhorn_terminal(clauses,w):
    vars_=sorted({abs(l) for c in clauses for l in c})
    qvars={v for v in vars_ if w[v]==1 and w[-v]==1}
    hvars=set(vars_)-qvars
    pos_lit={v:(v if w[v]==2 else -v) for v in hvars}

    horn=[]
    mixed=[]
    for ci,c in enumerate(clauses):
        q=[l for l in c if abs(l) in qvars]
        h=[l for l in c if abs(l) in hvars]
        if len(q)==0:
            hl=[]
            for l in h:
                v=abs(l)
                hl.append(v if l==pos_lit[v] else -v)
            horn.append({"original_clause_index":ci,"literals":hl})
        else:
            if len(q)>2:
                raise AssertionError(("QHORN_Q_WIDTH_GT2",ci,c))
            for l in h:
                if l==pos_lit[abs(l)]:
                    raise AssertionError(("MIXED_POSITIVE_H_LITERAL",ci,l))
            mixed.append({
              "original_clause_index":ci,
              "q_literals":q,
              "h_literals":h
            })

    hs=horn_minimum_model(horn,hvars)
    decomposition={
      "q_variables":sorted(qvars),
      "h_variables":sorted(hvars),
      "positive_h_literal":{str(v):pos_lit[v] for v in sorted(hvars)},
      "horn_clause_count":len(horn),
      "mixed_clause_count":len(mixed)
    }

    if hs["status"]=="UNSAT":
        return {
          "terminal_status":"UNSAT",
          "terminal_stage":"HORNSAT",
          "decomposition":decomposition,
          "horn_terminal":hs,
          "terminal_replay_verified":True
        }

    htrue=set(hs["true_variables"])
    residual=[]
    satisfied_by_h=[]
    for mc in mixed:
        sat_h=any(abs(l) not in htrue for l in mc["h_literals"])
        if sat_h:
            satisfied_by_h.append(mc["original_clause_index"])
        else:
            residual.append({
              "original_clause_index":mc["original_clause_index"],
              "q_literals":list(mc["q_literals"])
            })

    ts=solve_2sat(residual)
    if ts["status"]=="INTERNAL_ERROR":
        return {
          "terminal_status":"INFRASTRUCTURE_ERROR",
          "terminal_stage":"2SAT",
          "decomposition":decomposition,
          "horn_terminal":hs,
          "two_sat_terminal":ts,
          "terminal_replay_verified":False
        }

    if ts["status"]=="UNSAT":
        return {
          "terminal_status":"UNSAT",
          "terminal_stage":"2SAT",
          "decomposition":decomposition,
          "horn_terminal":hs,
          "satisfied_mixed_clauses_by_h":satisfied_by_h,
          "residual_2sat":residual,
          "two_sat_terminal":ts,
          "terminal_replay_verified":True
        }

    qassign={int(k):v for k,v in ts["assignment"].items()}
    model={}
    for v in sorted(hvars):
        hv=v in htrue
        model[v]=hv if pos_lit[v]==v else (not hv)
    model.update(qassign)
    failed=verify_original_model(clauses,model)

    return {
      "terminal_status":"SAT" if not failed else "INFRASTRUCTURE_ERROR",
      "terminal_stage":"MODEL_REPLAY",
      "decomposition":decomposition,
      "horn_terminal":hs,
      "satisfied_mixed_clauses_by_h":satisfied_by_h,
      "residual_2sat":residual,
      "two_sat_terminal":ts,
      "complete_boolean_model":{str(k):v for k,v in sorted(model.items())},
      "original_clause_replay_failed":failed,
      "terminal_replay_verified":not failed
    }


def onode(l:int)->str:
    return f"x:{l:+d}"


def ynode(ci:int,i:int,positive=True)->str:
    return f"y:{ci}:{i}:{'+' if positive else '-'}"


def comp_node(n:str)->str:
    if n.startswith("x:"):
        return onode(-int(n[2:]))
    p=n.split(":")
    return f"y:{p[1]}:{p[2]}:{'-' if p[3]=='+' else '+'}"


def quadratic_cover(clauses):
    pairs=[]
    for ci,c0 in enumerate(clauses):
        c=[lit for _,lit in sorted(enumerate(c0),
                                   key=lambda z:(abs(z[1]),z[0]))]
        r=len(c)
        for j in range(1,r):
            y=ynode(ci,j,True)
            ny=comp_node(y)
            pairs.append((onode(c[j-1]),y,
                          {"clause":ci,"kind":"LI_Y","i":j}))
            pairs.append((ny,onode(c[j]),
                          {"clause":ci,"kind":"NY_LNEXT","i":j}))
        for j in range(1,r-1):
            pairs.append((ynode(ci,j,False),ynode(ci,j+1,True),
                          {"clause":ci,"kind":"NY_YNEXT","i":j}))

    adj=collections.defaultdict(set)
    src=collections.defaultdict(list)

    def add(u,v,s):
        adj[u].add(v)
        adj[v]
        src[(u,v)].append(s)

    for a,b,s in pairs:
        add(comp_node(a),b,s)
        add(comp_node(b),a,s)
        adj[comp_node(a)]
        adj[comp_node(b)]
    return adj,src,pairs


def kosaraju_generic(adj):
    nodes=sorted(adj)
    seen=set()
    order=[]

    def dfs(u):
        seen.add(u)
        for v in sorted(adj[u]):
            if v not in seen:
                dfs(v)
        order.append(u)

    for u in nodes:
        if u not in seen:
            dfs(u)

    radj={u:set() for u in nodes}
    for u in nodes:
        for v in adj[u]:
            radj.setdefault(v,set()).add(u)
            radj.setdefault(u,set())

    comp={}
    cid=0

    def rdfs(u):
        comp[u]=cid
        for v in sorted(radj[u]):
            if v not in comp:
                rdfs(v)

    for u in reversed(order):
        if u not in comp:
            rdfs(u)
            cid+=1
    return comp


def build_obstruction(clauses):
    adj,src,pairs=quadratic_cover(clauses)
    comp=kosaraju_generic(adj)
    for ci,c in enumerate(clauses):
        bad=[]
        for lit in c:
            a=onode(lit)
            b=onode(-lit)
            if a in comp and b in comp and comp[a]==comp[b]:
                bad.append(lit)
        if len(bad)>=3:
            triple=bad[:3]
            paths=[]
            for lit in triple:
                a=onode(lit)
                b=onode(-lit)
                paths.append({
                  "literal":lit,
                  "lit_to_complement":bfs_path(adj,a,b),
                  "complement_to_lit":bfs_path(adj,b,a)
                })
            return {
              "original_clause_index":ci,
              "original_clause":c,
              "triple":triple,
              "paths":paths,
              "quadratic_cover":{
                "binary_clause_count":len(pairs),
                "node_count":len(adj),
                "arc_count":sum(len(v) for v in adj.values())
              }
            }
    return None


def verify_obstruction(clauses,cert):
    if not isinstance(cert,dict):
        return False,{"reason":"MISSING_OBSTRUCTION"}
    ci=cert.get("original_clause_index")
    if not isinstance(ci,int) or not (0<=ci<len(clauses)):
        return False,{"reason":"BAD_CLAUSE_INDEX"}

    triple=cert.get("triple")
    if not isinstance(triple,list) or len(triple)!=3:
        return False,{"reason":"BAD_TRIPLE"}

    clause=clauses[ci]
    rem=list(clause)
    for l in triple:
        if l not in rem:
            return False,{
              "reason":"TRIPLE_LITERAL_NOT_IN_ORIGINAL_CLAUSE",
              "literal":l
            }
        rem.remove(l)

    adj,src,pairs=quadratic_cover(clauses)
    pm={p.get("literal"):p for p in cert.get("paths",[])
        if isinstance(p,dict)}

    for lit in triple:
        p=pm.get(lit)
        if not p:
            return False,{"reason":"MISSING_PATH_PAIR","literal":lit}
        for key,start,goal in [
            ("lit_to_complement",onode(lit),onode(-lit)),
            ("complement_to_lit",onode(-lit),onode(lit))
        ]:
            path=p.get(key)
            if (not isinstance(path,list) or not path or
                    path[0]!=start or path[-1]!=goal):
                return False,{
                  "reason":"PATH_ENDPOINT_FAIL",
                  "literal":lit,
                  "path_key":key,
                  "path":path
                }
            for a,b in zip(path,path[1:]):
                if b not in adj.get(a,set()):
                    return False,{
                      "reason":"PATH_EDGE_FAIL",
                      "literal":lit,
                      "path_key":key,
                      "edge":[a,b]
                    }

    return True,{
      "quadratic_cover_binary_clauses":len(pairs),
      "quadratic_cover_nodes":len(adj),
      "quadratic_cover_arcs":sum(len(v) for v in adj.values())
    }


def load_source_metadata(path):
    if path is None or not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {
          "metadata_parse_error":True,
          "metadata_file_sha256":file_sha256(path)
        }


def check_row(row,index,proposal,source_binding):
    t0=time.perf_counter()
    clauses=row["residual_formula"]
    rawsha=formula_sequence_sha256(clauses)

    base={
      "index":index,
      "role":"PRIMARY_S7" if index in PRIMARY else "CONTROL",
      "family":row.get("family"),
      "source_residual_hash":row.get("residual_hash"),
      "raw_cnf_sha256":rawsha,
      "normalization_applied":False,
      "normalized_cnf_sha256":None,
      "source_binding":source_binding
    }

    if (proposal.get("index")!=index or
        proposal.get("source_residual_hash")!=row.get("residual_hash") or
        proposal.get("raw_cnf_sha256")!=rawsha):
        base.update({
          "verdict":"FAIL_CERTIFICATE",
          "failure":{"reason":"PROPOSAL_SOURCE_BINDING_MISMATCH"}
        })
        return base

    status=proposal.get("solver_status")

    if status=="SAT":
        weights=(proposal.get("certificate") or {}).get("weights")
        ok,detail=verify_weights(clauses,weights)
        if not ok:
            base.update({
              "verdict":"FAIL_CERTIFICATE",
              "qhorn_certificate_verified":False,
              "failure":detail
            })
            return base

        w=detail["weights"]
        terminal=qhorn_terminal(clauses,w)
        proof={"weights":weights,"terminal":terminal}

        if terminal.get("terminal_replay_verified"):
            base.update({
              "verdict":"PASS_DIRECT_QHORN_POLYNOMIAL_TERMINAL",
              "direct_qhorn_membership":"VERIFIED",
              "qhorn_certificate_verified":True,
              "polynomial_qhorn_terminal_replay":"VERIFIED",
              "terminal_status":terminal["terminal_status"],
              "proof":proof,
              "certificate_bytes":cert_size(proof)
            })
        else:
            base.update({
              "verdict":"INFRASTRUCTURE_ERROR",
              "direct_qhorn_membership":"VERIFIED",
              "qhorn_certificate_verified":True,
              "polynomial_qhorn_terminal_replay":"NOT_VERIFIED",
              "proof":proof,
              "certificate_bytes":cert_size(proof)
            })

    elif status=="UNSAT":
        obstruction=build_obstruction(clauses)
        ok,detail=(verify_obstruction(clauses,obstruction)
                   if obstruction is not None
                   else (False,{"reason":"NO_VIOLATING_TRIPLE_FOUND"}))
        if ok:
            proof={"obstruction":obstruction,"verification":detail}
            base.update({
              "verdict":"CERTIFIED_NOT_QHORN",
              "external_unsat_used_as_authority":False,
              "negative_obstruction_verified":True,
              "proof":proof,
              "certificate_bytes":cert_size(proof)
            })
        else:
            base.update({
              "verdict":"INFRASTRUCTURE_ERROR",
              "external_unsat_used_as_authority":False,
              "negative_obstruction_verified":False,
              "failure":detail
            })

    elif status=="UNKNOWN":
        base.update({
          "verdict":"UNKNOWN_RESOURCE_LIMIT",
          "reason_unknown":proposal.get("reason_unknown"),
          "negative_obstruction_attempted":False
        })

    elif status=="ERROR":
        base.update({
          "verdict":"INFRASTRUCTURE_ERROR",
          "failure":{
            "external_proposer_error":proposal.get("error"),
            "error_type":proposal.get("error_type")
          }
        })

    else:
        base.update({
          "verdict":"INFRASTRUCTURE_ERROR",
          "failure":{
            "reason":"UNRECOGNIZED_PROPOSER_STATUS",
            "status":status
          }
        })

    base["proposer_runtime_seconds"]=proposal.get("runtime_seconds")
    base["checker_runtime_seconds"]=time.perf_counter()-t0
    return base


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("proposals")
    ap.add_argument("output")
    ap.add_argument("--indices",required=True)
    ap.add_argument("--source-artifact-metadata")
    ap.add_argument("--source-zip-sha256-file")
    ap.add_argument("--prereg-commit",required=True)
    ap.add_argument("--implementation-head",default="")
    ns=ap.parse_args()

    source=Path(ns.source)
    propdir=Path(ns.proposals)
    outp=Path(ns.output)
    data=json.loads(source.read_text(encoding="utf-8"))
    indices=[int(x) for x in ns.indices.split(",") if x.strip()]
    if set(indices)!=ALLOWED:
        raise SystemExit(f"INDEX_CONTRACT_MISMATCH {indices}")

    meta=load_source_metadata(
        Path(ns.source_artifact_metadata)
        if ns.source_artifact_metadata else None
    )
    zipsha=None
    if ns.source_zip_sha256_file:
        zipsha=Path(ns.source_zip_sha256_file).read_text().strip().split()[0]

    source_binding={
      "source_artifact_id":9992845123,
      "source_artifact_api_digest":meta.get("digest"),
      "source_artifact_workflow_head_sha":
          ((meta.get("workflow_run") or {}).get("head_sha")),
      "downloaded_source_zip_sha256":zipsha,
      "source_json_sha256":file_sha256(source),
      "source_internal_X_preregistration_commit":
          data.get("X_preregistration_commit"),
      "source_internal_parent_W_journal_commit":
          data.get("parent_W_journal_commit")
    }

    rows=[]
    for i in indices:
        pp=propdir/f"r50g25x_{i:02d}.proposal.json"
        if not pp.exists():
            rows.append({
              "index":i,
              "role":"PRIMARY_S7" if i in PRIMARY else "CONTROL",
              "verdict":"INFRASTRUCTURE_ERROR",
              "failure":{"reason":"MISSING_PROPOSAL_FILE"}
            })
            continue

        proposal=json.loads(pp.read_text(encoding="utf-8"))
        row=check_row(data["residuals"][i],i,proposal,source_binding)
        row["proposal_file"]=pp.name
        row["proposal_file_sha256"]=file_sha256(pp)
        row["proposal_file_bytes"]=pp.stat().st_size
        rows.append(row)

    out={
      "schema":"janus.trump.stage6.public_qhorn_certificate_gate.result.v1",
      "authority":
          "EXTERNAL_GENERIC_PROPOSAL_PLUS_INDEPENDENT_QHORN_CERTIFICATE_AND_TERMINAL_REPLAY",
      "gate":"TRUMP_STAGE6_PUBLIC_QHORN_CERTIFICATE_GATE",
      "prereg_commit":ns.prereg_commit,
      "implementation_head":ns.implementation_head,
      "source_binding":source_binding,
      "indices":indices,
      "rows":rows,
      "verdict_counts":dict(collections.Counter(r["verdict"] for r in rows)),
      "claim_ceiling":{
        "new_janus_controller_authorized":False,
        "general_sat_in_p":"NOT_PROVED",
        "p_eq_np":"NOT_PROVED",
        "p_vs_np":"OPEN",
        "finite_structural_success_is_asymptotic_theorem":False
      },
      "stage6B_stage6C_stage6D_executed":False
    }

    outp.parent.mkdir(parents=True,exist_ok=True)
    outp.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",
                    encoding="utf-8")
    print(json.dumps({
      "verdict_counts":out["verdict_counts"],
      "rows":[{"index":r["index"],"verdict":r["verdict"]}
              for r in rows]
    },sort_keys=True))


if __name__=="__main__":
    main()
