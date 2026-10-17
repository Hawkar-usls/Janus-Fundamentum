# R5 E9 — Two-Edge SAT 2-Lift Survives Full RKPR with Linear Rational Nullity

Date: 2026-09-28

Status: `JANUS_DERIVED_ARBITRARY_SIZE_POST_RKPR_HIGH_NULLITY_FALSIFIER__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_TWO_EDGE_TWIST_3CUT_IRREDUCIBLE_LINEAR_NULLITY_FAMILY_2026-09-28_v1.0.md`
- `research/R5_E9_RATIONAL_KERNEL_PROJECTIVE_RATIO_PINNING_QUOTIENT_2026-09-28_v1.0.md`
- `research/R5_E9_RATIONAL_TOPE_DEFECT_SYNDROME_PROJECTIVE_FILTER_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_two_edge_sat_2lift_rkpr_survival.py`

Scientific ceiling:

```text
THE INFINITE DOILY TWO-EDGE-TWIST SAT 2-LIFT FAMILY SURVIVES THE FULL
RKPR PREPROCESSOR WITH RATIONAL NULLITY

    nu_Q >= n/5 + 2.

RKPR CAN PERFORM ONLY EQUALITY MERGES ON THIS FAMILY.  IT CANNOT CREATE
ZERO-ROW / ILLEGAL-RATIO UNSAT TERMINALS OR -2/-1/2 PINS, AND ORDINARY
EXACT-ONE PROPAGATION HAS NO INITIAL PIN OR REPEATED CLASS INSIDE A ROW.

THEREFORE THE PROPOSED UNIVERSAL SHORTCUT

    FULL RKPR => post-quotient rational nullity O(log n)

IS FALSE EVEN ON AN EXPLICIT INFINITE CONNECTED LINEAR-CUBIC SAT FAMILY.

THIS IS A ROUTE CLOSURE, NOT A P=NP RESULT.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Parent family

Use the arbitrary-size family from the two-edge-twist theorem.  Its base is the
`15 x 15` incidence matrix of the doily `GQ(2,2)`: columns are the 15 edges of
`K_6`, rows are its 15 perfect matchings, and incidence means membership.

At every stage two nonadjacent incidences outside a frozen strong odd cycle are
crossed in a graph 2-lift.  The parent theorem proves for all `t>=0`:

```text
n_t = 15 * 2^t,
connected = true,
linear = true,
cubic / square = true,
SAT = true,
unbalanced = true,
3-cut-irreducible = true,
k_t := nu_Q(A_t) >= 3*2^t + 2 = n_t/5 + 2.
```

The present note asks whether the later RKPR preprocessor destroys that
high-nullity family.

## 2. Six base witnesses with coordinate-wise variation

For each ground vertex `a in {0,1,2,3,4,5}`, let `x^(a)` select exactly the five
`K_6` edges incident with `a`.

Every perfect matching contains exactly one edge incident with `a`, so every
`x^(a)` is an Exact-One witness for the doily.

Fix any base column / edge

```text
e={u,v}.
```

Then

```text
x^(u)_e = x^(v)_e = 1,
```

while for each of the other four ground vertices `a`,

```text
x^(a)_e = 0.
```

Hence every base coordinate takes both Boolean values among these six exact
witnesses.

## 3. Fiber-constant lift preserves coordinate-wise variation

For every graph cover, a base Exact-One witness lifts fiber-constantly: assign
the same base Boolean value to every variable in its fiber.  Every lifted row
projects to one base row and therefore still sees exactly one selected
coordinate.

Iterating this observation through the whole two-edge 2-lift tower gives six
Exact-One witnesses on every `A_t`.

Every lifted coordinate `j` has a unique base ancestor edge `e`.  Across the six
fiber-constant witnesses its value is exactly the six-value pattern of `e`.
Therefore:

### Theorem RKS-1 — no universal Boolean pins

For every stage `t` and every coordinate `j` of `A_t`, there exist Exact-One
witnesses `x,x'` with

```text
x_j=0,
x'_j=1.
```

Thus no coordinate of any member of the family is forced to a constant Boolean
value.

## 4. Consequences for every RKPR projective class

Let `B_t` be any rational basis matrix for `ker_Q(A_t)` and let `b_j` denote its
`j`-th row.

### No zero rows

A zero row would force every rational kernel vector to have coordinate zero.
But for any Exact-One witness `x`, the kernel word

```text
y=3x-1
```

has every coordinate in `{-1,2}`.  Hence every `b_j` is nonzero.

### No illegal ratios

The family is SAT.  RKPR-1 already proves that any proportional nonzero pair in
a SAT source has ratio only

```text
{1,-2,-1/2}.
```

So no illegal-ratio UNSAT certificate occurs.

### No -2 or -1/2 classes

RKPR proves that a ratio `-2` or `-1/2` forces absolute complementary Boolean
pins on the two coordinates in every Exact-One witness.

RKS-1 says every coordinate takes both values among the six lifted star
witnesses.  Therefore such a pinned projective pair cannot exist.

Consequently:

### Theorem RKS-2 — RKPR classes are equality-only

For every stage `t`, every nontrivial rational projective class of `B_t`
consists of exactly equal rows, ratio `1`.

Thus full RKPR can only merge Boolean equality variables on this family.

## 5. Equality quotient preserves rational nullity exactly

Let the equality classes be `C_1,...,C_q`.  Let

```text
R in {0,1}^{n_t x q}
```

be the disjoint class-incidence matrix and let `H` contain one rational kernel
row representative per class.  Since all members of a class are equal,

```text
B_t = R H.
```

Put

```text
M=A_t R.
```

The previously proved quotient-kernel identity applies:

```text
ker_Q(M)=col(H),
nu_Q(M)=nu_Q(A_t)=k_t.
```

Therefore equality contraction does **not** reduce the rational-kernel
dimension of this family.

Since `M` has only `q` columns, it follows additionally that

```text
q >= k_t >= n_t/5+2.
```

So the quotient itself remains linear-size; this is not a case where the old
nullity is retained only relative to an exponentially compressed coordinate
set.

## 6. Ordinary propagation cannot start after the equality quotient

Consider one original source row with coordinate kernel functionals

```text
b_i + b_j + b_k = 0.
```

Suppose two coordinates in that row belonged to the same equality class, say

```text
b_i=b_j.
```

Then

```text
b_k=-2 b_i.
```

All three rows are nonzero, so this would be an RKPR ratio `-2`, contradicting
RKS-2.  Therefore every source row contains three **distinct** equality classes.

Hence after equality merging:

- no quotient row contains a coefficient `2` or `3`;
- there are no RKPR pins;
- no row begins with a pinned `1` or pinned `0`;
- ordinary exact-one propagation has no first move.

Duplicate quotient rows, if any, may be removed, but duplicate constraints do
not change the rational kernel or generate a pin.

Thus the full RKPR fixpoint on this family consists only of equality merging and
harmless duplicate-row deletion.

## 7. Arbitrary-size post-RKPR nullity lower bound

Combining the parent family nullity theorem with Sections 4--6 gives:

### Theorem RKS-3 — linear nullity survives full RKPR

For every `t>=0`, after exhaustive RKPR and its stated ordinary Exact-One
propagation,

\[
\boxed{
\nu_{\mathbb Q}(A_t^{\rm RKPR})
=
u_{\mathbb Q}(A_t)
\ge 3\cdot2^t+2
= n_t/5+2.
}
\]

In particular

```text
nu_Q(A_t^RKPR)=Omega(n_t)=omega(log n_t).
```

Therefore:

```text
FULL_RKPR => O(log n) RATIONAL NULLITY
```

is false even on an explicit infinite SAT family satisfying the current
linear-cubic, unbalanced, separator-resistant source conditions.

## 8. Exact finite regression

The checker reconstructs the doily and the first two canonical two-edge lifts.
It verifies exactly:

```text
stage 0: n=15, nullity=5,  q_RKPR=15,
stage 1: n=30, nullity=8,  q_RKPR=27,
stage 2: n=60, nullity=14, q_RKPR=51.
```

At all three stages it checks:

```text
zero kernel rows = 0,
illegal proportional ratios = 0,
-2/-1/2 pinning ratios = 0,
all nontrivial projective classes have ratio 1,
all six lifted star witnesses satisfy Exact-One,
every coordinate takes both 0 and 1 across those six witnesses.
```

The finite replay is regression evidence only.  The arbitrary-size proof is the
fiber-constant witness argument plus RKPR semantics and the exact equality
quotient kernel identity above.

## 9. Strategic consequence

The attractive architecture

```text
RKPR
-> residual d=O(log n)
-> existing exact 2^d kernel-word router
-> polynomial universal Exact-One solver
```

is now forbidden.

The family shows that a universal algorithm must process a post-RKPR core with
all of the following simultaneously:

```text
SAT,
linear cubic,
unbalanced,
3-cut-irreducible,
no universal coordinate pins,
no illegal rational projective ratios,
only equality projective classes,
rational nullity Omega(n).
```

The remaining viable target is therefore genuinely **global**: compress or
solve the interaction between the affine/parity constraints and the realizable
Exact-One / cycle-transfer structure without enumerating the high-dimensional
kernel.

## 10. New mandatory replay gate

Freeze

```text
R5_E9_POST_RKPR_TWO_EDGE_SAT_HIGH_NULLITY_REPLAY_GATE_V1
```

Every proposed universal P-time mechanism must be replayed on this family.
A PASS must give a polynomial construction and reconstruction proof without:

- enumerating `2^nu_Q` or `2^nu_F2` kernel points;
- hiding an exponential syndrome table;
- relying on bounded-radius tope descent;
- assuming a low-nullity prime core;
- treating equality contraction as a nullity reduction.

## 11. Ceiling

```text
SIX DOILY STAR WITNESSES
= EVERY BASE COORDINATE TAKES BOTH 0 AND 1

FIBER-CONSTANT LIFT
= PRESERVES THAT PROPERTY AT EVERY LEVEL

ZERO KERNEL ROW
= IMPOSSIBLE

ILLEGAL PROJECTIVE RATIO
= IMPOSSIBLE BY SAT

-2 / -1/2 PROJECTIVE RATIO
= IMPOSSIBLE BY COORDINATE-WISE WITNESS VARIATION

RKPR PROJECTIVE CLASSES
= EQUALITY ONLY

EQUALITY QUOTIENT
= EXACTLY PRESERVES nu_Q

ORDINARY RKPR PROPAGATION AFTER QUOTIENT
= NO INITIAL MOVE

POST-RKPR NULLITY
>= n/5+2
= PROVED FOR THE INFINITE FAMILY

FULL_RKPR => O(log n) NULLITY
= FALSIFIED

UNIVERSAL POLYNOMIAL DECIDER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```