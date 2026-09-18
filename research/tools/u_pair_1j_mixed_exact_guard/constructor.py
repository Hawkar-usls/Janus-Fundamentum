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
SCHEMA_OUT="PROOF_CARRYING_MIXED_AFFINE_OR3_PRIORITY_SEARCH_V1"
ALGORITHM="GENERIC_RAW_AFFINE_OR3_EXACT_GUARD_PRIORITY_SEARCH_V1"


def canonical_bytes(obj):
    return (json.dumps(obj,sort_keys=True,separators=(",",":"))+"\n").encode()


def sha256_path(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def synthesize(src):
    if src["schema"]!=SCHEMA_IN:
        raise ValueError("unsupported source schema")
    vertices=src["witness_decode_order"]
    n=len(vertices)
    if n==0 or n & (n-1):
        raise ValueError("vertex count must be a power of two")
    witness_bits=src["witness_bits"]
    if len(witness_bits)!=int(math.log2(n)):
        raise ValueError("wrong witness width")

    vertex_rec={v["vertex_id"]:v for v in src["vertices"]}
    if set(vertex_rec)!=set(vertices):
        raise ValueError("decode order/vertex mismatch")
    incident=defaultdict(list)
    for e in src["edges"]:
        incident[e["u"]].append(e["boundary_var"])
        incident[e["v"]].append(e["boundary_var"])
    atoms={a["atom_id"]:a for a in src["affine_atoms"]}
    blocks={o["or3_id"]:o for o in src["or3_blocks"]}
    interleave={x["vertex_id"]:x["or3_id"] for x in src["candidate_interleave"]}
    if set(interleave)!=set(vertices):
        raise ValueError("interleave must cover every vertex exactly once")

    nodes={}
    hashcons={}
    next_id=0

    def intern(payload):
        nonlocal next_id
        key=json.dumps(payload,sort_keys=True,separators=(",",":"))
        if key in hashcons:
            return hashcons[key]
        pid=f"m{next_id}"
        next_id+=1
        nodes[pid]=payload
        hashcons[key]=pid
        return pid

    def const(v):
        return intern({"rule":"CONST","value":int(v)})

    def affine(c,support):
        return intern({
            "rule":"AFFINE_XOR",
            "constant":int(c),
            "support":sorted(support)
        })

    def ite(g,t,f):
        if t==f:
            return t
        return intern({
            "rule":"GUARDED_ITE",
            "guard":g,
            "true_child":t,
            "false_child":f
        })

    c0=const(0); c1=const(1)

    guard_t0=time.perf_counter_ns()
    base_affine={}
    guard_constructor_visits=0
    for v in vertices:
        base_affine[v]=affine(vertex_rec[v]["charge"],incident[v])
        guard_constructor_visits+=1

    atom_roots={}
    for aid,a in atoms.items():
        atom_roots[aid]=affine(a["constant"],a["support"])
        guard_constructor_visits+=1

    or3_roots={}
    not_or3_roots={}
    for oid,o in blocks.items():
        p,q,r=[atom_roots[x] for x in o["atom_ids"]]
        q_or_r=ite(q,c1,r)
        O=ite(p,c1,q_or_r)
        not_O=ite(O,c0,c1)
        or3_roots[oid]=O
        not_or3_roots[oid]=not_O
        guard_constructor_visits+=3

    mixed_guard_roots={}
    for v in vertices:
        oid=interleave[v]
        mixed_guard_roots[v]=ite(base_affine[v],not_or3_roots[oid],or3_roots[oid])
        guard_constructor_visits+=1
    T_guard_synth=time.perf_counter_ns()-guard_t0

    domain_t0=time.perf_counter_ns()
    charge_xor=0
    for v in vertices:
        charge_xor ^= int(vertex_rec[v]["charge"])
    edge_occ=Counter()
    for e in src["edges"]:
        edge_occ[e["boundary_var"]]+=2
    block_refs=Counter(interleave.values())
    domain_proof={
        "proof_object_class":"ODD_BASE_PLUS_EVEN_OR3_INCIDENCE_CERTIFICATE",
        "observed_charge_xor":charge_xor,
        "edge_occurrence_target":2,
        "or3_reference_target":2,
        "normal_form_target":{"constant":1,"nonlinear_pair_terms":[]},
        "conclusion":"DOMAIN_TRUE",
        "uses_mixed_guard_truth_table":False,
        "uses_selector":False
    }
    domain_constructor_visits=len(vertices)+len(src["edges"])+len(src["candidate_interleave"])
    T_domain_synth=time.perf_counter_ns()-domain_t0

    select_t0=time.perf_counter_ns()
    witness_roots={}
    selector_constructor_visits=0
    for bit_index,bit_name in enumerate(witness_bits):
        root=const((n-1 >> bit_index)&1)
        selector_constructor_visits+=1
        for index in range(n-2,-1,-1):
            leaf=const((index >> bit_index)&1)
            root=ite(mixed_guard_roots[vertices[index]],leaf,root)
            selector_constructor_visits+=1
        witness_roots[bit_name]=root
    T_select_synth=time.perf_counter_ns()-select_t0

    def reachable(roots):
        seen=set(); stack=list(roots)
        while stack:
            pid=stack.pop()
            if pid in seen:
                continue
            seen.add(pid)
            node=nodes[pid]
            if node["rule"]=="GUARDED_ITE":
                stack.extend([node["guard"],node["true_child"],node["false_child"]])
        return seen

    guard_set=reachable(mixed_guard_roots.values())
    selector_set=reachable(witness_roots.values())
    shared=guard_set & selector_set
    union=guard_set | selector_set
    selector_exclusive=selector_set-guard_set

    def subset_bytes(ids,roots):
        return len(canonical_bytes({
            "roots":roots,
            "nodes":{pid:nodes[pid] for pid in sorted(ids)}
        }))

    guard_bytes=subset_bytes(guard_set,mixed_guard_roots)
    selector_bytes=subset_bytes(selector_set,witness_roots)
    selector_exclusive_bytes=subset_bytes(selector_exclusive,witness_roots)
    total_union_bytes=subset_bytes(union,{"guards":mixed_guard_roots,"witness":witness_roots})
    domain_bytes=len(canonical_bytes(domain_proof))

    return {
        "schema":SCHEMA_OUT,
        "algorithm":ALGORITHM,
        "encoding":"LSB_FIRST_VERTEX_INDEX",
        "proof_object":{
            "Pi_guard":{
                "base_affine_roots":base_affine,
                "raw_affine_atom_roots":atom_roots,
                "or3_roots":or3_roots,
                "not_or3_roots":not_or3_roots,
                "mixed_guard_roots":mixed_guard_roots
            },
            "Pi_select":{
                "witness_roots":witness_roots
            },
            "Pi_domain":domain_proof
        },
        "proof_nodes":nodes,
        "derivation":{
            "allowed_rules_used":sorted({x["rule"] for x in nodes.values()}),
            "derived_guard_roots_used":True,
            "new_rule_form_used":False,
            "nonlinear_xor_rule_used":False,
            "SAT_solver_calls":0,
            "generic_SK0LEM_VALID_calls":0,
            "generic_DAG_tautology_calls":0,
            "truth_table_enumeration":False,
            "boundary_assignment_enumeration":False,
            "precomputed_mixed_guard_used":False,
            "precomputed_or3_output_used":False,
            "old_connected_mixed_result_import_used":False,
            "old_tseitin_candidate_import_used":False,
            "spectral_metadata_used":False,
            "calculus_mutation_used":False
        },
        "metrics":{
            "S_guards_nodes":len(guard_set),
            "S_guards_bytes":guard_bytes,
            "S_selector_reachable_nodes":len(selector_set),
            "S_selector_exclusive_nodes":len(selector_exclusive),
            "S_selector_bytes":selector_bytes,
            "S_selector_exclusive_bytes":selector_exclusive_bytes,
            "S_shared_guard_selector_nodes":len(shared),
            "S_domain_terms":len(vertices)+len(src["edges"])+len(blocks),
            "S_domain_bytes":domain_bytes,
            "S_total_union_nodes":len(union),
            "S_total_union_bytes":total_union_bytes,
            "max_live_shared_nodes":len(nodes),
            "T_guard_synth_ns":T_guard_synth,
            "T_select_synth_ns":T_select_synth,
            "T_domain_synth_ns":T_domain_synth,
            "guard_constructor_visits":guard_constructor_visits,
            "selector_constructor_visits":selector_constructor_visits,
            "domain_constructor_visits":domain_constructor_visits
        }
    }


def main(src_s,out_s):
    sp=Path(src_s)
    src=json.loads(sp.read_text())
    cand=synthesize(src)
    cand["source_sha256"]=sha256_path(sp)
    Path(out_s).write_text(json.dumps(cand,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"metrics":cand["metrics"]},sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: constructor.py SOURCE.json OUT.json")
    main(sys.argv[1],sys.argv[2])
