#!/usr/bin/env python3
from __future__ import annotations

import copy

import janus_c049_1_b4_6_2_full_iterative_cycle_verifier as verifier


def verify_reconstruction(
    reconstruction: dict,
    manifest: dict,
    transcript: dict,
    blocks: list[tuple[int, ...]],
    offsets: list[int],
    d: int,
    k: int,
) -> dict:
    verifier.verify_object_digest(reconstruction, "reconstruction_digest")
    root_id = int(manifest["execution"]["root_node_id"])
    root_node = next(
        item for item in manifest["node_results"] if int(item["node_id"]) == root_id
    )
    accepted = verifier.accepting_root_indices(root_node, k)
    if not accepted:
        raise AssertionError("round root has no accepting entry")
    selected = min(
        accepted,
        key=lambda index: (
            verifier.digest(root_node["node_up_k"]["entries"][index]),
            index,
        ),
    )
    expected_selection = {
        "accepting_root_entry_count": len(accepted),
        "selected_root_entry_index": selected,
        "rule": "MINIMUM_SHA256_THEN_ENTRY_INDEX_AMONG_EMPTY_BOUNDARY_WIDTH_AT_MOST_K",
    }
    if reconstruction["root_selection"] != expected_selection:
        raise AssertionError("round root selection mismatch")

    work = [int(manifest["audit"]["cumulative_work"])]
    events: list[dict] = []
    work[0] += len(accepted)
    events.append(
        {
            "event_index": 0,
            "kind": "ROOT_ACCEPTANCE_TESTS",
            "amount": len(accepted),
            "cumulative_work": work[0],
            "node_id": root_id,
        }
    )
    receipt = verifier.trace_entry(
        root_id,
        selected,
        manifest,
        transcript,
        set(),
        work,
        events,
    )
    order = [int(value) for value in receipt["order"]]
    cuts = verifier.exact_cut_widths(blocks, order, d)
    work[0] += len(cuts)
    events.append(
        {
            "event_index": len(events),
            "kind": "EXACT_LAYOUT_CUT_RECOMPUTATIONS",
            "amount": len(cuts),
            "cumulative_work": work[0],
            "order": order,
        }
    )
    maximum_width = max(item["width"] for item in cuts)
    layout = [
        {
            "position": position,
            "factor_id": factor_id,
            "normal_space_block_rref": list(blocks[factor_id]),
            "affine_offset": offsets[factor_id],
        }
        for position, factor_id in enumerate(order)
    ]
    expected = {
        "status": "ROUND_LAYOUT_WITNESS_RECONSTRUCTED",
        "root_selection": expected_selection,
        "reconstruction_receipt": receipt,
        "reconstructed_factor_order": order,
        "reconstructed_layout": layout,
        "exact_cut_transcript": cuts,
        "exact_maximum_width": maximum_width,
        "reconstruction_work": work[0]
        - int(manifest["audit"]["cumulative_work"]),
        "cumulative_work_after_reconstruction": work[0],
        "work_events": events,
        "found_layout": False,
        "no_layout_at_cap": False,
        "terminal": verifier.TERMINAL,
    }
    body = copy.deepcopy(reconstruction)
    body.pop("reconstruction_digest", None)
    if body != expected:
        raise AssertionError("round reconstruction transcript mismatch")
    if maximum_width > k:
        raise AssertionError("round reconstructed order exceeds k")
    return expected


verifier.verify_reconstruction = verify_reconstruction


if __name__ == "__main__":
    verifier.main()
