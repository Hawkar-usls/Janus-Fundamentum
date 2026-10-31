# R5 E9 — Triple-empty integer-lattice completeness falsifier via exact two-edge lift

Date: 2026-09-29

Status: `JANUS_EXACT_LINEAR_CUBIC_FALSIFIER__TRIPLE_EMPTY_COMPLETENESS_FALSE__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS NOTE FALSIFIES THE CLAIM THAT
SNF + RKPR + SAT PAIR2 + NO EMPTY BOOLEAN TRIPLE PROJECTION
IS SUFFICIENT FOR EXACT-ONE SAT.

IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_PAIR2_COMPLETENESS_FALSIFIER_AND_TRIPLE_MOD7_TERMINAL_2026-09-29_v1.0.md`
- `research/R5_E9_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER_2026-09-28_v1.0.md`
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`

Checker:
- `experiments/r5_e9_triple_empty_completeness_two_edge_lift_falsifier.py`

## 1. Base cubic source

Use the 24-variable cubic source from the pair2/triple-mod7 control:

```text
A = I + P + Q

P = [5,18,17,19,16,3,21,10,9,6,23,15,8,14,20,2,1,7,0,13,11,22,12,4]
Q = [16,6,19,10,23,4,2,13,7,17,9,21,22,11,3,12,15,20,5,0,1,8,14,18]
```

It has `rank_Q(A)=21`, integer nullity three, and an explicit integer solution

```text
x*=(0,0,0,-1,1,1,1,0,1,0,1,0,0,0,1,1,0,0,0,1,1,0,0,0).
```

A short mod-7 certificate proves Boolean UNSAT. With

```text
lambda=(6,0,2,3,6,1,0,3,6,0,1,0,1,2,4,5,2,5,0,2,5,0,1,0)
```

we have, modulo seven,

```text
lambda^T A = e_0 + e_3 + 2 e_22,
lambda^T 1 = 6.
```

Thus every integer solution obeys

```math
x_0+x_3+2x_{22}+1\equiv0\pmod7.
```

No Boolean triple can satisfy this identity, so the base source is UNSAT.

## 2. Two-edge lift

Cross the two nonincident identity incidences

```text
F={(12,12),(21,21)}.
```

Let `E` mark these incidences and define

```math
\widehat A=
\begin{pmatrix}
A-E&E\\
E&A-E
\end{pmatrix}.
```

The lift is square cubic on 48 rows and columns.

### Exact UNSAT preservation

An integer left-kernel vector of the base is

```text
y=(0,0,-1,1,0,0,0,-1,0,0,0,-1,-1,1,-1,1,0,1,0,0,0,1,0,0),
```

with

```text
y_12=-1,
y_21=+1.
```

For a hypothetical Boolean lift model `(u,v)`, put `h=u-v`. The standard two-edge-lift identity gives

```math
A h=2(h_{12}e_{12}+h_{21}e_{21}).
```

Summing coordinates through the cubic column sums gives

```math
h_{12}+h_{21}=0.
```

Left-multiplying by `y^T` gives

```math
-h_{12}+h_{21}=0.
```

Therefore both distinguished values are zero. Hence `E h=0`, and the upper/lower lift equations reduce to

```math
Au=Av=\mathbf1.
```

This contradicts base UNSAT. Conversely every base Boolean model would lift diagonally, so here

```text
SAT(Ahat) iff SAT(A) = false.
```

## 3. Explicit six-dimensional integer kernel sublattice

A full integer kernel basis of the base is given row-wise by

```text
( 4,-2,-1)
( 2,-1, 0)
( 1, 0, 0)
( 3, 0, 1)
( 0,-1,-1)
(-3, 1, 0)
(-1, 0,-1)
( 1, 0, 0)
( 0,-1,-1)
(-1, 1, 1)
( 0,-1,-1)
( 1, 0, 0)
( 0, 0, 1)
(-1, 1, 1)
( 0,-1,-1)
(-1, 0,-1)
(-1, 1, 1)
( 2,-1, 0)
(-1, 1, 1)
(-3, 1, 0)
(-3, 1, 0)
( 0, 0, 1)
( 0, 1, 0)
( 1, 0, 0).
```

For the signed block `S=A-2E`, an integer kernel basis is

```text
z1=(-7,-2,-2,-1,-3,4,-1,-4,3,1,-1,-2,3,5,-3,-1,3,0,3,2,4,3,0,0)
z2=(-2,-1,0,0,-1,1,0,0,-1,1,-1,0,0,1,-1,0,1,-1,1,1,1,0,1,0)
z3=(4,2,1,3,0,-3,-1,1,0,-1,0,1,0,-1,0,-1,-1,2,-1,-3,-3,0,0,1).
```

Therefore the 48-variable lift has six explicit independent integer kernel directions:

```text
(k1,k1), (k2,k2), (k3,k3),
(z1,-z1), (z2,-z2), (z3,-z3).
```

The diagonal vector `(x*,x*)` is an integer particular solution.

Exact rational elimination gives

```text
rank_Q(Ahat)=42,
nullity_Q(Ahat)=6,
```

so these six directions span the full rational kernel.

## 4. RKPR passes

Evaluate the 48 coordinate functionals on the six displayed kernel directions. Exact proportionality testing gives

```text
zero coordinate rows = 0
all proportional nonidentical coordinate rows have ratio +1
all other projective ratios = absent.
```

Thus RKPR has equality merges only; there is no zero-row, pin, or illegal-ratio UNSAT terminal.

## 5. Full pair2 remains SAT

Let

```text
y48=0^48.
```

For every coordinate `i`, and every pair `i<j`, the checker finds an integer vector `c in Z^6` such that

```math
(x*,x*)+Kc
```

has the requested coordinate(s) equal to zero. Each candidate is verified directly against

```math
\widehat A x=\mathbf1.
```

Hence every singleton state `0` and every pair state `(0,0)` is integer-extendable. Therefore the complete pair-projection 2-CSP is satisfiable, witnessed by `0^48`.

## 6. No empty Boolean triple exists

For each of the

```math
\binom{48}{3}=17,296
```

coordinate triples, the checker tests all eight Boolean states for membership in the integer image of the explicit six-direction kernel sublattice.

Integer membership in a `r x 6` system with `r<=3` is checked exactly by rank and determinantal-divisor/gcd arithmetic; no floating point or optimization oracle is used.

Result:

```text
empty triple projections = 0
minimum number of witnessed Boolean states on a triple = 1
```

A complete census for this explicit sublattice is

```text
8 states : 8902 triples
4 states : 7710 triples
3 states :  260 triples
2 states :  350 triples
1 state  :   74 triples
0 states :    0 triples
```

Because every displayed sublattice point is an actual integer solution of `Ahat x=1`, these witnesses are sufficient to prove that the **full** affine integer lattice also has no empty Boolean triple projection.

Thus

```text
SNF membership = PASS
RKPR           = PASS
full pair2     = SAT
empty-triple terminal = PASS / no rejection
Exact-One      = UNSAT.
```

This falsifies triple-empty completeness already on a 48-variable cubic source.

## 7. Transfer to the exact linear-cubic carrier

Apply the frozen EQ3 regularizer to `Ahat`. The output `L` has

```text
480 rows,
480 columns,
connected = true,
linear = true,
cubic = true,
SAT(L) iff SAT(Ahat)=false.
```

Its integer affine coordinates in gadget `v` are

```text
T_v=q_v,
R_v=r_v,
S_v=1-q_v-r_v,
```

with `q` an integer solution of the 48-variable source and every `r_v` free.

### Projection-nonemptiness transfer lemma

For any fixed `k`, if every source coordinate set of size at most `k` has at least one Boolean state extendable to an integer source solution, then every regularized coordinate set of size at most `k` has at least one Boolean state extendable to an integer regularized solution.

Proof: take the at-most-`k` source gadgets touched by the selected regularized coordinates. Choose any Boolean source state on those gadgets that extends to an integer source solution `q`. Set the selected regularized coordinates according to the canonical local Boolean block

```text
T_v=q_v,
R_v=0,
S_v=1-q_v.
```

Then choose `r_v=0`. The resulting selected values are Boolean and extend to an integer regularized solution. QED.

Applying this lemma with `k=3` proves that `L` has no empty Boolean triple projection.

The same canonical-block argument transfers the source pair2 witness `0^48` to a satisfying assignment of the full regularized pair2 CSP.

The homogeneous regularizer form

```text
T_v=u_v,
R_v=w_v,
S_v=-u_v-w_v
```

also shows that, because the source has only equality projective classes, the regularized kernel introduces only equality classes: the private `w_v` prevent new cross-gadget proportionalities. Hence exhaustive RKPR does not reject `L`.

Therefore there exists an explicit connected square linear-cubic UNSAT source on 480 variables that passes

```text
integer-lattice membership,
RKPR,
full pair2 consistency,
no-empty-triple terminal.
```

## 8. Consequence

The live gate

```text
R5_E9_POST_SNF_RKPR_PAIR2_TRIPLE_EMPTY_LINEAR_CUBIC_FALSIFIER_GATE_V1
```

is CLOSED / FALSIFIED.

Naively increasing the fixed local projection arity is not an adequate universal strategy. The raw `EXACT_ONE_3` relation has projection-only polymorphisms and is outside bounded width; independently, the present theorem shows that even globally computed integer-lattice information through arity three can remain locally nonempty on an UNSAT source.

The surviving algorithmic route must be genuinely global. The strongest exact current formulation is the integer-lattice L1 optimization

```math
\min_{Az=1,\ z\in\mathbb Z^n}\sum_i|2z_i-1|,
```

where optimum `n` is equivalent to Exact-One SAT and UNSAT has an exact gap of at least two. A universal polynomial route therefore needs a nonlocal augmentation/contraction mechanism (for example the frozen Graver-best-step gate), not another fixed small projection test.

## 9. Updated frontier

Freeze

```text
R5_E9_LINEAR_CUBIC_GRAVER_BEST_STEP_POLYTIME_GATE_V1
```

as a primary global candidate, together with representation-changing root-aware decomposition as reserve.

Required PASS:

```text
construct a deterministic polynomial improving/global-optimality step
for F(z)=sum_i |2z_i-1| over {z in Z^n:Az=1},
for every connected square linear-cubic source,
with polynomial total bit complexity and witness reconstruction.
```

Forbidden pseudo-progress:

- fixed local-consistency width;
- pair2 completeness;
- empty-triple completeness;
- merely increasing projection arity by another fixed constant;
- enumerating an exponential Graver basis;
- assuming a negative circuit / Graver-best direction oracle for free.

## 10. Firewall

```text
TRIPLE-EMPTY COMPLETENESS
= FALSE

EXPLICIT CUBIC FALSIFIER
= 48 x 48

EXPLICIT LINEAR-CUBIC TRANSFER
= 480 x 480

SNF + RKPR + PAIR2 + NO EMPTY TRIPLE
= STILL INSUFFICIENT

GLOBAL L1 / GRAVER AUGMENTATION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```