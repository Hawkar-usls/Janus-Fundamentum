# R5 E10Q — Rational-kernel alphabet terminal and source-face frontier

Date: 2026-10-02

Status: **NEW EXACT TERMINAL + NEGATIVE ROUTE RESULT; UNIVERSAL GATE OPEN**

Claim ceiling:

```text
P_VS_NP = OPEN
UNIVERSAL_POLYNOMIAL_ZERO_D_SOLVER = NOT_ESTABLISHED
SQUARE_LINEAR_CUBIC_NP_HARDNESS_BRIDGE = NOT_YET_ADMITTED
```

This note records an exact bounded-alphabet normal form over the rational kernel, a polynomial terminal when the rational nullity is logarithmic, an exact stable-set/source-face identity, exact PG15 controls, and a connected high-nullity counterfamily that blocks a false universalization of the kernel terminal.

The executable control is:

```text
experiments/r5_e10q_rational_kernel_source_face.py
```

---

## 1. Source class

Let

\[
A\in\{0,1\}^{n\times n}
\]

satisfy:

1. every row has weight 3;
2. every column has weight 3;
3. any two distinct columns overlap in at most one row.

Call this a **square linear-cubic Exact-One source**. The decision problem is whether

\[
\exists x\in\{0,1\}^n:\qquad Ax=\mathbf1.
\]

The associated column-intersection graph \(G_A\) has one vertex per source column and an edge between two columns when they meet in a source row.

Linearity and cubicity give the exact Gram identity

\[
\boxed{A^\top A=3I+\operatorname{Adj}(G_A).}
\]

Hence \(G_A\) is 6-regular and

\[
\lambda_{\min}(G_A)\ge -3.
\]

Moreover, stable sets of \(G_A\) are exactly collections of pairwise disjoint source columns. Since every selected column covers three source rows,

\[
\boxed{A\text{ SAT}\iff \alpha(G_A)=n/3.}
\]

---

## 2. Exact rational-kernel alphabet theorem

### Theorem E10Q.1

For every square cubic source \(A\),

\[
\boxed{
A\text{ SAT}
\iff
\ker_{\mathbb Q}(A)\cap\{-1,2\}^n\ne\varnothing.
}
\]

### Proof

If \(x\in\{0,1\}^n\) satisfies \(Ax=\mathbf1\), define

\[
y=3x-\mathbf1.
\]

Because each row of \(A\) has sum 3,

\[
A\mathbf1=3\mathbf1,
\]

so

\[
Ay=3Ax-A\mathbf1=3\mathbf1-3\mathbf1=0.
\]

Every coordinate of \(y\) is \(-1\) or \(2\).

Conversely, if \(y\in\ker_{\mathbb Q}(A)\cap\{-1,2\}^n\), set

\[
x=(y+\mathbf1)/3.
\]

Then \(x\in\{0,1\}^n\), and

\[
Ax=(Ay+A\mathbf1)/3=\mathbf1.
\]

QED.

---

## 3. Exact bounded-nullity algorithm

Let

\[
d=\dim_{\mathbb Q}\ker A.
\]

Compute a rational kernel basis

\[
B\in\mathbb Q^{n\times d}.
\]

Choose \(d\) coordinate rows of \(B\) forming an invertible \(d\times d\) submatrix. Any vector in \(\ker A\) is uniquely determined by its values on those coordinates. Therefore enumerate the \(2^d\) assignments of those coordinates from \(\{-1,2\}\), reconstruct the unique kernel vector, and accept precisely when every reconstructed coordinate lies in \(\{-1,2\}\).

This gives the exact algorithm

\[
\boxed{T(A)=O(2^d\operatorname{poly}(n)).}
\]

### Corollary E10Q.2

If

\[
d=O(\log n),
\]

then square linear-cubic Exact-One is solvable in polynomial time on that source.

This is a genuine polynomial terminal, not a universal theorem.

---

## 4. Spectral interpretation

From the Gram identity,

\[
(\operatorname{Adj}(G_A)+3I)v=A^\top Av.
\]

Over \(\mathbb R\),

\[
v^\top A^\top Av=\|Av\|^2,
\]

so

\[
\boxed{E_{-3}(G_A)=\ker_{\mathbb R}A.}
\]

Thus the rational-kernel terminal is equivalently an exact search for a two-valued vector in the \(-3\)-eigenspace:

\[
\boxed{
A\text{ SAT}
\iff
E_{-3}(G_A)\cap\{-1,2\}^n\ne\varnothing.
}
\]

The multiplicity of eigenvalue \(-3\) equals the real/rational nullity of \(A\).

---

## 5. Exact source face inside STAB

Let \(\operatorname{STAB}(G_A)\) be the stable-set polytope of \(G_A\).

Every source row corresponds to a triangle in \(G_A\). Hence, for every stable-set incidence vector \(z\),

\[
Az\le\mathbf1.
\]

Define

\[
F_A=\operatorname{STAB}(G_A)\cap\{z:Az=\mathbf1\}.
\]

### Theorem E10Q.3 — Source-face identity

\[
\boxed{
F_A=\operatorname{conv}\{x\in\{0,1\}^n:Ax=\mathbf1\}.
}
\]

In particular,

\[
\boxed{A\text{ SAT}\iff F_A\ne\varnothing.}
\]

### Proof

The inclusion from right to left is immediate: an Exact-One witness selects pairwise disjoint columns, so it is a stable-set vector and satisfies \(Ax=\mathbf1\).

For the other direction write

\[
z=\sum_S\lambda_S\chi^S\in\operatorname{STAB}(G_A),
\qquad \lambda_S\ge0,
\qquad \sum_S\lambda_S=1,
\]

where each \(S\) is stable. For every source row \(r\),

\[
(A\chi^S)_r\in\{0,1\}.
\]

If \(Az=\mathbf1\), then for each row

\[
1=\sum_S\lambda_S(A\chi^S)_r.
\]

A convex combination of numbers from \(\{0,1\}\) equals 1 only if every term with positive coefficient equals 1. Therefore every stable set in the support of the convex combination covers every source row exactly once. Each such \(\chi^S\) is an Exact-One witness.

QED.

---

## 6. Why source-aligned inequalities are the right certificates

Suppose

\[
a=A^\top\pi.
\]

For every Exact-One witness \(x\),

\[
a^\top x=\pi^\top Ax=\pi^\top\mathbf1.
\]

Therefore any valid stable-set inequality

\[
(A^\top\pi)^\top z\le b
\]

with

\[
b<\pi^\top\mathbf1
\]

is an immediate UNSAT certificate.

Equivalently, for a source-aligned indicator normal

\[
\mathbf1_U=A^\top\pi,
\]

we have, using \(A\mathbf1=3\mathbf1\),

\[
3\pi^\top\mathbf1
=
\mathbf1^\top A^\top\pi
=
|U|,
\]

so every Exact-One witness must satisfy

\[
\boxed{x(U)=|U|/3.}
\]

Hence

\[
\boxed{
\mathbf1_U\in\operatorname{row}_{\mathbb Q}(A)
\quad\text{and}\quad
\alpha(G_A[U])<|U|/3
\Longrightarrow
A\text{ UNSAT}.
}
\]

This is the corrected version of the earlier over-broad idea that an arbitrary valid STAB inequality cutting \(\tfrac13\mathbf1\) would certify UNSAT. It does not: a SAT source can have valid non-source-aligned cuts that exclude \(\tfrac13\mathbf1\).

---

## 7. Exact PG15 controls

### 7.1 Frozen PG15 SAT

The checker uses the previously frozen 15 triples:

```text
123, 1-10-11, 1-12-13, 2-9-11, 2-12-14,
3-4-7, 3-5-6, 4-9-13, 4-10-14, 5-8-13,
5-10-15, 6-8-14, 6-9-15, 7-8-15, 7-11-12.
```

Exact rational elimination gives

\[
\boxed{\operatorname{rank}_{\mathbb Q}A=11,\qquad d_{\mathbb Q}=4.}
\]

The \(2^4=16\) bounded-alphabet kernel assignments yield exactly four vectors in \(\{-1,2\}^{15}\), decoding to exactly four Exact-One witnesses.

Also

\[
\alpha(G_A)=5=n/3.
\]

### 7.2 Hostile PG15 UNSAT — canonical projective representative

A canonical representative matching the frozen projective signature is

```text
123, 145, 167, 2-8-10, 2-12-14,
3-9-10, 3-13-14, 4-8-12, 4-11-15, 5-8-13,
5-10-15, 6-9-15, 6-11-13, 7-9-14, 7-11-12.
```

The checker verifies exactly:

- square, row/column weight 3;
- linearity;
- each triple is a line of \(PG(3,2)\) under the nonzero 4-bit-vector labeling;
- the 15 selected lines split into three spreads;
- every projective hyperplane contains exactly three selected lines;
- \(\dim_{\mathbb F_2}\ker A=4\);
- \(\alpha(G_A)=4\);
- no Exact-One witness.

Rationally,

\[
\boxed{\operatorname{rank}_{\mathbb Q}A=13,\qquad d_{\mathbb Q}=2.}
\]

One rational kernel basis is

\[
\begin{aligned}
v_1={}&(1,-1,0,-1,0,0,-1,1,0,0,1,0,-1,1,0),\\
v_2={}&(3,-1,-2,-1,-2,-2,-1,0,1,1,0,1,2,0,1).
\end{aligned}
\]

The four assignments to two independent kernel coordinates produce no vector in \(\{-1,2\}^{15}\). Therefore the hostile control is rejected exactly by the rational-kernel terminal.

Important provenance note: this object is **not** the older `singular UNSAT` control used by `r5_e9_affine_f3_nowhere_zero_exactone_normal_form.py`. The two controls must not be conflated.

---

## 8. Negative theorem: connected sources can have linear rational nullity

The low-nullity terminal does not universalize by connectedness.

Take \(k\) disjoint copies of PG15 SAT and fix the exact witness

\[
S=\{3,11,13,14,15\}
\]

inside every copy.

Between adjacent blocks apply a 2-switch to two selected incidences

\[
(r_1,c_1),(r_2,c_2)
\mapsto
(r_1,c_2),(r_2,c_1).
\]

If \(x_{c_1}=x_{c_2}=1\), the fixed Exact-One witness survives the switch. The switch preserves every row and column sum. With the explicit ports in the checker it also preserves linearity and makes the total incidence support connected.

The matrix difference of one switch is supported on a 2x2 block

\[
\begin{pmatrix}
-1&1\\
1&-1
\end{pmatrix},
\]

which has rational rank 1. Therefore one switch can increase rank by at most one.

Starting from \(k\) PG15 SAT blocks,

\[
\operatorname{rank}\le 11k+(k-1)=12k-1,
\]

while the matrix has size \(15k\). Hence

\[
\boxed{d_{\mathbb Q}\ge 3k+1=\Omega(n).}
\]

The exact checker obtains equality for \(k=1,\ldots,6\):

```text
k : 1  2  3  4  5  6
n : 15 30 45 60 75 90
d : 4  7 10 13 16 19
```

Thus the route

```text
connected square linear-cubic source => d_Q = O(log n)
```

is **FALSIFIED**.

The rational-kernel method remains an exact polynomial terminal for low-nullity instances, but the universal branch must handle connected instances with \(d_{\mathbb Q}=\Theta(n)\).

---

## 9. Hardness bridge audit

A polynomial solver for the target source class implies \(P=NP\) only after NP-hardness of the **same restricted class** is established.

At this checkpoint, the previously stated compiler

```text
3SAT -> J(F) -> square linear-cubic Exact-One
```

is not admitted here because the current repository audit did not recover one proof object simultaneously establishing:

```text
square
row weight = 3
column weight = 3
linearity
polynomial size
SAT iff Exact-One SAT
```

The nearby external hardness landscape is strong but does not by itself close the intersection:

1. Perfect matching is NP-complete for **linear 3-uniform hypergraphs**. A source route appears in the proof chain `DEC(2,K3) -> PMlin(3)` in the hypergraph matching literature (see DOI `10.1016/j.ejc.2011.12.009`).
2. Perfect matching is NP-complete for **3-partite 3-regular 3-uniform hypergraphs**; a concise statement appears as Theorem 10 in Berczi--Bernath--Vizer, EGRES Quick-Proof 2015-04.
3. The literature also explicitly uses **3-bounded 1-common 3-dimensional matching**, where every element occurs in at most three triples and any two triples share at most one element, as an NP-hard source problem; this is already bounded + linear, but does not yet supply the exact degree-3 / square completion required here.

Therefore the honest hardness frontier is:

\[
\boxed{
\text{linear + degree}\le3
\quad\xrightarrow{\text{missing exact regularization}}\quad
\text{linear + degree}=3.
}
\]

The missing reduction must preserve perfect-cover satisfiability and linearity while completing all deficits to degree exactly three.

---

## 10. Current universal frontier

The exact funnel is now

\[
\boxed{
\text{square linear-cubic Exact-One}
\to
\begin{cases}
\text{perfect/balanced terminals},\\
\text{rational-kernel alphabet terminal } O(2^{d_{\mathbb Q}}\mathrm{poly}(n)),\\
\text{source-face / source-aligned obstruction terminals},\\
\text{high-nullity connected hard core}.
\end{cases}
}
\]

Two independent universal gates remain:

### Gate A — algorithmic

Handle the connected high-nullity hard core in polynomial time, or derive a polynomially recognizable source-aligned obstruction family that always fires on UNSAT.

### Gate B — hardness

Give an admitted polynomial reduction from a known NP-complete problem to the exact square linear-cubic source class, most narrowly by regularizing bounded linear 3DM while preserving perfect matching.

Only after **both** gates close may a polynomial target solver be promoted to a proof of \(P=NP\).

Until then:

\[
\boxed{P\stackrel?=NP\text{ remains OPEN}.}
\]
