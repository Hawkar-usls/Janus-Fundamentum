from __future__ import annotations

import copy
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_bucket_k5_raw_semantic_forensic import forensic as k5_parent
from research.tools.apma_bucket_closed_two_factor import two_factor_component as two_factor

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-CLOSED-INTERNAL-TWO-FACTOR-F-FACTOR-CARRIER-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_V1"

PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "1240d183461bfab4defe42df14ffdb2df31396da"
THEOREM = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_F_FACTOR_CARRIER_THEOREM_CANDIDATE_2026-09-15.md")
THEOREM_BLOB = "3c3db06ec64f6f130deca98fef0e0f0f060ac562"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.17.json")
PARENT_STATE_BLOB = "bf871e4e574381373f8c4d207eca9a12c9175ea4"
V36 = Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py")
V36_BLOB = "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8"
V38 = Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py")
V38_BLOB = "cd17292b7451b03b966dbcf62d1b6e4c767f7ac0"
GUARDED = Path("research/tools/apma_guarded_elimination/guarded_bounded_output_elimination.py")
GUARDED_BLOB = "314034bac990e524d1db7743aef0aebd3b4565c1"
PARENT_SUPPORT = Path("research/tools/apma_cut_support_carrier/cut_support_carrier.py")
PARENT_SUPPORT_BLOB = "012aa1acf52fa12de26bb64df303b2208d396ea9"
COMMON_CORE = Path("research/tools/apma_bucket_common_core/common_core_semijoin_prefilter.py")
COMMON_CORE_BLOB = "f103bf9b14e3b208200f429b75d0858c4963fa7c"
K5_PARENT = Path("research/tools/apma_bucket_k5_raw_semantic_forensic/forensic.py")
K5_PARENT_BLOB = "4128f0db77dfc1391b6ec539f201250bfb3d8b6e"
MATCHING_CORE = Path("research/tools/apma_bucket_closed_two_factor/matching_core.py")
MATCHING_CORE_BLOB = "347022fca80b5b5788fc3946368a5cfaf69bd762"
TWO_FACTOR_COMPONENT = Path("research/tools/apma_bucket_closed_two_factor/two_factor_component.py")
TWO_FACTOR_COMPONENT_BLOB = "06a8980dc56d8d098618ddee0fe74e5b328dcac7"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg_blob": git_blob(r / PREREG) == PREREG_BLOB,
        "theorem_candidate_blob": git_blob(r / THEOREM) == THEOREM_BLOB,
        "parent_v3_17_blob": git_blob(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "v3_6_blob": git_blob(r / V36) == V36_BLOB,
        "v3_8_blob": git_blob(r / V38) == V38_BLOB,
        "guarded_blob": git_blob(r / GUARDED) == GUARDED_BLOB,
        "parent_support_blob": git_blob(r / PARENT_SUPPORT) == PARENT_SUPPORT_BLOB,
        "common_core_blob": git_blob(r / COMMON_CORE) == COMMON_CORE_BLOB,
        "k5_parent_blob": git_blob(r / K5_PARENT) == K5_PARENT_BLOB,
        "matching_core_blob": git_blob(r / MATCHING_CORE) == MATCHING_CORE_BLOB,
        "two_factor_component_blob": git_blob(r / TWO_FACTOR_COMPONENT) == TWO_FACTOR_COMPONENT_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict[str, Any]:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "SIZE4_BRANCHING_LICENSED": False,
        "BOUNDARY_BEARING_TWO_FACTOR_COMPONENTS": "OPEN",
        "MULTIPLE_COMMON_CORE_STATES": "OPEN",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE",
    }


def explicit_size(raw: dict[str, Any]) -> int:
    total = len(raw.get("variables", []))
    for rel in raw.get("constraints", []):
        total += 1 + len(rel.get("scope", []))
        for row in rel.get("allowed", []):
            total += len(row)
    return max(1, total)


def proposal_record(prep: dict[str, Any]) -> dict[str, Any]:
    body = {
        "kind": "UNIQUE_CORE_CLOSED_INTERNAL_TWO_FACTOR_PLUS_SEALED_LE2_PORTFOLIO",
        "raw_object_sha256": sha256_obj(prep["canonical"]),
        "failed_variable": int(prep["ready"]["failed_variable"]),
        "target_component": list(prep["ready"]["component"]),
        "parent_cut": list(prep["ready"]["cut"]),
        "common_core": list(prep["core"]),
        "unique_common_state": list(prep["state"]),
        "residual_components": [list(c) for c in prep["residual_components"]],
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(prep: dict[str, Any], proposal: dict[str, Any]) -> bool:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    return isinstance(claimed, str) and sha256_obj(body) == claimed and proposal == proposal_record(prep)


def _le2_carrier(prep: dict[str, Any], component: list[int], ordinal: int) -> dict[str, Any]:
    cut = {int(v) for v in prep["ready"]["cut"]}
    if len(component) == 1:
        carrier = v36._singleton_carrier(prep["conditioned"][component[0]], prep["core"], cut, ordinal)
    elif len(component) == 2:
        carrier = v36._pair_carrier(
            prep["conditioned"][component[0]],
            prep["conditioned"][component[1]],
            prep["core"],
            cut,
            ordinal,
        )
    else:
        raise ValueError("LE2_HELPER_CALLED_ON_GT2_COMPONENT")
    if carrier.get("status") == "ADMIT_COMPONENT":
        carrier["carrier_class"] = "SEALED_V3_6_LE2"
    return carrier


def build_mixed_portfolio(prep: dict[str, Any]) -> dict[str, Any]:
    carriers: list[dict[str, Any]] = []
    public: list[dict[str, Any]] = []
    boundary_constraints: list[dict[str, Any]] = []
    two_factor_components = 0
    pair_components = 0
    pair_joins = 0
    pair_comparisons = 0
    total_boundary_rows = 0
    total_gadget_vertices = 0
    total_gadget_edges = 0
    total_matching_calls = 0

    for ordinal, component in enumerate(prep["residual_components"]):
        comp = list(component)
        if len(comp) <= 2:
            carrier = _le2_carrier(prep, comp, ordinal)
            if carrier.get("status") != "ADMIT_COMPONENT":
                return carrier
            carriers.append(carrier)
            public.append({"carrier_class": "SEALED_V3_6_LE2", **carrier["public"]})
            pair_components += int(carrier["public"].get("kind") == "PAIR_RESIDUAL_COMPONENT")
            pair_joins += int(carrier["public"].get("pair_join_count", 0))
            pair_comparisons += int(carrier["public"].get("pair_row_comparisons", 0))
            total_boundary_rows += len(carrier["boundary_rows"])
            if carrier["boundary_scope"]:
                boundary_constraints.append({
                    "id": f"residual_component_{ordinal}",
                    "scope": list(carrier["boundary_scope"]),
                    "allowed": [list(row) for row in carrier["boundary_rows"]],
                })
            continue

        recognized = two_factor.recognize_component(
            prep["conditioned"], comp, prep["core"], prep["ready"]["cut"]
        )
        if recognized.get("status") == "OPEN_TWO_FACTOR_BOUNDARY_INTERFACE_NOT_SEALED":
            return {
                "status": "OPEN_TWO_FACTOR_BOUNDARY_INTERFACE_NOT_SEALED",
                "component": comp,
                "boundary_scope": list(recognized.get("boundary_scope", [])),
                "solver_calls": 0,
            }
        if recognized.get("status") != "ADMIT_CLOSED_INTERNAL_EXACT_TWO_FACTOR_COMPONENT":
            return {
                "status": "OPEN_UNADMITTED_RESIDUAL_GT2_COMPONENT_BEFORE_SOLVER_EXECUTION",
                "component": comp,
                "recognition": recognized,
                "solver_calls": 0,
            }

        solved = two_factor.solve_component(recognized)
        if solved.get("status") == "OPEN_MATCHING_CARRIER_INTERNAL_FAILURE":
            return solved
        if solved.get("status") == "UNSAT_BY_VERIFIED_TWO_FACTOR_TUTTE_OBSTRUCTION":
            return {
                "status": "EXACT_UNSAT_BY_VERIFIED_CLOSED_INTERNAL_TWO_FACTOR_TUTTE_OBSTRUCTION",
                "component": comp,
                "graph": recognized["graph"],
                "gadget": solved["gadget_public"],
                "certificate": solved["certificate"],
                "static_verification": solved["static_verification"],
                "obstruction_derivation": solved["obstruction_derivation"],
                "global_residual_cartesian_products_materialized": 0,
                "size4_boolean_separator_assignments_enumerated": 0,
            }
        if solved.get("status") != "SAT_BY_VERIFIED_TWO_FACTOR_PERFECT_MATCHING":
            return {"status": "OPEN_MATCHING_CARRIER_INTERNAL_FAILURE", "detail": solved}

        residual_assignment = {
            int(k): int(v) for k, v in solved["static_verification"]["residual_assignment"].items()
        }
        conditioned_replay = two_factor.recover_conditioned_factor_rows(
            prep["conditioned"], recognized, prep["core"], tuple(prep["state"]), residual_assignment
        )
        if not conditioned_replay["ok"]:
            return {
                "status": "OPEN_MATCHING_CARRIER_INTERNAL_FAILURE",
                "reason": "CONDITIONED_FACTOR_REPLAY_FAILED_AFTER_STATIC_SAT_CERTIFICATE",
                "detail": conditioned_replay,
            }

        carrier = {
            "status": "ADMIT_COMPONENT",
            "carrier_class": "CLOSED_INTERNAL_TWO_FACTOR",
            "component_ordinal": ordinal,
            "recognized": recognized,
            "solution": solved,
            "residual_assignment": residual_assignment,
            "conditioned_rows": conditioned_replay["chosen_rows"],
            "boundary_scope": [],
            "boundary_rows": [tuple()],
        }
        carriers.append(carrier)
        two_factor_components += 1
        total_gadget_vertices += int(solved["gadget_public"]["vertex_count"])
        total_gadget_edges += int(solved["gadget_public"]["edge_count"])
        total_matching_calls += 1
        public.append({
            "carrier_class": "CLOSED_INTERNAL_TWO_FACTOR",
            "component_ordinal": ordinal,
            "graph": recognized["graph"],
            "gadget": solved["gadget_public"],
            "certificate": solved["certificate"],
            "static_certificate_verified": bool(solved["static_verification"]["ok"]),
            "boundary_scope": [],
        })

    if two_factor_components == 0:
        return {
            "status": "OPEN_NO_CLOSED_INTERNAL_TWO_FACTOR_COMPONENT",
            "solver_calls": 0,
        }

    return {
        "status": "ADMIT_MIXED_CLOSED_TWO_FACTOR_PORTFOLIO",
        "carriers": carriers,
        "portfolio_public": public,
        "boundary_constraints": boundary_constraints,
        "metrics": {
            "residual_component_count": len(carriers),
            "two_factor_component_count": two_factor_components,
            "pair_component_count": pair_components,
            "pair_join_count": pair_joins,
            "pair_row_comparisons": pair_comparisons,
            "total_boundary_rows_stored": total_boundary_rows,
            "total_tutte_gadget_vertices": total_gadget_vertices,
            "total_tutte_gadget_edges": total_gadget_edges,
            "maximum_matching_calls_for_sat_components": total_matching_calls,
            "size4_boolean_separator_assignments_enumerated": 0,
            "separator_sets_size_ge_3_executed_as_boolean_branches": 0,
            "global_residual_cartesian_products_materialized": 0,
            "join_chains_materialized": 0,
            "budget_raised": False,
        },
    }


def reconstruct_original(
    prep: dict[str, Any],
    portfolio: dict[str, Any],
    transformed_assignment: dict[int, int],
) -> dict[str, Any]:
    assignment = {int(k): int(v) for k, v in transformed_assignment.items()}
    cut = {int(v) for v in prep["ready"]["cut"]}
    target_internal = {
        int(v)
        for gi in prep["ready"]["component"]
        for v in prep["canonical"]["constraints"][gi]["scope"]
        if int(v) not in cut
    }
    for v in target_internal:
        assignment.pop(v, None)
    for v, bit in zip(prep["core"], prep["state"]):
        assignment[int(v)] = int(bit)

    chosen_rows: list[dict[str, Any]] = []
    for carrier in portfolio["carriers"]:
        if carrier["carrier_class"] == "SEALED_V3_6_LE2":
            boundary = carrier["boundary_scope"]
            key = tuple(int(assignment[v]) for v in boundary)
            witness = carrier["witness"].get(key)
            if witness is None:
                return {"ok": False, "reason": "BOUNDARY_TUPLE_MISSING_FROM_SEALED_LE2_COMPONENT"}
            rows = [witness] if len(carrier["factors"]) == 1 else list(witness)
            for factor, row in zip(carrier["factors"], rows):
                for v, bit in zip(factor["scope"], row):
                    v, bit = int(v), int(bit)
                    if v in assignment and assignment[v] != bit:
                        return {"ok": False, "reason": "SEALED_LE2_RECONSTRUCTION_CONFLICT", "factor_id": factor["id"], "variable": v}
                    assignment[v] = bit
                chosen_rows.append({"factor_id": str(factor["id"]), "sorted_row": list(row), "carrier_class": "SEALED_V3_6_LE2"})
            continue

        if carrier["carrier_class"] != "CLOSED_INTERNAL_TWO_FACTOR":
            return {"ok": False, "reason": "UNKNOWN_CARRIER_CLASS"}
        for var, bit in carrier["residual_assignment"].items():
            var, bit = int(var), int(bit)
            if var in assignment and assignment[var] != bit:
                return {"ok": False, "reason": "TWO_FACTOR_RECONSTRUCTION_CONFLICT", "variable": var}
            assignment[var] = bit
        for chosen in carrier["conditioned_rows"]:
            factor = prep["conditioned"][int(chosen["conditioned_index"])]
            row = tuple(int(x) for x in chosen["sorted_row"])
            for v, bit in zip(factor["scope"], row):
                v, bit = int(v), int(bit)
                if v in assignment and assignment[v] != bit:
                    return {"ok": False, "reason": "TWO_FACTOR_ROW_RECONSTRUCTION_CONFLICT", "factor_id": factor["id"], "variable": v}
                assignment[v] = bit
            chosen_rows.append({"factor_id": str(factor["id"]), "sorted_row": list(row), "carrier_class": "CLOSED_INTERNAL_TWO_FACTOR"})

    verified = guarded.verify_original_assignment(prep["canonical"], assignment)
    return {
        "ok": bool(verified),
        "reason": "ORIGINAL_RELATION_REPLAY" if verified else "ORIGINAL_RELATION_REPLAY_FAILED",
        "assignment": assignment,
        "chosen_rows": chosen_rows,
    }


def build(raw: dict[str, Any], proposal_override: dict[str, Any] | None = None) -> dict[str, Any]:
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return prep
    proposal = proposal_override or proposal_record(prep)
    if not verify_proposal(prep, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE"}

    portfolio = build_mixed_portfolio(prep)
    if portfolio.get("status") == "EXACT_UNSAT_BY_VERIFIED_CLOSED_INTERNAL_TWO_FACTOR_TUTTE_OBSTRUCTION":
        return {
            **portfolio,
            "proposal": proposal,
            "witness": None,
            "witness_verified": True,
        }
    if portfolio.get("status") != "ADMIT_MIXED_CLOSED_TWO_FACTOR_PORTFOLIO":
        return portfolio

    transformed = canonicalize_raw(v36._transformed_raw(prep, portfolio))
    transformed_components = parent_support.constraint_components_after_cut(
        transformed, list(prep["ready"]["cut"])
    )
    handoff = guarded.run_guarded_elimination(
        transformed, list(prep["ready"]["cut"]), transformed_components
    )
    L = explicit_size(prep["canonical"])
    receipt = {
        "original_explicit_input_size_L": L,
        "failed_variable": int(prep["ready"]["failed_variable"]),
        "common_core": list(prep["core"]),
        "unique_common_state": list(prep["state"]),
        "residual_components": [list(c) for c in prep["residual_components"]],
        "residual_component_sizes": [len(c) for c in prep["residual_components"]],
        **portfolio["metrics"],
        "transformed_handoff_terminal": handoff.get("status"),
        "external_matching_library_calls": 0,
        "raw_cut_assignments_enumerated": 0,
        "uniform_complexity_envelope": "O(L^4)",
        "certificate_bytes_envelope": "O(L^2)",
    }
    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {
            "status": "EXACT_UNSAT_BY_CLOSED_TWO_FACTOR_FACTORIZED_BOUNDARY_HANDOFF",
            "proposal": proposal,
            "portfolio": portfolio["portfolio_public"],
            "receipt": receipt,
            "witness": None,
            "witness_verified": True,
        }
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {
            "status": "OPEN_CLOSED_TWO_FACTOR_TRANSFORMED_HANDOFF",
            "proposal": proposal,
            "portfolio": portfolio["portfolio_public"],
            "receipt": receipt,
            "handoff": {k: v for k, v in handoff.items() if k != "records_internal"},
        }

    transformed_assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
    reconstruction = reconstruct_original(prep, portfolio, transformed_assignment)
    receipt["original_witness_verified"] = bool(reconstruction["ok"])
    if not reconstruction["ok"]:
        return {
            "status": "OPEN_ORIGINAL_WITNESS_REPLAY_FAILURE",
            "proposal": proposal,
            "portfolio": portfolio["portfolio_public"],
            "receipt": receipt,
            "reconstruction": reconstruction,
        }
    return {
        "status": "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_CLOSED_INTERNAL_TWO_FACTOR_FACTORIZED_PAYLOAD_PORTFOLIO",
        "proposal": proposal,
        "portfolio": portfolio["portfolio_public"],
        "receipt": receipt,
        "witness": {str(v): int(reconstruction["assignment"][v]) for v in sorted(reconstruction["assignment"])},
        "witness_verified": True,
        "reconstruction_rows": reconstruction["chosen_rows"],
    }


def explain(raw: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": guard, "scientific_firewall": firewall()}
    carrier = build(raw)
    return {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "status": carrier["status"],
        "source_guard": guard,
        "carrier": carrier,
        "scientific_firewall": firewall(),
    }


def positive_k5_control() -> dict[str, Any]:
    return k5_parent.build_raw_k5("EXACT_2_OF_4")


def _weight_two_patterns(d: int) -> list[tuple[int, ...]]:
    rows: list[tuple[int, ...]] = []
    for chosen in itertools.combinations(range(d), 2):
        row = [0] * d
        for p in chosen:
            row[p] = 1
        rows.append(tuple(row))
    return sorted(rows)


def cubic_three_bridge_unsat_control() -> dict[str, Any]:
    raw = copy.deepcopy(cc_v1.filtered_still_overbudget_control())
    target_count = 16
    central = 15
    graph_edges: list[tuple[int, int]] = []
    for lobe in range(3):
        base = 5 * lobe
        x, a, b, c, d = base, base + 1, base + 2, base + 3, base + 4
        graph_edges.extend([
            (a, c), (a, d), (b, c), (b, d), (c, d),
            (a, x), (x, b), (x, central),
        ])
    graph_edges = sorted(tuple(sorted(e)) for e in graph_edges)
    if len(graph_edges) != 24 or len(set(graph_edges)) != 24:
        raise RuntimeError("CUBIC_CONTROL_EDGE_CONSTRUCTION_BROKEN")
    degree = {v: 0 for v in range(target_count)}
    for a, b in graph_edges:
        degree[a] += 1
        degree[b] += 1
    if any(degree[v] != 3 for v in range(target_count)):
        raise RuntimeError(f"CUBIC_CONTROL_NOT_CUBIC:{degree}")

    start = max(int(v) for v in raw["variables"]) + 1
    pair_to_var = {edge: start + i for i, edge in enumerate(graph_edges)}
    raw["variables"].extend(range(start, start + len(graph_edges)))
    patterns = _weight_two_patterns(3)
    for vertex in range(target_count):
        rel = next(r for r in raw["constraints"] if r["id"] == f"sticky_{vertex}")
        old_scope = [int(v) for v in rel["scope"]]
        core_scope = old_scope[:-2]
        core_rows = sorted({tuple(int(x) for x in row[:-2]) for row in rel["allowed"]})
        incident = sorted(
            pair_to_var[edge]
            for edge in graph_edges
            if vertex in edge
        )
        if len(incident) != 3:
            raise RuntimeError("CUBIC_CONTROL_INCIDENT_COUNT_BROKEN")
        rel["scope"] = core_scope + incident
        rel["allowed"] = [list(core) + list(bits) for core in core_rows for bits in patterns]
    return raw


def malformed_relation_control() -> dict[str, Any]:
    raw = positive_k5_control()
    rel = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    if len(rel["allowed"]) < 2:
        raise RuntimeError("POSITIVE_K5_CONTROL_UNEXPECTED_ROWS")
    rel["allowed"] = rel["allowed"][:-1]
    return raw


def invalid_incidence_control() -> dict[str, Any]:
    raw = positive_k5_control()
    s0 = next(r for r in raw["constraints"] if r["id"] == "sticky_0")
    s1 = next(r for r in raw["constraints"] if r["id"] == "sticky_1")
    s2 = next(r for r in raw["constraints"] if r["id"] == "sticky_2")
    tail0, tail1, tail2 = [int(v) for v in s0["scope"][-4:]], [int(v) for v in s1["scope"][-4:]], [int(v) for v in s2["scope"][-4:]]
    shared01 = sorted(set(tail0) & set(tail1))
    if len(shared01) != 1 or shared01[0] in tail2:
        raise RuntimeError("K5_CONTROL_EDGE_IDENTIFICATION_FAILED")
    s2["scope"][-1] = shared01[0]
    return raw


def boundary_bearing_unit_control() -> dict[str, Any]:
    raw = positive_k5_control()
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"status": "CONTROL_PREP_NOT_READY", "prep": prep}
    gt2 = [list(c) for c in prep["residual_components"] if len(c) > 2]
    if len(gt2) != 1:
        return {"status": "CONTROL_EXPECTED_ONE_GT2", "components": gt2}
    first = two_factor.recognize_component(prep["conditioned"], gt2[0], prep["core"], prep["ready"]["cut"])
    if first.get("status") != "ADMIT_CLOSED_INTERNAL_EXACT_TWO_FACTOR_COMPONENT":
        return {"status": "CONTROL_BASE_RECOGNITION_FAILED", "recognition": first}
    edge_var = int(first["edge_records"][0]["var"])
    mutated_cut = list(prep["ready"]["cut"]) + [edge_var]
    return two_factor.recognize_component(prep["conditioned"], gt2[0], prep["core"], mutated_cut)


def tampered_sat_certificate_control() -> dict[str, Any]:
    raw = positive_k5_control()
    prep = v38._prepare(raw)
    gt2 = next(list(c) for c in prep["residual_components"] if len(c) > 2)
    recognized = two_factor.recognize_component(prep["conditioned"], gt2, prep["core"], prep["ready"]["cut"])
    solved = two_factor.solve_component(recognized)
    if solved.get("status") != "SAT_BY_VERIFIED_TWO_FACTOR_PERFECT_MATCHING":
        return {"status": "CONTROL_BASE_NOT_SAT", "solved": solved}
    cert = copy.deepcopy(solved["certificate"])
    cert["perfect_matching"] = cert["perfect_matching"][:-1]
    return two_factor.verify_sat_certificate(recognized, cert)


def tampered_unsat_certificate_control() -> dict[str, Any]:
    raw = cubic_three_bridge_unsat_control()
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return {"status": "CONTROL_PREP_NOT_READY", "prep": prep}
    gt2 = [list(c) for c in prep["residual_components"] if len(c) > 2]
    if len(gt2) != 1:
        return {"status": "CONTROL_EXPECTED_ONE_GT2", "components": gt2}
    recognized = two_factor.recognize_component(prep["conditioned"], gt2[0], prep["core"], prep["ready"]["cut"])
    solved = two_factor.solve_component(recognized)
    if solved.get("status") != "UNSAT_BY_VERIFIED_TWO_FACTOR_TUTTE_OBSTRUCTION":
        return {"status": "CONTROL_BASE_NOT_UNSAT", "solved": solved}
    cert = copy.deepcopy(solved["certificate"])
    cert["tutte_obstruction_U"] = []
    return two_factor.verify_unsat_certificate(recognized, cert)


def multiple_common_core_control() -> dict[str, Any]:
    return v36.v35.multiple_common_core_states_control()


def tampered_proposal_control() -> dict[str, Any]:
    raw = positive_k5_control()
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return prep
    proposal = proposal_record(prep)
    proposal["residual_components"] = list(reversed(proposal["residual_components"]))
    return build(raw, proposal)


def main() -> None:
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "source_guard": source_guard(),
        "positive_k5": explain(positive_k5_control()),
        "unsat_cubic_three_bridge": explain(cubic_three_bridge_unsat_control()),
        "malformed_relation": explain(malformed_relation_control()),
        "invalid_incidence": explain(invalid_incidence_control()),
        "boundary_bearing_unit": boundary_bearing_unit_control(),
        "multiple_common_core": explain(multiple_common_core_control()),
        "tampered_proposal": tampered_proposal_control(),
        "tampered_sat_certificate": tampered_sat_certificate_control(),
        "tampered_unsat_certificate": tampered_unsat_certificate_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
