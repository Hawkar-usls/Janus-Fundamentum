# C033 — Proof-Carrying Tractable Portfolio

**Status:** `CONSTRUCTIVE RESTRICTED ALGORITHM / P_VS_NP=OPEN`

## Purpose

C032 identified JANUS semantic cut signatures with PS-width. C033 builds the first strict proof-carrying solver portfolio that combines exact preprocessing and three polynomially recognizable CNF classes without silently invoking general SAT.

The dispatcher is:

```text
normalize by tautology deletion, duplicate deletion and subsumption
  -> Horn
  -> dual-Horn
  -> beta-acyclic nest-point elimination
  -> OPEN
```

Every accepted path returns an exact SAT answer and a witness when satisfiable. Inputs outside the admitted classes return `OPEN`.

## Constructive lemma

Let `P_1,...,P_t` be polynomial-time recognizable CNF classes with exact polynomial-time solvers, witness recovery and replayable certificates. A deterministic ordered dispatcher that invokes a solver only after its recognizer accepts is sound and polynomial on the union of those classes, provided normalization preserves satisfiability and witness transfer.

C033 instantiates this lemma with Horn, dual-Horn and beta-acyclic CNF.

## Normalization

The implementation deletes:

- tautological clauses;
- duplicate literals and duplicate clauses;
- every clause subsumed by a smaller clause.

These operations preserve SAT. Any satisfying assignment of the normalized formula satisfies the original formula directly, so witness transfer is free.

## Horn and dual-Horn

Horn formulas are solved by least-model forward chaining. Each forced head records the clause that fired; a negative clause whose body becomes true records a conflict.

Dual-Horn is reduced by complementing all variables and invoking the Horn solver, then complementing the recovered witness.

## Beta-acyclic elimination

The hypergraph recognizer repeatedly selects a nest point: a variable whose incident hyperedges are linearly ordered by inclusion after restriction to the remaining variables.

For an accepted order, Davis–Putnam elimination is applied exactly. At a nest point, the structural theorem guarantees that elimination can be performed without uncontrolled clause growth after subsumption. Witnesses are reconstructed in reverse elimination order by selecting a value for the eliminated variable that satisfies every clause present at that elimination step under the already reconstructed suffix assignment.

This is a proof-carrying implementation of the polynomial beta-acyclic SAT route of Ordyniak–Paulusma–Szeider. It is also compatible with the later weighted-elimination view of Brault-Baron–Capelli–Mengel.

## Frozen audit

```bash
python experiments/direct/janus_c033_tractable_portfolio.py --self-test
```

The deterministic audit checks 900 mixed random formulas against exhaustive truth tables on up to eight variables. It verifies every SAT witness and requires strict `OPEN` on a cyclic hypergraph negative control.

## Comparison with C023–C032

- C023 supplied fixed-language polymorphism admission and component rescue.
- C028 identified decomposability and support overlap.
- C029 blocked definitional occurrence splitting as a width reduction.
- C032 identified explicit semantic-cut tables with PS-width.
- C033 adds an elimination branch that is not PS-table dynamic programming and therefore covers a structurally different tractable regime.

This matters because beta-acyclic #SAT is known to evade the usual PS-width/dynamic-programming framework on some families. A universal portfolio cannot insist that every tractable formula first acquire a small explicit PS table.

## New bottleneck

```text
PORTFOLIO_SELECTION_WITH_SYMBOLIC_MESSAGES
```

The remaining constructive route is not merely to add more named tractable classes. It must provide a polynomial selector and a closed symbolic message algebra that composes Horn closure, dual-Horn closure, affine equations, beta-acyclic elimination and compiled representations across interacting regions.

The selector, representation construction, composition, equality/merge proof, elimination, witness recovery and UNSAT certificate discovery must all be charged.

## Next attacks

C034 must add a verified affine/GF(2) branch and then attack cross-class composition on:

- Horn plus parity interfaces;
- beta-acyclic regions joined by a cyclic separator;
- deterministic 3-CNF embeddings;
- Tseitin and expander CNFs;
- order-sensitive equality families;
- duplicate-clause families with tiny semantic cut quotient.

## Claim boundary

C033 is a genuine deterministic polynomial solver on the union of three recognized classes. It does not solve arbitrary CNF, construct a universal PS decomposition, or prove `P=NP`.

```text
P_VS_NP=OPEN
```
