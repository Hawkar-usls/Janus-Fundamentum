# TRUMP Bicameral Pair-Separator Explanation — scoped theorem

Authority: `SCOPED_THEOREM__NO_GLOBAL_PROMOTION`

Frozen lineage: `research/trump-bicameral-pair-separator-2026-09-15`

Preregistration: `b0d08ba3a8fc0c3008a3595d275d0a7bb3e2c78b`

Candidate: `edfaabb0da23c4bd7f227a878ee852d3335a6a14`

Independent checker: `4569ab71bf9fd05169236620859cfac52ce6eb2a`

Workflow head: `24af9a7ce126a594e5bf8b1c5e1b8e9b8bb6c039`

Actions run: `34915069368`

Actions job: `104210825463`

## Scoped theorem

Let `F` be a raw explicit Boolean-relation object admitted by the frozen input grammar. Let `S={u,v}` be an unordered pair of variables discovered solely from the raw variable–constraint incidence graph such that removing `u` and `v` separates the constraint-bearing incidence graph into at least two components.

For every assignment `sigma in {0,1}^S`, construct the exact simultaneous relational restriction `F|S=sigma` by filtering every explicit allowed-tuple relation and deleting the assigned coordinates. A branch whose relation becomes empty is exact UNSAT; a branch with no residual constraints is exact trivial SAT; every other branch is independently replayed through the already sealed raw compositional-basis inducer.

If all four branches are admitted by one of those exact terminals, then the pair proposal is an exact structural explanation and:

`SAT(F) <=> OR_{sigma in {0,1}^S} SAT(F|S=sigma)`.

The explanation is content-bound to the canonical raw object, incidence observation, pair proposal, four restriction receipts, and independent replay receipts.

## Discovery/resource bound

The frozen proposal library enumerates every unordered variable pair: at most `V(V-1)/2` candidates. Each candidate has exactly four Boolean assignments. Incidence separation, explicit tuple restriction, certificate construction, and the sealed explicit-table basis replay are polynomial in the explicit input length. Therefore the complete discovery/admission lifecycle for **fixed separator size 2** is polynomial in the explicit relation-table input length.

This theorem does **not** establish polynomial discovery for growing separator size. Enumerating all subsets of size `O(log L)` naively would itself introduce superpolynomial discovery cost; no such inference is permitted.

## Frozen control outcome

The prior single-variable biconnected control `OR2([0,1]) + EVEN_XOR3([0,1,2])` has no admissible single-variable articulation explanation. Blind pair discovery finds exactly `{0,1}`. Its four branch replays are:

- `00 -> EXACT_UNSAT_BY_EMPTY_RELATION`
- `01 -> ADMIT_BRANCH_EXACT_BASIS_PORTFOLIO`
- `10 -> ADMIT_BRANCH_EXACT_BASIS_PORTFOLIO`
- `11 -> ADMIT_BRANCH_EXACT_BASIS_PORTFOLIO`

A mixed control in which the two constraints share all three variables has no one- or two-variable incidence separator and remains `OPEN_NO_EXACT_PAIR_SEPARATOR_EXPLANATION`.

## Verdict

`PASS_SCOPED_BICAMERAL_TWO_VARIABLE_SEPARATOR_EXPLANATION_INDUCTION`

## Permanent firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- `CONNECTED_MIXED_CORE_SOLVED = NO`
- `ARBITRARY_UNSEEN_INVARIANT_DISCOVERY = NOT_PROVED`
- `GROWING_SEPARATOR_DISCOVERY = NOT_PROVED`
- `GLOBAL_APMA_FRONTIER_ADVANCE = NONE_PENDING_HQ_REVIEW`
