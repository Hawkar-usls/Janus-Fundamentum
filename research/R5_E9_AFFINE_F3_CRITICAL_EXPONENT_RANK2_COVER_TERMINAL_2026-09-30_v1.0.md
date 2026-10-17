# R5 E9 — Affine F3 Critical-Exponent Dichotomy and Rank-2 Cover Terminal

Date: 2026-09-30

Status:
`JANUS_EXACT_TERNARY_CRITICAL_EXPONENT_DICHOTOMY__RANK2_AFFINE_COVER_POLYNOMIAL_TERMINAL__NO_D1_PROMOTION`

Parent:
`research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`

Checker:
`experiments/r5_e9_affine_f3_critical_exponent_rank2_cover_terminal.py`

## 1. Scientific firewall

This note does **not** prove P=NP and does not claim that every UNSAT source has a rank-2 cover certificate.

It proves two exact structural facts:

1. after F3 consistency, the augmented ternary code has critical exponent only `1` or `2`;
2. if the coordinate-zero hyperplane cover has normal rank at most two, UNSAT has a certificate using at most five coordinates and is therefore deterministically polynomially detectable.

Generic finite geometry admits minimal blocking sets of unbounded projective dimension, so bounded-rank coverage is **not** a free theorem. Any universal promotion must use the special source-line relations.

`E8_D1 = EMPTY` and `P_VS_NP = OPEN`.

## 2. Recall the AF3 normal form

Let `A` be a 0/1 matrix with exactly three ones in every source row. Over F3,

```text
A 1 = 0.
```

The parent theorem proves

```text
Exact-One(A) SAT
iff
exists r in (F3*)^n with A r = 1.
```

Equivalently, for

```text
A_tilde = [A | -1],
C_A = ker_F3(A_tilde),
```

Exact-One is SAT iff `C_A` contains a full-support codeword.

If `Ar=1` is consistent, write

```text
r = r0 + B alpha,
alpha in F3^d,
```

and define coordinate-zero hyperplanes

```text
H_i = { alpha : r0_i + b_i alpha = 0 },
```

where `b_i` is row `i` of `B`.

Then Exact-One is UNSAT iff the `H_i` cover all of `F3^d`.

## 3. Critical exponent collapses to 1 versus 2

Let

```text
c0 = (1_n, 0).
```

Because `A1=0` over F3,

```text
c0 in C_A.
```

Its support contains every original coordinate and misses only the augmented syndrome coordinate.

Assume now that `Ar=1` is consistent. Then

```text
c1 = (r,1) in C_A.
```

The last coordinate of `c1` is nonzero, so

```text
supp(c0) union supp(c1) = [n+1].
```

The Critical Theorem identifies the critical exponent `c(M(C_A);3)` with the minimum number of codewords whose union of supports is the whole ground set. Hence

```text
c(M(C_A);3) <= 2
```

for every F3-consistent source.

### Theorem CE3-1

For every row-weight-three source for which `Ar=1` is consistent over F3,

```text
Exact-One SAT
iff c(M(C_A);3) = 1,

Exact-One UNSAT
iff c(M(C_A);3) = 2.
```

Equivalently,

```text
SAT:
    chi_M(3) > 0.

F3-consistent UNSAT:
    chi_M(3) = 0
    and chi_M(9) > 0.
```

So the source residual is not an arbitrary critical-problem instance: its critical exponent is already promised to be at most two.

This is a structural simplification, not an algorithm. Deciding critical exponent one is hard in generic represented-matroid families; source structure remains essential.

## 4. Rank of an affine hyperplane cover

For an affine hyperplane

```text
H_i = {alpha : b_i alpha = c_i},
```

call `b_i` its normal. A subcover has **normal rank r** if the F3-span of its nonzero normals has dimension `r`.

A zero normal with `c_i=0` is the whole parameter space and is an immediate one-coordinate UNSAT certificate. A zero normal with nonzero offset is empty and can be discarded.

Suppose a cover has normal rank `r<=2`. Quotient the parameter space by the common kernel of its normals. Every covering hyperplane is the inverse image of an affine hyperplane in `F3^r`. Thus coverage is completely decided in an affine space of at most nine points.

## 5. Exact AG(2,3) cover bound

There are exactly four projective normal directions in `F3^2`; each direction has three parallel affine lines, for a total of twelve lines in `AG(2,3)`.

### Lemma R2C-1

Every inclusion-minimal cover of `AG(2,3)` by affine lines has size `3`, `4`, or `5`. In particular it has size at most five.

### Proof

If a minimal cover contains all three lines of one parallel class, those three lines already partition and cover the plane; minimality forces the cover to have exactly three members.

Otherwise no direction occurs three times.

If no two selected lines are parallel, there is at most one line from each of the four directions, so the cover has size at most four.

Finally suppose the cover contains a parallel pair `L0,L1` but not the third line `L2` of that direction. The pair covers six of the nine points. Every additional nonparallel line meets the remaining line `L2` in exactly one point. Since all its other points already lie on `L0 union L1`, its only possible private point is that intersection with `L2`. Irredundancy therefore permits at most one additional line for each of the three points of `L2`. Hence the cover has size at most `2+3=5`.

This proves the bound. The checker independently enumerates all `2^12=4096` line subsets and verifies that the inclusion-minimal covers have sizes exactly `3`, `4`, and `5`.

## 6. Polynomial rank-2 UNSAT terminal

### Theorem R2C-2

If the AF3 coordinate-zero hyperplanes cover the affine solution parameter space and some covering subfamily has normal rank at most two, then there is such a covering subfamily of at most five coordinate hyperplanes.

Therefore this condition can be detected deterministically in polynomial time:

```text
for every coordinate subset I with 1 <= |I| <= 5:
    compute rank_F3({b_i : i in I});
    if rank <= 2:
        test exactly whether union_{i in I} H_i covers the quotient F3^rank;
        if yes: return UNSAT with I as certificate.
```

For each fixed subset the quotient contains at most nine points, so its coverage test is constant-size exact arithmetic. The total search is `O(n^5 poly(n))`.

No SAT oracle, characteristic-polynomial evaluation, or exponential affine enumeration is hidden in the detector.

## 7. Why this is not universal by finite geometry alone

A tempting next step would be to claim that every affine hyperplane cover over F3 contains a rank-2 or rank-3 subcover. That is false in generic projective geometry.

Known blocking-set constructions combine lower-dimensional minimal blocking sets to create minimal blocking sets in higher-dimensional projective spaces. Iterating them gives genuinely high-dimensional minimal blockers. Thus bounded blocker rank is not a field-size-three theorem.

The only remaining legitimate bounded-rank conjecture would have to use the source-specific incidence identities described next.

## 8. Source-specific projective-line structure

Let `p_i` be the coordinate functionals of the augmented ternary code and `p_*` the last-coordinate functional. Every source row `{i,j,k}` gives

```text
p_i + p_j + p_k = p_*.
```

After quotienting by `<p_*>`,

```text
bar(p_i) + bar(p_j) + bar(p_k) = 0.
```

Hence every source row becomes a projective ternary line. On a linear cubic source:

```text
each coordinate point lies in exactly three source lines,
any two source lines meet in at most one coordinate point.
```

This 3-regular partial geometry is the additional structure absent from generic blocking-set counterexamples.

## 9. New live gate

Freeze

```text
R5_E9_SOURCE_TERNARY_BLOCKING_GEOMETRY_HIGH_RANK_GATE_V1
```

Input:

```text
connected square linear-cubic source A,
Ar=1 consistent over F3,
no full-support affine solution found by existing polynomial terminals,
no rank<=2 coordinate-hyperplane subcover,
no already recognized network/TU/binet/regular/bounded-width terminal.
```

Required progress is one of:

1. prove that the 3-regular source-line geometry forces a bounded-rank blocker and give a polynomial detector;
2. construct a polynomial decomposition/augmentation for high-rank blockers with exact witness lifting;
3. construct an explicit source-generated affine-consistent UNSAT family whose minimum blocker rank grows, thereby falsifying bounded-rank source coverage and identifying the true residual.

Generic blocking-set or generic critical-exponent results are not sufficient.

## 10. Ceiling

```text
AF3 CONSISTENT RESIDUAL CRITICAL EXPONENT <= 2
= PROVED

SAT
iff CRITICAL EXPONENT = 1
= PROVED

AF3-CONSISTENT UNSAT
iff CRITICAL EXPONENT = 2
= PROVED

NORMAL-RANK <= 2 COVER
=> <= 5 COORDINATE CERTIFICATE
= PROVED

RANK-2 CERTIFICATE DISCOVERY
= DETERMINISTIC POLYNOMIAL O(n^5 poly(n))

GENERIC BOUNDED-RANK BLOCKER CLAIM
= FALSE / FORBIDDEN

SOURCE-SPECIFIC BOUNDED-RANK OR HIGH-RANK DECOMPOSITION
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```