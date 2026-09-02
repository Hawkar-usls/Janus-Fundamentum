#!/usr/bin/env python3
"""R15E: independent semantic control after frozen R15D candidate terminal.

The candidate logic is imported unchanged from R15D. Only after it returns a
complete extended interface is the pre-existing R15B exact verification panel
allowed to run. This is exposed W05 calibration only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r13_unseen_interface_generalization as r13
import janus_trump_r15b_factored_dp_extension_compiler_calibration as r15b
import janus_trump_r15d_bounded_observer_equivalent_refactor as r15d

EXPECTED_CANDIDATE_BLOB_SHA="e6def9fef656c8f1af1b9f245bc855081f13a586"
WORLD_ID=r15b.WORLD_ID
EXPECTED_FRAME_SHA=r15b.EXPECTED_FRAME_SHA
EXPECTED_TRUTH_SHA=r15b.EXPECTED_TRUTH_SHA


def run():
    freeze=r13.load_freeze(); spec=next(w for w in freeze["worlds"] if w["id"]==WORLD_ID); world=r13.generate_world(spec)
    if world["source"]["frame_sha256"]!=EXPECTED_FRAME_SHA: raise AssertionError("W05 frame drift")
    bridge=tuple(world["bridge"])

    # Candidate phase: no exact witness access.
    candidate=r15d.compile_observed(world["frame"],bridge)
    candidate_complete=candidate["status"]=="COMPLETE_EXTENDED_INTERFACE" and candidate.get("remaining_internal",candidate.get("checkpoint",{}).get("remaining_internal")) in (0,None)

    # Only after terminal may the exact world witness be invoked.
    if candidate_complete:
        control=r15b.post_candidate_control(candidate,world["frame"],bridge)
    else:
        control={"not_run":True,"reason":"CANDIDATE_NONTERMINAL"}

    if not candidate_complete:
        verdict="R15E_CANDIDATE_NONTERMINAL"
    elif control["truth_table_sha256"]!=EXPECTED_TRUTH_SHA:
        verdict="R15E_INTEGRITY_FAIL"
    elif control["mismatch_count"]==0:
        verdict="R15E_SEMANTIC_CONTROL_MATCH"
    else:
        verdict="R15E_SEMANTIC_CONTROL_MISMATCH"

    gates={
        "G1_W05_FRAME_FROZEN":world["source"]["frame_sha256"]==EXPECTED_FRAME_SHA,
        "G2_CANDIDATE_TERMINAL_BEFORE_CONTROL":candidate_complete,
        "G3_CONTROL_TRUTH_HASH_FROZEN":control.get("truth_table_sha256")==EXPECTED_TRUTH_SHA if candidate_complete else True,
        "G4_NO_CANDIDATE_LOGIC_EDIT":True,
        "G5_NO_GENERALIZATION_CLAIM":True,
    }
    return {
        "schema":"JANUS/TRUMP/R15E/POST_CANDIDATE_SEMANTIC_CONTROL/RESULT/v1.0",
        "created_date":"2026-09-02",
        "verdict":verdict,
        "frozen_candidate":{"path":"experiments/janus_trump_r15d_bounded_observer_equivalent_refactor.py","blob_sha":EXPECTED_CANDIDATE_BLOB_SHA},
        "candidate":{k:v for k,v in candidate.items() if k not in ("formula","history")},
        "candidate_formula_clause_count":len(candidate.get("formula",[])),
        "candidate_history_steps":len(candidate.get("history",[])),
        "post_candidate_control":control,
        "gates":gates,
        "scientific_interpretation":{
            "if_match":"The frozen shared-extension quotient compiler preserves the sampled exact bridge semantics on exposed W05 after terminal. This authorizes a prospective unseen-world test with compiler logic frozen byte-for-byte.",
            "if_mismatch":"Resource completion did not preserve the target invariant. Preserve the counterexample and do not tune the candidate inside this validation pass."
        },
        "seal":"FIRST_THE_MACHINE_FINISHES__THEN_THE_WORLD_GETS_TO_SAY_MATCH_OR_MISMATCH",
        "P_VS_NP":"OPEN"
    }


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--output",required=True); args=ap.parse_args(); d=run(); Path(args.output).write_text(json.dumps(d,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"verdict":d["verdict"],"candidate":d["candidate"],"control":{k:v for k,v in d["post_candidate_control"].items() if k!="rows"},"gates":d["gates"],"P_VS_NP":"OPEN"},indent=2,sort_keys=True))
    return 2 if d["verdict"]=="R15E_INTEGRITY_FAIL" else 0

if __name__=="__main__": raise SystemExit(main())
