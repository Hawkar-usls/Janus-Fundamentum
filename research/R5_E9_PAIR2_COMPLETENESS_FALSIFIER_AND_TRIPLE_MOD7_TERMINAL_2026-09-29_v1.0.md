# R5 E9 — Pair2 completeness falsifier and triple-mod7 terminal

Date: 2026-09-29
Status: PROVED LINEAR-CUBIC FALSIFIER + STRICT POLYNOMIAL TRIPLE TERMINAL
Global status: `P_VS_NP = OPEN`; `E8_D1 = EMPTY`.

## 1. Main result

The polynomial integer-lattice pair-projection 2-SAT layer is **not complete**, even on the exact connected square linear-cubic Positive-1-in-3 carrier.

There is an explicit connected square linear-cubic UNSAT source `L` with 240 variables/rows such that

```text
1 in L Z^240                         = true
RKPR                                 = equality-only
full unary/pair integer projection   = 2-SAT SAT
Exact-One(L)                         = UNSAT
```

The first obstruction appears on a three-coordinate Boolean projection.  On a 24-variable cubic seed `A`, every integer solution satisfies

```math
x_0+x_3+2x_{22}+1 \equiv 0 \pmod 7,
```

but for Boolean values the left side is one of `1,2,3,4,5`.  Hence

```math
\Pi_{\{0,3,22\}}(\{x\in\mathbb Z^{24}:Ax=\mathbf1\})
\cap\{0,1\}^3
=\varnothing.
```

The frozen EQ3 regularizer transfers this empty triple relation to occurrence terminals of the 240-variable linearized source.

Therefore

```text
POST-SNF + RKPR + FULL PAIR2 CONSISTENCY => SAT
```

is false.

---

## 2. Cubic seed A

Let

```text
A = I + P + Q
```

with zero-based permutations

```text
P = [5,18,17,19,16,3,21,10,9,6,23,15,8,14,20,2,1,7,0,13,11,22,12,4]
Q = [16,6,19,10,23,4,2,13,7,17,9,21,22,11,3,12,15,20,5,0,1,8,14,18].
```

`Q` differs from the earlier pair-projection strict control only by swapping the images at source rows `10` and `20`.

Exact arithmetic gives

```text
shape(A)      = 24 x 24
row degree    = 3
column degree = 3
rank_Q(A)     = 21
nullity_Q(A)  = 3
```

The nonzero Smith invariant factors are

```text
1 repeated 20 times, then 3.
```

Therefore the integer affine system is nonempty.

One exact integer solution is

```text
x* =
(0,0,0,-1,1,1,1,0,1,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0),
```

and direct multiplication gives `A x* = 1`.

---

## 3. Complete integer-affine parameterization

A Smith decomposition gives the full integer solution lattice

```math
x=x^*+K(a,b,c)^T,
\qquad a,b,c\in\mathbb Z,
```

where the rows of the integer kernel basis `K` are

```text
 0: ( 4,-2,-1)
 1: ( 2,-1, 0)
 2: ( 1, 0, 0)
 3: ( 3, 0, 1)
 4: ( 0,-1,-1)
 5: (-3, 1, 0)
 6: (-1, 0,-1)
 7: ( 1, 0, 0)
 8: ( 0,-1,-1)
 9: (-1, 1, 1)
10: ( 0,-1,-1)
11: ( 1, 0, 0)
12: ( 0, 0, 1)
13: (-1, 1, 1)
14: ( 0,-1,-1)
15: (-1, 0,-1)
16: (-1, 1, 1)
17: ( 2,-1, 0)
18: (-1, 1, 1)
19: (-3, 1, 0)
20: (-3, 1, 0)
21: ( 0, 0, 1)
22: ( 0, 1, 0)
23: ( 1, 0, 0).
```

Because this basis comes from the unimodular Smith transformation, it is the **full integer kernel lattice**, not merely a rational sublattice.

---

## 4. RKPR remains equality-only

The rational kernel is the span of the same three columns.  Its projective coordinate classes are

```text
{1,17}
{2,7,11,23}
{4,8,10,14}
{5,19,20}
{6,15}
{9,13,16,18}
{12,21}
```

plus singletons `{0}`, `{3}`, `{22}`.

Every nontrivial class is literal ratio `+1`.  There are

```text
zero kernel rows = 0
-2 ratios        = 0
-1/2 ratios      = 0
illegal ratios   = 0.
```

Thus exhaustive RKPR performs equality merges only and does not reject the source.

---

## 5. Full pair projection is satisfiable

For every coordinate `i` and Boolean value `u`, and every pair `i,j` and Boolean state `(u,v)`, define integer extendability exactly as in

`R5_E9_INTEGER_LATTICE_PAIR_PROJECTION_2SAT_TERMINAL_2026-09-29_v1.0.md`.

Using the complete integer basis above, every query reduces to one or two integer linear equations in `(a,b,c)` and is decided exactly by Smith/determinantal-divisor arithmetic.

The full induced Boolean 2-CSP over all 24 coordinates is satisfiable.  One satisfying pair-consistency assignment is

```text
(1,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1,1,0,0).
```

It is **not** an Exact-One witness; the row sums under this Boolean vector include both `0` and `2`.

Thus pairwise integer extendability has a globally consistent Boolean selection while no true Exact-One witness exists.

---

## 6. Exact three-coordinate obstruction

From the affine parameterization,

```math
x_0  = 4a-2b-c,
```

```math
x_3  = -1+3a+c,
```

and

```math
x_{22}=b.
```

Therefore every integer solution satisfies the exact identity

```math
x_0+x_3+2x_{22}+1=7a.
```

If all three coordinates were Boolean, then

```math
1\le x_0+x_3+2x_{22}+1\le5,
```

which cannot be a multiple of seven. Hence

```math
\boxed{
R_{0,3,22}^{(3)}
=
\varnothing
}
```

for the Boolean triple projection of the integer affine lattice.

This alone is a short exact UNSAT certificate for the cubic seed.  No exhaustive Boolean enumeration is needed.

---

## 7. Polynomial triple-empty terminal

For every triple `i<j<k`, test each of the eight Boolean states for integer extendability of

```math
Ax=\mathbf1,
\quad
x_i=u,
\quad
x_j=v,
\quad
x_k=w.
```

Each state is an integer linear-system feasibility query and is decidable in polynomial bit complexity by Smith/Hermite normal form.

There are

```math
8\binom n3=O(n^3)
```

queries.

Therefore the following router is polynomial and sound:

```text
INTEGER_LATTICE_EMPTY_TRIPLE_TERMINAL(A):
    for every i<j<k:
        compute the eight Boolean integer-extendable states
        if none exists:
            return UNSAT + triple lattice certificate
    return UNRESOLVED
```

The seed above is rejected by the triple `(0,3,22)` with the mod-7 certificate.

This terminal is strictly stronger than global SNF + RKPR + satisfiable full pair2 on this control.

---

## 8. Linearization by the frozen EQ3 regularizer

Apply

`R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`

to the 24-variable seed.  The output `L` has

```text
240 variables
240 clauses
connected = true
linear    = true
cubic     = true
SAT(L) iff SAT(A)
```

so `L` is UNSAT.

For each source variable `v`, the gadget integer-affine coordinates are

```text
T_v = q_v                      local {0,1,2,9}
R_v = r_v                      local {6,7,8}
S_v = 1-q_v-r_v                local {3,4,5}
```

where `q` is an integer source solution and every `r_v` is an independent integer.

Consequently the full integer kernel lattice of `L` is generated by:

- the three source integer-kernel directions lifted through every gadget;
- twenty-four independent private `r_v` directions.

Hence

```text
integer nullity = rational nullity = 27.
```

An exact rank-213 minor modulo 5 gives

```math
\operatorname{rank}_{\mathbb Q}(L)=213,
\qquad
\nu_{\mathbb Q}(L)=27.
```

The same private-coordinate argument as in the previous EQ3-linearized control shows that RKPR is equality-only.

---

## 9. Full 240-variable pair2 remains satisfiable

The companion checker constructs the **complete** 240-variable integer affine basis and evaluates every unary and pair Boolean projection, not merely terminal-terminal projections.

The resulting 2-SAT implication graph has no variable whose two literals lie in the same strongly connected component.  A satisfying assignment is reconstructed and rechecked directly against every computed unary/pair relation.

Therefore

```text
FULL_INTEGER_PAIR2(L) = SAT.
```

This is the critical point: the linearized counterexample is not obtained by checking only the terminal subformula.

---

## 10. Triple obstruction transfers to the linear carrier

All three occurrence terminals of source variable `v` equal `q_v` in every integer solution of the regularized system.  Choose local terminal `0` as representative, giving flattened coordinates

```text
source 0  -> output 0
source 3  -> output 30
source 22 -> output 220.
```

Hence every integer solution of `Lz=1` satisfies

```math
z_0+z_{30}+2z_{220}+1\equiv0\pmod7.
```

No Boolean state on `(0,30,220)` can satisfy it. Therefore the 240-variable linear-cubic source is rejected by the same empty-triple terminal.

---

## 11. Consequence for the universal search

Closed / falsified:

```text
SNF + RKPR => SAT
SNF + RKPR + FULL PAIR2 CONSISTENCY => SAT
```

both fail inside the exact linear-cubic NP-complete carrier.

The next live gate is

```text
R5_E9_POST_SNF_RKPR_PAIR2_TRIPLE_EMPTY_LINEAR_CUBIC_FALSIFIER_GATE_V1
```

Question:

```text
Does there exist a connected square linear-cubic UNSAT source that
passes integer-lattice membership,
passes RKPR,
has satisfiable full pair2 projection,
and has NO empty Boolean triple projection?
```

A negative answer would still require a proof that checking all empty triples is complete.  No such proof is claimed.

---

## 12. Firewall

```text
PAIR2 COMPLETENESS
= FALSIFIED

EXPLICIT LINEAR-CUBIC POST-PAIR2 UNSAT SOURCE
= PROVED

EMPTY INTEGER-LATTICE TRIPLE TERMINAL
= SOUND / POLYNOMIAL / STRICTLY STRONGER ON THE CONTROL

TRIPLE-EMPTY COMPLETENESS
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
