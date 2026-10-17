# R5 E9 — AF3 Normal-Excess / Syndrome-Rank Dual FPT Router

Date: 2026-09-30

Status:
`JANUS_EXACT_AF3_FPT_ROUTER__NORMAL_RANK_VS_SYNDROME_IMAGE_RANK__PROJECTIVE_INVARIANT__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`
- `research/R5_E9_AF3_PROJECTIVE_SCALING_FULL_SUPPORT_INVARIANCE_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS IS AN EXACT DETERMINISTIC FPT ROUTER FOR AN APSQ-SATURATED AF3 RESIDUAL.
IT DOES NOT PROVE THAT ITS PARAMETERS ARE O(log n) ON ALL SOURCES.
THE APSQ ARRANGEMENT RANK/EXCESS IS INVARIANT UNDER LEGAL AF3 PROJECTIVE CHANGES.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT SOLVER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. APSQ-saturated input

After AF3 conversion and exact parallel saturation, write the surviving avoidance system as

\[
a_j\alpha\ne b_j,\qquad j=1,\dots,m,
\]

over `F3`, with nonzero pairwise nonprojective normals. Let

\[
r=\operatorname{rank}_{F3}\{a_1,\dots,a_m\},
\qquad k=m-r.
\]

`k` is the AF3 normal excess. This is distinct from the older rational row-basis overlap excess.

## 2. Exact Boolean-cube quotient

Choose `r` surviving constraints whose normals form a basis and put those normals into a matrix `B`. Define

\[
y_i=a_i\alpha-b_i,
\qquad i=1,\dots,r.
\]

Directions in `ker B` are invisible to the entire residual. The basis constraints become `y_i != 0`, hence

\[
\boxed{y\in(F_3^*)^r=\{1,2\}^r.}
\]

For each of the `k` extra constraints write

\[
a_{r+j}=c_jB.
\]

With `b_B=(b_1,...,b_r)^T`, its forbidden equation becomes

\[
c_jy=e_j,
\qquad e_j=b_{r+j}-c_jb_B.
\]

Collect the coefficient rows into

\[
C\in F_3^{k\times r},
\qquad e\in F_3^k.
\]

### Theorem NED-1

The APSQ residual is satisfiable iff

\[
\boxed{
\exists y\in\{1,2\}^r
\quad\forall j\in[k]:(Cy)_j\ne e_j.
}
\]

A successful `y` reconstructs `alpha` from `B alpha=y+b_B`, then reconstructs the AF3 word and the Boolean Exact-One witness.

## 3. Direct router

Enumerating the quotient cube gives

\[
\boxed{T_{direct}=2^r\operatorname{poly}(n).}
\]

Thus `r=O(log n)` is a polynomial island.

## 4. First dual bound: normal excess

Writing the columns of `C` as `v_i in F3^k`,

\[
Cy=\sum_i y_iv_i,
\qquad y_i\in\{+1,-1\}.
\]

The standard reachable-syndrome recurrence is

\[
S_0=\{0\},
\qquad
S_i=(S_{i-1}+v_i)\cup(S_{i-1}-v_i),
\]

with at most `3^k` states. This already gives a `3^k poly(n)` router.

## 5. Exact syndrome-image compression

The `3^k` ambient bound is unnecessary. Every reachable syndrome lies in

\[
\operatorname{im}C\subseteq F_3^k.
\]

Let

\[
\rho:=\operatorname{rank}_{F3}C.
\]

Choose a column-space basis

\[
Q\in F_3^{k\times\rho}
\]

for `im C`. For each column `v_i` compute its unique compressed coordinate

\[
w_i\in F_3^\rho,
\qquad v_i=Qw_i.
\]

Then

\[
Cy=Q\left(\sum_i y_iw_i\right).
\]

Run the same DP in the compressed space:

\[
T_0=\{0\},
\qquad
T_i=(T_{i-1}+w_i)\cup(T_{i-1}-w_i).
\]

At all times

\[
|T_i|\le3^\rho.
\]

At the root, a compressed state `t` is accepting exactly when

\[
(Qt)_j\ne e_j\quad\forall j.
\]

Store one predecessor/sign for each reached state to reconstruct `y`.

### Theorem NED-2 — syndrome-rank router

The APSQ residual is decidable with exact witness reconstruction in

\[
\boxed{3^\rho\operatorname{poly}(n)},
\qquad
\rho=\operatorname{rank}_{F3}C\le\min(r,k).
\]

Therefore the strongest immediate two-sided bound is

\[
\boxed{
T=\min(2^r,3^\rho)\operatorname{poly}(n).
}
\]

This strictly dominates the raw `3^k` bound whenever the extra-hyperplane coefficient rows are rank-deficient.

Polynomial islands now include

```text
r = O(log n),
or
rho = O(log n).
```

## 6. Basis dependence of rho

Unlike the arrangement invariants `(m,r,k)`, the value `rho=rank(C)` is attached to the chosen basis of normal directions: it is exactly the rank of the span of the nonbasis normals after expressing them in that basis.

An implementation may try polynomially many certified basis choices and keep the best discovered `rho`; however no polynomial algorithm for globally minimizing `rho` over all normal bases is assumed here.

Thus no hidden minimum-rank-basis oracle is used in NED-2.

## 7. Sharp generic control: excess two may already be UNSAT

Take `r>=2`, basis forbidden hyperplanes `y_i=0`, and two extra forbidden hyperplanes

\[
y_1+y_2=0,
\qquad y_1-y_2=0.
\]

Here `k=2` and `rho=2`, yet every `(+/-1,+/-1)` pair is either equal or opposite. Hence there is no avoiding point:

\[
\boxed{k=2\not\Rightarrow SAT.}
\]

The compressed DP decides the control in at most `3^2=9` states.

## 8. PG15 control

For canonical PG15 after AF3 + APSQ:

```text
m   = 11
r   = 4
k   = 7
rho = 4   (for the deterministic normal basis used by the checker)
```

The direct quotient has `2^4=16` points and exactly four avoiding points, reconstructing the four frozen Exact-One witnesses.

The old ambient syndrome bound is `3^7=2187`; image-rank compression reduces the theorem-level DP state bound to `3^4=81`. The direct side remains cheaper on this finite control.

## 9. Projective invariance of (m,r,k)

Let the augmented ternary representation be

\[
M=[A\mid-\mathbf1]
\]

and let

\[
N=UMD,
\qquad U\in GL,
\qquad D=\operatorname{diag}(d_e),\ d_e\ne0.
\]

The AF3 projective-invariance theorem gives a support-preserving kernel isomorphism `z -> Dz`. After normalizing the syndrome coordinate to one, the affine source coordinates differ only by nonzero diagonal scaling `z_i -> (d_i/d_b)z_i`.

Therefore the coordinate-zero hyperplane arrangements are affine-linearly isomorphic. They have the same coincident hyperplanes, parallel classes, normal dependencies, normal rank `r`, distinct-hyperplane count `m`, and excess `k=m-r`. APSQ uses only those preserved structures, so its saturated residual has the same `(m,r,k)`.

### Theorem NED-3

\[
\boxed{(m,r,k)_{APSQ}\text{ is invariant under legal AF3 projective representation changes}.}
\]

Projective transformations may reveal another tractable structural class, but cannot make `r` or `k` smaller for this router.

## 10. Correct live frontier

Freeze

```text
R5_E9_AF3_MIDDLE_RANK_OR_NEW_REPRESENTATION_CLASS_GATE_V3
```

A universal PASS must handle residuals for which every polynomially obtained normal basis leaves both direct rank `r` and compressed syndrome rank `rho` superlogarithmic, or enter a different polynomial representation/decomposition class with exact witness lifting.

## 11. Ceiling

```text
AF3 BASIS-CUBE NORMAL FORM
= PROVED

DIRECT ROUTER
= 2^r poly

RAW DUAL ROUTER
= 3^k poly

COMPRESSED DUAL ROUTER
= 3^rho poly, rho=rank(C)

STRONGEST CURRENT BOUND
= min(2^r,3^rho) poly

APSQ (m,r,k) UNDER PROJECTIVE CHANGES
= INVARIANT / PROVED

PG15
= (m,r,k,rho)=(11,4,7,4), FOUR WITNESSES

UNIVERSAL MIDDLE-RANK COVERAGE
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```