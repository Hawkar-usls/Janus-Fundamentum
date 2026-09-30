# C025 — Akinator RSPC bounded-support ER3 elimination

Canonical TOPA source:

`Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_AKINATOR_RSPC_BOUNDED_SUPPORT_ER3_ELIMINATION.md`

Status: **INTERNAL ANALYTIC THEOREM**  
Claim ceiling: **P_VS_NP = OPEN**

## Theorem

Let `pi` be an ER3/B2 refutation of root CNF `F` with `S` proof lines. Let

`K_root(pi) = max_e |supp(e)|`

where `supp(e)` is the transitive syntactic root support of extension variable `e`.

Every width-3 ER3 clause can be substituted into a root Boolean formula on at most `3*K_root` roots and encoded by its canonical falsifying-assignment CNF. One ER3 Resolution inference involves at most `6*K_root` roots. Brute-force Resolution saturation of that local clause space has at most `3^(6*K_root)=2^O(K_root)` clauses.

Thus bounded-support extensions can be eliminated with

`ResSize(F) <= S * 2^O(K_root(pi))`.

Extension-definition axioms substitute to tautologies; root axioms remain root clauses; the final empty clause remains empty.

## Frozen hard-family consequence

Using the previously frozen root Resolution lower bound

`ResSize(F_N) >= exp(N^eta)`

for fixed `eta>0`, any hypothetical polynomial-size ER3 escape `S<=N^d` must satisfy

`K_root(pi)=Omega(N^eta)`.

Since the direct parity encoding has `2^(Delta-1)<=N`, hence `Delta<=log_2 N+1`, at least one extension macro has minimum NW-neighborhood cover

`Omega(N^eta/log N)`.

## Meaning

This does **not** prove a superpolynomial ER3 size lower bound. It proves that a polynomial-size ER3 refutation, if one exists, must contain a large-support extension macro.

Consequently the fixed-cover exact truth-table survival route cannot serve as a universal polynomial selector mechanism: at the forced large-support macro its exhaustive route costs `2^Omega(N^eta)` assignments.

This still does not prove that every semantic-survival algorithm for that macro needs exponential time.

## Next gate

Find a succinct large-support proof-carrying certificate with polynomial bytes, deterministic polynomial discovery and verification, no SAT/model-counting oracle, no exponential witness frontier, no backtracking, source-matched restriction survival, and a globally sound polynomial progress potential.

Tracking: `Hawkar-usls/Janus-Fundamentum#227`.

`UNRESTRICTED_ER3_SUPERPOLY_SIZE_LOWER_BOUND = NOT_PROVED`  
`POLYNOMIAL_AKINATOR = OPEN`  
`P_VS_NP = OPEN`
