# U-PAIR-1G — Anti-alias cycle killer

Date: 2026-09-17

Status: `FAIL_STRICT_PER_MACROSTEP_ANTI_ALIAS_PROGRESS_FOR_REVERSIBLE_DEFINITIONAL_REENCODINGS__NO_P_EQ_NP_PROMOTION`

## Frozen candidate under attack

`U-PAIR-1G__GF2_RREF_PLUS_SHARED_BOOLEAN_DAG_WITH_FROZEN_PROGRESS_ACCOUNTING`

The candidate allows fresh definitional auxiliaries, exact DAG rewrites, affine pivots and exact existential elimination. Its preregistered progress proposal requires a lexicographically strict decrease of a polynomially bounded certified potential at every macro-step, with aliasing forbidden unless charged.

## Semantic anti-alias requirement

A progress measure intended to represent unresolved semantics must be invariant under an exact bijective reparameterization of the live interface. Renaming a semantic bit through an invertible definitional circuit is not progress.

Let a state encode a relation `R(X,Z)`, where `X` is the live interface and `Z` is a protected continuation/witness side.

Let `B:{0,1}^n -> {0,1}^n` be a bijection whose forward and inverse maps have polynomial-size bounded-fanin Boolean DAGs. Introduce fresh live bits `Y=B(X)` definitionally, then exactly eliminate `X` using `X=B^{-1}(Y)`. The resulting state is

`R'(Y,Z) = R(B^{-1}(Y),Z)`.

The two states differ only by coordinates on the live interface.

## Theorem — reversible re-encoding obstruction

Let `Phi` be invariant under exact bijective definitional re-encoding. Then

`Phi(R(X,Z)) = Phi(R(B^{-1}(Y),Z))`.

Therefore no such `Phi` can strictly decrease on every allowed macro-step if a reversible definitional re-encoding counts as a macro-step.

Conversely, if `Phi` strictly decreases on the re-encoding step, it depends on representational accidents such as variable names, direct alias counts or DAG placement, and therefore fails the anti-alias requirement.

### Proof

The map `Y=B(X)` is bijective and admits the exact inverse `X=B^{-1}(Y)`. Hence the second state can be transformed back to the first by the same allowed definitional machinery. They represent isomorphic continuation relations. Anti-alias invariance gives equality of `Phi`. Strict decrease on the forward step would contradict equality. QED.

## Concrete two-bit cycle

Take

`y1 = x1 XOR x2`

`y2 = x2`.

Its inverse is

`x1 = y1 XOR y2`

`x2 = y2`.

XOR is available in the frozen Boolean DAG language because it has a constant-size `AND/OR/NOT` implementation; the same transform is also directly representable in the affine RREF layer.

Use the protected equality relation

`R(X,Z) = [z1=x1 AND z2=x2]`.

Before re-encoding, each of the four `X` assignments induces a distinct singleton continuation on `Z`. After re-encoding, each of the four `Y` assignments again induces a distinct singleton continuation, merely permuted by `B^{-1}`. No semantic information has been removed.

Applying the inverse transform returns to the original representation class, yielding a two-step definitional cycle.

## Gold-standard semantic interface quantity

For a finite relation `R(B,W)`, define residual continuation equivalence by

`b ~ b' iff R_b(W) = R_b'(W)`.

Let

`N_R(B|W) = number of equivalence classes`

and

`mu_R(B|W) = ceil(log2 N_R(B|W))`.

A bijective reparameterization of `B` only permutes the rows/residual relations, so `N` and `mu` are invariant.

For the n-bit equality zipper `R(X,Z)=[Z=X]`, `N=2^n` and `mu=n`; every invertible re-encoding preserves this value.

This `mu` is used only as a semantic checker reference. No claim is made that computing it exactly is polynomial-time for arbitrary states.

## Frozen verdict

The following forms are rejected:

- live-variable count as semantic progress;
- quotienting only direct equality aliases;
- strict decrease on every macro-step while reversible definitional re-encodings remain legal macro-steps.

The representation itself is not falsified. What fails is the current progress accounting theorem candidate.

## Required repair

Move the progress measure to the quotient of representations by reversible definitional re-encoding. Normalization/re-encoding steps inside one quotient class must be allowed to have zero semantic progress. Strict decrease may only be claimed on certified irreversible quotient transitions.

Successor:

`U-PAIR-1H__QUOTIENTED_SEMANTIC_PROGRESS_OVER_REVERSIBLE_REENCODINGS`

Firewall:

`GENERAL_SAT_IN_P = NOT_PROVED`

`P_VS_NP = OPEN`
