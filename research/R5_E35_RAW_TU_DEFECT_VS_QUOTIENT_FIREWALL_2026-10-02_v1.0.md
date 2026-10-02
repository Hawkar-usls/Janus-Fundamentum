# R5 E35 — Raw TU Defect vs Exact Quotient Firewall

Date: 2026-10-02

Status:
`EXACT_LINEAR_RAW_TU_DISTANCE_FIREWALL__E16_HAS_OMEGA_N_BAD_MINOR_PACKING__POST_QUOTIENT_TU_DEFECT_ZERO`

Scientific ceiling:

```text
THIS NOTE KILLS THE NAIVE HOPE THAT SMALL RAW DISTANCE-TO-TU IS NECESSARY
FOR TRACTABILITY.

THE CONNECTED R5 E16 k-BLOCK RING HAS k PAIRWISE COLUMN-DISJOINT 3x3 MINORS
OF DETERMINANT -2.

THEREFORE ANY COLUMN-DELETION SET THAT MAKES THE RAW MATRIX TU MUST HAVE
SIZE AT LEAST

  k = n/9 = Theta(n).

YET THE EXACT R5 E28 PROJECTIVE QUOTIENT OF THE SAME FAMILY IS

  [ 1 | I_k | I_k ],

WHICH IS TOTALLY UNIMODULAR.

SO RAW TU DEFECT IS LINEAR WHILE EFFECTIVE POST-QUOTIENT TU DEFECT IS ZERO.
P_VS_NP = OPEN.
```

## 1. Recall the R5 E16 family

R5 E16 builds a connected square+cubic+linear source from `k` modified `3x3`
toroidal blocks.

The total size is

```text
n=9k.
```

R5 E27 proves the free kernel-projective diversity is

```text
q=2k+1,
```

and R5 E28 proves the projective quotient has exact elimination width two.

E35 now measures the raw distance of the original incidence matrix to total
unimodularity.

## 2. A fixed determinant-2 minor in every block

Number local variables in block `b` by offsets `0,...,8` as in the E16 checker.

Take rows

```text
9b+0,
9b+2,
9b+5
```

and columns

```text
9b+0,
9b+3,
9b+5.
```

The induced submatrix is exactly

```text
[1 1 0]
[1 0 1]
[0 1 1]
```

and therefore

```text
det = -2.
```

Hence the raw E16 matrix is not TU.

## 3. Disjoint bad-minor packing

For different blocks `b`, the three displayed columns lie in disjoint 9-variable
blocks.

Therefore the `k` determinant-2 minors have pairwise disjoint column supports.

Any column set whose deletion makes the whole matrix TU must hit every bad minor:
otherwise one untouched determinant-2 minor survives.

Because the supports are disjoint, at least one distinct deleted column is required
per block.

Thus

```text
boxed:
column_TU_distance(A_k) >= k = n/9.
```

So the raw TU-backdoor parameter from R5 E34 can be linear even on a family that is
already exactly polynomial by another JANUS branch.

## 4. The exact projective quotient

R5 E28 proves that after exact KPROJ compression the free quotient variables are

```text
H,
A_0,...,A_(k-1),
B_0,...,B_(k-1)
```

and every block contributes the single relation

```text
H + A_b + B_b = 1.
```

The quotient coefficient matrix is therefore

```text
Q_k = [ 1_k | I_k | I_k ].
```

It has `k` rows and `2k+1` columns.

## 5. Q_k is totally unimodular

Use the Ghouila-Houri signing criterion.

Take any subset of rows of `Q_k`.  Assign signs `+1,-1,+1,-1,...` as evenly as
possible inside that subset.

Then:

* the hub column `1_k` has signed sum in `{-1,0,1}`;
* every column of either identity copy has at most one selected nonzero, whose
  signed value is `+1` or `-1`.

Thus every column has signed sum in

```text
{-1,0,1}.
```

The Ghouila-Houri criterion gives

```text
boxed:
Q_k is totally unimodular.
```

Therefore the effective TU defect after exact quotienting is

```text
boxed:
0.
```

## 6. Raw vs effective defect

The same family satisfies simultaneously

```text
raw column-TU distance >= n/9,
post-KPROJ quotient TU distance = 0,
projective quotient width = 2.
```

So raw distance to TU is not an intrinsic hardness measure.

This repeats a pattern already seen for other raw parameters:

```text
raw nullity      -> local-gauge quotient may collapse it;
raw q            -> quotient width may collapse it;
raw TU defect    -> exact projective quotient may collapse it.
```

The router must therefore measure **effective** complexity only after all sound
forcing / equality / gauge / projective reductions have run.

## 7. Bad-minor packing as a general lower-bound certificate

The argument is not specific to E16.

Let an integer matrix contain bad square minors

```text
M_1,...,M_s
```

with

```text
|det(M_i)| >= 2.
```

If their column supports are pairwise disjoint, then every column deletion set that
makes the matrix TU has size at least `s`.

Thus a family of disjoint bad minors is a short proof-carrying lower bound on
column distance to TU.

More generally, arbitrary bad-minor supports turn the lower-bound problem into a
hitting-set packing problem.  The pairwise-disjoint case used here is exact and
immediate.

## 8. Router order correction

R5 E34 introduced TU-backdoors.  E35 fixes their position in the router.

The correct order is

```text
1. forced-coordinate propagation,
2. equality/projective quotient,
3. local-gauge / bounded-interface quotient,
4. simplify / deduplicate quotient relations,
5. only then measure or search distance-to-TU.
```

A raw TU-distance test before quotienting can dramatically overestimate true
complexity.

## 9. Updated TU frontier

After E35, the relevant firewall parameter is

```text
EFFECTIVE TU DEFECT
```

of the fully reduced quotient language, not of the original incidence matrix.

A genuine post-E35 survivor must retain

```text
effective TU column-deletion distance = omega(log n)
```

after all exact reductions.

This must coexist with the earlier hard-core conditions:

```text
integer feasibility,
large effective nullity,
large effective q,
large quotient width,
no root/TU global potential normal form,
no KPROJ/KLOC obstruction,
no bounded-interface decomposition,
no commuting/near-commuting structure.
```

## 10. Next target

The next useful construction should therefore avoid the E16 failure mode.

We need an explicit family whose **reduced quotient itself** contains many
distributed non-TU obstructions with no small separator and no low-width
elimination order.

A practical firewall target is:

```text
EFFECTIVE NON-TU PACKING CORE

After exact quotienting, produce Omega(n^epsilon) pairwise independent bad minors
or another certified TU-distance lower bound, while also keeping quotient width
superlogarithmic.
```

If every attempted high-defect family collapses under quotienting, that pattern may
point toward a stronger global regularization theorem.

```text
P_VS_NP = OPEN.
```

Companion exact checker:

```text
experiments/r5_e35_raw_tu_defect_firewall.py
```
