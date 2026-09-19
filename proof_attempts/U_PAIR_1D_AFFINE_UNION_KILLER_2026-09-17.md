# U-PAIR-1D — first symbolic high-rank grammar attack: affine-union killer

Date: 2026-09-17

Status:
`PASS_SCOPED_KILLER__POLYNOMIAL_AFFINE_UNION_NOT_UNIVERSAL__FACTORIZED_SYMBOLIC_GRAMMAR_STILL_OPEN`

## Candidate grammar

After U-PAIR-1C killed polynomial explicit bond dimension, the first symbolic
escape is to represent a relation as a union of polynomially many affine
subspaces of `GF(2)^n`. Each component is stored by a polynomial-size linear
system.

This grammar is attractive because one affine component represents an arbitrary
linear code exactly, projection/existential elimination preserves affinity, and
intersection with affine constraints is handled by Gaussian elimination.

The universal claim under attack is:

`every OR_3 + PAIR relation admits an exact union of poly(L) affine subspaces`.

## Killer family

For `m>=1`, take `3m` Boolean variables grouped into disjoint triples and define

`S_m = AND_{i=1}^m (x_{i,1} OR x_{i,2} OR x_{i,3})`.

This is already an `OR_3` instance of encoded length `L=Theta(m)`; no PAIR
interaction is needed for the lower bound.

Each block admits exactly seven assignments, so

`|S_m| = 7^m`.

## Lemma — maximum affine component size

Let `A` be any affine subspace contained in `S_m`. Project `A` onto block `i`.
The projection `pi_i(A)` is an affine subspace of `GF(2)^3` and cannot contain
`000`, because every point of `A` satisfies the block OR clause.

A 3-dimensional affine subspace of `GF(2)^3` is the whole cube and therefore
contains `000`. Hence

`dim(pi_i(A)) <= 2`

for every block.

The map from `A` into the direct product of its block projections is injective,
so

`dim(A) <= sum_i dim(pi_i(A)) <= 2m`.

Therefore every affine subspace contained in `S_m` has at most

`2^(2m) = 4^m`

points.

## Cover lower bound

If

`S_m = union_{j=1}^r A_j`

is an exact affine-union representation, every `A_j` must be contained in
`S_m`; otherwise the union would include a falsifying assignment. Thus

`7^m = |S_m| <= sum_j |A_j| <= r 4^m`,

so

`r >= (7/4)^m`.

Since `L=Theta(m)`, the number of affine components is exponential in input
length.

## Frozen verdict

`FAIL_POLYNOMIAL_AFFINE_UNION_AS_UNIVERSAL_SYMBOLIC_GRAMMAR`

This kills the direct idea that Gaussian-elimination-friendly affine pieces can
simply be unioned in polynomial quantity to absorb arbitrary `OR_3` semantics.

## Claim ceiling and surviving route

The killer does **not** rule out a factorized symbolic representation. Indeed,
`S_m` itself has a compact product-of-local-OR representation. So the next
candidate must preserve factorization while supporting exact elimination.

Next frontier:

`U-PAIR-1E__FACTORIZED_AFFINE_OR_SYMBOLIC_ELIMINATION`

The new question is whether a fixed factorized grammar can remain polynomial
under arbitrary exact elimination, or whether elimination necessarily creates
an exponential number of coupled affine/OR states on a hostile connected
family.

`GENERAL_SAT_IN_P = NOT_PROVED`
`P_VS_NP = OPEN`
