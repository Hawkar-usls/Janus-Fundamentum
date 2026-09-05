# JANUS TRUMP R50G23 — DIRECT5 skeleton collapse cascade and anti-collapse debt

## Scope

R50G22 left exactly 30 sources in its frozen 11,520-source family that were both pre-BVE-clean and whose first frozen R33 microstep was an immediate W4 escape by BVE on pivot 1. Every one of those 30 then had an open same-pivot R47J door ending in `DIRECT_EMPTY_CNF`.

R50G23 does **not** enlarge that family. It replays exactly those 30 sources and extracts the complete certified normalization history of the same-pivot R47J candidate.

The finite 30-source classification is evidence about the frozen skeleton family only. It is not a proof that every possible ALL-DIRECT5 source has the same cascade.

## Exact cascade object

For a selected source `F`, let exact DP on pivot 1 produce `H0`. R47J then iterates the already-frozen normalization machine:

`R33 -> affine test -> complete RUP pass -> restart if changed`.

Every R33 history record and every successful RUP strengthening is already proof-carrying and independently replayed in the existing R47J/R35B machinery. R50G23 merely exposes these records in order and computes the longest common transition prefix across the 30 sealed skeletons.

## Direct-blocking debt lemmas

The following statements concern **pure clause addition to the same current state** and only the direct invalidation of a specific already-applicable transition. They do not say that satisfying the debt is sufficient to produce an unsafe R47J result.

### Tautology deletion

If clause `C` already contains `l` and `-l`, adding clauses cannot change `C`. Therefore the frozen tautology deletion remains applicable. Pure addition cannot directly invalidate it.

### Unit propagation

If unit clause `(l)` is already present, adding clauses cannot remove it. An opposite unit only creates an earlier contradiction; it does not invalidate the original unit. Pure addition cannot directly remove the unit-propagation obligation.

### Pure-literal autarky

If variable `x` occurs only with polarity `sigma` in the current state, the only way for pure clause addition to make it non-pure is to add at least one occurrence of `-sigma*x`. Hence any direct additive block pays at least one new clause and at least one opposite-polarity literal incidence.

### Subsumption

If existing clause `A` is a subset of existing clause `B`, adding clauses preserves `A subseteq B`. Therefore the existing subsumption deletion remains valid. Pure addition cannot directly invalidate that relation.

### Blocked-clause elimination

Suppose `C` is blocked on literal `l`. By definition, every clause containing `-l` gives a tautological resolvent with `C`. To invalidate that exact blockedness by addition, at least one added clause `D` must contain `-l` and must yield a non-tautological resolvent with `C`. Thus a direct additive block needs at least one new clause and one opposite blocking-literal occurrence, with a non-tautological support geometry.

### Bounded variable elimination

Let BVE on pivot `x` be accepted in state `F`. Add a distinct clause `D` not containing `x`.

The pivot parent sets and their cross-polarity resolvents are unchanged. `D` survives untouched to the transformed formula unless it duplicates a generated resolvent; in the ordinary untouched case it adds the same clause/literal contribution to both before and after measures, preserving strict lexicographic descent. If it duplicates a generated resolvent, canonicalization can only make the transformed side smaller, strengthening rather than destroying descent. The resolvent-count condition is also unchanged.

Therefore a distinct added clause that omits `x` cannot turn this accepted BVE into a rejected BVE. Any **direct additive** BVE block must contain the pivot `x` (or the source must be modified non-additively). Minimum direct additive incidence debt: at least one occurrence of `x` or `-x`.

### RUP strengthening

A successful single-literal RUP strengthening is certified by unit-propagation conflict under fixed assumptions. Adding clauses cannot remove clauses used by the UP derivation and cannot turn a conflict into a non-conflict. Therefore the certificate is monotone under pure clause addition at the same state. Pure addition cannot directly invalidate an already-certified RUP strengthening.

## What the gate may conclude

If the 30 cascades share a first transition, R50G23 may name that transition as the first common collapse mechanism **for the frozen 30 skeletons** and attach the appropriate necessary direct-blocking debt above.

If the cascades split immediately, R50G23 must emit the partition rather than invent a common mechanism.

Even if all 30 share one transition and the direct-blocking debt is proved, that debt is only necessary for directly disabling the transition at the same state. It is not sufficient for ALL-DIRECT5 all-doors-closed geometry, reachability, V7 elimination, `U_mu`, `SAT in P`, or `P=NP`.
