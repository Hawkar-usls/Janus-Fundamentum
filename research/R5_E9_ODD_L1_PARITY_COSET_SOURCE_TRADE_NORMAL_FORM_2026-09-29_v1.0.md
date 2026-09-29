# R5 E9 — Odd-L1 parity-coset source-trade normal form

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_GLOBAL_NORMAL_FORM__SOURCE_TRADE_GATE__NO_D1_PROMOTION`

Parent:
- `research/R5_E9_INTEGER_LATTICE_L1_GRAVER_AUGMENTATION_GATE_2026-09-29_v1.0.md`

Scientific ceiling:

```text
THIS NOTE IS AN EXACT REPRESENTATION CHANGE FOR THE GLOBAL L1 FRONTIER.
IT DOES NOT CONSTRUCT THE MISSING POLYNOMIAL SOURCE-TRADE ORACLE.
IT DOES NOT PROVE P=NP.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Cubic source

Let

\[
A\in\{0,1\}^{n\times n}
\]

be square cubic: every row and every column contains exactly three ones.
The current global optimization frontier is

\[
\min\left\{F(z):Az=\mathbf1,\ z\in\mathbb Z^n\right\},
\qquad
F(z)=\sum_i|2z_i-1|.
\]

Exact-One SAT is equivalent to optimum `n`.

## 2. Odd-parity affine-coset bijection

Define

\[
y=2z-\mathbf1.
\]

Then `y` is coordinatewise odd. Since every row of `A` has sum three,

\[
A\mathbf1=3\mathbf1.
\]

Therefore

\[
Az=\mathbf1
\iff
A(2z-\mathbf1)=-\mathbf1
\iff
Ay=-\mathbf1.
\]

Conversely, if `y` is coordinatewise odd and `Ay=-1`, then

\[
z=(y+\mathbf1)/2\in\mathbb Z^n
\]

and

\[
Az=\frac{Ay+A\mathbf1}{2}
=\frac{-\mathbf1+3\mathbf1}{2}
=\mathbf1.
\]

Hence there is an exact bijection

\[
\boxed{
\{z\in\mathbb Z^n:Az=\mathbf1\}
\longleftrightarrow
\{y\in(2\mathbb Z+1)^n:Ay=-\mathbf1\}.
}
\]

Under it,

\[
\boxed{F(z)=\|y\|_1.}
\]

### Theorem OL1-1

\[
\boxed{
\text{Exact-One}(A)\text{ is SAT}
\iff
\min_{Ay=-\mathbf1,\ y\equiv\mathbf1\pmod2}\|y\|_1=n.
}
\]

Because an odd integer has absolute value at least one, equality holds iff
`y in {+1,-1}^n`.

Thus the Boolean target is exactly a minimum-L1 odd representative of a fixed integer affine coset.

## 3. Fixed total sum

Because every column of `A` also has sum three,

\[
\mathbf1^T A=3\mathbf1^T.
\]

For every feasible `y`,

\[
3\sum_i y_i
=\mathbf1^TAy
=-n.
\]

Therefore

\[
\boxed{\sum_i y_i=-n/3.}
\]

In particular integer-lattice feasibility itself implies `3|n`, and every Boolean target `y in {±1}^n` has exactly `n/3` positive coordinates and `2n/3` negative coordinates.

## 4. Defect mass

For odd `y_i`, define

\[
d_i(y)=\frac{|y_i|-1}{2}\in\mathbb Z_{\ge0}.
\]

Then

\[
\boxed{
D(y):=\sum_i d_i(y)
=\frac{\|y\|_1-n}{2}.
}
\]

Hence

```text
D(y)=0  <=> SAT witness,
D(y)>=1 <=> non-Boolean integer point.
```

The earlier exact gap-two theorem becomes the integral defect gap

\[
\boxed{\operatorname{OPT}_D=0\text{ or }\operatorname{OPT}_D\ge1.}
\]

## 5. Every feasible move is a balanced integer source trade

Let `y,y'` be two feasible odd points. Their difference is even, so

\[
y'=y+2g
\]

for a unique `g in Z^n`. Feasibility gives

\[
A(y+2g)=-\mathbf1=Ay,
\]

hence

\[
\boxed{Ag=0.}
\]

Column cubicity then forces

\[
3\sum_i g_i
=\mathbf1^TAg
=0,
\]

so

\[
\boxed{\sum_i g_i=0.}
\]

Thus every admissible move is a **balanced integer kernel trade**.

Conversely every integer `g` satisfying `Ag=0` preserves the odd affine coset under `y -> y+2g`.

### Theorem OL1-2 — source-trade equivalence

At a current feasible odd point `y`, the exact missing augmentation primitive is

\[
\boxed{
\text{find }g\in\mathbb Z^n
\text{ with }Ag=0,\ \sum_i g_i=0,
\ \|y+2g\|_1<\|y\|_1,
}
\]

or certify that no such trade exists.

The displayed zero-sum condition is redundant once `Ag=0` is known on a column-cubic matrix, but it exposes the combinatorial meaning: mass is redistributed, not created.

## 6. Relation to Graver augmentation

Any globally improving difference to a better feasible point is an integer source trade. Graver theory says that a nonoptimal point admits a conformal improving Graver component, and supplies polynomially many augmentation iterations **provided** a suitable improving/best component can be found efficiently.

This note removes two distractions from that gate:

1. parity maintenance is automatic by moving in steps `2g`;
2. the objective is exactly odd-coset L1 defect mass.

What remains open is algorithmic discovery of a guaranteed improving trade on the unrestricted connected square linear-cubic source without enumerating an exponential Graver basis.

## 7. Polynomial islands and the true residual

When the integer kernel is represented by a network/TU/graphic/binet structure already certified elsewhere in JANUS, the analogous signed trade search can be expressed by the corresponding polynomial flow/circuit machinery.

The universal carrier is broader. In particular the frozen EQ3 NP-hard image has exponentially large subdeterminants and linear row/column deletion distance to TU, so those islands cannot be assumed globally.

Therefore the live gate is not generic `compute Graver(A)` and not `matrix is nearly TU`; it is source-specific:

```text
R5_E9_LINEAR_CUBIC_SOURCE_TRADE_AUGMENTATION_GATE_V1
```

Required PASS:

```text
INPUT: connected square linear-cubic A and feasible odd y with Ay=-1.
OUTPUT, in deterministic polynomial time:
  either an integer g with Ag=0 and ||y+2g||_1 < ||y||_1,
  or a certificate that y globally minimizes ||.||_1 on the odd affine coset.
TOTAL: polynomial bit complexity and polynomial witness reconstruction.
```

## 8. Anti-loop warning

A rational or real improving direction in `ker(A)` is not enough. Scaling it to an integer vector can cross the L1 breakpoints and destroy improvement. Any rounding/scaling theorem must therefore prove an integer proximity/coefficient statement specific to this source class.

Likewise, assuming a negative circuit or Graver-best-step oracle for free simply renames the missing P-vs-NP-level primitive.

## 9. Ceiling

```text
ODD AFFINE COSET Ay=-1, y odd
= EXACTLY EQUIVALENT TO INTEGER Ax=1

L1 OBJECTIVE
= EXACTLY F(z)

SAT
= ODD-COSET L1 OPTIMUM n

EVERY FEASIBLE MOVE
= y -> y+2g WITH Ag=0

EVERY SOURCE TRADE
= ZERO-SUM AUTOMATICALLY

POLYNOMIAL SOURCE-TRADE AUGMENTATION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
