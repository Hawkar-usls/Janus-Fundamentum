# R5 E9 — Standard Exact-One CNF is BIG-ELS lean

Date: 2026-09-27
Status: THEOREM_CANDIDATE__NOT_LEDGER_PROMOTED
Global status: `P_VS_NP = OPEN`

## Scope

This note closes one precise polynomial `R1` donor: equivalent-literal substitution (`ELS`) obtained from strongly connected components of the **binary implication graph** (`BIG`). It does not claim to find every semantic literal equivalence of an arbitrary CNF.

For each Exact-One constraint on distinct variables `a,b,c`, use the standard CNF

\[
(a\vee b\vee c)\wedge(\neg a\vee\neg b)\wedge(\neg a\vee\neg c)\wedge(\neg b\vee\neg c).
\]

The positive ternary clause contributes no edge to the BIG. A binary clause

\[
(\neg x\vee\neg y)
\]

contributes exactly the implications

\[
x\to\neg y,\qquad y\to\neg x.
\]

## Theorem

For every conjunction of untouched standard Exact-One triples, every directed BIG edge goes from a positive literal to a negative literal. Hence every negative literal has out-degree zero in the BIG. Therefore the BIG contains no directed cycle involving two distinct vertices and every strongly connected component is a singleton.

Consequently SCC-based equivalent-literal substitution finds no nontrivial equivalence class on the untouched carrier.

### Proof

The only binary clauses in a standard Exact-One triple are the three pairwise at-most-one clauses. Each has two negative literals, so both implication edges have a positive tail and negative head. Taking a union over arbitrarily many triples does not create any other BIG edge type. Thus a directed path can contain at most one edge: after the first edge it is at a negative literal, which has no outgoing BIG edge. A nontrivial directed cycle is impossible, and therefore no non-singleton SCC exists. QED.

## Scheduler consequence

`R0` precedes `R1` in the frozen WDR scheduler. On the survivor regime where `R0` performs no unit/pure cleanup and the standard Exact-One representation remains untouched, BIG/SCC ELS also performs no step.

The resulting precise frontier statement is:

```text
R1_BIG_SCC_EQUIVALENT_LITERAL_SUBSTITUTION = CLOSED_ON_UNTOUCHED_STANDARD_EXACT_ONE
R1_BROADER_CERTIFIED_EQUIVALENCE            = OPEN
R2_MATCHING_AUTARKY                         = CLOSED_ON_CUBIC_LINEAR_EXACT_ONE
R2_SIMPLE_LINEAR_AUTARKY                    = CLOSED_ON_STANDARD_EXACT_ONE
R5_SIGNED_STRUCTURAL_DOMINANCE              = OPEN
R6_RANKED_SR_MACRO                          = OPEN
REPRESENTATION_CHANGE                       = OPEN
```

## Prior-art binding

Equivalent-literal substitution by SCCs of the binary implication graph is standard SAT preprocessing, not JANUS novelty. The SAT preprocessing literature states that each nontrivial SCC of the BIG yields equivalent literals and can be collapsed to a representative; SCCs are computable in linear time in the graph size.

Sources checked before promotion:

- A. Biere, M. Järvisalo, B. Kiesl, *Preprocessing in SAT Solving*, Handbook of Satisfiability, 2021 manuscript; section on BIG and equivalent-literal substitution.
- N. Manthey, *Coprocessor — a Standalone SAT Preprocessor*, description of equivalence elimination from SCCs of the binary implication graph.
- Existing JANUS WDR lean normal-form scheduler and current Exact-One closure notes.

The JANUS contribution in this note is only the Exact-One specialization proving that the relevant BIG is a one-way positive-to-negative DAG of depth one.

## Epistemic firewall

```text
BIG_SCC_ELS = SOURCE_BOUND_PREPROCESSING_DONOR
BIG_SCC_ELS_ON_STANDARD_EXACT_ONE = CLOSED_BY_STRUCTURAL_THEOREM_CANDIDATE
ALL_SEMANTIC_LITERAL_EQUIVALENCES = NOT_CLAIMED
UNIVERSAL_SELECTOR = OPEN
E8_D1 = EMPTY
P_VS_NP = OPEN
```
