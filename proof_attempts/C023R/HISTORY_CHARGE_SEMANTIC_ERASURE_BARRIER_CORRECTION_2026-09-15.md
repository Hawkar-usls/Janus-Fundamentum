# C023R correction — semantic irrelevance is not byte-CNF elimination

Date: 2026-09-15
Authority: `HQ_PRE_RUN_SELF_CORRECTION__REPRESENTATION_FIREWALL`

Parent artifact being corrected:

`HISTORY_CHARGE_SEMANTIC_ERASURE_BARRIER_2026-09-15.md`

No new execution run or asymptotic family data was observed between the parent note and this correction.

## Error

The parent note correctly observed that two equal assigned coordinates force a MAJ3 output and make the third coordinate **semantically irrelevant** to the Boolean relation.

It then made an invalid representation step: it claimed that canonical exact truth-table restriction therefore removes the remaining irrelevant coordinate from the source residual CNF and that different choices of forcing pair yield the same byte-level source CNF.

That implication is false for the frozen JANUS representation.

`canonical_cnf` removes tautologies and exact duplicate clauses. It does not perform existential variable projection, subsumption elimination, or semantic minimization.

## Exact counteranalysis

Let `Q(Y)` be the residual relation on all other variables after a MAJ3 block has been forced to a constant. Let `x` be the third, unassigned coordinate of that block. The restricted Boolean relation is independent of `x`:

`P(x,Y) = Q(Y)`.

But the exact truth-table blocking CNF over the **remaining variable set `{x} union Y`** contains, for every falsifying row `y` of `Q`, two blockers:

`B_y union {x}`

and

`B_y union {-x}`.

These clauses are neither identical nor tautological. Frozen canonicalization therefore retains both. It does not replace them by the shorter blocker `B_y`.

Consequently, for a block `(a,b,c)` forced to output zero:

- history `a=0,b=0` leaves paired source blockers labelled by `c`;
- history `a=0,c=0` leaves analogous paired blockers labelled by `b`.

The two restricted **relations** are semantically equivalent after forgetting the irrelevant coordinate, but the two historical byte CNFs are not equal because different variable IDs remain syntactically present.

## Retraction boundary

The following strong claims from the parent note are RETRACTED:

- that equal-pair forcing witnesses on different coordinate pairs directly induce the same exact source-residual CNF;
- the derived `3^|F|` byte-CNF forcing-witness fibre claim;
- any inference from that claim to cache-key ambiguity.

The following earlier results remain valid and are not retracted:

- the MAJ3 partial-restriction truth table as a statement about Boolean functions;
- `01/10` equality when the same two coordinate positions are fixed and the same third coordinate remains live;
- incidence-syndrome / cycle-space semantic quotient for fully eliminated edge outputs;
- `SEMANTIC_PREIMAGE_CAPACITY != EXECUTION_FIBER`;
- the expander boundary/stifling history-charge theorem.

## Correct replacement insight

The frozen redundant truth-table representation can itself preserve the identity of an otherwise irrelevant coordinate. This is potentially a **positive fingerprint resource** rather than an erasure mechanism.

However, the same redundancy creates a precise merge opportunity once the irrelevant coordinate is actually branched or otherwise fixed:

for a relation `P(x,Y)=Q(Y)`, exact restriction by either `x=0` or `x=1` yields the same exact truth-table CNF `C(Q)` over `Y` after `x` is removed.

Thus an execution state containing a semantically irrelevant but syntactically represented variable `x` has a potential exact sibling merge:

`child_key(x=0) = child_key(x=1)`

provided inherited/non-source clauses are also value-symmetric under the two restrictions and subsequent pre-UP.

This is a much cleaner execution object because both children are automatically reachable from the same deterministic branch state whenever Policy-0A selects `x`.

## New nearest gate

`C023R_STIFLED_IRRELEVANT_VARIABLE_SIBLING_MERGE`

Two obligations:

1. **branch capture:** prove when frozen Policy-0A selects the remaining irrelevant coordinate of a stifled MAJ3 block;
2. **metadata symmetry:** prove whether every inherited/non-source clause restricts/canonicalizes identically under `x=0` and `x=1`, or identify the exact asymmetric clause that prevents the merge.

If both hold, one exact sibling merge cell is certified without any alternate-variable reachability assumption.

Linear serial composition remains a separate later obligation.

## Status

`PARENT_STRONG_BYTE_ERASURE_CLAIM_RETRACTED_BEFORE_RUN__SEMANTIC_RESULTS_PRESERVED__SIBLING_MERGE_GATE_OPEN`

## Claim ceiling

No exponential cache fibre, Policy-0A lower bound, C022 H137 promotion, SAT result or P-vs-NP result follows from this correction.
