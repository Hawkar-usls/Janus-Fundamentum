# C020 addendum — Policy-0A masked Tseitin attack

## Status

`EXPLORATORY / CONCRETE POLICY FALSIFIED AT A FIXED ENVELOPE`

This addendum replaces an unspecified ideal Tear policy with one executable
machine.

## Policy-0A

At the root:

1. group clauses by exact variable scope;
2. reconstruct the represented relation on each complete scope;
3. if every clause belongs to an affine relation, extract the exact `GF(2)`
   equations and run Gaussian elimination.

At every residual state:

1. exhaust unit propagation;
2. attempt at most `4 * literal_count` deterministic resolution pairs;
3. add at most `max(8, clause_count / 4)` non-tautological resolvents;
4. allow derived width at most current maximum width plus one;
5. branch on the most frequent variable, breaking ties by the smallest index;
6. try `false` before `true`;
7. memoize the exact canonical residual CNF.

Every per-state operation has an explicit polynomial budget. The experiment
charges the number of distinct residual states separately.

## Visible contradiction

Take the odd-charge Tseitin system on `K4`. It has:

```text
edge variables:      6
clauses:             16
maximum width:        3
```

The root affine extractor reconstructs four parity equations and Gaussian
elimination rejects the formula without branching:

```text
affine equations:     4
residual states:      0
answer:           UNSAT
```

## Local nonlinear mask

Replace each edge bit by three fresh bits through the bijection

```text
x = b XOR (a AND c).
```

The inverse is

```text
a = a
b = x XOR (a AND c)
c = c.
```

Thus satisfiability and the odd global charge are preserved. On a cubic graph,
each original degree-three parity relation becomes one fixed relation on nine
bits. Its exact CNF has 256 clauses, so the transformation has constant overhead
per vertex and remains linear in graph size.

The transformed relation is not affine, so Policy-0A's root Tear extractor emits
no equations.

## Exact `K4` result

For the masked `K4` instance:

```text
variables:                 18
clauses:                 1024
maximum width:              9
affine equations:           0
residual states:         3842
resolution attempts:  1114956
resolution additions:   61559
answer:                 UNSAT
```

The semantic contradiction that required zero branching in its visible encoding
now requires 3,842 distinct residual states under this exact policy.

This is a representation-dependence result for Policy-0A. It is not an
asymptotic lower bound.

## Quadratic-envelope failure on `K3,3`

The next cubic graph has six vertices and nine edges. Its masked formula has:

```text
variables:        27
clauses:        1536
maximum width:     9
```

Fix the explicit state promise

```text
B(v) = 4 v^2.
```

For `v=27`, the budget is `2916` states. Policy-0A reaches state `2917` without
returning SAT or UNSAT, so this concrete quadratic-envelope version is falsified.

This finite failure does not exclude a larger polynomial envelope. Establishing
superpolynomial growth requires an asymptotic family theorem, not merely larger
benchmarks.

## Reproduction

```bash
python experiments/direct/janus_tear_policy0a_masked_tseitin.py --self-test
python experiments/direct/janus_tear_policy0a_masked_tseitin.py --case visible-k4
python experiments/direct/janus_tear_policy0a_masked_tseitin.py --case masked-k4
python experiments/direct/janus_tear_policy0a_masked_tseitin.py --case masked-k33
```

## Decisive scope

The experiment rejects the statement:

> visible affine extraction, polynomially budgeted local resolution, unit
> propagation, deterministic branching, and exact residual memoization always
> fit within the stated quadratic state envelope.

It does **not** reject:

- arbitrary semantic normalization;
- unrestricted proof systems;
- a different branching policy;
- a larger polynomial state bound;
- all possible JANUS Tear policies;
- `P = NP` or `P != NP`.

## Next gate

The next non-cosmetic step is asymptotic. Select an explicit bounded-degree
expander family and prove, for the fully specified policy rather than generic
DPLL, that nonlinear masking preserves a superpolynomial lower bound on at least
one charged resource:

```text
residual states
resolution work
representation normalization
or witness-recovery information.
```

Without that theorem, Policy-0A is only one destroyed machine, not a complexity
separation.
