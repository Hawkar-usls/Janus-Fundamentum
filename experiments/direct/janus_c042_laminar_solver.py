from janus_c042_affine_core import *

def decide(
    cnf: CNF,
    affine: tuple[Equation, ...] = (),
    *,
    nvars_hint: int = 0,
    budget_cap: int | None = None,
) -> dict[str, Any]:
    cnf = normalize_cnf(cnf)
    nvars = max(nvars_hint, max(variables_in_cnf(cnf) | variables_in_affine(affine), default=0))
    input_object = canonical_input(cnf, affine, nvars)
    input_digest = digest(input_object)
    ledger = Ledger(encoded_length(cnf, affine, nvars), budget_cap)
    try:
        basis = parameterize_affine(affine, nvars, ledger)
        capability = {
            "budget_exponent": BUDGET_EXPONENT,
            "budget_multiplier": BUDGET_MULTIPLIER,
            "budget_cap": None if budget_cap is None else str(budget_cap),
        }
        if basis["status"] == "UNSAT":
            return finalize_certificate(
                {
                    "schema": SCHEMA,
                    "status": "UNSAT",
                    "reason": "AFFINE_CONTRADICTION",
                    "input_digest": input_digest,
                    "nvars": nvars,
                    "capability": capability,
                    "basis_artifact": basis,
                    "p_vs_np": "OPEN",
                },
                ledger,
            )

        dimension = int(basis["dimension"])
        coordinate_forms = [(int(mask), int(constant)) for mask, constant in basis["coordinate_forms"]]
        raw_factors = [
            translate_clause(clause_id, clause, coordinate_forms, dimension, ledger)
            for clause_id, clause in enumerate(cnf)
        ]
        factor_to_clauses: dict[tuple[Equation, ...], list[int]] = {}
        for factor in raw_factors:
            if not factor["empty"]:
                factor_to_clauses.setdefault(canonical_factor_system(factor), []).append(int(factor["clause_id"]))
        spaces = sorted(factor_to_clauses, key=lambda system: (len(system), system))
        unique_spaces = [
            {
                "index": index,
                "system": [[mask, rhs] for mask, rhs in system],
                "dimension": system_dimension(system, dimension),
                "clause_ids": factor_to_clauses[system],
            }
            for index, system in enumerate(spaces)
        ]
        pair_records: list[dict[str, Any]] = []
        for left_index in range(len(spaces)):
            for right_index in range(left_index + 1, len(spaces)):
                ledger.charge("pair_tests")
                rel = relation(spaces[left_index], spaces[right_index], dimension, ledger)
                pair_records.append({"left": left_index, "right": right_index, "relation": rel})
                if rel == "CROSSING":
                    overlap_system = intersection(spaces[left_index], spaces[right_index], dimension, ledger)
                    assert overlap_system is not None
                    common = solve_system(overlap_system, dimension, ledger)
                    left_only = next(
                        (
                            solve_system(spaces[left_index] + ((mask, rhs ^ 1),), dimension, ledger)
                            for mask, rhs in spaces[right_index]
                            if solve_system(spaces[left_index] + ((mask, rhs ^ 1),), dimension, ledger) is not None
                        ),
                        None,
                    )
                    right_only = next(
                        (
                            solve_system(spaces[right_index] + ((mask, rhs ^ 1),), dimension, ledger)
                            for mask, rhs in spaces[left_index]
                            if solve_system(spaces[right_index] + ((mask, rhs ^ 1),), dimension, ledger) is not None
                        ),
                        None,
                    )
                    return finalize_certificate(
                        {
                            "schema": SCHEMA,
                            "status": "OPEN_NON_LAMINAR",
                            "reason": "CROSSING_FORBIDDEN_SUBSPACES",
                            "input_digest": input_digest,
                            "nvars": nvars,
                            "dimension": dimension,
                            "capability": capability,
                            "basis_artifact": basis,
                            "raw_factors": raw_factors,
                            "unique_spaces": unique_spaces,
                            "pair_records": pair_records,
                            "crossing_pair": {
                                "left": left_index,
                                "right": right_index,
                                "common_lambda_mask": str(common),
                                "left_not_right_lambda_mask": str(left_only),
                                "right_not_left_lambda_mask": str(right_only),
                            },
                            "p_vs_np": "OPEN",
                        },
                        ledger,
                    )

        contained_records: list[dict[str, Any]] = []
        maximal_indices: list[int] = []
        for left_index, left in enumerate(spaces):
            containers: list[int] = []
            for right_index, right in enumerate(spaces):
                if left_index == right_index:
                    continue
                ledger.charge("maximality_tests")
                if subset(left, right, dimension, ledger):
                    containers.append(right_index)
            if containers:
                contained_records.append({"child": left_index, "containers": containers})
            else:
                maximal_indices.append(left_index)
        maximal_spaces = [spaces[index] for index in maximal_indices]
        for left_index in range(len(maximal_spaces)):
            for right_index in range(left_index + 1, len(maximal_spaces)):
                ledger.charge("maximal_disjointness_tests")
                if intersection(maximal_spaces[left_index], maximal_spaces[right_index], dimension, ledger) is not None:
                    raise AssertionError("laminar maxima must be disjoint")

        maximal_sizes: list[str] = []
        covered = 0
        for system in maximal_spaces:
            size = 1 << system_dimension(system, dimension)
            ledger.charge("big_integer_bits", max(1, size.bit_length()))
            covered += size
            maximal_sizes.append(str(size))
        total = 1 << dimension
        ledger.charge("big_integer_bits", max(1, total.bit_length()))
        base = {
            "schema": SCHEMA,
            "input_digest": input_digest,
            "nvars": nvars,
            "dimension": dimension,
            "capability": capability,
            "basis_artifact": basis,
            "raw_factors": raw_factors,
            "unique_spaces": unique_spaces,
            "pair_records": pair_records,
            "contained_records": contained_records,
            "maximal_indices": maximal_indices,
            "maximal_sizes": maximal_sizes,
            "covered_points": str(covered),
            "total_points": str(total),
            "p_vs_np": "OPEN",
        }
        if covered == total:
            return finalize_certificate(
                dict(base, status="UNSAT", reason="DISJOINT_MAXIMAL_AFFINE_COVER"), ledger
            )

        prefix: tuple[Equation, ...] = ()
        trace: list[dict[str, Any]] = []
        for coordinate in range(1, dimension + 1):
            branch_records: list[dict[str, Any]] = []
            chosen: tuple[int, tuple[Equation, ...]] | None = None
            for bit in (0, 1):
                cell = rref_system(prefix + ((1 << (coordinate - 1), bit),), dimension, ledger)
                if cell is None:
                    branch_records.append({"bit": bit, "cell_points": "0", "covered_points": "0", "parts": []})
                    continue
                cell_points = 1 << system_dimension(cell, dimension)
                ledger.charge("big_integer_bits", max(1, cell_points.bit_length()))
                branch_covered = 0
                parts = []
                for maximal_index, maximal_space in zip(maximal_indices, maximal_spaces):
                    ledger.charge("conditional_count_terms")
                    overlap = intersection(cell, maximal_space, dimension, ledger)
                    count = 0 if overlap is None else 1 << system_dimension(overlap, dimension)
                    ledger.charge("big_integer_bits", max(1, count.bit_length()))
                    branch_covered += count
                    parts.append({"maximal_index": maximal_index, "points": str(count)})
                branch_records.append(
                    {
                        "bit": bit,
                        "cell_points": str(cell_points),
                        "covered_points": str(branch_covered),
                        "parts": parts,
                    }
                )
                if chosen is None and branch_covered < cell_points:
                    chosen = (bit, cell)
            if chosen is None:
                raise AssertionError("conditional counting lost every uncovered point")
            bit, prefix = chosen
            trace.append({"coordinate": coordinate, "chosen_bit": bit, "branches": branch_records})
        lambda_mask = solve_system(prefix, dimension, ledger)
        if lambda_mask is None:
            raise AssertionError("complete prefix must be consistent")
        witness_mask = lift_coordinate_mask(lambda_mask, basis, nvars)
        ledger.charge("witness_recovery_bits", max(1, nvars + dimension))
        if not evaluate_equations(affine, witness_mask) or not evaluate_cnf(cnf, witness_mask):
            raise AssertionError("constructed witness failed")
        return finalize_certificate(
            dict(
                base,
                status="SAT",
                reason="POINT_OUTSIDE_LAMINAR_UNION",
                conditional_count_trace=trace,
                lambda_witness_mask=str(lambda_mask),
                lambda_witness=assignment_dict(lambda_mask, dimension),
                witness_mask=str(witness_mask),
                witness=assignment_dict(witness_mask, nvars),
            ),
            ledger,
        )
    except BudgetExceeded as error:
        return make_open_budget(input_digest, nvars, ledger, error.stage, budget_cap)
