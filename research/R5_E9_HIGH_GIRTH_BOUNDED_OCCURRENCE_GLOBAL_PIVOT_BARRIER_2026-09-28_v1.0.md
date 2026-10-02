# R5 E9 — High-Girth + Bounded-Occurrence Global-Pivot Barrier

Date: 2026-09-28

Status:
`SOURCE_BOUND_HIGH_GIRTH_BOUNDED_DEGREE_ANTI_LOOP__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_SPARSE_INCOMPARABILITY_HIGH_GIRTH_GLOBAL_PIVOT_BARRIER_2026-09-28_v1.0.md`
- `research/R5_E9_TWO_PATH_SINGLE_VARIABLE_PROJECTION_DP_ANTI_LOOP_2026-09-28_v1.0.md`

Checker:
- `experiments/r5_e9_high_girth_bounded_occurrence_pivot_barrier.py`

Scientific firewall:

```text
THIS CLOSES "A HARD RESIDUAL MUST EXPOSE AN UNBOUNDED-DEGREE SOURCE VARIABLE"
AS A UNIVERSAL PROGRESS PREMISE.
IT DOES NOT PROVE A LOWER BOUND FOR SAT.
IT DOES NOT RULE OUT SEMANTIC RULES THAT WORK ON BOUNDED-DEGREE HIGH-GIRTH INSTANCES.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Bounded-occurrence hard source

Craig A. Tovey proved that 3-SAT remains NP-complete when every variable appears in at most four clauses:

- C. A. Tovey, *A simplified NP-complete satisfiability problem*, Discrete Applied Mathematics 8 (1984), 85–89.
- DOI: `10.1016/0166-218X(84)90081-7`.

Tovey's formulation uses clauses with three variables and no repeated variable inside a clause.

Under the fixed signed-clause relational encoding from the companion high-girth note, a 3-SAT-4 instance becomes a `tau`-structure `S` with

```text
Delta(S) <= 4,
```

where relational degree is exactly source variable occurrence count because every constraint tuple has distinct coordinates.

## 2. Degree control inside Kun's deterministic Sparse-Incomparability construction

The proof of Kun's deterministic Sparse Incomparability theorem constructs the high-girth structure as a twisted product.

For the fixed signed-3SAT relational type `tau`, target-size threshold `t=3`, and maximum relation arity `r=3`, the proof chooses a fixed expansion tolerance

```text
epsilon = 1 / t^r = 1/27.
```

Kun's large-girth expander theorem supplies, for every required girth threshold and sufficiently large size, an auxiliary `tau`-structure `A` with

```text
Delta(A) <= M_{tau,epsilon},
```

where the bound `M_{tau,epsilon}` is independent of the requested girth and independent of the input instance size.

The transformed instance `S'` is a twisted product of `A` with `S`.

### Lemma BD-1 — twisted-product degree bound

For every twisted product `C` of relational structures `A` and `B`,

```text
Delta(C) <= Delta(A) * Delta(B).
```

Reason: fix an element `(a,b)` of the product universe.  Every relational-tuple occurrence containing it projects to one tuple occurrence of `B` containing `b`, and inside that fibre it corresponds to a tuple occurrence of `A` containing the associated preimage of `(a,b)`.  Thus at most the product of the two maximum degrees is possible.  This is the degree bound used in Kun's twisted-product analysis.

Therefore, starting from Tovey's source,

```text
Delta(S')
<= Delta(A) Delta(S)
<= 4 M_{tau,1/27}.
```

Define the absolute constant

```text
D := 4 M_{tau,1/27}.
```

Crucially, `D` depends only on the fixed signed-3SAT signature / fixed target parameters. It does **not** depend on the source instance size and does **not** depend on the chosen fixed girth threshold.

## 3. Combined hard-family theorem

### Theorem HGBD-1

There exists a finite constant `D` such that for every fixed positive integer `g`, signed exact-3SAT is NP-complete even when restricted to source relational structures satisfying simultaneously

```text
girth > g,
maximum source-variable occurrence <= D,
every constraint has exactly three distinct source variables.
```

### Proof

Take an arbitrary Tovey 3-SAT-4 instance and encode it as the fixed Boolean signed-clause CSP instance `S`. Apply Kun's deterministic polynomial Sparse-Incomparability construction with target threshold `t=3` and desired relational girth `>g`. The companion high-girth theorem gives exact satisfiability preservation into the fixed two-element target. Lemma BD-1 and the bounded-degree auxiliary expander theorem give `Delta(S')<=D`. For `g>=1`, no transformed relation tuple has a repeated coordinate because that would be a degenerate relational cycle of length one. Membership in NP is unchanged. QED.

## 4. Consequence for the primary GLOBAL_PIVOT search

The following universal strategy is now closed:

```text
IF THERE IS NO SHORT SOURCE CYCLE,
THEN SOME SOURCE VARIABLE MUST HAVE VERY LARGE DEGREE;
PIVOT ON THAT VARIABLE.
```

It is false as a universal coverage theorem.  For every fixed forbidden short-cycle radius there remains an NP-hard source class with all variable degrees bounded by the same constant `D`.

Combined with the previous barriers:

```text
single whole variable path -> ordinary Davis-Putnam;
mandatory bounded source cycle -> unavailable on high-girth hard sources;
mandatory unbounded-degree source variable -> unavailable on high-girth bounded-degree hard sources.
```

Therefore a universal primary pivot must survive a source regime that is simultaneously sparse, bounded-degree, and locally tree-like to every fixed radius chosen in advance.

## 5. What remains admissible

This theorem does not rule out:

- a rule triggered by a bounded-degree tree neighborhood and proved universally progressive;
- long structures whose radius grows with input size;
- global parity/syndrome/cycle-space objects;
- exact projected-boundary compilation with polynomial closed operations;
- nonlocal witness dominance;
- representation changes with a global polynomial progress measure.

It only removes high degree as a mandatory fallback after short-cycle pivots fail.

## 6. Strengthened primary gate

The active gate remains

```text
R5_E9_HIGH_GIRTH_SAFE_NONLOCAL_GLOBAL_PIVOT_GATE_V1
```

with an additional hostile-source requirement:

```text
coverage must include a bounded-occurrence, arbitrarily-high-fixed-girth signed-3SAT family.
```

Any PASS must therefore be semantic/nonlocal rather than relying on a guaranteed local density defect.

## 7. Ceiling

```text
3-SAT-4 NP-COMPLETE
= SOURCE-BOUND PRIOR ART (TOVEY 1984)

SPARSE INCOMPARABILITY + TWISTED-PRODUCT DEGREE CONTROL
= SOURCE-BOUND PRIOR ART + DIRECT SPECIALIZATION

EXISTS CONSTANT D SUCH THAT FOR EVERY FIXED g:
HIGH-GIRTH > g AND MAX-OCCURRENCE <= D SIGNED-3SAT IS NP-COMPLETE
= PROVED BY COMPOSITION

SHORT-CYCLE-OR-HIGH-DEGREE UNIVERSAL DICHOTOMY
= CLOSED

HIGH-GIRTH-SAFE NONLOCAL GLOBAL PIVOT
= OPEN <<< PRIMARY MICRO-GAP

UNIVERSAL POLYNOMIAL DECIDER
= OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```