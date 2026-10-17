# R5 E9 — EQ3-linearized post-SNF/RKPR strict pair-projection control

Date: 2026-09-29
Status: PROVED LINEAR-CUBIC FALSIFIER + STRICT POLYNOMIAL TERMINAL CONTROL
Global status: `P_VS_NP = OPEN`; `E8_D1 = EMPTY`.

## 1. Result

There exists an explicit connected square **linear cubic** Positive-1-in-3 source `L` such that

```text
|V(L)| = |C(L)| = 240
Exact-One(L) = UNSAT
1 in L Z^240 = true
RKPR(L) has equality classes only
```

but the integer-lattice pair-projection 2-CSP is UNSAT.

Therefore the conjectural shortcut

```text
linear cubic + integer-lattice membership + exhaustive RKPR => SAT
```

is false.

At the same time this gives a strict source-specific success case for

```text
INTEGER_LATTICE_PAIR_PROJECTION_2SAT.
```

It does not prove that pair projection is complete on the linear cubic carrier.

---

## 2. Cubic source before linearization

Use the 24-variable connected cubic control from

`R5_E9_INTEGER_LATTICE_PAIR_PROJECTION_2SAT_TERMINAL_2026-09-29_v1.0.md`:

```text
A = I + P + Q

P = [5,18,17,19,16,3,21,10,9,6,23,15,8,14,20,2,1,7,0,13,11,22,12,4]
Q = [16,6,19,10,23,4,2,13,7,17,1,21,22,11,3,12,15,20,5,0,9,8,14,18]
```

Exact facts already checked:

```text
rank_Q(A) = 21
nullity_Q(A) = 3
1 in A Z^24 = true
Exact-One(A) = UNSAT
zero rational kernel rows = 0
RKPR ratios = equality only
```

A concrete integer solution is

```text
x0 = (0,0,0,-1,1,1,1,0,1,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0),
```

for which `A x0 = 1`.

The decisive integer Boolean pair projections are

```text
R_A(5,12) = {(1,0)}
R_A(3,5)  = {(1,0)}.
```

Hence every Boolean witness would require simultaneously `x5=1` and `x5=0`.

This source is cubic but not linear.

---

## 3. Apply the frozen EQ3 regularizer

Apply the exact regularizer from

`R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`.

For every source variable `v`, create ten local variables

```text
(v,0),...,(v,9)
```

where `(v,0),(v,1),(v,2)` are the three occurrence terminals and the nine gadget rows are

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

Keep each old source clause after replacing its three variable occurrences by their three distinct terminal copies.

Call the resulting `240 x 240` incidence matrix `L`.

The frozen regularizer theorem gives immediately:

```text
square / cubic / linear = true
connected               = true
SAT(L) iff SAT(A)
```

and therefore `L` is Exact-One UNSAT.

---

## 4. Exact rational parameterization of the regularized system

Inside one gadget, exact row reduction gives

```text
T_v := local coordinates {0,1,2,9} = q_v,
S_v := local coordinates {3,4,5}   = 1-r_v-q_v,
R_v := local coordinates {6,7,8}   = r_v.
```

The retained old source rows impose exactly

```math
Aq=\mathbf1.
```

Therefore the full affine rational solution space of `Lz=1` is parameterized by

```text
q in {source affine solutions Aq=1}
r_v arbitrary independently for every v.
```

For the homogeneous kernel write `u` for a source kernel vector and `w_v` for the independent gadget gauge coordinate. Then

```text
T_v = u_v
R_v = w_v
S_v = -u_v-w_v.
```

Hence

```math
\nu_Q(L)=\nu_Q(A)+24=27,
\qquad
\operatorname{rank}_Q(L)=240-27=213.
```

---

## 5. Integer-lattice membership survives

If `q` is any integer solution of `Aq=1`, choose for every gadget

```text
r_v=0.
```

Then

```text
T_v=q_v,
R_v=0,
S_v=1-q_v
```

are all integers and satisfy every gadget and retained source row.

In particular the explicit `x0` above lifts to an integer solution of

```math
Lz=\mathbf1.
```

Thus

```text
1 in L Z^240 = true.
```

So the global Smith/Hermite terminal passes.

---

## 6. RKPR remains equality-only

The homogeneous parameterization also gives the complete projective-coordinate structure.

For every source variable `v`:

```text
T_v functional = u_v
R_v functional = w_v
S_v functional = -u_v-w_v.
```

The `w_v` are independent private gauge coordinates.

Consequences:

1. `R_v` cannot be proportional to any coordinate outside its own `R_v` triple.
2. `S_v` cannot be proportional to `R_v`, to any `T_w`, or to any coordinate in another gadget, because its coefficient on the private `w_v` is nonzero and it also contains `u_v`.
3. `T_v` and `T_w` are proportional exactly when the corresponding source kernel coordinate rows `u_v,u_w` are proportional.
4. The source control has no zero rows, no `-2/-1/2` projective ratios, and no illegal ratios; its only nontrivial projective relations are equality.

Therefore `L` has no zero kernel rows and no RKPR pin/illegal-ratio rejection. Its only projective classes are equality classes.

More explicitly, from the source classes

```text
{9,16,18},
{1,17}, {2,11}, {6,15}, {8,14}, {12,21},
plus 11 source singletons,
```

we obtain:

```text
T-classes: one class of size 12,
           five classes of size 8,
           eleven classes of size 4;
R-classes: 24 classes of size 3;
S-classes: 24 classes of size 3.
```

Thus exhaustive RKPR performs equality merges only and does not decide UNSAT.

---

## 7. Pair-projection contradiction transfers exactly

Choose one terminal representative, say local terminal `0`, for each source variable.

Every integer solution of `Lz=1` has equal gadget terminals and therefore collapses to an integer source solution `q` of `Aq=1`.

Conversely every integer source solution extends to an integer solution of `Lz=1` by choosing all `r_v=0`.

Hence for any source variables `i,j`, the Boolean integer pair projection on their terminal representatives is exactly preserved:

```math
R_L((i,0),(j,0))=R_A(i,j).
```

In particular, using zero-based flattened coordinates `10v`:

```text
R_L(50,120) = {(1,0)}
R_L(30,50)  = {(1,0)}.
```

The first forces terminal/source value `x5=1`; the second forces it to `0`.

Therefore the induced pair-projection 2-CSP is UNSAT.

This proves that the pair-projection terminal is strictly stronger than

```text
global integer-lattice membership + exhaustive RKPR
```

even **inside the exact connected square linear-cubic NP-complete carrier**.

---

## 8. Consequence

The previous live conjecture

```text
R5_E9_POST_SNF_RKPR_LINEAR_CUBIC_SUFFICIENCY_FALSIFIER_GATE_V1
```

is now CLOSED / FALSIFIED.

The surviving positive question is stronger:

```text
R5_E9_POST_SNF_RKPR_PAIR2_LINEAR_CUBIC_COMPLETENESS_FALSIFIER_GATE_V1
```

Does there exist a connected square linear-cubic UNSAT source whose integer affine lattice has a satisfiable induced Boolean pair-projection 2-CSP after all equality/pin propagation?

A proof that no such source exists would give a polynomial solver for the NP-complete linear-cubic carrier and therefore imply `P=NP`.  No such proof is claimed here.

---

## 9. Firewall

```text
LINEAR-CUBIC SNF+RKPR SUFFICIENCY
= FALSIFIED

INTEGER-LATTICE PAIR-PROJECTION 2SAT
= STRICTLY STRONGER ON AN EXPLICIT LINEAR-CUBIC SOURCE

PAIR-PROJECTION COMPLETENESS
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
