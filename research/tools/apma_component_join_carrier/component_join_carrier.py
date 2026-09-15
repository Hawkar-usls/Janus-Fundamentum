from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-COMPONENT-BOUNDARY-JOIN-CARRIER-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_COMPONENT_BOUNDARY_JOIN_CARRIER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "a020a0c54995580f8d02e51d931624948060ecfa"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v2.8.json")
PARENT_STATE_BLOB = "98d7bb5b0067ef281f8727a45b1ecf76b741bf61"
PARENT_MINCUT = Path("research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py")
PARENT_MINCUT_BLOB = "c0c612676e39241b95026c15823e7af6b3da8f0d"
PARENT_SUPPORT = Path("research/tools/apma_cut_support_carrier/cut_support_carrier.py")
PARENT_SUPPORT_BLOB = "012aa1acf52fa12de26bb64df303b2208d396ea9"
PARENT_SUPPORT_V11_CHECKER = Path("research/tools/apma_cut_support_carrier/independent_checker_v1_1.py")
PARENT_SUPPORT_V11_CHECKER_BLOB = "02a5c47ad3e0afe430b7286a4fc8a6c82d7e527e"
HISTORICAL_GYO = Path("archive/trump_apma_v1_1_successor/PREREG_DRAFT_SEMANTIC_JOIN_TREE_REPRESENTATION_v0.3.json")
HISTORICAL_GYO_BLOB = "bbf046833b2cd7aa3d4bb5c165be6ba8851d58b6"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_guard() -> dict:
    r = root()
    prereg = json.loads((r / PREREG).read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "prereg_frozen": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_gate": prereg.get("frozen_gate") == "TRUMP_BICAMERAL_COMPONENT_BOUNDARY_RELATION_JOIN_TREE_CARRIER_FALSIFIER_GATE",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "parent_mincut_blob": git_blob_sha1(r / PARENT_MINCUT) == PARENT_MINCUT_BLOB,
        "parent_support_blob": git_blob_sha1(r / PARENT_SUPPORT) == PARENT_SUPPORT_BLOB,
        "parent_support_v11_checker_blob": git_blob_sha1(r / PARENT_SUPPORT_V11_CHECKER) == PARENT_SUPPORT_V11_CHECKER_BLOB,
        "historical_gyo_blob": git_blob_sha1(r / HISTORICAL_GYO) == HISTORICAL_GYO_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION": "NOT_PROVED",
        "GENERAL_ALPHA_ACYCLIC_CSP_THEOREM_NEW_CLAIM": "NOT_CLAIMED__SOUND_VERIFIED_JOIN_TREE_SUBCLASS_ONLY",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        "SCOPE": "OVERWIDTH_CANONICAL_CUT_WITH_FULL_CUT_ANCHOR_AND_VERIFIED_COMPONENT_JOIN_TREE",
    }


def _dsu_make(n: int) -> tuple[list[int], list[int]]:
    return list(range(n)), [0] * n


def _dsu_find(parent: list[int], x: int) -> int:
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def _dsu_union(parent: list[int], rank: list[int], a: int, b: int) -> bool:
    a, b = _dsu_find(parent, a), _dsu_find(parent, b)
    if a == b:
        return False
    if rank[a] < rank[b]:
        a, b = b, a
    parent[b] = a
    if rank[a] == rank[b]:
        rank[a] += 1
    return True


def deterministic_join_tree(relations: list[dict]) -> dict:
    n = len(relations)
    if n == 0:
        return {"ok": False, "reason": "EMPTY_COMPONENT", "edges": []}
    if n == 1:
        return {"ok": True, "reason": "SINGLE_RELATION", "edges": [], "running_intersection": True}
    scopes = [set(r["scope"]) for r in relations]
    weighted = []
    for i in range(n):
        for j in range(i + 1, n):
            shared = tuple(sorted(scopes[i] & scopes[j]))
            weighted.append((-len(shared), i, j, shared))
    weighted.sort()
    parent, rank = _dsu_make(n)
    edges: list[dict] = []
    for negw, i, j, shared in weighted:
        if _dsu_union(parent, rank, i, j):
            edges.append({"a": i, "b": j, "separator": list(shared), "weight": -negw})
            if len(edges) == n - 1:
                break
    if len(edges) != n - 1:
        return {"ok": False, "reason": "NO_SPANNING_TREE", "edges": edges}
    adj = {i: set() for i in range(n)}
    for e in edges:
        adj[e["a"]].add(e["b"])
        adj[e["b"]].add(e["a"])
    variables = sorted(set().union(*scopes))
    violations = []
    for v in variables:
        nodes = {i for i, s in enumerate(scopes) if v in s}
        if len(nodes) <= 1:
            continue
        start = min(nodes)
        seen = {start}
        stack = [start]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w in nodes and w not in seen:
                    seen.add(w)
                    stack.append(w)
        if seen != nodes:
            violations.append({"variable": v, "nodes": sorted(nodes), "tree_connected_nodes": sorted(seen)})
    body = {
        "relation_count": n,
        "edges": edges,
        "running_intersection": not violations,
        "violations": violations,
        "construction": "DETERMINISTIC_MAX_WEIGHT_KRUSKAL_THEN_RUNNING_INTERSECTION_VERIFY",
        "backtracking": False,
    }
    body["tree_sha256"] = sha256_obj(body)
    return {"ok": not violations, **body}


def choose_anchor(relations: list[dict], cut: list[int]) -> dict | None:
    B = set(cut)
    candidates = []
    for i, r in enumerate(relations):
        if B.issubset(set(r["scope"])):
            candidates.append((len(r["allowed"]), str(r.get("id", "")), i))
    if not candidates:
        return None
    _, _, idx = min(candidates)
    return {"relation_index": idx, "relation_id": relations[idx]["id"], "input_rows": len(relations[idx]["allowed"])}


def anchor_states(anchor_relation: dict, cut: list[int]) -> list[tuple[int, ...]]:
    scope = list(anchor_relation["scope"])
    pos = [scope.index(v) for v in cut]
    states = {tuple(int(row[p]) for p in pos) for row in anchor_relation["allowed"]}
    return sorted(states)


def _restrict_rows(relation: dict, cut_assignment: dict[int, int]) -> list[tuple[int, ...]]:
    scope = list(relation["scope"])
    positions = [(i, v) for i, v in enumerate(scope) if v in cut_assignment]
    out = []
    for raw in relation["allowed"]:
        t = tuple(int(x) for x in raw)
        if all(t[i] == cut_assignment[v] for i, v in positions):
            out.append(t)
    return sorted(set(out))


def _compatible(scope_a: list[int], row_a: tuple[int, ...], scope_b: list[int], row_b: tuple[int, ...]) -> bool:
    pos_b = {v: i for i, v in enumerate(scope_b)}
    for i, v in enumerate(scope_a):
        j = pos_b.get(v)
        if j is not None and row_a[i] != row_b[j]:
            return False
    return True


def _semijoin(dst_scope: list[int], dst_rows: list[tuple[int, ...]], src_scope: list[int], src_rows: list[tuple[int, ...]]) -> tuple[list[tuple[int, ...]], int]:
    kept = []
    comparisons = 0
    for d in dst_rows:
        ok = False
        for s in src_rows:
            comparisons += 1
            if _compatible(dst_scope, d, src_scope, s):
                ok = True
                break
        if ok:
            kept.append(d)
    return kept, comparisons


def conditional_join(relations: list[dict], tree: dict, cut: list[int], sigma: tuple[int, ...]) -> dict:
    assignment = {v: int(b) for v, b in zip(cut, sigma)}
    tables = {i: _restrict_rows(r, assignment) for i, r in enumerate(relations)}
    if any(not rows for rows in tables.values()):
        return {"sat": False, "reason": "EMPTY_RESTRICTED_RELATION", "row_witnesses": {}, "comparisons": 0}
    if len(relations) == 1:
        return {"sat": True, "reason": "SINGLE_RELATION", "row_witnesses": {0: list(tables[0][0])}, "comparisons": 0}
    adj = {i: set() for i in range(len(relations))}
    for e in tree["edges"]:
        adj[e["a"]].add(e["b"])
        adj[e["b"]].add(e["a"])
    root_idx = 0
    parent = {root_idx: None}
    order = [root_idx]
    q = [root_idx]
    while q:
        u = q.pop(0)
        for w in sorted(adj[u]):
            if w in parent:
                continue
            parent[w] = u
            order.append(w)
            q.append(w)
    scopes = {i: list(relations[i]["scope"]) for i in range(len(relations))}
    comparisons = 0
    for child in reversed(order[1:]):
        p = parent[child]
        assert p is not None
        tables[p], c = _semijoin(scopes[p], tables[p], scopes[child], tables[child])
        comparisons += c
        if not tables[p]:
            return {"sat": False, "reason": "BOTTOM_UP_EMPTY", "row_witnesses": {}, "comparisons": comparisons}
    for child in order[1:]:
        p = parent[child]
        assert p is not None
        tables[child], c = _semijoin(scopes[child], tables[child], scopes[p], tables[p])
        comparisons += c
        if not tables[child]:
            return {"sat": False, "reason": "TOP_DOWN_EMPTY", "row_witnesses": {}, "comparisons": comparisons}
    chosen: dict[int, tuple[int, ...]] = {root_idx: tables[root_idx][0]}
    for child in order[1:]:
        p = parent[child]
        assert p is not None
        candidates = [row for row in tables[child] if _compatible(scopes[child], row, scopes[p], chosen[p])]
        if not candidates:
            raise AssertionError("SEMIJOIN_RECONSTRUCTION_GAP")
        chosen[child] = candidates[0]
    return {"sat": True, "reason": "VERIFIED_JOIN_TREE_SEMIJOIN", "row_witnesses": {i: list(chosen[i]) for i in sorted(chosen)}, "comparisons": comparisons}


def component_boundary_support(canonical: dict, component: list[int], cut: list[int]) -> dict:
    relations = [canonical["constraints"][i] for i in component]
    anchor = choose_anchor(relations, cut)
    if anchor is None:
        return {"status": "OPEN_NO_FULL_CUT_ANCHOR", "component": component, "support": {}, "resource": {"raw_cut_assignments_enumerated": 0}}
    tree = deterministic_join_tree(relations)
    if not tree.get("ok"):
        return {"status": "OPEN_NO_VERIFIED_COMPONENT_JOIN_TREE", "component": component, "anchor": anchor, "tree": tree, "support": {}, "resource": {"raw_cut_assignments_enumerated": 0, "join_tree_backtracks": 0}}
    anchor_relation = relations[anchor["relation_index"]]
    states = anchor_states(anchor_relation, cut)
    support: dict[tuple[int, ...], dict] = {}
    comparisons = 0
    for sigma in states:
        joined = conditional_join(relations, tree, cut, sigma)
        comparisons += int(joined["comparisons"])
        if joined["sat"]:
            support[sigma] = joined
    receipt = {
        "component": component,
        "anchor_relation_id": anchor["relation_id"],
        "anchor_input_rows": anchor["input_rows"],
        "anchor_state_count": len(states),
        "support_size": len(support),
        "support_states": [list(x) for x in sorted(support)],
        "tree_sha256": tree["tree_sha256"],
        "semijoin_comparisons": comparisons,
    }
    receipt["component_support_sha256"] = sha256_obj(receipt)
    return {
        "status": "ADMIT_COMPONENT_JOIN_TREE_SUPPORT",
        "component": component,
        "anchor": anchor,
        "tree": tree,
        "support": support,
        "receipt": receipt,
        "resource": {
            "raw_cut_assignments_enumerated": 0,
            "anchor_states_tested": len(states),
            "full_join_rows_materialized": 0,
            "join_tree_backtracks": 0,
            "semijoin_comparisons": comparisons,
        },
    }


def verify_original_assignment(canonical: dict, assignment: dict[int, int]) -> bool:
    for row in canonical["constraints"]:
        scope = list(row["scope"])
        if any(v not in assignment for v in scope):
            return False
        tup = [int(assignment[v]) for v in scope]
        if tup not in [list(map(int, x)) for x in row["allowed"]]:
            return False
    return True


def _merge_component_witness(canonical: dict, component: list[int], joined: dict, assignment: dict[int, int]) -> list[dict]:
    rows = []
    for local_i, global_i in enumerate(component):
        relation = canonical["constraints"][global_i]
        raw = list(joined["row_witnesses"][local_i])
        rows.append({"relation_id": relation["id"], "tuple": raw})
        for v, bit in zip(relation["scope"], raw):
            bit = int(bit)
            if v in assignment and assignment[v] != bit:
                raise AssertionError("GLOBAL_WITNESS_MERGE_CONFLICT")
            assignment[v] = bit
    return rows


def carrier_proposal(canonical: dict, parent: dict, components: list[list[int]]) -> dict:
    body = {
        "role": "INAIHR_CANDIDATE_ONLY_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER",
        "kind": "FULL_CUT_ANCHOR_PLUS_VERIFIED_JOIN_TREE_SEMIJOIN",
        "raw_object_sha256": sha256_obj(canonical),
        "parent_cut_receipt_sha256": parent["cut"]["cut_receipt_sha256"],
        "cut_variables": list(parent["cut"]["cut_variables"]),
        "constraint_components": components,
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(canonical: dict, parent: dict, components: list[list[int]], proposal: dict) -> bool:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    return (
        isinstance(claimed, str)
        and sha256_obj(body) == claimed
        and proposal.get("kind") == "FULL_CUT_ANCHOR_PLUS_VERIFIED_JOIN_TREE_SEMIJOIN"
        and proposal.get("raw_object_sha256") == sha256_obj(canonical)
        and proposal.get("parent_cut_receipt_sha256") == parent["cut"]["cut_receipt_sha256"]
        and proposal.get("cut_variables") == parent["cut"]["cut_variables"]
        and proposal.get("constraint_components") == components
    )


def build_carrier(canonical: dict, parent: dict, components: list[list[int]], proposal: dict) -> dict:
    if not verify_proposal(canonical, parent, components, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE", "resource_receipt": {"raw_cut_assignments_enumerated": 0}}
    cut = list(parent["cut"]["cut_variables"])
    component_results = []
    for comp in components:
        result = component_boundary_support(canonical, comp, cut)
        component_results.append(result)
        if result["status"] != "ADMIT_COMPONENT_JOIN_TREE_SUPPORT":
            return {
                "status": result["status"],
                "failed_component": comp,
                "component_results": component_results,
                "resource_receipt": {
                    "raw_cut_assignments_enumerated": 0,
                    "full_join_rows_materialized": 0,
                    "generic_transfer_calls": 0,
                    "external_solver_invocations": 0,
                },
            }
    supports = [set(r["support"]) for r in component_results]
    common = set.intersection(*supports) if supports else set()
    sorted_common = sorted(common)
    total_anchor_states = sum(r["resource"]["anchor_states_tested"] for r in component_results)
    total_comparisons = sum(r["resource"]["semijoin_comparisons"] for r in component_results)
    resource = {
        "raw_cut_assignments_enumerated": 0,
        "anchor_states_tested": total_anchor_states,
        "full_join_rows_materialized": 0,
        "cartesian_products_materialized": 0,
        "join_tree_backtracks": 0,
        "generic_transfer_calls": 0,
        "external_solver_invocations": 0,
        "semijoin_comparisons": total_comparisons,
        "effective_states_materialized": len(sorted_common),
    }
    base = {
        "cut_variables": cut,
        "cut_size": len(cut),
        "parent_L": parent["canonical_input_bytes_L"],
        "parent_raw_branch_budget": parent["redteam"]["branch_budget"],
        "component_receipts": [r["receipt"] for r in component_results],
        "effective_support_size": len(sorted_common),
        "effective_support": [list(x) for x in sorted_common],
        "resource_receipt": resource,
    }
    if not sorted_common:
        out = {**base, "status": "EXACT_UNSAT_BY_EMPTY_COMPONENT_BOUNDARY_SUPPORT", "witness": None, "witness_verified": True}
        out["carrier_sha256"] = sha256_obj(out)
        return out
    sigma = sorted_common[0]
    assignment = {v: int(b) for v, b in zip(cut, sigma)}
    relation_rows = []
    for comp, result in zip(components, component_results):
        relation_rows.extend(_merge_component_witness(canonical, comp, result["support"][sigma], assignment))
    verified = verify_original_assignment(canonical, assignment)
    out = {
        **base,
        "status": "ADMIT_EXACT_COMPONENT_JOIN_TREE_BOUNDARY_CARRIER" if verified else "OPEN_UNSUPPORTED_COMPONENT_BOUNDARY_CARRIER",
        "witness": {"assignment": {str(v): assignment[v] for v in sorted(assignment)}, "relation_rows": relation_rows},
        "witness_verified": verified,
    }
    out["carrier_sha256"] = sha256_obj(out)
    return out


def explain_overwidth_component_join(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonical = canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": guard, "scientific_firewall": firewall()}
    parent = parent_mincut.explain_with_mincut(raw)
    if parent.get("status") != "OPEN_MINCUT_BRANCH_BUDGET":
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_PARENT_NOT_OVERWIDTH", "parent_status": parent.get("status"), "source_guard": guard, "scientific_firewall": firewall()}
    if parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") != 0:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "HALT_PARENT_RESOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    smaller = parent_support.explain_overwidth_cut(raw)
    if smaller.get("status") in {"ADMIT_EXACT_CUT_SUPPORT_INTERSECTION_CARRIER", "EXACT_UNSAT_BY_EMPTY_CUT_SUPPORT_INTERSECTION"}:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_SINGLETON_CARRIER_ALREADY_EXISTS", "parent_support_status": smaller.get("status"), "source_guard": guard, "scientific_firewall": firewall()}
    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    if len(components) < 2 or not any(len(c) >= 2 for c in components):
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_NO_MULTI_RELATION_COMPONENT", "components": components, "source_guard": guard, "scientific_firewall": firewall()}
    proposal = carrier_proposal(canonical, parent, components)
    carrier = build_carrier(canonical, parent, components, proposal)
    receipt = {
        "raw_object_sha256": sha256_obj(canonical),
        "parent_cut_receipt_sha256": parent["cut"]["cut_receipt_sha256"],
        "proposal_sha256": proposal["proposal_sha256"],
        "carrier_sha256": carrier.get("carrier_sha256"),
        "terminal": carrier["status"],
    }
    receipt["explanation_sha256"] = sha256_obj(receipt)
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": carrier["status"],
        "source_guard": guard,
        "parent_status": parent["status"],
        "parent_support_status": smaller.get("status"),
        "parent_cut": parent["cut"],
        "parent_resource_receipt": parent["redteam"]["resource_receipt"],
        "components": components,
        "proposal": proposal,
        "carrier": carrier,
        "provenance_receipt": receipt,
        "execution_authorized": False,
        "complexity": {
            "claim": "POLYNOMIAL_IN_CANONICAL_EXPLICIT_INPUT_LENGTH_FOR_FROZEN_ANCHOR_PLUS_VERIFIED_JOIN_TREE_SCOPE",
            "candidate_states": "at most explicit anchor relation rows per component",
            "join_tree": "deterministic polynomial maximum-weight spanning tree plus running-intersection verification",
            "semijoin": "two passes over explicit relation tables per anchor state",
            "raw_2_to_k_enumeration": "FORBIDDEN_AND_ZERO",
            "full_join_materialization": "FORBIDDEN_AND_ZERO",
        },
        "scientific_firewall": firewall(),
    }


def _bits(seed: int, n: int) -> list[int]:
    return [((seed >> (i % 8)) ^ (i // 3)) & 1 for i in range(n)]


def positive_multi_relation_k20() -> dict:
    B = list(range(20))
    Y = list(range(20, 40))
    p, z = 40, 41
    A, C, D = _bits(5, 20), _bits(11, 20), _bits(23, 20)
    X, Y1, Y2 = _bits(7, 20), _bits(19, 20), _bits(29, 20)
    return {
        "variables": list(range(42)),
        "constraints": [
            {"id": "anchor_left", "scope": B + Y, "allowed": [A + X, C + Y1, D + X]},
            {"id": "filter_left", "scope": B + Y + [p], "allowed": [A + X + [1], C + Y2 + [0]]},
            {"id": "right", "scope": B + [z], "allowed": [A + [0], D + [1]]},
        ],
    }


def empty_conditional_join_control() -> dict:
    raw = positive_multi_relation_k20()
    B = list(range(20))
    Y = list(range(20, 40))
    p = 40
    C = _bits(11, 20)
    Y2 = _bits(29, 20)
    raw["constraints"][1] = {"id": "filter_left", "scope": B + Y + [p], "allowed": [C + Y2 + [0]]}
    return raw


def alpha_cycle_control() -> dict:
    B = list(range(20))
    Y12 = list(range(20, 40))
    Y23 = list(range(40, 60))
    Y31 = list(range(60, 80))
    z = 80
    A = _bits(5, 20)
    x12, x23, x31 = _bits(7, 20), _bits(13, 20), _bits(17, 20)
    return {
        "variables": list(range(81)),
        "constraints": [
            {"id": "cycle_r1", "scope": B + Y12 + Y31, "allowed": [A + x12 + x31]},
            {"id": "cycle_r2", "scope": B + Y12 + Y23, "allowed": [A + x12 + x23]},
            {"id": "cycle_r3", "scope": B + Y23 + Y31, "allowed": [A + x23 + x31]},
            {"id": "cycle_right", "scope": B + [z], "allowed": [A + [1]]},
        ],
    }


def no_anchor_unit_control() -> dict:
    B = list(range(20))
    Y = list(range(20, 40))
    canonical = {
        "variables": list(range(40)),
        "constraints": [
            {"id": "half_a", "scope": B[:10] + Y, "allowed": [[0] * 30]},
            {"id": "half_b", "scope": B[10:] + Y, "allowed": [[0] * 30]},
        ],
    }
    return component_boundary_support(canonical, [0, 1], B)


def injected_hint_control() -> dict:
    raw = positive_multi_relation_k20()
    raw["boundary_carrier"] = "JOIN_TREE"
    return raw


def tampered_control() -> dict:
    raw = positive_multi_relation_k20()
    canonical = canonicalize_raw(raw)
    parent = parent_mincut.explain_with_mincut(raw)
    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    proposal = carrier_proposal(canonical, parent, components)
    proposal["constraint_components"] = [[0], [1], [2]]
    return build_carrier(canonical, parent, components, proposal)


def main() -> None:
    print(json.dumps({
        "artifact_id": ARTIFACT_ID,
        "positive": explain_overwidth_component_join(positive_multi_relation_k20()),
        "negative_empty": explain_overwidth_component_join(empty_conditional_join_control()),
        "negative_cycle": explain_overwidth_component_join(alpha_cycle_control()),
        "negative_no_anchor_unit": no_anchor_unit_control(),
        "negative_hint": explain_overwidth_component_join(injected_hint_control()),
        "negative_tamper": tampered_control(),
        "scientific_firewall": firewall(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
