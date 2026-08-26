#!/usr/bin/env python3
"""C025 MACRO_RESTORE_CAP v2: exhaustive proof-carrying OR-pair discovery.

This is not a new SAT solver.  It replaces one syntactic utility heuristic in the
existing JEC lane: v1 only considered an OR pair when the same literal pair
occurred in >=2 clauses.  v2 deterministically enumerates every non-degenerate
literal pair that co-occurs in any live clause.  A candidate is still admitted
only when:

  1. the B2 definitional extension replays exactly;
  2. the extended CNF stays under the same fixed N^C state cap;
  3. it immediately restores an exact capped elimination of an ORIGINAL variable;
  4. the frozen global progress potential strictly decreases.

Thus removing the frequency filter enlarges deterministic discovery without
allowing heuristic state promotion.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

from pathlib import Path
import sys
from typing import List, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base

CNF = base.CNF


def all_or_pair_candidates(cnf: CNF) -> List[Tuple[int, int]]:
    pairs: set[Tuple[int, int]] = set()
    for clause in cnf:
        for i in range(len(clause)):
            for j in range(i + 1, len(clause)):
                a, b = clause[i], clause[j]
                if abs(a) == abs(b):
                    continue
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                pairs.add(pair)
    return sorted(pairs, key=lambda p: tuple((abs(z), z < 0) for z in p))


def apply_or_pair_v2(cnf: CNF, a: int, b: int, e: int):
    """Exact B2 compression of OR(a,b), allowing even one replaced occurrence."""
    if e in base.vars_of(cnf) or e <= max(base.vars_of(cnf), default=0):
        raise ValueError("extension variable must be fresh and topologically greater")
    if abs(a) == abs(b):
        raise ValueError("degenerate pair")

    replaced = []
    untouched = []
    for clause in cnf:
        if a in clause and b in clause:
            rest = [lit for lit in clause if lit not in (a, b)]
            cc = base.canon_clause([-e, *rest])
            if cc is not None:
                replaced.append(cc)
        else:
            untouched.append(clause)

    if not replaced:
        raise ValueError("pair must occur in at least one clause")

    # e <-> ((not a) AND (not b)); therefore (a OR b OR R) <-> ((not e) OR R).
    defs = [(-e, -a), (-e, -b), (e, a, b)]
    out = base.canon_cnf([*untouched, *replaced, *defs])
    cert = {
        "kind": "B2_OR_PAIR_MACRO_EXHAUSTIVE_V2",
        "extension": e,
        "left_literal": -a,
        "right_literal": -b,
        "represents": [a, b],
        "replaced_occurrences": len(replaced),
        "candidate_policy": "ALL_COOCCURRING_LITERAL_PAIRS_CANONICAL_ORDER",
        "before_fingerprint": base.fingerprint(cnf),
        "after_fingerprint": base.fingerprint(out),
    }
    return out, cert


def verify_or_pair_v2(before: CNF, after: CNF, cert: dict) -> bool:
    try:
        e = int(cert["extension"])
        a, b = (int(x) for x in cert["represents"])
        rebuilt, rebuilt_cert = apply_or_pair_v2(before, a, b, e)
        return (
            rebuilt == after
            and rebuilt_cert["before_fingerprint"] == cert["before_fingerprint"]
            and rebuilt_cert["after_fingerprint"] == cert["after_fingerprint"]
            and rebuilt_cert["candidate_policy"] == cert["candidate_policy"]
        )
    except (KeyError, TypeError, ValueError):
        return False


def discover_macro_restore_v2(state: base.EngineState):
    if state.ledger.extension_count >= state.extension_cap:
        return None

    live = base.vars_of(state.residual)
    fresh = max([*live, *state.root_vars], default=0) + 1
    before_phi = state.progress_phi()

    for a, b in all_or_pair_candidates(state.residual):
        state.ledger.proposal_work += 1
        try:
            macro_cnf, macro_cert = apply_or_pair_v2(state.residual, a, b, fresh)
        except ValueError:
            continue

        state.ledger.certificate_discovery_work += 1
        if base.state_units(macro_cnf) > state.state_cap:
            continue

        state.ledger.verification_work += 1
        if not verify_or_pair_v2(state.residual, macro_cnf, macro_cert):
            raise AssertionError("v2 macro replay mismatch")

        elim = base.first_capped_elimination(state, macro_cnf, roots_only=True)
        if elim is None:
            continue
        pivot, after, elim_stats = elim
        after_phi = state.progress_phi(after, state.ledger.extension_count + 1)
        if after_phi >= before_phi:
            continue

        return macro_cnf, pivot, after, macro_cert, elim_stats
    return None


def solve_fail_closed_v2(*args, **kwargs):
    """Run the frozen unified engine with only MACRO_RESTORE_CAP discovery swapped."""
    old = base.discover_macro_restore
    base.discover_macro_restore = discover_macro_restore_v2
    try:
        result = base.solve_fail_closed(*args, **kwargs)
    finally:
        base.discover_macro_restore = old
    result["macro_restore_version"] = "EXHAUSTIVE_OR_PAIR_V2"
    result["scientific_boundary"]["repeated_pair_frequency_filter"] = False
    return result


def selftest() -> None:
    before = base.canon_cnf([[1, 2, 3], [-1, 4]])
    after, cert = apply_or_pair_v2(before, 1, 2, 5)
    assert cert["replaced_occurrences"] == 1
    assert verify_or_pair_v2(before, after, cert)

    # Truth-table conservativity for the single-use case.
    for mask in range(16):
        root = {i: (mask >> (i - 1)) & 1 for i in range(1, 5)}
        e = int((not bool(root[1])) and (not bool(root[2])))
        ext = dict(root)
        ext[5] = e
        assert base.verify_total_assignment(before, root) == base.verify_total_assignment(after, ext)

    print("PASS: MACRO_RESTORE_CAP exhaustive OR-pair v2 selftest")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    selftest()
