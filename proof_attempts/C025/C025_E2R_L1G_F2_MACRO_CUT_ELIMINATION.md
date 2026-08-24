# C025-E2R-L1G-F2 — Negative-edge budget to macro cut-elimination cost

**Status:** `ANALYTICAL_PROOF_V1_1_COMPLETE_PENDING_PROVIDER_REPLAY`.

Let `q` be the global number of negative crossing dependency edges and `S>=2` the explicit B2/ER3 proof volume. F1 gives per-literal structural expansion `<=S^((q+2)!)`; ER3 width three gives a safe per-line expansion ceiling `B_q=S^((q+3)!)`.

## Pure context lifting

The authoritative v1.1 route uses no weakening.

For a partial assignment `rho`, restricting a pure Resolution proof gives a pure Resolution proof of the restricted CNF with no size increase: each old Resolution step either remains a Resolution step or one restricted parent already subsumes the restricted resolvent.

For a non-tautological context clause `C`, let `rho_C` falsify every literal of `C`. If a current derivation contains clauses contained in `gamma OR C` for all `gamma in Gamma` plus `Delta`, and `Gamma union Delta` has a Resolution refutation `pi`, then restrict by `rho_C`, replay the restricted `pi`, and lift the restricted refutation back. Every literal removed as false under `rho_C` belongs to `C`, so the lifted pure-Resolution derivation ends in a clause `C' subseteq C`. Context/proof-variable overlap is allowed.

## Macro complement refutation

Use the F1 positive-closure normal form

`F = L AND (~F_1) AND ... AND (~F_k)`, with `k<=q`.

`P(F)` contains local units and every `N(F_j)`; `N(F)` consists of Cartesian clauses `neg(L) OR p_1 OR ... OR p_k`, `p_j in P(F_j)`.

Resolve away `neg(L)` with local units. Then eliminate frontier children sequentially by the pure context-lifting lemma applied to an inductive refutation of `P(F_j) union N(F_j)`. No disjointness of child cones is assumed.

With `H(q)=(q+2)!`, the safe recurrence

`R_q <= S^(H(q)+1) + q*S^H(q)*R_(q-1)`

is dominated by

`R_q <= S^((q+4)!)`.

## Macro pivot and full proof

For an ER3 pivot `(A OR e),(B OR ~e)->A OR B`, expand source and target lines. For each target local clause `alpha OR beta`, the parent expansions contain contextualized `P(F)` and `N(F)` premises. Pure context lifting of the complement refutation derives a subclause of `alpha OR beta`.

Combining line expansion, complement-refutation cost and at most `S` source proof nodes gives

`S_local <= S^((q+5)!)`.

After the already-audited NW-local literal substitution, this is a pure Resolution proof of the functional encoding used by the heavy-width lower bound.

## Hard-family consequence

For the polynomial-input NW-parity family, absorb fixed polylog losses to write `L(N)>=exp(N^eta)` for some fixed `eta>0` on sufficiently large family members. If `S<=N^d`, then

`(N^d)^((q+5)!) >= exp(N^eta)`.

Hence `(q+5)!*O(log N)>=N^eta`, and `log(r!)=Theta(r log r)` yields

`q = Omega(log N / log log N)`.

Thus every polynomial-size unrestricted ER3/B2 escape on the stated existential family needs a growing polarity-inversion DAG with at least `Omega(log N/log log N)` negative crossing edges.

This is not a superpolynomial total-extension lower bound and does not resolve Issue #217.

```text
F2_RESTRICTION_LEMMA            = PROVED_ANALYTICALLY
F2_PURE_CONTEXT_LIFTING         = PROVED_ANALYTICALLY
F2_COMPLEMENT_REFUTATION        = PROVED_ANALYTICALLY
F2_MACRO_PIVOT_SIMULATION       = PROVED_ANALYTICALLY
F2_FULL_LOCAL_SIMULATION        = PROVED_ANALYTICALLY
F2_Q_LOWER_BOUND                = DERIVED_FROM_SOURCE_LOWER_BOUND
F2_PROVIDER_REPLAY              = PENDING
ISSUE_217_FULL_ER3              = OPEN
P_VS_NP                         = OPEN
```
