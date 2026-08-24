# C025-E2R-L1G-F2 — Negative-edge budget to macro cut-elimination cost

**Status:** `ANALYTICAL_PROOF_COMPLETE_PENDING_PROVIDER_REPLAY`.

This provider note mirrors the TOPA canonical proof. Let `q` be the global number of negative crossing dependency edges and `S>=2` the explicit B2/ER3 proof volume.

F1 gives a safe per-literal structural CNF expansion bound `S^((q+2)!)`; width three therefore gives a per-source-line expansion ceiling `B_q=S^((q+3)!)`.

## Weakening elimination

Weakening is used only as analytical scaffolding. Any Resolution+Weakening proof of empty can be normalized to pure Resolution with no node increase by maintaining a stronger subclause at each old node: weakening aliases its parent; a Resolution node is replayed if the complementary pivot survives in the stronger parents, otherwise the stronger parent that lost the pivot already subsumes the old resolvent. The final stronger subclause of empty is empty.

## Context lifting

Given a pure Resolution refutation of `Gamma union Delta`, contextual premises `gamma OR C` for every `gamma in Gamma`, and `Delta`, weaken every side to carry context `C`, replay the refutation, and derive `C`. Global weakening normalization then removes the scaffolding. Overlap between context and proof variables is allowed.

## Macro complement refutation

Use the F1 positive-closure form

`F = L AND (~F_1) AND ... AND (~F_k)`, `k<=q`.

`P(F)` contains local units and each `N(F_j)`. `N(F)` is the Cartesian CNF of clauses `neg(L) OR p_1 OR ... OR p_k`, `p_j in P(F_j)`.

Resolve away `neg(L)` with local units. Then eliminate frontier children sequentially by context-lifting an inductive refutation of `P(F_j) union N(F_j)`. No disjointness of child cones is assumed.

With `H(q)=(q+2)!`, the safe recurrence

`R_q <= S^(H(q)+1) + q*S^H(q)*R_(q-1)`

is dominated by

`R_q <= S^((q+4)!)`.

## Macro pivot simulation

For an ER3 pivot `(A OR e),(B OR ~e) -> A OR B`, expand source and target lines. For each target local clause `alpha OR beta`, the parents contain the contextualized `P(F)` and `N(F)` premises. Lift the complement refutation to derive a clause contained in `alpha OR beta`.

Combining the width-3 line expansion, complement-refutation ceiling, and at most `S` original proof nodes gives the deliberately loose full bound

`S_local <= S^((q+5)!)`.

After identifying duplicate NW-local function variables by literal substitution, this is a pure Resolution proof of the functional encoding used by the established NW heavy-width transfer.

## Hard-family consequence

For the polynomial-input NW-parity family, absorb the source polylog loss to write `L(N)>=exp(N^eta)` for some fixed `eta>0` and sufficiently large family members. If `S<=N^d`, then

`(N^d)^((q+5)!) >= exp(N^eta)`.

Hence `(q+5)!*O(log N)>=N^eta`, so by `log(r!)=Theta(r log r)`,

`q = Omega(log N / log log N)`.

This is a structural lower bound on negative crossing edges in every polynomial-size unrestricted ER3/B2 escape for the stated existential family. It is not a superpolynomial total-extension lower bound and does not resolve Issue #217.

Exact gate status before provider replay:

```text
F2_WEAKENING_ELIMINATION       = PROVED_ANALYTICALLY
F2_CONTEXT_LIFTING             = PROVED_ANALYTICALLY
F2_COMPLEMENT_REFUTATION       = PROVED_ANALYTICALLY
F2_MACRO_PIVOT_SIMULATION      = PROVED_ANALYTICALLY
F2_FULL_LOCAL_SIMULATION       = PROVED_ANALYTICALLY
F2_Q_LOWER_BOUND               = DERIVED_FROM_SOURCE_LOWER_BOUND
F2_PROVIDER_REPLAY             = PENDING
ISSUE_217_FULL_ER3             = OPEN
P_VS_NP                        = OPEN
```
