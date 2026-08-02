# C022 pre-admission — JANUS Definitional Circuit Unmasking

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

This cycle extends C021 from one `OR` definition to an exact functional gate
library:

```text
OR
AND
XOR
EQUIV / XNOR
```

No swarm, ESP32, NAS, Telegram backend, external model or physical system was
used.

## Question

Can easy heterogeneous SAT modules be hidden behind deep Tseitin-like extension
circuits so that the Cognitive Portfolio loses them?

## Construction

Each mixed formula contains modules solved by different proof languages:

```text
2-SAT
Horn
dual-Horn
affine/XOR
```

Fresh variables are then introduced as exact gates:

```text
z <-> gate(a,b)
```

The gates connect all modules into one primal component. Clause order and literal
order are shuffled.

## Result

```text
cases                         180
gate definitions per case     24
naive component OPEN          180
certified unmasking solved    180
mismatches                    0
definitions recovered         4322
```

Gate coverage:

```text
OR       1040
AND      1100
XOR      1094
EQUIV    1088
```

The Observer removes only a root definition whose output variable occurs nowhere
outside its exact gate clauses. It repeats root-first until the base modules are
exposed, solves them through C021, then reconstructs outputs dependency-first.

## Scaling fixture

A chain of 256 definitions was recovered:

```text
definitions       256
recognizer rounds 257
gate comparisons  1689
```

This does not prove an asymptotic theorem, but the implemented recognizer performs
a directly charged polynomial pattern search for the bounded gate library.

## Safety attacks

### Output used by a real constraint

A unit clause was added on the final extension output. The Observer refused to
strip the circuit:

```text
definitions stripped  0
solver status         OPEN
```

This prevents the unsound move of deleting a definition whose value matters to
the original problem.

### Non-functional connector

A one-way relation was added instead of an equivalence. It was not recognized:

```text
definitions stripped  0
```

## Meaning for the P versus NP route

Explicit acyclic definitional masking is **not itself** the missing barrier for
the tested portfolio. When the extension circuit is exact, fresh and functional,
the Observer can expose the underlying proof languages and reconstruct the
original witness.

The remaining obstruction moved to harder cases:

```text
overlapping definitions
shared outputs used by core constraints
cyclic extension systems
implicit semantic definitions
symbolic substitution instead of safe deletion
general equivalence/equisatisfiability discovery
```

Those cases may require reasoning as hard as the original SAT instance.

## Verdict

```text
PASS explicit deep OR/AND/XOR/EQUIV unmasking
PASS witness recovery
PASS safe refusal on constrained outputs
PASS rejection of non-functional relations
OPEN overlapping/cyclic/implicit semantic structure
NO P=NP proof
```
