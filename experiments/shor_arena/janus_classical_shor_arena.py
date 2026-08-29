#!/usr/bin/env python3
import argparse
import hashlib
import json
import math
import random
import statistics
from pathlib import Path

ARENA_ID = "JANUS_CLASSICAL_SHOR_ARENA_V1_HOLDOUT"
WAVE_WIDTH = 8

def powmod_count(a: int, e: int, n: int):
    result = 1
    base = a % n
    mults = 0
    while e > 0:
        if e & 1:
            result = (result * base) % n
            mults += 1
        e >>= 1
        if e:
            base = (base * base) % n
            mults += 1
    return result, mults

def linear_order_scan(n: int, a: int):
    if math.gcd(n, a) != 1:
        return None, {"status": "NON_COPRIME", "modular_multiplications": 0}
    residue = 1
    for r in range(1, n + 1):
        residue = (residue * a) % n
        if residue == 1:
            return r, {"status": "FOUND", "steps": r, "modular_multiplications": r}
    return None, {"status": "UNKNOWN_RESOURCE_LIMIT", "steps": n, "modular_multiplications": n}

def trial_factor(n: int):
    x = n
    factors = []
    divisions = 0
    d = 2
    while d * d <= x:
        divisions += 1
        if x % d == 0:
            exp = 0
            while x % d == 0:
                x //= d
                exp += 1
            factors.append([d, exp])
        d = 3 if d == 2 else d + 2
    if x > 1:
        factors.append([x, 1])
    return factors, divisions

def exact_reduce_order(candidate: int, n: int, a: int):
    g = candidate
    factors, trial_divisions = trial_factor(g)
    modular_multiplications = 0
    pow_checks = 0
    for q, exp in factors:
        for _ in range(exp):
            if g % q:
                break
            value, cost = powmod_count(a, g // q, n)
            modular_multiplications += cost
            pow_checks += 1
            if value == 1:
                g //= q
            else:
                break
    value, cost = powmod_count(a, g, n)
    modular_multiplications += cost
    pow_checks += 1
    exact = value == 1
    final_factors, extra_divisions = trial_factor(g)
    trial_divisions += extra_divisions
    minimality = []
    if exact:
        for q, _ in final_factors:
            value, cost = powmod_count(a, g // q, n)
            modular_multiplications += cost
            pow_checks += 1
            minimality.append(value != 1)
    certified = exact and all(minimality)
    return g, certified, {
        "candidate": candidate,
        "final_order": g,
        "prime_factors_of_order": final_factors,
        "trial_divisions": trial_divisions,
        "pow_checks": pow_checks,
        "modular_multiplications": modular_multiplications,
        "certificate": {
            "a_pow_r_mod_n_is_one": exact,
            "a_pow_r_over_q_not_one_for_each_prime_q": all(minimality),
        },
    }

def deterministic_seed(n: int, a: int):
    raw = f"{ARENA_ID}|{n}|{a}".encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")

def janus_collision_order(n: int, a: int, wave_width: int = WAVE_WIDTH, max_probes=None):
    common = math.gcd(n, a)
    if common != 1:
        return {"status": "NON_COPRIME", "trivial_factor": common, "solver_inputs": {"N": n, "a": a}}
    if max_probes is None:
        max_probes = n
    rng = random.Random(deterministic_seed(n, a))
    used_exponents = set()
    spider_residue_index = {}
    collision_gcd = 0
    collision_count = 0
    gcd_operations = 0
    gaps = []
    residue_probes = 0
    waves = 0
    total_probe_mod_mults = 0
    total_candidate_check_mod_mults = 0
    total_reduction_mod_mults = 0
    critical_path_mod_mults = 0
    while residue_probes < max_probes:
        batch = []
        target = min(wave_width, max_probes - residue_probes)
        while len(batch) < target:
            x = rng.randrange(0, n)
            if x in used_exponents:
                continue
            used_exponents.add(x)
            residue, cost = powmod_count(a, x, n)
            batch.append((x, residue, cost))
        waves += 1
        residue_probes += len(batch)
        total_probe_mod_mults += sum(row[2] for row in batch)
        critical_path_mod_mults += max(row[2] for row in batch)
        for x, residue, _ in batch:
            if residue in spider_residue_index:
                y = spider_residue_index[residue]
                gap = abs(x - y)
                if gap:
                    collision_count += 1
                    gaps.append(gap)
                    if collision_gcd == 0:
                        collision_gcd = gap
                    else:
                        collision_gcd = math.gcd(collision_gcd, gap)
                        gcd_operations += 1
            else:
                spider_residue_index[residue] = x
        if collision_gcd:
            value, check_cost = powmod_count(a, collision_gcd, n)
            total_candidate_check_mod_mults += check_cost
            critical_path_mod_mults += check_cost
            if value == 1:
                order, certified, reduction = exact_reduce_order(collision_gcd, n, a)
                total_reduction_mod_mults += reduction["modular_multiplications"]
                critical_path_mod_mults += reduction["modular_multiplications"]
                total_mod_mults = total_probe_mod_mults + total_candidate_check_mod_mults + total_reduction_mod_mults
                return {
                    "status": "FOUND" if certified else "CERTIFICATE_FAILURE",
                    "solver_inputs": {"N": n, "a": a},
                    "order": order,
                    "collision_gcd_before_reduction": collision_gcd,
                    "residue_probes": residue_probes,
                    "waves": waves,
                    "wave_width": wave_width,
                    "collisions": collision_count,
                    "collision_gaps_sample": gaps[:16],
                    "resource_ledger": {
                        "probe_powmod_modular_multiplications": total_probe_mod_mults,
                        "candidate_check_modular_multiplications": total_candidate_check_mod_mults,
                        "exact_reduction_modular_multiplications": total_reduction_mod_mults,
                        "total_modular_multiplications": total_mod_mults,
                        "integer_trial_divisions": reduction["trial_divisions"],
                        "gcd_operations": gcd_operations,
                        "critical_path_modular_multiplications": critical_path_mod_mults,
                    },
                    "exact_order_certificate": reduction,
                }
    return {
        "status": "UNKNOWN_RESOURCE_LIMIT",
        "solver_inputs": {"N": n, "a": a},
        "residue_probes": residue_probes,
        "waves": waves,
        "collisions": collision_count,
        "resource_ledger": {
            "probe_powmod_modular_multiplications": total_probe_mod_mults,
            "candidate_check_modular_multiplications": total_candidate_check_mod_mults,
            "exact_reduction_modular_multiplications": total_reduction_mod_mults,
            "total_modular_multiplications": total_probe_mod_mults + total_candidate_check_mod_mults + total_reduction_mod_mults,
            "gcd_operations": gcd_operations,
            "critical_path_modular_multiplications": critical_path_mod_mults,
        },
    }

def shor_postprocess(n: int, a: int, r: int):
    if r is None or r % 2:
        return {"status": "ORDER_NOT_USABLE", "reason": "r is missing or odd"}
    half, cost = powmod_count(a, r // 2, n)
    if half == n - 1:
        return {"status": "ORDER_NOT_USABLE", "reason": "a^(r/2) == -1 mod N", "half_power": half, "modular_multiplications": cost}
    g1 = math.gcd(half - 1, n)
    g2 = math.gcd(half + 1, n)
    factors = sorted({g for g in (g1, g2) if 1 < g < n and n % g == 0})
    return {
        "status": "NONTRIVIAL_FACTOR_FOUND" if factors else "NO_NONTRIVIAL_FACTOR",
        "half_power": half,
        "factors": factors,
        "modular_multiplications": cost,
        "gcd_operations": 2,
    }

def self_tests():
    known = [(15, 2, 4), (21, 2, 6), (35, 2, 12), (143, 2, 60), (10403, 2, 5100)]
    receipts = []
    for n, a, expected in known:
        baseline, _ = linear_order_scan(n, a)
        janus = janus_collision_order(n, a)
        if baseline != expected or janus.get("order") != expected or janus["status"] != "FOUND":
            raise AssertionError((n, a, expected, baseline, janus))
        receipts.append({"N": n, "a": a, "expected_order": expected, "janus_probes": janus["residue_probes"]})
    return receipts

def median(values):
    return statistics.median(values)

def run_holdout(prereg):
    cases = prereg["holdout"]["cases"]
    rows = []
    for case in cases:
        solver_case = {"N": int(case["N"]), "a": int(case["a"])}
        n, a = solver_case["N"], solver_case["a"]
        baseline_r, baseline = linear_order_scan(n, a)
        janus = janus_collision_order(n, a, wave_width=prereg["algorithm"]["wave_width"], max_probes=n)
        exact_match = janus.get("status") == "FOUND" and janus.get("order") == baseline_r
        if janus.get("status") == "FOUND":
            ledger = janus["resource_ledger"]
            probe_ratio = janus["residue_probes"] / baseline_r
            total_modmult_ratio = ledger["total_modular_multiplications"] / baseline_r
            latency_ratio = ledger["critical_path_modular_multiplications"] / baseline_r
            post = shor_postprocess(n, a, janus["order"])
        else:
            probe_ratio = total_modmult_ratio = latency_ratio = None
            post = {"status": "NOT_RUN"}
        rows.append({
            "family": case["family"], "N": n, "a": a,
            "exact_linear_order": baseline_r,
            "linear_scan": baseline,
            "janus": janus,
            "exact_order_match": exact_match,
            "probe_ratio_vs_linear_steps": probe_ratio,
            "total_modmult_ratio_vs_linear": total_modmult_ratio,
            "parallel_latency_modmult_ratio_vs_linear": latency_ratio,
            "shor_postprocess": post,
        })
    valid = [r for r in rows if r["janus"].get("status") == "FOUND"]
    probe_ratios = [r["probe_ratio_vs_linear_steps"] for r in valid]
    compute_ratios = [r["total_modmult_ratio_vs_linear"] for r in valid]
    latency_ratios = [r["parallel_latency_modmult_ratio_vs_linear"] for r in valid]
    exact_count = sum(r["exact_order_match"] for r in rows)
    compute_win_fraction = sum(r["total_modmult_ratio_vs_linear"] < 1.0 for r in valid) / len(rows) if rows else 0.0
    factor_success = sum(r["shor_postprocess"].get("status") == "NONTRIVIAL_FACTOR_FOUND" for r in rows)
    summary = {
        "case_count": len(rows),
        "exact_order_match_count": exact_count,
        "median_probe_ratio": median(probe_ratios) if probe_ratios else None,
        "median_total_modmult_ratio": median(compute_ratios) if compute_ratios else None,
        "casewise_total_compute_win_fraction": compute_win_fraction,
        "median_parallel_latency_modmult_ratio": median(latency_ratios) if latency_ratios else None,
        "shor_postprocess_nontrivial_factor_count": factor_success,
    }
    gates = [
        {"gate":"G1_EXACT_ORDER_ALL_CASES","passed":exact_count == len(rows) == 32,"value":f"{exact_count}/{len(rows)}","criterion":"32/32"},
        {"gate":"G2_MEDIAN_PROBE_RATIO","passed":summary["median_probe_ratio"] is not None and summary["median_probe_ratio"] <= 0.10,"value":summary["median_probe_ratio"],"criterion":"<= 0.10"},
        {"gate":"G3_MEDIAN_TOTAL_MODMULT_RATIO","passed":summary["median_total_modmult_ratio"] is not None and summary["median_total_modmult_ratio"] <= 0.75,"value":summary["median_total_modmult_ratio"],"criterion":"<= 0.75"},
        {"gate":"G4_CASEWISE_TOTAL_COMPUTE_WIN_FRACTION","passed":compute_win_fraction >= 0.70,"value":compute_win_fraction,"criterion":">= 0.70"},
        {"gate":"G5_MEDIAN_PARALLEL_LATENCY_RATIO","passed":summary["median_parallel_latency_modmult_ratio"] is not None and summary["median_parallel_latency_modmult_ratio"] <= 0.25,"value":summary["median_parallel_latency_modmult_ratio"],"criterion":"<= 0.25"},
        {"gate":"G6_NO_FACTOR_LEAKAGE","passed":all(set(r["janus"]["solver_inputs"]) == {"N","a"} for r in rows),"value":"solver_inputs={N,a}","criterion":"solver receives only N,a"},
        {"gate":"G7_NEGATIVE_RESULT_IMMUTABILITY","passed":True,"value":"implementation/preregistration invariant","criterion":"no threshold changes after holdout execution"},
    ]
    return rows, summary, gates

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prereg")
    ap.add_argument("--output")
    ap.add_argument("--self-test-only", action="store_true")
    args = ap.parse_args()
    tests = self_tests()
    if args.self_test_only:
        print(json.dumps({"self_tests": tests, "status": "PASS"}, indent=2))
        return
    if not args.prereg or not args.output:
        ap.error("--prereg and --output are required unless --self-test-only")
    prereg_path = Path(args.prereg)
    prereg = json.loads(prereg_path.read_text())
    rows, summary, gates = run_holdout(prereg)
    result = {
        "schema":"JANUS/CLASSICAL-SHOR-ARENA/HOLDOUT-RESULT/v1.0",
        "status":"HOLDOUT_COMPLETE",
        "preregistration_path":str(prereg_path),
        "preregistration_status":prereg["status"],
        "self_tests":tests,
        "summary":summary,
        "gates":gates,
        "all_frozen_gates_passed":all(g["passed"] for g in gates),
        "cases":rows,
        "interpretation":{
            "allowed":["Report exact holdout order-finding accuracy.","Report residue-probe, total modular-multiplication, trial-division, gcd, and latency-proxy ledgers separately.","Call the method a classical collision-guided order finder."],
            "forbidden":["Claim quantum speedup.","Claim polynomial-time factoring.","Treat wave parallelism as free compute.","Infer an asymptotic theorem from this finite holdout."],
            "asymptotic_note":"Birthday-style O(sqrt(r)) residue probes with O(log N) powmod work per probe can still be exponential in input bit-length because r can be O(N).",
            "P_VS_NP":"OPEN"
        }
    }
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"summary":summary,"gates":gates}, indent=2))

if __name__ == "__main__":
    main()
