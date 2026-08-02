# C038 — Proof-Carrying Recursive Separator Compiler

**Status:** `CONSTRUCTIVE RESTRICTED STRUCTURED COMPILER / P_VS_NP=OPEN`

## Purpose

C037A identified exact fixed-order partition refinement with reduced OBDD
minimization. C037B independently added a one-way Horn–affine separator and a
proof-carrying shared-literal negotiation trace.

C038 moves beyond one linear variable order. It constructs one recursive
assignment-independent separator plan, converts it to one vtree, and compiles the
CNF along that fixed structure.

The cycle does not assume that a good vtree is supplied for free.

## Admitted structure

Fix constants:

```text
maximum separator size k
constant base-table arity b
balance ratio 2/3
```

At every primal-graph region, the plan builder performs exactly one of:

1. split disconnected components;
2. accept a base region of at most `b` variables;
3. enumerate separators of size at most `k` and choose the first separator `S`
   such that every component of `G-S` contains at most `2|V|/3` variables;
4. return `OPEN` when no separator is found.

The plan is completed before any truth assignment is explored.

## Fixed-vtree property

A separator node is converted into a vtree whose root separates:

```text
the variables of S
from
the recursively decomposed components of G-S.
```

All `2^|S|` branches use this same plan. Branch-specific vtree selection is
forbidden.

This matters because independently choosing a new decomposition after every
assignment would not establish one structured circuit.

## Compilation

For every separator assignment `a`:

1. restrict the formula by `a`;
2. reject the branch immediately if an empty clause appears;
3. partition the residual clauses among the predetermined components;
4. compile each component against its fixed child plan;
5. combine the child circuits by decomposable AND.

The separator assignments form a complete disjoint partition, so their OR is
deterministic.

Base regions are represented by constant-size truth tables.

The resulting macro DAG expands into a deterministic structured decomposable
circuit respecting the recorded vtree.

## Constructive theorem

For every fixed separator bound `k`, formulas admitted by the recursive plan are
compiled exactly with:

```text
deterministic construction
one independently checkable vtree
replayable CNF restrictions
decomposable component joins
complete deterministic separator branches
SAT witness recovery
UNSAT certification by the exhaustive branch DAG
```

Let the child component sizes be `n_1,...,n_r`, with

```text
sum n_i <= n
max n_i <= 2n/3.
```

The circuit-size recurrence is bounded by:

```text
T(n) <= 2^k * sum_i T(n_i) + poly(n).
```

For a sufficiently large constant `q=O(k)`:

```text
sum_i n_i^q
<= (2n/3)^(q-1) * n,
```

and `2^k(2/3)^(q-1)<1`. Hence:

```text
T(n) = n^O(k).
```

Separator enumeration and certificate replay are also `n^O(k)`.

This is polynomial only when `k` is fixed. Allowing `k` to grow silently with
the input would invalidate the P-time claim.

## Verifier

The independent verifier checks:

- exact plan variable coverage;
- connected-component partitions;
- separator size and balance;
- vtree leaf set;
- every restricted branch formula;
- completeness and uniqueness of separator assignments;
- absence of clauses crossing planned component boundaries;
- every constant-size truth table;
- reconstructed SAT witnesses.

For UNSAT, the same verified DAG proves that every separator assignment ends in
a false child.

## Frozen audit

```bash
python experiments/direct/janus_c038_recursive_separator_compiler.py --self-test
```

Random audit:

```text
cases                  600
EXACT                  559
OPEN                   41
SAT mismatches         0
witness failures       0
verification failures  0
plan nodes checked     2183
circuit nodes checked  4500
```

Large tree-structured control:

```text
variables        127
plan nodes       113
separator nodes  33
circuit nodes    316
branches         118
```

Negative controls:

```text
dense clique primal graph  -> NO_BALANCED_SEPARATOR
explicit node budget       -> NODE_BUDGET
corrupt branch assignment  -> REJECTED
```

Integrity:

```text
38ee7bc6a7d9917ae069824ca161a50b011e534ebb21331ce5b53d1a65ccae8e
```

Finite tests validate the implementation. They are not the universal proof.

## Equality order separation

For

```text
EQ_n = AND_i (x_i <-> y_i)
```

the blocked OBDD order

```text
x_1,...,x_n,y_1,...,y_n
```

has exactly `2^n` distinct residuals after the first block.

The recursive component plan discovers the `n` independent equality components
without an ordering guess.

At `n=12`:

```text
blocked OBDD width       4096
structured plan nodes      13
structured circuit nodes   13
```

This does not lower-bound every OBDD: the interleaved order remains small. It
shows that recursive structure can remove one form of order sensitivity.

## Exact alignment with existing theory

C038 is not a new knowledge-compilation language.

Its positive theorem is a proof-carrying restricted instance of the known route:

```text
bounded recursive graph width
-> structured deterministic decomposable representation.
```

Published work gives constructive singly-exponential compilation from bounded
treewidth to d-SDNNF and SDD-style upper bounds. SDDs can also be exponentially
more succinct than OBDDs on selected functions.

C038 adds an executable JANUS implementation that explicitly charges plan
discovery, records one vtree, verifies every branch and returns `OPEN` outside
the admitted recursive-separator class.

## Decisive limitation

The dense pair-clause formula used as a negative control has a clique primal
graph and no size-one balanced separator, so C038 returns `OPEN`.

Yet the same formula is dual-Horn and is solved by C033.

Therefore:

```text
small primal separators are not a universal tractability criterion
```

even inside the existing JANUS portfolio.

Graph decomposition and symbolic message language must be selected jointly.

## Bottom-up warning

A small final structured representation does not imply that a naive bottom-up
`Apply` compilation keeps all intermediate objects small. Published lower bounds
show formulas with tiny final structured representations but unavoidable
exponential intermediate results for broad bottom-up compilation strategies.

C038 therefore certifies its own construction trace and never infers polynomial
construction from final representation size alone.

## New gate

```text
SEMANTIC_VTREE_DISCOVERY_BEYOND_GRAPH_SEPARATORS
```

The next mechanism must combine:

```text
graph separators
Horn / dual-Horn closure
affine row spaces
beta-acyclic elimination
PS signatures
cross-language facts from C037B
compiled messages
```

while charging decomposition discovery, message construction, joins,
projections, merge/separator proofs, witness recovery and UNSAT handling.

## Claim boundary

C038 proves an exact `n^O(k)` compiler for a fixed recursively discoverable
separator bound. It does not show that arbitrary CNF has bounded `k`, does not
globally optimize vtrees, does not solve unrestricted CNF, and does not resolve
P versus NP.

```text
P_VS_NP=OPEN
```
