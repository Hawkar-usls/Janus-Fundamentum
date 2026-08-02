# C037 — Certified Polynomial Ping-Pong

**Status:** `CONSTRUCTIVE_RESTRICTED_LEMMA + DECISIVE OBSTRUCTION / P_VS_NP=OPEN`

## Purpose

C036 completed proof-carrying merge and separation inside Horn and affine message languages. C037 begins the cross-language bridge without introducing a general mixed Horn-affine solver.

The cycle admits only two operations:

1. a complete directed test from an affine relation to a Horn relation;
2. a sound but incomplete fixpoint exchange of entailed shared literals.

A fixpoint without conflict is always `OPEN`. It is never interpreted as compatibility or equivalence.

## Lemma 1 — complete affine-to-Horn directed inclusion

Let `A` be an affine `GF(2)` system and `H` a Horn CNF over the same boundary variables. For every Horn clause `C`, falsifying all literals of `C` adds only unit equations to `A`.

Therefore `A AND NOT C` is still affine and deterministic Gaussian elimination returns exactly one of:

- SAT: a complete assignment satisfying `A` and falsifying `C`, hence an explicit cross-language separator in `MODELS(A) - MODELS(H)`;
- UNSAT: a Gauss-Jordan provenance certificate proving `A |= C`.

Testing every clause of `H` decides

```text
MODELS(A) subseteq MODELS(H)
```

in polynomial time and attaches replayable evidence to every result.

This theorem is directional. The reverse test requires deciding whether a Horn model can violate an affine row. C037 does not assume that operation.

## Lemma 2 — certified unary shared-consequence fixpoint

For a Horn module `H`, affine module `A`, shared variable set `S`, and current interface facts `U`, C037 repeatedly asks each native engine whether an unassigned `x in S` is forced.

A literal `x=b` is admitted only when the native engine refutes the opposite assumption `x=1-b`:

```text
H AND U AND (x=1-b) -> Horn conflict trace
A AND U AND (x=1-b) -> GF(2) provenance for 0=1
```

The admitted literal is then injected into both modules. Since each accepted event fixes one previously unassigned shared variable, at most `|S|` events are emitted. Every native call, Horn clause scan, Gaussian row XOR, event, certificate byte, and total work unit is charged.

Possible terminals are:

```text
CONFLICT       one native module refutes the accumulated facts
OPEN_FIXPOINT  no new shared literal is derivable
OPEN_BUDGET    an explicit polynomial work budget is exceeded
OPEN_LANGUAGE  an unsupported message language is supplied
```

Only `CONFLICT` is a semantic conclusion. `OPEN_FIXPOINT` states only that unary propagation stopped.

## Negotiation Trace v1

The machine-readable certificate has this logical shape:

```json
{
  "schema": "janus.cross_language_negotiation.v1",
  "policy": "UNARY_SHARED_CONSEQUENCE_FIXPOINT_V1",
  "modules": [
    {"language": "HORN", "digest": "..."},
    {"language": "AFFINE_GF2", "digest": "..."}
  ],
  "shared_vars": [1, 2, 3],
  "initial_facts": [{"var": 1, "value": true}],
  "events": [
    {
      "seq": 0,
      "kind": "ENTAILED_LITERAL",
      "producer": "HORN",
      "var": 2,
      "value": true,
      "fact_id": "content-addressed-id",
      "native_proof": {
        "status": "UNSAT",
        "trace": [{"op": "set", "var": 1, "clause": 0}]
      }
    }
  ],
  "terminal": {
    "status": "CONFLICT",
    "module": "AFFINE_GF2",
    "native_proof": {"status": "UNSAT", "provenance": 13}
  },
  "cost": {
    "work_units": 41,
    "horn_calls": 5,
    "affine_calls": 4,
    "horn_clause_scans": 22,
    "row_xors": 10,
    "step_count": 1,
    "certificate_bytes": 917
  },
  "integrity": {"sha256": "..."}
}
```

The verifier does not trust the embedded native proof blindly. It replays the opposite-assumption query in the producer language, reconstructs the accumulated fact set, and checks the terminal conflict independently.

## SQLite cache layout

Canonical JSON is the interchange format, not the primary database layout. The executable normalizes storage into:

```text
negotiation_certificate
negotiation_step
proof_blob
```

The cache key is

```text
SHA256(
  schema_version || policy_id ||
  ordered module digests || ordered shared scope || initial facts
)
```

Memory controls:

- module bodies are referenced by digest and are not copied into every step;
- native proofs are content-addressed and inserted with `INSERT OR IGNORE`;
- steps store only opcode, producer, variable, value and proof digest;
- no full RREF snapshot is stored per step;
- no full Horn closure is stored per step;
- repeated insertion of the same certificate is idempotent;
- separator assignments may be bit-packed in a separate chunk table when used by the production database.

For `k=|S|`, the literal event stream contains at most `k` accepted facts. Certificate volume is still charged explicitly because native proof traces may dominate the event count.

## Decisive obstruction — constants-only exchange is incomplete

Take the Horn equality relation

```text
H = (not x or y) AND (x or not y)
```

and the affine disequality

```text
A = x XOR y = 1.
```

Neither module fixes `x` or `y`, so unary ping-pong immediately reaches a fixpoint. Yet `H AND A` is UNSAT.

Thus:

```text
OPEN_FIXPOINT != compatible
```

and a universal C037 cannot be obtained by exchanging constants alone.

The same unary bridge correctly remains `OPEN` on a `{NAND3,NEQ}` reduction image with no initial forced literals. This prevents the mechanism from silently becoming a general SAT oracle.

## Frozen audit

```bash
python experiments/direct/janus_c037_certified_polynomial_ping_pong.py --self-test
```

The deterministic audit checks:

```text
400 random Horn/affine directed-inclusion cases
400 random unary ping-pong cases
all accepted directed certificates replayed
all accepted conflicts checked against exhaustive mixed semantics on small domains
307 certified random conflicts
93 honest OPEN fixpoints
Horn equality + affine disequality -> OPEN on a jointly UNSAT instance
NAND3 + NEQ image -> OPEN
a unit-exposed Tseitin/parity mixture -> certified conflict
SQLite certificate insertion -> idempotent
```

Finite counts are validation only.

## Relation to the active route

- C025 separated quotient size from merge-proof size.
- C032 identified explicit cut signatures with PS-width.
- C034 proved bounded-interface heterogeneous composition.
- C035 gave proof-carrying same-message merging.
- C036 gave complete same-language separator extraction.
- C037 gives the first complete cross-language direction and the first replayable negotiation trace, while proving that unary negotiation is not complete.

This is an alignment with cooperating decision procedures, propagation explanations, and DPLL(XOR)-style native reasoning. It is not named as a new width invariant.

## Remaining gate

```text
REVERSE_HORN_TO_AFFINE_SEPARATOR_OR_STRONGER_FACT_ALGEBRA
```

A next bridge must either:

1. construct a polynomial procedure that finds a Horn model violating an affine row or certifies that every Horn model satisfies it; or
2. enlarge the exchanged fact algebra with polynomial discovery, polynomial representation, native replay, and an explicit proof that the enlarged closure avoids the `{NAND3,NEQ}` NP-hardness image.

Supplied decompositions, fixed unsupported arity, nonuniform exponents, and failure to derive a fact do not satisfy this gate.

## Claim boundary

C037 proves a complete one-way Horn-affine separator theorem and a sound polynomial unary conflict protocol. It does not decide unrestricted Horn-affine conjunctions, certify compatibility at fixpoint, bound universal quotient size, solve arbitrary CNF, or prove `P=NP`.

```text
P_VS_NP=OPEN
```
