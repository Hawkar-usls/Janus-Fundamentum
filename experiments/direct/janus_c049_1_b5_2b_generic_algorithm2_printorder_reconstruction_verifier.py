from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import janus_c049_1_b3_expand_join_shrink_core as b3

SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_candidate.v1"
SPEC_SCHEMA = "janus.c049_1.b5_2b.generic_algorithm2_printorder_reconstruction_spec.v1"
CARRIER_SCHEMA = "janus.c049_1.b5_2a.generic_algorithm2_provenance_carrier.v1_1"
B5_1_SCHEMA = "janus.c049_1.b5_1.generic_corrected_runtime_trace.v1"


def cb(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def dg(value: Any) -> str:
    return hashlib.sha256(cb(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def idk(value: Any) -> str:
    return cb(value).decode("utf-8")


def t_width(raw: Sequence[dict]) -> int:
    if not raw:
        raise AssertionError("empty trajectory")
    return max(int(x["value"]) for x in raw)


def canonical_input_catalog(raw_input: dict) -> list[dict]:
    d = int(raw_input["ambient_dim"])
    out = []
    seen = set()
    for item in raw_input["factors"]:
        key = idk(item["id"])
        if key in seen:
            raise AssertionError("duplicate input factor id")
        seen.add(key)
        out.append(
            {
                "id": item["id"],
                "normal_space": list(b3.xor_basis(item["normal_space"], d)),
                "affine_offset": item.get("affine_offset"),
            }
        )
    return sorted(out, key=lambda item: idk(item["id"]))


def compact_identity(raw: Sequence[dict], compact_source: Sequence[dict], boundary: Sequence[int], d: int) -> list[dict]:
    gamma = b3.decode_trajectory(raw, boundary, d, require_compact=False)
    compact, trace = b3.compactify(gamma)
    if b3.encode_trajectory(compact) != list(compact_source):
        raise AssertionError("runtime compact source is not the compactification of the paper trajectory")
    return trace


def preorder(lower_raw: Sequence[dict], upper_raw: Sequence[dict], boundary: Sequence[int], d: int) -> dict:
    lower = b3.decode_trajectory(lower_raw, boundary, d, require_compact=False)
    upper = b3.decode_trajectory(upper_raw, boundary, d, require_compact=False)
    found = b3.extension_preorder_witness(lower, upper)
    if found is None:
        raise AssertionError("required paper-faithful preorder lift missing")
    return found


def independent_x(path: Sequence[Sequence[int]], lower_len: int, upper_len: int) -> list[int]:
    points = [[int(p[0]), int(p[1])] for p in path]
    if not points or points[0] != [0, 0] or points[-1] != [lower_len - 1, upper_len - 1]:
        raise AssertionError("up path endpoints")
    for p, q in zip(points, points[1:]):
        if (q[0] - p[0], q[1] - p[1]) not in {(1, 0), (0, 1), (1, 1)}:
            raise AssertionError("up path step")
    xs = []
    for j in range(upper_len):
        column = [i for i, jj in points if jj == j]
        if not column:
            raise AssertionError("up path column missing")
        chosen = 0 if j == 0 else (lower_len - 1 if j == upper_len - 1 else min(column))
        if [chosen, j] not in points:
            raise AssertionError("x sequence point absent from path")
        xs.append(chosen)
    if xs[0] != 0 or xs[-1] != lower_len - 1 or any(a > b for a, b in zip(xs, xs[1:])):
        raise AssertionError("invalid Algorithm-2 x sequence")
    return xs


def cut_data(catalog: list[dict], order: list[Any], d: int) -> tuple[list[dict], int]:
    by = {idk(x["id"]): x for x in catalog}
    keys = [idk(x) for x in order]
    if len(keys) != len(by) or len(set(keys)) != len(keys) or sorted(keys) != sorted(by):
        raise AssertionError("not a whole-factor permutation")
    blocks = [tuple(int(v) for v in by[key]["normal_space"]) for key in keys]
    cuts = []
    maximum = 0
    for cut in range(len(blocks) + 1):
        left = b3.xor_basis(tuple(v for block in blocks[:cut] for v in block), d)
        right = b3.xor_basis(tuple(v for block in blocks[cut:] for v in block), d)
        boundary = b3.subspace_intersection(left, right, d)
        width = len(boundary)
        maximum = max(maximum, width)
        cuts.append(
            {
                "cut": cut,
                "left_factor_ids": order[:cut],
                "right_factor_ids": order[cut:],
                "left_span_rref": list(left),
                "right_span_rref": list(right),
                "boundary_rref": list(boundary),
                "width": width,
            }
        )
    return cuts, maximum


def reconstruct(raw_input: dict, b5_1: dict, carrier: dict) -> dict:
    if b5_1.get("schema") != B5_1_SCHEMA or carrier.get("schema") != CARRIER_SCHEMA:
        raise AssertionError("upstream schema")
    b = b5_1["proof_payload"]
    c = carrier["proof_payload"]
    if b.get("capability_status") != "CLOSED_COMPLETE_TRACE":
        raise AssertionError("B5.1 not CLOSED")
    if c["subject"]["b5_1_semantic_digest"] != b5_1["semantic_digest"]:
        raise AssertionError("carrier subject semantic digest")
    if c["subject"]["b5_1_root_full_set_digest"] != b["root_full_set_digest_if_closed"]:
        raise AssertionError("carrier root digest")
    if c["subject"]["b5_1_root_entry_count"] != b["root_entry_count_if_closed"]:
        raise AssertionError("carrier root count")
    if int(raw_input["ambient_dim"]) != int(c["ambient_dim"]) or int(raw_input["k"]) != int(c["k"]):
        raise AssertionError("input/carrier parameters")
    if canonical_input_catalog(raw_input) != c["canonical_factor_catalog"]:
        raise AssertionError("input/carrier factor catalog identity")

    d = int(c["ambient_dim"])
    k = int(c["k"])
    nodes = {x["node_id"]: x for x in c["node_carriers"]}
    root = nodes[c["root_id"]]
    entries = root["final_entries"]
    if not entries:
        return {
            "empty": True,
            "selected": None,
            "root_width": None,
            "root_digest": None,
            "certificates": [],
            "events": [],
            "order": None,
            "layout": None,
            "cuts": None,
            "max_width": None,
        }

    selected = min(
        range(len(entries)),
        key=lambda i: (t_width(entries[i]["trajectory"]), dg(entries[i]["trajectory"]), i),
    )
    selected_entry = entries[selected]
    bt = c["root_entry_backtracks"][selected]
    if int(bt["entry_index"]) != selected:
        raise AssertionError("root traceback index")

    certs: list[dict] = []
    cert_cache: dict[tuple, dict] = {}
    events: list[dict] = []
    order: list[Any] = []

    def event(kind: str, **kw: Any) -> None:
        events.append({"event_index": len(events), "kind": kind, **kw})

    def cert(stage: str, node_id: Any, entry_index: int, lower: Sequence[dict], upper: Sequence[dict], boundary: Sequence[int], retained: dict | None = None, compact_source: Sequence[dict] | None = None, compact_trace: list[dict] | None = None) -> dict:
        key = (idk(node_id), stage, int(entry_index), dg(lower), dg(upper))
        if key in cert_cache:
            return cert_cache[key]
        w = preorder(lower, upper, boundary, d)
        if retained is not None and retained != w:
            raise AssertionError("retained witness differs from independent B3 replay")
        xs = independent_x(w["path"], len(lower), len(upper))
        value: dict[str, Any] = {
            "certificate_index": len(certs),
            "stage": stage,
            "node_id": node_id,
            "entry_index": int(entry_index),
            "boundary_rref": list(boundary),
            "lower_trajectory_digest": dg(lower),
            "upper_trajectory_digest": dg(upper),
            "lower_length": len(lower),
            "upper_length": len(upper),
            "extension_preorder_witness": w,
            "algorithm2_x_sequence_zero_based": xs,
            "slack_metadata_used": False,
        }
        if compact_source is not None:
            trace = compact_identity(lower, compact_source, boundary, d)
            if compact_trace is not None and trace != compact_trace:
                raise AssertionError("runtime compactification trace")
            value["compactification_lift"] = {
                "runtime_compact_source_digest": dg(compact_source),
                "compactification_identity": True,
                "compactification_trace": trace,
            }
        certs.append(value)
        cert_cache[key] = value
        return value

    zero_leaves = sorted(
        [n for n in c["node_carriers"] if n["kind"] == "leaf" and n["B_v_rref"] == []],
        key=lambda n: idk(n["leaf_factor_id"]),
    )
    for leaf in zero_leaves:
        order.append(leaf["leaf_factor_id"])
        event("ZERO_BOUNDARY_LEAF_PREPRINT", node_id=leaf["node_id"], factor_id=leaf["leaf_factor_id"])

    def final_emit(back: dict, interval: int) -> None:
        node = nodes[back["node_id"]]
        ei = int(back["entry_index"])
        target = node["final_entries"][ei]
        if not 0 <= interval < len(target["trajectory"]) - 1:
            raise AssertionError("final interval")
        if back["kind"] == "leaf":
            if node["kind"] != "leaf" or node["leaf_factor_id"] != back["factor_id"]:
                raise AssertionError("leaf identity")
            lower = target["source_trajectory"]
            cc = cert("LEAF_FINAL_UP", node["node_id"], ei, lower, target["trajectory"], node["B_v_rref"], retained=target["extension_witness"])
            xs = cc["algorithm2_x_sequence_zero_based"]
            for q in range(xs[interval], xs[interval + 1]):
                if len(lower) == 2 and q == 0:
                    order.append(back["factor_id"])
                    event("LEAF_PRINT", node_id=node["node_id"], factor_id=back["factor_id"], parent_interval=interval, leaf_interval=q)
                elif len(lower) == 1:
                    continue
                else:
                    raise AssertionError("leaf interval")
            return
        if node["kind"] != "internal":
            raise AssertionError("internal identity")
        si = int(back["shrink_generator_index"])
        shrink = node["shrink_generators"][si]
        if int(target["source_index"]) != si or target["source_trajectory"] != shrink["shrunk_generator"]:
            raise AssertionError("final source ancestry")
        raw_shrink = shrink["shrink_receipt"]["projected_precompact"]
        cc = cert("FINAL_UP_FROM_PAPER_SHRINK", node["node_id"], ei, raw_shrink, target["trajectory"], node["B_v_rref"], compact_source=target["source_trajectory"], compact_trace=shrink["shrink_receipt"]["compactification_trace"])
        xs = cc["algorithm2_x_sequence_zero_based"]
        event("UP_DISPATCH", stage="FINAL_UP_FROM_PAPER_SHRINK", node_id=node["node_id"], parent_interval=interval, child_interval_start=xs[interval], child_interval_stop=xs[interval + 1])
        for q in range(xs[interval], xs[interval + 1]):
            shrink_emit(back, node, q)

    def shrink_emit(back: dict, node: dict, interval: int) -> None:
        ji = int(back["joined_entry_index"])
        joined = node["joined_entries"][ji]
        shrink = node["shrink_generators"][int(back["shrink_generator_index"])]
        raw_shrink = shrink["shrink_receipt"]["projected_precompact"]
        if int(shrink["joined_entry_index"]) != ji or len(raw_shrink) != len(joined["trajectory"]):
            raise AssertionError("paper shrink identity")
        if not 0 <= interval < len(joined["trajectory"]) - 1:
            raise AssertionError("shrink interval")
        event("SHRINK_IDENTITY_DISPATCH", node_id=node["node_id"], shrink_interval=interval, joined_child_interval=interval)
        joined_up_emit(back, node, interval)

    def joined_up_emit(back: dict, node: dict, interval: int) -> None:
        ji = int(back["joined_entry_index"])
        target = node["joined_entries"][ji]
        gi = int(back["successful_join_generator_index"])
        join = node["successful_join_generators"][gi]
        if int(target["source_index"]) != gi or target["source_trajectory"] != join["joined_generator"]:
            raise AssertionError("joined source ancestry")
        raw_join = join["join_receipt"]["raw_join"]
        cc = cert("JOINED_UP_FROM_RAW_HV_JOIN", node["node_id"], ji, raw_join, target["trajectory"], node["Bprime_v_rref"], compact_source=target["source_trajectory"], compact_trace=join["join_receipt"]["compactification_trace"])
        xs = cc["algorithm2_x_sequence_zero_based"]
        if not 0 <= interval < len(target["trajectory"]) - 1:
            raise AssertionError("joined interval")
        event("UP_DISPATCH", stage="JOINED_UP_FROM_RAW_HV_JOIN", node_id=node["node_id"], parent_interval=interval, child_interval_start=xs[interval], child_interval_stop=xs[interval + 1])
        for q in range(xs[interval], xs[interval + 1]):
            join_emit(back, node, join, q)

    def join_emit(back: dict, node: dict, join: dict, interval: int) -> None:
        path = [[int(v[0]), int(v[1])] for v in join["path"]]
        if path != join["join_receipt"]["path"] or len(path) != len(join["join_receipt"]["raw_join"]):
            raise AssertionError("raw join/path identity")
        if not 0 <= interval < len(path) - 1:
            raise AssertionError("join interval")
        p, q = path[interval], path[interval + 1]
        step = (q[0] - p[0], q[1] - p[1])
        if step == (1, 0):
            event("JOIN_DISPATCH_LEFT", node_id=node["node_id"], join_interval=interval, child_interval=p[0])
            expanded_emit(back["left_child"], node, "left", int(back["left_expanded_entry_index"]), p[0])
        elif step == (0, 1):
            event("JOIN_DISPATCH_RIGHT", node_id=node["node_id"], join_interval=interval, child_interval=p[1])
            expanded_emit(back["right_child"], node, "right", int(back["right_expanded_entry_index"]), p[1])
        else:
            raise AssertionError("ordinary join is not H/V")

    def expanded_emit(child_back: dict, node: dict, side: str, entry_index: int, interval: int) -> None:
        target = node[f"{side}_expanded_entries"][entry_index]
        source_index = int(target["source_index"])
        transport = node[f"{side}_transport_generators"][source_index]
        if int(transport["generator_index"]) != source_index:
            raise AssertionError("transport generator index")
        if int(transport["child_output_entry_index"]) != int(child_back["entry_index"]):
            raise AssertionError("transport child ancestry")
        if target["source_trajectory"] != transport["transported_generator"]:
            raise AssertionError("transported source trajectory")
        cc = cert(f"{side.upper()}_EXPANDED_CHILD_UP", node["node_id"], entry_index, target["source_trajectory"], target["trajectory"], node["Bprime_v_rref"], retained=target["extension_witness"])
        xs = cc["algorithm2_x_sequence_zero_based"]
        if not 0 <= interval < len(target["trajectory"]) - 1:
            raise AssertionError("expanded interval")
        event("UP_DISPATCH", stage=f"{side.upper()}_EXPANDED_CHILD_UP", node_id=node["node_id"], parent_interval=interval, child_interval_start=xs[interval], child_interval_stop=xs[interval + 1])
        for q in range(xs[interval], xs[interval + 1]):
            event("TRANSPORT_IDENTITY_DISPATCH", node_id=node["node_id"], side=side, transported_interval=q, child_output_interval=q)
            final_emit(child_back, q)

    for i in range(len(selected_entry["trajectory"]) - 1):
        final_emit(bt, i)

    cuts, maximum = cut_data(c["canonical_factor_catalog"], order, d)
    if maximum > k:
        raise AssertionError("independently replayed layout exceeds k")
    by = {idk(x["id"]): x for x in c["canonical_factor_catalog"]}
    layout = [
        {"position": i, "factor_id": factor_id, "normal_space": by[idk(factor_id)]["normal_space"], "affine_offset": by[idk(factor_id)]["affine_offset"]}
        for i, factor_id in enumerate(order)
    ]
    return {
        "empty": False,
        "selected": selected,
        "root_width": t_width(selected_entry["trajectory"]),
        "root_digest": dg(selected_entry["trajectory"]),
        "root_key": [t_width(selected_entry["trajectory"]), dg(selected_entry["trajectory"]), selected],
        "certificates": certs,
        "events": events,
        "order": order,
        "layout": layout,
        "cuts": cuts,
        "max_width": maximum,
    }


def verify(candidate: dict, spec: dict, raw_input: dict, b5_1: dict, carrier: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA or spec.get("status") != "SPEC_FROZEN_CANDIDATE_ONLY":
        raise AssertionError("spec")
    if candidate.get("schema") != SCHEMA:
        raise AssertionError("candidate schema")
    if candidate.get("semantic_digest_scope") != "proof_payload" or candidate.get("semantic_digest") != dg(candidate["proof_payload"]):
        raise AssertionError("candidate semantic digest")
    p = candidate["proof_payload"]
    if p.get("gate") != spec["gate"] or p.get("status") != "CANDIDATE_PENDING_EXACT_HEAD_CI_AND_REVIEW":
        raise AssertionError("candidate gate/status")
    expected = reconstruct(raw_input, b5_1, carrier)
    if p.get("carrier_semantic_digest") != carrier["semantic_digest"] or p.get("b5_1_semantic_digest") != b5_1["semantic_digest"]:
        raise AssertionError("upstream digest binding")
    if p.get("canonical_factor_catalog") != carrier["proof_payload"]["canonical_factor_catalog"]:
        raise AssertionError("catalog binding")
    policy = p.get("compactification_lift_policy", {})
    if policy != {
        "join_node_trajectory": "RAW_NONCOMPACT_HV_JOIN",
        "shrink_node_trajectory": "PROJECTED_PRECOMPACT",
        "compact_runtime_sources_used_only_as_projection_bindings": True,
        "b5_2a_slack_metadata_used_by_printorder": False,
    }:
        raise AssertionError("compactification lift policy")

    if expected["empty"]:
        if p.get("reconstruction_status") != "NOT_APPLICABLE_EMPTY_ROOT":
            raise AssertionError("empty status")
        for field in ("selected_root_entry_index", "selected_root_width", "factor_order_ids", "layout_records", "cut_certificates", "maximum_cut_width"):
            if p.get(field) is not None:
                raise AssertionError("empty root emitted reconstruction field: " + field)
        if p.get("paper_faithful_lift_certificates") != [] or p.get("printorder_event_trace") != []:
            raise AssertionError("empty root emitted printorder certificate")
        if p.get("candidate_found_layout") is not False or p.get("found_layout_promotion") != "FORBIDDEN":
            raise AssertionError("empty root terminal promotion")
        return expected

    comparisons = {
        "selected_root_entry_index": expected["selected"],
        "selected_root_trajectory_digest": expected["root_digest"],
        "selected_root_width": expected["root_width"],
        "root_selection_key": expected["root_key"],
        "paper_faithful_lift_certificates": expected["certificates"],
        "printorder_event_trace": expected["events"],
        "factor_order_ids": expected["order"],
        "layout_records": expected["layout"],
        "cut_certificates": expected["cuts"],
        "maximum_cut_width": expected["max_width"],
    }
    for field, value in comparisons.items():
        if p.get(field) != value:
            raise AssertionError("candidate mismatch: " + field)
    if p.get("reconstruction_status") != "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW":
        raise AssertionError("reconstruction status")
    if p.get("candidate_found_layout") is not True:
        raise AssertionError("candidate local layout flag")
    if p.get("found_layout_promotion") != "FORBIDDEN_PENDING_B5_2B_EXACT_HEAD_CI_AND_REVIEW":
        raise AssertionError("premature FOUND_LAYOUT promotion")
    if expected["max_width"] > int(raw_input["k"]):
        raise AssertionError("width cap")
    strict = p.get("strict_boundary")
    if strict != spec["strict_boundary"]:
        raise AssertionError("strict boundary altered")
    return expected


def repair(candidate: dict) -> dict:
    candidate["semantic_digest"] = dg(candidate["proof_payload"])
    return candidate


def tamper_suite(nonempty: dict, empty: dict, spec: dict, nonempty_subject: tuple[dict, dict, dict], empty_subject: tuple[dict, dict, dict]) -> tuple[int, int]:
    raw, b5, carrier = nonempty_subject
    eraw, eb5, ecarrier = empty_subject
    attacks: list[tuple[str, dict, tuple[dict, dict, dict]]] = []

    def add(name: str, base: dict, subject: tuple[dict, dict, dict], mutation) -> None:
        c = copy.deepcopy(base)
        mutation(c["proof_payload"])
        attacks.append((name, repair(c), subject))

    def cert_by_stage(p: dict, stage: str) -> dict:
        return next(x for x in p["paper_faithful_lift_certificates"] if x["stage"] == stage)

    def first_event(p: dict, kind: str) -> dict:
        return next(x for x in p["printorder_event_trace"] if x["kind"] == kind)

    add("T01_NONMIN_ROOT", nonempty, nonempty_subject, lambda p: p.__setitem__("selected_root_entry_index", 1 if p["selected_root_entry_index"] == 0 else 0))
    add("T02_ROOT_TIE_BREAK", nonempty, nonempty_subject, lambda p: p["root_selection_key"].__setitem__(1, "0" * 64))
    add("T03_FINAL_LIFT_WITNESS", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "FINAL_UP_FROM_PAPER_SHRINK")["extension_preorder_witness"]["path"].__setitem__(0, [999, 999]))
    add("T04_FINAL_X", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "FINAL_UP_FROM_PAPER_SHRINK")["algorithm2_x_sequence_zero_based"].__setitem__(0, 999))
    add("T05_COMPACT_SHRINK_AS_PAPER_NODE", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "FINAL_UP_FROM_PAPER_SHRINK").__setitem__("lower_trajectory_digest", cert_by_stage(p, "FINAL_UP_FROM_PAPER_SHRINK")["compactification_lift"]["runtime_compact_source_digest"]))
    add("T06_SHRINK_INDEX", nonempty, nonempty_subject, lambda p: first_event(p, "SHRINK_IDENTITY_DISPATCH").__setitem__("joined_child_interval", 999))
    add("T07_JOIN_LIFT_WITNESS", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "JOINED_UP_FROM_RAW_HV_JOIN")["extension_preorder_witness"]["path"].__setitem__(0, [999, 999]))
    add("T08_JOIN_X", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "JOINED_UP_FROM_RAW_HV_JOIN")["algorithm2_x_sequence_zero_based"].__setitem__(0, 999))
    add("T09_COMPACT_JOIN_AS_HV_NODE", nonempty, nonempty_subject, lambda p: cert_by_stage(p, "JOINED_UP_FROM_RAW_HV_JOIN").__setitem__("lower_trajectory_digest", cert_by_stage(p, "JOINED_UP_FROM_RAW_HV_JOIN")["compactification_lift"]["runtime_compact_source_digest"]))
    add("T10_DIAGONAL_JOIN_DISPATCH", nonempty, nonempty_subject, lambda p: first_event(p, "JOIN_DISPATCH_LEFT" if any(e["kind"] == "JOIN_DISPATCH_LEFT" for e in p["printorder_event_trace"]) else "JOIN_DISPATCH_RIGHT").__setitem__("kind", "JOIN_DISPATCH_DIAGONAL"))
    add("T11_REVERSE_JOIN_DISPATCH", nonempty, nonempty_subject, lambda p: first_event(p, "JOIN_DISPATCH_LEFT" if any(e["kind"] == "JOIN_DISPATCH_LEFT" for e in p["printorder_event_trace"]) else "JOIN_DISPATCH_RIGHT").__setitem__("kind", "JOIN_DISPATCH_RIGHT" if any(e["kind"] == "JOIN_DISPATCH_LEFT" for e in p["printorder_event_trace"]) else "JOIN_DISPATCH_LEFT"))
    add("T12_EXPANDED_X", nonempty, nonempty_subject, lambda p: next(x for x in p["paper_faithful_lift_certificates"] if "EXPANDED_CHILD_UP" in x["stage"])["algorithm2_x_sequence_zero_based"].__setitem__(0, 999))
    add("T13_CHILD_ANCESTRY", nonempty, nonempty_subject, lambda p: first_event(p, "TRANSPORT_IDENTITY_DISPATCH").__setitem__("child_output_interval", 999))
    add("T14_DUPLICATE_FACTOR", nonempty, nonempty_subject, lambda p: p["factor_order_ids"].__setitem__(-1, p["factor_order_ids"][0]))
    add("T15_OMIT_FACTOR", nonempty, nonempty_subject, lambda p: p["factor_order_ids"].pop())
    add("T16_UNKNOWN_FACTOR", nonempty, nonempty_subject, lambda p: p["factor_order_ids"].__setitem__(0, "__unknown_factor__"))
    add("T17_SPLIT_REPLACE_FACTOR", nonempty, nonempty_subject, lambda p: p["layout_records"][0].__setitem__("normal_space", []))
    add("T18_AFFINE_OFFSET", nonempty, nonempty_subject, lambda p: p["layout_records"][0].__setitem__("affine_offset", {"tamper": True}))
    add("T19_CUT_BOUNDARY", nonempty, nonempty_subject, lambda p: p["cut_certificates"][1].__setitem__("boundary_rref", [999]))
    add("T20_MAX_WIDTH", nonempty, nonempty_subject, lambda p: p.__setitem__("maximum_cut_width", 0 if p["maximum_cut_width"] != 0 else 999))
    add("T21_ORDER_REPLAY", nonempty, nonempty_subject, lambda p: p["factor_order_ids"].__setitem__(slice(0, 2), list(reversed(p["factor_order_ids"][:2]))))
    add("T22_EMPTY_ROOT_FAKE_ORDER", empty, empty_subject, lambda p: p.update({"factor_order_ids": ["fake"], "layout_records": [{"factor_id": "fake"}], "candidate_found_layout": True}))
    add("T23_PREMATURE_FOUND_LAYOUT", nonempty, nonempty_subject, lambda p: p.__setitem__("found_layout_promotion", "TRUE"))
    add("T24_GLOBAL_PROMOTION", nonempty, nonempty_subject, lambda p: p["strict_boundary"].update({"generic_no_layout_at_cap": "TRUE", "polynomial_runtime": "TRUE", "b5_complete": True, "p_vs_np": "CLOSED"}))

    rejected = 0
    for name, candidate, subject in attacks:
        sr, sb, sc = subject
        try:
            verify(candidate, spec, sr, sb, sc)
        except Exception:
            rejected += 1
            continue
        raise AssertionError(name + " survived")
    return rejected, len(attacks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--b5-1-artifact", type=Path, required=True)
    parser.add_argument("--carrier", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--tamper-suite", action="store_true")
    parser.add_argument("--empty-input", type=Path)
    parser.add_argument("--empty-b5-1-artifact", type=Path)
    parser.add_argument("--empty-carrier", type=Path)
    parser.add_argument("--empty-candidate", type=Path)
    args = parser.parse_args()

    spec = load(args.spec)
    raw = load(args.input)
    b5 = load(args.b5_1_artifact)
    carrier = load(args.carrier)
    candidate = load(args.candidate)
    expected = verify(candidate, spec, raw, b5, carrier)

    print("JANUS_B5_2B_GENERIC_ALGORITHM2_PRINTORDER_INDEPENDENT_VERIFIER = PASS")
    print("RECONSTRUCTION_STATUS =", "NOT_APPLICABLE_EMPTY_ROOT" if expected["empty"] else "LAYOUT_CANDIDATE_RECONSTRUCTED_PENDING_REVIEW")
    print("INDEPENDENT_ROOT_SELECTION = PASS")
    print("PAPER_RAW_JOIN_LIFT = PASS")
    print("PAPER_PRECOMPACT_SHRINK_LIFT = PASS")
    print("ALGORITHM2_X_SEQUENCE_REPLAY = PASS")
    print("B5_2A_SLACK_METADATA_USED_BY_PRINTORDER = FALSE")
    print("INDEPENDENT_PRINTORDER_REPLAY = PASS")
    print("WHOLE_FACTOR_PERMUTATION =", "N/A_EMPTY_ROOT" if expected["empty"] else "PASS")
    print("INDEPENDENT_CUT_WIDTH_RECOMPUTATION =", "N/A_EMPTY_ROOT" if expected["empty"] else "PASS")
    print("MAXIMUM_CUT_WIDTH =", expected["max_width"])
    print("GENERIC_FOUND_LAYOUT = FORBIDDEN_PENDING_REVIEW")
    print("GENERIC_NO_LAYOUT_AT_CAP = FORBIDDEN_PENDING_B5_3")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")

    if args.tamper_suite:
        required = [args.empty_input, args.empty_b5_1_artifact, args.empty_carrier, args.empty_candidate]
        if any(x is None for x in required):
            raise AssertionError("tamper suite requires empty-root subject")
        empty_subject = (load(args.empty_input), load(args.empty_b5_1_artifact), load(args.empty_carrier))
        rejected, total = tamper_suite(
            candidate,
            load(args.empty_candidate),
            spec,
            (raw, b5, carrier),
            empty_subject,
        )
        print(f"DIGEST_REPAIRED_TAMPERS_REJECTED = {rejected}/{total}")


if __name__ == "__main__":
    main()
