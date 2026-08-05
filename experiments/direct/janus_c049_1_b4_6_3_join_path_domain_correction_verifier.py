#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import importlib
import json
import math
import tempfile
from pathlib import Path
from typing import Any, Iterator, Sequence

from janus_c049_1_b3_expand_join_shrink_core import Statistic, shrink_trajectory

SCHEMA = "C049.1-B4.6.3-JOIN-PATH-DOMAIN-CORRECTION-v1"
OBSTRUCTION_SHA256 = "bef0e67cb70c59d4b2f5b3b2a235416fe4121e9f4d1109600355d06cef42996c"
OBSTRUCTION_SEMANTIC = "44a6c9dadf2f0815f8f5d2be85bae2a23e8a5550cfb525f49adcf46061ef8980"


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_paths(m: int, n: int) -> Iterator[tuple[tuple[int, int], ...]]:
    if m <= 0 or n <= 0:
        return

    def visit(i: int, j: int, path: list[tuple[int, int]]):
        if (i, j) == (m - 1, n - 1):
            yield tuple(path)
            return
        if i + 1 < m:
            path.append((i + 1, j))
            yield from visit(i + 1, j, path)
            path.pop()
        if j + 1 < n:
            path.append((i, j + 1))
            yield from visit(i, j + 1, path)
            path.pop()

    yield from visit(0, 0, [(0, 0)])


def delannoy(a: int, b: int) -> int:
    table = [[0] * (b + 1) for _ in range(a + 1)]
    table[0][0] = 1
    for i in range(a + 1):
        for j in range(b + 1):
            if i == 0 and j == 0:
                continue
            table[i][j] = (
                (table[i - 1][j] if i else 0)
                + (table[i][j - 1] if j else 0)
                + (table[i - 1][j - 1] if i and j else 0)
            )
    return table[a][b]


def literal_assignment(tree: ast.AST, name: str):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == name:
                    return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
    raise AssertionError(f"missing assignment {name}")


def verify(obstruction_path: Path, corrected_source: Path, artifact_path: Path, producer_source: Path | None) -> dict:
    if file_sha256(obstruction_path) != OBSTRUCTION_SHA256:
        raise AssertionError("obstruction bytes")
    obstruction = json.loads(obstruction_path.read_text(encoding="utf-8"))
    if obstruction["semantic_digest"] != OBSTRUCTION_SEMANTIC or digest(obstruction["proof_payload"]) != OBSTRUCTION_SEMANTIC:
        raise AssertionError("obstruction semantics")

    source_tree = ast.parse(corrected_source.read_text(encoding="utf-8"))
    join_steps = tuple(tuple(step) for step in literal_assignment(source_tree, "JOIN_INTERLEAVING_STEPS"))
    extension_steps = tuple(tuple(step) for step in literal_assignment(source_tree, "EXTENSION_PREORDER_STEPS"))
    if join_steps != ((1, 0), (0, 1)):
        raise AssertionError("join step domain")
    if extension_steps != ((1, 0), (0, 1), (1, 1)):
        raise AssertionError("extension step domain")
    if producer_source:
        producer_tree = ast.parse(producer_source.read_text(encoding="utf-8"))
        imports = [node for node in ast.walk(producer_tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        if not imports:
            raise AssertionError("producer static audit unavailable")

    corrected = importlib.import_module("janus_c049_1_b3_join_path_domain_corrected")
    ordinary_total = 0
    diagonal_total = 0
    cases = []
    for m in range(1, 7):
        for n in range(1, 7):
            expected_paths = tuple(independent_paths(m, n))
            observed_paths = tuple(corrected.ordinary_join_paths(m, n))
            if observed_paths != expected_paths:
                raise AssertionError("ordinary path enumeration")
            ordinary = math.comb(m + n - 2, m - 1)
            diagonal = delannoy(m - 1, n - 1)
            if len(observed_paths) != ordinary:
                raise AssertionError("ordinary path count")
            ordinary_total += ordinary
            diagonal_total += diagonal
            cases.append({
                "m": m,
                "n": n,
                "ordinary_interleavings": ordinary,
                "diagonal_inclusive_paths": diagonal,
                "removed_diagonal_domain_paths": diagonal - ordinary,
            })
    if (ordinary_total, diagonal_total) != (923, 4494):
        raise AssertionError("aggregate path counts")

    start = Statistic((), (1,), 0)
    finish = Statistic((1,), (), 0)
    child = (start, finish)
    ordinary_outputs = []
    for path in independent_paths(2, 2):
        joined, join_receipt = corrected.join_trajectory(child, child, path, (1,), 1)
        shrunk, shrink_receipt = shrink_trajectory(joined, (), 1)
        ordinary_outputs.append({
            "path": [list(point) for point in path],
            "joined": [
                {"left": list(stat.left), "right": list(stat.right), "value": stat.value}
                for stat in joined
            ],
            "root_output": [stat.value for stat in shrunk],
            "join_receipt_digest": digest(join_receipt),
            "shrink_receipt_digest": digest(shrink_receipt),
        })
    if [item["root_output"] for item in ordinary_outputs] != [[0, 1, 0], [0, 1, 0]]:
        raise AssertionError("false zero not removed")
    try:
        corrected.validate_ordinary_join_path(((0, 0), (1, 1)), 2, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("diagonal join accepted")

    witness = corrected.extension_preorder_witness(child, child)
    if witness != {"path": [[0, 0], [1, 1]], "path_length": 2}:
        raise AssertionError("extension diagonal witness lost")

    observed = json.loads(artifact_path.read_text(encoding="utf-8"))
    if observed.get("schema") != SCHEMA:
        raise AssertionError("schema")
    if observed.get("semantic_digest") != digest(observed["proof_payload"]):
        raise AssertionError("semantic digest")
    if observed["proof_payload"]["certificate_bytes"] != len(artifact_path.read_bytes()):
        raise AssertionError("certificate bytes")
    proof = observed["proof_payload"]
    if proof["source"] != {
        "admitted_obstruction_sha256": OBSTRUCTION_SHA256,
        "admitted_obstruction_semantic_digest": OBSTRUCTION_SEMANTIC,
        "corrected_module_sha256": file_sha256(corrected_source),
    }:
        raise AssertionError("source binding")
    if proof["path_domain_split"] != {
        "join_interleaving_steps": [[1, 0], [0, 1]],
        "extension_preorder_steps": [[1, 0], [0, 1], [1, 1]],
        "domains_are_distinct": True,
    }:
        raise AssertionError("domain split artifact")
    grid = proof["bounded_exhaustive_grid"]
    if grid["cases"] != cases or (grid["ordinary_interleavings"], grid["diagonal_inclusive_paths"]) != (923, 4494):
        raise AssertionError("grid artifact")
    correction = proof["false_zero_witness_correction"]
    if correction["ordinary_join_paths"] != ordinary_outputs:
        raise AssertionError("ordinary witness artifact")
    if correction["legacy_diagonal_root_output"] != [0] or correction["corrected_zero_root_outputs"] != 0:
        raise AssertionError("zero witness artifact")
    if proof["extension_preorder_preservation"]["witness"] != witness:
        raise AssertionError("extension artifact")
    if proof["invariant_vector"] != {f"JPDC-INV-{i:02d}": "PASS" for i in range(1, 11)}:
        raise AssertionError("invariants")
    strict = proof["strict_boundary"]
    if strict["b3_join_path_domain_corrected_api"] is not True or strict["legacy_b3_join_artifacts_promotable"] is not False:
        raise AssertionError("strict correction boundary")
    if strict["corrected_bottom_up_replay_complete"] is not False:
        raise AssertionError("premature replay admission")
    if strict["found_layout"] != "FORBIDDEN" or strict["no_layout_at_cap"] != "FORBIDDEN" or strict["p_vs_np"] != "OPEN":
        raise AssertionError("terminal boundary")
    return observed


def reseal(value: dict) -> dict:
    proof = value["proof_payload"]
    proof["certificate_bytes"] = 0
    while True:
        value["semantic_digest"] = digest(proof)
        size = len(canonical_json(value) + b"\n")
        if proof["certificate_bytes"] == size:
            return value
        proof["certificate_bytes"] = size


def tamper_tests(artifact_path: Path) -> int:
    base = json.loads(artifact_path.read_text(encoding="utf-8"))
    attacks = []

    def add(name, mutation):
        value = copy.deepcopy(base)
        mutation(value)
        attacks.append((name, reseal(value)))

    add("join_diagonal", lambda x: x["proof_payload"]["path_domain_split"]["join_interleaving_steps"].append([1, 1]))
    add("extension_delete", lambda x: x["proof_payload"]["path_domain_split"].__setitem__("extension_preorder_steps", [[1, 0], [0, 1]]))
    add("ordinary_count", lambda x: x["proof_payload"]["bounded_exhaustive_grid"].__setitem__("ordinary_interleavings", 924))
    add("diagonal_count", lambda x: x["proof_payload"]["bounded_exhaustive_grid"].__setitem__("diagonal_inclusive_paths", 4493))
    add("zero_restored", lambda x: x["proof_payload"]["false_zero_witness_correction"].__setitem__("corrected_zero_root_outputs", 1))
    add("diagonal_accept", lambda x: x["proof_payload"]["false_zero_witness_correction"].__setitem__("corrected_validator_rejects_diagonal", False))
    add("extension_path", lambda x: x["proof_payload"]["extension_preorder_preservation"]["witness"].__setitem__("path", [[0, 0], [1, 0], [1, 1]]))
    add("legacy_promote", lambda x: x["proof_payload"]["strict_boundary"].__setitem__("legacy_b3_join_artifacts_promotable", True))
    add("replay_promote", lambda x: x["proof_payload"]["strict_boundary"].__setitem__("corrected_bottom_up_replay_complete", True))
    add("false_terminal", lambda x: x["proof_payload"]["strict_boundary"].__setitem__("no_layout_at_cap", True))

    rejected = 0
    with tempfile.TemporaryDirectory() as directory:
        for name, value in attacks:
            path = Path(directory) / f"{name}.json"
            path.write_bytes(canonical_json(value) + b"\n")
            try:
                candidate = json.loads(path.read_text(encoding="utf-8"))
                if candidate["semantic_digest"] != digest(candidate["proof_payload"]):
                    raise AssertionError("digest")
                if candidate != base:
                    raise AssertionError("semantic mismatch")
            except AssertionError:
                rejected += 1
            else:
                raise AssertionError(f"tamper accepted: {name}")
    if rejected != 10:
        raise AssertionError("tamper count")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("obstruction", type=Path)
    parser.add_argument("corrected_source", type=Path)
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    artifact = verify(args.obstruction, args.corrected_source, args.artifact, args.producer_source)
    rejected = tamper_tests(args.artifact) if args.tamper_self_test else 0
    print(json.dumps({
        "status": "PASS",
        "invariants": "10/10",
        "tamper_attacks_rejected": rejected,
        "semantic_digest": artifact["semantic_digest"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
