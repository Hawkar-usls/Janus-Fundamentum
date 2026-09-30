# C025-B2 — Extension-Aware Portable Reason v0

**Status:** `PROVED_IN_SCOPE` for certificate soundness, context-independent original-variable reuse, and frozen verifier admission rules. Provider replay PASS after post-PASS definition-closure repair.

**Claim ceiling:** this does **not** establish universal polynomial proof size, polynomial active representation, deterministic polynomial proof search, `P=NP`, or `P!=NP`.

## Frozen language

For canonical root CNF `F0`, an extension definition is

```text
EXTEND(e, a, b)
e <-> (a AND b)
```

with exact definitional CNF

```text
(~e OR a)
(~e OR b)
(e OR ~a OR ~b)
```

Rules:

1. extension ids are fresh and strictly increasing above root ids;
2. operands reference root or earlier extension variables only;
3. proof nodes are `ROOT_AXIOM`, `EXTENSION_AXIOM`, or exact `RESOLVE`;
4. the advertised reusable clause contains root/original variables only;
5. every serialized proof node is reachable from the final node;
6. every declared extension definition is in the transitive definition closure required by reachable extension axioms;
7. portable export prunes unused nodes and definitions.

## Conservative-extension theorem

Every assignment to root variables extends sequentially by setting

```text
e := value(a) AND value(b).
```

Because dependencies are topological, every definition is well-defined and all three definitional clauses are satisfied.

Therefore, if the verifier accepts a derivation of original-variable clause `C`, then every model of `F0` extends to a model of the definitions and hence satisfies `C`. Since `C` contains original variables only,

```text
F0 |= C.
```

If a partial root assignment `rho` falsifies `C`, then `F0|rho` is UNSAT. □

## Extension-participating fixture

From

```text
(a OR c)
(b OR c)
(~a OR ~b OR d)
```

with `e <-> (a AND b)`, the verified derivation obtains `(e OR c)`, `(~e OR d)`, and finally original-only `(c OR d)`.

## Strengthened provider replay

Authoritative replay occurred after TOPA found a certificate-payload loophole involving unused extension definitions.

```text
branch      = c025-policy0b-fair-reason
PR          = #214
head        = 736f4b7e532ee285bcb6f05b48e47c483a2c0613
workflow    = Validate C025 Fair Scheduler and Reasons
run         = 32720170819
job         = 97409694435
conclusion  = SUCCESS
```

Positive provider markers include:

```text
C025_B2_EXTENSION_AWARE_VERIFIER = PASS
C025_B2_CONSERVATIVE_ORIGINAL_CLAUSE_REUSE = PASS
C025_B2_EXTENSION_PARTICIPATING_FIXTURE = PASS
C025_B2_EXTENSION_DEFINITION_CLOSURE = PASS
C025_B2_BUILDER_UNUSED_DEFINITION_PRUNING = PASS
C025_B2_EXTENSION_LEAK_REJECTION = PASS
```

Adversarial replay rejects root collision, duplicate/nonfresh ids, descending ids, forward and cyclic dependency attempts, extension leak, extension-axiom clause/slot tampering, Resolution tampering, advertised-clause tampering, wrong root binding, unreachable proof-node garbage, and unused-definition garbage.

## Authority split

Canonical research/process source and machine-readable receipt live in `Hawkar-usls/TOPA`.

Fundamentum is the proof-provider/replay surface. Provider PASS establishes only the frozen verifier/soundness scope.

## Exact frontier

```text
C025_B2_EXTENSION_RULE_SEMANTICS             = FROZEN_V0
C025_B2_CONSERVATIVE_EXTENSION_SOUNDNESS     = PROVED
C025_B2_ORIGINAL_CLAUSE_REUSE                = PROVED
C025_B2_STANDALONE_VERIFIER                  = PROVIDER_PASS
C025_B2_ADVERSARIAL_ADMISSION_SUITE          = PROVIDER_PASS
C025_B2_DEFINITION_CLOSURE                   = PROVIDER_PASS
C025_B2_STATUS                               = PROVED_IN_SCOPE

C025_E1_PLAIN_RESOLUTION_CERT_SIZE           = REFUTED
C025_E2_UNIVERSAL_EXTENSION_AWARE_PROOF_SIZE = OPEN
C025_C2_EXTENSION_DEFINITION_DISCOVERY       = OPEN
C025_C2_GLOBAL_DETERMINISTIC_PROOF_SEARCH    = OPEN
ISSUE_212_ACTIVE_REPRESENTATION              = OPEN
P_VS_NP                                      = OPEN
```

Hard law:

```text
SOUNDNESS != CERTIFICATE_SIZE != CACHE_SIZE != PROOF_DISCOVERY != TOTAL_RUNTIME
```
