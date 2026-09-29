# R5 E9 — Two-edge prime unique-model linear-nullity SAT tower

Date: 2026-09-29

Status: `JANUS_DERIVED_ARBITRARY_N_PRIME_UNIQUE_MODEL_HIGH_NULLITY_SAT_FAMILY__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_ONE_EDGE_TWIST_2LIFT_DISSOCIATED_NULLITY_AMPLIFIER_2026-09-27_v1.0.md`
- `research/R5_E9_TWO_EDGE_2LIFT_3CUT_IRREDUCIBLE_LINEAR_NULLITY_FAMILY_2026-09-28_v1.0.md`
- `research/R5_E9_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER_2026-09-28_v1.0.md`

Scientific ceiling:

```text
THIS NOTE CONSTRUCTS AN INFINITE SAT FAMILY THAT IS SIMULTANEOUSLY
CONNECTED, LINEAR-CUBIC, UNIQUE-MODEL, SIGNED-TRADE-FREE,
3-CUT-IRREDUCIBLE, UNBALANCED, AND OF LINEAR RATIONAL NULLITY.

IT DOES NOT PROVIDE THE MISSING POLYNOMIAL SIGN-CROSSING / SOURCE-TRADE
ALGORITHM.  THE FAMILY IS A HOSTILE CONTROL FOR SUCH AN ALGORITHM.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen unique-model seed

Use the frozen `18_3` incidence matrix `A_0` with rows

```text
(0,15,17)
(1,4,12)
(2,10,14)
(3,4,11)
(4,8,9)
(3,5,13)
(1,6,10)
(2,7,15)
(1,8,14)
(3,7,9)
(9,10,16)
(7,11,13)
(5,12,17)
(0,13,16)
(0,12,14)
(5,8,15)
(2,6,16)
(6,11,17).
```

The parent theorems already prove that `A_0` is connected, square,
linear-cubic, satisfiable, signed-trade-free, and has a unique Exact-One model

```text
x*=(1,1,1,0,0,1,0,0,0,1,0,1,0,0,0,0,0,0).
```

They also prove

```text
rank_Q(A_0)=16,
nu_Q(A_0)=2,
no nontrivial edge cut of size <=3,
unbalanced with a distinguished strong odd Levi cycle of length 18.
```

One integer right-kernel basis is

```text
k1=(0,0,-2,-2,3,3,1,2,-3,0,-1,-1,-3,-1,3,0,1,0),
k2=(-2,-2,0,3,-2,-5,0,-1,4,-2,2,-1,4,2,-2,1,0,1).
```

An integer left-kernel vector is

```text
ell=(1,2,2,-1,-1,-1,-1,-3,-1,2,-1,1,-1,0,-1,2,1,0).
```

## 2. Distinguished two-edge signing

Choose

```text
F_0={(row 0,column 15),(row 1,column 1)}.
```

Both are incidences of `A_0`; they are nonincident in the Levi graph. They also
avoid the distinguished strong odd cycle frozen in the two-edge-prime parent.

On the right-kernel basis, evaluation at the two distinguished columns is

```text
(ev_15(k1),ev_15(k2))=(0,1),
(ev_1 (k1),ev_1 (k2))=(0,-2).
```

Hence the two coordinate functionals have rank exactly one on `ker_Q(A_0)`.
Therefore

\[
W_0^0=\{w\in\ker_Q(A_0):w_{15}=w_1=0\}
\]

has dimension at least one.

On the left kernel,

```text
ell_0=1,
ell_1=2,
```

so the two distinguished rows are separated. The exact two-edge SAT-contraction
theorem from the parent therefore applies.

## 3. Two-edge signed-trade-free preservation lemma

Let `A` be signed-trade-free and choose two nonincident incidences
`(i1,j1),(i2,j2)`.  Suppose there exists `y in ker_Z(A^T)` such that the only
pair

\[
(d_1,d_2)\in\{-2,-1,0,1,2\}^2
\]

satisfying both

\[
d_1+d_2\equiv0\pmod3
\]

and

\[
y_{i_1}d_1+y_{i_2}d_2=0
\]

is `(0,0)`.

### Lemma PUM-1

Under these hypotheses the two-edge-twist 2-lift is signed-trade-free.

### Proof

Let `(p,q)` be a signed trade of the lift, with each coordinate in
`{-1,0,1}`. Put

\[
d_a=p_{j_a}-q_{j_a}\in\{-2,-1,0,1,2\}.
\]

The lifted equations give

\[
Ap=d_1e_{i_1}+d_2e_{i_2},
\qquad
Aq=-d_1e_{i_1}-d_2e_{i_2}.
\]

Every column of `A` has sum three. Summing `Ap` yields

\[
3\sum_jp_j=d_1+d_2,
\]

hence `d_1+d_2` is divisible by three. Left-multiplying by `y^T` gives

\[
y_{i_1}d_1+y_{i_2}d_2=0.
\]

By hypothesis `d_1=d_2=0`. Thus `Ap=Aq=0`; signed-trade-freeness of `A`
forces `p=q=0`. QED.

For the frozen pair, `y=ell` gives `(y_0,y_1)=(1,2)`.  If

\[
d_1+2d_2=0,
\]

with `|d_i|<=2`, the only nonzero candidates are `(d_1,d_2)=(-2,1)` and
`(2,-1)`, whose sums are `-1` and `1`, not divisible by three. Hence the
hypothesis holds exactly.

## 4. One recursive lift step

Let `E_t` mark the two distinguished incidences and form

\[
A_{t+1}=\begin{pmatrix}A_t-E_t&E_t\\E_t&A_t-E_t\end{pmatrix}.
\]

The standard symmetric/antisymmetric change of basis gives blocks

\[
A_t\oplus(A_t-2E_t).
\]

Let `W_t` be a tracked right-kernel subspace of dimension `d_t` on which the two
distinguished column evaluations have rank at most one. Define

\[
W_t^0=\{w\in W_t:w_{j_1}=w_{j_2}=0\}.
\]

Then

\[
\dim W_t^0\ge d_t-1.
\]

The lift contains the independent subspaces

\[
\{(w,w):w\in W_t\}
\]

and

\[
\{(u,-u):u\in W_t^0\}.
\]

Therefore

\[
\boxed{d_{t+1}\ge2d_t-1.}
\]

Choose the next distinguished pair to be the two upper-right crossed copies of
the old pair, exactly as in the already-proved UNSAT prime tower. On the
symmetric part their evaluations are the old dependent evaluations; on the
antisymmetric part from `W_t^0` both are zero. Hence the rank-at-most-one
condition is inherited.

The symmetric left-kernel vector `(ell_t,ell_t)` preserves the distinguished
row values `1,2`. Therefore both the exact SAT-contraction condition and the
signed-trade-free defect condition are inherited at every level.

## 5. Structural preservation

The two-edge-prime theorem proves that two nonincident crossed incidences on a
cubic base with no nontrivial `<=3` edge cuts have frustration index two, and
that the resulting 2-lift again has no nontrivial `<=3` edge cut.

Thus every `A_t` remains 3-cut-irreducible.

Because the distinguished pair avoids the frozen strong odd cycle, that cycle
lifts positively to two copies. Choose the upper copy recursively. Hence every
`A_t` remains unbalanced.

Graph covers preserve cubicity, bipartiteness, and the absence of Levi 4-cycles,
so the carrier remains square linear-cubic and connected.

## 6. SAT and unique-model preservation

Every base Exact-One witness lifts fiber-constantly, so SAT is preserved.

By Lemma PUM-1 every level is signed-trade-free. If a satisfiable incidence
matrix had two different Boolean Exact-One models, their difference would be a
nonzero vector in `{-1,0,1}^n` in the integer kernel, contradicting
signed-trade-freeness. Therefore every level has exactly one Exact-One model.

Independently, the parent exact two-edge contraction theorem says every lifted
model contracts to base models because the distinguished left-kernel vector
separates the two crossed rows; thus uniqueness is also witnessed directly by
the recursive contraction.

## 7. Linear nullity

At level zero

\[
d_0=\nu_Q(A_0)=2.
\]

The recurrence

\[
d_{t+1}\ge2d_t-1
\]

implies

\[
d_t\ge2^t+1.
\]

The order is

\[
n_t=18\cdot2^t.
\]

Consequently

\[
\boxed{
\nu_Q(A_t)\ge d_t\ge \frac{n_t}{18}+1.
}
\]

## 8. Main consequence

There is an explicit recursively constructible infinite family satisfying
simultaneously

```text
connected,
square linear-cubic,
SAT,
exactly one Exact-One model,
signed-trade-free,
unbalanced,
no nontrivial edge cut of size <=3,
rational nullity >= n/18 + 1.
```

Hence none of the following can be used as a universal reason why a
crossing-penalty/source-trade state is easy:

```text
large rational nullity => many Boolean witnesses;
large rational nullity => a small signed trade exists;
3-cut-prime + large nullity => model multiplicity;
prime high-nullity SAT => local Boolean repair choices.
```

This does not prove that every improving integer trade on this tower has large
crossing support. That stronger statement requires a separate theorem and is
not claimed here.

Likewise, the family is recursively a 2-lift family; a future exact cover
recognizer may contract it. It is a hostile semantic control, not a lower bound
against arbitrary representation-changing algorithms.

## 9. Updated crossing gate

Together with the complement-witness zero-crossing theorem, the universal
obligation is now sharper:

```text
R5_E9_GLOBAL_SIGN_CROSSING_SOURCE_TRADE_GATE_V2
```

A PASS cannot rely on low nullity, small separators, existence of small signed
trades, or multiplicity of Boolean witnesses. It must construct or certify the
relevant sign-crossing move by a genuinely global polynomial mechanism.

## 10. Ceiling

```text
TWO-EDGE DEFECT-SAFE SIGNED-TRADE-FREE PRESERVATION
= PROVED

TRACKED NULLITY RECURRENCE
= d' >= 2d-1

SAT
= PRESERVED

UNIQUE MODEL
= PRESERVED

3-CUT IRREDUCIBILITY
= PRESERVED BY PARENT TEL-2 THEOREM

PERSISTENT STRONG ODD CYCLE
= PRESERVED

NULLITY
>= n/18+1

GLOBAL SIGN-CROSSING SOURCE-TRADE ALGORITHM
= OPEN

UNIVERSAL POLYNOMIAL SAT DECIDER
= NOT PROVED

E8_D1
= EMPTY
P_VS_NP
= OPEN
```
