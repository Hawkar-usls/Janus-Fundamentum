from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path("research/source_data/SATLIB_UF20_01_2026-09-16.cnf")
RAW = Path("research/source_data/SATLIB_UF20_01_RAW_2026-09-16.json")
FREEZE = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_NEW_EVIDENCE_SOURCE_FREEZE_SATLIB_UF20_01_2026-09-16.json")
PREREG = Path("research/TRUMP_SOURCE_AUTHORIZED_CONNECTED_MIXED_RAW_POST_ORBIT_NEW_EVIDENCE_REPLAY_PREREGISTRATION_SATLIB_UF20_01_2026-09-16.json")
REPLAY = Path("research/tools/apma_external_satlib_uf20_01_replay/replay.py")
EXPECTED_BLOBS = {
    SOURCE: "8330041b292e0501f8d74c1b1d32ca96c4498864",
    RAW: "8b69a8f533ffaec44f196eea8791b0678f3f579c",
    FREEZE: "e21a59d5f4a248dfa2b25f643e9220c96affb1cf",
    PREREG: "76a88842bbf0403f0838e3d7811b5205dced0eaf",
    REPLAY: "67ae8bd40c58c6bb1f22f7651111d33ba6be1d0b",
}
EXPECTED_RAW_SHA = "a99bb4047dee6969bd3339ba99ba9df434ecc808a4a161139462e1993fc3b874"
EXPECTED_SOURCE_SHA = "abd551864c6ff7403c3f4fc52737467a029954ce5ae7b0e5bf9ef0a9dde13509"
CLOSED_ORBIT = {"ADMIT_ORBIT_COUNT_QUOTIENT_SAT", "ADMIT_ORBIT_COUNT_QUOTIENT_UNSAT"}
SCHAEFER = ("ZERO_VALID", "ONE_VALID", "HORN", "DUAL_HORN", "BIJUNCTIVE", "AFFINE")


def blob_sha(path: Path) -> str:
    data = (ROOT / path).read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def cbytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def parse_source() -> tuple[int, list[tuple[int, ...]]]:
    nvars = nclauses = None
    clauses = []
    for raw in (ROOT / SOURCE).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("c"):
            continue
        if line.startswith("p "):
            p = line.split()
            if p[:2] != ["p", "cnf"] or len(p) != 4:
                raise ValueError("BAD_HEADER")
            nvars, nclauses = int(p[2]), int(p[3])
            continue
        vals = tuple(int(x) for x in line.split())
        if not vals or vals[-1] != 0:
            raise ValueError("BAD_CLAUSE_TERMINATOR")
        clause = vals[:-1]
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
            raise ValueError("BAD_WIDTH3_CLAUSE")
        clauses.append(clause)
    if (nvars, nclauses, len(clauses)) != (20, 91, 91):
        raise ValueError("COUNT_MISMATCH")
    return nvars, clauses


def canonical_raw(raw: dict) -> dict:
    variables = list(raw["variables"])
    if variables != sorted(set(variables)):
        raise ValueError("BAD_VARIABLES")
    rows = []
    ids = set()
    for c in raw["constraints"]:
        if set(c) != {"id", "scope", "allowed"}:
            raise ValueError("BAD_CONSTRAINT_KEYS")
        rid = str(c["id"])
        if rid in ids:
            raise ValueError("DUPLICATE_ID")
        ids.add(rid)
        scope = list(c["scope"])
        if len(scope) != len(set(scope)) or any(v not in variables for v in scope):
            raise ValueError("BAD_SCOPE")
        allowed = sorted({tuple(int(b) for b in t) for t in c["allowed"]})
        if not allowed or any(len(t) != len(scope) or any(b not in (0, 1) for b in t) for t in allowed):
            raise ValueError("BAD_ALLOWED")
        rows.append({"id": rid, "scope": scope, "allowed": [list(t) for t in allowed]})
    rows.sort(key=lambda r: (tuple(r["scope"]), tuple("".join(map(str, t)) for t in r["allowed"]), r["id"]))
    return {"variables": variables, "constraints": rows}


def normalize_source(nvars: int, clauses: list[tuple[int, ...]]) -> dict:
    rows = []
    for i, clause in enumerate(clauses, 1):
        scope = sorted(abs(l) for l in clause)
        allowed = []
        for bits in itertools.product((0, 1), repeat=3):
            a = dict(zip(scope, bits, strict=True))
            if any((a[abs(l)] == 1) if l > 0 else (a[abs(l)] == 0) for l in clause):
                allowed.append(list(bits))
        rows.append({"id": f"satlib_uf20_01_c{i:03d}", "scope": scope, "allowed": allowed})
    return canonical_raw({"variables": list(range(1, nvars + 1)), "constraints": rows})


def relation_sets(raw: dict) -> list[set[tuple[int, ...]]]:
    uniq = {}
    for c in raw["constraints"]:
        rel = {tuple(t) for t in c["allowed"]}
        key = (len(c["scope"]), tuple(sorted(rel)))
        uniq[key] = rel
    return [uniq[k] for k in sorted(uniq)]


def fp(rel: set[tuple[int, ...]]) -> dict[str, bool]:
    arity = len(next(iter(rel)))
    zero = tuple(0 for _ in range(arity)) in rel
    one = tuple(1 for _ in range(arity)) in rel
    horn = all(tuple(x & y for x, y in zip(a, b)) in rel for a in rel for b in rel)
    dual = all(tuple(x | y for x, y in zip(a, b)) in rel for a in rel for b in rel)
    bij = all(tuple(int(x + y + z >= 2) for x, y, z in zip(a, b, c)) in rel for a in rel for b in rel for c in rel)
    affine = all(tuple(x ^ y ^ z for x, y, z in zip(a, b, c)) in rel for a in rel for b in rel for c in rel)
    return {"ZERO_VALID": zero, "ONE_VALID": one, "HORN": horn, "DUAL_HORN": dual, "BIJUNCTIVE": bij, "AFFINE": affine}


def connected(raw: dict) -> bool:
    adj = {v: set() for v in raw["variables"]}
    for c in raw["constraints"]:
        s = c["scope"]
        for i, u in enumerate(s):
            for v in s[i + 1:]:
                adj[u].add(v); adj[v].add(u)
    start = raw["variables"][0]
    seen, stack = {start}, [start]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v); stack.append(v)
    return len(seen) == len(raw["variables"])


def check(candidate: dict) -> dict[str, Any]:
    observed = {str(p): blob_sha(p) for p in EXPECTED_BLOBS}
    guard = {str(p): observed[str(p)] == sha for p, sha in EXPECTED_BLOBS.items()}

    nvars, clauses = parse_source()
    src_obj = {"format": "DIMACS_CNF", "variables": nvars, "clauses": [list(c) for c in clauses]}
    src_sha = hashlib.sha256(cbytes(src_obj)).hexdigest()
    generated = normalize_source(nvars, clauses)
    stored = canonical_raw(json.loads((ROOT / RAW).read_text()))
    raw_sha = hashlib.sha256(cbytes(generated)).hexdigest()

    freeze = json.loads((ROOT / FREEZE).read_text())
    frozen23 = set(freeze["frozen_corpus_nonalias_guard"]["frozen_23_sha256"])
    rels = relation_sets(stored)
    local = [fp(r) for r in rels]
    global_fp = {name: all(x[name] for x in local) for name in SCHAEFER}
    eligible = connected(stored) and all(any(x.values()) for x in local) and not any(global_fp.values())
    exact_or2_xor_surface = False

    e4 = candidate.get("E4_orbit_replay", {})
    if e4.get("executed") is True and e4.get("status") in CLOSED_ORBIT and e4.get("solver_authority") is True:
        expected_verdict = "PASS_DIAGNOSTIC_NEW_SOURCE_CLOSED_BY_SEALED_ORBIT_COUNT_V1"
        expected_obstruction_none = True
    elif e4.get("executed") is True:
        expected_verdict = "PASS_DIAGNOSTIC_FIRST_REAL_NEW_POST_PORTFOLIO_OBSTRUCTION_IDENTIFIED"
        expected_obstruction_none = False
    else:
        expected_verdict = candidate.get("verdict")
        expected_obstruction_none = candidate.get("first_real_post_portfolio_obstruction") is None

    checks = {
        "source_guard": all(guard.values()),
        "source_sha": src_sha == EXPECTED_SOURCE_SHA,
        "raw_regeneration_exact": generated == stored,
        "raw_sha": raw_sha == EXPECTED_RAW_SHA,
        "nonalias_frozen23": raw_sha not in frozen23,
        "connected": connected(stored),
        "eight_relation_surfaces": len(rels) == 8,
        "every_local_schaefer_admissible": all(any(x.values()) for x in local),
        "no_single_global_schaefer_basis": not any(global_fp.values()),
        "eligible_connected_mixed": eligible,
        "log_alien_not_applicable": candidate.get("E3_log_alien_replay", {}).get("applicable") is False and not exact_or2_xor_surface,
        "candidate_source_guard": candidate.get("source_guard", {}).get("ok") is True,
        "candidate_e0_raw_sha": candidate.get("E0", {}).get("raw_sha256") == raw_sha,
        "candidate_e0_source_sha": candidate.get("E0", {}).get("source_semantic_sha256") == src_sha,
        "candidate_e1_eligible": candidate.get("E1", {}).get("eligible") is True,
        "candidate_verdict_consistent": candidate.get("verdict") == expected_verdict,
        "obstruction_presence_consistent": (candidate.get("first_real_post_portfolio_obstruction") is None) == expected_obstruction_none,
        "no_full_cube": candidate.get("resource_receipt", {}).get("full_variable_cube_enumerations") == 0,
        "no_new_solver": candidate.get("resource_receipt", {}).get("new_solver_mechanisms") == 0,
        "no_new_carrier": candidate.get("resource_receipt", {}).get("new_carrier_mechanisms") == 0,
        "p_vs_np_open": candidate.get("scientific_firewall", {}).get("P_VS_NP") == "OPEN",
        "general_sat_not_proved": candidate.get("scientific_firewall", {}).get("GENERAL_SAT_IN_P") == "NOT_PROVED",
    }
    return {
        "artifact_id": "JANUS-TRUMP-SATLIB-UF20-01-INDEPENDENT-REPLAY-CHECK-2026-09-16-v1.0",
        "authority": "INDEPENDENT_DIAGNOSTIC_CHECK_ONLY",
        "verified": all(checks.values()),
        "verdict": candidate.get("verdict"),
        "source_guard": {"ok": all(guard.values()), "checks": guard, "replay_imported": False},
        "checks": checks,
        "independent_receipt": {
            "source_semantic_sha256": src_sha,
            "raw_sha256": raw_sha,
            "relation_surface_count": len(rels),
            "global_language_fingerprint": global_fp,
            "eligible_connected_mixed": eligible,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-json", required=True)
    args = ap.parse_args()
    candidate = json.loads(Path(args.candidate_json).read_text().strip().splitlines()[-1])
    print(json.dumps(check(candidate), sort_keys=True))


if __name__ == "__main__":
    main()
