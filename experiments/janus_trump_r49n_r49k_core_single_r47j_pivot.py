from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r47j_normalization_fixpoint_restart_v25_gap as r47j
import janus_trump_r49i_bipolar_nontauto_cross_union_width5_core_hunt as r49i
import janus_trump_r49m_r49k_obstruction_targeted_r47j_discharge as r49m

GATE = "JANUS_TRUMP_R49N_R49K_CORE_SINGLE_R47J_PIVOT"


def run(var: int):
    _, _, core = r49m.recreate_core()
    profile = r49i.variable_profile(core, int(var))
    row, candidate = r49m.candidate_row(core, int(var), profile)
    replay_pass = None
    if row.get("width4_safe", False):
        replay = r47j.independent_fixpoint_macro_replay(core, candidate)
        if not replay["pass"]:
            raise AssertionError(("R49N_SAFE_REPLAY_FAIL", var, replay))
        replay_pass = True
    row["R47J_independent_replay_pass"] = replay_pass
    return {
        "gate": GATE,
        "var": int(var),
        "core_hash": r49i.fhash(core),
        "core_CLV": list(r49i.clv(core)),
        "profile": profile,
        "candidate": row,
        "verdict": "WIDTH4_SAFE_R47J_DISCHARGE_FOUND" if row.get("width4_safe", False) else "PIVOT_DOES_NOT_DISCHARGE_TO_WIDTH4",
        "firewall": {
            "DIRECT_W4_STEP_COVERAGE": "OPEN",
            "P_VS_NP": "OPEN",
            "TRUMP_finished": False
        }
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--var", type=int, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a=ap.parse_args()
    out=run(a.var)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, sort_keys=True, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"gate":out["gate"],"var":out["var"],"verdict":out["verdict"],"candidate":out["candidate"],"firewall":out["firewall"]},sort_keys=True))


if __name__ == "__main__":
    main()
