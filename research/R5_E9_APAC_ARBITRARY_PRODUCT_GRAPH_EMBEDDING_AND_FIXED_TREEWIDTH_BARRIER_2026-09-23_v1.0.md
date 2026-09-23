# R5 E9 — APAC Arbitrary Product-Graph Embedding / Fixed-Treewidth Barrier

Date: 2026-09-23

Authority:
`DERIVED_UNCONDITIONAL_SCOPED_BARRIER__GRAPH_WIDTH_DONORS_ONLY__NO_D1_PROMOTION`

Parents:

- `R5_E9_NONLOCAL_RANK1_JOINT_CONTRACTION_PIVOT_GATE_V1`
- `JANUS_KEYMASTER_TDD_CIRCUIT_TREEWIDTH_R2_DONORS_2026-09-23_v0.1`
- `R5_B1B1C5B2B2_E8_6I_KROM_DEFECT_PLANE_BRIDGE_2026-09-23_v1.0`

Checker:

`research/tools/r5_e9_apac_arbitrary_product_graph_embedding_checker.py`

## 1. Construction

Let `G=(V,E)` be an arbitrary finite simple graph.

For each edge `e={x,y}` introduce a fresh private Boolean variable `s_e` and one monotone clause

```text
C_e = (x OR y OR s_e).
```

Let

```text
F_G = AND_{e in E} C_e.
```

This is a valid polynomial-size 3CNF.

Apply the frozen exact three-sheet quadratic / rank-one normal form.

For each clause `(a OR b OR c)` the semantic quadratic expansion contains the three products

```text
ab, ac, bc.
```

Hence clause `C_e` creates in particular the semantic product `xy`.

After occurrence-copy equalities are contracted, the product interaction graph restricted to the original vertex set `V` contains exactly the edges of `G`.

The extra products `x s_e` and `y s_e` touch only the private vertex `s_e` and therefore do not create new edges among original vertices.

Thus:

```text
G
=
induced subgraph of the semantic product graph on V.
```

## 2. APAC does not remove these edge-products initially

For one frozen clause, keep the affine moment relaxation before imposing rank-one identities.

The local affine equations include

```text
p_uv = 0

p_ab + p_au + p_ac + p_av
+ p_bc + p_bv + p_cu + p_uv
=
1.
```

For each semantic product triple

```text
(a,b,p_ab),
(a,c,p_ac),
(b,c,p_bc),
```

the exact affine projection is the full cube

```text
F_2^3.
```

The checker enumerates the local affine solution set and verifies all eight assignments occur in each of these three projections.

Therefore these semantic products have APAC type

```text
FULL.
```

No local affine absorption removes them.

Consequently the unresolved FULL-product graph after the initial APAC closure still contains `G` on the original vertices.

## 3. Arbitrary graph theorem

### Theorem E9-APG1

For every finite simple graph `G`, there is a polynomial-size JANUS-generated APAC hard core whose unresolved FULL-product interaction graph contains `G` as an induced subgraph.

This is unconditional and constructive.

### Corollary

No universal theorem of the form

```text
"every JANUS APAC hard-core product graph belongs to C"
```

can hold for any proper hereditary graph class `C`.

In particular, the family has no fixed universal bound on:

- treewidth;
- any fixed excluded-minor condition;
- genus;
- rank-width, whenever used through a hereditary bounded-rank-width hypothesis.

For treewidth the statement is immediate by taking `G=K_t` for arbitrary `t`.

## 4. Circuit-treewidth consequence

The production Keymaster already has the exact mechanism

```text
XOR_AND_FIXED_BOOLEAN_CSP
->
BOOLEAN_XOR_AND_CHECK_CIRCUIT.
```

An AND identity

```text
p = x AND y
```

is checked by a constant-size subcircuit receiving both `x` and `y`.

In the underlying undirected circuit graph this creates a connected constant-size gadget joining `x` and `y`.

Contract that gadget to one edge.

For every product edge `xy` of `G`, this contraction recovers edge `xy`.

Therefore `G` is a minor of the checker circuit graph.

Treewidth is minor-monotone, hence

```text
tw(check circuit)
>=
tw(G).
```

Since `G` is arbitrary:

```text
JANUS XOR/AND CHECK CIRCUIT TREEWIDTH
=
UNBOUNDED.
```

## 5. TDD donor interaction

Capelli, Choi, Mengel, Muñoz and Van den Broeck,
*A Canonical Generalization of OBDD*, SAT 2026,
prove efficient TDD compilation for bounded-treewidth CNF/circuit inputs; for fixed treewidth this gives polynomial-size / polynomial-time compilation.

That remains a valid positive donor.

But the missing bridge

```text
BOOLEAN_XOR_AND_CHECK_CIRCUIT
->
BOOLEAN_CIRCUIT_TREEWIDTH_LE_FIXED_K
```

fails universally for every fixed `k`.

Hence bounded circuit treewidth / fixed-width TDD compilation is a strict positive island, not the universal contraction currency.

## 6. Consequence for the active contraction search

A universal nonlocal pivot cannot derive polynomiality merely by proving a fixed bound on the raw product/circuit graph width.

Any successful contraction theorem must instead:

1. actively reduce a width/connectivity measure under exact quotienting, or
2. exploit algebraic information not visible in the raw graph, or
3. produce a compact boundary representation whose size is not controlled by fixed raw graph width.

This sharply separates

```text
STATIC WIDTH ASSUMPTION
=
BLOCKED
```

from

```text
DYNAMIC EXACT CONTRACTION
WITH PROVED DECREASING POTENTIAL
=
OPEN.
```

## 7. Ceiling

```text
ARBITRARY PRODUCT GRAPH EMBEDDING
=
PROVED

INITIAL APAC SEMANTIC PRODUCTS
=
FULL

FIXED PRODUCT-GRAPH TREEWIDTH
=
BLOCKED

FIXED CIRCUIT TREEWIDTH / TDD BRIDGE
=
BLOCKED AS UNIVERSAL ROUTE

DYNAMIC NONLOCAL CONTRACTION
=
OPEN

D1
=
EMPTY

P_VS_NP
=
OPEN
```
