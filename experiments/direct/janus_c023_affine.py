"""C023 GF(2) elimination and affine projection."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from janus_c023_primitives import *

# ---------------------------------------------------------------------------
# GF(2) elimination, projection, and certificates
# ---------------------------------------------------------------------------

@dataclass
class AffineSolution:
    consistent: bool
    variables: tuple[int, ...]
    particular_mask: int | None
    basis_masks: tuple[int, ...]
    rank: int
    conflict_equation_indices: tuple[int, ...] | None
    row_operations: int
    fixed_equation_offset: int

    def assignment_from_mask(self, mask: int) -> dict[int, bool]:
        return {
            v: bool((mask >> i) & 1)
            for i, v in enumerate(self.variables)
        }


def affine_solve(
    equations: list[Equation],
    universe: list[int],
    fixed: dict[int, bool] | None = None,
) -> AffineSolution:
    fixed = dict(fixed or {})
    vars_ = tuple(sorted(set(universe) | set(equation_variables(equations)) | set(fixed)))
    pos = {v: i for i, v in enumerate(vars_)}

    rows: list[list[int]] = []
    for idx, (eq_vars, rhs) in enumerate(equations):
        mask = 0
        for v in eq_vars:
            mask ^= 1 << pos[v]
        rows.append([mask, rhs & 1, 1 << idx])

    offset = len(equations)
    for j, (v, value) in enumerate(sorted(fixed.items())):
        rows.append([1 << pos[v], int(value), 1 << (offset + j)])

    operations = 0
    pivot_row = 0
    pivot_cols: list[int] = []
    for col in range(len(vars_)):
        pivot = next(
            (r for r in range(pivot_row, len(rows)) if (rows[r][0] >> col) & 1),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        for r in range(len(rows)):
            if r != pivot_row and ((rows[r][0] >> col) & 1):
                rows[r][0] ^= rows[pivot_row][0]
                rows[r][1] ^= rows[pivot_row][1]
                rows[r][2] ^= rows[pivot_row][2]
                operations += 1
        pivot_cols.append(col)
        pivot_row += 1

    for mask, rhs, provenance in rows:
        if mask == 0 and rhs == 1:
            indices = tuple(i for i in range(len(rows)) if (provenance >> i) & 1)
            return AffineSolution(
                consistent=False,
                variables=vars_,
                particular_mask=None,
                basis_masks=(),
                rank=len(pivot_cols),
                conflict_equation_indices=indices,
                row_operations=operations,
                fixed_equation_offset=offset,
            )

    pivot_to_row = {col: i for i, col in enumerate(pivot_cols)}
    free_cols = [c for c in range(len(vars_)) if c not in pivot_to_row]

    particular = 0
    for col in reversed(pivot_cols):
        row = rows[pivot_to_row[col]]
        rhs = row[1]
        value = rhs
        mask = row[0] & ~(1 << col)
        while mask:
            lsb = mask & -mask
            j = lsb.bit_length() - 1
            value ^= (particular >> j) & 1
            mask ^= lsb
        if value:
            particular |= 1 << col

    basis: list[int] = []
    for free in free_cols:
        vector = 1 << free
        for col in reversed(pivot_cols):
            row = rows[pivot_to_row[col]]
            value = 0
            mask = row[0] & ~(1 << col)
            while mask:
                lsb = mask & -mask
                j = lsb.bit_length() - 1
                value ^= (vector >> j) & 1
                mask ^= lsb
            if value:
                vector |= 1 << col
        basis.append(vector)

    result = AffineSolution(
        consistent=True,
        variables=vars_,
        particular_mask=particular,
        basis_masks=tuple(basis),
        rank=len(pivot_cols),
        conflict_equation_indices=None,
        row_operations=operations,
        fixed_equation_offset=offset,
    )
    assignment = result.assignment_from_mask(particular)
    if not satisfies_affine(equations, assignment):
        raise AssertionError("affine particular solution failed")
    for v, value in fixed.items():
        if assignment[v] != value:
            raise AssertionError("affine fixed value failed")
    return result


def verify_affine_conflict(
    equations: list[Equation],
    fixed: dict[int, bool],
    solution: AffineSolution,
) -> bool:
    if solution.consistent or solution.conflict_equation_indices is None:
        return False
    vars_ = solution.variables
    pos = {v: i for i, v in enumerate(vars_)}
    all_equations = list(equations) + [((v,), int(value)) for v, value in sorted(fixed.items())]
    mask = 0
    rhs = 0
    for idx in solution.conflict_equation_indices:
        if not (0 <= idx < len(all_equations)):
            return False
        eq_vars, eq_rhs = all_equations[idx]
        for v in eq_vars:
            mask ^= 1 << pos[v]
        rhs ^= eq_rhs & 1
    return mask == 0 and rhs == 1


@dataclass
class ProjectedAffine:
    particular_full_mask: int
    direction_full_masks: tuple[int, ...]
    interface_variables: tuple[int, ...]
    dimension: int


def project_affine(
    solution: AffineSolution,
    interface: list[int],
) -> ProjectedAffine:
    if not solution.consistent or solution.particular_mask is None:
        raise ValueError("cannot project inconsistent affine system")
    pos = {v: i for i, v in enumerate(solution.variables)}
    interface_tuple = tuple(interface)
    ipos = {v: i for i, v in enumerate(interface_tuple)}

    pivots: dict[int, tuple[int, int]] = {}
    for full in solution.basis_masks:
        projected = 0
        for v in interface_tuple:
            if (full >> pos[v]) & 1:
                projected |= 1 << ipos[v]
        reduced_p = projected
        reduced_f = full
        while reduced_p:
            pivot = reduced_p.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (reduced_p, reduced_f)
                break
            bp, bf = pivots[pivot]
            reduced_p ^= bp
            reduced_f ^= bf

    directions = tuple(full for _, full in sorted(pivots.values(), reverse=True))
    return ProjectedAffine(
        particular_full_mask=solution.particular_mask,
        direction_full_masks=directions,
        interface_variables=interface_tuple,
        dimension=len(directions),
    )


def affine_forced_values(
    solution: AffineSolution,
    candidates: list[int],
) -> dict[int, bool]:
    if not solution.consistent or solution.particular_mask is None:
        return {}
    pos = {v: i for i, v in enumerate(solution.variables)}
    forced = {}
    for v in candidates:
        bit = pos[v]
        if all(((basis >> bit) & 1) == 0 for basis in solution.basis_masks):
            forced[v] = bool((solution.particular_mask >> bit) & 1)
    return forced
