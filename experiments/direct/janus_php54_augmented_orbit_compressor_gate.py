#!/usr/bin/env python3
from __future__ import annotations

from collections import Counter, deque
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.direct import janus_unified_proof_carrying_akinator_jec as base
from experiments.direct import janus_unified_macro_restore_v2 as v2
from experiments.direct.janus_php54_macro_restore_attack import pigeonhole

BLOCKS = ((23, 24, 25), (26, 27, 28), (29, 30, 31), (32, 33, 34))
CENTER = 21
CAPTURED: base.EngineState | None = None
ORIGINAL = v2.discover_macro_restore_v2


def capture(state: base.EngineState):
    global CAPTURED
    out = ORIGINAL(state)
    if out is None and not any(v in set(state.root_vars) for v in base.vars_of(state.residual)):
        CAPTURED = state
    return out


def compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    """Permutation composition p after q on block indices."""
    return tuple(p[q[i]] for i in range(len(q)))


def generator_closure() -> tuple[tuple[int, ...], ...]:
    ident = (0, 1, 2, 3)
    gens = ((1, 0, 2, 3), (0, 2, 1, 3), (0, 1, 3, 2))
    seen = {ident}
    q = deque([ident])
    while q:
        cur = q.popleft()
        for g in gens:
            nxt = compose(g, cur)
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return tuple(sorted(seen))


def mapping_for_perm(perm: tuple[int, ...]) -> dict[int, int]:
    mapping = {CENTER: CENTER}
    for src_i, dst_i in enumerate(perm):
        for pos in range(3):
            mapping[BLOCKS[src_i][pos]] = BLOCKS[dst_i][pos]
    return mapping


def rename_clause(clause: base.Clause, perm: tuple[int, ...]) -> base.Clause:
    mapping = mapping_for_perm(perm)
    out = base.canon_clause(
        (mapping.get(abs(l), abs(l)) if l > 0 else -mapping.get(abs(l), abs(l)))
        for l in clause
    )
    assert out is not None
    return out


def orbit_of_clause(clause: base.Clause, group: tuple[tuple[int, ...], ...]) -> tuple[base.Clause, ...]:
    return tuple(sorted({rename_clause(clause, p) for p in group}, key=lambda c: (len(c), c)))


def compact_bytes(obj) -> int:
    return len(json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8"))


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
    assert base.fingerprint(residual) == "990124522dc5ee1a6871de798a0f3ef40f05c20a28cd9f3d9d2f062841695ea6"

    group = generator_closure()
    assert len(group) == 24

    residual_set = set(residual)
    unseen = set(residual)
    orbit_rows = []
    reps = []
    expanded_union: set[base.Clause] = set()

    while unseen:
        seed = min(unseen, key=lambda c: (len(c), c))
        orbit = orbit_of_clause(seed, group)
        orbit_set = set(orbit)
        assert orbit_set <= residual_set
        rep = min(orbit, key=lambda c: (len(c), c))
        reps.append(rep)
        expanded_union |= orbit_set
        unseen -= orbit_set
        orbit_rows.append({
            "representative": list(rep),
            "width": len(rep),
            "orbit_size": len(orbit),
            "members": [list(c) for c in orbit],
        })

    assert expanded_union == residual_set
    assert sum(row["orbit_size"] for row in orbit_rows) == len(residual)

    width_orbits = Counter(row["width"] for row in orbit_rows)
    width_clauses = Counter(len(c) for c in residual)

    # A proof-language candidate, not the existing CNF state metric.  We count
    # integer atoms/records explicitly: representatives plus one shared block
    # action certificate.  The generator certificate specifies 12 block vars,
    # the fixed center, and three adjacent swaps (six block indices + 3 records).
    representative_units = 1 + len(reps) + sum(len(c) for c in reps)
    group_certificate_units = 1 + 1 + 12 + 3 + 6
    augmented_candidate_units = representative_units + group_certificate_units

    certificate = {
        "kind": "AUGMENTED_CLAUSE_S4_ORBIT_CERTIFICATE",
        "center": CENTER,
        "blocks": [list(b) for b in BLOCKS],
        "generators": [[0, 1], [1, 2], [2, 3]],
        "group_order_from_generator_closure": len(group),
        "representatives": [list(c) for c in reps],
        "source_fingerprint": base.fingerprint(residual),
    }

    raw_payload = [list(c) for c in residual]
    raw_bytes = compact_bytes(raw_payload)
    cert_bytes = compact_bytes(certificate)

    report = {
        "schema": "JANUS/C025/PHP54-AUGMENTED-ORBIT-COMPRESSOR-GATE/v1",
        "P_VS_NP": "OPEN",
        "frozen_case": "PHP_5_4_C1",
        "fingerprint": base.fingerprint(residual),
        "existing_cnf": {
            "clauses": len(residual),
            "state_units": base.state_units(residual),
            "compact_json_bytes": raw_bytes,
            "width_histogram": {str(k): width_clauses[k] for k in sorted(width_clauses)},
        },
        "group_certificate": {
            "group": "S4 on four 3-variable blocks; center fixed",
            "generators": [[0, 1], [1, 2], [2, 3]],
            "generator_closure_order": len(group),
            "exact_replay": expanded_union == residual_set,
            "certificate_units": group_certificate_units,
        },
        "augmented_clause_representation": {
            "orbit_count": len(orbit_rows),
            "representative_count": len(reps),
            "representative_units": representative_units,
            "candidate_total_units": augmented_candidate_units,
            "candidate_under_existing_numeric_cap_256": augmented_candidate_units <= state.state_cap,
            "compact_json_bytes": cert_bytes,
            "raw_to_certificate_byte_ratio": raw_bytes / cert_bytes,
            "raw_clause_to_orbit_ratio": len(residual) / len(orbit_rows),
            "orbit_width_histogram": {str(k): width_orbits[k] for k in sorted(width_orbits)},
            "orbits": orbit_rows,
        },
        "interpretation_gate": {
            "positive": "ONE_SHARED_GROUP_CERTIFICATE_EXACTLY_REPLAYS_THE_FROZEN_56_CLAUSE_RESIDUAL_FROM_ORBIT_REPRESENTATIVES_WITHOUT_MATERIALIZING_ALL_S4_IMAGES",
            "next": "IMPLEMENT_AUGMENTED_RESOLUTION_OR_AN_EQUIVALENT_PROOF_CARRYING_ORBIT_OPERATION_DIRECTLY_ON_REPRESENTATIVE_PLUS_GENERATORS_AND_TEST_WHETHER_PHI_CAN_DROP_BELOW_13_WITHOUT_EXPANDING_THE_ORBITS",
            "failure_mode": "IF_GROUP_LEVEL_INFERENCE_REQUIRES_EXPANDING_FACTORIALLY_MANY_IMAGES_OR_NONPOLYNOMIAL_DISCOVERY_THEN_THE_COMPRESSION_IS_DESCRIPTIVE_ONLY",
        },
        "scientific_boundary": {
            "finite_frozen_witness": True,
            "exact_group_generator_closure": True,
            "no_sat_oracle": True,
            "no_semantic_equivalence_oracle": True,
            "heuristic_promotion": False,
            "existing_state_units_and_augmented_candidate_units_are_different_proof_languages": True,
            "candidate_under_256_is_not_yet_an_admission_to_the_existing_engine_cap": True,
            "universal_polynomial_group_inference": "OPEN",
            "universal_P_vs_NP_conclusion": "NONE",
            "P_VS_NP": "OPEN",
        },
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
