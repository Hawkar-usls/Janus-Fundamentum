# C036.1 — Explicit Residual Automaton / OBDD Alignment

**Status:** `CONSTRUCTIVE CONDITIONAL THEOREM / P_VS_NP=OPEN`

## Purpose

C036 proves complete polynomial separator extraction inside Horn and affine message languages when residual objects are already available. C036.1 separates that cost from explicit generation and minimization of all reachable residual states for one fixed variable order.

The validated executable retains its pre-admission filename for exact replay:

```text
experiments/direct/janus_c037_explicit_residual_obdd_alignment.py
```

The logical cycle identifier is `C036.1`; `C037` is reserved for Horn-affine negotiation.

## Constructive theorem

For a fixed variable order and an explicitly generated exact layered residual graph with `M` represented states, deterministic bottom-up refinement constructs:

1. the coarsest continuation-equivalence quotient;
2. one replayable distinguishing suffix for every pair of distinct quotient states at the same depth;
3. a complete SAT witness when the root reaches `TRUE`;
4. a replayable UNSAT quotient DAG when no accepting continuation exists.

Every transition is replayed by exact CNF restriction. No SAT or formula-equivalence oracle is used.

The full pairwise separator package has volume `O(Q^2 n)` for `Q` quotient nodes. State generation and separator volume have explicit budgets and return `OPEN` when exceeded.

## Exact alignment

For a fixed order:

```text
C036.1 continuation quotient
= minimal ordered residual automaton
= reduced OBDD.
```

This is an alignment with an existing representation, not a new width invariant.

## Exact controls

```text
Horn syntax under-merging:
raw states at depth 2       3
continuation classes        2

Equality EQ_n:
interleaved maximum width  <= 3
blocked width               = 2^n
n=8 blocked width           = 256
n=12 blocked construction   = OPEN on state budget

NAND3 + NEQ pressure:
source instances            250
explicit residual states    6088
quotient nodes              5232
merged states               856
replayed separators         5575
```

A corrupt separator is rejected independently. Finite controls validate the implementation only.

## Located obstruction

Partition refinement is polynomial after the exact transition graph exists. The graph itself can be exponential and strongly order-sensitive. Therefore the surviving gate is:

```text
POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION
```

An assumed equivalence-query teacher or supplied good order is not free.

## Numbering allocation

```text
C036   proof-carrying same-language partition refinement
C036.1 explicit residual / OBDD alignment
C037   Horn-affine negotiation
C037.1 proof-carrying parity-alias negotiation extension
C038   structured vtree decomposition
```

## Reproduction

```bash
python experiments/direct/janus_c037_explicit_residual_obdd_alignment.py --self-test
```

## Claim boundary

C036.1 is polynomial in the explicit residual graph and certificate volume, not necessarily in the source CNF. It does not construct a universally small quotient, find a universally good order, prove `P=NP`, or imply `P!=NP` from an order-specific OBDD explosion.

```text
P_VS_NP=OPEN
```
