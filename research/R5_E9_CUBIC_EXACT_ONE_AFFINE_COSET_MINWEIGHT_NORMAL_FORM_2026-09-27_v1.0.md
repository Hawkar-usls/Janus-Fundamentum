# R5 E9 — Cubic Exact-One Affine-Coset Minimum-Weight Normal Form

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_REPRESENTATION_CHANGE__THEOREM_CANDIDATE__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_cubic_exact_one_affine_coset_minweight.py`

Parents:
- `R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`
- `R5_E9_TRANSLATION_STABILIZER_REPAIR_ACTION_CALCULUS_2026-09-23_v1.0.md`
- `R5_E9_LINEAR_EXACT_ONE_PARTIAL_WDR_CLOSURE_2026-09-27_v1.0.md`
- `R5_E9_UNIVERSAL_SELECTOR_INTERNAL_ANTI_LOOP_BINDING_2026-09-27_v1.0.md`

Scientific firewall:

```text
THIS IS AN EXACT REPRESENTATION CHANGE.
IT IS NOT A POLYNOMIAL SOLVER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `H=(V,E)` be a 3-uniform `d`-regular hypergraph with

```text
|V| = n,
|E| = m,
```

and let `A` be its `m x n` incidence matrix.

Regularity and 3-uniformity give

```text
d n = 3 m.
```

For a Boolean vector `x in {0,1}^n`, the Exact-One condition is

```text
for every e in E:
    sum_{v in e} x_v = 1.
```

Reduce only the row equations modulo two.  The affine parity relaxation is

```text
A x = 1  (mod 2).
```

Because every row has exactly three ones,

```text
A 1 = 1  (mod 2),
```

so this affine system is always consistent.  In particular the all-ones vector
is always a parity solution.  The hard content is therefore not affine
feasibility.

## 2. Exact defect identity

Take any parity solution

```text
A x = 1  (mod 2).
```

Every hyperedge contains either one or three selected vertices.  Define

```text
t(x) = number of hyperedges containing three selected vertices.
```

Summing row cardinalities in two ways gives

```text
sum_e sum_{v in e} x_v = m + 2 t(x),
```

because every row contributes `1`, plus an extra `2` exactly when it is an
all-ones triple.

On the other hand every selected vertex is counted in exactly `d` rows, so

```text
d |x| = m + 2 t(x).
```

Using `m = d n / 3`,

```text
t(x) = (d/2) ( |x| - n/3 ).
```

This identity is integral automatically on every parity solution.

### Theorem ACW-1 — affine-coset minimum-weight equivalence

For every Boolean `x`,

```text
x is an Exact-One witness
iff
A x = 1 (mod 2)
and
|x| = n/3.
```

Equivalently, among all points in the affine coset

```text
C_1 = {x in F_2^n : A x = 1},
```

the universal lower bound on Hamming weight is

```text
|x| >= n/3,
```

and equality holds exactly at the Exact-One witnesses.

### Proof

If `x` is Exact-One, every row has sum one, so parity holds and counting gives
`d|x|=m`, hence `|x|=m/d=n/3`.

Conversely, if parity holds then ACW-1's defect identity gives

```text
t(x) = (d/2)(|x|-n/3).
```

If `|x|=n/3`, then `t(x)=0`; every odd row therefore has sum one rather than
three, so `x` is Exact-One.  QED.

## 3. Cubic specialization

For the current cubic carrier `d=3`, hence `m=n` and

```text
t(x) = (3|x|-n)/2.
```

Thus

```text
SAT_EXACT_ONE(H)
iff
min { |x| : A x = 1 (mod 2) } = n/3.
```

The optimization objective is not an approximation: it counts the exact number
of all-ones clause defects up to the fixed linear factor above.

This gives a canonical potential on the affine carrier:

```text
rho(x) = |x|
```

or equivalently

```text
rho_defect(x) = t(x).
```

Both decrease together on parity-preserving moves.

## 4. Kernel-flip calculus

Let `x` be any parity solution and let

```text
z in ker_F2(A).
```

Then

```text
x' = x XOR z
```

is another parity solution.

Its Hamming-weight change is exactly

```text
|x XOR z| - |x|
=
|z| - 2 |supp(x) intersect supp(z)|.
```

Therefore `z` is a strict weight-improving kernel move iff

```text
|supp(x) intersect supp(z)| > |z|/2.
```

The Exact-One defect changes by

```text
t(x XOR z)-t(x)
=
(d/2)(|x XOR z|-|x|).
```

So every affine-preserving ranked repair on this carrier can be audited against
an exact integer progress measure.

This is useful for `R5/R6`: a proposed structural dominance / ranked macro that
acts only through affine kernel flips has no ambiguity about whether it made
real progress.

## 5. All-ones start state

The vector

```text
1^n
```

is always a parity solution and has weight `n`.

If `y` is an Exact-One witness, then

```text
z = 1 XOR y
```

lies in `ker_F2(A)` and

```text
|z| = 2n/3,
1 XOR z = y.
```

Thus every satisfiable instance has a global kernel descent from the trivial
all-ones parity point to the minimum-weight sphere.

The missing algorithmic object is the deterministic polynomial synthesis of an
appropriate descent direction, not its existential existence.

## 6. Relation to the existing rational kernel-word normal form

The prior exact normal form uses

```text
w = 3x - 1,
w in {-1,2}^n,
A w = 0 over Q.
```

The present theorem is a different exact projection of the same source problem:

```text
A x = 1 over F_2
+
minimum Hamming weight n/3.
```

The rational form exposes rational nullity and the `I+P+Q` overlay.
The binary form exposes a linear code / affine coset plus a global weight
objective and therefore a natural ranked-repair potential.

Neither representation is claimed to be easier in general.

For cubic incidence, the existing three-perfect-matching factorization gives

```text
A = I + P + Q,
```

so the binary carrier may equivalently be written

```text
(I+P+Q)x = 1 (mod 2),
minimize |x|.
```

## 7. Coding-theoretic anti-loop

This representation enters a classical hard algorithmic territory.
For a general binary parity-check matrix `H`, syndrome decoding asks for a
low-Hamming-weight vector satisfying

```text
H x = s.
```

Berlekamp, McEliece, and van Tilborg proved the general decoding problem and
the general codeword-weight problem NP-complete:

- E. R. Berlekamp, R. J. McEliece, H. C. A. van Tilborg,
  *On the Inherent Intractability of Certain Coding Problems*,
  IEEE Transactions on Information Theory 24(3), 384-386 (1978),
  DOI `10.1109/TIT.1978.1055873`.

The present theorem does not import general syndrome-decoding hardness as a
lower bound on the restricted JANUS matrices.  Instead it records that a naive
claim of "linear algebra solves the affine carrier" is invalid: Gaussian
elimination solves coset membership, not the minimum-weight slice.

Independently, cubic monotone Positive 1-in-3 / 3-regular 3-uniform exact cover
is a standard NP-complete source class, so a polynomial solver for the full
restricted minimum-weight carrier above would already be a P=NP-level result.

## 8. Exact finite controls

The checker validates two small controls by exhaustive enumeration, explicitly
marked `OFFLINE_FALSIFIER_ONLY`.

### Fano-7

The Fano plane is 3-uniform and cubic but `n=7` is not divisible by three.
It has parity solutions, including all-ones, but no Exact-One solution.
The checker verifies the defect identity on every parity point.

### Affine 3x3

Rows, columns, and one diagonal parallel class over `Z_3` give a connected
cubic linear satisfiable control on nine vertices.

The checker finds:

```text
parity weights = {3,9},
Exact-One solution count = 3,
Exact-One weight = 3,
all-ones -> Exact-One kernel flip support = 6.
```

Again this finite enumeration is a checker, not the proof and not an E8
algorithm.

## 9. New attack frontier

The representation change turns the surviving selector question into the exact
gate

```text
R5_E9_AFFINE_COSET_MINWEIGHT_DESCENT_GATE_V1
```

Input:

```text
3-uniform d-regular incidence A,
C_1 = {x : A x = 1 mod 2}.
```

Target:
construct in deterministic polynomial time either

1. a parity-preserving kernel move with strict certified weight decrease;
2. a nonlocal quotient that reduces the exact minimum-weight problem while
   preserving witness reconstruction;
3. a decomposition whose total solve cost is polynomial;
4. direct proof that the lower bound `n/3` is or is not attained.

Forbidden:

- enumerate `ker A` when nullity is superlogarithmic;
- search all Hamming-weight `n/3` points;
- invoke syndrome decoding / exact cover / SAT as an oracle;
- claim progress from Gaussian elimination alone;
- use existential existence of an improving kernel vector as if it were a
  polynomial construction.

## 10. Ceiling

```text
AFFINE PARITY FEASIBILITY
= TRIVIAL YES VIA ALL-ONES

EXACT-ONE
= AFFINE COSET MINIMUM WEIGHT n/3

DEFECT POTENTIAL
= t(x) = (d/2)(|x|-n/3)

KERNEL MOVE PROGRESS
= EXACTLY AUDITABLE BY HAMMING WEIGHT

POLYNOMIAL MINWEIGHT SYNTHESIS
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
