from __future__ import annotations

import argparse
import json
from pathlib import Path

import janus_trump_r48q_width4_full_frozen_frontier_falsifier as r48q
import janus_trump_r48r_standard_php_width4_falsifier as r48r

GATE = "JANUS_TRUMP_R48R2_STANDARD_PHP_WIDTH4_PER_N_SHARDED_RECOVERY"
PARENT_UNKNOWN_SEAL = "5f325b2785c017bb7d9c7d1882725e3434cd162c"
ALLOWED_N = {5, 6, 7}
WIDTH_CAP = 4


def write_checkpoint(path: Path | None, data):
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def base_firewall():
    return {
        "UNIVERSAL_WIDTH_4_COVERAGE": "NOT_PROVED",
        "UNIVERSAL_CONSTANT_WIDTH_COVERAGE": "NOT_PROVED",
        "UNIVERSAL_POLYNOMIAL_ENVELOPE_COVERAGE": "OPEN",
        "O4_UNIVERSAL_COVERAGE": "OPEN",
        "SAT_IN_P": "NOT_PROVED",
        "P_EQ_NP": "NOT_PROVED",
        "P_NE_NP": "NOT_PROVED",
        "P_VS_NP": "OPEN",
        "TRUMP_finished": False,
    }


def run(n: int, output: Path | None = None):
    if n not in ALLOWED_N:
        raise AssertionError(("R48R2_N_OUT_OF_FROZEN_SCOPE", n, sorted(ALLOWED_N)))

    state = {
        "gate": GATE,
        "parent_UNKNOWN_RESOURCE_LIMIT_seal": PARENT_UNKNOWN_SEAL,
        "n_holes": int(n),
        "n_pigeons": int(n + 1),
        "width_cap": WIDTH_CAP,
        "stage": "INIT",
        "completed": False,
        "verdict": None,
        "source": None,
        "normalization": None,
        "width4": None,
        "error": None,
        "interpretation": {
            "single_structured_member_only": True,
            "success_proves_universal_W4": False,
            "one_explicit_obstruction_refutes_universal_W4_for_frozen_grammar": True,
            "external_timeout_or_cancel_is_negative_evidence": False,
        },
        "firewall": base_firewall(),
    }
    write_checkpoint(output, state)

    try:
        source, counts = r48r.standard_php_3cnf(n)
        source_hash = r48r.formula_hash(source)
        source_clv = list(r48r.clv(source))
        source_max_width = r48q.max_width(source)
        if source_max_width > 3:
            raise AssertionError(("R48R2_SOURCE_WIDTH_DRIFT", n, source_max_width))
        state["source"] = {
            **counts,
            "hash": source_hash,
            "CLV": source_clv,
            "max_width": int(source_max_width),
        }
        state["stage"] = "SOURCE_GENERATED"
        write_checkpoint(output, state)
    except Exception as e:
        state["stage"] = "SOURCE_ERROR"
        state["error"] = repr(e)
        write_checkpoint(output, state)
        raise

    try:
        norm, residual = r48r.normalize_source(source)
        if norm["semantic_sat"] is True:
            raise AssertionError(("R48R2_PHP_FALSE_SAT_TERMINAL", n, norm["terminal"]))
        state["normalization"] = {
            "terminal": norm["terminal"],
            "semantic_sat": norm["semantic_sat"],
            "segment_count": int(norm["segment_count"]),
            "SA_BVE_application_count": int(norm["SA_BVE_application_count"]),
            "residual_hash": r48r.formula_hash(residual),
            "residual_CLV": list(r48r.clv(residual)),
            "residual_max_width": int(r48q.max_width(residual)),
        }
        state["stage"] = "NORMALIZATION_COMPLETE"
        write_checkpoint(output, state)
    except Exception as e:
        state["stage"] = "NORMALIZATION_ERROR"
        state["error"] = repr(e)
        write_checkpoint(output, state)
        raise

    if norm["terminal"] is not None:
        state["verdict"] = "CERTIFIED_PREPROJECTION_UNSAT_TERMINAL"
        state["stage"] = "WIDTH4_CHAIN_COMPLETE"
        state["completed"] = True
        write_checkpoint(output, state)
        print(json.dumps(state, sort_keys=True), flush=True)
        return state

    try:
        width_result = r48q.run_width4_root(
            residual,
            {"family": "STANDARD_3CNF_PHP", "n_holes": n, "source_hash": source_hash},
        )
        compact = r48r.compact_width_result(width_result)
        if compact["terminal"] is not None and compact["terminal"].get("semantic_sat") is True:
            raise AssertionError(("R48R2_PHP_WIDTH_CHAIN_FALSE_SAT", n, compact["terminal"]))
        state["width4"] = compact
        state["verdict"] = (
            "WIDTH4_CHAIN_COVERED__FINITE_ONLY"
            if compact["covered"]
            else "EXPLICIT_STANDARD_PHP_WIDTH4_OBSTRUCTION_FOUND"
        )
        state["stage"] = "WIDTH4_CHAIN_COMPLETE"
        state["completed"] = True
        write_checkpoint(output, state)
    except Exception as e:
        state["stage"] = "WIDTH4_CHAIN_ERROR"
        state["error"] = repr(e)
        write_checkpoint(output, state)
        raise

    print(json.dumps({
        "gate": GATE,
        "n_holes": n,
        "stage": state["stage"],
        "verdict": state["verdict"],
        "normalization": state["normalization"],
        "width4": state["width4"],
        "firewall": state["firewall"],
    }, sort_keys=True), flush=True)
    return state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    run(a.n, a.output)


if __name__ == "__main__":
    main()
