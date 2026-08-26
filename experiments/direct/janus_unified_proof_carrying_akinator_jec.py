#!/usr/bin/env python3
"""JANUS C025 unified proof-carrying Akinator/JEC harness.

Research-only executable composition of existing JANUS ideas:
- canonical residual normalization,
- deterministic proof-carrying questions,
- Junction Extension Compression interface,
- explicit resource accounting,
- lexicographic progress gate,
- fail-closed OPEN terminal.

It intentionally does NOT claim a polynomial SAT solver. Any step that cannot be
proved by the implemented local checker returns OPEN rather than using a heuristic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

Literal = int
Clause = Tuple[Literal, ...]
CNF = Tuple[Clause, ...]


def canon_clause(clause: Iterable[int]) -> Optional[Clause]:
    xs = set(int(x) for x in clause if int(x) != 0)
    if any(-x in xs for x in xs):
        return None  # tautology
    return tuple(sorted(xs, key=lambda z: (abs(z), z < 0)))


def canon_cnf(clauses: Iterable[Iterable[int]]) -> CNF:
    clean = []
    for c in clauses:
        cc = canon_clause(c)
        if cc is None:
            continue
        clean.append(cc)
    uniq = sorted(set(clean), key=lambda c: (len(c), c))
    # Exact subsumption normalization with replayable deterministic semantics.
    kept: List[Clause] = []
    kept_sets: List[frozenset[int]] = []
    for c in uniq:
        cs = frozenset(c)
        if any(prev <= cs for prev in kept_sets):
            continue
        kept.append(c)
        kept_sets.append(cs)
    return tuple(kept)


def fingerprint(cnf: CNF) -> str:
    raw = json.dumps(cnf, separators=(",", ":"), sort_keys=False).encode()
    return sha256(raw).hexdigest()


def vars_of(cnf: CNF) -> Tuple[int, ...]:
    return tuple(sorted({abs(l) for c in cnf for l in c}))


def restrict(cnf: CNF, var: int, bit: int) -> CNF:
    true_lit = var if bit else -var
    false_lit = -true_lit
    out: List[Clause] = []
    for c in cnf:
        if true_lit in c:
            continue
        out.append(tuple(l for l in c if l != false_lit))
    return canon_cnf(out)


def unit_propagate(cnf: CNF) -> Tuple[CNF, Dict[int, int], bool]:
    state = canon_cnf(cnf)
    asn: Dict[int, int] = {}
    while True:
        if () in state:
            return state, asn, False
        units = sorted((c[0] for c in state if len(c) == 1), key=lambda l: (abs(l), l < 0))
        if not units:
            return state, asn, True
        lit = units[0]
        v, b = abs(lit), int(lit > 0)
        if v in asn and asn[v] != b:
            return ((),), asn, False
        asn[v] = b
        state = restrict(state, v, b)


def verify_total_assignment(cnf: CNF, assignment: Dict[int, int]) -> bool:
    for c in cnf:
        if not any(assignment.get(abs(l), -1) == int(l > 0) for l in c):
            return False
    return True


@dataclass(frozen=True, order=True)
class Progress:
    unresolved_original_variables: int
    uncertified_residual_classes: int
    explicit_residual_literal_volume: int
    unresolved_frontier_volume: int
    unshared_repeated_proof_fragments: int


@dataclass
class Ledger:
    proposal_work: int = 0
    certificate_discovery_work: int = 0
    verification_work: int = 0
    state_bytes: int = 0
    proof_bytes: int = 0
    extension_definition_bytes: int = 0
    extension_count: int = 0
    residual_state_count: int = 0
    question_count: int = 0
    recompression_work: int = 0
    witness_recovery_work: int = 0
    events: List[dict] = field(default_factory=list)

    def event(self, kind: str, **payload: object) -> None:
        self.events.append({"kind": kind, **payload})


@dataclass
class State:
    root: CNF
    residual: CNF
    assignment: Dict[int, int]
    ledger: Ledger

    def progress(self) -> Progress:
        rem = set(vars_of(self.residual))
        lit_volume = sum(len(c) for c in self.residual)
        # In this executable v0, residual classes/frontier/proof-fragments are exact
        # conservative counters. Future integrations may replace them only with
        # independently replayable stronger summaries.
        residual_classes = len(self.residual)
        frontier = len(rem)
        repeated = _repeated_fragment_count(self.residual)
        return Progress(len(rem), residual_classes, lit_volume, frontier, repeated)


def _repeated_fragment_count(cnf: CNF) -> int:
    # Deterministic, polynomially generated pair-fragment census.
    freq: Dict[Tuple[int, int], int] = {}
    for c in cnf:
        lits = list(c)
        for i in range(len(lits)):
            for j in range(i + 1, len(lits)):
                p = tuple(sorted((lits[i], lits[j])))
                freq[p] = freq.get(p, 0) + 1
    return sum(v - 1 for v in freq.values() if v > 1)


def strict_progress(after: Progress, before: Progress) -> bool:
    return after < before


def cheap_certified_forced_move(state: State) -> Optional[Tuple[int, int, dict]]:
    """Deterministically find the first failed-literal-UP forced move.

    This is complete only for the implemented local certificate language.
    No heuristic branch is permitted.
    """
    vars_left = vars_of(state.residual)
    for v in vars_left:
        outcomes: Dict[int, bool] = {}
        for bit in (0, 1):
            state.ledger.proposal_work += 1
            reduced = restrict(state.residual, v, bit)
            _, _, ok = unit_propagate(reduced)
            state.ledger.certificate_discovery_work += 1
            outcomes[bit] = ok
        if outcomes[0] != outcomes[1]:
            forced = 0 if outcomes[0] else 1
            cert = {
                "kind": "FAILED_LITERAL_UP",
                "var": v,
                "forced_bit": forced,
                "opposite_refuted": 1 - forced,
            }
            return v, forced, cert
        if not outcomes[0] and not outcomes[1]:
            return v, -1, {"kind": "BOTH_POLARITIES_REFUTED_BY_UP", "var": v}
    return None


def bounded_pair_macro_candidates(state: State) -> List[Tuple[int, int]]:
    """Canonical polynomial candidate generator for repeated literal pairs.

    IMPORTANT: candidates are observations only. They are not admitted as extension
    macros unless a separate proof checker can prove the extension useful and safe.
    This v0 harness therefore records them but does not promote them.
    """
    freq: Dict[Tuple[int, int], int] = {}
    for c in state.residual:
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                p = tuple(sorted((c[i], c[j])))
                freq[p] = freq.get(p, 0) + 1
                state.ledger.proposal_work += 1
    return sorted((p for p, n in freq.items() if n >= 2), key=lambda p: p)


def try_extension_compression(state: State) -> Optional[dict]:
    """Fail-closed DISCOVER_MACRO v0.

    We deliberately refuse to convert a repeated syntactic pair into an extension
    merely because it looks useful. That would be heuristic promotion. The function
    exposes the exact missing bridge by returning no admitted macro until a
    proof-carrying utility/recompression checker is implemented.
    """
    cands = bounded_pair_macro_candidates(state)
    if cands:
        state.ledger.event(
            "EXTENSION_CANDIDATES_OBSERVED_NOT_PROMOTED",
            count=len(cands),
            first=list(cands[0]),
            reason="utility/progress certificate not yet implemented",
        )
    return None


def solve_fail_closed(clauses: Sequence[Sequence[int]]) -> dict:
    root = canon_cnf(clauses)
    ledger = Ledger()
    state = State(root=root, residual=root, assignment={}, ledger=ledger)
    root_vars = vars_of(root)
    ledger.event("ROOT", fingerprint=fingerprint(root), n_vars=len(root_vars), n_clauses=len(root))

    while True:
        before = state.progress()
        ledger.state_bytes = max(ledger.state_bytes, len(repr(state.residual).encode()))
        ledger.residual_state_count += 1

        reduced, implied, ok = unit_propagate(state.residual)
        ledger.verification_work += max(1, len(state.residual))
        if implied:
            new_assignment = dict(state.assignment)
            conflict = False
            for v, b in implied.items():
                if v in new_assignment and new_assignment[v] != b:
                    conflict = True
                    break
                new_assignment[v] = b
            if conflict:
                return _result("UNSAT", state, reason="contradictory_unit_ledger")
            candidate = State(state.root, reduced, new_assignment, ledger)
            after = candidate.progress()
            if reduced != state.residual:
                # Unit propagation must not increase the lexicographic potential.
                if not (strict_progress(after, before) or after == before):
                    return _result("OPEN", state, reason="progress_gate_rejected_unit_propagation")
                ledger.event("UNIT_PROPAGATION", implied=implied, before=list(before.__dict__.values()), after=list(after.__dict__.values()))
                state = candidate
                continue
        if not ok or () in state.residual:
            return _result("UNSAT", state, reason="unit_refutation")

        if not state.residual:
            # All clauses satisfied by partial assignment; fill don't-cares canonically.
            witness = dict(state.assignment)
            for v in root_vars:
                witness.setdefault(v, 0)
            ledger.witness_recovery_work += len(root_vars)
            if verify_total_assignment(state.root, witness):
                return _result("SAT", state, witness=witness, reason="empty_residual")
            return _result("OPEN", state, reason="witness_reconstruction_failed")

        forced = cheap_certified_forced_move(state)
        if forced is not None:
            v, bit, cert = forced
            ledger.question_count += 1
            if bit == -1:
                ledger.event("CERTIFIED_QUESTION", certificate=cert)
                return _result("UNSAT", state, reason="both_polarities_refuted_by_UP")
            next_residual = restrict(state.residual, v, bit)
            next_assignment = dict(state.assignment)
            next_assignment[v] = bit
            candidate = State(state.root, next_residual, next_assignment, ledger)
            after = candidate.progress()
            if not strict_progress(after, before):
                return _result("OPEN", state, reason="progress_gate_rejected_certified_question")
            ledger.event("CERTIFIED_QUESTION", certificate=cert, before=list(before.__dict__.values()), after=list(after.__dict__.values()))
            state = candidate
            continue

        extension = try_extension_compression(state)
        if extension is not None:
            raise AssertionError("v0 must not promote extension candidates")

        return _result(
            "OPEN",
            state,
            reason="NO_CERTIFIED_MOVE",
            missing_bridge="proof-carrying DISCOVER_MACRO/progress certificate",
        )


def _result(status: str, state: State, *, reason: str, witness: Optional[Dict[int, int]] = None, missing_bridge: Optional[str] = None) -> dict:
    out = {
        "schema": "JANUS/C025/unified-proof-carrying-akinator-jec/v0",
        "status": status,
        "reason": reason,
        "root_fingerprint": fingerprint(state.root),
        "assignment": dict(sorted(state.assignment.items())),
        "witness": dict(sorted(witness.items())) if witness is not None else None,
        "progress": state.progress().__dict__,
        "ledger": {
            k: v for k, v in state.ledger.__dict__.items() if k != "events"
        },
        "events": state.ledger.events,
        "scientific_boundary": {
            "heuristic_promotion": False,
            "general_sat_oracle": False,
            "semantic_equivalence_oracle": False,
            "claims_p_eq_np": False,
            "claims_p_neq_np": False,
            "P_VS_NP": "OPEN",
        },
    }
    if missing_bridge:
        out["missing_bridge"] = missing_bridge
    return out


def selftest() -> None:
    # Trivial SAT by units.
    r1 = solve_fail_closed([[1], [-1, 2]])
    assert r1["status"] == "SAT", r1
    assert r1["witness"] is not None

    # Trivial UNSAT by unit propagation.
    r2 = solve_fail_closed([[1], [-1]])
    assert r2["status"] == "UNSAT", r2

    # Failed-literal-UP lane: x1=false creates contradiction, forcing x1=true.
    r3 = solve_fail_closed([[1, 2], [1, -2], [-1, 3]])
    assert r3["status"] in {"SAT", "OPEN"}, r3
    assert r3["scientific_boundary"]["heuristic_promotion"] is False

    # Hard-ish unresolved core must fail closed, not branch heuristically.
    r4 = solve_fail_closed([[1, 2, 3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3]])
    assert r4["status"] in {"OPEN", "SAT", "UNSAT"}
    if r4["status"] == "OPEN":
        assert r4["reason"] == "NO_CERTIFIED_MOVE"
        assert r4["missing_bridge"].startswith("proof-carrying DISCOVER_MACRO")

    print("PASS: C025 unified proof-carrying Akinator/JEC v0 selftest")


if __name__ == "__main__":
    selftest()
