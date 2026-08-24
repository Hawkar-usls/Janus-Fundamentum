# C025-B2 — Extension-Aware Portable Reason v0

**Status:** candidate stronger reason language; conservative-extension soundness proved on paper; provider verifier/replay required before promotion.

**Claim ceiling:** this language is designed to remove the known plain-Resolution pigeonhole certificate-size obstruction. It does **not** establish universal polynomial proof size, polynomial active representation, deterministic polynomial proof search, `P=NP`, or `P!=NP`.

## 1. Motivation

C025-B-v1 uses only root axioms + Resolution. A root-applicable reason is therefore a Resolution refutation, and C025-E1 shows that explicit polynomial-size CNF families require superpolynomial/exponential such certificates.

Haken's Resolution lower-bound paper explicitly notes that Extended Resolution can furnish polynomial-length proofs for the pigeonhole formulas used in the lower bound. Extension variables therefore remove that specific obstruction and are a natural next language to test.

## 2. Frozen extension rule

Let root variables be the variables occurring in canonical root CNF `F0`.

An extension definition is

```text
EXTEND(e, a, b)
```

where:

- `e` is a fresh positive variable id not in the root and not previously defined;
- `a,b` are literals whose variables are root variables or earlier extension variables;
- `e` does not occur in `a` or `b`;
- definitions are topologically ordered.

The semantics is

```text
e <-> (a AND b)
```

with exact definitional CNF

```text
(~e OR a)
(~e OR b)
(e OR ~a OR ~b)
```

No other clause may be called an extension axiom.

For v0, extension variable ids must be strictly increasing above every root variable and every operand variable. This is stronger than logically necessary but makes freshness/dependency verification deterministic and trivial.

## 3. Portable certificate grammar

A returned reason is

```text
R_ext = (
  root_fingerprint,
  extension_definitions,
  advertised_clause C,
  final_node,
  reachable_proof_DAG
)
```

Proof nodes are:

```text
ROOT_AXIOM(source_clause_index)
EXTENSION_AXIOM(definition_index, slot in {0,1,2})
RESOLVE(left_node, right_node, pivot)
```

The verifier recomputes every extension axiom and every resolvent.

### Original-variable boundary

The advertised reusable clause `C` must contain **only root/original variables**. Internal proof clauses may contain extension variables.

This boundary is what makes cross-context reuse refer to the original SAT instance rather than to an accidental extension-variable valuation.

## 4. Conservative-extension theorem

### Lemma B2.1 — every root assignment extends through the definitions

For any truth assignment `alpha` to root variables, process extension definitions in order and set

```text
e := value_alpha(a) AND value_alpha(b).
```

Because operands mention only root or earlier extension variables, this is well-defined. The resulting extended assignment satisfies all three definitional clauses for every extension. □

### Theorem B2.2 — accepted original-variable reason is globally implied by F0

If the standalone verifier accepts `R_ext` and advertised clause `C` mentions only root variables, then

```text
F0 |= C.
```

**Proof.** Take any model `alpha` of `F0`. By Lemma B2.1 extend it to satisfy all verified definitions. Every proof axiom is then true: root axioms because `alpha |= F0`, extension axioms by construction. Resolution preserves consequence, so the final clause `C` is true in the extended assignment. Since `C` contains only original variables, its truth depends only on the original `alpha`. Hence every model of `F0` satisfies `C`. □

### Corollary B2.3 — context-independent reuse survives

If a partial assignment `rho` over root variables falsifies all literals of accepted advertised clause `C`, then `F0|rho` is UNSAT. □

## 5. Why extension-variable advertised clauses are rejected in v0

A clause containing extension variable `e` can be valid in the conservative extension without being directly evaluable from a partial assignment over only root variables. Reusing such a clause would require separately transporting/evaluating extension semantics under the context.

Rather than hide that complexity, v0 rejects it. A later language may add certified extension-expression evaluation as a separate rule.

## 6. Small proof fixture

Root CNF:

```text
(a OR c)
(b OR c)
(~a OR ~b OR d)
```

Define

```text
e <-> (a AND b).
```

Using the definition and Resolution:

1. derive `(e OR c)` from `(a OR c)`, `(b OR c)`, and `(e OR ~a OR ~b)`;
2. derive `(~e OR d)` from `(~a OR ~b OR d)`, `(~e OR a)`, and `(~e OR b)`;
3. resolve on `e` to derive original-only clause

```text
(c OR d).
```

Thus the extension participates essentially in the presented derivation while the reusable output contains no extension variable. Context `{c=0,d=0}` falsifies the certified clause and is therefore UNSAT for the root formula.

## 7. Required negative tests

Provider replay must reject:

- extension variable colliding with a root variable;
- duplicate/nonfresh extension variable;
- descending/noncanonical extension ids;
- forward dependency;
- cyclic dependency attempt;
- malformed extension-axiom slot/clause;
- advertised clause containing any extension variable;
- wrong root fingerprint;
- malformed Resolution step;
- advertised-clause/final-node mismatch;
- unreachable serialized proof garbage.

## 8. Proof-size and search firewall

The known pigeonhole obstruction for **plain Resolution** is removed as an objection to the language class because Extended Resolution has polynomial proofs for that family.

But no universal conclusion follows:

```text
PHP_HAS_SHORT_ER_PROOF != ALL_UNSAT_CNF_HAVE_POLY_ER_PROOFS
SHORT_ER_PROOF_EXISTS != POLICY0B_FINDS_IT_IN_POLYTIME
POLY_VERIFY_IN_CERT_SIZE != POLY_CERT_SIZE_IN_INPUT_N
```

The extension-definition search space can itself be enormous. Choosing useful abbreviations is part of C025-C2 proof search and must be charged.

## 9. Authority split

Canonical research/process source:

`Hawkar-usls/TOPA/research/mathematics/p-vs-np/C025_B2_EXTENSION_AWARE_REASON_V0.md`

This Fundamentum mirror is the proof-provider/replay surface. Mirroring does not create theorem authority; the derivation plus provider replay does.

## 10. Exact frontier before provider replay

```text
C025_B_PLAIN_RESOLUTION_SOUNDNESS       = PROVED_IN_SCOPE
C025_E1_PLAIN_RESOLUTION_CERT_SIZE      = REFUTED

C025_B2_EXTENSION_RULE_SEMANTICS        = FROZEN_V0
C025_B2_CONSERVATIVE_SOUNDNESS          = PROVED_ON_PAPER
C025_B2_STANDALONE_VERIFIER             = IMPLEMENTED_PENDING_PROVIDER_REPLAY
C025_B2_NEGATIVE_ADMISSION_SUITE        = IMPLEMENTED_PENDING_PROVIDER_REPLAY
C025_E2_UNIVERSAL_EXTENDED_PROOF_SIZE   = OPEN
C025_C2_EXTENSION_DEFINITION_SEARCH     = OPEN
C025_C2_GLOBAL_DETERMINISTIC_SEARCH     = OPEN
P_VS_NP                                 = OPEN
```
