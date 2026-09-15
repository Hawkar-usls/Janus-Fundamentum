# C024-A / Issue #211 — Second Derivation Review

**Verdict:** `UNIVERSAL_POLYNOMIAL_RESIDUAL_COUNT_FOR_CURRENT_POLICY0A = REFUTED`.

**Claim ceiling:** this result refutes the first premise of the positive residual-cache bridge for the exact current Policy-0A. It does not prove `P != NP`, does not refute the conditional bridge theorem, and does not rule out a different SAT calculus.

## Gates replayed

### R0 — root affine dispatch

Every core-frequency booster contains a fresh two-variable clause `(x OR b)`. Its satisfying relation has cardinality three. A nonempty affine solution set over `F_2` has size `2^k`; therefore the booster relation is non-affine. Because `b` is private, the registered exact-scope detector cannot complete that scope into an affine relation. Hence the root affine recognizer returns no decision for every padded `H_n`, not merely on finite fixtures.

### R1–R4 — registered Policy-0A mechanics

Dedicated GitHub Actions workflow `Validate C024 Resolution Sink`, run `32697547130`, completed `success` against the registered implementation primitives. Frozen `n=3` replay:

```text
literal_count                = 31140
attempt_budget               = 124560
sink_pairs_available         = 331776
resolution_attempts          = 124560
resolution_additions         = 0
branch_variable              = GT-core variable
```

The probe also checks exact core projection after both Boolean values of the first selected core branch.

The asymptotic mechanics are proved independently of the fixture:

```text
B = 256 n^2
p = 64 n^2
L_GT = 3n(n-1)^2
L_boost = 2 n(n-1) B
L_sink = 6p
p^2 > 4(L_GT + L_boost + L_sink)
```

for every `n>=3`. The smallest-id sink pivot therefore exhausts the registered `max(64,4L)` attempt budget entirely on tautological resolvents and adds zero clauses. As restrictions and unit propagation only reduce the formula afterwards, the inequality persists inductively.

All unassigned core variables have frequency at least `B`; the largest padding frequencies are `2p`; `B>2p`. Therefore every nonterminal branch remains in the core.

### R5 — source theorem scope

Primary source rechecked: Beame, Impagliazzo, Pitassi, Segerlind, *Formula Caching in DPLL*, ACM TOCT 1(3), 2010.

- Definition 4.24 defines theorem-matched directed `GT_n` as the complete-graph ordering formula plus totality.
- Basic exact Formula Caching is a restricted case of `FCWS`.
- Theorem 4.28 lower-bounds every `FCWS` refutation of `GT_n` by `2^(n-2)` nodes.
- Its proof explicitly identifies at least `2^(n-2)` distinct residual formulas and explicitly incorporates unit propagation in the novelty argument.

Thus the lower bound applies to a valid projected exact-FC execution.

### R6 — projection and parameter map

Let `P(K)` delete all clauses containing padding variables from an augmented pre-resolution key. Induction on core branch depth gives

```text
P(K_rho) = unitprop(GT_n | rho).
```

The sink is core-disjoint; private booster propagation cannot force another core variable; no local Resolution inference leaves the sink. Equality of augmented exact keys implies equality of projected core residuals, so the augmented cache cannot merge distinct projected GT residuals.

Therefore

```text
S(H_n) >= 2^(n-2).
```

Freeze the complexity input representation to a standard self-delimiting signed-binary literal-list encoding. The padded family has `O(n^4)` variables/clauses/literal occurrences and maximum variable id `O(n^4)`, hence

```text
N_n = O(n^4 log n).
```

`2^(n-2)` is superpolynomial in `N_n`, so no fixed `c` can satisfy `S(F)<=N^c` for all CNFs.

## Final C024-A status

```text
ISSUE_211_UNIVERSAL_POLYNOMIAL_RESIDUAL_COUNT = REFUTED_FOR_POLICY0A
CONDITIONAL_POLYNOMIAL_RESIDUAL_CACHE_BRIDGE = PROVED
ISSUE_212_UNIVERSAL_POLYNOMIAL_RESIDUAL_SIZE = OPEN_BUT_CANNOT_RESCUE_POLICY0A_ALONE
P_EQUALS_NP = NOT_ESTABLISHED
P_NOT_EQUALS_NP = NOT_ESTABLISHED
P_VS_NP = OPEN
```

The counterfamily becomes a design constraint for the next calculus:

```text
LOCAL_INFERENCE_SCHEDULING_MUST_NOT_BE_STARVABLE_BY_IRRELEVANT_EARLY_PIVOTS.
```
