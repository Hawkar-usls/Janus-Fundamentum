# R5 E9 — Two-Edge Exact UNSAT Linear-Nullity Prime Tower

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_N_UNSAT_HOSTILE_FAMILY__RAW_NULLITY_CURRENCY_CLOSED__NO_D1_PROMOTION`

Scientific ceiling:

```text
THIS CONSTRUCTS AN INFINITE CONNECTED LINEAR-CUBIC EXACT-ONE UNSAT FAMILY
THAT IS 3-CUT-IRREDUCIBLE, UNBALANCED, AND HAS RATIONAL NULLITY OMEGA(n).
IT DOES NOT PROVIDE A UNIVERSAL POLYNOMIAL DECIDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

Parents:
- `research/R5_E9_SINGULAR_UNSAT_3CUT_IRREDUCIBLE_ODD_CYCLE_CONTROL_2026-09-28_v1.0.md`
- `research/R5_E9_TWO_EDGE_TWIST_3CUT_IRREDUCIBLE_LINEAR_NULLITY_FAMILY_2026-09-28_v1.0.md`
- `research/R5_E9_ONE_EDGE_TWIST_2LIFT_EXACT_SAT_CONTRACTION_2026-09-27_v1.0.md`

## 1. Frozen UNSAT seed

Let `A_0` be the frozen `15_3` matrix with rows

```text
(0,5,12),(1,7,9),(2,9,14),(3,10,11),(3,4,13),
(1,5,10),(6,7,14),(2,3,7),(1,4,8),(0,6,9),
(2,10,12),(5,11,13),(6,8,12),(0,8,13),(4,11,14).
```

The parent artifact proves:

```text
connected / linear / cubic,
UNSAT,
rank_Q(A_0)=14,
nu_Q(A_0)=1,
no nontrivial edge cut of size <=3,
unbalanced.
```

A rational right-kernel generator is

```text
g=(1,4,1,1,-2,-2,1,-2,-2,-2,-2,1,1,1,1).
```

An integer left-kernel vector is

```text
ell=(-8,4,-5,-11,1,16,-14,10,-20,1,-5,-8,13,7,19).
```

## 2. First exact two-edge lift

Choose the two nonincident incidences

```text
F_0={(0,12),(2,9)}.
```

Let `E_0` be their incidence matrix and

```text
S_0=A_0-2E_0.
```

Exact elimination gives

```text
nu_Q(S_0)=1
```

with signed-kernel vector

```text
z=(-7,-4,3,1,-2,2,-1,-4,6,8,2,-3,-5,1,5).
```

Form the two-edge-twist 2-lift

```text
A_1 = [[A_0-E_0, E_0],
       [E_0, A_0-E_0]].
```

The usual sum/difference basis gives

```text
nu_Q(A_1)=nu_Q(A_0)+nu_Q(S_0)=2.
```

### Exact SAT contraction criterion

For a general square cubic matrix `A` and two nonincident incidences
`(i1,j1),(i2,j2)`, let `E` mark those incidences and let

```text
Ahat=[[A-E,E],[E,A-E]].
```

If `(u,v)` is a Boolean Exact-One model of `Ahat`, put `h=u-v`. Then

```text
A h = 2(h_j1 e_i1 + h_j2 e_i2).
```

Because every column of `A` has sum three,

```text
3 sum(h) = 2(h_j1+h_j2).
```

Since `h_j1,h_j2 in {-1,0,1}`, the right side is one of `{-4,-2,0,2,4}`; the only multiple of three is zero. Hence

```text
h_j1+h_j2=0.
```

If there exists `y in ker(A^T)` with `y_i1 != y_i2`, a nonzero pair
`(h_j1,h_j2)=(1,-1)` or `(-1,1)` is impossible after left-multiplying by `y^T`.
Therefore

```text
h_j1=h_j2=0,
```

so `Au=Av=1`. Conversely every base model lifts diagonally. Thus under this
left-kernel separation condition

```text
Ahat SAT iff A SAT.
```

For `F_0`, `ell_0=-8 != -5=ell_2`, so `A_1` is UNSAT.

The existing two-edge-twist theorem also preserves 3-cut irreducibility because
`F_0` is nonincident.

The strong odd 3x3 cycle on rows `{1,6,9}` and columns `{6,7,9}` avoids `F_0`,
so it lifts to two copies; hence `A_1` is unbalanced.

## 3. Distinguished recursive pair on A_1

In `A_1` choose

```text
F_1={(0,5),(1,1)}.
```

This pair is nonincident and avoids the designated strong odd cycle.

Under the exact kernel decomposition

```text
ker(A_1) = {(x,x): x in ker(A_0)} direct_sum {(z,-z): z in ker(S_0)},
```

use the basis `(g,g),(z,-z)`. Evaluation at the two distinguished columns gives

```text
ev_5 = (-2, 2),
ev_1 = ( 4,-4) = -2 ev_5.
```

Hence the two coordinate functionals are linearly dependent on the full
2-dimensional `ker(A_1)`.

The symmetric left-kernel vector `(ell,ell)` satisfies

```text
(ell,ell)_0=-8 != 4=(ell,ell)_1,
```

so the exact SAT-contraction criterion applies to `F_1`.

## 4. Recursive tracked-kernel theorem

For `t>=1`, suppose `A_t` has a distinguished nonincident pair

```text
F_t={(i1,j1),(i2,j2)}
```

and a subspace

```text
W_t subset ker_Q(A_t)
```

of dimension `d_t` such that the coordinate functionals at `j1,j2` are linearly
dependent on `W_t` by rank at most one.

Put

```text
W_t^0={x in W_t: x_j1=x_j2=0}.
```

Because the two coordinate functionals have rank at most one,

```text
dim W_t^0 >= d_t-1.
```

Form the two-edge-twist lift `A_{t+1}` using `F_t`. Then

```text
(x,x) in ker(A_{t+1})        for every x in W_t,
(z,-z) in ker(A_{t+1})       for every z in W_t^0.
```

The symmetric and antisymmetric subspaces intersect trivially, so

```text
d_t+1 >= d_t + (d_t-1) = 2d_t-1.
```

Define `W_{t+1}` to be their direct sum.

Now define the next distinguished pair `F_{t+1}` to be the two **upper-right
crossed copies** of the incidences in `F_t`. These two incidences exist in the
lift. On the symmetric part of `W_{t+1}` their column evaluations are exactly
the old dependent evaluations. On the antisymmetric part they are both zero,
because that part came from `W_t^0`. Therefore the same rank-at-most-one
coordinate dependence holds on `W_{t+1}`.

If `y_t in ker(A_t^T)` separates the two distinguished rows, then

```text
(y_t,y_t) in ker(A_{t+1}^T)
```

separates the two upper-sheet rows of `F_{t+1}`. Hence the exact SAT-contraction
criterion is inherited at every level.

Nonincidence is inherited. Since the designated strong odd cycle avoids `F_t`,
it lifts positively to two copies; choose the upper copy as the next designated
cycle. Thus unbalancedness is inherited as well. The existing two-edge-twist
small-cut theorem preserves 3-cut irreducibility at every level.

## 5. Arbitrary-size lower bound

At level `t=1`, take

```text
W_1=ker(A_1),
d_1=2.
```

The recurrence gives

```text
d_t >= 2^(t-1)+1.
```

The variable count is

```text
n_t=30*2^(t-1).
```

Therefore

```text
boxed(nu_Q(A_t) >= d_t >= n_t/30 + 1).
```

Every `A_t` is simultaneously

```text
connected,
linear,
cubic / square,
UNSAT,
unbalanced,
3-cut-irreducible,
nu_Q(A_t)=Omega(n_t).
```

The construction and the distinguished pair at every level are explicit and
recursive.

## 6. Consequence

The proposed residual dichotomy

```text
3-cut-irreducible + unbalanced + large rational nullity => SAT
```

is false, even with linear nullity.

Together with the already-proved SAT two-edge-twist family, both SAT and UNSAT
occur in the same separator-resistant / unbalanced / linear-nullity regime.
Hence raw rational nullity cannot be the universal semantic currency for the
remaining NP-complete carrier.

Freeze:

```text
R5_E9_LARGE_NULLITY_PRIME_CORE_SAT_DICHOTOMY
= FALSIFIED BY ARBITRARY-SIZE UNSAT FAMILY.
```

## 7. New frontier

The universal solver must use a genuinely semantic/global mechanism that
separates SAT from UNSAT inside a regime where all of the following may hold
simultaneously:

```text
3-cut-irreducible,
unbalanced,
linear rational nullity,
strong odd cycles,
no low-nullity terminal.
```

The next admissible targets are therefore representation-changing/global:

1. exact polynomial correlation/contraction algebra not parameterized by raw
   nullity;
2. a polynomially discoverable global certificate separating the SAT and UNSAT
   prime towers;
3. a direct polynomial solver for the affine-parity plus cycle-2factor
   independence formulation.

## 8. Ceiling

```text
EXACT TWO-EDGE SAT CONTRACTION UNDER LEFT-KERNEL SEPARATION = PROVED
TRACKED KERNEL RECURRENCE d' >= 2d-1                         = PROVED
UNSAT PRESERVATION                                           = PROVED
3-CUT-IRREDUCIBILITY                                         = INHERITED FROM PROVED TWO-EDGE-TWIST THEOREM
UNBALANCEDNESS                                                = PERSISTENT STRONG ODD CYCLE
UNSAT PRIME NULLITY                                           >= n/30+1

RAW NULLITY AS UNIVERSAL RESIDUAL CURRENCY                    = CLOSED
UNIVERSAL POLYNOMIAL DECIDER                                  = OPEN
E8_D1                                                         = EMPTY
P_VS_NP                                                       = OPEN
```