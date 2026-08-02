# C020 addendum — the formula-caching barrier

## Status

`DECISIVE ATTACK / NAIVE POLICY0A-TO-RESOLUTION SIMULATION BLOCKED`

The first Policy-0A lifting plan assumed that exact residual memoization was only
DAG sharing and that a run of charged work `W` could therefore be converted to a
Resolution or `Res(⊕)` proof of size `O(W)`.

That assumption is not currently justified.

## Primary reference

P. Beame, R. Impagliazzo, T. Pitassi, and N. Segerlind,
*Formula Caching in DPLL*, ACM Transactions on Computation Theory 1(3), 2010,
Article 9, DOI `10.1145/1714450.1714452`.

The paper studies exactly the operation at issue: remember unsatisfiable residual
formulas and, before a recursive call, check whether the current residual formula
is already in the cache.

Its basic system is called `FC`. The authors show that `FC` is p-equivalent to a
formula-level caching calculus `CC`, not to ordinary DAG Resolution. They stress
that the initial intuition

```text
DPLL tree + memoization = DAG Resolution
```

is wrong: several natural caching systems have different proof-complexity power,
and some strengthened but implementable variants are exponentially more powerful
than Resolution.

The paper also leaves open whether even the basic `FC`, `FCW`, or `FCWS`
systems are p-simulated by Resolution or regular Resolution.

## Relation to Policy-0A

Policy-0A performs:

```text
exact canonical residual-CNF lookup
+ cached UNSAT answer reuse
```

This contains the defining basic-`FC` operation. It additionally performs local
Resolution additions before branching and caches residuals containing those
added clauses.

Therefore Policy-0A is not automatically weaker than ordinary Resolution, and a
proof of

```text
Policy-0A work W
  -> Resolution proof size O(W)
```

cannot be inferred merely from exact hashing or DAG reuse.

The finite work audit reinforces the distinction. On the current fixtures:

```text
triangular masked K4:
  unique residual states: 3842
  recursive calls:        7077
  memo hits:              2111

MAJ3-lifted K4:
  unique residual states: 2427
  recursive calls:        4117
  memo hits:               888
```

Even this finite accounting shows that incoming cache contexts are a separate
resource from unique residual nodes.

## Consequence for the MAJ3 lifting route

The 2026 width-to-depth lifting theorem applies to `Res(⊕)` proofs. It cannot be
applied directly to a formula-caching computation unless we first prove one of:

1. Policy-0A is efficiently simulated by `Res(⊕)` with the required depth bound;
2. the lifting theorem extends to the exact caching calculus representing
   Policy-0A;
3. Policy-0A is restricted so that cache reuse becomes syntactic proof-DAG reuse.

None of these statements is currently proved.

Thus the earlier conditional implication remains blocked at the simulation edge:

```text
Policy-0A polynomial work
-X-> shallow polynomial-size Res(⊕) proof
```

The crossed arrow is the missing theorem, not an innocent implementation detail.

## Clean split

### Policy-0T — tree policy

Remove exact residual memoization. Count every recursive occurrence. The remaining
mechanism is DPLL search plus explicit Resolution additions and unit propagation.
The standard DPLL-to-Resolution translation can plausibly support the MAJ3
lifting route, because no formula-level cache rule must be simulated.

### Policy-0A — caching policy

Retain exact residual memoization. Its natural proof object is a formula-caching
calculus, not automatically Resolution. It needs a direct lower bound or a new
lifting theorem for caching proofs.

## Decisive result

The statement

> exact residual memoization merely converts the Policy-0A search tree into an
> ordinary Resolution DAG with constant overhead

is rejected as unsupported and contrary to the known formula-caching framework.

This does not show that Policy-0A escapes the MAJ3 family. It shows that the
proposed proof route did not yet charge or model the cache's proof-theoretic
power.

## Next gates

1. Implement `Policy-0T` with no memoization and certify its execution-to-proof
   translation.
2. Express Policy-0A as an explicit `FC`/`CC`-style proof object and determine
   exactly which caching rules its local learned clauses require.
3. Search for lower bounds for that exact caching calculus, rather than importing
   Resolution lower bounds through an unproved simulation.
4. Keep recursive calls, branch edges, memo hits, unique cache entries, and local
   proof work as separate charged resources.
