# C037 — Explicit Residual Automaton / OBDD Alignment

**Status:** `CONSTRUCTIVE CONDITIONAL THEOREM / P_VS_NP=OPEN`

## Purpose

C036 proves complete polynomial separator extraction inside Horn and affine
message languages when the residual objects are already available.

C037 asks the next exact question:

> If all reachable exact residual states are generated explicitly, can
> proof-carrying partition refinement recover the complete continuation quotient
> without a SAT or formula-equivalence oracle?

The answer is yes. The resulting quotient is not a new representation. It is
exactly the reduced ordered binary decision diagram (OBDD), or equivalently the
minimal ordered residual automaton, for the selected variable order.

## Ordered residual machine

Let a CNF `F` have variable order

```text
pi = (x1, ..., xn).
```

At depth `i`, every prefix assignment `alpha` induces the exact residual

```text
F | alpha.
```

The transition on the next bit is exact restriction:

```text
delta(F | alpha, b) = F | (alpha union {xi+1 = b}).
```

C037 stores normalized residual CNFs. Restriction only deletes satisfied clauses
and assigned literals, so every transition and its construction record are
polynomial in the source size.

The number of distinct reachable residuals is not assumed polynomial.

## Constructive theorem

Suppose the explicit layered residual graph contains `M` states and every state
and transition has polynomial representation and replay cost.

Then C037 deterministically constructs:

1. the coarsest continuation-equivalence partition;
2. one explicit distinguishing suffix for every pair of distinct quotient
   states at the same depth;
3. a SAT witness when the root reaches `TRUE`;
4. a replayable UNSAT DAG certificate when every root continuation reaches
   `FALSE`.

The implementation emits a full pairwise separator package. Its volume is

```text
O(Q^2 * n)
```

for `Q` quotient nodes. This remains polynomial whenever the explicit quotient is
polynomial.

The procedure returns `OPEN` when the explicit-state or separator-volume budget
is exceeded.

## Why the quotient is exact

At the final layer, states are partitioned by the constants `TRUE` and `FALSE`.

Inductively, two states at depth `i` are placed in one class exactly when their
`0`-children and `1`-children belong to the same classes at depth `i+1`.

Thus they agree on every remaining assignment. Conversely, two distinct classes
have different child signatures. Following one differing child recursively
produces a concrete suffix that separates their outputs.

No general SAT query and no formula-equivalence query appears in this induction.

## Exact alignment with OBDD

For a fixed order, an OBDD node represents one residual Boolean function after a
prefix assignment. Reduced OBDDs merge nodes precisely when those residual
functions are equal.

Therefore:

```text
C037 continuation quotient
  = minimal ordered residual automaton
  = reduced OBDD for the selected order.
```

C037 is registered as an alignment result, not as a newly invented width
parameter.

## C036 versus C037

C036 performs symbolic separator extraction directly inside Horn and affine
languages. It need not enumerate every continuation.

C037 is language-agnostic once an exact finite transition graph has been built.
It computes the complete quotient and separating continuations, but its cost is
polynomial in the explicit graph rather than necessarily in the original CNF.

The two results expose different costs:

```text
C036: separator discovery inside a closed symbolic language
C037: exact minimization after explicit state generation
```

## Horn syntax under-merging control

For

```text
(-x3) AND (-x2) AND (-x1 OR x3)
```

the exact residual graph has three syntactically different states at depth two,
but only two continuation classes.

Frozen result:

```text
raw states at depth 2       3
quotient states at depth 2  2
merged syntax states        1
```

The partition refinement merges the two different always-false residuals without
calling formula equivalence. Their transition behavior supplies the proof.

## Order-sensitive equality family

Let

```text
EQ_n = AND_i (xi <-> yi).
```

### Interleaved order

```text
x1, y1, x2, y2, ..., xn, yn
```

has quotient width at most three: one false sink and at most two active
expectation states.

### Blocked order

```text
x1, ..., xn, y1, ..., yn
```

has width exactly

```text
2^n
```

after the `x` block. Every assignment `a` to the `x` variables leaves the unique
residual

```text
AND_i (yi = ai).
```

Two different prefixes are separated by the continuation `y=a`, so all `2^n`
residual functions are distinct.

Machine audit:

```text
n=8 interleaved maximum width  3
n=8 blocked maximum width      256
n=8 blocked explicit states    774
n=12 blocked budget control    OPEN
states before OPEN             1023
largest completed width        512
```

This is an exact order-specific OBDD lower bound, not a lower bound against all
algorithms and not evidence for `P!=NP`.

## NAND3 + NEQ pressure

C037 was also tested on the C023/C034 witness-preserving image of random 3-CNF in
Horn NAND3 clauses plus complement equations encoded as NEQ clauses.

```text
source cases                   250
explicit residual states       6088
exact quotient nodes           5232
states merged by refinement    856
cases with a strict merge      201
separators replayed            5575
maximum state/quotient ratio   2.666667
```

For every layer of every small fixture, the computed quotient count was checked
against exhaustive continuation vectors. These finite controls validate the
implementation only.

## Proof-carrying outputs

Every accepted package contains:

- the exact normalized root;
- every residual state;
- both restriction transitions from every nonterminal state;
- the continuation class of every state;
- a representative for every class;
- one separating suffix and terminal labels for every distinct class pair;
- either a complete SAT assignment or a quotient DAG proving that the root has
  no path to `TRUE`.

A corrupt separator is rejected independently.

```text
UNSAT control verified: TRUE
corrupt separator:      REJECTED
```

## The active obstruction

C037 proves that partition refinement itself is not the missing exponential
miracle.

The missing work occurs before or around refinement:

```text
choose an order or decomposition
choose a closed exact message language
generate the reachable message graph
keep its nodes and certificates polynomial
```

New gate:

```text
POLYNOMIAL_ORDER_DECOMPOSITION_AND_REACHABLE_QUOTIENT_CONSTRUCTION
```

A procedure that simply enumerates the full residual automaton has only moved
the exhaustive search into state generation.

## Learning-theory warning

Angluin-style active learning is polynomial in the size of the minimal automaton
when supplied with membership and equivalence-query answers and counterexamples.

For SAT interfaces, an assumed teacher that produces a separating continuation
for an arbitrary wrong quotient is precisely an uncharged oracle unless that
counterexample-generation procedure is independently constructed and costed.

C036 supplies such construction for same-language Horn and affine pairs. C037
supplies it after the complete explicit transition graph exists. Neither result
yet supplies a universal polynomial teacher.

## Next target

### C038 — Proof-Carrying Structured Decomposition Search

A linear variable order is too restrictive. The next constructive step should
replace the OBDD path order by a verified recursive decomposition such as a
vtree / structured DNNF interface, while preserving:

```text
polynomial decomposition discovery
polynomial message construction
replayable joins and projections
explicit separator or merge evidence
SAT witness recovery
independently checkable UNSAT handling
strict OPEN on budget exhaustion
```

The route must compare against existing SDD, d-SDNNF and width results before
introducing any new object.

## Reproduction

```bash
python experiments/direct/janus_c037_explicit_residual_obdd_alignment.py --self-test
```

Integrity:

```text
b367d0b765228c23dac18d53d85e676ebbcaba59e2ad230c6c917565119d25df
```

## Claim boundary

C037 proves an exact proof-carrying compiler conditional on a polynomial explicit
reachable residual graph. It does not prove that such a graph or a suitable order
exists for arbitrary CNF and does not resolve P versus NP.

```text
P_VS_NP=OPEN
```
