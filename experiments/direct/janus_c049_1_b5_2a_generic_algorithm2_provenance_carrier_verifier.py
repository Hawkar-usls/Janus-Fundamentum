from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

from janus_c049_1_b2_up_k_core import extension_witness, up_k
from janus_c049_1_b3_expand_join_shrink_core import (
    Statistic,
    contains,
    decode_trajectory,
    encode_trajectory,
    expand_trajectory,
    shrink_trajectory,
    subspace_intersection,
    subspace_sum,
    width,
    xor_basis,
)
from janus_c049_1_b3_join_path_domain_corrected import join_trajectory

SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier.v1"
SPEC_SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier_spec.v1"
B5_1_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"
HVD = {(1, 0), (0, 1), (1, 1)}
HV = {(1, 0), (0, 1)}


def cb(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(x: Any) -> str:
    return hashlib.sha256(cb(x)).hexdigest()


def load(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def entries_digest(entries: Sequence[dict]) -> str:
    return dg(sorted(dg(e["trajectory"]) for e in entries))


def normalize_entries(receipt: dict) -> list[dict]:
    out = [{"trajectory": e["trajectory"], "source_index": int(e["source_index"]), "witness": e["witness"]} for e in receipt.get("entries", [])]
    return sorted(out, key=lambda e: (dg(e["trajectory"]), e["source_index"], dg(e["witness"])))


def parse_input(raw: dict):
    d, k = int(raw["ambient_dim"]), int(raw["k"])
    if d <= 0 or k < 0:
        raise AssertionError("bad d/k")
    factors = {}
    for f in raw.get("factors", []):
        fid = str(f["id"])
        if not fid or fid in factors:
            raise AssertionError("factor id")
        factors[fid] = {"id": fid, "normal_space": list(xor_basis(f.get("normal_space", []), d)), "affine_offset": f.get("affine_offset")}
    if not factors:
        raise AssertionError("empty factors")
    tr = raw["tree"]
    root = str(tr["root"])
    nodes = {}
    for n in tr["nodes"]:
        nid = str(n["id"])
        if not nid or nid in nodes:
            raise AssertionError("node id")
        leaf = "factor_id" in n
        internal = "left" in n or "right" in n
        if leaf == internal:
            raise AssertionError("node kind")
        if leaf:
            nodes[nid] = {"id": nid, "kind": "leaf", "factor_id": str(n["factor_id"])}
        else:
            if "left" not in n or "right" not in n or str(n["left"]) == str(n["right"]):
                raise AssertionError("children")
            nodes[nid] = {"id": nid, "kind": "internal", "left": str(n["left"]), "right": str(n["right"])}
    if root not in nodes:
        raise AssertionError("root")
    mark, post, leaves = {}, [], []
    def dfs(nid):
        if nid not in nodes or mark.get(nid) == 1:
            raise AssertionError("cycle/missing")
        if mark.get(nid) == 2:
            raise AssertionError("multiple parent")
        mark[nid] = 1
        n = nodes[nid]
        if n["kind"] == "leaf":
            if n["factor_id"] not in factors:
                raise AssertionError("unknown factor")
            leaves.append(n["factor_id"])
        else:
            dfs(n["left"]); dfs(n["right"])
        mark[nid] = 2; post.append(nid)
    dfs(root)
    if len(mark) != len(nodes) or sorted(leaves) != sorted(factors) or len(leaves) != len(set(leaves)):
        raise AssertionError("coverage")
    caps = {"max_boundary_dim": max(0, min(d, 3)), "max_k": max(k, 1), "max_full_set_entries": 10000, "max_child_pairs": 200000, "max_join_paths": 2000000}
    caps.update(raw.get("caps", {})); caps = {x: int(v) for x, v in caps.items()}
    return d, k, factors, nodes, root, post, caps


def geometry(d, factors, nodes, post):
    covers, V = {}, {}
    for nid in post:
        n = nodes[nid]
        ids = (n["factor_id"],) if n["kind"] == "leaf" else tuple(sorted((*covers[n["left"]], *covers[n["right"]])))
        covers[nid] = ids
        V[nid] = xor_basis([x for fid in ids for x in factors[fid]["normal_space"]], d)
    allids = set(factors); B = {}
    for nid in post:
        outside = sorted(allids - set(covers[nid]))
        vo = xor_basis([x for fid in outside for x in factors[fid]["normal_space"]], d)
        B[nid] = subspace_intersection(V[nid], vo, d)
    return covers, V, B


def subset(a, b): return contains(tuple(b), tuple(a))


def caller(Vl, Vr, Bl, Br, Bv, Bp, d):
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
    return {"checks": checks, "left_intersection": list(li), "right_intersection": list(ri), "join_separation": list(sep), "all_pass": all(checks.values())}


def expected_up_label(entry: dict, lower, upper) -> dict:
    witness = extension_witness(lower, upper)
    if witness is None or witness != entry["extension_witness"]:
        raise AssertionError("extension witness")
    native, one, slack, selected = [], [], [], []
    prev = None
    for idx, pt in enumerate(witness["path"]):
        li, ui = int(pt["lower_index"]), int(pt["upper_index"])
        s = int(pt["upper"]["lambda"]) - int(pt["lower"]["lambda"])
        if s < 0:
            raise AssertionError("negative slack")
        native.append([li, ui]); one.append([li + 1, ui + 1]); slack.append(s)
        if s == 0 and (idx == 0 or li != prev): selected.append(li)
        prev = li
    return {"native_zero_based_path": native, "paper_one_based_path": one, "slack_sequence": slack, "zero_slack_child_positions_zero_based": selected, "source_index": int(entry["source_index"]), "witness_digest": dg(witness)}


def validate_carrier_entries(c_entries, generators, boundary, d, k):
    if not generators:
        expected = []
    else:
        r = up_k(generators, boundary, d, k)
        expected = normalize_entries(r)
    if len(c_entries) != len(expected):
        raise AssertionError("carrier up_k count")
    for i, (c, e) in enumerate(zip(c_entries, expected)):
        if c["entry_index"] != i or c["trajectory"] != e["trajectory"] or c["trajectory_digest"] != dg(e["trajectory"]) or c["source_index"] != e["source_index"] or c["extension_witness"] != e["witness"]:
            raise AssertionError("carrier up_k entry")
        if not (0 <= e["source_index"] < len(generators)):
            raise AssertionError("source index")
        target = decode_trajectory(e["trajectory"], boundary, d, require_compact=True)
        label = expected_up_label(c, generators[e["source_index"]], target)
        if c["algorithm2_up_label"] != label:
            raise AssertionError("algorithm2 up label")
    return expected


def verify(candidate, raw, subject, spec):
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_NO_FOUND_LAYOUT_PROMOTION": raise AssertionError("spec")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload" or dg(candidate.get("proof_payload")) != candidate.get("semantic_digest"): raise AssertionError("candidate")
    if subject.get("schema") != B5_1_SCHEMA or subject.get("semantic_digest_scope") != "proof_payload" or dg(subject.get("proof_payload")) != subject.get("semantic_digest"): raise AssertionError("subject")
    sp = subject["proof_payload"]
    if sp["capability_status"] != "CLOSED_COMPLETE_TRACE" or sp["terminal_promotion"] != "NONE": raise AssertionError("subject scope")

    d, k, factors, nodes, root, post, caps = parse_input(raw)
    covers, V, B = geometry(d, factors, nodes, post)
    canonical_factors = [factors[x] for x in sorted(factors)]
    canonical_tree = {"root": root, "nodes": [nodes[x] for x in sorted(nodes)]}
    if sp["canonical_factor_catalog"] != canonical_factors or sp["canonical_tree"] != canonical_tree or sp["root_id"] != root or sp["postorder"] != post:
        raise AssertionError("subject/input identity")
    p = candidate["proof_payload"]
    if p["subject"] != {"b5_1_semantic_digest": subject["semantic_digest"], "b5_1_root_full_set_digest": sp["root_full_set_digest_if_closed"], "b5_1_root_entry_count": sp["root_entry_count_if_closed"]}: raise AssertionError("subject binding")
    if p["ambient_dim"] != d or p["k"] != k or p["canonical_factor_catalog"] != canonical_factors or p["canonical_tree"] != canonical_tree or p["root_id"] != root or p["postorder"] != post: raise AssertionError("candidate/input identity")

    cnodes = {n["node_id"]: n for n in p["node_carriers"]}
    snodes = {n["node_id"]: n for n in sp["node_receipts"]}
    if set(cnodes) != set(nodes) or set(snodes) != set(nodes): raise AssertionError("node sets")
    node_entries = {}
    for nid in post:
        n, c, s = nodes[nid], cnodes[nid], snodes[nid]
        if c["kind"] != n["kind"] or c["covered_factor_ids"] != list(covers[nid]) or c["B_v_rref"] != list(B[nid]): raise AssertionError("carrier node geometry")
        if n["kind"] == "leaf":
            delta = (Statistic((), B[nid], 0), Statistic(B[nid], (), 0))
            if c["leaf_factor_id"] != n["factor_id"] or c["delta_generators"] != [{"generator_index": 0, "trajectory": encode_trajectory(delta)}]: raise AssertionError("leaf delta")
            expected = validate_carrier_entries(c["final_entries"], [delta], B[nid], d, k)
        else:
            left, right = n["left"], n["right"]
            if c["left_child_id"] != left or c["right_child_id"] != right: raise AssertionError("child ids")
            Bp = subspace_sum(B[left], B[right], d)
            if c["Bprime_v_rref"] != list(Bp) or c["caller_premise_certificate"] != caller(V[left], V[right], B[left], B[right], B[nid], Bp, d): raise AssertionError("caller")

            left_child = [decode_trajectory(e["trajectory"], B[left], d, require_compact=True) for e in node_entries[left]]
            right_child = [decode_trajectory(e["trajectory"], B[right], d, require_compact=True) for e in node_entries[right]]
            if len(c["left_transport_generators"]) != len(left_child) or len(c["right_transport_generators"]) != len(right_child): raise AssertionError("transport count")
            left_generators=[]
            for i,(rec,g) in enumerate(zip(c["left_transport_generators"],left_child)):
                out, rr = expand_trajectory(g,B[left],Bp,d)
                if rec != {"generator_index":i,"child_output_entry_index":i,"child_trajectory":encode_trajectory(g),"transported_generator":encode_trajectory(out),"expand_receipt":rr}: raise AssertionError("left transport")
                left_generators.append(out)
            right_generators=[]
            for i,(rec,g) in enumerate(zip(c["right_transport_generators"],right_child)):
                out, rr = expand_trajectory(g,B[right],Bp,d)
                if rec != {"generator_index":i,"child_output_entry_index":i,"child_trajectory":encode_trajectory(g),"transported_generator":encode_trajectory(out),"expand_receipt":rr}: raise AssertionError("right transport")
                right_generators.append(out)
            left_entries=validate_carrier_entries(c["left_expanded_entries"],left_generators,Bp,d,k)
            right_entries=validate_carrier_entries(c["right_expanded_entries"],right_generators,Bp,d,k)
            left_g=[decode_trajectory(e["trajectory"],Bp,d,require_compact=True) for e in left_entries]
            right_g=[decode_trajectory(e["trajectory"],Bp,d,require_compact=True) for e in right_entries]

            successful=[]; successful_g=[]
            for li,g1 in enumerate(left_g):
                for ri,g2 in enumerate(right_g):
                    from janus_c049_1_b3_join_path_domain_corrected import ordinary_join_paths
                    for path in ordinary_join_paths(len(g1),len(g2)):
                        joined,jr=join_trajectory(g1,g2,path,Bp,d)
                        if width(joined)<=k:
                            idx=len(successful)
                            successful_g.append(joined)
                            successful.append({"generator_index":idx,"left_expanded_entry_index":li,"right_expanded_entry_index":ri,"path":[list(x) for x in path],"joined_generator":encode_trajectory(joined),"join_receipt":jr})
            if c["successful_join_generators"] != successful: raise AssertionError("join generator catalog")
            joined_entries=validate_carrier_entries(c["joined_entries"],successful_g,Bp,d,k)
            joined_g=[decode_trajectory(e["trajectory"],Bp,d,require_compact=True) for e in joined_entries]
            shr=[]; shrink_records=[]
            for ji,g in enumerate(joined_g):
                out,sr=shrink_trajectory(g,B[nid],d); idx=len(shrink_records); shr.append(out)
                shrink_records.append({"generator_index":idx,"joined_entry_index":ji,"joined_full_set_trajectory":encode_trajectory(g),"shrunk_generator":encode_trajectory(out),"shrink_receipt":sr})
            if c["shrink_generators"] != shrink_records: raise AssertionError("shrink catalog")
            expected=validate_carrier_entries(c["final_entries"],shr,B[nid],d,k)
        node_entries[nid]=expected
        if c["b5_1_projection"] != {"output_entry_count":len(expected),"output_full_set_digest":entries_digest(expected)}: raise AssertionError("carrier projection")
        if s["output_entry_count"] != len(expected) or s["output_full_set_digest"] != entries_digest(expected): raise AssertionError("B5.1 projection")

    if p["semantic_projection"] != {"node_count":len(nodes),"node_digest_count_matches":len(nodes),"node_entry_count_matches":len(nodes),"root_full_set_digest_unchanged":True,"root_entry_count_unchanged":True,"new_semantic_entries_added":0}: raise AssertionError("projection summary")
    if entries_digest(node_entries[root]) != sp["root_full_set_digest_if_closed"] or len(node_entries[root]) != sp["root_entry_count_if_closed"]: raise AssertionError("root projection")

    def reconstruct(nid, ei, seen):
        key=(nid,ei)
        if key in seen: raise AssertionError("cycle")
        seen=set(seen); seen.add(key)
        c=cnodes[nid]; finals=c["final_entries"]
        if not (0<=ei<len(finals)): raise AssertionError("dangling final")
        f=finals[ei]
        if c["kind"]=="leaf":
            if f["source_index"]!=0: raise AssertionError("leaf source")
            return {"node_id":nid,"entry_index":ei,"kind":"leaf","factor_id":c["leaf_factor_id"],"delta_generator_index":0,"up_label_digest":dg(f["algorithm2_up_label"])}
        si=f["source_index"]; shr=c["shrink_generators"]
        if not (0<=si<len(shr)): raise AssertionError("final source")
        ji=shr[si]["joined_entry_index"]; joined=c["joined_entries"]
        if not (0<=ji<len(joined)): raise AssertionError("joined ref")
        je=joined[ji]; jsi=je["source_index"]; joins=c["successful_join_generators"]
        if not (0<=jsi<len(joins)): raise AssertionError("join source")
        jr=joins[jsi]
        li,ri=jr["left_expanded_entry_index"],jr["right_expanded_entry_index"]
        le,re=c["left_expanded_entries"],c["right_expanded_entries"]
        if not (0<=li<len(le) and 0<=ri<len(re)): raise AssertionError("expanded ref")
        ltsi,rtsi=le[li]["source_index"],re[ri]["source_index"]
        lt,rt=c["left_transport_generators"],c["right_transport_generators"]
        if not (0<=ltsi<len(lt) and 0<=rtsi<len(rt)): raise AssertionError("transport ref")
        lcei,rcei=lt[ltsi]["child_output_entry_index"],rt[rtsi]["child_output_entry_index"]
        return {"node_id":nid,"entry_index":ei,"kind":"internal","final_up_label_digest":dg(f["algorithm2_up_label"]),"shrink_generator_index":si,"joined_entry_index":ji,"joined_up_label_digest":dg(je["algorithm2_up_label"]),"successful_join_generator_index":jsi,"join_HV_path":jr["path"],"left_expanded_entry_index":li,"right_expanded_entry_index":ri,"left_expand_up_label_digest":dg(le[li]["algorithm2_up_label"]),"right_expand_up_label_digest":dg(re[ri]["algorithm2_up_label"]),"left_child":reconstruct(c["left_child_id"],lcei,seen),"right_child":reconstruct(c["right_child_id"],rcei,seen)}

    root_back=[reconstruct(root,i,set()) for i in range(len(node_entries[root]))]
    if p["root_entry_backtracks"] != root_back: raise AssertionError("root backtracks")
    if p["backtracking_summary"] != {"root_entries":len(root_back),"root_entries_with_complete_backtrack":len(root_back),"dangling_reference_count":0,"cycle_count":0}: raise AssertionError("backtrack summary")
    if p["algorithm2_boundary"] != {"labels_retained":["leaf_delta","up_path_and_slack","join_HV_path","shrink_relation"],"factor_order_emitted":False,"printorder_correctness_claimed":False,"found_layout":"FORBIDDEN"}: raise AssertionError("Algorithm2 boundary")
    b=p["strict_boundary"]
    expected_b={"generic_algorithm2_backtracking_certificate_candidate":True,"b5_2b_generic_printorder_reconstruction":False,"generic_found_layout_enabled":False,"generic_no_layout_at_cap_enabled":False,"polynomial_runtime_claim":"FORBIDDEN","b5_complete":False,"p_vs_np":"OPEN","formal_admission":"BLOCKED_PENDING_REVIEW"}
    if b != expected_b: raise AssertionError("strict boundary")
    serialized=cb(p)
    for forbidden in (b'"factor_order"',b'"layout_order"',b'"found_layout":true',b'"no_layout_at_cap":true'):
        if forbidden in serialized: raise AssertionError("forbidden output/promotion")
    return len(root_back)


def repair(c): c["semantic_digest"] = dg(c["proof_payload"]); return c


def tamper_suite(base, raw, subject, spec):
    attacks=[]
    def add(name,fn): c=copy.deepcopy(base); fn(c["proof_payload"]); attacks.append((name,repair(c)))
    add("T01_SUBJECT",lambda p:p["subject"].__setitem__("b5_1_root_entry_count",p["subject"]["b5_1_root_entry_count"]+1))
    def first_entry(p,stage="final_entries"):
        for n in p["node_carriers"]:
            if n.get(stage): return n[stage][0]
        raise AssertionError("no entry")
    add("T02_REMOVE_FINAL_CERT",lambda p:next(n for n in p["node_carriers"] if n["final_entries"])["final_entries"].pop())
    add("T03_FINAL_SOURCE",lambda p:first_entry(p).__setitem__("source_index",999))
    add("T04_EXTENSION_PATH",lambda p:first_entry(p)["extension_witness"]["path"][0].__setitem__("upper_index",999))
    add("T05_SLACK",lambda p:first_entry(p)["algorithm2_up_label"]["slack_sequence"].__setitem__(0,999))
    add("T06_ZERO_SLACK",lambda p:first_entry(p)["algorithm2_up_label"].__setitem__("zero_slack_child_positions_zero_based",[999]))
    def internal(p): return next(n for n in p["node_carriers"] if n["kind"]=="internal")
    add("T07_SHRINK_REF",lambda p:internal(p)["shrink_generators"][0].__setitem__("joined_entry_index",999))
    add("T08_SHRINK_OUTPUT",lambda p:internal(p)["shrink_generators"][0].__setitem__("shrunk_generator",[]))
    add("T09_JOINED_SOURCE",lambda p:internal(p)["joined_entries"][0].__setitem__("source_index",999))
    add("T10_JOIN_LEFT",lambda p:internal(p)["successful_join_generators"][0].__setitem__("left_expanded_entry_index",999))
    add("T11_JOIN_RIGHT",lambda p:internal(p)["successful_join_generators"][0].__setitem__("right_expanded_entry_index",999))
    def diag(p):
        r=internal(p)["successful_join_generators"][0]
        path=r["path"]
        if len(path)>1: path[1]=[1,1]
        else: path.append([1,1])
    add("T12_DIAGONAL_JOIN",diag)
    add("T13_JOIN_TRAJECTORY",lambda p:internal(p)["successful_join_generators"][0].__setitem__("joined_generator",[]))
    add("T14_EXPANDED_SOURCE",lambda p:internal(p)["left_expanded_entries"][0].__setitem__("source_index",999))
    add("T15_TRANSPORT_REF",lambda p:internal(p)["left_transport_generators"][0].__setitem__("child_output_entry_index",999))
    add("T16_TRANSPORT_OUTPUT",lambda p:internal(p)["left_transport_generators"][0].__setitem__("transported_generator",[]))
    add("T17_BACKTRACK_CYCLE",lambda p:p["root_entry_backtracks"][0].__setitem__("left_child",copy.deepcopy(p["root_entry_backtracks"][0])))
    add("T18_OMIT_ROOT_ANCESTRY",lambda p:p["root_entry_backtracks"].pop())
    add("T19_AFFINE_IDENTITY",lambda p:p["canonical_factor_catalog"][0].__setitem__("affine_offset",{"tamper":True}))
    add("T20_FACTOR_ORDER",lambda p:p["algorithm2_boundary"].update({"factor_order_emitted":True,"factor_order":["fake"],"found_layout":"TRUE"}))
    add("T21_PROMOTION",lambda p:p["strict_boundary"].update({"generic_no_layout_at_cap_enabled":True,"polynomial_runtime_claim":"TRUE","b5_complete":True,"p_vs_np":"CLOSED"}))
    rejected=0
    for name,c in attacks:
        try: verify(c,raw,subject,spec)
        except Exception: rejected+=1; continue
        raise AssertionError(name+" survived")
    return rejected,len(attacks)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--spec",type=Path,required=True); p.add_argument("--input",type=Path,required=True); p.add_argument("--b5-1-artifact",type=Path,required=True); p.add_argument("--candidate",type=Path,required=True); p.add_argument("--tamper-suite",action="store_true")
    a=p.parse_args(); spec=load(a.spec); raw=load(a.input); subject=load(a.b5_1_artifact); candidate=load(a.candidate)
    roots=verify(candidate,raw,subject,spec)
    print("JANUS_B5_2A_GENERIC_ALGORITHM2_PROVENANCE_CARRIER_INDEPENDENT_VERIFIER = PASS")
    print("ROOT_ENTRIES_WITH_COMPLETE_BACKTRACK =",roots)
    print("DANGLING_REFERENCE_COUNT = 0")
    print("CYCLE_COUNT = 0")
    print("ALGORITHM2_UP_LABELS = PASS")
    print("JOIN_HV_LABELS = PASS")
    print("SEMANTIC_PROJECTION_TO_B5_1 = PASS")
    print("FACTOR_ORDER_EMITTED = FALSE")
    print("FOUND_LAYOUT = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    if a.tamper_suite:
        r,t=tamper_suite(candidate,raw,subject,spec); print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}")

if __name__=="__main__": main()
