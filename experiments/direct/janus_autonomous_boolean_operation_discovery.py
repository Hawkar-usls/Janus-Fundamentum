#!/usr/bin/env python3
"""JANUS autonomous Boolean operation discovery.

Input: finite extensional Boolean relations only.
No family labels, algebra names, or preferred operation tables are accepted.

For every Boolean operation of arity 1..max_arity, enumerate its full truth
table and test exact preservation of every supplied relation.  The output is the
arity-bounded polymorphism fragment, together with operation identities derived
from the truth table itself and an explicit work ledger.

This is a bounded-domain / bounded-arity discovery experiment.  Relation
preservation is exact, but its cost is polynomial only in the extensional
relation size supplied to this module; constructing extensional relations from
wide CNF scopes can itself cost 2^w.  Therefore this file is not an
arbitrary-CNF polynomial SAT algorithm.  P_VS_NP remains OPEN.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import permutations, product
import json
from typing import Iterable, Sequence

BitTuple = tuple[int, ...]
Relation = tuple[BitTuple, ...]
OperationTable = tuple[int, ...]


def canonical_relation(rows: Iterable[Iterable[int]]) -> Relation:
    clean = []
    width = None
    for row in rows:
        item = tuple(int(bit) for bit in row)
        if any(bit not in (0, 1) for bit in item):
            raise ValueError("NON_BOOLEAN_RELATION")
        if width is None:
            width = len(item)
        if len(item) != width:
            raise ValueError("NON_RECTANGULAR_RELATION")
        clean.append(item)
    if width is None or width == 0:
        raise ValueError("EMPTY_OR_ZERO_WIDTH_RELATION")
    return tuple(sorted(set(clean)))


def canonical_language(relations: Iterable[Iterable[Iterable[int]]]) -> tuple[Relation, ...]:
    out = tuple(canonical_relation(relation) for relation in relations)
    if not out:
        raise ValueError("EMPTY_LANGUAGE")
    return tuple(sorted(out, key=lambda relation: (len(relation[0]), len(relation), relation)))


def fingerprint_language(relations: Sequence[Relation]) -> str:
    payload = json.dumps(relations, separators=(",", ":")).encode("ascii")
    return sha256(payload).hexdigest()


def operation_value(table: OperationTable, args: Sequence[int]) -> int:
    index = 0
    for bit in args:
        index = (index << 1) | int(bit)
    return table[index]


def table_from_mask(arity: int, mask: int) -> OperationTable:
    size = 1 << arity
    if mask < 0 or mask >= (1 << size):
        raise ValueError("OPERATION_MASK_OUT_OF_RANGE")
    return tuple((mask >> (size - 1 - index)) & 1 for index in range(size))


def all_operation_tables(arity: int):
    if arity < 1:
        raise ValueError("ARITY_MUST_BE_POSITIVE")
    size = 1 << arity
    for mask in range(1 << size):
        yield table_from_mask(arity, mask)


def projection_index(arity: int, table: OperationTable) -> int | None:
    for argument in range(arity):
        expected = []
        for index in range(1 << arity):
            shift = arity - 1 - argument
            expected.append((index >> shift) & 1)
        if tuple(expected) == table:
            return argument
    return None


def constant_output(table: OperationTable) -> int | None:
    values = set(table)
    if len(values) == 1:
        return next(iter(values))
    return None


def preserves_relation(
    table: OperationTable,
    arity: int,
    relation: Relation,
    ledger: dict[str, int],
) -> bool:
    allowed = set(relation)
    width = len(relation[0])
    for inputs in product(relation, repeat=arity):
        ledger["tuple_combinations_tested"] += 1
        output = tuple(
            operation_value(table, tuple(row[column] for row in inputs))
            for column in range(width)
        )
        ledger["coordinate_operation_evaluations"] += width
        ledger["relation_membership_checks"] += 1
        if output not in allowed:
            return False
    return True


def _universal_pattern_identity(
    table: OperationTable,
    arity: int,
    pattern: tuple[int, ...],
    target_symbol: int,
) -> bool:
    symbol_count = max(pattern + (target_symbol,)) + 1
    for assignment in product((0, 1), repeat=symbol_count):
        args = tuple(assignment[symbol] for symbol in pattern)
        if operation_value(table, args) != assignment[target_symbol]:
            return False
    return True


def derive_identity_profile(arity: int, table: OperationTable) -> dict:
    profile: dict[str, object] = {
        "projection_index": projection_index(arity, table),
        "constant_output": constant_output(table),
        "idempotent": all(
            operation_value(table, (bit,) * arity) == bit for bit in (0, 1)
        ),
        "argument_permutation_symmetries": [],
        "projection_equations": [],
    }

    for permutation in permutations(range(arity)):
        symmetric = True
        for args in product((0, 1), repeat=arity):
            permuted = tuple(args[index] for index in permutation)
            if operation_value(table, args) != operation_value(table, permuted):
                symmetric = False
                break
        if symmetric:
            profile["argument_permutation_symmetries"].append(list(permutation))

    symbol_count = min(3, max(2, arity))
    symbols = tuple(range(symbol_count))
    for pattern in product(symbols, repeat=arity):
        for target in symbols:
            if _universal_pattern_identity(table, arity, pattern, target):
                profile["projection_equations"].append(
                    {"pattern": list(pattern), "equals_symbol": target}
                )

    if arity == 2:
        profile["commutative"] = all(
            operation_value(table, (x, y)) == operation_value(table, (y, x))
            for x, y in product((0, 1), repeat=2)
        )
        profile["associative"] = all(
            operation_value(table, (operation_value(table, (x, y)), z))
            == operation_value(table, (x, operation_value(table, (y, z))))
            for x, y, z in product((0, 1), repeat=3)
        )
    if arity == 3:
        profile["totally_symmetric"] = len(
            profile["argument_permutation_symmetries"]
        ) == 6
    return profile


def discover(relations, max_arity: int = 3) -> dict:
    if max_arity < 1 or max_arity > 3:
        raise ValueError("THIS_GATE_FREEZES_MAX_ARITY_IN_1_TO_3")
    language = canonical_language(relations)
    ledger = {
        "operation_candidates": 0,
        "relation_preservation_attempts": 0,
        "tuple_combinations_tested": 0,
        "coordinate_operation_evaluations": 0,
        "relation_membership_checks": 0,
        "preserving_operations": 0,
    }
    discovered = []
    by_arity = {}

    for arity in range(1, max_arity + 1):
        records = []
        for table in all_operation_tables(arity):
            ledger["operation_candidates"] += 1
            ok = True
            for relation in language:
                ledger["relation_preservation_attempts"] += 1
                if not preserves_relation(table, arity, relation, ledger):
                    ok = False
                    break
            if not ok:
                continue
            ledger["preserving_operations"] += 1
            record = {
                "arity": arity,
                "table": list(table),
                "table_bits": "".join(str(bit) for bit in table),
                "identity_profile": derive_identity_profile(arity, table),
            }
            records.append(record)
            discovered.append(record)
        by_arity[str(arity)] = records

    nonprojection = [
        record
        for record in discovered
        if record["identity_profile"]["projection_index"] is None
    ]
    return {
        "schema": "JANUS/C025/AUTONOMOUS-BOOLEAN-OPERATION-DISCOVERY/v2",
        "source_fingerprint": fingerprint_language(language),
        "domain": [0, 1],
        "max_operation_arity": max_arity,
        "relation_count": len(language),
        "relations": [[list(row) for row in relation] for relation in language],
        "discovered_operations_by_arity": by_arity,
        "preserving_operation_count": len(discovered),
        "nonprojection_operation_count": len(nonprojection),
        "nonprojection_operations": nonprojection,
        "ledger": ledger,
        "admission_semantics": "EXACT_RELATION_PRESERVATION_ONLY",
        "family_label_used": False,
        "preselected_algebra_name_used": False,
        "heuristic_promotion_used": False,
        "P_VS_NP": "OPEN",
    }


def verify_discovery(relations, report: dict) -> bool:
    try:
        language = canonical_language(relations)
        if report.get("source_fingerprint") != fingerprint_language(language):
            return False
        max_arity = int(report["max_operation_arity"])
        rerun = discover(language, max_arity=max_arity)
        keys = (
            "source_fingerprint",
            "discovered_operations_by_arity",
            "preserving_operation_count",
            "nonprojection_operation_count",
            "nonprojection_operations",
            "admission_semantics",
        )
        return all(report.get(key) == rerun.get(key) for key in keys)
    except (KeyError, TypeError, ValueError):
        return False


def main() -> int:
    # Deliberately no embedded named family or named operation examples.
    print(json.dumps({
        "schema": "JANUS/C025/AUTONOMOUS-BOOLEAN-OPERATION-DISCOVERY/v2",
        "input": "FINITE_EXTENSIONAL_BOOLEAN_RELATIONS",
        "operation_space": "ALL_TRUTH_TABLES_ARITY_1_TO_3",
        "admission": "EXACT_PRESERVATION",
        "P_VS_NP": "OPEN",
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
