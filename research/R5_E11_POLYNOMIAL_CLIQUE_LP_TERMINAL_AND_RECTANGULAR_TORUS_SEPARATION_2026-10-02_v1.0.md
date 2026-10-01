# R5 E11 — Polynomial Clique-LP Terminal and Rectangular-Torus Separation

Date: 2026-10-02

Status:
`NEW_POLYNOMIAL_UNSAT_TERMINAL__EXACT_DUAL_CERTIFICATE__EXPLICIT_INCOMPLETENESS_FIREWALL`

Scientific ceiling:

```text
THE CLIQUE LP IS A SOUND POLYNOMIAL UNSAT TERMINAL.
IT IS NOT A COMPLETE DECISION PROCEDURE.
THE RECTANGULAR TORUS FAMILY BELOW GIVES EXPLICIT K4-FREE UNSAT FALSE POSITIVES.
P_VS_NP = OPEN.
```

## 1. Setting

Let `A in {0,1}^{m x n}` encode a monotone Exact-One instance with exactly three ones in every row.  Let `G_A` be the conflict graph on columns: two variables are adjacent iff they co-occur in a source row.

Every Boolean Exact-One witness satisfies

```text
A x = 1,
x >= 0,
x(C) <= 1 for every clique C of G_A.
```

The last inequalities are valid because a witness is an independent set of `G_A`.

## 2. Polynomial clique-LP terminal for cubic sources

Consider the LP feasibility system

```text
A x = 1,
x >= 0,
x(C) <= 1  for every maximal clique C of G_A.
```

If the LP is infeasible, then the original Exact-One instance is UNSAT.

For a cubic source every variable occurs in at most three 3-clauses, so

```text
Delta(G_A) <= 6.
```

Every maximal clique containing a vertex `v` is contained in the closed neighborhood `N[v]`, whose size is at most seven.  Hence all maximal cliques can be enumerated by testing the at most `2^7` subsets of each closed neighborhood and deduplicating them.

Thus the complete maximal-clique list is polynomial-size and polynomial-time enumerable on this source class.  Standard rational linear programming therefore gives a deterministic polynomial terminal:

```text
CLIQUE_LP(A):
  enumerate maximal cliques of G_A;
  solve the rational feasibility LP;
  if infeasible: return certified UNSAT;
  otherwise: return UNKNOWN / pass to the next terminal.
```

This is a genuine algorithmic terminal, not only a certificate verifier.

## 3. Dual source-aligned weighted-clique certificate

A particularly transparent infeasibility certificate is obtained as follows.

Let `theta_C >= 0` be nonnegative clique weights and let `lambda in Q^m` satisfy

```text
A^T lambda <= sum_C theta_C 1_C
```

coordinatewise.

For any Exact-One witness `x>=0`,

```text
lambda^T 1
= lambda^T A x
= (A^T lambda)^T x
<= sum_C theta_C x(C)
<= sum_C theta_C.
```

Therefore the strict inequality

```text
lambda^T 1 > sum_C theta_C
```

is a polynomially checkable UNSAT certificate.

This is the weighted extension of the R5 E10 source-aligned subset/clique-cover theorem.

## 4. PG15_UNSAT is caught exactly

For the frozen PG15_UNSAT control, R5 E10 already provides

```text
U = V \ {2,6,11},
```

three disjoint `K4` cliques

```text
{1,7,9,13},
{3,8,10,15},
{4,5,12,14},
```

and the scaled row-space vector

```text
c = (9,5,8,10,6,-18,11,3,13,6,8,9,2,4,0)
```

with

```text
A^T c = 19 * 1_U,
sum(c)=76.
```

Take

```text
lambda = c/19
```

and clique weights `theta_C=1` on the three displayed `K4`s.  Then

```text
A^T lambda = 1_U = sum_C theta_C 1_C
```

because the three cliques are disjoint, while

```text
lambda^T 1 = 76/19 = 4 > 3 = sum_C theta_C.
```

Thus the general LP dual recovers the explicit local contradiction `4<=3`.

On the frozen PG15_SAT control the primal LP is feasible, as it must be; in an exact finite replay it can return an actual Boolean witness.

## 5. Why this terminal cannot be universal

If `G_A` has clique number at most three, then the universal fractional point

```text
x = (1/3) 1
```

satisfies

```text
A x = 1
```

because every source row has size three, and every clique inequality because

```text
x(C) = |C|/3 <= 1.
```

Therefore for every `K4`-free source the clique LP is automatically feasible, irrespective of whether the Boolean Exact-One instance is SAT or UNSAT.

So a `K4`-free UNSAT source is an explicit false positive for this relaxation.

## 6. Rectangular toroidal source family

For integers `a,b >= 4`, define variables

```text
x_{i,j},  (i,j) in Z_a x Z_b,
```

and clauses

```text
C_{i,j} = {x_{i,j}, x_{i+1,j}, x_{i,j+1}},
```

with indices modulo `a,b`.

Call the square incidence matrix `A_{a,b}`.

It has `ab` variables and `ab` clauses; every row and every column has weight three.  Distinct clauses share at most one variable, so it is linear.

Its conflict graph is the triangular torus with adjacency differences

```text
+-e1,
+-e2,
+-(e1-e2).
```

For `a,b>=4` there is no short wrap-around identification creating a fourth mutually adjacent vertex; hence

```text
omega(G_{a,b}) = 3.
```

In particular, the clique LP always accepts the fractional point `x=(1/3)1`.

## 7. Exact rational rank of the rectangular torus

The matrix is block-circulant.  On a Fourier character `(z,w)`, where

```text
z^a=1,
w^b=1,
```

the eigenvalue is, up to the harmless convention of inverse shifts,

```text
1 + z + w.
```

For unit complex numbers, `1+z+w=0` holds iff `{1,z,w}` are the three cube roots of unity.  Consequently a zero eigenvalue exists iff

```text
3 | a  and  3 | b.
```

More precisely, over characteristic zero,

```text
nullity_Q(A_{a,b}) = 2  if 3|a and 3|b,
nullity_Q(A_{a,b}) = 0  otherwise.
```

Thus whenever at least one dimension is not divisible by three, `A_{a,b}` is rationally invertible.  Since

```text
A_{a,b} * (1/3 1) = 1,
```

the unique rational solution is `x=(1/3)1`, which is not Boolean.  Therefore the Exact-One instance is UNSAT.

When both dimensions are divisible by three, an explicit Boolean witness is

```text
x_{i,j}=1 iff i-j == 0 (mod 3),
```

so the instance is SAT.

Hence

```text
A_{a,b} is Exact-One SAT
iff
3|a and 3|b.
```

## 8. Strong separation family

Take

```text
a = 3t,
b = 3t+1,
t >= 2.
```

Then

```text
n = a b = 3t(3t+1)
```

is divisible by three, so the global cardinality obstruction `n mod 3` does not reject the instance.

Nevertheless:

```text
A_{a,b} is square, cubic and linear;
G_{a,b} is K4-free;
G_{a,b} contains a large toroidal grid and has unbounded treewidth;
x=(1/3)1 passes every clique inequality;
A_{a,b} is full rank over Q;
the Boolean instance is UNSAT.
```

Therefore this family cleanly separates the two polynomial terminals:

```text
CLIQUE_LP  -> UNKNOWN / feasible,
Q-RANK     -> certified UNSAT.
```

It is also a stronger hostile control than the square `k x k` UNSAT torus, because `n` is already divisible by three.

## 9. Combined polynomial router now available

For square cubic sources we can safely run:

```text
T0: if n mod 3 != 0 -> UNSAT.

T1: exact rational rank/nullity.
    if nullity_Q(A)=0 -> UNSAT,
    since the unique solution is (1/3)1.

T2: if nullity d is small -> enumerate 2^d free Boolean assignments exactly.

T3: maximal-clique LP.
    if infeasible -> UNSAT with a dual weighted-clique certificate.

otherwise -> unresolved hard core.
```

Every branch is exact.  No `SAT` or `UNSAT` is promoted from a relaxation without a reconstructible certificate.

## 10. What remains for P=NP

The remaining obstruction is sharply localized:

```text
square/cubic source,
nullity_Q(A) large enough that 2^d is not polynomial,
clique LP feasible,
no earlier decomposition/terminal applies.
```

For linear sources this is equivalently a 6-regular triangle-decomposed graph with a large `-3` eigenspace, because

```text
A^T A = 3I + Adj(G_A).
```

The next target is therefore not generic treewidth and not generic clique LP.  It is:

```text
LARGE -3 EIGENSPACE + SOURCE TRIANGLE DECOMPOSITION
    -> constructive {-1,2} kernel vector
       OR a polynomially detectable stronger obstruction
       OR a polynomial decomposition reducing nullity.
```

That is the current universal frontier.

P_VS_NP = OPEN.
