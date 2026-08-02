# H048 — decisive refutation by general-Resolution lower bounds

## Target

H048 asserted one fixed deterministic first-UIP CDCL policy with polynomial memory and polynomially many conflicts on every CNF, returning a satisfying assignment or a Resolution refutation trace.

## Reduction

Consider an unsatisfiable CNF `F` with `N` variables.

1. Every learned clause produced by ordinary first-UIP conflict analysis has a Resolution derivation from clauses currently available to the solver.
2. The implication graph contains at most polynomially many vertices and edges in `N` and the current database encoding. Expanding one conflict analysis therefore costs at most polynomially many Resolution inferences.
3. If the solver has at most `N^c` conflicts and maintains a polynomial-size explicit proof log, concatenating the conflict derivations and the final contradiction yields a polynomial-size general-Resolution refutation of `F`.

Thus the universal H048 promise implies polynomial-size Resolution refutations for every unsatisfiable CNF.

## Contradiction

Explicit bounded-degree expander Tseitin contradictions require exponential-size general-Resolution refutations. The width-to-size framework of Ben-Sasson and Wigderson gives this for explicit expander-based families.

Therefore H048's polynomial-conflict promise cannot hold on all CNFs.

## Why policy changes do not help

The lower bound quantifies over all general-Resolution refutations. It is independent of the branching heuristic, restart schedule, clause-deletion policy, and deterministic tie breaking. Those choices can alter which Resolution proof is found, but cannot create a polynomial proof when every Resolution proof is exponential.

## Boundary

This refutation applies to ordinary CDCL whose logged proof remains in Resolution. It does not automatically apply to descendants that change the proof system, such as H063 with arbitrary parity decisions and Res(XOR) proof logging.

## Primary sources

- `R056`: Ben-Sasson and Wigderson, *Short Proofs Are Narrow — Resolution Made Simple*.
- `R058`: Vinyals et al., *Limits of CDCL Learning via Merge Resolution*.

## Verdict

`H048 = DESTROYED` by decisive attack `A137`.
