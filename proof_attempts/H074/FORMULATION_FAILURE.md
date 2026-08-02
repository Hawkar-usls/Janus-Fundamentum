# H074 — formulation failure

## Terminal status

`REJECTED`

H074 attempted to require SAT and UNSAT families to agree on a bounded-level theta profile, all registered low-degree moments, and every polynomial-bit dual statistic exposed by a preprocessing grammar.

## Decisive failure

The quantified observable interface was never fixed.

1. **The profile was not finite or canonical.** No encoding, monomial basis, coordinate order, objective list, or equality convention was specified.
2. **The statistic set depended on the grammar.** A permitted grammar could expose an additional polynomial-bit field containing the SAT answer itself. The universal equality demand would then become trivially false.
3. **Independent falsification was impossible.** Two implementations could choose different observables and reach incompatible conclusions without disagreeing on any formal statement.

These defects are recorded as decisive attacks `A203` and `A204`.

## Why this is rejection, not a mathematical lower bound

The intended bounded-theta obstruction may still be true after formalization. What failed is the exact registered statement, not every possible descendant.

## Salvage

`H078` fixes one Boolean-ideal encoding, one finite monomial basis through degree `2k`, one objective list, and one coordinate-normalized equality relation. `H081-H082` separately define the rational certificate and bit-complexity interface.

No result here proves a theta or SoS lower bound.
