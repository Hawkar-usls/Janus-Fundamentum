# C023R — history-charge semantic-erasure barrier

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_THEOREM_NOTE__NO_GLOBAL_PROMOTION`

## Purpose

Combine two already established C023R facts without silently promoting either beyond its scope:

1. the expander boundary/stifling/width theorem: a narrow boundary implicate over a large connected provenance region requires the execution history to have already assigned linearly many boundary gadget coordinates;
2. the exact MAJ3 restriction/syndrome lemmas: the source-semantic restriction map is many-to-one.

The question is whether the linear **history charge** can itself be treated as evidence of cache-history injectivity. The answer is no: history charge and source-semantic retention are different quantities.

## Lemma 1 — a forced MAJ3 output does not retain its forcing-pair identity

Let one lifted edge block be `(a,b,c)` with `M=MAJ3(a,b,c)`.

For target output `0`, each of the three partial assignments

- `a=0,b=0`,
- `a=0,c=0`,
- `b=0,c=0`

forces `M=0` for every completion of the remaining coordinate.

For target output `1`, each of

- `a=1,b=1`,
- `a=1,c=1`,
- `b=1,c=1`

forces `M=1` for every completion.

Under any one of these restrictions the remaining third coordinate is semantically irrelevant to every vertex relation containing this block. Because the JANUS source encoding is an exact truth-table CNF and exact restriction commutes with that encoding, canonical source restriction removes the entire block dependence and retains only the same forced output contribution.

Hence for a fixed forced output bit `z`, the exact source-semantic residual cannot distinguish which of the three equal-coordinate pairs supplied the two-assignment forcing witness.

This is a three-to-one semantic quotient at the level of forcing-witness identity. It is not an execution-reachability claim.

## Lemma 2 — product forcing-witness multiplicity

Let `F` be any set of pairwise distinct MAJ3 edge blocks. Fix one output vector

`z in {0,1}^F`.

For every block `e in F`, choose one of the three equal-coordinate pairs and assign that pair the value `z_e`. Leave the third coordinate unassigned.

There are exactly

`3^|F|`

such pair-choice partial assignments.

Hold all restrictions outside `F` fixed. Every one of the `3^|F|` histories forces the same block-output vector `z`, makes every third coordinate inside `F` irrelevant, and therefore induces the same exact source-semantic residual CNF after canonical restriction.

Thus the source restriction map has a forcing-witness fibre of size at least

`3^|F|`

for this fixed output vector.

Again, this is a semantic/preimage statement. Frozen Policy-0A may visit only a subset of these pair-choice histories.

## Lemma 3 — output-vector information can be erased further by Tseitin syndrome

If a set `H` of lifted edge blocks is fully eliminated with fixed effective outputs `z`, the remaining Tseitin source relations remember those outputs through the incidence syndrome

`B_H z`.

Therefore output vectors differing by an element of `ker(B_H)` induce the same remaining source parity relations when all non-eliminated restrictions are fixed.

For undirected `H`, the kernel dimension is the cycle rank

`beta(H)=|E(H)|-|V(H)|+c(H)`,

so one attainable syndrome has `2^beta(H)` output-vector preimages.

This is the previously established cycle-space semantic quotient. It is independent of the new three-way forcing-pair quotient in Lemma 2.

## Theorem — expansion history charge does not imply source-residual injectivity

Let a connected provenance region `Q` have boundary `delta(Q)`, and let `C` be a boundary-only implicate of width `W` under history `alpha`.

The established expander/stifling theorem gives at least

`|delta(Q)| - W`

already-forced boundary blocks and at least

`2(|delta(Q)|-W)`

assigned boundary coordinates.

This lower bound is a **cost paid by the history**. It does not imply that the exact source residual remembers those assignments.

Indeed, for each forced block with fixed output, Lemma 1 exhibits three distinct two-coordinate forcing witnesses with the same source-semantic effect. For any chosen set of `f` such blocks and fixed forced output vector, Lemma 2 gives `3^f` source-semantic forcing-witness preimages. If fully eliminated outputs also vary inside an incidence-syndrome coset, Lemma 3 supplies a further independent source-semantic quotient.

Therefore no implication of the form

`large |alpha_boundary|  =>  near-injective source residual history`

is valid from the expansion charge theorem alone.

In particular, the bound

`|Q| <= |alpha_boundary| + 2W`

cannot by itself upper-bound cache-fibre multiplicity.

## What the theorem does NOT prove

It does **not** prove an exponential Policy-0A cache fibre.

The execution policy fixes numeric branch order dynamically through clause frequencies, unit consequences and inherited deterministic Resolution. It may realize only one forcing-pair witness per block, or inherited clauses may retain enough information to distinguish histories that the source-semantic relation forgets.

Thus

`SOURCE_SEMANTIC_PREIMAGE_CAPACITY != REACHABLE_EXECUTION_FIBER`.

The theorem only removes one invalid positive route: history charge cannot be reinterpreted as history retention without a separate execution-specific proof.

## Consequence for Captain Obvious

The nearest missing link is no longer the broad statement

`HISTORY_CHARGE_TO_CACHE_FIBER_INJECTIVITY`.

It sharpens to the only possible rescue channel left after source-semantic erasure:

`C023R_INHERITED_METADATA_RETENTION_OF_ERASED_FORCING_WITNESS_BITS`

Exact question:

> For histories actually reachable under frozen Policy-0A, do inherited non-source clauses / the at-most-one partial-pivot asymmetry / deterministic transition consequences encode all but `o(L)` of the forcing-pair and syndrome degrees of freedom that the source-semantic residual erases?

Positive target:

`REACHABLE_ERASED_HISTORY_AMBIGUITY = o(L)`

in information bits, sufficient for a `2^{o(L)}` cache-fibre ceiling.

Decisive falsifier:

an explicit infinite symbolic family of reachable histories carrying `Omega(L)` independent erased forcing-witness/syndrome bits while producing the same byte-identical historical key.

## Verdict

`PASS_HISTORY_CHARGE_SEMANTIC_ERASURE_BARRIER__EXECUTION_METADATA_RETENTION_OPEN`

## Claim ceiling

- no Policy-0A lower bound is proved;
- no exponential cache fibre is proved;
- C022 H137 remains source-blocked by the unavailable primary lifting theorem text under GitHub-only execution;
- `P_VS_NP = OPEN`.
