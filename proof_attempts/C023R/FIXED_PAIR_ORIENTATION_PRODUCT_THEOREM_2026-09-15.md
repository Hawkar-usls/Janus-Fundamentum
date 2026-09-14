# C023R — fixed-pair MAJ3 orientation product theorem

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_LEMMA__NO_SCIENTIFIC_PROMOTION`

## Setting

For every lifted base edge `e`, write its MAJ3 block as

`(a_e,b_e,c_e)`

using the frozen coordinate positions of the JANUS encoding.

Let `S` be any set of lifted edge blocks. For every `e in S`, assign the same two coordinate positions `{a_e,b_e}` in one of the two opposite-value orientations

`(a_e,b_e)=(0,1)`

or

`(a_e,b_e)=(1,0)`,

and leave `c_e` unassigned. Hold the assignment domain and values outside these orientation choices fixed identically across all histories being compared.

## Lemma 1 — one-block orientation equality

For every bit `c`,

`MAJ3(0,1,c)=c`

and

`MAJ3(1,0,c)=c`.

Therefore the two restrictions of one block leave exactly the same Boolean function of the same remaining variable `c_e`.

Unlike the earlier equal-pair forcing-witness comparison, the **assigned coordinate set is also identical** in the two orientations. Hence the remaining variable set has the same numeric variable IDs on both histories.

## Lemma 2 — exact source byte-CNF equality for one block orientation flip

Consider any vertex relation containing edge block `e`. Restrict all common assignments and compare only the two orientations of `(a_e,b_e)`.

By Lemma 1 the restricted Boolean relation on the same remaining variable set is identical. The JANUS exact truth-table restriction lemma then gives the same blocking-clause CNF after canonical duplicate removal.

Therefore changing `01` to `10` on the fixed coordinate pair of one edge block changes neither endpoint's restricted source byte-CNF.

This is a representation-level equality, not merely a semantic quotient after variable renaming or projection.

## Theorem — exact `2^|S|` source orientation product

Choose independently, for every `e in S`, orientation bit

`omega_e in {01,10}`.

There are exactly `2^|S|` orientation vectors `omega`.

Because each block's restricted output is exactly its same remaining coordinate `c_e`, every vertex relation in the MAJ3-lifted Tseitin formula restricts to the same relation on the same remaining variable IDs for every orientation vector.

Hence, after all common restrictions are applied,

`SourceKey(omega) = SourceKey(omega')`

byte-for-byte for every `omega,omega' in {01,10}^S`.

Thus the frozen source representation has an exact Cartesian preimage product of size

`2^|S|`

under fixed-pair orientation flips.

No graph expansion assumption is needed for this identity.

## Stronger interpretation when all edge blocks are oriented

If `S=E(G)` and every edge block has its first two coordinates fixed in either `01` or `10`, then every `MAJ3(a_e,b_e,c_e)` reduces exactly to `c_e`.

The source residual becomes the ordinary Tseitin relation on the remaining third coordinates `c_e`, with the original charge vector, represented in the JANUS exact truth-table CNF convention.

All `2^|E|` orientation vectors induce that same source residual byte-CNF.

Historical Policy-0A does **not** rerun the root affine dispatcher on descendants, so this descendant residual is not automatically sent to Gaussian elimination merely because its source semantics have become affine.

This statement does not assert that frozen Policy-0A can reach all such orientation vectors or that inherited derived clauses are equal across them.

## Relation to the K4 revealed diagnostic

The exact K4 max-fibre audit for state 1040 found a full Cartesian product of size 128. Four of the six MAJ3 blocks contribute precisely one fixed-pair `01/10` orientation bit each. The remaining two blocks contribute same-output full-assignment multiplicities.

Thus the local orientation mechanism in this theorem is not only semantically possible: it is realized simultaneously and independently for multiple blocks in one revealed historical Policy-0A cache fibre.

This finite observation is a falsifier/structure witness only. It does not establish asymptotic density of such blocks.

## Exact asymptotic falsifier target

The C022→C023 subexponential-fibre transfer is falsified if one proves an infinite sequence of frozen q=4 instances with reachable cache keys `K_t` and edge subsets `S_t` such that:

1. `|S_t| = Omega(L_t)` where `L_t` is the lifted input length / equivalent linear family size;
2. for each `e in S_t`, the two fixed-pair orientations `01` and `10` are both realized in execution histories reaching `K_t`;
3. the orientation choices compose independently, giving all `2^|S_t|` combinations;
4. inherited non-source clauses and deterministic pre-UP are byte-identical at `K_t` across those combinations.

Then

`m(K_t) >= 2^|S_t| = 2^{Omega(L_t)}`.

## Positive-route alternative

To preserve a subexponential fibre theorem, it is enough to prove that for every reachable key the number of independently composable fixed-pair orientation bits is `o(L)`, because every additional source-semantic collision mechanism must then be separately bounded as well.

The existing partial-pivot asymmetry theorem identifies the only source of sign-asymmetric metadata capable of distinguishing an otherwise balanced irrelevant/orientation bit: descendants of budget-cutoff defects.

## Captain Obvious next gate

`C023R_SCALABLE_FIXED_PAIR_ORIENTATION_PRODUCT_GATE`

The nearest question is now purely execution-specific:

> Does frozen q=4 Policy-0A admit `Omega(L)` independently composable fixed-pair `01/10` orientation bits in one reachable cache fibre, or do partial-pivot defect lineages force the maximum independent orientation-product dimension to `o(L)`?

The K4 result fixes the mechanism; only scalability remains open.

## Verdict

`PASS_EXACT_SOURCE_ORIENTATION_PRODUCT__FINITE_EXECUTION_PRODUCT_WITNESS_EXISTS__ASYMPTOTIC_REACHABILITY_OPEN`

## Claim ceiling

No asymptotic cache-fibre lower bound or Policy-0A lower bound is established. `P_VS_NP = OPEN`.
