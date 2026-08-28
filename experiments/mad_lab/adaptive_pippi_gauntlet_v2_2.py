#!/usr/bin/env python3
"""PIPPI ruthless gauntlet v2.2 exact-label scalability wrapper.

Relative to v2.0 experimental policy, nothing is changed. Relative to v2.1,
this also replaces materialization of every candidate's post-elimination CNF
when only the canonical engine's pre-compression raw-cap label is needed.
The replacement is an exact 2-CNF raw-set resolution evaluator self-tested for
field-by-field equality against eliminate_var_capped.

Counted STATIC/KEYMASTER/ORACLE transitions still use the canonical engine plus
verify_elimination_transition. P_VS_NP=OPEN.
"""
from __future__ import annotations

from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import adaptive_pippi_gauntlet_v2 as v2
from experiments.mad_lab import keymaster_scalable_feature_tokens as scalable_features
from experiments.mad_lab import keymaster_scalable_exact_root_labels as scalable_labels

P_VS_NP = "OPEN"


def main() -> int:
    v1.candidate_tokens = scalable_features.candidate_tokens_fast
    v2.exact_pq_episode = scalable_labels.exact_track_episode_fast
    return v2.main()


if __name__ == "__main__":
    raise SystemExit(main())
