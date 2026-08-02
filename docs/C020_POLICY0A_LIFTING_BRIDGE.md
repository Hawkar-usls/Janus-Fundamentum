# C020 addendum — MAJ3 lifting bridge and the caching obstruction

## Status

`FORMALIZING / TREE ROUTE SURVIVES / CACHING ROUTE BLOCKED`

The finite masked-Tseitin experiments show representation sensitivity but do not
by themselves prove superpolynomial growth. A 2026 lifting theorem supplies an
asymptotic route for shallow `Res(⊕)` proofs. The critical question is now which
JANUS policies actually translate to that proof system.

## Primary lifting theorem

D. Itsykson, V. Podolskii, and A. Shekhovtsov,
*Resolution Width Lifts to Near-Quadratic-Depth Res(⊕) Size*, ECCC TR26-018,
2026.

For an unsatisfiable CNF `phi` requiring Resolution width at least `w`, and a
constant-size 1-stifling gadget `g`, every `Res(⊕)` refutation of `phi o g` of
size at most `S` has depth

```text
Omega(w^2 / log S).
```

The paper gives `MAJ3` as a 1-stifling gadget.

## Executable gadget audit

```text
MAJ3(a,b,c) = 1 iff a+b+c >= 2.
```

The C020 script exhaustively verifies:

- all six coordinate/target cases of 1-stifling;
- neither output fibre is affine over `GF(2)`;
- Policy-0A's visible affine root extractor emits no equations on the lifted
  fixtures.

```bash
python experiments/direct/janus_tear_maj3_stifling_audit.py --self-test
```

Finite results:

```text
MAJ3-lifted odd K4 Tseitin:
  variables:          18
  clauses:          1024
  root affine tears:   0
  residual states:  2427
  answer:           UNSAT

MAJ3-lifted odd K3,3 Tseitin:
  variables:          27
  clauses:          1536
  quadratic cap:    2916
  first unresolved: 2917
```

## The original bridge

The initial plan was:

```text
Policy-0A polynomial work
  -> shallow polynomial-size Res(⊕) proof
  -> contradiction with MAJ3 lifting
  -> exponential Policy-0A lower bound.
```

The middle arrow is not established.

## Formula-caching obstruction

Policy-0A caches exact unsatisfiable residual formulas. Beame, Impagliazzo,
Pitassi, and Segerlind's *Formula Caching in DPLL* studies this exact kind of
operation as a separate proof-complexity resource.

Their work shows that the intuition

```text
DPLL tree + cache = ordinary Resolution DAG
```

is wrong in general. Formula-caching computations are naturally represented by
formula-level caching calculi; some natural variants can be exponentially more
powerful than Resolution, and even the relationship between basic exact caching
and Resolution is nontrivial.

Therefore a short Policy-0A run cannot currently be replaced by a short
`Res(⊕)` proof merely by charging memo edges.

Read:

- `docs/C020_FORMULA_CACHING_BARRIER.md`;
- `proof_attempts/C020/POLICY0A_SIMULATION_LEMMA.md`.

## Route A — Policy-0T without caching

Delete exact residual memoization and count every recursive occurrence. The
remaining procedure consists of:

- DPLL variable branching;
- unit propagation;
- explicit ordinary Resolution additions;
- no formula-level cache inference.

For this restricted tree policy, the standard DPLL-to-Resolution translation can
be extended by attaching the recorded local resolvents. A complete certificate
should yield

```text
proof size  O(full tree work)
proof depth O(N).
```

Now take a bounded-degree expander family with odd-charge Tseitin formulas of
Resolution width `Omega(n)` and lift every variable by `MAJ3`. The lifted input
has `N=Theta(n)` variables.

If Policy-0T had polynomial total work, the translated proof would have

```text
S = poly(N)
D = O(N),
```

while the lifting theorem demands

```text
D = Omega(N^2 / log N).
```

Thus a certified Policy-0T simulation would produce an exponential asymptotic
lower bound for Policy-0T.

## Route B — Policy-0A with caching

The lifting theorem cannot presently be applied. One of the following new
results is required:

1. a valid Policy-0A-to-`Res(⊕)` simulation;
2. a width/depth lifting theorem for the exact formula-caching calculus;
3. a direct lower bound for Policy-0A's caching proof objects;
4. a restriction of the cache rule that reduces it to syntactic proof-DAG reuse.

## Work-accounting audit

The finite audit separates unique residuals from cache traffic:

```text
triangular masked K4:
  unique states:    3842
  recursive calls: 7077
  memo hits:       2111

MAJ3-lifted K4:
  unique states:    2427
  recursive calls: 4117
  memo hits:        888
```

```bash
python experiments/direct/janus_tear_policy0a_work_accounting.py
```

Counting these calls repairs an accounting error, but does not by itself create
a clause-level simulation theorem.

## Current conclusion

The MAJ3 asymptotic bridge is real for proof systems covered by the lifting
theorem. It has **not** yet crossed Policy-0A's exact formula cache.

The clean next result is either:

- an exponential lower bound for the no-cache Policy-0T; or
- a new classification/lower bound for the Policy-0A caching calculus.

Neither result would prove `P != NP`; each would precisely eliminate one more
explicit JANUS Tear policy.
