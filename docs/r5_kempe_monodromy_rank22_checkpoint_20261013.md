# R5 checkpoint — Kempe monodromy F37 -> F22

Date: 2026-10-13. Branch: `research/r5-kempe-coupled-involutions-20261013`.

## Objective and scope

The target is the *all-size* obstruction (or actual realization) for a properly 3-edge-colourable cubic **sixpole** with three ordered boundary-pair equality bits taking precisely `100,010,001`. This is NOT a solution of the general NP-complete square/cubic/linear SCL problem.

Prerequisite: [Saturation-or-Forbidden and uniform fibres](r5_kempe_sixpole_saturation_or_forbidden_proof_20261013.md).

New executable: [Monodromy square rank22 audit](../experiments/r5_kempe_monodromy_square_rank22.py).

## Theorem A — canonical boundary complex

For each fixed allowed truth bit `b`, consider the forced two-colour Kempe graph `Gamma_b` with one vertex per physical even-parity boundary tuple having bit b. An edge is one **single alternating path** flip whose matching is the UNIQUE matching compatible with all independent path flips staying in the allowed bit set.

Direct exhaustive finite computation of the 108 physical allowed tuples and 324 tuple/colour-pair decisions gives:
* 252 UNIQUE-compatible decisions and 72 ambiguous decisions;
* exactly 432 directed forced transitions on all three bits;
* per bit: 36 vertices, 72 undirected edges, connected, `beta_1=72-36+1=37`;
* exactly 15 distinct canonical same-colour-pair commutation squares; 12 have two `222` and two `42` states, three consist of four `222` states;
* the 15 squares are simple and pairwise **edge-disjoint**, using 60 edges, with 12 edges remaining untouched; the square boundary vectors have F2-rank 15.

**Universal physical identity:** In any proper colouring of an actual cubic sixpole, the two alternating paths of the same colour pair underlying such a square are distinct connected components of the a/b subgraph. Switching one does not change the other; hence their flips commute **on the full set of internal edge colours**, not merely on the six exposed ports. Under the global hypothesis `Bits(M) subset {100,010,001}`, the forced boundary pairing is realized in every full colouring, so each such square lifts to a *closed* four-move loop on each full-colouring fibre.

Attach a 2-cell along each of these 15 squares. Because no graph edge belongs to two distinct 2-cells, there is a free 1-cell in every square and elementary collapses eliminate all 15 2-cells together with 15 edges. The resulting connected graph has 36 vertices and 57 edges. Therefore the 2-complex is homotopy equivalent to a wedge of **22 circles**:

```
pi1(Gamma_b with 15 compulsory square faces) = F_22.
```

This conclusion is stronger than an F2 homology rank count; it identifies the nonabelian fundamental group. Consequently any honest boundary-fibre monodromy of a global GOOD-only sixpole factors through an abstract representation

```
rho_b: F_22 -> Sym(m_b).
```

The internal-colouring fibre dimension `m_b` is unknown and need not be polynomial in graph size.

## Theorem B — explicit symmetric nontrivial abstract control

Classify the 72 undirected forced edges of each `Gamma_b` by its **full bit-preserving boundary symmetry group**: all 6 permutations of colours; independent swaps inside each of the three port pairs; and permutation of the two *unequal* bit-pairs (the pair marked 1 is held fixed). This group has 6 * 2^3 * 2 = **96** elements.

The edge-orbit sizes are `12,12,24,24`. Exactly one 12-edge orbit is **disjoint from every compulsory square**, hence assigning `Z2` voltage 1 to all its edges and voltage 0 to the remaining 60 produces an invariant voltage assignment. Every square has voltage sum zero, yet the associated two-sheet covering graph is **connected**: there is a closed boundary walk of length five with voltage one. A complete finite 72-vertex lift verifies this connectivity for all three bits.

Thus parity, forced path pairings, independent same-colour commutations, **and the full colour-plus-port boundary symmetry** still admit nontrivial abstract monodromy. This is a definitive NO-GO for proving trivial monodromy or universal nonexistence from only those axioms.

**Critical:** This is an ABSTRACT covering graph, NOT a realizable cubic multipole. No claim is made that its sheets can be identified with internal proper 3-edge-colourings. Additional necessary equations involving paths of DISTINCT colour pairs and a single shared set of cubic internal vertices are required.

## Next physical realizability gate

For a candidate sixpole choose three edge-colour matchings `P_0,P_1,P_2` on the SAME set of internal vertices plus the six dangling terminals. At each internal vertex there must be exactly one edge/semiedge of each colour. The pairwise unions `P_a union P_b` must induce the forced boundary terminal pairings, **and** after any forced path swap all three matchings must update consistently on the same graph.

Develop an exact *cross-colour path-holonomy verifier*:
1. explicitly store the involutions and physical edge incidence of one actual coloured graph;
2. lift each of the 15 commutation squares and check that internal colours return unchanged;
3. for independent closed boundary walks involving two or three different colour pairs, record the actual permutation of full-colouring fibres;
4. identify a new universal physical relation among these cross-colour loops, or produce an actual graph-level counterexample.

A monodromy argument is not complete until it proves an **additional forbidden physical relation** or constructively realizes the exact 108-state signature. The remaining 22 free generators must NOT be casually assumed trivial.

## Provenance and epistemic status

Independently recomputed locally with exhaustive 108-state boundary enumeration, square enumeration and F2 rank; repo executable and its new Actions job are committed. **GitHub CI result is unverified unless an actual run conclusion is retrieved.**

Current scientific verdict:

* `SQUARE_COMMUTATION_15`: PROVED conditional on the global GOOD-only promise.
* `MONODROMY_F22`: PROVED necessary topological constraint.
* `SYMMETRIC_CONNECTED_Z2_COVER`: FINITE ABSTRACT COUNTERMODEL, **NOT** REAL SIXPOLE.
* `REALIZABILITY_EXACTONE_SIXPOLE`: OPEN.
* `ALL_N_EXACTONE_NO_GO`: OPEN.
* `NATIVE_PC_DEGREE_UNBOUNDED`: OPEN.
* `SolveLinearCubicXSAT`: NOT_CONSTRUCTED.
* `P_VS_NP`: OPEN.

Related independent literature: Fiol & Vilaltella (2015), *Some Results on the Structure of Multipoles in the Study of Snarks*, EJC 22(1) P1.45, https://doi.org/10.37236/3629. Goedgebeur & Ostergard (2022), *Switching 3-edge-colorings of cubic graphs*, Discrete Mathematics 345(9), doi:10.1016/j.disc.2022.112963. Existing edge-Kempe-equivalence results show different Kempe classes can occur in cubic graphs; they do not establish the required sixpole obstruction.
