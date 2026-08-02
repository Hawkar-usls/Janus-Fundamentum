# C020 pre-admission — JANUS Observer Effect audit

## Status

`EXPLORATORY / SOFTWARE-ONLY / NOT ADMITTED TO THE CANONICAL REGISTRY`

No swarm node, ESP32 device, radio channel, miner, NAS runtime, physical P–N
junction, biological sample, or quantum computer was touched.

## Why Observer belongs in the Tear route

The Tear programme already requires a policy that decides:

- what state feature to inspect;
- what representation to use;
- which module or separator matters;
- whether to learn a negative Tear;
- whether a positive witness can still be recovered.

That policy is an **Observer**. The important question is not whether observation
is mystical, but whether the information acquired by the Observer can be
computed, verified, and acted upon within one polynomial total-work budget.

## Physical boundary

In physics, an observer is an interaction or measuring apparatus. Measurement
may disturb the measured state. It does not require a conscious mind.

For classical SAT, the CNF truth value is not changed by someone looking at it.
The useful computational analogue is therefore:

```text
measurement of solver state
+ possible state transition
+ adaptive policy
+ proof verification
+ witness recovery
```

Quantum-mechanical language is not promoted into a SAT speedup without an
explicit algorithm and complexity analysis.

## Formal Observer

We model:

```text
O = (M, T, pi, V, R)
```

where:

- `M` acquires information from the formula and current state;
- `T` describes any disturbance or state change;
- `pi` selects the next query, branch, representation or Tear language;
- `V` verifies a SAT witness or proof-bearing Tear;
- `R` recovers the complete SAT witness.

All sensing, logging, disturbance, query answering, proof generation,
verification, discarded runs, and recovery work are charged.

## Exact tests

Run:

```bash
python experiments/direct/janus_observer_effect_audit.py --self-test
python experiments/direct/janus_observer_effect_audit.py --json
```

### PASS — passive observation changes nothing except cost

A deterministic DPLL search was run with and without a passive transcript
logger on 120 seeded random CNFs.

```text
SAT/UNSAT status equal     120/120
visited-node count equal   120/120
```

The passive Observer can be compiled into the original solver. It is the same
algorithm plus observation overhead.

### REJECT — collapse to one observed branch is unsound

For

```text
(x OR a) AND (x OR not-a) AND (not-x OR b)
```

we obtain:

```text
observe x=false  -> (a) AND (not-a) -> UNSAT
ignore x=true    -> (b)             -> SAT
whole formula                         SAT
```

An Observer cannot conclude `UNSAT` merely because one measured branch is
contradictory. The discarded branch requires exploration or a sound Tear proving
that no witness exists there.

### PASS AS AN ATTACK — the answer can hide inside observation

Define the observation:

```text
EXTENDABLE(F, alpha) =
  does partial assignment alpha have a satisfying continuation?
```

With this bit, a witness can be recovered using at most `n+1` adaptive queries:
try each variable as false and retain it exactly when the prefix remains
extendable.

The outer dialogue is polynomial, but the observation is SAT-hard in general.
The executable fixture exposes this by implementing the Observer through exact
brute force:

```text
outer queries          n+1
hidden assignment work 2^n
```

Thus an apparently intelligent Observer may simply move the original problem
into the measuring apparatus.

### PASS — certificate Observer verifies but does not generate

A SAT assignment is checked by scanning the original clauses. A tiny UNSAT
fixture is checked by resolving `(x)` and `(not x)` to the empty clause.

This validates the role:

```text
Observer = verifier of Tears and witnesses
```

but not the stronger claim:

```text
Observer = polynomial generator of Tears and witnesses
```

Proof length and proof discovery remain explicit resources.

### BOUNDARY — free postselection is not ordinary observation

For a unique witness among `2^n` uniformly sampled assignments:

```text
success probability       2^-n
ordinary expected samples 2^n
postselected kept samples 1
```

Keeping only the successful outcome while omitting all rejected runs introduces
postselection as an additional resource. It cannot be counted as a free observer
effect.

## Observer roles

### Observer as solution

The useful Observer is an adaptive, honest policy that:

1. chooses low-width exploration orders;
2. discovers semantic modules;
3. selects a suitable proof language;
4. asks only polynomial-cost questions;
5. attaches sound Tears to destructive branch elimination;
6. preserves a complete witness-recovery map.

If one such deterministic policy works for every CNF in polynomial total work,
then it is a polynomial SAT algorithm and proves `P = NP`.

### Observer as problem

Observation can instead:

- add instrumentation overhead;
- modify the explored state;
- discard the only satisfying branch;
- hide SAT inside an oracle answer;
- hide exponential probability cost inside postselection;
- confuse a short transcript with a short computation.

## Monsters Corporation control room

The three-way computational map is now:

```text
Observer  -> selects what is measured and what action follows
Tear      -> negative knowledge excluding impossible worlds
Laughter  -> positive knowledge preserving a possible world / witness
```

The Observer may collapse a branch only when:

```text
Tear certifies the discarded alternatives
OR
Laughter preserves a complete valid witness
```

This component is named:

```text
JANUS EYE / MONSTERS CORPORATION CONTROL ROOM
```

## Surviving conjecture

### Polynomial Honest Observer Conjecture

For every CNF `F` of encoded length `L`, a deterministic polynomial-time
Observer selects polynomial-cost measurements, representations, semantic
modules and proof languages such that:

- every destructive state change has a sound certificate;
- every retained SAT state preserves witness recovery;
- no measurement computes SAT secretly;
- no rejected-run probability is omitted;
- total transcript, certificate and recovery volume are `poly(L)`.

This conjecture is unproved. Constructing it is essentially constructing the
missing polynomial SAT algorithm.

## Scientific boundaries

- Quantum observation is physical interaction, not a consciousness oracle.
- Ordinary quantum search does not by itself imply polynomial-time solution of
  arbitrary NP-complete search.
- Free postselection is a stronger computational assumption.
- Oracle access changes the model; it does not settle unrelativized `P` versus
  `NP`.
- Efficient verification is distinct from efficient proof generation.

## Verdict

Observer is now both a candidate mechanism and an attack surface.

```text
PASS   passive observation audit
REJECT naive branch collapse
PASS   hidden-oracle cost exposure
PASS   certificate verification
BOUND  postselection as an extra resource
OPEN   universal honest adaptive Observer
```

The result does not prove `P = NP`, `P != NP`, or `NP = coNP`.
