from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict, deque
from pathlib import Path

import janus_trump_r50g25av_reachable_multi_defect_growth_witness as av
import janus_trump_r50g25at_tautology_hardened_runner as ath

GATE = "JANUS_TRUMP_R50G25AW_DEFECT_COMPONENT_DECOMPOSITION_COMPRESSION_DOOR_OR_COUNTEREXAMPLE"
PREREG_COMMIT = "0ae90542aea7198149c88cc1455e5553d473ea60"
PARENT_AV_SEALED_HEAD = "a69980c1076a8b6d1f81365a0ca74078e536cc1f"
PARENT_AV_RECEIPT = "7300ba3f105b53e3920ee601285e7e6d679f51c8"
PARENT_AV_META = "c7f953e47b40035eed0e4ded24c0b8847c771d54"
EXPECTED_FIRST_MULTI_HASH = "df779dc7d8a076d22ca970220fc82275f882861c85965857f6ac4a4799a17592"
EXPECTED_AV_OBSTRUCTION_HASH = "cfbe4a9b4d4fbe5ec09ad3aa1c1ad8fe633e358b4d8744c92890133b6fa8056b"
TAUTOLOGY_POLICY = "DETECT_AND_DROP_AS_ALWAYS_TRUE_BEFORE_AFFINE_GROUPING"

PASS = "DEFECT_COMPONENT_FACTORIZATION_WITHIN_L4_ON_FROZEN_REACHABLE_DOMAIN__UNIVERSAL_COVERAGE_OPEN"
OBSTRUCTION = "REACHABLE_DEFECT_COMPONENT_COST_EXCEEDS_L4"
CONTRACT_FAILURE = "FACTOR_GRAPH_OR_SEMANTIC_INDEPENDENCE_CONTRACT_FAILURE"
IMPLEMENTATION_FAILURE = "IMPLEMENTATION_OR_VERIFICATION_FAILURE"
UNKNOWN = "UNKNOWN_RESOURCE_LIMIT"


def constraint_supports(extraction):
    constraints = []
    for i, eq in enumerate(extraction["equations"]):
        vars_ = tuple(sorted(set(int(v) for v in eq["vars"])))
        constraints.append({
            "kind": "AFFINE",
            "index": int(i),
            "vars": vars_,
            "rhs": int(eq["rhs"]),
        })
    for i, clause in enumerate(extraction["defects"]):
        vars_ = tuple(sorted({abs(int(lit)) for lit in clause}))
        constraints.append({
            "kind": "DEFECT",
            "index": int(i),
            "vars": vars_,
            "width": len(clause),
            "clause": tuple(int(lit) for lit in clause),
        })
    return constraints


def factor_components(extraction):
    constraints = constraint_supports(extraction)
    by_var = defaultdict(list)
    for ci, c in enumerate(constraints):
        for v in c["vars"]:
            by_var[int(v)].append(ci)

    # Constraint graph adjacency induced only by shared variables. This is
    # exactly equivalent to connected components of the preregistered
    # bipartite constraint-variable factor graph.
    adj = [set() for _ in constraints]
    for v, members in by_var.items():
        for ci in members:
            adj[ci].update(members)
            adj[ci].discard(ci)

    seen = set()
    components = []
    for start in range(len(constraints)):
        if start in seen:
            continue
        q = deque([start])
        seen.add(start)
        members = []
        while q:
            ci = q.popleft()
            members.append(ci)
            for nxt in sorted(adj[ci]):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)

        eq_indices = []
        defect_indices = []
        variables = set()
        defect_widths = []
        for ci in members:
            c = constraints[ci]
            variables.update(c["vars"])
            if c["kind"] == "AFFINE":
                eq_indices.append(c["index"])
            else:
                defect_indices.append(c["index"])
                defect_widths.append(int(c["width"]))
        p = math.prod(defect_widths) if defect_widths else 1
        components.append({
            "constraint_count": len(members),
            "variable_count": len(variables),
            "variables": sorted(map(int, variables)),
            "affine_equation_count": len(eq_indices),
            "affine_equation_indices": sorted(eq_indices),
            "defect_count": len(defect_indices),
            "defect_indices": sorted(defect_indices),
            "defect_widths": defect_widths,
            "P_j": int(p),
        })

    # Independent verifier for the semantic factorization contract.
    assigned_eq = sorted(i for comp in components for i in comp["affine_equation_indices"])
    assigned_def = sorted(i for comp in components for i in comp["defect_indices"])
    expected_eq = list(range(len(extraction["equations"])))
    expected_def = list(range(len(extraction["defects"])))

    cross_intersections = []
    for i in range(len(components)):
        vi = set(components[i]["variables"])
        for j in range(i + 1, len(components)):
            inter = sorted(vi.intersection(components[j]["variables"]))
            if inter:
                cross_intersections.append({"a": i, "b": j, "variables": inter})

    partition_pass = assigned_eq == expected_eq and assigned_def == expected_def
    independence_pass = len(cross_intersections) == 0
    return {
        "components": components,
        "component_count_total": len(components),
        "component_count_with_defects": sum(1 for c in components if c["defect_count"] > 0),
        "factorization_partition_pass": bool(partition_pass),
        "semantic_independence_pass": bool(independence_pass),
        "cross_component_variable_intersection_count": len(cross_intersections),
        "cross_component_variable_intersections": cross_intersections,
    }


def audit_residual(root, meta, replay):
    residual = av.canonical(replay["state"])
    effective, tautologies = av.effective_canonical(residual)
    extraction = ath.hardened_extract(residual)
    failures = []

    if extraction.get("explicit_tautology_policy") != TAUTOLOGY_POLICY or not extraction.get("tautology_check_pass"):
        failures.append({"kind": "TAUTOLOGY_POLICY_DRIFT"})
    if not extraction.get("partition_pass") or extraction.get("replay_failures"):
        failures.append({
            "kind": "AFFINE_EXTRACTION_OR_REPLAY_FAILURE",
            "partition_pass": bool(extraction.get("partition_pass")),
            "replay_failures": extraction.get("replay_failures", []),
        })

    factor = factor_components(extraction)
    if not factor["factorization_partition_pass"] or not factor["semantic_independence_pass"]:
        failures.append({
            "kind": CONTRACT_FAILURE,
            "partition_pass": factor["factorization_partition_pass"],
            "independence_pass": factor["semantic_independence_pass"],
            "cross_component_variable_intersection_count": factor["cross_component_variable_intersection_count"],
        })

    L = sum(len(c) for c in effective)
    defect_components = [c for c in factor["components"] if c["defect_count"] > 0]
    B_component = sum(int(c["P_j"]) for c in defect_components)
    max_P = max((int(c["P_j"]) for c in defect_components), default=0)
    budget = int(L) ** 4
    slack = int(budget - B_component)

    row = {
        "meta": meta,
        "root_hash": av.formula_hash(root),
        "root_CLV": list(av.clv(root)),
        "policy_kind": "RESIDUAL",
        "residual_hash": av.formula_hash(residual),
        "residual_CLV": list(av.clv(residual)),
        "route_length": len(replay.get("route", [])),
        "tautology_count": len(tautologies),
        "extraction": {
            "affine_clause_count": int(extraction["affine_clause_count"]),
            "recognized_equation_count": int(extraction["recognized_equation_count"]),
            "defect_clause_count": int(extraction["defect_clause_count"]),
            "partition_pass": bool(extraction["partition_pass"]),
            "replay_failure_count": len(extraction.get("replay_failures", [])),
            "explicit_tautology_policy": extraction.get("explicit_tautology_policy"),
        },
        "factorization": factor,
        "ledger": {
            "L": int(L),
            "L4_budget": int(budget),
            "B_component": int(B_component),
            "maximum_component_P_j": int(max_P),
            "budget_slack": int(slack),
            "component_cost_formula": "sum_j product_{defect in component j}(defect width)",
        },
        "failure_count": len(failures),
        "failures": failures,
    }
    if failures:
        row["classification"] = IMPLEMENTATION_FAILURE
    elif B_component > budget:
        row["classification"] = "DEFECT_COMPONENT_COST_EXCEEDS_L4"
    else:
        row["classification"] = "COMPONENT_FACTORIZATION_WITHIN_L4"
    return row


def audit_candidate(index: int):
    candidates = list(av.frozen_candidates())
    if len(candidates) != 9:
        raise AssertionError(("AV_FROZEN_GENERATOR_DRIFT", len(candidates)))
    if index < 0 or index >= len(candidates):
        raise AssertionError(("CANDIDATE_INDEX_OUT_OF_RANGE", index))
    root, meta = candidates[index]
    root = av.canonical(root)
    replay = av.asmod.y.policy_replay(root, av.asmod.r50g25g._chain())
    kind = str(replay.get("kind"))
    if kind in {"TERMINAL", "AFFINE"}:
        return {
            "candidate_index": index,
            "row": {
                "meta": meta,
                "root_hash": av.formula_hash(root),
                "root_CLV": list(av.clv(root)),
                "policy_kind": kind,
                "classification": "NON_FALSIFYING_CHEAP_POLICY_ABSORPTION",
                "route_length": len(replay.get("route", [])),
                "failure_count": 0,
                "failures": [],
            },
        }
    if kind != "RESIDUAL":
        return {
            "candidate_index": index,
            "row": {
                "meta": meta,
                "root_hash": av.formula_hash(root),
                "root_CLV": list(av.clv(root)),
                "policy_kind": kind,
                "classification": IMPLEMENTATION_FAILURE,
                "failure_count": 1,
                "failures": [{"kind": "POLICY_CONTRACT_DRIFT", "observed_kind": kind}],
            },
        }
    return {"candidate_index": index, "row": audit_residual(root, meta, replay)}


def aggregate(input_dir: Path):
    results = []
    for i in range(9):
        p = input_dir / f"candidate-{i}.json"
        if not p.exists():
            raise AssertionError(("MISSING_CANDIDATE_ARTIFACT", i, str(p)))
        x = json.loads(p.read_text())
        if int(x["candidate_index"]) != i:
            raise AssertionError(("CANDIDATE_ORDER_DRIFT", i, x.get("candidate_index")))
        results.append(x)

    rows = []
    failures = []
    first_obstruction = None
    max_B = 0
    max_P = 0
    min_slack = None
    residual_count = 0
    first_multi_seen = False
    av_obstruction_seen = False

    for x in results:
        row = x["row"]
        rows.append(row)
        failures.extend(row.get("failures", []))
        if row.get("policy_kind") != "RESIDUAL":
            continue
        residual_count += 1
        rh = row["residual_hash"]
        if rh == EXPECTED_FIRST_MULTI_HASH:
            first_multi_seen = True
        if rh == EXPECTED_AV_OBSTRUCTION_HASH:
            av_obstruction_seen = True
        ledger = row["ledger"]
        max_B = max(max_B, int(ledger["B_component"]))
        max_P = max(max_P, int(ledger["maximum_component_P_j"]))
        min_slack = int(ledger["budget_slack"]) if min_slack is None else min(min_slack, int(ledger["budget_slack"]))
        if row["classification"] == "DEFECT_COMPONENT_COST_EXCEEDS_L4" and first_obstruction is None:
            first_obstruction = {
                "class": "DEFECT_COMPONENT_COST_EXCEEDS_L4",
                "candidate_index": int(x["candidate_index"]),
                "meta": row["meta"],
                "root_hash": row["root_hash"],
                "root_CLV": row["root_CLV"],
                "residual_hash": row["residual_hash"],
                "residual_CLV": row["residual_CLV"],
                "route_length": row["route_length"],
                "component_count_total": row["factorization"]["component_count_total"],
                "component_count_with_defects": row["factorization"]["component_count_with_defects"],
                "components": row["factorization"]["components"],
                "ledger": row["ledger"],
            }
            break

    if not first_multi_seen:
        failures.append({"kind": "AV_FIRST_MULTI_CONTROL_NOT_REPLAYED", "expected_hash": EXPECTED_FIRST_MULTI_HASH})
    if not av_obstruction_seen:
        failures.append({"kind": "AV_OBSTRUCTION_CONTROL_NOT_REPLAYED", "expected_hash": EXPECTED_AV_OBSTRUCTION_HASH})

    if failures:
        verdict = IMPLEMENTATION_FAILURE
    elif first_obstruction is not None:
        verdict = OBSTRUCTION
    else:
        verdict = PASS

    return {
        "gate": GATE,
        "status": "SCIENTIFIC_RESULT",
        "preregistration_commit": PREREG_COMMIT,
        "parent_AV_sealed_head": PARENT_AV_SEALED_HEAD,
        "parent_AV_receipt": PARENT_AV_RECEIPT,
        "parent_AV_meta": PARENT_AV_META,
        "verdict": verdict,
        "candidate_count_frozen": 9,
        "candidate_count_physically_computed": len(results),
        "candidate_count_scientifically_audited_to_stop": len(rows),
        "residual_count_audited_to_stop": residual_count,
        "first_component_obstruction": first_obstruction,
        "maximum_B_component_observed": int(max_B),
        "maximum_component_P_j_observed": int(max_P),
        "minimum_budget_slack_observed": min_slack,
        "AV_first_multi_control_seen": first_multi_seen,
        "AV_obstruction_control_seen": av_obstruction_seen,
        "failure_count": len(failures),
        "failures": failures,
        "rows": rows,
        "frozen_contract": {
            "graph": "undirected bipartite constraint-variable factor graph over affine equations plus defect clauses",
            "component_cost": "B_component=sum_j product_i |D_i| within component j",
            "budget": "L^4",
            "recursive_separator_or_treewidth_rescue_inside_AW": false,
        },
        "truth_oracle": {
            "used_for_generation": False,
            "used_for_selection": False,
            "used_for_verdict": False,
        },
        "scientific_scope": {
            "component_factorization_on_frozen_domain": "FALSIFIED" if first_obstruction is not None else "SURVIVES",
            "recursive_separator_or_treewidth_compression": "NOT_TESTED_REQUIRES_NEW_PREREGISTRATION",
            "solver_correctness": "NOT_FALSIFIED_BY_AW",
            "arbitrary_CNF_coverage": "OPEN",
            "general_SAT_polynomial_time": "NOT_PROVED",
        },
        "recommended_next_gate": "R50G25AX_WITHIN_COMPONENT_SEPARATOR_OR_AFFINE_QUOTIENT_COMPRESSION_DOOR" if first_obstruction is not None else "R50G25AX_COMPONENT_FACTORIZATION_GENERALIZATION_OR_COUNTEREXAMPLE",
        "firewall": {
            "P_VS_NP": "OPEN",
            "SAT_IN_P": "NOT_PROVED",
            "TRUMP_finished": False,
        },
    }


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)
    p_c = sub.add_parser("candidate")
    p_c.add_argument("--index", type=int, required=True)
    p_c.add_argument("--out", type=Path, required=True)
    p_a = sub.add_parser("aggregate")
    p_a.add_argument("--input-dir", type=Path, required=True)
    p_a.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    if args.mode == "candidate":
        result = audit_candidate(args.index)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        row = result["row"]
        print(json.dumps({
            "candidate_index": args.index,
            "classification": row.get("classification"),
            "policy_kind": row.get("policy_kind"),
            "residual_hash": row.get("residual_hash"),
            "component_count": None if row.get("factorization") is None else row["factorization"]["component_count_total"],
            "B_component": None if row.get("ledger") is None else row["ledger"]["B_component"],
            "budget_slack": None if row.get("ledger") is None else row["ledger"]["budget_slack"],
            "failure_count": row.get("failure_count", 0),
        }, sort_keys=True))
        raise SystemExit(0 if row.get("failure_count", 0) == 0 else 1)

    result = aggregate(args.input_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": result["verdict"],
        "candidate_count_audited": result["candidate_count_scientifically_audited_to_stop"],
        "residual_count": result["residual_count_audited_to_stop"],
        "maximum_B_component": result["maximum_B_component_observed"],
        "minimum_budget_slack": result["minimum_budget_slack_observed"],
        "failure_count": result["failure_count"],
    }, sort_keys=True))
    raise SystemExit(0 if result["failure_count"] == 0 else 1)


if __name__ == "__main__":
    main()
