# C049 — Grouped-subspace partition obstruction

```text
C049 = DECISIVE_REPRESENTATION_OBSTRUCTION
       / GROUP_CONSTRAINT_MANDATORY
       / EXECUTABLE_PRODUCER
       / INDEPENDENT_VERIFIER
       / DRAFT
P_VS_NP = OPEN
```

## 1. Target

C049 starts from the exact fixed-parameter bridges admitted by C048:

```text
fixed-k subspace linear-layout construction
fixed-k subspace branch-decomposition construction
+ C047 offset-aware affine-functional messages
```

The first implementation question is whether a faster constructor for an ordinary represented
matroid can be substituted after expanding every factor normal space into basis columns.

The answer is **no if the basis-block partition is discarded**.

## 2. Exact obstruction

For every integer `d >= 1`, let the grouped subspace arrangement be

```text
V_d = { V_1, V_2 }
V_1 = V_2 = GF(2)^d.
```

There is only one nontrivial grouped cut. Its boundary is

```text
V_1 intersect V_2 = GF(2)^d,
```

so

```text
grouped branch-width(V_d) = d.
```

Choose the canonical basis `e_1,...,e_d` for each copy and form a represented matroid on the
`2d` basis columns. If the two basis blocks are forgotten, the ordinary matroid is

```text
d direct-summed parallel pairs U_{1,2}.
```

Pair each parallel pair as a cherry in a subcubic branch tree. Every cherry-external cut keeps
whole pairs on one side and has connectivity zero. Every leaf edge splits exactly one parallel
pair and has connectivity one. Because every leaf edge has connectivity one,

```text
ordinary represented-matroid branch-width = 1.
```

Hence the ratio between grouped and group-forgotten width is `d`, and is unbounded.

## 3. Consequence for discovery

At cap `k=1`, an ordinary represented-matroid constructor legitimately returns
`FOUND_LAYOUT` for every member of the family. The grouped subspace problem must return
`NO_LAYOUT_AT_CAP` for every `d>1`.

Therefore none of the following is sound:

```text
expand each normal space to basis elements
forget the block partition
run an ordinary matroid branch-width constructor
promote its tree or no-layout result to the grouped factor problem
```

A C049 constructor must preserve whole factor normal spaces as leaves. Equivalently, after basis
expansion it must preserve the partition whose parts are the basis blocks and solve the
partitioned-matroid connectivity problem.

## 4. Primary-source specialization

Jeong–Kim–Oum formulate the constructive theorem directly for a multiset of input subspaces:
each tree leaf is one whole input subspace and every cut measures the intersection of the sums of
whole subspaces on the two sides (`arXiv:1711.01381`).

Choi–Korhonen–Oum explicitly identify a subspace arrangement with a **partitioned matroid** by
choosing one basis block for each subspace and retaining that partition (`arXiv:2605.14428`,
Section 2.5). Their headline represented-matroid theorem and Corollary 5.8 are stated for ordinary
matroid elements. C049 therefore blocks only the shortcut that discards the partition. It does not
claim that a partition-aware adaptation is impossible.

The C048 linear-layout theorem remains direct for grouped subspaces (`arXiv:1507.02184`).
One-dimensional matroid path-width and code trellis complexity remain faithful special cases, not
replacements for grouped leaves.

## 5. Affine-offset discipline

Each grouped leaf in the executable carries:

```text
canonical normal-space RREF
beta values on that normal basis
```

The audit includes equal-offset and distinct-offset copies of the same full normal space. The
structural widths are identical, while the `d=1` avoidance semantics differ:

```text
equal offsets    -> SAT
opposite offsets -> UNSAT
```

Thus C046 remains active: preserving the group partition is necessary for width, and preserving
`beta_i` is separately necessary for semantics.

## 6. Proof-carrying package

The producer emits, for dimensions `1, 2, 3, 4, 8, 16, 32, 64`:

- canonical grouped normal bases and both offset controls;
- the exact grouped cut-space RREF;
- a canonical subcubic pair-cherry tree descriptor for the group-forgotten matroid;
- a digest of every expanded tree edge and its exact intersection RREF;
- exact upper and leaf-edge lower bounds proving ordinary width one;
- cap-one terminal divergence;
- charged work and fixed-point certificate bytes.

The independent verifier does not import the producer. It rebuilds tree connectivity, degrees,
all cuts, ranks, offset semantics, work accounting, certificate bytes, and the integrity digest.

Frozen audit:

```text
8 audit dimensions
maximum certified grouped width 64
ordinary width 1 in every case
full cut certificates for every tree edge
16,830 certificate bytes
0 failures
```

Finite audit validates the implementation. The universal theorem follows from the explicit family
and the symbolic width proof above.

## 7. Surviving C049 gate

```text
PARTITION_AWARE_PROOF_CARRYING_FPT_CONSTRUCTOR_INTEGRATION
```

The next admitted constructor must either:

1. reimplement the direct Jeong–Kim–Oum grouped-subspace branch algorithm, including iterative
   compression, transcripts, boundary coordinate changes, compact partial-decomposition states,
   every failed refinement, and `FOUND_LAYOUT`/`NO_LAYOUT_AT_CAP`; or
2. prove and implement a partition-aware adaptation of a represented-matroid constructor.

After discovery, every leaf and separator must compile to C047-compatible offset-aware functional
states. This PR does not implement that final constructor, does not close NAND3+NEQ, and does not
resolve P versus NP.
