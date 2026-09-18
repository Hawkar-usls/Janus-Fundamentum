#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

SCHEMA="MIXED_EXACT_GUARD_KILLER_CONTROL_SOURCE_V1"
OUT_SCHEMA="MIXED_EXACT_GUARD_KILLER_CONTROL_CANDIDATES_V1"


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"))


def sha256_path(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build(src):
    if src["schema"]!=SCHEMA:
        raise ValueError("wrong source schema")
    atoms=src["raw_affine_atoms"]

    nodes={}
    hashcons={}
    next_id=0

    def intern(payload):
        nonlocal next_id
        key=canonical(payload)
        if key in hashcons:
            return hashcons[key]
        pid=f"k{next_id}"
        next_id+=1
        nodes[pid]=payload
        hashcons[key]=pid
        return pid

    def const(v):
        return intern({"rule":"CONST","value":int(v)})

    def affine(name):
        a=atoms[name]
        return intern({
            "rule":"AFFINE_XOR",
            "constant":int(a["constant"]),
            "support":sorted(a["support"])
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

    A=affine("A")
    P=affine("P")
    Q=affine("Q")
    R=affine("R")
    c0=const(0)
    c1=const(1)

    # O = P OR Q OR R, using only frozen V1.1 forms.
    q_or_r=ite(Q,c1,R)
    O=ite(P,c1,q_or_r)

    # NOT O = ITE(O, 0, 1), no new NOT rule.
    not_O=ite(O,c0,c1)

    # G = A XOR O = ITE(A, NOT O, O), no nonlinear XOR rule.
    G=ite(A,not_O,O)

    return {
        "schema":OUT_SCHEMA,
        "nodes":nodes,
        "roots":{
            "A":A,"P":P,"Q":Q,"R":R,
            "O":O,"NOT_O":not_O,"G":G,
            "AFFINE_ONLY_SHORTCUT":A,
            "OR3_ONLY_SHORTCUT":O
        },
        "derivation_contract":{
            "allowed_rule_forms":["CONST","AFFINE_XOR","GUARDED_ITE"],
            "derived_guard_roots_used":True,
            "new_rule_form_used":False,
            "nonlinear_xor_rule_used":False,
            "SAT_solver_calls":0,
            "generic_SK0LEM_VALID_calls":0,
            "generic_DAG_tautology_calls":0,
            "truth_table_enumeration":False,
            "source_precomputed_or3_output_used":False,
            "source_precomputed_mixed_guard_used":False
        }
    }


def main(src_s,out_s):
    sp=Path(src_s)
    src=json.loads(sp.read_text())
    out=build(src)
    out["source_sha256"]=sha256_path(sp)
    Path(out_s).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "root_G":out["roots"]["G"],
        "proof_nodes":len(out["nodes"]),
        "new_rule_form_used":False
    },sort_keys=True))


if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: killer_control_build.py SOURCE.json OUT.json")
    main(sys.argv[1],sys.argv[2])
