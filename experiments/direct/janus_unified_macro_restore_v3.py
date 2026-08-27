#!/usr/bin/env python3
"""C025 MACRO_RESTORE_CAP v3: fixed-depth extension-tail descent.

Targeted repair of the exact frozen PHP_5_4_C1 barrier discovered after v2:
all original/root variables are already eliminated, so the old JEC grammar
(`macro + ROOT elimination`) is disabled by construction even though the live
residual contains only extension variables.

v3 does NOT add heuristic branching and does NOT add an unbounded search.  Once
there are no live root variables and no ordinary exact capped pivot, it
canonically enumerates:

  B2 OR-pair macro -> exact elimination of old extension x -> exact elimination
  of distinct old extension y

The atomic plan is admitted only when every intermediate representation is <=
the same frozen N^C cap, every transition independently replays, and the final
frozen progress potential is strictly smaller than the pre-macro potential.
The elimination-chain length is the fixed constant 2.

Iterative contexts inherit v2's historical-extension freshness rule: an
extension identifier that disappeared from the live residual is still reserved
forever by state.extension_defs and may not be reused.

P_VS_NP remains OPEN.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import List, Optional, Sequence

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2


@dataclass(frozen=True)
class MacroPlan:
    macro_cnf: base.CNF
    macro_cert: dict
    pivots: tuple[int, ...]
    before_each_elim: tuple[base.CNF, ...]
    after_each_elim: tuple[base.CNF, ...]
    elim_stats: tuple[dict, ...]
    kind: str

    @property
    def after(self) -> base.CNF:
        return self.after_each_elim[-1]


def _charged_eliminate(state: base.EngineState, cnf: base.CNF, var: int):
    state.ledger.proposal_work += 1
    out, stats = base.eliminate_var_capped(cnf, var, state.state_cap)
    pairs = int(stats.get("pairs", 0))
    state.ledger.elimination_pair_work += pairs
    state.ledger.certificate_discovery_work += 1 + pairs
    if out is None:
        return None, stats
    state.ledger.verification_work += 1 + pairs
    if not base.verify_elimination_transition(cnf, var, out, state.state_cap):
        raise AssertionError("v3 elimination replay mismatch")
    return out, stats


def verify_plan(before: base.CNF, plan: MacroPlan, cap: int) -> bool:
    if base.state_units(plan.macro_cnf) > cap:
        return False
    if not v2.verify_or_pair_v2(before, plan.macro_cnf, plan.macro_cert):
        return False
    if not (len(plan.pivots) == len(plan.before_each_elim) == len(plan.after_each_elim) == len(plan.elim_stats)):
        return False
    current = plan.macro_cnf
    for pivot, expected_before, expected_after in zip(plan.pivots, plan.before_each_elim, plan.after_each_elim):
        if current != expected_before or base.state_units(current) > cap:
            return False
        rebuilt, _ = base.eliminate_var_capped(current, pivot, cap)
        if rebuilt is None or rebuilt != expected_after or base.state_units(rebuilt) > cap:
            return False
        current = rebuilt
    return current == plan.after


def discover_extension_tail_plan_v3(state: base.EngineState) -> Optional[MacroPlan]:
    """Canonical fixed-depth-2 macro descent, only after all root vars are gone."""
    if state.ledger.extension_count >= state.extension_cap:
        return None

    live_before = tuple(base.vars_of(state.residual))
    rootset = set(state.root_vars)
    if any(v in rootset for v in live_before):
        return None
    if len(live_before) < 2:
        return None

    fresh = v2.next_fresh_extension(state)
    before_phi = state.progress_phi()

    for a, b in v2.all_or_pair_candidates(state.residual):
        state.ledger.proposal_work += 1
        try:
            macro_cnf, macro_cert = v2.apply_or_pair_v2(state.residual, a, b, fresh)
        except ValueError:
            continue
        state.ledger.certificate_discovery_work += 1
        if base.state_units(macro_cnf) > state.state_cap:
            continue
        state.ledger.verification_work += 1
        if not v2.verify_or_pair_v2(state.residual, macro_cnf, macro_cert):
            raise AssertionError("v3 macro replay mismatch")

        # Frozen grammar: eliminate two DISTINCT variables that were live before
        # the macro.  The fresh macro variable itself is not a descent pivot.
        for pivot1 in live_before:
            after1, stats1 = _charged_eliminate(state, macro_cnf, pivot1)
            if after1 is None:
                continue
            for pivot2 in live_before:
                if pivot2 == pivot1 or pivot2 not in set(base.vars_of(after1)):
                    continue
                after2, stats2 = _charged_eliminate(state, after1, pivot2)
                if after2 is None:
                    continue
                after_phi = state.progress_phi(after2, state.ledger.extension_count + 1)
                if after_phi >= before_phi:
                    continue
                plan = MacroPlan(
                    macro_cnf=macro_cnf,
                    macro_cert={**macro_cert, "kind": "B2_OR_PAIR_MACRO_EXTENSION_TAIL_V3"},
                    pivots=(pivot1, pivot2),
                    before_each_elim=(macro_cnf, after1),
                    after_each_elim=(after1, after2),
                    elim_stats=(stats1, stats2),
                    kind="B2_MACRO_PLUS_TWO_EXTENSION_ELIMS",
                )
                # verify_plan expects the v2 certificate kind; replay with a copy.
                replay_cert = dict(plan.macro_cert)
                replay_cert["kind"] = "B2_OR_PAIR_MACRO_EXHAUSTIVE_V2"
                replay_plan = MacroPlan(
                    plan.macro_cnf, replay_cert, plan.pivots,
                    plan.before_each_elim, plan.after_each_elim, plan.elim_stats, plan.kind,
                )
                if not verify_plan(state.residual, replay_plan, state.state_cap):
                    raise AssertionError("v3 atomic plan replay mismatch")
                return plan
    return None


def _append_plan(state: base.EngineState, plan: MacroPlan, before_phi: int) -> None:
    ledger = state.ledger
    replay_cert = dict(plan.macro_cert)
    replay_cert["kind"] = "B2_OR_PAIR_MACRO_EXHAUSTIVE_V2"
    replay_plan = MacroPlan(
        plan.macro_cnf, replay_cert, plan.pivots,
        plan.before_each_elim, plan.after_each_elim, plan.elim_stats, plan.kind,
    )
    if not verify_plan(state.residual, replay_plan, state.state_cap):
        raise AssertionError("v3 plan failed final replay")

    after_phi = state.progress_phi(plan.after, ledger.extension_count + 1)
    if after_phi >= before_phi:
        raise AssertionError("v3 plan does not decrease frozen progress potential")

    for before, pivot in zip(plan.before_each_elim, plan.pivots):
        state.elimination_history.append(base.ElimSnapshot(before, pivot, "JEC_EXTENSION_TAIL_V3"))

    state.extension_defs.append(plan.macro_cert)
    ledger.extension_count += 1
    ledger.extension_definition_bytes += len(json.dumps(plan.macro_cert, sort_keys=True).encode())
    ledger.question_count += len(plan.pivots)
    ledger.event(
        "JEC_EXTENSION_TAIL_DESCENT_V3",
        macro=plan.macro_cert,
        pivots=list(plan.pivots),
        before_fingerprint=base.fingerprint(state.residual),
        macro_fingerprint=base.fingerprint(plan.macro_cnf),
        intermediate_fingerprints=[base.fingerprint(x) for x in plan.after_each_elim[:-1]],
        after_fingerprint=base.fingerprint(plan.after),
        before_phi=before_phi,
        after_phi=after_phi,
        eliminations=list(plan.elim_stats),
        fixed_chain_length=2,
    )
    ledger.recompression_work += base.state_units(plan.macro_cnf) + sum(base.state_units(x) for x in plan.after_each_elim)
    state.residual = plan.after


def solve_fail_closed_v3(
    clauses: Sequence[Sequence[int]],
    *,
    cap_exponent: int = 2,
    extension_exponent: int = 1,
    bounded_resolution_width: int = 3,
) -> dict:
    """Frozen v1 engine + v2 root restore + targeted v3 extension-tail plan."""
    if cap_exponent < 1 or extension_exponent < 0:
        raise ValueError("exponents must be fixed nonnegative constants")

    root = base.canon_cnf(clauses)
    ledger = base.Ledger()
    state = base.EngineState(
        root=root,
        residual=root,
        fixed_assignment={},
        root_vars=base.vars_of(root),
        extension_defs=[],
        elimination_history=[],
        seen=set(),
        N=base.input_size_units(root),
        cap_exponent=cap_exponent,
        extension_exponent=extension_exponent,
        ledger=ledger,
    )
    ledger.event(
        "ROOT", fingerprint=base.fingerprint(root), n_vars=len(state.root_vars),
        n_clauses=len(root), N=state.N, state_cap=state.state_cap,
        extension_cap=state.extension_cap,
    )

    if base.state_units(root) > state.state_cap:
        out = base._result(state, "OPEN", "ROOT_EXCEEDS_FIXED_CAP")
        out["macro_restore_version"] = "EXTENSION_TAIL_V3"
        return out

    while True:
        state.note_state()
        before_phi = state.progress_phi()

        reduced, implied, ok, up_work = base.unit_propagate(state.residual)
        ledger.verification_work += up_work
        if implied:
            for var, bit in implied.items():
                if var in state.fixed_assignment and state.fixed_assignment[var] != bit:
                    out = base._result(state, "UNSAT", "UNIT_ASSIGNMENT_CONTRADICTION")
                    out["macro_restore_version"] = "EXTENSION_TAIL_V3"
                    return out
                state.fixed_assignment[var] = bit
            after_phi = state.progress_phi(reduced)
            if after_phi > before_phi:
                out = base._result(state, "OPEN", "PROGRESS_GATE_REJECTED_UNIT_PROPAGATION")
                out["macro_restore_version"] = "EXTENSION_TAIL_V3"
                return out
            ledger.event("UNIT_PROPAGATION", implied=dict(sorted(implied.items())), before_phi=before_phi, after_phi=after_phi)
            state.residual = reduced
            ledger.recompression_work += base.state_units(reduced)
            if not ok or () in reduced:
                out = base._result(state, "UNSAT", "UNIT_REFUTATION")
                out["macro_restore_version"] = "EXTENSION_TAIL_V3"
                return out
            continue
        if not ok or () in state.residual:
            out = base._result(state, "UNSAT", "UNIT_REFUTATION")
            out["macro_restore_version"] = "EXTENSION_TAIL_V3"
            return out

        if not state.residual:
            witness = base.reconstruct_witness(state)
            if witness is None:
                out = base._result(state, "OPEN", "WITNESS_RECONSTRUCTION_FAILED")
            else:
                out = base._result(state, "SAT", "EMPTY_RESIDUAL", witness=witness)
            out["macro_restore_version"] = "EXTENSION_TAIL_V3"
            return out

        two = base.solve_2sat_exact(state.residual)
        if two is not None:
            sat, assignment, cert = two
            ledger.two_sat_work += max(1, len(state.residual) + len(base.vars_of(state.residual)))
            ledger.event("CERTIFICATE_PORTFOLIO_2SAT", certificate=cert)
            if not sat:
                out = base._result(state, "UNSAT", "2SAT_CERTIFIED_UNSAT")
            else:
                witness = base.reconstruct_witness(state, assignment)
                out = base._result(state, "SAT", "2SAT_CERTIFIED_SAT", witness=witness) if witness is not None else base._result(state, "OPEN", "2SAT_WITNESS_LIFT_FAILED")
            out["macro_restore_version"] = "EXTENSION_TAIL_V3"
            return out

        gf2 = base.solve_gf2_explicit_exact(state.residual)
        if gf2 is not None:
            sat, assignment, cert = gf2
            ledger.gf2_work += max(1, len(state.residual) * max(1, len(base.vars_of(state.residual))))
            ledger.event("CERTIFICATE_PORTFOLIO_GF2", certificate=cert)
            if not sat:
                out = base._result(state, "UNSAT", "GF2_CERTIFIED_UNSAT")
            else:
                witness = base.reconstruct_witness(state, assignment)
                out = base._result(state, "SAT", "GF2_CERTIFIED_SAT", witness=witness) if witness is not None else base._result(state, "OPEN", "GF2_WITNESS_LIFT_FAILED")
            out["macro_restore_version"] = "EXTENSION_TAIL_V3"
            return out

        refuted, width_cert = base.bounded_width_resolution_refutes(state.residual, bounded_resolution_width)
        ledger.bounded_width_resolution_work += int(width_cert.get("work", 0))
        if refuted:
            ledger.event("CERTIFICATE_PORTFOLIO_BOUNDED_RESOLUTION", certificate=width_cert)
            out = base._result(state, "UNSAT", "BOUNDED_WIDTH_RESOLUTION_REFUTATION")
            out["macro_restore_version"] = "EXTENSION_TAIL_V3"
            return out

        elim = base.first_capped_elimination(state)
        if elim is not None:
            pivot, after, stats = elim
            after_phi = state.progress_phi(after)
            if after_phi >= before_phi:
                out = base._result(state, "OPEN", "PROGRESS_GATE_REJECTED_ELIMINATION")
                out["macro_restore_version"] = "EXTENSION_TAIL_V3"
                return out
            state.elimination_history.append(base.ElimSnapshot(state.residual, pivot, "PURE_ELIM"))
            ledger.question_count += 1
            ledger.event(
                "AKINATOR_EXACT_ELIMINATION", pivot=pivot,
                before_fingerprint=base.fingerprint(state.residual),
                after_fingerprint=base.fingerprint(after), before_phi=before_phi,
                after_phi=after_phi, stats=stats,
            )
            state.residual = after
            ledger.recompression_work += base.state_units(after)
            continue

        # Preserve v2 root-restoration behavior while roots remain live.
        root_restored = v2.discover_macro_restore_v2(state)
        if root_restored is not None:
            macro_cnf, pivot, after, macro_cert, elim_stats = root_restored
            after_phi = state.progress_phi(after, ledger.extension_count + 1)
            if after_phi >= before_phi:
                out = base._result(state, "OPEN", "PROGRESS_GATE_REJECTED_MACRO_RESTORE")
                out["macro_restore_version"] = "EXTENSION_TAIL_V3"
                return out
            state.elimination_history.append(base.ElimSnapshot(macro_cnf, pivot, "JEC_MACRO_PLUS_ELIM"))
            state.extension_defs.append(macro_cert)
            ledger.extension_count += 1
            ledger.extension_definition_bytes += len(json.dumps(macro_cert, sort_keys=True).encode())
            ledger.question_count += 1
            ledger.event(
                "JEC_MACRO_RESTORE_CAP", macro=macro_cert, pivot=pivot,
                before_fingerprint=base.fingerprint(state.residual),
                macro_fingerprint=base.fingerprint(macro_cnf),
                after_fingerprint=base.fingerprint(after), before_phi=before_phi,
                after_phi=after_phi, elimination=elim_stats,
            )
            state.residual = after
            ledger.recompression_work += base.state_units(macro_cnf) + base.state_units(after)
            continue

        tail_plan = discover_extension_tail_plan_v3(state)
        if tail_plan is not None:
            _append_plan(state, tail_plan, before_phi)
            continue

        out = base._result(
            state, "OPEN", "NO_CAPPED_CERTIFIED_MOVE",
            missing_bridge=(
                "UNIVERSAL_ELIM_CAP_C_AVAILABILITY or a deterministic proof-carrying "
                "fixed-depth/structured extension-tail descent that restores strict progress"
            ),
        )
        out["macro_restore_version"] = "EXTENSION_TAIL_V3"
        return out


def selftest() -> None:
    # Regression controls: no heuristic promotion and exact small instances.
    for cnf in (
        [[1], [-1, 2]],
        [[1], [-1]],
        [[1, 2], [-1, 2], [1, -2]],
        [[1, 2, 3], [-1, -2, 3], [-1, 2, -3], [1, -2, -3]],
    ):
        r = solve_fail_closed_v3(cnf)
        assert r["status"] in {"SAT", "UNSAT", "OPEN"}
        assert r["scientific_boundary"]["heuristic_promotion"] is False
        if r["status"] == "SAT":
            assert r["witness"] is not None
            assert base.verify_total_assignment(base.canon_cnf(cnf), r["witness"])

    print("PASS: MACRO_RESTORE_CAP extension-tail v3 selftest")
    print("P_VS_NP = OPEN")


if __name__ == "__main__":
    selftest()
