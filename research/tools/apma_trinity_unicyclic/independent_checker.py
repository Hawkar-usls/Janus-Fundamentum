from pathlib import Path
import inspect, itertools, json, subprocess, sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import research.tools.apma_trinity_unicyclic.unicyclic as candidate
import research.tools.apma_trinity_sovereign.trinity as old
from research.tools.apma_typed_module_forest.module_forest import encoding_size


def eval_cnf(source, assignment):
    return all(any(bool(assignment[abs(l)]) == (l > 0) for l in c) for c in source)


def brute(source, n):
    for bits in itertools.product((False, True), repeat=n):
        a = {i + 1: bits[i] for i in range(n)}
        if eval_cnf(source, a):
            return True, a
    return False, None


def exact_outcome(source, n, result):
    actual, _ = brute(source, n)
    d = result["sovereign"]["decision"]
    if d == "COMMIT_SAT":
        w = {int(k): bool(v) for k, v in result["sovereign"]["witness"].items()}
        return actual and eval_cnf(source, {i: w.get(i, False) for i in range(1, n + 1)})
    if d == "COMMIT_UNSAT":
        return not actual
    return False


def cycle_sources():
    slots = ((1, 3, 4), (1, 2, 5), (2, 3))
    for signs in itertools.product((-1, 1), repeat=8):
        p = 0; clauses = []
        for vs in slots:
            c = []
            for v in vs:
                c.append(signs[p] * v); p += 1
            clauses.append(tuple(c))
        yield tuple(clauses), 5


def shift_source(source, delta):
    return tuple(tuple((1 if l > 0 else -1) * (abs(l) + delta) for l in c) for c in source)


def wide_center_tree(k):
    clauses = []
    x = list(range(1, k + 1))
    y0 = k + 1
    y = list(range(y0, y0 + k + 1))
    nxt = y[-1]
    for i in range(k):
        clauses.append((-x[i], -y[i], y[i + 1]))
    for i in range(k):
        a, b = nxt + 1, nxt + 2
        nxt += 2
        clauses.append((x[i], a, b))
    return tuple(clauses), nxt


def main():
    checks = {}
    cycle_records = []
    old_open = 0; new_open = 0; new_door = 0; wrong = 0
    max_outer_ratio = 0.0; max_row_ratio = 0.0

    for source, n in cycle_sources():
        oz = old.run_trinity(source, n)
        nz = candidate.run_trinity(source, n)
        old_open += int(oz["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS")
        new_open += int(nz["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS")
        new_door += int(nz["proposal"].get("door") == candidate.UNICYCLIC)
        ok = exact_outcome(source, n, nz)
        wrong += int(not ok)
        if nz["proposal"].get("door") == candidate.UNICYCLIC:
            ev = nz["proposal"]["evidence"]
            L = encoding_size(source, n)
            sep = ev["cut_separator"]
            exe = nz.get("demiurge") or {}
            tested = int(exe.get("tested_sigma_count", 0))
            rows = int(exe.get("row_count", 0))
            M = int(ev["module_count"])
            if L:
                max_outer_ratio = max(max_outer_ratio, tested / L)
                max_row_ratio = max(max_row_ratio, rows / (M * L * L))
            if len(sep) > ev["budget"] or (2 ** len(sep)) > L or tested > L or rows > M * L * L:
                wrong += 1
        cycle_records.append({
            "source": [list(c) for c in source],
            "old_decision": oz["sovereign"]["decision"],
            "new_decision": nz["sovereign"]["decision"],
            "new_door": nz["proposal"].get("door"),
            "exact": ok,
        })

    checks["cycle_product_256_complete"] = len(cycle_records) == 256
    checks["historical_open_surface_reproduced"] = old_open == 128
    checks["successor_closes_frozen_cycle_surface"] = new_open == 0
    checks["unicyclic_door_used_on_prior_open_half"] = new_door >= old_open
    checks["cycle_product_exact_256_of_256"] = wrong == 0

    rep = ((-1, -3, -4), (-1, 2, 5), (-2, -3))
    multi = rep + shift_source(rep, 5)
    mz = candidate.run_trinity(multi, 10)
    checks["multicycle_fails_closed"] = mz["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS" and mz["proposal"].get("door") is None

    wide, wn = wide_center_tree(8)
    wz = candidate.run_trinity(wide, wn)
    checks["width_overflow_stays_open"] = wz["sovereign"]["decision"] == "OPEN_UNKNOWN_STATE_CLASS" and wz["proposal"].get("door") is None

    sat2 = ((1, 2), (-1, 2), (1, -2))
    good = candidate.akinator_propose(sat2, 2)
    tampered = dict(good); tampered["door"] = candidate.UNICYCLIC
    tz = candidate.run_trinity(sat2, 2, forced_proposal=tampered)
    checks["tampered_successor_proposal_rejected"] = tz["sovereign"]["decision"] == "ROLLBACK_CAPTAIN_REJECT"
    checks["tampered_root_preserved"] = tz["root_hash"] == tz["sovereign"]["authority_root_hash"]

    old_checker = ROOT / "research/tools/apma_trinity_sovereign/independent_checker.py"
    proc = subprocess.run([sys.executable, str(old_checker)], cwd=ROOT, text=True, capture_output=True)
    old_result = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    checks["v1_0_regression_checker_passes"] = proc.returncode == 0 and old_result.get("verdict") == "PASS_APMA_TRINITY_SOVEREIGN_FIRST_RUN__KNOWN_DOORS_SELECTED__UNKNOWN_CLASSES_FAIL_CLOSED"

    src = inspect.getsource(candidate).lower()
    forbidden = ["random.", "score_candidate", "best_candidate", "truth_label", "root_brute"]
    hits = [x for x in forbidden if x in src]
    checks["candidate_source_guard"] = not hits
    checks["symbolic_outer_bound_checked"] = max_outer_ratio <= 1.0
    checks["symbolic_row_envelope_checked"] = max_row_ratio <= 1.0

    ok = all(bool(v) for v in checks.values())
    verdict = "PASS_SCOPED_BOUNDED_INTERFACE_UNICYCLIC_TRANSFER" if ok else "FAIL_UNICYCLIC_SUCCESSOR_GATE"
    out = {
        "artifact": "JANUS-TRUMP-APMA-TRINITY-UNICYCLIC-TRANSFER-GATE-2026-09-15-v1.0",
        "verdict": verdict,
        "checks": checks,
        "cycle_product": {
            "count": len(cycle_records),
            "historical_open": old_open,
            "successor_open": new_open,
            "unicyclic_door_uses": new_door,
            "wrong": wrong,
        },
        "negative_controls": {
            "multicycle_decision": mz["sovereign"]["decision"],
            "multicycle_evidence": mz["proposal"].get("evidence"),
            "width_decision": wz["sovereign"]["decision"],
            "width_evidence": wz["proposal"].get("evidence"),
        },
        "complexity_checks": {
            "max_tested_sigma_over_L": max_outer_ratio,
            "max_rows_over_M_L2": max_row_ratio,
            "symbolic_claim": "outer <= L; rows <= M*L^2; native module solves are polynomial for frozen typed carriers"
        },
        "source_guard_hits": hits,
        "scientific_firewall": {
            "scope": "BOUNDED_INTERFACE_CONNECTED_UNICYCLIC_TYPED_MODULE_INTERACTION_ONLY",
            "UNIVERSAL_DISCOVERY": "NOT_CLAIMED",
            "SAT_IN_P": "NOT_PROVED",
            "P_VS_NP": "OPEN",
            "scientific_promotion": "NONE_BEYOND_SCOPED_GATE"
        }
    }
    print(json.dumps(out, sort_keys=True))
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
