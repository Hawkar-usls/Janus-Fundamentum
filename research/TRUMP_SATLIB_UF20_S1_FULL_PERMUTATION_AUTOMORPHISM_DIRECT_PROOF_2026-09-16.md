# TRUMP SATLIB UF20 S1 full-permutation automorphism certificate — direct proof

**Authority:** diagnostic proof certificate only.  
**Scope:** pure variable permutations of finite multisets of the frozen 3-ary Boolean clause relations produced by the preregistered DIMACS normalization. No variable bit-flips or signed automorphisms are included.

## Frozen definitions

A normalized clause relation is a pair `(S,R)` where `S={v1,v2,v3}` contains three distinct Boolean variables and

`R = {0,1}^S \ {f}`

for a unique forbidden assignment `f:S->{0,1}`.  The primal graph has one vertex per variable and an edge `{u,v}` whenever some constraint scope contains both `u` and `v`.

For a variable `v`, define

- `deg(v)` = primal degree;
- `p(v)` = number of incident clause relations whose unique forbidden assignment has `f(v)=0`;
- `n(v)` = number of incident clause relations whose unique forbidden assignment has `f(v)=1`;
- `S1(v) = (deg(v), p(v), n(v))`.

For the frozen DIMACS clause normalization, `f(v)=0` is exactly a positive source-literal occurrence and `f(v)=1` is exactly a negative source-literal occurrence.

An exact pure-variable permutation automorphism is a permutation `sigma` of the variables such that transporting every constraint `(S,R)` by `sigma` — including the corresponding coordinate transport of every relation row — preserves the complete normalized constraint multiset.

## Lemma 1 — primal degree is invariant

Let `sigma` be an exact variable-permutation automorphism. If `{u,v}` is a primal edge, some constraint contains both `u` and `v`. Transporting that constraint by `sigma` produces a constraint containing both `sigma(u)` and `sigma(v)`. Hence `{sigma(u),sigma(v)}` is a primal edge. Applying the same argument to `sigma^{-1}` gives the converse.

Therefore `sigma` is an automorphism of the primal graph, so

`deg(sigma(v)) = deg(v)`

for every variable `v`.

## Lemma 2 — forbidden-bit occurrence counts are invariant

Fix a variable `v`. Exact constraint-multiset preservation gives a bijection between constraints incident to `v` and transported constraints incident to `sigma(v)`.

For an incident clause relation `(S,R)`, let `f` be its unique forbidden assignment. Under coordinate transport by `sigma`, the transported relation has unique forbidden assignment `f_sigma` satisfying

`f_sigma(sigma(x)) = f(x)`

for every `x in S`.

In particular,

`f_sigma(sigma(v)) = f(v)`.

Thus the incident-constraint bijection preserves separately the number of occurrences whose forbidden bit at the moved variable is `0` and the number whose forbidden bit is `1`. Therefore

`p(sigma(v)) = p(v)` and `n(sigma(v)) = n(v)`.

## Theorem — S1 is a necessary invariant

Combining Lemma 1 and Lemma 2,

`S1(sigma(v)) = S1(v)`

for every variable `v` and every exact pure-variable permutation automorphism `sigma` in the frozen domain.

Consequently every orbit of the full pure-variable permutation automorphism group is contained in one S1 equivalence class. This is a necessary-condition statement only; equal S1 signatures do **not** imply semantic exchangeability.

## Frozen five-source consequence

The already frozen signature-ablation receipt gives these S1 partitions:

- `UF20_02`, `UF20_03`, `UF20_04`: all 20 S1 classes are singleton. By the theorem every exact pure-variable permutation automorphism fixes every variable, so the group is identity-only.
- `UF20_01`: exactly one non-singleton S1 class remains, `{4,20}`; all other variables are singleton. Therefore any exact pure-variable permutation automorphism is either the identity or the transposition `(4 20)`. The gate must replay the already sealed exact-transposition predicate on that pair.
- `UF20_05`: exactly one non-singleton S1 class remains, `{6,14}`; all other variables are singleton. Therefore any exact pure-variable permutation automorphism is either the identity or the transposition `(6 14)`. The gate must replay the already sealed exact-transposition predicate on that pair.

If both sealed swaps fail, then the full pure-variable permutation automorphism group is trivial on each of the five frozen sources. No `20!` enumeration is needed.

## Scientific firewall

This theorem is only about pure variable-permutation automorphisms in the stated frozen clause-relation representation. It says nothing about bit-flip/signed automorphisms, does not establish SAT hardness or tractability, does not license a solver or carrier, and does not change `P_VS_NP = OPEN` or `GENERAL_SAT_IN_P = NOT_PROVED`.
