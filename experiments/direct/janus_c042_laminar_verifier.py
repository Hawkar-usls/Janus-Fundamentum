from janus_c042_affine_core import *
from janus_c042_laminar_solver import decide

def parse_system(rows: list[list[Any]]) -> tuple[Equation, ...]:
    return tuple((int(row[0]), int(row[1])) for row in rows)


def verify_provenance_rows(
    source_equations: tuple[Equation, ...], rows: list[list[Any]], dimension: int, ledger: Ledger
) -> bool:
    canonical = rref_system(source_equations, dimension, ledger)
    if canonical is None:
        return False
    stated = tuple((int(row[0]), int(row[1])) for row in rows)
    if stated != canonical:
        return False
    for mask, rhs, provenance_text in rows:
        ledger.charge("verifier_provenance_rows")
        if xor_provenance(source_equations, int(provenance_text)) != (int(mask), int(rhs)):
            return False
    return True


def verify_basis_artifact(
    affine: tuple[Equation, ...], nvars: int, artifact: dict[str, Any], ledger: Ledger
) -> bool:
    if artifact.get("status") == "UNSAT":
        provenance = int(artifact.get("conflict_provenance", "0"))
        return xor_provenance(affine, provenance) == (0, 1) and rref_system(affine, nvars, ledger) is None
    if artifact.get("status") != "SAT":
        return False
    rows = artifact.get("rref", [])
    if not verify_provenance_rows(affine, rows, nvars, ledger):
        return False
    canonical = tuple((int(row[0]), int(row[1])) for row in rows)
    free = [int(variable) for variable in artifact.get("free_variables", [])]
    pivots = {(mask & -mask).bit_length() for mask, _ in canonical}
    if free != [variable for variable in range(1, nvars + 1) if variable not in pivots]:
        return False
    particular = int(artifact.get("particular_mask", "0"))
    basis = [int(vector) for vector in artifact.get("basis_masks", [])]
    if len(basis) != len(free) or int(artifact.get("dimension", -1)) != len(free):
        return False
    if not evaluate_equations(affine, particular):
        return False
    homogeneous = tuple((mask, 0) for mask, _ in affine)
    for index, vector in enumerate(basis):
        ledger.charge("verifier_basis_vectors", max(1, nvars))
        if not evaluate_equations(homogeneous, vector):
            return False
        for free_index, variable in enumerate(free):
            expected = index == free_index
            if bool(vector & (1 << (variable - 1))) != expected:
                return False
    expected_forms = []
    for variable in range(1, nvars + 1):
        coordinate_mask = 0
        for index, vector in enumerate(basis):
            ledger.charge("verifier_coordinate_form_bits")
            if vector & (1 << (variable - 1)):
                coordinate_mask |= 1 << index
        expected_forms.append([coordinate_mask, int(bool(particular & (1 << (variable - 1))))])
    return artifact.get("coordinate_forms") == expected_forms



def verify_stated_producer_ledger(
    certificate: dict[str, Any], expected_input_length: int, budget_cap: int | None
) -> bool:
    stated = certificate.get("producer_ledger")
    if not isinstance(stated, dict):
        return False
    polynomial_limit = BUDGET_MULTIPLIER * (expected_input_length + 1) ** BUDGET_EXPONENT
    applied_limit = min(polynomial_limit, budget_cap if budget_cap is not None else polynomial_limit)
    if int(stated.get("input_length", -1)) != expected_input_length:
        return False
    if int(stated.get("budget_exponent", -1)) != BUDGET_EXPONENT:
        return False
    if int(stated.get("budget_multiplier", -1)) != BUDGET_MULTIPLIER:
        return False
    if int(stated.get("polynomial_limit", -1)) != polynomial_limit:
        return False
    if int(stated.get("applied_limit", -1)) != applied_limit:
        return False
    counters = stated.get("counters")
    if not isinstance(counters, dict) or any(not isinstance(value, int) or value < 0 for value in counters.values()):
        return False
    total = int(stated.get("total_work_units", -1))
    if total != sum(counters.values()):
        return False
    if certificate.get("status") == "OPEN_BUDGET":
        return total > applied_limit
    if total > applied_limit:
        return False
    return counters.get("certificate_bytes") == len(canonical_json(certificate).encode())

def verify_certificate_report(
    cnf: CNF,
    affine: tuple[Equation, ...],
    certificate: dict[str, Any],
    *,
    nvars_hint: int = 0,
) -> tuple[bool, dict[str, Any]]:
    cnf = normalize_cnf(cnf)
    nvars = max(nvars_hint, max(variables_in_cnf(cnf) | variables_in_affine(affine), default=0))
    capability = certificate.get("capability", {})
    budget_cap_value = capability.get("budget_cap")
    budget_cap = None if budget_cap_value is None else int(budget_cap_value)
    ledger = Ledger(encoded_length(cnf, affine, nvars), budget_cap)
    try:
        if certificate.get("schema") != SCHEMA or certificate.get("p_vs_np") != "OPEN":
            return False, ledger.snapshot()
        body = dict(certificate)
        stated_hash = body.pop("integrity_sha256", None)
        ledger.charge("verifier_certificate_bytes", len(canonical_json(certificate).encode()))
        if stated_hash is None or digest(body) != stated_hash:
            return False, ledger.snapshot()
        input_digest = digest(canonical_input(cnf, affine, nvars))
        if certificate.get("input_digest") != input_digest or int(certificate.get("nvars", -1)) != nvars:
            return False, ledger.snapshot()
        if (int(capability.get("budget_exponent", -1)) != BUDGET_EXPONENT
                or int(capability.get("budget_multiplier", -1)) != BUDGET_MULTIPLIER):
            return False, ledger.snapshot()
        if not verify_stated_producer_ledger(
            certificate, encoded_length(cnf, affine, nvars), budget_cap
        ):
            return False, ledger.snapshot()
        status = certificate.get("status")
        if status == "OPEN_BUDGET":
            replay = decide(cnf, affine, nvars_hint=nvars_hint, budget_cap=budget_cap)
            return replay == certificate, ledger.snapshot()
        basis = certificate.get("basis_artifact", {})
        if not verify_basis_artifact(affine, nvars, basis, ledger):
            return False, ledger.snapshot()
        if status == "UNSAT" and certificate.get("reason") == "AFFINE_CONTRADICTION":
            return basis.get("status") == "UNSAT", ledger.snapshot()
        if basis.get("status") != "SAT":
            return False, ledger.snapshot()
        dimension = int(basis["dimension"])
        coordinate_forms = [(int(mask), int(constant)) for mask, constant in basis["coordinate_forms"]]
        expected_factors = [
            translate_clause(clause_id, clause, coordinate_forms, dimension, ledger)
            for clause_id, clause in enumerate(cnf)
        ]
        if certificate.get("raw_factors") != expected_factors:
            return False, ledger.snapshot()
        factor_to_clauses: dict[tuple[Equation, ...], list[int]] = {}
        for factor in expected_factors:
            if not factor["empty"]:
                factor_to_clauses.setdefault(canonical_factor_system(factor), []).append(int(factor["clause_id"]))
        spaces = sorted(factor_to_clauses, key=lambda system: (len(system), system))
        expected_unique = [
            {
                "index": index,
                "system": [[mask, rhs] for mask, rhs in system],
                "dimension": system_dimension(system, dimension),
                "clause_ids": factor_to_clauses[system],
            }
            for index, system in enumerate(spaces)
        ]
        if certificate.get("unique_spaces") != expected_unique:
            return False, ledger.snapshot()
        expected_pairs: list[dict[str, Any]] = []
        crossing: tuple[int, int] | None = None
        for left_index in range(len(spaces)):
            for right_index in range(left_index + 1, len(spaces)):
                ledger.charge("verifier_pair_tests")
                rel = relation(spaces[left_index], spaces[right_index], dimension, ledger)
                expected_pairs.append({"left": left_index, "right": right_index, "relation": rel})
                if rel == "CROSSING":
                    crossing = (left_index, right_index)
                    break
            if crossing is not None:
                break
        if certificate.get("pair_records") != expected_pairs:
            return False, ledger.snapshot()
        if status == "OPEN_NON_LAMINAR":
            if crossing is None:
                return False, ledger.snapshot()
            pair = certificate.get("crossing_pair", {})
            if (int(pair.get("left", -1)), int(pair.get("right", -1))) != crossing:
                return False, ledger.snapshot()
            left, right = spaces[crossing[0]], spaces[crossing[1]]
            common = int(pair.get("common_lambda_mask", "-1"))
            left_only = int(pair.get("left_not_right_lambda_mask", "-1"))
            right_only = int(pair.get("right_not_left_lambda_mask", "-1"))
            if not (evaluate_equations(left, common) and evaluate_equations(right, common)):
                return False, ledger.snapshot()
            if not (evaluate_equations(left, left_only) and not evaluate_equations(right, left_only)):
                return False, ledger.snapshot()
            if not (evaluate_equations(right, right_only) and not evaluate_equations(left, right_only)):
                return False, ledger.snapshot()
            return True, ledger.snapshot()
        if crossing is not None:
            return False, ledger.snapshot()

        expected_contained = []
        maxima = []
        for left_index, left in enumerate(spaces):
            containers = []
            for right_index, right in enumerate(spaces):
                if left_index == right_index:
                    continue
                ledger.charge("verifier_maximality_tests")
                if subset(left, right, dimension, ledger):
                    containers.append(right_index)
            if containers:
                expected_contained.append({"child": left_index, "containers": containers})
            else:
                maxima.append(left_index)
        if certificate.get("contained_records") != expected_contained or certificate.get("maximal_indices") != maxima:
            return False, ledger.snapshot()
        maximal_spaces = [spaces[index] for index in maxima]
        for left_index in range(len(maximal_spaces)):
            for right_index in range(left_index + 1, len(maximal_spaces)):
                if intersection(maximal_spaces[left_index], maximal_spaces[right_index], dimension, ledger) is not None:
                    return False, ledger.snapshot()
        sizes = [1 << system_dimension(system, dimension) for system in maximal_spaces]
        covered = sum(sizes)
        total = 1 << dimension
        if certificate.get("maximal_sizes") != [str(size) for size in sizes]:
            return False, ledger.snapshot()
        if certificate.get("covered_points") != str(covered) or certificate.get("total_points") != str(total):
            return False, ledger.snapshot()
        if status == "UNSAT":
            return certificate.get("reason") == "DISJOINT_MAXIMAL_AFFINE_COVER" and covered == total, ledger.snapshot()
        if status != "SAT" or covered >= total:
            return False, ledger.snapshot()
        trace = certificate.get("conditional_count_trace", [])
        if len(trace) != dimension:
            return False, ledger.snapshot()
        prefix: tuple[Equation, ...] = ()
        for coordinate, record in enumerate(trace, start=1):
            if int(record.get("coordinate", -1)) != coordinate:
                return False, ledger.snapshot()
            expected_branches = []
            first_undercovered = None
            cells: dict[int, tuple[Equation, ...]] = {}
            for bit in (0, 1):
                cell = rref_system(prefix + ((1 << (coordinate - 1), bit),), dimension, ledger)
                if cell is None:
                    expected_branches.append({"bit": bit, "cell_points": "0", "covered_points": "0", "parts": []})
                    continue
                cells[bit] = cell
                cell_points = 1 << system_dimension(cell, dimension)
                branch_covered = 0
                parts = []
                for maximal_index, maximal_space in zip(maxima, maximal_spaces):
                    overlap = intersection(cell, maximal_space, dimension, ledger)
                    count = 0 if overlap is None else 1 << system_dimension(overlap, dimension)
                    branch_covered += count
                    parts.append({"maximal_index": maximal_index, "points": str(count)})
                expected_branches.append(
                    {
                        "bit": bit,
                        "cell_points": str(cell_points),
                        "covered_points": str(branch_covered),
                        "parts": parts,
                    }
                )
                if first_undercovered is None and branch_covered < cell_points:
                    first_undercovered = bit
            if record.get("branches") != expected_branches or record.get("chosen_bit") != first_undercovered:
                return False, ledger.snapshot()
            if first_undercovered is None:
                return False, ledger.snapshot()
            prefix = cells[first_undercovered]
        lambda_mask = int(certificate.get("lambda_witness_mask", "-1"))
        expected_lambda = solve_system(prefix, dimension, ledger)
        if lambda_mask != expected_lambda:
            return False, ledger.snapshot()
        if certificate.get("lambda_witness") != assignment_dict(lambda_mask, dimension):
            return False, ledger.snapshot()
        witness_mask = int(certificate.get("witness_mask", "-1"))
        if witness_mask != lift_coordinate_mask(lambda_mask, basis, nvars):
            return False, ledger.snapshot()
        if certificate.get("witness") != assignment_dict(witness_mask, nvars):
            return False, ledger.snapshot()
        if not evaluate_equations(affine, witness_mask) or not evaluate_cnf(cnf, witness_mask):
            return False, ledger.snapshot()
        for space in spaces:
            if evaluate_equations(space, lambda_mask):
                return False, ledger.snapshot()
        return True, ledger.snapshot()
    except (BudgetExceeded, KeyError, TypeError, ValueError, AssertionError):
        return False, ledger.snapshot()


def verify_certificate(
    cnf: CNF, affine: tuple[Equation, ...], certificate: dict[str, Any], *, nvars_hint: int = 0
) -> bool:
    return verify_certificate_report(cnf, affine, certificate, nvars_hint=nvars_hint)[0]
