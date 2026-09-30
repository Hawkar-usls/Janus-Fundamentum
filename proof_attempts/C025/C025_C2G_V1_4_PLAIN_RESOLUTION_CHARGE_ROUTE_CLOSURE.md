# C025-C2G v1.4 — Plain-Resolution Charge Route Closure

**Status:** `PLAIN_RESOLUTION_FORK_CHARGE_POLY_ROUTE_REFUTED`.

Let `H_n=PHP_{n+1}^n` be the standard pigeonhole CNF with all variables renumbered above selector id `1`. Define

`F_n=Sel_s(H_n)={s OR C : C in H_n}`.

Then `F_n` is SAT at `s=1`, while `F_n|s=0=H_n` is UNSAT and `F_n |= s`.

By the selector-lift theorem, every plain Resolution derivation `F_n |- s` restricts at `s=0` to a Resolution refutation of `H_n`; conversely a refutation of `H_n` lifts to a derivation of `(s)`. Haken's theorem therefore gives

`RES_SIZE(F_n |- s) = 2^Omega(n)`.

Policy-0B.1 root preprocessing has only fixed-polynomial Resolution-contained work. Hence for sufficiently large `n` it cannot derive `(s)` at the root without contradicting Haken. Because `s` is the minimum root id, the baseline reaches the actual root branch on `s`:

- false child `s=0`: `H_n`, UNSAT;
- true child `s=1`: trivially SAT.

At this root fork the first-child root context assigns only `s=0`. The only nonempty non-tautological root clause fully falsified by that context is exactly `(s)`.

Therefore any C2G charge using the C025-B **plain Resolution** reason language is forced to carry an exponential proof certificate on this family. Polynomial total charge-proof bytes and polynomial-time certificate output/discovery are impossible for this lane.

This does not close B2/Extended Resolution: pigeonhole formulas have polynomial-size proofs in stronger Extended-Resolution/Frege-style systems. Hence the theorem requires a genuine stronger-reason escape but does not solve its discovery problem.

```text
C2G_PLAIN_RESOLUTION_CHARGE_PROOF_BYTES = REFUTED_POLY
C2G_PLAIN_RESOLUTION_DISCOVERY           = REFUTED_POLY
C2G_B2_ER_CHARGE_PROOF_SIZE              = OPEN_GENERALLY
C2G_B2_ER_DETERMINISTIC_DISCOVERY        = OPEN
P_VS_NP                                  = OPEN
```

Arbiter: `Hawkar-usls/Demi_Head/docs/TOPA_C025_C2G_V1_4_PLAIN_RESOLUTION_CHARGE_ROUTE_CLOSURE.md`.
