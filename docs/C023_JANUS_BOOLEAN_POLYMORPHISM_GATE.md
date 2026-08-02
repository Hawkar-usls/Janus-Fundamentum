# C023 — JANUS Boolean Polymorphism Fracture Gate

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

Base:

```text
994dd693604d1f557c367acc7b1b3ed6083ee4a8
```

C023 replaces ad hoc language names with an algebraic admission gate. It verifies
which closure operation is preserved by every relation in a connected component
before any specialized solver is allowed to act.

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend,
external LLM, BCI, biological sample, physical P–N junction, or quantum device
was touched.

## Gate

For each Boolean relation `R`, the audit checks preservation under:

```text
ZERO   all-zero tuple
ONE    all-one tuple
AND    coordinate-wise conjunction
OR     coordinate-wise disjunction
MAJ    ternary majority
XOR3   ternary minority / parity
```

A connected component is admitted only if all of its relations share at least
one operation.

The dispatch is:

```text
ZERO -> all-zero witness
ONE  -> all-one witness
AND  -> Horn forward chaining
OR   -> dual-Horn forward chaining
MAJ  -> 2-SAT implication SCC
XOR3 -> GF(2) Gaussian elimination
```

If the common fingerprint is empty, the gate returns:

```text
OPEN
```

It never calls a general SAT oracle.

## Exhaustive ternary reconstruction

All `2^(2^3) = 256` ternary Boolean relations were enumerated.

```text
relations                         256
AND-preserved                     121
OR-preserved                      121
majority-preserved                165
XOR3-preserved                    51
0-valid                           128
1-valid                           128
distinct fingerprints             23
reconstruction failures           0
```

Every relation preserving:

- `AND` was reconstructed exactly as Horn CNF;
- `OR` as dual-Horn CNF;
- `MAJ` as 2-CNF;
- `XOR3` as GF(2) equations.

This is an exhaustive finite check, not sampling.

## Random exact dispatch

Random CSPs were generated from each closure class and checked against complete
truth-table enumeration.

```text
cases                             200
OPEN                              0
mismatches                        0
false accepts                     0
brute-force assignments checked   9869
dispatch targets                  {'AND': 47, 'ZERO': 7, 'OR': 46, 'ONE': 4, 'MAJ': 79, 'XOR3': 17}
```

## Component-wise heterogeneous rescue

The audit combined:

- a Horn/NAND3 component;
- a disjoint NEQ affine/bijunctive component.

Their global fingerprint is empty, but HRain-style connected-component
decomposition dispatches them independently.

```text
cases                      100
OPEN                       0
mismatches                 0
targets                    {'ZERO': 104, 'MAJ': 128}
```

Therefore:

```text
no global polymorphism
does not imply hardness
when the incompatible languages are disconnected
```

## Heterogeneous backdoor

A four-variable switch relation was automatically selected with:

```text
full relation fingerprint     EMPTY
z=0 residual                  AND / MAJ / OR / XOR3
z=1 residual                  MAJ / XOR3
minimum strong backdoor       [z]
```

Exact result:

```text
switch fingerprint              []
single minimum backdoor         [1]
z=0 fingerprint                 ['AND', 'MAJ', 'OR', 'XOR3']
z=1 fingerprint                 ['MAJ', 'XOR3']
```

Repeating `m` disconnected switch blocks requires a strong backdoor of size `m`
for this fixed target, even though every block and the full disconnected instance
are satisfiable.

This rejects backdoor size as a universal measure of intrinsic difficulty.

## Decisive fixed-language boundary

Use two relations:

```text
NAND3(a,b,c) = NOT(a AND b AND c)
NEQ(x,c)     = x XOR c = 1
```

Fingerprints:

```text
NAND3   ['AND', 'ZERO']
NEQ     ['MAJ', 'XOR3']
common  []
```

For every source variable `x`, introduce complement `c` with `NEQ(x,c)`.
For every source 3-clause:

```text
positive x   -> use c in NAND3
negative -x  -> use x in NAND3
```

This linearly and witness-preservingly expresses arbitrary 3-SAT.

Balanced exact audit:

```text
cases                       80
SAT                          40
UNSAT                        40
mapping failures             0
dispatcher OPEN              80
false accepts                0
```

The gate refuses all hard images because the connected relation language has no
common Schaefer operation.

## Meaning for the JANUS route

The failure is no longer described vaguely as:

```text
different languages do not combine
```

The exact statement is:

> Different tractable relations can be combined by one fixed polynomial
> dispatcher only while the connected language retains a common tractability
> operation. Losing all Schaefer operations is already enough to express
> arbitrary 3-SAT.

This matches the fixed-language boundary identified by Schaefer's Boolean
dichotomy and the later algebraic polymorphism view.

## What remains alive

The fixed-language route is closed. The surviving route must be genuinely
instance-specific:

```text
connected-component decomposition
small polymorphism fracture sets
bounded incidence/tree decompositions
heterogeneous strong backdoors
proof systems not reducible to one fixed constraint language
```

## Surviving conjecture

### Polynomial Instance-Specific Polymorphism Fracture Conjecture

Every CNF instance admits a polynomially discoverable proof-carrying
decomposition into regions preserving Schaefer operations, joined through a
polynomial total fracture interface that supports exact conjunction,
elimination, certification and witness recovery.

This remains open.

The fixed-language version cannot prove `P=NP`: the `NAND3 + NEQ` reduction
places arbitrary 3-SAT exactly at the empty-fingerprint boundary.

## Reproduction

```bash
python experiments/direct/janus_c023_polymorphism_gate.py --self-test
```

## References

- Thomas J. Schaefer, *The Complexity of Satisfiability Problems*,
  STOC 1978, 216–226. DOI `10.1145/800133.804350`.
- Peter Jeavons, *On the Algebraic Structure of Combinatorial Problems*,
  Theoretical Computer Science 200 (1998), 185–204.
  DOI `10.1016/S0304-3975(97)00230-2`.

## Claim boundary

This addendum does not prove `P=NP`, `P!=NP`, or a lower bound against all
algorithms. It gives an exact machine-checked admission boundary for the current
Boolean interface-language portfolio and identifies where only instance-specific
structure can still help.
