#!/usr/bin/env python3
from __future__ import annotations
from janus_c037_2_horn_affine_hull_core import *
from janus_c037_2_horn_affine_hull_protocol import *

def all_models(formula: CNF, variable_count: int) -> list[Assignment]:
    result: list[Assignment] = []
    for bits in itertools.product((False, True), repeat=variable_count):
        assignment = {
            variable + 1: bits[variable] for variable in range(variable_count)
        }
        if eval_cnf(formula, assignment):
            result.append(assignment)
    return result


def generated_equation_space(rows: list[Equation]) -> set[Equation]:
    space: set[Equation] = {(0, 0)}
    for mask, rhs in rows:
        additions = {(left ^ mask, value ^ rhs) for left, value in space}
        space |= additions
    return space


def valid_equations_for_models(
    models: list[Assignment], variable_count: int
) -> set[Equation]:
    result: set[Equation] = set()
    for mask in range(1 << variable_count):
        for rhs in (0, 1):
            if all(eval_row((mask, rhs), assignment) for assignment in models):
                result.add((mask, rhs))
    return result


def family_basis(family: set[int], variable_count: int) -> list[Equation]:
    ordered = sorted(family)
    columns = [
        tuple((assignment >> variable) & 1 for assignment in ordered)
        for variable in range(variable_count)
    ]
    rows: list[Equation] = []
    groups: dict[tuple[int, ...], list[int]] = {}
    for variable, column in enumerate(columns):
        if all(value == 0 for value in column):
            rows.append((1 << variable, 0))
        elif all(value == 1 for value in column):
            rows.append((1 << variable, 1))
        else:
            groups.setdefault(column, []).append(variable)
    for variables in groups.values():
        root = variables[0]
        for variable in variables[1:]:
            rows.append(((1 << root) | (1 << variable), 0))
    return rows


def meet_closed(family: set[int]) -> bool:
    return all((left & right) in family for left in family for right in family)


def exhaustive_meet_semilattice_audit(variable_count: int = 4) -> dict:
    family_count = 0
    for family_mask in range(1, 1 << (1 << variable_count)):
        family = {
            assignment
            for assignment in range(1 << variable_count)
            if family_mask >> assignment & 1
        }
        if not meet_closed(family):
            continue
        family_count += 1
        rows = family_basis(family, variable_count)
        models = [
            {
                variable + 1: bool(assignment >> variable & 1)
                for variable in range(variable_count)
            }
            for assignment in sorted(family)
        ]
        if generated_equation_space(rows) != valid_equations_for_models(
            models, variable_count
        ):
            raise AssertionError("meet-semilattice affine basis mismatch")
    return {
        "variables": variable_count,
        "nonempty_meet_closed_families": family_count,
        "mismatches": 0,
    }


def random_horn(
    rng: random.Random, variable_count: int, clause_count: int
) -> CNF:
    clauses: list[Clause] = []
    for _ in range(clause_count):
        body = rng.sample(
            range(1, variable_count + 1),
            rng.randint(0, min(3, variable_count)),
        )
        remaining = [
            variable
            for variable in range(1, variable_count + 1)
            if variable not in body
        ]
        head = rng.choice(remaining) if remaining and rng.random() < 0.65 else None
        clauses.append(tuple([-variable for variable in body] + ([head] if head else [])))
    return normalize(tuple(clauses))


def random_affine_rows(
    rng: random.Random, variable_count: int, row_count: int
) -> tuple[Equation, ...]:
    rows: list[Equation] = []
    for _ in range(row_count):
        mask = rng.randrange(1, 1 << variable_count)
        rows.append((mask, rng.randrange(2)))
    return tuple(rows)


def random_reverse_inclusion_audit(
    seed: int = 370_372, cases: int = 500
) -> dict:
    rng = random.Random(seed)
    counters = {
        "directed_inclusion": 0,
        "separator": 0,
        "horn_empty_subset": 0,
    }
    basis_checks = 0
    total_horn_calls = 0
    total_clause_scans = 0

    for _ in range(cases):
        variable_count = rng.randint(1, 7)
        formula = random_horn(
            rng, variable_count, rng.randint(0, 12)
        )
        affine_rows = random_affine_rows(
            rng, variable_count, rng.randint(0, 6)
        )
        models = all_models(formula, variable_count)
        expected = all(
            eval_affine(affine_rows, assignment) for assignment in models
        )
        certificate = reverse_horn_to_affine_inclusion(
            formula, affine_rows, variable_count, 100_000_000
        )
        if not replay_certificate(certificate):
            raise AssertionError("reverse inclusion certificate failed replay")

        terminal = certificate["terminal"]["status"]
        if not models:
            if terminal != "HORN_EMPTY_SUBSET":
                raise AssertionError("empty Horn relation was not recognized")
            counters["horn_empty_subset"] += 1
        elif expected:
            if terminal != "DIRECTED_INCLUSION":
                raise AssertionError("true reverse inclusion was rejected")
            counters["directed_inclusion"] += 1
        else:
            if terminal != "SEPARATOR":
                raise AssertionError("failed reverse inclusion lacked separator")
            counters["separator"] += 1

        if models:
            meter = Meter(100_000_000)
            basis = extract_affine_consequence_basis(
                formula, variable_count, {}, meter
            )
            actual = valid_equations_for_models(models, variable_count)
            represented = generated_equation_space(basis["rows"])
            if actual != represented:
                raise AssertionError("Horn affine hull basis is incomplete")
            basis_checks += 1
        total_horn_calls += certificate.get("cost", {}).get("horn_calls", 0)
        total_clause_scans += certificate.get("cost", {}).get(
            "horn_clause_scans", 0
        )

    return {
        "seed": seed,
        "cases": cases,
        "basis_checks_on_nonempty_horn_relations": basis_checks,
        **counters,
        "total_horn_calls": total_horn_calls,
        "total_horn_clause_scans": total_clause_scans,
    }


def complete_three_cnf_hard_image():
    horn_clauses: list[Clause] = []
    for signs in itertools.product((False, True), repeat=3):
        falsity_indicators = [
            3 + variable if positive else variable
            for variable, positive in enumerate(signs, start=1)
        ]
        horn_clauses.append(tuple(-variable for variable in falsity_indicators))
    affine_rows = tuple(
        (
            (1 << (variable - 1)) | (1 << (3 + variable - 1)),
            1,
        )
        for variable in range(1, 4)
    )
    return normalize(tuple(horn_clauses)), affine_rows, 6


def adversarial_controls() -> dict:
    equality = normalize(((-1, 2), (1, -2)))
    disequality = ((0b11, 1),)
    equality_certificate = reverse_horn_to_affine_inclusion(
        equality, disequality, 2, 10_000_000
    )
    if equality_certificate["terminal"]["status"] != "SEPARATOR":
        raise AssertionError("equality/disequality must have a Horn separator")
    equality_negotiation = complete_affine_consequence_negotiation(
        equality, disequality, 2, 10_000_000
    )
    if equality_negotiation["terminal"]["status"] != "CERTIFIED_CONFLICT":
        raise AssertionError("complete equality basis must close affine disequality")

    higher_horn = normalize(
        (
            (-1, 2), (1, -2),
            (-3, 4), (3, -4),
            (-5, 6), (5, -6),
        )
    )
    higher_row = ((0b111111, 0),)
    higher_certificate = reverse_horn_to_affine_inclusion(
        higher_horn, higher_row, 6, 10_000_000
    )
    if higher_certificate["terminal"]["status"] != "DIRECTED_INCLUSION":
        raise AssertionError("six-variable parity must follow from three equalities")
    higher_conflict = complete_affine_consequence_negotiation(
        higher_horn, ((0b111111, 1),), 6, 10_000_000
    )
    if higher_conflict["terminal"]["status"] != "CERTIFIED_CONFLICT":
        raise AssertionError("higher-arity parity conflict was not closed")

    chain_size = 20
    chain_clauses: list[Clause] = []
    for variable in range(1, chain_size):
        chain_clauses.extend(
            [(-variable, variable + 1), (variable, -(variable + 1))]
        )
    chain_formula = normalize(tuple(chain_clauses))
    chain_row = (((1 << chain_size) - 1, 0),)
    chain_certificate = reverse_horn_to_affine_inclusion(
        chain_formula, chain_row, chain_size, 100_000_000
    )
    if chain_certificate["terminal"]["status"] != "DIRECTED_INCLUSION":
        raise AssertionError("even equality chain parity must be entailed")
    chain_basis_rows = len(chain_certificate["basis"]["rows"])
    if chain_basis_rows != chain_size - 1:
        raise AssertionError("equality chain basis must be a spanning tree")

    beta_acyclic_non_horn = ((1, 2),)
    language_control = reverse_horn_to_affine_inclusion(
        beta_acyclic_non_horn, ((0b11, 0),), 2, 100
    )
    if language_control["terminal"]["status"] != "OPEN_LANGUAGE":
        raise AssertionError("non-Horn beta-acyclic control must remain OPEN_LANGUAGE")

    horn_hard, affine_hard, variable_count = complete_three_cnf_hard_image()
    horn_models = all_models(horn_hard, variable_count)
    mixed_models = [
        assignment
        for assignment in horn_models
        if eval_affine(affine_hard, assignment)
    ]
    basis = extract_affine_consequence_basis(
        horn_hard, variable_count, {}, Meter(100_000_000)
    )
    hard_certificate = reverse_horn_to_affine_inclusion(
        horn_hard, affine_hard, variable_count, 100_000_000
    )
    hard_negotiation = complete_affine_consequence_negotiation(
        horn_hard, affine_hard, variable_count, 100_000_000
    )
    if mixed_models:
        raise AssertionError("complete 3-CNF reduction image must be UNSAT")
    if basis["rows"]:
        raise AssertionError("hard image unexpectedly has affine Horn consequences")
    if hard_certificate["terminal"]["status"] != "SEPARATOR":
        raise AssertionError("hard image reverse inclusion must expose a separator")
    if (
        hard_negotiation["terminal"]["status"]
        != "OPEN_AFFINE_CONSEQUENCE_COMPLETE"
    ):
        raise AssertionError("hard image must survive complete consequence exchange")

    budget_certificate = reverse_horn_to_affine_inclusion(
        tuple(),
        ((0b1111111111, 0),),
        10,
        1,
    )
    if budget_certificate["terminal"]["status"] != "OPEN_BUDGET":
        raise AssertionError("tiny work budget must return OPEN_BUDGET")

    corrupt = json.loads(json.dumps(equality_certificate))
    if corrupt["terminal"]["status"] == "SEPARATOR":
        corrupt["terminal"]["assignment"]["1"] ^= 1
    if replay_certificate(corrupt):
        raise AssertionError("corrupt separator was accepted")

    return {
        "equality_vs_disequality": "CERTIFIED_CONFLICT_AFTER_BASIS_INJECTION",
        "higher_arity_six_variable_parity": "DIRECTED_INCLUSION",
        "higher_arity_opposite_parity": "CERTIFIED_CONFLICT",
        "equality_chain": {
            "variables": chain_size,
            "semantic_equalities": chain_size * (chain_size - 1) // 2,
            "emitted_basis_rows": chain_basis_rows,
            "twenty_variable_parity": "DIRECTED_INCLUSION",
        },
        "beta_acyclic_non_horn": "OPEN_LANGUAGE",
        "complete_3cnf_nand3_neq": {
            "horn_models": len(horn_models),
            "mixed_models": len(mixed_models),
            "horn_affine_basis_rows": len(basis["rows"]),
            "reverse_inclusion_terminal": hard_certificate["terminal"]["status"],
            "negotiation_terminal": hard_negotiation["terminal"]["status"],
            "meaning": (
                "all Horn affine consequences are exhausted, but the jointly "
                "UNSAT multirow interaction remains outside consequence exchange"
            ),
        },
        "corrupt_separator": "REJECTED",
        "budget_control": "OPEN_BUDGET",
    }


def run() -> dict:
    semilattice = exhaustive_meet_semilattice_audit(4)
    random_audit = random_reverse_inclusion_audit()
    controls = adversarial_controls()
    result = {
        "artifact_id": "C037.2-HORN-AFFINE-HULL-COLLAPSE",
        "status": "PASS",
        "p_vs_np": "OPEN",
        "theorem": (
            "For every satisfiable Horn formula, every affine GF(2) consequence "
            "is generated by forced literals and pairwise equalities."
        ),
        "constructive_bridge": (
            "MODELS(HORN) subseteq MODELS(AFFINE) is completely decided in "
            "polynomial time with either Horn-native basis proofs or an explicit "
            "Horn model violating one affine row."
        ),
        "proof_core": (
            "Horn models form a meet semilattice. Nonzero distinct coordinate "
            "functions, together with the constant-one function, are distinct "
            "multiplicative semilattice characters and are linearly independent."
        ),
        "semilattice_exhaustive_audit": semilattice,
        "random_reverse_inclusion_audit": random_audit,
        "adversarial_controls": controls,
        "closed_gate": (
            "HIGHER_ARITY_HORN_TO_AFFINE_CONSEQUENCE_DISCOVERY"
        ),
        "new_gate": (
            "MULTIROW_HORN_AFFINE_INTERACTION_OR_PORTFOLIO_DECOMPOSITION"
        ),
        "claim_boundary": (
            "The theorem exhausts unconditional affine consequences of Horn "
            "messages. It does not decide unrestricted Horn-affine conjunctions; "
            "the NAND3+NEQ image remains jointly NP-hard and is returned as a "
            "multirow interaction obstruction rather than solved."
        ),
    }
    payload = canonical_json(result).encode()
    result["integrity_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    result = run()
    print(json.dumps(result, indent=2, sort_keys=True))
    if arguments.self_test:
        assert result["status"] == "PASS"
        assert result["semilattice_exhaustive_audit"][
            "nonempty_meet_closed_families"
        ] == 4959
        assert result["adversarial_controls"]["corrupt_separator"] == "REJECTED"
        assert result["p_vs_np"] == "OPEN"


if __name__ == "__main__":
    main()
