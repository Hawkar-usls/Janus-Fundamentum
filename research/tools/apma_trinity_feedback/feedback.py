from __future__ import annotations

import math
from collections import deque

import research.tools.apma_trinity_sovereign.trinity as base
import research.tools.apma_trinity_unicyclic.unicyclic as predecessor
from research.tools.apma_typed_module_forest.module_forest import (
    discover_modules,
    build_interaction,
    encoding_size,
    _native_solve,
    _assignments,
    _key,
    _merge_witness,
)

FEEDBACK = "BOUNDED_FEEDBACK_INTERFACE_TRANSFER"


def _connected(adj):
    if not adj:
        return False
    start = min(adj)
    seen = {start}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in sorted(adj[u]):
            if v not in seen:
                seen.add(v)
                q.append(v)
    return len(seen) == len(adj)


def _canonical_bfs_tree(adj):
    """Return deterministic BFS tree edges from lexicographically minimum root."""
    if not _connected(adj):
        return None
    root = min(adj)
    seen = {root}
    q = deque([root])
    tree = set()
    parent = {root: None}
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in sorted(adj[u]):
            if v in seen:
                continue
            seen.add(v)
            parent[v] = u
            tree.add(tuple(sorted((u, v))))
            q.append(v)
    return root, parent, order, tree


def feedback_certificate(state, source, n):
    modules = discover_modules(state)
    interaction = build_interaction(modules)
    if interaction.get("status") == "OPEN_INTERFACE_HYPEREDGE":
        return None, {"feedback_status": "OPEN_INTERFACE_HYPEREDGE"}
    if interaction.get("status") != "OPEN_MODULE_CYCLE":
        return None, {"feedback_status": "NOT_CYCLIC_INTERACTION"}

    adj = interaction["adj"]
    edge_vars = interaction["edge_vars"]
    if not _connected(adj):
        return None, {"feedback_status": "OPEN_DISCONNECTED_INTERACTION"}

    V = len(modules)
    E = len(edge_vars)
    cycle_rank = E - V + 1
    if cycle_rank < 2:
        return None, {
            "feedback_status": "NOT_MULTICYCLE_FEEDBACK_TARGET",
            "cycle_rank": cycle_rank,
        }

    tree_data = _canonical_bfs_tree(adj)
    if tree_data is None:
        return None, {"feedback_status": "OPEN_DISCONNECTED_INTERACTION"}
    root, _, _, tree_edges = tree_data
    all_edges = set(edge_vars)
    feedback_edges = tuple(sorted(all_edges - tree_edges))
    if len(feedback_edges) != cycle_rank:
        return None, {"feedback_status": "INTERNAL_FEEDBACK_RANK_MISMATCH"}

    B = set()
    for e in feedback_edges:
        B.update(edge_vars[e])

    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    if len(B) > budget:
        return None, {
            "feedback_status": "OPEN_FEEDBACK_INTERFACE_WIDTH",
            "budget": budget,
            "feedback_interface_width": len(B),
            "cycle_rank": cycle_rank,
        }

    full_boundary = {m["id"]: set() for m in modules}
    for (a, b), vs in edge_vars.items():
        full_boundary[a].update(vs)
        full_boundary[b].update(vs)
    remaining_boundary = {
        mid: (vs - B) for mid, vs in full_boundary.items()
    }
    too_wide = {
        mid: sorted(vs)
        for mid, vs in remaining_boundary.items()
        if len(vs) > budget
    }
    if too_wide:
        return None, {
            "feedback_status": "OPEN_CONDITIONED_TREE_BOUNDARY_WIDTH",
            "budget": budget,
            "too_wide": too_wide,
        }

    cert = {
        "feedback_status": "ADMIT_CANONICAL_BOUNDED_FEEDBACK_INTERFACE",
        "module_count": V,
        "edge_count": E,
        "cycle_rank": cycle_rank,
        "canonical_root": root,
        "tree_edges": [list(e) for e in sorted(tree_edges)],
        "feedback_edges": [list(e) for e in feedback_edges],
        "feedback_interface": sorted(B),
        "feedback_interface_width": len(B),
        "budget": budget,
        "max_conditioned_tree_boundary": max(
            (len(vs) for vs in remaining_boundary.values()), default=0
        ),
    }
    return cert, cert


def _solve_conditioned_tree(modules, interaction, source, n, cert, sigma):
    edge_vars = interaction["edge_vars"]
    tree_edges = {tuple(e) for e in cert["tree_edges"]}
    feedback_edges = {tuple(e) for e in cert["feedback_edges"]}
    B = set(cert["feedback_interface"])

    if tree_edges | feedback_edges != set(edge_vars):
        return {"status": "INTERNAL_EDGE_PARTITION_MISMATCH"}
    if tree_edges & feedback_edges:
        return {"status": "INTERNAL_EDGE_PARTITION_OVERLAP"}

    tree_adj = {m["id"]: set() for m in modules}
    for a, b in tree_edges:
        tree_adj[a].add(b)
        tree_adj[b].add(a)
    if not _connected(tree_adj) or len(tree_edges) != len(modules) - 1:
        return {"status": "INTERNAL_FEEDBACK_REMOVAL_NOT_TREE"}

    # Reconstruct deterministic root/parents on the frozen tree.
    root = cert["canonical_root"]
    parent = {root: None}
    order = []
    q = deque([root])
    while q:
        u = q.popleft()
        order.append(u)
        for v in sorted(tree_adj[u]):
            if v in parent:
                continue
            parent[v] = u
            q.append(v)
    if len(order) != len(modules):
        return {"status": "INTERNAL_TREE_TRAVERSAL_INCOMPLETE"}

    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    full_boundary = {m["id"]: set() for m in modules}
    for (a, b), vs in edge_vars.items():
        full_boundary[a].update(vs)
        full_boundary[b].update(vs)
    remaining_boundary = {mid: vs - B for mid, vs in full_boundary.items()}
    too_wide = {
        mid: sorted(vs)
        for mid, vs in remaining_boundary.items()
        if len(vs) > budget
    }
    if too_wide:
        return {
            "status": "OPEN_CONDITIONED_TREE_BOUNDARY_WIDTH",
            "budget": budget,
            "too_wide": too_wide,
        }

    by_id = {m["id"]: m for m in modules}
    tables = {}
    row_count = 0
    native_solve_calls = 0

    for mid in reversed(order):
        m = by_id[mid]
        p = parent[mid]
        if p is None:
            psep = set()
        else:
            psep = set(edge_vars[tuple(sorted((mid, p)))]) - B
        children = [v for v in sorted(tree_adj[mid]) if parent.get(v) == mid]
        table = {}

        for free_assignment in _assignments(remaining_boundary[mid]):
            row_count += 1
            pa = dict(free_assignment)
            for v in B & set(m["vars"]):
                pa[v] = bool(sigma[v])
            native_solve_calls += 1
            local = _native_solve(m, n, pa)
            if not local["sat"]:
                continue

            ok = True
            for ch in children:
                sep = set(edge_vars[tuple(sorted((mid, ch)))]) - B
                ck = _key(sep, pa)
                if ck not in tables[ch]:
                    ok = False
                    break
            if not ok:
                continue

            pk = _key(psep, pa)
            if pk not in table:
                table[pk] = {
                    "boundary": dict(pa),
                    "witness": local["witness"],
                }
        tables[mid] = table

    if () not in tables[root]:
        return {
            "status": "REJECTED_SIGMA",
            "row_count": row_count,
            "native_solve_calls": native_solve_calls,
        }

    def recover(mid, key):
        row = tables[mid][key]
        out = dict(row["witness"])
        for ch in sorted(tree_adj[mid]):
            if parent.get(ch) != mid:
                continue
            sep = set(edge_vars[tuple(sorted((mid, ch)))]) - B
            ck = _key(sep, row["boundary"])
            cw = recover(ch, ck)
            out = _merge_witness(out, cw)
            if out is None:
                raise AssertionError("feedback witness merge mismatch")
        return out

    witness = recover(root, ())
    for v, b in sigma.items():
        if v in witness and bool(witness[v]) != bool(b):
            return {"status": "INTERNAL_SIGMA_WITNESS_MISMATCH"}
        witness[v] = bool(b)
    return {
        "status": "SAT_SIGMA",
        "witness": witness,
        "row_count": row_count,
        "native_solve_calls": native_solve_calls,
    }


def compile_feedback(source, n):
    source = base.canonical_source(source)
    state = base._typed_state(source)
    if state is None:
        return {"status": "OPEN_MOSAIC_NOT_CLOSED"}
    cert, diag = feedback_certificate(state, source, n)
    if cert is None:
        return {
            "status": diag.get("feedback_status", "OPEN_NOT_FEEDBACK_TARGET"),
            "diagnostic": diag,
        }

    modules = discover_modules(state)
    interaction = build_interaction(modules)
    B = tuple(cert["feedback_interface"])
    tested = 0
    total_rows = 0
    total_native_calls = 0
    rejected = []

    for sigma in _assignments(B):
        tested += 1
        z = _solve_conditioned_tree(
            modules, interaction, source, int(n), cert, sigma
        )
        total_rows += int(z.get("row_count", 0))
        total_native_calls += int(z.get("native_solve_calls", 0))
        if z["status"] == "SAT_SIGMA":
            witness = z["witness"]
            if not base.verify_root_witness(source, witness, n):
                return {"status": "HALT_ROOT_REPLAY_MISMATCH"}
            return {
                "status": "CERTIFIED_SAT_MODULE_FEEDBACK",
                "witness": witness,
                "certificate": cert,
                "tested_sigma_count": tested,
                "row_count": total_rows,
                "native_solve_calls": total_native_calls,
            }
        if z["status"] != "REJECTED_SIGMA":
            return z
        rejected.append([int(bool(sigma[v])) for v in B])

    return {
        "status": "CERTIFIED_UNSAT_MODULE_FEEDBACK",
        "witness": None,
        "certificate": cert,
        "tested_sigma_count": tested,
        "rejected_sigma": rejected,
        "row_count": total_rows,
        "native_solve_calls": total_native_calls,
    }


def akinator_propose(source, n):
    source = base.canonical_source(source)
    old = predecessor.akinator_propose(source, n)
    if old.get("door") is not None:
        return old
    state = base._typed_state(source)
    if state is None:
        return old
    cert, _ = feedback_certificate(state, source, n)
    if cert is None:
        return old
    return {
        "door": FEEDBACK,
        "root_hash": base.source_hash(source),
        "evidence": cert,
    }


def captain_verify(source, n, proposal):
    expected = akinator_propose(source, n)
    ok = proposal == expected and proposal.get("root_hash") == base.source_hash(source)
    return {
        "status": "ADMIT" if ok else "REJECT",
        "expected": expected,
        "received": proposal,
    }


def janus_demiurge_execute(source, n, proposal):
    if proposal.get("door") == FEEDBACK:
        return compile_feedback(source, int(n))
    return predecessor.janus_demiurge_execute(source, int(n), proposal)


def janus_sovereign_decide(source, n, proposal, captain, execution):
    if proposal.get("door") != FEEDBACK:
        return predecessor.janus_sovereign_decide(
            source, n, proposal, captain, execution
        )
    root_hash = base.source_hash(source)
    if captain.get("status") != "ADMIT":
        return {
            "decision": "ROLLBACK_CAPTAIN_REJECT",
            "authority_root_hash": root_hash,
        }
    if proposal.get("root_hash") != root_hash:
        return {
            "decision": "HALT_INTERNAL_MISMATCH",
            "reason": "ROOT_HASH_DRIFT",
        }
    status = execution.get("status")
    if status == "CERTIFIED_SAT_MODULE_FEEDBACK":
        witness = execution.get("witness") or {}
        if not base.verify_root_witness(source, witness, n):
            return {
                "decision": "HALT_INTERNAL_MISMATCH",
                "reason": "BAD_ROOT_WITNESS",
            }
        return {
            "decision": "COMMIT_SAT",
            "authority_root_hash": root_hash,
            "witness": witness,
        }
    if status == "CERTIFIED_UNSAT_MODULE_FEEDBACK":
        return {
            "decision": "COMMIT_UNSAT",
            "authority_root_hash": root_hash,
            "certificate_status": status,
        }
    return {
        "decision": "OPEN_UNKNOWN_STATE_CLASS",
        "authority_root_hash": root_hash,
        "demiurge_status": status,
    }


def run_trinity(source, n, forced_proposal=None):
    source = base.canonical_source(source)
    root_hash = base.source_hash(source)
    proposed = akinator_propose(source, n)
    trace = [{"role": "AKINATOR", "proposal": proposed}]
    if proposed.get("door") is None and forced_proposal is None:
        sovereign = {
            "decision": "OPEN_UNKNOWN_STATE_CLASS",
            "authority_root_hash": root_hash,
            "evidence": proposed.get("evidence", {}),
        }
        trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
        return _final(source, n, proposed, None, None, sovereign, trace)

    candidate = forced_proposal if forced_proposal is not None else proposed
    captain = captain_verify(source, n, candidate)
    trace.append({"role": "CAPTAIN_OBVIOUS", "result": captain["status"]})
    if captain["status"] != "ADMIT":
        sovereign = janus_sovereign_decide(source, n, candidate, captain, {})
        trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
        return _final(source, n, candidate, captain, None, sovereign, trace)

    execution = janus_demiurge_execute(source, n, candidate)
    trace.append({"role": "JANUS_DEMIURGE", "status": execution.get("status")})
    sovereign = janus_sovereign_decide(
        source, n, candidate, captain, execution
    )
    trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
    return _final(source, n, candidate, captain, execution, sovereign, trace)


def _final(source, n, proposal, captain, execution, sovereign, trace):
    return {
        "schema": "JANUS_TRUMP_APMA_TRINITY_FEEDBACK_SUCCESSOR_V1",
        "root_hash": base.source_hash(source),
        "n": int(n),
        "proposal": proposal,
        "captain": captain,
        "demiurge": execution,
        "sovereign": sovereign,
        "trace": trace,
        "scientific_status": {
            "scope": "CANONICAL_LOG_FEEDBACK_INTERFACE_TYPED_MODULE_INTERACTION_ONLY",
            "WIDE_INTERFACE_COMPRESSION": "NOT_CLAIMED",
            "UNIVERSAL_DISCOVERY": "NOT_CLAIMED",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "Pi_negative_evidence_weight": 0,
        },
    }
