#!/usr/bin/env python3
import itertools, json
from janus_trump_r44_exact_representation_switchboard import dispatch, norm, verify_assignment

cnf = norm([
    [1,2,3],[1,2,-3],[1,-2,3],[1,-2,-3],
    [-1,2,3],[-1,2,-3],[-1,-2,3],[-1,-2,-3],
])

route, result, ledger = dispatch(cnf)
assert route is None, route
assert result["status"] == "OPEN_OUTSIDE_SWITCHBOARD"
assert result["decision_authority"] is False

# Independent semantic audit: every assignment to 1,2,3 falsifies the CNF.
assignment_rows = []
for bits in itertools.product([False, True], repeat=3):
    a = {1: bits[0], 2: bits[1], 3: bits[2]}
    sat = verify_assignment(cnf, a)
    assert sat is False
    falsified = [i for i,c in enumerate(cnf) if not any(a[abs(l)] == (l > 0) for l in c)]
    assert len(falsified) == 1
    assignment_rows.append({"assignment": [int(x) for x in bits], "falsified_clause_index": falsified[0]})

# Structural route exclusions independent of the dispatcher result.
assert all(len(c) == 3 for c in cnf)
assert any(sum(1 for l in c if l > 0) > 1 for c in cnf)
assert any(sum(1 for l in c if l < 0) > 1 for c in cnf)
assert len(cnf) == 8
assert len({tuple(sorted(abs(x) for x in c)) for c in cnf}) == 1

print(json.dumps({
    "gate_id": "R44C_UNIVERSAL_TOTALITY_OR_EXPLICIT_OBSTRUCTION",
    "status": "EXPLICIT_OBSTRUCTION_VERIFIED",
    "obstruction_id": "FULL_3_VARIABLE_CLAUSE_CUBE",
    "dispatcher_route": route,
    "dispatcher_status": result["status"],
    "decision_authority": False,
    "semantic_audit": "UNSAT_BY_COMPLETE_ASSIGNMENT_BLOCKING_CUBE",
    "assignment_rows": assignment_rows,
    "ledger": ledger,
    "U1_current_frozen_switchboard": "REFUTED",
    "U1_all_future_algorithms": "OPEN",
    "P_EQUALS_NP": "NOT_PROVED",
    "P_NE_NP": "NOT_PROVED",
    "P_VS_NP": "OPEN",
    "next_gate": "R44D_OBSTRUCTION_CONSUMPTION_AND_FRESH_RESIDUAL_SEARCH"
}, sort_keys=True))
