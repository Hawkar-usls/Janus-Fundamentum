# R5 E9 — Rational-Tope Defect Syndrome Projective Filter

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_CROSS_FIELD_PROJECTIVE_PARITY_FILTER__FPT_IN_RESIDUAL_PARITY_NULLITY__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_PROJECTIVE_RATIO_PINNING_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_SOURCE_KERNEL_POLYNOMIAL_NAVIGATION_SHELL_2026-09-28_v1.0.md`
- `research/R5_E9_AFFINE_COSET_CIRCUIT_AUGMENTATION_GLOBAL_OPTIMALITY_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_rational_tope_defect_syndrome_projective_filter.py`

Scientific ceiling:

```text
FOR EVERY FULL-SUPPORT RATIONAL-KERNEL TOPE, THE BINARY SYNDROME

    d = 1 + A x  (mod 2),   x_i = 1[y_i>0],

IS EXACTLY THE INDICATOR OF THE SOURCE ROWS OF SIGN TYPE ++-.
THEREFORE

    |d| = 3p-n,
    BOUNDARY <=> d=0.

AFTER COLLAPSING RATIONAL PROJECTIVE KERNEL-ROW CLASSES, ALL POSSIBLE
BOUNDARY TOPES LIE IN ONE EXPLICIT AFFINE GF(2) SUBSPACE

    G z = d0,   G=A R (mod 2).

IF ITS NULLITY kappa IS O(log n), ENUMERATING THAT AFFINE SUBSPACE AND
TESTING EACH SIGN PATTERN BY RATIONAL LP IS A DETERMINISTIC POLYNOMIAL
EXACT-ONE DECIDER WITH WITNESS RECONSTRUCTION.

THIS IS A NEW EXACT FPT/POLY TERMINAL, NOT A UNIVERSAL D1 SOLUTION.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Source and rational-kernel signs

Let

```text
A in {0,1}^{n x n}
```

be a cubic square positive Exact-One source matrix. Every row and every column
has weight three. Let

```text
B in Q^{n x d}
```

have columns forming a basis of `ker_Q(A)`. For a full-support coefficient
vector `alpha`, write

```text
y = B alpha,
x_i = 1[y_i>0],
p = |x|.
```

Because `Ay=0`, the three nonzero coordinates of `y` in every source row sum to
zero. Hence every row has exactly one of the two sign types

```text
+--
++-
```

up to permutation.

The earlier Tukey-depth theorem counted the second type and proved

```text
#(++- rows) = 3p-n.
```

The present note identifies that count with an exact binary syndrome.

## 2. Defect syndrome identity

Work over `F2` and define

```text
d(x) = 1 + A x.
```

On a source row:

- sign type `+--` has one positive coordinate, so `(Ax)_r=1` and `d_r=0`;
- sign type `++-` has two positive coordinates, so `(Ax)_r=0` and `d_r=1`.

Therefore:

### Theorem RTDS-1 — exact defect syndrome

For every full-support rational-kernel tope,

\[
\boxed{d(x)=\mathbf 1+A x\pmod 2}
\]

is exactly the indicator vector of the `++-` source rows. Consequently

\[
\boxed{|d(x)|=3p-n.}
\]

In particular,

\[
\boxed{
 p=n/3
 \iff d(x)=0
 \iff A x=\mathbf1\pmod2.
}
\]

Because a rational-kernel tope has only one-positive or two-positive rows, the
last parity condition is stronger here than it is for an arbitrary Boolean
vector: `Ax=1 (mod 2)` forces exactly one positive coordinate in every source
row. Hence its positive set is an integer Exact-One witness.

Thus the real-arrangement boundary and the binary affine syndrome meet exactly,
not approximately.

## 3. Projective-class toggle coordinates

Partition the nonzero rows of `B` into their rational projective classes

```text
C_1,...,C_q,
```

where rows belong to the same class iff they are nonzero rational scalar
multiples. Choose any full-support base tope `alpha_0` and let

```text
x_0 = 1[B alpha_0 > 0].
```

Define the class-incidence matrix

\[
R\in\mathbb F_2^{n\times q},
\qquad
R_{ij}=1 \iff i\in C_j.
\]

Every other chamber of the simplified projective arrangement has a unique
projective toggle vector

```text
z in F2^q
```

relative to the base chamber: `z_j=1` exactly when chamber and base lie on
opposite sides of projective hyperplane class `C_j`.

Flipping one projective class reverses the raw sign of every original coordinate
in that class, including antiparallel representatives. Therefore the raw sign
bits of any chamber obey the exact identity

\[
\boxed{x(z)=x_0+Rz\pmod2.}
\]

This identity is purely combinatorial once the rational projective classes have
been computed.

## 4. Boundary becomes one affine GF(2) filter

Put

```text
G  = A R       (mod 2),
d0 = 1 + A x0  (mod 2).
```

Substituting `x(z)=x0+Rz` into RTDS-1 gives

\[
\boxed{d(z)=d_0+Gz.}
\]

Therefore:

### Theorem RTDS-2 — projective parity filter

Every boundary chamber satisfies

\[
\boxed{Gz=d_0.}
\]

Conversely, if a projective sign pattern with toggle vector `z` is realizable as
a full-support rational-kernel chamber and satisfies `Gz=d0`, then its defect
syndrome is zero and its positive set is an Exact-One witness.

Thus Exact-One is equivalent to

```text
there exists z with Gz=d0
whose projective sign pattern is realizable by the rational arrangement.
```

The Boolean linear system is a necessary filter for arbitrary sign patterns and
is necessary-and-sufficient after the rational sign pattern is certified
realizable.

## 5. Exact FPT algorithm

Let

```text
kappa = dim ker_F2(G) = q-rank_F2(G).
```

Gaussian elimination over `F2` does one of two things in polynomial time:

1. proves `Gz=d0` inconsistent, which is an immediate exact UNSAT certificate;
2. returns one solution `z_*` and a basis `v_1,...,v_kappa` of `ker(G)`.

In the second case every parity-compatible projective target is

\[
z=z_*+\sum_{j=1}^{\kappa}\lambda_jv_j,
\qquad \lambda_j\in\mathbb F_2.
\]

Enumerate all `2^kappa` such vectors. For each one, ask whether its desired
projective sign vector is realizable. If `h_1,...,h_q` are oriented rational
representatives of the projective kernel rows and `s_j in {+1,-1}` is the
desired sign, realizability is the homogeneous strict system

\[
s_j h_j\alpha>0\quad(j=1,...,q).
\]

As in the navigation-shell theorem, strict feasibility is equivalent by scaling
to the rational LP

\[
s_j h_j\alpha\ge1\quad(j=1,...,q).
\]

If one candidate is feasible, RTDS-2 reconstructs the Exact-One witness from the
positive coordinates of `B alpha`. If none is feasible, no boundary chamber
exists and the source is UNSAT.

Therefore:

### Theorem RTDS-3 — FPT/poly terminal

The projective-boundary problem is deterministically solvable in

```text
2^kappa * poly(input bit length)
```

time, with exact witness reconstruction.

In particular, whenever

```text
kappa = O(log n),
```

the route is polynomial.

This strictly combines two earlier representations: rational projective
compression reduces the sign-coordinate count, while binary syndrome algebra
filters the surviving projective patterns before any arrangement search.

## 6. Relation to previous nullity routers

If every rational projective class is a singleton, then `R=I` and

```text
G=A (mod 2),
kappa=nullity_F2(A).
```

So RTDS-3 contains ordinary binary-nullity enumeration as a special case.

When rational projective equality classes exist, `q<n` and `G=AR` acts on class
toggles rather than raw coordinates. The residual `kappa` can therefore be
strictly smaller than a raw-coordinate parity search dimension.

The theorem does not assert that `kappa` is always logarithmic. A universal D1
promotion would require either proving such a bound after admitted preprocessing
or solving the large-`kappa` residual by another polynomial mechanism.

## 7. Exact PG15 positive control

Use the frozen `PG15_SAT_R11` source and its rational kernel basis. Its eleven
rational projective classes are

```text
C1 ={1,5}
C2 ={2,6}
C3 ={3}
C4 ={4}
C5 ={7}
C6 ={8,12}
C7 ={9}
C8 ={10}
C9 ={11,15}
C10={13}
C11={14}.
```

Take

```text
alpha0=(-1,2,2,-2).
```

Then

```text
p(x0)=6,
|d0|=3=3*6-15.
```

For the exact class-incidence matrix `R`, the checker proves

```text
q                 = 11,
rank_F2(G)         = 7,
kappa              = 4,
# solutions Gz=d0  = 16.
```

So the cross-field filter reduces the complete projective target search to only
sixteen parity-compatible sign patterns.

The checker then gives exact certificates for all sixteen candidates:

- four are realizable, by the four frozen rational coefficient vectors for the
  four Exact-One witnesses;
- each of the remaining twelve is unrealizable because three desired signed
  projective normals sum exactly to zero, which is incompatible with all three
  corresponding strict inequalities being positive.

Thus the sixteen parity candidates collapse exactly to the four known boundary
topes, with no floating-point or sampled-arrangement argument.

## 8. Why this is not yet P=NP

The hostile residual is now precise:

```text
large kappa
+
affine parity-compatible projective sign family
+
rational arrangement realizability.
```

Enumerating `2^kappa` is forbidden when `kappa` is superlogarithmic. The prime
and high-nullity families already warn that large algebraic dimensions can
persist under strong graph structure.

The next universal step must therefore exploit additional structure of the
affine solution space and the oriented arrangement jointly; it cannot merely
rename exhaustive character enumeration.

## 9. Sharpened live gate

Freeze

```text
R5_E9_PROJECTIVE_PARITY_SLICE_LARGE_KAPPA_GATE_V1
```

Input:
- cubic square positive Exact-One source surviving admitted terminals;
- rational projective class matrix `R`;
- `G=AR (mod 2)`;
- an affine parity slice `Z={z:Gz=d0}` of superlogarithmic dimension;
- exact rational projective hyperplane representatives.

PASS requires one of:

1. a deterministic polynomial algorithm deciding whether `Z` contains a
   realizable tope sign vector;
2. a polynomial contraction reducing `kappa` while preserving boundary
   realizability and reconstructing witnesses;
3. a polynomially verifiable certificate that no `z in Z` is realizable;
4. a different complete universal polynomial solver satisfying the E8-DIRECT
   contract.

Forbidden pseudo-progress:
- enumerating all `2^kappa` vectors for superlogarithmic `kappa`;
- treating parity compatibility alone as rational realizability;
- using floating-point sign sampling as an exact certificate;
- promoting the PG15 finite collapse to an asymptotic theorem;
- claiming D1 or P=NP from this FPT terminal.

## 10. Ceiling

```text
RATIONAL-TOPE DEFECT SYNDROME
= 1 + A x (mod 2)
= EXACT ++- ROW INDICATOR

DEFECT COUNT
= 3p-n

BOUNDARY
<=> DEFECT SYNDROME ZERO

PROJECTIVE TOGGLE FORM
x(z)=x0+Rz

BOUNDARY PARITY FILTER
Gz=d0, G=AR (mod 2)

RESIDUAL PARAMETER
kappa=q-rank_F2(G)

EXACT RUN TIME
2^kappa * poly(input)

kappa=O(log n)
=> POLYNOMIAL EXACT-ONE TERMINAL

PG15
q=11, rank(G)=7, kappa=4
16 parity candidates -> exactly 4 realizable boundary topes

LARGE-kappa PARITY-SLICE REALIZABILITY
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```