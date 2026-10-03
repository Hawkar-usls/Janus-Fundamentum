# R5 E61 — Two-Level Kernel / Hoffman Regular-Set Theorem

Date: 2026-10-03

Status:
`EXACT_ONE_IFF_TWO_LEVEL_REAL_KERNEL_IFF_HOFFMAN_TIGHT_0_3_REGULAR_SET__FPT_IN_REAL_NULLITY`

Scientific ceiling:

```text
THIS NOTE DOES NOT GIVE A UNIVERSAL POLYNOMIAL ALGORITHM.

IT IDENTIFIES THE EXACT DISCRETE OBJECT MISSING FROM THE E57 HOFFMAN ENDPOINT,
AND IT GIVES AN EXACT 2^d * poly(n) ALGORITHM PARAMETERIZED BY

    d = dim_R ker(A).

FOR A LINEAR SQUARE-CUBIC CARRIER, THE SAME PARAMETER IS

    d = mult_G(-3)

FOR THE 6-REGULAR CONFLICT GRAPH G=A^T A-3I.

EXACT-ONE IS EQUIVALENT TO THE -3 EIGENSPACE CONTAINING A TWO-LEVEL VECTOR
WITH COORDINATES {-1,2}.  EQUIVALENTLY, G MUST CONTAIN A (0,3)-REGULAR SET,
A PERFECT 2-COLORING WITH QUOTIENT MATRIX

    [0 6]
    [3 3]

THAT SET IS AN INDEPENDENT SET OF SIZE n/3 ATTAINING THE HOFFMAN BOUND.

THE PARAMETERIZED SEARCH IS POLYNOMIAL WHEN d=O(log n), BUT d IS NOT KNOWN
TO BE O(log n) ON THE UNIVERSAL HARD CLASS.  THEREFORE THIS IS A REAL GLOBAL
SOLVER MECHANISM, NOT A P=NP CLOSURE.

P_VS_NP = OPEN.
```

## 1. Universal two-level kernel equivalence

Let `A` be a square `n x n` `0/1` carrier with every row and every column of
weight `3`.  Exact-One asks for

```text
x in {0,1}^n
A x = 1
```

where the equality is over the integers, not merely modulo a field.

Define

```text
y = 3x - 1.
```

Since every row of `A` has weight `3`,

```text
A 1 = 3 1.
```

Therefore

```text
A y = 3 A x - A 1.
```

Hence

```text
boxed:
A x = 1 with x in {0,1}^n
iff
A y = 0 with y in {-1,2}^n.
```

The converse is exact: given `y in {-1,2}^n`, put

```text
x=(y+1)/3.
```

Then `x` is Boolean and `Ay=0` gives `Ax=1`.

Because every column also has weight `3`, any real kernel vector is orthogonal
to the all-one vector:

```text
0 = 1^T A y = 3 1^T y.
```

For a two-level vector this forces exactly `n/3` coordinates equal to `2` and
`2n/3` coordinates equal to `-1`.

Thus if

```text
S={i:y_i=2},
```

then every Exact-One witness has

```text
|S|=n/3.
```

This theorem does not require linearity.

## 2. Gram bridge and the -3 eigenspace

Now assume the square-cubic carrier is linear, so two columns meet in at most
one row.  Define the column conflict graph `G` by joining two columns when they
occur in a common row.  Then

```text
A^T A = 3I + Adj(G).
```

Every column belongs to three rows and each row contributes two distinct
conflict neighbours, hence `G` is simple and 6-regular.

Also `A^T A` is positive semidefinite, so

```text
lambda_min(G) >= -3.
```

For every `y in ker_R(A)`,

```text
(A^T A)y=0
```

and therefore

```text
boxed:
Adj(G)y=-3y.
```

Consequently

```text
dim_R ker(A) = mult_G(-3).
```

R5 E57 showed that the existence of the eigenvalue `-3`, singularity of `A`,
and even a full-support real kernel vector are not sufficient for Exact-One.
E61 identifies the missing condition exactly: the `-3` eigenspace must contain
a vector whose coordinates take precisely the two levels `-1` and `2`.

## 3. Local quotient forced by the two levels

Let `y in {-1,2}^n` satisfy

```text
Adj(G)y=-3y
```

and let `S={i:y_i=2}`.

Fix a vertex `v`, and let `a(v)` be the number of its neighbours that lie in
`S`.  Since `G` is 6-regular, the sum of the neighbouring `y` values is

```text
2 a(v) - (6-a(v)) = 3a(v)-6.
```

If `v in S`, the eigen-equation requires

```text
3a(v)-6=-6,
```

so

```text
a(v)=0.
```

If `v notin S`, the eigen-equation requires

```text
3a(v)-6=3,
```

so

```text
a(v)=3.
```

Therefore `S` is independent, every vertex outside `S` has exactly three
neighbours in `S`, and the partition `(S,V-S)` is equitable with quotient
matrix

```text
boxed:
Q = [[0,6],
     [3,3]].
```

In the standard terminology, `S` is a `(0,3)`-regular set and the partition is
a perfect 2-coloring.

Conversely, a `(0,3)`-regular set in this 6-regular graph gives the same
`{-1,2}` eigenvector and therefore, through Section 1, an Exact-One solution.

Thus for the linear square-cubic class:

```text
boxed:
Exact-One
iff {-1,2}-valued vector in E_G(-3)
iff (0,3)-regular set in G
iff perfect 2-coloring with quotient [[0,6],[3,3]].
```

## 4. Hoffman equality is exact, not merely necessary

For a 6-regular graph with least eigenvalue `-3`, Hoffman's ratio bound gives

```text
alpha(G) <= n * 3/(6+3) = n/3.
```

The standard equality characterization says that if an independent set attains
this bound, every vertex outside it has exactly `3` neighbours in the set.  So
in our class an independent set of size `n/3` is automatically the `(0,3)`
regular set above.

Hence

```text
boxed:
Exact-One
iff alpha(G)=n/3
iff the Hoffman bound is attained.
```

This explains precisely why R5 E57's condition `lambda_min=-3` was too weak:
the endpoint eigenvalue only makes equality possible.  The hard discrete step
is finding a Boolean/two-level point in the endpoint eigenspace.

This is the classical bridge between Hoffman-tight independent sets and
`(k,tau)`-regular sets / perfect 2-colorings.  Useful literature anchors:

* D. M. Cardoso, V. V. Lozin, C. J. Luz, M. F. Pacheco,
  "Efficient domination through eigenvalues", Discrete Applied Mathematics
  214 (2016), 54-62.  Proposition 2.1 characterizes `(k,tau)`-regular sets as
  0-1 solutions of

      (Adj(G)-(k-tau)I)x=tau*1.

  For `(k,tau)=(0,3)` this is exactly

      (Adj(G)+3I)x=3*1.

  Open manuscript: https://wrap.warwick.ac.uk/80237/

* D. M. Cardoso et al., "An overview of (kappa,tau)-regular sets and their
  applications", Discrete Applied Mathematics 269 (2019), 2-10,
  DOI 10.1016/j.dam.2018.12.020.  The survey records that recognition is
  NP-complete in general while spectral algorithms become effective on classes
  with bounded/small relevant eigenvalue multiplicity.

The literature therefore confirms that the eigenspace-plus-Boolean-point
formulation is a standard hard combinatorial boundary, rather than an automatic
spectral solution.

## 5. Exact 2^d algorithm from free coordinates

Let

```text
d = dim_R ker(A).
```

Compute an exact rational RREF of `A` in polynomial time.  Let

```text
f_1,...,f_d
```

be the free coordinate positions.  Choose the standard nullspace basis

```text
b_1,...,b_d
```

where the restriction to the free coordinates is the identity matrix:

```text
(b_j)_(f_i) = delta_ij.
```

Every kernel vector is uniquely

```text
y = c_1 b_1 + ... + c_d b_d,
```

and its free coordinate values are exactly `c_1,...,c_d`.

If `y` is an Exact-One two-level kernel vector, each free coordinate must be
one of

```text
-1, 2.
```

Therefore there are only

```text
2^d
```

possible assignments to inspect.  For each assignment, all pivot coordinates
are forced by linear algebra; accept precisely when every forced coordinate is
again in `{-1,2}`.

So we have the exact deterministic algorithmic bound

```text
boxed:
T(n,d) = 2^d * poly(n).
```

For the linear class,

```text
d = mult_G(-3).
```

Hence Exact-One is polynomial whenever `d=O(log n)`.

This is not claimed to be a universal polynomial bound: arbitrary square-cubic
carriers can have growing real nullity, and no theorem in this note bounds `d`
by `O(log n)` on the frozen hard family.

## 6. Replay controls

The companion checker freezes two linear `n=12` carriers.

### SAT12

```text
real nullity       = 1
two-level witnesses= 1
S                  = {8,9,10,11}
```

The witness is

```text
y=(-1,-1,-1,-1,-1,-1,-1,-1,2,2,2,2).
```

It satisfies

```text
Ay=0,
Gy=-3y,
```

and `S` has quotient matrix `[[0,6],[3,3]]`.

### UNSAT12_E57

The frozen R5 E57 negative control has

```text
real nullity       = 1
two-level witnesses= 0.
```

Yet it has the full-support integer kernel vector

```text
(-1,-1,2,-1,2,2,2,-4,2,-4,-1,2).
```

So even at nullity one, the exact distinction is not "kernel or no kernel" and
not "full support or not".  It is exactly the two-level intersection.

Companion checker:

```text
experiments/r5_e61_two_level_kernel_hoffman_regular_set.py
```

## 7. Consequence for the universal frontier

E61 gives a clean hierarchy:

```text
linear algebra:
    compute ker_R(A)                     polynomial

spectral endpoint:
    detect mult_G(-3)>0                  polynomial

parameterized exact search:
    test {-1,2} intersection             2^d poly(n)

universal missing theorem:
    remove the exponential dependence on d
    OR prove a new structural compression of the -3 eigenspace on all
    square-cubic-linear hard instances.
```

The next high-value question is therefore not another local claw case and not
another spectral endpoint test.  It is:

```text
Can the {-1,2}-intersection of E_G(-3)=ker_R(A) be decided without enumerating
2^d free-coordinate assignments, using the additional triangle decomposition
G inherits from the rows of A?
```

Equivalently, can the `(0,3)`-regular-set problem be compressed polynomially on
this very special 6-regular, edge-disjoint-triangle-decomposed conflict class?

Until such a mechanism is proved:

```text
P_VS_NP = OPEN.
```
