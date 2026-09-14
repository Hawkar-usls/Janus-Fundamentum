# C023R P1–P3 — Exact collision decomposition

Authority: `SYMBOLIC_DERIVATION__NO_SCIENTIFIC_PROMOTION`  
Method: `STRICT_ALGEBRA_ONLY__NO_HEURISTICS`

## Frozen objects

The cache key is the canonical CNF after exhaustive pre-unit propagation and before the deterministic local Resolution pass. The next branch is chosen only after that local pass and post-unit propagation. Thus cache equality is a statement about exact restricted truth-table CNF syntax, not about a learned-clause closure.

For every base edge `e`, the lift uses one MAJ3 block `B_e={e_1,e_2,e_3}`. For every degree-5 base vertex `v`, the source factor is the exact truth-table CNF of

`XOR_{e incident v} MAJ3(B_e) = charge(v)`

over the 15 block variables incident to `v`.

## Lemma P1.1 — exact factor restriction

Let `C_v` be one source vertex factor and let `alpha` be any partial assignment. Simplifying `C_v` by `alpha` gives the complete blocking-clause CNF of the restricted vertex predicate on the unassigned variables of the original scope.

This is the already frozen restriction-commutation lemma: falsifying extensions consistent with `alpha` are in bijection with surviving reduced blocking clauses.

## Lemma P1.2 — uniform clause scope inside one active factor

Let `U_v(alpha)` be the unassigned variables from the original scope of `v`. If the restricted predicate at `v` is not identically TRUE, every surviving blocking clause contributed by `v` contains exactly one literal for every variable in `U_v(alpha)`. Hence every clause from that active factor has absolute-variable scope exactly `U_v(alpha)`.

If the restricted predicate is identically TRUE, the factor contributes no clauses. If it is identically FALSE, it contributes every blocking clause over `U_v(alpha)` (and the empty clause when the scope is empty).

Therefore a variable may become semantically inessential while still remaining syntactically present in the pre-Resolution cache key; stifling alone does not authorize deleting an unassigned variable.

## Lemma P1.3 — what a provenance-free cache key recovers

Group the clauses of a canonical residual key by their absolute-variable scope `S`. For each `S`, the group is exactly the union of blocking-clause sets contributed by active source vertex factors whose residual scope is `S`, modulo duplicate-clause collapse.

Consequently:

- if exactly one active source vertex has scope `S`, its exact restricted relation is recovered from the cache key;
- if multiple source vertices have the same `S`, the cache key recovers their conjunction but not their individual relation identities.

No stronger provenance claim is assumed.

## Lemma P1.4 — scope-coincidence locality

In the frozen simple 5-regular base graph, two distinct source vertices have original lifted scopes whose intersection is:

- empty if they are nonadjacent;
- exactly the three variables of their common MAJ3 edge-block if they are adjacent.

Hence if two distinct active source vertices have the same nonempty residual scope `S`, then they are adjacent and

`S subseteq B_e`

for their common edge `e`. In particular `|S|<=3`.

Corollary: every active vertex relation with residual scope size `>3` is individually recoverable from the provenance-free cache key.

This isolates source-identity ambiguity to scope groups of size at most three.

## Lemma P2.1 — complete MAJ3 restriction functions

For `M(a,b,c)=MAJ3(a,b,c)`:

- 3 live coordinates: `M`;
- after fixing one coordinate to 0: `AND` on the two remaining coordinates;
- after fixing one coordinate to 1: `OR` on the two remaining coordinates;
- with one live coordinate after fixing the other two to `00`: constant 0;
- after `11`: constant 1;
- after `01` or `10`: the remaining coordinate itself;
- with zero live coordinates: the corresponding constant MAJ3 output.

For a fixed live-coordinate set, the only distinct restricted MAJ3 functions whose XOR difference is a constant are:

1. identical functions (difference 0);
2. constant 0 versus constant 1 (difference 1).

`AND` versus `OR` is not a constant difference. The identity function has no attainable complemented-identity partner under a two-coordinate MAJ3 restriction.

## Lemma P2.2 — zero-difference local history multiplicity

Fix the set of live coordinates of one MAJ3 block and fix its restricted function.

- 3 live: multiplicity 1;
- 2 live: multiplicity 1;
- 1 live and restricted function is the live coordinate: multiplicity 2 (`01` versus `10` on the fixed coordinates);
- 1 live and restricted function is constant: multiplicity 1 for that constant;
- 0 live and fixed output: multiplicity 4.

Thus, before execution reachability is imposed, the block-local same-function history exponent is

`sigma_e = 1` for a one-live identity block,
`sigma_e = 2` for a zero-live block,
and `0` otherwise.

This counts semantic restriction histories only; it does not assert that frozen Policy-0A visits all of them.

## Lemma P3.1 — disjoint-block XOR decomposition

Let one individually recoverable active vertex have incident block-restriction functions `f_e` in context A and `g_e` in context B, on the same residual block-variable sets. If the two contexts induce the same restricted vertex predicate, then

`XOR_e f_e = XOR_e g_e`.

Because different edge blocks use disjoint variables, every difference function

`d_e = f_e XOR g_e`

must be constant. Proof: hold every other block fixed and vary only the variables of block `e`; the XOR of all `d_e` is identically zero, so `d_e` cannot vary. The constants satisfy

`XOR_{e incident v} delta_e = 0`.

By Lemma P2.1, a nonzero `delta_e` can occur only between constant-0 and constant-1 restrictions of the same live-coordinate set.

## Lemma P3.2 — cycle-space form on recoverable vertices

Collect the constant-flip bits `delta_e` on blocks whose local restricted functions differ by a constant. For every individually recoverable active vertex `v`, equality of the cache-key-recovered vertex relation imposes

`XOR_{e incident v} delta_e = 0`.

Therefore the admissible constant-flip vectors lie in the kernel of the corresponding GF(2) incidence constraints. When all relevant endpoint relations are individually recoverable, this is exactly a cycle-space condition.

This is the rigorous version of the earlier syndrome observation; it is not used at vertices whose provenance has collapsed into a common scope group of size at most three.

## Exact collision budget before reachability

For a residual key `R`, define:

- `sigma(R)` = sum of the block-local same-function history exponents from Lemma P2.2;
- `beta_rec(R)` = dimension of the constant-flip solution space constrained by individually recoverable active vertex relations;
- `kappa(R)` = remaining ambiguity contributed by active source-vertex groups whose equal residual scope has size at most three.

Then any semantic-history upper bound compatible with the exact cache key must charge all three terms. A valid execution-fiber theorem cannot use only the old cycle rank `beta(H)`.

The next proof task is to replace the placeholder `kappa(R)` by an exact finite local bound and then study which of the `2^{sigma+beta_rec+kappa}` semantic representatives are actually reachable under frozen branch/UP/local-Resolution dynamics.

## New sharpened theorem obligation

The C023R subexponential route now requires one of the following:

**PASS route:** prove for every reachable residual on the frozen q=4 Morgenstern family that the logarithm of the number of *reachable* representatives is `o(L_t)`, despite the semantic collision budget above.

**FAIL route:** prove an infinite family of reachable residuals with `Omega(L_t)` independent reachable collision degrees, giving `2^{Omega(L_t)}` exact execution fibers.

No finite multiplicity curve may choose between these alternatives.

## Claim boundary

`SOURCE_SCOPE_RECOVERY != SOURCE_PROVENANCE_EVERYWHERE`.

`SEMANTIC_COLLISION_BUDGET != REACHABLE_EXECUTION_FIBER`.

`P1_P3_DERIVATION != CACHED_POLICY_LOWER_BOUND`.

`P_VS_NP = OPEN`.
