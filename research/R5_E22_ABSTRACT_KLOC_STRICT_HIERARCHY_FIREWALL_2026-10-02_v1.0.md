# R5 E22 — Abstract KLOC Strict-Hierarchy Firewall

Date: 2026-10-02

Status:
`EXACT_ABSTRACT_STRICT_HIERARCHY__ARBITRARILY_LARGE_FIRST_INCOMPATIBLE_KERNEL_CIRCUIT__CARRIER_REALIZATION_OPEN`

Scientific ceiling:

```text
THIS NOTE PROVES THAT NO FIXED KERNEL-LOCAL PROJECTION RADIUS CAN BE
UNIVERSAL FOR ARBITRARY RATIONAL KERNEL SUBSPACES.

FOR EVERY s NOT DIVISIBLE BY 3 THERE IS AN s-COORDINATE RATIONAL SUBSPACE
WHOSE EVERY PROPER COORDINATE PROJECTION IS FULL, WHILE THE GLOBAL
{-1,2}-ALPHABET INTERSECTION IS EMPTY.

THIS IS AN ABSTRACT KERNEL FIREWALL ONLY.  IT DOES NOT YET REALIZE THE
FAMILY AS FULL KERNELS OF SQUARE+CUBIC+LINEAR EXACT-ONE SOURCES.
P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
Sigma = {-1,2}.
```

R5 E20 introduced the exact local test

```text
KLOC-s:
pi_S(K) cap Sigma^S = empty
```

for coordinate subsets `S` of fixed cardinality.  Every fixed level is polynomial,
but E20 left open whether one universal constant radius might suffice on the
square+cubic+linear carrier.

R5 E21 already supplied the first strictness example

```text
K = {y in Q^4 : y_1+y_2+y_3+y_4=0},
```

for which all 3-projections pass while the 4-projection is empty.

The same mechanism extends to arbitrary radius.

## 2. Strict-hierarchy family

For an integer `s>=2`, define

```text
K_s = { y in Q^s : y_1+...+y_s = 0 }.
```

Then

```text
dim_Q K_s = s-1.
```

A convenient basis matrix is

```text
B_s =
[ I_{s-1} ]
[ -1 ... -1].
```

The `s` coordinate rows of this basis have one unique linear dependency:

```text
b_1+...+b_s=0.
```

Every proper subset of the rows is independent.  Hence the row matroid has a
single minimal circuit, of support exactly `s`.

## 3. Every proper coordinate projection is full

Let

```text
T proper subset [s].
```

Take any desired vector

```text
z in Q^T.
```

Because at least one coordinate `j` is omitted from `T`, define a vector `y` by

```text
y_i = z_i          for i in T,
y_j = -sum_{i in T} z_i,
y_l = 0            on all other omitted coordinates.
```

Then

```text
sum_i y_i = 0,
```

so `y in K_s`, and its projection to `T` is exactly `z`.

Therefore

```text
boxed:
pi_T(K_s) = Q^T
for every proper T subset [s].
```

In particular every proper local test is maximally feasible:

```text
pi_T(K_s) cap Sigma^T = Sigma^T != empty.
```

Thus all levels below `s` pass.

## 4. Global alphabet obstruction

Let

```text
y in Sigma^s.
```

If exactly `m` coordinates are equal to `2`, then the remaining `s-m` coordinates
are `-1`, and therefore

```text
sum_i y_i = 2m-(s-m) = -s+3m.
```

Hence

```text
sum_i y_i = 0
iff
s = 3m.
```

Therefore

```text
boxed:
K_s cap Sigma^s = empty
iff
3 does not divide s.
```

When `3|s`, the intersection consists exactly of the vectors having `s/3`
coordinates equal to `2`, so

```text
|K_s cap Sigma^s| = binom(s,s/3).
```

## 5. Strict hierarchy theorem

Combining Sections 3 and 4 gives:

### Theorem KLOC-STRICT

For every

```text
s>=2 with 3 not dividing s,
```

there is a rational kernel subspace `K_s` such that

```text
all KLOC-r tests pass for every r<s,
```

but

```text
KLOC-s rejects.
```

Equivalently, the first incompatible kernel circuit can have arbitrarily large
support.

For every fixed constant `r`, choose any

```text
s>r,
3 not dividing s.
```

Then `K_s` passes every coordinate projection test of cardinality at most `r` but
has no global `{-1,2}` vector.

Thus:

```text
boxed:
NO FIXED KLOC RADIUS IS A UNIVERSAL SOLVER FOR ARBITRARY RATIONAL KERNELS.
```

This is unconditional linear algebra and does not use a complexity assumption.

## 6. Consequence for the JANUS route

The post-E20 strategy must not become

```text
try KLOC-4,
then KLOC-5,
then KLOC-6,
...
```

and hope that some unproved constant eventually becomes universal.

A valid universal theorem must instead use extra structure of the actual
square+cubic+linear carrier.

The remaining possibilities are now sharper:

```text
(A) CARRIER CIRCUIT-WIDTH THEOREM
    prove that every projectively reduced UNSAT carrier contains an incompatible
    kernel circuit of bounded size;

(B) CARRIER COMPRESSION THEOREM
    if all small kernel circuits are alphabet-compatible, derive an exact
    polynomial decomposition / quotient / normal form;

(C) GLOBAL CERTIFICATE
    exploit a nonlocal invariant not reducible to bounded coordinate projections.
```

## 7. What is still open

The family `K_s` is an abstract rational subspace family.

This note does **not** prove that for arbitrarily large `s` there exists a
square+cubic+linear incidence matrix `A_s` with

```text
ker_Q(A_s) congruent to K_s
```

or even with the same local-projection profile after the exact R5 E17--E20
quotients.

That realization question is now the correct firewall target.

If the carrier forbids such long first-obstruction circuits, that prohibition could
be the missing structural theorem.  If the carrier admits them for unbounded `s`,
then every fixed-radius KLOC strategy is dead even on the NP-complete target class.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e22_abstract_kloc_strict_hierarchy.py
```
