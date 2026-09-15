from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor_v1_1 as pair_gate

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-UNIFORM-RAW-DERIVED-AFFINE-BOUNDARY-FACTOR-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__NO_SCIENTIFIC_PROMOTION"
PREREG = Path("research/TRUMP_BICAMERAL_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "b5af3098fc0bb6b35981a29460f5113edebe0928"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.0.json")
PARENT_STATE_BLOB = "9d8b199b855e947e6adfdbce2ac5ae902556ad64"
SEALED_QUOTIENT = Path("research/tools/apma_interface_quotient/exact_quotient.py")
SEALED_QUOTIENT_BLOB = "cc331245bd71b6c83ab6c43b86f961fe53ed31c8"
HISTORICAL_AFFINE_SEAL = "cd170c2b51a1342eaa776e9ab55f7fbf5a103fa0"


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
    p = json.loads((r / PREREG).read_text(encoding="utf-8"))
    checks = {
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "prereg_frozen": p.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_gate": p.get("frozen_gate") == "TRUMP_BICAMERAL_COMPONENT_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR_FALSIFIER_GATE",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "sealed_quotient_blob": git_blob_sha1(r / SEALED_QUOTIENT) == SEALED_QUOTIENT_BLOB,
        "historical_affine_seal_declared": p.get("anti_loop", {}).get("historical_typed_affine_open_boundary_seal", {}).get("commit") == HISTORICAL_AFFINE_SEAL,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "GENERAL_MULTI_RELATION_BOUNDARY_COMPRESSION": "NOT_PROVED",
        "GENERAL_UNIFORM_BOUNDARY_ELIMINATION": "NOT_PROVED",
        "ALL_AFFINE_BOOLEAN_CSP_TRACTABILITY": "REUSED_KNOWN_SCOPED_STRUCTURE_NOT_NEW_GLOBAL_CLAIM",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        "SCOPE": "OVERWIDTH_CANONICAL_CUT_ALL_RAW_RELATIONS_EXACTLY_AFFINE_WITH_AT_LEAST_ONE_3PLUS_RELATION_COMPONENT",
    }


def _xor(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x ^ y for x, y in zip(a, b))


def _dot(a: list[int] | tuple[int, ...], b: list[int] | tuple[int, ...]) -> int:
    return sum((int(x) & int(y)) for x, y in zip(a, b)) & 1


def rref(rows: list[list[int]], ncols: int) -> tuple[list[list[int]], list[int]]:
    a = [list(map(lambda x: int(x) & 1, row[:ncols])) for row in rows if any(int(x) & 1 for x in row[:ncols])]
    pivots: list[int] = []
    rr = 0
    for c in range(ncols):
        pivot = next((i for i in range(rr, len(a)) if a[i][c]), None)
        if pivot is None:
            continue
        a[rr], a[pivot] = a[pivot], a[rr]
        for i in range(len(a)):
            if i != rr and a[i][c]:
                a[i] = [x ^ y for x, y in zip(a[i], a[rr])]
        pivots.append(c)
        rr += 1
        if rr == len(a):
            break
    a = [row for row in a if any(row)]
    return a, pivots


def nullspace(matrix: list[list[int]], ncols: int) -> list[list[int]]:
    rr, pivots = rref(matrix, ncols)
    free = [c for c in range(ncols) if c not in pivots]
    out: list[list[int]] = []
    for f in free:
        x = [0] * ncols
        x[f] = 1
        for i in range(len(pivots) - 1, -1, -1):
            p = pivots[i]
            s = 0
            for j in range(p + 1, ncols):
                s ^= rr[i][j] & x[j]
            x[p] = s
        out.append(x)
    return out


def solve_linear(equations: list[tuple[list[int], int]], nvars: int) -> dict:
    aug = [list(map(lambda x: int(x) & 1, coeff[:nvars])) + [int(rhs) & 1] for coeff, rhs in equations]
    pivots: list[int] = []
    rr = 0
    for c in range(nvars):
        pivot = next((i for i in range(rr, len(aug)) if aug[i][c]), None)
        if pivot is None:
            continue
        aug[rr], aug[pivot] = aug[pivot], aug[rr]
        for i in range(len(aug)):
            if i != rr and aug[i][c]:
                aug[i] = [x ^ y for x, y in zip(aug[i], aug[rr])]
        pivots.append(c)
        rr += 1
        if rr == len(aug):
            break
    for row in aug:
        if not any(row[:nvars]) and row[nvars]:
            return {"consistent": False, "solution": None, "rank": len(pivots), "rref": aug, "pivots": pivots}
    x = [0] * nvars
    for i, p in enumerate(pivots):
        x[p] = aug[i][nvars]
    return {"consistent": True, "solution": x, "rank": len(pivots), "rref": aug, "pivots": pivots}


def relation_affine_certificate(relation: dict) -> dict:
    scope = list(relation["scope"])
    rows = sorted({tuple(int(x) for x in raw) for raw in relation["allowed"]})
    if not rows:
        return {"affine": False, "reason": "EMPTY_RELATION"}
    a0 = rows[0]
    diffs = [_xor(r, a0) for r in rows]
    basis, pivots = rref([list(d) for d in diffs], len(scope))
    rank = len(pivots)
    expected = 1 << rank
    if len(rows) != expected:
        return {"affine": False, "reason": "CARDINALITY_NOT_POWER_OF_SPAN", "row_count": len(rows), "rank": rank, "expected_row_count": expected}
    orth = nullspace(basis, len(scope))
    equations = [(h, _dot(h, list(a0))) for h in orth]
    exact_rows_ok = all(all(_dot(coeff, list(row)) == rhs for coeff, rhs in equations) for row in rows)
    cert = {
        "affine": bool(exact_rows_ok),
        "reason": "EXACT_AFFINE_COSET_BY_RANK_CARDINALITY" if exact_rows_ok else "EQUATION_REPLAY_FAILED",
        "scope": scope,
        "anchor": list(a0),
        "row_count": len(rows),
        "direction_rank": rank,
        "expected_row_count": expected,
        "direction_basis": basis,
        "equations": [{"coeff": list(c), "rhs": int(rhs)} for c, rhs in equations],
        "ambient_cube_enumerated": False,
    }
    cert["certificate_sha256"] = sha256_obj(cert)
    return cert


def component_equations(canonical: dict, component: list[int], cut: list[int]) -> dict:
    vars_used = sorted({v for gi in component for v in canonical["constraints"][gi]["scope"]})
    pos = {v: i for i, v in enumerate(vars_used)}
    equations: list[tuple[list[int], int]] = []
    relation_certs = []
    for gi in component:
        rel = canonical["constraints"][gi]
        cert = relation_affine_certificate(rel)
        relation_certs.append({"global_relation_index": gi, "relation_id": rel["id"], "certificate": cert})
        if not cert.get("affine"):
            return {"status": "OPEN_NON_AFFINE_RAW_RELATION", "component": component, "failed_relation_index": gi, "relation_certs": relation_certs}
        for eq in cert["equations"]:
            coeff = [0] * len(vars_used)
            for lv, bit in zip(rel["scope"], eq["coeff"]):
                coeff[pos[lv]] ^= int(bit)
            equations.append((coeff, int(eq["rhs"])))
    B = list(cut)
    b_positions = [pos[v] for v in B if v in pos]
    if len(b_positions) != len(B):
        return {"status": "OPEN_COMPONENT_DOES_NOT_TOUCH_FULL_CUT_UNION", "component": component, "relation_certs": relation_certs}
    internal = [v for v in vars_used if v not in set(B)]
    u_positions = [pos[v] for v in internal]
    # A_U is m x |U|. Boundary consistency uses the left nullspace of A_U,
    # i.e. nullspace of A_U^T over m equation-combination coordinates.
    m = len(equations)
    au_t = [[equations[i][0][up] for i in range(m)] for up in u_positions]
    left_null = nullspace(au_t, m)
    boundary_eqs: list[tuple[list[int], int]] = []
    for y in left_null:
        coeff_b = [0] * len(B)
        rhs = 0
        for i, yi in enumerate(y):
            if not yi:
                continue
            rhs ^= equations[i][1]
            for bj, bp in enumerate(b_positions):
                coeff_b[bj] ^= equations[i][0][bp]
        boundary_eqs.append((coeff_b, rhs))
    reduced_aug = [c + [rhs] for c, rhs in boundary_eqs]
    # Canonicalize boundary equations by RREF on augmented rows, preserving contradiction rows.
    nB = len(B)
    aug = [row[:] for row in reduced_aug]
    pivots = []
    rridx = 0
    for c in range(nB):
        pivot = next((i for i in range(rridx, len(aug)) if aug[i][c]), None)
        if pivot is None:
            continue
        aug[rridx], aug[pivot] = aug[pivot], aug[rridx]
        for i in range(len(aug)):
            if i != rridx and aug[i][c]:
                aug[i] = [x ^ y for x, y in zip(aug[i], aug[rridx])]
        pivots.append(c)
        rridx += 1
    canon = []
    for row in aug:
        if any(row[:nB]) or row[nB]:
            canon.append((row[:nB], row[nB]))
    body = {
        "status": "ADMIT_AFFINE_COMPONENT_BOUNDARY_SYSTEM",
        "component": component,
        "component_variables": vars_used,
        "internal_variables": internal,
        "relation_certs": relation_certs,
        "equation_count": len(equations),
        "left_nullity": len(left_null),
        "boundary_equations": [{"coeff": c, "rhs": rhs} for c, rhs in canon],
        "raw_cut_assignments_enumerated": 0,
        "materialized_relation_joins": 0,
    }
    body["component_boundary_sha256"] = sha256_obj(body)
    body["_raw_equations"] = equations
    return body


def verify_original_assignment(canonical: dict, assignment: dict[int, int]) -> bool:
    for rel in canonical["constraints"]:
        if any(v not in assignment for v in rel["scope"]):
            return False
        tup = [int(assignment[v]) for v in rel["scope"]]
        if tup not in [list(map(int, row)) for row in rel["allowed"]]:
            return False
    return True


def proposal_record(canonical: dict, parent: dict, components: list[list[int]]) -> dict:
    body = {
        "role": "INAIHR_CANDIDATE_ONLY_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR",
        "kind": "RAW_AFFINE_RECOGNITION_GF2_BOUNDARY_ELIMINATION",
        "raw_object_sha256": sha256_obj(canonical),
        "parent_cut_receipt_sha256": parent["cut"]["cut_receipt_sha256"],
        "cut_variables": list(parent["cut"]["cut_variables"]),
        "components": components,
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha256_obj(body)
    return body


def verify_proposal(canonical: dict, parent: dict, components: list[list[int]], proposal: dict) -> bool:
    b = dict(proposal)
    claimed = b.pop("proposal_sha256", None)
    return (
        isinstance(claimed, str)
        and sha256_obj(b) == claimed
        and proposal.get("kind") == "RAW_AFFINE_RECOGNITION_GF2_BOUNDARY_ELIMINATION"
        and proposal.get("raw_object_sha256") == sha256_obj(canonical)
        and proposal.get("parent_cut_receipt_sha256") == parent["cut"]["cut_receipt_sha256"]
        and proposal.get("cut_variables") == parent["cut"]["cut_variables"]
        and proposal.get("components") == components
    )


def build_carrier(canonical: dict, parent: dict, components: list[list[int]], proposal: dict) -> dict:
    if not verify_proposal(canonical, parent, components, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE", "resource_receipt": {"raw_cut_assignments_enumerated": 0}}
    cut = list(parent["cut"]["cut_variables"])
    component_results = []
    global_boundary_eqs: list[tuple[list[int], int]] = []
    for comp in components:
        cr = component_equations(canonical, comp, cut)
        component_results.append(cr)
        if cr["status"] != "ADMIT_AFFINE_COMPONENT_BOUNDARY_SYSTEM":
            return {
                "status": cr["status"],
                "failed_component": comp,
                "component_results": component_results,
                "resource_receipt": {"raw_cut_assignments_enumerated": 0, "materialized_relation_joins": 0, "generic_transfer_calls": 0, "external_solver_calls": 0},
            }
        global_boundary_eqs.extend((list(e["coeff"]), int(e["rhs"])) for e in cr["boundary_equations"])
    bsolve = solve_linear(global_boundary_eqs, len(cut))
    resource = {
        "raw_cut_assignments_enumerated": 0,
        "materialized_relation_joins": 0,
        "cartesian_products_materialized": 0,
        "generic_transfer_calls": 0,
        "external_solver_calls": 0,
        "raw_relation_rows_scanned": sum(len(r["allowed"]) for r in canonical["constraints"]),
        "component_count": len(components),
        "relation_count": len(canonical["constraints"]),
        "boundary_equation_count": len(global_boundary_eqs),
    }
    public_components = []
    for cr in component_results:
        public_components.append({k: v for k, v in cr.items() if k != "_raw_equations"})
    if not bsolve["consistent"]:
        out = {
            "status": "EXACT_UNSAT_BY_AFFINE_BOUNDARY_INCONSISTENCY",
            "cut_variables": cut,
            "component_results": public_components,
            "global_boundary_rank": bsolve["rank"],
            "witness": None,
            "witness_verified": True,
            "resource_receipt": resource,
        }
        out["carrier_sha256"] = sha256_obj(out)
        return out
    bvals = bsolve["solution"]
    assignment: dict[int, int] = {v: int(bit) for v, bit in zip(cut, bvals)}
    component_backsolves = []
    for comp, cr in zip(components, component_results):
        vars_used = list(cr["component_variables"])
        internal = list(cr["internal_variables"])
        ipos = {v: i for i, v in enumerate(internal)}
        vpos = {v: i for i, v in enumerate(vars_used)}
        equations_u: list[tuple[list[int], int]] = []
        for coeff, rhs in cr["_raw_equations"]:
            r = int(rhs)
            for bv in cut:
                r ^= int(coeff[vpos[bv]]) & assignment[bv]
            cu = [0] * len(internal)
            for uv in internal:
                cu[ipos[uv]] = int(coeff[vpos[uv]])
            equations_u.append((cu, r))
        usolve = solve_linear(equations_u, len(internal))
        if not usolve["consistent"]:
            return {"status": "OPEN_RECONSTRUCTION_GAP", "resource_receipt": resource}
        for uv, bit in zip(internal, usolve["solution"]):
            if uv in assignment and assignment[uv] != int(bit):
                return {"status": "OPEN_RECONSTRUCTION_MERGE_CONFLICT", "resource_receipt": resource}
            assignment[uv] = int(bit)
        component_backsolves.append({"component": comp, "internal_count": len(internal), "rank": usolve["rank"]})
    verified = verify_original_assignment(canonical, assignment)
    out = {
        "status": "ADMIT_EXACT_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR" if verified else "OPEN_ORIGINAL_TUPLE_REPLAY_FAILED",
        "cut_variables": cut,
        "component_results": public_components,
        "global_boundary_rank": bsolve["rank"],
        "witness": {"assignment": {str(v): assignment[v] for v in sorted(assignment)}, "component_backsolves": component_backsolves},
        "witness_verified": verified,
        "resource_receipt": resource,
    }
    out["carrier_sha256"] = sha256_obj(out)
    return out


def explain(raw: dict) -> dict:
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
    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    if not any(len(c) >= 3 for c in components):
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "OUT_OF_SCOPE_NO_THREE_RELATION_COMPONENT", "components": components, "source_guard": guard, "scientific_firewall": firewall()}
    predecessor = pair_gate.explain(raw)
    proposal = proposal_record(canonical, parent, components)
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
        "parent_cut": parent["cut"],
        "parent_resource_receipt": parent["redteam"]["resource_receipt"],
        "predecessor_two_relation_status": predecessor.get("status"),
        "components": components,
        "proposal": proposal,
        "carrier": carrier,
        "provenance_receipt": receipt,
        "execution_authorized": False,
        "complexity": {
            "claim": "UNIFORM_POLYNOMIAL_GF2_LIFECYCLE_FOR_FROZEN_RAW_ALL_AFFINE_SCOPE",
            "raw_affine_recognition": "rank/cardinality plus GF(2) nullspace over explicit rows",
            "component_projection": "left-nullspace internal elimination",
            "global_solve": "GF(2) elimination over cut equations",
            "polynomial_degree_depends_on_relation_count": False,
            "raw_2_to_k_enumeration": 0,
            "materialized_relation_join": 0,
        },
        "scientific_firewall": firewall(),
    }


def _bits(seed: int, n: int) -> list[int]:
    return [((seed >> (i % 8)) ^ (i // 3)) & 1 for i in range(n)]


def positive_affine_k20() -> dict:
    B0 = list(range(10))
    B1 = list(range(10, 20))
    Y = list(range(20, 40))
    p, z = 40, 41
    A, C, D = _bits(5, 20), _bits(11, 20), _bits(23, 20)
    X, Y1, Y2 = _bits(7, 20), _bits(19, 20), _bits(29, 20)
    return {
        "variables": list(range(42)),
        "constraints": [
            {"id": "left_affine_0", "scope": B0 + Y, "allowed": [A[:10] + X, C[:10] + Y1]},
            {"id": "left_affine_1", "scope": B1 + Y, "allowed": [A[10:] + X, C[10:] + Y2]},
            {"id": "left_affine_pin", "scope": Y + [p], "allowed": [X + [1]]},
            {"id": "right_affine_full", "scope": list(range(20)) + [z], "allowed": [A + [0], D + [1]]},
        ],
    }


def affine_boundary_inconsistency_control() -> dict:
    raw = positive_affine_k20()
    D = _bits(23, 20)
    raw["constraints"][3] = {"id": "right_affine_full", "scope": list(range(20)) + [41], "allowed": [D + [0]]}
    return raw


def non_affine_control() -> dict:
    raw = positive_affine_k20()
    scope = list(raw["constraints"][2]["scope"])
    X = _bits(7, 20)
    r0 = X + [0]
    r1 = X[:] + [1]
    r2 = X[:] + [0]
    r2[0] ^= 1
    raw["constraints"][2] = {"id": "left_non_affine_three_rows", "scope": scope, "allowed": [r0, r1, r2]}
    return raw


def injected_hint_control() -> dict:
    raw = positive_affine_k20()
    raw["boundary_carrier"] = "TRUSTED_AFFINE_SYNDROME"
    return raw


def tampered_control() -> dict:
    raw = positive_affine_k20()
    canonical = canonicalize_raw(raw)
    parent = parent_mincut.explain_with_mincut(raw)
    cut = list(parent["cut"]["cut_variables"])
    components = parent_support.constraint_components_after_cut(canonical, cut)
    p = proposal_record(canonical, parent, components)
    p["components"] = list(reversed(components))
    return build_carrier(canonical, parent, components, p)


def main() -> None:
    result = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "positive": explain(positive_affine_k20()),
        "negative_boundary_unsat": explain(affine_boundary_inconsistency_control()),
        "negative_non_affine": explain(non_affine_control()),
        "negative_hint": explain(injected_hint_control()),
        "negative_tamper": tampered_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
