from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Callable

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis
from research.tools.apma_bicameral_pair_separator import pair_separator_explainer as pair_sep
from research.tools.apma_bicameral_mincut import mincut_logwidth_explainer as mincut
from research.tools.apma_cut_support_carrier import cut_support_carrier as cut_support
from research.tools.apma_component_join_carrier import component_join_carrier as component_join
from research.tools.apma_derived_boundary_factor import derived_two_relation_factor as derived
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_bucket_common_core import common_core_semijoin_prefilter as cc_v1
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as v310
from research.tools.apma_bucket_fixed_depth_122 import fixed_depth_122 as v314
from research.tools.apma_bucket_k5_raw_semantic_forensic import forensic as v316
from research.tools.apma_log_alien_transfer import log_alien_transfer
from research.tools.apma_unseen_local_invariant_orbit_count import independent_checker as orbit_checker

ARTIFACT_ID = "JANUS-TRUMP-SOURCE-AUTHORIZED-CONNECTED-MIXED-RAW-POST-ORBIT-PORTFOLIO-OBSTRUCTION-CENSUS-INDEPENDENT-CHECKER-2026-09-16-v1.0"
PASS_FOUND = "PASS_DIAGNOSTIC_FIRST_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_OBSTRUCTION_FROZEN"
PASS_NONE = "PASS_DIAGNOSTIC_NO_CURRENT_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_OBSTRUCTION_FOUND"

PREREG = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_PORTFOLIO_OBSTRUCTION_CENSUS_PREREGISTRATION_2026-09-16.json")
PREREG_BLOB = "d5742ab49067f8d842bb8d805254b7cbba6e3f10"
PROFILER = Path("research/tools/apma_connected_mixed_post_orbit_obstruction_census/census.py")
PROFILER_BLOB = "f5aa39804983d49149c976e8367a96397bad888e"
PRIOR_CLOSURE = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_GT2_UNADMITTED_RAW_OBSTRUCTION_CENSUS_RESULT_2026-09-16.json")
PRIOR_CLOSURE_BLOB = "df02fe97ac99c6d930c186680f9440c826c570ee"

SOURCE_BLOBS = {
    "research/tools/apma_unseen_basis/raw_relation_basis.py": "63490c05ef3e91a4f682f75da26ff2af811839a6",
    "research/tools/apma_bicameral_pair_separator/pair_separator_explainer.py": "b6dc5fde585affb167e74308bc8f10c64f7d2990",
    "research/tools/apma_bicameral_mincut/mincut_logwidth_explainer.py": "c0c612676e39241b95026c15823e7af6b3da8f0d",
    "research/tools/apma_cut_support_carrier/cut_support_carrier.py": "012aa1acf52fa12de26bb64df303b2208d396ea9",
    "research/tools/apma_component_join_carrier/component_join_carrier.py": "89f5d591d4d553bb26489908a79f2c739f62b756",
    "research/tools/apma_derived_boundary_factor/derived_two_relation_factor.py": "1047351df47ed5f326eef2650da0c9f5ee0f2fda",
    "research/tools/apma_guarded_elimination/guarded_bounded_output_elimination.py": "314034bac990e524d1db7743aef0aebd3b4565c1",
    "research/tools/apma_bucket_common_core/common_core_semijoin_prefilter.py": "f103bf9b14e3b208200f429b75d0858c4963fa7c",
    "research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py": "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8",
    "research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py": "cd17292b7451b03b966dbcf62d1b6e4c767f7ac0",
    "research/tools/apma_bucket_residual_pair_separator/residual_pair_separator_factorized_payload.py": "0853ebb9a3e273fdaeca172dbe2502cc7214cf61",
    "research/tools/apma_bucket_fixed_depth_122/fixed_depth_122.py": "2e02bac1d78b751d22df2c50a01980ae06bd2751",
    "research/tools/apma_bucket_k5_raw_semantic_forensic/forensic.py": "4128f0db77dfc1391b6ec539f201250bfb3d8b6e",
    "research/tools/apma_log_alien_transfer/log_alien_transfer.py": "d20cd94fa2e0324e301f55211152c2d410099425",
    "research/tools/apma_unseen_local_invariant_orbit_count/independent_checker.py": "0e12304d843ef0bcce6b6c032fd2af2c68abcd14",
}

SCHAEFER_NAMES = ("ZERO_VALID", "ONE_VALID", "HORN", "DUAL_HORN", "BIJUNCTIVE", "AFFINE")
OR2_KEY = (2, ("01", "10", "11"))
EVEN_XOR3_KEY = (3, ("000", "011", "101", "110"))


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def source_guard() -> dict[str, Any]:
    r = root()
    checks = {
        "prereg_blob": git_blob_sha1(r / PREREG) == PREREG_BLOB,
        "profiler_blob_bound_without_import": git_blob_sha1(r / PROFILER) == PROFILER_BLOB,
        "prior_closure_blob": git_blob_sha1(r / PRIOR_CLOSURE) == PRIOR_CLOSURE_BLOB,
    }
    for path, expected in SOURCE_BLOBS.items():
        checks[path] = git_blob_sha1(r / path) == expected
    return {"ok": all(checks.values()), "checks": checks, "new_profiler_imported": False}


def fixture_defs() -> list[dict[str, Any]]:
    defs: list[tuple[str, str, str, Callable[[], dict]]] = [
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "PAIR_SEPARATOR_POSITIVE_PRIOR_BICONNECTED", "pair_separator_explainer.positive_prior_biconnected()", pair_sep.positive_prior_biconnected),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "PAIR_SEPARATOR_NEGATIVE_THREE_VARIABLE_CUT_REQUIRED", "pair_separator_explainer.negative_three_variable_cut_required()", pair_sep.negative_three_variable_cut_required),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "MINCUT_POSITIVE_LOGWIDTH_CUT3", "mincut_logwidth_explainer.positive_logwidth_cut3()", mincut.positive_logwidth_cut3),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "MINCUT_NEGATIVE_OVERWIDTH_CUT20", "mincut_logwidth_explainer.negative_overwidth_cut(20)", lambda: mincut.negative_overwidth_cut(20)),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "CUT_SUPPORT_POSITIVE_OVERWIDTH", "cut_support_carrier.positive_overwidth()", cut_support.positive_overwidth),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "CUT_SUPPORT_EMPTY_INTERSECTION20", "cut_support_carrier.empty_intersection_control(20)", lambda: cut_support.empty_intersection_control(20)),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "CUT_SUPPORT_MULTI_RELATION_COMPONENT20", "cut_support_carrier.multi_relation_component_control(20)", lambda: cut_support.multi_relation_component_control(20)),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "CUT_SUPPORT_PARTIAL_CUT_VISIBILITY", "cut_support_carrier.partial_cut_visibility_control()", cut_support.partial_cut_visibility_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "COMPONENT_JOIN_POSITIVE_MULTI_RELATION_K20", "component_join_carrier.positive_multi_relation_k20()", component_join.positive_multi_relation_k20),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "COMPONENT_JOIN_EMPTY_CONDITIONAL_JOIN", "component_join_carrier.empty_conditional_join_control()", component_join.empty_conditional_join_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "COMPONENT_JOIN_ALPHA_CYCLE", "component_join_carrier.alpha_cycle_control()", component_join.alpha_cycle_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "DERIVED_POSITIVE_NO_ANCHOR_K20", "derived_two_relation_factor.positive_no_anchor_k20()", derived.positive_no_anchor_k20),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "DERIVED_EMPTY_PAIR_SUPPORT", "derived_two_relation_factor.empty_pair_support_control()", derived.empty_pair_support_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "DERIVED_THREE_RELATION_NO_ANCHOR", "derived_two_relation_factor.three_relation_no_anchor_control()", derived.three_relation_no_anchor_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "GUARDED_POSITIVE_MIXED_THREE_RELATION", "guarded_bounded_output_elimination.positive_mixed_three_relation_control()", guarded.positive_mixed_three_relation_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "GUARDED_SCOPED_UNSAT", "guarded_bounded_output_elimination.scoped_unsat_control()", guarded.scoped_unsat_control),
        ("HISTORICAL_PRE_NONUNIQUE_RAW_CONTROLS", "GUARDED_OVERBUDGET", "guarded_bounded_output_elimination.overbudget_control()", guarded.overbudget_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_4_POSITIVE_ALIGNED_OVERBUDGET_CONTROL", "common_core_semijoin_prefilter.positive_aligned_overbudget_control()", cc_v1.positive_aligned_overbudget_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_4_FILTERED_STILL_OVERBUDGET_CONTROL", "common_core_semijoin_prefilter.filtered_still_overbudget_control()", cc_v1.filtered_still_overbudget_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_6_RESIDUAL_COMPONENT_GT2_CONTROL", "residual_le2_factorized_payload.residual_component_gt2_control()", v36.residual_component_gt2_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_8_NO_SINGLE_VARIABLE_ARTICULATION_CONTROL", "residual_single_separator_factorized_payload.no_single_variable_articulation_control()", v38.no_single_variable_articulation_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_8_BRANCH_STILL_GT2_CONTROL", "residual_single_separator_factorized_payload.branch_still_gt2_control()", v38.branch_still_gt2_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROLS", "V3_10_NO_PAIR_K4_CONTROL", "residual_pair_separator_factorized_payload.no_pair_k4_control()", v310.no_pair_k4_control),
        ("V3_20_BASELINE_SOURCE_AUTHORIZED_RAW_CONTROL_ALIAS", "V3_14_POSITIVE_K4_CONTROL", "fixed_depth_122.positive_k4_control()", v314.positive_k4_control),
        ("V3_20_BASELINE_REPRODUCIBLY_GENERATED_RAW_PREDECESSOR_PROBES", "V3_16_RAW_K5_FULL_CUBE", "k5_raw_semantic_forensic.build_raw_k5('FULL_CUBE')", lambda: v316.build_raw_k5("FULL_CUBE")),
        ("V3_20_BASELINE_REPRODUCIBLY_GENERATED_RAW_PREDECESSOR_PROBES", "V3_16_RAW_K5_EXACT_2_OF_4", "k5_raw_semantic_forensic.build_raw_k5('EXACT_2_OF_4')", lambda: v316.build_raw_k5("EXACT_2_OF_4")),
    ]
    return [
        {"ordinal": i, "source_class": cls, "name": name, "constructor": ctor, "raw": fn()}
        for i, (cls, name, ctor, fn) in enumerate(defs)
    ]


def canonical_raw(raw: dict) -> dict:
    return raw_basis.canonicalize_raw(raw)


def raw_sha256(raw: dict) -> str:
    return hashlib.sha256(canonical_bytes(canonical_raw(raw))).hexdigest()


def dedup() -> list[dict[str, Any]]:
    entries = fixture_defs()
    if len(entries) != 26:
        raise RuntimeError("SOURCE_ENTRY_COUNT_NOT_26")
    table: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for e in entries:
        sha = raw_sha256(e["raw"])
        if sha not in table:
            table[sha] = {"raw_sha256": sha, "first_ordinal": e["ordinal"], "raw": canonical_raw(e["raw"]), "aliases": [], "source_classes": [], "constructors": []}
            order.append(sha)
        table[sha]["aliases"].append(e["name"])
        table[sha]["source_classes"].append(e["source_class"])
        table[sha]["constructors"].append(e["constructor"])
    return [table[s] for s in order]


def incidence_component_count(canonical: dict) -> int:
    constraints = canonical["constraints"]
    if not constraints:
        return 0
    parent = list(range(len(constraints)))
    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            if ra > rb:
                ra, rb = rb, ra
            parent[rb] = ra
    first: dict[int, int] = {}
    for i, c in enumerate(constraints):
        for v in c["scope"]:
            if v in first:
                union(i, first[v])
            else:
                first[v] = i
    return len({find(i) for i in range(len(constraints))})


def eligibility(raw: dict) -> dict[str, Any]:
    canonical = canonical_raw(raw)
    surface = raw_basis.relation_surface(canonical)
    per = raw_basis.classify_each(surface)
    global_fp = raw_basis.classify_language(raw_basis.surface_to_relations(surface))
    connected = incidence_component_count(canonical) == 1
    every_local = bool(per) and all(any(bool(r["fingerprint"].get(n)) for n in SCHAEFER_NAMES) for r in per)
    global_bases = [n for n in SCHAEFER_NAMES if global_fp.get(n)]
    if not connected:
        cls = "OUT_OF_SCOPE_NOT_CONNECTED"
    elif not every_local:
        cls = "OUT_OF_SCOPE_INTRINSICALLY_NON_SCHAEFER_RELATION_PRESENT"
    elif global_bases:
        cls = "OUT_OF_SCOPE_SINGLE_GLOBAL_SCHAEFER_BASIS"
    else:
        cls = "ELIGIBLE_CONNECTED_MIXED"
    return {"eligible": cls == "ELIGIBLE_CONNECTED_MIXED", "eligibility_class": cls, "incidence_component_count": incidence_component_count(canonical), "per_relation_fingerprint": per, "global_language_fingerprint": global_fp, "global_candidate_bases": global_bases}


def closure_sets() -> dict[str, set[str]]:
    data = json.loads((root() / PRIOR_CLOSURE).read_text(encoding="utf-8"))
    r = data["machine_receipt"]
    return {"normalization": set(r.get("closed_by_universal_normalization", [])), "two_factor": set(r.get("closed_by_v3_18_two_factor", []))}


def prior_closure(aliases: list[str], sets: dict[str, set[str]]) -> str | None:
    if any(a in sets["normalization"] for a in aliases):
        return "ELIGIBLE_CONNECTED_MIXED_CLOSED_BY_EXACT_PRIOR_RAW_SHA_RECEIPT"
    if any(a in sets["two_factor"] for a in aliases):
        return "ELIGIBLE_CONNECTED_MIXED_CLOSED_BY_EXACT_PRIOR_RAW_SHA_RECEIPT"
    return None


def relation_key_from_constraint(row: dict) -> tuple[int, tuple[str, ...]]:
    return len(row["scope"]), tuple(sorted("".join(str(int(b)) for b in t) for t in row["allowed"]))


def independent_log_alien(raw: dict) -> dict[str, Any]:
    canonical = canonical_raw(raw)
    surface = raw_basis.relation_surface(canonical)
    keys = {(int(r["arity"]), tuple(r["allowed"])) for r in surface}
    if keys != {OR2_KEY, EVEN_XOR3_KEY}:
        return {"applicable": False}
    attempts = []
    for base_key, alien_key in ((OR2_KEY, EVEN_XOR3_KEY), (EVEN_XOR3_KEY, OR2_KEY)):
        base = []
        aliens = []
        for row in canonical["constraints"]:
            k = relation_key_from_constraint(row)
            rec = {"id": str(row["id"]), "scope": [int(v) for v in row["scope"]]}
            if k == base_key:
                rec["kind"] = "OR2" if k == OR2_KEY else "EVEN_XOR3"
                base.append(rec)
            elif k == alien_key:
                rec["kind"] = "OR2" if k == OR2_KEY else "EVEN_XOR3"
                aliens.append(rec)
            else:
                raise RuntimeError("UNEXPECTED_RELATION_KEY")
        instance = {"L": len(canonical_bytes(canonical)), "base_kind": "OR2" if base_key == OR2_KEY else "EVEN_XOR3", "alien_kind": "OR2" if alien_key == OR2_KEY else "EVEN_XOR3", "base_constraints": base, "alien_constraints": aliens}
        result = log_alien_transfer.solve_instance(instance)
        attempts.append({"status": result.get("status"), "base_kind": instance["base_kind"], "alien_kind": instance["alien_kind"], "q_pow_k": result.get("q_pow_k"), "L": result.get("L", instance["L"])})
        if result.get("status") in {"SAT", "UNSAT"}:
            return {"applicable": True, "closed": True, "attempts": attempts}
    return {"applicable": True, "closed": False, "attempts": attempts}


def independent_orbit(raw: dict) -> dict[str, Any]:
    f = orbit_checker.normalize(raw)
    edges = orbit_checker.all_generator_edges(f)
    cells = orbit_checker.components(f.variables, edges)
    nontrivial = [c for c in cells if len(c) >= 2]
    if not nontrivial:
        return {"status": "OPEN_NO_NONTRIVIAL_EXCHANGEABILITY", "solver_authority": False, "cells": cells, "Q": None}
    q, within = orbit_checker.q_count(cells, f.L * f.L)
    if not within:
        return {"status": "OPEN_ORBIT_COUNT_QUOTIENT_OVER_BUDGET", "solver_authority": False, "cells": cells, "Q": q}
    if q >= (1 << len(f.variables)):
        return {"status": "OPEN_NO_STRICT_ORBIT_COMPRESSION", "solver_authority": False, "cells": cells, "Q": q}
    enumerated = 0
    for counts in itertools.product(*[range(len(c) + 1) for c in cells]):
        enumerated += 1
        a = orbit_checker.assignment(cells, counts)
        if not orbit_checker.violated(f, a):
            return {"status": "ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "solver_authority": True, "cells": cells, "Q": q, "count_states_enumerated": enumerated}
    return {"status": "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT", "solver_authority": True, "cells": cells, "Q": q, "count_states_enumerated": enumerated}


def expected_rows() -> tuple[list[dict[str, Any]], dict[str, Any] | None, int]:
    rows = []
    first_obstruction = None
    eligible_count = 0
    sets = closure_sets()
    for rec in dedup():
        elig = eligibility(rec["raw"])
        if not elig["eligible"]:
            classification = elig["eligibility_class"]
            rows.append({"raw_sha256": rec["raw_sha256"], "classification": classification, "eligibility": elig})
            continue
        eligible_count += 1
        classification = prior_closure(rec["aliases"], sets)
        log = None
        orbit = None
        if classification is None:
            log = independent_log_alien(rec["raw"])
            if log.get("closed"):
                classification = "ELIGIBLE_CONNECTED_MIXED_CLOSED_BY_SEALED_LOG_ALIEN_TRANSFER"
            else:
                orbit = independent_orbit(rec["raw"])
                if orbit["status"] in {"ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"} and orbit["solver_authority"]:
                    classification = "ELIGIBLE_CONNECTED_MIXED_CLOSED_BY_SEALED_ORBIT_COUNT_V1"
                else:
                    classification = "ELIGIBLE_CONNECTED_MIXED_UNADMITTED_POST_ORBIT_PORTFOLIO_OBSTRUCTION"
                    first_obstruction = {"raw_sha256": rec["raw_sha256"], "aliases": rec["aliases"], "eligibility": elig, "log_alien": log, "orbit": orbit}
        rows.append({"raw_sha256": rec["raw_sha256"], "classification": classification, "eligibility": elig, "log_alien": log, "orbit": orbit})
        if first_obstruction is not None:
            break
    return rows, first_obstruction, eligible_count


def verify(candidate: dict[str, Any]) -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        raise RuntimeError("INDEPENDENT_SOURCE_GUARD_FAILED")
    expected, obstruction, eligible_count = expected_rows()
    observed = candidate.get("rows")
    if not isinstance(observed, list):
        raise RuntimeError("CANDIDATE_ROWS_MISSING")
    observed_map = {str(r["raw_sha256"]): r for r in observed}
    checks = {
        "candidate_verdict_known": candidate.get("verdict") in {PASS_FOUND, PASS_NONE},
        "constructor_count_26": candidate.get("constructor_entry_count") == 26,
        "row_count_match": len(observed) == len(expected),
        "rows_match_by_sha": True,
        "eligibility_match": True,
        "classification_match": True,
        "first_obstruction_match": True,
        "eligible_count_match": candidate.get("eligible_connected_mixed_count_before_stop") == eligible_count,
    }
    for exp in expected:
        obs = observed_map.get(exp["raw_sha256"])
        if obs is None:
            checks["rows_match_by_sha"] = False
            continue
        if obs.get("classification") != exp["classification"]:
            checks["classification_match"] = False
        oe = obs.get("eligibility", {})
        ee = exp["eligibility"]
        if oe.get("eligibility_class") != ee.get("eligibility_class") or oe.get("global_language_fingerprint") != ee.get("global_language_fingerprint"):
            checks["eligibility_match"] = False
        if exp.get("orbit") is not None:
            observed_orbit = obs.get("orbit_replay", {})
            if observed_orbit.get("status") != exp["orbit"].get("status") or observed_orbit.get("quotient_states_Q") != exp["orbit"].get("Q"):
                checks["classification_match"] = False
    cand_obs = candidate.get("first_real_post_orbit_obstruction")
    expected_sha = obstruction["raw_sha256"] if obstruction else None
    observed_sha = cand_obs.get("raw_sha256") if isinstance(cand_obs, dict) else None
    checks["first_obstruction_match"] = expected_sha == observed_sha
    expected_verdict = PASS_FOUND if obstruction else PASS_NONE
    checks["candidate_verdict_known"] = checks["candidate_verdict_known"] and candidate.get("verdict") == expected_verdict
    if not all(checks.values()):
        raise RuntimeError(f"INDEPENDENT_MISMATCH:{json.dumps(checks, sort_keys=True)}")
    return {"artifact_id": ARTIFACT_ID, "verified": True, "verdict": expected_verdict, "source_guard": guard, "unique_rows_evaluated": len(expected), "eligible_connected_mixed_count_before_stop": eligible_count, "first_real_post_orbit_obstruction_sha256": expected_sha, "checks": checks, "scientific_firewall": {"P_VS_NP": "OPEN", "GENERAL_SAT_IN_P": "NOT_PROVED", "CONNECTED_MIXED_CORE_SOLVED": "NO", "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED"}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-json", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.candidate_json).read_text(encoding="utf-8").strip().splitlines()[-1])
    print(json.dumps(verify(data), sort_keys=True))


if __name__ == "__main__":
    main()
