# C025-B — Context-Independent Proof-Carrying Reason

**Status:** reason semantics frozen; standalone verifier mirrored from TOPA; CI required before promotion.

**Claim ceiling:** this is a reason-soundness result for Policy-0B. It does not establish polynomial total SAT search, polynomial cache discovery, polynomial active representation, `P=NP`, or `P!=NP`.

## Reason object

For canonical root CNF `F0`, a returned UNSAT reason is

```text
R = (root_fingerprint, clause C, resolution_DAG pi)
```

where every leaf of `pi` is an indexed clause of `F0`, every internal node is an exact Resolution step, and the final node is `C`. Decision assumptions are never proof axioms.

`R` applies to partial assignment `rho` exactly when `rho` falsifies every literal of `C`.

## Theorem B1 — certificate soundness

If the standalone verifier accepts `pi`, then `F0 |= C`.

**Proof.** Root clauses are consequences of `F0`; Resolution preserves consequence; induct over the proof DAG. □

## Theorem B2 — context-independent reuse

If `VERIFY(F0,R)=PASS` and `rho` falsifies `C`, then `F0|rho` is UNSAT.

**Proof.** Every model of `F0` satisfies `C`, while any extension of `rho` falsifies `C`. □

Thus reason reuse depends only on an independently verified global implicate and a local falsification test, not on residual identity or similarity.

## Lemma B3 — branch composition

Let `x` be unassigned in parent context `rho`. Let certified child reasons `C0,C1` be applicable to `rho+x=0` and `rho+x=1` respectively.

- if `rho` already falsifies one child reason, return it unchanged;
- otherwise `C0` must contain `x` and `C1` must contain `~x`;
- resolve them on `x` and return the resolvent.

The resolvent is globally certified by one new Resolution node and is falsified by `rho`. □

## Lemma B4 — unit-conflict lifting

Every propagated literal carries a certified antecedent clause that was unit at the propagation prefix. Starting from a certified conflict clause, resolve propagated literals away in reverse propagation order using those antecedents. The final clause is globally certified and falsified by the decision assignment alone.

At most one Resolution node is added per eliminated propagated variable. □

## Cost firewall

The verifier is polynomial in the encoded certificate size. Branch composition has constant proof-node overhead; unit-conflict lifting is polynomial in the supplied propagation trace.

None of these implies a polynomial bound in original input length `N` because the explored trace, reason cache, and proof DAG may themselves be superpolynomial.

Keep distinct:

```text
REASON_VALIDITY
REASON_LOCAL_CONSTRUCTION
REASON_DISCOVERY_IN_CACHE
TOTAL_REASON_DAG_SIZE
GLOBAL_PROOF_SEARCH
```

`REASON_DISCOVERY_IN_CACHE` and `TOTAL_REASON_DAG_SIZE` remain open gates.

## Literature boundary

Beame–Impagliazzo–Pitassi–Segerlind, *Formula Caching in DPLL* (ACM TOCT 2010), define the more general formula-level `FCW_reason` system and prove it p-simulates regular Resolution. C025's clause-only reason object is intentionally stricter. The external p-simulation theorem is motivation only until a formal simulation/equivalence is proved.

## Required replay

The mirrored standalone verifier must pass:

1. direct Resolution reason verification;
2. cross-context reuse;
3. branch composition;
4. reverse unit-conflict lifting;
5. malformed proof rejection;
6. root-fingerprint mismatch rejection.

Canonical research/process source: `Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_B_CONTEXT_INDEPENDENT_PROOF_CARRYING_REASON.md`.

Current frontier:

```text
C025_B_REASON_SOUNDNESS              = PROVED_ON_PAPER
C025_B_CONTEXT_REUSE                 = PROVED_ON_PAPER
C025_B_BRANCH_COMPOSITION            = PROVED_ON_PAPER
C025_B_UNIT_CONFLICT_LIFT            = PROVED_ON_PAPER
C025_B_PROVIDER_CI                   = PENDING
C025_C_REASON_DISCOVERY              = OPEN
C025_E_TOTAL_REASON_SIZE             = OPEN
P_VS_NP                              = OPEN
```
