import json

from research.tools.apma_trinity_sovereign.trinity_v2 import (
    canonical_source,
    source_hash,
    verify_root_witness,
    FROZEN_DOOR_ORDER as V2_DOOR_ORDER,
    IMPORT_PROVENANCE as V2_IMPORT_PROVENANCE,
    execute_door as execute_v2_door,
    SAT_STATUSES as V2_SAT_STATUSES,
    UNSAT_STATUSES as V2_UNSAT_STATUSES,
)
from research.tools.apma_dense_bipartite_grid.dense_bipartite_grid import compile_dense_bipartite_grid

DENSE = "DENSE_BIPARTITE_GRID"
FROZEN_DOOR_ORDER = tuple(V2_DOOR_ORDER) + (DENSE,)
IMPORT_PROVENANCE = dict(V2_IMPORT_PROVENANCE)
IMPORT_PROVENANCE[DENSE] = {
    "sealed_commit": "45140abcc163fd99d67c0b94e6fa37d9d6e023e2",
    "git_blob_sha1": "243ee05b8f34c1b67bc5cb14fba5ecbd990ae7f8",
}
SAT_STATUSES = set(V2_SAT_STATUSES) | {"CERTIFIED_SAT_DENSE_BIPARTITE_GRID"}
UNSAT_STATUSES = set(V2_UNSAT_STATUSES)


def akinator_propose(source, n):
    return {
        "schema": "APMA_TRINITY_V3_FIXED_AUTHORIZED_PORTFOLIO",
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


def execute_door(door, source, n):
    if door == DENSE:
        return compile_dense_bipartite_grid(source, int(n))
    return execute_v2_door(door, source, int(n))


def run_trinity_v3(source, n, forced_proposal=None):
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
                sovereign = {
                    "decision": "HALT_INTERNAL_MISMATCH",
                    "reason": "BAD_ROOT_WITNESS",
                    "authority_root_hash": root_hash,
                }
            else:
                sovereign = {
                    "decision": "COMMIT_SAT",
                    "authority_root_hash": root_hash,
                    "door": door,
                    "certificate_status": status,
                    "witness": {int(k): bool(v) for k, v in witness.items()},
                }
            trace.append({"role": "JANUS_SOVEREIGN", "result": sovereign})
            return _final(source, n, candidate, captain, attempts, sovereign, trace)
        if status in UNSAT_STATUSES:
            sovereign = {
                "decision": "COMMIT_UNSAT",
                "authority_root_hash": root_hash,
                "door": door,
                "certificate_status": status,
            }
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
        "schema": "JANUS_TRUMP_APMA_TRINITY_EXECUTABLE_PORTFOLIO_V3",
        "root_hash": source_hash(source),
        "n": int(n),
        "proposal": proposal,
        "captain": captain,
        "attempts": attempts,
        "sovereign": sovereign,
        "trace": trace,
        "scientific_status": {
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "Pi_negative_evidence_weight": 0,
        },
    }
