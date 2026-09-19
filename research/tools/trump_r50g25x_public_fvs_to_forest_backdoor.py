#!/usr/bin/env python3
"""Public exact FVS -> variable-only strong Forest backdoor composition.

No FVS/backdoor search algorithm is implemented here. The external solver
proposes an exact feedback vertex set X of the CNF incidence graph.

For fixed-width CNF, convert X into a variable-only set:
  Y = (X ∩ Variables) ∪ ⋃_{clause c ∈ X} N(c).

If G_inc - X is a forest, then G_inc - Y is also a forest: each replaced
clause vertex c remains only as an isolated vertex because all N(c) are in Y,
and every other surviving cycle would already survive G_inc - X.

Hence Y is a deletion backdoor to incidence-forest, and therefore a strong
Forest backdoor for SAT: assigning Y can only delete further clause/edge
structure.

The harness independently verifies both G-X and G-Y are forests.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from collections import defaultdict, deque

S13={1,2,3,4,5,6,7,9,10,11,12,13,14}

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def build(clauses):
    adj=defaultdict(set)
    variables=sorted({abs(l) for c in clauses for l in c})
    for v in variables:
        adj[f"v{v}"]
    for ci,clause in enumerate(clauses):
        c=f"c{ci}"
        adj[c]
        for v in sorted({abs(l) for l in clause}):
            a=f"v{v}"
            adj[a].add(c); adj[c].add(a)
    return {k:set(v) for k,v in adj.items()},variables

def is_forest(adj, removed):
    seen=set()
    for root in adj:
        if root in removed or root in seen:
            continue
        stack=[(root,None)]
        seen.add(root)
        while stack:
            u,p=stack.pop()
            for v in adj[u]:
                if v in removed:
                    continue
                if v==p:
                    continue
                if v in seen:
                    return False
                seen.add(v)
                stack.append((v,u))
    return True

def emit(source:Path,out:Path):
    data=json.loads(source.read_text(encoding="utf-8"))
    out.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for i,row in enumerate(data["residuals"]):
        if i not in S13: continue
        clauses=row["residual_formula"]
        adj,vars_=build(clauses)
        graph=out/f"r50g25x_{i:02d}.graph"
        with graph.open("w",encoding="ascii") as f:
            f.write(f"# R50G25X index {i} {row['residual_hash']}\n")
            done=set()
            for u in sorted(adj):
                for v in sorted(adj[u]):
                    e=tuple(sorted((u,v)))
                    if e in done: continue
                    done.add(e)
                    f.write(f"{e[0]} {e[1]}\n")
        manifest.append({
            "index":i,"family":row["family"],"hash":row["residual_hash"],
            "CLV":row["residual_CLV"],"canonical_formula_sha256":canonical_sha(clauses),
            "graph_file":graph.name,"variable_ids":vars_,
            "max_clause_width":max((len(c) for c in clauses),default=0),
            "incidence_vertices":len(adj),
            "incidence_edges":sum(len(x) for x in adj.values())//2,
        })
    (out/"manifest.json").write_text(json.dumps({
        "schema":"janus.trump.r50g25x.public_fvs_forest_backdoor_manifest.v1",
        "source_artifact_id":9992845123,"indices":sorted(S13),"rows":manifest
    },indent=2,sort_keys=True)+"\n",encoding="utf-8")

def parse_solution(path:Path):
    if not path.exists(): return []
    return [x.strip() for x in path.read_text(encoding="utf-8",errors="replace").splitlines()
            if x.strip() and not x.lstrip().startswith("#")]

def verify(source:Path, manifest_path:Path, sol_dir:Path, status_dir:Path, output:Path, solver_commit:str):
    data=json.loads(source.read_text(encoding="utf-8"))
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    rows=[]
    for m in manifest["rows"]:
        i=m["index"]; src=data["residuals"][i]
        if canonical_sha(src["residual_formula"])!=m["canonical_formula_sha256"]:
            raise AssertionError(("SOURCE_HASH_MISMATCH",i))
        adj,_=build(src["residual_formula"])
        sol=parse_solution(sol_dir/f"r50g25x_{i:02d}.out")
        rcpath=status_dir/f"r50g25x_{i:02d}.rc"
        rc=rcpath.read_text().strip() if rcpath.exists() else "MISSING"
        known=set(adj)
        invalid=sorted(set(sol)-known)
        if invalid: raise AssertionError(("UNKNOWN_FVS_VERTEX",i,invalid))
        exact_completed=(rc=="0")
        x=set(sol)
        fvs_pass=is_forest(adj,x) if exact_completed else False

        y={u for u in x if u.startswith("v")}
        replaced={}
        for c in sorted(u for u in x if u.startswith("c")):
            ns=sorted(v for v in adj[c] if v.startswith("v"))
            replaced[c]=ns
            y.update(ns)
        y_pass=is_forest(adj,y) if exact_completed and fvs_pass else False
        if exact_completed and (not fvs_pass or not y_pass):
            raise AssertionError(("FOREST_REPLAY_FAIL",i,fvs_pass,y_pass))

        rows.append({
            **m,
            "solver_returncode":rc,
            "exact_solver_completed":exact_completed,
            "public_fvs_vertices":sorted(x),
            "public_fvs_size":len(x) if exact_completed else None,
            "public_fvs_replay":"PASS" if fvs_pass else ("NOT_RUN_TIMEOUT" if not exact_completed else "FAIL"),
            "clause_vertices_replaced":replaced,
            "variable_only_backdoor":sorted(y),
            "variable_only_backdoor_size":len(y) if exact_completed else None,
            "variable_only_forest_replay":"PASS" if y_pass else ("NOT_RUN_TIMEOUT" if not exact_completed else "FAIL"),
        })
    completed=[r for r in rows if r["exact_solver_completed"]]
    out={
      "schema":"janus.trump.r50g25x.public_exact_fvs_to_strong_forest_backdoor.v1",
      "authority":"PUBLIC_EXACT_FVS_PROPOSAL_PLUS_INDEPENDENT_FOREST_REPLAY__FINITE_CORPUS_ONLY",
      "external_solver":{
        "repo":"wata-orz/fvs","commit":solver_commit,
        "algorithm":"default FPTBranchingSolver","published_runtime":"O*(4^k)"
      },
      "composition":{
        "rule":"replace every clause-vertex in FVS X by all its incident variable vertices",
        "bound":"|Y| <= d*|X| for d-CNF",
        "soundness":"G_inc-X forest => G_inc-Y forest => Y is a strong Forest deletion backdoor",
        "polynomial_promotion":"for fixed d, if public FVS parameter k=O(log n), O*(4^k) discovery plus 2^(d*k) Forest-backdoor branching is polynomial"
      },
      "rows":rows,
      "completed_indices":[r["index"] for r in completed],
      "claim_ceiling":{
        "minimum_variable_only_forest_backdoor":"NOT_CLAIMED",
        "timeouts_mean_no_fvs":False,
        "general_sat_in_p":"NOT_PROVED","p_eq_np":"NOT_PROVED","p_vs_np":"OPEN"
      }
    }
    output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    a=sub.add_parser("emit"); a.add_argument("source"); a.add_argument("out")
    b=sub.add_parser("verify"); b.add_argument("source"); b.add_argument("manifest"); b.add_argument("solutions"); b.add_argument("statuses"); b.add_argument("output"); b.add_argument("--solver-commit",required=True)
    ns=ap.parse_args()
    if ns.cmd=="emit": emit(Path(ns.source),Path(ns.out))
    else: verify(Path(ns.source),Path(ns.manifest),Path(ns.solutions),Path(ns.statuses),Path(ns.output),ns.solver_commit)

if __name__=="__main__": main()
