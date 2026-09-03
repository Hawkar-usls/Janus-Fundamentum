# JANUS TRUMP R44BR — coupled equality stars force unbounded signed-transport support

## Claim ceiling

This note refutes only the route

`UNIVERSAL_CONSTANT_K_SIGNED_PERMUTATION_TRANSPORT_COVERAGE`.

It does **not** refute polynomial discovery of unbounded-support transports, more general substitutions/model maps, or P=NP.

## 1. Base critical sibling pair

Use the fixed R44AS parent `G` on variables `1,...,6`, pivot `x2`. Let

- `A = G[x2=0]`,
- `B = G[x2=1]`.

The already replayed finite theorem gives

`delta*(G)=2`, `delta*(A)=delta*(B)=1`,

and the full five-root signed-permutation search gives:

1. `B -> A` has no transport of support at most four;
2. the R44BP transport
   `pi={1:-3,3:-5,4:6,5:-1,6:-4}`
   has support five;
3. `A -> B` has no signed-permutation transport at all.

The finite replay also checks that `G,A,B` are maximum-deficiency critical: their whole clause sets attain maximum deficiency and every one-clause deletion has smaller maximum deficiency.

## 2. Coupled equality-star construction

Fix `L>=2`. For every root

`v in R={1,3,4,5,6}`

introduce fresh variables `z(v,1),...,z(v,L)` and for every leaf add

`(-v OR z(v,j))` and `(v OR -z(v,j))`.

Call the extended parent/siblings `G_L,A_L,B_L`.

These are **coupled** extensions: the new variables are attached to the five roots that any base transport must move. They are not variable-disjoint copies of the old obstruction.

## 3. Equality-extension criticality lemma

Let `F` be `delta*`-critical, let `v` occur in `F`, and let `z` be fresh. Define

`F' = F union {(-v OR z),(v OR -z)}`.

Then `F'` is `delta*`-critical and

`delta*(F')=delta*(F)+1`.

Proof. Write `k=delta*(F)=delta(F)`. Consider any selected old subformula `S subseteq F` and 0,1,or 2 selected equality clauses.

- With zero new clauses, deficiency is at most `k`.
- With one new clause, at least the fresh variable `z` is added together with one clause, so deficiency cannot increase above that of `S`.
- With both new clauses: if `v` is absent from `S`, two variables (`v,z`) accompany two clauses and deficiency does not rise. If `v` is already present, the pair contributes exactly +1. For a proper `S`, criticality gives `delta(S)<=k-1`, hence the result is at most `k`.
- Only `S=F` together with both equality clauses reaches `k+1`.

Thus the full extension is the unique maximum-deficiency clause set. QED.

Iterating the lemma over all `5L` leaves gives

`delta*(G_L)=2+5L`,

`delta*(A_L)=delta*(B_L)=1+5L`.

So branching on `x2` still gives strict rank descent by one.

## 4. Binary clauses are mapped bijectively

A signed permutation maps a binary target clause to a binary clause. The transport condition says some source clause is contained in that binary image. There are no unit or empty clauses, so that source clause must itself be the identical binary clause.

Distinct target binary clauses have distinct images under a signed permutation. `A_L` and `B_L` contain the same number of binary clauses (`10L+2`). Therefore any signed transport induces a bijection between their binary clause sets.

Consequently the binary incidence degree of every underlying variable is preserved.

## 5. Roots cannot map to leaves

Every equality leaf occurs in exactly two binary clauses, hence has binary degree 2.

Every root occurs in `2L` equality clauses plus zero, one, or two original binary sibling clauses. For `L>=2`, every root therefore has binary degree at least 4.

Binary-degree preservation implies:

- roots map to roots;
- leaves map to leaves.

## 6. Restriction recovers a base transport

Take any `B_L -> A_L` signed transport and restrict it to the five roots. Every original clause of `A` contains roots only, so its image also contains roots only.

A source equality clause contains a leaf and therefore cannot be a subset of a root-only image. Hence every original target clause is witnessed by an original clause of `B`.

Thus the root restriction is a valid signed transport `B -> A`.

By the exact R44BQ finite theorem, its support on roots is at least five. Since there are exactly five roots, **all five roots move**.

The same argument in the reverse direction would produce a base `A -> B` transport, which does not exist. Hence no reverse extended transport exists.

## 7. Moving a root forces all of its leaves to move

Let a root map as `v -> sigma*w`, where `sigma in {+1,-1}`. Let one attached leaf map as `z -> tau*u`.

The two equality clauses map to

`(-sigma*w OR tau*u)` and `(sigma*w OR -tau*u)`.

Since root-leaf binary clauses in the source occur only as equality pairs, these images can belong to the source binary set only when

- `u` is a leaf attached to `w`, and
- `tau=sigma`.

Therefore if the root moves to another underlying root, every leaf moves to that root's star. If the root only sign-flips, every leaf must sign-flip as well. In either case every attached leaf belongs to the signed support.

All five roots move, so every one of the `5L` leaves moves:

`support >= 5+5L = 5(L+1)`.

## 8. Tightness

Extend the R44BP base permutation `pi` to leaves by

`z(v,j) -> sign(pi(v))*z(|pi(v)|,j)`.

This maps every equality pair exactly to the equality pair attached to the image root and preserves the already proved base transport. Its support is exactly

`5(L+1)`.

Hence

`min_support(B_L -> A_L) = 5(L+1)`.

The reverse direction has no transport.

## 9. Quantified barrier

For every fixed constant `K`, choose `L>=max(2,ceil(K/5))`. Then

`5(L+1)>K`.

Therefore there exists a maximum-deficiency-critical sibling pair for which no signed-permutation safe-delete transport of support at most `K` exists in either direction.

So

`UNIVERSAL_CONSTANT_K_SIGNED_PERMUTATION_TRANSPORT_COVERAGE = FALSE`.

What remains open is whether an **unbounded-support** signed transport can be found in polynomial time on every critical pair, or whether a richer polynomially discoverable transport class can give universal destructive descent.

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`
