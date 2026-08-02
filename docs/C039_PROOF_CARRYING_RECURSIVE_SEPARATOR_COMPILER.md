# C039 — Proof-Carrying Recursive Separator Compiler

**Status:** `CONSTRUCTIVE RESTRICTED SYMBOLIC FACTOR CONSTRUCTION / P_VS_NP=OPEN`

## Canonical numbering

The implementation was first committed under `C038` before the parallel exact
vtree-factor alignment reserved canonical cycle `C038`.

Canonical allocation is now:

```text
C036   same-language proof-carrying refinement
C036.1 Horn-affine negotiation
C037   explicit residual OBDD alignment
C038   exact structured-vtree factor alignment
C039   fixed-k symbolic recursive separator compiler
```

The old branch and implementation files retain their original `c038` spelling
only as replayable legacy aliases. The canonical executable is:

```bash
python experiments/direct/janus_c039_recursive_separator_compiler.py --self-test
```

## Constructive theorem

Fix constants `k` and `b`. The constructor builds one assignment-independent
recursive plan from the CNF primal graph:

```text
disconnected components
or a balanced separator S with |S| <= k
or a base table with at most b variables
or OPEN
```

The full plan and its vtree are fixed before branching over any truth values.
Every separator branch reuses the same child plans.

For admitted formulas, the generated macro DAG is deterministic and structured
decomposable:

- separator assignments give mutually exclusive OR branches;
- residual components have disjoint variable sets and give decomposable ANDs;
- base regions use constant-size truth tables;
- all restrictions and component partitions are independently replayable.

The recurrence

```text
T(n) <= 2^k * sum_i T(n_i) + poly(n)
```

with `max n_i <= 2n/3` and `sum n_i <= n` gives

```text
T(n) = n^O(k)
```

for fixed `k`. The claim is not polynomial when `k` is allowed to grow silently
with the input.

## Proof objects

The verifier checks:

```text
plan variable coverage
separator size and balance
one vtree leaf set
complete separator assignments
exact CNF restriction
no clause crossing a child component
constant-size truth tables
SAT witness reconstruction
UNSAT exhaustive branch DAG
```

## Frozen audit

```text
600 random formulas
559 EXACT
41 OPEN
0 SAT mismatches
0 witness failures
0 verification failures

127-variable tree control
113 plan nodes
316 circuit nodes

EQ_12 blocked OBDD width  4096
C039 structured nodes        13

clique-primal control       OPEN
node-budget control         OPEN
corrupt branch certificate  REJECTED
```

The finite audit validates the implementation only.

## Relation to C038

C038 constructs exact continuation-row quotients for a supplied/heuristically
constructed vtree, but explicitly enumerates factor tables.

C039 gives a first restricted symbolic construction that avoids enumerating all
cut rows: it branches only over recursively found separators of fixed size and
composes the resulting component messages.

Thus C039 is a genuine constructive subcase of the C038 gate, not a competing
renaming.

## Decisive limitation

A dense positive pair-clause formula has clique primal graph, so C039 cannot find
a small separator and returns `OPEN`. The formula is dual-Horn and is solved by
C033.

Therefore graph separators alone cannot be the universal selector. The next
route must discover **semantic** structure using the complete portfolio:

```text
Horn / dual-Horn closure
affine row spaces
beta-acyclic elimination
PS signatures
C036.1 cross-language facts
structured compiled messages
```

## Active gate

```text
SEMANTIC_VTREE_DISCOVERY_BEYOND_GRAPH_SEPARATORS
```

## Claim boundary

C039 is exact and proof-carrying on the fixed-k admitted family. It does not show
that arbitrary CNF has fixed `k`, does not solve unrestricted SAT and does not
resolve P versus NP.

```text
P_VS_NP=OPEN
```
