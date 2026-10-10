# R5 E9 — Rational-Kernel Projective-Ratio Pinning Quotient

Date: 2026-09-28

Status: `JANUS_DERIVED_EXACT_RATIONAL_PROJECTIVE_RATIO_TERMINAL_AND_PINNING_QUOTIENT__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_TUKEY_DEPTH_BOUNDARY_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_SOURCE_KERNEL_POLYNOMIAL_NAVIGATION_SHELL_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_rational_kernel_projective_ratio_pinning.py`

Scientific ceiling:

```text
FOR A SAT SOURCE, TWO PROPORTIONAL NONZERO ROWS OF A RATIONAL KERNEL-BASIS
MATRIX MAY HAVE SCALAR RATIO ONLY 1, -2, OR -1/2.

RATIO OUTSIDE {1,-2,-1/2}
=> POLYNOMIAL UNSAT TERMINAL.

RATIO 1
=> EXACT BOOLEAN EQUALITY.

RATIO -2 OR -1/2
=> ABSOLUTE 1/0 PINNING OF THE TWO COORDINATES.

AFTER EXHAUSTIVE CLASSIFICATION, EVERY UNPINNED RATIONAL PROJECTIVE CLASS
COLLAPSES TO ONE BOOLEAN EQUALITY VARIABLE WITH ITS MULTIPLICITY.

THIS IS A POLYNOMIAL PREPROCESSOR / REPRESENTATION QUOTIENT, NOT A
UNIVERSAL POLYNOMIAL SAT ALGORITHM.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let `A in {0,1}^{n x n}` be a cubic square positive Exact-One source and let

```text
B in Q^{n x d}
```

be any rational matrix whose columns form a basis of `ker_Q(A)`.  Write `b_i`
for row `i` of `B`.

The already proved cubic-kernel normal form is

\[
A x=\mathbf1,\ x\in\{0,1\}^n
\iff
\exists y\in\ker_{\mathbb Q}(A)\cap\{-1,2\}^n,
\]

with the exact bijection

```text
y=3x-1,
x=(y+1)/3.
```

Every kernel vector has the form `y=B alpha`.

A zero row `b_i=0` was already frozen as an UNSAT terminal because every
kernel vector then has `y_i=0`, impossible for a SAT word in `{-1,2}^n`.
Assume here that all rows are nonzero.

## 2. Exact pair theorem

Suppose two rational kernel rows are proportional:

\[
b_i=\lambda b_j,
\qquad \lambda\in\mathbb Q^*.
\]

Then every rational kernel vector obeys

\[
y_i=\lambda y_j.
\]

If the source is SAT, take its exact kernel word `y=3x-1`.  Both `y_i,y_j`
belong to `{-1,2}`, so

\[
\lambda=\frac{y_i}{y_j}
\in
\left\{
\frac{-1}{-1},\frac2{2},\frac2{-1},\frac{-1}{2}
\right\}.
\]

Therefore:

### Theorem RKPR-1 — allowed projective ratios

\[
\boxed{
A\text{ SAT and }b_i=\lambda b_j
\Longrightarrow
\lambda\in\{1,-2,-1/2\}.
}
\]

Hence any proportional pair with

```text
lambda notin {1,-2,-1/2}
```

is an exact polynomially checkable UNSAT certificate.

## 3. Ratios are semantic, not merely geometric

The three allowed ratios have exact Boolean meaning.

### Ratio 1

If `b_i=b_j`, every kernel vector has `y_i=y_j`, hence every Exact-One witness
has

```text
x_i=x_j.
```

So equal rational kernel rows form an exact Boolean equality class.

### Ratio -2

If

```text
b_i=-2 b_j,
```

then on a SAT word the only possible pair in `{-1,2}^2` is

```text
(y_i,y_j)=(2,-1).
```

Therefore

```text
x_i=1,
x_j=0.
```

The pins are absolute: they hold for every Exact-One witness.

### Ratio -1/2

Symmetrically,

```text
b_i=-(1/2)b_j
```

forces

```text
(y_i,y_j)=(-1,2),
x_i=0,
x_j=1.
```

Thus antiparallel projective rows are not a harmless orientation detail at the
Boolean boundary. Their exact rational scale determines forced Boolean values.

## 4. Complete structure of one rational projective class

Let `C` be one geometric projective class: all rows `{b_i:i in C}` are nonzero
rational scalar multiples of one another.

For SAT compatibility every pairwise scalar ratio must belong to

```text
{1,-2,-1/2}.
```

This has a strong consequence.

### Theorem RKPR-2 — two-level class dichotomy

Every SAT-compatible rational projective class is exactly one of:

1. **equality class** — all rows are identical;
2. **pinned two-level class** — there are exactly two distinct row vectors
   `v` and `-2v` (equivalently `v` and `-(1/2)v` depending on which vector is
   chosen as reference).

No third scalar level is possible.

### Proof

Normalize one row to scalar `1`. Every other normalized scalar must be one of
`1,-2,-1/2`.  But the ratio between `-2` and `-1/2` equals `4`, which is not an
allowed pairwise ratio. Hence both nontrivial scalar levels cannot coexist.
QED.

In a two-level class, the pins are fixed for the entire class:

```text
rows v       -> one Boolean value,
rows -2 v    -> the opposite Boolean value,
```

with the orientation determined by `b_i=-2b_j => x_i=1,x_j=0`.

Consequently every unpinned surviving projective class consists of **exactly
equal** rational rows and can be represented by one Boolean variable carrying
the class multiplicity.

## 5. Basis invariance

Replace the kernel basis by another basis:

```text
B' = B T,
```

where `T in GL_d(Q)`.

If `b_i=lambda b_j`, then

```text
b_i T = lambda (b_j T).
```

Conversely, since `T` is invertible, proportionality and its exact scalar ratio
cannot be created or destroyed by the basis change.

Therefore:

```text
projective classes,
exact proportionality ratios,
equality classes,
ratio pins,
illegal-ratio UNSAT certificates
```

are all intrinsic invariants of the rational kernel subspace, not artifacts of
one Gaussian-elimination basis.

## 6. Polynomial quotient algorithm

The complete preprocessing pass is deterministic polynomial time.

1. Compute a rational kernel basis `B` by exact Gaussian elimination.
2. Apply the already frozen full-rank / zero-row terminals.
3. Partition nonzero rows into projective classes by exact cross multiplication.
4. Within each class compute exact rational row ratios.
5. If any pair has ratio outside `{1,-2,-1/2}`, return UNSAT.
6. If a class has two scalar levels, record the forced 0/1 pins.
7. If a class has one level, merge all its coordinates into one Boolean
   equality variable.
8. Substitute the pins/equalities into the original Exact-One rows and run
   ordinary exact-one propagation to a fixpoint:
   - a row already containing one pinned `1` forces every other participating
     unpinned variable to `0`;
   - more than one pinned `1` is a contradiction;
   - if an equality variable occurs twice or three times in one row, it cannot
     be `1` unless the row arithmetic permits it; in the present `=1` rows a
     coefficient at least two forces that variable to `0`;
   - once all but one unit-coefficient variable of a row are zero, the last is
     forced to `1`.

Every operation is exact and every merge/pin has a constant-size reconstruction
record.  If no contradiction appears, the quotient has precisely the same
Boolean Exact-One witness set after expanding merged equality variables and
restoring pins.

This may leave an unbounded residual and is therefore not a completeness claim.

## 7. Positive rank-8 / nullity-1 linear-cubic control

Freeze the following `n=9` linear cubic source:

```text
(1,8,9)
(5,6,9)
(1,2,5)
(4,6,8)
(2,7,9)
(2,3,8)
(3,4,5)
(1,4,7)
(3,6,7)
```

Every row and column has degree three and distinct rows intersect in at most one
coordinate.

Exact rational rank is

```text
rank_Q(A)=8,
nullity_Q(A)=1.
```

Its unique Exact-One witness is

```text
X={5,7,8}.
```

The rational kernel is generated by

```text
g=3 1_X-1
 =(-1,-1,-1,-1,2,-1,2,2,-1).
```

Because the kernel is one-dimensional, all nine kernel-basis rows lie in one
geometric projective class. Their only scalar levels are `-1` and `2`, whose
ratio is `-2`.

RKPR-2 therefore pins the entire class and reconstructs exactly

```text
X={5,7,8}
```

without enumerating Boolean assignments.

This is the positive pinning control.

## 8. Frozen singular rank-14 UNSAT control collapses immediately

Reuse the frozen connected cubic UNSAT control with

```text
n=15,
rank_Q(A)=14,
nullity_Q(A)=1,
```

whose rational kernel generator is

```text
g=(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

Again every nonzero kernel row lies in one geometric projective class.  But
coordinates with values `1` and `4` have exact row ratio

```text
lambda=4.
```

Since

```text
4 notin {1,-2,-1/2},
```

RKPR-1 gives an immediate exact UNSAT certificate.

Thus this old hostile control no longer needs chamber-depth optimization: the
new local rational projective-ratio terminal kills it before navigation.

## 9. PG15 SAT equality quotient

On the frozen `PG15_SAT_R11` rational kernel basis, the nontrivial projective
classes are

```text
{1,5}, {2,6}, {8,12}, {11,15}.
```

In each pair the two rational kernel rows are **equal**, ratio `1`.  There are no
mixed-ratio classes and hence no forced pins.

RKPR-1 therefore accepts the SAT control and yields four exact Boolean equality
relations:

```text
x1=x5,
x2=x6,
x8=x12,
x11=x15.
```

The raw 15 Boolean coordinates collapse to 11 equality variables before any
tope navigation.  This is a strict exact representation contraction on the
positive control, although the remaining 11-variable weighted/equality quotient
is not claimed polynomially solvable in general.

## 10. Prior-art / anti-loop boundary

The broad use of linear-algebra kernels for positive 1-in-3 SAT is known, and
bounded-entry nullspace questions remain hard in related regular graph classes.
For example Dehghan, Sadeghi and Ahadi, *Not-All-Equal and 1-in-Degree
Decompositions: Algorithmic Complexity and Applications*, Algorithmica 80
(2018), DOI `10.1007/s00453-018-0412-y`, show NP-completeness of related
regular-bipartite 1-in-degree/nullspace formulations and derive hardness for
finding nullspace vectors with entries in `{±1,±2}`.

Therefore RKPR-1/RKPR-2 are deliberately scoped as **local exact preprocessing
invariants**. They do not imply that bounded-entry kernel feasibility is
polynomial in general, and no literature novelty claim is made here.

The internal anti-loop audit also distinguishes this theorem from:
- cubic source-boundary pinning gadgets, which construct external forcing
  contexts;
- rooted series-pair contraction, which uses binary-matroid 2-cocircuits;
- binary-kernel signature classes, which identify equality over `F2`.

RKPR uses the exact **rational** scalar ratio of coordinate functionals on
`ker_Q(A)` and the special two-value boundary alphabet `{-1,2}`.

## 11. Sharpened live gate

Insert RKPR before the source-kernel navigation shell.

After exhaustive ratio classification and propagation, the hard residual must
satisfy:

```text
no zero rational kernel row,
no illegal proportional-row ratio,
no unpropagated -2/-1/2 projective pin,
every remaining nontrivial rational projective class = exact row equality,
all immediate Exact-One pin consequences exhausted.
```

Freeze

```text
R5_E9_RATIONAL_PROJECTIVE_QUOTIENTED_BOUNDARY_DIRECTION_GATE_V1
```

A PASS still requires a deterministic polynomial algorithm for the surviving
weighted/equality-quotiented boundary problem, a polynomial UNSAT certificate,
or another complete exact universal route.

## 12. Ceiling

```text
SAT-COMPATIBLE PROPORTIONAL RATIONAL KERNEL-ROW RATIOS
= {1,-2,-1/2}

RATIO 1
= BOOLEAN EQUALITY

RATIO -2 OR -1/2
= ABSOLUTE BOOLEAN PINS

ANY OTHER RATIO
= UNSAT

SAT-COMPATIBLE PROJECTIVE CLASS
= ONE EQUALITY LEVEL
  OR TWO PINNED LEVELS WITH RATIO -2

NULLITY-1 n=9 SAT CONTROL
= COMPLETELY PINNED / UNIQUE WITNESS RECOVERED

SINGULAR RANK-14 UNSAT CONTROL
= KILLED BY RATIO 4

PG15 SAT CONTROL
= 15 COORDINATES -> 11 EQUALITY VARIABLES

GENERAL QUOTIENTED BOUNDARY DIRECTION ORACLE
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```