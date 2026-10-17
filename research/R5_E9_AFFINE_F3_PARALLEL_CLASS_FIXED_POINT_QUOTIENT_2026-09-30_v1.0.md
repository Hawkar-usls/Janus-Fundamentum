# R5 E9 — Affine F3 Parallel-Class Fixed-Point Quotient

Date: 2026-09-30

Status:
`JANUS_EXACT_POLYNOMIAL_CONTRACTION__TERNARY_AFFINE_PARALLEL_CLASSES__NO_D1_PROMOTION`

Parent:
`research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`

## 1. Setting

For a row-weight-three Exact-One source A, solve over F3

    A r = 1.

If inconsistent, Exact-One is UNSAT. Otherwise write every affine solution as

    r = r0 + B alpha,

where the columns of B form ker_F3(A), alpha in F3^d, and b_i denotes row i of B.
By AF3-1,

    Exact-One SAT
    iff
    exists alpha such that r0_i + b_i alpha != 0 for every coordinate i.

Thus each coordinate with b_i != 0 forbids one affine hyperplane.

## 2. Exact projective normalization

For b_i != 0 choose the unique scalar lambda_i in F3^* such that

    b_i = lambda_i v_i

and the first nonzero coordinate of v_i is 1.  The zero-coordinate condition is

    r0_i + lambda_i v_i alpha = 0,

or equivalently

    v_i alpha = c_i,

where

    c_i = -r0_i / lambda_i in F3.

Group all coordinates with the same projective normal v.  Let C_v be the set of distinct forbidden offsets c occurring in that class.  Duplicate copies of the same pair (v,c) have no semantic effect.

## 3. Three exact cases over F3

Because F3 has exactly three values, every projective class has only the following possibilities.

### Case 0 — zero normal

If b_i=0 then coordinate i is constant on the affine solution space.

- r0_i=0 => every affine solution has a zero coordinate => UNSAT.
- r0_i!=0 => coordinate i is permanently safe and can be dropped from the avoidance system.

### Case 1 — one forbidden offset

If |C_v|=1, retain one avoidance constraint

    v alpha != c.

### Case 2 — two forbidden offsets

If

    C_v={a,b}

with a!=b, let t be the unique element of

    F3 \ C_v.

Avoiding both forbidden hyperplanes is exactly the linear equation

    v alpha = t.

Therefore this projective class does not require branching: it forces one affine linear equation.
Restrict the parameter space to that hyperplane and recompute the remaining coordinate forms.
Since v!=0, the affine dimension drops by exactly one.

### Case 3 — all three offsets

If

    C_v=F3,

then for every alpha the scalar v alpha is one of the three forbidden values.  The three parallel hyperplanes cover the entire parameter space, so return UNSAT.

## 4. Fixed-point algorithm

Apply the previous rules repeatedly.

    INPUT: A

    1. Solve A r=1 over F3.
       inconsistent => UNSAT.

    2. Build r=r0+B alpha.

    3. Repeat:
       a. remove safe zero-normal coordinates;
       b. zero-normal with r0_i=0 => UNSAT;
       c. canonicalize every nonzero b_i projectively;
       d. collapse duplicate (v,c) constraints;
       e. some |C_v|=3 => UNSAT;
       f. some |C_v|=2 => impose v alpha=t, restrict the affine
          parameterization, and restart;
       g. otherwise stop at the reduced residual.

Every Case-2 step lowers d by one, so there are at most d such iterations.
All arithmetic is over the fixed field F3 and each restriction is Gaussian elimination / substitution of polynomial bit complexity.

Hence the complete fixed-point reduction is deterministic polynomial time.

## 5. Semantic theorem

### Theorem AF3-PCQ-1

The fixed-point quotient preserves the affine nowhere-zero solution set exactly under the explicit affine reconstruction map.
It can terminate only in one of three states:

1. `UNSAT`, with either an inconsistent affine system, a forced-zero coordinate, or a three-offset projective cover certificate;
2. `SAT`, if the affine parameter dimension reaches zero and the unique represented point is nowhere-zero;
3. `RESIDUAL`, in which every remaining nonzero projective normal direction occurs with exactly one forbidden offset.

For every Case-2 contraction there is a bijection between solutions before contraction satisfying both parallel avoidance constraints and solutions after contraction.
Therefore witness reconstruction is polynomial and exact.

## 6. Canonical residual invariant

At fixed point, after deleting vacuous coordinates:

    every b_i != 0,
    every projective normal direction has exactly one forbidden offset,
    no duplicate (v,c) constraint is semantically needed.

Thus all easy F3 parallel-class structure has been exhausted.
Any universal continuation may assume this invariant without loss of Exact-One semantics.

## 7. Frozen controls

The exact regression uses the same n=15 controls as AF3-1.

### PG15 SAT

For PG15:

    rank_F3(A)=11,
    affine dimension d=4.

The quotient reaches a fixed point immediately:

    projective normal classes = 11,
    every class has exactly one forbidden offset,
    Case-2 pins = 0,
    Case-3 covers = 0.

So the hard positive control is not spuriously solved or rejected.

### Singular rank-14 UNSAT control

For the frozen singular UNSAT source:

    rank_F3(A)=14,
    affine dimension d=1.

Its coordinate-zero constraints contain one projective normal direction with all three offsets 0,1,2.  Therefore AF3-PCQ returns UNSAT immediately by Case 3.
This agrees with exhaustive Boolean replay and with the existing exact UNSAT proofs.

## 8. Relation to RKPR

This quotient is not the rational RKPR theorem.

RKPR groups rational kernel-coordinate rows and exploits ratios compatible with the Boolean {-1,2} embedding over Q.
AF3-PCQ instead works after the exact F3 affine reformulation and groups affine zero-hyperplanes by projective normal plus offset.
Characteristic three is essential: two forbidden offsets force the unique third value.

The two quotients can be run independently as polynomial preprocessors.

## 9. Prior-art boundary

Finite-field affine hyperplane covers and irredundant coset covers are classical.  Generic cover theorems do not yield a universal shortcut here: in characteristic three, small covers may live in a low-rank quotient, and the strongest additive-basis/coset-cover bounds used for p>=5 do not improve the rank bound at p=3.

The JANUS-specific result is the exact fixed-point contraction of the coordinate-zero hyperplanes arising from

    A r=1, r_i!=0

for the literal Exact-One source, together with witness-preserving affine reconstruction.

## 10. New frontier

After AF3-PCQ the bounded finite-field gate can be sharpened to:

    R5_E9_AFFINE_F3_SIMPLE_PROJECTIVE_HYPERPLANE_COVER_GATE_V1

Input residual:

    affine parameter space F3^d,
    one forbidden affine hyperplane per surviving projective normal direction,
    source-triple relations inherited from A B=0.

Required universal PASS:
construct a point avoiding all surviving hyperplanes, or a polynomial certificate that these single-offset, projectively distinct hyperplanes cover the whole parameter space.

Forbidden shortcuts:

    enumerate 3^d points,
    generic full-support-code oracle,
    generic characteristic-polynomial evaluation,
    assume large d implies SAT,
    assume the p>=5 Alon-Jaeger-Tarsi/coset-cover bounds extend to p=3.

## 11. Ceiling

    AFFINE F3 PARALLEL-CLASS FIXED-POINT REDUCTION = POLYNOMIAL / PROVED
    THREE OFFSETS IN ONE PROJECTIVE CLASS = EXACT UNSAT CERTIFICATE
    TWO OFFSETS IN ONE PROJECTIVE CLASS = EXACT DIMENSION-DROP PIN
    PG15 = SURVIVES AS RESIDUAL
    SINGULAR RANK14 UNSAT CONTROL = SOLVED BY THREE-OFFSET COVER
    SIMPLE-PROJECTIVE RESIDUAL = OPEN
    UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
    E8_D1 = EMPTY
    P_VS_NP = OPEN
