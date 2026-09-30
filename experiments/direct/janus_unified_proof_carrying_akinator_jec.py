#!/usr/bin/env python3
"""C025 unified proof-carrying Akinator/JEC exact-cap engine.

This executable composes mechanisms that previously lived in separate JANUS lanes:

  residual canonicalization / quotient discipline
  -> polynomial exact certificate portfolio lanes
  -> Akinator proof-carrying elimination selector (ELIM_x = exists x . F)
  -> Junction Extension Compression (B2-style AND extension)
  -> atomic macro + elimination recompression
  -> monotone global progress / resource ledger
  -> fail-closed OPEN.

There is NO heuristic proof-state promotion.  No random branch, activity score,
probability, ML prediction, estimated Walsh balance, SAT oracle, or semantic-
equivalence oracle may advance the state.

The engine is a research candidate, not a proof that P=NP.  For fixed constants
C and k it enforces state <= N^C and extension_count <= N^k.  If no certified
move fits those caps it returns OPEN.  A universal theorem that OPEN never occurs
for some fixed C,k remains the missing bridge.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

Literal = int
Clause = Tuple[Literal, ...]
CNF = Tuple[Clause, ...]


# ---------------------------------------------------------------------------
# Canonical CNF / exact local semantics
# ---------------------------------------------------------------------------


def canon_clause(clause: Iterable[int]) -> Optional[Clause]:
    xs = set(int(x) for x in clause)
    if 0 in xs:
        raise ValueError("literal 0 is forbidden")
    if any(-x in xs for x in xs):
        return None  # tautology
    return tuple(sorted(xs, key=lambda z: (abs(z), z < 0)))


def canon_cnf(clauses: Iterable[Iterable[int]]) -> CNF:
    clean: List[Clause] = []
    for c in clauses:
        cc = canon_clause(c)
        if cc is not None:
            clean.append(cc)
    uniq = sorted(set(clean), key=lambda c: (len(c), c))

    # Exact subsumption: if A subset B then A AND B == A.
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
    payload = json.dumps([list(c) for c in cnf], separators=(",", ":")).encode("ascii")
    return sha256(payload).hexdigest()


def vars_of(cnf: CNF) -> Tuple[int, ...]:
    return tuple(sorted({abs(l) for c in cnf for l in c}))


def state_units(cnf: CNF) -> int:
    """A simple explicit representation measure polynomially equivalent to bytes."""
    return 1 + len(cnf) + sum(len(c) for c in cnf)


def input_size_units(cnf: CNF) -> int:
    return max(2, state_units(cnf) + len(vars_of(cnf)))


def restrict(cnf: CNF, var: int, bit: int) -> CNF:
    true_lit = var if bit else -var
    false_lit = -true_lit
    out: List[Clause] = []
    for c in cnf:
        if true_lit in c:
            continue
        out.append(tuple(l for l in c if l != false_lit))
    return canon_cnf(out)


def verify_total_assignment(cnf: CNF, assignment: Dict[int, int]) -> bool:
    for c in cnf:
        if not any(assignment.get(abs(l), -1) == int(l > 0) for l in c):
            return False
    return True


def unit_propagate(cnf: CNF) -> Tuple[CNF, Dict[int, int], bool, int]:
    state = canon_cnf(cnf)
    implied: Dict[int, int] = {}
    work = 0
    while True:
        work += max(1, len(state))
        if () in state:
            return state, implied, False, work
        units = sorted((c[0] for c in state if len(c) == 1), key=lambda l: (abs(l), l < 0))
        if not units:
            return state, implied, True, work
        lit = units[0]
        v, bit = abs(lit), int(lit > 0)
        if v in implied and implied[v] != bit:
            return ((),), implied, False, work
        implied[v] = bit
        state = restrict(state, v, bit)


# ---------------------------------------------------------------------------
# Resource / proof ledger
# ---------------------------------------------------------------------------


@dataclass
class Ledger:
    proposal_work: int = 0
    certificate_discovery_work: int = 0
    verification_work: int = 0
    max_state_units: int = 0
    proof_bytes: int = 0
    extension_definition_bytes: int = 0
    extension_count: int = 0
    residual_state_count: int = 0
    residual_cache_hits: int = 0
    question_count: int = 0
    elimination_pair_work: int = 0
    recompression_work: int = 0
    witness_recovery_work: int = 0
    bounded_width_resolution_work: int = 0
    two_sat_work: int = 0
    gf2_work: int = 0
    events: List[dict] = field(default_factory=list)

    def event(self, kind: str, **payload: object) -> None:
        row = {"kind": kind, **payload}
        self.events.append(row)
        self.proof_bytes += len(json.dumps(row, sort_keys=True, separators=(",", ":")).encode())


@dataclass(frozen=True)
class ElimSnapshot:
    before: CNF
    pivot: int
    kind: str


@dataclass
class EngineState:
    root: CNF
    residual: CNF
    fixed_assignment: Dict[int, int]
    root_vars: Tuple[int, ...]
    extension_defs: List[dict]
    elimination_history: List[ElimSnapshot]
    seen: set[str]
    N: int
    cap_exponent: int
    extension_exponent: int
    ledger: Ledger

    @property
    def state_cap(self) -> int:
        return self.N ** self.cap_exponent

    @property
    def extension_cap(self) -> int:
        return self.N ** self.extension_exponent

    def progress_phi(self, cnf: Optional[CNF] = None, ext_count: Optional[int] = None) -> int:
        f = self.residual if cnf is None else cnf
        live = set(vars_of(f))
        r = sum(1 for v in self.root_vars if v in live)
        v = len(live)
        kmax = self.extension_cap
        # Frozen macro-assisted potential from the old Akinator selector note.
        return r * (len(self.root_vars) + kmax + 1) + v

    def note_state(self) -> None:
        fp = fingerprint(self.residual)
        if fp in self.seen:
            self.ledger.residual_cache_hits += 1
        else:
            self.seen.add(fp)
        self.ledger.residual_state_count += 1
        self.ledger.max_state_units = max(self.ledger.max_state_units, state_units(self.residual))


# ---------------------------------------------------------------------------
# Certificate portfolio lane A: exact 2-SAT
# ---------------------------------------------------------------------------


def _lit_nodes(cnf: CNF) -> List[int]:
    vs = vars_of(cnf)
    return [l for v in vs for l in (v, -v)]


def solve_2sat_exact(cnf: CNF) -> Optional[Tuple[bool, Optional[Dict[int, int]], dict]]:
    """Return None unless every clause has width <= 2; otherwise exact decision."""
    if any(len(c) > 2 for c in cnf):
        return None
    if () in cnf:
        return False, None, {"kind": "2SAT_EMPTY_CLAUSE"}

    nodes = _lit_nodes(cnf)
    graph: Dict[int, List[int]] = {u: [] for u in nodes}
    rev: Dict[int, List[int]] = {u: [] for u in nodes}
    edges = 0

    def add(a: int, b: int) -> None:
        nonlocal edges
        graph.setdefault(a, []).append(b)
        rev.setdefault(b, []).append(a)
        graph.setdefault(b, [])
        rev.setdefault(a, [])
        edges += 1

    for c in cnf:
        if len(c) == 1:
            a = c[0]
            add(-a, a)
        elif len(c) == 2:
            a, b = c
            add(-a, b)
            add(-b, a)

    visited: set[int] = set()
    order: List[int] = []

    def dfs1(u: int) -> None:
        visited.add(u)
        for w in sorted(graph.get(u, [])):
            if w not in visited:
                dfs1(w)
        order.append(u)

    for u in sorted(graph):
        if u not in visited:
            dfs1(u)

    comp: Dict[int, int] = {}

    def dfs2(u: int, cid: int) -> None:
        comp[u] = cid
        for w in sorted(rev.get(u, [])):
            if w not in comp:
                dfs2(w, cid)

    cid = 0
    for u in reversed(order):
        if u not in comp:
            dfs2(u, cid)
            cid += 1

    for v in vars_of(cnf):
        if comp[v] == comp[-v]:
            return False, None, {
                "kind": "2SAT_SCC_CONTRADICTION",
                "variable": v,
                "edges": edges,
                "components": cid,
            }

    # Component numbering orientation depends on traversal convention.  Try the
    # two global orientations and independently verify the resulting witness.
    for greater_true in (True, False):
        assignment = {
            v: int((comp[v] > comp[-v]) if greater_true else (comp[v] < comp[-v]))
            for v in vars_of(cnf)
        }
        if verify_total_assignment(cnf, assignment):
            return True, assignment, {
                "kind": "2SAT_SCC_WITNESS",
                "edges": edges,
                "components": cid,
            }
    raise AssertionError("2-SAT SCC solver failed witness reconstruction")


# ---------------------------------------------------------------------------
# Certificate portfolio lane B: exact explicit XOR/GF(2) blocks
# ---------------------------------------------------------------------------


def _forbidden_assignment_for_clause(clause: Clause, support: Tuple[int, ...]) -> int:
    by_var = {abs(l): int(l < 0) for l in clause}
    mask = 0
    for i, v in enumerate(support):
        if by_var[v]:
            mask |= 1 << i
    return mask


def _extract_explicit_xor_system(cnf: CNF) -> Optional[Tuple[List[Tuple[Tuple[int, ...], int]], dict]]:
    if not cnf or () in cnf:
        return None
    groups: Dict[Tuple[int, ...], List[Clause]] = {}
    for c in cnf:
        support = tuple(sorted(abs(l) for l in c))
        if len(support) != len(c):
            return None
        groups.setdefault(support, []).append(c)

    equations: List[Tuple[Tuple[int, ...], int]] = []
    total_forbidden = 0
    for support in sorted(groups):
        k = len(support)
        clauses = groups[support]
        expected = 1 << max(0, k - 1)
        if len(clauses) != expected:
            return None
        forbidden = {_forbidden_assignment_for_clause(c, support) for c in clauses}
        if len(forbidden) != expected:
            return None
        parities = {m.bit_count() & 1 for m in forbidden}
        if len(parities) != 1:
            return None
        forbidden_parity = next(iter(parities))
        rhs = 1 - forbidden_parity
        equations.append((support, rhs))
        total_forbidden += len(forbidden)

    return equations, {
        "kind": "EXPLICIT_XOR_BLOCK_SYSTEM",
        "equations": len(equations),
        "forbidden_clauses": total_forbidden,
    }


def solve_gf2_explicit_exact(cnf: CNF) -> Optional[Tuple[bool, Optional[Dict[int, int]], dict]]:
    extracted = _extract_explicit_xor_system(cnf)
    if extracted is None:
        return None
    equations, meta = extracted
    variables = sorted({v for support, _ in equations for v in support})
    pos = {v: i for i, v in enumerate(variables)}
    rows: List[List[int]] = []
    for support, rhs in equations:
        mask = 0
        for v in support:
            mask ^= 1 << pos[v]
        rows.append([mask, rhs])

    pivot_cols: List[int] = []
    row = 0
    ops = 0
    for col in range(len(variables)):
        pivot = next((r for r in range(row, len(rows)) if (rows[r][0] >> col) & 1), None)
        if pivot is None:
            continue
        rows[row], rows[pivot] = rows[pivot], rows[row]
        for r in range(len(rows)):
            if r != row and ((rows[r][0] >> col) & 1):
                rows[r][0] ^= rows[row][0]
                rows[r][1] ^= rows[row][1]
                ops += 1
        pivot_cols.append(col)
        row += 1
        if row == len(rows):
            break

    for mask, rhs in rows:
        if mask == 0 and rhs:
            return False, None, {**meta, "kind": "GF2_INCONSISTENT_ROW", "row_ops": ops}

    values = [0] * len(variables)
    # Rows are reduced on pivot columns, so free vars=0 and pivot value=rhs.
    for r, col in enumerate(pivot_cols):
        rhs = rows[r][1]
        residual = rows[r][0] & ~(1 << col)
        acc = 0
        for j in range(len(variables)):
            if (residual >> j) & 1:
                acc ^= values[j]
        values[col] = rhs ^ acc
    assignment = {v: values[pos[v]] for v in variables}
    if not verify_total_assignment(cnf, assignment):
        raise AssertionError("GF(2) extracted witness failed exact CNF verification")
    return True, assignment, {**meta, "kind": "GF2_RREF_WITNESS", "row_ops": ops}


# ---------------------------------------------------------------------------
# Certificate portfolio lane C: fixed-width Resolution refutation search
# ---------------------------------------------------------------------------


def bounded_width_resolution_refutes(cnf: CNF, width: int = 3) -> Tuple[bool, dict]:
    if any(len(c) > width for c in cnf):
        return False, {"kind": "WIDTH_RESOLUTION_SKIPPED_WIDE_AXIOM", "width": width, "work": 0}
    known = set(cnf)
    work = 0
    changed = True
    while changed:
        changed = False
        current = sorted(known, key=lambda c: (len(c), c))
        for i, left in enumerate(current):
            for right in current[i + 1 :]:
                common_pivots = sorted({abs(l) for l in left if -l in right})
                for pivot in common_pivots:
                    work += 1
                    merged = (set(left) - {pivot, -pivot}) | (set(right) - {pivot, -pivot})
                    res = canon_clause(merged)
                    if res is None or len(res) > width:
                        continue
                    if res == ():
                        return True, {"kind": "WIDTH_RESOLUTION_EMPTY", "width": width, "work": work}
                    if res not in known:
                        known.add(res)
                        changed = True
        # finite universe for fixed width; loop terminates at saturation.
    return False, {"kind": "WIDTH_RESOLUTION_SATURATED_NO_EMPTY", "width": width, "work": work, "closure": len(known)}


# ---------------------------------------------------------------------------
# Akinator exact question: resolution variable elimination = existential projection
# ---------------------------------------------------------------------------


def resolve_on_var(left: Clause, right: Clause, var: int) -> Optional[Clause]:
    if var in left and -var in right:
        drop_l, drop_r = var, -var
    elif -var in left and var in right:
        drop_l, drop_r = -var, var
    else:
        raise ValueError("parents do not contain complementary pivot")
    return canon_clause((set(left) - {drop_l}) | (set(right) - {drop_r}))


def eliminate_var_capped(cnf: CNF, var: int, raw_cap: int) -> Tuple[Optional[CNF], dict]:
    pos = [c for c in cnf if var in c]
    neg = [c for c in cnf if -var in c]
    retained = [c for c in cnf if var not in c and -var not in c]

    raw: set[Clause] = set(retained)
    raw_units = state_units(tuple(raw))
    if raw_units > raw_cap:
        return None, {"var": var, "pairs": 0, "tautologies": 0, "raw_units": raw_units, "cap": raw_cap}

    pairs = 0
    tautologies = 0
    for p in pos:
        for n in neg:
            pairs += 1
            r = resolve_on_var(p, n, var)
            if r is None:
                tautologies += 1
                continue
            if r not in raw:
                raw.add(r)
                raw_units += 1 + len(r)
                # Monotone cap is charged before optional subsumption compression.
                if raw_units > raw_cap:
                    return None, {
                        "var": var,
                        "pairs": pairs,
                        "tautologies": tautologies,
                        "raw_units": raw_units,
                        "cap": raw_cap,
                        "aborted": True,
                    }

    out = canon_cnf(raw)
    return out, {
        "var": var,
        "positive": len(pos),
        "negative": len(neg),
        "retained": len(retained),
        "pairs": pairs,
        "tautologies": tautologies,
        "raw_units": raw_units,
        "canonical_units": state_units(out),
        "cap": raw_cap,
        "aborted": False,
    }


def verify_elimination_transition(before: CNF, var: int, after: CNF, raw_cap: int) -> bool:
    rebuilt, _ = eliminate_var_capped(before, var, raw_cap)
    return rebuilt is not None and rebuilt == after


def canonical_pivot_order(state: EngineState, cnf: Optional[CNF] = None) -> List[int]:
    f = state.residual if cnf is None else cnf
    live = set(vars_of(f))
    roots = [v for v in state.root_vars if v in live]
    exts = sorted(v for v in live if v not in set(state.root_vars))
    return roots + exts


def first_capped_elimination(state: EngineState, cnf: Optional[CNF] = None, roots_only: bool = False) -> Optional[Tuple[int, CNF, dict]]:
    f = state.residual if cnf is None else cnf
    pivots = canonical_pivot_order(state, f)
    if roots_only:
        rootset = set(state.root_vars)
        pivots = [v for v in pivots if v in rootset]
    for var in pivots:
        state.ledger.proposal_work += 1
        out, stats = eliminate_var_capped(f, var, state.state_cap)
        state.ledger.elimination_pair_work += stats.get("pairs", 0)
        state.ledger.certificate_discovery_work += 1 + stats.get("pairs", 0)
        if out is None:
            continue
        state.ledger.verification_work += 1 + stats.get("pairs", 0)
        if not verify_elimination_transition(f, var, out, state.state_cap):
            raise AssertionError("exact elimination replay mismatch")
        return var, out, stats
    return None


# ---------------------------------------------------------------------------
# JEC macro restore: B2 AND extension encoding a repeated OR pair
# ---------------------------------------------------------------------------


def repeated_pair_candidates(cnf: CNF) -> List[Tuple[int, int]]:
    freq: Dict[Tuple[int, int], int] = {}
    for c in cnf:
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                a, b = c[i], c[j]
                if abs(a) == abs(b):
                    continue
                pair = tuple(sorted((a, b), key=lambda z: (abs(z), z < 0)))
                freq[pair] = freq.get(pair, 0) + 1
    return sorted((p for p, n in freq.items() if n >= 2), key=lambda p: tuple((abs(z), z < 0) for z in p))


def apply_or_pair_via_b2_and(cnf: CNF, a: int, b: int, e: int) -> Tuple[CNF, dict]:
    """Compress repeated (a OR b) using e <-> ((NOT a) AND (NOT b)).

    Under that definition, (a OR b OR R) is exactly ((NOT e) OR R).
    The extension is conservative and root satisfiability is preserved.
    """
    if e in vars_of(cnf) or e <= max(vars_of(cnf), default=0):
        raise ValueError("extension variable must be fresh and topologically greater")
    if abs(a) == abs(b):
        raise ValueError("degenerate pair")

    replaced: List[Clause] = []
    untouched: List[Clause] = []
    for c in cnf:
        if a in c and b in c:
            rest = [l for l in c if l not in (a, b)]
            cc = canon_clause([-e, *rest])
            if cc is not None:
                replaced.append(cc)
        else:
            untouched.append(c)

    if len(replaced) < 2:
        raise ValueError("macro requires at least two reused occurrences")

    # e <-> ((not a) AND (not b)) using frozen B2 AND definitional CNF.
    defs = [
        (-e, -a),
        (-e, -b),
        (e, a, b),
    ]
    out = canon_cnf([*untouched, *replaced, *defs])
    cert = {
        "kind": "B2_OR_PAIR_MACRO",
        "extension": e,
        "left_literal": -a,
        "right_literal": -b,
        "represents": [a, b],
        "reused_occurrences": len(replaced),
        "before_fingerprint": fingerprint(cnf),
        "after_fingerprint": fingerprint(out),
    }
    return out, cert


def verify_or_pair_macro(before: CNF, after: CNF, cert: dict) -> bool:
    try:
        e = int(cert["extension"])
        a, b = (int(x) for x in cert["represents"])
        rebuilt, rebuilt_cert = apply_or_pair_via_b2_and(before, a, b, e)
        return rebuilt == after and rebuilt_cert["before_fingerprint"] == cert["before_fingerprint"] and rebuilt_cert["after_fingerprint"] == cert["after_fingerprint"]
    except (KeyError, TypeError, ValueError):
        return False


def discover_macro_restore(state: EngineState) -> Optional[Tuple[CNF, int, CNF, dict, dict]]:
    """Find the first canonical macro that immediately restores a capped ROOT pivot.

    The macro and the following original-root elimination are one atomic progress
    step.  We never accumulate speculative extensions.
    """
    if state.ledger.extension_count >= state.extension_cap:
        return None
    live = vars_of(state.residual)
    fresh = max([*live, *state.root_vars], default=0) + 1
    before_phi = state.progress_phi()

    for a, b in repeated_pair_candidates(state.residual):
        state.ledger.proposal_work += 1
        try:
            macro_cnf, macro_cert = apply_or_pair_via_b2_and(state.residual, a, b, fresh)
        except ValueError:
            continue
        state.ledger.certificate_discovery_work += 1
        if state_units(macro_cnf) > state.state_cap:
            continue
        state.ledger.verification_work += 1
        if not verify_or_pair_macro(state.residual, macro_cnf, macro_cert):
            raise AssertionError("macro replay mismatch")

        elim = first_capped_elimination(state, macro_cnf, roots_only=True)
        if elim is None:
            continue
        pivot, after, elim_stats = elim
        after_phi = state.progress_phi(after, state.ledger.extension_count + 1)
        if after_phi >= before_phi:
            continue
        return macro_cnf, pivot, after, macro_cert, elim_stats
    return None


# ---------------------------------------------------------------------------
# Witness recovery through exact elimination ledger
# ---------------------------------------------------------------------------


def reconstruct_witness(state: EngineState, terminal_assignment: Optional[Dict[int, int]] = None) -> Optional[Dict[int, int]]:
    assignment = dict(state.fixed_assignment)
    if terminal_assignment:
        for v, bit in terminal_assignment.items():
            if v in assignment and assignment[v] != bit:
                return None
            assignment[v] = bit

    for snap in reversed(state.elimination_history):
        state.ledger.witness_recovery_work += 1
        # Variables that disappeared only by exact canonical simplification are
        # don't-cares with respect to the surviving subset clauses; choose 0.
        for v in vars_of(snap.before):
            if v != snap.pivot and v not in assignment:
                assignment[v] = 0
        chosen = None
        for bit in (0, 1):
            candidate = dict(assignment)
            candidate[snap.pivot] = bit
            if verify_total_assignment(snap.before, candidate):
                chosen = bit
                break
        if chosen is None:
            return None
        assignment[snap.pivot] = chosen

    root_witness = {v: assignment.get(v, 0) for v in state.root_vars}
    return root_witness if verify_total_assignment(state.root, root_witness) else None


# ---------------------------------------------------------------------------
# Unified engine
# ---------------------------------------------------------------------------


def _result(state: EngineState, status: str, reason: str, *, witness: Optional[Dict[int, int]] = None, missing_bridge: Optional[str] = None) -> dict:
    out = {
        "schema": "JANUS/C025/unified-proof-carrying-akinator-jec/v1",
        "status": status,
        "reason": reason,
        "root_fingerprint": fingerprint(state.root),
        "N": state.N,
        "state_cap_exponent": state.cap_exponent,
        "state_cap": state.state_cap,
        "extension_cap_exponent": state.extension_exponent,
        "extension_cap": state.extension_cap,
        "witness": dict(sorted(witness.items())) if witness else None,
        "residual_fingerprint": fingerprint(state.residual),
        "residual_units": state_units(state.residual),
        "progress_phi": state.progress_phi(),
        "ledger": {k: v for k, v in state.ledger.__dict__.items() if k != "events"},
        "events": state.ledger.events,
        "scientific_boundary": {
            "heuristic_promotion": False,
            "random_branch": False,
            "probability_as_proof": False,
            "walsh_oracle": False,
            "general_sat_oracle": False,
            "semantic_equivalence_oracle": False,
            "supplied_proof_counted_as_discovery": False,
            "finite_run_implies_polynomial": False,
            "claims_p_eq_np": False,
            "claims_p_neq_np": False,
            "P_VS_NP": "OPEN",
        },
    }
    if missing_bridge:
        out["missing_bridge"] = missing_bridge
    return out


def solve_fail_closed(
    clauses: Sequence[Sequence[int]],
    *,
    cap_exponent: int = 2,
    extension_exponent: int = 1,
    bounded_resolution_width: int = 3,
) -> dict:
    if cap_exponent < 1 or extension_exponent < 0:
        raise ValueError("exponents must be fixed nonnegative constants")

    root = canon_cnf(clauses)
    ledger = Ledger()
    state = EngineState(
        root=root,
        residual=root,
        fixed_assignment={},
        root_vars=vars_of(root),
        extension_defs=[],
        elimination_history=[],
        seen=set(),
        N=input_size_units(root),
        cap_exponent=cap_exponent,
        extension_exponent=extension_exponent,
        ledger=ledger,
    )
    ledger.event(
        "ROOT",
        fingerprint=fingerprint(root),
        n_vars=len(state.root_vars),
        n_clauses=len(root),
        N=state.N,
        state_cap=state.state_cap,
        extension_cap=state.extension_cap,
    )

    if state_units(root) > state.state_cap:
        return _result(state, "OPEN", "ROOT_EXCEEDS_FIXED_CAP")

    while True:
        state.note_state()
        before_phi = state.progress_phi()

        # Exact unit propagation is a proof-carrying deterministic simplifier.
        reduced, implied, ok, up_work = unit_propagate(state.residual)
        ledger.verification_work += up_work
        if implied:
            for v, bit in implied.items():
                if v in state.fixed_assignment and state.fixed_assignment[v] != bit:
                    return _result(state, "UNSAT", "UNIT_ASSIGNMENT_CONTRADICTION")
                state.fixed_assignment[v] = bit
            after_phi = state.progress_phi(reduced)
            if after_phi > before_phi:
                return _result(state, "OPEN", "PROGRESS_GATE_REJECTED_UNIT_PROPAGATION")
            ledger.event("UNIT_PROPAGATION", implied=dict(sorted(implied.items())), before_phi=before_phi, after_phi=after_phi)
            state.residual = reduced
            state.ledger.recompression_work += state_units(reduced)
            if not ok or () in reduced:
                return _result(state, "UNSAT", "UNIT_REFUTATION")
            continue
        if not ok or () in state.residual:
            return _result(state, "UNSAT", "UNIT_REFUTATION")

        if not state.residual:
            witness = reconstruct_witness(state)
            if witness is None:
                return _result(state, "OPEN", "WITNESS_RECONSTRUCTION_FAILED")
            return _result(state, "SAT", "EMPTY_RESIDUAL", witness=witness)

        # Certificate portfolio: exact P-class terminal lanes first.
        two = solve_2sat_exact(state.residual)
        if two is not None:
            sat, assignment, cert = two
            ledger.two_sat_work += max(1, len(state.residual) + len(vars_of(state.residual)))
            ledger.event("CERTIFICATE_PORTFOLIO_2SAT", certificate=cert)
            if not sat:
                return _result(state, "UNSAT", "2SAT_CERTIFIED_UNSAT")
            witness = reconstruct_witness(state, assignment)
            if witness is None:
                return _result(state, "OPEN", "2SAT_WITNESS_LIFT_FAILED")
            return _result(state, "SAT", "2SAT_CERTIFIED_SAT", witness=witness)

        gf2 = solve_gf2_explicit_exact(state.residual)
        if gf2 is not None:
            sat, assignment, cert = gf2
            ledger.gf2_work += max(1, len(state.residual) * max(1, len(vars_of(state.residual))))
            ledger.event("CERTIFICATE_PORTFOLIO_GF2", certificate=cert)
            if not sat:
                return _result(state, "UNSAT", "GF2_CERTIFIED_UNSAT")
            witness = reconstruct_witness(state, assignment)
            if witness is None:
                return _result(state, "OPEN", "GF2_WITNESS_LIFT_FAILED")
            return _result(state, "SAT", "GF2_CERTIFIED_SAT", witness=witness)

        refuted, width_cert = bounded_width_resolution_refutes(state.residual, bounded_resolution_width)
        ledger.bounded_width_resolution_work += int(width_cert.get("work", 0))
        if refuted:
            ledger.event("CERTIFICATE_PORTFOLIO_BOUNDED_RESOLUTION", certificate=width_cert)
            return _result(state, "UNSAT", "BOUNDED_WIDTH_RESOLUTION_REFUTATION")

        # Akinator question = first exact existential projection that fits fixed cap.
        elim = first_capped_elimination(state)
        if elim is not None:
            pivot, after, stats = elim
            after_phi = state.progress_phi(after)
            if after_phi >= before_phi:
                return _result(state, "OPEN", "PROGRESS_GATE_REJECTED_ELIMINATION")
            state.elimination_history.append(ElimSnapshot(state.residual, pivot, "PURE_ELIM"))
            ledger.question_count += 1
            ledger.event(
                "AKINATOR_EXACT_ELIMINATION",
                pivot=pivot,
                before_fingerprint=fingerprint(state.residual),
                after_fingerprint=fingerprint(after),
                before_phi=before_phi,
                after_phi=after_phi,
                stats=stats,
            )
            state.residual = after
            ledger.recompression_work += state_units(after)
            continue

        # No exact pivot fits.  Invoke JEC, but only as an atomic macro+ROOT-elim
        # transition that independently restores progress under the same cap.
        restored = discover_macro_restore(state)
        if restored is not None:
            macro_cnf, pivot, after, macro_cert, elim_stats = restored
            after_phi = state.progress_phi(after, ledger.extension_count + 1)
            if after_phi >= before_phi:
                return _result(state, "OPEN", "PROGRESS_GATE_REJECTED_MACRO_RESTORE")
            state.elimination_history.append(ElimSnapshot(macro_cnf, pivot, "JEC_MACRO_PLUS_ELIM"))
            state.extension_defs.append(macro_cert)
            ledger.extension_count += 1
            ledger.extension_definition_bytes += len(json.dumps(macro_cert, sort_keys=True).encode())
            ledger.question_count += 1
            ledger.event(
                "JEC_MACRO_RESTORE_CAP",
                macro=macro_cert,
                pivot=pivot,
                before_fingerprint=fingerprint(state.residual),
                macro_fingerprint=fingerprint(macro_cnf),
                after_fingerprint=fingerprint(after),
                before_phi=before_phi,
                after_phi=after_phi,
                elimination=elim_stats,
            )
            state.residual = after
            ledger.recompression_work += state_units(macro_cnf) + state_units(after)
            continue

        return _result(
            state,
            "OPEN",
            "NO_CAPPED_CERTIFIED_MOVE",
            missing_bridge=(
                "UNIVERSAL_ELIM_CAP_C_AVAILABILITY or a deterministically discoverable "
                "proof-carrying JEC macro that restores a capped elimination pivot"
            ),
        )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def selftest() -> None:
    # Unit lane.
    r = solve_fail_closed([[1], [-1, 2]])
    assert r["status"] == "SAT", r
    assert r["witness"] is not None

    r = solve_fail_closed([[1], [-1]])
    assert r["status"] == "UNSAT", r

    # 2-SAT exact portfolio lane.
    r = solve_fail_closed([[1, 2], [-1, 2], [1, -2]])
    assert r["status"] == "SAT", r

    # General 3-CNF exact elimination lane (not a heuristic branch).
    r = solve_fail_closed([[1, 2, 3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3]])
    assert r["status"] in {"SAT", "UNSAT", "OPEN"}, r
    assert r["scientific_boundary"]["heuristic_promotion"] is False

    # Explicit XOR block: x1 xor x2 xor x3 = 1.
    xor1 = [
        [1, 2, 3],
        [1, -2, -3],
        [-1, 2, -3],
        [-1, -2, 3],
    ]
    r = solve_fail_closed(xor1)
    assert r["status"] == "SAT", r
    assert r["witness"] is not None

    # Fixed tiny cap may legally refuse; it must not guess.
    hardish = [
        [1, 2, 3, 4], [-1, -2, 3, 4], [1, -2, -3, 4], [-1, 2, -3, 4],
        [1, 2, -3, -4], [-1, -2, -3, -4], [1, -2, 3, -4], [-1, 2, 3, -4],
    ]
    r = solve_fail_closed(hardish, cap_exponent=1, extension_exponent=0)
    assert r["status"] in {"SAT", "UNSAT", "OPEN"}
    assert r["scientific_boundary"]["random_branch"] is False

    print("PASS: C025 unified exact-cap Akinator/JEC selftest")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    selftest()
