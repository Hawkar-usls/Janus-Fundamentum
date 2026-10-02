# R5 E8 6I — Static Gamma/Delta 1-Independence Barrier

Date: 2026-09-22

Authority: `PROVED_EXACT_FINITE_SOURCE_BOUND_BARRIER__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_6I_THREE_SHEET_SOURCE_MODEL_BINDING_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_6I_DELTA_SHEET_GS_FALSIFIER_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_6I_DISJUNCTIVE_INDEPENDENCE_REFINEMENT_SHEET_ABSORPTION_GATE_2026-09-22_v1.0.md`

Checker:

`research/tools/r5_e8_6i_static_gamma_delta_1independence_checker.py`

Receipt:

`research/R5_B1B1C5B2B2_E8_6I_STATIC_GAMMA_DELTA_1INDEPENDENCE_BARRIER_2026-09-22_v1.0.json`

## 1. Source-exact 1-independence definition

The Handbook of Constraint Programming, Definition 78, states:

For constraint languages `Gamma` and `Delta` over domain `D`, `Delta` is `k)-independent with respect to `Gamma` iff every instance

```text
I in CSP(Gamma union Delta)
```

has a solution provided that every subinstance of `I` containing at most `k` constraints from `Delta` has a solution.

For `k=1`:

```text
1-INDEPENDENCE
=
all Delta constraints are globally compatible
whenever every one-Delta subinstance is compatible
with the Gamma core.
```

The same source gives the Horn-like composition theorem:

```text
if CSP_{Delta<=1}(Gamma union Delta)
is tractable

and

Delta is 1-independent with respect to Gamma,

then the Horn-like disjunctive class
Gamma OR Delta*
is tractable.
```

No such property is assumed here; it is tested.

## 2. Immediate necessary condition

Take the `Gamma` core to be empty.

Every individual frozen threshold-two sheet relation is nonempty.

Therefore, if `Delta` is 1-independent with respect to any `Gamma`, then every finite set of `Delta)-constraints must be jointly satisfiable whenever each individual constraint is satisfiable.

Hence:

```text
1-INDEPENDENCE(Delta wrt Gamma)
=>
GS(Delta).
```

This implication is direct from Definition 78 and does not use a complexity assumption.

## 3. Frozen three-sheet cover hypergraph

The eight frozen sheet relations are indexed by sign vectors

```text
tau in {0,1}^3.
```

For each signed OR3 prototype row with sign vector `tau`, the canonical three-sheet cover is

```text
{
 M_tau,
 M_{tau xor 010},
 M_{tau xor 001}
}.
```

For each fixed first sign bit, there are four relations corresponding to the four values of the last two sign bits.

The eight frozen covers restricted to one first-sign layer are exactly **all four 3-element subsets** of those four relations.

Thus any two relations in the same first-sign layer appear together in at least one three-sheet OR3 cover.

## 4. Static Horn-like partition consequence

Consider a static partition:

```text
Delta_sheet
=
Gamma disjoint_union Delta.
```

To place every frozen three-sheet OR3 cover into the source Horn-like family

```text
Gamma OR Delta*
```

each three-sheet disjunction may contain at most one `Gamma` relation.

Because every pair in one first-sign layer co-occurs in some cover:

```text
|Gamma intersect layer_0|
<=
1

|Gamma intersect layer_1|
<=
1.
```

Therefore:

```text
|Gamma|
<=
2

and

|Delta|
>=
6.
```

## 5. Complementary-pair obstruction

The eight sheet relations form four complementary sign pairs:

```text
M_tau
and
M_not_tau.
```

On the same variable triple:

```text
M_tau
=
AT_LEAST_2(sign-adjusted literals)

M_not_tau
=
AT_MOST_1(the same sign-adjusted literals).
```

Their conjunction is unsatisfiable.

A subset of the eight sheets avoiding all complementary pairs can contain at most one element from each of the four pairs, hence at most four relations.

But every Horn-admissible static split has:

```text
|Delta| >= 6.
```

Therefore `Delta` necessarily contains a complementary unsatisfiable pair.

Hence:

```text
GS(Delta)
=
FALSE.
```

By Section 2:

```text
Delta
is not 1-independent
with respect to Gamma.
```

## 6. Exact exhaustive replay

The checker enumerates all:

```text
2^8 = 256
```

static partitions of the eight frozen sheet relations.

Results:

```text
HORN-ADMISSIBLE STATIC PARTITIONS
=
25

MAX |Gamma|
=
2

MIN |Delta|
=
6

MIN COMPLEMENTARY UNSAT PAIRS
REMAINING INSIDE Delta
=
2.
```

Thus every static partition satisfying the Horn-like cover syntax violates the necessary GS condition for 1-independence.

## 7. Barrier theorem

### R5_E8_6I_STATIC_GAMMA_DELTA_1INDEPENDENCE_BARRIER_V1

There is no static partition of the existing eight frozen `Delta_sheet` threshold-two relations into `Gamma` and `Delta` such that both hold:

```text
A.
every frozen three-sheet OR3 cover
belongs to the Horn-like
Gamma OR Delta* source family;

B.
Delta is 1-independent
with respect to Gamma.
```

This is an unconditional finite/combinatorial barrier.

## 8. Scope firewall

The theorem blocks only:

```text
STATIC RELATION-LANGUAGE
PARTITION / RELABELING
OF THE EXISTING EIGHT SHEETS.
```

It does **not** block:

- representation-changing refinements;
- derived/refined relation languages;
- polynomial instance-specific refinement certificates;
- additional tractable base relations;
- a different source-supported disjunctive composition theorem.

Therefore the correct next target is no longer:

```text
find a better static Gamma/Delta split.
```

It is:

```text
find or rule out a polynomial exact refinement
that changes the relation/interface structure
before applying a source-supported
1-independence/refinement theorem.
```

## 9. Current state

```text
I0 SOURCE-MODEL BINDING
=
PROVED

DIRECT GS(Delta_sheet)
=
FALSIFIED

STATIC Gamma/Delta
1-INDEPENDENCE REPAIR
=
FALSIFIED

REPRESENTATION-CHANGING
REFINEMENT ESCAPE
=
OPEN

GLOBAL SHEET COHERENCE
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
