#!/usr/bin/env python3
"""C023 JANUS Boolean Polymorphism Gate — adversarial audit entry."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any
from janus_c023_primitives import canonical_cnf, satisfies_cnf
from janus_c023_polymorphism_core import *
from janus_c023_polymorphism_dispatch import *
from janus_c023_polymorphism_fixtures import *

DEFAULT_SEED = 9379992
CANONICAL_SEED_SHA256 = "44e21fdc9d37fda98e2e73b0c9eb268bd04cdca9d84d0519e4f1166be22b46fc"

# ---------------------------------------------------------------------------
# Audits
# ---------------------------------------------------------------------------

def exhaustive_ternary_relation_audit() -> dict[str, Any]:
    tuples = all_tuples(3)
    counts = Counter()
    signature_counts = Counter()
    reconstruction_checks = Counter()
    failures = []

    for mask in range(1 << len(tuples)):
        relation = Relation(
            f"R3_{mask:02x}",
            3,
            frozenset(tuples[i] for i in range(len(tuples)) if (mask >> i) & 1),
        )
        fp = fingerprint(relation)
        signature_counts[",".join(sorted(fp)) or "NONE"] += 1
        for op in OPS:
            if op in fp:
                counts[op] += 1

        try:
            if "AND" in fp:
                compile_horn_relation(relation)
                reconstruction_checks["AND"] += 1
            if "OR" in fp:
                compile_dual_horn_relation(relation)
                reconstruction_checks["OR"] += 1
            if "MAJ" in fp:
                compile_bijunctive_relation(relation)
                reconstruction_checks["MAJ"] += 1
            if "XOR3" in fp:
                compile_affine_relation(relation)
                reconstruction_checks["XOR3"] += 1
        except AssertionError as exc:
            failures.append({"relation": relation.name, "error": str(exc)})

    return {
        "relations": 256,
        "preservation_counts": dict(counts),
        "reconstruction_checks": dict(reconstruction_checks),
        "distinct_signatures": len(signature_counts),
        "top_signatures": signature_counts.most_common(20),
        "failures": failures,
    }


def random_relation_pool(operation: str) -> list[Relation]:
    tuples = all_tuples(3)
    pool = []
    for mask in range(1, 1 << len(tuples)):
        relation = Relation(
            f"P_{operation}_{mask:02x}",
            3,
            frozenset(tuples[i] for i in range(len(tuples)) if (mask >> i) & 1),
        )
        fp = fingerprint(relation)
        if operation in fp:
            pool.append(relation)
    return pool


def random_tractable_fuzz(
    rng: random.Random,
    cases_per_operation: int = 50,
) -> dict[str, Any]:
    mismatches = 0
    false_accepts = 0
    open_count = 0
    target_counts = Counter()
    checks = 0

    for operation in ("AND", "OR", "MAJ", "XOR3"):
        pool = random_relation_pool(operation)
        for _ in range(cases_per_operation):
            n = rng.randint(3, 7)
            constraints = []
            for _ in range(rng.randint(n, 3 * n)):
                relation = rng.choice(pool)
                scope = tuple(rng.sample(range(1, n + 1), 3))
                constraints.append(Constraint(relation, scope))

            result = dispatch_instance(constraints)
            truth, witness, brute_checks = brute_force_instance(constraints)
            checks += brute_checks
            if result.status != "EXACT":
                open_count += 1
                continue
            target_counts.update(result.component_targets)
            if result.sat != truth:
                mismatches += 1
            if result.sat and (
                result.assignment is None
                or not instance_satisfied(constraints, result.assignment)
            ):
                false_accepts += 1

    return {
        "cases": 4 * cases_per_operation,
        "mismatches": mismatches,
        "false_accepts": false_accepts,
        "open": open_count,
        "dispatch_targets": dict(target_counts),
        "bruteforce_assignments_checked": checks,
    }


def component_rescue_audit(rng: random.Random, cases: int = 100) -> dict[str, Any]:
    mismatches = 0
    opens = 0
    target_counts = Counter()

    for _ in range(cases):
        constraints = []
        for _ in range(rng.randint(2, 6)):
            scope = tuple(rng.sample(range(1, 7), 3))
            constraints.append(Constraint(NAND3, scope))
        offset = 10
        for _ in range(rng.randint(2, 6)):
            a, b = rng.sample(range(offset + 1, offset + 7), 2)
            constraints.append(Constraint(NEQ2, (a, b)))

        global_common = set(OPS)
        for constraint in constraints:
            global_common &= set(fingerprint(constraint.relation))

        result = dispatch_instance(constraints)
        truth, _, _ = brute_force_instance(constraints)
        if result.status != "EXACT":
            opens += 1
        elif result.sat != truth:
            mismatches += 1
        target_counts.update(result.component_targets)

        if global_common:
            raise AssertionError("test requires empty global fingerprint")

    return {
        "cases": cases,
        "global_common_fingerprint": [],
        "component_dispatch_mismatches": mismatches,
        "component_dispatch_open": opens,
        "targets": dict(target_counts),
        "result": (
            "Disconnected components need not share one global polymorphism; "
            "HRain-style decomposition allows separate exact dispatch."
        ),
    }


def switch_backdoor_audit(max_blocks: int = 5) -> dict[str, Any]:
    single = [Constraint(SWITCH4, (1, 2, 3, 4))]
    single_fp = sorted(fingerprint(SWITCH4))
    single_min = minimum_strong_backdoor(single, 1)

    rows = []
    for blocks in range(1, max_blocks + 1):
        constraints = []
        next_var = 1
        for _ in range(blocks):
            z, a, b, c = next_var, next_var + 1, next_var + 2, next_var + 3
            constraints.append(Constraint(SWITCH4, (z, a, b, c)))
            next_var += 4
        found = minimum_strong_backdoor(constraints, blocks)
        rows.append({
            "blocks": blocks,
            "minimum_backdoor_size": len(found) if found is not None else None,
            "backdoor": list(found) if found is not None else None,
            "trivial_sat_witness_exists": brute_force_instance(constraints)[0],
        })

    branch_zero = restrict_instance(single, {1: False})
    branch_one = restrict_instance(single, {1: True})
    fp_zero = sorted(common_fingerprint(branch_zero))
    fp_one = sorted(common_fingerprint(branch_one))

    return {
        "switch_fingerprint": single_fp,
        "single_minimum_backdoor": list(single_min) if single_min else None,
        "z_zero_fingerprint": fp_zero,
        "z_one_fingerprint": fp_one,
        "disjoint_blocks": rows,
        "interpretation": (
            "A one-variable strong heterogeneous backdoor can choose different "
            "tractable polymorphisms in different branches. Repeating an easy "
            "switch component makes this fixed backdoor target linear even though "
            "the whole disconnected instance is trivially satisfiable."
        ),
    }


def hard_reduction_audit(
    rng: random.Random,
    cases: int = 80,
) -> dict[str, Any]:
    core = complete_unsat_3core()
    mapping_failures = 0
    dispatcher_false_accepts = 0
    dispatcher_open = 0
    sat_count = 0
    unsat_count = 0
    common_masks = Counter()

    for i in range(cases):
        n = rng.randint(3, 8)
        if i % 2 == 0:
            formula, planted = planted_3cnf(rng, n, rng.randint(n, 4 * n))
            expected = True
        else:
            noise, _ = planted_3cnf(rng, n, rng.randint(1, max(1, n)))
            formula = canonical_cnf(core + noise)
            expected = False

        constraints = reduce_3cnf_to_csp(formula, n)
        truth, witness, _ = brute_force_instance(constraints)
        if truth != expected:
            mapping_failures += 1

        source_truth = False
        for bits in itertools.product((False, True), repeat=n):
            source_assignment = dict(zip(range(1, n + 1), bits))
            if satisfies_cnf(formula, source_assignment):
                source_truth = True
                extended = source_assignment_to_csp(source_assignment, n)
                if not instance_satisfied(constraints, extended):
                    mapping_failures += 1
                break
        if source_truth != truth:
            mapping_failures += 1

        result = dispatch_instance(constraints)
        if result.status == "OPEN":
            dispatcher_open += 1
        elif result.sat != truth:
            dispatcher_false_accepts += 1

        for component in components(constraints):
            common_masks[",".join(sorted(common_fingerprint(component))) or "NONE"] += 1

        if truth:
            sat_count += 1
        else:
            unsat_count += 1

    pair_common = sorted(set(fingerprint(NAND3)) & set(fingerprint(NEQ2)))
    return {
        "cases": cases,
        "sat": sat_count,
        "unsat": unsat_count,
        "mapping_failures": mapping_failures,
        "dispatcher_open": dispatcher_open,
        "dispatcher_false_accepts": dispatcher_false_accepts,
        "nand3_fingerprint": sorted(fingerprint(NAND3)),
        "neq_fingerprint": sorted(fingerprint(NEQ2)),
        "common_fingerprint": pair_common,
        "component_common_masks": dict(common_masks),
        "reduction": (
            "For each x introduce c with NEQ(x,c); replace positive x by c "
            "inside NAND3 and negative -x by x."
        ),
        "consequence": (
            "The fixed Boolean language {NAND3, NEQ} has no Schaefer "
            "polymorphism and linearly expresses arbitrary 3-SAT."
        ),
    }


def canonical_fingerprint_audit() -> dict[str, Any]:
    relations = [TRUE3, NAND3, OR3, NEQ2, EQ2, IMP2, XOR3_EVEN, SWITCH4]
    return {
        relation.name: sorted(fingerprint(relation))
        for relation in relations
    }


def run(seed: int = DEFAULT_SEED) -> dict[str, Any]:
    rng = random.Random(seed)
    exhaustive = exhaustive_ternary_relation_audit()
    canonical = canonical_fingerprint_audit()
    fuzz = random_tractable_fuzz(rng)
    components_result = component_rescue_audit(rng)
    switch = switch_backdoor_audit()
    hard = hard_reduction_audit(rng)

    assertions = {
        "all_ternary_reconstructions_exact": not exhaustive["failures"],
        "tractable_fuzz_exact": (
            fuzz["open"] == 0
            and fuzz["mismatches"] == 0
            and fuzz["false_accepts"] == 0
        ),
        "component_rescue_exact": (
            components_result["component_dispatch_open"] == 0
            and components_result["component_dispatch_mismatches"] == 0
        ),
        "switch_has_no_global_gate": not canonical["SWITCH_HETEROGENEOUS"],
        "switch_backdoor_one": switch["single_minimum_backdoor"] == [1],
        "hard_reduction_exact": (
            hard["mapping_failures"] == 0
            and hard["dispatcher_false_accepts"] == 0
            and hard["dispatcher_open"] == hard["cases"]
        ),
        "hard_language_no_common_polymorphism": not hard["common_fingerprint"],
    }
    status = "PASS" if all(assertions.values()) else "FAIL"

    result = {
        "artifact_id": "C023-JANUS-BOOLEAN-POLYMORPHISM-GATE",
        "status": status,
        "research_status": "EXPLORATORY_SOFTWARE_ONLY_NOT_CANONICAL",
        "seed": seed,
        "canonical_seed_sha256": CANONICAL_SEED_SHA256,
        "software_only": True,
        "general_sat_oracle_called": False,
        "swarm_touched": False,
        "devices_touched": False,
        "nas_touched": False,
        "external_models_called": False,
        "gate": {
            "operations": list(OPS),
            "dispatch": {
                "ZERO": "all-zero witness",
                "ONE": "all-one witness",
                "AND": "Horn forward chaining",
                "OR": "dual-Horn forward chaining",
                "MAJ": "2-SAT implication SCC",
                "XOR3": "GF(2) Gaussian elimination",
            },
            "component_rule": (
                "Every connected constraint component must have at least one "
                "common verified operation."
            ),
            "failure_behavior": "OPEN",
        },
        "canonical_fingerprints": canonical,
        "exhaustive_ternary_relations": exhaustive,
        "random_tractable_fuzz": fuzz,
        "component_rescue": components_result,
        "heterogeneous_backdoor": switch,
        "three_sat_hard_boundary": hard,
        "assertions": assertions,
        "positive_result": (
            "All 256 ternary Boolean relations were exhaustively classified and "
            "every relation preserving AND, OR, majority, or minority was compiled "
            "back into an exact Horn, dual-Horn, 2-CNF, or affine representation. "
            "Connected components sharing a verified operation are dispatched "
            "without a general SAT oracle."
        ),
        "negative_result": (
            "Separate tractability is insufficient. NAND3 is Horn and NEQ is "
            "bijunctive/affine, but their common Schaefer fingerprint is empty; "
            "the pair linearly expresses arbitrary 3-SAT."
        ),
        "distance_to_p_equals_np": {
            "mathematical_status": "UNCHANGED_OPEN",
            "what_improved": [
                (
                    "The interface-language portfolio now has a machine-checkable "
                    "algebraic admission gate rather than ad hoc class names."
                ),
                (
                    "The exact obstruction is a loss of a common polymorphism, "
                    "not merely the coexistence of different syntactic formats."
                ),
                (
                    "Component decomposition and heterogeneous strong backdoors "
                    "are cleanly separated from the fixed-language gate."
                ),
            ],
            "remaining_target": (
                "Exploit instance-specific structure after the common-polymorphism "
                "intersection becomes empty: small fracture sets, low-width "
                "incidence structure, or a new proof system whose operations are "
                "not captured by one fixed Boolean constraint language."
            ),
        },
        "surviving_conjecture": {
            "name": "Polynomial Instance-Specific Polymorphism Fracture Conjecture",
            "statement": (
                "Every CNF instance admits a polynomially discoverable "
                "proof-carrying decomposition into regions with Schaefer "
                "polymorphisms, connected through a polynomial total fracture "
                "interface that supports witness recovery."
            ),
            "status": "OPEN",
            "warning": (
                "The fixed-language version is blocked by Schaefer's dichotomy; "
                "only genuinely instance-specific structure can remain."
            ),
        },
        "literature_boundary": {
            "schaefer_1978": (
                "For a fixed Boolean constraint language, generalized SAT is "
                "polynomial in the Schaefer cases and NP-complete otherwise."
            ),
            "algebraic_view": (
                "Polymorphisms encode closure properties determining CSP "
                "complexity and justify the gate used here."
            ),
        },
    }

    clean = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    result["integrity"] = {
        "sha256": hashlib.sha256(clean.encode("utf-8")).hexdigest()
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    result = run(args.seed)
    if args.output:
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.self_test and result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
