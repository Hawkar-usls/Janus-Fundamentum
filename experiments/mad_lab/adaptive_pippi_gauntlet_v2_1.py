#!/usr/bin/env python3
"""PIPPI ruthless gauntlet v2.1 scalability wrapper.

No experimental policy, feature definition, adviser implementation, governance
rule, score, cap, schedule, or proof semantics changes relative to v2.0.
Only the implementation of the already-frozen candidate token computation is
replaced by a self-tested semantically identical incidence-count version so the
250:250 OOD boss measures JANUS rather than redundant Python membership scans.

P_VS_NP=OPEN.
"""
from __future__ import annotations

from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import adaptive_pippi_gauntlet_v2 as v2
from experiments.mad_lab import keymaster_scalable_feature_tokens as scalable

P_VS_NP = "OPEN"


def main() -> int:
    v1.candidate_tokens = scalable.candidate_tokens_fast
    return v2.main()


if __name__ == "__main__":
    raise SystemExit(main())
