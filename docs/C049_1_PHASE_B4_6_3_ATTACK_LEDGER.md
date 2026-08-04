# Router Hardening Lab-1 — B4.6.3 Attack Ledger

```text
LAB = Router Hardening Lab-1
GATE = C049.1 B4.6.3
DOOR = TERMINAL COMPLETENESS
SIM-3 = RESERVED FOR EXTERNAL AUTHOR
```

## Active attacks

| Attack | Expected safe response |
|---|---|
| Delete an accepting fixture witness and repair outer digests | Reject |
| Convert bounded exhaustive no-layout evidence into engine `NO_LAYOUT_AT_CAP` without a root certificate | Reject |
| Treat insertion-only failure as global nonexistence | Reject |
| Treat budget exhaustion as nonexistence | Reject |
| Alter a `FOUND_LAYOUT` whole-factor order without recomputing exact cuts | Reject |

## Current result

All five controls are implemented in the independent verifier. The A-gate closes only the terminal contract. It does not close the semantic induction from leaf languages to the root language.

## Open attack surface

```text
A1 leaf language exactly represented by the canonical leaf full set
A2 every feasible parent trajectory reflected by some child pair and lattice path
A3 failed width refinements cannot hide a feasible compact representative
A4 B2 dominance/up_k deletion preserves and reflects the represented language
A5 node-local biconditionals compose to the root
A6 empty accepting root plus complete transcript implies NO_LAYOUT_AT_CAP
```

Every counterexample must retain the complete fixture, factor partition, affine offsets, selected scaffold, child entries, lattice path, refinement result, deletion witness, work ledger and certificate byte accounting.
