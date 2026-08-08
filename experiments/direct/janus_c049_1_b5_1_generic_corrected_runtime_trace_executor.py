from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Sequence

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


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def save(value: Any, path: Path) -> None:
    path.write_bytes(canonical_bytes(value) + b"\n")


def basis_list(space: Sequence[int]) -> list[int]:
    return list(space)


def subset_of(a: Sequence[int], b: Sequence[int]) -> bool:
    """Return whether span(a) <= span(b)."""
    return contains(tuple(b), tuple(a))


def trajectory_key(raw: Sequence[dict]) -> str:
    return digest(raw)


def full_set_digest(entries: Sequence[dict]) -> str:
    payload = sorted((trajectory_key(e["trajectory"]) for e in entries))
    return digest(payload)


def normalized_entries(upk_receipt: dict) -> list[dict]:
    entries = [
        {
            "trajectory": e["trajectory"],
            "source_index": int(e["source_index"]),
            "witness": e["witness"],
        }
        for e in upk_receipt.get("entries", [])
    ]
    return sorted(entries, key=lambda e: (trajectory_key(e["trajectory"]), e["source_index"], digest(e["witness"])))


def safe_up_k(
    generators: Sequence[Sequence[Statistic]],
    boundary: Sequence[int],
    ambient_dim: int,
    k: int,
    caps: dict,
    stage: str,
) -> tuple[dict | None, dict]:
    B = xor_basis(boundary, ambient_dim)
    if len(B) > caps["max_boundary_dim"]:
        return None, {
            "status": OPEN,
            "reason": "BOUNDARY_DIM_CAP",
            "stage": stage,
            "observed": len(B),
            "cap": caps["max_boundary_dim"],
        }
    if k > caps["max_k"]:
        return None, {
            "status": OPEN,
            "reason": "K_CAP",
            "stage": stage,
            "observed": k,
            "cap": caps["max_k"],
        }
    if not generators:
        receipt = {
            "boundary": basis_list(B),
            "k": k,
            "generator_count": 0,
            "universe_size": None,
            "entry_count": 0,
            "entries": [],
            "empty_source_shortcut": True,
            "semantic_identity": "UP_K_EMPTY_SOURCE_EQUALS_EMPTY",
        }
        return receipt, {
            "status": CLOSED,
            "stage": stage,
            "empty_source_shortcut": True,
            "generator_count": 0,
            "entry_count": 0,
            "universe_size": None,
        }
    receipt = up_k(generators, B, ambient_dim, k)
    receipt["entries"] = normalized_entries(receipt)
    receipt["empty_source_shortcut"] = False
    if receipt["entry_count"] > caps["max_full_set_entries"]:
        return None, {
            "status": OPEN,
            "reason": "FULL_SET_ENTRY_CAP",
            "stage": stage,
            "observed": receipt["entry_count"],
            "cap": caps["max_full_set_entries"],
            "computed_before_commit": True,
        }
    return receipt, {
        "status": CLOSED,
        "stage": stage,
        "empty_source_shortcut": False,
        "generator_count": receipt["generator_count"],
        "entry_count": receipt["entry_count"],
        "universe_size": receipt["universe_size"],
    }


def validate_input(raw: dict) -> tuple[int, int, list[dict], dict, dict, str]:
    d = int(raw["ambient_dim"])
    k = int(raw["k"])
    if d <= 0 or k < 0:
        raise ValueError("ambient_dim must be positive and k nonnegative")
    factors_raw = raw.get("factors")
    if not isinstance(factors_raw, list) or not factors_raw:
        raise ValueError("nonempty factor catalog required")
    seen: set[str] = set()
    factors: list[dict] = []
    for item in factors_raw:
        fid = str(item["id"])
        if not fid or fid in seen:
            raise ValueError("factor IDs must be unique nonempty strings")
        seen.add(fid)
        normal = xor_basis(item.get("normal_space", []), d)
        factors.append({
            "id": fid,
            "normal_space": basis_list(normal),
            "affine_offset": item.get("affine_offset"),
        })
    factors.sort(key=lambda x: x["id"])
    factor_map = {f["id"]: f for f in factors}

    tree_raw = raw.get("tree")
    if not isinstance(tree_raw, dict):
        raise ValueError("tree object required")
    root = str(tree_raw["root"])
    nodes_raw = tree_raw.get("nodes")
    if not isinstance(nodes_raw, list) or not nodes_raw:
        raise ValueError("nonempty tree nodes required")
    nodes: dict[str, dict] = {}
    for item in nodes_raw:
        nid = str(item["id"])
        if not nid or nid in nodes:
            raise ValueError("node IDs must be unique nonempty strings")
        leaf = "factor_id" in item
        internal = "left" in item or "right" in item
        if leaf == internal:
            raise ValueError("each node must be exactly leaf or internal")
        if leaf:
            nodes[nid] = {"id": nid, "kind": "leaf", "factor_id": str(item["factor_id"])}
        else:
            if "left" not in item or "right" not in item:
                raise ValueError("internal node requires left and right")
            left, right = str(item["left"]), str(item["right"])
            if left == right:
                raise ValueError("binary children must differ")
            nodes[nid] = {"id": nid, "kind": "internal", "left": left, "right": right}
    if root not in nodes:
        raise ValueError("root missing")

    state: dict[str, int] = {}
    postorder: list[str] = []
    leaf_ids: list[str] = []

    def walk(nid: str) -> None:
        if nid not in nodes:
            raise ValueError(f"missing child node {nid}")
        mark = state.get(nid, 0)
        if mark == 1:
            raise ValueError("cycle in tree")
        if mark == 2:
            raise ValueError("node has multiple parents or repeated subtree")
        state[nid] = 1
        node = nodes[nid]
        if node["kind"] == "leaf":
            fid = node["factor_id"]
            if fid not in factor_map:
                raise ValueError("leaf references unknown factor")
            leaf_ids.append(fid)
        else:
            walk(node["left"])
            walk(node["right"])
        state[nid] = 2
        postorder.append(nid)

    walk(root)
    if len(state) != len(nodes):
        raise ValueError("unreachable tree node")
    if sorted(leaf_ids) != sorted(factor_map) or len(leaf_ids) != len(set(leaf_ids)):
        raise ValueError("tree leaves must cover every factor exactly once")

    default_caps = {
        "max_boundary_dim": max(0, min(d, 3)),
        "max_k": max(k, 1),
        "max_full_set_entries": 10000,
        "max_child_pairs": 200000,
        "max_join_paths": 2000000,
    }
    caps = dict(default_caps)
    caps.update(raw.get("caps", {}))
    for name in default_caps:
        caps[name] = int(caps[name])
        if caps[name] < 0:
            raise ValueError("negative capability cap")

    canonical_tree = {
        "root": root,
        "nodes": [nodes[nid] for nid in sorted(nodes)],
    }
    return d, k, factors, nodes, caps, root, postorder, canonical_tree


def compute_coverages(
    postorder: Sequence[str], nodes: dict[str, dict], factors: dict[str, dict], d: int
) -> tuple[dict[str, tuple[str, ...]], dict[str, tuple[int, ...]], tuple[int, ...]]:
    covers: dict[str, tuple[str, ...]] = {}
    V: dict[str, tuple[int, ...]] = {}
    all_vectors: list[int] = []
    for f in factors.values():
        all_vectors.extend(f["normal_space"])
    all_span = xor_basis(all_vectors, d)
    for nid in postorder:
        node = nodes[nid]
        if node["kind"] == "leaf":
            ids = (node["factor_id"],)
        else:
            ids = tuple(sorted((*covers[node["left"]], *covers[node["right"]])))
        covers[nid] = ids
        vecs: list[int] = []
        for fid in ids:
            vecs.extend(factors[fid]["normal_space"])
        V[nid] = xor_basis(vecs, d)
    return covers, V, all_span


def compute_boundaries(
    postorder: Sequence[str], covers: dict[str, tuple[str, ...]], V: dict[str, tuple[int, ...]],
    factors: dict[str, dict], d: int
) -> dict[str, tuple[int, ...]]:
    all_ids = set(factors)
    out: dict[str, tuple[int, ...]] = {}
    for nid in postorder:
        outside = sorted(all_ids - set(covers[nid]))
        vecs: list[int] = []
        for fid in outside:
            vecs.extend(factors[fid]["normal_space"])
        V_out = xor_basis(vecs, d)
        out[nid] = subspace_intersection(V[nid], V_out, d)
    return out


def caller_premises(
    V_left: Sequence[int], V_right: Sequence[int], B_left: Sequence[int], B_right: Sequence[int],
    B_parent: Sequence[int], Bprime: Sequence[int], d: int
) -> dict:
    l_inter = subspace_intersection(V_left, Bprime, d)
    r_inter = subspace_intersection(V_right, Bprime, d)
    separation = subspace_intersection(
        subspace_sum(V_left, Bprime, d), subspace_sum(V_right, Bprime, d), d
    )
    checks = {
        "B_left_le_Bprime": subset_of(B_left, Bprime),
        "span_left_inter_Bprime_le_B_left": subset_of(l_inter, B_left),
        "B_right_le_Bprime": subset_of(B_right, Bprime),
        "span_right_inter_Bprime_le_B_right": subset_of(r_inter, B_right),
        "join_separation_equals_Bprime": tuple(separation) == tuple(xor_basis(Bprime, d)),
        "B_parent_le_Bprime": subset_of(B_parent, Bprime),
    }
    return {
        "checks": checks,
        "left_intersection": basis_list(l_inter),
        "right_intersection": basis_list(r_inter),
        "join_separation": basis_list(separation),
        "all_pass": all(checks.values()),
    }


def entries_to_trajectories(entries: Sequence[dict], boundary: Sequence[int], d: int) -> list[tuple[Statistic, ...]]:
    return [decode_trajectory(e["trajectory"], boundary, d, require_compact=True) for e in entries]


def open_artifact(
    base: dict, node_receipts: dict[str, dict], work: dict, stop_node: str, reason: dict
) -> dict:
    proof = dict(base)
    proof.update({
        "capability_status": OPEN,
        "stop_node": stop_node,
        "open_reason": reason,
        "node_receipts": [node_receipts[n] for n in sorted(node_receipts)],
        "root_full_set_digest_if_closed": None,
        "root_entry_count_if_closed": None,
        "global_work_ledger": work,
        "terminal_promotion": "NONE",
        "strict_boundary": {
            "generic_runtime_trace_mapping_candidate": False,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "polynomial_runtime_claim": "FORBIDDEN",
            "b5_complete": False,
            "p_vs_np": "OPEN",
        },
    })
    art = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": proof}
    art["semantic_digest"] = digest(proof)
    return art


def execute(raw: dict, spec: dict) -> dict:
    if spec.get("schema") != SPEC_SCHEMA:
        raise ValueError("wrong B5.1 spec")
    d, k, factor_list, nodes, caps, root, postorder, canonical_tree = validate_input(raw)
    factors = {f["id"]: f for f in factor_list}
    covers, V, all_span = compute_coverages(postorder, nodes, factors, d)
    B = compute_boundaries(postorder, covers, V, factors, d)
    if B[root] != ():
        raise AssertionError("canonical root boundary must be zero")

    base = {
        "ambient_dim": d,
        "k": k,
        "caps": caps,
        "canonical_factor_catalog": factor_list,
        "canonical_tree": canonical_tree,
        "root_id": root,
        "postorder": list(postorder),
        "all_factor_ids_exactly_once": True,
        "root_covers_all_factors": set(covers[root]) == set(factors),
        "all_input_span_rref": basis_list(all_span),
        "ordinary_join_steps": [list(x) for x in JOIN_INTERLEAVING_STEPS],
        "extension_preorder_steps": [list(x) for x in EXTENSION_PREORDER_STEPS],
        "affine_offset_identity_ledger": [
            {"factor_id": f["id"], "affine_offset": f["affine_offset"]} for f in factor_list
        ],
        "acceptance_oracles": {
            "fixed_factor_count": None,
            "fixed_ambient_dim": None,
            "fixed_k": None,
            "fixed_factor_vectors": None,
            "historical_layout_count": None,
            "historical_root_refinement_count": None,
            "historical_node_ids": None,
        },
    }

    node_receipts: dict[str, dict] = {}
    node_entries: dict[str, list[dict]] = {}
    work = {
        "leaf_up_k_calls": 0,
        "expand_up_k_calls": 0,
        "join_paths": 0,
        "child_pairs": 0,
        "join_up_k_calls": 0,
        "shrink_trajectories": 0,
        "final_up_k_calls": 0,
        "empty_source_shortcuts": 0,
    }

    for nid in postorder:
        node = nodes[nid]
        factor_identity_records = [
            {"factor_id": fid, "affine_offset": factors[fid]["affine_offset"]} for fid in covers[nid]
        ]
        common = {
            "node_id": nid,
            "kind": node["kind"],
            "covered_factor_ids": list(covers[nid]),
            "factor_identity_records": factor_identity_records,
            "V_v_rref": basis_list(V[nid]),
            "B_v_rref": basis_list(B[nid]),
            "capability_status": CLOSED,
        }
        if node["kind"] == "leaf":
            delta = (Statistic((), B[nid], 0), Statistic(B[nid], (), 0))
            up, urec = safe_up_k([delta], B[nid], d, k, caps, f"{nid}:leaf_up_k")
            work["leaf_up_k_calls"] += 1
            if up is None:
                return open_artifact(base, node_receipts, work, nid, urec)
            if urec.get("empty_source_shortcut"):
                work["empty_source_shortcuts"] += 1
            entries = normalized_entries(up)
            node_entries[nid] = entries
            receipt = dict(common)
            receipt.update({
                "leaf_factor_id": node["factor_id"],
                "delta_B": encode_trajectory(delta),
                "final_up_k_receipt": {**urec, "output_full_set_digest": full_set_digest(entries)},
                "output_full_set_digest": full_set_digest(entries),
                "output_entry_count": len(entries),
                "charged_work": {"up_k_calls": 1},
            })
            node_receipts[nid] = receipt
            continue

        left, right = node["left"], node["right"]
        Bprime = subspace_sum(B[left], B[right], d)
        cp = caller_premises(V[left], V[right], B[left], B[right], B[nid], Bprime, d)
        if not cp["all_pass"]:
            raise AssertionError(f"canonical caller premise failure at {nid}")

        left_child = entries_to_trajectories(node_entries[left], B[left], d)
        right_child = entries_to_trajectories(node_entries[right], B[right], d)

        transported_left: list[tuple[Statistic, ...]] = []
        left_transport_receipts: list[dict] = []
        for gamma in left_child:
            out, tr = expand_trajectory(gamma, B[left], Bprime, d)
            transported_left.append(out)
            left_transport_receipts.append({"source_digest": digest(encode_trajectory(gamma)), "transport": tr})
        transported_right: list[tuple[Statistic, ...]] = []
        right_transport_receipts: list[dict] = []
        for gamma in right_child:
            out, tr = expand_trajectory(gamma, B[right], Bprime, d)
            transported_right.append(out)
            right_transport_receipts.append({"source_digest": digest(encode_trajectory(gamma)), "transport": tr})

        left_up, left_urec = safe_up_k(transported_left, Bprime, d, k, caps, f"{nid}:expand_left_up_k")
        work["expand_up_k_calls"] += 1
        if left_up is None:
            return open_artifact(base, node_receipts, work, nid, left_urec)
        right_up, right_urec = safe_up_k(transported_right, Bprime, d, k, caps, f"{nid}:expand_right_up_k")
        work["expand_up_k_calls"] += 1
        if right_up is None:
            return open_artifact(base, node_receipts, work, nid, right_urec)
        if left_urec.get("empty_source_shortcut"):
            work["empty_source_shortcuts"] += 1
        if right_urec.get("empty_source_shortcut"):
            work["empty_source_shortcuts"] += 1

        left_entries = normalized_entries(left_up)
        right_entries = normalized_entries(right_up)
        pair_count = len(left_entries) * len(right_entries)
        if pair_count > caps["max_child_pairs"]:
            return open_artifact(base, node_receipts, work, nid, {
                "status": OPEN,
                "reason": "CHILD_PAIR_CAP",
                "stage": f"{nid}:join_precheck",
                "observed": pair_count,
                "cap": caps["max_child_pairs"],
            })
        work["child_pairs"] += pair_count

        left_g = entries_to_trajectories(left_entries, Bprime, d)
        right_g = entries_to_trajectories(right_entries, Bprime, d)
        path_total = 0
        for g1 in left_g:
            for g2 in right_g:
                path_total += math.comb((len(g1) - 1) + (len(g2) - 1), len(g1) - 1)
        if path_total > caps["max_join_paths"]:
            return open_artifact(base, node_receipts, work, nid, {
                "status": OPEN,
                "reason": "JOIN_PATH_CAP",
                "stage": f"{nid}:join_precheck",
                "observed": path_total,
                "cap": caps["max_join_paths"],
            })

        successful_join_generators: list[tuple[Statistic, ...]] = []
        join_catalog: list[dict] = []
        for li, g1 in enumerate(left_g):
            for ri, g2 in enumerate(right_g):
                for path in ordinary_join_paths(len(g1), len(g2)):
                    joined, jrec = join_trajectory(g1, g2, path, Bprime, d)
                    accepted = width(joined) <= k
                    if accepted:
                        successful_join_generators.append(joined)
                    join_catalog.append({
                        "left_entry_index": li,
                        "right_entry_index": ri,
                        "path": [list(p) for p in path],
                        "joined_digest": digest(encode_trajectory(joined)),
                        "joined_width": width(joined),
                        "accepted_width_le_k": accepted,
                        "join_receipt_digest": digest(jrec),
                    })
        if len(join_catalog) != path_total:
            raise AssertionError("ordinary H/V join inventory mismatch")
        work["join_paths"] += path_total

        joined_up, joined_urec = safe_up_k(successful_join_generators, Bprime, d, k, caps, f"{nid}:joined_up_k")
        work["join_up_k_calls"] += 1
        if joined_up is None:
            return open_artifact(base, node_receipts, work, nid, joined_urec)
        if joined_urec.get("empty_source_shortcut"):
            work["empty_source_shortcuts"] += 1
        joined_entries = normalized_entries(joined_up)
        joined_g = entries_to_trajectories(joined_entries, Bprime, d)

        shrunk_generators: list[tuple[Statistic, ...]] = []
        shrink_catalog: list[dict] = []
        for gamma in joined_g:
            shrunk, srec = shrink_trajectory(gamma, B[nid], d)
            shrunk_generators.append(shrunk)
            shrink_catalog.append({
                "source_digest": digest(encode_trajectory(gamma)),
                "output_digest": digest(encode_trajectory(shrunk)),
                "receipt_digest": digest(srec),
                "output_width": width(shrunk),
            })
        work["shrink_trajectories"] += len(shrink_catalog)

        final_up, final_urec = safe_up_k(shrunk_generators, B[nid], d, k, caps, f"{nid}:final_up_k")
        work["final_up_k_calls"] += 1
        if final_up is None:
            return open_artifact(base, node_receipts, work, nid, final_urec)
        if final_urec.get("empty_source_shortcut"):
            work["empty_source_shortcuts"] += 1
        final_entries = normalized_entries(final_up)
        node_entries[nid] = final_entries

        receipt = dict(common)
        receipt.update({
            "left_child_id": left,
            "right_child_id": right,
            "child_output_digests": {
                "left": node_receipts[left]["output_full_set_digest"],
                "right": node_receipts[right]["output_full_set_digest"],
            },
            "Bprime_v_rref_if_internal": basis_list(Bprime),
            "caller_premise_certificate_if_internal": cp,
            "expanded_left_receipt_if_internal": {
                "transport_count": len(left_transport_receipts),
                "transport_receipt_digest": digest(left_transport_receipts),
                "up_k": left_urec,
                "output_full_set_digest": full_set_digest(left_entries),
                "output_entry_count": len(left_entries),
            },
            "expanded_right_receipt_if_internal": {
                "transport_count": len(right_transport_receipts),
                "transport_receipt_digest": digest(right_transport_receipts),
                "up_k": right_urec,
                "output_full_set_digest": full_set_digest(right_entries),
                "output_entry_count": len(right_entries),
            },
            "ordinary_join_inventory_if_internal": {
                "child_pair_count": pair_count,
                "ordinary_hv_path_count": path_total,
                "successful_width_le_k_generators": len(successful_join_generators),
                "failed_width_gt_k_generators": path_total - len(successful_join_generators),
                "catalog_digest": digest(join_catalog),
                "diagonal_ordinary_join_steps": 0,
            },
            "joined_up_k_receipt_if_internal": {
                **joined_urec,
                "output_full_set_digest": full_set_digest(joined_entries),
            },
            "shrink_inventory_if_internal": {
                "input_count": len(joined_entries),
                "output_generator_count": len(shrunk_generators),
                "catalog_digest": digest(shrink_catalog),
            },
            "final_up_k_receipt": {
                **final_urec,
                "output_full_set_digest": full_set_digest(final_entries),
            },
            "output_full_set_digest": full_set_digest(final_entries),
            "output_entry_count": len(final_entries),
            "charged_work": {
                "child_pairs": pair_count,
                "ordinary_hv_paths": path_total,
                "successful_join_generators": len(successful_join_generators),
                "shrink_trajectories": len(shrink_catalog),
                "up_k_calls": 4,
            },
        })
        node_receipts[nid] = receipt

    root_entries = node_entries[root]
    proof = dict(base)
    proof.update({
        "capability_status": CLOSED,
        "stop_node": None,
        "open_reason": None,
        "node_receipts": [node_receipts[n] for n in sorted(node_receipts)],
        "root_full_set_digest_if_closed": full_set_digest(root_entries),
        "root_entry_count_if_closed": len(root_entries),
        "global_work_ledger": work,
        "terminal_promotion": "NONE",
        "strict_boundary": {
            "generic_runtime_trace_mapping_candidate": True,
            "found_layout": "FORBIDDEN",
            "no_layout_at_cap": "FORBIDDEN",
            "polynomial_runtime_claim": "FORBIDDEN",
            "b5_complete": False,
            "p_vs_np": "OPEN",
        },
    })
    art = {"schema": SCHEMA, "semantic_digest_scope": "proof_payload", "proof_payload": proof}
    art["semantic_digest"] = digest(proof)
    return art


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--spec", type=Path, required=True)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    spec = load(args.spec)
    raw = load(args.input)
    art = execute(raw, spec)
    save(art, args.output)
    q = art["proof_payload"]
    print("JANUS_B5_1_GENERIC_CORRECTED_RUNTIME_TRACE_EXECUTOR = PASS")
    print("CAPABILITY_STATUS =", q["capability_status"])
    print("FACTOR_COUNT =", len(q["canonical_factor_catalog"]))
    print("AMBIENT_DIM =", q["ambient_dim"])
    print("K =", q["k"])
    print("TREE_NODE_COUNT =", len(q["canonical_tree"]["nodes"]))
    print("ORDINARY_JOIN_DOMAIN = H/V_ONLY")
    print("EXTENSION_PREORDER_DOMAIN = H/V/DIAGONAL")
    print("TERMINAL_PROMOTION = NONE")
    print("GENERIC_FOUND_LAYOUT = FORBIDDEN")
    print("GENERIC_NO_LAYOUT_AT_CAP = FORBIDDEN")
    print("POLYNOMIAL_RUNTIME_CLAIM = FORBIDDEN")
    print("B5_COMPLETE = FALSE")
    print("P_VS_NP = OPEN")
    print("SEMANTIC_DIGEST =", art["semantic_digest"])


if __name__ == "__main__":
    main()
