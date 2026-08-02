# C021 — JANUS Overlap / Interface / Feedback Barrier

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT CANONICAL`

C021 starts from the current canonical `main` after C020 was admitted in schema
`2.9.0`. The previous divergent research branch is not used as its base.

No swarm node, ESP32 device, radio channel, miner, NAS runtime, Telegram backend,
BCI, external LLM, biological sample, physical P–N junction, or quantum computer
was touched.

## Architecture used

```text
iNaiHR -> proposes HORN / DUAL_HORN / AFFINE_SCC / FEEDBACK_CIRCUIT views
AURA   -> PAST / OBSTACLE / GUIDE / OUTCOME
HRain  -> content-addressed interface-state and proof DAG
JANUS  -> independently verifies witnesses, Tears and reductions
```

The experiment does not use language voting. A result is accepted only when the
corresponding witness or contradiction certificate verifies.

## Positive result — bounded semantic interfaces

Let a Horn module and a dual-Horn module share `k` variables. C021 enumerates the
shared assignment and invokes the two polynomial solvers on each residual:

```text
O(2^k poly(L))
```

This is polynomial when `k = O(log L)`.

Seeded test:

```text
cases                       160
mismatches                  0
false accepts               0
maximum interface width     6
maximum states examined     64
```

Every accepted SAT result contains a complete assignment checked against the
original conjunction. An exhausted interface produces an explicit finite Tear.

## Overlap obstruction

Every exact 3-clause is Horn or dual-Horn:

```text
0 or 1 positive literals -> Horn
2 or 3 positive literals -> dual-Horn
```

Therefore every 3-CNF can be partitioned clause by clause into two individually
tractable subformulas. This does not solve 3-SAT because the two subformulas may
share essentially all variables.

Generic seeded test:

```text
random 3-CNF cases              100
unclassified clauses             0
exact join mismatches             0
average interface width        9.36
maximum interface width          11
maximum theoretical states     2048
```

A constructed 18-variable fixture has a Horn half, a dual-Horn half, and all 18
variables in the shared interface:

```text
interface states = 2^18 = 262144
```

This does not prove that every possible algorithm must enumerate those states.
It proves that clause-wise tractable-language coverage is insufficient: that
coverage already contains arbitrary 3-SAT.

## Positive result — affine cyclic SCCs

Cycles are not uniformly hard. For the GF(2) cycle

```text
x_i XOR x_(i+1) = b_i
```

Gaussian elimination returns either a complete assignment or a provenance set
whose XOR is the contradiction `0 = 1`.

```text
cases                           240
SAT                             115
UNSAT                           125
status mismatches                 0
witness failures                  0
conflict-certificate failures     0
```

Thus a cyclic SCC should be dispatched to a certified algebraic solver when its
language is visible.

## Nonlinear constrained-feedback obstruction

For an arbitrary source 3-CNF `F`, C021 constructs exact clause OR gates, an AND
tree with output `o`, and the feedback SCC:

```text
p <-> (o AND q)
q <-> p
p = 1
```

The resulting cyclic CNF is satisfiable exactly when `F` is satisfiable. The
encoding has linear size.

The independent balanced companion uses 70 guaranteed SAT and 70 guaranteed
UNSAT source formulas:

```text
cases                            140
SAT                               70
UNSAT                             70
structure failures                 0
witness failures                   0
assignment-equivalence failures    0
```

Therefore a polynomial solver for unrestricted constrained nonlinear feedback
networks would already be a polynomial solver for arbitrary 3-SAT.

The cycle itself is not the sole source of hardness. The real constraint on the
circuit output carries the original SAT question into the feedback SCC.

## Symbolic substitution barrier

Shared expressions must stay in a DAG. At depth 32 the test has:

```text
DAG nodes                    33
expanded tree leaves         4294967296
```

Textual substitution is rejected as a canonical mechanism. HRain must preserve
shared nodes. DAG preservation removes a representation blow-up but does not
solve Circuit-SAT.

## Cycles are constraints, not automatically definitions

Exact truth tables give:

```text
z1 <-> z2, z2 <-> z1          two solutions
z1 <-> NOT z2, z2 <-> NOT z1  two solutions
z <-> NOT z                    no solutions
```

A cyclic SCC may be underdetermined, multi-solution, or inconsistent. It cannot
be eliminated as though every output were a fresh uniquely determined variable.

## What C021 removes

- Clause-wise language assignment as a universal SAT answer.
- The claim that every cycle is intrinsically hard.
- The need for textual expression expansion.
- The idea that the number of modules alone controls complexity.

## What survives

- Typed polynomial solvers for recognized modules and SCCs.
- HRain proof-DAG sharing.
- Exact `O(2^k poly(L))` module composition.
- A polynomial route when every semantic interface is `O(log L)`.
- Proof-carrying SAT witness recovery and UNSAT Tears.

## Surviving conjecture

### Polynomial Semantic Interface Selector Conjecture

For every CNF `F` of encoded length `L`, one deterministic polynomial-time
Observer constructs a proof-carrying network of tractable modules and cyclic SCC
solvers such that all of the following are polynomial in `L`:

- representation and language selection;
- module and SCC discovery;
- total semantic-interface state volume;
- proof and cache volume;
- verification;
- SAT witness recovery.

The conjecture remains open. A general solution of the constrained-feedback
class tested here would already solve 3-SAT.

## Reproduction

```bash
python experiments/direct/janus_overlap_feedback_barrier.py --self-test
python experiments/direct/janus_overlap_feedback_unsat_balance.py --self-test
```

## Verdict

C021 narrows the missing theorem from:

```text
choose the right proof language
```

to:

```text
compose proof languages while universally controlling semantic-interface width
```

The mathematical status of `P` versus `NP` is unchanged. The target is now more
precise: discover a universally polynomial interface representation, or a sound
mechanism that handles large overlaps without enumerating an exponential state
space.
