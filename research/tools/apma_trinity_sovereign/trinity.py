import hashlib, json, math

from research.tools.apma_dense_cardinality.apma_dense_cardinality import (
    recognize_complete_negative_triples,
)
from research.tools.apma_ss_provenance.apma_ss_controller import classify_source, solve_source
from research.tools.apma_ss_partial_mosaic.partial_mosaic import (
    make_state, propose_extract, verify_proposal, commit_proposal,
    verify_full_recomposition, MORPH_SEQUENCE,
)
from research.tools.apma_typed_module_forest.module_forest import (
    discover_modules, build_interaction, encoding_size, compile_typed_module_forest,
)
from research.tools.apma_factor_tree_hyperedge.factor_tree import (
    build_factor_graph, compile_factor_tree_hyperedge,
)

DIRECT = "DIRECT_NATIVE_2CNF_HORN_DUAL_HORN"
CARD = "COMPLETE_NEGATIVE_TRIPLES_TO_AT_MOST_2"
FOREST = "TYPED_MODULE_FOREST"
FACTOR = "FACTOR_TREE_HYPEREDGE"


def _norm_clause(c):
    return tuple(sorted((int(x) for x in c), key=lambda x: (abs(x), x)))


def canonical_source(source):
    return tuple(sorted(_norm_clause(c) for c in source))


def source_hash(source):
    raw = json.dumps([list(c) for c in canonical_source(source)], separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def verify_root_witness(source, witness, n):
    full = {i: bool(witness.get(i, False)) for i in range(1, int(n) + 1)}
    return all(any(full[abs(l)] == (l > 0) for l in c) for c in canonical_source(source))


def _typed_state(source):
    state = make_state(source)
    for kind in MORPH_SEQUENCE:
        proposal = propose_extract(state, kind)
        if not verify_proposal(state, proposal):
            return None
        state = commit_proposal(state, proposal)
    return state if verify_full_recomposition(state) else None


def _module_forest_certificate(state, source, n):
    modules = discover_modules(state)
    interaction = build_interaction(modules)
    if interaction["status"] != "FOREST":
        return None, {"module_status": interaction["status"]}
    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    boundary = {m["id"]: set() for m in modules}
    for (a, b), vs in interaction["edge_vars"].items():
        boundary[a].update(vs)
        boundary[b].update(vs)
    too_wide = {mid: sorted(vs) for mid, vs in boundary.items() if len(vs) > budget}
    if too_wide:
        return None, {"module_status": "OPEN_INTERFACE_WIDTH", "budget": budget}
    cert = {
        "module_status": "FOREST",
        "module_count": len(modules),
        "budget": budget,
        "max_boundary": max((len(v) for v in boundary.values()), default=0),
    }
    return cert, cert


def _factor_tree_certificate(state, source, n):
    modules = discover_modules(state)
    shared, adj = build_factor_graph(modules)
    seen = set()
    for start in sorted(adj):
        if start in seen:
            continue
        stack = [(start, None)]
        while stack:
            node, parent = stack.pop()
            if node in seen:
                return None, {"factor_status": "OPEN_FACTOR_GRAPH_CYCLE"}
            seen.add(node)
            for nxt in sorted(adj[node], reverse=True):
                if nxt != parent:
                    stack.append((nxt, node))
    L = encoding_size(source, n)
    budget = int(math.floor(math.log2(max(2, L))))
    boundary = {
        m["id"]: {v for v, mids in shared.items() if m["id"] in mids}
        for m in modules
    }
    too_wide = {mid: sorted(vs) for mid, vs in boundary.items() if len(vs) > budget}
    if too_wide:
        return None, {"factor_status": "OPEN_INTERFACE_WIDTH", "budget": budget}
    cert = {
        "factor_status": "FACTOR_FOREST",
        "module_count": len(modules),
        "shared_variable_count": len(shared),
        "max_variable_degree": max((len(ms) for ms in shared.values()), default=0),
        "max_module_boundary": max((len(vs) for vs in boundary.values()), default=0),
        "budget": budget,
    }
    return cert, cert


def akinator_propose(source, n):
    source = canonical_source(source)
    root_hash = source_hash(source)
    card = recognize_complete_negative_triples(source)
    if card is not None:
        return {"door": CARD, "root_hash": root_hash,
                "evidence": {"k": card["k"], "variables": list(card["variables"])}}
    kind = classify_source(source)
    if kind != "GENERAL_3CNF":
        return {"door": DIRECT, "root_hash": root_hash, "evidence": {"source_class": kind}}
    state = _typed_state(source)
    if state is None:
        return {"door": None, "root_hash": root_hash,
                "evidence": {"reason": "TYPED_RECOMPOSITION_FAILED"}}
    forest, forest_diag = _module_forest_certificate(state, source, n)
    if forest is not None:
        return {"door": FOREST, "root_hash": root_hash, "evidence": forest}
    factor, factor_diag = _factor_tree_certificate(state, source, n)
    if factor is not None:
        return {"door": FACTOR, "root_hash": root_hash, "evidence": factor}
    return {
        "door": None,
        "root_hash": root_hash,
        "evidence": {"forest": forest_diag, "factor": factor_diag},
    }


def captain_verify(source, n, proposal):
    expected = akinator_propose(source, n)
    ok = proposal == expected and proposal.get("root_hash") == source_hash(source)
    return {
        "status": "ADMIT" if ok else "REJECT",
        "expected": expected,
        "received": proposal,
    }


def _direct_execute(source, n, proposal):
    kind = proposal["evidence"]["source_class"]
    solved = solve_source(source, int(n), kind)
    if solved["sat"] is True:
        return {"status": "CERTIFIED_SAT_NATIVE", "witness": solved["witness"], "class": kind}
    if solved["sat"] is False:
        return {"status": "CERTIFIED_UNSAT_NATIVE", "witness": None, "class": kind}
    return {"status": "OPEN_NATIVE_MISMATCH", "class": kind}


def _cardinality_execute(source, n):
    carrier = recognize_complete_negative_triples(source)
    if carrier is None:
        return {"status": "MORPH_FAIL_CARDINALITY_REPLAY"}
    witness = {i: False for i in range(1, int(n) + 1)}
    return {
        "status": "CERTIFIED_SAT_CARDINALITY",
        "witness": witness,
        "carrier": {"kind": carrier["kind"], "k": carrier["k"],
                    "variables": list(carrier["variables"])},
    }


def janus_demiurge_execute(source, n, proposal):
    door = proposal["door"]
    if door == DIRECT:
        return _direct_execute(source, n, proposal)
    if door == CARD:
        return _cardinality_execute(source, n)
    if door == FOREST:
        return compile_typed_module_forest(source, int(n))
    if door == FACTOR:
        return compile_factor_tree_hyperedge(source, int(n))
    return {"status": "OPEN_UNAUTHORIZED_DOOR"}


SAT_STATUSES = {
    "CERTIFIED_SAT_NATIVE",
    "CERTIFIED_SAT_CARDINALITY",
    "CERTIFIED_SAT_MODULE_FOREST",
    "CERTIFIED_SAT_FACTOR_TREE",
}
UNSAT_BY_DOOR = {
    DIRECT: "CERTIFIED_UNSAT_NATIVE",
    FOREST: "CERTIFIED_UNSAT_MODULE_FOREST",
    FACTOR: "CERTIFIED_UNSAT_FACTOR_TREE",
}


def janus_sovereign_decide(source, n, proposal, captain, execution):
    root_hash = source_hash(source)
    if captain.get("status") != "ADMIT":
        return {"decision": "ROLLBACK_CAPTAIN_REJECT", "authority_root_hash": root_hash}
    if proposal.get("root_hash") != root_hash:
        return {"decision": "HALT_INTERNAL_MISMATCH", "reason": "ROOT_HASH_DRIFT"}
    status = execution.get("status")
    if status in SAT_STATUSES:
        witness = execution.get("witness") or {}
        if not verify_root_witness(source, witness, n):
            return {"decision": "HALT_INTERNAL_MISMATCH", "reason": "BAD_ROOT_WITNESS"}
        return {"decision": "COMMIT_SAT", "authority_root_hash": root_hash,
                "witness": {int(k): bool(v) for k, v in witness.items()}}
    expected_unsat = UNSAT_BY_DOOR.get(proposal.get("door"))
    if status == expected_unsat and expected_unsat is not None:
        return {"decision": "COMMIT_UNSAT", "authority_root_hash": root_hash,
                "certificate_status": status}
    return {"decision": "OPEN_UNKNOWN_STATE_CLASS", "authority_root_hash": root_hash,
            "demiurge_status": status}


def run_trinity(source, n, forced_proposal=None):
    source = canonical_source(source)
    root_hash = source_hash(source)
    proposed = akinator_propose(source, n)
    trace = [{"role": "AKINATOR", "proposal": proposed}]
    if proposed.get("door") is None and forced_proposal is None:
        sovereign = {"decision": "OPEN_UNKNOWN_STATE_CLASS",
                     "authority_root_hash": root_hash,
                     "evidence": proposed.get("evidence", {})}
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
        "schema": "JANUS_TRUMP_APMA_TRINITY_SOVEREIGN_FIRST_RUN_V1",
        "root_hash": source_hash(source),
        "n": int(n),
        "proposal": proposal,
        "captain": captain,
        "demiurge": execution,
        "sovereign": sovereign,
        "trace": trace,
        "scientific_status": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "Pi_negative_evidence_weight": 0,
        },
    }
