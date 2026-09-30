# R5 E9 — AF3 Normal-Excess Dual FPT Router

Date: 2026-09-30

Status:
`JANUS_EXACT_AF3_FPT_ROUTER__NORMAL_RANK_VS_EXCESS_DUALITY__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS IS AN EXACT DETERMINISTIC FPT ROUTER FOR AN APSQ-SATURATED AF3 RESIDUAL.
IT DOES NOT PROVE THAT THE AF3 NORMAL EXCESS IS O(log n) ON ALL SOURCES.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT SOLVER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. APSQ-saturated input

After AF3 conversion and exact parallel saturation, write the surviving avoidance system as

\[
a_j\alpha\ne b_j,\qquad j=1,\dots,m,
\]

over `F3`, where:

- every `a_j` is nonzero;
- no two surviving constraints have projectively parallel normals;
- all constant-zero and constant-safe coordinates have already been removed;
- all two-offset parallel pins have already been substituted;
- a three-offset class would already have returned UNSAT.

Let

\[
r:=\operatorname{rank}_{\mathbb F_3}\{a_1,\dots,a_m\},
\qquad
k:=m-r.
\]

Call `k` the **AF3 normal excess**.

The distinction from the older rational row-basis overlap excess is essential: here `r` is the rank of the projectively simplified AF3 coordinate-normal family after APSQ, not `rank_Q(A)`.

## 2. Quotient away invisible parameter directions

Choose `r` surviving constraints whose normals form a basis, and relabel them `1,...,r`. Put their normals into the matrix

\[
B=\begin{pmatrix}a_1\\ \vdots\\ a_r\end{pmatrix}.
\]

The linear map `alpha -> B alpha` is onto `F3^r`. Any parameter direction in `ker B` is invisible to every surviving constraint because every other normal lies in the row span of `B`.

Define new quotient coordinates

\[
y_i=a_i\alpha-b_i,
\qquad i=1,\dots,r.
\]

For every `y in F3^r` there exists an `alpha` producing that `y`, and all surviving constraints depend only on `y`.

The `r` chosen basis constraints become simply

\[
y_i\ne0,
\]

so any avoiding point must satisfy

\[
\boxed{y\in(F_3^*)^r=\{1,2\}^r.}
\]

## 3. Extra constraints in basis coordinates

For each extra normal `a_{r+j}`, `j=1,...,k`, compute its unique coefficient row

\[
c_j\in F_3^r,
\qquad a_{r+j}=c_jB.
\]

Since

\[
B\alpha=y+b_B,
\]

where `b_B=(b_1,...,b_r)^T`, the extra forbidden equation

\[
a_{r+j}\alpha=b_{r+j}
\]

becomes

\[
c_j y=e_j,
\qquad
\boxed{e_j=b_{r+j}-c_jb_B.}
\]

Collect the rows `c_j` into

\[
C\in F_3^{k\times r},
\qquad e\in F_3^k.
\]

### Theorem NED-1 — exact Boolean-cube syndrome normal form

The APSQ residual is satisfiable iff

\[
\boxed{
\exists y\in\{1,2\}^r
\quad\forall j\in[k]:
(Cy)_j\ne e_j.
}
\]

Every successful `y` reconstructs an original AF3 parameter point by solving `B alpha=y+b_B`, and AF3 then reconstructs the Boolean Exact-One witness.

## 4. Direct-side exact router

Enumerating all `2^r` vectors `y in {1,2}^r` and checking the `k` extra equations gives

\[
T_{\rm direct}=2^r\operatorname{poly}(m,r).
\]

Thus `r=O(log n)` is a polynomial island.

## 5. Dual syndrome DP

The key new route parameterizes by `k=m-r`, not by `r`.

Write the `i`-th column of `C` as

\[
v_i\in F_3^k.
\]

For `y_i in {1,2}={+1,-1}` modulo 3,

\[
Cy=\sum_{i=1}^r y_i v_i.
\]

Process the columns one at a time. Let `S_i subseteq F3^k` be the set of syndromes reachable using the first `i` variables.

Initialize

\[
S_0=\{0\}.
\]

Update

\[
\boxed{
S_i=(S_{i-1}+v_i)\cup(S_{i-1}-v_i).
}
\]

At all times

\[
|S_i|\le3^k.
\]

After all `r` variables have been processed, NED-1 is SAT iff some reachable syndrome `s in S_r` satisfies

\[
\boxed{s_j\ne e_j\quad\forall j.}
\]

Store for each newly reached syndrome one predecessor and one sign choice; reversing those pointers reconstructs `y` in `O(r)` stages.

### Theorem NED-2 — dual exact FPT router

The APSQ residual is decidable with witness reconstruction in

\[
\boxed{3^k\operatorname{poly}(m,r)}
\]

bit operations, where `k=m-r` is the AF3 normal excess.

The algorithm never enumerates the `3^d` original affine parameter space and never enumerates hyperplane subfamilies.

## 6. Combined two-sided router

Run the cheaper of the direct cube enumeration and the syndrome DP:

\[
\boxed{
T=\min(2^r,3^{m-r})\operatorname{poly}(n).
}
\]

Therefore both of the following are exact polynomial islands:

```text
AF3 normal rank r = O(log n),
AF3 normal excess m-r = O(log n).
```

A universal polynomial algorithm would still need a theorem that handles the middle region where both quantities are superlogarithmic, or a different representation route that bypasses them.

## 7. Sharp generic control: excess two can already be UNSAT

The FPT theorem must not be confused with a statement that small positive excess forces SAT.

Take `r>=2`. Use the `r` basis hyperplanes

\[
y_i=0,
\]

and add only the two further forbidden hyperplanes

\[
y_1+y_2=0,
\qquad
y_1-y_2=0.
\]

All `r+2` normals are projectively distinct where relevant, so this is parallel-simple and has

\[
k=(r+2)-r=2.
\]

But for every `y_1,y_2 in {+1,-1}`, either `y_1=y_2` or `y_1=-y_2`. Therefore one of the two extra equations is always hit and there is no avoiding point.

Hence

\[
\boxed{k=2\not\Rightarrow SAT.}
\]

The dual DP correctly decides this control using at most `3^2=9` syndrome states.

## 8. PG15 control

For the canonical PG15 source, exact AF3 conversion followed by APSQ gives

```text
parameter dimension before quotient = 4,
distinct surviving hyperplanes m    = 11,
normal rank r                        = 4,
normal excess k=m-r                  = 7.
```

The direct side checks `2^4=16` quotient-cube points; the syndrome side uses at most `3^7=2187` states. The exact regression verifies that the reconstructed avoiding points decode to the four frozen Exact-One witnesses.

This finite control is not an asymptotic polynomial-coverage claim.

## 9. Relation to representation changes

AF3 projective row/column transformations preserve full-support existence. The parameters `(m,r,k)` are properties of a chosen APSQ hyperplane presentation and need not be invariant under every legal projective representation change.

That is an opportunity rather than a problem: a future polynomial representation algorithm may deliberately transform the augmented ternary matroid to reduce normal excess or enter a graphic/frame/bounded-width terminal, provided construction and witness transport are polynomially charged.

## 10. New frontier

Freeze the unresolved middle gate as

```text
R5_E9_AF3_PROJECTIVE_REPRESENTATION_OR_MIDDLE_EXCESS_GATE_V1
```

A universal PASS must either:

1. find in deterministic polynomial time a projectively equivalent representation whose AF3 residual has `r=O(log n)` or `m-r=O(log n)`; or
2. recognize another polynomial full-support class (graphic/cographic/frame/signed-graphic/bounded-width/etc.); or
3. provide a different global full-support constructor / cover certificate for the middle-excess residual.

No existence-only representation theorem is sufficient; representation discovery and witness reconstruction are charged.

## 11. Ceiling

```text
AF3 BASIS-CUBE NORMAL FORM
= PROVED

DIRECT ROUTER
= 2^r poly

DUAL SYNDROME ROUTER
= 3^(m-r) poly

COMBINED ROUTER
= min(2^r,3^(m-r)) poly

EXCESS 2 => SAT
= FALSE

PG15
= (m,r,k)=(11,4,7), SAT / FOUR WITNESSES

UNIVERSAL MIDDLE-EXCESS COVERAGE
= OPEN

E8_D1 = EMPTY
P_VS_NP = OPEN
```