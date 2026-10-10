# U-PAIR-1E — Factorized affine+OR symbolic elimination

Date: 2026-09-17

Status:
`SPLIT_GATE__QUANTIFIER_FREE_CLOSURE_FALSIFIED__AUXILIARY_FACTORIZATION_SURVIVES_AS_ENCODING_ONLY`

## Frozen gate

Representation: a factor graph whose factors are affine relations or bounded-arity OR relations.
Operations: exact conjunction and exact existential elimination.
Forbidden: full truth-table expansion and hidden enumeration of exponentially many affine components.
All intermediate descriptions were intended to remain polynomial.

The attack exposes a necessary distinction that the original gate did not make:
**quantifier-free elimination** versus **existential re-factorization with fresh auxiliaries**.

## 1. Exact wide-OR projection killer

For visible Boolean variables x_1,...,x_n introduce prefix auxiliaries q_i and encode

q_i <-> (q_{i-1} OR x_i)

with the standard three clauses

(not q_{i-1} OR q_i)
(not x_i OR q_i)
(q_{i-1} OR x_i OR not q_i).

Require q_n=1. The construction has O(n) variables/clauses and every clause has width at most 3.
After the ordinary pair-selector compilation, it is a PAIR+positive-OR_3 factor graph.

Existentially eliminating the q variables yields exactly

OR_n(x_1,...,x_n).

### Theorem A — no quantifier-free same-grammar representation

Let P be the PAIR affine subspace on visible selectors {t_i,f_i}, with f_i=1-t_i.
Let p0 be the all-false x assignment (all t_i=0, all f_i=1).
The desired relation is P \ {p0}.

For n>3, no conjunction of affine factors and positive OR factors of arity <=3
over only the surviving selector variables represents P \ {p0}.

Proof.

1. Any affine factor valid on all P\{p0} is also valid on p0.
   Indeed, for n>=2 the affine hull of P\{p0} is P.

2. Consider a positive OR factor of width <=3 that is false at p0.
   It cannot contain any f_i, since every f_i=1 at p0. Hence it contains only t_i.
   Since its support has at most 3 indices and n>3, choose j outside the support and set
   x_j=1 with every support variable false. This is a valid nonzero assignment in P\{p0},
   but it still falsifies the factor.

Thus no allowed individual factor can exclude p0 while accepting every desired model.
A conjunction that excludes p0 would need at least one such factor. Contradiction. QED.

Verdict:

`FAIL_QUANTIFIER_FREE_AFFINE_PLUS_BOUNDED_OR_CLOSURE_UNDER_EXISTENTIAL_ELIMINATION`.

## 2. Expander interleave attack on ordinary variable elimination

For standard exact factor elimination, eliminating a variable multiplies/combines
all factors containing it and projects it out. The maximum generated factor scope
under an order is the induced width; minimizing over orders gives treewidth.

Bounded-degree expander families have treewidth Omega(n) by the separator/treewidth
connection. A sparse affine expander backbone therefore forces an Omega(n) scope
under every ordinary elimination order. Injecting bounded-arity OR_3 factors between
distinct affine neighborhoods preserves the backbone.

Hence the preregistered CONNECTED_MIXED_AFFINE_OR3_EXPANDER_INTERLEAVE family kills
any backend whose symbolic factor is actually materialized as a table over its scope:
some intermediate table has 2^Omega(n) Boolean entries.

Verdict:

`FAIL_STANDARD_TABULAR_FACTOR_ELIMINATION_ON_EXPANDER_INTERLEAVE`.

Claim ceiling: treewidth/scope does not lower-bound every symbolic representation.
A wide affine factor can remain compact as a linear equation system.

## 3. Why the broad factorized gate survives vacuously

The wide OR relation itself has an O(n)-size factorization if fresh existential
prefix auxiliaries are allowed. Therefore "polynomial-size factor graph after projection"
is not enough: one may simply reintroduce the eliminated semantic information under
fresh names.

This preserves a compact **encoding**, not a polynomial-time **decision procedure**.

So U-PAIR-1E cannot honestly be marked either universal PASS or universal FAIL until
the representation/progress semantics are made operational.

## 4. Successor gate

`U-PAIR-1F__AUXILIARY_SAFE_SYMBOLIC_PROGRESS_AND_TERMINALIZATION`

A candidate must freeze:

- the exact representation grammar;
- whether fresh auxiliaries are allowed;
- an auditable progress potential that strictly decreases;
- polynomial bounds on every step and every intermediate object;
- polynomially many steps to a variable-free TRUE/FALSE terminal;
- SAT witness reconstruction and independent UNSAT replay.

A concrete next candidate is preferable to another umbrella class:
GF(2) affine row-space normalization + shared-DAG OR factors, with no truth-table expansion
and with a frozen auxiliary/progress accounting rule.

Firewall:
`GENERAL_SAT_IN_P = NOT_PROVED`
`P_VS_NP = OPEN`
