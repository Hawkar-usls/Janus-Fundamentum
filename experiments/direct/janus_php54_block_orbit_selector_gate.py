#!/usr/bin/env python3
from __future__ import annotations

from itertools import permutations
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


def exact_elim(cnf: base.CNF, pivot: int, cap: int):
    out, stats = base.eliminate_var_capped(cnf, pivot, cap)
    if out is None:
        return None, stats
    assert base.verify_elimination_transition(cnf, pivot, out, cap)
    return out, stats


def apply_selector_macro(cnf: base.CNF, a: int, b: int, c: int, e: int):
    """Conservative selector extension e <-> (b OR c).

    On the frozen PHP tail each block also contains the two gate clauses
      (-a OR -b)  and  (a OR -c),
    so b => -a and c => a.  Hence, once e is defined as b OR c, the pair
    (b,c) is uniquely recoverable from (a,e):
      a=0 -> b=e,c=0
      a=1 -> b=0,c=e.

    The extension itself is conservative even without the gate clauses; the
    gate witnesses explain why exact elimination of both b and c may be cheap.
    """
    live = set(base.vars_of(cnf))
    if e in live or e <= max(live, default=0):
        raise ValueError("selector extension must be fresh and topologically greater")
    if len({a, b, c}) != 3:
        raise ValueError("block variables must be distinct")

    defs = [(-b, e), (-c, e), (b, c, -e)]  # e <-> (b OR c)
    out = base.canon_cnf([*cnf, *defs])
    cert = {
        "kind": "B2_BLOCK_SELECTOR_OR",
        "block": [a, b, c],
        "extension": e,
        "selector": "e <-> (b OR c)",
        "left_gate": [-a, -b],
        "right_gate": [a, -c],
        "left_gate_present": base.canon_clause((-a, -b)) in cnf,
        "right_gate_present": base.canon_clause((a, -c)) in cnf,
        "before_fingerprint": base.fingerprint(cnf),
        "after_fingerprint": base.fingerprint(out),
    }
    return out, cert


def verify_selector_macro(before: base.CNF, after: base.CNF, cert: dict) -> bool:
    try:
        a, b, c = (int(x) for x in cert["block"])
        e = int(cert["extension"])
        rebuilt, rc = apply_selector_macro(before, a, b, c, e)
        return (
            rebuilt == after
            and rc["before_fingerprint"] == cert["before_fingerprint"]
            and rc["after_fingerprint"] == cert["after_fingerprint"]
            and rc["left_gate_present"] == cert["left_gate_present"]
            and rc["right_gate_present"] == cert["right_gate_present"]
        )
    except (KeyError, TypeError, ValueError):
        return False


def renamed(cnf: base.CNF, mapping: dict[int, int]) -> base.CNF:
    return base.canon_cnf(
        [tuple((mapping.get(abs(l), abs(l)) if l > 0 else -mapping.get(abs(l), abs(l))) for l in clause)
         for clause in cnf]
    )


def orbit_automorphism_report(cnf: base.CNF) -> dict:
    exact = []
    for perm in permutations(range(4)):
        mapping = {21: 21}
        for src_i, dst_i in enumerate(perm):
            for pos in range(3):
                mapping[BLOCKS[src_i][pos]] = BLOCKS[dst_i][pos]
        if renamed(cnf, mapping) == cnf:
            exact.append(list(perm))

    generators = []
    for left, right in ((0, 1), (1, 2), (2, 3)):
        perm = list(range(4))
        perm[left], perm[right] = perm[right], perm[left]
        mapping = {21: 21}
        for src_i, dst_i in enumerate(perm):
            for pos in range(3):
                mapping[BLOCKS[src_i][pos]] = BLOCKS[dst_i][pos]
        generators.append({"swap": [left, right], "exact": renamed(cnf, mapping) == cnf})

    return {
        "tested_block_permutations": 24,
        "exact_block_permutations": len(exact),
        "all_S4_exact": len(exact) == 24,
        "adjacent_swap_generators": generators,
        "exact_permutations": exact,
    }


def apply_orbit_batch(cnf: base.CNF, fresh_start: int):
    cur = cnf
    certs = []
    for i, (a, b, c) in enumerate(BLOCKS):
        cur, cert = apply_selector_macro(cur, a, b, c, fresh_start + i)
        certs.append(cert)
    return cur, {
        "kind": "B2_BLOCK_SELECTOR_ORBIT_BATCH",
        "blocks": [list(b) for b in BLOCKS],
        "extensions": list(range(fresh_start, fresh_start + 4)),
        "subcertificates": certs,
        "before_fingerprint": base.fingerprint(cnf),
        "after_fingerprint": base.fingerprint(cur),
    }


def main() -> None:
    global CAPTURED
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
    live = tuple(base.vars_of(start))
    assert set(live) == {21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34}

    fresh = max(live) + 1
    rows = []
    strict = []

    for block_index, (a, b, c) in enumerate(BLOCKS):
        macro, cert = apply_selector_macro(start, a, b, c, fresh)
        assert verify_selector_macro(start, macro, cert)
        macro_units = base.state_units(macro)
        row = {
            "block_index": block_index,
            "block": [a, b, c],
            "fresh": fresh,
            "gates_present": [cert["left_gate_present"], cert["right_gate_present"]],
            "macro_units": macro_units,
            "macro_under_cap": macro_units <= cap,
            "orders": [],
        }

        if macro_units <= cap:
            for order in ((b, c), (c, b)):
                s1, st1 = exact_elim(macro, order[0], cap)
                if s1 is None:
                    row["orders"].append({
                        "order": list(order),
                        "first_fit": False,
                        "second_fit": False,
                    })
                    continue
                s2, st2 = exact_elim(s1, order[1], cap)
                order_row = {
                    "order": list(order),
                    "first_fit": True,
                    "first_units": base.state_units(s1),
                    "first_pairs": int(st1.get("pairs", 0)),
                    "second_fit": s2 is not None,
                    "second_units": base.state_units(s2) if s2 is not None else None,
                    "second_pairs": int(st2.get("pairs", 0)) if s2 is not None else None,
                    "phi_after": state.progress_phi(s2, state.ledger.extension_count + 1) if s2 is not None else None,
                }
                row["orders"].append(order_row)
                if s2 is not None and order_row["phi_after"] < start_phi:
                    strict.append({
                        "block_index": block_index,
                        "block": [a, b, c],
                        "order": list(order),
                        "macro_units": macro_units,
                        "first_units": base.state_units(s1),
                        "second_units": base.state_units(s2),
                        "phi_after": order_row["phi_after"],
                        "after_fingerprint": base.fingerprint(s2),
                    })
        rows.append(row)

    batch, batch_cert = apply_orbit_batch(start, fresh)
    batch_units = base.state_units(batch)

    # Tiny truth-table sanity check for the selector definition itself.
    selector_truth_table_ok = True
    for b in (0, 1):
        for c in (0, 1):
            e = int(bool(b or c))
            clause_vals = [
                ((not b) or e),
                ((not c) or e),
                (b or c or (not e)),
            ]
            selector_truth_table_ok &= all(clause_vals)

    strict.sort(key=lambda x: (x["phi_after"], x["second_units"], x["block_index"], x["order"]))
    report = {
        "schema": "JANUS/C025/PHP54-BLOCK-ORBIT-SELECTOR-GATE/v1",
        "P_VS_NP": "OPEN",
        "fingerprint": base.fingerprint(start),
        "state_cap": cap,
        "start_units": base.state_units(start),
        "start_phi": start_phi,
        "selector_truth_table_ok": selector_truth_table_ok,
        "orbit_automorphism": orbit_automorphism_report(start),
        "single_block_selector": {
            "definition": "e <-> (b OR c) under witnessed gates b=>-a and c=>a",
            "rows": rows,
            "strict_phi_drop_plans": len(strict),
            "best_strict_phi_drop": strict[:16],
        },
        "whole_orbit_batch_certificate": {
            "kind": batch_cert["kind"],
            "extensions": batch_cert["extensions"],
            "units": batch_units,
            "under_cap": batch_units <= cap,
            "certificate_replay": batch_cert["before_fingerprint"] == base.fingerprint(start)
                                  and batch_cert["after_fingerprint"] == base.fingerprint(batch),
        },
        "interpretation_gate": {
            "if_single_block_strict_drop_positive": "DEBT_FREE_3_TO_2_BLOCK_SELECTOR_EXISTS_ON_FROZEN_TAIL; IMPLEMENT AS PROOF_CARRYING MACRO_RESTORE AND CONTINUE PHP_5_4_C1",
            "if_all_S4_exact": "THE_FOUR_TRIPLES_FORM_AN_EXACT_SYNTACTIC_BLOCK_ORBIT; ONE GENERATOR CERTIFICATE CAN VERIFY THE ORBIT SYMMETRY, BUT SYMMETRY ALONE DOES_NOT_LOWER_PHI",
            "if_batch_over_cap": "ONE_CERTIFICATE_MAY_BE_SMALL_WHILE_MATERIALIZING_ALL_ORBIT_EXTENSIONS_AT_ONCE_STILL_VIOLATES_THE_FROZEN_STATE_CAP",
            "if_no_single_block_drop": "THE_SIMPLE_SELECTOR_GRAMMAR_FAILS; SEARCH_A_RICHER_BLOCK_RELATION_WITHOUT_RELAXING_CAP_OR_EXACTNESS",
        },
        "scientific_boundary": {
            "finite_attack_only": True,
            "no_sat_oracle": True,
            "no_semantic_equivalence_oracle": True,
            "fixed_block_family": True,
            "heuristic_promotion": False,
            "universal_cap_availability": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
