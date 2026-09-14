import math

import research.tools.apma_trinity_sovereign.trinity as base
from research.tools.apma_typed_module_forest.module_forest import (
    discover_modules,
    build_interaction,
    encoding_size,
    _native_solve,
    _assignments,
    _key,
    _forest_parent_order,
    _merge_witness,
)

UNICYCLIC = "BOUNDED_INTERFACE_UNICYCLIC_TRANSFER"


def _connected(adj):
    if not adj:
        return False
    start = min(adj)
    seen = {start}
    stack = [start]
    while stack:
        u = stack.pop()
        for v in sorted(adj[u]):
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(adj)


def _remove_edge_adj(adj, edge):
    a, b = edge
    out = {u: set(vs) for u, vs in adj.items()}
    out[a].discard(b)
    out[b].discard(a)
    return out


def _canonical_cycle_edge(adj, edge_vars):
    # In a connected unicyclic simple graph, exactly the cycle edges are non-bridges.
    for edge in sorted(edge_vars):
        cut = _remove_edge_adj(adj, edge)
        if _connected(cut):
            return edge
    return None


def unicyclic_certificate(state, source, n):
    modules = discover_modules(state)
    interaction = build_interaction(modules)
    if interaction.get("status") == "OPEN_INTERFACE_HYPEREDGE":
        return None, {"unicyclic_status": "OPEN_INTERFACE_HYPEREDGE"}
    if interaction.get("status") != "OPEN_MODULE_CYCLE":
        return None, {"unicyclic_status": "NOT_CYCLIC_INTERACTION"}
    adj = interaction["adj"]
    edge_vars = interaction["edge_vars"]
    if not _connected(adj):
        return None, {"unicyclic_status": "OPEN_DISCONNECTED_CYCLIC_INTERACTION"}
    if len(edge_vars) != len(modules):
        return None, {
            "unicyclic_status": "OPEN_CYCLE_RANK_NOT_ONE",
            "module_count": len(modules),
            "edge_count": len(edge_vars),
        }
    cut_edge = _canonical_cycle_edge(adj, edge_vars)
    if cut_edge is None:
        return None, {"unicyclic_status": "OPEN_NO_CANONICAL_CYCLE_EDGE"}
    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    boundary = {m["id"]: set() for m in modules}
    for (a, b), vs in edge_vars.items():
        boundary[a].update(vs)
        boundary[b].update(vs)
    too_wide = {mid: sorted(vs) for mid, vs in boundary.items() if len(vs) > budget}
    if too_wide:
        return None, {
            "unicyclic_status": "OPEN_INTERFACE_WIDTH",
            "budget": budget,
            "too_wide": too_wide,
        }
    cert = {
        "unicyclic_status": "ADMIT_CONNECTED_CYCLE_RANK_ONE",
        "module_count": len(modules),
        "edge_count": len(edge_vars),
        "cut_edge": list(cut_edge),
        "cut_separator": sorted(edge_vars[cut_edge]),
        "budget": budget,
        "max_boundary": max((len(vs) for vs in boundary.values()), default=0),
    }
    return cert, cert


def _solve_conditioned_tree(modules, interaction, source, n, cut_edge, sigma):
    edge_vars = interaction["edge_vars"]
    original_adj = interaction["adj"]
    tree_adj = _remove_edge_adj(original_adj, cut_edge)
    tree_edge_vars = {e: set(vs) for e, vs in edge_vars.items() if e != cut_edge}
    if not _connected(tree_adj) or len(tree_edge_vars) != len(modules) - 1:
        return {"status": "INTERNAL_CUT_NOT_TREE"}

    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    full_boundary = {m["id"]: set() for m in modules}
    for (a, b), vs in edge_vars.items():
        full_boundary[a].update(vs)
        full_boundary[b].update(vs)
    too_wide = {mid: sorted(vs) for mid, vs in full_boundary.items() if len(vs) > budget}
    if too_wide:
        return {"status": "OPEN_INTERFACE_WIDTH", "budget": budget, "too_wide": too_wide}

    by_id = {m["id"]: m for m in modules}
    parent, order, roots = _forest_parent_order(tree_adj)
    if len(roots) != 1:
        return {"status": "INTERNAL_CUT_NOT_SINGLE_TREE"}
    cut_sep = set(edge_vars[cut_edge])
    cut_endpoints = set(cut_edge)
    tables = {}
    row_count = 0

    for mid in reversed(order):
        m = by_id[mid]
        p = parent[mid]
        psep = set() if p is None else set(tree_edge_vars[tuple(sorted((mid, p)))])
        children = [v for v in sorted(tree_adj[mid]) if parent.get(v) == mid]
        free_boundary = set(full_boundary[mid]) - (cut_sep if mid in cut_endpoints else set())
        table = {}
        for free_assignment in _assignments(free_boundary):
            row_count += 1
            pa = dict(free_assignment)
            if mid in cut_endpoints:
                pa.update(sigma)
            local = _native_solve(m, n, pa)
            if not local["sat"]:
                continue
            ok = True
            for ch in children:
                sep = set(tree_edge_vars[tuple(sorted((mid, ch)))])
                ck = _key(sep, pa)
                if ck not in tables[ch]:
                    ok = False
                    break
            if not ok:
                continue
            pk = _key(psep, pa)
            if pk not in table:
                table[pk] = {"boundary": dict(pa), "witness": local["witness"]}
        tables[mid] = table

    root = roots[0]
    if () not in tables[root]:
        return {"status": "REJECTED_SIGMA", "row_count": row_count}

    def recover(mid, key):
        row = tables[mid][key]
        out = dict(row["witness"])
        for ch in sorted(tree_adj[mid]):
            if parent.get(ch) != mid:
                continue
            sep = set(tree_edge_vars[tuple(sorted((mid, ch)))])
            ck = _key(sep, row["boundary"])
            cw = recover(ch, ck)
            out = _merge_witness(out, cw)
            if out is None:
                raise AssertionError("unicyclic witness merge mismatch")
        return out

    witness = recover(root, ())
    for v, b in sigma.items():
        if v in witness and bool(witness[v]) != bool(b):
            return {"status": "INTERNAL_SIGMA_WITNESS_MISMATCH"}
        witness[v] = bool(b)
    return {"status": "SAT_SIGMA", "witness": witness, "row_count": row_count}


def compile_unicyclic(source, n):
    source = base.canonical_source(source)
    state = base._typed_state(source)
    if state is None:
        return {"status": "OPEN_MOSAIC_NOT_CLOSED"}
    cert, diag = unicyclic_certificate(state, source, n)
    if cert is None:
        return {"status": diag.get("unicyclic_status", "OPEN_NOT_UNICYCLIC"), "diagnostic": diag}
    modules = discover_modules(state)
    interaction = build_interaction(modules)
    cut_edge = tuple(cert["cut_edge"])
    cut_separator = tuple(cert["cut_separator"])
    tested = 0
    total_rows = 0
    rejected = []
    for sigma in _assignments(cut_separator):
        tested += 1
        z = _solve_conditioned_tree(modules, interaction, source, n, cut_edge, sigma)
        total_rows += int(z.get("row_count", 0))
        if z["status"] == "SAT_SIGMA":
            witness = z["witness"]
            if not base.verify_root_witness(source, witness, n):
                return {"status": "HALT_ROOT_REPLAY_MISMATCH"}
            return {
                "status": "CERTIFIED_SAT_MODULE_UNICYCLIC",
                "witness": witness,
                "certificate": cert,
                "tested_sigma_count": tested,
                "row_count": total_rows,
            }
        if z["status"] != "REJECTED_SIGMA":
            return z
        rejected.append([int(bool(sigma[v])) for v in cut_separator])
    return {
        "status": "CERTIFIED_UNSAT_MODULE_UNICYCLIC",
        "witness": None,
        "certificate": cert,
        "tested_sigma_count": tested,
        "rejected_sigma": rejected,
        "row_count": total_rows,
    }


def akinator_propose(source, n):
    source = base.canonical_source(source)
    old = base.akinator_propose(source, n)
    if old.get("door") is not None:
        return old
    state = base._typed_state(source)
    if state is None:
        return old
    cert, _ = unicyclic_certificate(state, source, n)
    if cert is None:
        return old
    return {"door": UNICYCLIC, "root_hash": base.source_hash(source), "evidence": cert}


def captain_verify(source, n, proposal):
    expected = akinator_propose(source, n)
    ok = proposal == expected and proposal.get("root_hash") == base.source_hash(source)
    return {"status": "ADMIT" if ok else "REJECT", "expected": expected, "received": proposal}


def janus_demiurge_execute(source, n, proposal):
    if proposal.get("door") == UNICYCLIC:
        return compile_unicyclic(source, int(n))
    return base.janus_demiurge_execute(source, int(n), proposal)


def janus_sovereign_decide(source, n, proposal, captain, execution):
    if proposal.get("door") != UNICYCLIC:
        return base.janus_sovereign_decide(source, n, proposal, captain, execution)
    root_hash = base.source_hash(source)
    if captain.get("status") != "ADMIT":
        return {"decision": "ROLLBACK_CAPTAIN_REJECT", "authority_root_hash": root_hash}
    if proposal.get("root_hash") != root_hash:
        return {"decision": "HALT_INTERNAL_MISMATCH", "reason": "ROOT_HASH_DRIFT"}
    status = execution.get("status")
    if status == "CERTIFIED_SAT_MODULE_UNICYCLIC":
        witness = execution.get("witness") or {}
        if not base.verify_root_witness(source, witness, n):
            return {"decision": "HALT_INTERNAL_MISMATCH", "reason": "BAD_ROOT_WITNESS"}
        return {"decision": "COMMIT_SAT", "authority_root_hash": root_hash, "witness": witness}
    if status == "CERTIFIED_UNSAT_MODULE_UNICYCLIC":
        return {"decision": "COMMIT_UNSAT", "authority_root_hash": root_hash, "certificate_status": status}
    return {"decision": "OPEN_UNKNOWN_STATE_CLASS", "authority_root_hash": root_hash, "demiurge_status": status}


def run_trinity(source, n, forced_proposal=None):
    source = base.canonical_source(source)
    root_hash = base.source_hash(source)
    proposed = akinator_propose(source, n)
    trace = [{"role": "AKINATOR", "proposal": proposed}]
    if proposed.get("door") is None and forced_proposal is None:
        sovereign = {"decision": "OPEN_UNKNOWN_STATE_CLASS", "authority_root_hash": root_hash, "evidence": proposed.get("evidence", {})}
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
    sovereign = janus_sovereign_decide(source, n, candidate, captain, execution)
    trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
    return _final(source, n, candidate, captain, execution, sovereign, trace)


def _final(source, n, proposal, captain, execution, sovereign, trace):
    return {
        "schema": "JANUS_TRUMP_APMA_TRINITY_UNICYCLIC_SUCCESSOR_V1",
        "root_hash": base.source_hash(source),
        "n": int(n),
        "proposal": proposal,
        "captain": captain,
        "demiurge": execution,
        "sovereign": sovereign,
        "trace": trace,
        "scientific_status": {
            "scope": "BOUNDED_INTERFACE_CONNECTED_UNICYCLIC_TYPED_MODULE_INTERACTION_ONLY",
            "UNIVERSAL_DISCOVERY": "NOT_CLAIMED",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "Pi_negative_evidence_weight": 0,
        },
    }
