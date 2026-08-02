# C037 — Certified Polynomial Ping-Pong

**Status:** `CONSTRUCTIVE_RESTRICTED_LEMMA + DECISIVE OBSTRUCTION / P_VS_NP=OPEN`

## Numbering

```text
C036   proof-carrying same-language partition refinement
C036.1 explicit residual / OBDD alignment
C037   Horn-affine negotiation
C037.1 proof-carrying pairwise parity-alias extension
C038   structured vtree decomposition
```

The branch, executable, schema and file paths already use the canonical `c037` identifier.

## Purpose

C036 completed proof-carrying merge and separation inside Horn and affine message languages. C037 begins the cross-language bridge without introducing a general mixed Horn-affine solver.

The cycle admits only:

1. a complete directed test from an affine relation to a Horn relation;
2. a sound but incomplete fixpoint exchange of entailed shared literals.

A fixpoint without conflict is always `OPEN`. It is never interpreted as compatibility or equivalence.

## Lemma 1 — complete affine-to-Horn directed inclusion

Let `A` be an affine `GF(2)` system and `H` a Horn CNF. For every Horn clause `C`, falsifying all literals of `C` adds only unit equations to `A`. Gaussian elimination on

```text
A AND NOT C
```

returns either:

- SAT: an explicit assignment in `MODELS(A) - MODELS(H)`;
- UNSAT: Gauss-Jordan provenance proving `A |= C`.

Testing every clause decides

```text
MODELS(AFFINE) subseteq MODELS(HORN)
```

in polynomial time with replayable evidence. The reverse direction remains `OPEN`.

## Lemma 2 — certified unary shared-consequence fixpoint

For Horn module `H`, affine module `A`, shared variable set `S`, and current facts `U`, a literal `x=b` is published only after the producer refutes the opposite assumption:

```text
H AND U AND (x=1-b) -> Horn conflict trace
A AND U AND (x=1-b) -> GF(2) provenance for 0=1
```

The admitted literal is injected into both modules. Each event fixes one previously unassigned shared variable, so at most `|S|` events are accepted. Native calls, clause scans, row XORs, event count, proof bytes, certificate bytes and total work are charged.

Terminals:

```text
CONFLICT
SEPARATOR
DIRECTED_INCLUSION
OPEN_FIXPOINT
OPEN_BUDGET
OPEN_LANGUAGE
```

Only the first three are semantic conclusions. `OPEN_FIXPOINT` states only that unary propagation stopped.

## Negotiation Trace v1

```text
janus.cross_language_negotiation.v1
```

Each event records the producer, shared fact, opposite assumption and native proof. The independent verifier reconstructs accumulated facts, replays every opposite-assumption query in the producer language and checks the terminal result.

SQLite storage is normalized into content-addressed certificate, event and proof-blob tables. Module bodies, Horn closures and full RREF snapshots are not copied into every event. Reinsertion is idempotent.

## Decisive obstruction — constants are incomplete

```text
H = (not x or y) AND (x or not y)   # x = y
A = x XOR y = 1                     # x != y
```

Neither side fixes `x` or `y`, so unary ping-pong reaches `OPEN_FIXPOINT`, while `H AND A` is UNSAT. Therefore:

```text
OPEN_FIXPOINT != compatible
```

The same bridge remains `OPEN` on a `{NAND3,NEQ}` reduction image with no initial forced literal.

## Frozen audit

```bash
python experiments/direct/janus_c037_certified_polynomial_ping_pong.py --self-test
python experiments/direct/janus_c037_adversarial_matrix.py
```

The deterministic audit includes 400 directed inclusion checks, 400 unary negotiation checks, replayed conflicts, equality/NEQ and NAND3/NEQ controls, a unit-exposed parity conflict and idempotent SQLite insertion. Finite counts validate the implementation only.

## Remaining gate

```text
REVERSE_HORN_TO_AFFINE_SEPARATOR_OR_STRONGER_FACT_ALGEBRA
```

C037.1 attacks the second branch by extracting proof-carrying pairwise parity aliases from arbitrary Horn formulas over shared variables. It must remain incomplete and return `OPEN` when no certified literal or pairwise alias closes the interaction.

## Claim boundary

C037 proves a complete affine-to-Horn direction and a sound polynomial unary conflict protocol. It does not decide unrestricted Horn-affine conjunctions, certify compatibility at fixpoint, solve arbitrary CNF, or prove `P=NP`.

```text
P_VS_NP=OPEN
```
