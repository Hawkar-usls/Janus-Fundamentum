# R5 E9 — Continuous L1 barycenter and exact crossing-penalty barrier

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_CONTINUOUS_RELAXATION_COLLAPSE__CROSSING_PENALTY_GATE__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_ODD_L1_PARITY_COSET_SOURCE_TRADE_NORMAL_FORM_2026-09-29_v1.0.md`
- `research/R5_E9_INTEGER_LATTICE_NAE_DEFECT_FLOW_POSITIVE_LAYER_BARRIER_2026-09-29_v1.0.md`

Checker:
- `experiments/r5_e9_continuous_l1_barycenter_crossing_penalty.py`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE THE MISSING POLYNOMIAL SOURCE-TRADE ORACLE.
IT PROVES THAT THE REAL L1 RELAXATION IS UNIVERSALLY TRIVIAL ON THE
SQUARE CUBIC SOURCE AND ISOLATES THE EXACT DISCRETE CROSSING PENALTY.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let

\[
A\in\{0,1\}^{n\times n}
\]

be square cubic: every row and every column contains exactly three ones.
The odd-coset form is

\[
Ay=-\mathbf1,
\qquad
y\in(2\mathbb Z+1)^n,
\]

with objective `||y||_1`. Exact-One SAT is equivalent to odd-lattice optimum `n`.

## 2. The real L1 relaxation has the same optimum for every cubic source

Because every column has sum three,

\[
\mathbf1^TA=3\mathbf1^T.
\]

Hence every real feasible `y` satisfies

\[
3\mathbf1^Ty
=\mathbf1^TAy
=-n,
\]

so

\[
\boxed{\mathbf1^Ty=-n/3.}
\]

Therefore by the triangle inequality

\[
\|y\|_1\ge |\mathbf1^Ty|=n/3.
\]

On the other hand row cubicity gives `A1=3 1`, so

\[
\bar y=-\frac13\mathbf1
\]

is feasible and has `||bar y||_1=n/3`.

### Theorem CL1-1 — universal real optimum

For every square row/column-cubic source,

\[
\boxed{
\min\{\|y\|_1:Ay=-\mathbf1,\ y\in\mathbb R^n\}=n/3.
}
\]

Thus the continuous optimum is independent of SAT/UNSAT and is always attained by the same barycenter `-1/3 * 1`.

Every odd feasible point has `||y||_1>=n`, hence the continuous-to-odd integrality gap is at least a factor three even on SAT instances.

## 3. No odd feasible point is a continuous L1 optimum

Let `y` be odd feasible and put

\[
s=\operatorname{sign}(y)\in\{\pm1\}^n.
\]

Since no coordinate of `y` is zero, `s` is the unique subgradient of `||.||_1` at `y`.
A feasible point is a global real L1 minimizer only if

\[
s\in\operatorname{row}(A)=\operatorname{im}(A^T).
\]

But this cannot happen.
Suppose `s=A^T\lambda`. Then

\[
\|y\|_1=s^Ty
=\lambda^TAy
=-\lambda^T\mathbf1,
\]

while

\[
\mathbf1^Ts
=\lambda^TA\mathbf1
=3\lambda^T\mathbf1
=-3\|y\|_1.
\]

The left-hand side has absolute value at most `n`, whereas oddness gives `||y||_1>=n`, so the right-hand side has absolute value at least `3n`. Contradiction.

### Corollary CL1-2

For every odd feasible source point,

\[
\boxed{s\notin\operatorname{row}(A).}
\]

Hence every odd feasible point admits a strict **real** L1 descent direction in `ker_R(A)`.

This is a structural firewall: continuous optimality can never certify an odd-lattice optimum on this carrier.

## 4. Exact integer crossing penalty

Fix odd feasible `y`, write

\[
s_i=\operatorname{sign}(y_i),
\qquad a_i=|y_i|,
\]

and take any integer source trade

\[
g\in\ker_{\mathbb Z}(A).
\]

Since

\[
y_i+2g_i=s_i(a_i+2s_i g_i),
\]

and for every real `r`, `|r|=r+2 max(0,-r)`, coordinatewise

\[
|y_i+2g_i|-|y_i|
=2s_i g_i
+2\max(0,-a_i-2s_i g_i).
\]

Summing gives the exact identity

\[
\boxed{
\frac{\|y+2g\|_1-\|y\|_1}{2}
=s^Tg+P_y(g),
}
\]

where

\[
\boxed{
P_y(g):=\sum_i\max(0,-|y_i|-2s_i g_i)\ge0.
}
\]

`P_y(g)` is exactly the penalty for coordinates whose integer step crosses the zero hyperplane far enough to reverse sign.

### Corollary CL1-3 — no-crossing subproblem

Let

\[
d_i=(|y_i|-1)/2.
\]

The step has zero crossing penalty iff

\[
\boxed{s_i g_i\ge-d_i\quad\forall i.}
\]

On that region improvement is exactly the linear condition

\[
\boxed{s^Tg<0.}
\]

The universal difficulty is therefore not finding a real negative direction; one always exists. It is finding an **integer** kernel direction whose linear gain survives the crossing penalty.

## 5. Why polynomial LP circuit walks do not close the integer gate

Recent circuit-walk results show that suitable improving circuit walks for linear programming can be constructed in polynomial time, while the analogous integer/Graver problem does not inherit that conclusion in general.

The present source theorem explains the mismatch concretely:

```text
REAL L1 TARGET
= fixed barycenter -1/3 * 1
= always value n/3

ODD INTEGER TARGET
= source-dependent lattice point
= value >= n

MISSING INFORMATION
= discrete crossing / congruence coupling
```

Therefore importing a polynomial continuous circuit-descent routine cannot establish the required integer SOURCE_TRADE_AUGMENT theorem.

## 6. Frozen hostile control

On the frozen connected rank-14 linear-cubic source from the NAE-defect-flow note,

```text
z0=(-1,1,0,1,-1,1,2,0,0,-1,1,1,1,-1,1),
y0=2z0-1,
||y0||_1=25,
```

while the real barycenter has L1 value `5`.

The primitive kernel generator

```text
v=(-4,2,-1,2,-4,2,5,-1,-1,-4,2,2,2,-4,2)
```

satisfies `Av=0`. The checker verifies the crossing identity exactly for several integer multiples of `v`.

It also verifies by exact rational elimination that `sign(y0)` is not in the rowspace, as required by CL1-2.

## 7. Sharpened live gate

Freeze the subgate

```text
R5_E9_LINEAR_CUBIC_CROSSING_PENALTY_TRADE_GATE_V1
```

Required PASS:

```text
INPUT:
  square connected linear-cubic A,
  odd feasible y with Ay=-1.

OUTPUT in deterministic polynomial time:
  either g in ker_Z(A) with
      s^T g + P_y(g) < 0,
  or a certificate that no such integer trade exists.

TOTAL:
  polynomial bit complexity,
  polynomially many augmentation steps,
  exact witness reconstruction.
```

Forbidden shortcuts:
- continuous/LP descent without an integer crossing theorem;
- scaling a rational direction and ignoring zero crossings;
- bounded primitive coefficients (already falsified exponentially);
- enumerating the Graver basis;
- assuming a best-Graver-step oracle.

## 8. Ceiling

```text
REAL L1 OPTIMUM FOR EVERY CUBIC SOURCE
= n/3

CANONICAL REAL OPTIMIZER
= -1/3 * 1

ODD FEASIBLE L1 LOWER BOUND
= n

ODD FEASIBLE CONTINUOUS-OPTIMALITY CERTIFICATE
= IMPOSSIBLE

EXACT INTEGER OBJECTIVE CHANGE
= 2 * (linear gain + crossing penalty)

REAL NEGATIVE DIRECTION
= ALWAYS EXISTS AT EVERY ODD FEASIBLE POINT

INTEGER IMPROVING TRADE
= OPEN / DISCRETE CROSSING PROBLEM

SOURCE_TRADE_AUGMENT
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
