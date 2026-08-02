# C028 — JANUS Mixed-Cone Tractability Invariants

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

Base:

```text
f0ffb9b7afdd1797c4c6648b32f5ee5c5a80a9f0
```

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend,
external LLM, BCI, biological sample, physical P–N junction, or quantum device
was touched.

## Question

C027 isolated:

```text
TRACTABLE_PROJECTION_DISCOVERY
```

A compact mixed circuit is not enough, because arbitrary 3-SAT has a linear
AND/OR circuit.

C028 tests which circuit invariants actually imply tractability.

## Positive invariant: decomposability

An NNF circuit is decomposable when the children of every AND gate have pairwise
disjoint variable supports.

Then:

```text
literal       -> immediate witness
OR            -> choose one satisfiable child
AND           -> combine child witnesses
```

The AND combination is sound precisely because the child assignments cannot
conflict.

### Exact random audit

```text
circuits                            240
mismatches                          0
witness failures                    0
record-verifier failures            0
nondeterministic but tractable       129
truth assignments checked            844
```

This demonstrates that determinism is not required for SAT decision once AND
decomposability holds.

## Negative result: determinism is insufficient

Every exact 3-clause

```text
l1 OR l2 OR l3
```

is rewritten as:

```text
l1
OR (NOT l1 AND l2)
OR (NOT l1 AND NOT l2 AND l3)
```

The branches are mutually exclusive, so every OR gate is deterministic.

Conjoining these rewritten clauses gives a linear-size expression tree for the
original 3-CNF.

Properties:

```text
all OR gates deterministic
gate-only graph is a tree
maximum AND/OR type alternations = 2
```

Yet arbitrary 3-SAT is preserved because repeated variable labels occur in
different conjunctive clause regions.

### Balanced exact audit

```text
formulas                            120
SAT                                  60
UNSAT                                60
source/circuit mismatches            0
determinism failures                 0
topology failures                    0
false tractable admissions           0
```

Therefore none of the following is a universal tractability condition:

```text
deterministic OR gates
tree-shaped gate graph
constant gate-type alternation
```

## Semantic support overlap

Define the overlap set `D` as every variable appearing in two children of some
AND gate.

After assigning all variables in `D`, every remaining AND gate has disjoint
child supports.

Therefore every residual circuit is decomposable.

## Decomposability-Defect Criterion

For defect:

```text
d = |D|
```

exact SAT with witness recovery costs:

```text
O(2^d * |C|)
```

The implementation charges every defect assignment, simplification,
decomposability check, recursive record and final witness check.

### Small exact controls

```text
cases                              160
OPEN                               0
mismatches                         0
witness failures                   0
maximum defect                     8
branches examined                  3705
```

### Large small-defect circuits

Largest positive fixture:

```text
variables                          1128
blocks                             280
nodes                              3641
defect                             8
required branches                  256
branches examined                  256
status                             EXACT
SAT                                True
```

The circuit has more than one thousand variables, but only eight variables
connect conjunctive regions.

The exact solver therefore needs 256 overlap assignments rather than
`2^1128` total assignments.

### UNSAT control

```text
variables                          586
blocks                             145
defect branches                    64
status                             EXACT
SAT                                False
```

All 64 assignments to the six overlap variables were certified UNSAT.

## Minimal obstruction

```text
x AND NOT x
```

has:

```text
deterministic OR condition          True
decomposable                        False
overlap defect                      1
direct decomposable solver          OPEN
defect solver                       EXACT
result SAT                          False
```

This is the smallest example showing why independently satisfiable AND children
cannot be combined when they share a variable.

## Large defect is not a hardness certificate

Large positive monotone CNFs were tested.

They have overlap defect equal to the number of variables and an immediate
all-true witness.

```text
all controls easy                   True
some defect runs return OPEN        True
```

Thus defect is an exact parameter for this solver, not a classifier of intrinsic
difficulty.

## Located bottleneck

# SEMANTIC_SUPPORT_OVERLAP

The relevant interaction is not gate topology.

It is:

> repeated variable identity across conjunctive regions after local OR, XOR,
> Horn and other tractable cones have been summarized.

Duplicating literal leaves keeps the gate graph a tree while preserving the full
source CNF interaction through shared variable labels.

## Relation to knowledge compilation

DNNF uses decomposability to support tractable reasoning over compiled circuits.

C028 follows the knowledge-compilation distinction between:

```text
compact representation
and
queries supported in polynomial time
```

The result is also a backdoor-style parameterization: assigning the overlap set
moves the circuit into a tractable decomposable class.

## Next target

### C029 — Support-Overlap Width

Global branching on every overlap variable is deliberately crude.

The next cycle should replace `2^d` enumeration with dynamic programming over
the actual support-overlap or variable-clause incidence graph.

Required components:

- exact separator decomposition;
- proof-carrying boundary functions;
- width and total-message budgets;
- witness/Tear recovery;
- explicit rejection of poor decompositions;
- comparison with the deterministic 3-CNF embedding.

The next parameter is not the total number of repeated variables, but the maximum
number simultaneously crossing one valid decomposition boundary.

## Repository CI profile

The repository uses a compact dependency-free audit:

```text
experiments/direct/janus_mixed_cone_invariants_ci.py
```

Its frozen result is:

```text
status:                         PASS
nondeterministic tractable:     65
embedding SAT / UNSAT:          40 / 40
embedding equivalence failures: 0
defect mismatches:              0
largest CI fixture variables:   728
largest CI defect:              8
largest CI branches:            256
```

The downloadable package also contains the extended primary and holdout audits.

## Holdout

```text
seed:   280031
status: PASS
```

All primary assertions passed again.

## Claim boundary

C028 does not prove `P=NP`, `P!=NP`, or a lower bound against all algorithms.

It proves two structural lemmas in an explicit NNF model, implements exact
proof-carrying finite audits, and identifies semantic support overlap as the next
target.

## Reproduction

```bash
python experiments/direct/janus_mixed_cone_invariants_ci.py
```
