#!/usr/bin/env python3
"""Bind externally validated PACE incidence decompositions to frozen BA25.

No new SAT algorithm is implemented here. The script imports the byte-identical
frozen BA25 implementation and applies its already-certified arbitrary-CNF
embedding.

For a CNF F with incidence graph H_F and supplied TD T:
  * map PACE variable/clause vertices into BA25 v:x_i / C:j vertices,
  * attach the singleton block leaves required by embed_cnf,
  * attach the auxiliary z--{B_z,C_z} component,
  * independently call BA25.validate_td on G_star,
  * check tau_embedding == max(1, tau(T)).

Optionally, selected finite rows can be solved with BA25.run_dp and the returned
witness is replayed directly on the original frozen CNF.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve()
sys.path.insert(0,str(HERE.parents[1]))
import janus_trump_r50g25ba25 as ba25


def canonical_sha(clauses):
    raw=json.dumps(clauses,sort_keys=True,separators=(",",":")).encode()
    return hashlib.sha256(raw).hexdigest()


def parse_pace_td(path:Path):
    bags={}
    edges=[]
    claimed=None
    for raw in path.read_text(encoding="utf-8",errors="replace").splitlines():
        s=raw.strip()
        if not s or s.startswith("c"):
            continue
        p=s.split()
        if p[0]=="s":
            if len(p)<5 or p[1]!="td":
                raise ValueError(("BAD_TD_HEADER",s))
            claimed={"nbags":int(p[2]),"max_bag_size":int(p[3]),"graph_n":int(p[4]),"width":int(p[3])-1}
        elif p[0]=="b":
            bags[p[1]]=frozenset(map(int,p[2:]))
        else:
            if len(p)!=2:
                raise ValueError(("BAD_TD_EDGE",s))
            edges.append((p[0],p[1]))
    if claimed is None:
        raise ValueError("NO_TD_HEADER")
    if len(bags)!=claimed["nbags"]:
        raise ValueError(("BAG_COUNT",len(bags),claimed["nbags"]))
    return bags,tuple(edges),claimed


def source_to_ba25(clauses,variables):
    index={v:i for i,v in enumerate(variables)}
    c2=[]
    for clause in clauses:
        cc=[]
        for lit in clause:
            v=abs(lit)
            if v not in index:
                raise ValueError(("UNKNOWN_SOURCE_VAR",v))
            cc.append((f"x{index[v]}",1 if lit>0 else -1))
        c2.append(cc)
    return ba25.embed_cnf(len(variables),c2)


def lift_td(pace_bags,pace_edges,nv,nclauses):
    bags={}
    for bid,bag in pace_bags.items():
        mapped=set()
        for q in bag:
            if 1 <= q <= nv:
                mapped.add(f"v:x{q-1}")
            elif nv+1 <= q <= nv+nclauses:
                mapped.add(f"C:{q-nv-1}")
            else:
                raise ValueError(("PACE_VERTEX_OUT_OF_RANGE",q,nv,nclauses))
        bags[f"p{bid}"]=frozenset(mapped)
    edges=[(f"p{a}",f"p{b}") for a,b in pace_edges]

    # Attach one singleton block leaf for each original variable.
    for i in range(nv):
        v=f"v:x{i}"
        holders=[bid for bid,b in bags.items() if v in b]
        if not holders:
            raise ValueError(("VARIABLE_MISSING_FROM_PACE_TD",i))
        anchor=sorted(holders)[0]
        leaf=f"bx{i}"
        bags[leaf]=frozenset({v,f"B:{i+1}"})
        edges.append((anchor,leaf))

    # embed_cnf prepends variable z, uses B:0 for its singleton block,
    # and appends the unit clause (z), hence C:nclauses.
    bz="bz"
    cz="cz"
    bags[bz]=frozenset({"v:z","B:0"})
    bags[cz]=frozenset({"v:z",f"C:{nclauses}"})
    edges.append((bz,cz))
    if pace_bags:
        edges.append((sorted(f"p{x}" for x in pace_bags)[0],bz))

    return ba25.TD(bags,tuple(edges))


def replay_source(clauses,variables,witness):
    if witness is None:
        return False,None
    ass={v:bool(witness[f"x{i}"]) for i,v in enumerate(variables)}
    bad=[]
    for j,c in enumerate(clauses):
        if not any((lit>0 and ass[abs(lit)]) or (lit<0 and not ass[abs(lit)]) for lit in c):
            bad.append(j)
    return not bad,bad


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("source_json")
    ap.add_argument("manifest_json")
    ap.add_argument("td_dir")
    ap.add_argument("output_json")
    ap.add_argument("--solve-indices",default="")
    ns=ap.parse_args()

    src=json.loads(Path(ns.source_json).read_text(encoding="utf-8"))
    manifest=json.loads(Path(ns.manifest_json).read_text(encoding="utf-8"))
    mby={r["index"]:r for r in manifest["rows"]}
    solve={int(x) for x in ns.solve_indices.split(",") if x.strip()}
    rows=[]

    for i,row in enumerate(src["residuals"]):
        clauses=row["residual_formula"]
        mr=mby[i]
        if canonical_sha(clauses)!=mr["formula_canonical_sha256"]:
            raise AssertionError(("SOURCE_MANIFEST_HASH_MISMATCH",i))
        variables=mr["original_variable_ids"]
        if sorted({abs(l) for c in clauses for l in c})!=variables:
            raise AssertionError(("VARIABLE_MAP_MISMATCH",i))

        td_path=Path(ns.td_dir)/f"r50g25x_{i:02d}.td"
        pb,pe,ph=parse_pace_td(td_path)
        inst=source_to_ba25(clauses,variables)
        td=lift_td(pb,pe,len(variables),len(clauses))
        verts,gedges=ba25.factor_graph(inst)
        ok,vr=ba25.validate_td(verts,gedges,td)
        expected=max(1,ph["width"])
        if not ok or vr["tau"]!=expected:
            raise AssertionError(("BA25_TD_BIND_FAIL",i,ok,vr,expected))

        rr={
            "index":i,
            "family":row["family"],
            "hash":row["residual_hash"],
            "CLV":row["residual_CLV"],
            "pace_width":ph["width"],
            "ba25_tau":vr["tau"],
            "expected_tau":expected,
            "ba25_td_validation":"PASS",
            "embedding_contract":"FROZEN_BA25_embed_cnf",
        }

        if i in solve:
            dp=ba25.run_dp(inst,td,proof=False)
            source_ok,bad=replay_source(clauses,variables,dp["witness"])
            rr.update({
                "ba25_execution":"PASS",
                "sat":dp["sat"],
                "exact_count":str(dp["count"]),
                "max_states":dp["max_states"],
                "state_bound":dp["state_bound"],
                "nice_nodes":dp["nice_nodes"],
                "source_witness_replay":"PASS" if dp["sat"] and source_ok else ("N/A_UNSAT" if not dp["sat"] else "FAIL"),
                "source_bad_clauses":[] if bad is None else bad,
            })
            if dp["sat"] and not source_ok:
                raise AssertionError(("SOURCE_WITNESS_REPLAY_FAIL",i,bad))
        else:
            rr["ba25_execution"]="NOT_REQUESTED"
        rows.append(rr)

    out={
        "schema":"janus.trump.r50g25x.external_pace_td_to_frozen_ba25.v1",
        "authority":"EXACT_ADAPTER_VALIDATION_USING_BYTE_IDENTICAL_FROZEN_BA25_IMPLEMENTATION__FINITE_CORPUS_ONLY",
        "ba25_implementation_blob":"cad9c5f837d9d3c4e1c4bd4abef40976f2bb36ff",
        "source_artifact_id":9992845123,
        "rows":rows,
        "all_15_td_bindings_pass":all(r["ba25_td_validation"]=="PASS" for r in rows),
        "executed_indices":sorted(solve),
        "claim_ceiling":{
            "minimum_treewidth":"NOT_CLAIMED",
            "O_log_n_family_bound":"NOT_ESTABLISHED",
            "general_sat_in_p":"NOT_PROVED",
            "p_vs_np":"OPEN",
        },
    }
    Path(ns.output_json).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "all_15_td_bindings_pass":out["all_15_td_bindings_pass"],
        "executed_indices":out["executed_indices"],
        "taus":[r["ba25_tau"] for r in rows],
    },sort_keys=True))


if __name__=="__main__":
    main()
