import itertools
import json
import time
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.tools.typed_interface_basis_fixpoint.portfolio import run_portfolio


def hard_core(offset=0):
    horn = []
    for signs in itertools.product((False, True), repeat=3):
        inds = [offset + (3 + v if positive else v)
                for v, positive in enumerate(signs, start=1)]
        horn.append(tuple(-v for v in inds))
    rows = []
    for v in range(1, 4):
        x, y = offset + v, offset + 3 + v
        rows.append(((1 << (x - 1)) | (1 << (y - 1)), 1))
    return [
        {"kind": "HORN", "clauses": tuple(horn)},
        {"kind": "AFFINE", "rows": tuple(rows)},
    ]


def conflict_core(offset=0):
    x, y = offset + 1, offset + 2
    horn = ((-x, y), (x, -y))
    row = ((1 << (x - 1)) | (1 << (y - 1)), 1)
    return [{"kind": "HORN", "clauses": horn},
            {"kind": "AFFINE", "rows": (row,)}]

def count_horn_models(modules):
    horn = modules[0]["clauses"]
    variables = sorted({abs(l) for c in horn for l in c})
    total = 0
    for bits in itertools.product((False, True), repeat=len(variables)):
        a = dict(zip(variables, bits))
        ok = all(any(a[abs(l)] == (l > 0) for l in c) for c in horn)
        total += int(ok)
    return total


def scaling_ladder():
    counts = [1, 2, 4, 8, 16, 32, 64, 128]
    rows = []
    base_models = count_horn_models(hard_core())
    for k in counts:
        modules = []
        for i in range(k):
            modules.extend(hard_core(6 * i))
        t0 = time.perf_counter()
        result = run_portfolio(modules)
        elapsed_ms = round((time.perf_counter() - t0) * 1000, 3)
        terminals = {}
        for record in result["component_records"]:
            terminals[record["terminal"]] = terminals.get(record["terminal"], 0) + 1
        rows.append({
            "components": k,
            "horn_candidate_product": base_models ** k,
            "stored_component_records": result["stored_component_records"],
            "total_basis_rows": result["total_basis_rows"],
            "terminal_counts": terminals,
            "runtime_ms": elapsed_ms,
            "pass": result["stored_component_records"] == k and
                    terminals.get("OPEN_AFFINE_CONSEQUENCE_COMPLETE", 0) == k,
        })
    return rows

def controls():
    out = {}
    c = run_portfolio(conflict_core())
    out["equality_vs_disequality"] = {
        "pass": c["terminal"] == "CERTIFIED_CONFLICT",
        "terminal": c["terminal"],
    }
    h0 = run_portfolio(hard_core())
    h1 = run_portfolio(hard_core(100))
    open_ok = all(r["terminal"] == "OPEN_AFFINE_CONSEQUENCE_COMPLETE"
                  for r in h0["component_records"])
    out["multirow_obstruction_open"] = {
        "pass": h0["terminal"] == "OPEN_TYPED_FIXPOINT" and open_ok,
        "terminal": h0["terminal"],
    }
    out["alpha_renaming_invariance"] = {
        "pass": [r["terminal"] for r in h0["component_records"]] ==
                [r["terminal"] for r in h1["component_records"]],
        "base": [r["terminal"] for r in h0["component_records"]],
        "renamed": [r["terminal"] for r in h1["component_records"]],
    }
    mixed = hard_core() + conflict_core(100)
    m = run_portfolio(mixed)
    out["one_conflict_among_open"] = {
        "pass": m["terminal"] == "CERTIFIED_CONFLICT" and m["component_count"] == 2,
        "terminal": m["terminal"],
        "components": m["component_count"],
    }
    return out

def captain_obvious_guard():
    path = Path(__file__).with_name("portfolio.py")
    text = path.read_text(encoding="utf-8")
    forbidden = ["itertools.product", "all_models", "brute_sat", "dpll(", "cartesian"]
    hits = [x for x in forbidden if x in text]
    return {
        "pass": not hits,
        "hits": hits,
        "rule": "candidate must not materialize cross-products across disconnected typed cores or invoke a general SAT search",
    }


def main():
    ctl = controls()
    ladder = scaling_ladder()
    captain = captain_obvious_guard()
    ok = all(x["pass"] for x in ctl.values()) and all(x["pass"] for x in ladder) and captain["pass"]
    verdict = (
        "PASS_EXACT_TYPED_PORTFOLIO_BASIS_FIXPOINT__DISCONNECTED_OPEN_CORES_STAY_FACTORIZED__CONNECTED_MULTIROW_OPEN"
        if ok else "FALSIFIED_TYPED_INTERFACE_EXACTNESS"
    )
    result = {
        "schema": "JANUS_TRUMP_TYPED_INTERFACE_BASIS_FIXPOINT_GATE_V1",
        "verdict": verdict,
        "controls": ctl,
        "captain_obvious_guard": captain,
        "scaling_ladder": ladder,
        "interpretation": "complete Horn-to-affine basis exchange can be localized to connected typed components while disconnected OPEN cores remain factorized without Cartesian-product materialization",
        "limitation": "the connected C037.2 multirow Horn+Affine obstruction remains OPEN; portfolio factorization does not decide it",
        "next": "attack conditional multirow interaction inside one connected typed core, or discover a further exact decomposition of that core",
        "scientific_status": {"SAT_IN_P": "NOT_PROVED", "P_VS_NP": "OPEN", "Pi_negative_evidence_weight": 0},
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
