#!/usr/bin/env python3
"""JANUS E12C5 - preregistered narrow class profit experiment, never production.

All original CNF clauses are reconstructed per cold child and verified. The GF2
path may solve ONLY an exact, exclusive, complete XOR cover; no partial masks.
Thresholds, three fresh seeds, a known UNSAT guard and controls were committed
in E12C5_PREREG.json BEFORE this script or any E12C5 benchmark.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import itertools
import json
from pathlib import Path
import platform
import random
import resource
import subprocess
import sys
from statistics import median
from time import perf_counter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from janus_time_sat_004d1_xor import (
    group_parity_equations, solve_if_exact_xor, check_original_cnf,
    independently_replay_unsat_combination,
)

PREREG = ROOT / "experiments/time_sat_004_external/E12C5_PREREG.json"
ARMS = ("janus_gf2", "cryptominisat_native_xor",
        "cryptominisat_original_cnf", "cadical195_original_cnf")
CPU = 8
WALL = 12
AS = 2_147_483_648
ORDER_SEED = 202611031205
OUTCOME_SAT = "SAT_ORIGINAL_ALL_CLAUSES_VERIFIED"
OUTCOME_UNSAT = "UNSAT_SOURCE_GF2_COMBINATION_REPLAY_SAME_ADMIN"
OUTCOME_UNSAT_SOLVER = "UNSAT_SOLVER_ONLY_NO_PORTABLE_CERTIFICATE"
CASE_SPEC = (
    ("new_grid_19", 19, 202611030519),
    ("new_grid_25", 25, 202611030525),
    ("new_grid_37", 37, 202611030537),
)
UNSAT_ID = "old_unsat_guard"
UNSAT_FILE = ROOT / "experiments/time_sat_004_external/time_sat_004d3_evidence/lightsout-2.original.cnf"
UNSAT_SHA = "84729f80119b50efac42d9477438abbc58c8712654ffe1fcdf9f324e44ae165d"

def canonical(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()

def original_sha(rows, n):
    return sha256(canonical({"n": n, "rows": rows})).hexdigest()

def cnf_ok(rows, model):
    vals = {abs(v): v > 0 for v in model}
    return all(any(vals.get(abs(lit)) == (lit > 0) for lit in row) for row in rows)

def generate_grid(side, seed):
    if side not in (19, 25, 37) or type(seed) is not int:
        raise AssertionError("unregistered Lights-out size or seed")
    rng = random.Random(seed)
    n = side * side
    planted = [False] + [bool(rng.getrandbits(1)) for _ in range(n)]
    rows = []
    for r in range(side):
        for c in range(side):
            neighbors = [(r, c), (r - 1, c), (r + 1, c),
                         (r, c - 1), (r, c + 1)]
            support = sorted(1 + i * side + j for i, j in neighbors
                             if 0 <= i < side and 0 <= j < side)
            rhs = sum(planted[v] for v in support) % 2
            for mask in itertools.product((0, 1), repeat=len(support)):
                if sum(mask) % 2 != rhs:
                    rows.append([v if bit == 0 else -v
                                 for v, bit in zip(support, mask)])
    planted_model = [v if planted[v] else -v for v in range(1, n + 1)]
    if not cnf_ok(rows, planted_model):
        raise AssertionError("new CNF does not admit planted SAT model")
    return n, rows, "SAT"

def read_old_unsat():
    data = UNSAT_FILE.read_bytes()
    if sha256(data).hexdigest() != UNSAT_SHA:
        raise AssertionError("old UNSAT original CNF byte SHA drift")
    n = m = None
    rows = []
    for line in data.decode("ascii").splitlines():
        line = line.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            if n is not None:
                raise AssertionError("duplicate DIMACS header")
            header = line.split()
            if len(header) != 4 or header[:2] != ["p", "cnf"]:
                raise AssertionError("bad DIMACS header")
            n, m = int(header[2]), int(header[3])
            continue
        vals = [int(v) for v in line.split()]
        if n is None or not vals or vals[-1] != 0 or 0 in vals[:-1] or (
                any(abs(v) > n for v in vals[:-1])):
            raise AssertionError("invalid original DIMACS clause")
        rows.append(vals[:-1])
    if (n, m, len(rows)) != (529, 7744, 7744):
        raise AssertionError("pinned original UNSAT source dimensions drift")
    return n, rows, "UNSAT"

def source(case):
    for name, side, seed in CASE_SPEC:
        if name == case:
            return generate_grid(side, seed)
    if case == UNSAT_ID:
        return read_old_unsat()
    raise AssertionError("unregistered benchmark case")

def load_prereg():
    j = json.loads(PREREG.read_text())
    if (j["schema"] != "JANUS-TIME-SAT-004E12C5-PREREG-V1"
        or [x["id"] for x in j["cases"]]
        != [x[0] for x in CASE_SPEC] + [UNSAT_ID]
        or j["arms"] != list(ARMS)
        or [x["seed"] for x in j["cases"][:3]]
        != [x[2] for x in CASE_SPEC]
        or j["repeats_per_SAT_case_and_arm_and_host"] != 3
        or j["repeats_per_UNSAT_control_arm_and_host"] != 1
        or j["order_randomization_seed"] != ORDER_SEED
        or j["limits"]["child_cpu_seconds"] != CPU
        or j["limits"]["child_wall_seconds"] != WALL
        or j["limits"]["child_AS_bytes"] != AS):
        raise AssertionError("unregistered protocol drift")
    return j

def cms_assignment(values, n):
    if not isinstance(values, (tuple, list)) or not values or (
            values[0] is not None) or len(values) > n + 1:
        raise AssertionError("malformed CryptoMiniSat model")
    signed = []
    for var in range(1, n + 1):
        a = values[var] if var < len(values) else None
        if a is not None and type(a) is not bool:
            raise AssertionError("nonboolean CryptoMiniSat assignment")
        signed.append(var if a else -var)
    return signed

def child(case, arm, expected_source_sha):
    resource.setrlimit(resource.RLIMIT_AS, (AS, AS))
    resource.setrlimit(resource.RLIMIT_CPU, (CPU, CPU + 1))
    start = perf_counter()
    n, rows, expected = source(case)
    digest = original_sha(rows, n)
    if digest != expected_source_sha:
        raise AssertionError("SHA-linked original CNF drift")
    extracted = None
    model = None
    verdict = None
    if arm == "janus_gf2":
        solved = solve_if_exact_xor(rows, n)
        extracted = solved.get("equation_count")
        if solved["coverage_status"] != "EXACT_XOR_COVER_PASS":
            raise AssertionError("GF2 used without exact original XOR cover")
        if solved["verdict"] == "SAT_ORIGINAL_MODEL_VERIFIED":
            model = list(solved["model"])
        elif solved["verdict"] == "GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY":
            cover = group_parity_equations(rows, n)
            if not independently_replay_unsat_combination(
                    rows, n, solved["xor_contradiction_equation_indices"]):
                raise AssertionError("invalid source replay GF2 UNSAT")
            verdict = OUTCOME_UNSAT
        else:
            raise AssertionError("unverified exact GF2 output")
    elif arm.startswith("cryptominisat"):
        import pycryptosat
        solver = pycryptosat.Solver(threads=1)
        if arm == "cryptominisat_native_xor":
            cover = group_parity_equations(rows, n)
            if cover["status"] != "EXACT_XOR_COVER_PASS":
                raise AssertionError("invalid native XOR cover")
            extracted = len(cover["equations"])
            for eq in cover["equations"]:
                solver.add_xor_clause(list(eq["variables"]), bool(eq["rhs"]))
        else:
            for clause in rows:
                solver.add_clause(clause)
        sat, raw_model = solver.solve()
        if sat is True:
            model = cms_assignment(raw_model, n)
        elif sat is False:
            verdict = OUTCOME_UNSAT_SOLVER
        else:
            verdict = "UNKNOWN_SOLVER"
    elif arm == "cadical195_original_cnf":
        from pysat.solvers import Solver
        with Solver(name="cadical195", bootstrap_with=rows) as solver:
            sat = solver.solve()
            if sat is True:
                model = solver.get_model()
            elif sat is False:
                verdict = OUTCOME_UNSAT_SOLVER
            else:
                verdict = "UNKNOWN_SOLVER"
    else:
        raise AssertionError("unregistered child arm")
    if model is not None:
        if not cnf_ok(rows, model):
            raise AssertionError("SAT model violates original CNF")
        verdict = OUTCOME_SAT
    if expected == "SAT" and verdict != OUTCOME_SAT:
        raise AssertionError("SAT planted source was not independently verified")
    if expected == "UNSAT" and verdict not in (OUTCOME_UNSAT, OUTCOME_UNSAT_SOLVER):
        raise AssertionError("UNSAT source contradiction/control disagreement")
    result = {
        "schema": "JANUS-E12C5-COLD-CHILD-V1", "case": case, "arm": arm,
        "n": n, "m": len(rows), "source_sha256": digest,
        "expected_construction": expected,
        "verdict": verdict, "full_inner_wall_s": perf_counter()-start,
        "gf2_equations": extracted,
        "cpu_limit_s": CPU, "RAM_limit_bytes": AS,
        "peak_RSS_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "original_clause_replay": model is not None,
        "UNSAT_external_proof": False,
    }
    print(json.dumps(result, sort_keys=True), flush=True)

def self_test():
    p = load_prereg()
    sha_list = []
    for case in p["cases"]:
        n, rows, status = source(case["id"])
        cover = group_parity_equations(rows, n)
        if cover["status"] != "EXACT_XOR_COVER_PASS":
            raise AssertionError(case["id"] + ": not proven exact XOR")
        if len(cover["equations"]) != n:
            raise AssertionError("incorrect parity equation count")
        g = solve_if_exact_xor(rows, n)
        if status == "SAT" and g["verdict"] != "SAT_ORIGINAL_MODEL_VERIFIED":
            raise AssertionError("new source not SAT-verified")
        if status == "UNSAT" and g["verdict"] != "GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY":
            raise AssertionError("guard not replay-UNSAT")
        if status == "SAT":
            mutilated = rows[:-1]
            if group_parity_equations(mutilated, n)["status"] == "EXACT_XOR_COVER_PASS":
                raise AssertionError("tampered incomplete parity block mistakenly accepted")
        sha_list.append(original_sha(rows, n))
    if len(set(sha_list)) != len(sha_list):
        raise AssertionError("duplicate generated source SHA")
    print("E12C5_SOURCE_PROOF_PASS", json.dumps(
        {x["id"]: v for x,v in zip(p["cases"],sha_list)},sort_keys=True))

def benchmark(out):
    p = load_prereg()
    self_test()
    out.mkdir(parents=True, exist_ok=True)
    records = []
    sources = {}
    for i, case in enumerate(p["cases"]):
        case_id = case["id"]
        n,rows,expected = source(case_id)
        key = original_sha(rows,n)
        sources[case_id] = {"sha256":key,"n":n,"m":len(rows),
                            "expected":expected,
                            "known_prior_seen":case_id==UNSAT_ID}
        times = 1 if case_id==UNSAT_ID else 3
        for repeat in range(times):
            arms = list(ARMS)
            random.Random(ORDER_SEED+100*i+repeat).shuffle(arms)
            for slot, arm in enumerate(arms):
                cmd = [sys.executable, str(Path(__file__).resolve()),
                    "--child","--case",case_id,"--arm",arm,"--source-sha",key]
                started=perf_counter()
                try:
                    result = subprocess.run(cmd, text=True, capture_output=True,
                                            timeout=WALL, check=False)
                    if result.returncode == 0:
                        value=json.loads(result.stdout)
                        if (value.get("source_sha256")!=key or
                           value.get("arm")!=arm or value.get("case")!=case_id):
                            raise AssertionError("child receipt identity mismatch")
                    else:
                        value={"verdict":"ERROR_CHILD",
                               "return_code":result.returncode,
                               "stderr_tail":result.stderr[-1700:]}
                except subprocess.TimeoutExpired:
                    value={"verdict":"UNKNOWN_WALL_LIMIT"}
                elapsed=perf_counter()-started
                records.append({"case":case_id,"repeat":repeat,
                    "arm":arm,"order_slot":slot,
                    "full_end_to_end_wall_s":elapsed,"result":value})
                print("E12C5_COLD",case_id,repeat,arm,
                      value["verdict"],round(elapsed,4),flush=True)
    if len(records) != 40:
        raise AssertionError("wrong preregistered 3*3*4+1*4 control count")
    bycase = {}
    for case_id in sources:
        case_records=[r for r in records if r["case"]==case_id]
        complete={}
        for arm in ARMS:
            subset=[r for r in case_records if r["arm"]==arm]
            fully=(len(subset)==(1 if case_id==UNSAT_ID else 3)
                   and all(r["result"]["verdict"]==OUTCOME_SAT for r in subset))
            complete[arm]={"status":"SAT_VERIFIED" if fully else "CENSORED_OR_NEGATIVE_CONTROL",
                          "median_wall_s":median(r["full_end_to_end_wall_s"] for r in subset) if fully else None,
                          "all_outcomes":[r["result"]["verdict"] for r in subset]}
        candidate = complete[ARMS[0]]
        baselines=[complete[arm] for arm in ARMS[1:]]
        if candidate["status"]=="SAT_VERIFIED" and all(b["status"]=="SAT_VERIFIED" for b in baselines):
            ratio=min(b["median_wall_s"] for b in baselines)/candidate["median_wall_s"]
            result="MEETS_1_20_SINGLE_HOST" if ratio>=1.2 else "DOES_NOT_MEET_1_20"
        else:
            ratio=None
            result="NEGATIVE_UNSAT_CONTROL" if case_id==UNSAT_ID else "INDETERMINATE_CENSORED"
        bycase[case_id]={"arms":complete,"strict_ratio":ratio,"single_host_verdict":result}
    sha_src=sha256(Path(__file__).read_bytes()).hexdigest()
    report={"schema":"JANUS-E12C5-PREREGISTERED-RESULTS-V1",
        "pre_registration_sha256":sha256(PREREG.read_bytes()).hexdigest(),
        "pre_registration_status":p["status"],"script_sha256":sha_src,
        "host":platform.platform(),"python":sys.version,
        "cores_only_free_Github_runner":True,
        "source_manifest":sources,"results":records,"summary":bycase,
        "claim":"development narrow family only; cross-host synthesis and sealed outside witness still required",
        "E12C4_and_production_C023":"UNCHANGED",
        "no_source_replacement":True,"no_holdout_timed":True,
        "confidence_intervals":"NOT_ESTABLISHED_THREE_REPEATS_SINGLE_HOST"}
    (out/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("E12C5_COMPLETE",json.dumps({c:x["single_host_verdict"] for c,x in bycase.items()},sort_keys=True))

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--child",action="store_true")
    a.add_argument("--self-test",action="store_true")
    a.add_argument("--out",type=Path)
    a.add_argument("--case",choices=[x[0] for x in CASE_SPEC]+[UNSAT_ID])
    a.add_argument("--arm",choices=ARMS)
    a.add_argument("--source-sha")
    z=a.parse_args()
    if z.self_test:
        self_test()
    elif z.child:
        if not (z.case and z.arm and z.source_sha):
            a.error("child requires case, arm and source-sha")
        child(z.case,z.arm,z.source_sha)
    else:
        if not z.out:
            a.error("--out required")
        benchmark(z.out)
