#!/usr/bin/env python3
"""R30 exposed control: consuming fused existential restriction.

R29 showed that the frozen R27 replay reaches its node cap while constructing
the second Shannon restriction of one already-large factor.  R30 changes only
the implementation of exact existential abstraction.  It computes low/high in
one bottom-up pass and releases x-dependent source nodes after their output pair
has been built, while protecting every node reachable from retained factors.

The output is still a fully materialized R18 AND/OR DAG.  There is no lazy
EXISTS node, SAT solver, assignment enumeration, semantic equivalence oracle,
or external spill in the candidate lane.  W05 truth is inspected only if the
candidate reaches a bridge-only terminal interface.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import itertools
import json
import random
import time
from pathlib import Path

import janus_trump_r18_shannon_hashcons_interface_dag_discovery as r18
import janus_trump_r19_fresh_unseen_dag_holdout as r19
import janus_trump_r27_local_bucket_factored_shannon_elimination_discovery as r27


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PREREG_PATH = (
    REPO
    / "research"
    / "JANUS_TRUMP_R30_CONSUMING_FUSED_EXISTENTIAL_RESTRICTION_CONTROL_PREREGISTRATION_2026-09-02.json"
)
WORLD_ID = "R19-W05"
EXPECTED_FRAME_SHA = "cd8e7168819401fc2510f351b0c7d319fc9cacfa400b181cf6e91cecd1288384"
EXPECTED_R27_BLOB = "ff1139a4da7e9eaf43945995db95a6d22fb45dbe"
EXPECTED_R18_BLOB = "afa95321ec6edbb33bef222d8ee7234fe631a599"
EXPECTED_R29_RESULT_BLOB = "7c88481aaf4b308b6bfd12004f9e257d4b495315"


class FusedResourceOpen(RuntimeError):
    def __init__(self, reason, telemetry):
        super().__init__(reason)
        self.reason = reason
        self.telemetry = telemetry


def load_prereg():
    data = json.loads(PREREG_PATH.read_text(encoding="utf-8"))
    assert data["status"] == "FROZEN_BEFORE_R30_IMPLEMENTATION_AND_EXECUTION"
    assert data["parent_R29_sealed_result_commit"] == "1f1ca71c4a7a23dcca463fde5e3787772bbeac8e"
    assert data["frozen_lineage"]["R27_git_blob_sha"] == EXPECTED_R27_BLOB
    assert data["frozen_lineage"]["R18_git_blob_sha"] == EXPECTED_R18_BLOB
    assert data["frozen_lineage"]["R29_result_blob_sha"] == EXPECTED_R29_RESULT_BLOB
    assert data["resource_envelope"]["MAX_ACTIVE_DAG_NODES"] == r18.MAX_NODES
    assert data["resource_envelope"]["WALL_SECONDS"] == r18.WALL_SECONDS
    assert data["resource_envelope"]["cap_increase_for_candidate_forbidden"] is True
    assert data["new_operator_contract"]["lazy_EXISTS_node_forbidden"] is True
    assert data["theorem_firewall"]["P_VS_NP"] == "OPEN"
    return data


def reachable_nodes(dag, root):
    seen = set()
    stack = [int(root)]
    while stack:
        nid = stack.pop()
        if nid in seen:
            continue
        if nid not in dag.nodes:
            raise AssertionError(f"R30_REACHABILITY_MISSING_NODE:{nid}")
        seen.add(nid)
        node = dag.nodes[nid]
        if node[0] in ("AND", "OR"):
            stack.extend(node[1])
    return seen


def reachable_from_roots(dag, roots):
    seen = set()
    stack = [int(root) for root in roots]
    while stack:
        nid = stack.pop()
        if nid in seen:
            continue
        if nid not in dag.nodes:
            raise AssertionError(f"R30_PROTECTED_ROOT_MISSING_NODE:{nid}")
        seen.add(nid)
        node = dag.nodes[nid]
        if node[0] in ("AND", "OR"):
            stack.extend(node[1])
    return seen


def delete_consumed_source_node(dag, nid, record, protected):
    nid = int(nid)
    if nid in protected:
        raise AssertionError(f"R30_ATTEMPTED_PROTECTED_NODE_DELETE:{nid}")
    if nid in (0, 1):
        raise AssertionError(f"R30_ATTEMPTED_CONSTANT_DELETE:{nid}")
    if dag.nodes.get(nid) != record:
        raise AssertionError(f"R30_SOURCE_RECORD_DRIFT:{nid}")
    if dag.intern.get(record) == nid:
        del dag.intern[record]
    del dag.nodes[nid]
    del dag.support[nid]


def consume_exists_fused(dag, root, var, protected_roots):
    """Consume x-dependent source nodes and return exact fully materialized exists x."""
    root = int(root)
    var = int(var)
    bit = 1 << (var - 1)
    source = reachable_nodes(dag, root)
    protected = reachable_from_roots(dag, protected_roots)
    protected_overlap = source & protected
    x_dependent = {nid for nid in source if dag.support[nid] & bit}
    forbidden_overlap = x_dependent & protected
    if forbidden_overlap:
        raise AssertionError(
            "R30_X_DEPENDENT_SOURCE_REACHABLE_FROM_RETAINED_FACTOR:"
            + str(min(forbidden_overlap))
        )

    parent_remaining = {nid: 0 for nid in source}
    edge_count = 0
    for nid in source:
        node = dag.nodes[nid]
        if node[0] in ("AND", "OR"):
            for child in node[1]:
                if child not in parent_remaining:
                    raise AssertionError(f"R30_SOURCE_NOT_CLOSED:{child}")
                parent_remaining[child] += 1
                edge_count += 1

    created0 = dag.budget.nodes_created_total
    hits0 = dag.hashcons_hits
    active0 = len(dag.nodes)
    telemetry = {
        "status": "RUNNING",
        "quantified_var": var,
        "source_reachable_nodes": len(source),
        "source_x_dependent_nodes": len(x_dependent),
        "protected_nodes": len(protected),
        "source_protected_overlap_nodes": len(protected_overlap),
        "source_edges": edge_count,
        "source_index_entries": len(source),
        "parent_counter_entries": len(parent_remaining),
        "peak_pair_memo_entries": 0,
        "peak_aux_metadata_entries_lower_bound": (
            len(source) + len(protected) + len(parent_remaining)
        ),
        "source_nodes_released": 0,
        "fused_node_visits": 0,
        "active_DAG_nodes_before": active0,
        "peak_active_DAG_nodes": active0,
        "low_reachable_nodes": None,
        "high_reachable_nodes": None,
        "branch_intersection_nodes": None,
        "branch_union_nodes": None,
        "output_reachable_nodes": None,
    }
    pairs = {}

    try:
        for nid in sorted(source):
            telemetry["fused_node_visits"] += 1
            if (telemetry["fused_node_visits"] & 4095) == 0:
                dag.budget.check()
            if nid not in dag.nodes:
                raise AssertionError(f"R30_SOURCE_NODE_RELEASED_TOO_EARLY:{nid}")
            record = dag.nodes[nid]
            depends = bool(dag.support[nid] & bit)

            if not depends:
                low = high = nid
            elif record[0] == "LIT":
                lit = int(record[1])
                if abs(lit) != var:
                    raise AssertionError(f"R30_LITERAL_SUPPORT_DRIFT:{nid}")
                delete_consumed_source_node(dag, nid, record, protected)
                telemetry["source_nodes_released"] += 1
                low = 0 if lit > 0 else 1
                high = 1 if lit > 0 else 0
            elif record[0] in ("AND", "OR"):
                children = tuple(record[1])
                try:
                    low_children = tuple(pairs[c][0] for c in children)
                    high_children = tuple(pairs[c][1] for c in children)
                except KeyError as exc:
                    raise AssertionError(f"R30_PAIR_MISSING_FOR_CHILD:{exc.args[0]}") from exc
                delete_consumed_source_node(dag, nid, record, protected)
                telemetry["source_nodes_released"] += 1
                low = dag.mk(record[0], low_children)
                telemetry["peak_active_DAG_nodes"] = max(
                    telemetry["peak_active_DAG_nodes"], len(dag.nodes)
                )
                high = dag.mk(record[0], high_children)
                telemetry["peak_active_DAG_nodes"] = max(
                    telemetry["peak_active_DAG_nodes"], len(dag.nodes)
                )
            else:
                raise AssertionError(f"R30_UNEXPECTED_DEPENDENT_NODE:{record[0]}")

            pairs[nid] = (int(low), int(high))
            telemetry["peak_pair_memo_entries"] = max(
                telemetry["peak_pair_memo_entries"], len(pairs)
            )
            telemetry["peak_aux_metadata_entries_lower_bound"] = max(
                telemetry["peak_aux_metadata_entries_lower_bound"],
                len(source) + len(protected) + len(parent_remaining) + len(pairs),
            )

            if record[0] in ("AND", "OR"):
                for child in record[1]:
                    parent_remaining[child] -= 1
                    if parent_remaining[child] < 0:
                        raise AssertionError(f"R30_PARENT_COUNTER_NEGATIVE:{child}")
                    if parent_remaining[child] == 0:
                        parent_remaining.pop(child)
                        if child != root:
                            pairs.pop(child, None)

        if root not in pairs:
            raise AssertionError("R30_ROOT_PAIR_MISSING")
        low, high = pairs[root]
        low_nodes = reachable_nodes(dag, low)
        high_nodes = reachable_nodes(dag, high)
        output = dag.OR(low, high)
        telemetry["peak_active_DAG_nodes"] = max(
            telemetry["peak_active_DAG_nodes"], len(dag.nodes)
        )
        if dag.support[output] & bit:
            raise AssertionError("R30_QUANTIFIED_OUTPUT_RETAINS_VARIABLE")
        missing_protected = protected - set(dag.nodes)
        if missing_protected:
            raise AssertionError(
                "R30_PROTECTED_NODE_MISSING_AFTER_TRANSFORM:"
                + str(min(missing_protected))
            )
        output_nodes = reachable_nodes(dag, output)
        telemetry.update(
            {
                "status": "COMPLETE",
                "active_DAG_nodes_after": len(dag.nodes),
                "fused_nodes_created": dag.budget.nodes_created_total - created0,
                "fused_hashcons_hits": dag.hashcons_hits - hits0,
                "low_reachable_nodes": len(low_nodes),
                "high_reachable_nodes": len(high_nodes),
                "branch_intersection_nodes": len(low_nodes & high_nodes),
                "branch_union_nodes": len(low_nodes | high_nodes),
                "output_reachable_nodes": len(output_nodes),
            }
        )
        return int(output), telemetry
    except r18.ResourceLimit as exc:
        telemetry["peak_active_DAG_nodes"] = max(
            telemetry["peak_active_DAG_nodes"], len(dag.nodes)
        )
        telemetry.update(
            {
                "status": "OPEN_RESOURCE_LIMIT",
                "reason": exc.reason,
                "active_DAG_nodes_at_open": len(dag.nodes),
                "fused_nodes_created_before_open": (
                    dag.budget.nodes_created_total - created0
                ),
                "fused_hashcons_hits_before_open": dag.hashcons_hits - hits0,
            }
        )
        raise FusedResourceOpen(exc.reason, telemetry) from exc


def compile_fused_factored(frame, bridge):
    started = time.monotonic()
    budget = r18.Budget(deadline=started + r18.WALL_SECONDS)
    dag = r18.Dag(budget)
    trajectory = []
    partial = None
    phase = "INITIAL_FACTORS"
    max_live = len(dag.nodes)
    max_pair_memo = 0
    max_parent_counters = 0
    total_source_released = 0
    max_var = max({abs(int(lit)) for clause in frame for lit in clause}, default=0)
    try:
        factors = r27.compile_initial_factors(dag, frame)
        max_live = max(max_live, len(dag.nodes), dag.max_nodes_seen)
        order = tuple(r18.elimination_order(frame, bridge))
        if len(order) != len(set(order)):
            raise AssertionError("R18_ORDER_DUPLICATE")

        for step, var in enumerate(order, start=1):
            bit = 1 << (int(var) - 1)
            before_factors = len(factors)
            before_live = len(dag.nodes)
            created0 = budget.nodes_created_total
            hits0 = dag.hashcons_hits
            bucket = tuple(root for root in factors if dag.support[root] & bit)
            rest = tuple(root for root in factors if not (dag.support[root] & bit))
            bucket_union = 0
            for root in bucket:
                bucket_union |= dag.support[root]
            partial = {
                "step": step,
                "quantified_var": int(var),
                "factor_count_before": before_factors,
                "bucket_factor_count": len(bucket),
                "bucket_union_support_size": bucket_union.bit_count(),
                "before_live_nodes": before_live,
                "phase": "BUCKET_SELECT",
                "fused": None,
            }

            if bucket:
                phase = "LOCAL_AND"
                partial["phase"] = phase
                local_root = bucket[0] if len(bucket) == 1 else dag.AND(*bucket)
                local_reachable = len(reachable_nodes(dag, local_root))
                phase = "CONSUME_EXISTS_FUSED"
                partial["phase"] = phase
                quantified_root, fused = consume_exists_fused(
                    dag, local_root, int(var), rest
                )
                partial["fused"] = fused
                max_pair_memo = max(max_pair_memo, fused["peak_pair_memo_entries"])
                max_parent_counters = max(
                    max_parent_counters, fused["parent_counter_entries"]
                )
                total_source_released += fused["source_nodes_released"]
                factors = r27.normalize_factors(rest + (quantified_root,))
                pre_gc = len(dag.nodes)
                phase = "MULTI_ROOT_GC"
                partial["phase"] = phase
                removed = r27.multi_root_gc(dag, factors)
                after_live = len(dag.nodes)
            else:
                local_reachable = 0
                fused = None
                pre_gc = len(dag.nodes)
                removed = 0
                after_live = len(dag.nodes)

            max_live = max(max_live, pre_gc, after_live, dag.max_nodes_seen)
            remaining = sum(
                1
                for later_var in order[step:]
                if any(
                    dag.support[root] & (1 << (later_var - 1))
                    for root in factors
                )
            )
            trajectory.append(
                {
                    "step": step,
                    "quantified_var": int(var),
                    "factor_count_before": before_factors,
                    "bucket_factor_count": len(bucket),
                    "bucket_union_support_size": bucket_union.bit_count(),
                    "local_AND_reachable_nodes": local_reachable,
                    "factor_count_after": len(factors),
                    "before_live_nodes": before_live,
                    "pre_gc_live_nodes": pre_gc,
                    "after_gc_live_nodes": after_live,
                    "new_nodes_created_step": budget.nodes_created_total - created0,
                    "hashcons_hits_step": dag.hashcons_hits - hits0,
                    "gc_removed_nodes": removed,
                    "remaining_internal_variables_with_support": remaining,
                    "fused": fused,
                }
            )
            partial = None
            phase = "BETWEEN_STEPS"

        bridge_set = {int(var) for var in bridge}
        supports = [r27.factor_support_vars(dag, root, max_var) for root in factors]
        bad = sorted({var for support in supports for var in support if var not in bridge_set})
        if bad:
            return {
                "status": "FAIL_INTEGRITY",
                "reason": "FINAL_FACTOR_SUPPORT_NOT_BRIDGE_ONLY",
                "bad_support": bad,
                "trajectory": trajectory,
            }, None
        return {
            "status": "COMPLETE_FACTORED_BRIDGE_INTERFACE",
            "elapsed_seconds": time.monotonic() - started,
            "elimination_order": list(order),
            "completed_quantification_steps": len(trajectory),
            "initial_clause_count": len(frame),
            "final_factor_count": len(factors),
            "final_factor_roots": list(factors),
            "final_factor_supports": [list(support) for support in supports],
            "final_live_nodes": len(dag.nodes),
            "maximum_live_nodes": max(max_live, dag.max_nodes_seen),
            "nodes_created_total": budget.nodes_created_total,
            "hashcons_hits": dag.hashcons_hits,
            "gc_calls": dag.gc_calls,
            "gc_removed_total": dag.gc_removed_total,
            "maximum_pair_memo_entries": max_pair_memo,
            "maximum_parent_counter_entries": max_parent_counters,
            "total_source_nodes_released": total_source_released,
            "trajectory": trajectory,
        }, {"dag": dag, "roots": factors}
    except FusedResourceOpen as exc:
        if partial is not None:
            partial["phase"] = "CONSUME_EXISTS_FUSED"
            partial["fused"] = exc.telemetry
        return {
            "status": "OPEN_RESOURCE_LIMIT",
            "reason": exc.reason,
            "phase_at_open": "CONSUME_EXISTS_FUSED",
            "elapsed_seconds": time.monotonic() - started,
            "completed_quantification_steps": len(trajectory),
            "active_nodes_at_open": len(dag.nodes),
            "maximum_live_nodes": max(max_live, dag.max_nodes_seen),
            "nodes_created_total": budget.nodes_created_total,
            "hashcons_hits": dag.hashcons_hits,
            "gc_calls": dag.gc_calls,
            "gc_removed_total": dag.gc_removed_total,
            "partial_open_step": partial,
            "trajectory": trajectory,
        }, None
    except r18.ResourceLimit as exc:
        if partial is not None:
            partial["phase"] = phase
        return {
            "status": "OPEN_RESOURCE_LIMIT",
            "reason": exc.reason,
            "phase_at_open": phase,
            "elapsed_seconds": time.monotonic() - started,
            "completed_quantification_steps": len(trajectory),
            "active_nodes_at_open": len(dag.nodes),
            "maximum_live_nodes": max(max_live, dag.max_nodes_seen),
            "nodes_created_total": budget.nodes_created_total,
            "hashcons_hits": dag.hashcons_hits,
            "gc_calls": dag.gc_calls,
            "gc_removed_total": dag.gc_removed_total,
            "partial_open_step": partial,
            "trajectory": trajectory,
        }, None
    except AssertionError as exc:
        return {
            "status": "FAIL_INTEGRITY",
            "reason": str(exc),
            "phase_at_failure": phase,
            "elapsed_seconds": time.monotonic() - started,
            "partial_step": partial,
            "trajectory": trajectory,
        }, None


def candidate_firewall():
    source = "\n".join(
        inspect.getsource(fn)
        for fn in (
            reachable_nodes,
            reachable_from_roots,
            delete_consumed_source_node,
            consume_exists_fused,
            compile_fused_factored,
        )
    )
    forbidden = [
        "Solver(",
        ".solve(",
        ".evaluate(",
        ".restrict(",
        "Dag.exists",
        "range(1 <<",
        "allowed_masks",
        "truth_table",
        "dpll(",
        "resolve_on(",
        "pickle",
        "sqlite",
        "subprocess",
        "requests.",
    ]
    hits = [token for token in forbidden if token in source]
    return {"pass": not hits, "forbidden_hits": hits}


def tiny_factor_identity_control():
    frame = ((1, 2), (-1, 3), (4,))
    bridge = (2, 3, 4)
    candidate, live = compile_fused_factored(frame, bridge)
    if candidate.get("status") != "COMPLETE_FACTORED_BRIDGE_INTERFACE":
        return {"pass": False, "reason": candidate.get("reason")}
    got = r27.factor_set_allowed(live, bridge)["allowed_masks"]
    return {"pass": got == [5, 6, 7], "allowed_masks": got}


def tiny_protected_shared_subgraph_control():
    budget = r18.Budget(deadline=time.monotonic() + 10.0)
    dag = r18.Dag(budget)
    shared = dag.OR(dag.lit(2), dag.lit(3))
    root = dag.AND(shared, dag.OR(dag.lit(1), dag.lit(2)))
    protected_before = {
        nid: (dag.nodes[nid], dag.support[nid])
        for nid in reachable_nodes(dag, shared)
    }
    output, telemetry = consume_exists_fused(dag, root, 1, (shared,))
    protected_after = {
        nid: (dag.nodes[nid], dag.support[nid])
        for nid in protected_before
        if nid in dag.nodes
    }
    assignments = (
        {2: False, 3: False},
        {2: True, 3: False},
        {2: False, 3: True},
        {2: True, 3: True},
    )
    exact = all(
        dag.evaluate(output, assignment) == dag.evaluate(shared, assignment)
        for assignment in assignments
    )
    passed = protected_before == protected_after and exact
    return {
        "pass": passed,
        "protected_nodes_unchanged": protected_before == protected_after,
        "semantic_identity": exact,
        "telemetry": telemetry,
    }


def deterministic_small_operator_equivalence_suite():
    rng = random.Random(30052)
    cases = 128
    checked_assignments = 0
    try:
        for case in range(cases):
            variable_count = 5
            var = rng.randint(1, variable_count)
            frame = []
            for _ in range(rng.randint(1, 9)):
                variables = rng.sample(
                    range(1, variable_count + 1), rng.randint(1, 3)
                )
                frame.append(
                    tuple(value if rng.getrandbits(1) else -value for value in variables)
                )
            remaining = [
                value for value in range(1, variable_count + 1) if value != var
            ]
            first, last = remaining[0], remaining[-1]

            old_budget = r18.Budget(deadline=time.monotonic() + 10.0)
            old_dag = r18.Dag(old_budget)
            old_protected = old_dag.OR(old_dag.lit(first), old_dag.lit(-last))
            old_root = old_dag.AND(r18.compile_cnf(old_dag, frame), old_protected)
            old_output, _memo = old_dag.exists(old_root, var)

            new_budget = r18.Budget(deadline=time.monotonic() + 10.0)
            new_dag = r18.Dag(new_budget)
            new_protected = new_dag.OR(new_dag.lit(first), new_dag.lit(-last))
            new_root = new_dag.AND(r18.compile_cnf(new_dag, frame), new_protected)
            new_output, _telemetry = consume_exists_fused(
                new_dag, new_root, var, (new_protected,)
            )

            for values in itertools.product((False, True), repeat=len(remaining)):
                assignment = dict(zip(remaining, values))
                checked_assignments += 1
                if old_dag.evaluate(old_output, assignment) != new_dag.evaluate(
                    new_output, assignment
                ):
                    return {
                        "pass": False,
                        "seed": 30052,
                        "case": case,
                        "quantified_var": var,
                        "frame": frame,
                        "assignment": assignment,
                        "checked_assignments": checked_assignments,
                    }
    except (AssertionError, r18.ResourceLimit, FusedResourceOpen) as exc:
        return {
            "pass": False,
            "seed": 30052,
            "reason": str(exc),
            "checked_assignments": checked_assignments,
        }
    return {
        "pass": True,
        "seed": 30052,
        "cases": cases,
        "checked_assignments": checked_assignments,
    }


def mask_hash(masks):
    payload = json.dumps(list(masks), separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def candidate_summary(candidate):
    return dict(candidate)


def run():
    prereg = load_prereg()
    freeze = r19.load_freeze()
    spec = next(world for world in freeze["worlds"] if world["id"] == WORLD_ID)
    world = r19.generate_frozen_world(spec)
    if spec["frame_sha256"] != EXPECTED_FRAME_SHA:
        raise AssertionError("R19-W05 frame drift")
    frame = tuple(world["frame"])
    bridge = tuple(world["bridge"])

    firewall = candidate_firewall()
    tiny_factor = tiny_factor_identity_control()
    tiny_protected = tiny_protected_shared_subgraph_control()
    small_suite = deterministic_small_operator_equivalence_suite()
    base = {
        "schema": "JANUS/TRUMP/R30/CONSUMING_FUSED_EXISTENTIAL_RESTRICTION_CONTROL/RESULT/v1.0",
        "created_date": "2026-09-02",
        "scientific_role": "EXPOSED_W05_EXACT_REPRESENTATION_CONTROL__NEW_OPERATOR__NOT_UNSEEN__NO_THEOREM_AUTHORITY",
        "world": {
            "id": WORLD_ID,
            "frame_sha256": EXPECTED_FRAME_SHA,
            "frame_clauses": len(frame),
            "bridge_vars": list(bridge),
        },
        "frozen_lineage": prereg["frozen_lineage"],
        "resource_envelope": prereg["resource_envelope"],
        "candidate_firewall": firewall,
        "tiny_factor_identity_control": tiny_factor,
        "tiny_protected_shared_subgraph_control": tiny_protected,
        "deterministic_small_operator_equivalence_suite": small_suite,
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
    }
    if (
        not firewall["pass"]
        or not tiny_factor["pass"]
        or not tiny_protected["pass"]
        or not small_suite["pass"]
    ):
        return {
            **base,
            "verdict": "R30_FAIL_INTEGRITY",
            "candidate": {"not_run": True},
            "verifier": {"not_run": True},
            "truth_accessed": False,
            "claim_ceiling": prereg["claim_ceiling"],
        }

    candidate, live = compile_fused_factored(frame, bridge)
    summary = candidate_summary(candidate)
    if candidate["status"] == "OPEN_RESOURCE_LIMIT":
        return {
            **base,
            "verdict": "R30_OPEN_RESOURCE_LIMIT__NO_SEMANTIC_VERDICT",
            "candidate": summary,
            "verifier": {"not_run": True},
            "truth_accessed": False,
            "claim_ceiling": prereg["claim_ceiling"],
            "seal": "THE_CONSUMING_OPERATOR_REACHED_ITS_FROZEN_ENVELOPE__SILENCE_IS_NOT_NEGATIVE_EVIDENCE",
        }
    if candidate["status"] != "COMPLETE_FACTORED_BRIDGE_INTERFACE" or live is None:
        return {
            **base,
            "verdict": "R30_FAIL_INTEGRITY",
            "candidate": summary,
            "verifier": {"not_run": True},
            "truth_accessed": False,
            "claim_ceiling": prereg["claim_ceiling"],
        }

    verifier_started = time.monotonic()
    original = r18.independent_original_allowed(frame, bridge)
    candidate_allowed = r27.factor_set_allowed(live, bridge)
    if original.get("replay_failures"):
        return {
            **base,
            "verdict": "R30_FAIL_INTEGRITY",
            "candidate": summary,
            "verifier": {
                "started_after_candidate_terminal": True,
                "reason": "ORIGINAL_MODEL_REPLAY_FAIL",
            },
            "truth_accessed": True,
            "claim_ceiling": prereg["claim_ceiling"],
        }
    exact = set(original["allowed_masks"])
    have = set(candidate_allowed["allowed_masks"])
    false_positive = sorted(have - exact)
    false_negative = sorted(exact - have)
    match = not false_positive and not false_negative
    comparison = {
        "full_domain": True,
        "domain_size": 1 << len(bridge),
        "allowed_set_equal": match,
        "original_allowed": len(exact),
        "candidate_allowed": len(have),
        "false_positive_count": len(false_positive),
        "false_negative_count": len(false_negative),
        "first_false_positive_masks": false_positive[:32],
        "first_false_negative_masks": false_negative[:32],
        "original_truth_table_sha256": mask_hash(original["allowed_masks"]),
        "candidate_truth_table_sha256": mask_hash(candidate_allowed["allowed_masks"]),
        "original_sat_model_replay_failures": original.get("replay_failures", []),
    }
    verdict = (
        "R30_EXPOSED_W05_FUSED_FULL_DOMAIN_SEMANTIC_MATCH"
        if match
        else "R30_EXPOSED_W05_FUSED_SEMANTIC_MISMATCH"
    )
    return {
        **base,
        "verdict": verdict,
        "candidate": summary,
        "verifier": {
            "started_after_candidate_terminal": True,
            "elapsed_seconds": time.monotonic() - verifier_started,
        },
        "comparison": comparison,
        "truth_accessed": True,
        "scientific_interpretation": "This exposed W05 control tests whether consuming x-dependent source nodes can reduce transient DAG residency while preserving the exact fully materialized bridge relation. A finite match is not an unseen result or a polynomial bound.",
        "claim_ceiling": prereg["claim_ceiling"],
        "seal": "THE_OLD_X_DEPENDENT_MESSAGE_WAS_RELEASED_ONLY_AFTER_ITS_EXACT_LOW_HIGH_PAIR_WAS_BUILT",
        "TRUMP_finished": False,
        "SAT_IN_P": "NOT_PROVED",
        "P_VS_NP": "OPEN",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run()
    Path(args.output).write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    candidate = result.get("candidate") or {}
    candidate_log_summary = {
        key: value for key, value in candidate.items() if key != "trajectory"
    }
    print(
        json.dumps(
            {
                "verdict": result["verdict"],
                "candidate": candidate_log_summary,
                "comparison": result.get("comparison"),
                "candidate_firewall": result["candidate_firewall"],
                "tiny_factor_identity_control": result["tiny_factor_identity_control"]["pass"],
                "tiny_protected_shared_subgraph_control": result[
                    "tiny_protected_shared_subgraph_control"
                ]["pass"],
                "deterministic_small_operator_equivalence_suite": result[
                    "deterministic_small_operator_equivalence_suite"
                ]["pass"],
                "TRUMP_finished": False,
                "SAT_IN_P": "NOT_PROVED",
                "P_VS_NP": "OPEN",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 2 if result["verdict"] == "R30_FAIL_INTEGRITY" else 0


if __name__ == "__main__":
    raise SystemExit(main())
