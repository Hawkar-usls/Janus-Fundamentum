#!/usr/bin/env python3
"""Lightweight exact structural microscope for the preregistered depth-2 selector tower.

The full frozen v0.4 run is intentionally left untouched.  This diagnostic
computes the exact top-selector distributive product using the disjoint-antichain
structure of the frozen generator, then evaluates only syntactic resource
certificates.  It does not skip or alter the theorem machine and has no decision
authority.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_selector_product_tower_hostile_probe as tower

P_VS_NP = "OPEN"


def exact_disjoint_selector_product(root: base.CNF, selector: int) -> base.CNF:
    pos = [c for c in root if selector in c]
    neg = [c for c in root if -selector in c]
    retained = [c for c in root if selector not in c and -selector not in c]
    if retained:
        raise AssertionError("DEPTH2_TOP_SELECTOR_EXPECTED_TO_OCCUR_IN_EVERY_ROOT_CLAUSE")

    rows = []
    for p in pos:
        p0 = tuple(l for l in p if l != selector)
        for q in neg:
            q0 = tuple(l for l in q if l != -selector)
            # The frozen depth-2 construction gives disjoint variable supports
            # to the two top subtrees.  Hence no complementary literal can be
            # created across p0/q0 and each pair has a unique union.
            if set(map(abs, p0)) & set(map(abs, q0)):
                raise AssertionError("TOP_SUBTREE_SUPPORTS_NOT_DISJOINT")
            row = base.canon_clause((*p0, *q0))
            if row is None:
                raise AssertionError("UNEXPECTED_TAUTOLOGY_IN_DISJOINT_PRODUCT")
            rows.append(row)

    uniq = set(rows)
    if len(uniq) != len(rows):
        raise AssertionError("UNEXPECTED_DUPLICATE_IN_DISJOINT_PRODUCT")

    # Product of two antichains on disjoint supports is an antichain, so no
    # subsumption cleanup is possible.  Sorting gives the same canonical order
    # without invoking quadratic generic subsumption scanning on 20k+ clauses.
    return tuple(sorted(uniq, key=lambda c: (len(c), c)))


def analyze(cnf: base.CNF, N: int) -> dict:
    s = base.state_units(cnf)
    live = base.vars_of(cnf)
    n = len(live)
    cap = N**2

    pair_freq: Counter[tuple[int, int]] = Counter()
    p = defaultdict(int)
    q = defaultdict(int)
    A_p = defaultdict(int)
    A_q = defaultdict(int)

    for c in cnf:
        k1 = len(c) - 1
        for lit in c:
            v = abs(lit)
            if lit > 0:
                p[v] += 1
                A_p[v] += k1
            else:
                q[v] += 1
                A_q[v] += k1
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                a, b = c[i], c[j]
                if abs(a) == abs(b):
                    continue
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                pair_freq[pair] += 1

    T = max(pair_freq.values(), default=0)
    frequent_threshold = s - 2 * N + 11
    sign_split_upper = s + 12 * max(0, n - 1) ** 2 * T**2 - 12 * max(0, n - 1) * T

    local = []
    guaranteed_fit = []
    for x in live:
        px, qx = p[x], q[x]
        Ap, Aq = A_p[x], A_q[x]
        d = px + qx
        upper = s + px * qx + (qx - 1) * Ap + (px - 1) * Aq - 2 * d
        row = {
            "pivot": x,
            "p": px,
            "q": qx,
            "A_plus": Ap,
            "A_minus": Aq,
            "raw_multiset_upper": upper,
            "certified_fit": upper <= cap,
        }
        local.append(row)
        if row["certified_fit"]:
            guaranteed_fit.append(x)

    if guaranteed_fit:
        classification = "ORDINARY_ELIMINATION_CERTIFIED_BY_LOCAL_RAW_BOUND"
    elif T >= frequent_threshold:
        classification = "V2_RESCUE_CERTIFIED_BY_FREQUENT_PAIR_LEMMA"
    elif sign_split_upper <= cap:
        classification = "ORDINARY_ELIMINATION_CERTIFIED_BY_GLOBAL_SIGN_SPLIT_BOUND"
    else:
        classification = "BALANCED_PRESSURE_WEDGE_CANDIDATE_REQUIRES_EXACT_FROZEN_SCAN"

    return {
        "state_units": s,
        "live_variables": n,
        "state_cap": cap,
        "max_pair_frequency": T,
        "v2_frequent_pair_threshold": frequent_threshold,
        "sign_split_global_upper": sign_split_upper,
        "certified_local_fit_count": len(guaranteed_fit),
        "certified_local_fit_pivots": guaranteed_fit,
        "min_local_raw_upper": min((r["raw_multiset_upper"] for r in local), default=0),
        "max_local_raw_upper": max((r["raw_multiset_upper"] for r in local), default=0),
        "classification": classification,
        "local_pivot_bounds": local,
    }


def main() -> int:
    root = tower.build_tree(2)
    N = base.input_size_units(root)
    product = exact_disjoint_selector_product(root, 1)
    report = {
        "schema": "JANUS/C025/DEPTH2-BALANCED-PRESSURE-MICROSCOPE/v1",
        "source": {
            "fingerprint": base.fingerprint(root),
            "variables": len(base.vars_of(root)),
            "clauses": len(root),
            "state_units": base.state_units(root),
            "N": N,
            "state_cap": N**2,
        },
        "forced_top_selector_transition": {
            "pivot": 1,
            "role": "STRUCTURAL_DIAGNOSTIC_OF_THE_FROZEN_CANONICAL_TOP_SELECTOR_NOT_A_THEOREM_RUNTIME_OVERRIDE",
            "product_clauses": len(product),
            "product_fingerprint": base.fingerprint(product),
        },
        "post_top_product": analyze(product, N),
        "scientific_boundary": {
            "does_not_claim_actual_v0_4_reached_this_state_before_full_run_finishes": True,
            "does_not_skip_full_preregistered_depth2_run": True,
            "structural_product_is_exact_for_frozen_disjoint_selector_tree": True,
            "finite_structural_diagnostic_only": True,
            "absence_of_gap_is_not_totality_proof": True,
            "presence_of_wedge_candidate_is_not_an_OPEN_until_exact_frozen_scan_fails": True,
            "HIGH_VOLUME_RESCUE_TOTALITY": "OPEN",
            "P_VS_NP": P_VS_NP,
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
