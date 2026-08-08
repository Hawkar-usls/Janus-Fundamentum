from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b3_expand_join_shrink_core as b3
import janus_c049_1_b5_2a_generic_algorithm2_provenance_carrier_verifier_v11 as carrier_verifier

SCHEMA = "janus.c049_1.b5_2b.generic_printorder_reconstruction.v1"
SPEC_SCHEMA = "janus.c049_1.b5_2b.generic_printorder_reconstruction_spec.v1"


def cb(x: Any) -> bytes:
    return json.dumps(x, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(x: Any) -> str:
    return hashlib.sha256(cb(x)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalized_source_index(entry: dict) -> int:
    label = entry["algorithm2_up_label"]
    if "b5_1_source_index" in label:
        return int(label["b5_1_source_index"])
    if "source_index" in label:
        return int(label["source_index"])
    raise AssertionError("missing normalized source index")


def original_source_index(entry: dict) -> int:
    if "original_generator_index" in entry:
        return int(entry["original_generator_index"])
    return int(entry["source_index"])


def selected_lower_indices(label: dict, lower_length: int, upper_length: int) -> list[int]:
    path = label["native_zero_based_path"]
    if not isinstance(path, list) or not path:
        raise AssertionError("empty up path")
    buckets = [[] for _ in range(upper_length)]
    prev = None
    for raw in path:
        if not isinstance(raw, list) or len(raw) != 2:
            raise AssertionError("bad up path cell")
        i, j = map(int, raw)
        if not (0 <= i < lower_length and 0 <= j < upper_length):
            raise AssertionError("up path coordinate")
        if prev is not None:
            di, dj = i - prev[0], j - prev[1]
            if (di, dj) not in ((1, 0), (0, 1), (1, 1)):
                raise AssertionError("bad extension path step")
        buckets[j].append(i)
        prev = (i, j)
    if any(not x for x in buckets):
        raise AssertionError("up path skips upper coordinate")
    selected = [0] + [max(buckets[j]) for j in range(1, upper_length)] if upper_length else []
    if not selected or selected[0] != 0 or selected[-1] != lower_length - 1:
        raise AssertionError("up selection endpoints")
    if any(a > b for a, b in zip(selected, selected[1:])):
        raise AssertionError("nonmonotone up selection")
    return selected


def width_receipt(order: Sequence[str], factors: dict[str, dict], d: int) -> dict:
    if len(order) != len(factors) or len(set(order)) != len(order) or set(order) != set(factors):
        raise AssertionError("not a permutation")
    cuts = []
    for i in range(1, len(order)):
        pre = b3.xor_basis([v for fid in order[:i] for v in factors[fid]["normal_space"]], d)
        suf = b3.xor_basis([v for fid in order[i:] for v in factors[fid]["normal_space"]], d)
        inter = b3.subspace_intersection(pre, suf, d)
        cuts.append({"cut_after_position_zero_based": i - 1, "prefix_factor_ids": list(order[:i]), "suffix_factor_ids": list(order[i:]), "prefix_span_rref": list(pre), "suffix_span_rref": list(suf), "intersection_rref": list(inter), "width": len(inter)})
    return {"cut_count": len(cuts), "cuts": cuts, "max_cut_width": max((x["width"] for x in cuts), default=0)}


def reconstruct(carrier: dict, root_entry_index: int) -> tuple[list[str], dict]:
    p = carrier["proof_payload"]
    cnodes = {n["node_id"]: n for n in p["node_carriers"]}
    root = p["root_id"]
    events = []
    zero_boundary_leaf_ids = sorted(n["leaf_factor_id"] for n in cnodes.values() if n["kind"] == "leaf" and n["B_v_rref"] == [])

    def emit_up(entry, lower, rec):
        upper = entry["trajectory"]
        selected = selected_lower_indices(entry["algorithm2_up_label"], len(lower), len(upper))
        out = []
        for i in range(len(upper) - 1):
            for j in range(selected[i], selected[i + 1]):
                out.extend(rec(j))
        return out

    def final(nid, ei, interval):
        n = cnodes[nid]; e = n["final_entries"][ei]
        oi = original_source_index(e)
        events.append({"kind":"up_final","node_id":nid,"entry_index":ei,"interval":interval,"original_generator_index":oi,"normalized_source_index":normalized_source_index(e)})
        if n["kind"] == "leaf":
            if n["B_v_rref"] == []:
                return []
            if interval != 0:
                raise AssertionError("nonzero leaf interval")
            return [n["leaf_factor_id"]]
        sr = n["shrink_generators"][oi]
        return emit_up(e, sr["shrunk_generator"], lambda j: shrink(nid, oi, j))

    def shrink(nid, si, interval):
        n=cnodes[nid]; sr=n["shrink_generators"][si]; ji=int(sr["joined_entry_index"])
        events.append({"kind":"shrink","node_id":nid,"shrink_generator_index":si,"joined_entry_index":ji,"interval":interval})
        return joined_up(nid,ji,interval)

    def joined_up(nid,ei,interval):
        n=cnodes[nid]; e=n["joined_entries"][ei]; oi=original_source_index(e); jr=n["successful_join_generators"][oi]
        events.append({"kind":"up_joined","node_id":nid,"entry_index":ei,"interval":interval,"successful_join_generator_index":oi,"normalized_source_index":normalized_source_index(e)})
        return emit_up(e,jr["joined_generator"],lambda j: join(nid,oi,j))

    def join(nid,ji,interval):
        n=cnodes[nid]; jr=n["successful_join_generators"][ji]; path=[tuple(map(int,x)) for x in jr["path"]]
        if not (0 <= interval < len(path)-1): raise AssertionError("join interval")
        (li,ri),(li2,ri2)=path[interval],path[interval+1]; step=(li2-li,ri2-ri)
        events.append({"kind":"join","node_id":nid,"successful_join_generator_index":ji,"interval":interval,"path_point":[li,ri],"step":list(step)})
        if step==(1,0): return expanded(nid,"left",int(jr["left_expanded_entry_index"]),li)
        if step==(0,1): return expanded(nid,"right",int(jr["right_expanded_entry_index"]),ri)
        raise AssertionError("diagonal/nonordinary join step")

    def expanded(nid,side,ei,interval):
        n=cnodes[nid]; e=n[side+"_expanded_entries"][ei]; oi=original_source_index(e); tr=n[side+"_transport_generators"][oi]
        events.append({"kind":"up_expand","node_id":nid,"side":side,"entry_index":ei,"interval":interval,"transport_generator_index":oi,"normalized_source_index":normalized_source_index(e)})
        return emit_up(e,tr["transported_generator"],lambda j: transport(nid,side,oi,j))

    def transport(nid,side,ti,interval):
        n=cnodes[nid]; tr=n[side+"_transport_generators"][ti]; child=n[side+"_child_id"]; cei=int(tr["child_output_entry_index"])
        events.append({"kind":"transport","node_id":nid,"side":side,"transport_generator_index":ti,"child_id":child,"child_entry_index":cei,"interval":interval})
        return final(child,cei,interval)

    order=list(zero_boundary_leaf_ids)
    root_entry=cnodes[root]["final_entries"][root_entry_index]
    for i in range(len(root_entry["trajectory"])-1): order.extend(final(root,root_entry_index,i))
    return order,{"zero_boundary_leaf_prefix":zero_boundary_leaf_ids,"event_count":len(events),"events":events}


def verify(candidate: dict, raw: dict, b5_1: dict, carrier: dict, spec: dict, carrier_spec: dict) -> int:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_REVIEW_ONLY_FOUND_LAYOUT_CEILING": raise AssertionError("spec")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload" or dg(candidate.get("proof_payload")) != candidate.get("semantic_digest"): raise AssertionError("candidate digest")
    carrier_verifier.verify(carrier,raw,b5_1,carrier_spec)
    cp=carrier["proof_payload"]; p=candidate["proof_payload"]
    if p["subject"] != {"b5_2a_semantic_digest":carrier["semantic_digest"],"b5_1_semantic_digest":b5_1["semantic_digest"],"root_entry_count":cp["backtracking_summary"]["root_entries"]}: raise AssertionError("subject")
    if p["ambient_dim"] != cp["ambient_dim"] or p["k"] != cp["k"] or p["canonical_factor_catalog"] != cp["canonical_factor_catalog"] or p["canonical_tree"] != cp["canonical_tree"] or p["root_id"] != cp["root_id"]: raise AssertionError("identity")
    factors={f["id"]:f for f in cp["canonical_factor_catalog"]}; d=int(cp["ambient_dim"]); k=int(cp["k"]); roots=int(cp["backtracking_summary"]["root_entries"])
    if len(p["layouts"]) != roots: raise AssertionError("layout count")
    for idx,lay in enumerate(p["layouts"]):
        if lay["root_entry_index"] != idx: raise AssertionError("root entry index")
        order,tr = reconstruct(carrier,idx)
        if lay["factor_order"] != order or lay["factor_order_digest"] != dg(order) or lay["printorder_trace"] != tr: raise AssertionError("printorder reconstruction")
        wr=width_receipt(order,factors,d)
        if lay["width_receipt"] != wr or lay["within_width_cap"] is not True or wr["max_cut_width"] > k: raise AssertionError("cut width")
        for fid in order:
            if fid not in factors: raise AssertionError("unknown factor")
    expected_summary={"root_entries":roots,"layouts_emitted":roots,"all_orders_exact_factor_permutations":True if roots else True,"all_layouts_within_width_cap":True,"max_emitted_cut_width":max((x["width_receipt"]["max_cut_width"] for x in p["layouts"]),default=None)}
    if p["summary"] != expected_summary: raise AssertionError("summary")
    expected_boundary={"b5_2a_admitted_subject_verified":True,"generic_printorder_reconstruction_candidate":True,"factor_order_emitted":roots>0,"generic_found_layout_candidate":roots>0,"generic_found_layout_admitted":False,"generic_no_layout_at_cap":"FORBIDDEN","all_input_termination":"NOT_ESTABLISHED","polynomial_runtime":"NOT_ESTABLISHED","b5_complete":False,"p_vs_np":"OPEN","formal_admission":"BLOCKED_PENDING_REVIEW"}
    if p["strict_boundary"] != expected_boundary: raise AssertionError("boundary")
    return roots


def repair(c): c["semantic_digest"]=dg(c["proof_payload"]); return c


def tamper_suite(base,raw,b5_1,carrier,spec,carrier_spec):
    attacks=[]
    def add(name,fn): c=copy.deepcopy(base); fn(c["proof_payload"]); attacks.append((name,repair(c)))
    add("T01_SUBJECT",lambda p:p["subject"].__setitem__("b5_2a_semantic_digest","0"*64))
    if base["proof_payload"]["layouts"]:
        add("T02_ROOT_INDEX",lambda p:p["layouts"][0].__setitem__("root_entry_index",999))
        add("T03_OMIT_FACTOR",lambda p:p["layouts"][0]["factor_order"].pop())
        add("T04_DUP_FACTOR",lambda p:p["layouts"][0]["factor_order"].append(p["layouts"][0]["factor_order"][0]))
        def swap(p):
            o=p["layouts"][0]["factor_order"]
            if len(o)>1: o[0],o[1]=o[1],o[0]
            else: o[0]="tamper"
        add("T05_SWAP",swap)
        def upseq(p):
            ev=next(e for e in p["layouts"][0]["printorder_trace"]["events"] if e["kind"].startswith("up_")); ev["interval"]=999
        add("T06_UP_TRACE",upseq)
        def joinstep(p):
            ev=next((e for e in p["layouts"][0]["printorder_trace"]["events"] if e["kind"]=="join"),None)
            if ev is None: p["layouts"][0]["printorder_trace"]["events"].append({"kind":"join","step":[1,1]})
            else: ev["step"]=[1,1]
        add("T07_JOIN_DIAGONAL",joinstep)
        add("T08_LEAF_ID",lambda p:p["layouts"][0]["factor_order"].__setitem__(0,"__tampered_leaf__"))
        add("T10_MAX_WIDTH",lambda p:p["layouts"][0]["width_receipt"].__setitem__("max_cut_width",-1))
        def cut(p):
            cuts=p["layouts"][0]["width_receipt"]["cuts"]
            if cuts: cuts[0]["width"]+=1
            else: p["layouts"][0]["width_receipt"]["cut_count"]=999
        add("T11_CUT_RECEIPT",cut)
    add("T09_AFFINE_IDENTITY",lambda p:p["canonical_factor_catalog"][0].__setitem__("affine_offset",{"tamper":True}))
    if not base["proof_payload"]["layouts"]:
        add("T12_EMPTY_ORDER",lambda p:p["layouts"].append({"root_entry_index":0,"factor_order":[p["canonical_factor_catalog"][0]["id"]]}))
        add("T13_EMPTY_FOUND",lambda p:p["strict_boundary"].__setitem__("generic_found_layout_candidate",True))
    else:
        add("T12_LAYOUT_COUNT",lambda p:p["summary"].__setitem__("layouts_emitted",0))
        add("T13_FOUND_ADMITTED",lambda p:p["strict_boundary"].__setitem__("generic_found_layout_admitted",True))
    add("T14_NO_LAYOUT",lambda p:p["strict_boundary"].__setitem__("generic_no_layout_at_cap",True))
    add("T15_GLOBAL_PROMOTION",lambda p:p["strict_boundary"].update({"polynomial_runtime":"TRUE","b5_complete":True,"p_vs_np":"CLOSED"}))
    rejected=0
    for name,c in attacks:
        try: verify(c,raw,b5_1,carrier,spec,carrier_spec)
        except Exception: rejected+=1; continue
        raise AssertionError(name+" survived")
    return rejected,len(attacks)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--spec",type=Path,required=True); ap.add_argument("--carrier-spec",type=Path,required=True); ap.add_argument("--input",type=Path,required=True); ap.add_argument("--b5-1-artifact",type=Path,required=True); ap.add_argument("--carrier",type=Path,required=True); ap.add_argument("--candidate",type=Path,required=True); ap.add_argument("--tamper-suite",action="store_true")
    a=ap.parse_args(); spec=load(a.spec); cs=load(a.carrier_spec); raw=load(a.input); b=load(a.b5_1_artifact); c=load(a.carrier); cand=load(a.candidate)
    roots=verify(cand,raw,b,c,spec,cs)
    print("JANUS_B5_2B_GENERIC_PRINTORDER_RECONSTRUCTION_INDEPENDENT_VERIFIER = PASS")
    print("ROOT_ENTRIES_RECONSTRUCTED =",roots)
    print("FACTOR_PERMUTATION_CHECK = PASS")
    print("DIRECT_PREFIX_SUFFIX_CUT_WIDTH_REPLAY = PASS")
    print("B5_2A_CARRIER_REVERIFICATION = PASS")
    print("FOUND_LAYOUT_ADMITTED = FALSE")
    print("NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    if a.tamper_suite:
        r,t=tamper_suite(cand,raw,b,c,spec,cs); print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {r}/{t}")

if __name__=="__main__": main()
