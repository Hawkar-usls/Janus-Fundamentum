from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Sequence

from janus_c049_1_b3_expand_join_shrink_core import (
    Statistic,
    contains,
    decode_trajectory,
    encode_trajectory,
    expand_trajectory,
    shrink_trajectory,
    subspace_intersection,
    subspace_sum,
    up_k,
    width,
    xor_basis,
)
from janus_c049_1_b3_join_path_domain_corrected import (
    EXTENSION_PREORDER_STEPS,
    JOIN_INTERLEAVING_STEPS,
    join_trajectory,
    ordinary_join_paths,
)

SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"
SPEC_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace_executor_spec.v1"
CLOSED = "CLOSED_COMPLETE_TRACE"
OPEN = "OPEN_RUNTIME_CAPABILITY"


def cb(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(x: Any) -> str:
    return hashlib.sha256(cb(x)).hexdigest()


def load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def subset(a: Sequence[int], b: Sequence[int]) -> bool:
    return contains(tuple(b), tuple(a))


def entry_digest(entries: Sequence[dict]) -> str:
    return dg(sorted(dg(e["trajectory"]) for e in entries))


def normalize_entries(r: dict) -> list[dict]:
    out = [{"trajectory": e["trajectory"], "source_index": int(e["source_index"]), "witness": e["witness"]} for e in r.get("entries", [])]
    return sorted(out, key=lambda e: (dg(e["trajectory"]), e["source_index"], dg(e["witness"])))


def independent_upk(gens, B, d, k, caps, stage):
    B = xor_basis(B, d)
    if len(B) > caps["max_boundary_dim"]:
        return None, ("BOUNDARY_DIM_CAP", len(B), caps["max_boundary_dim"], stage)
    if k > caps["max_k"]:
        return None, ("K_CAP", k, caps["max_k"], stage)
    if not gens:
        return {"boundary": list(B), "k": k, "generator_count": 0, "universe_size": None, "entry_count": 0, "entries": []}, None
    r = up_k(gens, B, d, k)
    r["entries"] = normalize_entries(r)
    if r["entry_count"] > caps["max_full_set_entries"]:
        return None, ("FULL_SET_ENTRY_CAP", r["entry_count"], caps["max_full_set_entries"], stage)
    return r, None


def parse_input(raw: dict):
    d, k = int(raw["ambient_dim"]), int(raw["k"])
    if d <= 0 or k < 0:
        raise AssertionError("bad d/k")
    fac = {}
    for f in raw["factors"]:
        fid = str(f["id"])
        if not fid or fid in fac:
            raise AssertionError("duplicate factor")
        fac[fid] = {"id": fid, "normal_space": list(xor_basis(f.get("normal_space", []), d)), "affine_offset": f.get("affine_offset")}
    if not fac:
        raise AssertionError("empty factors")
    tr = raw["tree"]
    root = str(tr["root"])
    nodes = {}
    for n in tr["nodes"]:
        nid = str(n["id"])
        if not nid or nid in nodes:
            raise AssertionError("duplicate node")
        is_leaf = "factor_id" in n
        is_internal = "left" in n or "right" in n
        if is_leaf == is_internal:
            raise AssertionError("node kind")
        if is_leaf:
            nodes[nid] = {"id": nid, "kind": "leaf", "factor_id": str(n["factor_id"])}
        else:
            if "left" not in n or "right" not in n or str(n["left"]) == str(n["right"]):
                raise AssertionError("bad children")
            nodes[nid] = {"id": nid, "kind": "internal", "left": str(n["left"]), "right": str(n["right"])}
    if root not in nodes:
        raise AssertionError("root")
    mark, post, leaves = {}, [], []
    def dfs(nid):
        if nid not in nodes or mark.get(nid) == 1:
            raise AssertionError("tree cycle/missing")
        if mark.get(nid) == 2:
            raise AssertionError("multiple parent")
        mark[nid] = 1
        n = nodes[nid]
        if n["kind"] == "leaf":
            if n["factor_id"] not in fac:
                raise AssertionError("unknown factor")
            leaves.append(n["factor_id"])
        else:
            dfs(n["left"]); dfs(n["right"])
        mark[nid] = 2; post.append(nid)
    dfs(root)
    if len(mark) != len(nodes) or sorted(leaves) != sorted(fac) or len(leaves) != len(set(leaves)):
        raise AssertionError("coverage")
    caps = {"max_boundary_dim": max(0, min(d, 3)), "max_k": max(k, 1), "max_full_set_entries": 10000, "max_child_pairs": 200000, "max_join_paths": 2000000}
    caps.update(raw.get("caps", {})); caps = {x: int(v) for x, v in caps.items()}
    if any(v < 0 for v in caps.values()): raise AssertionError("negative cap")
    return d, k, fac, nodes, root, post, caps


def geometry(d, fac, nodes, post):
    covers, V = {}, {}
    for nid in post:
        n = nodes[nid]
        ids = (n["factor_id"],) if n["kind"] == "leaf" else tuple(sorted((*covers[n["left"]], *covers[n["right"]])))
        covers[nid] = ids
        V[nid] = xor_basis([x for fid in ids for x in fac[fid]["normal_space"]], d)
    allids = set(fac); B = {}
    for nid in post:
        outside = sorted(allids - set(covers[nid]))
        vo = xor_basis([x for fid in outside for x in fac[fid]["normal_space"]], d)
        B[nid] = subspace_intersection(V[nid], vo, d)
    return covers, V, B


def cp(Vl, Vr, Bl, Br, Bv, Bp, d):
    li = subspace_intersection(Vl, Bp, d); ri = subspace_intersection(Vr, Bp, d)
    sep = subspace_intersection(subspace_sum(Vl, Bp, d), subspace_sum(Vr, Bp, d), d)
    checks = {
        "B_left_le_Bprime": subset(Bl, Bp),
        "span_left_inter_Bprime_le_B_left": subset(li, Bl),
        "B_right_le_Bprime": subset(Br, Bp),
        "span_right_inter_Bprime_le_B_right": subset(ri, Br),
        "join_separation_equals_Bprime": tuple(sep) == tuple(xor_basis(Bp, d)),
        "B_parent_le_Bprime": subset(Bv, Bp),
    }
    return checks, li, ri, sep


def trajectories(entries, B, d):
    return [decode_trajectory(e["trajectory"], B, d, require_compact=True) for e in entries]


def replay(raw, candidate):
    d, k, fac, nodes, root, post, caps = parse_input(raw)
    covers, V, B = geometry(d, fac, nodes, post)
    if B[root] != (): raise AssertionError("root boundary")
    cand_nodes = {n["node_id"]: n for n in candidate["proof_payload"]["node_receipts"]}
    entries = {}; completed = []
    expected_open = None
    for nid in post:
        n = nodes[nid]
        if n["kind"] == "leaf":
            delta = (Statistic((), B[nid], 0), Statistic(B[nid], (), 0))
            r, err = independent_upk([delta], B[nid], d, k, caps, f"{nid}:leaf_up_k")
            if err:
                expected_open = (nid, err); break
            e = normalize_entries(r); entries[nid] = e
            if nid not in cand_nodes: raise AssertionError("missing leaf receipt")
            c = cand_nodes[nid]
            if c["kind"] != "leaf" or c["covered_factor_ids"] != list(covers[nid]) or c["V_v_rref"] != list(V[nid]) or c["B_v_rref"] != list(B[nid]): raise AssertionError("leaf geometry")
            if c["factor_identity_records"] != [{"factor_id": fid, "affine_offset": fac[fid]["affine_offset"]} for fid in covers[nid]]: raise AssertionError("leaf identity")
            if c["delta_B"] != encode_trajectory(delta) or c["output_entry_count"] != len(e) or c["output_full_set_digest"] != entry_digest(e): raise AssertionError("leaf output")
            completed.append(nid); continue
        l, rgt = n["left"], n["right"]
        Bp = subspace_sum(B[l], B[rgt], d)
        checks, li, ri, sep = cp(V[l], V[rgt], B[l], B[rgt], B[nid], Bp, d)
        if not all(checks.values()): raise AssertionError("caller premise")
        lg, rg = trajectories(entries[l], B[l], d), trajectories(entries[rgt], B[rgt], d)
        lexp = [expand_trajectory(g, B[l], Bp, d)[0] for g in lg]
        rexp = [expand_trajectory(g, B[rgt], Bp, d)[0] for g in rg]
        lu, err = independent_upk(lexp, Bp, d, k, caps, f"{nid}:expand_left_up_k")
        if err: expected_open = (nid, err); break
        ru, err = independent_upk(rexp, Bp, d, k, caps, f"{nid}:expand_right_up_k")
        if err: expected_open = (nid, err); break
        le, re = normalize_entries(lu), normalize_entries(ru)
        pairs = len(le) * len(re)
        if pairs > caps["max_child_pairs"]:
            expected_open = (nid, ("CHILD_PAIR_CAP", pairs, caps["max_child_pairs"], f"{nid}:join_precheck")); break
        lgs, rgs = trajectories(le, Bp, d), trajectories(re, Bp, d)
        paths = sum(math.comb((len(a)-1)+(len(b)-1), len(a)-1) for a in lgs for b in rgs)
        if paths > caps["max_join_paths"]:
            expected_open = (nid, ("JOIN_PATH_CAP", paths, caps["max_join_paths"], f"{nid}:join_precheck")); break
        good=[]; enumerated=0
        for a in lgs:
            for b in rgs:
                for path in ordinary_join_paths(len(a), len(b)):
                    j,_=join_trajectory(a,b,path,Bp,d); enumerated += 1
                    if width(j) <= k: good.append(j)
        if enumerated != paths: raise AssertionError("path enumeration")
        ju, err = independent_upk(good, Bp, d, k, caps, f"{nid}:joined_up_k")
        if err: expected_open = (nid, err); break
        je=normalize_entries(ju)
        shr=[shrink_trajectory(g,B[nid],d)[0] for g in trajectories(je,Bp,d)]
        fu, err=independent_upk(shr,B[nid],d,k,caps,f"{nid}:final_up_k")
        if err: expected_open=(nid,err); break
        fe=normalize_entries(fu); entries[nid]=fe
        if nid not in cand_nodes: raise AssertionError("missing internal receipt")
        c=cand_nodes[nid]
        if c["kind"]!="internal" or c["covered_factor_ids"]!=list(covers[nid]) or c["V_v_rref"]!=list(V[nid]) or c["B_v_rref"]!=list(B[nid]) or c["Bprime_v_rref_if_internal"]!=list(Bp): raise AssertionError("internal geometry")
        if c["factor_identity_records"] != [{"factor_id": fid, "affine_offset": fac[fid]["affine_offset"]} for fid in covers[nid]]: raise AssertionError("internal identity")
        cert=c["caller_premise_certificate_if_internal"]
        if cert["checks"]!=checks or cert["left_intersection"]!=list(li) or cert["right_intersection"]!=list(ri) or cert["join_separation"]!=list(sep) or cert["all_pass"] is not True: raise AssertionError("caller certificate")
        if c["child_output_digests"]!={"left":entry_digest(entries[l]),"right":entry_digest(entries[rgt])}: raise AssertionError("child handoff")
        if c["expanded_left_receipt_if_internal"]["output_entry_count"]!=len(le) or c["expanded_left_receipt_if_internal"]["output_full_set_digest"]!=entry_digest(le): raise AssertionError("left expand")
        if c["expanded_right_receipt_if_internal"]["output_entry_count"]!=len(re) or c["expanded_right_receipt_if_internal"]["output_full_set_digest"]!=entry_digest(re): raise AssertionError("right expand")
        ji=c["ordinary_join_inventory_if_internal"]
        if ji["child_pair_count"]!=pairs or ji["ordinary_hv_path_count"]!=paths or ji["successful_width_le_k_generators"]!=len(good) or ji["failed_width_gt_k_generators"]!=paths-len(good) or ji["diagonal_ordinary_join_steps"]!=0: raise AssertionError("join inventory")
        if c["joined_up_k_receipt_if_internal"]["output_full_set_digest"]!=entry_digest(je): raise AssertionError("joined upk")
        if c["shrink_inventory_if_internal"]["input_count"]!=len(je) or c["shrink_inventory_if_internal"]["output_generator_count"]!=len(shr): raise AssertionError("shrink inventory")
        if c["output_entry_count"]!=len(fe) or c["output_full_set_digest"]!=entry_digest(fe) or c["final_up_k_receipt"]["output_full_set_digest"]!=entry_digest(fe): raise AssertionError("final output")
        completed.append(nid)
    return d,k,fac,nodes,root,post,covers,V,B,entries,completed,expected_open


def verify(candidate, raw, spec):
    if spec.get("schema") != SPEC_SCHEMA: raise AssertionError("spec")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload" or dg(candidate.get("proof_payload")) != candidate.get("semantic_digest"): raise AssertionError("candidate digest")
    p=candidate["proof_payload"]
    d,k,fac,nodes,root,post,covers,V,B,entries,completed,expected_open=replay(raw,candidate)
    canonical_factors=[fac[x] for x in sorted(fac)]
    canonical_tree={"root":root,"nodes":[nodes[x] for x in sorted(nodes)]}
    if p["ambient_dim"]!=d or p["k"]!=k or p["canonical_factor_catalog"]!=canonical_factors or p["canonical_tree"]!=canonical_tree or p["root_id"]!=root or p["postorder"]!=post: raise AssertionError("global identity")
    if p["ordinary_join_steps"] != [list(x) for x in JOIN_INTERLEAVING_STEPS] or p["extension_preorder_steps"] != [list(x) for x in EXTENSION_PREORDER_STEPS]: raise AssertionError("path domains")
    if p["affine_offset_identity_ledger"] != [{"factor_id":x,"affine_offset":fac[x]["affine_offset"]} for x in sorted(fac)]: raise AssertionError("affine ledger")
    if any(v is not None for v in p["acceptance_oracles"].values()): raise AssertionError("fixture oracle")
    if p["terminal_promotion"]!="NONE": raise AssertionError("terminal promotion")
    b=p["strict_boundary"]
    if b["found_layout"]!="FORBIDDEN" or b["no_layout_at_cap"]!="FORBIDDEN" or b["polynomial_runtime_claim"]!="FORBIDDEN" or b["b5_complete"] is not False or b["p_vs_np"]!="OPEN": raise AssertionError("boundary")
    receipt_ids=[x["node_id"] for x in p["node_receipts"]]
    if receipt_ids != sorted(receipt_ids) or set(receipt_ids) != set(completed): raise AssertionError("atomic node commit")
    if expected_open is None:
        if p["capability_status"]!=CLOSED or p["stop_node"] is not None or p["open_reason"] is not None: raise AssertionError("closed status")
        if p["root_full_set_digest_if_closed"]!=entry_digest(entries[root]) or p["root_entry_count_if_closed"]!=len(entries[root]): raise AssertionError("root output")
        if b["generic_runtime_trace_mapping_candidate"] is not True: raise AssertionError("closed candidate")
    else:
        nid,err=expected_open
        if p["capability_status"]!=OPEN or p["stop_node"]!=nid or p["root_full_set_digest_if_closed"] is not None or p["root_entry_count_if_closed"] is not None or b["generic_runtime_trace_mapping_candidate"] is not False: raise AssertionError("open status")
        r=p["open_reason"]
        if r["reason"]!=err[0] or r["observed"]!=err[1] or r["cap"]!=err[2] or r["stage"]!=err[3]: raise AssertionError("open reason")
    return expected_open is None


def repair(c):
    c["semantic_digest"]=dg(c["proof_payload"]); return c


def tamper_suite(base, raw, spec):
    attacks=[]
    def add(name,fn):
        c=copy.deepcopy(base); fn(c["proof_payload"]); attacks.append((name,repair(c)))
    add("T01_DUP_FACTOR_LEAF",lambda p:p["canonical_tree"]["nodes"].append(copy.deepcopy(p["canonical_tree"]["nodes"][0])))
    add("T02_OMIT_FACTOR",lambda p:p["canonical_factor_catalog"].pop())
    add("T03_NORMAL_SPACE",lambda p:p["canonical_factor_catalog"][0].__setitem__("normal_space",[]))
    add("T04_AFFINE_OFFSET",lambda p:p["affine_offset_identity_ledger"][0].__setitem__("affine_offset",{"tampered":True}))
    def node_mut(p,key,value):
        if not p["node_receipts"]: raise AssertionError("no node")
        p["node_receipts"][0][key]=value
    add("T05_BOUNDARY",lambda p:node_mut(p,"B_v_rref",[1]))
    def mutate_bp(p):
        for n in p["node_receipts"]:
            if n["kind"]=="internal": n["Bprime_v_rref_if_internal"]=[1]; return
        p["root_id"]="tamper"
    add("T06_BPRIME",mutate_bp)
    def mutate_cp(p):
        for n in p["node_receipts"]:
            if n["kind"]=="internal": n["caller_premise_certificate_if_internal"]["all_pass"]=False; return
        p["root_id"]="tamper"
    add("T07_CALLER",mutate_cp)
    add("T08_DIAGONAL_JOIN",lambda p:p.__setitem__("ordinary_join_steps",[[1,0],[0,1],[1,1]]))
    def drop_expand(p):
        for n in p["node_receipts"]:
            if n["kind"]=="internal": n["expanded_left_receipt_if_internal"]["output_entry_count"] += 1; return
        p["root_id"]="tamper"
    add("T09_DROP_CHILD_ENTRY",drop_expand)
    def drop_path(p):
        for n in p["node_receipts"]:
            if n["kind"]=="internal": n["ordinary_join_inventory_if_internal"]["ordinary_hv_path_count"] -= 1; return
        p["root_id"]="tamper"
    add("T10_DROP_JOIN_PATH",drop_path)
    def width_filter(p):
        for n in p["node_receipts"]:
            if n["kind"]=="internal": n["ordinary_join_inventory_if_internal"]["successful_width_le_k_generators"] += 1; return
        p["root_id"]="tamper"
    add("T11_WIDTH_FILTER",width_filter)
    def shrink(p):
        for n in p["node_receipts"]:
            if n["kind"]=="internal": n["shrink_inventory_if_internal"]["output_generator_count"] += 1; return
        p["root_id"]="tamper"
    add("T12_SHRINK",shrink)
    add("T13_FINAL_UPK",lambda p:node_mut(p,"output_full_set_digest","0"*64))
    add("T14_CLOSED_AFTER_CAP",lambda p:p.__setitem__("capability_status",CLOSED if p["capability_status"]==OPEN else OPEN))
    add("T15_FOUND",lambda p:p["strict_boundary"].__setitem__("found_layout","TRUE"))
    add("T16_NO_LAYOUT",lambda p:p["strict_boundary"].__setitem__("no_layout_at_cap","TRUE"))
    add("T17_FIXTURE_ORACLE",lambda p:p["acceptance_oracles"].__setitem__("fixed_factor_count",6))
    add("T18_GLOBAL_PROMOTION",lambda p:p["strict_boundary"].update({"polynomial_runtime_claim":"TRUE","b5_complete":True,"p_vs_np":"CLOSED"}))
    rejected=0
    for name,c in attacks:
        try: verify(c,raw,spec)
        except Exception: rejected += 1; continue
        raise AssertionError(name+" survived")
    return rejected,len(attacks)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--spec",type=Path,required=True); p.add_argument("--input",type=Path,required=True); p.add_argument("--candidate",type=Path,required=True); p.add_argument("--tamper-suite",action="store_true")
    a=p.parse_args(); spec=load(a.spec); raw=load(a.input); c=load(a.candidate)
    closed=verify(c,raw,spec)
    print("JANUS_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR_INDEPENDENT_VERIFIER = PASS")
    print("RUNTIME_RESULT =", CLOSED if closed else OPEN)
    print("ORDINARY_JOIN_DOMAIN = H/V_ONLY")
    print("EXTENSION_PREORDER_DOMAIN = H/V/DIAGONAL")
    print("TREE_BOUNDARY_REPLAY = PASS")
    print("NODE_OUTPUT_DIGEST_REPLAY = PASS")
    print("AFFINE_OFFSET_IDENTITY = PASS")
    print("TERMINAL_PROMOTION = NONE")
    print("GENERIC_FOUND_LAYOUT = FORBIDDEN")
    print("GENERIC_NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("POLYNOMIAL_RUNTIME_CLAIM = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    if a.tamper_suite:
        r,t=tamper_suite(c,raw,spec); print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}")

if __name__=="__main__": main()
