# R5 E9 — Cubic Kernel Circuits as Connected Contracted Cubic Graphs

Date: 2026-09-27

Status:
`JANUS_DERIVED_EXACT_STRUCTURAL_THEOREM_CANDIDATE__NO_D1_PROMOTION`

Checker:
`experiments/r5_e9_cubic_kernel_circuit_contraction.py`

Parents:
- `R5_E9_CUBIC_EXACT_ONE_AFFINE_COSET_MINWEIGHT_NORMAL_FORM_2026-09-27_v1.0.md`
- `R5_E9_AFFINE_COSET_CIRCUIT_AUGMENTATION_GLOBAL_OPTIMALITY_2026-09-27_v1.0.md`
- `R5_E9_RATIONAL_KERNEL_NULLITY_FPT_ROUTER_2026-09-27_v1.0.md`
- `R5_E9_CUBIC_KERNEL_WORD_NORMAL_FORM_2026-09-24_v1.0.md`

Scientific firewall:

```text
THIS IS AN EXACT STRUCTURAL BRIDGE.
IT REMOVES CIRCUIT-MINIMALITY AS A SEPARATE SEARCH LAYER.
IT DOES NOT SUPPLY A POLYNOMIAL NEGATIVE-KERNEL FINDER.
E8_D1 = EMPTY.
P_VS_NP = OPEN.
```

## 1. Setup

Let

```text
A in {0,1}^{n x n}
```

be a cubic incidence matrix: every row and every column has exactly three ones.
Equivalently, the Tanner/incidence graph is 3-regular on both shores.

Let

```text
0 != z in ker_F2(A)
```

and put

```text
S = supp(z).
```

Because each row has weight three and `Az=0`, every row intersects `S` in an
even number of columns. Therefore every row intersects `S` in exactly

```text
0 or 2
```

columns.

Call a row **active** when it intersects `S` in two columns.

## 2. Contract the active checks

Construct a multigraph `G_z` as follows.

- vertex set: `S`;
- for every active row whose two selected columns are `u,v`, add one edge
  `uv` labelled by that row.

Parallel edges are allowed. Loops are absent because an incidence row contains
three distinct columns.

### Lemma KCC-1 — the contraction is cubic

Every vertex of `G_z` has degree exactly three.

### Proof

Take `v in S`. The corresponding column of `A` contains exactly three ones, so
`v` belongs to exactly three rows. Since `v` is selected and `Az=0`, each of
those rows must contain exactly one additional selected column. Hence each row
becomes one contracted edge incident with `v`. Thus

```text
deg_Gz(v)=3.
```

QED.

Consequently

```text
2 |E(G_z)| = 3 |S|,
```

so every nonzero binary-kernel support has even cardinality.

## 3. Kernel subsets are exactly unions of connected components

Let

```text
T subseteq S
```

and let `1_T` be its indicator vector.

### Lemma KCC-2

```text
1_T in ker_F2(A)
iff
T is a union of connected components of G_z.
```

### Proof

Consider a row that is inactive for `z`. It contains no element of `S`, hence no
element of `T`, and contributes parity zero automatically.

Now consider an active row. Its selected intersection with `S` is exactly the
two endpoints `u,v` of one edge of `G_z`. The parity equation for `1_T` on
this row is satisfied exactly when

```text
1_T(u) + 1_T(v) = 0 mod 2,
```

i.e. exactly when either both endpoints belong to `T` or neither does.

Thus membership in `T` must be constant along every edge of `G_z`, hence on
every connected component. Conversely any union of components satisfies every
active-row parity equation and therefore lies in the kernel. QED.

## 4. Exact circuit characterization

A binary-matroid circuit of the column matroid represented by `A` is the support
of an inclusion-minimal nonzero vector of `ker_F2(A)`.

### Theorem KCC-3

For every nonzero `z in ker_F2(A)`,

```text
supp(z) is a matroid circuit
iff
G_z is connected.
```

### Proof

By Lemma KCC-2, proper nonempty kernel supports contained in `S` are exactly the
proper nonempty unions of connected components of `G_z`.

If `G_z` is disconnected, one component is therefore a proper nonzero kernel
support, so `S` is not minimal.

If `G_z` is connected, the only unions of components are the empty set and all
of `S`, so no proper nonempty kernel support exists. Hence `S` is a circuit.
QED.

This specializes the general binary-matroid circuit decomposition to the cubic
incidence carrier and gives the components a concrete graph object.

## 5. Negative-circuit search loses its minimality layer

Fix a parity point

```text
A x = 1 mod 2
```

and define signed coordinate weights

```text
w_j(x)=1-2x_j in {-1,+1}.
```

For a kernel vector `z`, the affine Hamming augmentation charge is

```text
Delta_x(z)
= |x XOR z|-|x|
= sum_{j in supp(z)} w_j(x).
```

Let the connected components of `G_z` have vertex sets

```text
S_1,...,S_q.
```

By Lemma KCC-2 each `1_{S_i}` is a kernel vector; by Theorem KCC-3 each is a
circuit. The supports are disjoint, so

```text
Delta_x(z)
=
sum_i Delta_x(1_{S_i}).
```

Therefore:

### Theorem KCC-4 — negative circuit / negative kernel equivalence

```text
there exists a circuit c with Delta_x(c)<0
iff
there exists 0 != z in ker_F2(A) with Delta_x(z)<0.
```

The reverse implication is the new useful direction: if an arbitrary nonzero
kernel vector has negative charge, at least one connected contracted component
has negative charge and is automatically a circuit.

Thus the active augmentation primitive may be simplified from

```text
FIND A NEGATIVE MINIMAL DEPENDENCE
```

to

```text
FIND ANY NEGATIVE NONZERO BINARY-KERNEL VECTOR.
```

Circuit minimality can be recovered afterward in linear time in the support
incidence size by taking a negative connected component.

## 6. Why this is not ordinary shortest-cycle search

The contracted cubic graph `G_z` is **support dependent**. It is not a fixed
input graph whose cycles can be searched before `z` is known.

The unknown object is simultaneously:

1. the selected variable set `S`;
2. the set of active checks (those meeting `S` twice);
3. the cubic graph obtained after those checks are contracted.

Therefore

```text
CIRCUIT -> CONNECTED CUBIC GRAPH AFTER SUPPORT SELECTION
```

does not imply

```text
GENERAL NEGATIVE CIRCUIT -> SHORTEST CYCLE IN ONE FIXED GRAPH.
```

That invalid shortcut would erase the codeword/even-set selection problem.

## 7. External anti-loop: sparse regularity is not enough

The classical minimum-distance / binary-matroid-girth problem is NP-hard
(Vardy, 1997), so arbitrary binary-matroid circuit optimization is not a free
polynomial donor.

A stronger 2026 source now reaches the sparse regular regime directly:

Chenyuan Jia, Qingqing Peng, Ke Liu, Guanghui Wang, Guiying Yan,
*On the Intractability of the Minimum Distance Problem for Regular LDPC Codes*,
arXiv:2606.23161v3 (2026).

They prove NP-completeness of the standard at-most-weight minimum-distance
problem for `(J,K)`-regular Tanner graphs for every fixed `J,K >= 3`, including
`(3,3)`.

This does **not** prove that JANUS's signed negative-kernel query with its exact
Exact-One syndrome is NP-hard under every extra JANUS promise. It does prove
that row/column degree three by itself cannot justify a polynomial circuit
algorithm.

## 8. Relation to E10

The E10 matroid stack already supplies polynomial terminals when the represented
binary matroid is graphic, cographic, regular, graft, even-cycle, even-cut, or
another source-certified graph-like island.

KCC-3 is compatible with those terminals but applies before such recognition.
It explains the residual geometrically without pretending that the full cubic
incidence matroid is graphic.

Hence the combined router is:

```text
cubic incidence A
    |
    +-- low rational nullity -> exact 2^k router; polynomial for k=O(log n)
    |
    +-- E10 recognized graph/regular island -> known circuit/T-join machinery
    |
    +-- otherwise high-nullity non-regular residual
            -> signed nonzero-kernel / connected-cubic-even-set frontier
```

## 9. New exact gate

Freeze:

```text
R5_E9_HIGH_NULLITY_SIGNED_EVEN_SET_QUOTIENT_GATE_V1
```

Input:

```text
A: row/column-weight-3 binary incidence matrix,
nu_Q(A)=omega(log n) along the surviving family,
x: parity point with Ax=1,
w_j=1-2x_j.
```

Target: deterministic polynomial construction of one of

1. a nonzero `z in ker_F2(A)` with `sum_{j:z_j=1} w_j < 0`;
2. a certificate that no such `z` exists;
3. an exact quotient/decomposition reducing the same signed-kernel problem with
   polynomial total size and witness reconstruction;
4. a source-proved terminal representation handled by E10 or another polynomial
   carrier.

A successful negative vector immediately yields a negative circuit by connected
component extraction and strictly lowers the affine-coset Hamming potential.
At most `n` successful augmentations are needed by the parent CAD theorem.

Forbidden:

- enumerate the superlogarithmic kernel;
- enumerate all connected cubic supports;
- treat support-dependent `G_z` as one pre-existing graph;
- call SAT, Exact-Cover, syndrome decoding, nearest-codeword, or minimum-distance
  as an oracle;
- use certificate verification without charging certificate discovery.

## 10. Finite replay

The checker exhaustively validates the structural equivalences on:

- `FANO_7`;
- the satisfiable cubic-linear `AFFINE_3X3` control.

For every nonzero kernel vector it checks:

```text
row intersections are 0/2,
contracted degree is exactly 3,
circuit iff connected,
components are kernel circuits,
charge is component-additive.
```

For every parity point it also checks:

```text
EXISTS_NEGATIVE_KERNEL
iff
EXISTS_NEGATIVE_CIRCUIT.
```

All enumeration is `OFFLINE_FALSIFIER_ONLY`.

## 11. Ceiling

```text
CUBIC KERNEL SUPPORT
-> CONTRACTED 3-REGULAR MULTIGRAPH
= PROVED

CIRCUIT
iff CONTRACTED GRAPH CONNECTED
= PROVED

NEGATIVE CIRCUIT EXISTS
iff NEGATIVE NONZERO KERNEL VECTOR EXISTS
= PROVED

CIRCUIT MINIMALITY AS SEARCH LAYER
= ELIMINATED

HIGH-NULLITY SIGNED KERNEL SYNTHESIS / ABSENCE CERTIFICATE
= OPEN

UNIVERSAL SAT / EXACT-ONE SOLVER
= OPEN

E8_D1
= EMPTY

P_VS_NP
= OPEN
```
