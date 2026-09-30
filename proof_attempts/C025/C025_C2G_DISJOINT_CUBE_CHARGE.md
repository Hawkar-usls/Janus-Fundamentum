# C025-C2G — Disjoint Proof-Carrying Cube Charge

**Status:** `SUFFICIENT_PROGRESS_THEOREM_PROVED__UNIVERSAL_DISCOVERY_OPEN`.

For a non-tautological root clause `C`, define its falsifying cube

`Q(C)={root assignments that falsify every literal of C}`.

If `|C|=r` over `n` roots, then `|Q(C)|=2^(n-r)`.

For two clauses `C,D`:

`Q(C)` and `Q(D)` are disjoint iff some root variable occurs with opposite signs in the two clauses.

Hence pairwise disjointness is polynomially checkable without exact union counting.

If `C_1,...,C_k` have pairwise-disjoint falsifying cubes and `|C_i|<=w`, then

`k*2^(n-w)<=2^n`, so `k<=2^w`.

Therefore if every branch event in a deterministic successor machine is charged to one fresh globally proof-carrying clause satisfying

- standalone proof of `F |= C_j`;
- `|C_j|<=c log_2 N` for universal fixed `c`;
- `Q(C_j)` pairwise disjoint from all earlier charge cubes;

then total branch events are at most `2^w<=N^c`, and the total binary branch tree has polynomially many states.

This is a **sufficient global amortization theorem**. It does not establish that the required reason can be discovered on every branch, nor that all proof/ledger bytes remain polynomial.

Important barrier: branch-local reasons can be made disjoint by adding decision-prefix literals, but full prefix guarding grows width with branch depth and therefore does not preserve the required `O(log N)` width automatically.

```text
C2G_WIDTH_TO_COUNT_BOUND               = PROVED
C2G_BRANCH_COUNT_BOUND                 = PROVED_AS_SUFFICIENT_THEOREM
C2G_UNIVERSAL_DETERMINISTIC_DISCOVERY  = OPEN
C2G_TOTAL_REASON_PROOF_BYTES           = OPEN
P_VS_NP                                = OPEN
```

Arbiter: `Hawkar-usls/Demi_Head/docs/TOPA_C025_C2G_DISJOINT_CUBE_CHARGE_CANDIDATE.md`.
