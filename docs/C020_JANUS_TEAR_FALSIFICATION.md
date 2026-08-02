# C020 pre-admission — JANUS Tear falsification campaign

## Status

`EXPLORATORY / STRONG FORM FALSIFIED / NOT IN CANONICAL REGISTRY`

C020 treats a **JANUS Tear** as a computational object:

> a compact, independently checkable invariant condensed from one or more
> residual SAT states.

The purpose of this branch is adversarial. Every precise Tear language is to be
attacked before any survivor is considered for canonical admission.

## Relation to canonical C019

Canonical C019 already contains:

- `H125`: connected high-treewidth local SAT/UNSAT twins;
- `H126`: exact-list SAT-sound cover;
- `H127`: the remaining common-quotient factorization conjecture for the stated
  fixed-pass low-treewidth compiler model.

The C020 experiments do **not** refute H127. H127 concerns one restricted
compiler category on the H125 twins. C020 instead attacks a broader and initially
over-strong claim that every formula's entire residual-state space should admit
a polynomial continuation-complete quotient.

## Base definition

For a CNF formula `F` and partial assignment `alpha`, let

```text
tau(F, alpha) = Tear signature of the residual formula F|alpha.
```

A useful Tear must state exactly what equality of signatures preserves:

- current SAT/UNSAT status;
- all future continuations;
- witness recovery;
- or only behavior under one fixed algorithmic policy.

These meanings are not interchangeable.

## Positive result — a family-specific parity Tear

For the inherited two-component Tseitin charge layouts:

```text
SAT charge distribution:    (2,0)
UNSAT charge distribution:  (1,1)
```

Every tested bounded-local charge-signature multiset is equal, while one global
component-parity bit per component gives:

```text
SAT Tear:    (0,0)
UNSAT Tear:  (1,1)
```

Reproduction:

```bash
python experiments/direct/janus_tear_tseitin_condensation.py --self-test
python experiments/direct/janus_tear_tseitin_condensation.py --radius 3
```

This is a real compression result for one algebraically exposed family. It is
not a universal SAT invariant.

## Falsification 1 — bounded locality

The C017 XOR-cycle twins and H125's connected high-treewidth descendants show
that opposite SAT labels may have exactly equal bounded-radius signed-incidence
views.

Therefore no fixed-radius Tear language is complete for SAT.

The parity Tear repairs the Tseitin family only because the correct global
algebraic invariant is already known.

## Falsification 2 — rich marginals

C020 contains an exact three-variable collision:

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

The formulas have the same:

- exact unsigned clause scopes;
- clause-width histogram;
- sign counts per clause;
- positive and negative occurrence counts for every labelled variable;
- exact primal graph and component sizes;
- recognized equality/inequality XOR-gadget inventory.

Yet the first has exactly one witness and the second has none.

```bash
python experiments/direct/janus_tear_marginal_collision.py
```

Thus this rich marginal summary language is not a sound complete Tear signature.

## Falsification 3 — all-state continuation quotient explosion

The original strong candidate asked for polynomially many Tear classes across
all residual states while preserving arbitrary future behavior.

Take the linear-size equality family

```text
E_n(X,Y) = AND_i (x_i <-> y_i).
```

For every `a` in `{0,1}^n`, assign `X=a`. The residual formula is the set of unit
clauses forcing

```text
Y=a.
```

There are exactly `2^n` residuals. They are pairwise continuation-distinguishable:
continuation `Y=a` satisfies residual `a` and rejects residual `b` for every
`b != a`.

Therefore any equivalence whose equal Tears guarantee identical acceptance for
every future continuation requires at least `2^n` classes, although `E_n` has
only `2n` clauses.

```bash
python experiments/direct/janus_tear_congruence_explosion.py --self-test
python experiments/direct/janus_tear_congruence_explosion.py --n 10
```

The `n=10` audit checks:

```text
formula clauses:                    20
residual states:                  1024
pairwise distinct residuals:      1024
ordered cross-state tests:     1047552
```

### Decisive result

The following statement is false:

> Every CNF has a polynomial-size continuation-complete quotient of all partial
> assignments.

The counterexample family is itself easy. This is not a proof that `P != NP`;
it is a formulation failure of the strong Tear conjecture.

## The Tear trilemma

### Decision-only equality

If two states may merge whenever they share only the current SAT/UNSAT label,
there are at most two classes.

But extracting that class is exactly the SAT decision problem. The desired answer
has been hidden inside the Tear extractor.

### Continuation-complete equality

If equal Tears must preserve every future assignment and full residual solution
language, the equality family forces exponentially many classes.

This form is falsified.

### Policy-selected equality

A solver may choose not to visit most residual states. Suppose one explicit
polynomial-time Tear policy always generates only polynomially many states and
returns a witness or a sound rejection.

Then that policy is already a polynomial-time SAT algorithm:

```text
explicit polynomial Tear policy
  -> SAT in P
  -> P = NP
```

Consequently failure to find a counterexample to an unspecified policy proves
nothing. The extractor and transition policy themselves must be constructed and
proved polynomial.

## Surviving candidate

### JANUS Tear Guided-Policy Candidate

There exists one explicitly defined polynomial-time Tear language and transition
policy such that, on every CNF formula of length `L`:

1. every emitted Tear has a polynomially checkable derivation;
2. only `poly(L)` Tears and policy states are generated;
3. total extraction, representation, transition, and verification work is
   `poly(L)`;
4. a satisfying assignment is returned on SAT instances;
5. a sound polynomially checkable rejection artifact is returned otherwise.

Constructing this object would solve SAT in polynomial time. It has not been
constructed or proved.

## Next attacks

1. Fix a finite Tear language rather than quantify over an unknown perfect
   invariant.
2. Automatically enumerate small CNFs and search for opposite-label collisions.
3. Add exact residual formulas to the signature and measure the resulting state
   explosion.
4. Separate extraction cost from verification cost.
5. Require witness recovery and attack hidden path-dependent side information.
6. Hide parity behind equivalent encodings and extension variables.
7. Compare every proposed Tear with ordinary clause learning and proof systems.
8. Test whether a candidate policy merely invokes SAT-equivalence or circuit
   minimization during canonicalization.

## Claim boundary

C020 currently records:

- one family-specific positive compression result;
- one exact SAT/UNSAT marginal collision;
- one exponential lower bound against all-state continuation-complete Tear
  quotienting.

No result in this branch proves `P = NP`, proves `P != NP`, or refutes H127. The
strong universal Tear quotient has been rejected; the policy-selected form
survives only as an explicit algorithmic target.
