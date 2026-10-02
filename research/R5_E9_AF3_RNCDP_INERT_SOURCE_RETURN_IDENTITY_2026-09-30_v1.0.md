# R5 E9 — AF3 RNCDP Inert Source-Return Identity

Date: 2026-09-30

Status:
`JANUS_EXACT_ANTI_LOOP_THEOREM__RNCDP_WITHOUT_REAL_APSQ_COMPRESSION_RETURNS_SOURCE_AF3__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_AFFINE_F3_NOWHERE_ZERO_EXACTONE_NORMAL_FORM_2026-09-30_v1.0.md`
- `research/R5_E9_AFFINE_F3_PARALLEL_SATURATION_QUOTIENT_2026-09-30_v1.0.md`
- `research/R5_E9_AF3_RESIDUAL_NORMAL_CODIMENSION_DP_ROUTER_2026-09-30_v1.0.md`
- `research/R5_E9_PALEY_ORBIT_AF3_LINEAR_EXCESS_BARRIER_2026-09-30_v1.0.md`

Scientific ceiling:

```text
THIS NOTE IDENTIFIES AN EXACT SOURCE-RETURN REGIME OF RNCDP.
IT DOES NOT PROVE THAT APSQ IS ALWAYS INERT.
IT DOES NOT PROVE THAT EVERY LARGE-EPSILON RESIDUAL RETURNS THE SOURCE.
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SOLVER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let

```text
A in F3^{m x n}
```

be a row-weight-three Exact-One source matrix for which the affine system

\[
Ar=\mathbf1
\]

is consistent. Choose one affine solution `c` and a full-column-rank matrix

\[
B\in F_3^{n\times d},
\qquad \operatorname{col}(B)=\ker(A).
\]

Then every affine solution is

\[
r=c+B\alpha,
\qquad \alpha\in F_3^d.
\]

The AF3 theorem says that Exact-One is SAT iff some such `r` is coordinatewise nonzero.

Assume the subsequent APSQ preprocessing is **coordinate-inert** in the following precise sense:

1. no coordinate becomes a constant and is deleted;
2. no two coordinate constraints are identified as duplicate projective hyperplanes;
3. no two-offset class produces a pin;
4. no three-offset class terminates UNSAT.

Thus every one of the original `n` coordinate constraints survives as one residual constraint.

## 2. RNCDP normal matrix is the kernel-basis matrix

Coordinate `i` imposes

\[
c_i+b_i\alpha\ne0,
\]

where `b_i` is row `i` of `B`. In RNCDP notation this is

\[
b_i\alpha\ne -c_i.
\]

Hence, under the coordinate-inert premise,

\[
\boxed{N=B,
\qquad b=-c.}
\]

Here `b` on the right is the RNCDP vector of forbidden offsets, not a kernel basis row.

Because `B` has full column rank `d`,

\[
\operatorname{rank}(N)=d.
\]

Therefore the RNCDP excess is

\[
\boxed{\epsilon=n-d.}
\]

By rank-nullity,

\[
n-d=\operatorname{rank}(A),
\]

so

\[
\boxed{\epsilon=\operatorname{rank}_{F3}(A).}
\]

This already explains why an APSQ-inert high-rank source can have linear RNCDP excess.

## 3. Left kernel of N is exactly the source row space

RNCDP computes a full-row-rank matrix

\[
H\in F_3^{\epsilon\times n}
\]

whose rows span the left kernel of `N`:

\[
\operatorname{row}(H)=\ker(N^T).
\]

Since `N=B` and `col(B)=ker(A)`,

\[
\ker(B^T)
=(\ker A)^\perp
=\operatorname{row}(A).
\]

Therefore

\[
\boxed{
\operatorname{row}(H)=\operatorname{row}(A).
}
\]

Both spaces have dimension `rank(A)=epsilon`. Hence there are full-row-rank row bases `A_0` of `A` and an invertible matrix `U` with

\[
H=U A_0.
\]

No semantic compression has occurred at the row-space level.

## 4. RNCDP two-choice syndrome is exactly the source AF3 problem

RNCDP introduces

\[
y=N\alpha=B\alpha
\]

and writes

\[
y=b+s,
\qquad s_i\in F_3^*=\{1,2\}.
\]

Since `b=-c`,

\[
s=y-b=B\alpha+c=r.
\]

Thus the RNCDP sign/two-choice vector `s` is literally the original affine source vector `r`.

The RNCDP syndrome equation is

\[
Hs=-Hb.
\]

With `b=-c`, this is

\[
Hs=Hc.
\]

Equivalently,

\[
H(s-c)=0.
\]

Because `ker(H)=col(B)=ker(A)`, this is equivalent to

\[
A(s-c)=0.
\]

Since `Ac=1`,

\[
\boxed{
Hs=-Hb,\ s\in(F_3^*)^n
\iff
As=\mathbf1,\ s\in(F_3^*)^n.
}
\]

By AF3, the right-hand side is exactly the original Exact-One decision problem.

### Theorem IRSR-1 — inert source return

If AF3 is followed by APSQ and APSQ leaves all original coordinate hyperplanes intact with no pin, deletion, or projective duplicate, then RNCDP's two-choice syndrome instance is coordinatewise identical, up to invertible row operations, to the original affine-nowhere-zero source instance.

Consequently RNCDP is an exact re-encoding rather than an algorithmic simplification in this regime.

## 5. Paley reconciliation

For the Paley-orbit AF3 family already proved in the repository:

```text
n = q L,
dim ker_F3(A)=q,
all coordinate normals projectively distinct,
APSQ pins = 0,
APSQ duplicate classes = 0.
```

Thus the coordinate-inert theorem applies and gives

\[
\epsilon=n-q=\operatorname{rank}_{F3}(A),
\]

exactly matching the independent Paley AF3 linear-excess theorem.

The Paley family is nevertheless polynomially solved by the existing graphic/gradient-kernel representation router. This is the intended reconciliation:

```text
RNCDP alone: source return / large epsilon;
representation router: polynomial terminal.
```

## 6. Why this matters for the universal architecture

The theorem closes the following anti-loop:

```text
AF3
-> APSQ does nothing substantive
-> build RNCDP syndrome matrix H
-> treat H as a new easier global object
```

When APSQ is coordinate-inert, `H` has exactly the source row space and the two-choice vector is exactly the original AF3 variable vector. Calling it a new syndrome problem does not constitute progress.

Therefore a universal polynomial route based on AF3/RNCDP must obtain progress from at least one genuine source of compression:

1. APSQ deletes/identifies coordinates or produces affine pins;
2. another exact polynomial representation router recognizes the residual;
3. a decomposition/contraction changes the semantic carrier with a strict polynomially bounded progress measure;
4. a new polynomial solver exploits source structure not erased by the row-space identity.

A scalar bound on `epsilon` is only one sufficient lane, not the missing universal theorem.

## 7. Updated live gate

The appropriate combined frontier is

```text
R5_E9_AF3_EXCESS_OR_REPRESENTATION_DICHOTOMY_GATE_V2
```

Required universal PASS:

For every linear-cubic source after the already proved terminal stack, construct in deterministic polynomial time at least one of:

```text
(A) genuine AF3/APSQ semantic compression leading to epsilon=O(log n);

(B) a coordinate-exact recognized polynomial representation/decomposition
    (graphic, cycle, TU, binet, regular, lift-contraction, or a proved extension);

(C) another exact contraction with a globally polynomial progress measure;

(D) a direct polynomial constructor/certificate on the residual source-return regime.
```

The theorem forbids counting the purely formal transformation `A -> H` as lane `(C)` when APSQ is inert.

## 8. Ceiling

```text
APSQ COORDINATE-INERT
=> N=B
= PROVED

LEFT KERNEL OF N
= row_F3(A)
= PROVED

RNCDP EXCESS
= rank_F3(A)
= PROVED IN THE INERT REGIME

RNCDP TWO-CHOICE VECTOR
= ORIGINAL AF3 SOURCE VECTOR
= PROVED

RNCDP SYNDROME SYSTEM
= ORIGINAL AF3 SYSTEM UP TO INVERTIBLE ROW OPERATIONS
= PROVED

PALEY LARGE-EPSILON BEHAVIOR
= EXPLAINED / RECONCILED

UNIVERSAL DICHOTOMY
= OPEN

UNIVERSAL POLYNOMIAL SOLVER
= NOT PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```