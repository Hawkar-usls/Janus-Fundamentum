# R5 E23 — Integer-Saturation / 3-Primary Cokernel Terminal

Date: 2026-10-02

Status:
`EXACT_POLYNOMIAL_INTEGER_LIFT_UNSAT_TERMINAL__3_PRIMARY_COKERNEL__Q2_FIREWALL_CLOSED__PG15_FIREWALL_RETAINED`

Scientific ceiling:

```text
THIS NOTE ADDS A GLOBAL POLYNOMIAL UNSAT TERMINAL STRICTLY DIFFERENT FROM
BOUNDED KLOC TESTS AND FROM THE R5 E18 SCHUR-SQUARE NECESSARY CONDITION.

THE TERMINAL DECIDES WHETHER A x = 1 HAS ANY INTEGER SOLUTION AT ALL.
IF NOT, EXACT-ONE IS UNSAT.

FOR SQUARE+CUBIC SOURCES THE OBSTRUCTION LIVES ENTIRELY IN THE 3-PRIMARY
COKERNEL BECAUSE A 1 = 3 1.

THE R5 E18 42-VARIABLE Q2 FIREWALL IS CLOSED BY THIS TERMINAL.
PG15_UNSAT IS AN EXPLICIT FIREWALL AGAINST PROMOTING INTEGER FEASIBILITY TO
BOOLEAN FEASIBILITY.

P_VS_NP = OPEN.
```

## 1. Setting

Let

```text
A in Z^{n x n}
```

be a square cubic Exact-One incidence matrix, so

```text
A 1 = 3 1.
```

We seek

```text
x in {0,1}^n,
A x = 1.
```

Before enforcing the Boolean box, ask the weaker question:

```text
Does A x = 1 have any x in Z^n ?
```

If the answer is no, the Exact-One instance is certainly UNSAT.

Integer linear-system solvability is decidable in deterministic polynomial time
by Smith or Hermite normal form.

## 2. Saturated row-space certificate

Define the saturated integer row lattice

```text
L_sat = row_Q(A) cap Z^n.
```

Take any

```text
c in L_sat.
```

Then for some rational vector `lambda`,

```text
c = A^T lambda.
```

If `A x = 1`, then

```text
c^T x
= lambda^T A x
= lambda^T 1.
```

Because `A 1 = 3 1`,

```text
sum_i c_i
= c^T 1
= lambda^T A 1
= 3 lambda^T 1.
```

Therefore every solution satisfies the exact identity

```text
boxed:
c^T x = (sum_i c_i)/3.
```

If `c` is integral and `x` is integral, the left side is an integer.  Hence:

### Theorem INT-SAT-CERT

If there exists

```text
c in row_Q(A) cap Z^n
```

with

```text
sum_i c_i not congruent 0 mod 3,
```

then `A x = 1` has no integer solution, and therefore the Exact-One instance is
UNSAT.

The certificate is short:

```text
c,
a rational row-space witness for c (or an exact rank-membership check).
```

## 3. Completeness for integer infeasibility

The previous certificate family is not only sound; it is complete for the weaker
integer-feasibility question.

A standard lattice-duality criterion says

```text
b in A Z^n
iff
lambda^T b in Z
for every lambda in Q^n with A^T lambda in Z^n.
```

Apply this with

```text
b = 1.
```

For every such `lambda`, put

```text
c=A^T lambda in L_sat.
```

Then

```text
lambda^T 1 = (sum c_i)/3.
```

Therefore

```text
boxed:
A x = 1 has an integer solution
iff
sum_i c_i == 0 mod 3
for every c in L_sat.
```

Equivalently, if `C` is any integer basis of the saturated row lattice, integer
feasibility holds iff every basis vector has coordinate sum divisible by three.

Computing such a basis is polynomial via Smith/Hermite normal form.

## 4. 3-primary cokernel interpretation

Let

```text
G = Z^n / A Z^n
```

and let `[1]` denote the class of the all-ones vector.

Since

```text
A 1 = 3 1,
```

we have

```text
3 [1] = 0 in G.
```

Thus `[1]` has order `1` or `3`.

The integer system is solvable exactly when

```text
[1]=0.
```

Hence the entire integer obstruction lies in the 3-primary part of the cokernel.
In Smith normal form

```text
U A V = D,
b = U 1,
```

only diagonal invariant factors divisible by `3` can obstruct divisibility of the
transformed right-hand side.  Invariant factors coprime to `3` cannot obstruct,
because `D z = 3 b` has the known solution induced by `A 1 = 3 1`.

This explains why the terminal is naturally aligned with the Exact-One alphabet.

## 5. Centered-kernel interpretation

Write

```text
y = 3x - 1.
```

For an integer solution `x`,

```text
A y = 0,
y in Z^n,
y == -1 mod 3 coordinatewise.
```

Conversely any integer kernel vector satisfying

```text
y == -1 mod 3
```

gives an integer solution

```text
x=(y+1)/3.
```

Therefore integer feasibility is equivalent to the global congruence-lift problem

```text
boxed:
ker_Z(A) contains a vector congruent to -1 mod 3.
```

This is weaker than the Boolean requirement

```text
y in {-1,2}^n,
```

but it is global and polynomially decidable.

## 6. R5 E18 42-variable firewall is closed

Use the R5 E18 directed-arc construction on `K_7`.

Its exact rational kernel is the six-dimensional root space

```text
y_ij = t_i - t_j.
```

For an opposite arc pair `(i->j),(j->i)`, every kernel vector obeys

```text
y_ij + y_ji = 0.
```

Hence the integral vector

```text
c = e_ij + e_ji
```

lies in

```text
row_Q(A_42) cap Z^42.
```

But

```text
sum c = 2,
```

which is not divisible by three.

Therefore

```text
boxed:
A_42 x = 1 has no integer solution.
```

This is notable because R5 E18 constructed `A_42` specifically so that the
Schur-square/Q2 necessary condition passes.  Thus INT-SATURATION supplies a global
polynomial obstruction not seen by Q2.

The companion checker verifies independently that

```text
rank_Q(A_42)=36
```

and that this `c` is in the rational row space by an exact rank test.

## 7. PG15_UNSAT is a firewall against universality

The frozen singular UNSAT control has primitive rational-kernel generator

```text
z = (1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

Every coordinate is congruent to `1 mod 3`.

Set

```text
x_int = (1 + 2 z)/3.
```

Then `x_int` is integral, and because `A z=0` and `A 1=3 1`,

```text
A x_int = 1.
```

Explicitly,

```text
x_int = (1,3,1,1,-1,-1,1,-1,-1,-1,-1,1,1,1,1).
```

This is not Boolean.

Hence PG15_UNSAT satisfies

```text
INTEGER_FEASIBLE
but
BOOLEAN_UNSAT.
```

So the integer-saturation terminal is not a universal solver.

## 8. Router update

The algebraic router should now include the integer test before expensive local
hierarchy levels:

```text
K0  exact Q-rank / rational kernel
K1  integer-saturation / 3-primary cokernel test
    integer infeasible -> UNSAT
K2  KLOC-1 / zero coordinate
K3  KLOC-2 / projective ratios
K4  quotient equal / forced projective classes
K5  rerun cheap structural terminals
K6  bounded-interface / local-gauge quotient
K7  KCIRC3 / KLOC-3 propagation
K8  selected higher local/global obstruction terminals
```

The order is useful because the Smith/Hermite computation is polynomial and global.

## 9. Updated hard-core requirement

A post-E23 UNSAT survivor must now satisfy all earlier conditions and additionally

```text
A x = 1 has an integer solution.
```

Equivalently,

```text
[1]=0 in Z^n/A Z^n,
```

or

```text
ker_Z(A) contains a vector y == -1 mod 3.
```

Thus the unresolved gap is no longer rational or integral feasibility.  It is the
remaining **box compression**:

```text
integer affine lattice solution
->
can one reach the bounded alphabet {-1,2}^n ?
```

PG15_UNSAT proves that this last step can still fail.

A future universal theorem must exploit the cubic-linear structure to control this
integer-to-two-level gap, or else produce a different global certificate.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e23_integer_saturation_cokernel_terminal.py
```
