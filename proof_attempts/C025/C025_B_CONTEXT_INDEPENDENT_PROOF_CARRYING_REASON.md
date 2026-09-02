# C025-B — Context-Independent Proof-Carrying Reason

**Status:** portable reason semantics frozen; soundness proved; portable-v1 provider replay pending.

**Claim ceiling:** this is a soundness/portability theorem for returned Policy-0B reasons. It does not establish polynomial total SAT search, polynomial reason discovery, polynomial certificate size, `P=NP`, or `P!=NP`.

## 1. Portable reason object

For canonical root CNF `F0`, return the self-contained object

```text
R = (root_fingerprint, advertised_clause C, final_node, reachable_resolution_DAG pi)
```

Every leaf is an indexed root clause checked against `F0`; every internal node is an exact Resolution step; `final_node` is exactly `C`; all serialized nodes must be reachable from the final node. Decision assumptions are forbidden as proof axioms.

The verifier needs only `(F0,R)` and shares no producer proof store or local node numbering.

This repairs a post-CI gap in the first implementation: `(root_hash, local_node_number)` was safe inside one proof store but was not a genuinely portable standalone certificate.

## 2. Theorems

### B1 — certificate soundness

If `VERIFY(F0,R)=PASS`, then `F0 |= C`.

**Proof.** Accepted leaves are clauses of `F0`; Resolution preserves logical consequence; induct over the proof DAG. □

### B2 — context-independent reuse

If `rho` falsifies every literal of certified `C`, then `F0|rho` is UNSAT. □

### B3 — branch composition

For branch variable `x`, if certified reasons are applicable to `rho+x=0` and `rho+x=1`, either one already applies to `rho`, or the false reason contains `x`, the true reason contains `~x`, and their resolvent is certified and falsified by `rho`. □

In a **shared logical proof DAG**, this adds one Resolution node. A standalone serialized certificate must also materialize the reachable child sub-DAGs, so portable byte size is not constant-overhead. That cost belongs to C025-E/#212.

### B4 — unit-conflict lifting

With globally certified unit antecedents, reverse-resolution over the propagation trace eliminates propagated literals and returns a globally certified clause falsified by the decision assignment alone. At most one new logical Resolution node is added per eliminated propagated variable in the shared producer DAG. □

### B5 — verifier complexity

Verification is deterministic polynomial time in encoded certificate size `M`. This does not imply `M=poly(N)` for original input size `N`. □

## 3. Cost firewall

Keep distinct:

```text
REASON_VALIDITY                    = C025-B
REASON_PORTABILITY                 = C025-B
REASON_LOCAL_CONSTRUCTION          = trace/shared-DAG relative
REASON_DISCOVERY_IN_CACHE          = C025-C OPEN
TOTAL_REASON_DAG_SIZE              = C025-E/#212 OPEN
GLOBAL_DETERMINISTIC_PROOF_SEARCH  = C025-C/D OPEN
```

Hard boundaries:

```text
CHEAP_REASON_CHECK != CHEAP_REASON_DISCOVERY
SHORT_REASON_EXISTS != DETERMINISTIC_POLICY_FINDS_IT_IN_POLYTIME
ONE_NEW_LOGICAL_DAG_NODE != CONSTANT_PORTABLE_CERTIFICATE_BYTES
DAG_SHARING != POLY_TOTAL_DAG_SIZE_WITHOUT_A_BOUND
```

## 4. Literature boundary

Beame–Impagliazzo–Pitassi–Segerlind, *Formula Caching in DPLL* (ACM TOCT 1(3), 2010), define the more general formula-level `FCW_reason` and prove that proof system p-simulates regular Resolution. C025 clause reasons are deliberately stricter. No simulation or proof-search consequence is imported without a separate theorem.

## 5. Portable-v1 replay gates

Provider CI must pass:

1. standalone certificate verification with no shared producer store;
2. cross-context reuse;
3. same-root/different-store node-number independence;
4. branch composition;
5. reverse unit-conflict lifting;
6. wrong-root rejection;
7. advertised-clause tamper rejection;
8. internal proof tamper rejection;
9. unreachable proof-garbage rejection.

Canonical research/process source: `Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_B_CONTEXT_INDEPENDENT_PROOF_CARRYING_REASON.md`.

```text
C025_B_CERTIFICATE_SOUNDNESS            = PROVED
C025_B_CONTEXT_REUSE                    = PROVED
C025_B_BRANCH_COMPOSITION_LOGIC         = PROVED
C025_B_UNIT_CONFLICT_LIFT_LOGIC         = PROVED
C025_B_VERIFY_COST_IN_CERTIFICATE_SIZE  = PROVED
C025_B_PORTABLE_V1_PROVIDER_CI          = PENDING
C025_C_REASON_DISCOVERY                 = OPEN
C025_E_TOTAL_REASON_SIZE                = OPEN
P_VS_NP                                 = OPEN
```
