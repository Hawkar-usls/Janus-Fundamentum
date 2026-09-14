import hashlib, json

from research.tools.apma_dense_cardinality.apma_dense_cardinality import recognize_complete_negative_triples
from research.tools.apma_ss_provenance.apma_ss_controller import classify_source, solve_source
from research.tools.apma_typed_module_forest.module_forest import compile_typed_module_forest
from research.tools.apma_factor_tree_hyperedge.factor_tree import compile_factor_tree_hyperedge
from research.tools.apma_cycle_cut.cycle_cut import compile_canonical_cycle_cut
from research.tools.apma_symbolic_projection.symbolic_projection import compile_symbolic_typed_boundary_projection
from research.tools.apma_renamable_horn.renamable_horn import compile_renamable_horn

DIRECT = "DIRECT_NATIVE_2CNF_HORN_DUAL_HORN"
CARD = "COMPLETE_NEGATIVE_TRIPLES_TO_AT_MOST_2"
FOREST = "TYPED_MODULE_FOREST"
FACTOR = "FACTOR_TREE_HYPEREDGE"
CYCLE = "CANONICAL_CYCLE_CUT"
SYMBOLIC = "SYMBOLIC_TYPED_BOUNDARY_PROJECTION"
RENAMABLE = "RENAMABLE_HORN"

FROZEN_DOOR_ORDER = (DIRECT, CARD, FOREST, FACTOR, CYCLE, SYMBOLIC, RENAMABLE)
IMPORT_PROVENANCE = {
    CYCLE: {"sealed_commit": "a9cb1f86932d66d7b22e428b301de1dcfbce5617", "git_blob_sha1": "899ca44ab8850dff66dd6afff22f0f5dc74897c4"},
    SYMBOLIC: {"sealed_commit": "c06cefad1b11e0843adda70cfa2c13dd03fafb69", "git_blob_sha1": "1da70f106692ce0a93103b27289b0dc7ea86977e"},
    RENAMABLE: {"sealed_commit": "0a82218997096ada4f7489e47f412dd2b480b149", "git_blob_sha1": "b9aa81086cc65c14571b42c879f2bdbf63bbb11b"},
}


def _norm_clause(c):
    return tuple(sorted((int(x) for x in c), key=lambda x: (abs(x), x)))


def canonical_source(source):
    return tuple(sorted(_norm_clause(c) for c in source))


def source_hash(source):
    raw = json.dumps([list(c) for c in canonical_source(source)], separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def verify_root_witness(source, witness, n):
    full = {i: bool((witness or {}).get(i, (witness or {}).get(str(i), False))) for i in range(1, int(n) + 1)}
    return all(any(full[abs(l)] == (l > 0) for l in c) for c in canonical_source(source))


def akinator_propose(source, n):
    return {
        "schema": "APMA_TRINITY_V2_FIXED_AUTHORIZED_PORTFOLIO",
        "root_hash": source_hash(source),
        "n": int(n),
        "door_order": list(FROZEN_DOOR_ORDER),
        "import_provenance": IMPORT_PROVENANCE,
    }


def captain_verify(source, n, proposal):
    expected = akinator_propose(source, n)
    return {
        "status": "ADMIT" if proposal == expected else "REJECT",
        "expected": expected,
        "received": proposal,
    }


def _direct_execute(source, n):
    kind = classify_source(source)
    if kind == "GENERAL_3CNF":
        return {"status": "OPEN_NOT_NATIVE_CLASS", "class": kind}
    solved = solve_source(source, int(n), kind)
    if solved["sat"] is True:
        return {"status": "CERTIFIED_SAT_NATIVE", "witness": solved["witness"], "class": kind}
    if solved["sat"] is False:
        return {"status": "CERTIFIED_UNSAT_NATIVE", "class": kind}
    return {"status": "OPEN_NATIVE_MISMATCH", "class": kind}


def _cardinality_execute(source, n):
    carrier = recognize_complete_negative_triples(source)
    if carrier is None:
        return {"status": "OPEN_NOT_COMPLETE_NEGATIVE_TRIPLES"}
    witness = {i: False for i in range(1, int(n) + 1)}
    return {"status": "CERTIFIED_SAT_CARDINALITY", "witness": witness,
            "carrier": {"kind": carrier["kind"], "k": carrier["k"], "variables": list(carrier["variables"])}}


def execute_door(door, source, n):
    if door == DIRECT:
        return _direct_execute(source, n)
    if door == CARD:
        return _cardinality_execute(source, n)
    if door == FOREST:
        return compile_typed_module_forest(source, int(n))
    if door == FACTOR:
        return compile_factor_tree_hyperedge(source, int(n))
    if door == CYCLE:
        return compile_canonical_cycle_cut(source, int(n))
    if door == SYMBOLIC:
        return compile_symbolic_typed_boundary_projection(source, int(n))
    if door == RENAMABLE:
        return compile_renamable_horn(source, int(n))
    return {"status": "OPEN_UNAUTHORIZED_DOOR"}


SAT_STATUSES = {
    "CERTIFIED_SAT_NATIVE", "CERTIFIED_SAT_CARDINALITY",
    "CERTIFIED_SAT_MODULE_FOREST", "CERTIFIED_SAT_FACTOR_TREE",
    "CERTIFIED_SAT_CANONICAL_CYCLE_CUT", "CERTIFIED_SAT_SYMBOLIC_PROJECTION",
    "CERTIFIED_SAT_RENAMABLE_HORN",
}
UNSAT_STATUSES = {
    "CERTIFIED_UNSAT_NATIVE", "CERTIFIED_UNSAT_MODULE_FOREST",
    "CERTIFIED_UNSAT_FACTOR_TREE", "CERTIFIED_UNSAT_CANONICAL_CYCLE_CUT",
    "CERTIFIED_UNSAT_SYMBOLIC_PROJECTION", "CERTIFIED_UNSAT_RENAMABLE_HORN",
}


def run_trinity_v2(source, n, forced_proposal=None):
    source = canonical_source(source)
    root_hash = source_hash(source)
    proposed = akinator_propose(source, n)
    candidate = forced_proposal if forced_proposal is not None else proposed
    trace = [{"role": "AKINATOR", "proposal": proposed}]
    captain = captain_verify(source, n, candidate)
    trace.append({"role": "CAPTAIN_OBVIOUS", "result": captain["status"]})
    if captain["status"] != "ADMIT":
        sovereign = {"decision": "ROLLBACK_CAPTAIN_REJECT", "authority_root_hash": root_hash}
        trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
        return _final(source, n, candidate, captain, [], sovereign, trace)

    attempts = []
    for door in candidate["door_order"]:
        execution = execute_door(door, source, n)
        status = execution.get("status")
        attempts.append({"door": door, "status": status, "execution": execution})
        trace.append({"role": "JANUS_DEMIURGE", "door": door, "status": status})
        if status in SAT_STATUSES:
            witness = execution.get("witness") or {}
            if not verify_root_witness(source, witness, n):
                sovereign = {"decision": "HALT_INTERNAL_MISMATCH", "reason": "BAD_ROOT_WITNESS", "authority_root_hash": root_hash}
            else:
                sovereign = {"decision": "COMMIT_SAT", "authority_root_hash": root_hash, "door": door,
                             "certificate_status": status,
                             "witness": {int(k): bool(v) for k, v in witness.items()}}
            trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
            return _final(source, n, candidate, captain, attempts, sovereign, trace)
        if status in UNSAT_STATUSES:
            sovereign = {"decision": "COMMIT_UNSAT", "authority_root_hash": root_hash,
                         "door": door, "certificate_status": status}
            trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
            return _final(source, n, candidate, captain, attempts, sovereign, trace)

    sovereign = {
        "decision": "OPEN_UNKNOWN_STATE_CLASS",
        "authority_root_hash": root_hash,
        "portfolio_falsifier": True,
        "attempted_door_count": len(attempts),
        "attempted_doors": [a["door"] for a in attempts],
    }
    trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
    return _final(source, n, candidate, captain, attempts, sovereign, trace)


def _final(source, n, proposal, captain, attempts, sovereign, trace):
    return {
        "schema": "JANUS_TRUMP_APMA_TRINITY_EXECUTABLE_PORTFOLIO_V2",
        "root_hash": source_hash(source),
        "n": int(n),
        "proposal": proposal,
        "captain": captain,
        "attempts": attempts,
        "sovereign": sovereign,
        "trace": trace,
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
    }
