# C021 decisive attack — H130 ordinary-Resolution simulation

## Status

`H130 AS STATED: DESTROYED`

## Statement under attack

H130 claims that every terminating UNSAT execution of the full Policy-0T can be
translated into an ordinary Resolution refutation of size `O(W)` and depth
`O(N)`.

The full Policy-0T is not only a DPLL/Resolution search policy. Its dispatcher
first executes an exact visible-affine recognizer and Gaussian consistency test.
Only when that recognizer returns `None` does recursive search begin.

## Implementation witness

`experiments/direct/janus_tear_policy0t_no_cache.py` performs:

```text
affine_answer = visible_affine_root_decision(cnf)
if affine_answer is not None:
    return immediately
```

Its canonical visible-Tseitin self-test has:

```text
answer             = UNSAT
recursive_calls    = 0
affine_equations   = 4
```

The C021 finite audit extends this to `K3,3`, the cube graph and the Petersen
graph. All are bounded-degree odd-charge Tseitin CNFs and all terminate before
one recursive call.

```bash
python experiments/direct/janus_tear_policy0t_affine_resolution_obstruction.py
```

## Asymptotic contradiction

For every fixed degree bound `d`, the visible local parity relation at one
vertex has constant truth-table size. The current recognizer enumerates only
constant-size local scopes and then performs Gaussian elimination, so on a
bounded-degree graph its total work is polynomial in the graph size.

Classical proof-complexity lower bounds give bounded-degree expander-Tseitin
CNFs requiring exponential-size ordinary Resolution refutations. Primary
sources include:

- Alasdair Urquhart, *Hard Examples for Resolution*, JACM 34(1), 1987,
  DOI `10.1145/7531.8928`;
- Eli Ben-Sasson and Avi Wigderson, *Short Proofs Are Narrow — Resolution Made
  Simple*, JACM 48(2), 2001, DOI `10.1145/375827.375835`, ECCC TR99-022.

Choose the visible odd-charge Tseitin CNF over such an explicit bounded-degree
expander family. Then:

```text
Policy-0T charged affine work = poly(N)
ordinary Resolution size      = exp(Omega(N))
```

Therefore no translation with ordinary-Resolution size `O(W)` can exist for
**every** Policy-0T execution.

This falsifies the universal ordinary-Resolution clause in H130.

## Why the finite trace result remains valid

The C020/C021 trace fixture satisfies:

```text
affine_answer = None
```

and enters only the search core:

```text
unit propagation
+ one-pass local Resolution
+ deterministic branching
- memoization
```

The independently verified finite trace-to-proof bridge remains correct for
that fixture. The decisive attack concerns the quantifier over the **full**
Policy-0T dispatcher, not the legal branch proof already emitted.

## Minimal repair

### Descendant A — non-affine search-core simulation

Restrict the theorem to executions for which the initial affine recognizer
returns `None`:

> Every terminating UNSAT execution of the no-cache Policy-0T search core can be
> translated into ordinary Resolution with size `O(W)` and depth `O(N)`.

This is the theorem actually needed on the MAJ3-lifted target, because C020
already verifies that the visible affine recognizer does not classify that
encoding.

The remaining proof obligations are the decision-clause invariant, reverse
unit-reason elimination and residual learned-clause lifting.

### Descendant B — mixed dispatcher simulation

Alternatively, simulate the whole dispatcher directly in `Res(⊕)`:

```text
affine branch     -> explicit parity/Gaussian certificate
non-affine branch -> ordinary Resolution certificate, hence Res(⊕)
```

This requires a proof-producing affine extractor and a verified translation of
each recognized constant-scope affine relation from its CNF encoding into the
chosen `Res(⊕)` calculus.

## Decisive result

The implication

```text
full Policy-0T work W
  -> ordinary Resolution proof size O(W)
```

is false.

The surviving lower-bound route is narrower and cleaner:

```text
MAJ3-lifted Tseitin
  -> affine_answer=None
  -> Policy-0T non-affine search core only
  -> ordinary Resolution / Res(⊕) trace translation
  -> depth-controlled lifting lower bound
```

## Claim boundary

This attack does not prove `P != NP`, does not refute every Tear policy and does
not yet prove the repaired non-affine-core simulation. It terminally rejects one
incorrect proof-system target and identifies the exact descendant needed by the
existing MAJ3 route.
