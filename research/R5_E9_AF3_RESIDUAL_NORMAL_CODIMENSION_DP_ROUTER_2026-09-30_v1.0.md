# R5 E9 — AF3 Residual-Normal Codimension Syndrome-DP Router

Date: 2026-09-30

Status:
`JANUS_EXACT_FPT_ROUTER__POST_APSQ_NORMAL_CODIMENSION__POLYNOMIAL_WHEN_EPSILON_LOGARITHMIC__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS IS AN EXACT DETERMINISTIC ROUTER WITH COST O(m*3^epsilon*poly(L)).
IT IS POLYNOMIAL WHEN epsilon=O(log n), INCLUDING epsilon=0.
NO UNIVERSAL O(log n) BOUND ON epsilon IS CLAIMED.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Saturated affine-F3 residual

After AF3 and exhaustive APSQ, write the surviving nonzero constraints as

\[
a_i\alpha\ne b_i,
\qquad i=1,\ldots,m,
\]

where

```text
alpha in F3^d,
a_i in F3^d \ {0},
b_i in F3,
```

and no two surviving constraints belong to the same projective normal class with different offsets.  Duplicate identical hyperplanes have already been removed.

Let

\[
N=\begin{pmatrix}a_1\\ \vdots\\a_m\end{pmatrix}
\in\mathbb F_3^{m\times d}
\]

and put

\[
r=\operatorname{rank}_{\mathbb F_3}(N),
\qquad
\boxed{\epsilon:=m-r.}
\]

Call `epsilon` the **residual-normal codimension/excess**.

The parameter `epsilon` is not the rational nullity, ternary kernel dimension, branch-width, or number of source variables.  It measures only the number of linear dependencies among the surviving forbidden-hyperplane normals.

## 2. Image-space reformulation

Set

\[
y=N\alpha\in\mathbb F_3^m.
\]

The avoidance constraints are exactly

\[
y_i\ne b_i\quad\forall i.
\]

Compute by Gaussian elimination a full-row-rank matrix

\[
H\in\mathbb F_3^{\epsilon\times m}
\]

whose row space is the left kernel of `N`:

\[
HN=0,
\qquad
\operatorname{rank}(H)=\epsilon.
\]

Because `rank(N)=r`,

\[
\boxed{
\operatorname{im}(N)=\ker(H).
}
\]

Therefore the residual is SAT iff there exists

\[
y\in\mathbb F_3^m
\]

with

\[
Hy=0,
\qquad
y_i\ne b_i\quad\forall i.
\]

## 3. Two-choice syndrome form

For each coordinate write

\[
y_i=b_i+s_i.
\]

The inequality `y_i != b_i` is exactly

\[
s_i\in\mathbb F_3^*=\{1,2\}.
\]

Substituting gives

\[
\boxed{
Hs=-Hb,
\qquad s\in(\mathbb F_3^*)^m.
}
\]

This is a two-choice vector-sum problem whose syndrome dimension is only `epsilon`.

Let `h_i` be column `i` of `H` and let

\[
t=-Hb\in\mathbb F_3^\epsilon.
\]

We need signs `s_i in {1,2}` such that

\[
\sum_{i=1}^m s_i h_i=t.
\]

## 4. Exact dynamic program

Maintain reachable syndromes after processing the first `j` coordinates:

```text
R_0 = {0}

R_j = {
    z + h_j,
    z + 2 h_j
    : z in R_{j-1}
}.
```

All arithmetic is over `F3^epsilon`.
There are at most

\[
3^\epsilon
\]

states at every layer and exactly two transitions per state-coordinate pair.
Store one predecessor for every newly reached state.

At the end:

```text
t not in R_m -> UNSAT residual;
t in R_m     -> backtrack one s in {1,2}^m.
```

Then set `y=b+s` and solve

\[
N\alpha=y
\]

by Gaussian elimination.  Since `Hy=0`, image-space exactness guarantees consistency.
The recovered `alpha` avoids every surviving hyperplane.
Reverse the APSQ substitutions and the AF3 decoder to obtain the Exact-One witness.

### Theorem RNCDP-1

The algorithm above is sound and complete for every saturated AF3 residual.

## 5. Complexity

The DP has at most

\[
(m+1)3^\epsilon
\]

reachable-state records and at most

\[
2m3^\epsilon
\]

transitions.
Each syndrome operation costs `O(epsilon)` field operations with a direct tuple representation.
All rank, left-kernel, reconstruction and APSQ-lift operations are polynomial in the input bit-size.

Hence

\[
\boxed{
T=O(m\,\epsilon\,3^\epsilon)+\operatorname{poly}(L).
}
\]

In particular:

```text
epsilon fixed      -> deterministic polynomial;
epsilon=O(log n)   -> deterministic polynomial;
epsilon=0          -> one linear solve after choosing arbitrary nonzero s_i.
```

No decomposition-discovery oracle is required: `N`, `H`, `epsilon` and the DP are all obtained by ordinary `F3` Gaussian elimination.

## 6. Counting variant

Replacing predecessor flags by integer counts gives the exact number of residual avoiding vectors `y`, hence the number of avoiding `alpha` modulo any kernel of `N` if `rank(N)<d`.
For decision/search only reachability is needed.

The counting version is useful as a finite regression but is not required by the router.

## 7. Controls

### EQ3 gadget

After duplicate removal the gadget residual is

```text
m=3,
rank(N)=2,
epsilon=1.
```

The syndrome DP finds exactly three avoiding affine words, matching the exact AF3 gadget enumeration and terminal projection `EQ3`.

### PG15

After APSQ:

```text
m=11,
rank(N)=4,
epsilon=7.
```

The DP explores at most `3^7=2187` syndromes and reconstructs one of the four known Exact-One witnesses.  This is a finite control; `epsilon=7` on one instance is not an asymptotic statement.

### Globally regularized unique-model 18_3 SAT seed

For the full 180-variable EQ3-regularized instance, global APSQ reduces the affine system in two pinning rounds:

```text
d_F3: 20 -> 18 -> 12.
```

The final residual has

```text
m=12,
rank(N)=12,
epsilon=0.
```

Therefore RNCDP-1 immediately constructs a full-support affine solution.  In fact every independent residual normal can choose either allowed value independently, giving `2^12` residual full-support choices, exactly matching the independent extension multiplicity of the zero-valued source variables in the unique source model.

### Prime UNSAT seed after regularization

The globally regularized frozen prime UNSAT seed is already terminated earlier by APSQ through a three-offset parallel class, so RNCDP is not entered.

## 8. Strategic consequence

AF3/APSQ now has a second exact progress currency after parallel saturation:

\[
\boxed{\epsilon=m-\operatorname{rank}(N).}
\]

This currency can be small even when:

```text
rational nullity is large,
ternary affine dimension is large,
source size is large,
and local gadget modes are present.
```

The next universal question is therefore sharply testable:

```text
After exhaustive AF3 parallel saturation and all existing exact polynomial
terminals, is residual-normal excess epsilon universally O(log n), or can a
source-generated family force epsilon=omega(log n) while surviving every
other router?
```

A proof of the logarithmic bound would close the source carrier through RNCDP-1.
A counterfamily would kill this route cleanly and identify the next missing structure.

## 9. New live gate

Freeze

```text
R5_E9_AF3_RESIDUAL_NORMAL_EXCESS_UNIVERSAL_BOUND_GATE_V1
```

Required PASS for universal promotion:

```text
for every linear-cubic source surviving earlier terminals and APSQ,
epsilon <= C log n
```

with polynomially computable constants/representation and full witness/certificate reconstruction.

Required FAIL:

```text
an explicit arbitrary-size source family surviving APSQ and existing routers
with epsilon=omega(log n),
```

not merely finite large-epsilon examples.

## 10. Ceiling

```text
POST-APSQ RESIDUAL DECISION
= O(m*epsilon*3^epsilon)+poly(L)

EPSILON=0
= POLYNOMIAL / DIRECT CONSTRUCTOR

EPSILON=O(log n)
= POLYNOMIAL

PG15
= epsilon 7 / SOLVED BY FINITE DP

REGULARIZED UNIQUE-MODEL SAT SEED
= epsilon 0 AFTER GLOBAL APSQ / SOLVED

UNIVERSAL epsilon=O(log n)
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
