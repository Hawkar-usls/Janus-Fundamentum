#!/usr/bin/env python3
"""PIPPI ruthless gauntlet v2.4 — corrected control + TRUE 250 boss.

This preserves v2.0 learning/controller policy and v2 Keymaster governance while
fixing a benchmark artifact diagnosed from the completed v2.3 receipt:
- every non-formation track is randomly but deterministically relabelled by seed,
  preserving exact isomorphism while breaking numeric STATIC-order correlation
  with distinguished graph roles;
- the mandatory 250:250 OOD boss uses four independent fresh formulas;
- boss local cap is EXACT_MIN_RAW_ONLY, so a counted success must reach an exact
  minimum-raw pivot rather than any member of a huge q30 safe plateau.

Official race stages retain the q30 numeric cap from v2.0. The hard-boss policy
never rewrites the official frontier. All implementation fast paths are exact
and equivalence-gated. P_VS_NP=OPEN.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from experiments.mad_lab import adaptive_pippi_pitstop_ladder as v1
from experiments.mad_lab import adaptive_pippi_gauntlet_v2 as v2
from experiments.mad_lab import keymaster_scalable_feature_tokens as sf
from experiments.mad_lab import keymaster_scalable_exact_root_labels as sl
from experiments.mad_lab import keymaster_scalable_exact_2cnf_transition as st
from experiments.mad_lab import asymmetric_pq_track_relabelled as relabel

P_VS_NP = "OPEN"
BOSS_COUNT = 4
BOSS_FPS: list[str] = []
BOSS_SAFE_COUNTS: list[int] = []
BOSS_RAW_HISTS: list[dict[str, int]] = []


def hard_episode(cnf, p: int, q: int, seed: int, source: str, stage_serial: int) -> dict[str, Any]:
    e = sl.exact_track_episode_fast(cnf, p, q, seed, source, stage_serial)
    if "MANDATORY_BLIND_250x250_BOSS" in source:
        cap = min(e["raw"])
        e["local_stress_cap"] = cap
        e["safe_indices"] = [i for i, x in enumerate(e["raw"]) if x <= cap]
        e["boss_cap_policy"] = "EXACT_MIN_RAW_ONLY"
        BOSS_FPS.append(e["fingerprint"])
        BOSS_SAFE_COUNTS.append(len(e["safe_indices"]))
        hist: dict[str, int] = {}
        for x in e["raw"]:
            hist[str(x)] = hist.get(str(x), 0) + 1
        BOSS_RAW_HISTS.append(hist)
    return e


def _out_dir_from_argv() -> Path | None:
    if "--out-dir" not in sys.argv:
        return None
    i = sys.argv.index("--out-dir")
    return Path(sys.argv[i + 1]) if i + 1 < len(sys.argv) else None


def main() -> int:
    v1.candidate_tokens = sf.candidate_tokens_fast
    v2.exact_pq_episode = hard_episode
    v2.pqtrack.construct = relabel.construct_relabelled
    v2.root_runtime = st.root_runtime_fast

    original_make = v2.make_pq_stage
    def make_stage_hardened(p: int, q: int, stage_serial: int, count: int, used: set[str], source: str = "RUTHLESS_PQ_TRACK"):
        if "MANDATORY_BLIND_250x250_BOSS" in source:
            count = BOSS_COUNT
        return original_make(p, q, stage_serial, count, used, source)
    v2.make_pq_stage = make_stage_hardened

    rc = v2.main()
    out = _out_dir_from_argv()
    if rc == 0 and out is not None:
        path = out / "gauntlet-result.json"
        result = json.loads(path.read_text())
        boss = result.get("boss_250x250")
        if boss is None:
            raise AssertionError("v2.4 requires completed boss receipt")
        boss["formula_count"] = len(BOSS_FPS)
        boss["fresh_fingerprints"] = list(BOSS_FPS)
        boss["strict_min_raw_cap"] = True
        boss["cap_policy"] = "EXACT_MIN_RAW_ONLY"
        boss["safe_pivot_counts_per_formula"] = list(BOSS_SAFE_COUNTS)
        boss["raw_unit_histograms_per_formula"] = list(BOSS_RAW_HISTS)
        boss["numeric_static_baseline_decorrelated_by_seeded_isomorphic_relabelling"] = True
        boss["v2_3_q30_boss_score_is_not_used_as_strength_claim"] = True
        result["schema"] = "JANUS/PIPPI/RUTHLESS-GAUNTLET/v2.4.0"
        result["benchmark_correction"] = {
            "source": "V2_3_POST_RUN_DIAGNOSTIC",
            "problem": "LEXICOGRAPHIC_DISTINGUISHED_ROLE_CORRELATED_WITH_NUMERIC_STATIC_BASELINE_AND_Q30_TIE_EXPANDED_SAFE_SET",
            "correction": [
                "SEED_DERIVED_ISOMORPHIC_VARIABLE_RELABEL",
                "FOUR_INDEPENDENT_250x250_BOSS_FORMULAS",
                "BOSS_CAP_EXACT_MIN_RAW_ONLY"
            ],
            "official_stage_cap_policy_changed": False,
            "learning_stack_changed": False,
            "P_VS_NP": P_VS_NP,
        }
        result["scientific_firewall"]["BOSS_NUMERIC_BASELINE_ROLE_CORRELATION_BROKEN"] = True
        result["scientific_firewall"]["BOSS_REQUIRES_EXACT_MIN_RAW_PIVOT"] = True
        result["scientific_firewall"]["BOSS_FORMULA_COUNT"] = BOSS_COUNT
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps({
            "V2_4_POSTPROCESS": "PASS",
            "boss_formula_count": len(BOSS_FPS),
            "boss_safe_counts": BOSS_SAFE_COUNTS,
            "official_frontier": result["official_frontier"],
            "boss_score": boss["score"],
            "P_VS_NP": P_VS_NP,
        }, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
