# C024-A — ISSUE #211 ATTACK: GT ENCODING TRANSFER BEFORE LOCAL-RESOLUTION ROBUSTNESS

**Status:** first adversarial pass completed; a theorem-transfer encoding gap was found. Issue #211 remains open.

**Target:** prove or refute a universal polynomial bound on the number of exact pre-resolution cache keys produced by uncapped deterministic Policy-0A.

## 1. Why this pass comes before any asymptotic fit

A lower bound may be transferred only if the theorem's formula family is the same mathematical object as the family executed by the repository, or if a formal reduction connects the two while preserving the resource being lower-bounded.

Therefore the first gate is not `LOCAL_RESOLUTION_ROBUSTNESS`. The first gate is `OBJECT_IDENTITY / ENCODING_TRANSFER`.

## 2. Source theorem object

Beame, Impagliazzo, Pitassi and Segerlind, *Formula Caching in DPLL*, define the graph-tautology family `GT_n` used in their Formula-Caching lower bound with directed variables `x_(i,j)` for `i != j`. The paper explicitly states that `GT_n` includes the clauses of the graph-ordering principle on `K_n` together with totality clauses

`(x_(i,j) OR x_(j,i))`

for `i != j`.

Their Theorem 4.6 states that any `FC^WS` refutation of this `GT_n` family requires at least `2^(n-2)` nodes.

The proof uses structural information carried by these directed variables and the surviving totality clauses to define partial orders, `minimal`, `tops`, and `prune` and then to distinguish exponentially many residuals.

## 3. Repository proxy object

The current executable probe

`experiments/direct/janus_tear_policy0a_graph_tautology_probe.py`

uses a different compact representation:

- one variable for every **unordered** pair `{i,j}`;
- `variable_count = C(n,2)`;
- `lt(i,j)` is the positive literal of that pair variable when `i<j`;
- `lt(j,i)` is represented by the **negation of the same variable**.

Thus the compact probe compiles the opposite orientation into Boolean negation. The source theorem instead has distinct directed symbols `x_(i,j)` and `x_(j,i)` plus explicit totality constraints.

Hence

`REPOSITORY_SMART_GT_PROXY != SOURCE_THEOREM_GT_n`

has now been established at the representation level.

This does **not** say the two encodings are unrelated. It says their relationship must be proved before the historical residual-count lower bound is imported.

## 4. Consequence for the old C023/C024 argument

The statement

`historical GT Formula-Caching lower bound -> current smart GT probe`

was missing an encoding/reduction lemma.

Therefore there are now **two independent transfer gates** before `GT_n` can refute Issue #211 for Policy-0A:

1. `A0_ENCODING_TRANSFER` — use the theorem-matched original `GT_n` encoding, or prove a reduction/equivalence preserving the relevant residual-cache lower bound;
2. `A1_LOCAL_RESOLUTION_ROBUSTNESS` — prove that Policy-0A's deterministic one-layer Resolution pass does not invalidate the exponential novelty argument, or compile each annotated Policy-0A state to the theorem's proof system with polynomial overhead.

Neither gate is currently proved.

## 5. Parameter conversion gate

Even after A0 and A1, the lower bound must be stated in actual CNF input length `N`, not only in order parameter `n`.

For the theorem-matched directed-variable `GT_n`, the variable and clause counts are polynomial in `n`; the transitivity part has cubic order. Under any conventional explicit binary CNF encoding, `N = poly(n)` (more specifically cubic up to identifier/log factors).

Therefore a surviving `2^(n-2)` node lower bound would be superpolynomial in `N`. But the exact `n -> N` conversion must be frozen for the exact generator before promotion.

Gate:

`A2_PARAMETER_TRANSFER: 2^(n-2) -> superpoly(N)`.

## 6. Refined Issue #211 attack stack

```text
A0  reconstruct theorem-matched original GT_n encoding
    OR prove an exact reduction from source GT_n to the smart proxy

A1  include the exact Policy-0A one-layer Resolution pass
    and prove/refute survival of the novelty/prune invariant

A2  charge exact encoded length N and convert the lower bound

A3  if A0+A1+A2 pass:
    Policy-0A has a superpolynomial residual-count family
    -> UNIVERSAL_POLYNOMIAL_RESIDUAL_COUNT is REFUTED
```

If A1 fails because local Resolution truly collapses the source `GT_n` family, that is valuable positive information: `GT_n` stops being a counterfamily and we must search another family or derive the mechanism responsible for the collapse.

## 7. Immediate mathematical sublemmas

### A0.1 — source-family reconstruction

Freeze an executable `GT_n^source` whose variables and clauses match the theorem's stated formula, rather than relying on the compact tournament proxy.

**Status:** OPEN.

### A0.2 — compact-proxy transfer

Prove or refute that identifying opposite directed variables by

`x_(j,i) = NOT x_(i,j)`

and eliminating now-redundant order clauses preserves a lower bound on exact residual-cache state count up to polynomial factors.

**Status:** OPEN. No such preservation theorem is currently present in the repository.

### A1.1 — local resolvent classification on source GT

For every Policy-0A state reached from `GT_n^source`, classify every accepted one-step resolvent by the order information it adds and by its effect on the historical `prune` invariant.

**Status:** OPEN.

### A1.2 — bounded novelty destruction

Find polynomial `p` such that one complete frozen local pass can destroy/identify at most `p(n)` historical novelty classes, or produce a counterexample showing that a local pass can collapse superpolynomially many classes.

**Status:** OPEN.

## 8. TOPA mathematical-mode contribution

This pass demonstrates the intended role of TOPA in mathematics:

- it did not decide `P=NP`;
- it attacked the identity of the object used in a theorem transfer;
- it found a concrete missing premise;
- it converted that premise into a new exact proof gate.

The reusable rule is:

`BEFORE_THEOREM_TRANSFER -> VERIFY_OBJECT_IDENTITY + ENCODING + PARAMETERS + RESOURCE_MEASURE`.

## 9. Current verdict

```text
ISSUE_211_UNIVERSAL_POLYNOMIAL_RESIDUAL_COUNT = OPEN
SOURCE_GT_LOWER_BOUND                         = ESTABLISHED_FOR_SOURCE_SYSTEM
SMART_PROXY_TRANSFER                          = NOT_ESTABLISHED
LOCAL_RESOLUTION_ROBUSTNESS                   = NOT_ESTABLISHED
PARAMETER_TRANSFER                            = PENDING_EXACT_SOURCE_GENERATOR
P_EQUALS_NP                                   = NOT_ESTABLISHED
P_NOT_EQUALS_NP                               = NOT_ESTABLISHED
```

The next rigorous move is A0, not another curve fit.
