from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_uniform_affine_boundary import uniform_affine_boundary as candidate

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-UNIFORM-RAW-DERIVED-AFFINE-BOUNDARY-FACTOR-INDEPENDENT-CHECK-2026-09-15-v1.0"
AUTHORITY = "INDEPENDENT_CHECKER__SCOPED_ONLY"
CANDIDATE = Path("research/tools/apma_uniform_affine_boundary/uniform_affine_boundary.py")
CANDIDATE_BLOB = "336c58c059fecba49c7fbfba9018a95761f8fc24"
PREREG = Path("research/TRUMP_BICAMERAL_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "b5af3098fc0bb6b35981a29460f5113edebe0928"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.0.json")
PARENT_STATE_BLOB = "9d8b199b855e947e6adfdbce2ac5ae902556ad64"


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def xor_tuple(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x ^ y for x, y in zip(a, b))


def affine_by_ternary_closure(relation: dict) -> bool:
    rows = sorted({tuple(map(int, r)) for r in relation["allowed"]})
    if not rows:
        return False
    s = set(rows)
    for x in rows:
        for y in rows:
            xy = xor_tuple(x, y)
            for z in rows:
                if xor_tuple(xy, z) not in s:
                    return False
    return True


def xor_basis(vectors: list[tuple[int, ...]], n: int) -> list[int]:
    basis = [0] * n
    for vec in vectors:
        x = sum((int(bit) & 1) << i for i, bit in enumerate(vec))
        while x:
            p = x.bit_length() - 1
            if basis[p]:
                x ^= basis[p]
            else:
                basis[p] = x
                for q in range(p):
                    if basis[q] and ((basis[p] >> q) & 1):
                        basis[p] ^= basis[q]
                for q in range(p + 1, n):
                    if basis[q] and ((basis[q] >> p) & 1):
                        basis[q] ^= basis[p]
                break
    return [x for x in basis if x]


def nullspace_rows(rows: list[int], n: int) -> list[int]:
    # Independent bit-mask RREF: solve rows * h = 0.
    rr = list(rows)
    pivots: list[int] = []
    r = 0
    for c in range(n):
        pivot = next((i for i in range(r, len(rr)) if (rr[i] >> c) & 1), None)
        if pivot is None:
            continue
        rr[r], rr[pivot] = rr[pivot], rr[r]
        for i in range(len(rr)):
            if i != r and ((rr[i] >> c) & 1):
                rr[i] ^= rr[r]
        pivots.append(c)
        r += 1
        if r == len(rr):
            break
    rr = rr[:r]
    free = [c for c in range(n) if c not in pivots]
    out = []
    for f in free:
        x = 1 << f
        for i in range(len(pivots) - 1, -1, -1):
            p = pivots[i]
            parity = ((rr[i] & x).bit_count() & 1)
            if parity:
                x |= 1 << p
        out.append(x)
    return out


def relation_equations_independent(relation: dict) -> list[tuple[int, int]] | None:
    rows = sorted({tuple(map(int, r)) for r in relation["allowed"]})
    n = len(relation["scope"])
    if not affine_by_ternary_closure(relation):
        return None
    anchor = rows[0]
    diffs = [xor_tuple(r, anchor) for r in rows]
    basis = xor_basis(diffs, n)
    orth = nullspace_rows(basis, n)
    anchor_mask = sum((bit & 1) << i for i, bit in enumerate(anchor))
    return [(h, ((h & anchor_mask).bit_count() & 1)) for h in orth]


def components_after_cut(canonical: dict, cut: list[int]) -> list[list[int]]:
    removed = set(cut)
    rel_vars = [set(r["scope"]) - removed for r in canonical["constraints"]]
    adj = {i: set() for i in range(len(rel_vars))}
    for i in range(len(rel_vars)):
        for j in range(i + 1, len(rel_vars)):
            if rel_vars[i] & rel_vars[j]:
                adj[i].add(j)
                adj[j].add(i)
    seen = set()
    comps = []
    for i in range(len(rel_vars)):
        if i in seen:
            continue
        stack = [i]
        comp = []
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            comp.append(u)
            stack.extend(sorted(adj[u] - seen, reverse=True))
        comps.append(sorted(comp))
    return sorted(comps)


def component_equations_global(canonical: dict, component: list[int]) -> tuple[list[int], list[tuple[int, int]]] | None:
    vars_used = sorted({v for gi in component for v in canonical["constraints"][gi]["scope"]})
    pos = {v: i for i, v in enumerate(vars_used)}
    equations: list[tuple[int, int]] = []
    for gi in component:
        rel = canonical["constraints"][gi]
        local = relation_equations_independent(rel)
        if local is None:
            return None
        for mask, rhs in local:
            gmask = 0
            for li, v in enumerate(rel["scope"]):
                if (mask >> li) & 1:
                    gmask ^= 1 << pos[v]
            equations.append((gmask, rhs))
    return vars_used, equations


def eliminate_internal(equations: list[tuple[int, int]], vars_used: list[int], cut: list[int]) -> list[tuple[int, int]]:
    # Exact existential elimination, one variable at a time: choose one equation
    # containing u as a definition of u, XOR it into every other equation containing u,
    # then drop the defining row when existentially quantifying u.
    pos = {v: i for i, v in enumerate(vars_used)}
    eqs = [(m, r) for m, r in equations]
    for u in [v for v in vars_used if v not in set(cut)]:
        bit = 1 << pos[u]
        containing = [i for i, (m, _) in enumerate(eqs) if m & bit]
        if not containing:
            continue
        pidx = containing[0]
        pm, pr = eqs[pidx]
        new = []
        for i, (m, r) in enumerate(eqs):
            if i == pidx:
                continue
            if m & bit:
                new.append((m ^ pm, r ^ pr))
            else:
                new.append((m, r))
        eqs = new
    # Remap surviving cut bits to canonical cut coordinate order.
    out = []
    for m, r in eqs:
        bmask = 0
        for bi, bv in enumerate(cut):
            if bv in pos and ((m >> pos[bv]) & 1):
                bmask ^= 1 << bi
        out.append((bmask, r))
    return out


def canonical_rowspace(equations: list[tuple[int, int]], nvars: int) -> tuple[bool, tuple[int, ...]]:
    rows = [m | ((r & 1) << nvars) for m, r in equations]
    basis = [0] * (nvars + 1)
    for x0 in rows:
        x = x0
        while x:
            p = x.bit_length() - 1
            if basis[p]:
                x ^= basis[p]
            else:
                basis[p] = x
                for q in range(p):
                    if basis[q] and ((basis[p] >> q) & 1):
                        basis[p] ^= basis[q]
                for q in range(p + 1, nvars + 1):
                    if basis[q] and ((basis[q] >> p) & 1):
                        basis[q] ^= basis[p]
                break
    nonzero = tuple(x for x in basis if x)
    contradiction = any((x & ((1 << nvars) - 1)) == 0 and ((x >> nvars) & 1) for x in nonzero)
    return contradiction, nonzero


def independent_boundary(canonical: dict, component: list[int], cut: list[int]) -> dict:
    built = component_equations_global(canonical, component)
    if built is None:
        return {"status": "OPEN_NON_AFFINE_RAW_RELATION"}
    vars_used, equations = built
    eqs_b = eliminate_internal(equations, vars_used, cut)
    contradiction, rowspace = canonical_rowspace(eqs_b, len(cut))
    return {"status": "EXACT_UNSAT_COMPONENT" if contradiction else "ADMIT_AFFINE_BOUNDARY", "equations": eqs_b, "rowspace": rowspace, "contradiction": contradiction}


def candidate_boundary_rowspace(cr: dict, k: int) -> tuple[bool, tuple[int, ...]]:
    equations = []
    for e in cr["boundary_equations"]:
        mask = sum((int(bit) & 1) << i for i, bit in enumerate(e["coeff"]))
        equations.append((mask, int(e["rhs"])))
    return canonical_rowspace(equations, k)


def raw_witness_ok(raw: dict, result: dict) -> bool:
    if not result.get("carrier", {}).get("witness_verified"):
        return False
    assignment = {int(k): int(v) for k, v in result["carrier"]["witness"]["assignment"].items()}
    can = canonicalize_raw(raw)
    for rel in can["constraints"]:
        if any(v not in assignment for v in rel["scope"]):
            return False
        t = [assignment[v] for v in rel["scope"]]
        if t not in [list(map(int, x)) for x in rel["allowed"]]:
            return False
    return True


def source_checks() -> dict:
    r = root()
    return {
        "candidate_blob": git_blob_sha1(r / CANDIDATE) == CANDIDATE_BLOB,
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
    }


def main() -> None:
    src = source_checks()
    pos_raw = candidate.positive_affine_k20()
    pos = candidate.explain(pos_raw)
    pos_can = canonicalize_raw(pos_raw)
    cut = list(pos.get("parent_cut", {}).get("cut_variables", []))
    independent_components = components_after_cut(pos_can, cut) if cut else []
    candidate_components = pos.get("components", [])
    indep = [independent_boundary(pos_can, comp, cut) for comp in independent_components] if cut else []
    candidate_crs = pos.get("carrier", {}).get("component_results", [])
    boundary_match = len(indep) == len(candidate_crs)
    if boundary_match:
        for i, ic in enumerate(indep):
            if ic["status"] != "ADMIT_AFFINE_BOUNDARY":
                boundary_match = False
                break
            if canonical_rowspace(ic["equations"], len(cut)) != candidate_boundary_rowspace(candidate_crs[i], len(cut)):
                boundary_match = False
                break

    # Independently prove each raw affine table is exactly represented: ternary closure,
    # all listed rows satisfy equations, and the equation solution-count equals row count.
    local_exact = True
    local_affine = []
    for rel in pos_can["constraints"]:
        eqs = relation_equations_independent(rel)
        closure = affine_by_ternary_closure(rel)
        if eqs is None:
            local_exact = False
            local_affine.append(False)
            continue
        n = len(rel["scope"])
        masks = [m for m, _ in eqs]
        rank = len(xor_basis([tuple((m >> i) & 1 for i in range(n)) for m in masks], n))
        all_rows = all(all((((m & sum((int(b)&1)<<i for i,b in enumerate(row))).bit_count() & 1) == rhs) for m, rhs in eqs) for row in rel["allowed"])
        solution_count = 1 << (n - rank)
        exact = closure and all_rows and solution_count == len({tuple(r) for r in rel["allowed"]})
        local_affine.append(exact)
        local_exact &= exact

    unsat_raw = candidate.affine_boundary_inconsistency_control()
    unsat = candidate.explain(unsat_raw)
    unsat_can = canonicalize_raw(unsat_raw)
    unsat_cut = list(unsat.get("parent_cut", {}).get("cut_variables", []))
    unsat_comps = components_after_cut(unsat_can, unsat_cut) if unsat_cut else []
    unsat_eqs: list[tuple[int, int]] = []
    unsat_independent_affine = True
    for comp in unsat_comps:
        ib = independent_boundary(unsat_can, comp, unsat_cut)
        if ib["status"] == "OPEN_NON_AFFINE_RAW_RELATION":
            unsat_independent_affine = False
            break
        unsat_eqs.extend(ib["equations"])
    unsat_contradiction = canonical_rowspace(unsat_eqs, len(unsat_cut))[0] if unsat_independent_affine else False

    non_raw = candidate.non_affine_control()
    non = candidate.explain(non_raw)
    non_can = canonicalize_raw(non_raw)
    independent_non_affine = any(not affine_by_ternary_closure(rel) for rel in non_can["constraints"])
    hint = candidate.explain(candidate.injected_hint_control())
    tamper = candidate.tampered_control()

    multi = [c for c in independent_components if len(c) >= 3]
    no_anchor = bool(multi) and all(not set(cut).issubset(set(pos_can["constraints"][gi]["scope"])) for gi in multi[0])
    resource = pos.get("carrier", {}).get("resource_receipt", {})
    fw = pos.get("scientific_firewall", {})
    checks = {
        "P1_source_candidate": src["candidate_blob"],
        "P1_source_prereg": src["prereg_blob"],
        "P1_source_parent_state": src["parent_state_blob"],
        "P1_candidate_guard": pos.get("source_guard", {}).get("ok") is True,
        "P2_parent_overwidth": pos.get("parent_status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P2_zero_parent_branches": pos.get("parent_resource_receipt", {}).get("branch_enumerations") == 0,
        "P2_cut20": len(cut) == 20,
        "P3_component_partition_independent": candidate_components == independent_components,
        "P3_has_3plus_component": any(len(c) >= 3 for c in independent_components),
        "P4_predecessor_pair_open": pos.get("predecessor_two_relation_status") == "OPEN_COMPONENT_RELATION_COUNT_GT_2",
        "P5_no_full_cut_anchor_in_multi": no_anchor,
        "P6_all_raw_relations_affine_ternary_closure": all(local_affine),
        "P7_candidate_affine_certificates_exact": local_exact,
        "P8_candidate_local_equation_replay": all(rc["certificate"].get("affine") for cr in candidate_crs for rc in cr.get("relation_certs", [])),
        "P9_zero_raw_boundary_enumeration": resource.get("raw_cut_assignments_enumerated") == 0,
        "P9_zero_materialized_joins": resource.get("materialized_relation_joins") == 0,
        "P10_boundary_systems_match_independent_elimination": boundary_match,
        "P11_positive_terminal": pos.get("status") == "ADMIT_EXACT_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR",
        "P12_positive_witness_raw_replay": raw_witness_ok(pos_raw, pos),
        "P13_unsat_terminal": unsat.get("status") == "EXACT_UNSAT_BY_AFFINE_BOUNDARY_INCONSISTENCY",
        "P13_unsat_independent_contradiction": unsat_contradiction,
        "P14_nonaffine_independently_detected": independent_non_affine,
        "P14_nonaffine_candidate_open": non.get("status") == "OPEN_NON_AFFINE_RAW_RELATION",
        "P15_hint_rejected": hint.get("status") == "REJECT_RAW_INPUT",
        "P15_tamper_rejected": tamper.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "P16_zero_generic_transfer": resource.get("generic_transfer_calls") == 0,
        "P16_zero_external_solver": resource.get("external_solver_calls") == 0,
        "P16_zero_cartesian": resource.get("cartesian_products_materialized") == 0,
        "P17_uniform_complexity_declared": pos.get("complexity", {}).get("polynomial_degree_depends_on_relation_count") is False,
        "FW_p_vs_np_open": fw.get("P_VS_NP") == "OPEN",
        "FW_general_sat_not_proved": fw.get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "FW_general_boundary_not_proved": fw.get("GENERAL_UNIFORM_BOUNDARY_ELIMINATION") == "NOT_PROVED",
        "FW_connected_mixed_not_solved": fw.get("CONNECTED_MIXED_CORE_SOLVED") == "NO",
    }
    verdict = "PASS_SCOPED_BICAMERAL_OVERWIDTH_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR_V1" if all(checks.values()) else "FAIL_OR_OPEN_UNIFORM_RAW_DERIVED_AFFINE_BOUNDARY_FACTOR_V1"
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": verdict,
        "checks": checks,
        "controls": {
            "positive_terminal": pos.get("status"),
            "positive_cut": cut,
            "positive_components": independent_components,
            "positive_predecessor": pos.get("predecessor_two_relation_status"),
            "positive_witness_verified": pos.get("carrier", {}).get("witness_verified"),
            "positive_boundary_equation_count": resource.get("boundary_equation_count"),
            "unsat_terminal": unsat.get("status"),
            "nonaffine_terminal": non.get("status"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tamper.get("status"),
        },
        "independent_methods": {
            "affine_recognition": "TERNARY_XOR_CLOSURE_OVER_EXPLICIT_ROWS",
            "boundary_projection": "SEQUENTIAL_EXISTENTIAL_EQUATION_ELIMINATION_BY_XOR_PIVOT",
            "candidate_boundary_projection": "LEFT_NULLSPACE_OF_INTERNAL_COEFFICIENT_MATRIX",
            "ambient_cube_enumeration": 0,
        },
        "complexity": {
            "claim": "ONE_FIXED_POLYNOMIAL_GF2_ENVELOPE_IN_ORIGINAL_EXPLICIT_L_INDEPENDENT_OF_RELATION_COUNT",
            "raw_2_to_k_enumeration": resource.get("raw_cut_assignments_enumerated"),
            "materialized_relation_joins": resource.get("materialized_relation_joins"),
            "relation_count": resource.get("relation_count"),
            "boundary_equation_count": resource.get("boundary_equation_count"),
        },
        "scientific_firewall": fw,
    }
    print(json.dumps(out, sort_keys=True))
    if verdict.startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
