from __future__ import annotations

import janus_trump_r50d_top1_fail_top2_rescue_structural_lemma_hunt as r50d


def pair_record(formula, probe, root_index, trace_step, provenance):
    """Preserve the frozen R50D experiment while correcting one integrity check.

    R50C's first_safe_rank has asymmetric semantics:
      * rank 1 means v1 is already safe; v2 may be either safe or unsafe.
      * rank 2 means v1 failed and v2 is safe.

    The original R50D extractor incorrectly required v2 to be safe in both
    classes, which rejects legitimate RANK1_SAFE_CONTROL states before the
    twelve rescue pairs can be extracted.  This wrapper changes no selector,
    feature, candidate, corpus, outcome, or theorem authority; it only makes
    the replay check agree exactly with the already-frozen R50C semantics.
    """
    if not probe["applicable"]:
        raise r50d.IntegrityFailure("R50D_PAIR_PROBE_NOT_APPLICABLE")
    selected = probe["selected_rows"]
    if len(selected) != 2:
        raise r50d.IntegrityFailure(("R50D_EXPECTED_TOP2", len(selected), probe["state_hash"]))
    first_safe_rank = probe["first_safe_rank"]
    if first_safe_rank not in (1, 2):
        raise r50d.IntegrityFailure(("R50D_R50C_TOP2_REGRESSION", probe["state_hash"], first_safe_rank))

    v1 = int(selected[0]["var"])
    v2 = int(selected[1]["var"])
    i1 = r50d.input_descriptor(formula, v1)
    i2 = r50d.input_descriptor(formula, v2)
    o1 = r50d.outcome_descriptor(formula, v1)
    o2 = r50d.outcome_descriptor(formula, v2)

    if bool(o1["width4_safe"]) != (first_safe_rank == 1):
        raise r50d.IntegrityFailure(("R50D_RANK1_OUTCOME_MISMATCH", probe["state_hash"]))
    if first_safe_rank == 2 and not bool(o2["width4_safe"]):
        raise r50d.IntegrityFailure(("R50D_RANK2_RESCUE_OUTCOME_MISMATCH", probe["state_hash"]))

    return {
        "state_hash": probe["state_hash"],
        "state_CLV": probe["state_CLV"],
        "root_index": int(root_index),
        "trace_step": int(trace_step),
        "root_provenance": provenance,
        "class": "RANK1_SAFE_CONTROL" if first_safe_rank == 1 else "RANK1_FAIL_RANK2_RESCUE",
        "rank1": {"input": i1, "outcome": o1},
        "rank2": {"input": i2, "outcome": o2},
        "frozen_named_candidate": {
            "name": "MINORITY_POLARITY_SUPPORT_NONDECREASE",
            "formula": "min(|P_v2|,|N_v2|) >= min(|P_v1|,|N_v1|)",
            "holds": bool(i2["minority_parent_count"] >= i1["minority_parent_count"]),
        },
    }


r50d.pair_record = pair_record


if __name__ == "__main__":
    r50d.main()
