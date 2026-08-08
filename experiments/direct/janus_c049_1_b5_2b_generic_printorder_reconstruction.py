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


def selected_lower_indices(label: dict, lower_length: int, upper_length: int) -> list[int]:
    path = label["native_zero_based_path"]
    if not isinstance(path, list) or not path:
        raise AssertionError("empty up path")
    by_upper: dict[int, list[int]] = {j: [] for j in range(upper_length)}
    for cell in path:
        if not isinstance(cell, list) or len(cell) != 2:
            raise AssertionError("bad up path cell")
        i, j = map(int, cell)
        if not (0 <= i < lower_length and 0 <= j < upper_length):
            raise AssertionError("up path coordinate outside trajectory")
        by_upper[j].append(i)
    if any(not by_upper[j] for j in range(upper_length)):
        raise AssertionError("up path skips an upper coordinate")
    selected = [max(by_upper[j]) for j in range(upper_length)]
    if selected[0] != 0 or selected[-1] != lower_length - 1:
        raise AssertionError("up selection endpoints")
    if any(a > b for a, b in zip(selected, selected[1:])):
        raise AssertionError("up selection is not monotone")
    return selected


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
    return {
        "cut_count": len(cuts),
        "cuts": cuts,
        "max_cut_width": max((c["width"] for c in cuts), default=0),
    }


def normalized_source_index(entry: dict) -> int:
    label = entry["algorithm2_up_label"]
    if "b5_1_source_index" in label:
        return int(label["b5_1_source_index"])
    # v1.1 carrier keeps original_generator_index as entry.source_index and the
    # B5.1 normalized source index in the Algorithm-2 label.
    if "source_index" in label:
        return int(label["source_index"])
    raise AssertionError("missing normalized source index")


def original_source_index(entry: dict) -> int:
    if "original_generator_index" in entry:
        return int(entry["original_generator_index"])
    return int(entry["source_index"])


def emit_from_up(entry: dict, lower_trajectory: Sequence[dict], recurse_interval) -> list[str]:
    upper_trajectory = entry["trajectory"]
    lower_len, upper_len = len(lower_trajectory), len(upper_trajectory)
    selected = selected_lower_indices(entry["algorithm2_up_label"], lower_len, upper_len)
    emitted: list[str] = []
    for upper_interval in range(max(0, upper_len - 1)):
        lo = selected[upper_interval]
        hi = selected[upper_interval + 1]
        for lower_interval in range(lo, hi):
            emitted.extend(recurse_interval(lower_interval))
    return emitted


def reconstruct_root_order(carrier: dict, root_entry_index: int) -> tuple[list[str], dict]:
    p = carrier["proof_payload"]
    cnodes = {n["node_id"]: n for n in p["node_carriers"]}
    root = p["root_id"]
    trace = []

    def final_interval(nid: str, entry_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        finals = node["final_entries"]
        if not (0 <= entry_index < len(finals)):
            raise AssertionError("final entry reference")
        entry = finals[entry_index]
        if not (0 <= interval < max(1, len(entry["trajectory"]) - 1)):
            # length-one zero-boundary trajectories have no ordinary interval;
            # leaf special handling is reached through the source relation.
            if not (len(entry["trajectory"]) == 1 and interval == 0):
                raise AssertionError("final interval reference")
        oi = original_source_index(entry)
        trace.append({"kind": "up_final", "node_id": nid, "entry_index": entry_index, "interval": interval, "original_generator_index": oi, "normalized_source_index": normalized_source_index(entry)})
        if node["kind"] == "leaf":
            # The leaf Delta source has one factor.  Algorithm 2 emits it on its
            # first interval; for the zero-boundary length-one leaf this is the
            # paper's explicit root/leaf special case.
            if interval == 0:
                return [node["leaf_factor_id"]]
            return []
        shrinks = node["shrink_generators"]
        if not (0 <= oi < len(shrinks)):
            raise AssertionError("final original source index")
        lower = shrinks[oi]["shrunk_generator"]
        return emit_from_up(entry, lower, lambda j: shrink_interval(nid, oi, j)) if len(entry["trajectory"]) > 1 else []

    def shrink_interval(nid: str, shrink_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        sr = node["shrink_generators"][shrink_index]
        joined_entry_index = int(sr["joined_entry_index"])
        trace.append({"kind": "shrink", "node_id": nid, "shrink_generator_index": shrink_index, "joined_entry_index": joined_entry_index, "interval": interval})
        # Shrink is order-preserving in Algorithm 2: same interval index.
        return joined_up_interval(nid, joined_entry_index, interval)

    def joined_up_interval(nid: str, entry_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        entry = node["joined_entries"][entry_index]
        oi = original_source_index(entry)
        joins = node["successful_join_generators"]
        if not (0 <= oi < len(joins)):
            raise AssertionError("joined original source index")
        lower = joins[oi]["joined_generator"]
        trace.append({"kind": "up_joined", "node_id": nid, "entry_index": entry_index, "interval": interval, "successful_join_generator_index": oi, "normalized_source_index": normalized_source_index(entry)})
        return emit_from_up(entry, lower, lambda j: join_interval(nid, oi, j))

    def join_interval(nid: str, join_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        jr = node["successful_join_generators"][join_index]
        path = [tuple(map(int, x)) for x in jr["path"]]
        if not (0 <= interval < len(path) - 1):
            raise AssertionError("join interval")
        (li, ri), (li2, ri2) = path[interval], path[interval + 1]
        step = (li2 - li, ri2 - ri)
        trace.append({"kind": "join", "node_id": nid, "successful_join_generator_index": join_index, "interval": interval, "path_point": [li, ri], "step": list(step)})
        if step == (1, 0):
            return expanded_up_interval(nid, "left", int(jr["left_expanded_entry_index"]), li)
        if step == (0, 1):
            return expanded_up_interval(nid, "right", int(jr["right_expanded_entry_index"]), ri)
        raise AssertionError("ordinary join path contains non-H/V step")

    def expanded_up_interval(nid: str, side: str, entry_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        entries = node[side + "_expanded_entries"]
        entry = entries[entry_index]
        oi = original_source_index(entry)
        transports = node[side + "_transport_generators"]
        if not (0 <= oi < len(transports)):
            raise AssertionError("expanded original source index")
        lower = transports[oi]["transported_generator"]
        trace.append({"kind": "up_expand", "node_id": nid, "side": side, "entry_index": entry_index, "interval": interval, "transport_generator_index": oi, "normalized_source_index": normalized_source_index(entry)})
        return emit_from_up(entry, lower, lambda j: transport_interval(nid, side, oi, j))

    def transport_interval(nid: str, side: str, transport_index: int, interval: int) -> list[str]:
        node = cnodes[nid]
        tr = node[side + "_transport_generators"][transport_index]
        child_id = node[side + "_child_id"]
        child_entry_index = int(tr["child_output_entry_index"])
        trace.append({"kind": "transport", "node_id": nid, "side": side, "transport_generator_index": transport_index, "child_id": child_id, "child_entry_index": child_entry_index, "interval": interval})
        return final_interval(child_id, child_entry_index, interval)

    root_entry = cnodes[root]["final_entries"][root_entry_index]
    order: list[str] = []
    if len(root_entry["trajectory"]) == 1:
        # Paper line 19: zero-boundary single-space root special case.
        if len(p["canonical_factor_catalog"]) == 1:
            order = [p["canonical_factor_catalog"][0]["id"]]
        else:
            order = []
    else:
        for i in range(len(root_entry["trajectory"]) - 1):
            order.extend(final_interval(root, root_entry_index, i))
    return order, {"event_count": len(trace), "events": trace}


def build(raw: dict, b5_1: dict, carrier: dict, spec: dict, carrier_spec: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_REVIEW_ONLY_FOUND_LAYOUT_CEILING":
        raise AssertionError("wrong B5.2B spec")
    # Admission boundary: the B5.2A verifier is the authority on the carrier's
    # semantics and provenance.  Do not reconstruct from an unverified carrier.
    carrier_verifier.verify(carrier, raw, b5_1, carrier_spec)
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
