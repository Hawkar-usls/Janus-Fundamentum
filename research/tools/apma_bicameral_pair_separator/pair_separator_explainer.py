from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_explanation.bicameral_explainer import explain_connected_mixed_core

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-PAIR-SEPARATOR-EXPLANATION-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__PAIR_PROPOSAL_ONLY_UNTIL_EXACT_REPLAY"
PREREG_REL = Path("research/TRUMP_BICAMERAL_PAIR_SEPARATOR_EXPLANATION_PREREGISTRATION_2026-09-15.json")
PREREG_COMMIT = "b0d08ba3a8fc0c3008a3595d275d0a7bb3e2c78b"
PREREG_GIT_BLOB_SHA1 = "1ad44d91f9ea23dc6b1e7891ff5631ebbe13d149"
SEALED_COMPOSER_REL = Path("research/tools/apma_unseen_basis/compositional_basis.py")
SEALED_COMPOSER_GIT_BLOB_SHA1 = "fdc83a3368a4ad362f00d3ee8aad958f06f8d264"
PARENT_SINGLE_REL = Path("research/tools/apma_bicameral_explanation/bicameral_explainer.py")
PARENT_SINGLE_GIT_BLOB_SHA1 = "bc3a9e0040b255cd4c976512a619f90644434d45"


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
    parent = root / PARENT_SINGLE_REL
    p = json.loads(prereg.read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(prereg) == PREREG_GIT_BLOB_SHA1,
        "prereg_status": p.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_gate": p.get("frozen_gate") == "TRUMP_BICAMERAL_BOUNDED_MULTI_SEPARATOR_OR_QUOTIENT_EXPLANATION_FALSIFIER_GATE__PAIR_SEPARATOR_FIRST",
        "sealed_composer_blob": git_blob_sha1(composer) == SEALED_COMPOSER_GIT_BLOB_SHA1,
        "parent_single_blob": git_blob_sha1(parent) == PARENT_SINGLE_GIT_BLOB_SHA1,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "GROWING_SEPARATOR_DISCOVERY": "NOT_PROVED",
        "SCOPE": "RAW_EXPLICIT_TABLE_CONNECTED_MIXED_CORES_WITH_TWO_VARIABLE_INCIDENCE_SEPARATOR",
        "LLM_AUTHORITY": "NONE",
        "SEMANTIC_SIMILARITY_AUTHORITY": "NONE",
        "SOLVER_EXECUTION_IN_THIS_GATE": "FORBIDDEN",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
    }


def incidence_graph(canonical: dict) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {f"v:{v}": set() for v in canonical["variables"]}
    for i, row in enumerate(canonical["constraints"]):
        c = f"c:{i}"
        graph[c] = set()
        for v in row["scope"]:
            vn = f"v:{v}"
            graph[c].add(vn)
            graph[vn].add(c)
    return graph


def components_without_nodes(graph: dict[str, set[str]], removed: set[str]) -> list[set[str]]:
    seen: set[str] = set()
    out: list[set[str]] = []
    for start in sorted(n for n in graph if n not in removed):
        if start in seen:
            continue
        stack = [start]
        comp: set[str] = set()
        while stack:
            node = stack.pop()
            if node in seen or node in removed:
                continue
            seen.add(node)
            comp.add(node)
            for nxt in graph[node]:
                if nxt not in removed and nxt not in seen:
                    stack.append(nxt)
        out.append(comp)
    return out


def observation_receipt(canonical: dict) -> dict:
    graph = incidence_graph(canonical)
    constraint_nodes = {n for n in graph if n.startswith("c:")}
    pairs: list[list[int]] = []
    split_counts: dict[str, int] = {}
    for a, b in itertools.combinations(canonical["variables"], 2):
        comps = components_without_nodes(graph, {f"v:{a}", f"v:{b}"})
        with_constraints = [c for c in comps if c & constraint_nodes]
        split_counts[f"{a},{b}"] = len(with_constraints)
        if len(with_constraints) > 1:
            pairs.append([a, b])
    body = {
        "role": "HRAIN_DETERMINISTIC_PAIR_SEPARATOR_OBSERVATION",
        "incidence_node_count": len(graph),
        "incidence_edge_count": sum(len(x) for x in graph.values()) // 2,
        "constraint_scopes": [list(row["scope"]) for row in canonical["constraints"]],
        "pair_split_counts": split_counts,
        "pair_separators": pairs,
    }
    body["observation_sha256"] = sha256_obj(body)
    return body


def proposal_records(canonical: dict, observation: dict) -> list[dict]:
    raw_hash = sha256_obj(canonical)
    out: list[dict] = []
    for pair in observation["pair_separators"]:
        body = {
            "role": "INAIHR_CANDIDATE_ONLY_PAIR_SEPARATOR_PROPOSAL",
            "kind": "TWO_VARIABLE_INCIDENCE_SEPARATOR_CONDITIONING",
            "raw_object_sha256": raw_hash,
            "observation_sha256": observation["observation_sha256"],
            "separator_variables": list(pair),
            "branch_assignments": [[0,0],[0,1],[1,0],[1,1]],
            "truth_authority": False,
            "proof_authority": False,
            "automatic_promotion": False,
        }
        body["proposal_sha256"] = sha256_obj(body)
        out.append(body)
    return sorted(out, key=lambda x: (x["separator_variables"], x["proposal_sha256"]))


def restrict_on_assignment(canonical: dict, variables: list[int], values: list[int]) -> dict:
    if len(variables) != 2 or len(values) != 2 or len(set(variables)) != 2:
        raise ValueError("INVALID_PAIR_RESTRICTION")
    if any(v not in canonical["variables"] for v in variables) or any(x not in (0,1) for x in values):
        raise ValueError("INVALID_PAIR_RESTRICTION")
    assignment = dict(zip(variables, values))
    constraints: list[dict] = []
    branch_unsat = False
    for row in canonical["constraints"]:
        scope = list(row["scope"])
        allowed = [tuple(int(x) for x in t) for t in row["allowed"]]
        assigned_positions = [(i, v) for i, v in enumerate(scope) if v in assignment]
        if not assigned_positions:
            constraints.append({"id": row["id"], "scope": scope, "allowed": [list(t) for t in allowed]})
            continue
        kept = []
        for t in allowed:
            if all(t[i] == assignment[v] for i, v in assigned_positions):
                kept.append(t)
        if not kept:
            branch_unsat = True
            break
        keep_positions = [i for i, v in enumerate(scope) if v not in assignment]
        new_scope = [scope[i] for i in keep_positions]
        new_tuples = sorted({tuple(t[i] for i in keep_positions) for t in kept})
        if not new_scope:
            continue
        constraints.append({"id": row["id"], "scope": new_scope, "allowed": [list(t) for t in new_tuples]})
    residual_variables = sorted({v for row in constraints for v in row["scope"]})
    residual = {"variables": residual_variables, "constraints": constraints}
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
    return {
        "status": "ADMIT_BRANCH_EXACT_BASIS_PORTFOLIO" if admitted else "REJECT_BRANCH_EXPLANATION",
        "admitted": admitted,
        "basis_replay": cert,
        "restriction_sha256": restriction["restriction_sha256"],
    }


def redteam_pair_proposal(canonical: dict, observation: dict, proposal: dict) -> dict:
    raw_hash = sha256_obj(canonical)
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    pair = proposal.get("separator_variables")
    provenance_ok = (
        isinstance(claimed, str)
        and sha256_obj(body) == claimed
        and proposal.get("raw_object_sha256") == raw_hash
        and proposal.get("observation_sha256") == observation.get("observation_sha256")
        and proposal.get("kind") == "TWO_VARIABLE_INCIDENCE_SEPARATOR_CONDITIONING"
        and proposal.get("branch_assignments") == [[0,0],[0,1],[1,0],[1,1]]
        and isinstance(pair, list) and len(pair) == 2 and pair == sorted(pair) and len(set(pair)) == 2
        and all(v in canonical["variables"] for v in pair)
        and pair in observation.get("pair_separators", [])
    )
    if not provenance_ok:
        return {"status": "REJECT_TAMPERED_PROVENANCE", "proposal_sha256": claimed, "provenance_ok": False}

    branches = []
    for assignment in [[0,0],[0,1],[1,0],[1,1]]:
        restriction = restrict_on_assignment(canonical, pair, assignment)
        replay = replay_branch(restriction)
        branches.append({"assignment": assignment, "restriction": restriction, "replay": replay})
    all_admitted = all(b["replay"]["admitted"] for b in branches)
    obligations = {
        "P3_content_bound_pair": provenance_ok,
        "P4_pair_is_structural_separator": pair in observation["pair_separators"],
        "P5_exact_four_boolean_branches": [b["assignment"] for b in branches] == [[0,0],[0,1],[1,0],[1,1]],
        "P6_exact_restriction_receipts_present": all(bool(b["restriction"].get("restriction_sha256")) for b in branches),
        "P7_sealed_compositional_replay_or_exact_terminal": all(b["replay"]["status"] in {"ADMIT_BRANCH_EXACT_BASIS_PORTFOLIO", "EXACT_UNSAT_BY_EMPTY_RELATION", "EXACT_TRIVIAL_SAT_NO_RESIDUAL_CONSTRAINTS"} for b in branches),
        "P8_all_four_branches_admitted": all_admitted,
        "P10_no_solver_before_admission": True,
    }
    result = {
        "status": "PASS_PAIR_PROPOSAL_EXACT_REPLAY" if all(obligations.values()) else "REJECT_PAIR_PROPOSAL_EXACT_REPLAY",
        "proposal_sha256": claimed,
        "separator_variables": list(pair),
        "provenance_ok": provenance_ok,
        "branches": branches,
        "obligations": obligations,
        "resource_receipt": {
            "candidate_pair_count_charged": 1,
            "boolean_branch_count": 4,
            "full_variable_cube_enumerated": False,
            "generic_transfer_calls": 0,
            "solver_invocations": 0,
            "cartesian_products_materialized": 0,
        },
    }
    result["redteam_sha256"] = sha256_obj(result)
    return result


def explain_with_pair_separator(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonical = canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {
            "artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": guard,
            "metrics": {"solver_invocations": 0, "generic_transfer_calls": 0, "full_variable_assignments_enumerated": 0},
            "scientific_firewall": firewall(),
        }
    parent = explain_connected_mixed_core(raw)
    if parent.get("status") == "ADMIT_EXACT_STRUCTURAL_EXPLANATION":
        return {
            "artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_SINGLE_VARIABLE_EXPLANATION_ALREADY_EXISTS",
            "parent_single_variable_status": parent.get("status"), "source_guard": guard, "scientific_firewall": firewall(),
        }
    observation = observation_receipt(canonical)
    proposals = proposal_records(canonical, observation)
    redteams = [redteam_pair_proposal(canonical, observation, p) for p in proposals]
    passing = [r for r in redteams if r.get("status") == "PASS_PAIR_PROPOSAL_EXACT_REPLAY"]
    selected = passing[0] if passing else None
    terminal = "ADMIT_EXACT_PAIR_SEPARATOR_EXPLANATION" if selected else "OPEN_NO_EXACT_PAIR_SEPARATOR_EXPLANATION"
    receipt = {
        "raw_object_sha256": sha256_obj(canonical),
        "observation_sha256": observation["observation_sha256"],
        "proposal_sha256": selected.get("proposal_sha256") if selected else None,
        "redteam_sha256": selected.get("redteam_sha256") if selected else None,
        "terminal": terminal,
    }
    receipt["pair_separator_receipt_sha256"] = sha256_obj(receipt)
    pair_count = len(canonical["variables"]) * (len(canonical["variables"]) - 1) // 2
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "source_guard": guard,
        "status": terminal,
        "parent_single_variable_status": parent.get("status"),
        "raw_object_sha256": sha256_obj(canonical),
        "observation": observation,
        "proposals": proposals,
        "redteams": redteams,
        "selected_explanation": selected,
        "provenance_receipt": receipt,
        "execution_authorized": False,
        "metrics": {
            "candidate_pairs_examined": pair_count,
            "structural_pair_proposals_emitted": len(proposals),
            "exact_branch_replays": 4 * len(proposals),
            "full_variable_assignments_enumerated": 0,
            "generic_transfer_calls": 0,
            "solver_invocations": 0,
            "cartesian_products_materialized": 0,
        },
        "complexity": {
            "claim": "POLYNOMIAL_IN_EXPLICIT_TABLE_INPUT_FOR_FROZEN_TWO_VARIABLE_PROPOSAL_LIBRARY",
            "reason": "At most V(V-1)/2 pair proposals; exactly four restrictions per proposal; each restriction scans explicit tuples and invokes only sealed polynomial explicit-table basis replay.",
        },
        "scientific_firewall": firewall(),
    }


def positive_prior_biconnected() -> dict:
    return {
        "variables": [0,1,2],
        "constraints": [
            {"id": "opaque_a", "scope": [0,1], "allowed": [[0,1],[1,0],[1,1]]},
            {"id": "opaque_b", "scope": [0,1,2], "allowed": [[0,0,0],[0,1,1],[1,0,1],[1,1,0]]},
        ],
    }


def negative_three_variable_cut_required() -> dict:
    return {
        "variables": [0,1,2],
        "constraints": [
            {"id": "opaque_or3", "scope": [0,1,2], "allowed": [[a,b,c] for a,b,c in itertools.product((0,1), repeat=3) if a or b or c]},
            {"id": "opaque_xor3", "scope": [0,1,2], "allowed": [[0,0,0],[0,1,1],[1,0,1],[1,1,0]]},
        ],
    }


def injected_hint_control() -> dict:
    raw = positive_prior_biconnected()
    raw["separator"] = [0,1]
    return raw


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "positive": explain_with_pair_separator(positive_prior_biconnected()),
        "negative_three_variable_cut": explain_with_pair_separator(negative_three_variable_cut_required()),
        "negative_injected_hint": explain_with_pair_separator(injected_hint_control()),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
