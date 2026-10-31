# R5 E9 — Prime-Tower Projective Escape-Radius Recurrence

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_SIZE_LINEAR_GEOMETRIC_ESCAPE_RADIUS_BARRIER__SUBLINEAR_ALL_CHAMBER_AUGMENTATION_FALSIFIED__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_EDGE_EXACT_UNSAT_LINEAR_NULLITY_PRIME_TOWER_2026-09-28_v1.0.md`
- `research/R5_E9_PROJECTIVE_TOPE_BOUNDED_AUGMENTATION_AND_PRIME_TOWER_STRESS_2026-09-28_v1.0.md`

Finite checker:
- `experiments/r5_e9_prime_tower_geometric_tope_radius_stress.py`
- `experiments/r5_e9_prime_tower_projective_escape_radius_recurrence.py`

Scientific ceiling:

```text
THE SPECIAL RECURSIVE TWO-EDGE PRIME TOWER HAS AN EXACT FULL-KERNEL
RECURSION, AN EXACT TOPE-PAIR COMPOSITION LAW, AND AN EXPLICIT TRAP WHOSE
PROJECTIVE CHAMBER ESCAPE RADIUS IS

    r_t = (2/15) n_t + 1.

THEREFORE NO UNIVERSAL o(n) GEOMETRIC ESCAPE-RADIUS GUARANTEE CAN HOLD FOR
EVERY CHAMBER OF THE SOURCE-GENERATED RATIONAL-KERNEL ARRANGEMENTS.

THIS DOES NOT RULE OUT A POLYNOMIAL ALGORITHM THAT CHOOSES SPECIAL STARTING
CHAMBERS, USES NONLOCAL OPTIMIZATION, OR AVOIDS NEIGHBORHOOD DESCENT.

E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Recursive carrier and notation

Start at the frozen `n_1=30` member `A_1` of the exact-UNSAT two-edge prime
tower.  Its rational right kernel has dimension two and basis

```text
(g,g), (z,-z),
```

with the frozen vectors `g,z` from the parent artifact.

Use the distinguished nonincident pair

```text
F_1={(i_1,j_1),(i_2,j_2)}={(0,5),(1,1)}.
```

For each stage write

```text
K_t = ker_Q(A_t),
L_t = ker_Q(A_t^T),
d_t = dim K_t.
```

Let

```text
f_t: K_t -> Q,
f_t(x)=x_(j_1)
```

for the first distinguished column at that stage.  The second distinguished
column functional is a nonzero scalar multiple of `f_t`.

The next distinguished pair consists of the two upper-right crossed copies of
`F_t`, exactly as in the parent prime-tower construction.

## 2. Base right-evaluation rank is exactly one

On `K_1`, with basis `(g,g),(z,-z)`, the two distinguished column evaluations
are

```text
ev_5=(-2,2),
ev_1=(4,-4)=-2 ev_5.
```

Hence

```text
rank(ev_5,ev_1 on K_1)=1,
```

and `f_1` is nonzero.

Define

```text
K_t^0 = ker(f_t).
```

Because the second distinguished evaluation is a nonzero multiple of `f_t`,

```text
K_t^0
= {x in K_t : x_(j_1)=x_(j_2)=0}.
```

Whenever `f_t` has rank one,

```text
dim K_t^0 = d_t-1.
```

## 3. Base left-evaluation rank is exactly two

The frozen exact left-kernel basis for `A_1` gives the two distinguished row
signatures

```text
row i_1=0 : (23/6,-11/6),
row i_2=1 : (17/6, -5/6).
```

Their determinant is

```text
(23*(-5)-17*(-11))/36
=72/36
=2 != 0.
```

Therefore the row-evaluation map

```text
rho_1 : L_1 -> Q^2,
y |-> (y_(i_1),y_(i_2))
```

has rank two.

This strengthens the earlier left-kernel separation condition `y_i1 != y_i2`:
here the two row coordinates are fully independent on the left kernel.

## 4. Exact signed-block kernel theorem

At an arbitrary stage assume:

```text
rank(f_t, second distinguished column evaluation)=1 and nonzero,
rank(rho_t)=2.
```

Let

```text
E_t=e_(i_1)e_(j_1)^T + e_(i_2)e_(j_2)^T,
S_t=A_t-2E_t.
```

### Theorem PER-1

\[
\boxed{\ker_Q(S_t)=K_t^0.}
\]

### Proof

Take `x in ker(S_t)`. Then

```text
A_t x
=2(x_(j_1)e_(i_1)+x_(j_2)e_(i_2)).
```

For every `y in L_t`, left multiplication gives

```text
0
=y^T A_t x
=2(y_(i_1)x_(j_1)+y_(i_2)x_(j_2)).
```

Since `rho_t(L_t)=Q^2`, the vector

```text
(x_(j_1),x_(j_2))
```

is orthogonal to all of `Q^2` and must be zero.  Hence `A_t x=0`, so
`x in K_t`, and both distinguished coordinates vanish. Thus

```text
x in K_t^0.
```

Conversely every `x in K_t^0` satisfies both `A_t x=0` and `E_t x=0`, so
`S_t x=0`. QED.

Therefore

```text
nu_Q(S_t)=d_t-1.
```

This closes the exact-rank gap that the earlier lower-bound prime-tower note
left open.

## 5. Exact full-kernel lift recursion

The two-edge 2-lift is block-diagonalized by the symmetric/antisymmetric change
of basis:

```text
ker(A_(t+1))
=
sym(ker A_t) direct_sum asym(ker S_t).
```

By PER-1,

\[
\boxed{
K_{t+1}
=
\operatorname{sym}(K_t)
\oplus
\operatorname{asym}(K_t^0).
}
\]

Hence

```text
d_(t+1)=d_t+(d_t-1)=2d_t-1.
```

With `d_1=2`,

\[
\boxed{d_t=2^{t-1}+1.}
\]

Since

```text
n_t=30*2^(t-1),
```

this special tower has the exact nullity law

\[
\boxed{\nu_Q(A_t)=n_t/30+1.}
\]

not merely the previous lower bound.

## 6. The two rank conditions persist

### Right side

The next distinguished columns are the second-sheet crossed copies of the old
ones. On the symmetric summand their evaluations are the old two dependent
functionals. On the antisymmetric summand from `K_t^0` both are zero.
Therefore their rank remains exactly one and the first functional remains
nonzero.

### Left side

The left kernel has the analogous exact block decomposition. Regardless of the
antisymmetric summand, the symmetric copy

```text
sym(L_t) subseteq L_(t+1)
```

preserves the old evaluations at the two upper-sheet distinguished rows.
Because `rho_t` already has rank two, `rho_(t+1)` has rank at least two and at
most two, hence exactly two.

Thus PER-1 and the exact full-kernel recursion hold at every level by induction.

## 7. Exact tope-pair composition

A child kernel vector has the unique form

```text
(u+v, u-v),
u in K_t,
v in K_t^0.
```

Put

```text
y^+=u+v,
y^-=u-v.
```

Then `y^+,y^- in K_t` and

```text
f_t(y^+)=f_t(y^-)
```

because `f_t(v)=0`.

Conversely, if two parent kernel vectors satisfy

```text
f_t(y^+)=f_t(y^-),
```

then

```text
u=(y^++y^-)/2 in K_t,
v=(y^+-y^-)/2 in K_t^0,
```

and they produce a child kernel vector.

For **tope sign patterns**, exact equality of the two nonzero distinguished
values is equivalent to equality of their signs after harmless positive
rescaling of one parent vector. Positive scaling does not change its chamber.

Therefore:

### Theorem PER-2 — tope composition

The full-support projective topes of `A_(t+1)` are exactly the ordered pairs

```text
(T^+,T^-)
```

of parent topes having the same sign at the distinguished coordinate `j_1`.

Their positive-coordinate objective is additive:

\[
\boxed{p_{t+1}(T^+,T^-)=p_t(T^+)+p_t(T^-).}
\]

No child topes are omitted because the full kernel equality was proved in
Sections 4–6.

## 8. Exact projective-class splitting

View every original coordinate `i` as a nonzero linear functional

```text
ell_i : K_t -> Q.
```

Parallel/proportional functionals define one projective hyperplane class.

On

```text
K_(t+1)=K_t direct_sum K_t^0
```

in `(u,v)` coordinates, the two lifted copies are

```text
ell_i^+(u,v)=ell_i(u)+ell_i(v),
ell_i^-(u,v)=ell_i(u)-ell_i(v).
```

Equivalently their functional pairs are

```text
(ell_i, +ell_i|K_t^0),
(ell_i, -ell_i|K_t^0).
```

Two child functionals descending from different parent projective classes
cannot become proportional: restriction to the first `K_t` component would
already make their parent functionals proportional.

For one parent class, its `+` and `-` child copies coincide projectively iff

```text
ell_i|K_t^0=0.
```

Since `K_t^0=ker f_t` has codimension one, this happens iff

```text
ell_i in span(f_t),
```

namely iff the parent class is exactly the distinguished projective class.

Thus:

### Theorem PER-3

Every parent projective hyperplane class splits into two child classes except
exactly the distinguished class, which remains one class.

If `m_t` is the number of parent projective classes,

```text
m_(t+1)=2m_t-1.
```

The finite base has `m_1=12`, so

\[
\boxed{m_t=11\cdot2^{t-1}+1.}
\]

## 9. Exact chamber-distance composition

Tope graphs of realizable oriented matroids are partial cubes, so projective
chamber distance is Hamming distance on the simplified projective signs.

Let `T_t` be a parent trap and let `e_*` be its distinguished projective class.
For a child tope `(U,V)` with the required common distinguished sign,
PER-3 gives

\[
\boxed{
d_{t+1}((T_t,T_t),(U,V))
=
d_t(T_t,U)+d_t(T_t,V)-\delta,
}
\]

where

```text
delta=1  if U,V both flip the distinguished class relative to T_t,
delta=0  otherwise.
```

The subtraction occurs because the parent distance sum counts that class twice
but the child arrangement contains only one unsplit copy of it.

## 10. Exact base trap profile

The finite rank-two checker exhausts all 24 topes of `A_1`.
Choose the frozen radius-five trap `T_1` with

```text
p(T_1)=15=n_1/2,
distinguished sign = -.
```

The complete objective/sign profile is:

```text
distinguished sign - : p in {15,16,17,18},
distinguished sign + : p in {12,13,14,15}.
```

Therefore

```text
sign - => p >= 15,
sign + => p <= 15.
```

Moreover the minimum projective distance from `T_1` to **any** `+` tope is

```text
r_1=5,
```

and this distance is attained by a `+` tope with

```text
p=14<15.
```

These are exact finite base facts, not asymptotic assumptions.

## 11. Sign/objective separation is inherited

Assume at stage `t` the trap `T_t` has distinguished sign `-` and objective

```text
P_t=p(T_t),
```

with

```text
- branch => p >= P_t,
+ branch => p <= P_t.
```

Define the child trap

```text
T_(t+1)=(T_t,T_t).
```

By PER-2, a child `-` tope is a pair of parent `-` topes, hence

```text
p >= P_t+P_t=2P_t.
```

A child `+` tope is a pair of parent `+` topes, hence

```text
p <= 2P_t.
```

So the separation is preserved and

```text
P_(t+1)=2P_t.
```

With `P_1=15`,

\[
\boxed{P_t=15\cdot2^{t-1}=n_t/2.}
\]

In particular **every** tope with objective strictly below the trap must lie in
the opposite distinguished-sign branch.

## 12. Linear escape-radius recurrence

Let

```text
r_t
=
minimum projective distance from T_t to any + tope.
```

At the base `r_1=5`, and a minimizing `+` tope already has lower objective.

Every child `+` tope is a pair `(U,V)` of parent `+` topes. Therefore

```text
d_t(T_t,U) >= r_t,
d_t(T_t,V) >= r_t.
```

Both flip the distinguished class, so PER-3/PER-4 gives

```text
d_(t+1) >= 2r_t-1.
```

Conversely take two copies of a parent `+` tope attaining distance `r_t`.
Their pair is a valid child `+` tope and has distance exactly

```text
2r_t-1.
```

Because the base minimizer has `p<P_1`, repeated pairing keeps its objective
strictly below the repeated trap objective. Hence this same radius is the exact
escape radius to a **lower-objective** chamber.

Thus

\[
\boxed{r_{t+1}=2r_t-1,\qquad r_1=5.}
\]

Solving,

\[
\boxed{
r_t=4\cdot2^{t-1}+1
=\frac{2}{15}n_t+1.
}
\]

This is an arbitrary-size theorem.

## 13. Exact global minimum also recurses

The base exact minimum is

```text
min p_1 = 12.
```

It lies in the `+` branch.  By the sign-pair composition, the child minimum is
obtained by pairing two parent minima and no mixed-sign pair is legal:

```text
min p_(t+1)=2 min p_t.
```

Therefore

\[
\boxed{\min p_t=12\cdot2^{t-1}=\frac25 n_t.}
\]

The source SAT boundary is

```text
n_t/3.
```

Since `2n_t/5 > n_t/3`, every member remains strictly on the UNSAT side of the
rational-kernel depth boundary, consistently with the independent exact UNSAT
preservation theorem.

## 14. Consequence for bounded-neighborhood augmentation

The earlier conditional augmentation theorem showed:

```text
UNIVERSAL CONSTANT R SUCH THAT EVERY NONGLOBAL CHAMBER
HAS A LOWER-p CHAMBER WITHIN PROJECTIVE DISTANCE R
=> deterministic polynomial descent.
```

PER now gives explicit connected linear-cubic source instances with a chamber
whose exact escape radius is

```text
(2/15)n+1.
```

Therefore the stronger universal property

```text
every nonglobal chamber has escape radius o(n)
```

is false.

This kills, as universal guarantees:
- one-step greedy descent;
- every fixed geometric radius;
- logarithmic geometric radius;
- every other sublinear geometric-radius bound.

It also shows why exhaustive radius-neighborhood descent cannot become a
polynomial universal solver by proving a small universal radius.

### Firewall

This does **not** prove that all projective algorithms are hard. A different
algorithm may:
- choose a special starting chamber and avoid the trap;
- optimize globally without enumerating neighborhoods;
- use a source-specific contraction/decomposition;
- exploit a different representation entirely.

No complexity lower bound for all algorithms is claimed.

## 15. Finite replay beyond the base

The exact finite checker independently obtains:

```text
n=30,d=2:  m=12,  topes=24,    trap escape radius=5,
n=60,d=3:  m=23,  topes=288,   trap escape radius=9.
```

The recurrence checker additionally composes the complete `n=60` tope set to
obtain the complete `n=120,d=5` tope set without enumerating a five-dimensional
arrangement cell-by-cell:

```text
compatible ordered pairs = 41,472,
projective classes = 45,
exact global min p = 48,
trap p = 60,
exact trap escape radius = 17.
```

This matches

```text
5 -> 9 -> 17
```

and the theorem recurrence exactly.

## 16. New live gate

Freeze

```text
R5_E9_PROJECTIVE_KERNEL_NONLOCAL_OPTIMIZATION_GATE_V1
```

The local-neighborhood program is now exhausted as a universal all-chamber
route. A material PASS must instead provide at least one of:

1. a polynomially constructible **canonical starting tope** with a proved
   polynomial path/shortcut to the global depth minimum, avoiding the prime
   traps;
2. a direct polynomial global optimization method for the weighted
   source-generated tope objective;
3. an exact contraction/decomposition that changes the arrangement and has a
   strict polynomial progress theorem;
4. a source-specific certificate of `min p>n/3` or a boundary witness without
   local chamber descent;
5. the complete universal polynomial algorithm contract by another route.

Forbidden pseudo-progress:
- another fixed-radius local search;
- a sublinear-radius conjecture without confronting PER;
- counting raw proportional coordinates instead of projective classes;
- claiming this barrier proves `P!=NP`;
- treating exponential tope enumeration as a polynomial solver.

## 17. Ceiling

```text
SPECIAL PRIME-TOWER SIGNED-BLOCK KERNEL
= EXACTLY K_t^0

FULL CHILD KERNEL
= sym(K_t) direct_sum asym(K_t^0)

EXACT NULLITY
= n_t/30 + 1

CHILD TOPES
= ORDERED PARENT-TOPE PAIRS WITH EQUAL DISTINGUISHED SIGN

PROJECTIVE CLASS RECURRENCE
= m_(t+1)=2m_t-1
= 11*2^(t-1)+1

TRAP OBJECTIVE
= n_t/2

GLOBAL MIN p
= 2n_t/5

EXACT PROJECTIVE ESCAPE RADIUS
= (2/15)n_t + 1

UNIVERSAL o(n) ALL-CHAMBER ESCAPE-RADIUS GUARANTEE
= FALSIFIED

LOCAL NEIGHBORHOOD DESCENT AS THE UNIVERSAL ROUTE
= CLOSED

NONLOCAL / CANONICAL-START / GLOBAL OPTIMIZATION ROUTES
= OPEN

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```