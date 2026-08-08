from __future__ import annotations

import argparse
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


def save(value: Any, path: Path) -> None:
    path.write_bytes(cb(value) + b"\n")


def original_source_index(entry: dict) -> int:
    return int(entry["source_index"])


def normalized_source_index(entry: dict) -> int:
    return int(entry["b5_1_source_index"])


def up_selected_indices(entry: dict, lower_length: int) -> list[int]:
    upper_length = len(entry["trajectory"])
    path = entry["algorithm2_up_label"]["native_zero_based_path"]
    if not isinstance(path, list) or not path or lower_length <= 0 or upper_length <= 0:
        raise AssertionError("bad up path dimensions")
    if path[0] != [0, 0] or path[-1] != [lower_length - 1, upper_length - 1]:
        raise AssertionError("up path endpoints")
    buckets = [[] for _ in range(upper_length)]
    previous = None
    for raw in path:
        if not isinstance(raw, list) or len(raw) != 2:
            raise AssertionError("bad up path cell")
        i, j = map(int, raw)
        if not (0 <= i < lower_length and 0 <= j < upper_length):
            raise AssertionError("up path coordinate")
        if previous is not None and (i - previous[0], j - previous[1]) not in ((1, 0), (0, 1), (1, 1)):
            raise AssertionError("bad extension step")
        buckets[j].append(i)
        previous = (i, j)
    if any(not bucket for bucket in buckets):
        raise AssertionError("up path skips upper coordinate")
    if upper_length == 1:
        if lower_length != 1:
            raise AssertionError("Algorithm2 up sequence endpoint collision")
        return [0]
    selected = [0] + [max(buckets[j]) for j in range(1, upper_length)]
    if selected[-1] != lower_length - 1 or any(a > b for a, b in zip(selected, selected[1:])):
        raise AssertionError("invalid Algorithm2 selected sequence")
    return selected


def compact_survivor_indices(precompact: Sequence[dict], compact: Sequence[dict], trace: Sequence[dict]) -> list[int]:
    work = [dict(x) for x in precompact]
    origins = list(range(len(precompact)))
    for record in trace:
        if int(record["before_length"]) != len(work):
            raise AssertionError("compact trace before length")
        rule = record["rule"]
        start, end = int(record["start"]), int(record["end"])
        if rule == "duplicate":
            if end != start + 1 or not (0 <= start < end < len(work)) or work[start] != work[end]:
                raise AssertionError("invalid duplicate compactification record")
            removed = [work[end]]
            del work[end]
            del origins[end]
        elif rule == "interval":
            if not (0 <= start < end < len(work)) or end < start + 2:
                raise AssertionError("invalid interval compactification record")
            removed = work[start + 1:end]
            del work[start + 1:end]
            del origins[start + 1:end]
        else:
            raise AssertionError("unknown compactification rule")
        if record.get("removed") != removed or int(record["after_length"]) != len(work):
            raise AssertionError("compactification receipt mismatch")
    if work != list(compact) or len(origins) != len(compact):
        raise AssertionError("compactification output mismatch")
    return origins


def factor_width_receipt(order: Sequence[str], factors: dict[str, dict], ambient_dim: int) -> dict:
    if len(order) != len(factors) or len(set(order)) != len(order) or set(order) != set(factors):
        raise AssertionError("order is not an exact factor permutation")
    cuts = []
    for i in range(1, len(order)):
        prefix = b3.xor_basis([v for fid in order[:i] for v in factors[fid]["normal_space"]], ambient_dim)
        suffix = b3.xor_basis([v for fid in order[i:] for v in factors[fid]["normal_space"]], ambient_dim)
        inter = b3.subspace_intersection(prefix, suffix, ambient_dim)
        cuts.append({
            "cut_after_position_zero_based": i - 1,
            "prefix_factor_ids": list(order[:i]),
            "suffix_factor_ids": list(order[i:]),
            "prefix_span_rref": list(prefix),
            "suffix_span_rref": list(suffix),
            "intersection_rref": list(inter),
            "width": len(inter),
        })
    return {"cut_count": len(cuts), "cuts": cuts, "max_cut_width": max((x["width"] for x in cuts), default=0)}


def reconstruct_root_order(carrier: dict, root_entry_index: int) -> tuple[list[str], dict]:
    p = carrier["proof_payload"]
    cnodes = {n["node_id"]: n for n in p["node_carriers"]}
    root = p["root_id"]
    events: list[dict] = []
    zero_boundary_leaf_prefix = sorted(
        n["leaf_factor_id"] for n in cnodes.values() if n["kind"] == "leaf" and n["B_v_rref"] == []
    )

    def up_interval(entry: dict, lower: Sequence[dict], interval: int, recurse) -> list[str]:
        upper = entry["trajectory"]
        if not (0 <= interval < len(upper) - 1):
            raise AssertionError("up interval outside output trajectory")
        if entry["source_trajectory"] != list(lower):
            raise AssertionError("up source trajectory binding")
        selected = up_selected_indices(entry, len(lower))
        lo, hi = selected[interval], selected[interval + 1]
        events.append({
            "kind": "up",
            "entry_index": int(entry["entry_index"]),
            "output_interval": interval,
            "selected_lower_indices": selected,
            "source_interval_range": [lo, hi],
            "b5_1_source_index": normalized_source_index(entry),
            "original_generator_index": original_source_index(entry),
        })
        out: list[str] = []
        for source_interval in range(lo, hi):
            out.extend(recurse(source_interval))
        return out

    def leaf_source_interval(node: dict, interval: int) -> list[str]:
        if node["B_v_rref"] == []:
            return []
        if interval != 0:
            raise AssertionError("nonzero-boundary leaf has only its Delta interval")
        events.append({"kind": "leaf", "node_id": node["node_id"], "factor_id": node["leaf_factor_id"], "interval": interval})
        return [node["leaf_factor_id"]]

    def final_interval(nid: str, entry_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        entry = node["final_entries"][entry_index]
        oi = original_source_index(entry)
        if node["kind"] == "leaf":
            delta = node["delta_generators"][oi]["trajectory"]
            return up_interval(entry, delta, interval, lambda j: leaf_source_interval(node, j))
        shrink = node["shrink_generators"][oi]
        return up_interval(entry, shrink["shrunk_generator"], interval, lambda j: shrink_interval(nid, oi, j))

    def shrink_interval(nid: str, shrink_index: int, compact_interval: int) -> list[str]:
        node = cnodes[nid]
        sr = node["shrink_generators"][shrink_index]
        receipt = sr["shrink_receipt"]
        if receipt["output"] != sr["shrunk_generator"]:
            raise AssertionError("shrink output binding")
        survivors = compact_survivor_indices(receipt["projected_precompact"], receipt["output"], receipt["compactification_trace"])
        if not (0 <= compact_interval < len(survivors) - 1):
            raise AssertionError("shrink compact interval")
        a, b = survivors[compact_interval], survivors[compact_interval + 1]
        joined_entry_index = int(sr["joined_entry_index"])
        events.append({
            "kind": "shrink_compaction_lift",
            "node_id": nid,
            "shrink_generator_index": shrink_index,
            "joined_entry_index": joined_entry_index,
            "compact_interval": compact_interval,
            "survivor_original_indices": survivors,
            "precompact_interval_range": [a, b],
        })
        out: list[str] = []
        for joined_interval in range(a, b):
            out.extend(joined_up_interval(nid, joined_entry_index, joined_interval))
        return out

    def joined_up_interval(nid: str, entry_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        entry = node["joined_entries"][entry_index]
        oi = original_source_index(entry)
        join_record = node["successful_join_generators"][oi]
        return up_interval(entry, join_record["joined_generator"], interval, lambda j: join_interval(nid, oi, j))

    def join_interval(nid: str, join_index: int, compact_interval: int) -> list[str]:
        node = cnodes[nid]
        jr = node["successful_join_generators"][join_index]
        receipt = jr["join_receipt"]
        if receipt["compact_join"] != jr["joined_generator"] or receipt["path"] != jr["path"]:
            raise AssertionError("join receipt binding")
        survivors = compact_survivor_indices(receipt["raw_join"], receipt["compact_join"], receipt["compactification_trace"])
        if not (0 <= compact_interval < len(survivors) - 1):
            raise AssertionError("join compact interval")
        a, b = survivors[compact_interval], survivors[compact_interval + 1]
        path = [tuple(map(int, x)) for x in jr["path"]]
        events.append({
            "kind": "join_compaction_lift",
            "node_id": nid,
            "successful_join_generator_index": join_index,
            "compact_interval": compact_interval,
            "survivor_raw_indices": survivors,
            "raw_path_interval_range": [a, b],
        })
        out: list[str] = []
        for raw_interval in range(a, b):
            (li, ri), (li2, ri2) = path[raw_interval], path[raw_interval + 1]
            step = (li2 - li, ri2 - ri)
            events.append({
                "kind": "join_step",
                "node_id": nid,
                "successful_join_generator_index": join_index,
                "raw_interval": raw_interval,
                "path_point": [li, ri],
                "step": list(step),
            })
            if step == (1, 0):
                out.extend(expanded_up_interval(nid, "left", int(jr["left_expanded_entry_index"]), li))
            elif step == (0, 1):
                out.extend(expanded_up_interval(nid, "right", int(jr["right_expanded_entry_index"]), ri))
            else:
                raise AssertionError("ordinary join contains non-H/V step")
        return out

    def expanded_up_interval(nid: str, side: str, entry_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        entry = node[side + "_expanded_entries"][entry_index]
        oi = original_source_index(entry)
        transport = node[side + "_transport_generators"][oi]
        return up_interval(entry, transport["transported_generator"], interval, lambda j: transport_interval(nid, side, oi, j))

    def transport_interval(nid: str, side: str, transport_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        tr = node[side + "_transport_generators"][transport_index]
        child_id = node[side + "_child_id"]
        child_entry_index = int(tr["child_output_entry_index"])
        events.append({
            "kind": "transport",
            "node_id": nid,
            "side": side,
            "transport_generator_index": transport_index,
            "child_id": child_id,
            "child_entry_index": child_entry_index,
            "interval": interval,
        })
        return final_interval(child_id, child_entry_index, interval)

    order = list(zero_boundary_leaf_prefix)
    root_entry = cnodes[root]["final_entries"][root_entry_index]
    for interval in range(len(root_entry["trajectory"]) - 1):
        order.extend(final_interval(root, root_entry_index, interval))
    return order, {
        "zero_boundary_leaf_prefix": zero_boundary_leaf_prefix,
        "event_count": len(events),
        "events": events,
    }


def build(raw: dict, b5_1: dict, carrier: dict, spec: dict, carrier_spec: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_REVIEW_ONLY_FOUND_LAYOUT_CEILING":
        raise AssertionError("wrong B5.2B spec")
    carrier_verifier.verify_v11(carrier, raw, b5_1, carrier_spec)
    p = carrier["proof_payload"]
    factors = {f["id"]: f for f in p["canonical_factor_catalog"]}
    d, k = int(p["ambient_dim"]), int(p["k"])
    root_entries = int(p["backtracking_summary"]["root_entries"])
    layouts = []
    for root_entry_index in range(root_entries):
        order, print_trace = reconstruct_root_order(carrier, root_entry_index)
        width_receipt = factor_width_receipt(order, factors, d)
        if width_receipt["max_cut_width"] > k:
            raise AssertionError("Algorithm2 reconstruction exceeds width cap")
        layouts.append({
            "root_entry_index": root_entry_index,
            "factor_order": order,
            "factor_order_digest": dg(order),
            "printorder_trace": print_trace,
            "width_receipt": width_receipt,
            "within_width_cap": True,
        })
    payload = {
        "subject": {
            "b5_2a_semantic_digest": carrier["semantic_digest"],
            "b5_1_semantic_digest": b5_1["semantic_digest"],
            "root_entry_count": root_entries,
        },
        "ambient_dim": d,
        "k": k,
        "canonical_factor_catalog": p["canonical_factor_catalog"],
        "canonical_tree": p["canonical_tree"],
        "root_id": p["root_id"],
        "layouts": layouts,
        "summary": {
            "root_entries": root_entries,
            "layouts_emitted": len(layouts),
            "all_orders_exact_factor_permutations": all(len(x["factor_order"]) == len(factors) and set(x["factor_order"]) == set(factors) for x in layouts),
            "all_layouts_within_width_cap": all(x["within_width_cap"] for x in layouts),
            "max_emitted_cut_width": max((x["width_receipt"]["max_cut_width"] for x in layouts), default=None),
        },
        "strict_boundary": {
            "b5_2a_admitted_subject_verified": True,
            "generic_printorder_reconstruction_candidate": True,
            "factor_order_emitted": root_entries > 0,
            "generic_found_layout_candidate": root_entries > 0,
            "generic_found_layout_admitted": False,
            "generic_no_layout_at_cap": "FORBIDDEN",
            "all_input_termination": "NOT_ESTABLISHED",
            "polynomial_runtime": "NOT_ESTABLISHED",
            "b5_complete": False,
            "p_vs_np": "OPEN",
            "formal_admission": "BLOCKED_PENDING_REVIEW",
        },
    }
    artifact = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": payload}
    artifact["semantic_digest"] = dg(payload)
    return artifact


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--carrier-spec", type=Path, required=True)
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--b5-1-artifact", type=Path, required=True)
    ap.add_argument("--carrier", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    art = build(load(a.input), load(a.b5_1_artifact), load(a.carrier), load(a.spec), load(a.carrier_spec))
    save(art, a.output)
    s = art["proof_payload"]["summary"]
    print("JANUS_B5_2B_GENERIC_PRINTORDER_RECONSTRUCTION = PASS")
    print("ROOT_ENTRIES =", s["root_entries"])
    print("LAYOUTS_EMITTED =", s["layouts_emitted"])
    print("ALL_ORDERS_EXACT_FACTOR_PERMUTATIONS =", str(s["all_orders_exact_factor_permutations"]).upper())
    print("ALL_LAYOUTS_WITHIN_WIDTH_CAP =", str(s["all_layouts_within_width_cap"]).upper())
    print("MAX_EMITTED_CUT_WIDTH =", s["max_emitted_cut_width"])
    print("FOUND_LAYOUT = CANDIDATE" if s["layouts_emitted"] else "FOUND_LAYOUT = FALSE_NO_ROOT_ENTRY")
    print("NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", art["semantic_digest"])


if __name__ == "__main__":
    main()
