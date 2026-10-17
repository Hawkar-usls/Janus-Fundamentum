# R5 E9 — Integer-lattice pair-projection completeness falsifier on the linear-cubic carrier

Date: 2026-09-29

Status: `JANUS_EXACT_FINITE_FALSIFIER__PAIR2_COMPLETENESS_FALSE_ON_LINEAR_CUBIC_CARRIER__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE FALSIFIES COMPLETENESS OF THE INTEGER-LATTICE ONE/TWO-COORDINATE
PROJECTION 2-CSP, INCLUDING AFTER TRANSFER INTO THE CONNECTED SQUARE
LINEAR-CUBIC NP-COMPLETE CARRIER.

IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_INTEGER_LATTICE_PAIR_PROJECTION_2SAT_TERMINAL_2026-09-29_v1.0.md`
- `research/R5_E9_EQ3_LINEARIZED_POST_SNF_RKPR_PAIR_PROJECTION_STRICT_CONTROL_2026-09-29_v1.0.md`
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_pair2_completeness_linear_cubic_falsifier.py`

## 1. Nine-variable cubic source

Let

```text
A = I + P + Q

P = [7,6,4,2,0,1,8,5,3]
Q = [6,8,7,0,5,2,1,3,4]
```

with zero-based indices. Its row supports are

```text
(0,6,7)
(1,6,8)
(2,4,7)
(0,2,3)
(0,4,5)
(1,2,5)
(1,6,8)
(3,5,7)
(3,4,8)
```

Thus `A` is connected, square and cubic. It is intentionally not linear: rows 1 and 6 coincide. Exact rational rank is

```text
rank_Q(A)=7.
```

## 2. Complete integer affine solution lattice

Exact elimination gives every integer solution of `Ax=1` in the form

\[
\begin{aligned}
x_0&=s, & x_1&=2s-2r-1, & x_2&=1-s+r,\\
x_3&=-r,& x_4&=-r,&x_5&=1-s+r,\\
x_6&=1-2s,&x_7&=s,&x_8&=2r+1,
\end{aligned}
\]

for `s,r in Z`, and every integer pair `(s,r)` gives an integer solution.

For example `(s,r)=(-3,-2)` gives an explicit integer solution; the checker verifies the parameterization directly against `A`.

### Boolean UNSAT

If all coordinates were Boolean, `x_8=2r+1 in {0,1}` forces `r=0`. Then `x_7=s in {0,1}` together with `x_6=1-2s in {0,1}` forces `s=0`. But then

```text
x_1 = -1,
```

contradiction. Therefore

\[
\boxed{A\text{ is Exact-One UNSAT}.}
\]

This is an analytic proof; the checker also exhausts all `2^9` Boolean vectors.

## 3. Yet the full integer pair-projection 2-CSP is SAT

Let

```text
y = (0,1,0,0,0,0,1,0,1).
```

For every coordinate `i`, the Boolean value `y_i` extends to an integer solution of `Ax=1`. More strongly, for every pair `i<j`, the pair

```text
(x_i,x_j)=(y_i,y_j)
```

extends to an integer solution.

The companion checker proves this exactly by finding `(s,r)` in the finite certificate set

```text
{-1,0,1} x {-1,0,1}
```

for each of the 9 singleton pins and all 36 pair pins, then directly verifying `Ax=1` and the requested coordinates.

Hence `y` satisfies every one- and two-coordinate Boolean relation induced by the integer affine lattice even though no global Boolean Exact-One witness exists.

Therefore

\[
\boxed{\text{INTEGER-LATTICE PAIR-PROJECTION 2-CSP IS NOT COMPLETE}.}
\]

already on a connected square cubic source.

## 4. General EQ3 pair-projection transfer lemma

Apply the frozen 10-variable EQ3 regularizer independently to every source variable. In gadget `v`, every integer affine solution has the form

```text
T_v = q_v   on local coordinates {0,1,2,9},
R_v = r_v   on local coordinates {6,7,8},
S_v = 1-r_v-q_v on local coordinates {3,4,5},
```

where `q` is an integer solution of the source system and every `r_v` is an independent arbitrary integer.

Suppose `y in {0,1}^n` satisfies all one/two-coordinate integer projections of the source lattice. Define a Boolean vector `z` on the regularized variables by

```text
T_v = y_v,
R_v = 0,
S_v = 1-y_v.
```

### Lemma P2-EQ3

`z` satisfies every one/two-coordinate integer projection of the regularized affine lattice.

### Proof

Fix at most two regularized coordinates to their values in `z`.

- A pinned `T_v` requires `q_v=y_v`.
- A pinned `R_v` requires only `r_v=0`.
- A pinned `S_v` requires `r_v+q_v=y_v` and therefore can always be met by choosing `r_v=y_v-q_v`.
- If both an `R_v` and an `S_v` from the same gadget are pinned, then `r_v=0` and hence `q_v=y_v`; this contributes one source pin.

Thus any pair of regularized pins induces at most two source-coordinate requirements `q_i=y_i`, `q_j=y_j`. By the source pair-projection hypothesis these extend to an integer source solution `q`. The independent `r_v` are then chosen as above. This gives an integer regularized solution realizing the two requested Boolean values. QED.

## 5. Linear-cubic falsifier

Apply the frozen EQ3 regularizer to the nine-variable source above. The resulting matrix `L` has

```text
90 rows,
90 columns,
row degree = 3,
column degree = 3,
connected = true,
linear = true.
```

The regularizer theorem gives

```text
Exact-One(L) iff Exact-One(A).
```

Therefore `L` is UNSAT.

By Lemma P2-EQ3, the vector obtained from `y` via

```text
T_v=y_v, R_v=0, S_v=1-y_v
```

satisfies the complete integer-lattice one/two-coordinate projection 2-CSP of `L`.

Hence

\[
\boxed{\text{pair-projection completeness is false even on the exact connected square linear-cubic carrier}.}
\]

## 6. Consequence for the local-projection hierarchy

The previous gate

```text
R5_E9_POST_SNF_RKPR_PAIR2_LINEAR_CUBIC_COMPLETENESS_FALSIFIER_GATE_V1
```

is CLOSED / FALSIFIED.

Naively raising the projection arity from 2 to 3 is not a new universal solver route: every original source row itself has arity three, and the three-coordinate integer projection on a source row already contains the original `EXACT_ONE_3` Boolean relation. Thus generic triple-projection CSP reconstruction reintroduces the NP-hard source language rather than eliminating it.

Any next polynomial mechanism must therefore be genuinely global/representation-changing; it may not be described merely as fixed-arity integer-lattice projection.

## 7. Updated ceiling

```text
GLOBAL SNF/HNF INTEGER TERMINAL
= POLY / SOUND

ONE/TWO-COORDINATE INTEGER PROJECTION 2-SAT TERMINAL
= POLY / SOUND / STRICTLY STRONGER

PAIR2 COMPLETENESS ON CUBIC
= FALSE

PAIR2 COMPLETENESS ON CONNECTED SQUARE LINEAR-CUBIC
= FALSE

NAIVE ARITY-3 PROJECTION
= RETURNS ORIGINAL EXACT_ONE_3 HARD RELATION

NEXT REQUIRED MECHANISM
= GLOBAL REPRESENTATION-CHANGING CONTRACTION / DECOMPOSITION

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```