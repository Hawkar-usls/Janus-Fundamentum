# R5 E20 — Kernel-Local Projection and the 3-Circuit Terminal

Date: 2026-10-02

Status:
`SOUND_POLYNOMIAL_KLOC3_TERMINAL__KPROJ_UNIFIED_AS_KLOC2__PALEY_E19_QUOTIENT_CLOSED_BY_NONDIAGONAL_3_COORDINATE_CERTIFICATE`

Scientific ceiling:

```text
THIS NOTE ADDS A NEW EXACT POLYNOMIAL UNSAT TERMINAL BASED ON
LOW-CARDINALITY COORDINATE PROJECTIONS OF THE RATIONAL KERNEL.

KLOC-2 RECOVERS THE R5 E18 KERNEL-PROJECTIVE RULES.
KLOC-3 STRICTLY EXTENDS THE PAIRWISE STAGE AND CLOSES THE PALEY-11
QUOTIENT FROM R5 E19 BY 110 EXPLICIT NONDIAGONAL 3-COORDINATE
OBSTRUCTIONS, EVEN THOUGH THAT QUOTIENT HAS NO PROPORTIONAL KERNEL ROWS.

THIS IS NOT A UNIVERSAL POLYNOMIAL ALGORITHM.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in {0,1}^{n x n}
```

be a square+cubic+linear Exact-One source and let

```text
K = ker_Q(A).
```

Choose any full-column-rank basis matrix

```text
B in Q^{n x d},
col(B)=K.
```

The `i`th row `b_i` of `B` is the coordinate functional of the kernel at source
coordinate `i`.

As in R5 E10/E15/E18, Exact-One is equivalent to the existence of

```text
y in K intersect {-1,2}^n.
```

For a coordinate subset `S`, write

```text
pi_S(K)
```

for the coordinate projection of `K` onto `S`.
Since `B` spans `K`,

```text
pi_S(K) = col(B_S),
```

where `B_S` is the submatrix formed by the rows indexed by `S`.

## 2. Kernel-local projection theorem

Let

```text
Sigma = {-1,2}.
```

Every global Boolean witness projects to an alphabet vector on every coordinate
subset. Therefore:

### Theorem KLOC-S

For any `S subseteq [n]`, if

```text
pi_S(K) intersect Sigma^S = empty,
```

then `A` is Exact-One UNSAT.

Equivalently, if no vector

```text
sigma in {-1,2}^{|S|}
```

lies in the column space of `B_S`, then no global witness exists.

Proof is immediate: a global witness `y in K intersect Sigma^n` would have

```text
y_S in pi_S(K) intersect Sigma^S,
```

contradicting emptiness.

The condition is basis-invariant because `pi_S(K)` depends only on the kernel
subspace, not on the chosen basis.

## 3. Fixed-cardinality search is polynomial

Fix a constant `s`.

For every `S` with

```text
|S| <= s,
```

enumerate the at most

```text
2^s
```

alphabet vectors and test exact rational membership in `col(B_S)` by Gaussian
elimination.

The resulting runtime is

```text
O(n^s 2^s poly(n)).
```

Therefore every fixed level `KLOC-s` is a deterministic polynomial terminal.

If a local relation is not empty, its complete allowed-pattern table may also be
used for exact propagation:

```text
forced coordinates,
equality / opposition classes,
small finite local relations.
```

Only an empty table is promoted directly to UNSAT.

## 4. KLOC-1 and KLOC-2 recover earlier exact rules

### KLOC-1

For `S={i}`, if the kernel projection is `{0}`, then no value from `{-1,2}` is
possible. This is exactly the R5 E18 `KPROJ-0` rule.

### KLOC-2

Let the two kernel rows satisfy

```text
b_j = lambda b_i.
```

Then every projected kernel vector obeys

```text
y_j = lambda y_i.
```

The only ratios possible between two alphabet values are

```text
1, -2, -1/2.
```

Hence KLOC-2 gives exactly:

```text
lambda outside {1,-2,-1/2} -> UNSAT,
lambda = 1                 -> Boolean equality,
lambda = -2 or -1/2        -> forced Boolean pair.
```

Thus the R5 E18 kernel-projective branch is the `s<=2` part of one general
kernel-local hierarchy.

## 5. Circuit form

Suppose a set of kernel rows indexed by `S` has a linear dependency

```text
sum_{i in S} c_i b_i = 0.
```

Then every `y in K` satisfies

```text
sum_{i in S} c_i y_i = 0.
```

Therefore, if

```text
sum c_i sigma_i != 0
```

for every

```text
sigma in {-1,2}^S,
```

then the instance is UNSAT.

For a minimal dependency this is a kernel-circuit certificate.
KLOC-s is slightly more general because it tests the entire projected subspace,
not just one displayed dependency.

In centered-to-Boolean coordinates

```text
y = 3x-1,
```

a circuit relation becomes the source-aligned identity

```text
sum c_i x_i = (sum c_i)/3.
```

So KLOC certificates are also short-support source-aligned certificates in the
language of R5 E10.

## 6. Paley-11 quotient from R5 E19

Use the Paley tournament on `Z_11` from R5 E19.
Its 55 tournament arcs are the source variables and its 55 cyclic directed
triangles are the source rows.

The companion checker verifies exactly:

```text
n = 55,
row weight = 3,
column weight = 3,
linearity holds,
rank_Q(A) = 45,
nullity_Q(A) = 10.
```

A full rational kernel is the `A_10` root space

```text
r_ij = e_i - e_j.
```

No two tournament arcs are opposite copies of one another, so no two root rows are
proportional. Therefore

```text
KLOC-2 / KPROJ is completely clean:
0 zero rows,
0 proportional pairs,
0 pairwise forced relations.
```

This makes the Paley quotient a useful test of genuinely higher local kernel
relations.

## 7. KLOC-3 closes the Paley quotient

Every unordered triple of tournament vertices produces three tournament arcs.
There are

```text
C(11,3)=165
```

such rank-two root triples.

They split exactly into:

```text
55 cyclic triples,
110 transitive triples.
```

For a cyclic triple

```text
i -> j -> k -> i,
```

the root relation is

```text
r_ij + r_jk + r_ki = 0.
```

This relation is alphabet-compatible: the permitted patterns are precisely the
three permutations of

```text
(2,-1,-1).
```

These are exactly the ordinary Exact-One source rows.

For a transitive triple, for example

```text
0 -> 3 -> 1
and
0 -> 1,
```

we have

```text
-r_01 + r_03 + r_31 = 0.
```

A Boolean witness would therefore require

```text
-y_01 + y_03 + y_31 = 0,
y_* in {-1,2}.
```

But the eight alphabet triples give no solution.
Indeed `y_03+y_31` can only be

```text
-2, 1, 4,
```

while `y_01` can only be

```text
-1, 2.
```

So this three-coordinate kernel projection is empty.

The exact checker finds

```text
rank-2 kernel triples = 165,
KLOC-3 compatible     = 55,
KLOC-3 incompatible   = 110.
```

Therefore the Paley-11 quotient is rejected immediately by KLOC-3 despite being
completely clean at the KLOC-2/KPROJ level.

## 8. Relation to the connected R5 E19 165-variable firewall

R5 E19 constructed a connected 165-variable 3-lift whose entire rational kernel
is copy-constant on the three copies of each base arc.

The exact router is therefore:

```text
165-variable connected lift
-> KLOC-2 / KPROJ equality quotient
-> 55-variable Paley base
-> KLOC-3 transitive-triple obstruction
-> UNSAT.
```

R5 E19 already closed the quotient by the cardinality contradiction `3 |S|=55`.
E20 adds a different closure mechanism: a genuinely non-diagonal three-coordinate
kernel relation.

This directly answers the E19 frontier statement that the next useful object must
exploit relations among multiple distinct kernel rows rather than only diagonal
coordinate moments.

## 9. Router update

The post-E19 algebraic router should now read:

```text
K0  compute exact rational kernel
K1  KLOC-1 zero-coordinate test
K2  KLOC-2 / projective pair rules
K3  propagate pairwise forced/equality classes and quotient
K4  rerun cheap exact terminals
K5  bounded-interface / local-gauge quotient
K6  KLOC-3 scan over three-coordinate projections
K7  optional higher fixed KLOC-s levels
K8  Schur/moment obstructions as auxiliary UNSAT terminals
```

The order matters: exact quotienting should occur before expensive higher local or
moment tests.

## 10. What E20 does not prove

For fixed `s`, KLOC-s is polynomial, but nothing here proves that one universal
constant `s` detects every UNSAT source.

The original source clauses themselves are compatible three-circuits, so an
arbitrary NP-hard instance can survive all clause-local checks.

A future universal theorem would need either:

```text
(A) a constant bound on the size of some incompatible kernel projection in every
    projectively reduced UNSAT hard core,

or

(B) a polynomial compression/decomposition theorem when all bounded-size
    projections are alphabet-compatible,

or

(C) a different global certificate beyond bounded local consistency.
```

No such exhaustive theorem is claimed here.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e20_kernel_local_projection.py
```
