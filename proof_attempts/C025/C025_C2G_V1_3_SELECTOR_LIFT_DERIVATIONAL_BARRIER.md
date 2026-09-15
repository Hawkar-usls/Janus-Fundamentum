# C025-C2G v1.3 — Selector-Lift Derivational Barrier

**Status:** `SHORT_LAMINAR_REASON_GEOMETRY_DOES_NOT_REMOVE_DERIVATIONAL_HARDNESS`.

For arbitrary CNF `H={C_i}` and fresh root selector `s`, define

```text
Sel_s(H) = { (s OR C_i) : C_i in H }.
```

This formula is always satisfiable at `s=1`, while

```text
Sel_s(H) |= s  iff  H is UNSAT.
```

Therefore exact recognition of the width-1 root reason `(s)` is coNP-complete.

## Plain Resolution proof equivalence

Any Resolution refutation of `H` lifts by adjoining `s` to every root-dependent clause. The final empty clause becomes `(s)`.

Conversely, restricting any derivation of `(s)` from `Sel_s(H)` by `s=0` yields a Resolution refutation of `H`.

Hence

```text
RES_REFUTATION_SIZE(H)
<->_linear/poly
RES_DERIVATION_SIZE(Sel_s(H) |- s).
```

## B2 / ER version

The same reduction respects the frozen B2/Extended-Resolution language up to the already admitted polynomial encodings. A proof of `(s)` restricts at `s=0` to an ER refutation of `H`; an ER refutation of `H` lifts with the same extension definitions and polynomial overhead to a derivation of `(s)`.

Thus a width-1 conclusion may hide the complete derivational complexity of the original UNSAT instance.

## Consequence for exact total discovery

If a deterministic total procedure, in polynomial time, returns a verifier-accepted proof of `(s)` exactly when `Sel_s(H)|=s` and `NONE` otherwise, then it decides CNF-UNSAT in polynomial time. Therefore such a universal exact selector-reason discovery algorithm implies

```text
P = NP = coNP.
```

This is an implication theorem, not an existence theorem.

## C2G interpretation

v1.2 solved a **counting geometry** problem conditionally: short laminar fork charges imply polynomially many states.

v1.3 shows that neither width nor geometry supplies the proof/discovery for free:

```text
SHORT_REASON_WIDTH != SHORT_REASON_PROOF != CHEAP_REASON_DISCOVERY.
```

The remaining gate is therefore derivational/search complexity, not cube bookkeeping.

```text
C2G_SELECTOR_UNIT_REASON_RECOGNITION       = coNP-COMPLETE
C2G_SELECTOR_PLAIN_RES_PROOF_EQUIVALENCE   = PROVED
C2G_SELECTOR_B2_ER_PROOF_EQUIVALENCE       = PROVED_UP_TO_FROZEN_POLY_ENCODING
C2G_POLY_TOTAL_SELECTOR_DISCOVERY_IMPLIES_PNP = PROVED_AS_IMPLICATION
C2G_UNIVERSAL_POLY_DISCOVERY               = OPEN
P_VS_NP                                    = OPEN
```

Arbiter: `Hawkar-usls/Demi_Head/docs/TOPA_C025_C2G_V1_3_SELECTOR_LIFT_DERIVATIONAL_BARRIER.md`.
