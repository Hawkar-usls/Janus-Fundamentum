# C040 — Portfolio-Guided Semantic Vtree Discovery Contract

```text
STATUS = SPECIFICATION_IMPLEMENTED / DRAFT
P_VS_NP = OPEN
```

## Purpose

C039.0 receives a supplied, verified vtree and validates proof-carrying symbolic
factor operations. C040 defines the missing discovery envelope: construct and
select one assignment-independent vtree without treating a supplied good tree,
a width oracle, a hidden truth table, or branch-dependent search as free.

This cycle is a contract and structural validator. It does not prove that the
registered candidate portfolio contains a polynomially compiling vtree for every
CNF.

## Compiler capability ladder

```text
C039.0  symbolic-factor operation contract
C039.1  pure-affine symbolic vtree factors
C039.2  single-head Horn symbolic projection
C039.3  low-affine-dimension Horn/dual-Horn plus affine composition
C040    portfolio-guided semantic-vtree discovery
C041    joint compiler/portfolio completeness
```

A C040 result is meaningful only relative to the exact compiler capability digest.
Adding C039.2, C039.3 or a later message implementation can turn a previously
failing vtree into a complete `CLOSED_POLY` compile. Every older
`OPEN_PORTFOLIO_EXHAUSTED` record therefore becomes stale when the compiler ladder
changes.

## Bounded portfolio-selection theorem

Fix:

1. a deterministic candidate-constructor portfolio of polynomial cardinality;
2. polynomial feature, generation, probe, representation and certificate budgets;
3. a C039 compiler that either returns a replayable `CLOSED_POLY` certificate or
   an explicit `OPEN_*` terminal within its committed budget.

Then C040 can select the least-cost successful candidate in polynomial total work.
Every accepted vtree is sound because it is accompanied by a full C039 certificate.
If no frozen candidate closes, C040 returns `OPEN_PORTFOLIO_EXHAUSTED`.

This is a meta-theorem about safe selection. It is not a completeness theorem for
the candidate portfolio.

## Phase discipline

```text
canonical formula and capability
-> proof-carrying feature extraction
-> generate the entire candidate list
-> freeze and hash the candidate manifest
-> run exactly one bounded full C039 probe per candidate
-> select by deterministic certified cost tuple
```

No candidate may be created, rotated, repaired or replaced after a probe result is
observed. Candidate generation must be independent of SAT branch values and SAT or
UNSAT witnesses.

## Registered feature classes

```text
CLAUSE_INCIDENCE
EQUALITY_FOREST
FORCED_LITERAL_SET
AFFINE_ROW_SUPPORT
AFFINE_HULL_STATUS
HORN_HEAD_MAP
BETA_ELIMINATION_ORDER
EXACT_OPEN_TRACE
```

Every feature is bound to the exact formula and capability digest and carries a
native proof digest. `EXACT_OPEN_TRACE` is advisory only. It cannot certify
hardness, compatibility or the quality of a related formula or vtree.

Equality and affine-hull traces may guide clustering, but remain features rather
than decomposition proofs.

## Registered candidate constructors

```text
FIXED_CANONICAL_BASELINE_V1
BALANCED_PRIMAL_SEPARATOR_V1
CLAUSE_COOCCURRENCE_V1
EQUALITY_CONTRACTED_V1
AFFINE_SUPPORT_CLUSTER_V1
HORN_HEAD_DISJOINT_V1
BETA_ELIMINATION_V1
```

Registration means only that the constructor ID and generation proof are accepted
by the contract. It does not claim a universal quality bound for any constructor.

Each candidate contains:

```text
candidate ID and digest
constructor ID/version digest
exact feature references
generation proof digest
complete binary vtree over every formula variable
generated_before_probe = true
depends_on_assignment_values = false
```

The validator checks exact leaf coverage, unique variable occurrence, binary-tree
shape, connectedness, acyclicity and deterministic digesting.

## C039 probes

Every frozen candidate receives exactly one full C039 probe bound to:

```text
formula digest
capability digest
C039 contract digest
vtree digest
C039 certificate digest
terminal
max node representation
total representation
total work
```

Only `CLOSED_POLY` makes a candidate selectable. Partial prefixes, optimistic size
estimates, sampled rows and heuristic width scores are not enough.

Among successful candidates C040 chooses the lexicographically least tuple:

```text
(max_node_representation,
 total_representation,
 total_work_units,
 vtree_digest)
```

The final digest is a deterministic tie breaker.

## Terminals

```text
VTREE_SELECTED_CERTIFIED
OPEN_PORTFOLIO_EXHAUSTED
OPEN_DISCOVERY_BUDGET
OPEN_FEATURE_LANGUAGE
OPEN_CAPABILITY_STALE
INVALID_DISCOVERY_CERTIFICATE
```

`OPEN_PORTFOLIO_EXHAUSTED` means only that no candidate in this exact frozen
portfolio closed under this exact compiler capability and budget. It is not
evidence of intrinsic hardness and does not transfer by similarity or reduction.

## Vault boundary

A selected vtree with a full C039 certificate routes to `record_poly`. An `OPEN_*`
terminal routes to `record_open` only under the exact current capability digest.
Changing constructors, feature extractors, C039 language implementations or
budgets changes the capability and makes older OPEN records stale.

## Frozen prohibitions

```text
NO_SUPPLIED_VTREE_SUBSTITUTION
NO_BRANCH_DEPENDENT_VTREE
NO_ADAPTIVE_CANDIDATE_GENERATION_AFTER_PROBES
NO_EXACT_WIDTH_ORACLE
NO_HIDDEN_TRUTH_TABLE_OR_COMMUNICATION_ROWS
NO_GENERAL_SAT_FALLBACK
NO_PARTIAL_PROBE_PROMOTED_TO_SUCCESS
NO_OPEN_PROMOTED_TO_HARDNESS
NO_SIMILARITY_BASED_OPEN_TRANSFER
```

## Acceptance gate

```bash
python experiments/direct/janus_c040_portfolio_guided_vtree_contract.py --self-test
```

The deterministic checks cover:

```text
digest determinism
certified candidate selection
cost tie breaking
missing generation proof rejection
branch-dependent discovery rejection
adaptive post-probe candidate rejection
invalid vtree rejection
stale exact-OPEN feature rejection
all-open portfolio terminal
candidate and total-work budgets
hidden truth-table rejection
capability-locked Vault routing
```

## Immediate priority

```text
1. Integrate PR #55 / C039.2 into the C039 operation envelope.
2. Integrate PR #56 / C039.3 as a mixed-language probe capability.
3. Re-run the frozen C040 candidate portfolio under the enlarged capability.
4. Open C041 only on the exact residual OPEN frontier.
```

Starting C041 before these integrations would conflate a weak compiler with weak
vtree discovery.

## Surviving gate

```text
POLYNOMIAL_SEMANTIC_VTREE_CANDIDATE_COMPLETENESS
```

The next theorem must prove that one polynomially generated candidate family,
together with the admitted compiler capability, always contains a vtree whose
complete C039 compilation is polynomial, or provide a stronger adaptive
decomposition method that remains assignment-independent and charges every
generated candidate and intermediate representation.

A good vtree found only by exhaustive search, a supplied decomposition, or a
portfolio whose size exponent depends on the input does not pass this gate.

## Numbering note

The single-head Horn projector is canonically `C039.2`. The low-affine-dimension
Horn/affine composer is canonically `C039.3`; its legacy branch, executable,
proposal filenames and wire schema containing `c040` are replay aliases. `C040`
is reserved here for charged semantic-vtree discovery.

## Claim boundary

C040 supplies a sound polynomial selector for a fixed polynomial candidate
portfolio. It does not establish universal candidate completeness, solve arbitrary
CNF, or resolve P versus NP.

```text
P_VS_NP=OPEN
```
