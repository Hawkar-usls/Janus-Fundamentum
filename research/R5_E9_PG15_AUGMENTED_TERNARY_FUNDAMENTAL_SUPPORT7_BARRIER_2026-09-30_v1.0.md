# R5 E9 — PG15 Augmented-Ternary Fundamental-Support-7 Barrier

Date: 2026-09-30

Status:
`JANUS_EXACT_FINITE_PROJECTIVE_SPARSIFICATION_COUNTERCONTROL__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AF3_PROJECTIVE_SCALING_FULL_SUPPORT_INVARIANCE_2026-09-30_v1.0.md`
- frozen `PG15_SAT_R11` source.

## 1. Object

Let `A` be the canonical PG15 `15 x 15` cubic Exact-One incidence matrix and work over `F3`. Form

\[
M=[A\mid-\mathbf1].
\]

Exact elimination gives

\[
\operatorname{rank}_{F3}M=11.
\]

For any column basis `B` of the represented ternary matroid, row-normalize the representation so that the basis columns are `I_11`. For a nonbasis element `e`, let

\[
s_B(e)=|\operatorname{supp}(N_e)|,
\]

where `N_e` is its normalized column. Equivalently `s_B(e)+1` is the size of the fundamental circuit of `e` with respect to `B`.

Define the projective fundamental-support width

\[
\sigma(M)=\min_B\max_{e\notin B}s_B(e).
\]

This is invariant under invertible row operations and nonzero column scalings, because it is determined by fundamental circuits of the represented matroid.

## 2. Exact exhaustive result

There are

\[
\binom{16}{11}=4368
\]

11-element column subsets. The exact checker enumerates all of them over `F3`.

Exactly `1904` are bases. For every one of these bases, at least one nonbasis normalized column has support at least seven. Hence

\[
\sigma(M)\ge7.
\]

The lower bound is attained. One basis, in zero-based ground-element indexing, is

```text
B = {0,1,2,3,4,5,6,7,8,10,12}.
```

The five nonbasis elements have normalized support sizes

```text
9  -> 5
11 -> 7
13 -> 5
14 -> 7
15 -> 7   (the syndrome element)
```

so

\[
\boxed{\sigma(M)=7.}
\]

## 3. Distinguished syndrome variant

Restrict to bases containing the syndrome element `e_b=15`.

Among the

\[
\binom{15}{10}=3003
\]

candidate subsets, exactly `1220` are bases. Again none has all nonbasis columns of support at most six.

The minimum maximum support remains seven. An attaining basis is

```text
B_b = {0,1,2,3,4,5,7,8,10,12,15}.
```

Its nonbasis support sizes are

```text
6  -> 7
9  -> 5
11 -> 7
13 -> 5
14 -> 7.
```

Thus even under the promise that the syndrome element lies in the basis,

\[
\boxed{\sigma_{e_b}(M)=7.}
\]

## 4. Consequence for frame / low-support representation routes

A frame basis would require every nonbasis element to be spanned by at most two basis elements, i.e. every normalized nonbasis column to have support at most two.

PG15 has no such basis. More strongly it has no basis with maximum nonbasis support at most `6`.

Therefore no legal AF3 projective representation change can transform this augmented ternary matroid into a basis-normal form whose nonbasis columns are uniformly 2-sparse (frame/signed-graphic), 3-sparse, ..., or 6-sparse.

This is a finite countercontrol against a universal low-fundamental-support sparsification theorem. It is not an asymptotic lower bound for all sources and does not rule out other projective decomposition classes.

## 5. External recognition boundary

Recent work announced by Davies, Geelen and Rodríguez gives a polynomial recognition algorithm for frame matroids with a distinguished frame element. That result remains a useful polynomial router for admitted instances.

PG15 proves only that such a router cannot be universal for the JANUS source carrier: the PG15 augmented ternary matroid is not frame at all, even before requiring the distinguished syndrome element to belong to a frame.

## 6. New frontier

The legal projective toolbox remains valuable, but the next universal representation class must genuinely extend beyond frame/signed-graphic low-support normalization.

A future PASS must either:

1. recognize and solve a broader projective matroid class that contains PG15;
2. decompose PG15-like residuals into polynomial full-support pieces with exact witness lifting; or
3. bypass basis sparsification by a different global AF3 constructor.

## 7. Ceiling

```text
PG15 augmented ternary rank = 11
TOTAL BASES = 1904
FUNDAMENTAL-SUPPORT WIDTH sigma = 7

BASES CONTAINING e_b = 1220
DISTINGUISHED WIDTH sigma_e_b = 7

FRAME / SIGNED-GRAPH BASIS EXISTS
= NO

UNIVERSAL LOW-SUPPORT <=6 PROJECTIVE NORMALIZATION
= FALSE BY PG15

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```