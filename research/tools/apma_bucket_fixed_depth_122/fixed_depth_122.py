from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw, RawBasisInputError
from research.tools.apma_bucket_residual_pair_separator import residual_pair_separator_factorized_payload as pair_v310
from research.tools.apma_bucket_residual_single_separator import residual_single_separator_factorized_payload as v38
from research.tools.apma_bucket_residual_le2 import residual_le2_factorized_payload as v36
from research.tools.apma_guarded_elimination import guarded_bounded_output_elimination as guarded
from research.tools.apma_cut_support_carrier import cut_support_carrier as parent_support

ARTIFACT_ID = "JANUS-TRUMP-BICAMERAL-BUCKET-UNIQUE-CORE-RESIDUAL-FIXED-DEPTH-1-2-2-SEPARATOR-PORTFOLIO-CANDIDATE-2026-09-15-v1.0"
AUTHORITY = "CANDIDATE_IMPLEMENTATION__FIXED_DEPTH_ONLY__NO_SCIENTIFIC_PROMOTION"
VERDICT = "PASS_SCOPED_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO_V1"
PREREG = Path("research/TRUMP_BICAMERAL_BUCKET_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO_PREREGISTRATION_2026-09-15.json")
PREREG_BLOB = "1f73029ff201702f87b3fe35214804fd75f88a30"
PARENT = Path("registry/TRUMP_CURRENT_STATE_2026-09-15_v3.13.json")
PARENT_BLOB = "8051f6d3f579b85f6fdb613c2ece11386d816d48"
PAIR = Path("research/tools/apma_bucket_residual_pair_separator/residual_pair_separator_factorized_payload.py")
PAIR_BLOB = "0853ebb9a3e273fdaeca172dbe2502cc7214cf61"
LE2 = Path("research/tools/apma_bucket_residual_le2/residual_le2_factorized_payload.py")
LE2_BLOB = "8c0c2802ccf8bf9b67b80cedb5b26797cd78d1c8"
V38 = Path("research/tools/apma_bucket_residual_single_separator/residual_single_separator_factorized_payload.py")
V38_BLOB = "cd17292b7451b03b966dbcf62d1b6e4c767f7ac0"
MAX_LOGICAL_LEAVES = 32


def root() -> Path:
    return Path(__file__).resolve().parents[3]


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def source_guard() -> dict:
    r = root()
    checks = {
        "prereg_blob": blob(r / PREREG) == PREREG_BLOB,
        "parent_v3_13_blob": blob(r / PARENT) == PARENT_BLOB,
        "pair_v3_10_blob": blob(r / PAIR) == PAIR_BLOB,
        "le2_v3_6_blob": blob(r / LE2) == LE2_BLOB,
        "single_v3_8_blob": blob(r / V38) == V38_BLOB,
    }
    return {"ok": all(checks.values()), "checks": checks}


def firewall() -> dict:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "GENERAL_RESIDUAL_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "GENERAL_BOUNDED_TREEWIDTH_TRACTABILITY": "NOT_PROVED",
        "GENERAL_RECURSIVE_SEPARATOR_TRACTABILITY": "NOT_PROVED",
        "GLOBAL_APMA_FRONTIER_ADVANCE": "NONE_PENDING_HQ_REVIEW",
        "SCOPE": "UNIQUE_COMMON_CORE_WITH_A_FIXED_DEPTH_1_2_2_RAW_RESIDUAL_SEPARATOR_PLAN_TERMINATING_IN_SEALED_LE2_CARRIERS",
    }


def rscope(factor: dict, core: list[int]) -> set[int]:
    cc = set(int(v) for v in core)
    return {int(v) for v in factor["scope"] if int(v) not in cc}


def componentize(factors: list[dict], core: list[int]) -> list[list[int]]:
    return v36.residual_components(factors, core)


def seed_root_provenance(factors: list[dict]) -> list[dict]:
    out = []
    for f in factors:
        scope = [int(v) for v in f["scope"]]
        rows = [tuple(int(x) for x in r) for r in f["rows"]]
        g = {**f, "scope": scope, "rows": rows}
        g["_root_origin_scope"] = list(scope)
        g["_root_origin_witness"] = {row: row for row in rows}
        out.append(g)
    return out


def restrict_factor(factor: dict, assignment: dict[int, int]) -> tuple[dict | None, dict]:
    scope = [int(v) for v in factor["scope"]]
    rows = [tuple(int(x) for x in r) for r in factor["rows"]]
    positions = [(i, v) for i, v in enumerate(scope) if v in assignment]
    keep = [i for i, v in enumerate(scope) if v not in assignment]
    root_scope = list(factor.get("_root_origin_scope", scope))
    old_root = factor.get("_root_origin_witness", {row: row for row in rows})
    witness: dict[tuple[int, ...], tuple[int, ...]] = {}
    matched = 0
    for row in rows:
        if all(int(row[i]) == int(assignment[v]) for i, v in positions):
            matched += 1
            new_row = tuple(int(row[i]) for i in keep)
            witness.setdefault(new_row, tuple(int(x) for x in old_root.get(tuple(row), tuple(row))))
    if not witness:
        return None, {"factor_id": str(factor["id"]), "matched_rows": 0}
    g = {**factor, "scope": [scope[i] for i in keep], "rows": sorted(witness)}
    g["_root_origin_scope"] = root_scope
    g["_root_origin_witness"] = witness
    return g, {"factor_id": str(factor["id"]), "matched_rows": matched, "surviving_projected_rows": len(witness)}


def restrict_factors(factors: list[dict], assignment: dict[int, int]) -> dict:
    out = []
    receipt = []
    for f in factors:
        z, rec = restrict_factor(f, assignment)
        receipt.append(rec)
        if z is None:
            return {"status": "EXACT_UNSAT_BY_EMPTY_FIXED_DEPTH_RESTRICTION", "factors": None, "receipt": receipt}
        out.append(z)
    return {"status": "READY", "factors": out, "receipt": receipt}


def target_gt2_component(factors: list[dict], core: list[int]) -> list[int] | None:
    gt = [c for c in componentize(factors, core) if len(c) > 2]
    if len(gt) != 1:
        return None
    return gt[0]


def pair_disconnects_component(factors: list[dict], core: list[int], comp: list[int], pair: tuple[int, int]) -> bool:
    scopes = [rscope(factors[i], core) for i in comp]
    before = pair_v310.comps(scopes)
    after = pair_v310.comps([s - set(pair) for s in scopes])
    return len(after) > len(before)


def second_pair_candidates(factors: list[dict], core: list[int], comp: list[int]) -> list[dict]:
    variables = sorted(set().union(*(rscope(factors[i], core) for i in comp)) if comp else set())
    out = []
    for pair in itertools.combinations(variables, 2):
        if not pair_disconnects_component(factors, core, comp, pair):
            continue
        statuses = []
        component_sizes = []
        ok = True
        for vals in ((0,0),(0,1),(1,0),(1,1)):
            rr = restrict_factors(factors, {pair[0]: vals[0], pair[1]: vals[1]})
            if rr["status"] != "READY":
                statuses.append(rr["status"])
                component_sizes.append([])
                continue
            cs = componentize(rr["factors"], core)
            sizes = [len(c) for c in cs]
            component_sizes.append(sizes)
            if any(x > 2 for x in sizes):
                statuses.append("STRUCTURAL_GT2")
                ok = False
            else:
                statuses.append("STRUCTURAL_LE2")
        out.append({"pair": list(pair), "branch_statuses": statuses, "branch_component_sizes": component_sizes, "structural_ok": ok})
    return out


def first_pair_plan(factors: list[dict], core: list[int]) -> dict | None:
    gt = target_gt2_component(factors, core)
    if gt is None:
        if all(len(c) <= 2 for c in componentize(factors, core)):
            return {"status": "DIRECT_LE2", "first_pair": None, "branches": []}
        return None
    variables = sorted(set().union(*(rscope(factors[i], core) for i in gt)))
    for pair in itertools.combinations(variables, 2):
        if not pair_disconnects_component(factors, core, gt, pair):
            continue
        branch_plans = []
        pair_ok = True
        for vals in ((0,0),(0,1),(1,0),(1,1)):
            rr = restrict_factors(factors, {pair[0]: vals[0], pair[1]: vals[1]})
            if rr["status"] != "READY":
                branch_plans.append({"values": list(vals), "status": "EXACT_EMPTY", "second_pair": None})
                continue
            cs = componentize(rr["factors"], core)
            gt2 = [c for c in cs if len(c) > 2]
            if not gt2:
                branch_plans.append({"values": list(vals), "status": "LE2", "second_pair": None})
                continue
            if len(gt2) != 1 or len(gt2[0]) != 3:
                pair_ok = False
                branch_plans.append({"values": list(vals), "status": "OUT_OF_SCOPE_GT2_SHAPE", "second_pair": None})
                continue
            cands = second_pair_candidates(rr["factors"], core, gt2[0])
            good = [c for c in cands if c["structural_ok"]]
            if not good:
                pair_ok = False
                branch_plans.append({"values": list(vals), "status": "NO_ADMISSIBLE_SECOND_PAIR", "second_pair": None})
                continue
            branch_plans.append({
                "values": list(vals),
                "status": "GT2_WITH_SECOND_PAIR",
                "gt2_component": list(gt2[0]),
                "second_pair": list(good[0]["pair"]),
            })
        if pair_ok:
            return {"status": "FIRST_PAIR_READY", "first_pair": list(pair), "branches": branch_plans}
    return None


def discover_plan_from_factors(factors: list[dict], core: list[int]) -> dict | None:
    gt = target_gt2_component(factors, core)
    if gt is None:
        return None
    variables = sorted(set().union(*(rscope(factors[i], core) for i in gt)))
    for variable in variables:
        single_branches = []
        ok = True
        for value in (0, 1):
            rr = restrict_factors(factors, {variable: value})
            if rr["status"] != "READY":
                single_branches.append({"value": value, "status": "EXACT_EMPTY", "first_pair_plan": None})
                continue
            fp = first_pair_plan(rr["factors"], core)
            if fp is None:
                ok = False
                single_branches.append({"value": value, "status": "NO_FIXED_DEPTH_FIRST_PAIR_PLAN", "first_pair_plan": None})
            else:
                single_branches.append({"value": value, "status": "READY", "first_pair_plan": fp})
        if ok:
            return {
                "kind": "FIXED_DEPTH_1_2_2_SEPARATOR_PLAN",
                "single_variable": int(variable),
                "single_branches": single_branches,
                "maximum_logical_leaf_count": MAX_LOGICAL_LEAVES,
                "dynamic_recursion": False,
            }
    return None


def discover_plan(prep: dict) -> dict | None:
    return discover_plan_from_factors(seed_root_provenance(prep["conditioned"]), prep["core"])


def proposal_record(prep: dict, plan: dict) -> dict:
    body = {
        "kind": "UNIQUE_CORE_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO",
        "raw_object_sha256": sha(prep["canonical"]),
        "failed_variable": int(prep["ready"]["failed_variable"]),
        "common_core": list(prep["core"]),
        "unique_common_state": list(prep["state"]),
        "plan": plan,
        "maximum_logical_leaf_count": MAX_LOGICAL_LEAVES,
        "truth_authority": False,
        "proof_authority": False,
        "automatic_promotion": False,
    }
    body["proposal_sha256"] = sha(body)
    return body


def verify_proposal(prep: dict, plan: dict, proposal: dict) -> bool:
    body = dict(proposal)
    claimed = body.pop("proposal_sha256", None)
    return isinstance(claimed, str) and sha(body) == claimed and proposal == proposal_record(prep, plan)


def portfolio_prep(prep: dict, factors: list[dict]) -> dict:
    return {
        "ready": prep["ready"],
        "canonical": prep["canonical"],
        "core": prep["core"],
        "state": prep["state"],
        "conditioned": factors,
        "residual_components": componentize(factors, prep["core"]),
    }


def reconstruct_original(prep: dict, portfolio: dict, factors: list[dict], fixed: dict[int, int], transformed_assignment: dict[int, int]) -> dict:
    assignment = {int(k): int(v) for k, v in transformed_assignment.items()}
    cut = set(int(v) for v in prep["ready"]["cut"])
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
    for v, bit in fixed.items():
        assignment[int(v)] = int(bit)

    chosen = []
    for carrier in portfolio["carriers"]:
        key = tuple(int(assignment[v]) for v in carrier["boundary_scope"])
        witness = carrier["witness"].get(key)
        if witness is None:
            return {"ok": False, "reason": "BOUNDARY_TUPLE_MISSING"}
        rows = [witness] if len(carrier["factors"]) == 1 else list(witness)
        for factor, row in zip(carrier["factors"], rows):
            root_scope = [int(v) for v in factor.get("_root_origin_scope", factor["scope"])]
            root_row = tuple(int(x) for x in factor.get("_root_origin_witness", {}).get(tuple(row), tuple(row)))
            for v, bit in zip(root_scope, root_row):
                if v in assignment and assignment[v] != bit:
                    return {"ok": False, "reason": "ROOT_ROW_RECONSTRUCTION_CONFLICT", "factor_id": str(factor["id"]), "variable": v}
                assignment[v] = bit
            chosen.append({"factor_id": str(factor["id"]), "original_conditioned_row": list(root_row)})
    verified = guarded.verify_original_assignment(prep["canonical"], assignment)
    return {"ok": verified, "assignment": assignment, "chosen_rows": chosen, "reason": "ORIGINAL_RELATION_REPLAY" if verified else "ORIGINAL_RELATION_REPLAY_FAILED"}


def execute_leaf(prep: dict, factors: list[dict], fixed: dict[int, int], leaf_path: dict) -> dict:
    comps = componentize(factors, prep["core"])
    sizes = [len(c) for c in comps]
    if any(x > 2 for x in sizes):
        return {"status": "OPEN_FIXED_DEPTH_LEAF_GT2", "exact_sat": False, "exact_unsat": False, "leaf_path": leaf_path, "component_sizes": sizes}
    bp = portfolio_prep(prep, factors)
    portfolio = v36.build_portfolio(bp)
    if portfolio.get("status") == "EXACT_UNSAT_BY_EMPTY_RESIDUAL_PAIR_JOIN":
        return {"status": "EXACT_UNSAT_BY_FIXED_DEPTH_LEAF_PAIR_JOIN", "exact_sat": False, "exact_unsat": True, "leaf_path": leaf_path, "component_sizes": sizes}
    if portfolio.get("status") != "ADMIT_RESIDUAL_LE2_PORTFOLIO":
        return {"status": "OPEN_FIXED_DEPTH_LEAF_PORTFOLIO", "exact_sat": False, "exact_unsat": False, "leaf_path": leaf_path, "portfolio_status": portfolio.get("status")}
    transformed = canonicalize_raw(v36._transformed_raw(bp, portfolio))
    tcs = parent_support.constraint_components_after_cut(transformed, list(prep["ready"]["cut"]))
    handoff = guarded.run_guarded_elimination(transformed, list(prep["ready"]["cut"]), tcs)
    receipt = {
        "component_sizes": sizes,
        "portfolio_records": portfolio["metrics"]["residual_component_count"],
        "pair_join_count": portfolio["metrics"]["pair_join_count"],
        "pair_row_comparisons": portfolio["metrics"]["pair_row_comparisons"],
        "transformed_handoff_terminal": handoff.get("status"),
        "three_plus_join_chains_materialized": 0,
        "global_residual_cartesian_products_materialized": 0,
    }
    if handoff.get("status") == "EXACT_UNSAT_BY_COMPLETE_GUARDED_ELIMINATION":
        return {"status": "EXACT_UNSAT_BY_FIXED_DEPTH_LEAF_HANDOFF", "exact_sat": False, "exact_unsat": True, "leaf_path": leaf_path, "receipt": receipt}
    if handoff.get("status") != "ADMIT_EXACT_GUARDED_BOUNDED_OUTPUT_ELIMINATION":
        return {"status": "OPEN_FIXED_DEPTH_LEAF_HANDOFF", "exact_sat": False, "exact_unsat": False, "leaf_path": leaf_path, "receipt": receipt}
    transformed_assignment = {int(k): int(v) for k, v in handoff["witness"]["assignment"].items()}
    reconstruction = reconstruct_original(prep, portfolio, factors, fixed, transformed_assignment)
    receipt["original_witness_verified"] = bool(reconstruction["ok"])
    if not reconstruction["ok"]:
        return {"status": "OPEN_FIXED_DEPTH_ORIGINAL_WITNESS_REPLAY_FAILURE", "exact_sat": False, "exact_unsat": False, "leaf_path": leaf_path, "receipt": receipt, "reconstruction": reconstruction}
    return {
        "status": "ADMIT_EXACT_FIXED_DEPTH_LEAF_SAT",
        "exact_sat": True,
        "exact_unsat": False,
        "leaf_path": leaf_path,
        "receipt": receipt,
        "witness": {str(v): int(reconstruction["assignment"][v]) for v in sorted(reconstruction["assignment"])},
        "witness_verified": True,
        "reconstruction_rows": reconstruction["chosen_rows"],
    }


def execute_plan(prep: dict, plan: dict) -> dict:
    seeded = seed_root_provenance(prep["conditioned"])
    terminals = []
    single_var = int(plan["single_variable"])
    for sb in plan["single_branches"]:
        sval = int(sb["value"])
        fixed1 = {single_var: sval}
        rr1 = restrict_factors(seeded, fixed1)
        if rr1["status"] != "READY":
            terminals.append({"status": rr1["status"], "exact_sat": False, "exact_unsat": True, "coverage": 16, "leaf_path": {"single": [single_var, sval]}})
            continue
        fp = sb["first_pair_plan"]
        if fp is None:
            terminals.append({"status": "OPEN_FIXED_DEPTH_PLAN_DRIFT", "exact_sat": False, "exact_unsat": False, "coverage": 16})
            continue
        if fp["status"] == "DIRECT_LE2":
            leaf = execute_leaf(prep, rr1["factors"], fixed1, {"single": [single_var, sval], "first_pair": None})
            leaf["coverage"] = 16
            terminals.append(leaf)
            continue
        first_pair = tuple(int(x) for x in fp["first_pair"])
        branch_plan = {tuple(int(x) for x in b["values"]): b for b in fp["branches"]}
        for vals1 in ((0,0),(0,1),(1,0),(1,1)):
            bplan = branch_plan[vals1]
            fixed2 = {**fixed1, first_pair[0]: vals1[0], first_pair[1]: vals1[1]}
            rr2 = restrict_factors(rr1["factors"], {first_pair[0]: vals1[0], first_pair[1]: vals1[1]})
            path2 = {"single": [single_var, sval], "first_pair": [list(first_pair), list(vals1)]}
            if rr2["status"] != "READY":
                terminals.append({"status": rr2["status"], "exact_sat": False, "exact_unsat": True, "coverage": 4, "leaf_path": path2})
                continue
            second_pair = bplan.get("second_pair")
            if second_pair is None:
                leaf = execute_leaf(prep, rr2["factors"], fixed2, path2)
                leaf["coverage"] = 4
                terminals.append(leaf)
                continue
            second_pair_t = tuple(int(x) for x in second_pair)
            for vals2 in ((0,0),(0,1),(1,0),(1,1)):
                fixed3 = {**fixed2, second_pair_t[0]: vals2[0], second_pair_t[1]: vals2[1]}
                rr3 = restrict_factors(rr2["factors"], {second_pair_t[0]: vals2[0], second_pair_t[1]: vals2[1]})
                path3 = {**path2, "second_pair": [list(second_pair_t), list(vals2)]}
                if rr3["status"] != "READY":
                    terminals.append({"status": rr3["status"], "exact_sat": False, "exact_unsat": True, "coverage": 1, "leaf_path": path3})
                    continue
                leaf = execute_leaf(prep, rr3["factors"], fixed3, path3)
                leaf["coverage"] = 1
                terminals.append(leaf)

    covered = sum(int(x.get("coverage", 0)) for x in terminals)
    sat = next((x for x in terminals if x.get("exact_sat") and x.get("witness_verified")), None)
    all_unsat = covered == MAX_LOGICAL_LEAVES and all(x.get("exact_unsat") for x in terminals)
    receipt = {
        "selected_single_variable": single_var,
        "terminal_records_executed": len(terminals),
        "logical_leaf_equivalents_covered": covered,
        "maximum_logical_leaf_count": MAX_LOGICAL_LEAVES,
        "separator_depth": 3,
        "separator_sets_size_three_or_more": 0,
        "unbounded_recursive_calls": 0,
        "three_plus_join_chains_materialized": 0,
        "global_residual_cartesian_products_materialized": 0,
        "alternative_elimination_order_search": 0,
        "external_solver_calls": 0,
        "budget_raised": False,
        "conservative_uniform_envelope": "O(L^12)",
        "polynomial_degree_depends_on_relation_count": False,
    }
    if sat:
        return {"status": "ADMIT_EXACT_UNIQUE_CORE_RESIDUAL_FIXED_DEPTH_1_2_2_SEPARATOR_PORTFOLIO", "terminals": terminals, "receipt": receipt, "witness": sat["witness"], "witness_verified": True}
    if all_unsat:
        return {"status": "EXACT_UNSAT_BY_ALL_FIXED_DEPTH_1_2_2_LEAVES", "terminals": terminals, "receipt": receipt, "witness": None, "witness_verified": True}
    return {"status": "OPEN_FIXED_DEPTH_1_2_2_LEAF_NOT_FULLY_ADMITTED", "terminals": terminals, "receipt": receipt}


def build(raw: dict, proposal_override: dict | None = None) -> dict:
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return prep
    direct = pair_v310.pair_candidates(prep)
    if any(c["structural_ok"] for c in direct):
        return {"status": "OUT_OF_SCOPE_DIRECT_V3_10_PAIR_ALREADY_ADMISSIBLE", "direct_pair_candidates": direct}
    plan = discover_plan(prep)
    if plan is None:
        return {"status": "OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND", "logical_leaf_assignments_enumerated": 0, "unbounded_recursive_calls": 0}
    proposal = proposal_override or proposal_record(prep, plan)
    if not verify_proposal(prep, plan, proposal):
        return {"status": "REJECT_TAMPERED_PROVENANCE"}
    execution = execute_plan(prep, plan)
    return {**execution, "proposal": proposal, "plan": plan}


def explain(raw: dict) -> dict:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": ARTIFACT_ID, "status": "HALT_SOURCE_GUARD", "source_guard": guard, "scientific_firewall": firewall()}
    if any(k in raw for k in ("fixed_depth_plan_hint", "separator_hint", "trusted_plan")):
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": "TRUSTED_PLAN_OR_SEPARATOR_HINT_FORBIDDEN", "source_guard": guard, "scientific_firewall": firewall()}
    try:
        canonicalize_raw(raw)
    except RawBasisInputError as exc:
        return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": "REJECT_RAW_INPUT", "reason": str(exc), "source_guard": guard, "scientific_firewall": firewall()}
    carrier = build(raw)
    return {"artifact_id": ARTIFACT_ID, "authority": AUTHORITY, "status": carrier["status"], "carrier": carrier, "source_guard": guard, "scientific_firewall": firewall()}


def positive_k4_control() -> dict:
    return pair_v310.no_pair_k4_control()


def injected_hint_control() -> dict:
    raw = positive_k4_control()
    raw["fixed_depth_plan_hint"] = {"single_variable": 92, "trusted": True}
    return raw


def tampered_control() -> dict:
    raw = positive_k4_control()
    prep = v38._prepare(raw)
    if prep.get("status") != "READY":
        return prep
    plan = discover_plan(prep)
    if plan is None:
        return {"status": "FAIL_CONTROL_NO_PLAN"}
    proposal = proposal_record(prep, plan)
    proposal["plan"] = json.loads(json.dumps(proposal["plan"]))
    proposal["plan"]["single_variable"] = int(proposal["plan"]["single_variable"]) + 1
    return build(raw, proposal)


def depth_cap_unit_control() -> dict:
    # A pure structural K5 relation-overlap graph. Each of five relation nodes carries
    # the four incident edge variables. Removing one variable then two more cannot
    # reach the frozen 1->2->2 skeleton; this unit test is deliberately not raw-input reachability evidence.
    edge_var = {}
    nxt = 200
    for i in range(5):
        for j in range(i + 1, 5):
            edge_var[(i, j)] = nxt
            nxt += 1
    factors = []
    for i in range(5):
        scope = sorted(edge_var[tuple(sorted((i, j)))] for j in range(5) if j != i)
        rows = list(itertools.product((0, 1), repeat=len(scope)))
        factors.append({"id": f"unit_k5_{i}", "scope": scope, "rows": rows})
    seeded = seed_root_provenance(factors)
    plan = discover_plan_from_factors(seeded, [])
    return {
        "status": "OPEN_FIXED_DEPTH_1_2_2_SKELETON_NOT_FOUND" if plan is None else "FAIL_DEPTH_CAP_UNIT_CONTROL_UNEXPECTED_PLAN",
        "plan": plan,
        "factor_count": 5,
        "residual_variable_count": len(edge_var),
        "unit_test_only": True,
        "raw_reachability_authority": False,
        "unbounded_recursive_calls": 0,
    }


def main() -> None:
    positive = explain(positive_k4_control())
    out = {
        "artifact_id": ARTIFACT_ID,
        "authority": AUTHORITY,
        "positive_k4": positive,
        "depth_cap_unit": depth_cap_unit_control(),
        "hint": explain(injected_hint_control()),
        "tamper": tampered_control(),
        "scientific_firewall": firewall(),
    }
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
