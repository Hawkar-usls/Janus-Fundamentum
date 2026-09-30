# C025 — Policy-0B.1 Resolution Lower-Bound Route Closure

**Status:** `POLICY0B1_POLYTIME_ROUTE_REFUTED_BY_RESOLUTION_LOWER_BOUND`.

Every complete UNSAT execution of the frozen Policy-0B.1 baseline compiles to an ordinary Resolution refutation of the root CNF:

- retained strengthenings are explicit Resolution resolvents;
- local UP/conflicts under a decision context are lifted to a root-derived blocking clause by the already-used restriction/lift lemma;
- sibling blocking clauses compose by one Resolution inference on the branch variable;
- at the empty root context the final blocking clause is empty.

If the execution visits `T` recursive states and each state performs at most fixed-polynomial local work, the compiled Resolution proof has size

`<= T * N^O(1)`.

Haken's exponential Resolution lower bound for the standard pigeonhole principle therefore implies an unconditional superpolynomial/exponential-in-the-PHP-parameter state/work lower bound for Policy-0B.1.

For standard `PHP_{n+1}^n`:

`RES_SIZE >= 2^(Omega(n))`, while the CNF input size is polynomial in `n`, so

`T >= 2^(Omega(n))/n^O(1) = 2^(Omega(n))`.

Thus:

```text
POLICY0B1_UNIVERSAL_POLYNOMIAL_TOTAL_RUNTIME = REFUTED.
```

This closes only the frozen plain-Resolution baseline. It does not imply `P!=NP` and does not lower-bound B2/Extended Resolution. In fact PHP has polynomial-size proofs in stronger Extended-Resolution/Frege-style systems, so the result identifies exactly why Policy-0B.2 must add a genuine proof-power/discovery escape rather than merely polish the baseline scheduler.

```text
POLICY0B1_TOTAL_CORRECTNESS          = PROVED
POLICY0B1_EXECUTION_TO_RESOLUTION     = PROVED
POLICY0B1_POLY_TOTAL_RUNTIME          = REFUTED
POLICY0B2_STRONGER_DISCOVERY          = REQUIRED
C2_DETERMINISTIC_DISCOVERY            = OPEN
P_VS_NP                               = OPEN
```

Arbiter: `Hawkar-usls/Demi_Head/docs/TOPA_POLICY0B1_RESOLUTION_LOWER_BOUND_ROUTE_CLOSURE.md`.
