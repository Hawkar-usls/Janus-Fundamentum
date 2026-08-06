#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import tempfile
from pathlib import Path
from typing import Any, Iterable, Sequence

SCHEMA = "C049.1-B4.6.3-CORRECTED-NODE7-SIX-GENERATOR-UP-K-v1"
PARENT_HEAD = "796ad144de65906c702e29928f683e6d53e3529c"
SOURCE_SHA256 = "b0d8d4e51be21f21218fd9ee63a367e3236ff2a53d9d5f29980e1c93340867ca"
SOURCE_SEMANTIC = "750990191184f37e321a83a66040fab490fa0db3ad3eb07e9941d3e31e7d88dd"
PATTERNS = ((0,), (0, 1), (0, 1, 0), (1,), (1, 0), (1, 0, 1))
CODES = {"".join(map(str, pattern)): pattern for pattern in PATTERNS}
STEPS = ((1, 0), (0, 1), (1, 1))


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xor_basis(rows: Iterable[int], ambient_dim: int = 2) -> tuple[int, ...]:
    basis: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= 1 << ambient_dim:
            raise AssertionError("CN7U-INV-01: GF(2) vector range")
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                for other in tuple(basis):
                    if other != pivot and ((basis[other] >> pivot) & 1):
                        basis[other] ^= value
                break
    return tuple(basis[p] for p in sorted(basis, reverse=True))


def stat(raw: dict) -> dict:
    value = int(raw["value"])
    if value not in (0, 1):
        raise AssertionError("CN7U-INV-02: nonbinary scalar")
    return {"left": list(xor_basis(raw["left"])), "right": list(xor_basis(raw["right"])), "value": value}


def geom(item: dict) -> tuple:
    return tuple(item["left"]), tuple(item["right"])


def witness(lower: Sequence[dict], upper: Sequence[dict]) -> list[list[int]] | None:
    m, n = len(lower), len(upper)
    live = {(0, 0)} if geom(lower[0]) == geom(upper[0]) and lower[0]["value"] <= upper[0]["value"] else set()
    prev: dict[tuple[int, int], tuple[int, int]] = {}
    for i in range(m):
        for j in range(n):
            if (i, j) not in live:
                continue
            for di, dj in STEPS:
                q = (i + di, j + dj)
                if q[0] < m and q[1] < n and q not in live:
                    if geom(lower[q[0]]) == geom(upper[q[1]]) and lower[q[0]]["value"] <= upper[q[1]]["value"]:
                        live.add(q)
                        prev[q] = (i, j)
    if (m - 1, n - 1) not in live:
        return None
    q = (m - 1, n - 1)
    path = [q]
    while q != (0, 0):
        q = prev[q]
        path.append(q)
    return [[i, j] for i, j in reversed(path)]


def source_generators(source: dict) -> list[dict]:
    output = []
    for item in source["quotient_frontier"]["classes"]:
        trajectory = [stat({**x, "value": 0}) for x in item["zero_envelope"]]
        if len(trajectory) != 4 or len({geom(x) for x in trajectory}) != 4:
            raise AssertionError("CN7U-INV-01: source generator geometry")
        output.append({"generator_id": item["class_id"], "trajectory": trajectory})
    output.sort(key=lambda x: x["generator_id"])
    if len(output) != 6:
        raise AssertionError("CN7U-INV-01: source generator count")
    return output


def reconstruct_entry(generator: dict, codes: Sequence[str]) -> tuple[list[dict], list[str]]:
    if len(codes) != 4:
        raise AssertionError("CN7U-INV-06: scalar assignment arity")
    out = []
    normalized = []
    for base, code in zip(generator["trajectory"], codes):
        if code not in CODES:
            raise AssertionError("CN7U-INV-05: unknown scalar pattern")
        pattern = CODES[code]
        run = []
        for value in pattern:
            if not run or run[-1] != value:
                run.append(value)
        if tuple(run) not in PATTERNS:
            raise AssertionError("CN7U-INV-05: compactification catalog")
        normalized.append("".join(map(str, run)))
        for value in run:
            item = copy.deepcopy(base)
            item["value"] = value
            out.append(item)
    return out, normalized


def expected_closure(generators: Sequence[dict]) -> list[dict]:
    entries = []
    for generator in generators:
        for codes in itertools.product(sorted(CODES), repeat=4):
            trajectory, normalized = reconstruct_entry(generator, codes)
            entries.append({
                "entry_id": f"{generator['generator_id']}:{'.'.join(normalized)}",
                "source_generator_id": generator["generator_id"],
                "scalar_pattern_codes": normalized,
                "trajectory_digest": digest(trajectory),
                "width": max(item["value"] for item in trajectory),
            })
    return sorted(entries, key=lambda x: x["entry_id"])


def verify(source_path: Path, artifact_path: Path) -> dict:
    if file_sha256(source_path) != SOURCE_SHA256:
        raise AssertionError("CN7U-INV-01: source bytes")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source.get("semantic_digest") != SOURCE_SEMANTIC:
        raise AssertionError("CN7U-INV-01: source semantic")
    observed = json.loads(artifact_path.read_text(encoding="utf-8"))
    if observed.get("schema") != SCHEMA:
        raise AssertionError("CN7U-INV-01: schema")
    unsigned = dict(observed)
    claimed = unsigned.pop("semantic_digest", None)
    if claimed != digest(unsigned):
        raise AssertionError("CN7U-INV-10: semantic digest")
    if observed.get("certificate_bytes") != len(artifact_path.read_bytes()):
        raise AssertionError("CN7U-INV-10: fixed point bytes")
    src = observed["source"]
    if src != {
        "parent_pr": 112,
        "parent_exact_head": PARENT_HEAD,
        "certificate_sha256": SOURCE_SHA256,
        "certificate_semantic_digest": SOURCE_SEMANTIC,
    }:
        raise AssertionError("CN7U-INV-01: source binding")

    generators = source_generators(source)
    if observed["input_generators"] != generators:
        raise AssertionError("CN7U-INV-02: generator inventory")

    expected_matrix = []
    for lower in generators:
        row = []
        for upper in generators:
            path = witness(lower["trajectory"], upper["trajectory"])
            row.append({"holds": path is not None, "witness": path})
        expected_matrix.append(row)
    pre = observed["preorder"]
    if pre["steps"] != [list(x) for x in STEPS] or pre["pair_count"] != 36:
        raise AssertionError("CN7U-INV-03: preorder domain")
    if pre["matrix"] != expected_matrix:
        raise AssertionError("CN7U-INV-03: 6x6 preorder matrix")
    relation_count = sum(int(cell["holds"]) for row in expected_matrix for cell in row)
    if pre["relation_count"] != relation_count:
        raise AssertionError("CN7U-INV-03: relation count")

    retained_ids: list[str] = []
    expected_removals = []
    for j, candidate in enumerate(generators):
        direct = None
        for rid in retained_ids:
            i = next(k for k, g in enumerate(generators) if g["generator_id"] == rid)
            if expected_matrix[i][j]["holds"]:
                direct = {"removed_generator_id": candidate["generator_id"], "retained_generator_id": rid, "witness": expected_matrix[i][j]["witness"]}
                break
        if direct is None:
            retained_ids.append(candidate["generator_id"])
        else:
            expected_removals.append(direct)
    if pre["retained_generator_ids"] != retained_ids or pre["direct_removals"] != expected_removals:
        raise AssertionError("CN7U-INV-04: direct minimization")
    if pre["transitive_removal_witnesses_used"] != 0:
        raise AssertionError("CN7U-INV-04: transitive removal used")
    for removal in pre["direct_removals"]:
        if not removal["witness"]:
            raise AssertionError("CN7U-INV-04: missing direct witness")

    catalog = observed["binary_typical_catalog"]
    if catalog != {
        "patterns": [list(x) for x in PATTERNS],
        "codes": sorted(CODES),
        "assignments_per_generator": 1296,
    }:
        raise AssertionError("CN7U-INV-05: scalar catalog")

    retained = [g for g in generators if g["generator_id"] in retained_ids]
    closure = expected_closure(retained)
    got = observed["reachable_closure"]
    if got["entry_count"] != len(closure) or got["entries_digest"] != digest(closure):
        raise AssertionError("CN7U-INV-06: closure replay")
    expected_per_generator = []
    for generator in retained:
        group = [entry for entry in closure if entry["source_generator_id"] == generator["generator_id"]]
        expected_per_generator.append({
            "generator_id": generator["generator_id"],
            "entry_count": len(group),
            "entries_digest": digest(group),
            "first_entry_id": group[0]["entry_id"],
            "last_entry_id": group[-1]["entry_id"],
        })
    if got["per_generator"] != expected_per_generator or got["full_entries_stored"] is not False or got["full_entries_replayed_by_verifier"] is not True:
        raise AssertionError("CN7U-INV-06: per-generator closure roots")
    if len({x["entry_id"] for x in closure}) != len(closure):
        raise AssertionError("CN7U-INV-07: closure uniqueness")

    second_generators = [g for g in retained if g["generator_id"] in {x["source_generator_id"] for x in closure}]
    second = expected_closure(second_generators)
    if second != closure or got["closure_of_closure_entry_count"] != len(second) or got["closure_of_closure_digest"] != digest(second) or got["idempotent"] is not True:
        raise AssertionError("CN7U-INV-08: idempotence")

    ledger = observed["work_ledger"]
    if ledger != {
        "gf2_generator_statistics_checked": 24,
        "preorder_pairs_replayed": 36,
        "direct_removal_witnesses_replayed": len(expected_removals),
        "scalar_assignments_replayed": 1296 * len(retained),
        "closure_entries_materialized": len(closure),
        "idempotence_entries_replayed": len(second),
    }:
        raise AssertionError("CN7U-INV-09: work ledger")
    if observed["invariant_vector"] != {f"CN7U-INV-{i:02d}": "PASS" for i in range(1, 11)}:
        raise AssertionError("CN7U-INV-10: invariant vector")
    strict = observed["strict_boundary"]
    if strict["corrected_node7_parent_up_k_complete"] is not False or strict["found_layout"] != "FORBIDDEN" or strict["no_layout_at_cap"] != "FORBIDDEN" or strict["p_vs_np"] != "OPEN":
        raise AssertionError("CN7U-INV-10: strict boundary")
    return observed


def reseal(value: dict) -> dict:
    value = copy.deepcopy(value)
    value["certificate_bytes"] = 0
    while True:
        unsigned = dict(value)
        unsigned.pop("semantic_digest", None)
        value["semantic_digest"] = digest(unsigned)
        size = len(canonical_json(value) + b"\n")
        if value["certificate_bytes"] == size:
            return value
        value["certificate_bytes"] = size


def tamper_tests(source_path: Path, artifact_path: Path) -> dict[str, str]:
    base = json.loads(artifact_path.read_text(encoding="utf-8"))
    attacks: list[tuple[str, str, Any]] = [
        ("source_head", "CN7U-INV-01", lambda x: x["source"].__setitem__("parent_exact_head", "0" * 40)),
        ("generator_delete", "CN7U-INV-02", lambda x: x["input_generators"].pop()),
        ("generator_geometry", "CN7U-INV-02", lambda x: x["input_generators"][0]["trajectory"][1].__setitem__("left", [1])),
        ("preorder_flip", "CN7U-INV-03", lambda x: x["preorder"]["matrix"][0][1].__setitem__("holds", True)),
        ("retained_delete", "CN7U-INV-04", lambda x: x["preorder"]["retained_generator_ids"].pop()),
        ("catalog_delete", "CN7U-INV-05", lambda x: x["binary_typical_catalog"]["codes"].pop()),
        ("closure_count", "CN7U-INV-06", lambda x: x["reachable_closure"].__setitem__("entry_count", 7775)),
        ("closure_root", "CN7U-INV-06", lambda x: x["reachable_closure"].__setitem__("entries_digest", "0" * 64)),
        ("idempotence_false", "CN7U-INV-08", lambda x: x["reachable_closure"].__setitem__("idempotent", False)),
        ("false_terminal", "CN7U-INV-10", lambda x: x["strict_boundary"].__setitem__("no_layout_at_cap", True)),
    ]
    outcomes = {}
    with tempfile.TemporaryDirectory() as directory:
        for name, expected, mutation in attacks:
            candidate = copy.deepcopy(base)
            mutation(candidate)
            candidate = reseal(candidate)
            path = Path(directory) / f"{name}.json"
            path.write_bytes(canonical_json(candidate) + b"\n")
            try:
                verify(source_path, path)
            except AssertionError as exc:
                message = str(exc)
                if expected not in message:
                    raise AssertionError(f"tamper {name} failed on wrong invariant: {message}")
                outcomes[name] = expected
            else:
                raise AssertionError(f"tamper accepted: {name}")
    if len(outcomes) != 10:
        raise AssertionError("CN7U-INV-10: tamper count")
    return outcomes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = verify(args.source, args.artifact)
    outcomes = tamper_tests(args.source, args.artifact) if args.tamper_self_test else {}
    print(json.dumps({
        "status": "PASS",
        "invariants": "10/10",
        "tamper_attacks_rejected": len(outcomes),
        "closure_entries": artifact["reachable_closure"]["entry_count"],
        "semantic_digest": artifact["semantic_digest"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
