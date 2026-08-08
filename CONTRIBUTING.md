# Contributing to JANUS Fundamentum

JANUS Fundamentum is a proof-search laboratory. The preferred contribution is not agreement; it is evidence that sharpens, breaks, reproduces, or correctly narrows a claim.

## Before opening a contribution

Read:

- [`README.md`](README.md)
- [`docs/CURRENT_RESEARCH_STATUS.md`](docs/CURRENT_RESEARCH_STATUS.md)
- [`docs/A3_PUBLICATION_TRACK.md`](docs/A3_PUBLICATION_TRACK.md) for the admitted A3 theorem
- [`docs/C023_FORMULA_CACHING_CALCULUS.md`](docs/C023_FORMULA_CACHING_CALCULUS.md) for the active C023 mainline

Always identify the exact commit, branch, theorem object, verifier, or publication target you are discussing.

## High-value contributions

### 1. Counterexample / proof defect

Please provide:

```text
TARGET_CLAIM = ...
TARGET_SHA = ...
MINIMAL_INSTANCE = ...
EXPECTED_BY_CLAIM = ...
OBSERVED = ...
REPRODUCTION_COMMAND = ...
```

A small explicit counterexample is preferred over a broad objection.

### 2. Independent reproduction

For A3, a strong reproduction should be clean-room where practical:

- implement from the theorem/specification rather than importing the existing implementation;
- identify language/runtime and dependency versions;
- report exact input fixtures and outputs;
- compare state counts, transition counts, endpoint values, and small-instance exhaustive controls;
- preserve discrepancies instead of normalizing them away.

Do not call a second run of the same implementation an independent implementation.

### 3. Prior art

Please include a stable bibliographic identifier when possible (DOI, arXiv identifier, journal citation, book/theorem reference) and explain the exact relation:

```text
EXACT_EQUIVALENT
DIRECT_COROLLARY
STRICTLY_STRONGER
STRICTLY_WEAKER
NEAR_NEIGHBOR
UNRELATED_AFTER_REVIEW
```

A report that a result "looks similar" is useful as a search lead but is not itself a novelty classification.

### 4. Verifier / provenance defect

Please state:

- the exact verifier/workflow path;
- the commit/tree you tested;
- the evidence object or binding that can be substituted, omitted, replayed, or misinterpreted;
- whether the defect changes mathematical truth, evidence strength, publication reproducibility, or only presentation.

### 5. Negative theorem result

A rigorous obstruction that kills a JANUS route is a successful research contribution. Preserve the counterexample or theorem and identify which descendants it invalidates.

## Permanent claim ceilings

Unless stronger evidence has actually been admitted, contributions and documentation must preserve:

```text
P_VS_NP = OPEN
A3_WORLD_NOVELTY_N4 = NOT_ESTABLISHED
A3_EXTERNAL_INDEPENDENT_REPLICATION = NOT_ESTABLISHED
C023_ASYMPTOTIC_LOWER_BOUND = OPEN
```

Do not use phrases such as "P vs NP solved", "world first", or "externally replicated" unless the repository has a specific admitted evidence object that establishes that exact statement.

## Pull requests

A research PR should explain:

1. the claim or gate it changes;
2. the exact predecessor state;
3. new proof/code/evidence objects;
4. attacks performed;
5. remaining blockers;
6. the strongest statement that is **not** established.

Prefer reproducible commands and machine-readable fixtures over screenshots.

## Scientific disagreement

Criticism of the mathematics, implementation, assumptions, novelty search, or verification architecture is welcome. Keep discussion centered on claims, evidence, and reproducible counterexamples.
