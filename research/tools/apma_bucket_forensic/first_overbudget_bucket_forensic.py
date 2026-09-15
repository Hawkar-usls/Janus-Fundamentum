from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut

ARTIFACT_ID = "JANUS-TRUMP-CAPTAIN-FIRST-OVERBUDGET-BUCKET-FORENSIC-2026-09-15-v1.0"
AUTHORITY = "DIAGNOSTIC_ONLY__NO_THEOREM_PROMOTION"
PREREG = Path("research/TRUMP_CAPTAIN_FIRST_OVERBUDGET_BUCKET_FORENSIC_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "36fe958ef1f521f5a12b6eca0ee57a10d3f439eb"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.2.json")
PARENT_STATE_BLOB = "2bf75f78e1115d31d51a35b37b7cb2d9e78079af"
GUARDED = Path("research/tools/apma_guarded_elimination/guarded_bounded_output_elimination.py")
GUARDED_BLOB = "314034bac990e524d1db7743aef0aebd3b4565c1"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict:
    r = root()
    checks = {
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "guarded_candidate_blob": git_blob_sha1(r / GUARDED) == GUARDED_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def _factor_from_relation(rel: dict, index: int) -> dict:
    original_scope = list(rel["scope"])
    scope = sorted(original_scope)
    pos = {v: i for i, v in enumerate(original_scope)}
    rows = sorted({tuple(int(raw[pos[v]]) for v in scope) for raw in rel["allowed"]})
    return {"id": f"orig:{index}", "relation_id": rel.get("id", f"r{index}"), "scope": scope, "rows": rows, "relation_index": index}


def _product(counts: list[int]) -> int:
    out = 1
    for x in counts:
        out *= int(x)
    return out


def _join_two(left_scope: tuple[int, ...], left_rows: set[tuple[int, ...]], right: dict) -> tuple[tuple[int, ...], set[tuple[int, ...]], dict]:
    rs = tuple(right["scope"])
    shared = tuple(v for v in left_scope if v in set(rs))
    lpos = [left_scope.index(v) for v in shared]
    rpos = [rs.index(v) for v in shared]
    index: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
    for row in right["rows"]:
        key = tuple(row[i] for i in rpos)
        index.setdefault(key, []).append(row)
    merged_scope = tuple(sorted(set(left_scope) | set(rs)))
    lmap = {v: i for i, v in enumerate(left_scope)}
    rmap = {v: i for i, v in enumerate(rs)}
    out: set[tuple[int, ...]] = set()
    probes = 0
    compatible_pairs = 0
    for lrow in left_rows:
        key = tuple(lrow[i] for i in lpos)
        matches = index.get(key, [])
        probes += 1
        compatible_pairs += len(matches)
        for rrow in matches:
            out.add(tuple(lrow[lmap[v]] if v in lmap else rrow[rmap[v]] for v in merged_scope))
    return merged_scope, out, {"shared_variables": list(shared), "hash_probes": probes, "compatible_pairs": compatible_pairs, "output_rows": len(out)}


def progressive_profile(bucket: list[dict]) -> dict:
    ordered = list(bucket)
    first = ordered[0]
    scope = tuple(first["scope"])
    rows = set(first["rows"])
    steps = [{
        "factor_id": first["id"],
        "relation_id": first["relation_id"],
        "factor_rows": len(first["rows"]),
        "progressive_rows": len(rows),
        "scope_size": len(scope),
        "compatible_pairs": len(rows),
    }]
    for factor in ordered[1:]:
        scope, rows, stats = _join_two(scope, rows, factor)
        steps.append({
            "factor_id": factor["id"],
            "relation_id": factor["relation_id"],
            "factor_rows": len(factor["rows"]),
            "progressive_rows": len(rows),
            "scope_size": len(scope),
            **stats,
        })
        if not rows:
            break
    return {"order": [f["id"] for f in ordered], "steps": steps, "final_compatible_rows": len(rows), "final_scope_size": len(scope)}


def pairwise_profile(bucket: list[dict]) -> list[dict]:
    out = []
    for i in range(len(bucket)):
        for j in range(i + 1, len(bucket)):
            a, b = bucket[i], bucket[j]
            shared = sorted(set(a["scope"]) & set(b["scope"]))
            apos = [a["scope"].index(v) for v in shared]
            bpos = [b["scope"].index(v) for v in shared]
            ai: dict[tuple[int, ...], int] = {}
            bi: dict[tuple[int, ...], int] = {}
            for row in a["rows"]:
                key = tuple(row[p] for p in apos)
                ai[key] = ai.get(key, 0) + 1
            for row in b["rows"]:
                key = tuple(row[p] for p in bpos)
                bi[key] = bi.get(key, 0) + 1
            compatible = sum(ai[k] * bi.get(k, 0) for k in ai)
            out.append({
                "a": a["id"], "b": b["id"],
                "shared_variables": shared,
                "shared_count": len(shared),
                "a_projection_signatures": len(ai),
                "b_projection_signatures": len(bi),
                "compatible_row_pairs": compatible,
                "raw_row_pairs": len(a["rows"]) * len(b["rows"]),
            })
    return out


def graph_profile(bucket: list[dict]) -> dict:
    adjacency = {f["id"]: [] for f in bucket}
    edges = []
    for i in range(len(bucket)):
        for j in range(i + 1, len(bucket)):
            shared = sorted(set(bucket[i]["scope"]) & set(bucket[j]["scope"]))
            if shared:
                a, b = bucket[i]["id"], bucket[j]["id"]
                adjacency[a].append(b)
                adjacency[b].append(a)
                edges.append({"a": a, "b": b, "shared_variables": shared, "shared_count": len(shared)})
    seen = set()
    components = []
    for node in adjacency:
        if node in seen:
            continue
        stack = [node]
        comp = []
        seen.add(node)
        while stack:
            x = stack.pop()
            comp.append(x)
            for y in adjacency[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        components.append(sorted(comp))
    all_scopes = [set(f["scope"]) for f in bucket]
    common = sorted(set.intersection(*all_scopes)) if all_scopes else []
    projection_counts = []
    for f in bucket:
        pos = [f["scope"].index(v) for v in common]
        sigs = {tuple(row[p] for p in pos) for row in f["rows"]}
        projection_counts.append({"factor_id": f["id"], "relation_id": f["relation_id"], "common_core_projection_signatures": len(sigs)})
    variable_degree: dict[int, int] = {}
    for f in bucket:
        for v in f["scope"]:
            variable_degree[v] = variable_degree.get(v, 0) + 1
    return {
        "node_count": len(bucket),
        "edge_count": len(edges),
        "components": components,
        "connected": len(components) == 1,
        "common_shared_core": common,
        "common_shared_core_size": len(common),
        "common_core_projection_counts": projection_counts,
        "variable_factor_degrees": {str(v): d for v, d in sorted(variable_degree.items())},
        "edges": edges,
    }


def extract_first_failed_bucket() -> dict:
    raw = guarded.overbudget_control()
    canonical = canonicalize_raw(raw)
    replay = guarded.explain(raw)
    if replay.get("status") != "OPEN_BUCKET_PRODUCT_BUDGET":
        raise AssertionError(f"EXPECTED_OPEN_BUCKET_PRODUCT_BUDGET_GOT_{replay.get('status')}")
    failed = replay["carrier"]["failed_bucket"]
    failed_var = int(failed["variable"])
    if failed_var != 20:
        raise AssertionError(f"EXPECTED_FAILED_VAR_20_GOT_{failed_var}")
    if replay["carrier"]["resource_receipt"].get("failed_bucket_combinations_enumerated") != 0:
        raise AssertionError("FAILED_BUCKET_WAS_ENUMERATED")

    cut = list(replay["parent_cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    target_component = None
    for comp in components:
        if any(failed_var in canonical["constraints"][gi]["scope"] for gi in comp):
            target_component = comp
            break
    if target_component is None:
        raise AssertionError("FAILED_VARIABLE_COMPONENT_NOT_FOUND")
    factors = [_factor_from_relation(canonical["constraints"][gi], gi) for gi in target_component]
    bucket = [f for f in factors if failed_var in f["scope"]]
    failed_ids = list(failed["bucket_factor_ids"])
    if [f["id"] for f in bucket] != failed_ids:
        raise AssertionError({"candidate_failed_ids": failed_ids, "reconstructed_ids": [f["id"] for f in bucket]})
    return {"raw": raw, "canonical": canonical, "replay": replay, "failed": failed, "cut": cut, "components": components, "component": target_component, "bucket": bucket}


def run() -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "HALT_SOURCE_GUARD", "source_guard": guard}
    x = extract_first_failed_bucket()
    bucket = x["bucket"]
    counts = [len(f["rows"]) for f in bucket]
    raw_product = _product(counts)
    L = int(x["replay"]["carrier"]["L"])
    L2 = int(x["replay"]["carrier"]["budget"])
    progressive = progressive_profile(bucket)
    pairwise = pairwise_profile(bucket)
    graph = graph_profile(bucket)
    result = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": "DIAGNOSTIC_COMPLETE",
        "source_guard": guard,
        "target": {
            "parent_terminal": x["replay"]["status"],
            "first_failed_variable": int(x["failed"]["variable"]),
            "failed_bucket_factor_ids": [f["id"] for f in bucket],
            "failed_bucket_relation_ids": [f["relation_id"] for f in bucket],
            "factor_count": len(bucket),
            "factor_row_counts": counts,
            "L": L,
            "L2": L2,
            "candidate_guard_capped_product": x["failed"].get("pre_expansion_capped_product"),
            "failed_bucket_combinations_enumerated": x["replay"]["carrier"]["resource_receipt"].get("failed_bucket_combinations_enumerated"),
        },
        "raw_product": {
            "exact": raw_product,
            "over_L2": raw_product > L2,
            "ratio_to_L2": raw_product / L2,
            "log2_raw_product": math.log2(raw_product) if raw_product else 0.0,
        },
        "progressive_compatibility": progressive,
        "pairwise": pairwise,
        "factor_graph": graph,
        "interpretation": {
            "finite_control_only": True,
            "theorem_promotion": False,
            "small_effective_space_if_observed_is_mechanism_discovery_evidence_only": True,
            "next_step_must_be_preregistered_after_this_result": True,
        },
        "scientific_firewall": {
            "P_VS_NP": "OPEN",
            "GENERAL_SAT_IN_P": "NOT_PROVED",
            "CONNECTED_MIXED_CORE_SOLVED": "NO",
            "GENERAL_EFFECTIVE_BUCKET_COMPRESSION": "NOT_PROVED",
            "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
        },
    }
    return result


def main() -> None:
    print(json.dumps(run(), sort_keys=True))


if __name__ == "__main__":
    main()
