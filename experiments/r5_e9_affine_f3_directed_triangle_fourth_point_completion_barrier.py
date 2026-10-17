#!/usr/bin/env python3
"""Exact Paley19 regression for DT4P-1/2.

The arbitrary-size directed-triangle completion theorem is proved symbolically in
the companion research note.  This checker reuses the frozen Paley19 source and
performs exact arithmetic over F3 only.
"""

from collections import Counter
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARENT = HERE / "r5_e9_affine_f3_rank2_cover_completeness_paley19_falsifier.py"
spec = importlib.util.spec_from_file_location("paley19_rank2", PARENT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def canon(v):
    v = tuple(x % 3 for x in v)
    first = next((x for x in v if x), None)
    assert first is not None
    inv = pow(first, -1, 3)
    return tuple((inv * x) % 3 for x in v)


def sub(u, v):
    return tuple((a - b) % 3 for a, b in zip(u, v))


def main():
    arcs, A = mod.build_source()
    mod.connected_linear_cubic(A)

    r0, B, rank = mod.affine_parameterization(A)
    assert r0 is not None
    assert rank == 152
    assert len(B) == 171
    assert len(B[0]) == 19

    coordinate_points = [canon(row) for row in B]
    assert len(set(coordinate_points)) == 171
    coordinate_set = set(coordinate_points)

    completion_counts = Counter()
    source_rows = 0

    for row in A:
        ids = [j for j, x in enumerate(row) if x]
        assert len(ids) == 3
        u, v, w = (B[j] for j in ids)

        # Every source triple sums to zero as coordinate functionals on ker(A).
        assert all((u[t] + v[t] + w[t]) % 3 == 0 for t in range(len(u)))

        pu, pv, pw = (canon(x) for x in (u, v, w))
        assert len({pu, pv, pw}) == 3

        # In PG(1,3), if the third source point is projectively u+v,
        # the fourth point is represented by u-v.
        kappa = canon(sub(u, v))
        assert kappa not in {pu, pv, pw}
        completion_counts[kappa] += 1
        source_rows += 1

    assert source_rows == 171
    assert len(completion_counts) == 171
    assert set(completion_counts.values()) == {1}
    assert set(completion_counts).isdisjoint(coordinate_set)

    print("PASS_DIRECTED_TRIANGLE_FOURTH_POINT_COMPLETION_BARRIER")
    print("Paley19 source_rows=171")
    print("coordinate_projective_points=171")
    print("distinct_fourth_points=171")
    print("fourth_points_inside_coordinate_set=0")
    print("max_completion_multiplicity=1")
    print("E8_D1=EMPTY P_VS_NP=OPEN")


if __name__ == "__main__":
    main()
