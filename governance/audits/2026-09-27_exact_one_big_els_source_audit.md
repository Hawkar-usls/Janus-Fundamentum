# Source audit — Exact-One BIG/SCC equivalent-literal substitution

Date: 2026-09-27
Decision: `PASS_SCOPED_GAP_CONFIRMED`
New math authorized: `true`
Scope: `R5_E9_EXACT_ONE_BIG_ELS_LEAN_GATE_V1`

## Internal anti-loop sweep

Checked the frozen WDR scheduler, the partial WDR closure, the universal-selector anti-loop binding, and the Exact-One matching/linear-autarky closures. `R1` was still open as exact equivalence substitution; the repo did not yet contain a proof that the standard Exact-One carrier is inert under the standard binary-implication SCC donor.

## External names / queries

Checked equivalent-literal substitution, equivalence elimination, binary implication graph, strongly connected components, SAT preprocessing, and linear-time SCC discovery.

## Sources checked

- A. Biere, M. Järvisalo, B. Kiesl, *Preprocessing in SAT Solving*, Handbook of Satisfiability (2021 manuscript): SCCs of the binary implication graph identify equivalent literals and support equivalent-literal substitution.
- N. Manthey, *Coprocessor — a Standalone SAT Preprocessor*: equivalence elimination via SCCs of the binary implication graph.
- Existing JANUS WDR scheduler and current Exact-One carrier notes.

## Collision result

BIG/SCC equivalent-literal substitution is fully source-bound prior art. The scoped live statement is only the structural specialization to standard Exact-One CNF: all BIG arcs go from positive to negative literals, so no nontrivial SCC exists. This does not claim completeness for all semantic literal equivalences.

## Authorized work

Authorize theorem/checker work only for BIG/SCC ELS on the untouched standard Exact-One carrier under the existing strict-equisatisfiable contraction route. Broader semantic equivalence discovery remains open and requires its own certified polynomial donor.

`P_VS_NP = OPEN`.
