# C023R — exact sibling-merge tail-balance criterion

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_LEMMA__NO_SCIENTIFIC_PROMOTION`

Parent correction:

`HISTORY_CHARGE_SEMANTIC_ERASURE_BARRIER_CORRECTION_2026-09-15.md`

## Setting

Let `S` be the exact canonical CNF immediately before historical Policy-0A branches on variable `x` (that is, after the state's local Resolution pass and post-unit propagation). Assume `S` is nonterminal and contains `x`.

Partition the canonical clauses of `S` into three disjoint classes:

- `N_x`: clauses not containing `x` or `-x`;
- `P_x`: clauses containing positive literal `x`;
- `M_x`: clauses containing negative literal `-x`.

Because clauses are canonical/non-tautological, no clause contains both signs of `x`.

Define the reduced tail sets

`T_+(x) = { C \ {x} : C in P_x }`

and

`T_-(x) = { C \ {-x} : C in M_x }`.

These are clause sets after exact canonical duplicate removal.

## Lemma 1 — exact raw children

Historical `simplify_one(S,x,False)` does exactly:

- keep every neutral clause in `N_x`;
- delete every negative-`x` clause because `-x` is true;
- remove false literal `x` from every positive-`x` clause.

Hence the false child before its recursive pre-UP is

`C_0 = canonical( N_x union T_+(x) )`.

Similarly the true child is

`C_1 = canonical( N_x union T_-(x) )`.

No proof provenance or semantic interpretation is needed for this identity.

## Theorem — byte-level sibling equality criterion before pre-UP

`C_0 = C_1`

iff

`T_+(x) \ N_x = T_-(x) \ N_x`.

Proof. Canonicalization at this point is set union plus exact duplicate removal. Therefore

`N_x union T_+(x) = N_x union T_-(x)`

iff the clauses contributed outside the already-common neutral set are equal. QED.

Call the symmetric difference

`A_x = (T_+(x) \ N_x) Delta (T_-(x) \ N_x)`

the **branch asymmetry basis** of `x` in state `S`.

Then

`A_x = empty`

is exactly equivalent to raw byte-identical siblings before child pre-UP.

## Corollary — exact cache merge after child pre-UP

Historical child recursion begins with deterministic exhaustive unit propagation. Therefore:

- `A_x=empty` is sufficient for the two child calls to reach the same cache key (or the same terminal outcome), because their raw child CNFs are byte-identical;
- `A_x != empty` does not by itself rule out a later merge, because distinct raw children can still be mapped by deterministic pre-UP to one identical propagated key.

Thus `A_x=empty` is an exact **strong merge certificate** requiring no unit-propagation reasoning.

The fully general sibling-cache criterion is

`UP(C_0) = UP(C_1)`

with identical contradiction/terminal status, but tail balance is the cheapest decisive sufficient condition.

## Lemma 2 — semantically irrelevant variable in an exact truth-table CNF is tail-balanced

Let relation `P(x,Y)` be independent of `x`:

`P(0,Y)=P(1,Y)=Q(Y)`.

In its exact truth-table blocking CNF, every falsifying row `y` of `Q` contributes exactly two blockers:

- one positive-`x` blocker with tail `B_y`;
- one negative-`x` blocker with the same tail `B_y`.

Therefore

`T_+(x)=T_-(x)`

for the source exact relation, so its branch asymmetry basis is empty.

This corrects the earlier representation mistake: the irrelevant variable is syntactically present before branching, but its two sign classes are perfectly tail-balanced.

## Lemma 3 — neutral clauses cannot create branch asymmetry

Adding any clause not containing `x` only enlarges `N_x`. It cannot introduce an element into `A_x`; it can only absorb an already-existing positive/negative tail if that exact tail becomes neutral.

In particular, Resolution **on pivot x itself** adds clauses that do not contain `x`. Such additions cannot create `x`-branch asymmetry and may reduce it by placing tails into `N_x`.

## Lemma 4 — complete source-only pivot closure preserves balance for a stifled irrelevant coordinate

The previously proved complete-source-pivot transparency theorem implies that fully processed source-only pivots produce additions whose restrictions are deterministic functions of the common restricted source relation.

For an already stifled block coordinate `x` that is semantically irrelevant, complete source-only additions do not break the source pair correspondence of Lemma 2. Additions neutral in `x` cannot create asymmetry by Lemma 3; additions containing `x` arise in matched source-semantic families under complete processing.

Therefore complete source-only Resolution does not by itself create a nonempty `A_x` for the irrelevant coordinate.

Any nonempty asymmetry basis at branch time must be attributable to incomplete/budget-truncated processing, inherited non-source clauses, cross-factor derived clauses, or their deterministic consequences.

## Exact metadata object

The earlier vague phrase "inherited metadata remembers the bit" is now replaced by a concrete byte-level object:

`A_x` — the unmatched positive/negative tail basis of the candidate irrelevant branch variable.

For one state:

- `A_x=empty` certifies an exact sibling merge before child UP;
- `A_x!=empty` identifies the exact clauses that encode value asymmetry and must be explained by frozen provenance.

## Captain Obvious next gate

`C023R_STIFLED_VARIABLE_BRANCH_CAPTURE_AND_ASYMMETRY_BASIS`

For a reachable state with one MAJ3 block already forced by two equal assigned coordinates and third coordinate `x` still syntactically present:

1. does the deterministic branch selector choose `x` before some other live variable?
2. if yes, is `A_x` empty?
3. if nonempty, can every element of `A_x` be traced to the localized allowed asymmetry sources and bounded/compositionally charged?

A state satisfying 1+2 is one exact reachable doubling cell in the execution DAG.

## Verdict

`PASS_EXACT_TAIL_BALANCE_SIBLING_MERGE_CRITERION__REACHABLE_BRANCH_CAPTURE_OPEN`

## Claim ceiling

One merge cell would not imply an exponential fibre; serial composition remains separate. No Policy-0A lower bound or P-vs-NP claim follows.
