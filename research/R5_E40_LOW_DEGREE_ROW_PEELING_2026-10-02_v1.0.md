# R5 E40 — Exact Low-Degree Row Peeling for Sparse Orthogonal Representations

Date: 2026-10-02

Status:
`EXACT_AFFINE_ROW_DEGREE_0_1_2_PROPAGATION__CANONICAL_3_CORE_PREPROCESSING`

Scientific ceiling:

```text
R5 E38 shows that unrestricted three-endpoint orthogonal representations already
contain the NP-complete square+cubic+linear Exact-One carrier.

This note adds the canonical exact preprocessing before any three-endpoint hard-core
analysis.

For an integer orthogonal representation R with ker_Q(R)=ker_Q(A), maintain the
affine centered system after forced Boolean assignments.  Every residual row of
support 0, 1, or 2 can be solved exactly without branching:

  support 0 -> consistency check,
  support 1 -> force one Boolean variable or UNSAT,
  support 2 -> at most two allowed Boolean pairs, hence forcing / equality /
               complement, or UNSAT.

Iterating these rules reaches a canonical residual 3-core in polynomial time.

This does not solve the degree-at-least-three core.
P_VS_NP = OPEN.
```

## 1. Affine centered system

Let

```text
R in Z^{m x n}
```

satisfy

```text
ker_Q(R)=ker_Q(A).
```

Exact-One is equivalent to

```text
y=3x-1,
x in {0,1}^n,
y_i in {-1,2},
R y=0.
```

During propagation some coordinates of `y` may become fixed. Move their
contributions to the right-hand side. The residual system has rows of the form

```text
sum_{i in S} c_i y_i = h,
```

where

```text
c_i in Z\{0},
y_i in {-1,2},
h in Z.
```

All transformations below preserve exact equivalence.

## 2. Residual support zero

If a residual row has no unfixed variables, it is

```text
0=h.
```

Therefore

```text
h != 0 -> UNSAT,
h = 0  -> delete the redundant row.
```

## 3. Residual support one

A one-variable row is

```text
c y_i = h,
c != 0.
```

Thus

```text
y_i=h/c.
```

There are only three possibilities:

```text
h/c = -1 -> force x_i=0,
h/c =  2 -> force x_i=1,
otherwise -> UNSAT.
```

No branching is required.

Every forced value is substituted into all remaining rows, which may create new
support-0/1/2 rows.

## 4. Residual support two

A two-variable row is

```text
a y_i+b y_j=h,
a b != 0.
```

Enumerate the four alphabet pairs

```text
(y_i,y_j) in {-1,2}^2.
```

Let `P` be the subset satisfying the equation.

A nonzero affine line in two variables cannot contain three corners of the square
`{-1,2}^2`, so

```text
|P| <= 2.
```

Hence:

```text
|P|=0 -> UNSAT;
|P|=1 -> force both variables;
|P|=2 -> one exact binary relation.
```

Every two-pattern relation on two Boolean bits is one of

```text
one variable fixed,
x_i=x_j,
x_i=1-x_j.
```

Indeed, if the two allowed bit strings share one coordinate, that coordinate is
fixed; if they differ in both coordinates, they are either the diagonal pair
`{00,11}` or anti-diagonal pair `{01,10}`.

Thus support-two rows are eliminated by ordinary forcing plus equality/complement
union-find. No branching is needed.

The homogeneous special case `h=0` recovers the R5 E18 projective ratio rule:

```text
y_j/y_i in {1,-2,-1/2}.
```

## 5. Polynomial fixed-point algorithm

Maintain:

```text
forced Boolean coordinates,
equality/complement classes,
residual affine rows,
and their current active support sizes.
```

Whenever a variable is fixed or two variables are identified, update the affected
rows. Process every row whose support falls to at most two.

Each successful forcing or identification strictly decreases the number of free
Boolean degrees of freedom. Each row deletion decreases the number of active rows.
Therefore there are only polynomially many major propagation events.

With sparse incidence lists, the whole fixed-point computation is polynomial in the
input size and coefficient bit length.

### Theorem LOW-DEGREE-PEEL

```text
boxed:
Every integer orthogonal representation can be reduced exactly in polynomial time
to either
  UNSAT,
or an equivalent residual affine system in which every active row contains at
least three free Boolean variables.
```

SAT reconstruction is immediate by reversing the recorded substitutions.

## 6. The three-endpoint hard boundary

Now suppose the representation under study has at most three nonzero entries per
column.

After LOW-DEGREE-PEEL, every active row has degree at least three. Therefore all
remaining difficulty is concentrated in a genuine higher-order incidence core; no
leaf or binary relation remains hidden inside it.

In the special square 3-regular case of R5 E12,

```text
number of rows = number of columns = n,
every column degree = 3,
every row degree = 3.
```

So the source is already exactly such a fully peeled 3-by-3 core. This explains why
the E38 support-three hardness wall is not caused by removable low-degree debris.

## 7. Relation to E39

R5 E39 branches on `t` exceptional non-signed-graphic columns and solves the
remaining two-endpoint system by f-factor.

LOW-DEGREE-PEEL should run before measuring the effective E39 backdoor:

```text
1. exact projective / gauge / equality reductions;
2. affine support-0/1/2 peeling;
3. delete all forced coordinates and redundant rows;
4. only then measure distance to the signed-graphic language.
```

This mirrors the E35 lesson that raw representation defects can dramatically
overestimate effective complexity.

## 8. Updated three-endpoint frontier

A genuine post-E40 representation-level survivor must now satisfy

```text
all active rows have support >=3,
effective distance to signed-graphic is superlogarithmic,
no projective/equality/complement reduction remains,
no TU/root/f-factor global representation is exposed,
and the residual three-endpoint coupling remains genuinely global.
```

The next useful target is therefore not arbitrary support-three structure. It is the
fully peeled, representation-invariant **3-core distance-to-signed-graphic** problem.

A future theorem must either

```text
(A) compress every such residual core to t=O(log n),
(B) expose another polynomial global language inside the 3-core,
(C) decompose it through bounded interfaces,
or
(D) exhibit a proof-carrying family whose reduced 3-core stays far from every
    signed-graphic representation.
```

```text
P_VS_NP = OPEN.
```
