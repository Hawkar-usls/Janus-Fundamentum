# R5 E8 6I — Disjunctive Independence / Refinement Sheet-Absorption Gate

Date: 2026-09-22

Authority: `OPEN_SOURCE_BOUND_COMPOSITION_GATE__NO_D1_PROMOTION`

## Parent authorities

- `research/R5_B1B1C5B2B2_E8_6I_THREE_SHEET_MAJORITY_COVER_AND_SELECTOR_CONTROL_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_6I_A3_SBM_MAJORITY_LIFT_POSITIVE_CONTROL_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_6I_EXPLICIT_SELECTOR_PSEUDOPARTITION_BARRIER_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_6I_HIDDEN_LIFT_PROJECTION_BARRIER_2026-09-22_v1.0.md`
- `research/R5_B1B1C5B2B2_E8_CORPUS_FIRST_MECHANISM_SYNTHESIS_DOCTRINE_2026-09-22_v1.0.md`

## 0. Current exact gap

```text
OR3
=
UNION OF THREE
TRACTABLE THRESHOLD-2
PROTOTYPE-ADMISSION SHEETS

LOCAL EXACTNESS
=
PASS

TRACTABLE SHEETS
=
PASS

POLY SOLVE / SHEET
=
PASS

POLY RECONSTRUCTION
=
PASS

GLOBAL ABSORPTION OF SHEET CHOICE
WITHOUT SAT-LIKE SELECTOR
=
OPEN
```

The explicit independent clause selector is an exact 3-SAT repackaging.
The direct semilattice/pseudopartition absorption of that explicit selector over Boolean visible coordinates is theorem-level blocked.

## 1. Source-bound mechanism donors

### D1 — Cohen–Jeavons–Jonsson–Koubarakis

*Building tractable disjunctive constraints*, JACM 47(5), 2000, 826–853.
DOI: 10.1145/355483.355485

Source record:
https://ora.ox.ac.uk/objects/uuid%3A0de17b9f-8994-42c8-90d4-9d677cf4df44

Role:

```text
GLOBAL DISJUNCTIVE COMPOSITION DONOR
```

The source gives general methods for constructing tractable disjunctive classes from simpler tractable classes.

### D2 — Broxvall–Jonsson–Renz

*Disjunctions, independence, refinements*, Artificial Intelligence 140(1–2), 2002, 153–173.
DOI: 10.1016/S0004-3702(02)00224-2

Source:
https://www.sciencedirect.com/science/article/pii/S0004370202002242

The source studies:

```text
GUARANTEED SATISFACTION
1-INDEPENDENCE
2-INDEPENDENCE
REFINEMENTS
```

as exact tractability controls for natural disjunctive constraint families.

A source summary distinguishes:

```text
Delta*
=
all finite disjunctions over Delta

Gamma OR Delta*
=
Horn-like disjunctions with
at most one Gamma relation per disjunction

Delta^2
=
disjunctions with at most
two Delta disjuncts
```

with GS / 1-independence / 2-independence controlling the corresponding classes under their base assumptions.

### Scope firewall

No current JANUS artifact proves that the A3 three-sheet shared-variable system is an instance of one of those source theorem classes.

That binding is the first obligation below.

## 2. Target object

Not:

```text
for each clause C
guess s_C in {0,1,2}.
```

Instead:

```text
construct a polynomial-size
global refinement / independence
certificate Q(F)

such that local sheet admissibility
is forced by Q(F)

and one coherent decoder state
is maintained per original variable.
```

## 3. I0 — source-model binding

Formalize the A3 three-sheet prototype-admission system as an exact source-supported disjunctive family.

Required:

```text
I0.1
freeze fixed relation languages
Gamma, Delta
(or another explicitly sourced split)

I0.2
map every sheet-admission constraint
and every shared-variable coherence relation
into that formalism

I0.3
prove exact equivalence:

source-model instance SAT
iff
globally coherent
three-sheet prototype exists

I0.4
construction time/size
=
poly(original L)
```

If this cannot be done:

```text
FAIL_SOURCE_MODEL_MISMATCH.
```

Do not use independence terminology merely by analogy.

## 4. I1 — three-sheet refinement formalization

Required:

```text
every refined local relation
=
known polynomial base relation

union/refinement semantics
=
ordinary OR3 prototype admission

one original variable
=
one global decoder state

no free clause-local selector.
```

## 5. I2 — sufficient independence / refinement certificate

Identify the weakest source-bound global condition sufficient for polynomial composition.

Candidates include:

```text
GS
1-INDEPENDENCE
2-INDEPENDENCE
REFINEMENT-BASED CONDITION
```

but none is assumed.

Required theorem:

```text
CERT(F)
=>
global coherent three-sheet
prototype problem is polynomial.
```

The proof must state the exact source theorem family used.

## 6. I3 — polynomial certificate discovery

Required:

```text
ConstructCert(F)
->
Q(F)

TIME
=
poly(L)

SIZE
=
poly(L).
```

If checking or constructing Q(F) is polynomially equivalent to original SAT:

```text
FAIL_HIDDEN_DISCOVERY_HARDNESS.
```

## 7. I4 — global variable coherence

Required:

```text
all occurrences of x / NOT x
share one decoder/lifted state

sheet orientation is derived
from Q(F)

occurrence-wise conjugations
cannot disagree.
```

No relaxation is sufficient; reconstruction must be exact.

## 8. I5 — hidden-selector firewall

Reject any certificate whose unresolved degrees of freedom include an independent:

```text
s_C in {0,1,2}
```

for each clause.

If solving Q(F) amounts to choosing an accepting sheet independently per clause, the construction is the already-sealed NP-complete three-sheet selector CSP.

Also reject value-coding/retract constructions that reproduce the original Boolean SAT choice inside certificate discovery.

## 9. I6 — total polynomial composition lifecycle

If I0–I5 pass, combine the global certificate with the already-sealed A3 lifted solver and prove:

```text
T_construct
+
T_certificate
+
T_refine
+
T_A3_lift
+
T_SBM_solve
+
T_reconstruct
+
T_verify
+
T_history

<=
poly(original L).
```

Forbidden hidden resources:

```text
SAT oracle
equivalence oracle
exponential refinement enumeration
unbounded backdoor / alien search
hidden existential semantic choice
semantic sweeping without poly theorem.
```

## 10. Conditional consequence

If I0–I6 all close for arbitrary signed 3-CNF:

```text
3SAT in P
=>
SAT in P
=>
P = NP.
```

No current result establishes these obligations.

## 11. Frozen negative controls

```text
INDEPENDENT CLAUSE SELECTOR
=
NP-COMPLETE REPACKAGING

DIRECT EXPLICIT-SELECTOR
SEMILATTICE / PSEUDOPARTITION
ABSORPTION
=
BLOCKED IN FROZEN
BOOLEAN-VISIBLE MODEL

FIXED-VISIBLE-A3
HIDDEN LIFT AUXILIARIES
=
DO NOT EXPAND DIRECT
DECODER-IMAGE COVERAGE

LOCAL BIJUNCTIVE
PP THRESHOLD REPAIR
=
BLOCKED
```

## 12. Status

```text
R5_E8_6I_DISJUNCTIVE_INDEPENDENCE_REFINEMENT_SHEET_ABSORPTION_GATE_V1

I0 SOURCE-MODEL BINDING
=
OPEN

I1 REFINEMENT FORMALIZATION
=
OPEN

I2 SUFFICIENT GLOBAL CERTIFICATE
=
OPEN

I3 POLY CERTIFICATE DISCOVERY
=
OPEN

I4 GLOBAL VARIABLE COHERENCE
=
OPEN

I5 HIDDEN SELECTOR FIREWALL
=
OPEN

I6 TOTAL POLY LIFECYCLE
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```

## 13. First authorized subtask

Do not enumerate another carrier yet.

First derive the exact relational encoding of:

```text
three A3 prototype sheets
+
shared-variable decoder coherence
```

and decide whether it fits a precisely cited disjunctive/refinement theorem family.

Only after I0 passes may independence testing begin.
