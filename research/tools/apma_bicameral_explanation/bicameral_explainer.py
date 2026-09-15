from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-CONNECTED-CORE-EXPLANATION-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__PROPOSAL_ONLY_UNTIL_EXACT_REPLAY"
PREREG_REL = Path("research/TRUMP_BICAMERAL_CONNECTED_CORE_EXPLANATION_PREREGISTRATION_2026-09-15.json")
PREREG_COMMIT = "259dcb8a4d5267a62a7b9a3d796f9295ff9c6907"
PREREG_GIT_BLOB_SHA1 = "8e7734d2b7776e8ab28c01aa4a56f770abf1c098"
SEALED_COMPOSER_REL = Path("research/tools/apma_unseen_basis/compositional_basis.py")
SEALED_COMPOSER_GIT_BLOB_SHA1 = "fdc83a3368a4ad362f00d3ee8aad958f06f8d264"


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
    prereg_obj = json.loads(prereg.read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(prereg) == PREREG_GIT_BLOB_SHA1,
        "prereg_status": prereg_obj.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_gate": prereg_obj.get("frozen_gate") == "TRUMP_BICAMERAL_CONNECTED_CORE_EXPLANATION_INDUCTION_FALSIFIER_GATE",
        "sealed_composer_blob": git_blob_sha1(composer) == SEALED_COMPOSER_GIT_BLOB_SHA1,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "SCOPE": "RAW_EXPLICIT_TABLE_CONNECTED_MIXED_CORES_WITH_SINGLE_VARIABLE_INCIDENCE_ARTICULATION",
        "LLM_AUTHORITY": "NONE",
        "SEMANTIC_SIMILARITY_AUTHORITY": "NONE",
        "SOLVER_EXECUTION_IN_THIS_GATE": "FORBIDDEN",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
    }


def incidence_graph(canonical: dict) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for v in canonical["variables"]:
        graph[f"v:{v}"] = set()
    for i, row in enumerate(canonical["constraints"]):
        c = f"c:{i}"
        graph[c] = set()
        for v in row["scope"]:
            n = f"v:{v}"
            graph[c].add(n)
            graph[n].add(c)
    return graph


def _components_without_node(graph: dict[str, set[str]], removed: str | None = None) -> list[set[str]]:
    live = [n for n in graph if n != removed]
    seen: set[str] = set()
    out: list[set[str]] = []
    for start in sorted(live):
        if start in seen:
            continue
        stack = [start]
        comp: set[str] = set()
        while stack:
            node = stack.pop()
            if node in seen or node == removed:
                continue
            seen.add(node)
            comp.add(node)
            for nxt in graph[node]:
                if nxt != removed and nxt not in seen:
                    stack.append(nxt)
        out.append(comp)
    return out


def observation_receipt(canonical: dict) -> dict:
    graph = incidence_graph(canonical)
    base_components = _components_without_node(graph)
    constraint_nodes = {n for n in graph if n.startswith("c:")}
    articulation_variables: list[int] = []
    split_counts: dict[str, int] = {}
    for v in canonical["variables"]:
        comps = _components_without_node(graph, f"v:{v}")
        with_constraints = [c for c in comps if c & constraint_nodes]
        split_counts[str(v)] = len(with_constraints)
        if len(with_constraints) > 1:
            articulation_variables.append(v)
    body = {
        "role": "HRAIN_DETERMINISTIC_STRUCTURAL_OBSERVATION",
        "incidence_node_count": len(graph),
        "incidence_edge_count": sum(len(x) for x in graph.values()) // 2,
        "input_component_count": len([c for c in base_components if c & constraint_nodes]),
        "variable_degrees": {str(v): len(graph[f"v:{v}"]) for v in canonical["variables"]},
        "constraint_scopes": [list(row["scope"]) for row in canonical["constraints"]],
        "single_variable_split_counts": split_counts,
        "articulation_variables": articulation_variables,
    }
    body["observation_sha256"] = sha256_obj(body)
    return body


def proposal_records(canonical: dict, observation: dict) -> list[dict]:
    raw_hash = sha256_obj(canonical)
    proposals: list[dict] = []
    for v in observation["articulation_variables"]:
        body = {
            "role": "INAIHR_CANDIDATE_ONLY_STRUCTURAL_PROPOSAL",
            "kind": "SINGLE_VARIABLE_ARTICULATION_CONDITIONING",
            "raw_object_sha256": raw_hash,
            "observation_sha256": observation["observation_sha256"],
            "separator_variables": [v],
            "branch_values": [0, 1],
            "truth_authority": False,
            "proof_authority": False,
            "automatic_promotion": False,
        }
        body["proposal_sha256"] = sha256_obj(body)
        proposals.append(body)
    return sorted(proposals, key=lambda x: (x["separator_variables"], x["proposal_sha256"]))


def restrict_on_value(canonical: dict, variable: int, value: int) -> dict:
    if variable not in canonical["variables"] or value not in (0, 1):
        raise ValueError("INVALID_RESTRICTION")
    constraints: list[dict] = []
    branch_unsat = False
    for row in canonical["constraints"]:
        scope = list(row["scope"])
        allowed = [tuple(int(x) for x in t) for t in row["allowed"]]
        if variable not in scope:
            constraints.append({"id": row["id"], "scope": scope, "allowed": [list(t) for t in allowed]})
            continue
        pos = scope.index(variable)
        new_scope = scope[:pos] + scope[pos + 1 :]
        new_tuples = sorted({t[:pos] + t[pos + 1 :] for t in allowed if t[pos] == value})
        if not new_tuples:
            branch_unsat = True
            break
        if not new_scope:
            # A surviving zero-arity tuple is true and contributes no residual constraint.
            continue
        constraints.append({"id": row["id"], "scope": new_scope, "allowed": [list(t) for t in new_tuples]})

    residual_variables = sorted({v for row in constraints for v in row["scope"]})
    residual = {"variables": residual_variables, "constraints": constraints}
    body = {
        "assigned_variable": variable,
        "assigned_value": value,
        "branch_unsat": branch_unsat,
        "residual": residual if not branch_unsat else None,
    }
    body["restriction_sha256"] = sha256_obj(body)
    return body


def replay_branch(restriction: dict) -> dict:
    if restriction["branch_unsat"]:
        return {
            "status": "EXACT_UNSAT_BY_EMPTY_RELATION",
            "restriction_sha256": restriction["restriction_sha256"],
            "admitted": True,
            "basis_replay": None,
        }
    residual = restriction["residual"]
    if not residual["constraints"]:
        return {
            "status": "EXACT_TRIVIAL_SAT_NO_RESIDUAL_CONSTRAINTS",
            "restriction_sha256": restriction["restriction_sha256"],
            "admitted": True,
            "basis_replay": None,
        }
    cert = induce_compositional_basis(residual)
    admitted = cert.get("status") == "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO"
    return {
        "status": "ADMIT_BRANCH_EXACT_BASIS_PORTFOLIO" if admitted else "REJECT_BRANCH_EXPLANATION",
        "restriction_sha256": restriction["restriction_sha256"],
        "admitted": admitted,
        "basis_replay": cert,
    }


def redteam_proposal(canonical: dict, proposal: dict) -> dict:
    raw_hash = sha256_obj(canonical)
    expected = dict(proposal)
    claimed = expected.pop("proposal_sha256", None)
    provenance_ok = (
        isinstance(claimed, str)
        and sha256_obj(expected) == claimed
        and proposal.get("raw_object_sha256") == raw_hash
        and proposal.get("kind") == "SINGLE_VARIABLE_ARTICULATION_CONDITIONING"
        and proposal.get("branch_values") == [0, 1]
        and isinstance(proposal.get("separator_variables"), list)
        and len(proposal["separator_variables"]) == 1
        and proposal["separator_variables"][0] in canonical["variables"]
    )
    if not provenance_ok:
        return {"status": "REJECT_TAMPERED_PROVENANCE", "proposal_sha256": claimed, "provenance_ok": False}

    variable = proposal["separator_variables"][0]
    branches = []
    for value in (0, 1):
        restriction = restrict_on_value(canonical, variable, value)
        replay = replay_branch(restriction)
        branches.append({"value": value, "restriction": restriction, "replay": replay})

    all_admitted = all(row["replay"]["admitted"] for row in branches)
    obligations = {
        "P2_content_bound_proposal": provenance_ok,
        "P3_exact_two_boolean_branches": [row["value"] for row in branches] == [0, 1],
        "P4_exact_restriction_receipts_present": all(bool(row["restriction"].get("restriction_sha256")) for row in branches),
        "P5_sealed_compositional_replay_or_exact_terminal": all(row["replay"]["status"] in {"ADMIT_BRANCH_EXACT_BASIS_PORTFOLIO", "EXACT_UNSAT_BY_EMPTY_RELATION", "EXACT_TRIVIAL_SAT_NO_RESIDUAL_CONSTRAINTS"} for row in branches),
        "P6_all_branches_admitted": all_admitted,
        "P8_no_solver_before_admission": True,
    }
    result = {
        "status": "PASS_PROPOSAL_EXACT_REPLAY" if all(obligations.values()) else "REJECT_PROPOSAL_EXACT_REPLAY",
        "proposal_sha256": proposal["proposal_sha256"],
        "separator_variables": [variable],
        "provenance_ok": provenance_ok,
        "branches": branches,
        "obligations": obligations,
        "resource_receipt": {
            "candidate_separator_count_charged": 1,
            "boolean_branch_count": 2,
            "full_variable_cube_enumerated": False,
            "generic_transfer_calls": 0,
            "solver_invocations": 0,
            "hidden_debt_claimed_free": False,
        },
    }
    result["redteam_sha256"] = sha256_obj(result)
    return result


def explain_connected_mixed_core(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonical = canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {
            "artifact_id": ARTIFACT_ID,
            "authority": AUTHORITY,
            "status": "REJECT_RAW_INPUT",
            "reason": str(exc),
            "source_guard": guard,
            "metrics": {"solver_invocations": 0, "generic_transfer_calls": 0, "full_variable_assignments_enumerated": 0},
            "scientific_firewall": firewall(),
        }

    raw_hash = sha256_obj(canonical)
    observation = observation_receipt(canonical)
    proposals = proposal_records(canonical, observation)
    redteams = [redteam_proposal(canonical, p) for p in proposals]
    passing = [r for r in redteams if r.get("status") == "PASS_PROPOSAL_EXACT_REPLAY"]
    selected = passing[0] if passing else None
    terminal = "ADMIT_EXACT_STRUCTURAL_EXPLANATION" if selected else "OPEN_NO_EXACT_BICAMERAL_EXPLANATION"

    receipt = {
        "raw_object_sha256": raw_hash,
        "observation_sha256": observation["observation_sha256"],
        "proposal_sha256": selected.get("proposal_sha256") if selected else None,
        "redteam_sha256": selected.get("redteam_sha256") if selected else None,
        "terminal": terminal,
    }
    receipt["bicameral_receipt_sha256"] = sha256_obj(receipt)

    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "prereg_commit": PREREG_COMMIT,
        "source_guard": guard,
        "status": terminal,
        "raw_object_sha256": raw_hash,
        "observation": observation,
        "proposals": proposals,
        "redteams": redteams,
        "selected_explanation": selected,
        "provenance_receipt": receipt,
        "execution_authorized": False,
        "metrics": {
            "candidate_variables_examined": len(canonical["variables"]),
            "structural_proposals_emitted": len(proposals),
            "exact_branch_replays": 2 * len(proposals),
            "full_variable_assignments_enumerated": 0,
            "generic_transfer_calls": 0,
            "solver_invocations": 0,
            "cartesian_products_materialized": 0,
        },
        "complexity": {
            "claim": "POLYNOMIAL_IN_EXPLICIT_TABLE_INPUT_FOR_FROZEN_SINGLE_VARIABLE_PROPOSAL_LIBRARY",
            "reason": "At most V structural proposals; exactly two restrictions per proposal; each restriction scans explicit tuples and invokes only the sealed polynomial explicit-table basis inducer.",
        },
        "scientific_firewall": firewall(),
    }


def positive_connected_articulation() -> dict:
    return {
        "variables": [0, 1, 2, 3],
        "constraints": [
            {"id": "opaque_a", "scope": [0, 1], "allowed": [[0, 1], [1, 0], [1, 1]]},
            {"id": "opaque_b", "scope": [1, 2, 3], "allowed": [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]},
        ],
    }


def negative_biconnected_mixed() -> dict:
    return {
        "variables": [0, 1, 2],
        "constraints": [
            {"id": "opaque_a", "scope": [0, 1], "allowed": [[0, 1], [1, 0], [1, 1]]},
            {"id": "opaque_b", "scope": [0, 1, 2], "allowed": [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]},
        ],
    }


def injected_hint_control() -> dict:
    raw = positive_connected_articulation()
    raw["separator"] = 1
    return raw


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "positive": explain_connected_mixed_core(positive_connected_articulation()),
        "negative_biconnected": explain_connected_mixed_core(negative_biconnected_mixed()),
        "negative_injected_hint": explain_connected_mixed_core(injected_hint_control()),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
