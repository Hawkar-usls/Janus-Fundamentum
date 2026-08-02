# C019 pre-admission — JANUS Tear condensation under attack

## Status

`WEAKENED / STRONG FORM FALSIFIED / NOT ADMITTED TO CANONICAL REGISTRY`

A **JANUS Tear** is treated only as a computational object:

> a compact, independently checkable invariant condensed from one or more
> residual SAT states.

The purpose of C019 is not to protect this image. It is to attack every precise
version until either a surviving theorem remains or the idea is rejected.

## Base definition

For a CNF formula `F` and a partial assignment `alpha`, let

```text
tau(F, alpha) = TEAR signature of the residual formula F|alpha.
```

A useful tear must be sound, polynomially extractable, polynomially verifiable,
and strong enough to merge search states without changing the answer or losing
witness recovery.

A learned clause, an UNSAT core, a parity invariant, a cut, or an extension
variable can all be viewed as restricted tear types. Merely renaming those
objects does not produce a complexity result.

## Exact positive result: family-specific parity tear

For the two-component Tseitin twins used by the current laboratory:

```text
SAT charge distribution:    (2,0)
UNSAT charge distribution:  (1,1)
```

Every tested bounded-local charge-signature multiset is equal, but the global
component-parity tear is:

```text
SAT:    (0,0)
UNSAT:  (1,1)
```

Reproduction:

```bash
python experiments/direct/janus_tear_condensation.py --self-test
python experiments/direct/janus_tear_condensation.py --radius 3
```

This is a real compression result for one algebraically exposed family. It is
not a general SAT algorithm.

## Attack 1 — bounded locality fails

The C017 XOR-cycle twins and their later high-treewidth descendants show that
for every fixed observation radius, opposite SAT labels can have exactly equal
multisets of rooted signed-incidence neighborhoods.

Therefore no fixed-radius tear language is complete for SAT.

A global parity tear repairs this family only because the correct invariant is
already visible in the representation.

## Attack 2 — rich marginals still collide

C019 contains an exact three-variable collision:

```text
SAT:
  (x1)
  (x2)
  (x1 OR NOT x2)
  (NOT x1 OR NOT x3)

UNSAT:
  (x1)
  (x2)
  (NOT x1 OR NOT x2)
  (x1 OR NOT x3)
```

The pair has the same:

- exact unsigned clause scopes;
- clause-width histogram;
- sign counts per clause;
- positive and negative occurrence counts for every labelled variable;
- exact primal graph and component sizes;
- recognized equality/inequality XOR-gadget inventory.

Yet the first formula has one witness and the second has none.

```bash
python experiments/direct/janus_tear_marginal_collision.py
```

Thus unsigned global structure plus rich signed marginals is not a sound
complete tear signature.

## Attack 3 — the strong polynomial quotient is false

The original candidate claimed that all residual states of every formula could
be partitioned into only polynomially many witness-preserving tear classes.

Take the linear-size equality family

```text
E_n(X,Y) = AND_i (x_i <-> y_i).
```

For every bit string `a` in `{0,1}^n`, assign `X=a`. The residual formula is

```text
Y=a,
```

represented by `n` unit clauses. There are exactly `2^n` such residuals.

They are pairwise continuation-distinguishable: continuation `Y=a` satisfies
residual `a` and rejects every residual `b != a`.

Therefore any tear equivalence whose equality guarantees identical behavior
under every future continuation requires at least

```text
2^n
```

classes, although the original formula has only `2n` binary clauses.

Reproduction:

```bash
python experiments/direct/janus_tear_congruence_explosion.py --self-test
python experiments/direct/janus_tear_congruence_explosion.py --n 10
```

The `n=10` audit checks 1,024 distinct residuals and 1,047,552 ordered
cross-residual continuations.

### Decisive conclusion

The statement

> every CNF has a polynomial-size continuation-complete quotient of all partial
> assignments

is false, even for a formula family already solvable in linear time.

This does **not** imply `P != NP`. It rejects an over-strong formulation of the
Tear conjecture.

## The Tear trilemma

### 1. Decision-only equivalence

If two residuals may merge whenever they merely share the current SAT/UNSAT
label, there are only two classes.

But computing the class is exactly the SAT decision problem. The tear extractor
has hidden the desired answer inside itself.

### 2. Continuation-complete equivalence

If equal tears must preserve every possible future assignment and witness
behavior, the equality family above forces exponentially many classes.

This strong form has been falsified.

### 3. Policy-selected equivalence

A solver may avoid most residual states and visit only a polynomially chosen
subset. If a polynomial-time tear policy always does this and returns a witness
or a sound UNSAT result, then it is already a polynomial-time SAT algorithm.

Consequently the surviving statement is not yet a proof route; it is an
equivalent algorithmic target:

```text
explicit polynomial Tear policy
  -> SAT in P
  -> P = NP
```

Failure to find a counterexample to an unspecified policy is not evidence of
this implication's premise.

## Surviving research target

### JANUS Tear Guided-Policy Candidate

There exists one explicitly defined, polynomial-time computable tear language
and transition policy such that, on every CNF formula of length `L`:

1. every emitted tear has a polynomially checkable derivation;
2. the algorithm generates only `poly(L)` tears and policy states;
3. the total representation and verification work is `poly(L)`;
4. the policy returns a satisfying assignment when one exists;
5. otherwise it returns a sound polynomially checkable rejection artifact.

This candidate has not been proved or refuted. As stated, constructing it would
amount to constructing a polynomial-time SAT algorithm.

## Next falsification gates

1. Define a finite candidate tear language rather than quantifying over an
   unknown perfect invariant.
2. Search automatically for opposite-label collisions at increasing formula
   size.
3. Test whether stronger tears merely encode exact residual formulas and cause
   exponential state growth.
4. Separate extraction cost from verification cost.
5. Require every compression claim to include witness recovery.
6. Attack representation dependence by hiding parity behind equivalent CNF
   encodings and extension variables.
7. Compare against ordinary clause learning so that renamed CDCL behavior is not
   counted as a new theorem.

## Claim boundary

C019 has produced one positive family-specific compression result and two exact
falsifications:

- bounded or marginal summary languages can merge SAT with UNSAT;
- continuation-complete quotienting of all residual states can require
  exponentially many classes on a linear-size easy formula.

No JANUS Tear result currently proves `P = NP` or `P != NP`. The surviving work
is to specify an actual polynomial policy and then attempt to destroy it.
