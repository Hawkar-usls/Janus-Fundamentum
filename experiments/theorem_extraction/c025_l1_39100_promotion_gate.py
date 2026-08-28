#!/usr/bin/env python3
"""Produce the exact, append-only C025 L1/39100 promotion evidence.

This producer never grants admission.  It reconstructs the frozen candidate,
produces exact reachability/Delta/Gamma components and assembles a hash-bound
composite.  A separate no-import verifier must admit that composite.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_pirc_decision_core_v0_4 as core
from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.theorem_extraction import c025_adversarial_delta_pair_search as adv
from experiments.theorem_extraction import c025_v2_gap_adversarial_search as gap

P_VS_NP = "OPEN"
REPOSITORY = "Hawkar-usls/Janus-Fundamentum"
BRANCH = "research/c025-phase5-9-polynomial-pivot-grammar-2026-08-28"
LEAF_NVARS = 10
LEAF_CLAUSES = 90
LEAF_WIDTH = 4
SEED = 39100
SOURCE_FP = "bc07cfeb7d1ef62916d7319ed59edc8d2e4a92ce34881a13186d2c47991c66bc"
PRODUCT_FP = "037cbc224816408ca1c76c65c9bb78ad660d3b612c40ef91d1ac76943c7c79c3"
N = 1102
CAP = 1_214_404
PRODUCT_UNITS = 72_901
PRODUCT_CLAUSES = 8_100
ROOTS = tuple(range(2, 22))
PAIR_COUNT = 744
ROUTE_COUNT = PAIR_COUNT * len(ROOTS)
ORIGINAL_V2_SHARDS = 64
GATE_PATH = Path("research/C025_L1_39100_EXACT_COUNTEREXAMPLE_PROMOTION_GATE_2026-08-28.json")
EQUIVALENCE_PATH = Path("research/C025_L1_39100_UNIFORM_V2_SEMANTIC_EQUIVALENCE_LEMMA_2026-08-28.json")


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def candidate() -> tuple[base.CNF, base.CNF]:
    source, left, right = adv.build_selector_source(LEAF_NVARS, LEAF_CLAUSES, LEAF_WIDTH, SEED)
    product = adv.direct_selector_product(left, right)
    assert base.fingerprint(source) == SOURCE_FP
    assert base.fingerprint(product) == PRODUCT_FP
    assert base.input_size_units(source) == N
    assert N * N == CAP
    assert base.state_units(product) == PRODUCT_UNITS
    assert len(product) == PRODUCT_CLAUSES
    assert base.vars_of(product) == ROOTS
    assert len(core.v2.all_or_pair_candidates(product)) == PAIR_COUNT
    return source, product


def candidate_meta(source: base.CNF, product: base.CNF) -> dict[str, Any]:
    source_bytes = canonical_json_bytes([list(c) for c in source])
    product_bytes = canonical_json_bytes([list(c) for c in product])
    return {
        "family": "DISJOINT_SELECTOR_PRODUCT",
        "leaf_nvars": LEAF_NVARS,
        "leaf_clauses": LEAF_CLAUSES,
        "leaf_width": LEAF_WIDTH,
        "seed": SEED,
        "source_fingerprint": base.fingerprint(source),
        "product_fingerprint": base.fingerprint(product),
        "source_canonical_bytes": len(source_bytes),
        "product_canonical_bytes": len(product_bytes),
        "source_canonical_sha256": sha256_bytes(source_bytes),
        "product_canonical_sha256": sha256_bytes(product_bytes),
        "N": N,
        "cap": CAP,
        "product_units": base.state_units(product),
        "product_clauses": len(product),
        "live_roots": list(ROOTS),
        "live_root_count": len(ROOTS),
        "v2_pair_count": PAIR_COUNT,
        "pair_root_route_count": ROUTE_COUNT,
    }


def product_text(product: base.CNF) -> bytes:
    return ("\n".join(" ".join(map(str, c)) for c in product) + "\n").encode("ascii")


def mode_identity(args: argparse.Namespace) -> int:
    source, product = candidate()
    payload = product_text(product)
    if args.product_out:
        Path(args.product_out).write_bytes(payload)
    report = {
        "schema": "JANUS/C025/L1-39100-PROMOTION/IDENTITY/v1",
        "status": "EXACT_IDENTITY_PASS",
        "candidate": candidate_meta(source, product),
        "product_text_bytes": len(payload),
        "product_text_sha256": sha256_bytes(payload),
        "generation": {
            "rng": "python_random_Random_fixed_seed",
            "left_seed": SEED,
            "right_seed": SEED + 1_000_003,
            "canonicalization": "equal_width_sorted_unique_tautology_rejection",
            "deterministic": True,
        },
        "uniform_exactness_preconditions": {
            "widths": sorted({len(c) for c in product}),
            "unique_clause_count": len(set(product)),
            "tautology_count": sum(any(-lit in c for lit in c) for c in product),
            "fresh_extension": 22,
            "fresh_absent": 22 not in base.vars_of(product),
        },
        "P_VS_NP": P_VS_NP,
    }
    write_json(Path(args.out), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def mode_ordinary(args: argparse.Namespace) -> int:
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        raise ValueError("invalid shard coordinates")
    source, product = candidate()
    selected = [(i, v) for i, v in enumerate(ROOTS) if i % args.shard_count == args.shard_index]
    rows = []
    for pivot_index, pivot in selected:
        after, stats = base.eliminate_var_capped(product, pivot, CAP)
        rows.append({
            "pivot_index": pivot_index,
            "pivot": pivot,
            "overflow": after is None,
            "stats": stats,
            "after_fingerprint": base.fingerprint(after) if after is not None else None,
        })
    all_overflow = all(row["overflow"] for row in rows)
    report = {
        "schema": "JANUS/C025/L1-39100-PROMOTION/ORDINARY-SHARD/v1",
        "status": "SHARD_COMPLETE_ALL_OVERFLOW" if all_overflow else "EXACT_ORDINARY_FIT_FOUND",
        "candidate": candidate_meta(source, product),
        "implementation": "ORIGINAL_PYTHON_ELIMINATE_VAR_CAPPED",
        "shard": {"index": args.shard_index, "count": args.shard_count},
        "global_pivot_count": len(ROOTS),
        "selected_pivot_indices": [i for i, _ in selected],
        "complete_for_selected_indices": len(rows) == len(selected),
        "all_selected_overflow": all_overflow,
        "rows": rows,
        "P_VS_NP": P_VS_NP,
    }
    write_json(Path(args.out), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def mode_reachability(args: argparse.Namespace) -> int:
    source, product = candidate()
    reachability = adv.verify_reachable_callsite(source, product)
    exact_product, selector_stats = base.eliminate_var_capped(source, 1, CAP)
    selector_exact = (
        exact_product == product
        and base.verify_elimination_transition(source, 1, product, CAP)
    )
    passed = bool(reachability["reachable_at_frozen_ordinary_callsite"] and selector_exact)
    report = {
        "schema": "JANUS/C025/L1-39100-PROMOTION/REACHABILITY/v1",
        "status": "PASS" if passed else "FAIL",
        "candidate": candidate_meta(source, product),
        "fixed_algorithm": "PIRC_DECISION_CORE_V0_4",
        "unmodified_core_prefix": True,
        "reachable_at_frozen_ordinary_callsite": bool(reachability["reachable_at_frozen_ordinary_callsite"]),
        "selector_pivot_1_exact_product": selector_exact,
        "selector_stats": selector_stats,
        "replay": reachability,
        "P_VS_NP": P_VS_NP,
    }
    write_json(Path(args.out), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if passed else 1


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_checker(report: dict[str, Any]) -> dict[str, Any]:
    root_count = report.get("root_pivot_count", report.get("root_pivot_count_per_pair"))
    margin = report.get("minimum_margin", report.get("minimum_observed_cap_margin"))
    return {
        "schema": report.get("schema"),
        "status": report.get("status"),
        "pair_count": int(report.get("candidate_pair_count", -1)),
        "root_count": int(root_count if root_count is not None else -1),
        "route_count": int(report.get("checked_pair_pivot_scope", PAIR_COUNT * int(root_count or 0))),
        "cap": int(report.get("cap", -1)),
        "minimum_first_crossing_margin": int(margin if margin is not None else -10**18),
        "rescue": report.get("rescue"),
    }


def direct_target_state(source: base.CNF, product: base.CNF) -> base.EngineState:
    return base.EngineState(
        root=source,
        residual=product,
        fixed_assignment={},
        root_vars=base.vars_of(source),
        extension_defs=[],
        elimination_history=[base.ElimSnapshot(source, 1, "PURE_ELIM")],
        seen={base.fingerprint(source), base.fingerprint(product)},
        N=N,
        cap_exponent=2,
        extension_exponent=2,
        ledger=base.Ledger(question_count=1),
    )


def run_general_checker(checker: Path, product: base.CNF, source: base.CNF) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="c025-l1-positive-control-") as tmp:
        product_path = Path(tmp) / "product.txt"
        product_path.write_bytes(product_text(product))
        roots = [v for v in base.vars_of(source) if v in set(base.vars_of(product))]
        env = dict(os.environ)
        env["OMP_NUM_THREADS"] = "2"
        proc = subprocess.run(
            [str(checker), str(product_path), str(base.input_size_units(source) ** 2), str(min(roots)), str(max(roots))],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        return json.loads(proc.stdout)


def mode_gamma_audit(args: argparse.Namespace) -> int:
    source, product = candidate()
    supplied_product = Path(args.product).read_bytes()
    if supplied_product != product_text(product):
        raise AssertionError("PRODUCT_TEXT_IDENTITY_MISMATCH")

    independent_receipt_path = Path(args.independent)
    general_receipt_path = Path(args.general)
    independent_checker_path = Path(args.independent_checker).resolve()
    general_checker_path = Path(args.general_checker).resolve()
    independent_raw = load_json(independent_receipt_path)
    general_raw = load_json(general_receipt_path)
    independent = normalize_checker(independent_raw)
    general = normalize_checker(general_raw)
    expected_checker_schemas = {
        "independent": "JANUS/C025/L1-UNIFORM-INDEPENDENT-EXACT-CHECKER/v1",
        "general": "JANUS/C025/GENERAL-UNIFORM-EXACT-V2-CHECKER/v1",
    }
    for name, normalized in (("independent", independent), ("general", general)):
        if normalized["schema"] != expected_checker_schemas[name]:
            raise AssertionError(f"{name.upper()}_BACKEND_SCHEMA_DRIFT")
        if normalized["status"] != "COMPLETE_NO_V2_RESCUE":
            raise AssertionError(f"{name.upper()}_BACKEND_DID_NOT_COMPLETE_NEGATIVE_SCOPE")
        if normalized["pair_count"] != PAIR_COUNT or normalized["root_count"] != len(ROOTS):
            raise AssertionError(f"{name.upper()}_BACKEND_SCOPE_DRIFT")
        if normalized["route_count"] != ROUTE_COUNT:
            raise AssertionError(f"{name.upper()}_BACKEND_ROUTE_COUNT_DRIFT")
        if normalized["cap"] != CAP or normalized["minimum_first_crossing_margin"] <= 0:
            raise AssertionError(f"{name.upper()}_BACKEND_CAP_CERTIFICATE_INVALID")
        if normalized["rescue"] is not None:
            raise AssertionError(f"{name.upper()}_BACKEND_RESCUE_CONTRADICTION")

    pairs = core.v2.all_or_pair_candidates(product)
    fresh = core.v2.next_fresh_extension(direct_target_state(source, product))
    equivalence_indices = sorted({0, 1, 10, len(pairs) // 2, len(pairs) - 1})
    equivalence_samples = []
    for pair_index in equivalence_indices:
        pair = pairs[pair_index]
        fast = gap.fast_apply_uniform_product(product, pair[0], pair[1], fresh)
        original, cert = core.v2.apply_or_pair_v2(product, pair[0], pair[1], fresh)
        verified = core.v2.verify_or_pair_v2(product, original, cert)
        if fast != original or not verified:
            raise AssertionError(f"ORIGINAL_MACRO_EQUIVALENCE_FAILED_AT_{pair_index}")
        equivalence_samples.append({
            "pair_index": pair_index,
            "pair": list(pair),
            "macro_fingerprint": base.fingerprint(original),
            "macro_units": base.state_units(original),
            "original_certificate_verified": verified,
        })

    boundary_pair = pairs[0]
    boundary_macro, boundary_cert = core.v2.apply_or_pair_v2(product, *boundary_pair, fresh)
    boundary_verified = core.v2.verify_or_pair_v2(product, boundary_macro, boundary_cert)
    boundary_after, boundary_stats = base.eliminate_var_capped(boundary_macro, 2, CAP)
    if not boundary_verified or boundary_after is not None or int(boundary_stats["raw_units"]) <= CAP:
        raise AssertionError("ORIGINAL_PYTHON_BOUNDARY_ROUTE_DID_NOT_OVERFLOW")

    controls = []
    for leaf_clauses in (80, 88):
        control_source, control_left, control_right = adv.build_selector_source(8, leaf_clauses, 4, 29100)
        control_product = adv.direct_selector_product(control_left, control_right)
        control = run_general_checker(general_checker_path, control_product, control_source)
        if control.get("status") != "EXACT_V2_RESCUE_FOUND" or control.get("rescue") is None:
            raise AssertionError(f"POSITIVE_CONTROL_{leaf_clauses}_FAILED")
        controls.append({
            "leaf_clauses": leaf_clauses,
            "source_fingerprint": base.fingerprint(control_source),
            "product_fingerprint": base.fingerprint(control_product),
            "status": control["status"],
            "rescue": control["rescue"],
        })

    preconditions = {
        "product_clause_count": len(product),
        "product_widths": sorted({len(c) for c in product}),
        "product_unique": len(set(product)) == len(product),
        "product_tautology_free": all(not any(-lit in c for lit in c) for c in product),
        "live_roots": list(ROOTS),
        "fresh_extension": fresh,
        "fresh_absent": fresh not in base.vars_of(product),
        "candidate_pair_count": len(pairs),
    }
    if preconditions != {
        "product_clause_count": PRODUCT_CLAUSES,
        "product_widths": [8],
        "product_unique": True,
        "product_tautology_free": True,
        "live_roots": list(ROOTS),
        "fresh_extension": 22,
        "fresh_absent": True,
        "candidate_pair_count": PAIR_COUNT,
    }:
        raise AssertionError("UNIFORM_EQUIVALENCE_PRECONDITION_DRIFT")

    report = {
        "schema": "JANUS/C025/L1-39100-PROMOTION/GAMMA-EXACT/v1",
        "status": "COMPLETE_EXACT_ORIGINAL_SEMANTICS_NO_V2_RESCUE",
        "candidate": candidate_meta(source, product),
        "Gamma": {
            "strictly_positive_by_complete_cap_crossing": True,
            "candidate_pair_count": PAIR_COUNT,
            "root_count_per_pair": len(ROOTS),
            "complete_pair_root_scope": ROUTE_COUNT,
            "first_exact_rescue": None,
            "independent_backend": independent,
            "general_backend": general,
            "backend_verdicts_agree": independent["status"] == general["status"],
            "parent_order_independent_fit_verdict": True,
            "first_crossing_amount_is_not_promoted_to_exact_Gamma_value": True,
        },
        "semantic_equivalence": {
            "lemma": str(EQUIVALENCE_PATH),
            "preconditions": preconditions,
            "original_macro_equivalence_samples": equivalence_samples,
            "original_python_boundary_route": {
                "pair_index": 0,
                "pair": list(boundary_pair),
                "pivot": 2,
                "macro_fingerprint": base.fingerprint(boundary_macro),
                "macro_units": base.state_units(boundary_macro),
                "original_certificate_verified": boundary_verified,
                "elimination_fit": boundary_after is not None,
                "elimination_stats": boundary_stats,
                "strict_cap_crossing": int(boundary_stats["raw_units"]) > CAP,
            },
            "positive_rescue_controls": controls,
        },
        "backend_provenance": {
            "independent": {
                "source_path": "experiments/theorem_extraction/c025_l1_uniform_exact_checker.cpp",
                "source_sha256": sha256_file(Path("experiments/theorem_extraction/c025_l1_uniform_exact_checker.cpp")),
                "binary_bytes": independent_checker_path.stat().st_size,
                "binary_sha256": sha256_file(independent_checker_path),
                "raw_receipt_bytes": independent_receipt_path.stat().st_size,
                "raw_receipt_sha256": sha256_file(independent_receipt_path),
                "execution_threads": 1,
            },
            "general": {
                "source_path": "experiments/theorem_extraction/c025_uniform_exact_checker_general.cpp",
                "source_sha256": sha256_file(Path("experiments/theorem_extraction/c025_uniform_exact_checker_general.cpp")),
                "binary_bytes": general_checker_path.stat().st_size,
                "binary_sha256": sha256_file(general_checker_path),
                "raw_receipt_bytes": general_receipt_path.stat().st_size,
                "raw_receipt_sha256": sha256_file(general_receipt_path),
                "execution_threads": 4,
            },
        },
        "P_VS_NP": P_VS_NP,
    }
    write_json(Path(args.out), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def collect_schema(root: Path, schema: str) -> list[tuple[Path, dict[str, Any]]]:
    matches = []
    for path in sorted(root.rglob("*.json")):
        try:
            value = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if value.get("schema") == schema:
            matches.append((path, value))
    return matches


def assert_candidate_consistency(receipts: Iterable[dict[str, Any]]) -> dict[str, Any]:
    candidates = [r["candidate"] for r in receipts]
    if not candidates or any(candidate != candidates[0] for candidate in candidates[1:]):
        raise AssertionError("CANDIDATE_IDENTITY_INCONSISTENT_ACROSS_RECEIPTS")
    return candidates[0]


def mode_assemble(args: argparse.Namespace) -> int:
    root = Path(args.input_dir)
    identity_matches = collect_schema(root, "JANUS/C025/L1-39100-PROMOTION/IDENTITY/v1")
    ordinary_matches = collect_schema(root, "JANUS/C025/L1-39100-PROMOTION/ORDINARY-SHARD/v1")
    gamma_matches = collect_schema(root, "JANUS/C025/L1-39100-PROMOTION/GAMMA-EXACT/v1")
    reach_matches = collect_schema(root, "JANUS/C025/L1-39100-PROMOTION/REACHABILITY/v1")
    original_v2_matches = collect_schema(root, "JANUS/C025/L1-FANOUT/V2-SHARD/v1")
    if len(identity_matches) != 1 or len(gamma_matches) != 1 or len(reach_matches) != 1:
        raise AssertionError("MISSING_OR_DUPLICATE_NONSHARDED_RECEIPT")
    if len(ordinary_matches) != args.ordinary_shards:
        raise AssertionError("ORDINARY_SHARD_RECEIPT_COUNT_MISMATCH")
    if len(original_v2_matches) != args.original_v2_shards:
        raise AssertionError("ORIGINAL_V2_SHARD_RECEIPT_COUNT_MISMATCH")

    identity = identity_matches[0][1]
    gamma = gamma_matches[0][1]
    reachability = reach_matches[0][1]
    ordinary = [value for _, value in ordinary_matches]
    candidate_value = assert_candidate_consistency([identity, gamma, reachability, *ordinary])
    identity_product_path = root / "c025-l1-39100-identity/product.txt"
    if identity.get("status") != "EXACT_IDENTITY_PASS" or not identity_product_path.is_file():
        raise AssertionError("IDENTITY_RECEIPT_NOT_EXACT")
    identity_product_bytes = identity_product_path.read_bytes()
    if (
        len(identity_product_bytes) != identity.get("product_text_bytes")
        or sha256_bytes(identity_product_bytes) != identity.get("product_text_sha256")
    ):
        raise AssertionError("IDENTITY_PRODUCT_BYTES_DRIFT")

    by_shard: dict[int, dict[str, Any]] = {}
    covered: set[int] = set()
    rows = []
    for receipt in ordinary:
        shard = receipt.get("shard", {})
        index = int(shard.get("index", -1))
        if int(shard.get("count", -1)) != args.ordinary_shards or index in by_shard:
            raise AssertionError("ORDINARY_SHARD_COORDINATE_INVALID")
        by_shard[index] = receipt
        if receipt.get("complete_for_selected_indices") is not True:
            raise AssertionError("ORDINARY_SHARD_INCOMPLETE")
        covered.update(int(x) for x in receipt.get("selected_pivot_indices", []))
        rows.extend(receipt.get("rows", []))
    if set(by_shard) != set(range(args.ordinary_shards)) or covered != set(range(len(ROOTS))):
        raise AssertionError("ORDINARY_SCOPE_NOT_COMPLETE")
    rows.sort(key=lambda row: int(row["pivot_index"]))
    if [int(row["pivot"]) for row in rows] != list(ROOTS):
        raise AssertionError("ORDINARY_PIVOT_ORDER_OR_COVERAGE_DRIFT")
    if not all(row.get("overflow") is True and int(row["stats"]["raw_units"]) > CAP for row in rows):
        raise AssertionError("DELTA_NOT_STRICTLY_POSITIVE")
    min_delta_crossing = min(int(row["stats"]["raw_units"]) - CAP for row in rows)

    if reachability.get("status") != "PASS" or reachability.get("reachable_at_frozen_ordinary_callsite") is not True:
        raise AssertionError("REACHABILITY_NOT_ADMITTED")
    if reachability.get("selector_pivot_1_exact_product") is not True:
        raise AssertionError("SELECTOR_PRODUCT_TRANSITION_NOT_EXACT")
    if gamma.get("status") != "COMPLETE_EXACT_ORIGINAL_SEMANTICS_NO_V2_RESCUE":
        raise AssertionError("GAMMA_RECEIPT_NOT_COMPLETE")
    gamma_core = gamma.get("Gamma", {})
    if gamma_core.get("strictly_positive_by_complete_cap_crossing") is not True:
        raise AssertionError("GAMMA_NOT_STRICTLY_POSITIVE")
    if int(gamma_core.get("complete_pair_root_scope", -1)) != ROUTE_COUNT or gamma_core.get("first_exact_rescue") is not None:
        raise AssertionError("GAMMA_SCOPE_OR_RESCUE_CONTRADICTION")

    original_by_shard: dict[int, dict[str, Any]] = {}
    original_covered: set[int] = set()
    original_tested = 0
    for _, receipt in original_v2_matches:
        shard = receipt.get("shard", {})
        index = int(shard.get("index", -1))
        count = int(shard.get("count", -1))
        if count != args.original_v2_shards or index in original_by_shard:
            raise AssertionError("ORIGINAL_V2_SHARD_COORDINATE_INVALID")
        original_by_shard[index] = receipt
        candidate_receipt = receipt.get("candidate", {})
        if (
            candidate_receipt.get("source_fingerprint") != SOURCE_FP
            or candidate_receipt.get("product_fingerprint") != PRODUCT_FP
            or candidate_receipt.get("N") != N
            or candidate_receipt.get("cap") != CAP
            or candidate_receipt.get("product_units") != PRODUCT_UNITS
        ):
            raise AssertionError("ORIGINAL_V2_CANDIDATE_IDENTITY_DRIFT")
        expected_indices = list(range(index, PAIR_COUNT, args.original_v2_shards))
        rows_receipt = receipt.get("tested_rows", [])
        row_indices = [int(row.get("pair_index", -1)) for row in rows_receipt]
        authority = receipt.get("authority_boundary", {})
        if (
            receipt.get("status") != "SHARD_COMPLETE_NO_RESCUE"
            or receipt.get("global_pair_count") != PAIR_COUNT
            or receipt.get("selected_pair_indices") != expected_indices
            or row_indices != expected_indices
            or receipt.get("tested_count") != len(expected_indices)
            or receipt.get("complete_for_selected_indices") is not True
            or receipt.get("rescue") is not None
            or not all(
                authority.get(key) is True
                for key in (
                    "original_v2_candidate_generator",
                    "original_v2_apply_verify",
                    "original_eliminate_var_capped_via_first_capped_elimination",
                    "original_progress_phi",
                )
            )
        ):
            raise AssertionError("ORIGINAL_V2_SHARD_NOT_COMPLETE_EXACT_NO_RESCUE")
        if any(row.get("macro_over_cap") is not True and row.get("fitting_root_pivot") is not None for row in rows_receipt):
            raise AssertionError("ORIGINAL_V2_FITTING_ROOT_CONTRADICTION")
        original_covered.update(expected_indices)
        original_tested += len(expected_indices)
    if (
        set(original_by_shard) != set(range(args.original_v2_shards))
        or original_covered != set(range(PAIR_COUNT))
        or original_tested != PAIR_COUNT
    ):
        raise AssertionError("ORIGINAL_V2_CANONICAL_SCOPE_INCOMPLETE")
    original_v2_summary = {
        "status": "COMPLETE_ORIGINAL_FROZEN_V2_NO_RESCUE",
        "shard_count": args.original_v2_shards,
        "candidate_pair_count": PAIR_COUNT,
        "covered_candidate_indices": list(range(PAIR_COUNT)),
        "tested_pair_count": original_tested,
        "first_exact_rescue": None,
        "direct_state_is_exact_reached_callsite_state": True,
        "uses_original_v2_candidate_generator": True,
        "uses_original_v2_apply_and_verify": True,
        "uses_original_capped_root_elimination": True,
        "uses_original_progress_gate": True,
    }

    gate = load_json(GATE_PATH)
    equivalence = load_json(EQUIVALENCE_PATH)
    if gate.get("status") != "FROZEN_ARMED__EXACT_HEAD_CI_AND_INDEPENDENT_ADMISSION_REQUIRED":
        raise AssertionError("PROMOTION_GATE_NOT_ARMED")
    if not str(equivalence.get("status", "")).startswith("PROVED_FOR_FROZEN_UNIFORM_PRODUCT_FAMILY"):
        raise AssertionError("SEMANTIC_EQUIVALENCE_LEMMA_NOT_AVAILABLE")
    immutable_hashes = gate["immutable_parent_receipts"]
    for path_text, expected in immutable_hashes.items():
        if sha256_file(Path(path_text)) != expected:
            raise AssertionError(f"IMMUTABLE_PARENT_RECEIPT_DRIFT:{path_text}")

    evidence_paths = sorted(path for path in root.rglob("*") if path.is_file())
    evidence_hashes = {str(path.relative_to(root)): sha256_file(path) for path in evidence_paths}
    source_paths = [
        Path("experiments/theorem_extraction/c025_l1_39100_promotion_gate.py"),
        Path("experiments/theorem_extraction/c025_l1_39100_admission_verifier.py"),
        Path("experiments/theorem_extraction/c025_l1_uniform_exact_checker.cpp"),
        Path("experiments/theorem_extraction/c025_uniform_exact_checker_general.cpp"),
        Path("experiments/theorem_extraction/c025_l1_fanout_exact_gate.py"),
        Path("experiments/direct/janus_pirc_decision_core_v0_4.py"),
        Path("experiments/direct/janus_unified_macro_restore_v2.py"),
        Path("experiments/direct/janus_unified_proof_carrying_akinator_jec.py"),
        GATE_PATH,
        EQUIVALENCE_PATH,
        Path(".github/workflows/validate-c025-l1-39100-promotion.yml"),
    ]
    source_hashes = {str(path): sha256_file(path) for path in source_paths}

    semantic = {
        "schema": "JANUS/C025/L1-39100-EXACT-COUNTEREXAMPLE/SEMANTIC/v1",
        "subject": {
            "repository": args.repository,
            "commit": args.subject_commit,
            "branch": args.branch,
            "fixed_algorithm": "PIRC_DECISION_CORE_V0_4",
        },
        "candidate": candidate_value,
        "reachability": {
            "exact": True,
            "reachable_at_frozen_ordinary_callsite": True,
            "selector_pivot_1_exact_product": True,
            "receipt": reachability,
        },
        "Delta": {
            "strictly_positive": True,
            "original_eliminate_var_capped": True,
            "pivot_count": len(ROOTS),
            "covered_pivot_indices": list(range(len(ROOTS))),
            "minimum_observed_first_crossing_margin": min_delta_crossing,
            "first_crossing_margin_is_not_promoted_to_exact_Delta_value": True,
            "rows": rows,
        },
        "Gamma": gamma_core,
        "original_frozen_v2": original_v2_summary,
        "semantic_equivalence": gamma["semantic_equivalence"],
        "backend_provenance": gamma["backend_provenance"],
        "candidate_results": {
            "L1_ROOT_PHASE_POLYNOMIAL_GRAMMAR_TOTALITY": "REFUTED_BY_EXACT_REACHABLE_39100_COUNTEREXAMPLE",
            "L1A_ALL_PIVOT_OVERFLOW_FORCES_FREQUENT_PAIR": "REFUTED_PREVIOUSLY",
            "L1B_ALL_PIVOT_OVERFLOW_FORCES_PAIR_DENSITY": "REFUTED_PREVIOUSLY",
            "L1C_POLARITY_DRAINAGE_TOTALITY": "REFUTED_PREVIOUSLY",
        },
        "scientific_boundary": {
            "finite_witness_refutes_only_L1": True,
            "P2_REACHABLE_PRESERVATION": "OPEN",
            "ROOT_FREE_V3_TAIL": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
        "P_VS_NP": P_VS_NP,
    }
    semantic_digest = sha256_bytes(canonical_json_bytes(semantic))
    report = {
        "schema": "JANUS/C025/L1-39100-EXACT-COUNTEREXAMPLE/COMPOSITE/v1",
        "production_state": "EXACT_COUNTEREXAMPLE_PRODUCED__INDEPENDENT_ADMISSION_REQUIRED",
        "semantic_receipt": semantic,
        "semantic_sha256": semantic_digest,
        "provenance": {
            "evidence_file_sha256": evidence_hashes,
            "source_file_sha256": source_hashes,
            "immutable_parent_receipts": immutable_hashes,
            "old_unknown_or_pending_receipt_rewritten": False,
            "raw_ci_stdout_reconstructed": False,
            "generation_modes": {
                "reachability": "unmodified_frozen_core_prefix",
                "Delta": "eight_disjoint_original_python_shards",
                "Gamma_primary": "independent_exact_CXX_backend_OMP1",
                "Gamma_replay": "general_exact_CXX_backend_OMP4",
                "Gamma_original_boundary": "original_python_macro_verify_eliminate",
                "original_frozen_v2": "sixty_four_disjoint_original_python_canonical_pair_shards",
                "aggregation": "canonical_pivot_and_scope_sets_order_independent",
            },
        },
        "resource_ledger": {
            "ordinary_parent_pairs_examined_until_cap_crossing": sum(int(row["stats"].get("pairs", 0)) for row in rows),
            "ordinary_pivots": len(rows),
            "v2_candidate_pairs": PAIR_COUNT,
            "v2_root_probes": ROUTE_COUNT,
            "original_v2_pairs_replayed": original_tested,
            "explicit_evidence_files": len(evidence_paths),
        },
        "admission": {
            "state": "PENDING_SEPARATE_NO_IMPORT_VERIFIER",
            "verifier": "experiments/theorem_extraction/c025_l1_39100_admission_verifier.py",
        },
        "P_VS_NP": P_VS_NP,
    }
    write_json(Path(args.out), report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)

    identity = sub.add_parser("identity")
    identity.add_argument("--out", required=True)
    identity.add_argument("--product-out")
    identity.set_defaults(func=mode_identity)

    ordinary = sub.add_parser("ordinary")
    ordinary.add_argument("--shard-index", type=int, required=True)
    ordinary.add_argument("--shard-count", type=int, required=True)
    ordinary.add_argument("--out", required=True)
    ordinary.set_defaults(func=mode_ordinary)

    reachability = sub.add_parser("reachability")
    reachability.add_argument("--out", required=True)
    reachability.set_defaults(func=mode_reachability)

    gamma = sub.add_parser("gamma-audit")
    gamma.add_argument("--product", required=True)
    gamma.add_argument("--independent", required=True)
    gamma.add_argument("--general", required=True)
    gamma.add_argument("--independent-checker", required=True)
    gamma.add_argument("--general-checker", required=True)
    gamma.add_argument("--out", required=True)
    gamma.set_defaults(func=mode_gamma_audit)

    assemble = sub.add_parser("assemble")
    assemble.add_argument("--input-dir", required=True)
    assemble.add_argument("--ordinary-shards", type=int, default=8)
    assemble.add_argument("--original-v2-shards", type=int, default=ORIGINAL_V2_SHARDS)
    assemble.add_argument("--repository", default=REPOSITORY)
    assemble.add_argument("--subject-commit", required=True)
    assemble.add_argument("--branch", default=BRANCH)
    assemble.add_argument("--out", required=True)
    assemble.set_defaults(func=mode_assemble)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
