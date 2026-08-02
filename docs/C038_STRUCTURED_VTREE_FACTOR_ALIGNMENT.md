# C038 — Structured Vtree Factor Alignment

**Status:** `CONSTRUCTIVE CONDITIONAL COMPILER / P_VS_NP=OPEN`

## Purpose

C037 showed that exact continuation refinement for one linear variable order is reduced OBDD minimization. C038 replaces the line by a supplied recursive vtree and asks what must be paid before structured d-DNNF, SDD or TDD-style compilation becomes constructive.

## Exact object

For every internal vtree node with variable set `X`, C038 forms the Boolean communication matrix

```text
rows    = assignments to X
columns = assignments to Vars(F) \ X
entry   = F(row union column)
```

Two rows are merged exactly when their continuation vectors coincide. Distinct rows carry an explicit outside assignment on which they disagree.

The maximum number of distinct rows over vtree cuts is an exact structured cut quotient. It is a communication/factor-width quantity already present in structured knowledge compilation, not a new universal width parameter.

## Conditional theorem

Given a vtree and the explicitly enumerated cut tables, C038 constructs in time polynomial in their total volume:

- exact continuation classes at every cut;
- replayable separating assignments for every distinct class pair;
- a SAT witness when one exists;
- an exhaustive UNSAT table certificate otherwise.

Every evaluation and separator is charged. No SAT or formula-equivalence oracle is called.

## Deterministic candidate construction

The executable includes a charged greedy co-occurrence vtree constructor. It repeatedly joins the pair of clusters sharing the largest number of clauses, with deterministic tie breaking.

This is a candidate heuristic only. Its output is verified, but no claim is made that it minimizes factor width or finds a polynomial representation whenever one exists.

## Equality control

For

```text
EQ_n = AND_i (x_i <-> y_i)
```

a paired vtree groups `(x_i,y_i)`, while a blocked vtree separates all `x` variables from all `y` variables.

At the blocked root child there are exactly `2^n` continuation rows: every assignment to the `x` variables requires a different assignment to the `y` variables. The paired tree keeps local equality interactions together and remains small. The greedy co-occurrence tree rediscovers the pairs deterministically on this family.

This demonstrates that recursive structure can remove the linear-order explosion of C037 on a suitable family, but a bad vtree still exposes an exponential interface.

## Literature alignment

- Structured d-DNNF and SDD are vtree-respecting knowledge-compilation languages.
- Tree Decision Diagrams (TDDs) are a 2026 canonical generalization of OBDD inside structured d-DNNF; their bottom-up compilation complexity is related to factor width.
- Known compilation results are fixed-parameter or output-sensitive under structural width assumptions. They do not supply a universal polynomial vtree constructor for arbitrary CNF.
- Known lower bounds for one structured representation do not imply `P != NP`.

## Frozen audit

```bash
python experiments/direct/janus_c038_structured_vtree_factor_alignment.py --self-test
```

The audit checks paired, blocked and greedily constructed vtrees for equality formulas through `n=8`, requires `OPEN` on a blocked `n=12` budget control, verifies every emitted separator, checks SAT witnesses, and applies the deterministic constructor to 120 random 3-CNFs.

Finite tests validate the implementation only.

## Located gate

```text
POLYNOMIAL_VTREE_DISCOVERY_AND_SYMBOLIC_FACTOR_CONSTRUCTION
```

A universal route must avoid explicit truth-table construction while still producing the same cut quotient, separators, witnesses and UNSAT evidence in total polynomial time. It must also discover a suitable recursive structure rather than receiving it for free.

## Lineage note

Two sibling draft PRs currently use the label `C037`: the OBDD alignment and the Horn-affine negotiation bridge. C038 is stacked on the OBDD-alignment branch because it generalizes its decomposition axis. The sibling cross-language result remains relevant and must be reconciled before canonical admission.

## Claim boundary

C038 is an exact, budgeted, output-sensitive structured compiler and an alignment with communication/factor width. It does not prove that arbitrary CNF admits a polynomial vtree quotient, does not solve arbitrary SAT, and does not resolve P versus NP.

```text
P_VS_NP=OPEN
```
