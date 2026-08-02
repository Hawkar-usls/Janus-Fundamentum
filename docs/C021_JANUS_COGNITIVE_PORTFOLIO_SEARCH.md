# C021 pre-admission — JANUS Cognitive Portfolio Search

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT ADMITTED TO THE CANONICAL REGISTRY`

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend,
external model API, biological sample, or physical P–N junction was touched.

## Why these three projects were used

The cycle maps the three existing interfaces into one typed search process:

```text
iNaiHR -> proposes four competing structural languages
AURA   -> frames PAST / OBSTACLE / GUIDE / OUTCOME
HRain  -> stores a deduplicated proof-DAG with provenance
JANUS  -> independently verifies every witness, Tear and transformation
```

The four initial proof languages are:

```text
2-SAT
Horn
dual-Horn
canonical bounded-arity affine/XOR
```

The purpose is not voting. A language is accepted only after its recognizer,
solver, certificate and witness-recovery map pass an independent verifier.

## Positive result

The typed portfolio was compared against exhaustive truth tables on:

```text
2-SAT cases       120
Horn cases        120
dual-Horn cases   120
XOR cases         120
total mismatches  0
```

All 480 restricted-family instances were solved and independently verified.

### Heterogeneous composition

A formula was built from disjoint modules belonging to different languages. The
whole CNF belonged to none of the four recognizers, so the direct portfolio
returned `OPEN`.

After polynomial primal-component decomposition:

```text
mixed cases        160
component solved   160
mismatches         0
```

SAT witnesses from independent components were combined. An UNSAT Tear from any
component would be sufficient to reject the conjunction.

### Certified definitional unmasking

The independent modules were then connected by fresh extension variables using:

```text
z <-> (a OR b)
```

This preserves every base assignment but makes the primal graph connected. The
naive component policy returned `OPEN` on all 160 masked cases.

A recognizer removed only exact three-clause OR definitions, stored a
transformation node in the proof-DAG, solved the restored components and
reconstructed the extension-variable values.

```text
definitions detected   582
masked cases solved    160
mismatches             0
```

This is a real representation-recovery mechanism, but only for one certified
extension pattern.

## HRain proof-DAG result

The same Horn formula was sent through the complete portfolio 100 times.

```text
logical runs      100
unique DAG nodes  5
```

Exact repeated claims, attempts and outcomes collapse by content hash. This
prevents repeated work and preserves provenance.

It does not merge genuinely continuation-distinct states.

## Main obstruction

The same portfolio was applied to generic random 3-CNF:

```text
cases          240
verified solve 0
OPEN           240
false accepts  0
```

The result is sound but incomplete.

A bounded exact search then tested 232 candidate variable subsets up to size 3.
No heterogeneous portfolio backdoor was found for the seeded 11-variable
instance.

The subset search itself is combinatorial and therefore cannot be promoted into
the missing polynomial Observer.

## What was learned

```text
PASS  four proof languages on their certified families
PASS  heterogeneous disjoint composition
PASS  exact OR-definition unmasking and witness recovery
PASS  HRain-style proof-DAG deduplication
PASS  zero false accepts on generic 3-CNF
OPEN  all generic 3-CNF instances
FAIL  no universal polynomial selector obtained
```

The three interfaces therefore improve the **research architecture**, not the
known worst-case complexity of SAT.

## Surviving conjecture

### Representation-Robust Proof-Carrying Selector Conjecture

For every CNF of length `L`, one deterministic process must, in total
`poly(L)` work:

1. propose only polynomially many representations;
2. certify safe transformations;
3. discover semantic modules;
4. select or synthesize a tractable proof language;
5. emit a SAT witness or UNSAT Tear;
6. verify the result;
7. recover the original-variable witness.

Constructing such a selector would itself construct a polynomial-time SAT
algorithm and prove `P = NP`.

## Next attack

The next cycle should expand definitional unmasking beyond `OR` to a certified
library of `AND`, `XOR`, equivalence and bounded circuits, then build adversarial
formulas whose easy modules are hidden behind compositions of those definitions.

The crucial measurement is not recognition accuracy. It is:

```text
candidate count
+ transformation proof volume
+ decomposition work
+ solver work
+ certificate volume
+ witness recovery
```

All must remain polynomial on every formula.
