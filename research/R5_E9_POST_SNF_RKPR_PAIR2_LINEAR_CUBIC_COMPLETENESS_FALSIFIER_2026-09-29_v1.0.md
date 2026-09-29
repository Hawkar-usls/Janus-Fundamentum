# R5 E9 — Post-SNF/RKPR pair-projection completeness falsifier on the linear-cubic carrier

Date: 2026-09-29
Status: PROVED LINEAR-CUBIC FALSIFIER
Global status: `P_VS_NP = OPEN`; `E8_D1 = EMPTY`.

## 1. Result

There is an explicit connected square **linear cubic** Positive-1-in-3 source `L` such that

```text
Exact-One(L) = UNSAT
1 in L Z^120 = true
RKPR(L) has no zero rows and no illegal projective ratio
full integer-lattice pair-projection 2-CSP Phi_L = SAT
```

Therefore the conjectural polynomial shortcut

```text
integer-lattice membership
+ exhaustive RKPR
+ all unary/pair Boolean integer projections
+ 2-SAT consistency
=> Exact-One SAT
```

is false even inside the connected square linear-cubic source carrier.

The live gate

```text
R5_E9_POST_SNF_RKPR_PAIR2_LINEAR_CUBIC_COMPLETENESS_FALSIFIER_GATE_V1
```

is therefore CLOSED / FALSIFIED.

This result does not imply `P != NP`; it only closes one proposed polynomial completeness criterion.

---

## 2. A 12-variable cubic pair2-survivor

Let

```text
A = I + P + Q
```

with zero-based permutations

```text
P = [4,2,6,9,3,8,0,10,1,11,5,7]
Q = [7,0,5,6,2,1,9,11,4,8,3,10].
```

Every row and column has weight three and the Levi graph is connected.

An exact integer particular solution is

```text
x0 = (0,1,0,0,1,1,0,0,-1,1,0,1).
```

An integer kernel basis is

```text
k1 = (-1, 2,-1,-1, 2, 2,-1,-1,-4, 2,-1, 2)
k2 = ( 1,-1, 0, 1,-1,-1, 1, 0, 2,-2, 0, 0).
```

Exact checks give

```text
A x0 = 1
A k1 = A k2 = 0.
```

A `10 x 10` minor on rows

```text
0,1,2,3,4,5,6,7,8,9
```

and columns

```text
0,1,2,3,4,5,6,7,8,10
```

has determinant `4`, so `rank_Q(A) >= 10`.  Since the two displayed kernel vectors are independent, `rank_Q(A) <= 10`; therefore

```text
rank_Q(A)=10,
nullity_Q(A)=2.
```

The gcd of all `2 x 2` minors of the `12 x 2` matrix `[k1 k2]` is `1`, so this kernel lattice is saturated. Hence **every integer solution** is exactly

```math
x=x_0+a k_1+b k_2,
\qquad a,b\in\mathbb Z.
```

---

## 3. Short symbolic Boolean-UNSAT certificate

Selected coordinates of the integer parameterization are

```text
x2  = -a
x11 = 1 + 2a
x0  = -a + b
x9  = 1 + 2a - 2b
x8  = -1 - 4a + 2b.
```

If all coordinates were Boolean, `x2 in {0,1}` gives

```text
a in {0,-1}.
```

But `a=-1` makes `x11=-1`, so necessarily

```text
a=0.
```

Then `x0=b in {0,1}`.  If `b=1`, `x9=-1`; hence

```text
b=0.
```

But then

```text
x8=-1,
```

contradiction. Therefore

```text
Exact-One(A)=UNSAT.
```

This is an algebraic certificate, not an exhaustive Boolean search.

---

## 4. Nevertheless the full pair-projection 2-CSP is SAT

Consider the Boolean vector

```text
s = (0,0,0,0,0,0,0,0,1,1,0,1).
```

For every coordinate `i`, the state `s_i` extends to some integer solution of `Ax=1`; and for every pair `i<j`, the state `(s_i,s_j)` extends to some integer solution of `Ax=1`.

The companion exact checker verifies these claims directly from

```math
x=x_0+a k_1+b k_2
```

using exact one- and two-equation Diophantine membership tests.

Consequently `s` satisfies every unit and binary clause of the induced integer-lattice projection formula `Phi_A`, even though `s` itself is not an Exact-One witness.

Thus pairwise integer extendability is not globally amalgamating already on this small connected cubic source.

The source `A` is not linear, so one more step is required to bind the falsifier to the frozen linear-cubic carrier.

---

## 5. Exact EQ3 linearization

Apply the frozen exact regularizer from

`R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`.

For every old variable `v`, create local variables `(v,0),...,(v,9)`.  The three old occurrences are attached to terminals `(v,0),(v,1),(v,2)`, and add the nine local rows

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6).
```

The result `L` is `120 x 120`, connected, square, cubic, and linear.

The local Boolean gadget has exactly three models:

```text
0000001110
0001110000
1110000001.
```

In every model the four terminal coordinates `{0,1,2,9}` are equal.  Both terminal values `0` and `1` occur. Therefore the regularizer preserves Exact-One satisfiability exactly:

```text
SAT(L) iff SAT(A).
```

Since `A` is UNSAT, so is `L`.

---

## 6. Integer affine parameterization of L

For each gadget define

```text
T_v = coordinates {0,1,2,9} = q_v
R_v = coordinates {6,7,8}   = r_v
S_v = coordinates {3,4,5}   = 1-r_v-q_v.
```

The retained source rows impose exactly

```math
Aq=\mathbf1.
```

Thus an integer particular solution is obtained from `q=x0` and all `r_v=0`.

For the homogeneous system write

```text
u = a k1 + b k2,
w_v = free integer gauge variables.
```

Then

```text
T_v = u_v
R_v = w_v
S_v = -u_v-w_v.
```

This gives 14 independent kernel directions.  Exact reduction modulo 3 gives

```text
rank_F3(L)=106,
```

and therefore

```text
rank_Q(L)=106,
nullity_Q(L)=14.
```

So the displayed 14 directions span the full rational kernel.

---

## 7. RKPR passes

Using the exact 14-dimensional kernel representation, the companion checker verifies

```text
zero kernel-coordinate rows = 0
proportional kernel-row pairs with ratio +1    = 288
proportional kernel-row pairs with ratio -1/2  = 144
all other proportional ratios                  = 0.
```

Thus RKPR sees only equality classes and legal `-1/2` pin relations. There is no illegal-ratio UNSAT certificate and no zero-row UNSAT terminal.

Because the pair-projection formula below is satisfiable, its satisfying assignment simultaneously respects every Boolean consequence of these legal pair relations.

---

## 8. The complete 120-coordinate pair projection is still SAT

Define a 10-bit block by the corresponding entry of the 12-bit vector `s` above:

```text
if s_v=0:  block(v) = 0001111110
if s_v=1:  block(v) = 1111111111.
```

Concatenate the twelve blocks to obtain a Boolean vector `S in {0,1}^120`.

The companion checker verifies, with exact integer arithmetic, that:

```text
for every coordinate i:
    S_i extends to an integer solution of Lz=1

for every pair i<j:
    (S_i,S_j) extends to an integer solution of Lz=1.
```

The verification uses the explicit 14-parameter integer family above. For a one-coordinate query it checks a gcd divisibility condition. For a two-coordinate query it checks exact membership in the rank-0, rank-1, or rank-2 integer image of the corresponding `2 x 14` parameter matrix using gcds of minors.

Therefore `S` is a satisfying assignment of the **full** induced pair-projection 2-CSP `Phi_L`.

Yet `S` is not an Exact-One witness, and no Exact-One witness exists because `SAT(L) iff SAT(A)=false`.

Hence

```math
\boxed{
\Phi_L\text{ SAT}
\quad\not\Rightarrow\quad
L\text{ Exact-One SAT}.
}
```

---

## 9. Consequence for the universal algorithm search

The following route is now forbidden:

```text
SNF/HNF integer membership
 -> RKPR equality/pin propagation
 -> exhaustive unary/pair integer projections
 -> solve induced 2-SAT
 -> assume global Boolean witness exists.
```

The obstruction is exact **higher-order amalgamation**: every selected one- and two-coordinate state can be extended separately in the integer affine lattice, while the whole Boolean vector cannot be extended simultaneously.

This points to the next honest question:

```text
R5_E9_INTEGER_LATTICE_BOUNDED_ARITY_AMALGAMATION_GATE_V1
```

Does some fixed projection arity `k` suffice on the linear-cubic source carrier, or can the minimum required arity grow with the instance?

A fixed `k` would still allow polynomially many `O(n^k)` integer-lattice projection queries, but **pairwise (`k=2`) is now rigorously insufficient**.

No claim is made that any fixed larger `k` is sufficient.

---

## 10. Firewall

```text
PAIR-PROJECTION 2SAT COMPLETENESS ON LINEAR CUBIC
= FALSIFIED

EXPLICIT CONNECTED SQUARE LINEAR-CUBIC FALSIFIER
= 120 x 120

INTEGER LATTICE MEMBERSHIP
= PASSES

RKPR
= PASSES (legal equality / -1/2 only)

FULL PAIR-PROJECTION BOOLEAN 2-CSP
= SAT

EXACT-ONE
= UNSAT

FIXED-k PROJECTION COMPLETENESS FOR k>=3
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```