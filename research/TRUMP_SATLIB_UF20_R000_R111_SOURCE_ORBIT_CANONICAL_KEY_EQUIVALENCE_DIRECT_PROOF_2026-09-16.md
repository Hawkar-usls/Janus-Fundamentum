# TRUMP SATLIB UF20 R000/R111 source-orbit canonical-key equivalence — direct proof

**Authority:** diagnostic definition-equivalence proof only. This document defines no new invariant, feature, solver, carrier, adapter, quotient, or group search.

## 1. Frozen domain

Consider a source-bound projection containing only original 3-CNF clauses whose unique forbidden tuples are `000` or `111`.

Write

- `R_000 = {0,1}^3 \ {000}`;
- `R_111 = {0,1}^3 \ {111}`.

A source clause in this domain is represented by the pair

`x = (t,S)`

where `t in {000,111}` is its relation type and `S={v1,v2,v3}` is its three-variable scope written in sorted variable order. The source projection is a **multiset** `M` of such items; repeated clauses/scopes therefore retain multiplicity.

## 2. Source item to canonical explicit-relation key

For each `t`, let `A_t` be the sorted explicit allowed-row table of `R_t`. Define

`Phi(t,S) = (S,A_t)`.

On the frozen domain, `A_000 != A_111`, so `t` is uniquely recoverable from `A_t`; the scope is already present in the key. Hence `Phi` is injective on source-item types `(t,S)`.

Applying `Phi` independently to every occurrence in the source multiset preserves multiplicity. Because the projected raw construction preserves each original clause as one explicit-relation constraint and the sealed normalizer canonicalizes scope and allowed rows, the multiset image `Phi_*(M)` is exactly the constraint multiset represented by the sealed `_formula_key`.

Therefore source-clause multiplicity is neither collapsed nor invented by this representation change.

## 3. Coordinate symmetry of R000 and R111

Both frozen relations are invariant under every permutation of their three coordinates:

- permuting `000` yields `000`, so the cube-minus-`000` relation is unchanged;
- permuting `111` yields `111`, so the cube-minus-`111` relation is unchanged.

Thus when variable identities are permuted inside a constraint scope, reordering the transported scope back to canonical sorted order does not change `A_t` for either `t=000` or `t=111`.

This coordinate symmetry is the special fact that permits the source-level representation `(t,S)` to commute exactly with the sealed explicit-relation transport on this frozen two-relation domain.

## 4. Transposition transport commutes with Phi

Fix any variable transposition `tau=(u v)`. Define source transport

`tau_s(t,S) = (t, sorted(tau(S)))`.

The relation type remains `t`: the action changes variable identities, not Boolean literal polarity, and coordinate canonicalization leaves `R_000` and `R_111` unchanged by Section 3.

The sealed `_formula_key_after_swap` applies the same variable transposition to the explicit relation constraint, transports its scope and relation coordinates, and canonicalizes the result. Hence for every frozen source item,

`Phi(tau_s(t,S)) = tau_k(Phi(t,S))`,

where `tau_k` is the transport performed by the sealed swapped-key construction.

Therefore the square commutes itemwise. Since both transports act independently on every multiset occurrence, it also commutes with multiplicity:

`Phi_*(tau_s(M)) = tau_k(Phi_*(M))`.

The right-hand side is exactly the sealed `_formula_key_after_swap` multiset.

## 5. Closure iff sealed canonical-key equality

By Section 2,

`Phi_*(M) = _formula_key(F)`.

By Section 4,

`Phi_*(tau_s(M)) = _formula_key_after_swap(F,u,v)`.

Because `Phi` is injective and multiplicity-preserving,

`M = tau_s(M)`

if and only if

`Phi_*(M) = Phi_*(tau_s(M))`.

Therefore

`source clause multiset is closed under tau`

if and only if

`_formula_key(F) == _formula_key_after_swap(F,u,v)`.

The sealed predicate `is_exact_transposition_automorphism(F,u,v)` returns precisely this canonical-key equality. Consequently, on this frozen R000/R111 source-projection domain, **source-clause orbit closure is not a new invariant**. It is a provenance-level presentation of the already sealed exact-transposition predicate.

## 6. Finite sanity controls are not the proof

The preregistered controls are used only to catch implementation mistakes:

- `UF20_01`, pair `[7,10]`: source multiset closure and sealed predicate are both expected `true`;
- `UF20_03`, pair `[4,20]`: source multiset closure and sealed predicate are both expected `false`.

Agreement on those two finite controls does not establish the theorem; Sections 1–5 do.

## 7. Scientific firewall

This proof licenses only the representation-equivalence statement on the frozen `R000/R111` projected-source domain. It does not say that orbit closure implies tractability, that orbit deficit implies hardness, or that a new useful invariant has been discovered. It does not search new pairs, solve any formula, or alter the status `P_VS_NP = OPEN` and `GENERAL_SAT_IN_P = NOT_PROVED`.
