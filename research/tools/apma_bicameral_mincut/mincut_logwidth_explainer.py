from __future__ import annotations

import collections
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_pair_separator.pair_separator_explainer import explain_with_pair_separator

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-MINCUT-LOGWIDTH-EXPLANATION-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__MINCUT_PROPOSAL_ONLY_UNTIL_EXACT_REPLAY"
PREREG_REL = Path("research/TRUMP_BICAMERAL_MINCUT_LOGWIDTH_EXPLANATION_PREREGISTRATION_2026-09-15.json")
PREREG_COMMIT = "80244eba21a7965733f6c705678fca88b4dc2c25"
PREREG_GIT_BLOB_SHA1 = "e83bf98bca925e49e43b4045b2795cd5c6b66ca1"
SEALED_COMPOSER_REL = Path("research/tools/apma_unseen_basis/compositional_basis.py")
SEALED_COMPOSER_GIT_BLOB_SHA1 = "fdc83a3368a4ad362f00d3ee8aad958f06f8d264"
PARENT_PAIR_REL = Path("research/tools/apma_bicameral_pair_separator/pair_separator_explainer.py")
PARENT_PAIR_GIT_BLOB_SHA1 = "b6dc5fde585affb167e74308bc8f10c64f7d2990"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_guard() -> dict:
    root = repo_root()
    prereg = root / PREREG_REL
    composer = root / SEALED_COMPOSER_REL
    parent = root / PARENT_PAIR_REL
    p = json.loads(prereg.read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(prereg) == PREREG_GIT_BLOB_SHA1,
        "prereg_status": p.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_gate": p.get("frozen_gate") == "TRUMP_BICAMERAL_CANONICAL_MIN_VARIABLE_CUT_LOG_WIDTH_EXPLANATION_FALSIFIER_GATE",
        "sealed_composer_blob": git_blob_sha1(composer) == SEALED_COMPOSER_GIT_BLOB_SHA1,
        "parent_pair_blob": git_blob_sha1(parent) == PARENT_PAIR_GIT_BLOB_SHA1,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "SCOPE": "RAW_EXPLICIT_TABLE_CONNECTED_MIXED_CORES_WITH_POLYNOMIALLY_DISCOVERED_LOGWIDTH_VARIABLE_MINCUT",
        "LLM_AUTHORITY": "NONE",
        "SEMANTIC_SIMILARITY_AUTHORITY": "NONE",
        "SOLVER_EXECUTION_IN_THIS_GATE": "FORBIDDEN",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
    }


def incidence_graph(canonical: dict) -> dict[str, set[str]]:
    g: dict[str, set[str]] = {f"v:{v}": set() for v in canonical["variables"]}
    for i, row in enumerate(canonical["constraints"]):
        c = f"c:{i}"
        g[c] = set()
        for v in row["scope"]:
            vn = f"v:{v}"
            g[c].add(vn)
            g[vn].add(c)
    return g


def _add_capacity(cap: dict[str, dict[str, int]], u: str, v: str, value: int) -> None:
    cap.setdefault(u, {})
    cap.setdefault(v, {})
    cap[u][v] = cap[u].get(v, 0) + value
    cap[v].setdefault(u, 0)


def node_split_network(canonical: dict) -> tuple[dict[str, dict[str, int]], int]:
    g = incidence_graph(canonical)
    inf = len(canonical["variables"]) + 1
    cap: dict[str, dict[str, int]] = {}
    for node in sorted(g):
        n_in, n_out = node + "|in", node + "|out"
        split_cap = 1 if node.startswith("v:") else inf
        _add_capacity(cap, n_in, n_out, split_cap)
    seen_edges: set[tuple[str, str]] = set()
    for u in sorted(g):
        for v in sorted(g[u]):
            edge = tuple(sorted((u, v)))
            if edge in seen_edges:
                continue
            seen_edges.add(edge)
            _add_capacity(cap, u + "|out", v + "|in", inf)
            _add_capacity(cap, v + "|out", u + "|in", inf)
    return cap, inf


def edmonds_karp_min_cut(canonical: dict, source_constraint: int, target_constraint: int) -> dict:
    capacity, inf = node_split_network(canonical)
    source = f"c:{source_constraint}|out"
    sink = f"c:{target_constraint}|in"
    residual = {u: dict(vs) for u, vs in capacity.items()}
    maxflow = 0
    while True:
        parent: dict[str, str | None] = {source: None}
        q = collections.deque([source])
        while q and sink not in parent:
            u = q.popleft()
            for v in sorted(residual.get(u, {})):
                if v not in parent and residual[u][v] > 0:
                    parent[v] = u
                    q.append(v)
                    if v == sink:
                        break
        if sink not in parent:
            break
        bottleneck = inf
        cur = sink
        while cur != source:
            prev = parent[cur]
            assert prev is not None
            bottleneck = min(bottleneck, residual[prev][cur])
            cur = prev
        cur = sink
        while cur != source:
            prev = parent[cur]
            assert prev is not None
            residual[prev][cur] -= bottleneck
            residual[cur][prev] = residual[cur].get(prev, 0) + bottleneck
            cur = prev
        maxflow += bottleneck

    reachable: set[str] = set()
    q = collections.deque([source])
    while q:
        u = q.popleft()
        if u in reachable:
            continue
        reachable.add(u)
        for v in sorted(residual.get(u, {})):
            if residual[u][v] > 0 and v not in reachable:
                q.append(v)

    cut = []
    for v in canonical["variables"]:
        if f"v:{v}|in" in reachable and f"v:{v}|out" not in reachable:
            cut.append(v)
    return {
        "source_constraint_index": source_constraint,
        "target_constraint_index": target_constraint,
        "maxflow_value": maxflow,
        "cut_variables": cut,
        "cut_size": len(cut),
        "inf_capacity": inf,
    }


def constraint_component_count(canonical: dict, removed_vars: set[int]) -> int:
    g = incidence_graph(canonical)
    removed = {f"v:{v}" for v in removed_vars}
    constraints = {n for n in g if n.startswith("c:")}
    seen: set[str] = set()
    count = 0
    for start in sorted(n for n in g if n not in removed):
        if start in seen:
            continue
        stack = [start]
        has_constraint = False
        while stack:
            n = stack.pop()
            if n in seen or n in removed:
                continue
            seen.add(n)
            if n in constraints:
                has_constraint = True
            stack.extend(x for x in g[n] if x not in seen and x not in removed)
        if has_constraint:
            count += 1
    return count


def canonical_min_variable_cut(canonical: dict) -> dict | None:
    ccount = len(canonical["constraints"])
    if ccount < 2:
        return None
    records = []
    for s in range(ccount):
        for t in range(s + 1, ccount):
            rec = edmonds_karp_min_cut(canonical, s, t)
            if rec["cut_size"] != rec["maxflow_value"]:
                continue
            if constraint_component_count(canonical, set(rec["cut_variables"])) <= 1:
                continue
            records.append(rec)
    if not records:
        return None
    records.sort(key=lambda r: (r["cut_size"], tuple(r["cut_variables"]), r["source_constraint_index"], r["target_constraint_index"]))
    chosen = records[0]
    body = {
        "role": "HRAIN_DETERMINISTIC_CANONICAL_MIN_VARIABLE_CUT",
        "source_constraint_index": chosen["source_constraint_index"],
        "target_constraint_index": chosen["target_constraint_index"],
        "cut_variables": chosen["cut_variables"],
        "cut_size": chosen["cut_size"],
        "maxflow_value": chosen["maxflow_value"],
        "constraint_component_count_after_cut": constraint_component_count(canonical, set(chosen["cut_variables"])),
        "constraint_pair_count_examined": ccount * (ccount - 1) // 2,
    }
    body["cut_receipt_sha256"] = sha256_obj(body)
    return body


def restrict_on_assignment(canonical: dict, variables: list[int], values: list[int]) -> dict:
    if len(variables) != len(values) or len(set(variables)) != len(variables):
        raise ValueError("INVALID_CUT_RESTRICTION")
    assignment = dict(zip(variables, values))
    constraints = []
    branch_unsat = False
    for row in canonical["constraints"]:
        scope = list(row["scope"])
        assigned_positions = [(i, v) for i, v in enumerate(scope) if v in assignment]
        if not assigned_positions:
            constraints.append({"id": row["id"], "scope": scope, "allowed": [list(t) for t in row["allowed"]]})
            continue
        survivors = []
        for raw_t in row["allowed"]:
            t = tuple(int(x) for x in raw_t)
            if all(t[i] == assignment[v] for i, v in assigned_positions):
                survivors.append(t)
        if not survivors:
            branch_unsat = True
            break
        keep = [i for i, v in enumerate(scope) if v not in assignment]
        new_scope = [scope[i] for i in keep]
        new_tuples = sorted({tuple(t[i] for i in keep) for t in survivors})
        if new_scope:
            constraints.append({"id": row["id"], "scope": new_scope, "allowed": [list(t) for t in new_tuples]})
    residual = {"variables": sorted({v for row in constraints for v in row["scope"]}), "constraints": constraints}
    body = {
        "assigned_variables": list(variables),
        "assigned_values": list(values),
        "branch_unsat": branch_unsat,
        "residual": residual if not branch_unsat else None,
    }
    body["restriction_sha256"] = sha256_obj(body)
    return body


def replay_branch(restriction: dict) -> dict:
    if restriction["branch_unsat"]:
        return {"status": "EXACT_UNSAT_BY_EMPTY_RELATION", "admitted": True, "basis_replay": None, "restriction_sha256": restriction["restriction_sha256"]}
    residual = restriction["residual"]
    if not residual["constraints"]:
        return {"status": "EXACT_TRIVIAL_SAT_NO_RESIDUAL_CONSTRAINTS", "admitted": True, "basis_replay": None, "restriction_sha256": restriction["restriction_sha256"]}
    cert = induce_compositional_basis(residual)
    admitted = cert.get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO"
    return {"status": "ADMIT_BRANCH_EXACT_BASIS_PORTFOLIO" if admitted else "REJECT_BRANCH_EXPLANATION", "admitted": admitted, "basis_replay": cert, "restriction_sha256": restriction["restriction_sha256"]}


def proposal_record(canonical: dict, cut: dict) -> dict:
    body = {
        "role": "INAIHR_CANDIDATE_ONLY_MINCUT_PROPOSAL",
        "kind": "CANONICAL_MIN_VARIABLE_CUT_CONDITIONING",
        "raw_object_sha256": sha256_obj(canonical),
        "cut_receipt_sha256": cut["cut_receipt_sha256"],
        "separator_variables": list(cut["cut_variables"]),
        "source_constraint_index": cut["source_constraint_index"],
        "target_constraint_index": cut["target_constraint_index"],
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def redteam_proposal(canonical: dict, cut: dict, proposal: dict) -> dict:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    provenance_ok = (
        isinstance(claimed, str)
        and sha256_obj(body) == claimed
        and proposal.get("raw_object_sha256") == sha256_obj(canonical)
        and proposal.get("cut_receipt_sha256") == cut.get("cut_receipt_sha256")
        and proposal.get("separator_variables") == cut.get("cut_variables")
        and proposal.get("source_constraint_index") == cut.get("source_constraint_index")
        and proposal.get("target_constraint_index") == cut.get("target_constraint_index")
        and proposal.get("kind") == "CANONICAL_MIN_VARIABLE_CUT_CONDITIONING"
    )
    if not provenance_ok:
        return {"status": "REJECT_TAMPERED_PROVENANCE", "provenance_ok": False, "proposal_sha256": claimed}

    L = max(2, len(canonical_bytes(canonical)))
    k = len(cut["cut_variables"])
    branch_budget = 1 << k
    if branch_budget > L:
        result = {
            "status": "OPEN_MINCUT_BRANCH_BUDGET",
            "provenance_ok": True,
            "separator_variables": list(cut["cut_variables"]),
            "k": k,
            "L": L,
            "branch_budget": branch_budget,
            "branches": [],
            "resource_receipt": {"branch_enumerations": 0, "solver_invocations": 0, "generic_transfer_calls": 0, "full_variable_cube_enumerated": False},
        }
        result["redteam_sha256"] = sha256_obj(result)
        return result

    branches = []
    for values in itertools.product((0,1), repeat=k):
        restriction = restrict_on_assignment(canonical, cut["cut_variables"], list(values))
        replay = replay_branch(restriction)
        branches.append({"assignment": list(values), "restriction": restriction, "replay": replay})
    all_admitted = all(b["replay"]["admitted"] for b in branches)
    result = {
        "status": "PASS_MINCUT_EXACT_REPLAY" if all_admitted else "OPEN_NO_EXACT_LOGWIDTH_MINCUT_EXPLANATION",
        "provenance_ok": True,
        "separator_variables": list(cut["cut_variables"]),
        "k": k,
        "L": L,
        "branch_budget": branch_budget,
        "branches": branches,
        "resource_receipt": {
            "branch_enumerations": len(branches),
            "solver_invocations": 0,
            "generic_transfer_calls": 0,
            "full_variable_cube_enumerated": False,
            "cartesian_products_materialized": 0,
        },
    }
    result["redteam_sha256"] = sha256_obj(result)
    return result


def explain_with_mincut(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonical = canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": guard, "scientific_firewall": firewall(), "metrics": {"branch_enumerations": 0, "solver_invocations": 0}}

    parent = explain_with_pair_separator(raw)
    if parent.get("status") in {"ADMIT_EXACT_PAIR_SEPARATOR_EXPLANATION", "OUT_OF_SCOPE_SINGLE_VARIABLE_EXPLANATION_ALREADY_EXISTS"}:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_SMALLER_SEPARATOR_EXPLANATION_ALREADY_EXISTS", "parent_pair_status": parent.get("status"), "source_guard": guard, "scientific_firewall": firewall()}

    global_basis = induce_compositional_basis(canonical)
    if global_basis.get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO":
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_GLOBAL_OR_DISCONNECTED_BASIS_ALREADY_EXISTS", "source_guard": guard, "scientific_firewall": firewall()}

    cut = canonical_min_variable_cut(canonical)
    if not cut:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OPEN_NO_EXACT_LOGWIDTH_MINCUT_EXPLANATION", "source_guard": guard, "scientific_firewall": firewall()}
    proposal = proposal_record(canonical, cut)
    redteam = redteam_proposal(canonical, cut, proposal)
    if redteam["status"] == "PASS_MINCUT_EXACT_REPLAY":
        terminal = "ADMIT_EXACT_LOGWIDTH_MINCUT_EXPLANATION"
    else:
        terminal = redteam["status"]
    receipt = {
        "raw_object_sha256": sha256_obj(canonical),
        "cut_receipt_sha256": cut["cut_receipt_sha256"],
        "proposal_sha256": proposal["proposal_sha256"],
        "redteam_sha256": redteam.get("redteam_sha256"),
        "terminal": terminal,
    }
    receipt["mincut_explanation_receipt_sha256"] = sha256_obj(receipt)
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "source_guard": guard,
        "status": terminal,
        "parent_pair_status": parent.get("status"),
        "raw_object_sha256": sha256_obj(canonical),
        "canonical_input_bytes_L": max(2, len(canonical_bytes(canonical))),
        "cut": cut,
        "proposal": proposal,
        "redteam": redteam,
        "provenance_receipt": receipt,
        "execution_authorized": False,
        "metrics": {
            "constraint_pair_maxflow_calls": len(canonical["constraints"]) * (len(canonical["constraints"]) - 1) // 2,
            "branch_enumerations": redteam.get("resource_receipt", {}).get("branch_enumerations", 0),
            "solver_invocations": 0,
            "generic_transfer_calls": 0,
            "full_variable_assignments_enumerated": 0,
            "cartesian_products_materialized": 0,
        },
        "complexity": {
            "claim": "POLYNOMIAL_IN_CANONICAL_EXPLICIT_INPUT_LENGTH_FOR_FROZEN_MINCUT_LOGWIDTH_SCOPE",
            "discovery": "O(C^2) deterministic Edmonds-Karp max-flow calls on a node-split graph",
            "branching": "2^k <= L checked before enumeration, hence at most L branch restrictions",
        },
        "scientific_firewall": firewall(),
    }


def positive_logwidth_cut3() -> dict:
    or4 = [list(t) for t in itertools.product((0,1), repeat=4) if any(t)]
    xor4 = [list(t) for t in itertools.product((0,1), repeat=4) if (sum(t) % 2) == 0]
    return {
        "variables": [0,1,2,3,4],
        "constraints": [
            {"id": "opaque_or4", "scope": [0,1,2,3], "allowed": or4},
            {"id": "opaque_xor4", "scope": [0,1,2,4], "allowed": xor4},
        ],
    }


def _embedded_or_relation(n: int) -> list[list[int]]:
    return [list((a,b) + (a,) * (n - 2)) for a,b in [(0,1),(1,0),(1,1)]]


def _embedded_xor_relation(n: int) -> list[list[int]]:
    return [list((a,b,c) + (a,) * (n - 3)) for a,b,c in [(0,0,0),(0,1,1),(1,0,1),(1,1,0)]]


def negative_overwidth_cut(n: int = 20) -> dict:
    scope = list(range(n))
    return {
        "variables": scope,
        "constraints": [
            {"id": "opaque_embedded_or", "scope": scope, "allowed": _embedded_or_relation(n)},
            {"id": "opaque_embedded_xor", "scope": scope, "allowed": _embedded_xor_relation(n)},
        ],
    }


def injected_hint_control() -> dict:
    raw = positive_logwidth_cut3()
    raw["separator"] = [0,1,2]
    return raw


def main() -> None:
    print(json.dumps({
        "artifact_id": ARTIFACT_ID,
        "positive": explain_with_mincut(positive_logwidth_cut3()),
        "negative_overwidth": explain_with_mincut(negative_overwidth_cut()),
        "negative_hint": explain_with_mincut(injected_hint_control()),
        "scientific_firewall": firewall(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
