# C025-E1 — Resolution-Certificate Size Barrier

**Status:** the universal polynomial-size target is refuted for the current clause-only portable C025-B Resolution-DAG language.

**Claim ceiling:** this does not prove `P!=NP` and does not refute stronger proof-carrying systems. It refutes one certificate representation target.

## Lemma E1 — root applicability forces the empty clause

A C025-B reason applies to context `rho` only if `rho` falsifies every literal of its advertised clause `C`. The empty root assignment assigns no variable, so it cannot falsify a nonempty clause. Therefore any root-applicable reason advertises the empty clause. □

## Corollary E2 — root reason is a Resolution refutation

The portable C025-B proof DAG has root-CNF clauses as axioms and exact Resolution as its only inference rule. If its advertised root clause is empty, the certificate is exactly a Resolution DAG refutation of the original CNF. □

## External lower bound

Haken, **The intractability of resolution**, Theoretical Computer Science 39 (1985), 297–308, proves that the pigeonhole tautology family has no polynomial-length Resolution proofs. The abstract also explicitly notes that Extended Resolution can furnish polynomial-length proofs for these same formulas.

The pigeonhole CNF family has polynomial encoded input size in its family parameter. Thus its Resolution refutation size is superpolynomial in original input length.

## Theorem E3 — no universal polynomial C025-B-v1 root-certificate bound

There is no fixed exponent `a` such that every UNSAT CNF of encoded length `N` has a root-applicable C025-B-v1 portable certificate of size at most `N^a`.

**Proof.** On the pigeonhole family, Corollary E2 turns every root C025-B-v1 certificate into a Resolution refutation. Haken's lower bound is superpolynomial while the input encoding is polynomial-size. □

The obstruction is not removed by ordinary proof-DAG sharing; Resolution proof-size lower bounds already measure DAG-style proofs, not merely naive tree copying.

## What survives

```text
C025_B_REASON_SOUNDNESS       = PROVED_IN_SCOPE
C025_B_PORTABILITY            = PROVED_IN_SCOPE
C025_C1_CACHE_QUERY_IN_M      = PROVED
```

Plain Resolution reasons remain a safe local learned-clause language.

What is refuted is:

```text
FOR_EVERY_UNSAT_F:
  POLY_SIZE_STANDALONE_ROOT_REASON_IN_PLAIN_RESOLUTION
```

## Required successor

C025-B2 must use a stronger or heterogeneous, independently verifiable certificate language. Extension/abbreviation rules are a natural first candidate because Extended Resolution bypasses the known pigeonhole obstruction.

This does **not** establish universal polynomial proof size or deterministic polynomial proof search for Extended Resolution.

```text
C025_E1_POLY_RESOLUTION_CERT_SIZE = REFUTED
C025_B2_STRONGER_REASON_LANGUAGE  = REQUIRED
C025_C2_GLOBAL_PROOF_SEARCH       = OPEN
C025_E2_STRONGER_PROOF_SIZE       = OPEN
P_VS_NP                           = OPEN
```

Canonical process source: `Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_E_RESOLUTION_CERTIFICATE_SIZE_BARRIER.md`.
