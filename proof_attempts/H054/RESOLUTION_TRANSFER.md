# H054 — policy-independent conflict lower bound from Resolution

## Statement under audit

H054 says that every fixed polynomial-time ordinary-CDCL policy has an explicit unsatisfiable CNF family requiring superpolynomially many conflicts.

## Stronger transfer

Under standard first-UIP learning and Resolution proof logging, the hard family need not depend on the policy.

Choose one explicit bounded-degree expander Tseitin family `T_n` requiring exponential-size general-Resolution refutations.

For any fixed branching, restart, and deletion policy:

1. a run with polynomially many conflicts expands into a polynomial-size Resolution proof;
2. every Resolution proof of `T_n` is exponential;
3. therefore the run must have superpolynomially many conflicts, fail its claimed polynomial resource bound, or leave the ordinary Resolution proof model.

The same `T_n` works for every policy covered by the model.

## Preprocessing boundary

Polynomial preprocessing does not help when each transformation is accompanied by a polynomial Resolution derivation permitting the final proof to be translated back to the original CNF. A stronger unlogged preprocessing language may leave Resolution and must be modeled separately.

## Status discipline

This document records a mathematical reduction and strong evidence for H054. The registry does not label H054 `PROVED`, because JANUS reserves that status for R5 formalization and independent verification.

## Primary sources

- `R056`: explicit general-Resolution lower bounds through width.
- `R058`: polynomial relationships between standard CDCL learning and Resolution.
- `R059`: tractable structural subclasses do not imply a universal CDCL policy.
