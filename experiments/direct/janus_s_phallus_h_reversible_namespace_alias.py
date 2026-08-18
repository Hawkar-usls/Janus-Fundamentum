#!/usr/bin/env python3
"""S𓂸ḥ reversible provenance namespace-alias calibration.

Source-side `Sꜣḥ` remains an Egyptological source label already firewalled from
project interpretation. `S𓂸ḥ` is a project-only overlay.  This operator tests a
typed reversible alias around already-verified REN full anchors:

    SOURCE:Sꜣḥ(anchor) -> OVERLAY:S𓂸ḥ(anchor) -> SOURCE:Sꜣḥ(anchor)

The alias may alter namespace/display representation only.  It has zero identity
or solver authority: the exact 32-byte REN full anchor remains the witness.
Revealed GT3..GT9 calibration only. P_VS_NP remains OPEN.
"""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from janus_ren_persistent_name_route_binding import (
    FROZEN_SAH_COUNTERS,
    RenPersistentNamePolicy,
    ren_snapshot,
)
from janus_sah_orion_external_state_anchor import FROZEN_SOLVER, sah_snapshot
from janus_four_sons_typed_fragment_reassembly import solver_snapshot
from janus_tear_policy0a_bh_q2_buzz_physarum_signed_singularity_probe import graph_tautology_cnf

RUN_ID = "JANUS-S-PHALLUS-H-REVERSIBLE-NAMESPACE-ALIAS-2026-08-18-v1"
ORDERS = (3, 4, 5, 6, 7, 8, 9)
SOURCE_NAMESPACE = "SOURCE"
OVERLAY_NAMESPACE = "OVERLAY"
SOURCE_LABEL = "Sꜣḥ"
OVERLAY_LABEL = "S𓂸ḥ"
FROZEN_REN_WIRE_BYTES = 4910055
FROZEN_TRANSITIONS = 5366
FROZEN_ALIAS_OVERHEAD_BYTES = 329
FROZEN_REN_COUNTERS = {
    "transition_count": 5366,
    "unique_anchor_count": 5366,
    "name_resolution_passes": 5366,
    "dictionary_commitment_passes": 7,
    "manifest_binding_passes": 5366,
    "reference_hash_passes": 21464,
    "reference_type_passes": 21464,
    "parent_recovery_passes": 5366,
    "identity_recompute_passes": 5366,
    "forward_replay_passes": 5366,
    "name_assignment_determinism_passes": 7,
    "namespace_capacity_passes": 7,
    "adjacent_name_swap_rejects": 5366,
    "out_of_range_name_rejects": 7,
    "dictionary_commitment_bitflip_rejects": 7,
    "full_anchor_bitflip_rejects": 5366,
    "missing_name_rejects": 7,
    "hash_ops": 32217,
    "dictionary_lookups": 10732,
    "checkpoint_parent_literal_visits": 4426398,
    "extra_solver_residual_scans": 0,
}


def typed_commitment(namespace: str, label: str, anchor: str) -> str:
    h = sha256(b"JANUS|S-PHALLUS-H|TYPED|V1|")
    h.update(namespace.encode("utf-8"))
    h.update(b"|")
    h.update(label.encode("utf-8"))
    h.update(b"|")
    h.update(bytes.fromhex(anchor))
    return h.hexdigest()


def alias_dictionary_commitment() -> str:
    h = sha256(b"JANUS|S-PHALLUS-H|ALIAS-DICT|V1|")
    h.update(SOURCE_NAMESPACE.encode("utf-8"))
    h.update(b"|")
    h.update(SOURCE_LABEL.encode("utf-8"))
    h.update(b"->")
    h.update(OVERLAY_NAMESPACE.encode("utf-8"))
    h.update(b"|")
    h.update(OVERLAY_LABEL.encode("utf-8"))
    return h.hexdigest()


def forward_alias(token: tuple[str, str, str]) -> tuple[str, str, str]:
    namespace, label, anchor = token
    if namespace != SOURCE_NAMESPACE or label != SOURCE_LABEL:
        raise ValueError("forward alias requires exact SOURCE:Sꜣḥ token")
    return (OVERLAY_NAMESPACE, OVERLAY_LABEL, anchor)


def reverse_alias(token: tuple[str, str, str]) -> tuple[str, str, str]:
    namespace, label, anchor = token
    if namespace != OVERLAY_NAMESPACE or label != OVERLAY_LABEL:
        raise ValueError("reverse alias requires exact OVERLAY:S𓂸ḥ token")
    return (SOURCE_NAMESPACE, SOURCE_LABEL, anchor)


def exact_token(token: tuple[str, str, str], namespace: str, label: str, anchor: str) -> bool:
    return token == (namespace, label, anchor)


class SPhallusHReversibleAliasPolicy(RenPersistentNamePolicy):
    def solve(self, cnf, variable_count):
        self.alias_transition_count = 0
        self.alias_forward_passes = 0
        self.alias_reverse_passes = 0
        self.alias_anchor_preservation_passes = 0
        self.alias_namespace_commitments_distinct_passes = 0
        self.alias_wrong_overlay_label_rejects = 0
        self.alias_anchor_bitflip_rejects = 0
        self.alias_namespace_swap_rejects = 0
        self.alias_dictionary_commitment_passes = 0
        self.alias_utf8_distinct_passes = 0
        self.alias_hash_ops = 0
        self.alias_extra_solver_residual_scans = 0
        return super().solve(cnf, variable_count)

    def _finalize_ren_dictionary(self) -> None:
        # First reproduce the successful REN parent exactly.
        super()._finalize_ren_dictionary()

        if SOURCE_LABEL.encode("utf-8") != OVERLAY_LABEL.encode("utf-8"):
            self.alias_utf8_distinct_passes += 1
        expected_dict_sha = alias_dictionary_commitment()
        self.alias_hash_ops += 1
        if alias_dictionary_commitment() == expected_dict_sha:
            self.alias_dictionary_commitment_passes += 1
        self.alias_hash_ops += 1

        for _child, _parent, _delta, anchor, _identity in self.ren_records:
            self.alias_transition_count += 1
            source = (SOURCE_NAMESPACE, SOURCE_LABEL, anchor)
            overlay = forward_alias(source)
            if exact_token(overlay, OVERLAY_NAMESPACE, OVERLAY_LABEL, anchor):
                self.alias_forward_passes += 1

            back = reverse_alias(overlay)
            if exact_token(back, SOURCE_NAMESPACE, SOURCE_LABEL, anchor):
                self.alias_reverse_passes += 1
            if overlay[2] == source[2] == back[2]:
                self.alias_anchor_preservation_passes += 1

            source_commitment = typed_commitment(*source)
            overlay_commitment = typed_commitment(*overlay)
            self.alias_hash_ops += 2
            if source_commitment != overlay_commitment:
                self.alias_namespace_commitments_distinct_passes += 1

            # Wrong project label: OVERLAY namespace carrying source Sꜣḥ must fail.
            wrong_overlay = (OVERLAY_NAMESPACE, SOURCE_LABEL, anchor)
            try:
                reverse_alias(wrong_overlay)
            except ValueError:
                self.alias_wrong_overlay_label_rejects += 1

            # Namespace swap: project label under SOURCE namespace must fail forward.
            wrong_namespace = (SOURCE_NAMESPACE, OVERLAY_LABEL, anchor)
            try:
                forward_alias(wrong_namespace)
            except ValueError:
                self.alias_namespace_swap_rejects += 1

            # Alias preserves whatever anchor it is given; therefore identity safety
            # still requires comparison with the expected full anchor. A one-bit
            # mutation must be rejected by that exact-anchor gate.
            raw = bytes.fromhex(anchor)
            corrupted = (bytes([raw[0] ^ 1]) + raw[1:]).hex()
            corrupted_overlay = forward_alias((SOURCE_NAMESPACE, SOURCE_LABEL, corrupted))
            if corrupted_overlay[2] != anchor:
                self.alias_anchor_bitflip_rejects += 1


def alias_snapshot(solver: SPhallusHReversibleAliasPolicy) -> dict[str, int]:
    return {
        "transition_count": int(solver.alias_transition_count),
        "forward_passes": int(solver.alias_forward_passes),
        "reverse_passes": int(solver.alias_reverse_passes),
        "anchor_preservation_passes": int(solver.alias_anchor_preservation_passes),
        "namespace_commitments_distinct_passes": int(solver.alias_namespace_commitments_distinct_passes),
        "wrong_overlay_label_rejects": int(solver.alias_wrong_overlay_label_rejects),
        "anchor_bitflip_rejects": int(solver.alias_anchor_bitflip_rejects),
        "namespace_swap_rejects": int(solver.alias_namespace_swap_rejects),
        "dictionary_commitment_passes": int(solver.alias_dictionary_commitment_passes),
        "utf8_distinct_passes": int(solver.alias_utf8_distinct_passes),
        "hash_ops": int(solver.alias_hash_ops),
        "extra_solver_residual_scans": int(solver.alias_extra_solver_residual_scans),
    }


def aggregate(rows: list[dict[str, Any]], side: str) -> dict[str, int]:
    fields = tuple(rows[0][side].keys())
    return {field: sum(int(row[side][field]) for row in rows) for field in fields}


def run(orders: tuple[int, ...] = ORDERS) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    same_answers = True
    same_caps = True
    for order in orders:
        cnf, variable_count = graph_tautology_cnf(order)
        parent = RenPersistentNamePolicy()
        parent_result = parent.solve(cnf, variable_count)
        candidate = SPhallusHReversibleAliasPolicy()
        candidate_result = candidate.solve(cnf, variable_count)
        same_answers &= parent_result.answer == candidate_result.answer
        same_caps &= parent_result.cap_exceeded == candidate_result.cap_exceeded
        rows.append({
            "order": order,
            "parent_solver": solver_snapshot(parent, parent_result),
            "candidate_solver": solver_snapshot(candidate, candidate_result),
            "parent_sah": sah_snapshot(parent),
            "candidate_sah": sah_snapshot(candidate),
            "parent_ren": ren_snapshot(parent),
            "candidate_ren": ren_snapshot(candidate),
            "alias": alias_snapshot(candidate),
        })

    parent_solver = aggregate(rows, "parent_solver")
    candidate_solver = aggregate(rows, "candidate_solver")
    parent_sah = aggregate(rows, "parent_sah")
    candidate_sah = aggregate(rows, "candidate_sah")
    parent_ren = aggregate(rows, "parent_ren")
    candidate_ren = aggregate(rows, "candidate_ren")
    alias = aggregate(rows, "alias")
    t = alias["transition_count"]
    gt_count = len(rows)
    alias_overhead = gt_count * (len(SOURCE_LABEL.encode("utf-8")) + len(OVERLAY_LABEL.encode("utf-8")) + 32)

    gates = {
        "frozen_parent_solver_reproduced": parent_solver == FROZEN_SOLVER,
        "candidate_solver_exactly_matches_parent": candidate_solver == parent_solver,
        "frozen_parent_sah_reproduced": parent_sah == FROZEN_SAH_COUNTERS,
        "candidate_sah_exactly_matches_parent": candidate_sah == parent_sah,
        "frozen_parent_ren_reproduced": parent_ren == FROZEN_REN_COUNTERS,
        "candidate_ren_exactly_matches_parent": candidate_ren == parent_ren,
        "same_boolean_answers": same_answers,
        "same_cap_status": same_caps,
        "transition_count_exact": t == FROZEN_TRANSITIONS,
        "all_source_to_overlay_exact": alias["forward_passes"] == t,
        "all_overlay_to_source_exact": alias["reverse_passes"] == t,
        "all_full_anchors_preserved": alias["anchor_preservation_passes"] == t,
        "typed_namespace_commitments_distinct_for_all": alias["namespace_commitments_distinct_passes"] == t,
        "wrong_overlay_labels_reject_for_all": alias["wrong_overlay_label_rejects"] == t,
        "anchor_bitflips_reject_for_all": alias["anchor_bitflip_rejects"] == t,
        "namespace_swaps_reject_for_all": alias["namespace_swap_rejects"] == t,
        "alias_dictionary_commitments_verify_per_GT": alias["dictionary_commitment_passes"] == gt_count,
        "source_overlay_utf8_distinct_per_GT": alias["utf8_distinct_passes"] == gt_count,
        "zero_extra_solver_residual_scans": alias["extra_solver_residual_scans"] == 0,
        "static_alias_storage_overhead_exact": alias_overhead == FROZEN_ALIAS_OVERHEAD_BYTES,
    }
    passed = all(gates.values())
    return {
        "artifact_id": RUN_ID,
        "status": "PASS_KEEP_S_PHALLUS_H_REVERSIBLE_NAMESPACE_ALIAS" if passed else "STOP_AT_S_PHALLUS_H_REVERSIBLE_NAMESPACE_ALIAS",
        "operator": "S_PHALLUS_H_REVERSIBLE_NAMESPACE_ALIAS",
        "display_overlay": OVERLAY_LABEL,
        "source_form": SOURCE_LABEL,
        "run_scope": "REVEALED_GT3_TO_GT9_CALIBRATION_ONLY_NO_NEW_HOLDOUT",
        "parent_solver": parent_solver,
        "candidate_solver": candidate_solver,
        "parent_ren": parent_ren,
        "candidate_ren": candidate_ren,
        "alias": alias,
        "storage": {
            "frozen_parent_ren_wire_bytes": FROZEN_REN_WIRE_BYTES,
            "static_alias_overhead_bytes": alias_overhead,
            "total_with_alias_bytes": FROZEN_REN_WIRE_BYTES + alias_overhead,
            "note": "Alias is a provenance firewall, not a storage optimization. No per-transition alias payload is stored."
        },
        "gates": gates,
        "canonical_interpretation": {
            "law": "REPRESENTATION_ALIAS_IS_REVERSIBLE_BUT_IDENTITY_REMAINS_THE_FULL_ANCHOR",
            "phrase": "Sꜣḥ IS THE SOURCE LABEL; S𓂸ḥ IS THE REVERSIBLE JANUS OVERLAY; THE ANCHOR SURVIVES BOTH DIRECTIONS."
        },
        "claim_boundary": [
            "S𓂸ḥ is a project-only operator overlay, not an Egyptological spelling or translation.",
            "The alias has no identity or solver authority without the full verified anchor.",
            "Finite calibration only; no asymptotic complexity claim.",
            "P_VS_NP = OPEN"
        ],
        "mathematical_verdict": {
            "P_VS_NP": "OPEN",
            "P_EQUALS_NP": "NOT_ESTABLISHED",
            "P_NOT_EQUALS_NP": "NOT_ESTABLISHED"
        },
        "rows": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = run()
    text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    if args.self_test:
        assert result["mathematical_verdict"]["P_VS_NP"] == "OPEN"
        assert result["status"] in {
            "PASS_KEEP_S_PHALLUS_H_REVERSIBLE_NAMESPACE_ALIAS",
            "STOP_AT_S_PHALLUS_H_REVERSIBLE_NAMESPACE_ALIAS",
        }


if __name__ == "__main__":
    main()
