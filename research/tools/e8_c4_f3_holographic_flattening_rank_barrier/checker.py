#!/usr/bin/env python3
"""v8.5.6 exact finite obstruction for the canonical arity-6 F3 current tensor.

We do NOT apply a symmetric-Holant dichotomy to this tensor: the tensor is
explicitly non-symmetric.  Instead we use exact bipartition flattening ranks,
which are invariant under arbitrary invertible basis changes on individual
ports, to rule out two concrete higher-domain holographic normal forms:

  * CP/tensor rank <= 3 (including GenEQ and the rank-3 pure-power forms),
  * domain separation {B,G}^6 union {R}^6.

The latter has every 3|3 flattening rank <= 2^3 + 1 = 9; our tensor has
rank 12 on four unordered 3|3 partitions.
"""

from fractions import Fraction
from itertools import combinations, product
from collections import Counter

VP = (1, 1, 0, 1, 1, 0)
VM = (1, 2, 0, 2, 0, 1)
N = 6
DOMAIN = range(3)


def dot3(a, b):
    return sum(x * y for x, y in zip(a, b)) % 3


def local_current_signature(x):
    # Canonical all-outgoing current orientation.  Reversing one physical edge
    # is the invertible local permutation k -> -k and therefore cannot alter
    # any flattening rank used below.
    if sum(x) % 3 != 0:
        return 0
    value = -2
    if dot3(VP, x) == 0:
        value += 3
    if dot3(VM, x) == 0:
        value += 3
    return value


TENSOR = {x: local_current_signature(x) for x in product(DOMAIN, repeat=N)}
assert Counter(TENSOR.values()) == Counter({0: 486, -2: 108, 1: 108, 4: 27})

# Explicitly freeze the scope mismatch with the 2025 symmetric-domain-3 Holant
# dichotomy: this ordered six-port tensor is not symmetric.
x = (0, 1, 0, 0, 0, 2)
y = (1, 0, 0, 0, 0, 2)
assert TENSOR[x] == -2
assert TENSOR[y] == 1


def exact_rank(matrix):
    """Gaussian rank over Q using exact Fractions."""
    if not matrix:
        return 0
    a = [[Fraction(v) for v in row] for row in matrix]
    rows = len(a)
    cols = len(a[0])
    r = 0
    for c in range(cols):
        pivot = next((i for i in range(r, rows) if a[i][c] != 0), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        pv = a[r][c]
        a[r] = [v / pv for v in a[r]]
        for i in range(rows):
            if i == r or a[i][c] == 0:
                continue
            f = a[i][c]
            a[i] = [u - f * v for u, v in zip(a[i], a[r])]
        r += 1
        if r == rows:
            break
    return r


def flatten_matrix(left_axes):
    left = tuple(left_axes)
    right = tuple(i for i in range(N) if i not in left)
    left_words = list(product(DOMAIN, repeat=len(left)))
    right_words = list(product(DOMAIN, repeat=len(right)))
    matrix = []
    for lw in left_words:
        row = []
        for rw in right_words:
            state = [0] * N
            for ax, val in zip(left, lw):
                state[ax] = val
            for ax, val in zip(right, rw):
                state[ax] = val
            row.append(TENSOR[tuple(state)])
        matrix.append(row)
    return matrix


mode_ranks = {}
for axis in range(N):
    mode_ranks[(axis,)] = exact_rank(flatten_matrix((axis,)))
assert set(mode_ranks.values()) == {3}

# Unordered 3|3 partitions: retain the representative containing port 0.
three_three = {}
for left in combinations(range(N), 3):
    if 0 not in left:
        continue
    three_three[left] = exact_rank(flatten_matrix(left))

expected_three_three = {
    (0, 1, 2): 12,
    (0, 1, 3): 9,
    (0, 1, 4): 9,
    (0, 1, 5): 12,
    (0, 2, 3): 12,
    (0, 2, 4): 6,
    (0, 2, 5): 9,
    (0, 3, 4): 9,
    (0, 3, 5): 12,
    (0, 4, 5): 6,
}
assert three_three == expected_three_three
assert Counter(three_three.values()) == Counter({12: 4, 9: 4, 6: 2})

# Algebraic consequences of flattening-rank invariance under any tensor product
# of invertible per-port basis changes:
#   - a sum of <=3 pure tensors has every bipartition rank <=3;
#   - support in a two-element subdomain has mode rank <=2;
#   - support in {B,G}^6 union {R}^6 decomposes into an arbitrary Boolean
#     3^3-by-3^3 block (rank <=8) plus one singleton R^6 pure tensor (rank <=1),
#     hence every 3|3 flattening rank <=9.
max_rank = max(three_three.values())
assert max_rank == 12
assert max_rank > 3
assert max_rank > 9

print("PASS: canonical F3 six-port current tensor value profile is 0:486,-2:108,1:108,4:27")
print("PASS: tensor is explicitly port-ordered/non-symmetric: swap(0,1) changes -2 to 1 on frozen witness")
print("PASS: all six 1|5 mode flattenings have exact Q-rank 3")
print("PASS: unordered 3|3 flattening rank profile is 6:2,9:4,12:4")
print("PASS: rank 12 excludes every invertible-per-port transform to CP-rank<=3 / GenEQ-type pure-tensor normal form")
print("PASS: rank 12 excludes every invertible-per-port transform to two-plus-one domain separation {B,G}^6 union {R}^6, whose 3|3 rank is <=9")
print("SCOPE: symmetric real-domain-3 Holant dichotomy is NOT invoked as a hardness theorem because this signature is non-symmetric and the JANUS source network is restricted")
print("VERDICT: EXACT_F3_HOLOGRAPHIC_FLATTENING_RANK_NORMAL_FORM_BARRIER_ESTABLISHED")
print("FRONTIER: SEEK_A_GENUINELY_NONSYMMETRIC_ORDER_SENSITIVE_GRAPH_STRUCTURAL_CONTRACTION; DO_NOT_RETRY_GEN_EQ_OR_DOMAIN_SEPARATION_BY_LOCAL_INVERTIBLE_BASES")
print("P_VS_NP=OPEN; P_EQUALS_NP_ALGORITHM=NOT_CONSTRUCTED; E8_D1=EMPTY")
