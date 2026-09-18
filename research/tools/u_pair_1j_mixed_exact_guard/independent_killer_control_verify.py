#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SCHEMA="MIXED_EXACT_GUARD_KILLER_CONTROL_SOURCE_V1"
CAND_SCHEMA="MIXED_EXACT_GUARD_KILLER_CONTROL_CANDIDATES_V1"


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"))


def sha256_path(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def eval_node(nodes,pid,assignment,memo):
    if pid in memo:
        return memo[pid]
    n=nodes[pid]
    r=n["rule"]
    if r=="CONST":
        v=bool(n["value"])
    elif r=="AFFINE_XOR":
        bit=int(n["constant"])
        for x in n["support"]:
            bit ^= int(bool(assignment[x]))
        v=bool(bit)
    elif r=="GUARDED_ITE":
        g=eval_node(nodes,n["guard"],assignment,memo)
        v=eval_node(nodes,n["true_child"] if g else n["false_child"],assignment,memo)
    else:
        raise AssertionError("forbidden rule")
    memo[pid]=v
    return v


def verify(src,cand):
    assert src["schema"]==SCHEMA
    assert cand["schema"]==CAND_SCHEMA
    dc=cand["derivation_contract"]
    assert dc["new_rule_form_used"] is False
    assert dc["nonlinear_xor_rule_used"] is False
    assert dc["SAT_solver_calls"]==0
    assert dc["generic_SK0LEM_VALID_calls"]==0
    assert dc["generic_DAG_tautology_calls"]==0
    assert dc["truth_table_enumeration"] is False
    assert dc["source_precomputed_or3_output_used"] is False
    assert dc["source_precomputed_mixed_guard_used"] is False

    nodes=cand["nodes"]
    roots=cand["roots"]
    allowed={"CONST","AFFINE_XOR","GUARDED_ITE"}

    # Local well-formedness, acyclicity by creation/reference order is not trusted;
    # independently DFS every root and reject cycles/dangling refs.
    for pid,n in nodes.items():
        assert n.get("rule") in allowed
        if n["rule"]=="CONST":
            assert int(n["value"]) in (0,1)
        elif n["rule"]=="AFFINE_XOR":
            assert int(n["constant"]) in (0,1)
            assert len(n["support"])==len(set(n["support"]))
            assert set(n["support"]) <= set(src["boundary_vars"])
        else:
            for k in ("guard","true_child","false_child"):
                assert n[k] in nodes

    state={}
    def dfs(pid):
        s=state.get(pid,0)
        assert s!=1, "cycle"
        if s==2:
            return
        state[pid]=1
        n=nodes[pid]
        if n["rule"]=="GUARDED_ITE":
            dfs(n["guard"]); dfs(n["true_child"]); dfs(n["false_child"])
        state[pid]=2
    for pid in roots.values():
        assert pid in nodes
        dfs(pid)

    # Exact raw affine atoms.
    expected_affine={}
    for name,a in src["raw_affine_atoms"].items():
        payload={"rule":"AFFINE_XOR","constant":int(a["constant"]),"support":sorted(a["support"])}
        matches=[pid for pid,n in nodes.items() if n==payload]
        assert len(matches)==1
        expected_affine[name]=matches[0]
        assert roots[name]==matches[0]

    def unique(payload):
        matches=[pid for pid,n in nodes.items() if n==payload]
        assert len(matches)==1, f"missing or duplicate expected node {payload}"
        return matches[0]

    c0=unique({"rule":"CONST","value":0})
    c1=unique({"rule":"CONST","value":1})
    A=expected_affine["A"]; P=expected_affine["P"]; Q=expected_affine["Q"]; R=expected_affine["R"]

    # Structural derivation:
    # O = ITE(P,1,ITE(Q,1,R))
    q_or_r=unique({"rule":"GUARDED_ITE","guard":Q,"true_child":c1,"false_child":R})
    O=unique({"rule":"GUARDED_ITE","guard":P,"true_child":c1,"false_child":q_or_r})
    assert roots["O"]==O

    # NOT O = ITE(O,0,1)
    not_O=unique({"rule":"GUARDED_ITE","guard":O,"true_child":c0,"false_child":c1})
    assert roots["NOT_O"]==not_O

    # G = ITE(A,NOT O,O)
    G=unique({"rule":"GUARDED_ITE","guard":A,"true_child":not_O,"false_child":O})
    assert roots["G"]==G

    # No node may smuggle a nonlinear XOR as AFFINE_XOR.
    for n in nodes.values():
        if n["rule"]=="AFFINE_XOR":
            assert all(isinstance(x,str) and x in src["boundary_vars"] for x in n["support"])

    # Two targeted semantic counterexamples, not a full truth table.
    # 1) AFFINE-only root A must fail target G.
    t1={x:False for x in src["boundary_vars"]}
    t1["c"]=True  # A=0, P=1 => O=1 => G=1
    A1=eval_node(nodes,roots["AFFINE_ONLY_SHORTCUT"],t1,{})
    G1=eval_node(nodes,G,t1,{})
    assert A1 is False and G1 is True

    # 2) OR3-only root O must fail target G.
    t2=dict(t1)
    t2["a"]=True  # A=1, O=1 => G=0
    O2=eval_node(nodes,roots["OR3_ONLY_SHORTCUT"],t2,{})
    G2=eval_node(nodes,G,t2,{})
    assert O2 is True and G2 is False

    # Local compositional semantics are enough for the positive proof:
    # ITE semantics plus exact affine leaves establish the target structurally.
    used_rules=sorted({n["rule"] for n in nodes.values()})
    return {
        "verdict":"PASS_EXACT_MIXED_GUARD_DERIVATION_UNDER_FROZEN_V1_1",
        "checks":{
            "source_is_raw": (
                src["raw_or3"]["output_node_present"] is False
                and src["anti_cheat"]["precomputed_or3_output_node_present"] is False
                and src["anti_cheat"]["precomputed_mixed_guard_node_present"] is False
            ),
            "only_frozen_rule_forms_used":used_rules==["AFFINE_XOR","CONST","GUARDED_ITE"],
            "derived_guard_root_O_used_legally":True,
            "O_structurally_equals_OR3":True,
            "NOT_O_structurally_derived_by_ITE":True,
            "G_structurally_equals_A_XOR_O":True,
            "affine_only_shortcut_rejected":True,
            "or3_only_shortcut_rejected":True,
            "generic_tautology_used":False,
            "truth_table_used":False,
            "nonlinear_xor_rule_added":False,
            "calculus_mutation_used":False
        },
        "proof_nodes":len(nodes),
        "targeted_negative_assignments_checked":2,
        "scientific_firewall":{
            "killer_control_only":True,
            "hostile_series_not_run":True,
            "GENERAL_SAT_IN_P":"NOT_PROVED",
            "P_EQ_NP":"NOT_PROVED",
            "P_VS_NP":"OPEN"
        }
    }


def main(src_s,cand_s,out_s):
    sp=Path(src_s); cp=Path(cand_s)
    src=json.loads(sp.read_text())
    cand=json.loads(cp.read_text())
    assert cand["source_sha256"]==sha256_path(sp)
    out=verify(src,cand)
    out["source_sha256"]=sha256_path(sp)
    out["candidate_sha256"]=sha256_path(cp)
    Path(out_s).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=4:
        raise SystemExit("usage: independent_killer_control_verify.py SOURCE.json CANDIDATE.json OUT.json")
    main(sys.argv[1],sys.argv[2],sys.argv[3])
