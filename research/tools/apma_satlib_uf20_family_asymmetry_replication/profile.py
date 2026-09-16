from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

from research.tools.apma_unseen_basis.raw_relation_basis import canonicalize_raw
from research.tools.apma_satlib_uf20_01_missing_invariant_profile import profile as frozen

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_SATLIB_UF20_FAMILY_ASYMMETRY_REPLICATION_PREREGISTRATION_2026-09-16.json"
EXPECTED_PREREG_BLOB = "TO_BE_BOUND_BY_WORKFLOW"
SOURCES = {
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b"),
}


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def canonical_sha256(obj: object) -> str:
    data = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def parse_dimacs(path: Path) -> list[tuple[int, ...]]:
    clauses = []
    declared = None
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("c") or s == "%" or s == "0":
            continue
        if s.startswith("p "):
            p = s.split()
            if len(p) != 4 or p[1] != "cnf":
                raise ValueError(f"BAD_HEADER:{path.name}")
            declared = (int(p[2]), int(p[3]))
            continue
        row = [int(x) for x in s.split()]
        if not row or row[-1] != 0:
            raise ValueError(f"BAD_CLAUSE:{path.name}")
        clause = tuple(row[:-1])
        if len(clause) != 3 or len({abs(x) for x in clause}) != 3:
            raise ValueError(f"NOT_DISTINCT_3CNF:{path.name}")
        clauses.append(clause)
    if declared != (20, 91) or len(clauses) != 91:
        raise ValueError(f"BAD_DIMACS_COUNTS:{path.name}:{declared}:{len(clauses)}")
    return clauses


def raw_from_clauses(source_key: str, clauses: list[tuple[int, ...]]) -> dict:
    constraints = []
    prefix = source_key.lower()
    for ordinal, clause in enumerate(clauses, 1):
        scope = sorted(abs(x) for x in clause)
        lit_by_var = {abs(x): x for x in clause}
        allowed = []
        for bits in itertools.product((0, 1), repeat=3):
            assignment = dict(zip(scope, bits))
            sat = any(bool(assignment[abs(lit)]) if lit > 0 else not bool(assignment[abs(lit)]) for lit in clause)
            if sat:
                allowed.append(list(bits))
        constraints.append({"id": f"satlib_{prefix}_c{ordinal:03d}", "scope": scope, "allowed": allowed})
    return canonicalize_raw({"variables": list(range(1, 21)), "constraints": constraints})


def profile_one(source_key: str, path: Path) -> dict:
    clauses = parse_dimacs(path)
    raw = raw_from_clauses(source_key, clauses)
    vars_ = raw["variables"]

    adj = {v: set() for v in vars_}
    for c in raw["constraints"]:
        for u, v in itertools.combinations(c["scope"], 2):
            adj[u].add(v); adj[v].add(u)
    edges = sum(len(x) for x in adj.values()) // 2
    deg = {v: len(adj[v]) for v in vars_}
    arts, bridges = frozen.tarjan_art_bridges(vars_, adj)
    cuts = frozen.low_cuts(vars_, adj)

    iadj = defaultdict(set); inodes = set()
    for v in vars_:
        inodes.add(f"v:{v}")
    for c in raw["constraints"]:
        cn = f"c:{c['id']}"; inodes.add(cn)
        for v in c["scope"]:
            vn = f"v:{v}"; iadj[vn].add(cn); iadj[cn].add(vn)
    iarts, ibridges = frozen.tarjan_art_bridges(inodes, iadj)
    ivcuts = frozen.incidence_var_cuts(raw)

    overlap = Counter(); o1 = {c["id"]: set() for c in raw["constraints"]}; o2 = {c["id"]: set() for c in raw["constraints"]}
    for a, b in itertools.combinations(raw["constraints"], 2):
        k = len(set(a["scope"]) & set(b["scope"])); overlap[k] += 1
        if k >= 1:
            o1[a["id"]].add(b["id"]); o1[b["id"]].add(a["id"])
        if k >= 2:
            o2[a["id"]].add(b["id"]); o2[b["id"]].add(a["id"])
    clause_ids = list(o1)

    keys = sorted({frozen.relkey(c) for c in raw["constraints"]}); idx = {k: i for i, k in enumerate(keys)}
    rfp = [frozen.fp(k) for k in keys]
    rel_counts = [0] * len(keys); var_rel = {v: [0] * len(keys) for v in vars_}; horn = {v: 0 for v in vars_}; dual = {v: 0 for v in vars_}
    for c in raw["constraints"]:
        i = idx[frozen.relkey(c)]; rel_counts[i] += 1
        for v in c["scope"]:
            var_rel[v][i] += 1; horn[v] += int(rfp[i]["HORN"]); dual[v] += int(rfp[i]["DUAL_HORN"])

    pos = Counter(); neg = Counter()
    for cl in clauses:
        for lit in cl:
            (pos if lit > 0 else neg)[abs(lit)] += 1
    sig = {}; groups = defaultdict(list)
    for v in vars_:
        s = (deg[v], pos[v], neg[v], tuple(var_rel[v]), tuple(sorted(deg[n] for n in adj[v])))
        h = hashlib.sha256(json.dumps(s, separators=(",", ":")).encode()).hexdigest()[:16]
        sig[v] = h; groups[h].append(v)

    rem = set(vars_); work = {v: set(adj[v]) for v in vars_}; degen = 0
    while rem:
        v = min(rem, key=lambda x: (len(work[x] & rem), x)); degen = max(degen, len(work[v] & rem)); rem.remove(v)
    triangles = sum(1 for a, b, c in itertools.combinations(vars_, 3) if b in adj[a] and c in adj[a] and c in adj[b])

    return {
        "source": source_key,
        "source_blob_sha1": git_blob_sha1(path),
        "raw_sha256": canonical_sha256(raw),
        "P1_primal": {"vertices": 20, "edges": edges, "density": edges / 190, "degree_min": min(deg.values()), "degree_max": max(deg.values()), "articulation_points": arts, "bridges": bridges, **cuts},
        "P2_incidence": {"vertices": len(inodes), "edges": sum(len(x) for x in iadj.values()) // 2, "articulation_count": len(iarts), "bridge_count": len(ibridges), "variable_only_cuts": ivcuts},
        "P3_overlap": {"pair_intersection_counts": {str(k): overlap[k] for k in sorted(overlap)}, "graph_ge1_connected": frozen.conn(clause_ids, o1), "graph_ge2_connected": frozen.conn(clause_ids, o2), "graph_ge1_edges": sum(len(x) for x in o1.values()) // 2, "graph_ge2_edges": sum(len(x) for x in o2.values()) // 2},
        "P4_local_mixing": {"relation_surface_count": len(keys), "relation_constraint_counts": rel_counts, "relation_fingerprints": rfp},
        "P5_variable_signature": {"distinct_signature_count": len(groups), "all_singleton_signatures": all(len(x) == 1 for x in groups.values()), "signature_groups": dict(sorted(groups.items()))},
        "P6_core": {"degeneracy": degen, "triangle_count": triangles, "low_order_primal_cut_counts": cuts["cut_counts"]},
    }


def main() -> dict:
    source_guard = {name: git_blob_sha1(path) == expected for name, (path, expected) in SOURCES.items()}
    if not all(source_guard.values()):
        return {"verdict": "SOURCE_OR_NORMALIZATION_GUARD_FAILURE", "source_guard": source_guard}
    rows = [profile_one(name, path) for name, (path, _) in SOURCES.items()]
    all_rep = all(
        row["P1_primal"]["cut_counts"] == {"1": 0, "2": 0, "3": 0, "4": 0}
        and row["P2_incidence"]["variable_only_cuts"]["cut_counts"] == {"1": 0, "2": 0, "3": 0, "4": 0}
        and row["P5_variable_signature"]["distinct_signature_count"] == 20
        and row["P5_variable_signature"]["all_singleton_signatures"] is True
        for row in rows
    )
    if all_rep:
        verdict = "REPLICATION_ALL_FOUR_MATCH_DENSE_LOW_CUT_ALL_SINGLETON_PROFILE"
    elif any(row["P1_primal"]["minimum_cut_if_le4"] is not None or row["P2_incidence"]["variable_only_cuts"]["minimum_variable_only_cut_if_le4"] is not None for row in rows):
        verdict = "PARTIAL_REPLICATION_LOW_ORDER_SEPARATOR_EMERGES"
    elif any(not row["P5_variable_signature"]["all_singleton_signatures"] for row in rows):
        verdict = "PARTIAL_REPLICATION_SIGNATURE_CLASSES_EMERGE"
    else:
        verdict = "PARTIAL_REPLICATION_OTHER_PROFILE_DIVERGENCE"
    return {
        "artifact_id": "JANUS-TRUMP-SATLIB-UF20-FAMILY-ASYMMETRY-REPLICATION-2026-09-16-v1.0",
        "authority": "DIAGNOSTIC_ONLY__SOURCE_BOUND_FAMILY_REPLICATION_BEFORE_MECHANISM_DESIGN",
        "verdict": verdict,
        "source_guard": source_guard,
        "rows": rows,
        "scientific_firewall": {"P_VS_NP": "OPEN", "GENERAL_SAT_IN_P": "NOT_PROVED", "CONNECTED_MIXED_CORE_SOLVED": "NO", "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED", "NEW_SOLVER_MECHANISMS": 0, "NEW_CARRIER_MECHANISMS": 0},
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True))
