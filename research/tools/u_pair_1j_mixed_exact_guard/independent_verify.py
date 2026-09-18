#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

SCHEMA_IN="CONNECTED_MIXED_AFFINE_OR3_SOURCE_V1"
SCHEMA_CAND="PROOF_CARRYING_MIXED_AFFINE_OR3_PRIORITY_SEARCH_V1"


def canonical_bytes(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()


def sha256_path(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify(sp:Path,cp:Path):
    src=json.loads(sp.read_text())
    cand=json.loads(cp.read_text())
    assert src["schema"]==SCHEMA_IN
    assert cand["schema"]==SCHEMA_CAND
    assert cand["source_sha256"]==sha256_path(sp)

    d=cand["derivation"]
    assert d["new_rule_form_used"] is False
    assert d["nonlinear_xor_rule_used"] is False
    assert d["SAT_solver_calls"]==0
    assert d["generic_SK0LEM_VALID_calls"]==0
    assert d["generic_DAG_tautology_calls"]==0
    assert d["truth_table_enumeration"] is False
    assert d["boundary_assignment_enumeration"] is False
    assert d["precomputed_mixed_guard_used"] is False
    assert d["precomputed_or3_output_used"] is False
    assert d["old_connected_mixed_result_import_used"] is False
    assert d["old_tseitin_candidate_import_used"] is False
    assert d["spectral_metadata_used"] is False
    assert d["calculus_mutation_used"] is False

    nodes=cand["proof_nodes"]
    allowed={"CONST","AFFINE_XOR","GUARDED_ITE"}
    content_to_pid={}
    for pid,node in nodes.items():
        assert node.get("rule") in allowed
        key=json.dumps(node,sort_keys=True,separators=(",",":"))
        assert key not in content_to_pid
        content_to_pid[key]=pid
        if node["rule"]=="CONST":
            assert int(node["value"]) in (0,1)
        elif node["rule"]=="AFFINE_XOR":
            assert int(node["constant"]) in (0,1)
            assert len(node["support"])==len(set(node["support"]))
        else:
            for k in ("guard","true_child","false_child"):
                assert node[k] in nodes

    # Independent cycle check.
    state={}
    def dfs(pid,seen):
        s=state.get(pid,0)
        assert s!=1
        if s==2:
            seen.add(pid); return
        state[pid]=1; seen.add(pid)
        n=nodes[pid]
        if n["rule"]=="GUARDED_ITE":
            dfs(n["guard"],seen); dfs(n["true_child"],seen); dfs(n["false_child"],seen)
        state[pid]=2

    def reachable(roots):
        seen=set()
        for r in roots:
            state.clear()
            dfs(r,seen)
        return seen

    def node_id(payload):
        key=json.dumps(payload,sort_keys=True,separators=(",",":"))
        assert key in content_to_pid, f"missing expected node {payload}"
        return content_to_pid[key]

    pi=cand["proof_object"]
    pg=pi["Pi_guard"]
    ps=pi["Pi_select"]
    pd=pi["Pi_domain"]
    vertices=src["witness_decode_order"]
    vertex_rec={v["vertex_id"]:v for v in src["vertices"]}
    atoms={a["atom_id"]:a for a in src["affine_atoms"]}
    blocks={o["or3_id"]:o for o in src["or3_blocks"]}
    interleave={x["vertex_id"]:x["or3_id"] for x in src["candidate_interleave"]}
    n=len(vertices)
    assert n>0 and n & (n-1)==0
    assert len(src["witness_bits"])==int(math.log2(n))

    boundary_vars={e["boundary_var"] for e in src["edges"]}
    for node in nodes.values():
        if node["rule"]=="AFFINE_XOR":
            assert set(node["support"]) <= boundary_vars

    incident=defaultdict(list)
    for e in src["edges"]:
        incident[e["u"]].append(e["boundary_var"])
        incident[e["v"]].append(e["boundary_var"])

    guard_t0=time.perf_counter_ns()
    base={}
    guard_verifier_visits=0
    for v in vertices:
        payload={
            "rule":"AFFINE_XOR",
            "constant":int(vertex_rec[v]["charge"]),
            "support":sorted(incident[v])
        }
        pid=node_id(payload)
        assert pg["base_affine_roots"][v]==pid
        base[v]=pid
        guard_verifier_visits+=1

    atom_roots={}
    for aid,a in atoms.items():
        payload={
            "rule":"AFFINE_XOR",
            "constant":int(a["constant"]),
            "support":sorted(a["support"])
        }
        pid=node_id(payload)
        assert pg["raw_affine_atom_roots"][aid]==pid
        atom_roots[aid]=pid
        guard_verifier_visits+=1

    c0=node_id({"rule":"CONST","value":0})
    c1=node_id({"rule":"CONST","value":1})
    O={}; NOTO={}
    for oid,o in blocks.items():
        p,q,r=[atom_roots[x] for x in o["atom_ids"]]
        q_or_r=node_id({"rule":"GUARDED_ITE","guard":q,"true_child":c1,"false_child":r})
        oroot=node_id({"rule":"GUARDED_ITE","guard":p,"true_child":c1,"false_child":q_or_r})
        nroot=node_id({"rule":"GUARDED_ITE","guard":oroot,"true_child":c0,"false_child":c1})
        assert pg["or3_roots"][oid]==oroot
        assert pg["not_or3_roots"][oid]==nroot
        O[oid]=oroot; NOTO[oid]=nroot
        guard_verifier_visits+=3

    G={}
    for v in vertices:
        oid=interleave[v]
        groot=node_id({
            "rule":"GUARDED_ITE",
            "guard":base[v],
            "true_child":NOTO[oid],
            "false_child":O[oid]
        })
        assert pg["mixed_guard_roots"][v]==groot
        G[v]=groot
        guard_verifier_visits+=1
    T_guard_verify=time.perf_counter_ns()-guard_t0

    # Independent exact domain verification from raw source only.
    domain_t0=time.perf_counter_ns()
    assert pd["proof_object_class"]=="ODD_BASE_PLUS_EVEN_OR3_INCIDENCE_CERTIFICATE"
    assert pd["uses_mixed_guard_truth_table"] is False
    assert pd["uses_selector"] is False
    charge_xor=0
    for v in vertices:
        charge_xor ^= int(vertex_rec[v]["charge"])
    assert charge_xor==1==pd["observed_charge_xor"]

    edge_occ=Counter()
    for v in vertices:
        for y in incident[v]:
            edge_occ[y]+=1
    assert set(edge_occ)==boundary_vars
    assert all(x==2 for x in edge_occ.values())
    assert pd["edge_occurrence_target"]==2

    block_refs=Counter(interleave.values())
    assert set(block_refs)==set(blocks)
    assert all(x==2 for x in block_refs.values())
    assert pd["or3_reference_target"]==2
    assert pd["normal_form_target"]=={"constant":1,"nonlinear_pair_terms":[]}
    assert pd["conclusion"]=="DOMAIN_TRUE"
    domain_verifier_visits=len(vertices)+len(src["edges"])+len(src["candidate_interleave"])
    T_domain_verify=time.perf_counter_ns()-domain_t0

    # Canonical shared priority selector over exact mixed guards.
    select_t0=time.perf_counter_ns()
    roots=ps["witness_roots"]
    assert set(roots)==set(src["witness_bits"])
    selector_verifier_visits=0
    for bit_index,bit_name in enumerate(src["witness_bits"]):
        current=c1 if ((n-1 >> bit_index)&1) else c0
        selector_verifier_visits+=1
        for index in range(n-2,-1,-1):
            leaf=c1 if ((index >> bit_index)&1) else c0
            selector_verifier_visits+=1
            if leaf==current:
                continue
            current=node_id({
                "rule":"GUARDED_ITE",
                "guard":G[vertices[index]],
                "true_child":leaf,
                "false_child":current
            })
        assert roots[bit_name]==current
    T_select_verify=time.perf_counter_ns()-select_t0

    guard_set=reachable(G.values())
    selector_set=reachable(roots.values())
    shared=guard_set & selector_set
    union=guard_set | selector_set
    selector_exclusive=selector_set-guard_set

    def subset_bytes(ids,roots_obj):
        return len(canonical_bytes({
            "roots":roots_obj,
            "nodes":{pid:nodes[pid] for pid in sorted(ids)}
        }))

    expected={
        "S_guards_nodes":len(guard_set),
        "S_guards_bytes":subset_bytes(guard_set,G),
        "S_selector_reachable_nodes":len(selector_set),
        "S_selector_exclusive_nodes":len(selector_exclusive),
        "S_selector_bytes":subset_bytes(selector_set,roots),
        "S_selector_exclusive_bytes":subset_bytes(selector_exclusive,roots),
        "S_shared_guard_selector_nodes":len(shared),
        "S_domain_terms":len(vertices)+len(src["edges"])+len(blocks),
        "S_domain_bytes":len(canonical_bytes(pd)),
        "S_total_union_nodes":len(union),
        "S_total_union_bytes":subset_bytes(union,{"guards":G,"witness":roots}),
        "max_live_shared_nodes":len(nodes),
        "guard_constructor_visits":len(vertices)+len(atoms)+3*len(blocks)+len(vertices),
        "selector_constructor_visits":len(src["witness_bits"])*n,
        "domain_constructor_visits":len(vertices)+len(src["edges"])+len(src["candidate_interleave"])
    }
    metrics=cand["metrics"]
    for k,val in expected.items():
        assert metrics[k]==val, (k,metrics[k],val)

    return {
        "verdict":"PASS_INDEPENDENT_MIXED_GUARD_DOMAIN_SELECTOR_PROOF",
        "metrics_verified":True,
        "T_guard_verify_ns":T_guard_verify,
        "T_select_verify_ns":T_select_verify,
        "T_domain_verify_ns":T_domain_verify,
        "guard_verifier_visits":guard_verifier_visits,
        "selector_verifier_visits":selector_verifier_visits,
        "domain_verifier_visits":domain_verifier_visits,
        "domain_verified":"TRUE_BY_ODD_BASE_PARITY_PLUS_EVEN_DUPLICATED_OR3_INCIDENCE",
        "mixed_guards_verified":"AFFINE_XOR_PLUS_RAW_OR3_COMPOSITION",
        "selector_verified":"CANONICAL_PRIORITY_SELECTION_OVER_EXACT_MIXED_GUARDS",
        "candidate_constructor_imported":False,
        "reference_DAG_read":False,
        "semantic_truth_table_used":False,
        "generic_validity_used":False
    }


def main(src_s,cand_s,out_s):
    out=verify(Path(src_s),Path(cand_s))
    Path(out_s).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("usage: independent_verify.py SOURCE.json CANDIDATE.json OUT.json")
    main(sys.argv[1],sys.argv[2],sys.argv[3])
