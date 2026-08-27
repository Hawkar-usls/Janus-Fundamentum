#!/usr/bin/env python3
"""Exhaustive forward census of every normalized legitimate root with N=12.

This is a finite exact theorem-run for ONE input-size layer only.  It enumerates
all canonical nonempty roots over consecutive normalized variable IDs 1..r with

    input_size_units(root) == 12

and full variable coverage, then runs the frozen v3 solver on every root.
Order-preserving renaming from arbitrary positive IDs to 1..r preserves the
frozen pivot order and fresh-extension topology, so this is complete up to the
irrelevant numeric gaps between variable IDs.

If OPEN_COUNT=0, frozen v3 totality is established only for N=12, not for
unbounded N. P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter
from itertools import product
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v3 as v3

TARGET_N = 12
P_VS_NP = "OPEN"


def clause_universe(r: int) -> tuple[base.Clause, ...]:
    rows = []
    for choices in product((-1, 0, 1), repeat=r):
        if all(x == 0 for x in choices):
            continue
        c = tuple((i + 1) * (1 if s > 0 else -1) for i, s in enumerate(choices) if s)
        cc = base.canon_clause(c)
        if cc is not None and cc:
            rows.append(cc)
    return tuple(sorted(set(rows), key=lambda c: (len(c), c)))


def canonical_roots_for_r(r: int) -> tuple[base.CNF, ...]:
    """Enumerate every canonical full-coverage root with input N=12."""
    U = clause_universe(r)
    weights = tuple(1 + len(c) for c in U)
    target_clause_units = TARGET_N - r - 1
    found: set[base.CNF] = set()

    def rec(start: int, remaining: int, chosen: list[base.Clause], covered: set[int]) -> None:
        if remaining == 0:
            if covered != set(range(1, r + 1)):
                return
            cnf = base.canon_cnf(chosen)
            if not cnf:
                return
            if base.vars_of(cnf) != tuple(range(1, r + 1)):
                return
            if base.input_size_units(cnf) != TARGET_N:
                return
            # Canonicalization must not have changed the selected antichain's
            # encoding budget; otherwise this raw selection belongs to smaller N.
            if sum(1 + len(c) for c in cnf) != target_clause_units:
                return
            found.add(cnf)
            return
        if remaining < 0:
            return

        for i in range(start, len(U)):
            w = weights[i]
            if w > remaining:
                continue
            c = U[i]
            cs = set(c)
            # Prune noncanonical supersets/subsets early. Canonical CNF keeps an
            # antichain under literal-set inclusion.
            bad = False
            for p in chosen:
                ps = set(p)
                if ps <= cs or cs <= ps:
                    bad = True
                    break
            if bad:
                continue
            rec(i + 1, remaining - w, [*chosen, c], covered | {abs(x) for x in c})

    rec(0, target_clause_units, [], set())
    return tuple(sorted(found, key=lambda f: (len(f), f)))


def enumerate_all_roots() -> dict[int, tuple[base.CNF, ...]]:
    # From N>=2r+2, r<=5 at N=12. r=0 is terminal/empty and has N=2, not 12.
    return {r: canonical_roots_for_r(r) for r in range(1, 6)}


def main() -> int:
    by_r = enumerate_all_roots()
    counts_by_r = {str(r): len(rows) for r, rows in by_r.items()}
    all_roots = [f for r in sorted(by_r) for f in by_r[r]]

    statuses: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    extension_count_hist: Counter[int] = Counter()
    v3_tail_event_roots = 0
    macro_restore_roots = 0
    first_open = None
    first_open_result = None
    max_residual_units = 0
    max_extension_count = 0

    for idx, root in enumerate(all_roots):
        if base.input_size_units(root) != TARGET_N:
            raise AssertionError("ENUMERATOR_EMITTED_WRONG_N")
        result = v3.solve_fail_closed_v3(root)
        status = str(result["status"])
        reason = str(result["reason"])
        statuses[status] += 1
        reasons[reason] += 1
        ext_count = int(result["ledger"].get("extension_count", 0))
        extension_count_hist[ext_count] += 1
        max_extension_count = max(max_extension_count, ext_count)
        max_residual_units = max(max_residual_units, int(result["residual_units"]))
        kinds = [e.get("kind") for e in result.get("events", [])]
        if "JEC_MACRO_RESTORE_CAP" in kinds:
            macro_restore_roots += 1
        if "JEC_EXTENSION_TAIL_DESCENT_V3" in kinds:
            v3_tail_event_roots += 1
        if status == "OPEN" and first_open is None:
            first_open = {
                "index": idx,
                "root": root,
                "root_fingerprint": base.fingerprint(root),
                "reason": reason,
                "residual_fingerprint": result["residual_fingerprint"],
                "residual_units": result["residual_units"],
                "events": result.get("events", []),
            }
            first_open_result = result

    report = {
        "schema": "JANUS/C025/V3-EXHAUSTIVE-LEGITIMATE-ROOTS-N12/v1",
        "N": TARGET_N,
        "normalized_variable_ids": True,
        "counts_by_root_var_count": counts_by_r,
        "total_roots": len(all_roots),
        "status_counts": dict(sorted(statuses.items())),
        "reason_counts": dict(sorted(reasons.items())),
        "extension_count_histogram": {str(k): v for k, v in sorted(extension_count_hist.items())},
        "roots_using_v2_macro_restore": macro_restore_roots,
        "roots_using_v3_tail": v3_tail_event_roots,
        "max_terminal_residual_units": max_residual_units,
        "max_extension_count": max_extension_count,
        "first_open": first_open,
        "first_open_full_result": first_open_result,
        "finite_totality_N12": first_open is None,
        "scientific_boundary": {
            "exhaustive_only_for_N12": True,
            "order_preserving_variable_renaming_only": True,
            "finite_totality_does_not_imply_asymptotic_totality": True,
            "no_open_at_N12_does_not_prove_universal_availability": True,
            "heuristic_or_predictive_layer_has_theorem_authority": False,
            "P_VS_NP": P_VS_NP,
        },
    }
    report["status"] = "FINITE_TOTALITY_N12_PASS" if first_open is None else "REACHABLE_OPEN_N12_FOUND"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
