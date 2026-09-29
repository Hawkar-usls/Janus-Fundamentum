# R5 E9 — EQ3 regularizer L1 private elimination returns the source core

Date: 2026-09-29

Status: `JANUS_DERIVED_EXACT_OBJECTIVE_QUOTIENT__PRIVATE_EQ3_FREEDOM_DOES_NOT_REMOVE_SOURCE_HARDNESS__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `research/R5_E9_INTEGER_LATTICE_L1_GRAVER_AUGMENTATION_GATE_2026-09-29_v1.0.md`

Scientific ceiling:

```text
THIS NOTE DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL SAT DECIDER.
IT EXACTLY ELIMINATES THE PRIVATE INTEGER DEGREE OF FREEDOM OF EACH FROZEN
EQ3 REGULARIZER GADGET FROM THE LIVE L1 OBJECTIVE.
THE RESULTING GLOBAL OPTIMIZATION IS AN EXACT SEPARABLE CONVEX OBJECTIVE ON
THE ORIGINAL CUBIC POSITIVE-1-IN-3 SOURCE VARIABLES.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Frozen EQ3 affine form

For one regularizer gadget the exact integer affine solution is

```text
x0=x1=x2=x9=q,
x3=x4=x5=1-r-q,
x6=x7=x8=r,
q,r in Z.
```

The three `q` terminals are the split source occurrences and `x9` is the fourth copy of `q`. The retained source clauses constrain only the terminal/source value `q`; `r` is private to the gadget.

The live L1 objective on all ten gadget coordinates is therefore

\[
F_G(q,r)
=4|2q-1|
+3|1-2r-2q|
+3|2r-1|.
\]

## 2. Exact elimination of r

Put

\[
t=2r-1.
\]

Then `t` ranges over the odd integers and

\[
|1-2r-2q|+|2r-1|=|t+2q|+|t|.
\]

For `q != 0`, the interval between `0` and `-2q` contains an odd integer, so the triangle inequality is attained and

\[
\min_{t\text{ odd}}\bigl(|t|+|t+2q|\bigr)=2|q|.
\]

For `q=0`, oddness forbids `t=0`, and the minimum is `2`, attained at `t=+/-1`.

Thus for every integer `q`,

\[
\boxed{
\min_{r\in\mathbb Z}
\left(|1-2r-2q|+|2r-1|\right)
=2\max(1,|q|).
}
\]

Define the exact private-eliminated gadget penalty

\[
\boxed{
\phi(q):=\min_{r\in\mathbb Z}F_G(q,r)
=4|2q-1|+6\max(1,|q|).
}
\]

Equivalently,

\[
\phi(q)=
\begin{cases}
14|q|+4,&q\le -1,\\
10,&q=0,1,\\
14q-4,&q\ge2.
\end{cases}
\]

A hinge representation is

\[
\boxed{
\phi(q)=10+8(-q)_+ +6(-q-1)_+ +14(q-1)_+.
}
\]

Hence `phi` is discrete convex and

\[
\boxed{
\phi(q)\ge10,
\qquad
\phi(q)=10\iff q\in\{0,1\}.
}
\]

## 3. Global exact objective quotient

Let a cubic Positive-1-in-3 source have variables `q_1,...,q_m` and incidence matrix `A_src`. Apply the frozen EQ3 regularizer independently to each source variable.

All private parameters `r_v` occur only inside their own gadgets. The retained source clauses impose exactly

\[
A_{src}q=\mathbf1.
\]

Therefore minimization of the regularized L1 objective separates over private coordinates:

\[
\boxed{
\min_{z:\,A_{reg}z=\mathbf1} F_{reg}(z)
=
\min_{q\in\mathbb Z^m:\,A_{src}q=\mathbf1}
\sum_{v=1}^m \phi(q_v).
}
\]

No approximation or projection is used: every integer regularized lattice point maps to its source vector `q`, and every integer source vector satisfying `A_src q=1` extends by independently choosing an integer minimizer `r_v` for each gadget.

## 4. Exact SAT threshold survives elimination

The regularized instance has `N=10m` variables. Since every `phi(q_v)>=10`,

\[
\sum_v\phi(q_v)\ge10m=N.
\]

Equality holds iff every source coordinate is Boolean. Consequently

\[
\boxed{
\min_{A_{reg}z=1}F_{reg}(z)=10m
\iff
\exists q\in\{0,1\}^m:A_{src}q=\mathbf1.
}
\]

Thus the exact L1 threshold on the linear-cubic hard image is precisely the original cubic Positive-1-in-3 decision problem after private elimination.

## 5. Algorithmic consequence

This closes the tempting shortcut

```text
EQ3 regularization introduces many private integer kernel coordinates
=> optimize them away
=> the remaining L1 problem becomes a flow/network/TU problem.
```

The first implication is valid; the second is false without a new theorem. Exact elimination returns the original source variables equipped with the explicit separable convex penalty `phi`.

This does **not** prove that SOURCE_TRADE_AUGMENT is hard or impossible. A genuinely global polynomial augmentation mechanism could still solve the resulting source optimization and would then solve the NP-complete source carrier, which is exactly the P-vs-NP-scale obligation.

The correct live target remains a global source-trade / crossing-penalty oracle, not exploitation of private regularizer freedom.

## 6. Checker

Executable regression:

`experiments/r5_e9_eq3_regularizer_l1_private_elimination.py`

It verifies the frozen gadget equations, the exact finite samples of the minimization identity, the closed form for `phi`, convex first differences, and the Boolean equality set `{0,1}`.

## 7. Ceiling

```text
EQ3 PRIVATE INTEGER PARAMETER r
= ELIMINATED EXACTLY

phi(q)
= 4|2q-1| + 6 max(1,|q|)

phi(q)=10
iff q in {0,1}

REGULARIZED GLOBAL L1 OPTIMUM
= min_{A_src q=1} sum_v phi(q_v)

PRIVATE-GADGET-FREEDOM UNIVERSAL SHORTCUT
= CLOSED

SOURCE_TRADE_AUGMENTATION
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= NOT PROVED

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
