# JANUS TRUMP R50G25J — structural DP pivot-free confluence and quotient

## Scope

This gate does **not** add any new source skeleton. It replaces repeated source-preimage replay by a structural lemma about the exact DP implementation already used by TRUMP.

Let `NF` be strict-subsumption minimization and let

`DP_p(F) = NF(B_p(F) ∪ R_p(F))`,

where `B_p(F)` is the pivot-free base and `R_p(F)` is the set of all non-tautological resolvents on pivot `p`.

For any finite pivot-free extension `K`:

1. `B_p(F ∪ K) = B_p(F) ∪ K`.
2. `R_p(F ∪ K) = R_p(F)` because `K` contributes no `+p/-p` parent.
3. For finite clause families, `NF(NF(A) ∪ K) = NF(A ∪ K)`.

Therefore

`DP_p(F ∪ K) = NF(DP_p(F) ∪ K)`.

This is the source-preimage confluence mechanism. It is a paper/set-theoretic proof over the implemented finite operators plus executable side-condition audit; it is **not** presented as a proof-assistant formalization.

## Why the R50G25 covers satisfy the lemma

The minimum incidence cover `K(T)` is generated from variables of the already post-DP target `T`. Pivot `1` is absent from `T`, so every generated cover clause is pivot-free by construction. R50G25J audits that side condition on all 1212 frozen target states.

## Quotient operator

Define

`Q(T) = NF(T ∪ K(T))`.

R50G25I observed 1212 target states but only 1074 actual post-DP states after source lifts. R50G25J treats this as a quotient induced by deterministic cover augmentation plus strict-subsumption normal form:

`T1 ~ T2  iff  Q(T1) = Q(T2)`.

The gate reports the quotient fiber histogram and whether the 1212→1074 compression appears only after NF or already before NF.

## Firewall

- Structural source-preimage confluence **does not** prove that every outer target has a useful cover.
- It **does not** prove that the micro scheduler terminates on arbitrary CNF.
- It **does not** prove universal DIRECT5 coverage.
- `SAT_IN_P = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.

If the lemma side conditions and quotient audit pass, the next gate is preregistration of outer coverage without expanding the family in this gate.
