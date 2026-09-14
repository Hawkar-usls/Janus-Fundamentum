#!/usr/bin/env python3
"""Exact revealed cache-fiber diagnostic for historical C023.

No asymptotic law is inferred from finite data. The script verifies exact DAG
multiplicity identities and compares the full cache unfolding with frozen
Policy-0T on the same revealed fixtures.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIRECT = ROOT / "experiments" / "direct"
sys.path.insert(0, str(DIRECT))

from janus_tear_maj3_stifling_audit import maj3_lifted_tseitin_cnf
from janus_tear_policy0a_context_obstruction import cache_diamond_cnf
from janus_tear_policy0a_fc_trace import FCTracePolicy, verify_fc_trace
from janus_tear_policy0a_masked_tseitin import K4_EDGES
from janus_tear_policy0t_no_cache import Policy0T


def key_sha(key) -> str:
    return hashlib.sha256(repr(key).encode("utf-8")).hexdigest()

def child_state(policy, child):
    call_id = child.get("call")
    if call_id is None:
        return None
    call = policy.calls[int(call_id)]
    if call["terminal"] == "STATE":
        return int(call["state"])
    if call["terminal"] == "CACHE_HIT":
        return int(call["cache_target"])
    return None


def exact_state_multiplicities(policy, root_call: int):
    root = policy.calls[root_call]
    assert root["terminal"] == "STATE"
    root_state = int(root["state"])

    edges = defaultdict(list)
    reachable = set()
    stack = [root_state]
    while stack:
        sid = stack.pop()
        if sid in reachable:
            continue
        reachable.add(sid)
        for child in policy.states[sid].get("children", []):
            target = child_state(policy, child)
            if target is not None:
                edges[sid].append(target)
                stack.append(target)

    indegree = {sid: 0 for sid in reachable}
    for sid in reachable:
        for target in edges[sid]:
            indegree[target] += 1
    q = deque(sorted(sid for sid, deg in indegree.items() if deg == 0))
    topo = []
    while q:
        sid = q.popleft()
        topo.append(sid)
        for target in edges[sid]:
            indegree[target] -= 1
            if indegree[target] == 0:
                q.append(target)
    assert len(topo) == len(reachable), "state dependency graph must be acyclic"
    assert topo[0] == root_state, "root must be the unique reachable source"

    multiplicity = {sid: 0 for sid in reachable}
    multiplicity[root_state] = 1
    for sid in topo:
        for target in edges[sid]:
            multiplicity[target] += multiplicity[sid]

    return root_state, topo, dict(edges), multiplicity


def run_case(name, cnf, variable_count):
    policy = FCTracePolicy()
    result, root_call = policy.solve(cnf, variable_count)
    assert result.answer is False
    assert root_call is not None
    assert verify_fc_trace(cnf, variable_count, policy, root_call) is False

    root_state, topo, edges, mult = exact_state_multiplicities(policy, root_call)
    tree = Policy0T().solve(cnf, variable_count)
    assert tree.answer is False and not tree.cap_exceeded

    state_occurrences = sum(mult.values())
    assert state_occurrences == tree.expanded_states
    m_max = max(mult.values())
    histogram = Counter(mult.values())
    max_states = sorted(sid for sid, m in mult.items() if m == m_max)

    return {
        "name": name,
        "variables": variable_count,
        "cached_calls": result.calls,
        "cached_unique_states": result.unique_states,
        "cache_hits": result.cache_hits,
        "no_cache_recursive_calls": tree.recursive_calls,
        "no_cache_expanded_states": tree.expanded_states,
        "state_occurrences_from_DAG_paths": state_occurrences,
        "state_occurrence_identity": state_occurrences == tree.expanded_states,
        "m_max": m_max,
        "multiplicity_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "max_multiplicity_states": [
            {"state_id": sid, "key_sha256": key_sha(policy.states[sid]["key"])}
            for sid in max_states
        ],
        "reachable_state_count": len(topo),
        "dependency_edge_count": sum(len(v) for v in edges.values()),
        "root_state": root_state,
        "cached_state_local_cost": sum(
            1 + int(s["resolution_attempts"]) + int(s["resolution_additions"])
            + sum(1 for c in s.get("children", []) if c.get("call") is not None)
            for s in policy.states.values()
        ),
        "unfolded_state_local_cost": sum(
            mult[sid] * (
                1 + int(policy.states[sid]["resolution_attempts"])
                + int(policy.states[sid]["resolution_additions"])
                + sum(1 for c in policy.states[sid].get("children", []) if c.get("call") is not None)
            )
            for sid in mult
        ),
        "no_cache_state_local_cost": (
            tree.expanded_states + tree.resolution_attempts
            + tree.resolution_additions + tree.branch_edges
        ),
    }


def main():
    cases = []
    for selectors in range(0, 8):
        cnf, nvars = cache_diamond_cnf(selectors)
        cases.append(run_case(f"CACHE_DIAMOND_{selectors}", cnf, nvars))

    cnf, nvars = maj3_lifted_tseitin_cnf(4, K4_EDGES)
    cases.append(run_case("MAJ3_LIFTED_K4", cnf, nvars))

    for row in cases:
        assert row["state_occurrence_identity"]
        assert row["unfolded_state_local_cost"] == row["no_cache_state_local_cost"]

    result = {
        "artifact_id": "TRUMP-C023R-MAJ3-CACHE-FIBER-INVARIANT-DIAGNOSTIC-RESULT-2026-09-14-v1.0",
        "authority_class": "REVEALED_DIAGNOSTIC_ONLY__NO_SCIENTIFIC_PROMOTION",
        "strict_method": "ALGEBRA_ONLY__NO_HEURISTICS",
        "cases": cases,
        "interpretation_rule": {
            "finite_data": "falsifier_and_exact_identity_check_only",
            "asymptotic_inference": "FORBIDDEN",
            "next_allowed": "derive symbolic MAJ3/Tseitin residual invariant independently of finite fit"
        },
        "scientific_firewall": {
            "CACHE_FIBER_DIAGNOSTIC": "NOT_A_CACHED_LOWER_BOUND_THEOREM",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN"
        }
    }
    out = Path(__file__).with_name("RESULT_C023R_CACHE_FIBER_DIAGNOSTIC_v1.0.json")
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({
        "status": "PASS_EXACT_FINITE_IDENTITIES",
        "result_file": str(out),
        "rows": [
            {"name": r["name"], "m_max": r["m_max"], "cached_unique_states": r["cached_unique_states"],
             "no_cache_expanded_states": r["no_cache_expanded_states"]}
            for r in cases
        ]
    }, indent=2))


if __name__ == "__main__":
    main()
