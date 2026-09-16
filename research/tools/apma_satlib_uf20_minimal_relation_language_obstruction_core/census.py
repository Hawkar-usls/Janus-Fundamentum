from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path
from typing import Any

from research.tools.apma_unseen_basis import raw_relation_basis as raw_basis

ROOT = Path(__file__).resolve().parents[3]
PREREG = ROOT / "research/TRUMP_SATLIB_UF20_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORE_PREREGISTRATION_2026-09-16.json"
PARENT = ROOT / "research/TRUMP_SATLIB_UF20_FAMILY_SEALED_PORTFOLIO_REPLICATION_RESULT_2026-09-16.json"
RAW_BASIS = ROOT / "research/tools/apma_unseen_basis/raw_relation_basis.py"
SEALED_PRIMITIVE = ROOT / "research/tools/apma_mixed_carrier_barrier/check_schaefer_barrier.py"
EXPECTED = {
    PREREG: "b75582fe0e0cb53e5b55dcf37a84944477505f92",
    PARENT: "277214289387abf6cf7e2d97bdf7dcf1f1727e07",
    RAW_BASIS: "63490c05ef3e91a4f682f75da26ff2af811839a6",
    SEALED_PRIMITIVE: "11fcacd5f0c550543f96648a7965734308509d22",
}
SOURCES = {
    "UF20_01": (ROOT / "research/source_data/SATLIB_UF20_01_2026-09-16.cnf", "8330041b292e0501f8d74c1b1d32ca96c4498864"),
    "UF20_02": (ROOT / "research/source_data/SATLIB_UF20_02_2026-09-16.cnf", "f924caaef0d868bf62b1658e83e030ad8daee865"),
    "UF20_03": (ROOT / "research/source_data/SATLIB_UF20_03_2026-09-16.cnf", "8f3d15154515457281f49201b843f2a7134dfa9f"),
    "UF20_04": (ROOT / "research/source_data/SATLIB_UF20_04_2026-09-16.cnf", "34ced5c169f967b2dc44ef5e42f2ee2c924813e1"),
    "UF20_05": (ROOT / "research/source_data/SATLIB_UF20_05_2026-09-16.cnf", "3b04eff26ee37bdd0bc21b1066486974f92a2c9b"),
}
BASIS_NAMES = ("ZERO_VALID", "ONE_VALID", "HORN", "DUAL_HORN", "BIJUNCTIVE", "AFFINE")
TYPE_IDS = tuple("".join(map(str, bits)) for bits in itertools.product((0, 1), repeat=3))
CUBE3 = tuple(itertools.product((0, 1), repeat=3))


def blob(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def source_guard() -> dict[str, Any]:
    bindings = {str(path.relative_to(ROOT)): blob(path) == expected for path, expected in EXPECTED.items()}
    source_bindings = {name: blob(path) == expected for name, (path, expected) in SOURCES.items()}
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    checks = {
        "prereg_status": prereg.get("status") == "FROZEN_BEFORE_256_SUBSET_RELATION_LANGUAGE_ENUMERATION",
        "parent_verdict": parent.get("verdict") == "PASS_DIAGNOSTIC_FAMILY_SEALED_PORTFOLIO_REPLICATION",
        "parent_replicated_count": parent.get("family_outcome", {}).get("replicated_unadmitted_count") == 5,
        "type_ids": tuple(prereg.get("frozen_relation_surface", {}).get("relation_type_ids", [])) == TYPE_IDS,
        "subset_count": prereg.get("frozen_relation_surface", {}).get("subset_count") == 256,
    }
    return {"ok": all(bindings.values()) and all(source_bindings.values()) and all(checks.values()), "bindings": bindings, "source_bindings": source_bindings, "checks": checks}


def relation_forbidden(type_id: str) -> set[tuple[int, ...]]:
    forbidden = tuple(int(ch) for ch in type_id)
    return {row for row in CUBE3 if row != forbidden}


def per_relation_basis_sets() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for type_id in TYPE_IDS:
        fp = raw_basis.classify_language([relation_forbidden(type_id)])
        out[type_id] = [name for name in BASIS_NAMES if fp.get(name)]
    return out


def subset_type_ids(mask: int) -> list[str]:
    return [TYPE_IDS[i] for i in range(8) if mask & (1 << i)]


def candidate_bases_for(ids: list[str]) -> tuple[list[str], dict[str, bool]]:
    if not ids:
        fp = {name: True for name in BASIS_NAMES}
        return list(BASIS_NAMES), fp
    relations = [relation_forbidden(type_id) for type_id in ids]
    fp = raw_basis.classify_language(relations)
    return [name for name in BASIS_NAMES if fp.get(name)], fp


def intersection_basis(ids: list[str], single: dict[str, list[str]]) -> list[str]:
    if not ids:
        return list(BASIS_NAMES)
    common = set(BASIS_NAMES)
    for type_id in ids:
        common &= set(single[type_id])
    return [name for name in BASIS_NAMES if name in common]


def parse_dimacs_surface(path: Path) -> tuple[Counter[str], list[tuple[int, int, int]]]:
    declared = None
    clauses: list[tuple[int, int, int]] = []
    pending: list[int] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("c") or line in {"%", "0"}:
            continue
        if line.startswith("p "):
            parts = line.split()
            if len(parts) != 4 or parts[1] != "cnf":
                raise AssertionError(("bad_header", path.name, line))
            declared = (int(parts[2]), int(parts[3]))
            continue
        for token in map(int, line.split()):
            if token == 0:
                if len(pending) != 3 or len({abs(x) for x in pending}) != 3:
                    raise AssertionError(("bad_clause", path.name, pending))
                clauses.append(tuple(pending))  # type: ignore[arg-type]
                pending = []
            else:
                pending.append(token)
    if pending or declared != (20, 91) or len(clauses) != 91:
        raise AssertionError(("dimacs_counts", path.name, declared, len(clauses), pending))

    counts: Counter[str] = Counter()
    for clause in clauses:
        by_var = {abs(lit): (0 if lit > 0 else 1) for lit in clause}
        scope = sorted(by_var)
        type_id = "".join(str(by_var[v]) for v in scope)
        if type_id not in TYPE_IDS:
            raise AssertionError(("unknown_relation_type", path.name, clause, type_id))
        counts[type_id] += 1
    return counts, clauses


def main() -> dict[str, Any]:
    guard = source_guard()
    if not guard["ok"]:
        return {"artifact_id": "JANUS-TRUMP-SATLIB-UF20-MINIMAL-RELATION-LANGUAGE-OBSTRUCTION-CORE-CENSUS-2026-09-16-v1.0", "verdict": "SOURCE_OR_FINGERPRINT_BINDING_FAILURE", "source_guard": guard, "scientific_firewall": firewall()}

    single = per_relation_basis_sets()
    rows = []
    obstruction_masks: list[int] = []
    basis_self_check = True
    for mask in range(256):
        ids = subset_type_ids(mask)
        bases, fp = candidate_bases_for(ids)
        intersection = intersection_basis(ids, single)
        if bases != intersection:
            basis_self_check = False
        obstruction = bool(ids) and not bases
        if obstruction:
            obstruction_masks.append(mask)
        rows.append({
            "mask": mask,
            "relation_types": ids,
            "size": len(ids),
            "candidate_bases": bases,
            "language_fingerprint": fp,
            "intersection_candidate_bases": intersection,
            "obstruction": obstruction,
        })

    if not basis_self_check:
        return {"artifact_id": "JANUS-TRUMP-SATLIB-UF20-MINIMAL-RELATION-LANGUAGE-OBSTRUCTION-CORE-CENSUS-2026-09-16-v1.0", "verdict": "BASIS_PREDICATE_SELF_CHECK_FAILURE", "source_guard": guard, "scientific_firewall": firewall()}

    obstruction_set = set(obstruction_masks)
    minimal_masks = []
    for mask in obstruction_masks:
        proper_masks = [sub for sub in range(256) if sub != mask and (sub & mask) == sub]
        if all(sub not in obstruction_set for sub in proper_masks):
            minimal_masks.append(mask)

    source_rows = []
    all_surface_ok = True
    for source, (path, _) in SOURCES.items():
        counts, _ = parse_dimacs_surface(path)
        surface = [type_id for type_id in TYPE_IDS if counts[type_id] > 0]
        surface_ok = surface == list(TYPE_IDS)
        all_surface_ok &= surface_ok
        source_rows.append({
            "source": source,
            "relation_surface": surface,
            "surface_is_exact_frozen_eight": surface_ok,
            "relation_type_clause_counts": {type_id: counts[type_id] for type_id in TYPE_IDS},
            "minimal_core_masks_present": [mask for mask in minimal_masks if all(type_id in counts and counts[type_id] > 0 for type_id in subset_type_ids(mask))],
        })

    minimal_cores = []
    for mask in minimal_masks:
        ids = subset_type_ids(mask)
        minimal_cores.append({
            "mask": mask,
            "relation_types": ids,
            "size": len(ids),
            "candidate_bases": [],
            "single_relation_basis_sets": {type_id: single[type_id] for type_id in ids},
            "present_in_sources": [row["source"] for row in source_rows if mask in row["minimal_core_masks_present"]],
        })

    if not all_surface_ok:
        verdict = "SOURCE_RELATION_SURFACE_GUARD_FAILURE"
    elif not minimal_cores:
        verdict = "NO_RELATION_LANGUAGE_OBSTRUCTION_FOUND"
    else:
        verdict = "PASS_MINIMAL_RELATION_LANGUAGE_OBSTRUCTION_CORES_ENUMERATED"

    return {
        "artifact_id": "JANUS-TRUMP-SATLIB-UF20-MINIMAL-RELATION-LANGUAGE-OBSTRUCTION-CORE-CENSUS-2026-09-16-v1.0",
        "authority": "DIAGNOSTIC_FINITE_RELATION_LANGUAGE_ANALYSIS_ONLY__NO_FORMULA_SOLVER_OR_MECHANISM",
        "verdict": verdict,
        "source_guard": guard,
        "frozen_relation_types": list(TYPE_IDS),
        "single_relation_basis_sets": single,
        "language_rows": rows,
        "obstruction_subset_count": len(obstruction_masks),
        "minimal_core_count": len(minimal_cores),
        "minimal_cores": minimal_cores,
        "source_presence_map": source_rows,
        "resource_receipt": {
            "relation_languages_enumerated": 256,
            "formula_subsets_enumerated": 0,
            "variable_assignment_cubes_enumerated": 0,
            "solver_invocations": 0,
            "new_solver_mechanisms": 0,
            "new_carrier_mechanisms": 0,
            "new_adapters": 0,
            "new_quotients": 0,
            "budget_raise": False,
        },
        "scientific_firewall": firewall(),
    }


def firewall() -> dict[str, Any]:
    return {
        "P_VS_NP": "OPEN",
        "GENERAL_SAT_IN_P": "NOT_PROVED",
        "GENERAL_GT2_TRACTABILITY": "NOT_PROVED",
        "CONNECTED_MIXED_CORE_SOLVED": "NO",
        "ARBITRARY_UNSEEN_INVARIANT_DISCOVERY": "NOT_PROVED",
        "MINIMAL_LANGUAGE_CORE_IMPLIES_HARDNESS": False,
    }


if __name__ == "__main__":
    print(json.dumps(main(), sort_keys=True, separators=(",", ":")))
