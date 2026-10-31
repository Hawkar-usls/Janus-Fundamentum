# R5 E9 — PG15 bounded-fanout NOR 3-SAT source return

Date: 2026-10-01

Status:
`JANUS_EXACT_PG15_BOUNDED_FANOUT_NOR_3SAT_RETURN__SOURCE_PRESERVING_POLY_REDUCTION__NO_D1_PROMOTION`

Parents:
- `research/R5_E9_PG15_MINIMAL_8MACRO_AFFINE_PIN_AND_NOR_RETURN_2026-10-01_v1.0.md`
- `research/R5_E9_PG15_NOR_FIXED_PORT_SOURCE_COMPOSITION_2026-10-01_v1.0.md`

Checker:
- `experiments/r5_e9_pg15_bounded_fanout_nor_3sat_source_return.py`

## 1. Purpose

The parent theorem proves an exact source-preserving PG15 implementation of Boolean

```text
NOR,
equality wires,
fanout <= 2,
NOT,
COPY,
pin0,
pin1,
```

under cubic, linear, connected Exact-One source geometry.

This note closes the remaining normalization gap: it gives an explicit polynomial reduction from nontrivial 3-CNF SAT to that bounded-fanout NOR language and then invokes the proved PG15 fixed-port composition theorem.

This is a hardness/representation return theorem.  It is not a polynomial SAT algorithm.

## 2. Input convention and trivial cases

Let `F` be a 3-CNF formula with

```text
n = number of variables that actually occur,
m = number of nonempty clauses,
L = total literal occurrences <= 3m.
```

Tautological clauses may be deleted and unused variables ignored in polynomial time.
An empty clause is an immediate UNSAT preprocessing terminal; an empty conjunction is an immediate SAT preprocessing terminal.  Hence below assume `m>=1` and every clause has size one, two, or three.

## 3. Primitive source atoms already proved

The parent PG15 composition theorem supplies the following exact source-valid atoms.

### 3.1 Free Boolean source

A PG15 gate copy with no incoming Boolean wires has local relation

```text
o = NOR(a,b).
```

Both output values occur:

```text
o=1 from (a,b)=(0,0),
o=0 from any of (0,1),(1,0),(1,1).
```

Therefore its output is a free existential Boolean signal.  Use one such gate for every input variable.

### 3.2 Constant zero source

The proved `pin0` construction pins the output of one PG15 gate to zero using one fresh helper PG15 copy.  The pin uses a third output occurrence, distinct from the two fixed output wiring ports, so both standard output ports remain available.

Thus one constant-zero signal costs two PG15 copies and one pin switch and may feed two ordinary fixed-port inputs.

### 3.3 One-port identity buffer

The parent theorem proves that a fixed-port wire is Boolean equality.  Given a signal `x`, use one pinned-zero signal `z=0` and two NOR gates:

```text
u = NOR(x,z) = NOT x,
y = NOR(u,z) = x.
```

The zero producer uses its two output ports once each, while `x` uses only one output port.  Hence this buffer consumes one available port of `x` and returns a fresh equal signal `y` with two unused output ports.

Source cost:

```text
4 PG15 copies = 2 NOR copies + 1 zero target + 1 zero helper,
5 switches    = 4 equality wires + 1 zero-pin switch.
```

This is the key fanout-normalization primitive; unlike tied-input double-NOT, it does not consume both ports of the input signal.

## 4. Linear-size fanout normalization

Suppose input variable `x_i` has `k_i>=1` literal occurrences.

If `k_i<=2`, its free generator output directly supplies the required uses.

If `k_i>2`, build a chain of exactly

```text
k_i-2
```

one-port identity buffers.  At each intermediate signal, reserve one output port for one literal occurrence and use the second output port to feed the next buffer.  The final signal has two free output ports and supplies the last two occurrences.

Thus exactly `k_i` one-port uses are produced and no signal ever has fanout greater than two.

Let

```text
B = sum_i max(k_i-2,0).
```

Then

```text
B <= L,
```

and the complete fanout normalization costs at most `4L` PG15 copies.

There is no signal-replication tree hidden in the representation: the construction emits each buffer explicitly and has linear size in the number of requested uses.

## 5. Literal normalization

Each positive literal uses its allocated signal directly.

For each negative literal `not x`, take its one-port allocated signal `x'`, a fresh pinned-zero producer `z=0`, and one NOR gate:

```text
ell = NOR(x',z) = NOT x'.
```

This consumes only one output port of `x'`.

Each negative occurrence costs

```text
3 PG15 copies = 1 NOR + zero target + zero helper,
3 switches    = 2 equality wires + zero pin.
```

Let `Nminus<=L` be the number of negative occurrences.

## 6. Clause OR with bounded fanout

For two inputs,

```text
t = NOR(a,b),
y = NOR(t,t),
```

so `y=a OR b`.  The intermediate `t` is fresh and both of its output ports are available for the tied input of the second gate.

For three inputs, compose two OR2 blocks:

```text
y = OR2(a,b),
out = OR2(y,c).
```

Thus every clause output is constructed with at most four PG15 NOR copies and no input signal is used more than once by the clause circuit.

A unit clause uses its literal signal directly.

Total clause logic costs at most

```text
4m PG15 copies.
```

## 7. Formula conjunction with one-port inputs

To avoid requiring two free ports from each clause output, implement

```text
AND(a,b) = NOR(NOR(a,0), NOR(b,0)).
```

Use one fresh pinned-zero signal `z=0` for both first-stage NOR gates; its two output ports feed one zero input each.

Each AND2 therefore consumes only one output port from each logical input and costs

```text
5 PG15 copies = 3 NOR + zero target + zero helper,
7 switches    = 6 equality wires + zero pin.
```

Combine the `m` clause outputs by any acyclic binary tree or left fold.  This uses exactly `m-1` AND2 blocks and at most `5(m-1)` PG15 copies.

## 8. Final normalization and output pin

Before pinning the formula output, pass it through one one-port identity buffer.  This guarantees a fresh equal signal with both output ports unused, including the unit-clause case.

Then apply the already-proved `pin1` construction.  It uses a tied-input inverter and one fresh helper to pin the inverter output to zero, thereby forcing the formula output to one.

Additional cost:

```text
final identity buffer = 4 PG15 copies,
pin1                 = 2 PG15 copies.
```

The resulting wiring graph is acyclic.

## 9. Exact correctness theorem

### Theorem PG15-NOR-3SAT-RETURN

For every nontrivial 3-CNF `F`, the construction above emits in polynomial time a connected linear cubic Exact-One source `J(F)` such that

```text
F is SAT  iff  J(F) is Exact-One SAT.
```

### Soundness: source model -> 3-SAT model

By the fixed-port deletion theorem, every PG15 gate copy in any source model is one of its four canonical Boolean NOR states.  Every incidence switch used as a wire therefore enforces exact equality of the connected Boolean signals.  The pin constructions enforce their stated constants.

Project the source model to the outputs of the free variable-generator copies.  The explicit NOR network then evaluates deterministically.  The final output is pinned to one, so every clause output is one.  Hence the projected variable assignment satisfies `F`.

### Completeness: 3-SAT model -> source model

Take any satisfying assignment of `F` and assign those bits to the free variable-generator outputs.  Every requested copy, literal, clause and conjunction signal is then uniquely determined by its Boolean NOR equations, while each free generator has at least one compatible pair of local input bits.

The parent theorem states that every canonical terminal triple extends to exactly one full PG15 local model and that each fixed-port switch is equivalent to the corresponding equality.  Therefore the Boolean network assignment extends gate-by-gate to a complete Exact-One model of `J(F)`, including the final output pin.

### Witness reconstruction

Given a source model of `J(F)`, read one output bit from each free variable-generator PG15 copy.  This takes `O(n)` coordinate reads and yields a satisfying assignment of `F`.  Direct evaluation verifies it in `O(L)` time.

## 10. Source geometry

Every operation used above is one of the source-valid operations already proved by the PG15 fixed-port theorem.

- occurrence 2-switches preserve row size three and column degree three;
- the fixed input/output companion sets guarantee linearity for the acyclic wiring system;
- tied-input uses occupy the two distinct input ports and are among the exhaustively checked source-valid templates;
- every pinned-zero helper is fresh, so its cross-copy pairs are unique;
- pin occurrences are distinct from the standard output wiring occurrences;
- all generated copies belong to one connected circuit component when `F` has at least one clause and unused variables are removed.

Hence `J(F)` is a connected linear cubic Exact-One source.

## 11. Polynomial size accounting

Let `B=sum_i max(k_i-2,0)` and `Nminus` be as above.  Count PG15 copies:

```text
input generators         n
fanout buffers          4B
negative literals       3Nminus
clause OR logic        <=4m
AND tree                5(m-1)
final buffer               4
final pin1                 2
```

Therefore

```text
G <= n + 4B + 3Nminus + 9m + 1
  <= n + 7L + 9m + 1
  <= n + 30m + 1.
```

The composed Exact-One source has exactly

```text
15G variables,
15G rows.
```

A direct switch accounting gives

```text
W <= 5B + 3Nminus + 15m + 1
  <= 8L + 15m + 1
  <= 39m + 1
```

occurrence switches under the stated implementation.

All construction indices have logarithmic bit size and the compiler performs `O(n+L+m)` combinatorial operations.  Thus construction, witness reconstruction and verification are polynomial in the 3-CNF encoding size.

## 12. Strategic consequence

The PG15 residual is not an affine tractable island.  After maximal direct AF3 affine compression it reconstitutes full bounded-fanout Boolean circuit logic inside the original connected linear cubic Exact-One source geometry.

Therefore the route

```text
AF3 saturation
-> bounded local affine macros
-> automatically tractable residual
```

is closed.

Any universal polynomial solver must exploit a genuinely global invariant or contraction that remains polynomial even on these composed PG15-NOR networks; otherwise it is simply re-encoding arbitrary SAT circuitry.

This theorem is a hardness return and does not by itself provide such a contraction.

## 13. Next constructive gate

Freeze

```text
R5_E9_PG15_GLOBAL_CONTRACTION_BEYOND_LOCAL_AF3_GATE_V1
```

The next admissible target is now sharply defined:

1. take the explicit PG15-NOR source family `J(F)` produced here;
2. search for a global polynomial invariant/contraction that decides it without unfolding Boolean assignments;
3. require exact witness reconstruction and polynomial bit/state accounting;
4. immediately falsify any proposed invariant on the compiled family, rather than on unrelated random sources;
5. promote to E8-D1 only if the same mechanism covers the unrestricted source carrier with soundness, completeness, termination and polynomial bounds.

## 14. Firewall

```text
PG15 NOR local semantics                   = PROVED BY PARENT
source-preserving fixed-port composition   = PROVED BY PARENT
fanout >2 normalization                    = EXPLICIT LINEAR-SIZE CONSTRUCTION
3-CNF -> bounded-fanout NOR DAG            = PROVED HERE
NOR DAG -> cubic-linear Exact-One source   = PROVED BY COMPOSITION
SAT equivalence                            = PROVED
witness reconstruction                     = EXPLICIT / POLYNOMIAL
construction size                          = O(n+m+L)

LOCAL AF3 COMPRESSION AS UNIVERSAL SOLVER  = CLOSED BY BOOLEAN HARDNESS RETURN
GLOBAL POLYNOMIAL CONTRACTION              = OPEN
UNIVERSAL POLYNOMIAL SAT SOLVER            = NOT PROVED
E8_D1                                      = EMPTY
P_VS_NP                                    = OPEN
```
