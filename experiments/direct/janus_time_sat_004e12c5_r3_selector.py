#!/usr/bin/env python3
"""E12C5 R3: R1+R2 calibrated structural parity hypothesis, strict pre-solve.

Pre-solve policy is frozen from R1+R2 only. DEV research, NOT C023.
Never use R2 test labels or timings to choose its own routing algorithm.
"""
from __future__ import annotations
import argparse
from hashlib import sha1, sha256
import itertools
from math import isqrt
import janus_time_sat_004d1_xor as xor_core
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
import janus_time_sat_004e12c5_profit_test as r1
from janus_time_sat_004d1_xor import (_gauss_with_linear_combination,
    independently_replay_unsat_combination, check_original_cnf)

PREREG = ROOT / "experiments/time_sat_004_external/E12C5_R3_PREREG.json"
R2_EVIDENCE = ROOT / "experiments/time_sat_004_external/E12C5_R2_POSTRUN_REPORT.json"
FROZEN_R2_EVIDENCE_BLOB_SHA1 = "41109aed354e5f627f7c5834adc4705fb5b878ac"
R1_EVIDENCE = ROOT / "experiments/time_sat_004_external/E12C5_R1_POSTRUN_REPORT.json"
FROZEN_R1_EVIDENCE_BLOB_SHA1 = "3457551135c85f45564cd9125d363aefc8de83f8"
FROZEN_PROTOCOL_BLOB_SHA1 = "5e72bb67a201112b03c1f1ef317b9de0f1e61581"
ARMS = ("janus_pre_solve_selector", "janus_gf2",
        "cryptominisat_native_xor", "cryptominisat_original_cnf",
        "cadical195_original_cnf")
CASES = (("r3_grid_17", 17, 202611030817),
         ("r3_grid_27", 27, 202611030827),
         ("r3_grid_33", 33, 202611030833),
         ("r3_grid_35", 35, 202611030835),
         ("r3_grid_41a", 41, 202611030841),
         ("r3_grid_41b", 41, 202611040841))
ORDER_SEED = 202611031322
THRESHOLD_N = 400
xor_core.MAX_LITERALS = 140000  # bounded R3 research-only widened exact proof cap
CPU_LIMIT = 8
WALL_LIMIT = 12
MEM_LIMIT = 2_147_483_648
SAT = "SAT_VERIFIED_ORIGINAL_CNF"
UNSAT = "UNSAT_SAME_ADMIN_GF2_REPLAY_ONLY"

def protocol():
    raw = PREREG.read_bytes()
    git_blob = sha1(b"blob " + str(len(raw)).encode() + bytes([0]) + raw).hexdigest()
    if git_blob != FROZEN_PROTOCOL_BLOB_SHA1:
        raise AssertionError("R3 FROZEN PREREG BLOB CHANGED")
    r1raw = R1_EVIDENCE.read_bytes()
    r1blob = sha1(b"blob " + str(len(r1raw)).encode() + bytes([0]) + r1raw).hexdigest()
    if r1blob != FROZEN_R1_EVIDENCE_BLOB_SHA1:
        raise AssertionError("R3 R1 TRAINING EVIDENCE MUTATED")
    r1data = json.loads(r1raw)
    if (r1data["original_gate"]["verdict"] != "NOT_PASSED"
        or len(r1data["posthoc_rounded_median_seconds"]) != 12
        or set(r1data["source_sha256"]) != {
            "new_grid_19", "new_grid_25", "new_grid_37", "old_unsat_guard"}):
        raise AssertionError("R3 R1 EVIDENCE NOT THE REGISTERED TRAINING SET")
    r2raw = R2_EVIDENCE.read_bytes()
    r2blob = sha1(b"blob " + str(len(r2raw)).encode() + bytes([0]) + r2raw).hexdigest()
    if r2blob != FROZEN_R2_EVIDENCE_BLOB_SHA1:
        raise AssertionError("R3 R2 TRAINING EVIDENCE MUTATED")
    r2data = json.loads(r2raw)
    if (r2data["scientific_status"] != "FROZEN_R2_SELECTOR_GATE_NOT_PASSED"
        or len(r2data["median_seconds_rounded"]) != 4):
        raise AssertionError("R3 R2 TRAINING COHORT DRIFT")
    p = json.loads(raw)
    if (p.get("schema") != "JANUS-E12C5-R3-STRUCTURAL-MOD4-PREREG-V1"
        or [(x["id"], x["side"], x["seed"]) for x in p["new_unseen_cases"]] != list(CASES)
        or p["benchmark"]["trial_arms"] != list(ARMS)
        or p["benchmark"]["order_random_seed"] != ORDER_SEED
        or p["benchmark"]["limits"]["child_cpu_s"] != CPU_LIMIT
        or p["benchmark"]["limits"]["child_wall_s"] != WALL_LIMIT
        or p["benchmark"]["limits"]["memory_bytes"] != MEM_LIMIT
        or p["pre_solve_selector"]["max_literal_scan_research_only"] != xor_core.MAX_LITERALS):
        raise AssertionError("R3 FROZEN SCIENTIFIC PROTOCOL DRIFT")
    return p, sha256(raw).hexdigest()

def grid(side, seed):
    if (side, seed) not in {(c[1], c[2]) for c in CASES} and (
        side, seed) not in {(19, 202611030519), (25, 202611030525), (37, 202611030537)}:
        raise AssertionError("unregistered R3/R1 test source")
    rng = random.Random(seed)
    n = side * side
    planted = [False] + [bool(rng.getrandbits(1)) for _ in range(n)]
    rows = []
    for y in range(side):
        for x in range(side):
            neighbors = ((y, x), (y-1, x), (y+1, x),
                         (y, x-1), (y, x+1))
            support = sorted(1 + yy*side+xx for yy, xx in neighbors
                             if 0 <= yy < side and 0 <= xx < side)
            rhs = sum(planted[v] for v in support) & 1
            for mask in itertools.product((0, 1), repeat=len(support)):
                if sum(mask) % 2 != rhs:
                    rows.append([v if bit == 0 else -v
                                 for v, bit in zip(support, mask)])
    witness = [i if planted[i] else -i for i in range(1,n+1)]
    if not r1.cnf_ok(rows, witness):
        raise AssertionError("invalid SOURCE by construction")
    return n, rows

def source(case):
    for name, side, seed in CASES:
        if case == name:
            return grid(side, seed)
    raise AssertionError("R3 unknown source")

def verified_lightsout_supports(cover, n, side):
    """Input-only topological proof; never assume a grid merely from n being square."""
    if side * side != n or cover.get("status") != "EXACT_XOR_COVER_PASS":
        return False
    actual = [tuple(eq["variables"]) for eq in cover["equations"]]
    expected = []
    for y in range(side):
        for x in range(side):
            positions = ((y,x),(y-1,x),(y+1,x),(y,x-1),(y,x+1))
            expected.append(tuple(sorted(1+yy*side+xx for yy,xx in positions
                                         if 0<=yy<side and 0<=xx<side)))
    return (len(actual)==n and len(set(actual))==n
            and set(actual)==set(expected))


def choose_pre_solver(rows, n):
    """Strict input-only grid topology and R1+R2 mod4 class; no solver/probe."""
    if n < THRESHOLD_N:
        return "cadical195_original_cnf", None, "SMALL_ORIGINAL_RAW"
    cover = r1.group_parity_equations(rows, n)
    if cover["status"] != "EXACT_XOR_COVER_PASS":
        return "cryptominisat_original_cnf", None, "NO_COMPLETE_XOR_CERTIFICATE"
    side = isqrt(n)
    if not verified_lightsout_supports(cover,n,side):
        return "cryptominisat_original_cnf", None, "NOT_LIGHTSOUT_SUPPORT_TOPOLOGY"
    if side % 4 == 1:
        return "janus_gf2", cover, "R1_R2_ODD_GRID_MOD4_1"
    if side % 4 == 3:
        return "cadical195_original_cnf", None, "R1_R2_ODD_GRID_MOD4_3"
    return "cryptominisat_native_xor", cover, "UNKNOWN_EVEN_GRID_NATIVE_FALLBACK"

def gf2(rows, n, cover=None):
    if cover is None:
        cover = r1.group_parity_equations(rows, n)
    if cover["status"] != "EXACT_XOR_COVER_PASS":
        raise AssertionError("GF2 CANNOT SOLVE UNCERTIFIED CNF")
    equations = cover["equations"]
    outcome = _gauss_with_linear_combination(equations)
    if outcome["status"] == "EXACT_GF2_SAT_CANDIDATE":
        bits = outcome["bits"]
        if not check_original_cnf(rows, n, bits):
            raise AssertionError("GF2 MODEL VIOLATES ORIGINAL CNF")
        return [i if ((bits >> (i-1)) & 1) else -i
                for i in range(1,n+1)], None, len(equations)
    if outcome["status"] == "EXACT_GF2_UNSAT_COMBINATION":
        if not independently_replay_unsat_combination(
                rows, n, outcome["combination_indices"]):
            raise AssertionError("BAD GF2 CONTRADICTION")
        return None, UNSAT, len(equations)
    raise AssertionError("unknown GF2 algebra state")

def raw_cadical(rows):
    from pysat.solvers import Solver
    with Solver(name="cadical195", bootstrap_with=rows) as solver:
        sat = solver.solve()
        if sat is True:
            return solver.get_model(), None
        if sat is False:
            return None, "UNSAT_SOLVER_NO_PORTABLE_PROOF"
    return None, "UNKNOWN_SOLVER"

def crypto(rows, n, native):
    import pycryptosat
    solver = pycryptosat.Solver(threads=1)
    eq_count = None
    if native:
        idx = r1.group_parity_equations(rows, n)
        if idx["status"] != "EXACT_XOR_COVER_PASS":
            raise AssertionError("NATIVE XOR REQUIRES EXACT COVER")
        eq_count = len(idx["equations"])
        for eq in idx["equations"]:
            solver.add_xor_clause(list(eq["variables"]), bool(eq["rhs"]))
    else:
        for clause in rows:
            solver.add_clause(clause)
    sat, values = solver.solve()
    if sat is True:
        return r1.cms_assignment(values, n), None, eq_count
    if sat is False:
        return None, "UNSAT_SOLVER_NO_PORTABLE_PROOF", eq_count
    return None, "UNKNOWN_SOLVER", eq_count

def cold_child(case, arm, expected_source_sha):
    resource.setrlimit(resource.RLIMIT_AS, (MEM_LIMIT, MEM_LIMIT))
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_LIMIT, CPU_LIMIT+1))
    t = perf_counter()
    _, protocol_sha = protocol()
    n, rows = source(case)
    src_sha = r1.original_sha(rows, n)
    if src_sha != expected_source_sha:
        raise AssertionError("UNFROZEN / ALTERED ORIGINAL SHA")
    decision = arm
    selector_reason = "BASELINE"
    model = None
    status = None
    certified_equations = None
    if arm == "janus_pre_solve_selector":
        decision, cover, selector_reason = choose_pre_solver(rows, n)
        if decision == "janus_gf2":
            model, status, certified_equations = gf2(rows, n, cover)
        elif decision == "cadical195_original_cnf":
            model, status = raw_cadical(rows)
        else:
            model, status, certified_equations = crypto(
                rows, n, native=decision == "cryptominisat_native_xor")
    elif arm == "janus_gf2":
        model, status, certified_equations = gf2(rows, n)
    elif arm == "cadical195_original_cnf":
        model, status = raw_cadical(rows)
    elif arm in ("cryptominisat_native_xor", "cryptominisat_original_cnf"):
        model, status, certified_equations = crypto(
            rows, n, native=arm == "cryptominisat_native_xor")
    else:
        raise AssertionError("unknown arm")
    if model is not None:
        if not r1.cnf_ok(rows, model):
            raise AssertionError("SAT MODEL FAILED REPLAY ON EVERY ORIGINAL CNF CLAUSE")
        status = SAT
    if status != SAT:
        raise AssertionError("R3 NEW SAT SOURCE NOT SOLVED AND VERIFIED: " + str(status))
    print(json.dumps({
        "schema":"JANUS-E12C5-R3-COLD-CHILD-V1",
        "case":case,"arm":arm,"engine_selected":decision,
        "selector_reason":selector_reason,"n":n,"m":len(rows),
        "source_sha256":src_sha,"prereg_sha256":protocol_sha,
        "status":status,"original_cnf_checked":True,
        "gf2_equations":certified_equations,
        "cold_inner_wall_s":perf_counter()-t,
        "cpu_seconds_limit":CPU_LIMIT,
        "memory_limit_bytes":MEM_LIMIT,
        "peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "production_C023":"UNCHANGED"},sort_keys=True),flush=True)

def self_test():
    _, psha = protocol()
    # Generator must be identical to frozen R1 on R1 inputs before R2 tests.
    for side,seed in ((19,202611030519),(25,202611030525),(37,202611030537)):
        a,b = grid(side,seed)
        aa,bb,status = r1.generate_grid(side,seed)
        if (a, b) != (aa, bb) or status!="SAT":
            raise AssertionError("new Lights-out source generator drift from R1")
    shas = []
    for case, size, seed in CASES:
        n,rows=source(case)
        if n!=size**2:
            raise AssertionError("new case wrong N")
        digest=r1.original_sha(rows,n)
        shas.append(digest)
        actual,cover,reason=choose_pre_solver(rows,n)
        expected=next(x["expect_engine"] for x in p["new_unseen_cases"]
                      if x["id"]==case)
        if actual!=expected:
            raise AssertionError("R3 selector route disagrees with frozen prereg")
        cert=r1.group_parity_equations(rows,n)
        if cert["status"]!="EXACT_XOR_COVER_PASS":
            raise AssertionError("R3 source not full XOR")
        model,unsat,_=gf2(rows,n,cert)
        if unsat is not None or not model or not r1.cnf_ok(rows,model):
            raise AssertionError("R3 source original model replay failed")
        if size in (33,41):
            tamper=rows[:-1]
            selected,cv,why=choose_pre_solver(tamper,n)
            if selected!="cryptominisat_original_cnf" or cv is not None or (
                    why!="NO_COMPLETE_XOR_CERTIFICATE"):
                raise AssertionError("partial mask wrongly trusted as XOR")
        if size==33:
            def swap(lit):
                sign=1 if lit>0 else -1
                v=abs(lit)
                return sign*(2 if v==1 else 1 if v==2 else v)
            relabeled=[[swap(lit) for lit in row] for row in rows]
            cover2=r1.group_parity_equations(relabeled,n)
            if cover2["status"]!="EXACT_XOR_COVER_PASS":
                raise AssertionError("renamed full-XOR control lost exact cover")
            select2,cv2,reason2=choose_pre_solver(relabeled,n)
            if (select2!="cryptominisat_original_cnf" or cv2 is not None or
                reason2!="NOT_LIGHTSOUT_SUPPORT_TOPOLOGY"):
                raise AssertionError("non-Lightsout structure was trusted as grid")
    if len(set(shas))!=len(CASES):
        raise AssertionError("duplicate R3 source SHA")
    g=r1.source("old_unsat_guard")
    if r1.solve_if_exact_xor(g[1],g[0])["verdict"]!="GF2_UNSAT_SAME_ADMIN_REPLAY_ONLY":
        raise AssertionError("old negative UNSAT guard failed")
    print("R3_FREEZE_SOURCE_PROOF_PASS",
          json.dumps({"prereg_sha256":psha, "source_sha256":dict(zip(
              (x[0] for x in CASES),shas))},sort_keys=True),flush=True)

def benchmark(out):
    prereg, prereg_sha = protocol()
    self_test()
    out.mkdir(parents=True, exist_ok=True)
    result=[]
    sources={}
    for index,(case,side,seed) in enumerate(CASES):
        n,rows=source(case)
        source_sha=r1.original_sha(rows,n)
        sources[case]={"source_sha256":source_sha,"n":n,
                       "m":len(rows),"seed":seed,"size":side,
                       "train_source":False}
        for repeat in range(3):
            order=list(ARMS)
            random.Random(ORDER_SEED+index*100+repeat).shuffle(order)
            for slot,arm in enumerate(order):
                cmd=[sys.executable,str(Path(__file__).resolve()),
                     "--child","--case",case,"--arm",arm,
                     "--source-sha",source_sha]
                t=perf_counter()
                try:
                    child=subprocess.run(cmd,text=True,capture_output=True,
                                         timeout=WALL_LIMIT,check=False)
                    if child.returncode==0:
                        output=json.loads(child.stdout)
                        if (output["case"],output["arm"],output["source_sha256"],
                            output["prereg_sha256"],output["status"])!=(
                                case,arm,source_sha,prereg_sha,SAT):
                            raise AssertionError("R3 child result identity/proof drift")
                    else:
                        output={"status":"ERROR_OR_CPU_CENSORED",
                                "returncode":child.returncode,
                                "stderr_tail":child.stderr[-1000:]}
                except subprocess.TimeoutExpired:
                    output={"status":"UNKNOWN_WALL_CENSORED"}
                elapsed=perf_counter()-t
                result.append({"case":case,"arm":arm,"repeat":repeat,
                               "order_slot":slot,"full_cold_child_wall_s":elapsed,
                               "outcome":output})
                print("E12C5_R3_COLD",case,repeat,arm,output["status"],
                      round(elapsed,5),flush=True)
    if len(result)!=len(CASES)*3*len(ARMS):
        raise AssertionError("R3 prereg 6*3*5 cold matrix missing")
    summary={}
    for case in sources:
        records=[x for x in result if x["case"]==case]
        m={}
        for arm in ARMS:
            rr=[x for x in records if x["arm"]==arm]
            ok=(len(rr)==3 and all(x["outcome"]["status"]==SAT for x in rr))
            m[arm]={"verified_3_of_3":ok,
                    "median_full_cold_s":median(x["full_cold_child_wall_s"] for x in rr) if ok else None,
                    "statuses":[x["outcome"]["status"] for x in rr]}
        sel=m["janus_pre_solve_selector"]
        comp=[m[x]["median_full_cold_s"] for x in ARMS[1:]
              if m[x]["verified_3_of_3"]]
        ratio=min(comp)/sel["median_full_cold_s"] if (
            sel["verified_3_of_3"] and comp) else None
        summary[case]={"arms":m,"ratio_fastest_verified_baseline":ratio,
                       "censored_arms":[x for x in ARMS[1:] if not m[x]["verified_3_of_3"]],
                       "median_selector_s":sel["median_full_cold_s"]}
    report={"schema":"JANUS-E12C5-R3-RAW-RESULT-V1",
        "prereg_sha256":prereg_sha,
        "protocol_git_blob_sha1":FROZEN_PROTOCOL_BLOB_SHA1,
        "source_generator_script_git_blob_sha1_R1":"192dc83338cb25dde0bc36f276d2ff52325c93e1",
        "r3_script_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "platform":platform.platform(),"python":sys.version,
        "source_manifest":sources,"records":result,"summary":summary,
        "censored_not_numeric_win":True,
        "R3_source_labels_not_used_in_training":True,
        "no_C023_promotion":True,"E12C4_autonomous_loop":"UNTOUCHED",
        "external_independent_witness":"NOT_DONE",
        "stage5_universal":"NOT_CLAIMED"}
    (out/"RESULT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print("E12C5_R3_COMPLETE",json.dumps({
        k:{"ratio":v["ratio_fastest_verified_baseline"],
           "censored_arms":v["censored_arms"]} for k,v in summary.items()},
        sort_keys=True),flush=True)

if __name__=="__main__":
    a=argparse.ArgumentParser()
    a.add_argument("--self-test",action="store_true")
    a.add_argument("--child",action="store_true")
    a.add_argument("--case",choices=[x[0] for x in CASES])
    a.add_argument("--arm",choices=ARMS)
    a.add_argument("--source-sha")
    a.add_argument("--out",type=Path)
    z=a.parse_args()
    if z.self_test:
        self_test()
    elif z.child:
        if not(z.case and z.arm and z.source_sha):
            a.error("--child requires --case --arm and --source-sha")
        cold_child(z.case,z.arm,z.source_sha)
    else:
        if z.out is None:
            a.error("--out required")
        benchmark(z.out)
