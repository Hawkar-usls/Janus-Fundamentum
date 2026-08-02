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
compiler category on the H125 twins. C020 instead attacks broader and initially
over-strong Tear formulations and then fixes concrete policies for finite
falsification.

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
```

This is a real compression result for one algebraically exposed family. It is
not a universal SAT invariant.

## Falsified mechanisms

C020 now contains executable attacks against:

1. bounded-local Tear languages;
2. rich structural marginal signatures;
3. structural marginals augmented with exhaustive unit propagation;
4. continuation-complete polynomial quotienting of all residual states;
5. fixed bounded-width resolution Tears;
6. visible affine/XOR extraction under nonlinear bijective re-encoding.

The detailed finite witnesses and commands are recorded in:

- `docs/C020_TEAR_POLICY_ATTACKS.md`;
- `docs/C020_NONLINEAR_AFFINE_MASKING.md`;
- `docs/C020_POLICY0A_MASKED_TSEITIN.md`.

## Strong-form terminal result

Take

```text
E_n(X,Y) = AND_i (x_i <-> y_i).
```

For every `a` in `{0,1}^n`, assigning `X=a` produces the residual `Y=a`.
These `2^n` residuals are pairwise continuation-distinguishable. Therefore the
following statement is false:

> Every CNF has a polynomial-size continuation-complete quotient of all partial
> assignments.

This formulation failure is not a proof that `P != NP`.

## Concrete Policy-0A result

Policy-0A fixes:

- visible affine root extraction;
- unit propagation;
- polynomially budgeted local resolution;
- deterministic most-frequent-variable branching;
- false-first value order;
- exact residual memoization.

On the visible odd-charge `K4` Tseitin contradiction, four affine equations reject
the formula with zero residual states.

After replacing every edge bit by

```text
x = b XOR (a AND c),
```

the masked `K4` formula remains UNSAT but Policy-0A visits exactly 3,842 residual
states. On masked `K3,3`, the explicit envelope

```text
B(v) = 4 v^2
```

is exceeded at state 2,917 for `v=27` without an answer.

This rejects one exact policy/envelope. It is not an asymptotic lower bound and
does not exclude a larger polynomial.

```bash
python experiments/direct/janus_tear_policy0a_masked_tseitin.py --self-test
```

## The Tear trilemma

### Decision-only equality

If two states may merge whenever they share only the current SAT/UNSAT label,
there are at most two classes. But extracting the class is exactly SAT.

### Continuation-complete equality

If equal Tears must preserve every future assignment, the equality family forces
exponentially many classes. This form is falsified.

### Policy-selected equality

An explicit polynomial-time policy that always visits only polynomially many
states and returns a witness or sound rejection is already a polynomial-time SAT
algorithm.

Failure to find a counterexample to an unspecified policy proves nothing. The
extractor and transition rule must be constructed and their total cost proved.

## Surviving candidate

### JANUS Tear Guided-Policy Candidate

There exists one explicitly defined polynomial-time Tear language and transition
policy such that, on every CNF formula of length `L`:

1. every emitted Tear has a polynomially checkable derivation;
2. only `poly(L)` Tears and policy states are generated;
3. total extraction, representation, transition, verification, and recovery work
   is `poly(L)`;
4. a satisfying assignment is returned on SAT instances;
5. a sound polynomially checkable rejection artifact is returned otherwise.

Constructing this object would solve SAT in polynomial time. It has not been
constructed or proved.

## Next gate

The next meaningful step is asymptotic rather than cosmetic:

1. select one explicit bounded-degree expander family;
2. apply the fixed nonlinear edge mask with constant overhead;
3. analyze the fully specified Policy-0A transition system;
4. prove or destroy a superpolynomial lower bound on residual states, resolution
   work, representation normalization, or witness-recovery information.

## Claim boundary

C020 records exact finite counterexamples and one terminal formulation failure.
No result in this branch proves `P = NP`, proves `P != NP`, or refutes H127.
