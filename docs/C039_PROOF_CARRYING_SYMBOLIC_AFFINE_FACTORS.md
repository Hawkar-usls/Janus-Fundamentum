# C039 — Proof-Carrying Symbolic Affine Factor Compilation

**Status:** `CONSTRUCTIVE_RESTRICTED_LEMMA / P_VS_NP=OPEN`

## Purpose

C038 identifies the exact vtree-cut states with communication/factor rows and proves that explicit construction can still cost `2^n` even when a good recursive decomposition exists. C039 attacks the second half of that gate: construct region messages symbolically, without enumerating boundary assignments or truth-table columns.

This cycle closes that operation for the affine `GF(2)` branch of the active portfolio. It does not claim closure for Horn, beta-acyclic, mixed Horn-affine, or arbitrary CNF messages.

## Exact object

An input affine factor is an equation

```text
sum_{x_i in S} x_i = b mod 2.
```

For a vtree node `u` with variable set `X_u`, every factor is assigned to the lowest vtree node containing its support. The boundary

```text
B_u subseteq X_u
```

contains exactly the variables of `X_u` referenced by factors assigned to strict ancestors of `u`.

The message emitted by `u` is the canonical affine relation

```text
M_u(B_u) = exists (X_u \ B_u) . AND { factors assigned in the subtree of u }.
```

It is represented by a deterministic RREF row space over `B_u`, not by a table of its models and not by one continuation row per boundary assignment.

## Bottom-up compiler

For every node `u`, the executable constructs

```text
J_u = M_left AND M_right AND F_u
M_u = canonical_RREF(project_{B_u}(J_u)).
```

Here `F_u` is the conjunction of factors whose lowest containing vtree node is `u`.

Every operation is replayable:

- `join/conjoin`: child message rows and local factor identifiers are listed explicitly;
- `project`: deterministic Gaussian elimination first removes non-boundary columns and then canonicalizes the residual boundary row space;
- `merge`: equal boundary and equal canonical semantic digest authorize interning;
- `separate`: mutual affine row entailment is tested by adding the negation of one target row and solving by Gaussian elimination; a failed implication returns an explicit assignment in the symmetric difference;
- `decide`: the empty-boundary root is either the true affine relation or contains a replayable contradiction;
- `SAT recovery`: a top-down extension trace solves each node join under the parent boundary assignment and passes assignments to the child boundaries;
- `UNSAT handling`: every derived row carries an original-equation provenance bitset; a contradiction must XOR to exactly `0 = 1`.

The verifier reconstructs factor placement and boundaries, reruns every projection, recomputes every digest and merge decision, checks every row provenance, replays the complete witness-recovery trace, and validates the final witness or contradiction.

## Constructive theorem

Let an affine system contain `m` equations over `n` variables and let `T` be any validated vtree over those variables. Then the C039 compiler constructs exact messages at every node with the following properties.

1. Every satisfiable message contains at most `|B_u|` independent rows.
2. Join is affine conjunction and is closed by row concatenation.
3. Existential projection is affine and is computed exactly by variable elimination.
4. Canonicalization is deterministic RREF under the fixed variable order.
5. Equal canonical messages are semantically equal and may be merged.
6. Distinct affine messages admit a polynomially found separating assignment.
7. A satisfiable root admits polynomial top-down witness recovery.
8. An inconsistent root supplies a polynomially checkable XOR provenance for `0 = 1`.

There are at most `2n-1` vtree nodes. Each message has at most `n` rows, and every row has at most `n` coefficients plus an `m`-bit provenance vector. Deterministic vtree discovery, factor placement, joins, projections, comparison, witness recovery, and verification therefore use polynomial work and polynomial certificate volume.

This is a closure theorem for affine messages. It is not a theorem that arbitrary CNF admits affine messages.

## Why this is a genuine C038-to-C039 bridge

For

```text
EQ_n = AND_i (x_i XOR y_i = 0),
```

consider the blocked vtree whose root separates all `x_i` from all `y_i`.

C038's exact communication quotient at that cut has

```text
2^n
```

distinct rows: each assignment to the `x` block requires one different assignment to the `y` block.

C039 does not enumerate those rows. The crossing equality factors are placed at their lowest containing node, the root. Each child exports its live boundary variables symbolically, and the root joins the `n` equations by Gaussian elimination. The frozen audit reaches `n=64`, where the corresponding explicit quotient has

```text
18446744073709551616
```

rows, while the largest emitted affine message still has at most the boundary rank and the charged work remains polynomial.

This does not refute the C038 factor-width count. It shows that explicit continuation-row enumeration and symbolic factor manipulation are different costs. The symbolic compiler retains boundary variables and processes the crossing factor algebraically instead of materializing every residual state.

## Deterministic decomposition discovery

When no vtree is supplied, the executable constructs one deterministically by repeatedly merging the two variable clusters with maximum equation co-occurrence. Every cluster-pair/equation score is charged.

A supplied vtree is not free. It is validated against the variable set and the validation work is charged. The theorem does not require an optimal affine vtree: affine messages remain polynomial on every vtree, though practical work can still differ.

## Frozen audit

```bash
python experiments/direct/janus_c039_symbolic_affine_factor_compiler.py --self-test
```

The entry point imports the separately reviewable core, compiler, and verifier modules in `experiments/direct/`; CI compiles all four files.

The deterministic audit requires:

```text
450 random affine systems on up to 8 variables
exact SAT/UNSAT agreement with exhaustive validation on the small domain
exact existential-projection semantics checked at every vtree node
complete certificate replay for every random case
250 affine merge/separator checks
blocked EQ_n controls at n = 4, 8, 16, 32, 64
SAT and UNSAT Tseitin-cycle parity systems at n = 6, 10, 18, 30
corrupt UNSAT provenance rejected
explicit work-budget exhaustion -> OPEN
mixed Horn-affine -> OPEN_LANGUAGE
NAND3+NEQ 3-SAT image -> OPEN_LANGUAGE
non-affine beta-acyclic language -> OPEN_LANGUAGE
```

The exhaustive checks are test validators on bounded domains only. They are not called by the compiler or certificate verifier.

## Comparison with the active route

### C025 residual quotients

C025 separates residual-state volume from proof volume. C039 supplies a concrete case where the explicit state family can be exponential while one proof-carrying parametric relation remains polynomial.

### C032 PS-width

C032 identifies explicit cut signatures with PS-width-style tables. C039 does not rename those tables. It replaces enumeration, for affine factors only, by an exact projected row space.

### C034 bounded interfaces

C034 composes heterogeneous modules by enumerating a shared boundary of logarithmic size and already supplies the native affine solver. C039 removes that enumeration inside a pure affine region: the boundary may be linear, because Gaussian elimination manipulates all assignments symbolically.

### C035 certified congruence and C036 refinement

Canonical affine RREF supplies the merge certificate. The affine separator operation supplies the complementary distinguishing assignment. C039 composes both operations recursively on a vtree.

### C036.1 Horn-affine negotiation

Unary negotiation remains incomplete. C039 does not reinterpret its fixpoint as compatibility and does not claim that affine closure survives conjunction with unrestricted Horn messages.

### C037 OBDD alignment and C038 TDD/factor alignment

C037 and C038 characterize explicit continuation states under a fixed order or vtree. C039 proves that affine factors can be compiled by a different, parametric message algebra without materializing those states. It is an operation-level bridge, not a new decision-diagram width.

### Structured d-DNNF, SDD and TDD literature

Published structured-compilation results emphasize that existential projection and bottom-up apply can cause width or representation blow-up. C039 does not claim closure of structured d-DNNF under arbitrary projection. It uses the stronger algebraic closure of affine relations under conjunction and existential quantification.

## Adversarial controls

- **Order-sensitive equality:** blocked cuts retain `2^n` communication rows; the affine compiler stays symbolic.
- **NAND3+NEQ deterministic 3-CNF embeddings:** rejected as `OPEN_LANGUAGE`.
- **Tseitin/parity systems:** accepted, including independently checkable inconsistent charge systems.
- **Parity/Horn mixtures:** rejected as `OPEN_LANGUAGE` by this compiler; C036.1 remains the only admitted cross-language bridge.
- **Beta-acyclic non-affine formulas:** rejected here; C033 remains the separate elimination engine.
- **Representation lower bounds:** no exponential TDD/OBDD/row count is promoted to `P!=NP`.

## Located gate

The affine branch of symbolic factor construction is closed. The universal route now needs a message family that remains polynomial under the same recursive operations across language boundaries:

```text
CROSS_LANGUAGE_SYMBOLIC_PROJECTION_CLOSED_UNDER_JOIN
```

The next construction must provide a replayable algebra for Horn/affine/beta-acyclic/compiled interactions, or a decisive obstruction for one explicit proposed algebra. Failure to derive a separator or projection must return `OPEN`; it cannot authorize a merge.

## Claim boundary

C039 is a complete polynomial symbolic vtree compiler for affine systems. It does not decide unrestricted Horn-affine conjunctions, beta-acyclic mixtures, NAND3+NEQ images, arbitrary CNF, or P versus NP.

```text
P_VS_NP=OPEN
```
