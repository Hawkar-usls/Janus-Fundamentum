#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

EXPECTED_SCHEMA = "C049.1-B4.6.3-NODE7-THIRTEEN-GENERATOR-UP-K-CLOSURE-v1"
EXPECTED_SOURCE_SCHEMA = "C049.1-B4.6.3-NODE7-PARENT-FRONTIER-STRUCTURAL-COMPRESSION-v1"
EXPECTED_SOURCE_SHA256 = "6a0748219d829434feeb5de2c5488e1fa3aeb1fab16ecbfee0c5629be90130a9"
EXPECTED_SOURCE_SEMANTIC_DIGEST = "ed6b59821aaef10ac6bdb6286a72ffcafd15e2bbd2619e0edffc7f711a2b1103"
EXPECTED_INPUT = 13
EXPECTED_RETAINED = 13
EXPECTED_REMOVALS = 0
EXPECTED_REACHABLE = 9108
EXPECTED_ARTIFACT_BYTES = 4010990
EXPECTED_ARTIFACT_SHA256 = "c085a3bee4e0c92a01eb22715390079f9858c5704ebcbf8534f9de196087d189"
EXPECTED_SEMANTIC_DIGEST = "23079901348590eb39d60d904d52dfd5004f8b287382a288ccbea688802b22f2"
EXPECTED_STREAM_DIGEST = "aac8623a3c8c13cf284b39de0f5966606f733dd0dc71a55d6fd4227abd49ef8e"
EXPECTED_ENTRIES_DIGEST = "269d5cd926d3be3df5641066a7986dfb1df049abab68b4202f6bc9a39e27a46e"
EXPECTED_REPOSITORY = "Hawkar-usls/Janus-Fundamentum"
EXPECTED_RENAMING_WITNESS = "2026-08-05T05:05:00+03:00"
PATTERNS = (
    (0,),
    (0, 1),
    (0, 1, 0),
    (1,),
    (1, 0),
    (1, 0, 1),
)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass(frozen=True, order=True)
class Stat:
    left: tuple[int, ...]
    right: tuple[int, ...]
    value: int


def rref(rows: Iterable[int], dimension: int) -> tuple[int, ...]:
    pivots: dict[int, int] = {}
    for raw in rows:
        value = int(raw)
        if value < 0 or value >= (1 << dimension):
            raise ValueError("row outside represented boundary")
        while value:
            pivot = value.bit_length() - 1
            old = pivots.get(pivot)
            if old is not None:
                value ^= old
                continue
            pivots[pivot] = value
            for other in tuple(pivots):
                if other != pivot and ((pivots[other] >> pivot) & 1):
                    pivots[other] ^= value
            break
    for pivot in sorted(pivots):
        row = pivots[pivot]
        for other in sorted(pivots, reverse=True):
            if other != pivot and ((pivots[other] >> pivot) & 1):
                pivots[other] ^= row
    return tuple(pivots[pivot] for pivot in sorted(pivots, reverse=True))


def included(big: Sequence[int], small: Sequence[int]) -> bool:
    for vector in small:
        residue = int(vector)
        for row in big:
            residue = min(residue, residue ^ int(row))
        if residue:
            return False
    return True


def compact(sequence: Sequence[Stat]) -> tuple[Stat, ...]:
    work = list(sequence)
    while True:
        for index in range(1, len(work)):
            if work[index - 1] == work[index]:
                del work[index]
                break
        else:
            removed = False
            for start in range(len(work)):
                for end in range(start + 2, len(work)):
                    if (work[start].left, work[start].right) != (
                        work[end].left,
                        work[end].right,
                    ):
                        continue
                    values = [item.value for item in work[start : end + 1]]
                    between = values[1:-1]
                    monotone_interval = (
                        values[0] <= values[-1]
                        and all(
                            values[0] <= value <= values[-1]
                            for value in between
                        )
                    ) or (
                        values[0] >= values[-1]
                        and all(
                            values[0] >= value >= values[-1]
                            for value in between
                        )
                    if monotone_interval:
                        del work[start + 1 : end]
                        removed = True
                        break
                if removed:
                    break
            if not removed:
                return tuple(work)
            continue
        continue


def parse(raw: Sequence[dict]) -> tuple[Stat, ...]:
    if not raw:
        raise ValueError("empty trajectory")
    result = tuple(
        Stat(
            rref(item["left"], 2),
            rref(item["right"], 2),
            int(item["value"]),
        )
        for item in raw
    )
    if any(item.value < 0 for item in result):
        raise ValueError("negative value")
    if result[0].right != result[-1].left:
        raise ValueError("endpoint mismatch")
    for first, second in zip(result, result[1:]):
        if not included(second.left, first.left) or not included(
            first.right, second.right
        ):
            raise ValueError("trajectory monotonicity mismatch")
    if compact(result) != result:
        raise ValueError("trajectory not compact")
    return result


def emit(gamma: Sequence[Stat]) -> list[dict]:
    return [
        {
            "left": list(item.left),
            "right": list(item.right),
            "value": item.value,
        }
        for item in gamma
    ]


def key(gamma: Sequence[Stat]) -> tuple:
    return tuple((item.left, item.right, item.value) for item in gamma)


def signature(gamma: Sequence[Stat]) -> tuple:
    symbols = []
    for item in gamma:
        symbol = (item.left, item.right)
        if not symbols or symbols[-1] != symbol:
            symbols.append(symbol)
    return tuple(symbols)


def leq(lower: Stat, upper: Stat) -> bool:
    return (
        lower.left == upper.left
        and lower.right == upper.right
        and lower.value <= upper.value
    )


def independent_relation(
    lower: Sequence[Stat], upper: Sequence[Stat]
) -> dict | None:
    reachable: dict[tuple[int, int], tuple[int, int] | None] = {}
    for diagonal in range(len(lower) + len(upper) - 1):
        for i in range(len(lower)):
            j = diagonal - i
            if not (0 <= j < len(upper)) or not leq(lower[i], upper[j]):
                continue
            if (i, j) == (0, 0):
                reachable[(i, j)] = None
                continue
            candidates = ((i - 1, j - 1), (i - 1, j), (i, j - 1))
            predecessor = next(
                (cell for cell in candidates if cell in reachable), None
            )
            if predecessor is not None:
                reachable[(i, j)] = predecessor
    terminal = (len(lower) - 1, len(upper) - 1)
    if terminal not in reachable:
        return None
    path = []
    cursor: tuple[int, int] | None = terminal
    while cursor is not None:
        path.append(cursor)
        cursor = reachable[cursor]
    path.reverse()
    return {"path": [[i, j] for i, j in path], "path_length": len(path)}


def validate_claimed_witness(
    lower: Sequence[Stat], upper: Sequence[Stat], witness: dict
) -> None:
    cells = witness.get("path")
    if not isinstance(cells, list) or not cells:
        raise AssertionError("missing witness path")
    parsed = []
    for cell in cells:
        if not isinstance(cell, list) or len(cell) != 2:
            raise AssertionError("malformed witness cell")
        i, j = cell
        if not isinstance(i, int) or not isinstance(j, int):
            raise AssertionError("noninteger witness cell")
        if not (0 <= i < len(lower) and 0 <= j < len(upper)):
            raise AssertionError("witness cell outside trajectory")
        parsed.append((i, j))
    if parsed[0] != (0, 0) or parsed[-1] != (
        len(lower) - 1,
        len(upper) - 1,
    ):
        raise AssertionError("witness endpoint mismatch")
    if witness.get("path_length") != len(parsed):
        raise AssertionError("witness length mismatch")
    for first, second in zip(parsed, parsed[1:]):
        if (second[0] - first[0], second[1] - first[1]) not in (
            (1, 0),
            (0, 1),
            (1, 1),
        ):
            raise AssertionError("invalid witness step")
    if any(not leq(lower[i], upper[j]) for i, j in parsed):
        raise AssertionError("witness inequality mismatch")


def exhaustive_pattern_catalog() -> tuple[tuple[int, ...], ...]:
    found = set()
    for length in range(1, 16):
        for values in itertools.product((0, 1), repeat=length):
            scalar = tuple(Stat((), (), value) for value in values)
            if compact(scalar) == scalar:
                found.add(tuple(values))
    result = tuple(sorted(found))
    if result != PATTERNS:
        raise AssertionError("independent scalar catalog drift")
    return result


def reconstruct_source(source: dict) -> list[dict]:
    classes = source["quotient_frontier"]["classes"]
    records = []
    for item in classes:
        if digest(item["zero_envelope"]) != item["zero_envelope_digest"]:
            raise AssertionError("source zero envelope digest mismatch")
        gamma = parse(item["zero_envelope"])
        if any(stat.value != 0 for stat in gamma):
            raise AssertionError("source class is not a zero envelope")
        records.append({"class_id": item["class_id"], "gamma": gamma})
    records.sort(key=lambda item: (key(item["gamma"]), item["class_id"]))
    if len(records) != EXPECTED_INPUT or len(
        {key(item["gamma"]) for item in records}
    ) != EXPECTED_INPUT:
        raise AssertionError("source input family cardinality drift")
    if len({signature(item["gamma"]) for item in records}) != EXPECTED_INPUT:
        raise AssertionError("source signatures are not unique")
    return records


def reconstruct_closure(records: Sequence[dict]) -> tuple[list[dict], dict]:
    relation = {}
    for i, lower in enumerate(records):
        for j, upper in enumerate(records):
            witness = independent_relation(lower["gamma"], upper["gamma"])
            if witness is not None:
                relation[(i, j)] = witness
    summary = {
        "ordered_pair_tests": len(records) ** 2,
        "relation_edges": len(relation),
        "self_relation_edges": sum(
            (i, i) in relation for i in range(len(records))
        ),
        "cross_relation_edges": sum(i != j for i, j in relation),
    }
    if summary != {
        "ordered_pair_tests": 169,
        "relation_edges": 13,
        "self_relation_edges": 13,
        "cross_relation_edges": 0,
    }:
        raise AssertionError("independent relation matrix drift")
    patterns = exhaustive_pattern_catalog()
    entries = []
    seen = set()
    for source_index, record in enumerate(records):
        sig = signature(record["gamma"])
        if len(sig) != len(record["gamma"]) or len(set(sig)) != len(sig):
            raise AssertionError(
                "source signature is not a distinct zero skeleton"
            )
        for assignment in itertools.product(patterns, repeat=len(sig)):
            candidate = []
            for (left, right), values in zip(sig, assignment):
                candidate.extend(
                    Stat(left, right, value) for value in values
                )
            gamma = tuple(candidate)
            if compact(gamma) != gamma:
                raise AssertionError("independent candidate noncompact")
            if key(gamma) in seen:
                raise AssertionError("independent candidate duplicate")
            seen.add(key(gamma))
            witness = independent_relation(record["gamma"], gamma)
            if witness is None:
                raise AssertionError("independent direct witness missing")
            entries.append(
                {
                    "trajectory": emit(gamma),
                    "source_generator_index": source_index,
                    "source_class_id": record["class_id"],
                    "witness": witness,
                }
            )
    entries.sort(key=lambda item: canonical_json(item["trajectory"]))
    if len(entries) != EXPECTED_REACHABLE:
        raise AssertionError("independent reachable count drift")
    return entries, summary


def stream_digest(entries: Sequence[dict]) -> str:
    hasher = hashlib.sha256()
    for item in entries:
        hasher.update(canonical_json(item["trajectory"]))
        hasher.update(b"\n")
    return hasher.hexdigest()


def static_source_check(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imported = set()
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
        elif isinstance(node, ast.Call):
            target = node.func
            if isinstance(target, ast.Name):
                called.add(target.id)
            elif isinstance(target, ast.Attribute):
                called.add(target.attr)
    if any("verifier" in name for name in imported):
        raise AssertionError("producer imports verifier")
    banned = {"enumerate_compact_trajectories", "up_k_closure"}
    if called & banned:
        raise AssertionError("producer called global-universe closure")
    print("STATIC_NO_GLOBAL_COMPACT_UNIVERSE_ENUMERATION = PASS")


def verify(
    source_path: Path,
    artifact_value: dict,
    producer_source: Path | None = None,
) -> dict:
    if file_sha256(source_path) != EXPECTED_SOURCE_SHA256:
        raise AssertionError("source artifact byte digest drift")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if (
        source.get("schema") != EXPECTED_SOURCE_SCHEMA
        or source.get("semantic_digest") != EXPECTED_SOURCE_SEMANTIC_DIGEST
    ):
        raise AssertionError("source artifact identity drift")
    if artifact_value.get("schema") != EXPECTED_SCHEMA:
        raise AssertionError("closure schema drift")
    identity = artifact_value.get("repository_identity", {})
    if identity.get("canonical_repository") != EXPECTED_REPOSITORY:
        raise AssertionError("canonical repository identity drift")
    witness = identity.get("renaming_witness", {})
    if (
        witness.get("observed_local_datetime") != EXPECTED_RENAMING_WITNESS
        or witness.get("role") != "NON_PROOF_PROVENANCE"
    ):
        raise AssertionError("renaming provenance drift")
    proof = artifact_value.get("proof_payload")
    if (
        not isinstance(proof, dict)
        or artifact_value.get("semantic_digest_scope") != "proof_payload"
    ):
        raise AssertionError("semantic scope drift")
    if digest(proof) != artifact_value.get("semantic_digest"):
        raise AssertionError("semantic digest mismatch")
    source_claim = proof["source"]
    if (
        source_claim["node7_frontier_artifact_sha256"]
        != EXPECTED_SOURCE_SHA256
        or source_claim["node7_frontier_semantic_digest"]
        != EXPECTED_SOURCE_SEMANTIC_DIGEST
    ):
        raise AssertionError("proof source binding mismatch")

    records = reconstruct_source(source)
    expected_input = [emit(item["gamma"]) for item in records]
    if (
        proof["input_generator_count"] != EXPECTED_INPUT
        or proof["input_generators"] != expected_input
    ):
        raise AssertionError("canonical input generator replay mismatch")
    if proof["input_generator_family_digest"] != digest(expected_input):
        raise AssertionError("input generator family digest mismatch")

    entries, relation_summary = reconstruct_closure(records)
    minimization = proof["preorder_minimization"]
    if minimization["relation_summary"] != relation_summary:
        raise AssertionError("relation summary mismatch")
    if (
        minimization["retained_generator_count"] != EXPECTED_RETAINED
        or minimization["removal_count"] != EXPECTED_REMOVALS
        or minimization["removals"] != []
    ):
        raise AssertionError("minimization cardinality mismatch")
    if (
        minimization["every_removal_directly_witnessed"] is not True
        or minimization["zero_removal_case_explicit"] is not True
    ):
        raise AssertionError("zero-removal contract missing")
    if (
        proof["retained_generators"] != expected_input
        or proof["retained_generator_count"] != EXPECTED_RETAINED
    ):
        raise AssertionError("retained family mismatch")
    if proof["retained_class_ids"] != [
        item["class_id"] for item in records
    ]:
        raise AssertionError("retained class provenance mismatch")

    closure = proof["exact_reachable_closure"]
    if tuple(
        tuple(item) for item in closure["binary_typical_run_patterns"]
    ) != PATTERNS:
        raise AssertionError("binary typical run pattern catalog mismatch")
    if closure["binary_typical_run_pattern_count"] != len(PATTERNS):
        raise AssertionError("binary typical run pattern count mismatch")
    if (
        closure["complete_reachable_catalog_size"] != EXPECTED_REACHABLE
        or closure["reachable_entries"] != entries
    ):
        raise AssertionError("reachable catalog replay mismatch")
    if (
        closure["reachable_entries_digest"] != digest(entries)
        or closure["reachable_entries_digest"] != EXPECTED_ENTRIES_DIGEST
    ):
        raise AssertionError("reachable entry digest mismatch")
    if (
        closure["complete_reachable_catalog_stream_sha256"]
        != stream_digest(entries)
        or closure["complete_reachable_catalog_stream_sha256"]
        != EXPECTED_STREAM_DIGEST
    ):
        raise AssertionError("reachable stream digest mismatch")
    if closure["global_compact_universe_enumerated"] is not False:
        raise AssertionError("global universe enumeration was enabled")
    for item in closure["reachable_entries"]:
        source_record = records[item["source_generator_index"]]
        if source_record["class_id"] != item["source_class_id"]:
            raise AssertionError("entry source class mismatch")
        validate_claimed_witness(
            source_record["gamma"],
            parse(item["trajectory"]),
            item["witness"],
        )

    invariants = proof["invariant_vector"]
    if (
        len(invariants) != 10
        or set(invariants.values()) != {"PASS"}
        or proof["admit"] is not True
    ):
        raise AssertionError("admission invariant vector not green")
    strict = proof["strict_boundary"]
    required_true = (
        "node7_parent_generator_frontier_complete",
        "node7_parent_refinement_complete",
        "node7_parent_up_k_complete",
    )
    if any(strict[name] is not True for name in required_true):
        raise AssertionError("node-7 completion boundary drift")
    required_false = (
        "node7_integrated_into_bottom_up_executor",
        "node8_parent_refinement_started",
        "negative_root_reached",
        "terminal_completeness_proved",
        "found_layout_enabled",
        "no_layout_at_cap_enabled",
    )
    if any(strict[name] is not False for name in required_false):
        raise AssertionError("global strict boundary overclaim")
    if (
        strict["current_global_terminal"]
        != "OPEN_TRAJECTORY_ENGINE_INCOMPLETE"
        or strict["p_vs_np"] != "OPEN"
    ):
        raise AssertionError("global terminal drift")
    if producer_source is not None:
        static_source_check(producer_source)
    return {
        "input_generators": len(records),
        "retained_generators": EXPECTED_RETAINED,
        "removals": EXPECTED_REMOVALS,
        "reachable_entries": len(entries),
    }


def resign(value: dict) -> dict:
    out = copy.deepcopy(value)
    out["semantic_digest"] = digest(out["proof_payload"])
    return out


def tamper_self_test(artifact: dict) -> int:
    canonical_proof = copy.deepcopy(artifact["proof_payload"])
    canonical_identity = copy.deepcopy(artifact["repository_identity"])

    def quick_verify(value: dict) -> None:
        if value.get("schema") != EXPECTED_SCHEMA:
            raise AssertionError("schema mutation")
        if value.get("repository_identity") != canonical_identity:
            raise AssertionError("repository identity mutation")
        proof = value.get("proof_payload")
        if not isinstance(proof, dict):
            raise AssertionError("proof payload removed")
        if digest(proof) != value.get("semantic_digest"):
            raise AssertionError("semantic digest mismatch")
        if proof != canonical_proof:
            raise AssertionError(
                "proof payload differs from independently replayed canon"
            )

    def mutate_source_binding(value: dict) -> None:
        value["proof_payload"]["source"][
            "node7_frontier_artifact_sha256"
        ] = "0" * 64

    def mutate_input_generator(value: dict) -> None:
        value["proof_payload"]["input_generators"][0][0]["value"] = 1
        value["proof_payload"]["input_generator_family_digest"] = digest(
            value["proof_payload"]["input_generators"]
        )

    def delete_retained(value: dict) -> None:
        value["proof_payload"]["retained_generators"].pop()
        value["proof_payload"]["retained_generator_count"] -= 1

    def inject_closure_only_removal(value: dict) -> None:
        minimization = value["proof_payload"]["preorder_minimization"]
        minimization["removals"] = [{"reason": "CLOSURE_ONLY"}]
        minimization["removal_count"] = 1
        minimization["zero_removal_case_explicit"] = False

    def delete_reachable_entry(value: dict) -> None:
        closure = value["proof_payload"]["exact_reachable_closure"]
        closure["reachable_entries"].pop()
        closure["complete_reachable_catalog_size"] -= 1

    def mutate_source_class(value: dict) -> None:
        value["proof_payload"]["exact_reachable_closure"][
            "reachable_entries"
        ][0]["source_class_id"] = "FAKE_CLASS"

    def mutate_direct_witness(value: dict) -> None:
        value["proof_payload"]["exact_reachable_closure"][
            "reachable_entries"
        ][0]["witness"]["path"][0] = [0, 1]

    def reorder_reachable_entries(value: dict) -> None:
        closure = value["proof_payload"]["exact_reachable_closure"]
        entries = closure["reachable_entries"]
        entries[0], entries[1] = entries[1], entries[0]
        closure["reachable_entries_digest"] = digest(entries)

    def mutate_pattern_catalog(value: dict) -> None:
        value["proof_payload"]["exact_reachable_closure"][
            "binary_typical_run_patterns"
        ][0] = [1, 1]

    def overclaim_root(value: dict) -> None:
        value["proof_payload"]["strict_boundary"][
            "negative_root_reached"
        ] = True

    mutations = (
        mutate_source_binding,
        mutate_input_generator,
        delete_retained,
        inject_closure_only_removal,
        delete_reachable_entry,
        mutate_source_class,
        mutate_direct_witness,
        reorder_reachable_entries,
        mutate_pattern_catalog,
        overclaim_root,
    )
    rejected = 0
    for mutation in mutations:
        tampered = copy.deepcopy(artifact)
        mutation(tampered)
        tampered = resign(tampered)
        try:
            quick_verify(tampered)
        except Exception:
            rejected += 1
        else:
            raise AssertionError(
                f"tamper attack was accepted: {mutation.__name__}"
            )
        del tampered
    if rejected != len(mutations):
        raise AssertionError("tamper rejection count drift")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_artifact", type=Path)
    parser.add_argument("closure_artifact", type=Path)
    parser.add_argument("--producer-source", type=Path)
    parser.add_argument("--tamper-self-test", action="store_true")
    args = parser.parse_args()
    raw = args.closure_artifact.read_bytes()
    if (
        len(raw) != EXPECTED_ARTIFACT_BYTES
        or hashlib.sha256(raw).hexdigest() != EXPECTED_ARTIFACT_SHA256
    ):
        raise AssertionError("closure artifact byte identity drift")
    artifact = json.loads(raw)
    if artifact.get("semantic_digest") != EXPECTED_SEMANTIC_DIGEST:
        raise AssertionError("closure semantic digest drift")
    summary = verify(
        args.source_artifact, artifact, args.producer_source
    )
    rejected = tamper_self_test(artifact) if args.tamper_self_test else 0
    print("JANUS_C049_1_B4_6_3_NODE7_UP_K_CLOSURE_VERIFIER = PASS")
    print("INVARIANTS = 10/10")
    print("INPUT_GENERATORS =", summary["input_generators"])
    print("RETAINED_GENERATORS =", summary["retained_generators"])
    print("DIRECT_REMOVALS =", summary["removals"])
    print("REACHABLE_ENTRIES =", summary["reachable_entries"])
    print("ADMIT_NODE7_UP_K_CLOSURE = TRUE")
    if args.tamper_self_test:
        print("TAMPER_ATTACKS_REJECTED =", f"{rejected}/{rejected}")


if __name__ == "__main__":
    main()
