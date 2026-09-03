from __future__ import annotations

import contextlib
import io
import json

import janus_trump_r47t_depth2_pivot_unlocking_forensics as r47t


def run_compact():
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        d = r47t.run()
    compact = {
        "gate": "JANUS_TRUMP_R47T_COMPACT_RECEIPT",
        "source_gate": d["gate"],
        "source_verdict": d["verdict"],
        "sealed": d["sealed"],
        "delta": d["delta"],
        "candidate_explanations": d["candidate_explanations"],
        "successful_clause_drop_events": d["successful_clause_drop_events"],
        "v11_formula_diff": d["v11_layer"]["formula_diff"],
        "v20_parent_set_diff": d["v20_parent_set_diff"],
        "v20_resolvent_set_diff": d["v20_resolvent_set_diff"],
        "v20_before_summary": {
            "DP": {
                "p": d["v20_before_v11"]["DP"]["p"],
                "n": d["v20_before_v11"]["DP"]["n"],
                "p_times_n": d["v20_before_v11"]["DP"]["p_times_n"],
                "distinct_non_tautological_resolvents": d["v20_before_v11"]["DP"]["distinct_non_tautological_resolvents"],
                "forced_DP_CLV": d["v20_before_v11"]["DP"]["forced_DP_CLV"],
            },
            "final_CLV": d["v20_before_v11"]["normalization"]["final_CLV"],
            "accepted": d["v20_before_v11"]["accepted"],
        },
        "v20_after_summary": {
            "DP": {
                "p": d["v20_after_v11"]["DP"]["p"],
                "n": d["v20_after_v11"]["DP"]["n"],
                "p_times_n": d["v20_after_v11"]["DP"]["p_times_n"],
                "distinct_non_tautological_resolvents": d["v20_after_v11"]["DP"]["distinct_non_tautological_resolvents"],
                "forced_DP_CLV": d["v20_after_v11"]["DP"]["forced_DP_CLV"],
            },
            "final_CLV": d["v20_after_v11"]["normalization"]["final_CLV"],
            "accepted": d["v20_after_v11"]["accepted"],
        },
        "interpretation": d["interpretation"],
        "firewall": d["firewall"],
    }
    print(json.dumps(compact, sort_keys=True))
    return compact


if __name__ == "__main__":
    run_compact()
