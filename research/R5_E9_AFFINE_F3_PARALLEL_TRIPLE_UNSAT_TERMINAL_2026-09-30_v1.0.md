# R5 E9 — Affine F3 Parallel-Triple UNSAT Terminal

Date: 2026-09-30

Status:
`JANUS_EXACT_POLYNOMIAL_UNSAT_TERMINAL__AFFINE_F3_PROJECTIVE_PARALLEL_CLASS_COVER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS NOTE ADDS A POLYNOMIAL UNSAT CERTIFICATE INSIDE THE AFFINE-F3 NORMAL FORM.
IT DOES NOT PROVE THAT EVERY UNSAT SOURCE HAS SUCH A CERTIFICATE.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Affine parameter space

Let `A` be a row-weight-three Exact-One source. Work over `F3` and assume the affine system

```text
A r = 1
```

is consistent. Compute one affine solution `r0` and an exact kernel basis matrix

```text
B in F3^{n x d},
col(B)=ker_F3(A),
```

so every affine solution is

```text
r(alpha)=r0+B alpha,
alpha in F3^d.
```

Write `b_i` for row `i` of `B`. Coordinate `i` is zero exactly on

```text
H_i={alpha : b_i alpha = -r0_i}.
```

By the parent theorem, Exact-One is SAT iff the union of these coordinate-zero hyperplanes does not cover `F3^d`.

## 2. Projective normalization

For a nonzero row `b_i`, let `lambda_i in F3^*` be the unique scalar which normalizes the first nonzero coordinate of `lambda_i b_i` to `1`. Define

```text
c_i = lambda_i b_i,
t_i = -lambda_i r0_i.
```

Then

```text
H_i={alpha : c_i alpha=t_i}.
```

Two coordinates belong to the same projective-normal class iff their normalized normals `c_i` agree.

The property below is independent of the chosen kernel basis and affine basepoint: an invertible change of parameter coordinates sends common normals to common normals, while changing `r0` translates all offsets inside one parallel class by the same amount. Hence the set of realized offsets is permuted, and the condition that all three offsets occur is invariant.

## 3. Parallel-triple terminal

### Theorem PTF3-1

Suppose one projective-normal class contains coordinate hyperplanes with all three normalized offsets

```text
0,1,2.
```

Then the Exact-One source is UNSAT.

### Proof

For one fixed nonzero normal `c`, the three affine hyperplanes

```text
{alpha:c alpha=0},
{alpha:c alpha=1},
{alpha:c alpha=2}
```

partition `F3^d`. Therefore every affine parameter `alpha` makes at least one coordinate in that class equal to zero. Hence there is no nowhere-zero affine solution of `Ar=1`. By AF3-1, no Boolean Exact-One witness exists. QED.

### Zero-normal terminal

If some `b_i=0` and `r0_i=0`, then coordinate `i` is identically zero throughout the affine solution space, so the source is also immediately UNSAT.

If `b_i=0` and `r0_i!=0`, that coordinate is never zero and imposes no hyperplane.

## 4. Polynomial algorithm

```text
INPUT: row-weight-three Exact-One source A.

1. Gaussian-eliminate A r=1 over F3.
   - inconsistent => UNSAT.
2. Construct r0 and a kernel basis B.
3. For every coordinate i:
   a. if b_i=0 and r0_i=0 => UNSAT;
   b. if b_i=0 and r0_i!=0 => ignore;
   c. otherwise projectively normalize (b_i,-r0_i) to (c_i,t_i).
4. Hash by projective normal c_i and collect offsets t_i.
5. If any class realizes {0,1,2}, return UNSAT with three coordinate indices.
6. Otherwise return NOT_IN_PARALLEL_TRIPLE_TERMINAL.
```

All arithmetic is over the fixed field `F3`; Gaussian elimination and hashing are polynomial in the source size.

The three returned coordinate equations are a direct polynomially checkable cover certificate.

## 5. A single source row can never generate the certificate

Let one source row contain variables `i,j,k`. Since `AB=0`,

```text
b_i+b_j+b_k=0.
```

Since `Ar0=1`,

```text
r0_i+r0_j+r0_k=1.
```

Assume for contradiction that the three coordinate hyperplanes from this same source row are one complete parallel class.

Their nonzero normals are projectively equal, so for some nonzero `c`

```text
b_i=lambda_i c,
b_j=lambda_j c,
b_k=lambda_k c,
lambda_i,lambda_j,lambda_k in {1,2}.
```

The relation `b_i+b_j+b_k=0` forces

```text
lambda_i=lambda_j=lambda_k,
```

because over `F3` the only three-term sum of nonzero scalars equal to zero is `1+1+1=0` or `2+2+2=0`.

After the same normalization scalar is applied to all three equations, having three distinct offsets means the normalized right-hand sides are exactly `{0,1,2}`, whose sum is `0`. Therefore the correspondingly normalized values of `r0_i,r0_j,r0_k` also sum to `0`, contradicting `r0_i+r0_j+r0_k=1`.

Thus:

```text
NO SINGLE SOURCE ROW CAN BE THE WHOLE PARALLEL-TRIPLE CERTIFICATE.
```

The terminal detects a genuinely global interaction among source coordinates.

## 6. Frozen controls

Exact regression checks:

```text
PG15 SAT (n=15, dim_F3=4):
  projective classes = 11
  full parallel classes = 0
  max offsets in a class = 1

unique-model 18_3 SAT seed (dim_F3=2):
  projective classes = 3
  full parallel classes = 0
  max offsets in a class = 2

first prime SAT 2-lift (n=36, dim_F3=3):
  projective classes = 5
  full parallel classes = 0
  max offsets in a class = 2

frozen singular UNSAT seed (n=15, dim_F3=1):
  full parallel classes = 1

prime two-edge UNSAT tower:
  n=30  : dim_F3=2, full classes=2
  n=60  : dim_F3=3, full classes=3
  n=120 : dim_F3=5, full classes=5
  n=240 : dim_F3=9, full classes=9
```

These controls support the terminal and stress it against both SAT and UNSAT high-nullity constructions. They do not prove completeness.

## 7. Hyperplane-cover literature boundary

General affine hyperplane cover theory does not make this terminal complete. Over `F3`, an arbitrary affine space can be covered by three parallel hyperplanes, and irredundant spanning-normal covers are a separate finite-geometry problem. Recent work of Nagy--Pach--Tomon gives lower bounds for irredundant spanning-normal covers, but those bounds are compatible with linear-size source covers and therefore do not by themselves yield a universal Exact-One algorithm.

The source-specific opportunity is stronger and remains open: exploit the relations

```text
b_i+b_j+b_k=0,
r0_i+r0_j+r0_k=1
```

on every source triple to classify covers which avoid a complete parallel class.

## 8. New gate

Freeze

```text
R5_E9_AFFINE_F3_NO_PARALLEL_TRIPLE_COVER_CLASSIFICATION_GATE_V1
```

Required PASS:

```text
Given a linear-cubic source whose affine coordinate-zero hyperplanes cover F3^d,
prove that either
  (a) a complete projective-normal parallel class {0,1,2} exists and is found polynomially,
or
  (b) another polynomially discoverable source-specific cover certificate exists,
with a strict polynomial decomposition/recursion until every UNSAT cover is certified.
```

A theorem that every source-compatible full cover contains a parallel triple would by itself close the affine-F3 carrier, but that statement is NOT proved and must be attacked against the full hostile stack.

## 9. Ceiling

```text
FULL PARALLEL CLASS {0,1,2}
=> UNSAT
= PROVED

ZERO KERNEL NORMAL + ZERO OFFSET
=> UNSAT
= PROVED

TERMINAL RECOGNITION / CERTIFICATE
= DETERMINISTIC POLYNOMIAL

ONE SOURCE ROW GENERATES COMPLETE PARALLEL CLASS
= IMPOSSIBLE

PG15 + UNIQUE-MODEL SAT CONTROLS
= REJECT TERMINAL

FROZEN UNSAT PRIME TOWER
= ACCEPT TERMINAL ON TESTED LEVELS

EVERY UNSAT SOURCE HAS PARALLEL TRIPLE
= NOT PROVED

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
