# C023R — source frequency twins and defect-only splitting theorem

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_LEMMA__NO_SCIENTIFIC_PROMOTION`

## Setting

Consider a historical descendant source factor obtained by restricting one exact truth-table vertex relation of the MAJ3-lifted Tseitin encoding. Let its remaining variable set be `X` and restricted Boolean relation be `P|alpha`.

The frozen exact representation is one full blocking clause for every falsifying assignment to **all variables still in `X`**, followed only by tautology/duplicate canonicalization.

## Lemma 1 — uniform absolute occurrence inside one exact factor

Every blocking clause of `C(P|alpha)` contains exactly one signed literal for every variable in `X`.

Therefore, for any two live variables `x,y in X`,

`occ_source_factor(x) = occ_source_factor(y) = |C(P|alpha)|`,

where occurrence counts ignore literal sign, exactly as the historical branch selector does.

This holds even when one variable is semantically irrelevant to the restricted relation. Exact truth-table CNF still includes that variable in every full blocker.

## Lemma 2 — live coordinates of one edge block are source-frequency twins globally

Let lifted base edge `e=(u,v)` have coordinate block `(a_e,b_e,c_e)`. Any two coordinates of this block that remain unassigned occur in exactly the same set of source factors: endpoint vertex factors `u` and `v`.

By Lemma 1 their occurrence contribution inside each endpoint factor is identical. Hence for any two live coordinates `x,y` of the same edge block,

`freq_source(x)=freq_source(y)`

in the full restricted **source** CNF, regardless of:

- current vertex charges;
- whether the block relation is MAJ3, AND, OR, a remaining literal or a constant-output dependence;
- restrictions on other edge blocks;
- graph expansion.

Thus source truth-table representation alone cannot break the historical branch-frequency tie between live coordinates of one edge block.

## Corollary — deterministic source-only coordinate choice

If no derived/inherited clause contributes unequal occurrence counts to two live coordinates `x,y` of the same block, their total branch frequencies are equal. Historical tie-break then selects the smaller numeric variable ID whenever the maximum-frequency set contains both.

In particular, after the first coordinate of a fixed pair has been assigned, the source part gives the two remaining coordinates equal frequency in both value branches. Any difference in which coordinate is chosen next must come from non-source metadata or from competition with variables on other blocks, not from an intrinsic source-frequency preference between the two coordinates.

## Defect-split object

Let `D` be the multiset/set of historical derived/inherited clauses present in the post-UP state before branching.

For live coordinates `x,y` of one block define the derived occurrence imbalance

`Delta_D(x,y) = occ_D(x)-occ_D(y)`.

Since source contributions cancel exactly,

`freq_total(x)-freq_total(y) = Delta_D(x,y)`.

Call the edge block **coordinate-split by metadata** when some pair of its live coordinates has nonzero `Delta_D`.

Thus every within-block branch-frequency asymmetry is represented exactly by derived-clause incidence, not by the source factors.

## Relation to the partial-pivot defect theorem

If the relevant coordinate sign/frequency symmetry held before a pass, complete source-only pivots, ordinary restrictions and noncontradictory UP cannot create its first asymmetric memory; new sign asymmetry enters only through a partial-pivot cutoff defect and its descendants.

Consequently, metadata coordinate-splitting of a source-frequency-twin block has a traceable non-source cause. For a stifling/orientation block that remains outside all such effective defect incidence, the two candidate coordinates remain exact frequency twins and the historical minimum-ID tie-break is deterministic.

This theorem does not prove that many blocks remain unsplit: one inherited clause can contain many variables and one cutoff lineage can spread through later Resolution.

## Clause-incidence charging observation

One derived clause `C` can change the occurrence count of only variables actually present in `C`. Therefore the number of block-coordinate incidences whose frequency can be affected by a set of derived clauses is at most

`sum_{C in D} width(C)`.

This is a crude exact upper bound, not yet useful asymptotically unless the total derived-clause width mass can itself be bounded below the number of candidate orientation blocks.

## Captain Obvious next reduction

The scalable fixed-pair orientation-product gate can now be attacked through a smaller combinatorial quantity:

`DEFECT_SPLIT_COVERAGE`

= number of candidate edge blocks whose coordinate-frequency twins are split or whose sign-tail balance is broken by descendant cutoff-defect metadata.

If an infinite reachable family admits `Omega(L)` candidate orientation blocks but only `o(L)` are defect-split/coupled, then `Omega(L)` blocks remain locally eligible for exact `01/10` diamonds; serial/global composability must then be checked.

Conversely, a positive cache-fibre ceiling route may prove that cutoff-defect lineages necessarily split/couple all but `o(L)` candidate blocks before they can compose.

## Verdict

`PASS_SOURCE_COORDINATE_FREQUENCY_TWINS__ALL_WITHIN_BLOCK_SPLITTING_CHARGED_TO_DERIVED_METADATA`

## Claim ceiling

No asymptotic count of unsplit blocks is established. No cache-fibre or Policy-0A lower bound follows yet; `P_VS_NP = OPEN`.
