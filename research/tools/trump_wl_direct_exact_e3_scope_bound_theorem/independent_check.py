from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import deque
from pathlib import Path

from research.tools.apma_unseen_local_invariant_orbit_count import candidate as e3

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_PREREGISTRATION_2026-09-18_v1.0.json"
REVIEW = ROOT / "research/TRUMP_WL_DIRECT_EXACT_E3_SCOPE_BOUND_THEOREM_REVIEW_2026-09-18_v1.0.json"
PROOF = ROOT / "research/tools/trump_wl_direct_exact_e3_scope_bound_theorem/proof_certificate.py"
E3 = ROOT / "research/tools/apma_unseen_local_invariant_orbit_count/candidate.py"
PANELS = [
    ROOT / "research/TRUMP_UF20_026_075_PROSPECTIVE_WL_ORBIT_BRIDGE_REPLICATION_RESULT_2026-09-17_v1.0.json",
    ROOT / "research/TRUMP_UF20_076_175_SECOND_PROSPECTIVE_WL_ORBIT_BRIDGE_REPLICATION_RESULT_2026-09-17_v1.0.json",
    ROOT / "research/TRUMP_UF20_176_275_THIRD_PROSPECTIVE_WL_ORBIT_BRIDGE_REPLICATION_RESULT_2026-09-17_v1.0.json",
]
EXPECTED = {
    PREREG: "3ce13cf63ee3b752206fdd950283b457cc69bb99",
    REVIEW: "32071a278871f5f10e40f3e561ccbd70e5d50cf7",
    PROOF: "9b06efdd4dc6291e0af45fffbca01d20e75b988c",
    E3: "a076cfc56d68aad0348415e313705da1f6b9cdcd",
}
PROOF_MODULE = "research.tools.trump_wl_direct_exact_e3_scope_bound_theorem.proof_certificate"


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def partitions(n: int, lo: int = 1):
    if n == 0:
        yield ()
        return
    for first in range(lo, n + 1):
        for rest in partitions(n - first, first):
            yield (first,) + rest


def q_of(parts):
    q = 1
    for m in parts:
        q *= m + 1
    return q


def partition_check():
    checked = 0
    failures = []
    equality_cases = []
    for n in range(2, 21):
        bound = 3 * 2 ** (n - 2)
        for p in partitions(n):
            if max(p) < 2:
                continue
            checked += 1
            q = q_of(p)
            if q == bound:
                equality_cases.append([n, list(p)])
            if q > bound or q >= 2**n:
                failures.append([n, list(p), q, bound])
    symbolic_local_lemma = all((m + 1) <= 3 * 2 ** (m - 2) for m in range(2, 101))
    symbolic_k_factor = all(3 ** (k - 1) <= 4 ** (k - 1) for k in range(1, 101))
    return {
        "checked": checked,
        "failures": failures,
        "equality_cases": equality_cases,
        "symbolic_local_lemma_integer_sanity_2_100": symbolic_local_lemma,
        "symbolic_nontrivial_component_factor_integer_sanity_1_100": symbolic_k_factor,
    }


def connected(n, edge_set):
    adj = [set() for _ in range(n)]
    for u, v in edge_set:
        adj[u].add(v)
        adj[v].add(u)
    seen = {0}
    stack = [0]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == n


def compose(a, b):
    return tuple(a[b[i]] for i in range(len(a)))


def transposition(n, u, v):
    p = list(range(n))
    p[u], p[v] = p[v], p[u]
    return tuple(p)


def generated_group_size(n, edge_set):
    gens = [transposition(n, u, v) for u, v in edge_set]
    identity = tuple(range(n))
    seen = {identity}
    q = deque([identity])
    while q:
        g = q.popleft()
        for t in gens:
            h = compose(t, g)
            if h not in seen:
                seen.add(h)
                q.append(h)
    return len(seen)


def graph_group_check():
    graphs = 0
    failures = []
    for n in range(2, 6):
        edges = list(itertools.combinations(range(n), 2))
        for mask in range(1 << len(edges)):
            es = [edges[i] for i in range(len(edges)) if (mask >> i) & 1]
            if not connected(n, es):
                continue
            graphs += 1
            size = generated_group_size(n, es)
            if size != math.factorial(n):
                failures.append({"n": n, "edges": es, "group_size": size, "expected": math.factorial(n)})
    return {"connected_graphs_checked": graphs, "failures": failures}


def synthetic_e3_check():
    rows = []
    failures = []
    for n in range(2, 11):
        for unsat in (False, True):
            constraints = [{"id": "empty-nullary", "scope": [], "allowed": []}] if unsat else []
            raw = {"variables": list(range(n)), "constraints": constraints}
            f = e3.validate_and_normalize(raw)
            direct = e3.is_exact_transposition_automorphism(f, 0, 1)
            bound_ok = 3 * 2 ** (n - 2) <= f.L * f.L
            out = e3.run_candidate(raw)
            expect = "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT" if unsat else "ADMIT_ORBIT_COUNT_QUOTIENT_SAT"
            ok = direct and bound_ok and out.get("status") == expect and out.get("solver_authority") is True
            row = {"n": n, "unsat": unsat, "L": f.L, "bound_ok": bound_ok, "direct": direct, "status": out.get("status"), "q": out.get("quotient_states_Q"), "pass": ok}
            rows.append(row)
            if not ok:
                failures.append(row)
    return {"cases": rows, "failures": failures}


def uf20_corollary_check():
    rows = []
    failures = []
    for path in PANELS:
        data = json.loads(path.read_text())
        positives = data.get("summary", {}).get("wl_prediction_positive_sources", [])
        pred = {r["source"]: r for r in data.get("prediction_rows", [])}
        gt = {r["source"]: r for r in data.get("ground_truth_rows", [])}
        for source in positives:
            p = pred[source]
            g = gt[source]
            receipt = g.get("E3", {}).get("resource_receipt", {})
            n = int(receipt.get("variables_n"))
            L = int(receipt.get("input_bytes_L"))
            bound = 3 * 2 ** (n - 2)
            edges = [sorted(map(int, e)) for e in (g.get("E3", {}).get("generator_edges") or [])]
            pair = p.get("wl_derived_pair")
            ok = (
                p.get("prediction_positive") is True
                and p.get("direct_exact_transposition_automorphism") is True
                and pair in edges
                and bound <= L * L
                and g.get("e3_positive") is True
                and g.get("E3", {}).get("solver_authority") is True
            )
            row = {"panel": path.name, "source": source, "n": n, "L": L, "bound": bound, "L2": L * L, "pair": pair, "pass": ok}
            rows.append(row)
            if not ok:
                failures.append(row)
    return {"positive_rows": rows, "positive_count": len(rows), "failures": failures}


def main(candidate_path: Path):
    bindings = {str(p.relative_to(ROOT)): blob(p) == h for p, h in EXPECTED.items()}
    if not all(bindings.values()):
        return {"verdict": "HALT_INDEPENDENT_AUTHORITY_BINDING_FAILURE", "bindings": bindings}
    if PROOF_MODULE in sys.modules:
        return {"verdict": "HALT_INDEPENDENT_PROOF_MODULE_IMPORT_VIOLATION"}
    candidate = json.loads(candidate_path.read_text())
    pc = partition_check()
    gc = graph_group_check()
    sc = synthetic_e3_check()
    uc = uf20_corollary_check()
    checks = {
        "candidate_pass": candidate.get("verdict") == "PASS_SCOPE_BOUND_DIRECT_EXACT_TO_E3_ADMISSION_THEOREM_CERTIFICATE",
        "candidate_firewall": candidate.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
        "partition_bound": not pc["failures"],
        "connected_graph_transposition_generation": not gc["failures"],
        "synthetic_scope_sat_unsat": not sc["failures"],
        "uf20_corollary": not uc["failures"] and uc["positive_count"] == 6,
        "proof_module_not_imported": PROOF_MODULE not in sys.modules,
    }
    return {
        "artifact_id": "JANUS-TRUMP-WL-DIRECT-EXACT-E3-SCOPE-BOUND-THEOREM-INDEPENDENT-CHECK-2026-09-18-v1.0",
        "bindings": bindings,
        "comparison_checks": checks,
        "partition_check": pc,
        "connected_graph_group_check": gc,
        "synthetic_e3_check": sc,
        "uf20_source_bound_corollary": uc,
        "candidate_imported": False,
        "verdict": "PASS_INDEPENDENT_SCOPE_BOUND_E3_THEOREM_VERIFICATION" if all(checks.values()) else "FAIL_INDEPENDENT_SCOPE_BOUND_E3_THEOREM_VERIFICATION",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    args = ap.parse_args()
    print(json.dumps(main(Path(args.candidate)), sort_keys=True, separators=(",", ":")))
