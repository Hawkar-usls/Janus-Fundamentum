# R5 E51 — Equitable Block-Count Quotient Terminal

Date: 2026-10-02

Status:
`EXACT_INTEGER_BLOCK_COUNT_QUOTIENT__POLYNOMIAL_UNSAT_CERTIFICATES__NONCOMMUTATIVE_LINEAR_SEMIDIRECT_FAMILY`

Scientific ceiling:

```text
THIS NOTE ADDS A NEW GLOBAL EXACT-COUNT CERTIFICATE THAT IS INDEPENDENT OF
KERNEL ENUMERATION, TU, f-FACTOR, ROOT-POTENTIAL, CONFLICT-MIS, AND LOCAL
CLAW-STATE ROUTES.

PARTITION ROWS AND VARIABLES INTO BLOCKS. IF EVERY VARIABLE IN ONE COLUMN
BLOCK HAS THE SAME NUMBER OF INCIDENCES INTO EACH ROW BLOCK, THEN SUMMING
THE EXACT-ONE EQUATIONS OVER ROW BLOCKS PRODUCES A SMALL INTEGER SYSTEM FOR
THE NUMBERS OF SELECTED VARIABLES IN THE COLUMN BLOCKS.

ANY RATIONAL / INTEGRAL / BOX INCONSISTENCY OF THIS QUOTIENT SYSTEM IS AN
EXACT POLYNOMIAL UNSAT CERTIFICATE.

AS A NONTRIVIAL CONTROL, A GENUINELY NONCOMMUTATIVE CONNECTED
SQUARE+CUBIC+LINEAR FAMILY FROM REGULAR C_p ⋊ C_3 ACTIONS HAS QUOTIENT
  2 s_0+s_1=p,
  2 s_1+s_2=p,
  2 s_2+s_0=p,
SO s_0=s_1=s_2=p/3. FOR p≡1 (mod 3) THIS IS NONINTEGRAL, HENCE THE WHOLE
INFINITE FAMILY IS UNSAT.

P_VS_NP = OPEN.
```

## 1. General block setting

Let

```text
A in {0,1}^{m x n}
```

be any Exact-One incidence matrix and consider

```text
A x = 1,
x in {0,1}^n.
```

Partition the rows into blocks

```text
R_1,...,R_a
```

and the columns into blocks

```text
C_1,...,C_b.
```

For every row block `R_r` and column `j`, define

```text
d_r(j)=#{ i in R_r : A_ij=1 }.
```

Assume the column partition is equitable with respect to the row partition:
for every pair `(r,c)`, the number `d_r(j)` is constant over all

```text
j in C_c.
```

Write that constant as

```text
Q_(r,c).
```

Thus `Q` is an `a x b` nonnegative integer quotient-incidence matrix.

## 2. Selected block counts

For any Boolean vector `x`, define

```text
s_c = sum_{j in C_c} x_j.
```

Hence

```text
0 <= s_c <= |C_c|,
s_c in Z.
```

Now sum the Exact-One equations over one row block `R_r`:

```text
sum_{i in R_r} (Ax)_i = |R_r|.
```

Swap the order of summation:

```text
sum_j d_r(j) x_j = |R_r|.
```

Group columns by `C_c` and use equitability:

```text
sum_c Q_(r,c) s_c = |R_r|.
```

Therefore every Exact-One witness induces an integer block-count vector `s`
satisfying

```text
boxed:
Q s = rho,
```

where

```text
rho_r=|R_r|.
```

## 3. Equitable block-count obstruction

The quotient system gives immediate exact UNSAT certificates.

### Rational inconsistency

If

```text
Q s=rho
```

has no rational solution, then the original Exact-One instance is UNSAT.

### Integrality inconsistency

If every rational solution violates

```text
s in Z^b,
```

then the original instance is UNSAT.

A particularly cheap case occurs when `Q` has full column rank and the unique
rational solution contains a noninteger coordinate.

### Box inconsistency

Likewise, if no integer quotient solution obeys

```text
0 <= s_c <= |C_c|,
```

then the original instance is UNSAT.

All three are sound because they are necessary consequences obtained by summing
original source equations.

## 4. Polynomial regimes

The quotient is useful whenever its integer feasibility can be checked in polynomial
time.

Several exact cases are immediate and self-contained.

### Unique rational solution

If `rank(Q)=b`, solve the rational linear system exactly. Then check integrality and
box bounds coordinatewise. This is polynomial for arbitrary `b`.

### Constant number of column blocks

If

```text
b=O(1),
```

enumerate

```text
s_c in {0,...,|C_c|}.
```

There are at most

```text
(n+1)^b
```

count vectors, hence polynomially many for fixed `b`.

If none satisfies `Q s=rho`, return UNSAT.

The quotient is only a necessary condition in general: an integer block-count
solution does not by itself reconstruct an Exact-One witness unless an additional
block-internal theorem applies.

Therefore E51 is primarily an exact UNSAT terminal / certificate language, not a
universal SAT solver.

## 5. Source-aligned certificate form

Every quotient row is literally the sum of original Exact-One equations in one
row block.

Hence a verifier needs only:

```text
1. the row partition;
2. the column partition;
3. the quotient matrix Q;
4. verification that every column in C_c has the claimed incidence count Q_(r,c)
   into every row block R_r;
5. an exact rational/integer contradiction for Qs=rho under the block-count bounds.
```

So the certificate is proof-carrying and polynomially checkable.

This is an explicit source-aligned UNSAT mechanism in the sense sought earlier in
the R5 route.

## 6. Noncommutative linear semidirect family

Let

```text
p prime,
p ≡ 1 mod 3.
```

Choose

```text
a in F_p^*
```

of exact multiplicative order three:

```text
a^3=1,
a!=1.
```

Consider the nonabelian semidirect product

```text
G = C_p ⋊_a C_3
```

with presentation

```text
r^p=1,
s^3=1,
s r s^-1 = r^a.
```

The group has odd order

```text
|G|=3p.
```

Index variables and source rows by

```text
(k,i) in Z_3 x Z_p.
```

Use the three regular perfect matchings corresponding to

```text
identity,
right multiplication by r,
right multiplication by s.
```

In coordinates this gives source rows

```text
R_(k,i) = {
  (k,i),
  (k,i+a^k),
  (k+1,i)
}.
```

All indices are modulo `3` or `p` as appropriate.

## 7. Square, cubic, connected, noncommutative

There are exactly

```text
n=3p
```

rows and variables.

Every row has three distinct variables.

Fix a variable `(k,j)`. It occurs in exactly

```text
R_(k,j),
R_(k,j-a^k),
R_(k-1,j),
```

so every column also has degree three.

Thus the carrier is square+cubic.

The matchings generated by `r` and `s` generate the full regular group action, so
the incidence structure is connected.

Because

```text
a != 1,
```

`r` and `s` do not commute. Hence this family lies genuinely outside the connected
commuting sector closed by R5 E13/E29.

## 8. Linearity

A union of two perfect matchings in a bipartite incidence graph contains a 4-cycle
exactly when the relative permutation has a 2-cycle.

For the three regular matchings above, every nontrivial relative permutation is
right multiplication by a nonidentity element of `G`.

Since `|G|=3p` is odd, every group element has odd order. Therefore every cycle of a
nonidentity regular right multiplication has odd length and in particular not
length two.

So no pair of matching colors creates a 4-cycle.

Equivalently, no two source rows share two target variables.

Hence

```text
boxed:
the semidirect carrier is linear.
```

Thus this is a genuine infinite family inside the frozen square+cubic+linear
carrier class.

## 9. Three-layer equitable quotient

Partition rows and variables by their `k in Z_3` layer.

Let

```text
s_k = #{ selected variables in layer k }.
```

Each row of layer `k` contains

```text
two variables from layer k,
one variable from layer k+1.
```

More importantly for the summed equations, every variable of layer `k` is incident
twice with row layer `k`, and every variable of layer `k+1` is incident once with
row layer `k`.

Therefore the equitable quotient matrix is

```text
Q =
[2 1 0]
[0 2 1]
[1 0 2].
```

Each row block contains exactly `p` source rows, so

```text
rho=(p,p,p)^T.
```

Every Exact-One witness must satisfy

```text
2 s_0+s_1=p,
2 s_1+s_2=p,
2 s_2+s_0=p.
```

## 10. Unique quotient solution

The quotient matrix has determinant

```text
9.
```

Solving gives

```text
boxed:
s_0=s_1=s_2=p/3.
```

But

```text
p ≡ 1 mod 3,
```

so `p/3` is not an integer.

Therefore no Boolean Exact-One witness exists:

```text
boxed:
Every C_p ⋊ C_3 carrier above is UNSAT.
```

The decision is obtained solely from three aggregated count equations.

## 11. Finite controls

The companion checker constructs the carriers for

```text
p=7,13,19.
```

For each it verifies exactly:

```text
square,
cubic,
linear,
Q=[[2,1,0],[0,2,1],[1,0,2]],
unique quotient counts=(p/3,p/3,p/3),
nonintegrality -> UNSAT.
```

For `p=7` it additionally performs an independent direct layer enumeration and
finds no witness.

## 12. Relation to previous routes

This family survives the most obvious attempt to dismiss it as commuting:

```text
G is genuinely nonabelian.
```

It also avoids the dihedral false start where an involutory reflection matching
created 4-cycles and violated linearity.

The E51 obstruction instead comes from a global coarse quotient that is invisible
if one looks only at raw local clause structure.

The mechanism is independent of:

```text
small nullity enumeration,
commuting normal forms,
signed-graphic f-factors,
root potentials,
conflict line graphs,
chordal rigidity,
unique-claw 2-SAT.
```

## 13. Router branch

Add the global quotient layer:

```text
BCQ0  propose / discover row and column partitions;
BCQ1  verify incidence equitability exactly;
BCQ2  build quotient Q and row-size vector rho;
BCQ3  solve Qs=rho over Q;
BCQ4  if unique, test integer and box constraints;
BCQ5  for constant quotient dimension, enumerate bounded integer counts;
BCQ6  inconsistency -> exact UNSAT certificate;
BCQ7  feasible quotient -> continue to deeper branches unless a separate internal
      reconstruction theorem applies.
```

## 14. Updated frontier

A genuine hard survivor must now avoid yet another global compression mechanism:
its source incidence pattern cannot expose a small equitable block quotient whose
selected-count equations are arithmetically inconsistent.

This is especially relevant for highly symmetric noncommutative constructions: E51
shows that noncommutativity and linearity alone do not prevent a tiny exact quotient
from killing the instance.

The next high-value attack is therefore:

```text
EQUITABLE-QUOTIENT SATURATION
```

on the E12 hard bridge and other hostile controls: compute the coarsest useful
row/column incidence partitions and determine whether every surviving quotient is
count-feasible, then combine quotient counts with the existing local-state and
kernel-language reductions.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e51_equitable_block_count_quotient.py
```
