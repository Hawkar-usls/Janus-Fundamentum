# TRUMP SATLIB UF20 signed epsilon-determination residual bound — direct proof

**Authority:** diagnostic proof/counting certificate only. No signed action is tested for formula automorphism in this gate.

## Frozen premise from the signed-admissibility theorem

For a signed automorphism `g=(sigma,epsilon)` in the frozen single-forbidden-tuple clause domain, if `w=sigma(v)`, then

- when `epsilon(v)=0`, `(p(w),n(w))=(p(v),n(v))`;
- when `epsilon(v)=1`, `(p(w),n(w))=(n(v),p(v))`.

Also `deg(w)=deg(v)`. Hence `sigma` must map variables only within equal unsigned signatures

`U(v)=(deg(v),min(p(v),n(v)),max(p(v),n(v)))`.

## Lemma 1 — epsilon is unique on an unbalanced variable

Assume `p(v) != n(v)` and `U(w)=U(v)`.

Because the unordered pairs `{p(w),n(w)}` and `{p(v),n(v)}` are equal and contain two distinct values, exactly one of the following mutually exclusive cases holds:

1. `(p(w),n(w))=(p(v),n(v))`;
2. `(p(w),n(w))=(n(v),p(v))`.

The frozen signed-transform rule therefore forces exactly one value of `epsilon(v)`: `0` in case 1 and `1` in case 2. Both cannot be compatible because that would imply `p(v)=n(v)`.

## Lemma 2 — balanced variables leave one count-level flip bit free

If `p(v)=n(v)=q`, then both ordered pairs in the signed-transform rule are `(q,q)`. Thus the forbidden-bit count invariant alone cannot distinguish `epsilon(v)=0` from `epsilon(v)=1`.

This does **not** assert that either flip is an actual formula automorphism. It says only that both survive this necessary invariant.

## Lemma 3 — epsilon multiplicity for a fixed unsigned-S1-respecting sigma

Let `b` be the number of balanced variables with `p(v)=n(v)`.

For any fixed variable permutation `sigma` that respects all unsigned-S1 classes:

- each unbalanced variable has exactly one count-compatible `epsilon(v)` by Lemma 1;
- each balanced variable independently has two count-compatible choices by Lemma 2.

Therefore exactly `2^b` epsilon vectors survive the necessary count invariant for that fixed `sigma`.

## Lemma 4 — residual variable-permutation count

A permutation respects the unsigned-S1 invariant exactly when it independently permutes the members inside each unsigned-S1 class. If the class sizes are `s_1,...,s_k`, the number of such variable permutations is

`product_i s_i!`.

## Residual signed-action candidate count

Combining Lemma 3 and Lemma 4, the exact number of signed actions that survive **only the already proved necessary unsigned-S1 count invariant** is

`N_residual = (product_i s_i!) * 2^b`.

This is a residual candidate count, not an automorphism count. Every true signed automorphism must lie in this set, but members of this set may still fail exact formula preservation.

## Scientific firewall

The proof does not test `g.F=F`, does not enumerate the original `2^n n!` signed-action space, does not build a group-search algorithm or quotient, and has no SAT complexity consequence. `P_VS_NP=OPEN` and `GENERAL_SAT_IN_P=NOT_PROVED` remain unchanged.
