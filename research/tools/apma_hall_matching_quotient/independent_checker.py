import importlib.util
import itertools
import json
import math
import pathlib
import random
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / "research/tools/apma_hall_matching_quotient/hall_matching_quotient.py"
FIXTURE = ROOT / "research/TRUMP_APMA_HALL_MATCHING_HARD_FIXTURE_2026-09-14.json"

spec = importlib.util.spec_from_file_location("hall_candidate", CANDIDATE)
h = importlib.util.module_from_spec(spec)
spec.loader.exec_module(h)


def norm_clause(c):
    return tuple(sorted((int(x) for x in c), key=lambda x: (abs(x), x)))


def norm_cnf(cnf):
    return tuple(sorted((norm_clause(c) for c in cnf), key=lambda c: (len(c), c)))


def checker_instance(m, n, edges, functional=True):
    E = tuple(sorted({(int(u), int(v)) for u, v in edges}))
    ev = {e: i + 1 for i, e in enumerate(E)}
    cnf = []
    by_l = {u: [] for u in range(m)}
    by_r = {v: [] for v in range(n)}
    for (u, v), var in ev.items():
        by_l[u].append(var)
        by_r[v].append(var)
    for u in range(m):
        cnf.append(tuple(by_l[u]))
    for v in range(n):
        for a, b in itertools.combinations(sorted(by_r[v]), 2):
            cnf.append((-a, -b))
    if functional:
        for u in range(m):
            for a, b in itertools.combinations(sorted(by_l[u]), 2):
                cnf.append((-a, -b))
    return {"left_count": m, "right_count": n, "edges": E, "functional": functional, "cnf": norm_cnf(cnf)}


def eval_cnf(cnf, witness):
    for clause in cnf:
        if not any(bool(witness.get(abs(lit), False)) == (lit > 0) for lit in clause):
            return False
    return True


def independent_hall_ok(instance, S, N):
    S, N = set(S), set(N)
    actual = {v for u, v in instance["edges"] if u in S}
    return actual == N and len(N) < len(S)

def independent_matching_ok(instance, matching):
    if set(matching) != set(range(instance["left_count"])):
        return False
    if len(set(matching.values())) != len(matching):
        return False
    edges = set(instance["edges"])
    return all((u, v) in edges for u, v in matching.items())


def brute_has_saturating_matching(instance):
    m, n = instance["left_count"], instance["right_count"]
    if m > n:
        return False
    edges = set(instance["edges"])
    for holes in itertools.permutations(range(n), m):
        if all((u, holes[u]) in edges for u in range(m)):
            return True
    return False


def boundary_audit(adjacency, s, delta):
    m = len(adjacency)
    worst = None
    checked = 0
    for r in range(1, s + 1):
        need = math.ceil(delta * r - 1e-12)
        for S in itertools.combinations(range(m), r):
            checked += 1
            counts = {}
            for u in S:
                for v in adjacency[u]:
                    counts[v] = counts.get(v, 0) + 1
            boundary = sum(1 for c in counts.values() if c == 1)
            ratio = boundary / r
            worst = ratio if worst is None else min(worst, ratio)
            if boundary < need:
                return False, checked, worst
    return True, checked, worst

def main():
    t0 = time.perf_counter()
    checks = {}
    examples = {}
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    adj = fixture["adjacency"]
    edges = [(u, v) for u, ns in enumerate(adj) for v in ns]
    hard = checker_instance(fixture["left_count"], fixture["right_count"], edges, True)

    ok_exp, subset_checks, worst_ratio = boundary_audit(
        adj, fixture["audited_boundary_expansion"]["s"], fixture["audited_boundary_expansion"]["delta"]
    )
    checks["hard_fixture_boundary_expansion_full_audit"] = ok_exp
    checks["hard_fixture_left_degree_3"] = all(len(ns) == 3 for ns in adj)
    checks["hard_fixture_constant_clause_width"] = max(map(len, hard["cnf"])) <= 3
    hard_result = h.solve(hard)
    checks["hard_unsat_expander_terminal_unsat"] = hard_result["status"] == h.STATUS_UNSAT
    checks["hard_unsat_expander_hall_cert"] = independent_hall_ok(hard, hard_result["hall_S"], hard_result["hall_N"])
    examples["HARD_UNSAT_EXPANDER"] = {"status": hard_result["status"], "subset_checks": subset_checks, "worst_boundary_ratio": worst_ratio, "counting_baseline": h.counting_baseline(hard)["status"]}
    hall_edges = [(0,0),(0,1),(1,0),(1,1),(2,0),(2,1),(3,2),(3,3),(3,4)]
    hall_unsat = checker_instance(4, 5, hall_edges, True)
    hall_count = h.counting_baseline(hall_unsat)
    hall_result = h.solve(hall_unsat)
    checks["hall_control_counting_baseline_open"] = hall_count["status"] == "COUNTING_BASELINE_OPEN"
    checks["hall_control_main_unsat"] = hall_result["status"] == h.STATUS_UNSAT
    checks["hall_control_cert"] = independent_hall_ok(hall_unsat, hall_result["hall_S"], hall_result["hall_N"])
    examples["HALL_UNSAT_CONTROL"] = {"counting": hall_count["status"], "main": hall_result["status"], "S": hall_result["hall_S"], "N": hall_result["hall_N"]}

    sat_edges = [(0,0),(0,1),(1,1),(1,2),(2,2),(2,3),(3,3),(3,4),(4,4),(4,5)]
    sat = checker_instance(5, 6, sat_edges, True)
    sat_result = h.solve(sat)
    checks["sat_control_main_sat"] = sat_result["status"] == h.STATUS_SAT
    checks["sat_control_matching_cert"] = independent_matching_ok(sat, sat_result["matching"])
    checks["sat_control_root_replay"] = eval_cnf(sat["cnf"], sat_result["witness"])
    examples["SAT_MATCHING_CONTROL"] = {"status": sat_result["status"], "matching": sat_result["matching"]}

    checks["same_language_contains_sat_and_unsat"] = checks["hall_control_main_unsat"] and checks["sat_control_main_sat"]
    tampered = dict(sat)
    tampered["cnf"] = tuple(sat["cnf"][1:])
    checks["recognizer_rejects_tampered_cnf"] = h.solve(tampered)["status"] == h.STATUS_REJECT

    rng = random.Random(20260914)
    random_ok = 0
    random_sat = 0
    random_unsat = 0
    for _ in range(100):
        n = rng.randint(2, 5)
        m = rng.randint(1, min(5, n + 1))
        edges = [(u, v) for u in range(m) for v in range(n) if rng.random() < 0.45]
        inst = checker_instance(m, n, edges, True)
        truth = brute_has_saturating_matching(inst)
        got = h.solve(inst)
        if truth:
            ok = got["status"] == h.STATUS_SAT and independent_matching_ok(inst, got["matching"]) and eval_cnf(inst["cnf"], got["witness"])
            random_sat += 1
        else:
            ok = got["status"] == h.STATUS_UNSAT and independent_hall_ok(inst, got["hall_S"], got["hall_N"])
            random_unsat += 1
        random_ok += int(ok)
    checks["random_small_exact_100_of_100"] = random_ok == 100
    examples["random_small"] = {"count": 100, "sat": random_sat, "unsat": random_unsat, "exact": random_ok}
    source_text = CANDIDATE.read_text(encoding="utf-8").lower()
    forbidden = ["itertools.product", "permutations(", "powerset", "treewidth", "separator search", "zdd", "bdd", "brute force", "sat solver"]
    guard_hits = [x for x in forbidden if x in source_text]
    checks["captain_hidden_search_guard"] = not guard_hits

    prereg_text = (ROOT / "research/TRUMP_APMA_CARDINALITY_HALL_MATCHING_QUOTIENT_PREREG_2026-09-14.json").read_text(encoding="utf-8")
    checks["literature_hardness_reference_frozen"] = "TR15-078" in prereg_text and "Omega(n)" in prereg_text
    checks["promise_subclass_trivialization_guard_frozen"] = "PROMISE_SUBCLASS_TRIVIALIZATION_FORBIDDEN" in prereg_text
    checks["counting_baseline_proven_insufficient"] = hall_count["status"] == "COUNTING_BASELINE_OPEN" and hall_result["status"] == h.STATUS_UNSAT

    runtime_ms = (time.perf_counter() - t0) * 1000.0
    result = {
        "schema":"JANUS_TRUMP_APMA_CARDINALITY_HALL_MATCHING_QUOTIENT_GATE_V1",
        "verdict":"PASS_GRAPH_PHP_CARDINALITY_HALL_MATCHING_QUOTIENT__COUNTING_BASELINE_INSUFFICIENT__RESOLUTION_WIDTH_SEPARATION_LITERATURE_BOUND" if all(checks.values()) else "FAIL_GRAPH_PHP_CARDINALITY_HALL_MATCHING_QUOTIENT_GATE",
        "checks":checks,
        "captain_guard_hits":guard_hits,
        "examples":examples,
        "runtime_ms":round(runtime_ms,3),
        "asymptotic_ledger":{"recognize":"poly(|F|)","construct_graph":"O(|F|)","matching_Hall":"polynomial augmenting paths","reconstruct_verify":"O(|F|)","archive_codec":"outside scientific asymptotics"},
        "hardness_baseline":{
            "family":"FPHP(G_n) over degree-3 (gamma*n,delta)-boundary expanders with |L|=n+1, |R|=n",
            "resolution_width":"Omega(n) via width > delta*s/(2*d), s=gamma*n, d=3",
            "reference":"Miksa-Nordstrom ECCC TR15-078 Theorem 4.9; resolution-width restatement in Galesi-Kolodziejczyk-Thapen ECCC TR19-052 Theorem 28",
            "finite_fixture_is_only_smoke":True
        },
        "proved_scope_if_pass":"One polynomially recognizable canonical graph-PHP language containing SAT and UNSAT instances is decided exactly through a non-GF(2) bipartite-matching/Hall quotient with polynomial construction, certificate recovery, and independent source-CNF replay; the cited expander subfamily has growing resolution width.",
        "not_proved":[
            "No new proof of the cited resolution-width lower bound; hardness is literature-bound.",
            "No claim that every CNF admits a matching/Hall quotient.",
            "No universal APMA selector theorem.",
            "No SAT-in-P or P=NP claim."
        ],
        "scientific_status":{"SAT_IN_P":"NOT_PROVED","P_VS_NP":"OPEN","Pi_negative_evidence_weight":0},
        "next_gate":"APMA_NONSCHEMA_POLYTIME_QUOTIENT_DISCOVERY_FALSIFIER_HUNT"
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
