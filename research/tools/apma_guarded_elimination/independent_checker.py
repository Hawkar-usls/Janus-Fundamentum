from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_unseen_basis.compositional_basis import induce_compositional_basis
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as parent_mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor_v1_1 as pair_gate
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as candidate

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-GUARDED-BOUNDED-OUTPUT-ELIMINATION-INDEPENDENT-CHECK-2026-09-15-v1.0"
AUTHORITY = "INDEPENDENT_CHECKER__SCOPED_ONLY"
CANDIDATE = Path("research/tools/apma_guarded_elimination/guarded_bounded_output_elimination.py")
CANDIDATE_BLOB = "314034bac990e524d1db7743aef0aebd3b4565c1"
PREREG = Path("research/TRUMP_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "a2426b4600c6135e28d3b6fd8a981442a28093e0"
PARENT_STATE = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.1.json")
PARENT_STATE_BLOB = "2bea05bc87b0e1f29a241e22dab0fd2ab29f4088"
BUDGET_EXPONENT = 2


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def source_checks() -> dict:
    r = root()
    prereg = json.loads((r / PREREG).read_text(encoding="utf-8"))
    return {
        "candidate_blob": git_blob_sha1(r / CANDIDATE) == CANDIDATE_BLOB,
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "prereg_frozen": prereg.get("status") == "FROZEN_BEFORE_CANDIDATE_IMPLEMENTATION",
        "prereg_gate": prereg.get("frozen_gate") == "TRUMP_BICAMERAL_COMPONENT_GUARDED_BOUNDED_OUTPUT_ELIMINATION_FALSIFIER_GATE",
        "parent_state_blob": git_blob_sha1(r / PARENT_STATE) == PARENT_STATE_BLOB,
        "budget_exponent_two": BUDGET_EXPONENT == 2,
    }


def normalize_factor(rel: dict, gi: int) -> dict:
    original_scope = list(rel["scope"])
    scope = tuple(sorted(original_scope))
    pos = {v: i for i, v in enumerate(original_scope)}
    rows = tuple(sorted({tuple(int(raw[pos[v]]) for v in scope) for raw in rel["allowed"]}))
    return {"id": f"orig:{gi}", "scope": scope, "rows": rows}


def guarded_product(counts: list[int], budget: int) -> tuple[bool, int | None]:
    product = 1
    for raw in counts:
        count = int(raw)
        if count == 0:
            return False, 0
        if product > budget // count:
            return True, None
        product *= count
    return product > budget, product


def incremental_hash_join(bucket: list[dict]) -> tuple[list[int], list[tuple[int, ...]], int]:
    # Independent backend: join one factor at a time using an index on the
    # variables shared with the already-built partial assignment. This never
    # calls candidate Cartesian-product or merge helpers.
    first = bucket[0]
    current_scope = list(first["scope"])
    partials = [dict(zip(current_scope, row)) for row in first["rows"]]
    row_extensions = len(partials)

    for factor in bucket[1:]:
        fscope = list(factor["scope"])
        shared = sorted(set(current_scope) & set(fscope))
        fpos = {v: i for i, v in enumerate(fscope)}
        index: dict[tuple[int, ...], list[tuple[int, ...]]] = {}
        for row in factor["rows"]:
            key = tuple(int(row[fpos[v]]) for v in shared)
            index.setdefault(key, []).append(row)
        new_partials: list[dict[int, int]] = []
        for partial in partials:
            key = tuple(int(partial[v]) for v in shared)
            for row in index.get(key, []):
                row_extensions += 1
                merged = dict(partial)
                ok = True
                for v, bit in zip(fscope, row):
                    bit = int(bit)
                    if v in merged and merged[v] != bit:
                        ok = False
                        break
                    merged[v] = bit
                if ok:
                    new_partials.append(merged)
        partials = new_partials
        current_scope = sorted(set(current_scope) | set(fscope))
        if not partials:
            break
    rows = sorted({tuple(int(p[v]) for v in current_scope) for p in partials})
    return current_scope, rows, row_extensions


def eliminate_one_independent(factors: list[dict], var: int, budget: int, step: int, phase: str) -> dict:
    bucket = [f for f in factors if var in f["scope"]]
    if not bucket:
        return {"status": "NOOP", "factors": factors, "record": None}
    rest = [f for f in factors if var not in f["scope"]]
    counts = [len(f["rows"]) for f in bucket]
    over, product = guarded_product(counts, budget)
    if over:
        return {
            "status": "OPEN_BUCKET_PRODUCT_BUDGET",
            "factors": factors,
            "record": {
                "step": step,
                "phase": phase,
                "variable": int(var),
                "bucket_row_counts": counts,
                "budget": budget,
                "pre_expansion_product": product,
                "combinations_enumerated": 0,
                "guard_ran_before_enumeration": True,
            },
        }
    union_scope, joined_rows, extensions = incremental_hash_join(bucket)
    output_scope = [v for v in union_scope if v != var]
    pos = {v: i for i, v in enumerate(union_scope)}
    output_rows = tuple(sorted({tuple(int(row[pos[v]]) for v in output_scope) for row in joined_rows}))
    new_factor = {"id": f"ind:{step}:v{var}", "scope": tuple(output_scope), "rows": output_rows}
    return {
        "status": "ADMIT_BUCKET_ELIMINATION" if output_rows else "EXACT_EMPTY_BUCKET_PROJECTION",
        "factors": rest + [new_factor],
        "record": {
            "step": step,
            "phase": phase,
            "variable": int(var),
            "bucket_row_counts": counts,
            "budget": budget,
            "pre_expansion_product": product,
            "hash_row_extensions": extensions,
            "output_rows": len(output_rows),
            "output_scope": output_scope,
            "guard_ran_before_enumeration": True,
        },
    }


def independent_run(canonical: dict, cut: list[int], components: list[list[int]]) -> dict:
    L = max(2, len(canonical_bytes(canonical)))
    budget = L * L
    B = set(cut)
    boundary_factors: list[dict] = []
    records: list[dict] = []
    step = 0

    for ci, comp in enumerate(components):
        factors = [normalize_factor(canonical["constraints"][gi], gi) for gi in comp]
        internal = sorted({v for f in factors for v in f["scope"] if v not in B})
        for v in internal:
            step += 1
            res = eliminate_one_independent(factors, v, budget, step, f"COMPONENT_{ci}_PRIVATE")
            if res["record"] is not None:
                records.append(res["record"])
            if res["status"] == "OPEN_BUCKET_PRODUCT_BUDGET":
                return {"status": "OPEN_BUCKET_PRODUCT_BUDGET", "failed_bucket": res["record"], "records": records, "L": L, "budget": budget}
            factors = res["factors"]
            if any(len(f["rows"]) == 0 for f in factors):
                return {"status": "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION", "records": records, "L": L, "budget": budget}
        boundary_factors.extend(factors)

    factors = boundary_factors
    for v in sorted(cut):
        step += 1
        res = eliminate_one_independent(factors, v, budget, step, "GLOBAL_BOUNDARY")
        if res["record"] is not None:
            records.append(res["record"])
        if res["status"] == "OPEN_BUCKET_PRODUCT_BUDGET":
            return {"status": "OPEN_BUCKET_PRODUCT_BUDGET", "failed_bucket": res["record"], "records": records, "L": L, "budget": budget}
        factors = res["factors"]
        if any(len(f["rows"]) == 0 for f in factors):
            return {"status": "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION", "records": records, "L": L, "budget": budget}

    if any(f["scope"] for f in factors):
        return {"status": "OPEN_INDEPENDENT_ELIMINATION_GAP", "records": records, "L": L, "budget": budget}
    if any(len(f["rows"]) == 0 for f in factors):
        return {"status": "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION", "records": records, "L": L, "budget": budget}
    return {"status": "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION", "records": records, "L": L, "budget": budget}


def witness_ok(raw: dict, result: dict) -> bool:
    carrier = result.get("carrier", {})
    if not carrier.get("witness_verified"):
        return False
    assignment_raw = carrier.get("witness", {}).get("assignment")
    if not isinstance(assignment_raw, dict):
        return False
    assignment = {int(k): int(v) for k, v in assignment_raw.items()}
    canonical = canonicalize_raw(raw)
    for rel in canonical["constraints"]:
        if any(v not in assignment for v in rel["scope"]):
            return False
        t = tuple(assignment[v] for v in rel["scope"])
        if t not in {tuple(map(int, row)) for row in rel["allowed"]}:
            return False
    return True


def all_successful_bucket_bounds(result: dict) -> bool:
    carrier = result.get("carrier", {})
    L = int(carrier.get("L", 0))
    budget = L * L
    if L <= 0:
        return False
    for rec in carrier.get("bucket_records", []):
        if rec.get("status") == "OPEN_BUCKET_PRODUCT_BUDGET":
            continue
        product = rec.get("pre_expansion_product")
        if product is None or int(product) > budget:
            return False
        if int(rec.get("output_rows", 0)) > int(product):
            return False
        if int(rec.get("output_rows", 0)) > budget:
            return False
        if rec.get("guard_ran_before_enumeration") is not True:
            return False
    return True


def main() -> None:
    src = source_checks()

    positive_raw = candidate.positive_mixed_three_relation_control()
    positive_can = canonicalize_raw(positive_raw)
    positive_global = induce_compositional_basis(positive_can)
    positive_parent = parent_mincut.explain_with_mincut(positive_raw)
    cut = list(positive_parent.get("cut", {}).get("cut_variables", []))
    components = parent_support.constraint_components_after_cut(positive_can, cut) if cut else []
    predecessor = pair_gate.explain(positive_raw)
    positive = candidate.explain(positive_raw)
    independent_positive = independent_run(positive_can, cut, components) if cut else {"status": "NO_CUT"}

    unsat_raw = candidate.scoped_unsat_control()
    unsat_can = canonicalize_raw(unsat_raw)
    unsat_parent = parent_mincut.explain_with_mincut(unsat_raw)
    unsat_cut = list(unsat_parent.get("cut", {}).get("cut_variables", []))
    unsat_components = parent_support.constraint_components_after_cut(unsat_can, unsat_cut) if unsat_cut else []
    unsat = candidate.explain(unsat_raw)
    independent_unsat = independent_run(unsat_can, unsat_cut, unsat_components) if unsat_cut else {"status": "NO_CUT"}

    over_raw = candidate.overbudget_control()
    over_can = canonicalize_raw(over_raw)
    over_parent = parent_mincut.explain_with_mincut(over_raw)
    over_cut = list(over_parent.get("cut", {}).get("cut_variables", []))
    over_components = parent_support.constraint_components_after_cut(over_can, over_cut) if over_cut else []
    over = candidate.explain(over_raw)
    independent_over = independent_run(over_can, over_cut, over_components) if over_cut else {"status": "NO_CUT"}

    hint = candidate.explain(candidate.injected_hint_control())
    tamper = candidate.tampered_control()

    pres = positive.get("carrier", {}).get("resource_receipt", {})
    ores = over.get("carrier", {}).get("resource_receipt", {})
    over_failed = over.get("carrier", {}).get("failed_bucket", {})
    independent_over_failed = independent_over.get("failed_bucket", {})
    fw = positive.get("scientific_firewall", {})

    mixed_not_common_basis = positive_global.get("status") != "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO"
    checks = {
        "P1_source_candidate": src["candidate_blob"],
        "P1_source_prereg": src["prereg_blob"],
        "P1_prereg_frozen": src["prereg_frozen"],
        "P1_parent_state": src["parent_state_blob"],
        "P1_budget_exponent_two": src["budget_exponent_two"],
        "P1_candidate_source_guard": positive.get("source_guard", {}).get("ok") is True,
        "P2_positive_raw_basis_not_admitted": mixed_not_common_basis,
        "P2_positive_parent_overwidth": positive_parent.get("status") == "OPEN_MINCUT_BRANCH_BUDGET",
        "P2_positive_parent_zero_branches": positive_parent.get("redteam", {}).get("resource_receipt", {}).get("branch_enumerations") == 0,
        "P2_positive_cut20": len(cut) == 20,
        "P3_positive_has_3plus_component": any(len(c) >= 3 for c in components),
        "P3_positive_predecessor_open": predecessor.get("status") == "OPEN_COMPONENT_RELATION_COUNT_GT_2",
        "P4_positive_is_mixed_predecessor_open_surface": mixed_not_common_basis and positive.get("global_basis_status") != "ADMIT_COMPOSITIONAL_BASIS_PORTFOLIO",
        "P5_all_positive_guards_before_enumeration": all(rec.get("guard_ran_before_enumeration") is True for rec in positive.get("carrier", {}).get("bucket_records", [])),
        "P6_successful_bucket_bounds": all_successful_bucket_bounds(positive),
        "P7_independent_positive_terminal": independent_positive.get("status") == "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION",
        "P8_candidate_component_partition_matches": positive.get("components") == components,
        "P9_zero_raw_cut_cube": pres.get("raw_cut_assignments_enumerated") == 0,
        "P10_candidate_positive_terminal": positive.get("status") == "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION",
        "P10_candidate_positive_witness_replay": witness_ok(positive_raw, positive),
        "P11_candidate_unsat_terminal": unsat.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION",
        "P11_independent_unsat_terminal": independent_unsat.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION",
        "P12_candidate_overbudget_open": over.get("status") == "OPEN_BUCKET_PRODUCT_BUDGET",
        "P12_independent_overbudget_open": independent_over.get("status") == "OPEN_BUCKET_PRODUCT_BUDGET",
        "P12_same_first_failed_variable": over_failed.get("variable") == independent_over_failed.get("variable") and over_failed.get("variable") is not None,
        "P13_candidate_failed_bucket_zero_enumeration": ores.get("failed_bucket_combinations_enumerated") == 0 and over_failed.get("combinations_enumerated") == 0,
        "P13_independent_guard_before_enumeration": independent_over_failed.get("combinations_enumerated") == 0 and independent_over_failed.get("guard_ran_before_enumeration") is True,
        "P14_hint_rejected": hint.get("status") == "REJECT_RAW_INPUT",
        "P14_tamper_rejected": tamper.get("status") == "REJECT_TAMPERED_PROVENANCE",
        "P15_zero_generic_transfer": pres.get("generic_transfer_calls") == 0,
        "P15_zero_external_solver": pres.get("external_solver_calls") == 0,
        "P15_zero_alternative_orders": pres.get("alternative_order_retries") == 0,
        "P15_no_global_cut_cube": pres.get("materialized_global_cut_cube") is False,
        "P16_checker_backend_is_incremental_hash_join": True,
        "P17_fixed_uniform_complexity_declared": positive.get("complexity", {}).get("polynomial_degree_depends_on_relation_count") is False and positive.get("complexity", {}).get("conservative_total_lifecycle") == "O(L^6)",
        "FW_p_vs_np_open": fw.get("P_VS_NP") == "OPEN",
        "FW_general_sat_not_proved": fw.get("GENERAL_SAT_IN_P") == "NOT_PROVED",
        "FW_connected_mixed_not_solved": fw.get("CONNECTED_MIXED_CORE_SOLVED") == "NO",
        "FW_general_bucket_not_proved": fw.get("GENERAL_BUCKET_ELIMINATION_POLYNOMIAL") == "NOT_PROVED",
        "FW_overbudget_open_not_negative": fw.get("OVERBUDGET_BUCKETS") == "OPEN_NOT_NEGATIVE_EVIDENCE",
    }

    verdict = "PASS_SCOPED_BICAMERAL_GUARDED_BOUNDED_OUTPUT_ELIMINATION_V1" if all(checks.values()) else "FAIL_OR_OPEN_GUARDED_BOUNDED_OUTPUT_ELIMINATION_V1"
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "verdict": verdict,
        "checks": checks,
        "controls": {
            "positive_global_basis": positive_global.get("status"),
            "positive_parent": positive_parent.get("status"),
            "positive_cut": cut,
            "positive_components": components,
            "positive_predecessor": predecessor.get("status"),
            "positive_candidate_terminal": positive.get("status"),
            "positive_independent_terminal": independent_positive.get("status"),
            "positive_witness_verified": positive.get("carrier", {}).get("witness_verified"),
            "positive_total_combinations": pres.get("total_combinations_enumerated"),
            "positive_max_output_rows": pres.get("max_output_rows"),
            "unsat_candidate_terminal": unsat.get("status"),
            "unsat_independent_terminal": independent_unsat.get("status"),
            "overbudget_candidate_terminal": over.get("status"),
            "overbudget_independent_terminal": independent_over.get("status"),
            "overbudget_candidate_failed_variable": over_failed.get("variable"),
            "overbudget_independent_failed_variable": independent_over_failed.get("variable"),
            "overbudget_failed_bucket_counts": over_failed.get("bucket_row_counts"),
            "overbudget_failed_bucket_budget": over_failed.get("budget"),
            "hint_terminal": hint.get("status"),
            "tamper_terminal": tamper.get("status"),
        },
        "independent_methods": {
            "bucket_join": "INCREMENTAL_HASH_INDEXED_NATURAL_JOIN",
            "candidate_bucket_join": "FULL_CARTESIAN_PRODUCT_AFTER_PRE_GUARD",
            "shared_candidate_join_helpers": False,
            "same_frozen_order": True,
        },
        "complexity": {
            "candidate_budget": "L^2_PRE_EXPANSION_PER_BUCKET",
            "checker_budget": "L^2_PRE_EXPANSION_PER_BUCKET",
            "candidate_uniform_envelope": "O(L^6)",
            "polynomial_degree_depends_on_relation_count": False,
            "raw_2_to_k_enumeration": pres.get("raw_cut_assignments_enumerated"),
        },
        "scientific_firewall": fw,
    }
    print(json.dumps(out, sort_keys=True))
    if verdict.startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
