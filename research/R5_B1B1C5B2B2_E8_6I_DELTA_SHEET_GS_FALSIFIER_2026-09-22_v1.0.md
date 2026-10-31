# R5 E8 6I — Delta_sheet Guaranteed-Satisfaction Falsifier

Date: 2026-09-22

Authority: `PROVED_SOURCE_EXACT_NEGATIVE_GATE__NO_D1_PROMOTION`

Repository: `Hawkar-usls/Janus-Fundamentum`

Parent authorities:

- `research/R5_B1B1C5B2B2_E8_6I_THREE_SHEET_SOURCE_MODEL_BINDING_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_6I_DISJUNCTIVE_INDEPENDENCE_REFINEMENT_SHEET_ABSORPTION_GATE_2026-09-22_v1.0.md`
- `registry/R5_B1B1C5B2B2_E8_6I_DISJUNCTIVE_REFINEMENT_GATE_CHECKPOINT_2026-09-22_v1.0.json`

Checker:

`research/tools/r5_e8_6i_delta_sheet_gs_falsifier.py`

Receipt:

`research/R5_B1B1C5B2B2_E8_6I_DELTA_SHEET_GS_FALSIFIER_2026-09-22_v1.0.json`

## 1. Source-exact definition recovered

Primary source:

David Cohen, Peter Jeavons, Peter Jonsson, Manolis Koubarakis,
*Building tractable disjunctive constraints*,
Journal of the ACM 47(5), 2000, 826–853,
DOI 10.1145/355483.355485.

The indexed primary source gives Definition 7:

```text
A set of constraints has the
guaranteed satisfaction (GS) property
if every finite subset has a solution.
```

Primary indexed PDF:
https://dl.acm.org/doi/pdf/10.1145/355483.355485

The later Broxvall–Jonsson–Renz source confirms the theorem correspondence for the all-disjunction family:

```text
Delta*
=
all finite disjunctive relations over Delta

CSP(Delta*)
is tractable iff
Delta has GS
```

under the source setting.

Source:
Mathias Broxvall, Peter Jonsson, Jochen Renz,
*Disjunctions, independence, refinements*,
Artificial Intelligence 140(1–2), 2002, 153–173,
DOI 10.1016/S0004-3702(02)00224-2.

## 2. Frozen Delta_sheet

For each sign vector

```text
tau in {+,-}^3
```

the base relation

```text
M_tau
```

requires at least two sign-adjusted literals to be true.

Thus `Delta_sheet` contains, in particular:

```text
M_+++(x,y,z)
=
AT_LEAST_2(x,y,z)
```

and

```text
M_---(x,y,z)
=
AT_LEAST_2(NOT x,NOT y,NOT z).
```

The second relation is equivalently:

```text
AT_MOST_1(x,y,z).
```

## 3. Two-constraint falsifier

Consider the finite constraint set:

```text
C
=
{
  M_+++(x,y,z),
  M_---(x,y,z)
}.
```

The first constraint requires:

```text
x+y+z >= 2.
```

The second requires:

```text
(1-x)+(1-y)+(1-z) >= 2
```

equivalently:

```text
x+y+z <= 1.
```

These conditions are incompatible.

Therefore:

```text
C
has no solution.
```

Since `C` is a finite subset of the concrete `Delta_sheet` constraint family:

```text
GS(Delta_sheet)
=
FALSE.
```

The checker independently replays all eight Boolean assignments and confirms zero simultaneous solutions.

## 4. Theorem

### R5_E8_6I_DELTA_SHEET_GS_FALSIFIER_V1

```text
Delta_sheet
DOES NOT HAVE
THE GUARANTEED SATISFACTION PROPERTY.
```

Proof witness:

```text
M_+++(x,y,z)
AND
M_---(x,y,z).
```

This result is unconditional.

It uses:

```text
NO P != NP assumption
NO SAT oracle
NO complexity lower-bound transfer
NO finite extrapolation.
```

## 5. Consequence for the direct disjunctive route

The previously proved source-model binding remains valid:

```text
ARBITRARY SIGNED 3CNF
->
CSP(Delta_sheet*)
```

linearly and without selector variables.

But the direct all-disjunction tractability donor cannot be invoked through GS because:

```text
GS(Delta_sheet)
=
FALSE.
```

Hence:

```text
R5_E8_6I_DELTA_SHEET_GS_GATE_V1
=
FALSIFIED.
```

This does **not** show that every possible refinement-based composition route fails.

It closes only the direct source `Delta*` / GS route.

## 6. Refinement escape is now unlocked

The parent gate explicitly froze:

```text
REFINEMENT / 1-INDEPENDENCE ESCAPE
=
LOCKED UNTIL DIRECT GS ROUTE RESOLVES.
```

That condition is now satisfied.

Therefore the next source-bound task may examine:

```text
REFINEMENT-BASED
GLOBAL SHEET COMPOSITION
```

but only after recovering the exact source definition/model for the relevant Horn-like `Gamma OR Delta*` / 1-independence theorem.

Do not call the three-sheet system 1-independent by analogy.

Required next step:

```text
SOURCE-EXACT 1-INDEPENDENCE
DEFINITION RECOVERY

THEN

FREEZE A VALID Gamma / Delta SPLIT

THEN

PROVE OR FALSIFY
THE CORRESPONDING PROPERTY.
```

## 7. Scientific state

```text
I0 SOURCE-MODEL BINDING
=
PROVED

BASE CSP(Delta_sheet)
=
2SAT / POLYNOMIAL

DIRECT GS ROUTE
=
FALSIFIED BY TWO-CONSTRAINT WITNESS

REFINEMENT ESCAPE
=
UNLOCKED

1-INDEPENDENCE
=
NOT YET TESTED

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
