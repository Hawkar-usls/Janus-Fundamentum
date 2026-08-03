# C042 — Proof-Carrying Laminar Affine Forbidden-Subspace Cover

```text
P_VS_NP=OPEN
```

## Exact coordinate object

The input is a CNF formula `F(x)` together with an affine system `A x = b` over `GF(2)`. C042 does not receive a free coordinate basis. Provenance-carrying Gaussian elimination constructs and certifies

```text
x = p + B lambda,
lambda in GF(2)^d.
```

For every clause `C`, requiring every literal of `C` to be false gives an affine system over `lambda`. Its solution set is either empty or an affine subspace

```text
U_C = {lambda : C is false}.
```

Therefore

```text
F(x) AND A x=b is SAT
<=>
GF(2)^d \ union_C U_C is nonempty.
```

This is the Union-of-Subspace Avoidance / CNF-in-a-subspace formulation studied by Arvind and Guruswami. The general formulation is not treated as tractable: even 2-SUB-SAT is NP-hard. C042 closes only a separately recognized laminar subclass.

## Constructive theorem

Assume that every pair of nonempty clause-falsifying subspaces is disjoint or nested:

```text
U intersect V = empty,
U subseteq V,
or V subseteq U.
```

The property is discovered by exact affine intersection and inclusion tests; it is not supplied as an oracle.

After duplicate and contained subspaces are removed, the maximal forbidden subspaces are pairwise disjoint. Hence

```text
|union_C U_C| = sum_i 2^dim(M_i).
```

- If the sum equals `2^d`, the maximal members form a replayable disjoint affine cover and certify UNSAT.
- Otherwise coordinates are fixed one at a time. For both candidate bits, C042 intersects each maximal forbidden subspace with the prefix cell and counts the covered points by rank. It chooses the first branch whose covered count is smaller than the cell size. After `d` steps the resulting `lambda` lies outside every forbidden subspace and lifts through `x=p+B lambda` to a complete SAT witness.

No assignment enumeration, general SAT oracle, formula-equivalence oracle, supplied decomposition, or optimal subspace-arrangement oracle is used.

## Basis artifact and provenance

The coordinate basis is part of the proof object. The artifact records:

- canonical RREF rows of the input affine system;
- for every RREF row, the exact subset of original equations whose XOR derives it;
- a contradiction provenance subset when the affine system itself is inconsistent;
- the free-variable list;
- one particular solution `p`;
- a nullspace basis `B`;
- the affine coordinate form of every original variable.

The verifier independently recomputes canonical RREF, checks every provenance XOR, checks `A p=b`, checks `A B=0`, checks basis independence on the declared free coordinates, and reconstructs every coordinate form.

## Independent certificate verifier

`verify_certificate_report` does not accept a digest as semantic evidence. For SAT, UNSAT and non-laminar terminals it independently replays:

1. input canonicalization and digest binding;
2. affine basis construction and provenance;
3. clause-to-coordinate translation;
4. canonical RREF and literal-equation provenance for every forbidden factor;
5. duplicate compression and every pair relation;
6. maximality and pairwise disjointness;
7. exact cardinalities;
8. the complete conditional-count trace;
9. the final `lambda` and lifted assignment;
10. the original CNF and affine constraints.

For `OPEN_BUDGET`, deterministic replay under the identical capability and budget is required. Corrupt witness, basis, relation, count, ledger, or digest fields are rejected.

## Fixed polynomial ledger

Let `L` be the explicit encoded input length used by the executable. The capability fixes one polynomial envelope:

```text
B(L) = 64 * (L + 1)^6.
```

An optional smaller operational cap may force an earlier refusal, but never enlarges this theorem budget. The producer ledger charges:

```text
basis elimination and row scans
row XORs and swaps
coordinate-form construction
clause translation
all intersections and inclusion tests
pair and maximality discovery
big-integer cardinality operations
conditional counting
witness recovery
certificate bytes
```

The independent verifier uses the same fixed polynomial envelope and records its own work ledger. A certificate is rejected if its stated producer ledger is arithmetically inconsistent, exceeds the capability, or understates its serialized byte volume. Any producer or verifier overflow returns or validates only `OPEN_BUDGET`.

## Frozen audit

```bash
python experiments/direct/janus_c042_laminar_affine_forbidden_cover.py --self-test
```

Current deterministic audit:

```text
120 random laminar instances on d <= 8
120 EXACT / 0 OPEN
0 SAT/UNSAT mismatches
0 witness failures
0 independent replay failures

128-dimensional SAT without enumerating 2^128
128-dimensional UNSAT from two disjoint halfspaces
128-variable affine line with two hidden large-clause blockers -> UNSAT
24 nested factors -> 1 maximal factor
same nested family under a tight operational cap -> OPEN_BUDGET

C023 NAND3+NEQ coordinate images at n=24,32,48 -> OPEN_NON_LAMINAR
explicit crossing control -> OPEN_NON_LAMINAR
affine contradiction provenance -> UNSAT
corrupt certificate -> REJECTED
```

Finite controls validate the implementation. The universal restricted theorem follows from affine elimination, laminar maximality, disjoint cardinality addition, and the conditional-count invariant.

## Literature alignment

Björner and Ekedahl place finite-field subspace-union counting in the classical intersection-poset framework. Arvind and Guruswami identify CNF satisfiability in a subspace with both Union-of-Subspace Avoidance and common zeros of products of affine forms, and establish the hardness boundary of the unrestricted problem.

C042 is the elementary laminar specialization. Laminarity collapses the relevant inclusion-exclusion structure to pairwise disjoint maximal members. The implementation contribution is proof-carrying discovery, charged basis construction, exact witness/certificate recovery, and strict polynomial refusal. It is not promoted as a new general arrangement invariant.

## Decisive boundary

C041 proves that the C023 `{NAND3,NEQ}` hard image becomes the original arbitrary 3-CNF in affine coordinates. C042 adds real semantic compression only when a further laminar certificate is discovered. The registered high-dimensional hard-image controls contain crossing incomparable forbidden subspaces and therefore return

```text
OPEN_NON_LAMINAR.
```

The surviving gate is

```text
POLYNOMIAL_DECOMPOSITION_OF_CROSSING_AFFINE_FORBIDDEN_SUBSPACES.
```

A later route may use bounded intersection support, a decomposable arrangement cover, a vtree, or another join-closed symbolic language, but discovery, intermediate size, projection, counting, SAT witness recovery and UNSAT evidence must all remain inside one fixed polynomial budget.
