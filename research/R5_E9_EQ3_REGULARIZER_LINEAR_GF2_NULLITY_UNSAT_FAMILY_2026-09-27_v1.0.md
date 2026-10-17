# R5 E9 — EQ3 Regularizer Linear-GF2-Nullity UNSAT Family

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_INFINITE_COUNTERFAMILY__RAW_GF2_NULLITY_NOT_A_SAT_OR_PROGRESS_MEASURE`

Parents:
- `R5_E9_LINEAR_CUBIC_EQ3_REGULARIZATION_UNIVERSALITY_2026-09-27_v1.0.md`
- `R5_E9_SINGULAR_UNSAT_RANK14_COUNTERCONTROL_2026-09-27_v1.0.md`

Checker:
`experiments/r5_e9_eq3_regularizer_linear_nullity_unsat_family.py`

Scientific ceiling:

```text
THIS IS AN ANTI-LOOP THEOREM.
IT DOES NOT SUPPLY A POLYNOMIAL SAT DECIDER.
P_VS_NP = OPEN.
E8_D1 = EMPTY.
```

## 1. The existing exact EQ3 regularizer

The companion universality theorem uses the 10-variable, 9-clause Positive-1-in-3 gadget

```text
(2,5,6)
(1,4,7)
(5,7,9)
(0,3,7)
(4,6,9)
(2,4,8)
(3,8,9)
(0,5,8)
(1,3,6)
```

with terminals `0,1,2` and auxiliaries `3,...,9`.

Over Boolean Exact-One semantics its terminal projection is exactly

```text
EQ3 = {000,111}.
```

Every terminal has internal gadget degree two; every auxiliary has degree three.  After occurrence splitting and reconnecting one old clause occurrence to every terminal, the output is again square, cubic and linear.  Satisfiability and witnesses are preserved exactly under terminal collapse.

## 2. A terminal-zero binary kernel mode

Now view the gadget incidence matrix over `F_2` and put

```text
g = (0,0,0,1,1,1,1,1,1,0).
```

Thus

```text
supp(g) = {3,4,5,6,7,8}.
```

Every one of the nine gadget clauses meets this support in exactly zero or two positions.  Directly, the intersections have sizes

```text
2,2,2,2,2,2,2,2,2.
```

Hence

```text
A_gadget g = 0  (mod 2).
```

Moreover the three terminal coordinates of `g` are zero.  Therefore, when this gadget is attached to an arbitrary source instance, the same vector extended by zero outside this gadget remains a kernel vector of the full output incidence matrix: every external/source clause touches the gadget only through a terminal and therefore sees zero from `g`.

This is an exact local **gauge mode** of the binary parity representation.  It changes only auxiliary parity coordinates and carries no source-variable terminal signal.

For completeness, exact GF(2) elimination on the 9x10 gadget matrix gives

```text
rank_F2 = 7,
nullity_F2 = 3.
```

The theorem below needs only the one explicit terminal-zero vector `g`.

## 3. One independent gauge mode per source variable

Let `Phi` be any cubic Positive-1-in-3 instance with `N` source variables, and let `R(Phi)` be its output under the exact EQ3 regularizer.

There is one disjoint gadget for each source variable.  Let `g_v` denote the copy of `g` supported on the auxiliaries of the gadget belonging to source variable `v`.

By Section 2,

```text
g_v in ker_F2 A(R(Phi))
```

for every source variable `v`.

The supports of the vectors `g_v` are pairwise disjoint and nonempty.  Hence the `N` vectors are linearly independent over `F_2`.  Therefore

```text
nullity_F2 A(R(Phi)) >= N.
```

The regularizer creates exactly ten output variables per source variable, so if

```text
n' = |V(R(Phi))| = 10 N,
```

then

```text
boxed(nullity_F2 A(R(Phi)) >= n'/10).
```

Thus a linear-size binary kernel can arise purely from locally supported auxiliary gauge freedom, independently of the source SAT status.

## 4. Explicit connected linear-cubic UNSAT seed

Use the frozen 15-variable source from

`R5_E9_SINGULAR_UNSAT_RANK14_COUNTERCONTROL_2026-09-27_v1.0.md`.

It is a connected linear cubic Positive-1-in-3 carrier with normalized rows

```text
{0,5,12}
{1,7,9}
{2,9,14}
{3,10,11}
{3,4,13}
{1,5,10}
{6,7,14}
{2,3,7}
{1,4,8}
{0,6,9}
{2,10,12}
{5,11,13}
{6,8,12}
{0,8,13}
{4,11,14}
```

and it is Exact-One UNSAT by the exact rational-kernel proof in that artifact.

Call this seed `Phi_0` and define recursively

```text
Phi_(t+1) = R(Phi_t).
```

## 5. Preservation under iteration

The exact regularizer theorem applies to every cubic source, including each `Phi_t`.

### Exact satisfiability

For every `t`,

```text
Phi_(t+1) is SAT iff Phi_t is SAT.
```

Since `Phi_0` is UNSAT,

```text
Phi_t is UNSAT for every t >= 0.
```

### Cubic / square / linear

The companion theorem proves that occurrence splitting plus the gadget preserves:

```text
3-uniform,
3-regular,
square incidence,
pairwise linearity.
```

### Connectedness

Each variable gadget is connected and contains all three terminal copies of that source variable.  Contract every gadget back to its source variable.  The retained old-clause incidences then recover the source Levi graph.  A disconnected output would contract to a disconnected source graph.  Therefore connectedness of `Phi_t` implies connectedness of `Phi_(t+1)`.

Hence every member of the recursive family is a connected linear cubic carrier.

## 6. Linear binary nullity on every nontrivial level

If `n_t=|V(Phi_t)|`, then

```text
n_0 = 15,
n_(t+1) = 10 n_t,
```

so

```text
n_t = 15 * 10^t.
```

At level `t+1`, Section 3 gives one independent terminal-zero gauge vector for each of the `n_t` source variables.  Therefore

```text
nullity_F2 A(Phi_(t+1)) >= n_t = n_(t+1)/10.
```

Equivalently, for every `t>=1`,

```text
boxed(
  Phi_t is connected + linear + cubic + UNSAT,
  nullity_F2 A(Phi_t) >= n_t/10
).
```

This is an arbitrary-size theorem, not a finite-regression extrapolation.

## 7. Consequence for the universal solver

The following implication is false even inside the exact NP-complete JANUS carrier:

```text
large / linear binary nullity
=> SAT,
=> easy witness,
or => genuine global semantic freedom.
```

The regularizer can manufacture `Omega(n)` binary kernel dimension from local auxiliary gauge modes while preserving an UNSAT source exactly.

Therefore raw

```text
nu_F2(A)
```

is forbidden as a universal progress measure, SAT criterion, or evidence that the affine-cycle residual is globally easy.

Any future dimension-based route must first identify and quotient a **proved semantically neutral subspace**, with polynomial construction and exact witness reconstruction.  Merely dividing by all small-support kernel vectors is not universal either: the existing high-girth satisfiable controls prove that some satisfiable carriers have no bounded-support nonzero kernel vectors at all.

Thus the useful target is not

```text
HIGH NULLITY -> SAT,
```

but

```text
construct an exact polynomial semantic quotient
that removes certified local/decomposition gauge modes
without erasing source witness information,
then solve the remaining global affine-cycle coupling.
```

## 8. Harries correction

The older Harries nullity-amplifying family has

```text
n_t = 35 * 2^t.
```

Since a cubic Exact-One witness necessarily has size `n_t/3`, and `3` never divides `35*2^t`, every such member is automatically Exact-One UNSAT.  It remains a valid structural/high-nullity stress family, but it must not be cited as a SAT-side high-nullity obstruction.

## 9. Public-literature anti-loop

Equality gadgets for Positive 1-in-3 SAT and algebraic/kernel formulations of Positive 1-in-3 SAT are known techniques.  This artifact claims no novelty for equality gadgets, Gaussian elimination, or the term `kernel` separately.

The new content used by JANUS is the exact consequence of its already-materialized regularizer: a terminal-zero local kernel mode per source variable, and the resulting recursively regularized connected linear-cubic UNSAT family with linear `F_2` nullity.

## 10. Verdict

```text
EQ3 TERMINAL-ZERO GAUGE VECTOR
= PROVED

ONE INDEPENDENT GAUGE MODE PER SOURCE VARIABLE
= PROVED

ITERATED CONNECTED LINEAR-CUBIC UNSAT FAMILY
= PROVED

n_t
= 15 * 10^t

nullity_F2(A_t)
>= n_t/10  for t>=1

RAW GF2 NULLITY AS UNIVERSAL SAT / PROGRESS MEASURE
= FALSIFIED

NEXT
= SEMANTIC_GAUGE_QUOTIENT_OR_GLOBAL_AFFINE_CYCLE_SOLVER

UNIVERSAL POLYNOMIAL SAT DECIDER
= NOT YET PROVED

E8_D1 = EMPTY
P_VS_NP = OPEN
```
