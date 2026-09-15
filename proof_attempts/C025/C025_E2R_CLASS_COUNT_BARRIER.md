# C025-E2R — Class-count barrier and first structural frontier

**Status:** `NAIVE_CLASS_COUNT_INVARIANT_REFUTED`; `SUPPORT_LOCALITY_FRONTIER_OPEN`.

This provider note mirrors the canonical TOPA process note.

## 1. Semantic-signature ceiling

For `n` root variables and `K` deterministic extension variables, every root assignment induces a signature in `{0,1}^K`. Hence any partition distinguished only by extension signatures has at most `2^K` classes.

If `M` root-assignment classes must all be distinguished,

```text
K >= ceil(log2 M).
```

But `M <= 2^n`, so

```text
ceil(log2 M) <= n <= N.
```

Therefore pure assignment-class counting cannot by itself produce a superpolynomial extension-count lower bound in input length `N`.

## 2. Parity compression counterexample

Frozen B2 extensions are fan-in-2 AND gates with negated literals allowed.

Given current parity bit `y` and root bit `x`, define

```text
t1 <-> ( y AND  x)
t2 <-> (~y AND ~x)
y' <-> (~t1 AND ~t2)
```

Then `y'=y XOR x`.

Thus parity on `n` root variables is represented by exactly `3(n-1)` extension variables.

By contrast, any root-only CNF for `PARITY_n=1` has at least `2^(n-1)` clauses, and any root-only DNF has at least `2^(n-1)` terms: every nontrivial implicate/implicant must mention all `n` variables, because flipping any omitted variable flips parity without changing satisfaction of that clause/term.

Therefore flat clause/term/case count is not stable under recursive extensions and cannot support an additive `one extension -> bounded flat collapse` theorem.

## 3. Circuit interpretation

A list of `K` B2 definitions is a Boolean circuit DAG with exactly `K` non-input fan-in-2 AND gates and free input-wire negation.

A full #217 lower bound therefore needs either:

- a structural proof invariant that remains stable under these recursive auxiliary circuits, or
- a lower bound on the auxiliary circuit resource actually needed by every ER3 refutation.

Semantic cardinality and flattened formula size are insufficient.

## 4. First restricted frontier: transitive support locality

Define recursively

```text
support(root literal x) = {x}
support(e_i) = support(a_i) union support(b_i)
```

for `e_i <-> (a_i AND b_i)`.

Call a proof `kappa-local` if every extension satisfies

```text
|support(e_i)| <= kappa.
```

This restriction is intentionally stronger than full ER3 and is only a testbed.

Relevant literature provides lower-bound techniques for local extension variables in neighboring proof systems, including Sokolov's heavy-width lower bounds for Resolution on functional Nisan-Wigderson encodings and locality/arity tradeoffs for Polynomial Calculus with extension variables. These are **not** automatically lower bounds for B2/ER3. A transfer requires an exact reduction or simulation theorem.

## 5. Restricted target

For `kappa=O(log N)`, search for an explicit polynomial-size UNSAT CNF family such that every `ER3[kappa-local]` refutation either requires superpolynomially many extension variables or is impossible inside the restriction.

Any result here is restriction-only and must not be promoted to full ER3.

## 6. Status

```text
E2R_GLOBAL_EXTENSION_COUNT              = OPEN
E2R_SEMANTIC_CLASS_COUNT_METHOD         = REFUTED_AS_SUPERPOLY_ROUTE
E2R_FLAT_CASE_COUNT_METHOD              = REFUTED_BY_PARITY_COMPRESSION
E2R_EXTENSION_DAG_IS_K_GATE_CIRCUIT     = PROVED
E2R_SUPPORT_LOCALITY                    = FROZEN_V0
E2R_KAPPA_LOCAL_LOWER_BOUND             = OPEN_RESTRICTED_FRONTIER
TRANSFER_FROM_LOCAL_EXTENSION_LITERATURE= NOT_ESTABLISHED
P_VS_NP                                  = OPEN
```
