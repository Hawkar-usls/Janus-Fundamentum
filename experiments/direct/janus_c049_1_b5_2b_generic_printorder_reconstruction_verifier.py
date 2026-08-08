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


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def original_source_index(entry: dict) -> int:
    return int(entry["source_index"])


def normalized_source_index(entry: dict) -> int:
    return int(entry["b5_1_source_index"])


def independent_up_selected_indices(entry: dict, lower_length: int) -> list[int]:
    upper_length = len(entry["trajectory"])
    path = entry["algorithm2_up_label"]["native_zero_based_path"]
    if not isinstance(path, list) or not path or lower_length <= 0 or upper_length <= 0:
        raise AssertionError("bad up dimensions")
    if path[0] != [0, 0] or path[-1] != [lower_length - 1, upper_length - 1]:
        raise AssertionError("up path endpoints")
    buckets: list[list[int]] = [[] for _ in range(upper_length)]
    previous: tuple[int, int] | None = None
    for cell in path:
        if not isinstance(cell, list) or len(cell) != 2:
            raise AssertionError("bad up cell")
        i, j = int(cell[0]), int(cell[1])
        if not (0 <= i < lower_length and 0 <= j < upper_length):
            raise AssertionError("up coordinate")
        pair = (i, j)
        if previous is not None and (pair[0] - previous[0], pair[1] - previous[1]) not in ((1, 0), (0, 1), (1, 1)):
            raise AssertionError("illegal up step")
        buckets[j].append(i)
        previous = pair
    if any(not bucket for bucket in buckets):
        raise AssertionError("up path misses an upper coordinate")
    if upper_length == 1:
        if lower_length != 1:
            raise AssertionError("one-point upper cannot cover nontrivial source intervals")
        return [0]
    selected = [0]
    for j in range(1, upper_length):
        selected.append(max(buckets[j]))
    if selected[-1] != lower_length - 1:
        raise AssertionError("up selected endpoint")
    if any(a > b for a, b in zip(selected, selected[1:])):
        raise AssertionError("up selected sequence not monotone")
    return selected


def independent_compact_survivors(precompact: Sequence[dict], compact: Sequence[dict], trace: Sequence[dict]) -> list[int]:
    work = [dict(item) for item in precompact]
    origins = list(range(len(work)))
    for record in trace:
        if int(record.get("before_length", -1)) != len(work):
            raise AssertionError("compact before length")
        start, end = int(record["start"]), int(record["end"])
        if record["rule"] == "duplicate":
            if end != start + 1 or not (0 <= start < end < len(work)):
                raise AssertionError("duplicate compact coordinates")
            if work[start] != work[end]:
                raise AssertionError("duplicate compact semantics")
            removed = [work[end]]
            del work[end]
            del origins[end]
        elif record["rule"] == "interval":
            if not (0 <= start < end < len(work)) or end < start + 2:
                raise AssertionError("interval compact coordinates")
            left, right = work[start], work[end]
            if (left["left"], left["right"]) != (right["left"], right["right"]):
                raise AssertionError("interval compact geometry")
            values = [int(x["value"]) for x in work[start:end + 1]]
            increasing = values[0] <= values[-1] and all(values[0] <= z <= values[-1] for z in values[1:-1])
            decreasing = values[0] >= values[-1] and all(values[0] >= z >= values[-1] for z in values[1:-1])
            if not (increasing or decreasing):
                raise AssertionError("interval compact lambda rule")
            removed = work[start + 1:end]
            del work[start + 1:end]
            del origins[start + 1:end]
        else:
            raise AssertionError("unknown compact rule")
        if record.get("removed") != removed:
            raise AssertionError("compact removed payload")
        if int(record.get("after_length", -1)) != len(work):
            raise AssertionError("compact after length")
    if work != list(compact):
        raise AssertionError("compact output")
    return origins


def independent_width_receipt(order: Sequence[str], factors: dict[str, dict], ambient_dim: int) -> dict:
    if len(order) != len(factors) or len(set(order)) != len(order) or set(order) != set(factors):
        raise AssertionError("factor order is not an exact permutation")
    cuts: list[dict] = []
    for i in range(1, len(order)):
        prefix_rows = [v for fid in order[:i] for v in factors[fid]["normal_space"]]
        suffix_rows = [v for fid in order[i:] for v in factors[fid]["normal_space"]]
        prefix = b3.xor_basis(prefix_rows, ambient_dim)
        suffix = b3.xor_basis(suffix_rows, ambient_dim)
        intersection = b3.subspace_intersection(prefix, suffix, ambient_dim)
        cuts.append({
            "cut_after_position_zero_based": i - 1,
            "prefix_factor_ids": list(order[:i]),
            "suffix_factor_ids": list(order[i:]),
            "prefix_span_rref": list(prefix),
            "suffix_span_rref": list(suffix),
            "intersection_rref": list(intersection),
            "width": len(intersection),
        })
    return {"cut_count": len(cuts), "cuts": cuts, "max_cut_width": max((c["width"] for c in cuts), default=0)}


def independent_reconstruct(carrier: dict, root_entry_index: int) -> tuple[list[str], dict]:
    payload = carrier["proof_payload"]
    nodes = {node["node_id"]: node for node in payload["node_carriers"]}
    root = payload["root_id"]
    zero_prefix = sorted(
        node["leaf_factor_id"]
        for node in nodes.values()
        if node["kind"] == "leaf" and node["B_v_rref"] == []
    )
    events: list[dict] = []

    def up_interval(entry: dict, source: Sequence[dict], interval: int, recurse) -> list[str]:
        upper = entry["trajectory"]
        if entry["source_trajectory"] != list(source):
            raise AssertionError("up source bytes")
        if not (0 <= interval < len(upper) - 1):
            raise AssertionError("up output interval")
        selected = independent_up_selected_indices(entry, len(source))
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
        for j in range(lo, hi):
            out.extend(recurse(j))
        return out

    def leaf_source_interval(node: dict, interval: int) -> list[str]:
        if node["B_v_rref"] == []:
            return []
        if interval != 0:
            raise AssertionError("leaf interval")
        events.append({"kind": "leaf", "node_id": node["node_id"], "factor_id": node["leaf_factor_id"], "interval": interval})
        return [node["leaf_factor_id"]]

    def final_interval(node_id: str, entry_index: int, interval: int) -> list[str]:
        node = nodes[node_id]
        entry = node["final_entries"][entry_index]
        source_index = original_source_index(entry)
        if node["kind"] == "leaf":
            if not (0 <= source_index < len(node["delta_generators"])):
                raise AssertionError("leaf source")
            delta = node["delta_generators"][source_index]["trajectory"]
            return up_interval(entry, delta, interval, lambda j: leaf_source_interval(node, j))
        if not (0 <= source_index < len(node["shrink_generators"])):
            raise AssertionError("final shrink source")
        shrink = node["shrink_generators"][source_index]
        return up_interval(entry, shrink["shrunk_generator"], interval, lambda j: shrink_interval(node_id, source_index, j))

    def shrink_interval(node_id: str, shrink_index: int, compact_interval: int) -> list[str]:
        node = nodes[node_id]
        record = node["shrink_generators"][shrink_index]
        receipt = record["shrink_receipt"]
        if receipt["output"] != record["shrunk_generator"]:
            raise AssertionError("shrink output relation")
        survivors = independent_compact_survivors(
            receipt["projected_precompact"], receipt["output"], receipt["compactification_trace"]
        )
        if not (0 <= compact_interval < len(survivors) - 1):
            raise AssertionError("shrink compact interval")
        a, b = survivors[compact_interval], survivors[compact_interval + 1]
        joined_entry_index = int(record["joined_entry_index"])
        events.append({
            "kind": "shrink_compaction_lift",
            "node_id": node_id,
            "shrink_generator_index": shrink_index,
            "joined_entry_index": joined_entry_index,
            "compact_interval": compact_interval,
            "survivor_original_indices": survivors,
            "precompact_interval_range": [a, b],
        })
        out: list[str] = []
        for j in range(a, b):
            out.extend(joined_up_interval(node_id, joined_entry_index, j))
        return out

    def joined_up_interval(node_id: str, entry_index: int, interval: int) -> list[str]:
        node = nodes[node_id]
        entry = node["joined_entries"][entry_index]
        source_index = original_source_index(entry)
        if not (0 <= source_index < len(node["successful_join_generators"])):
            raise AssertionError("joined source")
        join = node["successful_join_generators"][source_index]
        return up_interval(entry, join["joined_generator"], interval, lambda j: join_interval(node_id, source_index, j))

    def join_interval(node_id: str, join_index: int, compact_interval: int) -> list[str]:
        node = nodes[node_id]
        record = node["successful_join_generators"][join_index]
        receipt = record["join_receipt"]
        if receipt["compact_join"] != record["joined_generator"] or receipt["path"] != record["path"]:
            raise AssertionError("join receipt relation")
        survivors = independent_compact_survivors(
            receipt["raw_join"], receipt["compact_join"], receipt["compactification_trace"]
        )
        if not (0 <= compact_interval < len(survivors) - 1):
            raise AssertionError("join compact interval")
        a, b = survivors[compact_interval], survivors[compact_interval + 1]
        path = [tuple(map(int, cell)) for cell in record["path"]]
        if len(path) != len(receipt["raw_join"]):
            raise AssertionError("join path/raw length")
        events.append({
            "kind": "join_compaction_lift",
            "node_id": node_id,
            "successful_join_generator_index": join_index,
            "compact_interval": compact_interval,
            "survivor_raw_indices": survivors,
            "raw_path_interval_range": [a, b],
        })
        out: list[str] = []
        for raw_interval in range(a, b):
            (left_i, right_i), (left_j, right_j) = path[raw_interval], path[raw_interval + 1]
            step = (left_j - left_i, right_j - right_i)
            events.append({
                "kind": "join_step",
                "node_id": node_id,
                "successful_join_generator_index": join_index,
                "raw_interval": raw_interval,
                "path_point": [left_i, right_i],
                "step": list(step),
            })
            if step == (1, 0):
                out.extend(expanded_up_interval(node_id, "left", int(record["left_expanded_entry_index"]), left_i))
            elif step == (0, 1):
                out.extend(expanded_up_interval(node_id, "right", int(record["right_expanded_entry_index"]), right_i))
            else:
                raise AssertionError("join path is not ordinary H/V")
        return out

    def expanded_up_interval(node_id: str, side: str, entry_index: int, interval: int) -> list[str]:
        node = nodes[node_id]
        entry = node[side + "_expanded_entries"][entry_index]
        source_index = original_source_index(entry)
        transports = node[side + "_transport_generators"]
        if not (0 <= source_index < len(transports)):
            raise AssertionError("expanded source")
        transport = transports[source_index]
        return up_interval(entry, transport["transported_generator"], interval, lambda j: transport_interval(node_id, side, source_index, j))

    def transport_interval(node_id: str, side: str, transport_index: int, interval: int) -> list[str]:
        node = nodes[node_id]
        transport = node[side + "_transport_generators"][transport_index]
        child_id = node[side + "_child_id"]
        child_entry_index = int(transport["child_output_entry_index"])
        events.append({
            "kind": "transport",
            "node_id": node_id,
            "side": side,
            "transport_generator_index": transport_index,
            "child_id": child_id,
            "child_entry_index": child_entry_index,
            "interval": interval,
        })
        return final_interval(child_id, child_entry_index, interval)

    root_entries = nodes[root]["final_entries"]
    if not (0 <= root_entry_index < len(root_entries)):
        raise AssertionError("root entry")
    order = list(zero_prefix)
    root_entry = root_entries[root_entry_index]
    for interval in range(len(root_entry["trajectory"]) - 1):
        order.extend(final_interval(root, root_entry_index, interval))
    return order, {"zero_boundary_leaf_prefix": zero_prefix, "event_count": len(events), "events": events}


def verify(candidate: dict, raw: dict, b5_1: dict, carrier: dict, spec: dict, carrier_spec: dict) -> int:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_REVIEW_ONLY_FOUND_LAYOUT_CEILING":
        raise AssertionError("spec")
    if candidate.get("schema") != SCHEMA or candidate.get("semantic_digest_scope") != "proof_payload":
        raise AssertionError("candidate schema")
    if dg(candidate.get("proof_payload")) != candidate.get("semantic_digest"):
        raise AssertionError("candidate digest")

    carrier_verifier.verify_v11(carrier, raw, b5_1, carrier_spec)
    cp = carrier["proof_payload"]
    p = candidate["proof_payload"]
    expected_subject = {
        "b5_2a_semantic_digest": carrier["semantic_digest"],
        "b5_1_semantic_digest": b5_1["semantic_digest"],
        "root_entry_count": cp["backtracking_summary"]["root_entries"],
    }
    if p["subject"] != expected_subject:
        raise AssertionError("subject")
    for field in ("ambient_dim", "k", "canonical_factor_catalog", "canonical_tree", "root_id"):
        if p[field] != cp[field]:
            raise AssertionError("identity " + field)

    factors = {f["id"]: f for f in cp["canonical_factor_catalog"]}
    ambient_dim, k = int(cp["ambient_dim"]), int(cp["k"])
    root_count = int(cp["backtracking_summary"]["root_entries"])
    if len(p["layouts"]) != root_count:
        raise AssertionError("layout count")

    for index, layout in enumerate(p["layouts"]):
        if int(layout["root_entry_index"]) != index:
            raise AssertionError("root entry index")
        expected_order, expected_trace = independent_reconstruct(carrier, index)
        if layout["factor_order"] != expected_order:
            raise AssertionError("factor order")
        if layout["factor_order_digest"] != dg(expected_order):
            raise AssertionError("factor order digest")
        if layout["printorder_trace"] != expected_trace:
            raise AssertionError("printorder trace")
        receipt = independent_width_receipt(expected_order, factors, ambient_dim)
        if layout["width_receipt"] != receipt:
            raise AssertionError("width receipt")
        if layout["within_width_cap"] is not True or receipt["max_cut_width"] > k:
            raise AssertionError("width cap")

    expected_summary = {
        "root_entries": root_count,
        "layouts_emitted": root_count,
        "all_orders_exact_factor_permutations": True,
        "all_layouts_within_width_cap": True,
        "max_emitted_cut_width": max((layout["width_receipt"]["max_cut_width"] for layout in p["layouts"]), default=None),
    }
    if p["summary"] != expected_summary:
        raise AssertionError("summary")
    expected_boundary = {
        "b5_2a_admitted_subject_verified": True,
        "generic_printorder_reconstruction_candidate": True,
        "factor_order_emitted": root_count > 0,
        "generic_found_layout_candidate": root_count > 0,
        "generic_found_layout_admitted": False,
        "generic_no_layout_at_cap": "FORBIDDEN",
        "all_input_termination": "NOT_ESTABLISHED",
        "polynomial_runtime": "NOT_ESTABLISHED",
        "b5_complete": False,
        "p_vs_np": "OPEN",
        "formal_admission": "BLOCKED_PENDING_REVIEW",
    }
    if p["strict_boundary"] != expected_boundary:
        raise AssertionError("strict boundary")
    return root_count


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def tamper_suite(base: dict, raw: dict, b5_1: dict, carrier: dict, spec: dict, carrier_spec: dict) -> tuple[int, int]:
    attacks: list[tuple[str, dict]] = []

    def add(name: str, mutation) -> None:
        candidate = copy.deepcopy(base)
        mutation(candidate["proof_payload"])
        attacks.append((name, repair(candidate)))

    layouts = base["proof_payload"]["layouts"]
    if not layouts:
        raise AssertionError("tamper suite requires nonempty root control")

    add("T01_SUBJECT", lambda p: p["subject"].__setitem__("b5_2a_semantic_digest", "0" * 64))
    add("T02_ROOT_INDEX", lambda p: p["layouts"][0].__setitem__("root_entry_index", 999))
    add("T03_OMIT_FACTOR", lambda p: p["layouts"][0]["factor_order"].pop())
    add("T04_DUP_FACTOR", lambda p: p["layouts"][0]["factor_order"].append(p["layouts"][0]["factor_order"][0]))

    def swap_order(p):
        order = p["layouts"][0]["factor_order"]
        if len(order) < 2:
            raise AssertionError("swap attack needs two factors")
        order[0], order[1] = order[1], order[0]
    add("T05_SWAP_ORDER", swap_order)

    def mutate_event(p, kind: str, field: str, value) -> None:
        events = p["layouts"][0]["printorder_trace"]["events"]
        event = next((x for x in events if x["kind"] == kind), None)
        if event is None:
            raise AssertionError("control does not exercise " + kind)
        event[field] = value

    add("T06_UP_SEQUENCE", lambda p: mutate_event(p, "up", "selected_lower_indices", [999]))
    add("T07_JOIN_STEP", lambda p: mutate_event(p, "join_step", "step", [1, 1]))
    add("T08_JOIN_COMPACTION", lambda p: mutate_event(p, "join_compaction_lift", "survivor_raw_indices", [999]))
    add("T09_SHRINK_COMPACTION", lambda p: mutate_event(p, "shrink_compaction_lift", "survivor_original_indices", [999]))
    add("T10_ZERO_PREFIX", lambda p: p["layouts"][0]["printorder_trace"].__setitem__("zero_boundary_leaf_prefix", ["__tampered__"]))
    add("T11_AFFINE_IDENTITY", lambda p: p["canonical_factor_catalog"][0].__setitem__("affine_offset", {"tamper": True}))
    add("T12_MAX_WIDTH", lambda p: p["layouts"][0]["width_receipt"].__setitem__("max_cut_width", -1))

    def mutate_cut(p):
        cuts = p["layouts"][0]["width_receipt"]["cuts"]
        if not cuts:
            raise AssertionError("cut attack needs a nontrivial order")
        cuts[0]["width"] = int(cuts[0]["width"]) + 1
    add("T13_CUT", mutate_cut)

    add("T14_LAYOUT_COUNT", lambda p: p["summary"].__setitem__("layouts_emitted", 0))
    add("T15_FOUND_ADMISSION", lambda p: p["strict_boundary"].__setitem__("generic_found_layout_admitted", True))
    add("T16_NO_LAYOUT", lambda p: p["strict_boundary"].__setitem__("generic_no_layout_at_cap", True))
    add("T17_GLOBAL_PROMOTION", lambda p: p["strict_boundary"].update({"polynomial_runtime": "TRUE", "b5_complete": True, "p_vs_np": "CLOSED"}))
    add("T18_ORDER_DIGEST", lambda p: p["layouts"][0].__setitem__("factor_order_digest", "0" * 64))

    rejected = 0
    for name, candidate in attacks:
        try:
            verify(candidate, raw, b5_1, carrier, spec, carrier_spec)
        except Exception:
            rejected += 1
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--carrier-spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--carrier", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--tamper-suite", action="store_true")
    args = parser.parse_args()
    spec = load(args.spec)
    carrier_spec = load(args.carrier_spec)
    raw = load(args.input)
    b5_1 = load(args.b5_1_artifact)
    carrier = load(args.carrier)
    candidate = load(args.candidate)
    roots = verify(candidate, raw, b5_1, carrier, spec, carrier_spec)
    print("JANUS_B5_2B_GENERIC_PRINTORDER_RECONSTRUCTION_INDEPENDENT_VERIFIER = PASS")
    print("ROOT_ENTRIES_RECONSTRUCTED =", roots)
    print("B5_2A_CARRIER_REVERIFICATION = PASS")
    print("ALGORITHM2_UP_SEQUENCE = PASS")
    print("JOIN_SHRINK_COMPACTIFICATION_LIFT = PASS")
    print("ZERO_BOUNDARY_LEAF_PREFIX = PASS")
    print("FACTOR_PERMUTATION_CHECK = PASS")
    print("DIRECT_PREFIX_SUFFIX_CUT_WIDTH_REPLAY = PASS")
    print("GENERIC_FOUND_LAYOUT_ADMITTED = FALSE")
    print("NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    if args.tamper_suite:
        rejected, total = tamper_suite(candidate, raw, b5_1, carrier, spec, carrier_spec)
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")


if __name__ == "__main__":
    main()
