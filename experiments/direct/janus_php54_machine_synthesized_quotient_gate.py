#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole
from experiments.direct import janus_php54_augmented_orbit_compressor_gate as aug

CAPTURED: base.EngineState | None = None
ORIGINAL = v2.discover_macro_restore_v2


def capture(state: base.EngineState):
    global CAPTURED
    out = ORIGINAL(state)
    if out is None and not any(v in set(state.root_vars) for v in base.vars_of(state.residual)):
        CAPTURED = state
    return out


def eval_lit(lit: int, assignment: dict[int, bool]) -> bool:
    value = assignment[abs(lit)]
    return value if lit > 0 else not value


def eval_clause(clause: base.Clause, assignment: dict[int, bool]) -> bool:
    return any(eval_lit(lit, assignment) for lit in clause)


def local_signature(clause: base.Clause, block: tuple[int, ...]) -> tuple[int, ...]:
    pos = {v: i + 1 for i, v in enumerate(block)}
    return tuple(sorted((pos[abs(lit)] if lit > 0 else -pos[abs(lit)]) for lit in clause))


def local_block_clauses(residual: base.CNF, block: tuple[int, ...]) -> tuple[base.Clause, ...]:
    bset = set(block)
    rows = []
    for clause in residual:
        vars_ = {abs(lit) for lit in clause}
        if vars_ and vars_ <= bset:
            rows.append(clause)
    return tuple(sorted(rows, key=lambda c: (len(c), c)))


def assignment_for_local_state(block: tuple[int, ...], state: tuple[int, ...]) -> dict[int, bool]:
    return {v: bool(bit) for v, bit in zip(block, state)}


def compositions(total: int, k: int):
    if k == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, k - 1):
            yield (first,) + tail


def canonical_assignment(
    hist: tuple[int, ...],
    center_value: int,
    local_states: tuple[tuple[int, ...], ...],
) -> dict[int, bool]:
    assignment: dict[int, bool] = {aug.CENTER: bool(center_value)}
    cursor = 0
    for state_idx, count in enumerate(hist):
        for _ in range(count):
            block = aug.BLOCKS[cursor]
            state = local_states[state_idx]
            assignment.update(assignment_for_local_state(block, state))
            cursor += 1
    assert cursor == len(aug.BLOCKS)
    return assignment


def clause_block_pattern(clause: base.Clause):
    var_to_block_pos = {}
    for bi, block in enumerate(aug.BLOCKS):
        for pos, var in enumerate(block):
            var_to_block_pos[var] = (bi, pos)

    source_blocks = []
    seen = set()
    for lit in clause:
        var = abs(lit)
        if var == aug.CENTER:
            continue
        bi, _ = var_to_block_pos[var]
        if bi not in seen:
            seen.add(bi)
            source_blocks.append(bi)

    role_of = {bi: role for role, bi in enumerate(source_blocks)}
    pattern = []
    for lit in clause:
        var = abs(lit)
        if var == aug.CENTER:
            pattern.append(("center", -1, -1, lit > 0))
        else:
            bi, pos = var_to_block_pos[var]
            pattern.append(("block", role_of[bi], pos, lit > 0))
    return tuple(pattern), len(source_blocks)


def feasible_type_tuple(type_tuple: tuple[int, ...], hist: tuple[int, ...]) -> bool:
    need = Counter(type_tuple)
    return all(need[t] <= hist[t] for t in need)


def augmented_clause_holds_direct(
    clause: base.Clause,
    hist: tuple[int, ...],
    center_value: int,
    local_states: tuple[tuple[int, ...], ...],
) -> bool:
    """Evaluate an entire S_m clause orbit from histogram coordinates only.

    No group elements or orbit images are enumerated.  If a representative
    mentions r distinct blocks, we enumerate only local-state TYPE tuples for
    those r roles.  Here the synthesized alphabet has constant size four and
    the frozen clause grammar has block arity at most two.
    """
    pattern, block_arity = clause_block_pattern(clause)
    assert block_arity <= 2
    for type_tuple in product(range(len(local_states)), repeat=block_arity):
        if not feasible_type_tuple(type_tuple, hist):
            continue
        clause_true = False
        for kind, role, pos, positive in pattern:
            if kind == "center":
                value = bool(center_value)
            else:
                value = bool(local_states[type_tuple[role]][pos])
            lit_true = value if positive else not value
            if lit_true:
                clause_true = True
                break
        if not clause_true:
            return False
    return True


def derive_orbit_representatives(residual: base.CNF):
    group = aug.generator_closure()
    residual_set = set(residual)
    unseen = set(residual)
    reps = []
    while unseen:
        seed = min(unseen, key=lambda c: (len(c), c))
        orbit = set(aug.orbit_of_clause(seed, group))
        assert orbit <= residual_set
        rep = min(orbit, key=lambda c: (len(c), c))
        reps.append(rep)
        unseen -= orbit
    return tuple(reps)


def direct_orbit_semantics_crosscheck(
    clause: base.Clause,
    hist: tuple[int, ...],
    center_value: int,
    local_states: tuple[tuple[int, ...], ...],
) -> bool:
    """Finite audit only: compare direct histogram semantics with explicit S4 orbit."""
    assignment = canonical_assignment(hist, center_value, local_states)
    explicit = all(
        eval_clause(image, assignment)
        for image in aug.orbit_of_clause(clause, aug.generator_closure())
    )
    direct = augmented_clause_holds_direct(clause, hist, center_value, local_states)
    assert direct == explicit
    return direct


def minimal_unsat_orbit_subset(
    reps: tuple[base.Clause, ...],
    quotient_states: tuple[tuple[int, tuple[int, ...]], ...],
    local_states: tuple[tuple[int, ...], ...],
):
    # Exact finite synthesis over the 2^8 rule subsets, cardinality then lexical.
    # No scoring, randomness, branch heuristic, SAT solver, or semantic oracle.
    for size in range(1, len(reps) + 1):
        for indices in combinations(range(len(reps)), size):
            if all(
                not all(
                    augmented_clause_holds_direct(reps[i], hist, center, local_states)
                    for i in indices
                )
                for center, hist in quotient_states
            ):
                return indices
    return None


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
    residual = state.residual
    fingerprint = base.fingerprint(residual)
    assert fingerprint == "990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6"

    # Machine-synthesize the local alphabet from clauses fully internal to a block.
    block_local = [local_block_clauses(residual, block) for block in aug.BLOCKS]
    signatures = [
        tuple(local_signature(c, block) for c in clauses)
        for block, clauses in zip(aug.BLOCKS, block_local)
    ]
    assert len(set(signatures)) == 1
    local_sig = signatures[0]

    first_block = aug.BLOCKS[0]
    local_states = tuple(
        bits
        for bits in product((0, 1), repeat=len(first_block))
        if all(eval_clause(c, assignment_for_local_state(first_block, bits)) for c in block_local[0])
    )
    assert len(local_states) == 4

    reps = derive_orbit_representatives(residual)
    assert len(reps) == 8

    # Exact assignment quotient: an S4 orbit is center bit + histogram of local types.
    hists = tuple(compositions(len(aug.BLOCKS), len(local_states)))
    quotient_states = tuple((center, hist) for center in (0, 1) for hist in hists)
    assert len(hists) == 35
    assert len(quotient_states) == 70

    # Coverage audit: local-gate-satisfying assignments are exactly partitioned by histograms.
    # Sum of multinomial orbit sizes over all histograms is 4^4; center doubles it.
    from math import factorial
    orbit_coverage = 0
    for hist in hists:
        denom = 1
        for count in hist:
            denom *= factorial(count)
        orbit_coverage += factorial(len(aug.BLOCKS)) // denom
    orbit_coverage *= 2
    assert orbit_coverage == 2 * (len(local_states) ** len(aug.BLOCKS)) == 512

    rejection_rows = []
    violating_orbit_counts = Counter()
    direct_explicit_crosschecks = 0
    max_block_arity = 0
    for center, hist in quotient_states:
        failed = []
        for idx, rep in enumerate(reps):
            _, arity = clause_block_pattern(rep)
            max_block_arity = max(max_block_arity, arity)
            direct = augmented_clause_holds_direct(rep, hist, center, local_states)
            # Audit every frozen quotient state against explicit S4 semantics.
            direct_orbit_semantics_crosscheck(rep, hist, center, local_states)
            direct_explicit_crosschecks += 1
            if not direct:
                failed.append(idx)
        assert failed, (center, hist)
        witness = min(failed)
        violating_orbit_counts[witness] += 1
        rejection_rows.append({
            "center": center,
            "hist": list(hist),
            "violated_orbit": witness,
        })

    minimal_indices = minimal_unsat_orbit_subset(reps, quotient_states, local_states)
    assert minimal_indices is not None

    # Compact structural certificate.  The verifier regenerates all 70 states;
    # rejection_rows are diagnostics and are not required certificate payload.
    certificate = {
        "kind": "SYMMETRY_QUOTIENT_PROGRAM",
        "source_fingerprint": fingerprint,
        "center": aug.CENTER,
        "blocks": [list(b) for b in aug.BLOCKS],
        "local_clause_signature": [list(sig) for sig in local_sig],
        "local_states": [list(s) for s in local_states],
        "orbit_representatives": [list(reps[i]) for i in minimal_indices],
        "histogram_sum": len(aug.BLOCKS),
    }
    cert_bytes = len(json.dumps(certificate, separators=(",", ":"), sort_keys=True).encode("utf-8"))

    # A transparent proof-language unit accounting, distinct from old CNF units.
    cert_units = (
        1
        + 1
        + sum(len(b) for b in aug.BLOCKS)
        + sum(len(sig) for sig in local_sig)
        + sum(len(s) for s in local_states)
        + sum(len(reps[i]) for i in minimal_indices)
        + len(minimal_indices)
    )

    report = {
        "schema": "JANUS/C025/PHP54-MACHINE-SYNTHESIZED-QUOTIENT/v1",
        "P_VS_NP": "OPEN",
        "frozen_case": "PHP_5_4_C1",
        "fingerprint": fingerprint,
        "source": {
            "live_variables": len(base.vars_of(residual)),
            "raw_assignment_space": 2 ** len(base.vars_of(residual)),
            "cnf_clauses": len(residual),
            "cnf_state_units": base.state_units(residual),
            "old_phi": base.progress_phi(state),
        },
        "machine_synthesized_coordinates": {
            "block_count": len(aug.BLOCKS),
            "block_width": len(aug.BLOCKS[0]),
            "local_clause_signature": [list(sig) for sig in local_sig],
            "local_state_alphabet": [list(s) for s in local_states],
            "local_state_count": len(local_states),
            "local_gate_assignment_space": 2 * (len(local_states) ** len(aug.BLOCKS)),
            "histogram_count": len(hists),
            "quotient_state_count": len(quotient_states),
            "exact_assignment_coverage": orbit_coverage,
            "raw_to_quotient_ratio": (2 ** len(base.vars_of(residual))) / len(quotient_states),
            "local_valid_to_quotient_ratio": orbit_coverage / len(quotient_states),
        },
        "direct_augmented_semantics": {
            "orbit_representatives": len(reps),
            "max_block_arity": max_block_arity,
            "group_elements_enumerated_by_decision_rule": 0,
            "frozen_crosschecks_against_explicit_S4": direct_explicit_crosschecks,
            "all_crosschecks_pass": True,
            "all_quotient_states_rejected": len(rejection_rows) == len(quotient_states),
            "violating_orbit_histogram": {str(k): v for k, v in sorted(violating_orbit_counts.items())},
        },
        "exact_program_synthesis": {
            "candidate_rule_subsets": 2 ** len(reps) - 1,
            "ordering": "subset cardinality then lexicographic indices",
            "heuristic": False,
            "minimal_orbit_rule_count": len(minimal_indices),
            "minimal_orbit_rule_indices": list(minimal_indices),
            "minimal_orbit_representatives": [list(reps[i]) for i in minimal_indices],
            "certificate_units": cert_units,
            "certificate_json_bytes": cert_bytes,
            "certificate_under_numeric_256": cert_units <= state.state_cap,
        },
        "result": {
            "quotient_status": "UNSAT",
            "reason": "ALL_70_EXACT_S4_QUOTIENT_STATES_REJECTED_BY_DIRECT_ORBIT_SEMANTICS",
            "frozen_php54_old_engine_status": result["status"],
            "strict_representation_breakthrough": True,
        },
        "interpretation_gate": {
            "positive": "THE_MACHINE_DERIVED_A_4_SYMBOL_LOCAL_ALPHABET_AND_A_70_STATE_EXACT_SYMMETRY_QUOTIENT; PHP_5_4_C1_IS_REFUTED_IN_THIS_NEW_PROOF_LANGUAGE_WITHOUT_ENUMERATING_8192_ASSIGNMENTS_OR_S4_IMAGES_DURING_THE_DECISION_RULE",
            "next": "GENERALIZE_THE_SYNTHESIS_FROM_HARDCODED_BLOCKS_TO_CERTIFIED_BLOCK_SYSTEM_DISCOVERY_AND_TEST_PHP_(m+1)_m_SCALING; THEN_SEARCH_FOR_OTHER_CONSTANT_LOCAL_ALPHABET_BOUNDED_BLOCK_ARITY_FAMILIES",
            "failure_mode": "A_UNIVERSAL_P_EQUALS_NP_CLAIM_REQUIRES_POLYNOMIAL_DISCOVERY_OF_THE_COORDINATE_SYSTEM_AND_POLYNOMIAL_QUOTIENT_SIZE_FOR_ARBITRARY_CNF; NEITHER_IS_ESTABLISHED",
        },
        "scientific_boundary": {
            "finite_frozen_witness": True,
            "no_sat_oracle": True,
            "no_semantic_equivalence_oracle": True,
            "no_ml": True,
            "no_randomness": True,
            "no_score_ranking": True,
            "exact_exhaustive_rule_subset_synthesis": True,
            "block_system_currently_supplied_by_exact_prior_S4_certificate": True,
            "universal_block_discovery": "OPEN",
            "universal_polynomial_quotient": "OPEN",
            "universal_polynomial_algorithm": "OPEN",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
