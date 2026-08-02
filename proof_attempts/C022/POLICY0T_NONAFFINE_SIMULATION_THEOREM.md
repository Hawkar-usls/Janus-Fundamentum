# C022 proof attempt — non-affine Policy-0T simulation theorem

## Status

`COMPLETE INTERNAL PROOF DRAFT / INDEPENDENT REVIEW REQUIRED`

## Exact scope

This theorem concerns only the no-cache Policy-0T search core after the root
dispatcher has returned

```text
affine_answer = None.
```

The full dispatcher is excluded. H130 was destroyed because its affine/Gaussian
shortcut cannot be polynomially simulated by ordinary Resolution on visible
expander-Tseitin formulas.

## Theorem candidate

Let `F` be an unsatisfiable CNF on `N` variables. Consider any complete
provenance trace produced by the exact non-affine Policy-0T core consisting of:

1. exhaustive unit propagation;
2. one deterministic local Resolution pass whose new clauses are not re-indexed
   during the same pass;
3. a second exhaustive unit-propagation phase;
4. deterministic single-variable branching;
5. no residual memoization.

Let

```text
m = number of root clauses,
r = number of recorded local Resolution events,
u = number of propagated-unit assignments,
b = number of branch nodes,
o = number of opposite-unit conflict events.
```

Then the trace can be mechanically transformed into an ordinary Resolution
refutation satisfying

```text
proof size  <= m + r + u + b + o,
proof depth <= 2N + 2.
```

Consequently, if charged work `W` includes these five quantities, proof size is
`O(W)` and proof depth is `O(N)`.

## Root-provenance invariant

For a current assignment `alpha`, every residual clause `C` stored by the
translator has a proof-line witness `D` such that:

```text
D is derived from the root CNF by Resolution,
D restricted by alpha equals C.
```

The translator never treats restriction as a proof rule. `C` is used only to
replay the execution; `D` is the actual proof line.

The invariant holds initially because each root clause witnesses its own
restriction under the empty assignment.

## Lemma 1 — restriction commutes with a recorded local resolution

Suppose residual clauses `C_1` and `C_2` are witnessed by root-derived clauses
`D_1` and `D_2`, and the recorded local event resolves them on unassigned
variable `x`.

Because both `D_1|alpha` and `D_2|alpha` survive restriction, neither root clause
contains a literal satisfied by `alpha`. Every assigned literal still present in
`D_1` or `D_2` is false under `alpha`.

A complementary pair on an assigned variable cannot occur across `D_1,D_2`:
one of the two literals would be true and would satisfy its parent clause.
Any complementary pair on an unassigned variable other than `x` would remain in
the residual resolvent, which the Policy-0T local pass rejects as tautological.

Therefore the root resolvent

```text
D = resolve(D_1, D_2, x)
```

is non-tautological and obeys

```text
D|alpha = resolve(C_1, C_2, x).
```

One recorded local event costs exactly one proof line. Since the local pass uses
only clauses indexed at the beginning of that pass, all local event lines add at
most one dependency layer at a search node.

## Lemma 2 — reverse unit-reason elimination

Assume unit propagation assigns literal `l` at assignment state `beta`. Its
recorded reason has a root-derived witness clause `R` satisfying

```text
R|beta = (l).
```

Hence every literal of `R` other than `l` is false under `beta`:

```text
R subseteq B(beta) union {l},
```

where `B(beta)` is the clause of literals falsified by `beta`.

Let a later conflict clause `C` be falsified by the assignment after `l` and any
subsequent propagated units. Process propagated units in reverse chronological
order. If `-l` is absent from `C`, no step is needed. If `-l` is present,
resolve `C` with `R` on `var(l)`. The resulting clause is falsified by the state
before `l` was assigned, while later units have already been removed.

After reversing all units created inside the node, the returned conflict clause
contains only literals falsified by the node-entry assignment.

Each propagated unit contributes at most one Resolution line and one dependency
layer.

## Lemma 3 — terminal cases

Every UNSAT terminal of the exact core is covered.

### Opposite units

Resolve the two unit-reason clauses on their common variable, obtaining a clause
falsified by the current assignment. Then apply Lemma 2 to earlier units.

### Empty clause during unit restriction

The root witness of the residual clause that becomes empty is already falsified
by the current assignment. Apply Lemma 2.

### Empty local resolvent

Lemma 1 provides a root-derived witness whose restriction is empty. Apply Lemma
2.

### Post-resolution unit conflict

Identical to the first two cases, using both pre- and post-resolution unit
reasons in reverse order.

### Immediate branch conflict

This case is unreachable. Exhaustive unit propagation leaves no unit clauses, so
every clause before branching has width at least two. One branch assignment
removes at most one false literal from a surviving clause and cannot make it
empty.

## Lemma 4 — branch combination without weakening

For an UNSAT node entered with assignment `alpha`, define

```text
B(alpha) = the clause of literals falsified by alpha.
```

Inductively, the false child at branch variable `x` returns a derived clause

```text
C_0 subseteq B(alpha) union {x},
```

and the true child returns

```text
C_1 subseteq B(alpha) union {-x}.
```

There are only three cases:

1. if `x in C_0` and `-x in C_1`, resolve on `x`;
2. if `x` is absent from `C_0`, return `C_0` directly;
3. if `-x` is absent from `C_1`, return `C_1` directly.

The returned clause is always a derived subclause of `B(alpha)`. No weakening is
used. A branch node costs at most one proof line and one dependency layer.

## Structural induction

Induct on the finite no-cache execution tree.

- Terminal nodes return a root-derived subclause of their entry decision
  boundary by Lemmas 2 and 3.
- Internal nodes translate both UNSAT children and return a parent-boundary
  subclause by Lemma 4, then reverse units created locally by Lemma 2.

At the root the entry assignment is empty, hence `B(empty)` is the empty clause.
The only subclause is the empty clause itself, so the construction is a
Resolution refutation.

## Size bound

The emitted proof contains:

- exactly `m` root axioms;
- one line for each of the `r` local Resolution events;
- at most one reverse-reason line for each of the `u` propagated units;
- at most one branch-combination line for each of the `b` branch nodes;
- one line for each of the `o` opposite-unit conflicts.

Thus

```text
S <= m + r + u + b + o.
```

Duplicate residual clauses do not increase this upper bound beyond recorded
local events. Choosing one legal root witness per canonical residual preserves
all execution parents required by the one-pass local rule.

## Depth bound

Follow any dependency path from a root axiom to the final empty clause.

- Each search node contributes at most one local-Resolution layer.
- Each propagated unit on the corresponding root-to-leaf execution path
  contributes at most one reverse-reason layer.
- Each branch on that path contributes at most one branch-combination layer.
- A terminal opposite-unit conflict contributes at most one additional layer.

Every branch or propagated unit fixes a previously unassigned variable, so along
one execution path

```text
branches + propagated units <= N.
```

The number of visited search nodes on that path is at most `branches + 1`.
Therefore

```text
D <= (branches + 1) + propagated_units + branches + 1
  <= 2N + 2.
```

## Executable witnesses

```bash
python experiments/direct/janus_tear_policy0t_recursive_trace_translator.py
python experiments/direct/janus_tear_policy0t_recursive_translator_fuzz.py
python experiments/direct/janus_tear_policy0t_proof_bound_audit.py
```

The executables are finite validations of the construction and numerical bounds;
they do not replace independent review of the universal induction above.

## Claim boundary

This theorem is about one exact provenance-complete, no-cache, non-affine search
core. It does not simulate the affine dispatcher, formula caching, arbitrary
clause learning, arbitrary SAT solvers, or unrestricted polynomial-time
algorithms. Its combination with a lifting theorem can lower-bound this policy,
not prove `P != NP`.
