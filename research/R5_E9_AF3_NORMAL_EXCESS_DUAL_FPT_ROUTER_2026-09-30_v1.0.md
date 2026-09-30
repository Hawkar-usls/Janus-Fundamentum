# R5 E9 — AF3 Normal-Excess Dual FPT Router

Date: 2026-09-30

Status:
`JANUS_EXACT_AF3_FPT_ROUTER__NORMAL_RANK_VS_EXCESS_DUALITY__PROJECTIVE_INVARIANT__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`
- `research/R5_E9_AF3_PROJECTIVE_SCALING_FULL_SUPPORT_INVARIANCE_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS IS AN EXACT DETERMINISTIC FPT ROUTER FOR AN APSQ-SATURATED AF3 RESIDUAL.
THE NORMAL RANK / EXCESS PARAMETERS ARE INVARIANT UNDER LEGAL AF3 PROJECTIVE
REPRESENTATION CHANGES; PROJECTIVE SCALING CANNOT BE USED TO MAKE k SMALLER.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT SOLVER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. APSQ-saturated input

After AF3 conversion and exact parallel saturation, write the surviving avoidance system as

\[
a_j\alpha\ne b_j,\qquad j=1,\dots,m,
\]

over `F3`, with nonzero pairwise nonprojective normals. Constant coordinates and all one-/two-/three-offset parallel terminals have already been processed by APSQ.

Let

\[
r:=\operatorname{rank}_{\mathbb F_3}\{a_1,\dots,a_m\},
\qquad k:=m-r.
\]

Call `k` the **AF3 normal excess**. This is different from the older rational row-basis overlap excess: here `r` is the rank of the coordinate-zero hyperplane normal family after AF3/APSQ, not `rank_Q(A)`.

## 2. Exact Boolean-cube quotient

Choose `r` surviving constraints whose normals form a basis and put their normals into a matrix `B`. Relabel them `1,...,r`, and define

\[
y_i=a_i\alpha-b_i.
\]

Every surviving normal lies in `row(B)`, and the map `alpha -> B alpha` is onto `F3^r`; directions in `ker B` are invisible to the whole residual. Therefore the residual depends only on `y`.

The basis constraints become

\[
y_i\ne0,
\]

so

\[
\boxed{y\in(F_3^*)^r=\{1,2\}^r.}
\]

For every extra constraint write uniquely

\[
a_{r+j}=c_jB.
\]

If `b_B=(b_1,...,b_r)^T`, then its forbidden equation becomes

\[
c_jy=e_j,
\qquad e_j=b_{r+j}-c_jb_B.
\]

Collect the `c_j` into `C in F3^{k x r}` and the offsets into `e in F3^k`.

### Theorem NED-1

The APSQ residual is satisfiable iff

\[
\boxed{
\exists y\in\{1,2\}^r\quad
\forall j\in[k]:(Cy)_j\ne e_j.
}
\]

Every successful `y` reconstructs an AF3 parameter point by solving `B alpha=y+b_B`; AF3 then reconstructs the Boolean Exact-One witness.

## 3. Direct router

Enumerate all `2^r` Boolean-cube points and check the `k` extra forbidden equations:

\[
\boxed{T_{direct}=2^r\operatorname{poly}(m,r).}
\]

Thus `r=O(log n)` is a polynomial island.

## 4. Dual syndrome DP

Write the `i`-th column of `C` as `v_i in F3^k`. Since `y_i in {1,2}={+1,-1}`,

\[
Cy=\sum_i y_iv_i.
\]

Let `S_i` be the reachable syndromes after the first `i` variables. Initialize

\[
S_0=\{0\}
\]

and update

\[
\boxed{S_i=(S_{i-1}+v_i)\cup(S_{i-1}-v_i).}
\]

At every stage `|S_i|<=3^k`. At the end, SAT holds iff some `s in S_r` obeys

\[
s_j\ne e_j\quad\forall j.
\]

Store one predecessor/sign for each reached syndrome to reconstruct `y`.

### Theorem NED-2

The APSQ residual is decidable with exact witness reconstruction in

\[
\boxed{3^k\operatorname{poly}(m,r)}.
\]

No `3^d` affine-space enumeration and no hyperplane-subfamily enumeration is used.

## 5. Combined two-sided router

Run the cheaper exact route:

\[
\boxed{
T=\min(2^r,3^{m-r})\operatorname{poly}(n).
}
\]

Hence both

```text
r = O(log n)
```

and

```text
m-r = O(log n)
```

are deterministic polynomial islands.

## 6. Sharp generic control: excess two may already be UNSAT

Take `r>=2`, the basis forbidden hyperplanes `y_i=0`, and only two extra forbidden hyperplanes

\[
y_1+y_2=0,
\qquad y_1-y_2=0.
\]

The four relevant normal directions are projectively distinct. Here `k=2`, yet every pair `y_1,y_2 in {+1,-1}` is either equal or opposite, so one extra hyperplane is always hit. Thus

\[
\boxed{k=2\not\Rightarrow SAT.}
\]

The dual DP decides this UNSAT control using at most nine syndrome states.

## 7. PG15 control

For canonical PG15, exact AF3 + APSQ gives

```text
m = 11
r = 4
k = 7
```

The direct quotient has only `2^4=16` points. The exact regression finds precisely four avoiding points and reconstructs the four frozen Exact-One witnesses. The syndrome DP visits at most `3^7` states (and only 16 on the frozen deterministic normalization).

## 8. Projective invariance of the arrangement parameters

The initial version of this note incorrectly suggested that a legal AF3 projective representation change might reduce `(m,r,k)`. That possibility is now explicitly closed.

Let

\[
M=[A\mid-\mathbf1]
\]

and let a legal projective representation change be

\[
N=UMD,
\qquad U\in GL,
\qquad D=\operatorname{diag}(d_e),\ d_e\ne0.
\]

The AF3 projective-invariance theorem gives the support-preserving code isomorphism

\[
z\mapsto Dz.
\]

Fix the distinguished syndrome coordinate `e_b`. On the affine slices normalized to syndrome value one, this isomorphism acts on source coordinates by the nonzero diagonal scaling

\[
z_i\longmapsto (d_i/d_{e_b})z_i.
\]

Therefore the two affine solution spaces are linearly isomorphic and each coordinate-zero set maps exactly to the corresponding coordinate-zero set.

Consequently the complete coordinate-hyperplane arrangement is preserved up to affine-linear isomorphism. In particular it preserves:

```text
which coordinate hyperplanes coincide,
parallel classes and their multiplicities,
all linear dependencies among normal directions,
normal rank r,
number m of distinct surviving hyperplanes,
normal excess k=m-r.
```

APSQ operations themselves are defined only from zero/constant hyperplanes and one-/two-/three-offset parallel classes. Those structures are also preserved by the same isomorphism. Thus APSQ-saturated residuals are isomorphic and have identical `(m,r,k)`.

### Theorem NED-3 — projective invariance

\[
\boxed{
(m,r,k)_{APSQ}
\text{ is invariant under legal AF3 row operations and nonzero column scalings.}
}
\]

Hence projective representation changes may expose a different polynomial structural class, but they cannot turn a middle-excess instance into a low-`r` or low-`k` instance of this router.

## 9. Correct live frontier

Freeze

```text
R5_E9_AF3_MIDDLE_EXCESS_OR_NEW_REPRESENTATION_CLASS_GATE_V2
```

A universal PASS must handle the residual where both `r` and `k=m-r` are superlogarithmic by one of:

1. recognizing another polynomial full-support class (regular/graphic/cographic/frame where applicable, bounded-width, etc.);
2. a source-specific polynomial decomposition with exact witness lifting; or
3. a direct global full-support constructor / cover certificate.

Projective representation changes remain legal and useful for entering such classes, but **not** for reducing `r` or `k` themselves.

## 10. Ceiling

```text
AF3 BASIS-CUBE NORMAL FORM
= PROVED

DIRECT ROUTER
= 2^r poly

DUAL SYNDROME ROUTER
= 3^(m-r) poly

COMBINED ROUTER
= min(2^r,3^(m-r)) poly

APSQ NORMAL RANK / EXCESS UNDER AF3 PROJECTIVE CHANGES
= INVARIANT / PROVED

EXCESS 2 => SAT
= FALSE

PG15
= (m,r,k)=(11,4,7), SAT / FOUR WITNESSES

UNIVERSAL MIDDLE-EXCESS COVERAGE
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```