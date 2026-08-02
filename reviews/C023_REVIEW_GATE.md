# C023 review gate

Review H138-H140 separately.

## H138 — execution/certificate equivalence

- Prove production Policy-0A and JANUS-FC_local certificate equivalence.
- Check unit propagation, local Resolution order and all budgets.
- Check exact residual equality and completed-before-use cache targets.
- Charge canonicalization, lookup, construction and replay.
- Independently attack malformed target, result, key, context, parent and pivot records.

Current finite pressure: 1,200 random production/trace comparisons, independent
serialized replay, four corrupted cache-record classes rejected, and structured
MAJ3/graph-tautology fixtures.

## H139 — reusable reason interface

- Separate decisions from inherited unit consequences.
- Specify the reusable reason language.
- State whether weakening, input lemmas, arbitrary lemmas, restarts or variable
  extensions are allowed.
- Prove polynomial reason extraction rather than post-hoc existence.
- Review the exact direct-context set-cover computation.

Current finite pressure on MAJ3-K4: 438 direct cache targets, 1,326 direct
contexts, one reusable unfolded C022 reason for only five targets, and a minimum
of 1,287 emitted reasons in total. This does not lower-bound stronger reason
languages.

## H140 — cached-calculus lower bound

### Graph tautologies

- Verify the smart encoding and actual input length.
- Verify the historical basic Formula-Caching lower-bound convention.
- Prove robustness under Policy-0A local Resolution.
- Explain why polynomially many local clauses per state cannot destroy the
  lower-bound invariant.
- Charge Weakening/Subsumption lookup work.
- Keep graph tautologies separate from stronger clause-learning systems with
  polynomial proofs.

Current finite pressure: GT_9 uses 4,001 states with local Resolution and 6,230
without it. GT_8 Weakening/Subsumption saves one state at a cost of 26,159,347
clause-pair checks. The GT_8 local pass emits 18,014 resolvents, 11,897 repeated.

### MAJ3-lifted Tseitin

- Verify exact lifted encoding and affine-dispatch bypass from C022.
- Prove a lower bound for residual-judgement DAGs with local proof ledgers, or a
  valid simulation into a proof system covered by lifting.
- Do not transfer the no-cache C022 theorem through memoization without a cache
  composition rule.

No C023 result resolves P versus NP or lower-bounds unrestricted SAT algorithms.
