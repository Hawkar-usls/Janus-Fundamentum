# R5 E34 — Distance-to-TU Backdoor

Date: 2026-10-02

Status:
`EXACT_FPT_COLUMN_DELETION_TO_TU__O_2T_POLY__TU_KERNEL_DEFECT_PARAMETER`

Scientific ceiling:

```text
THIS NOTE EXTENDS THE R5 E33 TU TERMINAL TO MATRICES THAT BECOME TU AFTER
DELETING / BRANCHING ON ONLY t VARIABLE COORDINATES.

IF A SET S OF t COLUMNS IS GIVEN SUCH THAT THE RESIDUAL MATRIX IS TOTALLY
UNIMODULAR, EXACT-ONE IS SOLVABLE IN

  O(2^t poly(n)).

THE SAME STATEMENT HOLDS FOR ANY EXPOSED INTEGER ORTHOGONAL REPRESENTATION
R WITH ker_Q(R)=ker_Q(A): IF R WITHOUT t COLUMNS IS TU, BRANCH ON THOSE
COORDINATES AND SOLVE EACH RESIDUAL BY TU LP.

THEREFORE t=O(log n) IS A NEW POLYNOMIAL ISLAND.
P_VS_NP = OPEN.
```

## 1. Direct matrix backdoor

Consider any Boolean linear system

```text
A x = 1,
x in {0,1}^n,
```

with integer matrix `A`.

Let

```text
S subseteq [n],
|S|=t,
T=[n]\S.
```

Write

```text
A=[A_S | A_T].
```

Assume

```text
A_T
```

is totally unimodular.

We call `S` a **column TU-backdoor**.

## 2. Branch on the backdoor coordinates

Enumerate all

```text
sigma in {0,1}^S.
```

For one branch, the remaining variables must satisfy

```text
A_T x_T = 1 - A_S sigma.
```

The right-hand side is integral.

Add the box constraints

```text
0 <= x_T <= 1.
```

Because `A_T` is totally unimodular, adjoining signed identity rows preserves total
unimodularity.  Therefore every vertex of the residual polytope is integral.

Hence the branch has a Boolean completion if and only if the residual LP is
feasible.

Each branch is solvable in polynomial time.

There are `2^t` branches, so:

### Theorem TU-BACKDOOR-A

```text
boxed:
Given a column set S of size t such that A_T is TU,
Exact-One is decidable in O(2^t poly(n)).
```

Consequently

```text
t=O(log n)
```

gives a deterministic polynomial algorithm.

## 3. Orthogonal-kernel representation version

R5 E33 showed that Exact-One depends only on the centered kernel language.

Suppose an integer matrix

```text
R in Z^{r x n}
```

satisfies

```text
ker_Q(R)=ker_Q(A).
```

A Boolean witness is equivalent to

```text
R(3x-1)=0,
```

or

```text
R x=(R1)/3.
```

Again partition columns into `S,T`, with `|S|=t`, and assume

```text
R_T
```

is TU.

For a branch `x_S=sigma`, the residual system is

```text
R_T x_T
=
(R1)/3 - R_S sigma.
```

If the right-hand side is not integral, the branch cannot contain a Boolean
solution and is rejected immediately.

If it is integral, solve

```text
R_T x_T=b,
0<=x_T<=1.
```

TU integrality again makes LP feasibility equivalent to Boolean completion.

Therefore:

### Theorem TU-BACKDOOR-KERNEL

```text
boxed:
If ker_Q(R)=ker_Q(A) and deleting t coordinate columns makes R TU,
Exact-One is decidable in O(2^t poly(n)).
```

This may be stronger than applying the backdoor directly to `A`, because a different
orthogonal representation can expose much smaller TU defect.

## 4. SAT reconstruction and UNSAT certificates

For a feasible branch, return any integral basic feasible solution of the TU
residual LP and combine it with the fixed bits on `S`.

For an infeasible branch, a rational Farkas / LP dual certificate proves residual
infeasibility.

An UNSAT result for the whole instance consists of the `2^t` branch certificates.
For `t=O(log n)` this collection has polynomial total size.

Thus the FPT algorithm is proof-carrying in the same sense as the earlier JANUS
router branches.

## 5. Relation to R5 E33

When

```text
t=0,
```

TU-BACKDOOR-KERNEL is exactly the R5 E33 TU-kernel terminal.

So E34 is a strict parameterized extension:

```text
E33 : TU defect 0,
E34 : TU defect t.
```

The relevant complexity parameter is not merely whether the kernel language is TU,
but how many coordinate variables must be fixed before the remaining language is
TU.

## 6. Relation to the original source matrix

The direct version needs no centered reformulation.

If the original square+cubic+linear matrix `A` becomes TU after deleting `t`
variable columns, branch on those `t` Exact-One variables directly.

This yields the exact branch

```text
T0  find / receive candidate TU-backdoor S
T1  verify A_T is TU
T2  enumerate sigma in {0,1}^S
T3  solve TU residual LP
T4  reconstruct SAT witness or combine branch UNSAT certificates
```

No assumptions about rational nullity, KLOC, projective diversity, or quotient width
are needed.

## 7. Interaction with projective quotienting

R5 E18/E28 may first identify/fix many original coordinates.

The TU-backdoor search should therefore run after exact quotienting whenever
possible: forced variables can be removed for free, and equality classes can be
represented once.

A high raw distance to TU can collapse to a small effective distance after these
exact reductions.

This parallels earlier lessons:

```text
raw nullity != effective nullity,
raw q       != quotient width,
raw TU defect != effective TU defect.
```

## 8. Updated hard core

After E34, a genuine survivor must have more than a non-TU row space.

It must have

```text
TU column-deletion distance = omega(log n)
```

for every useful exposed orthogonal representation, after the earlier exact
forcing/quotient steps.

Therefore the post-E34 frontier becomes:

```text
NON-TU HIGH-DEFECT GLOBAL KERNEL LANGUAGE
+
large effective nullity
+
large projective diversity
+
large projective-quotient width
+
integer feasibility
+
no KPROJ/KLOC/global-potential shortcut.
```

## 9. Next target

The next useful attack is not another binary question `TU or not TU`.

The stronger structural target is:

```text
TU-BACKDOOR COMPRESSION DICHOTOMY

For every projectively reduced integer-feasible carrier, either
  (A) expose a TU-backdoor of O(log n) coordinates,
  (B) expose another compact global normal form,
  (C) decompose/quotient the instance,
  or
  (D) construct an explicit family whose effective TU defect is omega(log n).
```

Branch (D) is the correct firewall target after E34.

```text
P_VS_NP = OPEN.
```

Companion finite controls:

```text
experiments/r5_e34_distance_to_tu_backdoor.py
```
