# JANUS TRUMP R50G25J — structural DP pivot-free confluence and quotient

## Sealed result

GitHub Actions run `34035151508` on head `162c61ecf8dd52a4df4a230a081dac2e58c316df` completed **SUCCESS**.

The gate adds **zero** new source skeletons. All 1212 frozen target states satisfy the application side conditions:

- pivot-free cover violations: `0`;
- NF antichain violations: `0`;
- NF absorption instance violations: `0`.

The structural lemma status is:

`STRUCTURAL_LEMMA_PROVED_FROM_IMPLEMENTED_DEFINITIONS`

with explicit firewall that this is a paper/set-theoretic proof over the implemented finite operators plus executable side-condition audit, **not** a proof-assistant formalization and **not** a proof of SAT in P or P=NP.

## Structural confluence lemma

Let `NF` be strict-subsumption minimization and let

`DP_p(F) = NF(B_p(F) ∪ R_p(F))`,

where `B_p(F)` is the pivot-free base and `R_p(F)` is the set of all non-tautological resolvents on pivot `p`.

For any finite pivot-free extension `K`:

1. `B_p(F ∪ K) = B_p(F) ∪ K`.
2. `R_p(F ∪ K) = R_p(F)` because `K` contributes no `+p/-p` parent.
3. For finite clause families, `NF(NF(A) ∪ K) = NF(A ∪ K)`.

Therefore

`DP_p(F ∪ K) = NF(DP_p(F) ∪ K)`.

This removes source-preimage identity from the exact-DP extension step whenever the added extension is pivot-free.

## Why the R50G25 covers satisfy the lemma

The minimum incidence cover `K(T)` is generated from variables of the already post-DP target `T`. Pivot `1` is absent from `T`, so every generated cover clause is pivot-free by construction. R50G25J audited this side condition on all 1212 frozen target states and found zero violations.

## Quotient operator and two-stage compression

Define

`Q(T) = NF(T ∪ K(T))`.

The sealed quotient counts are:

- target states: `1212`;
- distinct pre-NF cover-augmented unions `T ∪ K(T)`: `1188`;
- distinct canonical quotient states `Q(T)`: `1074`;
- total compression: `138` states (`11.386%`).

Therefore the compression is **two-stage**:

1. `1212 -> 1188`: `24` collisions already occur before strict-subsumption NF because distinct targets can produce the same deterministic cover-augmented union;
2. `1188 -> 1074`: a further `114` collisions are introduced by strict-subsumption normal form.

The quotient fiber histogram is:

- size 1: `950` fibers;
- size 2: `113` fibers;
- size 3: `8` fibers;
- size 4: `3` fibers.

So there are `124` non-singleton quotient fibers. The largest observed fibers have size `4`.

The structural equivalence relation is

`T1 ~ T2  iff  NF(T1 ∪ K(T1)) = NF(T2 ∪ K(T2))`.

Source-preimage identity is absent from `Q` by the structural exact-DP pivot-free extension lemma.

## Next gate

`R50G25K_OUTER_COVERAGE_PREREGISTRATION_NO_FAMILY_EXPANSION`

Before any family expansion, K should preregister the exact outer-coverage claim, admissible counterexample condition, polynomial accounting, and the distinction between:

- structural exact-DP confluence (now proved for pivot-free extensions),
- existence/constructibility of a useful `K(T)`,
- termination of the micro scheduler,
- universal DIRECT5 / arbitrary 3CNF coverage.

## Firewall

- Structural source-preimage confluence **does not** prove that every outer target has a useful cover.
- It **does not** prove that the micro scheduler terminates on arbitrary CNF.
- It **does not** prove universal DIRECT5 coverage.
- `SAT_IN_P = NOT_PROVED`.
- `P_VS_NP = OPEN`.
- `TRUMP_finished = false`.
