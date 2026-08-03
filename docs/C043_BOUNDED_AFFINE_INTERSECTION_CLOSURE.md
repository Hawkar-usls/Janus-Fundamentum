# C043 — Bounded Signed Affine-Intersection Support

```text
P_VS_NP=OPEN
```

## Exact coordinate object

C043 is stacked on the proof-carrying C042 basis layer. Its admitted input is a CNF together with an affine system; the parameterization

```text
x = p + B lambda
```

must be constructed or replayed through the C042 provenance contract. A free `coordinate_rows/constants` table is not an admitted theorem input.

For every clause `C`, simultaneous falsification defines an empty set or an affine subspace

```text
U_C subseteq GF(2)^d.
```

The coordinate formula is satisfiable exactly when

```text
GF(2)^d \ union_C U_C
```

is nonempty.

## Primary structural parameter

“Bounded crossing” does **not** mean a bounded number of crossing pairs, bounded clause width, or bounded codimension.

Process the nonempty forbidden subspaces in one deterministic order. After the first `t` factors, maintain

```text
1_(union_{i <= t} U_i) = sum_S c_t(S) 1_S,
```

where every key `S` is a canonical nonempty affine intersection and only nonzero coefficients are retained.

Define the live signed-support parameter

```text
K = max_t |supp(c_t)|.
```

This maximum intermediate support, not merely the final number of terms, is the C043 admission metric. Equal intersections are merged by canonical RREF and zero coefficients cancel. A raw intersection poset may contain many syntactic subset intersections; C043 materializes only the deterministic canonical nonzero signed support, but every attempted intersection and every intermediate term is charged.

Codimension and the number of crossings are secondary descriptive statistics. They are never promoted as the controlling invariant.

## Exact signed update

Adding `U_t` uses the pointwise identity

```text
1_(A union U_t) = 1_A + 1_(U_t) - 1_A 1_(U_t)
1_S 1_(U_t)     = 1_(S intersect U_t).
```

Equivalently, the coefficient map must satisfy

```text
c_t = c_(t-1) + e_(U_t) - T_(U_t)(c_(t-1)),
T_U(S) = S intersect U.
```

Every nonempty intersection is canonicalized, equal keys are added, and zero coefficients are removed. This recurrence is the proof-carrying replacement for enumerating the full `2^m` inclusion–exclusion table.

## Constructive theorem

Let `L` be the complete encoded input length, including the affine system, CNF, capability manifest and coordinate dimension. Fix one capability exponent `q` independently of the input and define

```text
K_limit(L) = min(absolute_support_cap, L^q).
```

If the deterministic construction satisfies

```text
K <= K_limit(L)
```

and all work, integer-bit and certificate-volume ledgers remain within their fixed polynomial envelopes, then C043 constructs the signed cover, exact counts, and SAT/UNSAT evidence in

```text
O(m K poly(d,L))
```

total standard-model work.

Coefficient magnitudes may grow exponentially as integers, so their **bit lengths** are explicitly charged; the sequential inclusion–exclusion recurrence gives an `O(m)`-bit bound per coefficient. Final compactness does not excuse a large intermediate support or large coefficient/certificate volume.

Strict terminals are separated by cause:

```text
OPEN_INTERSECTION_CLOSURE   live signed support exceeds K_limit
OPEN_WORK_BUDGET            total charged construction or verification work exceeds its polynomial envelope
OPEN_CERTIFICATE_VOLUME     emitted or replayed proof volume exceeds its polynomial envelope
```

None of these terminals is a hardness claim.

## Exact counting and decision

For the final coefficient map `c_m`,

```text
|union_C U_C| = sum_S c_m(S) 2^dim(S).
```

- Equality with `2^d` gives an exact signed affine-cover UNSAT certificate.
- Otherwise conditional signed counting fixes coordinates one at a time. For a prefix cell `P`,

```text
|P intersect union_C U_C|
  = sum_S c_m(S) |P intersect S|.
```

A child with covered count smaller than its cell size preserves an uncovered point. The final coordinate lies outside every clause-falsifying factor and lifts through the certified C042 basis to a complete SAT witness.

## Separate proof-carrying verifier

C043 requires a dedicated module:

```text
experiments/direct/janus_c043_crossing_verifier.py
```

It may import common affine primitives from C042, but it must not verify a certificate by simply calling the C043 producer and comparing outputs.

The verifier independently checks:

1. the C042 affine-basis artifact and coordinate forms;
2. clause-to-forbidden-subspace translation;
3. the deterministic factor order;
4. every incremental signed-support transition;
5. canonical RREF identity of every intersection key;
6. coefficient addition, cancellation and coefficient bit lengths;
7. `K_t = |supp(c_t)|`, `K = max_t K_t`, and the fixed support capability;
8. root union cardinality;
9. every conditional signed-count branch;
10. the final coordinate, lifted SAT witness, or signed-cover UNSAT equality;
11. producer and verifier work/certificate ledgers.

The universal indicator identity is verified algebraically, not by enumerating assignments. If the verifier replays

```text
c_t = c_(t-1) + e_(U_t) - T_(U_t)c_(t-1)
```

for every `t`, induction proves

```text
sum_S c_t(S) 1_S = 1_(union_{i <= t} U_i)
```

on every point of `GF(2)^d` simultaneously.

Möbius inversion over a supplied intersection poset is optional, not required. If used, discovery of the poset, inversion work and proof volume must be charged. The deterministic sequential recurrence is the canonical baseline because it avoids an optimal-poset oracle.

## Relationship to C042

Laminar arrangements are a degenerate signed-support case. After cancellation, the support is represented by the pairwise-disjoint maximal forbidden subspaces with coefficient `+1`.

Two genuinely crossing hyperplanes have support

```text
U,
V,
U intersect V
```

and therefore lie outside C042 but inside C043.

Thus C043 strictly extends the semantic class of C042 while inheriting its basis, witness and certificate obligations.

## Existing executable evidence

The current prototype demonstrates the signed recurrence on:

```text
300 random coordinate CNFs on d <= 8
64-dimensional crossing SAT with 3 terms
64-dimensional crossing UNSAT cover
200 repeated crossing factors compressed to 3 terms
24-variable NAND3+NEQ pressure -> OPEN_INTERSECTION_CLOSURE
```

These controls support the signed-support lemma. They do not yet by themselves admit the full C043 architecture, because the current prototype still accepts a ready coordinate map and uses producer replay as its verifier. The dedicated verifier and C042-basis integration remain explicit admission obligations.

## Boundary and next cycle

C043 closes only the **global bounded-live-signed-support** class. It does not contain local vtree decomposition as part of the same theorem.

The next route is reserved as C044:

```text
C044 LOCAL_SIGNED_SUPPORT_VTREE_COMPOSITION_OR_STRICT_OPEN
```

C044 may partition a globally large intersection arrangement into local components with polynomial local signed supports and combine them through proof-carrying join/project messages. It must charge vtree discovery, factor placement, local support maxima, separator representation, join/projection work, canonicalization, witness lifting, UNSAT proof volume and all intermediate products.

If a local component, separator message or join exceeds its fixed polynomial capability, C044 returns

```text
OPEN_LOCAL_SUPPORT
```

rather than weakening the global C043 definition.

The surviving C043 gate is therefore:

```text
COMPLETE_PROOF_CARRYING_GLOBAL_SIGNED_SUPPORT_COMPILER
```

and, after that compiler is admitted, the broader route is:

```text
LOCAL_SIGNED_SUPPORT_VTREE_COMPOSITION_OR_STRICT_OPEN.
```
