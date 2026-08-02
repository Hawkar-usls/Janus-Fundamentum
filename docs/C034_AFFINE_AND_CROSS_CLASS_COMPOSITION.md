# C034 — Proof-Carrying Affine Engine and Cross-Class Composition

**Status:** `CONSTRUCTIVE RESTRICTED ALGORITHM + DECISIVE COMPOSITION BARRIER / P_VS_NP=OPEN`

## Purpose

C033 established an exact ordered portfolio for normalized Horn, dual-Horn and beta-acyclic CNF. C034 adds a fourth symbolic language, `GF(2)`, and then tests the first real cross-class composition theorem.

The result has two positive parts and one decisive negative part:

```text
explicit affine systems       -> exact polynomial solver and verifier
logarithmic shared interface  -> exact proof-carrying composition
unrestricted Horn + affine    -> already contains arbitrary 3-SAT
```

## 1. Affine/GF(2) proof-carrying engine

An affine module is an explicit system

```text
A x = b over GF(2).
```

The implementation performs deterministic Gauss-Jordan elimination. Every row carries a provenance bitset over the input equations and every operation is recorded as either:

```text
swap(i,j)
xor(target,pivot)
```

### SAT output

For a consistent system the solver returns a complete assignment. The verifier replays every operation, recomputes every final row from its provenance, and checks the assignment against all original equations.

### UNSAT output

For an inconsistent system the solver returns a provenance set whose XOR is exactly:

```text
0 = 1.
```

The verifier independently recomputes this linear combination. Corrupt provenance is rejected.

This separates certificate existence, construction and replay: all three are explicit and polynomial.

## 2. Bounded-interface composition theorem

Consider modules from the admitted portfolio:

```text
Horn
Dual-Horn
beta-acyclic CNF
explicit affine GF(2)
```

Let `B` be the set of variables occurring in at least two modules and let `k=|B|`.

Enumerate all assignments to `B`. After substitution, solve every module with its exact engine.

- If one boundary assignment makes every module satisfiable, combine the boundary assignment and local witnesses.
- If every boundary assignment is blocked, record one exact local UNSAT certificate for each assignment.
- If a residual module is outside the admitted classes, return `OPEN`.

The total work and certificate volume are:

```text
O(2^k * poly(L)).
```

Therefore the composition is polynomial whenever:

```text
k = O(log L).
```

This is a proof-carrying extension of the bounded semantic-interface principle already isolated in C021, now instantiated with the C033 portfolio and an independently replayable affine engine.

## 3. Decisive unrestricted-composition obstruction

Merely combining polynomial solvers for named classes cannot be the universal algorithm.

For every source 3-CNF introduce, for each variable `x_i`, a complement variable `c_i` and the affine equation:

```text
x_i XOR c_i = 1.
```

Define the falsity indicator of a source literal by:

```text
false(x_i)      = c_i
false(NOT x_i)  = x_i.
```

Replace every source clause

```text
l1 OR l2 OR l3
```

by the Horn NAND3 clause

```text
NOT false(l1) OR NOT false(l2) OR NOT false(l3).
```

The transformation is linear and witness-preserving. The output contains only:

```text
Horn NAND3 clauses
+ affine NEQ equations.
```

Hence arbitrary 3-SAT is already present inside unrestricted Horn-affine composition. This is the C023 fixed-language obstruction restated at the exact C034 module interface.

Consequences:

1. A polynomial engine for arbitrary composition of these modules would itself be a proof that `P=NP`.
2. A selector that only recognizes each local module has not solved the cross-class interaction.
3. The missing object is an instance-specific proof-carrying quotient of the shared interface, not another named tractable class.

## Frozen audit

```bash
python experiments/direct/janus_c034_affine_portfolio_composition.py --self-test
```

Expected result:

```text
700 affine systems
0 truth-table mismatches
0 affine certificate failures

300 bounded heterogeneous networks
0 decision mismatches
0 composition certificate failures
0 unexpected OPEN

120 balanced 3-SAT -> Horn+affine reductions
60 SAT + 60 UNSAT
0 mapping failures
bounded-interface composer: OPEN on every hard-image case

corrupt affine UNSAT provenance: REJECTED
```

## Comparison with prior cycles

- C021 already proved the algorithmic value of logarithmic semantic interfaces.
- C023 proved that `{NAND3,NEQ}` has no common Schaefer tractability operation and linearly expresses 3-SAT.
- C025 isolated semantic quotient and merge-proof complexity.
- C032 identified explicit cut-signature tables with PS-width.
- C033 supplied exact Horn, dual-Horn and beta-acyclic engines.
- C034 unifies those observations in one executable cross-class interface and adds replayable GF(2) certificates.

No new width parameter is introduced.

## Located gate

```text
PROOF_CARRYING_CROSS_CLASS_INTERFACE_COMPRESSION
```

Equivalently, the active constructive problem is:

> For every CNF, discover in polynomial time an exact polynomial-size semantic quotient of the interactions between tractable symbolic regions, together with polynomial construction, composition, equality/merge proofs, SAT witness recovery and independently replayable UNSAT evidence.

This is the same nonlinear core seen from C025, C032 and C034. Renaming it does not advance the proof; constructing it does.

## Next cycle

C035 must attack instance-specific interface quotients rather than add another tractable class.

The first candidate is a certified congruence-refinement procedure over boundary assignments. It may merge two boundary states only when a polynomially replayable proof shows that every admitted continuation gives the same SAT response and witness-transfer behavior.

Required attacks:

```text
NAND3 + NEQ reduction image
Tseitin and parity mixtures
order-sensitive equality families
beta-acyclic regions joined by cyclic interfaces
duplicate-clause families with tiny PS quotient
```

The procedure must return `OPEN` when the quotient or its proof exceeds a polynomial budget.

## Claim boundary

C034 adds a genuine polynomial affine solver, independent affine certificates and an exact bounded-interface composition theorem. It also proves that unrestricted Horn-affine composition is already NP-hard.

It does not construct the universal interface quotient and does not prove `P=NP`.

```text
P_VS_NP=OPEN
```
