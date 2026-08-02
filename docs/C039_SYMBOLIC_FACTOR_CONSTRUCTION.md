# C039 — Symbolic Factor Construction

```text
STATUS = SPECIFICATION_IMPLEMENTED / DRAFT / CI_PENDING
P_VS_NP = OPEN
```

## Purpose

C039 specifies a proof-carrying construction of vtree cut factors without
enumerating Boolean communication rows. It receives a supplied, verified vtree
from C038. Polynomial vtree discovery is explicitly outside this cycle and is
reserved for C040.

The first commit is a contract only. It does not implement Horn projection,
affine composition, beta-acyclic elimination, or a general SAT solver.

## Branch lineage

```text
base: research/c038-structured-vtree-factor-alignment
head: research/c039-symbolic-factor-construction
```

C036.2 is an external service behind `OpenCoreVaultSink`; C039 does not import
or depend on `c0362_*` tables.

## Operators

| Operator | Contract |
|---|---|
| `LEAF` | Bind local formula material to a vtree leaf and require a replayable native proof. |
| `JOIN` | Combine two child messages only after scope, boundary, vtree and language checks. |
| `PROJECT` | Eliminate internal variables symbolically; assignment enumeration is forbidden. |
| `MERGE` | Merge two states only with replayable continuation-equivalence evidence. |
| `SEPARATE` | Distinguish states with a replayable symbolic continuation or native separator. |

Every operation commits to formula, vtree, vtree node, capability, language,
input messages, scopes, boundaries, payload, proof references, work and size.

```text
operation_digest =
SHA256("JANUS-C039-OP-V1\0" || canonical_json(certificate_without_digest))
```

Semantic digests contain no timestamp, hostname, PID, random nonce or machine
path.

## Registered symbolic payloads

C039.0 recognizes only these names for structural validation:

```text
HORN_CLOSURE
AFFINE_RREF
BETA_ACYCLIC_ELIMINATION
COMPOSED_C036_1_MESSAGE
SYMBOLIC_CONTINUATION
SYMBOLIC_STATE_PAIR
```

Recognition is not an implementation claim. Native algorithms enter only in
C039.1, C039.2 and C039.5.

These payload classes are always forbidden:

```text
RAW_BITMAP
EVALUATION_VECTOR
ROW_MATRIX
TRUTH_TABLE_BLOB
ASSIGNMENT_INDEX
ARBITRARY_LOOKUP_TABLE
```

Unknown payload classes and enumerative fields such as `assignments`,
`communication_rows`, `truth_table`, `raw_bitmap` or `lookup_table` produce
`INVALID_CERTIFICATE`.

## Terminals

```text
FACTOR_BUILT
MERGED_CERTIFIED
SEPARATED_CERTIFIED
CLOSED_POLY
OPEN_LANGUAGE
OPEN_BUDGET
OPEN_EQUIVALENCE
OPEN_REPRESENTATION_GROWTH
OPEN_COMPOSITION
INVALID_CERTIFICATE
```

`OPEN_REPRESENTATION_GROWTH` means only that the representation exceeded an
explicit budget under this vtree and capability. It is not a lower bound on the
formula and is not evidence for `P != NP`.

## Vault boundary

```python
class OpenCoreVaultSink(Protocol):
    async def current_capability_digest(self) -> bytes: ...
    async def record_open(self, core_digest, capability_digest, open_trace) -> None: ...
    async def record_poly(self, core_digest, capability_digest, certificate_digest) -> None: ...
```

`CLOSED_POLY` routes only to `record_poly`. `OPEN_*` routes only to
`record_open`. A current-capability mismatch blocks the write. C039.0 uses only
an in-memory adapter.

## Fixtures

The Horn chain, affine projection, beta-acyclic join tree, negative merge,
symbolic separator and growth-control fixtures validate schema binding,
deterministic digests, operator preconditions, terminal discipline and proof
reference closure. They do not establish completeness or implement the named
languages.

## Frozen acceptance gate

```bash
python experiments/direct/janus_c039_symbolic_factor_contract.py --self-test
```

The ten checks cover digest determinism, version invalidation, proof-required
LEAF, JOIN scope compatibility, encoded truth-table rejection, certified MERGE,
replayable SEPARATE, budgeted OPEN without a partial factor, and capability-locked
Vault routing.

## Non-negotiable invariants

```text
NO_EXPLICIT_COMMUNICATION_ROWS
NO_HIDDEN_TRUTH_TABLE
NO_ASSIGNMENT_ENUMERATION_AS_PROJECTION
NO_UNVERIFIED_MERGE
NO_SUPPLIED_VTREE_PROMOTED_TO_DISCOVERY
NO_GENERAL_SAT_FALLBACK
NO_OPEN_PROMOTED_TO_HARDNESS
```

Algorithms polynomial only in an already exponential payload must be described
as output-sensitive, never as an input-polynomial SAT algorithm.

## Staged implementation

```text
C039.0 contract and replay envelope
C039.1 Horn LEAF/JOIN/PROJECT
C039.2 affine LEAF/JOIN/PROJECT
C039.3 certified MERGE/SEPARATE
C039.4 C036.1 cross-language composition
C039.5 beta-acyclic symbolic elimination
C039.6 real Vault adapter activation
```

## Active gate

```text
POLYNOMIAL_SYMBOLIC_JOIN_PROJECT_MERGE
+
REPLAYABLE_FACTOR_EQUIVALENCE
```

The route-wide gate remains:

```text
POLYNOMIAL_VTREE_DISCOVERY
+
POLYNOMIAL_SYMBOLIC_FACTOR_CONSTRUCTION
```
