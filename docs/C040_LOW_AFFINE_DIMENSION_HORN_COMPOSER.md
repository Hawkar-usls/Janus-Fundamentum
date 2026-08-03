# C039.3 — Low-Affine-Dimension Horn / Dual-Horn Composition

**Status:** `CONSTRUCTIVE RESTRICTED THEOREM / P_VS_NP=OPEN`

The branch, executable, proposal filenames and wire schema retain the earlier
`c040` spelling only as pre-admission replay aliases. The canonical logical cycle
is `C039.3`; `C040` is reserved for portfolio-guided semantic-vtree discovery.

## Theorem

Let `H` be a Horn or dual-Horn CNF, let `A` be an affine `GF(2)` system, and let

```text
S = Vars(H) intersect Vars(A)
R = project_S(Models(A))
d = affine dimension of R.
```

C039.3 decides `H AND A` with replayable SAT/UNSAT evidence in

```text
O(2^d poly(L)).
```

For one fixed capability exponent `q`, the implementation closes only when

```text
2^d <= L^q.
```

Otherwise it returns `OPEN_DIMENSION_BUDGET`. The exponent is part of the fixed
solver capability, not an input-dependent exponent.

## Construction

1. A dual-Horn module is converted to Horn by complementing all coordinates. Each affine row changes RHS by the parity of its support size, so the affine language is preserved.
2. Provenance-carrying Gaussian elimination computes the exact projection of `A` onto `S`.
3. A particular solution and nullspace basis enumerate exactly the `2^d` affine-feasible interface states, rather than all `2^|S|` assignments.
4. Each state is extended by the affine engine and checked by Horn least-model closure.
5. SAT returns one combined checked witness. UNSAT contains one replayable Horn conflict trace for every projected affine state.

The verifier deterministically reconstructs the projection, basis, state
enumeration, native calls and terminal. It does not trust claimed semantic
equivalence and does not invoke a general SAT oracle.

## Frozen audit

```bash
python experiments/direct/janus_c040_low_affine_dimension_composer.py \
  --self-test \
  --output proposals/C040-JANUS-LOW-AFFINE-DIMENSION-HORN-COMPOSER.frozen.json
```

```text
500 random Horn/dual-Horn + affine cases
112 SAT
388 UNSAT
0 OPEN under the audit capability
0 truth-table mismatches
0 witness failures
0 verification failures
integrity f43feb4523ce5017c1288d59c247dee69923592597f31fae9a6dc732a220fa5d
```

Finite exhaustive checks validate the implementation; they are not the theorem.

## Dense semantic-interface control

Take every positive pair clause `(x_i OR x_j)` on 80 variables and add affine
equalities `x_1 XOR x_i = 0`. The primal graph is a clique, so the fixed-`k`
graph-separator route rejects sufficiently large instances. But the affine
projection on all 80 shared variables has dimension one.

```text
shared variables    80
projected dimension  1
states examined      1
status              SAT
```

Thus semantic dimension can be small when raw graph width and raw interface size
are large.

## Unary/pairwise fact obstruction

Let an affine module define the two-point line `{a, not a}` on ten variables. A
Horn module contains two large negative clauses, one forbidding each endpoint.
Their conjunction is UNSAT.

The Horn relation has no forced literal and every pairwise projection is the full
Boolean square. Unary exchange and pairwise equality aliases expose no conflict.
C039.3 enumerates the two one-dimensional affine states and emits two Horn
refutations.

This closes only that bounded fact basis; it is not a lower bound against every
stronger algebra.

## NAND3 + NEQ control

On the C023 reduction image with 24 source variables:

```text
projected affine dimension 24
required states             2^24
terminal                    OPEN_DIMENSION_BUDGET
```

C039.3 therefore does not silently decide arbitrary 3-SAT.

## Located gate

```text
CROSS_LANGUAGE_COMPOSITION_BEYOND_LOW_AFFINE_INTERFACE_DIMENSION
```

The next construction must cover high-dimensional interfaces by polynomial
symbolic Horn projection, a richer join-closed message language,
beta-acyclic/compiled regional messages, or a jointly discovered semantic vtree.
Missing closure or exceeded certificate volume must return `OPEN`.

## Canonical compiler ladder

```text
C039.0  supplied-vtree symbolic-factor contract
C039.1  pure-affine symbolic vtree factors
C039.2  single-head Horn symbolic projection
C039.3  low-affine-dimension Horn/dual-Horn plus affine composition
C040    portfolio-guided semantic-vtree discovery
C041    joint portfolio/compiler completeness gate
```

## Claim boundary

C039.3 is exact only for Horn or dual-Horn plus affine inputs whose projected
affine state space fits one fixed polynomial capability. It does not solve
unrestricted Horn-affine conjunctions, arbitrary CNF, the general NAND3+NEQ
image, or P versus NP.

```text
P_VS_NP=OPEN
```
