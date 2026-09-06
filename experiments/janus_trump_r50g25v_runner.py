from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r50g25v_two_residual_forensics as v


def corrected_dp_forensics(formula, r33, r47j):
    before = tuple(r33.measure(formula))
    rows = []
    for var in r33.variables(formula):
        record = r47j.r45a.exact_dp_record(formula, int(var))
        if record is None:
            rows.append({"var": int(var), "record": None})
            continue
        replay = r47j.r45a.independent_dp_replay(formula, record)
        transformed = r33.canonical_formula(record["transformed"])
        after = tuple(r33.measure(transformed))
        pos = sum(1 for c in formula if int(var) in c)
        neg = sum(1 for c in formula if -int(var) in c)
        rows.append({
            "var": int(var),
            "record": "PRESENT",
            "positive_parent_count": pos,
            "negative_parent_count": neg,
            "raw_parent_pair_upper": pos * neg,
            "replay_pass": bool(replay.get("pass")),
            "CLV_before": list(before),
            "CLV_after": list(after),
            "strict_CLV_descent": after < before,
            "clause_growth": int(after[0] - before[0]),
            "literal_growth": int(after[1] - before[1]),
        })
    rows.sort(key=lambda x: (
        x.get("record") is None,
        x.get("clause_growth", 10**9),
        x.get("literal_growth", 10**9),
        x["var"],
    ))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    # Correct a pre-run forensic bookkeeping defect in the implementation module:
    # successful exact-DP rows must explicitly mark record presence. The scientific
    # preregistration is unchanged; this runner is the authoritative V execution path.
    v.dp_forensics = corrected_dp_forensics
    out = v.run()
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "verdict": out["verdict"],
        "reproduced_residual_fixpoint_count": out["reproduced_residual_fixpoint_count"],
        "residuals": [
            {
                "source": r["source"],
                "minimized_hash": r["minimization"]["minimized_hash"],
                "minimized_CLV": r["minimization"]["minimized_CLV"],
                "residual_core_hash": r["minimization"]["residual_core_hash"],
                "residual_core_CLV": r["minimization"]["residual_core_CLV"],
                "multi_literal_RUP_checked": r["multi_literal_RUP"]["checked_candidate_count"],
                "multi_literal_RUP_found": r["multi_literal_RUP"]["certified_candidate_count"],
                "best_DP": r["unrestricted_DP_forensics"]["best_by_clause_then_literal_growth"],
                "best_DP_downstream": r["unrestricted_DP_forensics"]["best_downstream"],
            }
            for r in out["results"]
        ],
        "next_gate": out["next_gate"],
        "firewall": out["firewall"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
