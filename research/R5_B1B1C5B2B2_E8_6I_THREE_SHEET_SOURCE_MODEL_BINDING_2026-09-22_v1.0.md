# R5 E8 6I — Three-Sheet Source-Model Binding Theorem

Date: 2026-09-22

Authority: `PROVED_EXACT_SOURCE_MODEL_BINDING__NO_TRACTABILITY_PROMOTION__NO_D1_PROMOTION`

Parent gate:

`research/R5_B1B1C5B2B2_E8_6I_DISJUNCTIVE_INDEPENDENCE_REFINEMENT_SHEET_ABSORPTION_GATE_2026-09-22_v1.0.md`

## 1. Fixed base language

For a sign vector

```text
tau=(tau_1,tau_2,tau_3) in {+,-}^3
```

define the ternary Boolean relation

```text
M_tau(x,y,z)
```

to hold iff at least two of the three sign-adjusted literals are true.

Equivalently:

```text
M_tau
=
AT_LEAST_2(l_1,l_2,l_3)

=
(l_1 OR l_2)
AND
(l_1 OR l_3)
AND
(l_2 OR l_3).
```

Let:

```text
Delta_sheet
=
{M_tau : tau in {+,-}^3}.
```

There are exactly:

```text
8
```

distinct relations.

The apparent 24 signed `clause x sheet` variants collapse to these eight relations because the three frozen sheets differ only by additional coordinate conjugations.

## 2. Base tractability

Every member of `Delta_sheet` is definable by three binary clauses.

Therefore any conjunction of constraints from `Delta_sheet` reduces linearly to 2-SAT.

Hence:

```text
CSP(Delta_sheet)
=
POLYNOMIAL.
```

This is a direct syntactic theorem; no SAT oracle or complexity assumption is used.

## 3. Exact OR3 disjunctive cover

For literal truth values `a,b,c`:

```text
OR3(a,b,c)
=
MAJ(a,b,c)
OR
MAJ(a,NOT b,c)
OR
MAJ(a,b,NOT c).
```

The previously sealed truth-table checker verifies this identity and all signed variants.

Each of the three right-hand disjuncts is a member of `Delta_sheet`.

Therefore every signed 3-clause relation is a finite disjunction of exactly three base relations from `Delta_sheet`.

## 4. Exact source-model binding

Let:

```text
Delta_sheet*
```

denote the source-style closure containing all finite disjunctive relations over `Delta_sheet`.

Then every signed 3-CNF instance is directly a CSP instance over `Delta_sheet*`:

```text
signed 3-clause
->
one 3-way disjunctive relation
over Delta_sheet.
```

No selector variable is introduced.

Shared-variable coherence is automatic: the same CSP variable is used in every occurrence of the same original SAT variable.

Construction time and representation size are linear in the original formula size.

Thus:

```text
I0 SOURCE-MODEL BINDING
=
PASS

MODEL
=
CSP(Delta_sheet*)
```

for the all-disjunction family studied by the tractable-disjunctive-constraints literature.

## 5. Source theorem relevance

Cohen–Jeavons–Jonsson–Koubarakis develop general tractability constructions for disjunctive constraint languages.

Broxvall–Jonsson–Renz distinguish the all-disjunction family:

```text
Delta*
```

from Horn-like and bounded-two-disjunct families and identify the guaranteed-satisfaction property as the structural condition controlling the all-disjunction regime, under the source assumptions.

Therefore the direct three-sheet composition question is sharpened from:

```text
"some independence / refinement property?"
```

to:

```text
DIRECT ROUTE:
does Delta_sheet satisfy the exact
source GS condition?

REFINEMENT ESCAPE:
if not, can a polynomial exact refinement
move the problem into a different
source-supported tractable disjunctive regime
such as a 1-independent Horn-like form?
```

No claim about GS is made in this artifact.

## 6. Important distinction

The explicit selector encoding:

```text
exists s_C T(s_C,...)
```

is an NP-complete repackaging.

The source binding here does **not** introduce `s_C`.

It represents the clause directly as the disjunctive relation:

```text
M_0 OR M_1 OR M_2.
```

Thus:

```text
SOURCE-MODEL BINDING
!=
SELECTOR SOLUTION.
```

The remaining difficulty is exactly whether the disjunction can be globally solved/refined without enumerating one branch per clause.

## 7. Next exact obligations

```text
DIRECT-D1:
source-exact GS definition
for Delta_sheet
+
prove or falsify GS by a finite/symbolic witness.

REFINEMENT-D2:
only if direct GS route fails,
seek an exact polynomial refinement
into a source-supported regime
whose independence property is
poly-checkable and globally coherent.
```

Do not invoke 1-independence before defining a `Gamma/Delta` split that actually places the refined constraints in the corresponding source family.

## Claim ceiling

```text
I0 SOURCE-MODEL BINDING
=
PROVED

BASE Delta_sheet CSP
=
2SAT / POLYNOMIAL

ARBITRARY SIGNED 3CNF
=
EXACT SUBCLASS OF CSP(Delta_sheet*)

GS(Delta_sheet)
=
OPEN

REFINEMENT / 1-INDEPENDENCE ESCAPE
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
