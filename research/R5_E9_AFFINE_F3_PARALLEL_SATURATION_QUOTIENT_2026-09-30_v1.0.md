# R5 E9 — Affine F3 Parallel-Saturation Quotient

Date: 2026-09-30

Status:
`JANUS_EXACT_POLYNOMIAL_PREPROCESSOR__AFFINE_F3_PARALLEL_CLASSES__NO_D1_PROMOTION`

Parent:
`research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS IS AN EXACT POLYNOMIAL PREPROCESSOR FOR THE AFFINE F3 NOWHERE-ZERO FORM.
IT CAN PROVE UNSAT, PIN A LINEAR FUNCTIONAL, OR REMOVE DUPLICATE HYPERPLANES.
IT DOES NOT SOLVE THE PARALLEL-SIMPLE RESIDUAL IN GENERAL.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Input normal form

After solving `Ar=1` over `F3`, write every affine solution as

\[
r_i(\alpha)=c_i+a_i\alpha,
\qquad \alpha\in\mathbb F_3^d.
\]

Exact-One is SAT iff some `alpha` satisfies

\[
r_i(\alpha)\ne0\quad\forall i.
\]

Thus coordinate `i` forbids the affine hyperplane

\[
H_i=\{\alpha:a_i\alpha=-c_i\}.
\]

The problem is to decide whether these hyperplanes cover all of `F3^d`.

## 2. Canonical parallel classes

For nonzero `a_i`, normalize the linear functional projectively: multiply `(a_i,c_i)` by the inverse of the first nonzero coordinate of `a_i`.  The zero set is unchanged.

After normalization, all members of one parallel class have one common normal `a` and differ only by their forbidden offset

\[
a\alpha=b,
\qquad b\in\mathbb F_3.
\]

Let `F_a` be the set of distinct forbidden offsets in the class.

Because the field has exactly three elements, only three cases exist.

### Theorem APSQ-1 — one-offset class

If `|F_a|=1`, duplicate copies of the same affine hyperplane are semantically redundant and may be replaced by one copy.

### Theorem APSQ-2 — two-offset class pins the third value

If

\[
F_a=\{b_1,b_2\},
\]

then avoiding both hyperplanes is equivalent to the single linear equality

\[
\boxed{a\alpha=b_3}
\]

where `b_3` is the unique element of `F3 \ F_a`.

Hence a two-offset class is not a branch: it deterministically lowers the affine parameter dimension by one whenever the new equality is independent.

### Theorem APSQ-3 — three-offset class is UNSAT

If

\[
F_a=\mathbb F_3,
\]

then every parameter value satisfies one of the three hyperplane equations, so no nowhere-zero affine solution exists.  By AF3-1 the source is Exact-One UNSAT.

## 3. Constant-coordinate terminals

After imposing pins and reparameterizing, a coordinate may become constant.

For

\[
r_i(\gamma)=c_i
\]

with zero linear part:

```text
c_i = 0  -> UNSAT immediately;
c_i != 0 -> coordinate is permanently safe and can be deleted.
```

This is required for exact iteration.

## 4. Iterated saturation algorithm

The polynomial reducer is:

```text
INPUT: affine functions r_i(alpha)=c_i+a_i alpha over F3.

repeat:
    1. delete every safe nonzero constant coordinate;
    2. if a zero constant coordinate exists: return UNSAT;
    3. canonicalize every nonzero normal a_i projectively;
    4. group constraints by canonical normal;
    5. within each group keep only distinct forbidden offsets;

       3 offsets -> return UNSAT;
       2 offsets -> emit the equality a alpha = remaining value;
       1 offset  -> keep one representative hyperplane;

    6. solve all emitted equalities by Gaussian elimination;
       inconsistent -> return UNSAT;
       otherwise substitute an affine parameterization of their solution space
       into every surviving affine function;

until no two-offset class remains.
```

Each nonterminal saturation round either strictly lowers parameter dimension or removes duplicate constraints.  Dimension is at most `n` and the number of constraints is at most `n`, so there are only polynomially many rounds and every round uses polynomial-size `F3` linear algebra.

### Theorem APSQ-4 — exactness

At every iteration, the reduced system has a nowhere-zero parameter point iff the incoming system does.

Proof is casewise from APSQ-1/2/3 and exact affine substitution under the pin equalities.  Therefore SAT witnesses lift by reversing the stored affine substitutions, and every UNSAT terminal is exact.

## 5. Source-specific geometric form

For a row-weight-three source, `1 in ker_F3(A)`.  Choose a kernel basis whose first column is `1` and write its coordinate rows as

\[
b_i=(1,u_i),
\qquad u_i\in AG(d-1,3).
\]

For every source triple `{i,j,k}`, `AB=0` gives

\[
\boxed{u_i+u_j+u_k=0.}
\]

Over `F3`, this has a sharp geometric meaning:

- if two of `u_i,u_j,u_k` are equal, then all three are equal;
- otherwise the three points are exactly the three points of one affine line in `AG(d-1,3)`.

Thus after the parallel-saturation quotient removes repeated affine-normal information, the residual source is a 3-regular partial affine triple geometry: source clauses are affine lines of three distinct kernel points whenever the clause is nondegenerate in the quotient.

For a particular affine solution `r^(0)`, put `c_i=r_i^(0)`.  Every source row also obeys

\[
\boxed{c_i+c_j+c_k=1.}
\]

The remaining universal question is therefore an affine-function avoidance problem on this source-generated partial geometry.

## 6. Frozen controls

### PG15 SAT

For the canonical PG15 source:

```text
dim ker_F3(A) = 4.
15 coordinate constraints
-> 11 distinct parallel classes after exact duplicate removal.
```

No class has two distinct forbidden offsets, so no false pin is produced and the positive hard control remains a four-dimensional residual.  The four known Exact-One witnesses remain available.

### Singular n=15 UNSAT control

For the frozen singular UNSAT source:

```text
dim ker_F3(A) = 1.
```

The affine parameter is one scalar.  Its coordinate constraints contain all three forbidden offsets on the same normalized normal, so APSQ-3 returns `UNSAT` immediately.  This matches the exact exhaustive control from AF3.

## 7. What this closes and what it does not

Closed:

```text
repeated identical affine hyperplanes        -> deduplicate
parallel classes with two offsets             -> deterministic pin
parallel classes with all three offsets       -> exact UNSAT
new parallels created after substitution      -> iterate to saturation
witness reconstruction through substitutions -> polynomial
```

Still open:

```text
parallel-simple residual:
  every surviving normalized normal occurs with exactly one forbidden offset,
  no constant-zero coordinate,
  affine parameter dimension may remain large.
```

Generic hyperplane-cover counting does not solve this residual.  Full-span blocking configurations over `F3` can remain small relative to the ambient dimension, so a universal `large d => SAT` claim is not admitted.

## 8. New live gate

Freeze the residual as

```text
R5_E9_AFFINE_F3_PARALLEL_SIMPLE_PARTIAL_GEOMETRY_GATE_V1
```

Required PASS:

```text
INPUT:
  the saturated affine-F3 avoidance system from a linear-cubic source.

PROMISE:
  one forbidden offset per normalized nonzero functional;
  all forced affine equalities already substituted;
  source triples retain the induced affine-line relations.

OUTPUT in deterministic polynomial time:
  either an avoiding parameter alpha and Exact-One witness,
  or an exact polynomially constructible cover certificate.
```

Candidate donors now have to use the source-generated affine-line geometry, not only generic hyperplane counting.

## 9. Ceiling

```text
AFFINE F3 PARALLEL SATURATION
= EXACT / POLYNOMIAL

TWO-OFFSET CLASS
= DETERMINISTIC DIMENSION-REDUCING PIN

THREE-OFFSET CLASS
= EXACT UNSAT

PG15
= SURVIVES AS 11-HYPERPLANE d=4 RESIDUAL

FROZEN SINGULAR UNSAT
= CLOSED IMMEDIATELY BY THREE-OFFSET CLASS

PARALLEL-SIMPLE RESIDUAL
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
