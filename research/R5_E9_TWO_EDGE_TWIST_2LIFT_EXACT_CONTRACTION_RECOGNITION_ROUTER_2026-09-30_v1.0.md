# R5 E9 — Two-Edge-Twist 2-Lift Exact Contraction Recognition Router

Date: 2026-09-30

Status:
`JANUS_EXACT_POLYNOMIAL_REPRESENTATION_CONTRACTION_ROUTER__TWO_EDGE_TWIST_WITH_LEFT_KERNEL_SEPARATOR__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER_2026-09-28_v1.0.md`
- `research/R5_E9_ONE_EDGE_TWIST_2LIFT_EXACT_SAT_CONTRACTION_2026-09-27_v1.0.md`
- `research/R5_E9_AFFINE_F3_PCQ_LINE_FREE_2LIFT_UNSAT_INFINITE_FAMILY_2026-09-30_v1.0.md`

Scientific firewall:

```text
THIS IS A POLYNOMIAL CONTRACTION ROUTER FOR A RECOGNIZABLE TWO-EDGE 2-LIFT SUBCLASS.
IT DOES NOT CLAIM THAT EVERY LINEAR-CUBIC SOURCE HAS SUCH A QUOTIENT.
IT DOES NOT SOLVE THE TWO-EDGE-IRREDUCIBLE RESIDUAL.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Two-edge twist

Let `A in {0,1}^{n x n}` be square cubic. Choose two nonincident incidences

```text
F={(i1,j1),(i2,j2)},
i1 != i2,
j1 != j2,
```

and let `E` mark exactly those two positions. Put

```text
P=A-E
```

and form

\[
\widehat A=
\begin{pmatrix}
P&E\\
E&P
\end{pmatrix}.
\]

Assume there exists

\[
y\in\ker_{\mathbb Q}(A^T)
\]

with

\[
y_{i_1}\ne y_{i_2}.
\]

Call this the `LEFT_KERNEL_SEPARATOR` premise.

## 2. Exact model-space theorem

### Theorem TETC-1

Under `LEFT_KERNEL_SEPARATOR`,

\[
\boxed{
\operatorname{Mod}(\widehat A)
=
\{(u,v):
Au=Av=\mathbf1,
\ u_{j_1}=v_{j_1},
\ u_{j_2}=v_{j_2}
\}.
}
\]

In particular,

\[
\boxed{
\widehat A\text{ is Exact-One SAT}
\iff
A\text{ is Exact-One SAT}.
}
\]

### Proof

Let `(u,v)` be a Boolean model of `Ahat` and put

\[
h=u-v.
\]

Subtracting the two lifted block equations gives

\[
(A-2E)h=0,
\]

so

\[
Ah=2Eh
=2(h_{j_1}e_{i_1}+h_{j_2}e_{i_2}).
\]

Every column of `A` has sum three. Left-multiplication by the all-one row gives

\[
3\sum_jh_j=2(h_{j_1}+h_{j_2}).
\]

Since `u,v` are Boolean,

```text
h_j1,h_j2 in {-1,0,1}.
```

Therefore the right side lies in `{-4,-2,0,2,4}`.  The only multiple of three is zero, hence

\[
h_{j_1}+h_{j_2}=0.
\]

Now left-multiply `Ah=2Eh` by `y^T`. Because `y^T A=0`,

\[
0=2(y_{i_1}h_{j_1}+y_{i_2}h_{j_2})
=2(y_{i_1}-y_{i_2})h_{j_1}.
\]

The separator premise gives

\[
h_{j_1}=0,
\qquad h_{j_2}=0.
\]

Thus `Eh=0`.  The first lifted equation becomes

\[
Pu+Ev
=Au-Eu+Ev
=Au-Eh
=Au
=\mathbf1.
\]

Similarly `Av=1`. Hence every lifted model projects to two base models agreeing at both twisted columns.

Conversely, if `Au=Av=1` and the two displayed coordinate equalities hold, then `Eh=0` and both lifted equations follow immediately. QED.

## 3. Polynomial separator test

The separator premise does not require guessing `y`.

Compute an exact rational basis of

\[
\ker(A^T).
\]

The premise holds iff the two row-evaluation functionals

\[
y\mapsto y_{i_1},
\qquad
y\mapsto y_{i_2}
\]

are not identical on that kernel. Equivalently there is a basis vector or rational linear combination on which their difference is nonzero.

This is one exact Gaussian-elimination / row-space test and is polynomial in the input bit-size.

## 4. Recognition from the Levi graph

Let `Hhat` be the connected cubic bipartite Levi graph of an input source.  Suppose it is a two-edge-twist lift of a base Levi graph `H`, and suppose

```text
H-F is connected.
```

The two negative base incidences create four crossed lift edges. Removing those four crossed edges leaves exactly two connected components, each isomorphic to `H-F`.

This yields a deterministic recognition algorithm.

### Candidate enumeration

The lift has `O(n)` Levi edges. Enumerate every unordered four-edge set `C`. There are

\[
O(|E(Hhat)|^4)=\operatorname{poly}(n)
\]

candidates.

For each candidate:

1. delete `C`;
2. require exactly two connected components `K0,K1` of equal bipartite sizes;
3. require exactly two left-shore and two right-shore cut endpoints in each component;
4. enumerate the constant number of possible correspondences among those marked endpoints;
5. test color-preserving marked isomorphism `phi:K0 -> K1`;
6. require the four deleted edges to occur in two crossed orbits under the sheet-swap induced by `phi`;
7. reconstruct a candidate base `H` from one component by restoring the two corresponding base incidences;
8. rebuild the two-edge-twist lift from `(H,F)` and verify directly that it is color-preserving isomorphic to the original `Hhat` with the candidate sheet map.

The degree is at most three throughout.  Colored/marked bounded-valence graph isomorphism is polynomial-time by the classical Luks algorithm.  The boundary has constant size, so its correspondence enumeration is constant-factor work.

The final rebuild check is mandatory: an arbitrary four-edge cut is never accepted merely because the two shores happen to be isomorphic.

Hence recognition/recovery of this subclass is deterministic polynomial time.

## 5. Exact contraction router

The router is:

```text
INPUT: connected square cubic Exact-One source Ahat.

1. Search for a certified two-edge-twist quotient (A,F)
   by the polynomial four-edge-cut reconstruction algorithm.

2. If none exists:
      return NOT_IN_TETC_BRANCH.

3. Verify H(A)-F is connected.

4. Compute ker_Q(A^T) and test LEFT_KERNEL_SEPARATOR.

5. If separator fails:
      return NOT_IN_TETC_BRANCH.

6. Contract Ahat -> A.

7. Solve A by the global router recursively / by another certified terminal.

8. Witness maps:
      base SAT x -> lifted SAT (x,x),
      lifted SAT (u,v) -> base SAT u (and v).
```

Every acceptance is independently rebuild-verifiable and every witness map is linear time after recognition.

## 6. Recursive contraction complexity

Every successful contraction halves the number of source variables. Therefore any chain of successful TETC contractions has length at most

\[
\lfloor\log_2 n\rfloor.
\]

At level `s`, four-edge-cut enumeration, bounded-degree marked isomorphism, exact kernel computation, rebuild verification, contraction and witness bookkeeping are all polynomial in the current instance size.

A logarithmic number of polynomial-size levels is polynomial in the original input size. Thus iterated recognized TETC towers are polynomially reducible to their first irreducible root.

## 7. Positive SAT control

Take

```text
A=J_3.
```

Choose twists `(0,0)` and `(1,1)`.  The two incidences are nonincident, `H-F` is connected, and

```text
y=(1,-1,0)
in ker(A^T)
```

separates rows 0 and 1.

The base has exactly three Exact-One models.  Exhaustive replay on the six-variable lift verifies TETC-1: every lifted model is an ordered pair of base models agreeing at columns `0` and `1`, and every such pair is a lifted model.

This is a non-vacuous SAT model-space control.

## 8. Proper-blocking infinite family is absorbed

Apply the router to the family

```text
R5_E9_AFFINE_F3_PCQ_LINE_FREE_2LIFT_UNSAT_INFINITE_FAMILY.
```

Its construction freezes at every level:

```text
F_t = two distinguished nonincident incidences,
G_t-F_t connected,
y_t in ker(A_t^T) with y_t[i1] != y_t[i2].
```

Therefore every non-base member is recognized by the TETC premise and contracts exactly to its predecessor.  Repeating contracts a size

\[
15\cdot2^t
\]

member to the fixed `15`-variable source `A*` in exactly `t` successful contractions.

The fixed root `A*` is already an exact finite UNSAT control. Therefore this entire infinite AF3 proper-blocking family is polynomially decidable by the enlarged router portfolio.

This is scientifically important: the family remains a valid falsifier of

```text
PCQ + projective-line terminal = universal AF3 solver,
```

but it is **not** a hard survivor against representation-changing two-edge-lift contraction.

## 9. Relation to one-edge contraction

The existing one-edge theorem is the special case where the column-sum divisibility argument by itself forces the single twisted coordinate difference to vanish.

With two twisted incidences, divisibility gives only

\[
h_{j_1}+h_{j_2}=0,
\]

and the left-kernel separator is exactly the additional certificate needed to force both differences to zero.

Thus the two routers form a strict representation hierarchy:

```text
ONE-EDGE TWIST
  -> unconditional exact contraction.

TWO-EDGE TWIST
  -> exact contraction when a polynomially checkable left-kernel separator exists.
```

## 10. Scope firewall

Do not infer:

```text
all 4-edge cuts are TETC quotients;
all two-edge lifts satisfy the separator;
all proper blocking residuals are lift-contractible;
TETC-irreducible sources are hard;
P=NP.
```

The router may return `NOT_IN_TETC_BRANCH` without making a SAT/UNSAT claim.

## 11. New live residual

After adding this router, the AF3 proper-blocking frontier should be intersected with representation irreducibility:

```text
R5_E9_AFFINE_F3_PROPER_BLOCKING_TETC_IRREDUCIBLE_GLOBAL_GATE_V1
```

A genuine next hostile control must survive simultaneously:

```text
AF3-PCQ fixed point,
projective-line-free,
known network/TU/binet/regular terminals,
OET contraction,
TETC contraction,
and all older source terminals.
```

The next constructive target is a polynomial contraction or witness selector on that full intersection residual.

## 12. Ceiling

```text
TWO-EDGE LIFT MODEL SPACE UNDER LEFT-KERNEL SEPARATOR = PROVED
TWO-EDGE EQSAT CONTRACTION = PROVED
SEPARATOR DISCOVERY = POLYNOMIAL
FOUR-CROSSED-EDGE RECOGNITION / REBUILD = POLYNOMIAL
WITNESS PROJECTION / DIAGONAL LIFT = POLYNOMIAL
ITERATED TETC CHAIN = POLYNOMIAL TOTAL COST

AF3 PCQ-FIXED LINE-FREE INFINITE FAMILY = ABSORBED BY THIS ROUTER
TETC-IRREDUCIBLE PROPER-BLOCKING RESIDUAL = OPEN

UNIVERSAL POLYNOMIAL SOLVER = NOT PROVED
E8_D1 = EMPTY
P_VS_NP = OPEN
```