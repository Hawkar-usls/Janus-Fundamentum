#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole

CAPTURED: base.EngineState | None = None
ORIGINAL = v2.discover_macro_restore_v2
BLOCKS = ((23, 24, 25), (26, 27, 28), (29, 30, 31), (32, 33, 34))


def capture(state: base.EngineState):
    global CAPTURED
    out = ORIGINAL(state)
    if out is None and not any(v in set(state.root_vars) for v in base.vars_of(state.residual)):
        CAPTURED = state
    return out


def block_values(a_bit: int, e_bit: int) -> dict[int, int]:
    # Exact inverse coordinates under the witnessed block gates:
    #   b -> not a, c -> a, e <-> (b OR c)
    # hence b = e AND not a, c = e AND a.
    return {
        0: int(a_bit),
        1: int(e_bit and not a_bit),
        2: int(e_bit and a_bit),
    }


def transform_clause(clause: base.Clause, a: int, b: int, c: int, e: int):
    """Exact clause rewrite under (a,b,c) <-> (a,e).

    For each assignment alpha=(a,e), evaluate the local literals from variables
    {a,b,c}.  If the local part is already true, this clause imposes no condition
    on the remaining variables at alpha.  Otherwise emit the implication
      alpha -> OR(rest)
    as one CNF clause block(alpha) OR rest.

    There are only 4 alpha values, so this replay is constant local work per
    source clause and never needs to materialize Davis-Putnam resolvents.
    """
    local_vars = {a, b, c}
    rest = tuple(l for l in clause if abs(l) not in local_vars)
    local = tuple(l for l in clause if abs(l) in local_vars)
    pos = {a: 0, b: 1, c: 2}
    emitted = []

    for abit in (0, 1):
        for ebit in (0, 1):
            vals = block_values(abit, ebit)
            local_true = False
            for lit in local:
                bit = vals[pos[abs(lit)]]
                if bit == int(lit > 0):
                    local_true = True
                    break
            if local_true:
                continue

            # Negation of the exact coordinate assignment alpha.
            block = [(-a if abit else a), (-e if ebit else e)]
            cc = base.canon_clause([*block, *rest])
            if cc is not None:
                emitted.append(cc)
    return emitted


def apply_direct_block_coordinate(cnf: base.CNF, block: tuple[int, int, int], e: int):
    a, b, c = block
    live = set(base.vars_of(cnf))
    if e in live or e <= max(live, default=0):
        raise ValueError("coordinate extension must be fresh and topologically greater")
    if not {a, b, c} <= live:
        raise ValueError("block not live")

    left_gate = base.canon_clause((-a, -b))
    right_gate = base.canon_clause((a, -c))
    if left_gate not in cnf or right_gate not in cnf:
        raise ValueError("required selector gates absent")

    out_clauses = []
    emitted_count = 0
    for clause in cnf:
        rows = transform_clause(clause, a, b, c, e)
        emitted_count += len(rows)
        out_clauses.extend(rows)
    out = base.canon_cnf(out_clauses)

    cert = {
        "kind": "BLOCK_COORDINATE_CHANGE_3_TO_2",
        "block": [a, b, c],
        "extension": e,
        "coordinate_map": {
            "e": "b OR c",
            "b": "e AND NOT a",
            "c": "e AND a",
        },
        "gate_witnesses": [list(left_gate), list(right_gate)],
        "source_clause_count": len(cnf),
        "raw_emitted_clause_count": emitted_count,
        "before_fingerprint": base.fingerprint(cnf),
        "after_fingerprint": base.fingerprint(out),
    }
    return out, cert


def verify_direct_block_coordinate(before: base.CNF, after: base.CNF, cert: dict) -> bool:
    try:
        block = tuple(int(x) for x in cert["block"])
        e = int(cert["extension"])
        rebuilt, rc = apply_direct_block_coordinate(before, block, e)
        return (
            rebuilt == after
            and rc["before_fingerprint"] == cert["before_fingerprint"]
            and rc["after_fingerprint"] == cert["after_fingerprint"]
            and rc["gate_witnesses"] == cert["gate_witnesses"]
            and rc["coordinate_map"] == cert["coordinate_map"]
        )
    except (KeyError, TypeError, ValueError):
        return False


def local_bijection_selftest() -> None:
    # All gated (a,b,c) states map bijectively to all four (a,e) states.
    seen = {}
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                gates = ((not a) or (not b)) and (a or (not c))
                if not gates:
                    continue
                e = int(bool(b or c))
                key = (a, e)
                assert key not in seen
                seen[key] = (a, b, c)
                inv = block_values(a, e)
                assert (inv[0], inv[1], inv[2]) == (a, b, c)
    assert set(seen) == {(0, 0), (0, 1), (1, 0), (1, 1)}


def main() -> None:
    global CAPTURED
    local_bijection_selftest()

    old = v2.discover_macro_restore_v2
    v2.discover_macro_restore_v2 = capture
    try:
        result = v2.solve_fail_closed_v2(pigeonhole(5, 4), cap_exponent=1, extension_exponent=1)
    finally:
        v2.discover_macro_restore_v2 = old

    assert result["status"] == "OPEN" and CAPTURED is not None
    state = CAPTURED
    start = state.residual
    cap = state.state_cap
    start_phi = state.progress_phi()
    start_units = base.state_units(start)

    single_rows = []
    for block in BLOCKS:
        e = max(base.vars_of(start)) + 1
        out, cert = apply_direct_block_coordinate(start, block, e)
        assert verify_direct_block_coordinate(start, out, cert)
        row = {
            "block": list(block),
            "extension": e,
            "after_units": base.state_units(out),
            "under_cap": base.state_units(out) <= cap,
            "after_live_variables": list(base.vars_of(out)),
            "after_live_variable_count": len(base.vars_of(out)),
            "phi_after": state.progress_phi(out, state.ledger.extension_count + 1),
            "strict_phi_drop": state.progress_phi(out, state.ledger.extension_count + 1) < start_phi,
            "certificate_replay": True,
            "raw_emitted_clause_count": cert["raw_emitted_clause_count"],
            "after_fingerprint": base.fingerprint(out),
        }
        single_rows.append(row)

    # One streaming proof object for the full exact S4 orbit.  Each substep is a
    # separately replayable 3->2 coordinate change; unlike materializing four
    # selector definitions at once, we retain only the current state.
    cur = start
    orbit_subcerts = []
    orbit_states = []
    next_e = max(base.vars_of(cur)) + 1
    for block in BLOCKS:
        out, cert = apply_direct_block_coordinate(cur, block, next_e)
        assert verify_direct_block_coordinate(cur, out, cert)
        units = base.state_units(out)
        phi = state.progress_phi(out, state.ledger.extension_count + len(orbit_subcerts) + 1)
        orbit_subcerts.append(cert)
        orbit_states.append({
            "block": list(block),
            "extension": next_e,
            "units": units,
            "under_cap": units <= cap,
            "phi": phi,
            "live_variable_count": len(base.vars_of(out)),
            "fingerprint": base.fingerprint(out),
        })
        if units > cap:
            cur = out
            break
        cur = out
        next_e = max(base.vars_of(cur)) + 1

    streaming_complete = len(orbit_states) == 4 and all(x["under_cap"] for x in orbit_states)
    final_phi = orbit_states[-1]["phi"] if orbit_states else start_phi

    report = {
        "schema": "JANUS/C025/PHP54-DIRECT-BLOCK-COORDINATE-GATE/v1",
        "P_VS_NP": "OPEN",
        "fingerprint": base.fingerprint(start),
        "state_cap": cap,
        "start_units": start_units,
        "start_phi": start_phi,
        "local_bijection": {
            "gates": ["(-a OR -b)", "(a OR -c)"],
            "forward": "e = b OR c",
            "inverse": ["b = e AND NOT a", "c = e AND a"],
            "valid_abc_states": 4,
            "ae_states": 4,
            "exact": True,
        },
        "single_block_coordinate_change": {
            "rows": single_rows,
            "strict_drop_count": sum(1 for x in single_rows if x["strict_phi_drop"] and x["under_cap"]),
        },
        "whole_orbit_streaming_certificate": {
            "kind": "S4_ORBIT_STREAMING_BLOCK_COORDINATE_CERTIFICATE",
            "subcertificates": len(orbit_subcerts),
            "states": orbit_states,
            "complete_under_cap": streaming_complete,
            "final_units": base.state_units(cur),
            "final_phi": final_phi,
            "phi_drop": start_phi - final_phi,
            "final_live_variables": list(base.vars_of(cur)),
            "final_live_variable_count": len(base.vars_of(cur)),
            "certificate_replay": all(
                cert["after_fingerprint"] == orbit_states[i]["fingerprint"]
                for i, cert in enumerate(orbit_subcerts)
            ),
        },
        "interpretation_gate": {
            "if_single_block_under_cap_and_drop": "DIRECT_COORDINATE_CHANGE_BYPASSES_RESOLUTION_BLOWUP_AND_GIVES_DEBT_FREE_PROGRESS_ON_FROZEN_TAIL",
            "if_streaming_complete": "ONE_STREAMING_CERTIFICATE_COMPRESSES_THE_ENTIRE_EXACT_S4_ORBIT_WITH_ALL_RETAINED_STATES_UNDER_THE_SAME_C1_CAP",
            "if_single_block_over_cap": "SEMANTIC_3_TO_2_BIJECTION_EXISTS_BUT_EVEN_DIRECT_PROOF_CARRYING_COORDINATE_CHANGE_EXCEEDS_C1",
            "claim_firewall": "FINITE_BLOCK_COORDINATE_SUCCESS_DOES_NOT_PROVE_UNIVERSAL_DISCOVERY_OR_P_EQUALS_NP",
        },
        "scientific_boundary": {
            "finite_attack_only": True,
            "fixed_frozen_residual": True,
            "constant_local_truth_table_rewrite": True,
            "no_sat_oracle": True,
            "no_semantic_equivalence_oracle": True,
            "no_resolution_intermediate_for_removed_pair": True,
            "universal_block_discovery": "OPEN",
            "universal_cap_availability": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
