# C020 proof attempt — Policy-0T tree lifting lower bound

## Status

`FORMALIZING / CACHE BARRIER REMOVED / PROOF-EMITTING CERTIFICATE PENDING`

## Policy

`Policy-0T` is Policy-0A with exact residual memoization deleted. It retains:

1. visible affine reconstruction and Gaussian elimination at the root;
2. exhaustive unit propagation;
3. one deterministic polynomially budgeted Resolution pass per residual;
4. most-frequent-variable branching with smallest-index tie break;
5. false-first value order.

Every recursive occurrence is charged. No cached formula can terminate a call.

```bash
python experiments/direct/janus_tear_policy0t_no_cache.py
```

## Target theorem

For every UNSAT CNF `F` on `N` variables on which the root affine shortcut does
not fire, a completed Policy-0T execution of charged work `W` yields an ordinary
Resolution refutation with

```text
size  O(W)
depth O(N).
```

Ordinary Resolution is a subsystem of `Res(⊕)`.

## Translation skeleton

### Local Resolution additions

Every added clause stores two parent clauses and a pivot. Since a Policy-0T pass
does not recursively re-index clauses added during that same pass, all clauses
added at one residual increase proof depth by at most one over clauses available
at entry to the residual.

### Unit propagation

Record one forcing clause for every propagated literal. If a conflict appears,
resolve the conflict clause backwards against the unit reasons. This produces a
clause falsified by the current branch decisions.

### Branch combination

If the false branch under `x=0` derives a conflict clause containing `x`, and the
true branch under `x=1` derives the corresponding clause containing `¬x`, resolve
on `x` to derive the parent conflict clause.

Because there is no memoization, every child derivation has one parent context.
No formula-level caching inference or context wrapper is needed.

## Size recurrence

Charge in `W`:

```text
recursive occurrences
branch edges
unit-reason edges
resolution attempts
accepted resolvents
terminal conflicts.
```

Every proof line is associated with one charged event. The intended recurrence is

```text
S(u) <= S(u_0) + S(u_1)
        + local_resolvents(u)
        + unit_reason_steps(u)
        + O(1).
```

Summed over the execution tree, this gives `S(root)=O(W)`.

## Depth recurrence

Along a root-to-leaf execution path:

- every branch fixes a previously unassigned variable;
- every propagated unit fixes another previously unassigned variable;
- there are at most `N` recursive branch levels;
- each residual contributes at most one local-Resolution depth layer;
- each branch combination contributes one layer;
- the total unit-reason chain length is at most `N`.

Therefore the proposed bound is

```text
D <= 3N + O(1).
```

The proof-emitting verifier must calculate this recurrence rather than accept it
as metadata.

## MAJ3 lifting consequence

Let `T_n` be odd-charge Tseitin contradictions on a constant-degree expander
family. Their Resolution width is `Omega(n)`. Replace every edge variable by a
constant-size `MAJ3` block.

The C020 audit verifies the local gadget interface:

```text
MAJ3 is 1-stifling:          true
MAJ3 output fibres affine:   false
lifted variables N:          Theta(n)
root affine shortcut:        absent on fixtures.
```

The width-to-depth lifting theorem of Itsykson, Podolskii, and Shekhovtsov states
that every `Res(⊕)` refutation of size at most `S` has depth

```text
Omega(n^2 / log S).
```

If Policy-0T had polynomial work on the lifted family, the translation would
produce

```text
S = poly(N)
D = O(N),
```

contradicting the lifting lower bound for sufficiently large `N`.
Rearranging the tradeoff with `D=O(N)` gives

```text
S >= 2^Omega(N),
```

and hence exponential Policy-0T work.

## Missing certificate

The asymptotic conclusion is not yet admitted because the executable policy does
not emit:

- clause provenance;
- unit reasons;
- branch conflict clauses;
- a verified Resolution DAG/tree;
- computed proof size and depth.

The next artifact must be a proof-emitting Policy-0T and an independent checker.

## Claim boundary

Once certified, this route eliminates one explicit no-cache JANUS Tear policy.
It does not eliminate Policy-0A with formula caching, all SAT algorithms, or
prove `P != NP`.
