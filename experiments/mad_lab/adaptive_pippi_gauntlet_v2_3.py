#!/usr/bin/env python3
"""PIPPI ruthless gauntlet v2.3 exact-scalability wrapper.

Experimental policy remains v2.0. Adviser algorithms remain frozen; only the
v2 Keymaster governance is the controlled architecture change vs the frozen
v1.2 race. This wrapper selects three self-tested implementation-equivalent
fast paths needed for the 250:250 boss:
- identical candidate feature tokens;
- identical pre-compression exact root labels;
- identical uniform-width-2 track canonicalization and width<=2 exact replay.

P_VS_NP=OPEN.
"""
from __future__ import annotations

from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import adaptive_pippi_gauntlet_v2 as v2
from experiments.mad_lab import keymaster_scalable_feature_tokens as sf
from experiments.mad_lab import keymaster_scalable_exact_root_labels as sl
from experiments.mad_lab import keymaster_scalable_exact_2cnf_transition as st
from experiments.mad_lab import asymmetric_pq_track_scalable as sg

P_VS_NP = "OPEN"


def main() -> int:
    v1.candidate_tokens = sf.candidate_tokens_fast
    v2.exact_pq_episode = sl.exact_track_episode_fast
    v2.pqtrack.construct = sg.construct_fast
    v2.root_runtime = st.root_runtime_fast
    return v2.main()


if __name__ == "__main__":
    raise SystemExit(main())
