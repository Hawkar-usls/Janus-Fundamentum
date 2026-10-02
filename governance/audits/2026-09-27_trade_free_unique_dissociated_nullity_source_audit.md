# Source audit — trade-free unique-model control / dissociated-nullity gate

Date: 2026-09-27

Decision: `PASS_SCOPED_GAP_CONFIRMED`

Authorized scope:
`R5_E9_DISSOCIATED_CUBIC_LINEAR_NULLITY_GATE_V1`

## Internal anti-loop

Checked the current PR #510 scientific tree before materialization. Existing
artifacts already cover:

- binary-kernel bipartite-support iff signed-lift theorem;
- difference-of-models implies a signed trade;
- signed-trade polynomial boundary projection;
- rational-nullity `2^k poly(n,L)` exact router;
- cubic-linear and girth-ten spectral rational-nullity bounds;
- affine-coset and rational-kernel Exact-One normal forms.

No existing artifact named or indexed as a `TRADE_FREE` or `UNIQUE_MODEL`
countercontrol was found in the current tree.

The new object is therefore not another trade donor. It is a falsifier of the
stronger, previously unproved route assumption

```text
SAT CUBIC-LINEAR EXACT-ONE => NONZERO SIGNED TRADE.
```

## External source audit

### Trades / null 3-hypergraphs

Kocay and Li study 3-hypergraphs with equal degree sequences and use
degree-preserving signed null 3-hypergraphs / trades. This binds the terminology
and prevents a novelty claim for the underlying signed-kernel object.

Source:
W. Kocay and P. C. Li, *On 3-Hypergraphs with Equal Degree Sequences*,
Ars Combinatoria 82, 145-157.

### Dissociated sets

A set is dissociated when it has no nontrivial relation with coefficients in
`{-1,0,1}`; equivalently its subset sums are pairwise distinct. General
`{0,1}^r` contains dissociated sets substantially larger than `r`, so
dissociation alone does not imply a near-full rational rank.

Source:
V. F. Lev and R. Yuster, *On the Size of Dissociated Bases*,
Electronic Journal of Combinatorics 18(1), P117 (2011),
DOI `10.37236/604`, arXiv:1005.0155.

### Uniform-hypergraph incidence rank

General characteristic-zero / mod-p incidence-rank theory for connected
uniform hypergraphs is prior art.

Source:
A. Bjoerner and J. Karlander, *The mod p Rank of Incidence Matrices for
Connected Uniform Hypergraphs*, European Journal of Combinatorics 14 (1993),
151-155, DOI `10.1006/eujc.1993.1021`.

## Collision result

```text
TRADES / NULL 3-HYPERGRAPHS
= SOURCE_BOUND PRIOR ART

DISSOCIATED SET TERMINOLOGY
= SOURCE_BOUND PRIOR ART

GENERAL UNIFORM-HYPERGRAPH INCIDENCE RANK
= SOURCE_BOUND PRIOR ART

EXACT 9x9 CONNECTED CUBIC-LINEAR
SAT + UNIQUE + TRADE-FREE CONTROL
= JANUS DERIVED FINITE COUNTERCONTROL
= NO NOVELTY CLAIM

TRADE-FREE CONNECTED CUBIC-LINEAR
NULLITY O(log n) THEOREM
= NOT FOUND IN CHECKED SOURCES
= OPEN GATE, NOT CLAIMED
```

The audit authorizes only the exact countercontrol and the formulation of the
new falsifiable nullity gate. It does not authorize a universal P=NP claim.

## Scientific boundary

```text
E8_D1 = EMPTY
P_VS_NP = OPEN
```
