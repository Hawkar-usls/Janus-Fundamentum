#!/usr/bin/env python3
"""Exhaustive frozen-v3 forward census for normalized legitimate roots N=13,14.

Finite exact size-layer census only.  Every canonical full-coverage root with
input_size_units(root)==N is enumerated up to order-preserving variable renaming
and replayed through the unchanged v3 solver.  Stop reporting only after both
layers are complete; any OPEN or first extension use is preserved explicitly.
P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter
from itertools import product
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v3 as v3

TARGETS = (13, 14)
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


def roots_for_layer(N: int, r: int) -> tuple[base.CNF, ...]:
    U = clause_universe(r)
    weights = tuple(1 + len(c) for c in U)
    target = N - r - 1
    found: set[base.CNF] = set()
    full = set(range(1, r + 1))

    def rec(start: int, remaining: int, chosen: list[base.Clause], covered: set[int]) -> None:
        if remaining == 0:
            if covered != full:
                return
            cnf = base.canon_cnf(chosen)
            if not cnf or base.vars_of(cnf) != tuple(range(1, r + 1)):
                return
            if base.input_size_units(cnf) != N:
                return
            if sum(1 + len(c) for c in cnf) != target:
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
            if any(set(p) <= cs or cs <= set(p) for p in chosen):
                continue
            rec(i + 1, remaining - w, [*chosen, c], covered | {abs(x) for x in c})

    rec(0, target, [], set())
    return tuple(sorted(found, key=lambda f: (len(f), f)))


def census(N: int) -> dict:
    rmax = (N - 2) // 2
    by_r = {r: roots_for_layer(N, r) for r in range(1, rmax + 1)}
    roots = [f for r in sorted(by_r) for f in by_r[r]]
    statuses: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    ext_hist: Counter[int] = Counter()
    roots_v2 = 0
    roots_v3 = 0
    first_open = None
    first_extension = None

    for idx, root in enumerate(roots):
        result = v3.solve_fail_closed_v3(root)
        statuses[result["status"]] += 1
        reasons[result["reason"]] += 1
        ext = int(result["ledger"].get("extension_count", 0))
        ext_hist[ext] += 1
        kinds = [e.get("kind") for e in result.get("events", [])]
        used_v2 = "JEC_MACRO_RESTORE_CAP" in kinds
        used_v3 = "JEC_EXTENSION_TAIL_DESCENT_V3" in kinds
        roots_v2 += int(used_v2)
        roots_v3 += int(used_v3)
        if ext > 0 and first_extension is None:
            first_extension = {
                "index": idx,
                "root": root,
                "root_fingerprint": base.fingerprint(root),
                "status": result["status"],
                "reason": result["reason"],
                "extension_count": ext,
                "used_v2": used_v2,
                "used_v3": used_v3,
                "events": result.get("events", []),
            }
        if result["status"] == "OPEN" and first_open is None:
            first_open = {
                "index": idx,
                "root": root,
                "root_fingerprint": base.fingerprint(root),
                "reason": result["reason"],
                "residual_fingerprint": result["residual_fingerprint"],
                "residual_units": result["residual_units"],
                "events": result.get("events", []),
            }

    return {
        "N": N,
        "counts_by_root_var_count": {str(r): len(v) for r, v in by_r.items()},
        "total_roots": len(roots),
        "status_counts": dict(sorted(statuses.items())),
        "reason_counts": dict(sorted(reasons.items())),
        "extension_count_histogram": {str(k): v for k, v in sorted(ext_hist.items())},
        "roots_using_v2_macro_restore": roots_v2,
        "roots_using_v3_tail": roots_v3,
        "first_extension": first_extension,
        "first_open": first_open,
        "finite_totality": first_open is None,
    }


def main() -> int:
    layers = [census(N) for N in TARGETS]
    first_extension_layer = next((x for x in layers if x["first_extension"] is not None), None)
    first_open_layer = next((x for x in layers if x["first_open"] is not None), None)
    report = {
        "schema": "JANUS/C025/V3-EXHAUSTIVE-LEGITIMATE-ROOT-LAYERS-13-14/v1",
        "layers": layers,
        "first_extension_layer": None if first_extension_layer is None else first_extension_layer["N"],
        "first_open_layer": None if first_open_layer is None else first_open_layer["N"],
        "scientific_boundary": {
            "exhaustive_only_for_listed_finite_layers": True,
            "order_preserving_variable_renaming_only": True,
            "finite_totality_does_not_imply_asymptotic_totality": True,
            "no_open_does_not_prove_universal_availability": True,
            "heuristic_or_predictive_layer_has_theorem_authority": False,
            "P_VS_NP": P_VS_NP,
        },
    }
    report["status"] = "REACHABLE_OPEN_FOUND" if first_open_layer else ("FIRST_EXTENSION_FOUND" if first_extension_layer else "FINITE_TOTALITY_13_14_NO_EXTENSION")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
