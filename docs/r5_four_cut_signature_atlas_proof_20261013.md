# R5 / Four-cut signature atlas — proof and reproducibility checkpoint

**Date:** 2026-10-13
**Scope:** 3-edge-colourable cubic 4-poles, 6 physical external ports, native SCL context.
**Scientific status:** semantic/gluing replacement theorem PROVED (using elementary parity + 11 finite templates); native PC degree-1 back-simulation NOT ESTABLISHED; universal open Exact-One nonexistence OPEN; \`SolveLinearCubicXSAT\` NOT CONSTRUCTED; P vs NP OPEN.

## Definitions

A cubic 4-pole has four labelled semiedges; all vertices have three total incident ordinary edges/semiedges. A *proper 3-edge-colouring* assigns colours 0,1,2 so every vertex sees each colour exactly once. The ordered boundary relation \`Col4(B)\` is the **set**, not multiset, of all four-tuples of semiedge colours induced by proper colourings. We allow distinct semiedges to meet the same old vertex. \`Col6(M)\` similarly uses all six *ordered physical* outer semiedges. No colour anchoring is imposed.

### Lemma 1 — four boundary orbit types

By the parity lemma, every colour occurs an even number of times among four semiedges. Up to global colour relabelling, only these four patterns are possible:

\`1111\`, \`1122\`, \`1212\`, \`1221\`.

A type with four equal port colours contains 3 physical tuples; each two-pair type contains 6. Each non-empty colour set is a union of complete S3 colour relabelling orbits.

### Lemma 2 — at least two orbit types

Fix a proper colouring of a colourable 4-pole. If the ports are all colour A, select absent colour B and switch one A/B Kempe path ending at two A ports: the result has two A and two B terminals, hence changes orbit type.

Otherwise the boundary is \`AABB\` after a port permutation. In the A/B subgraph, the four exposed terminals pair into two alternating paths. Switching the path containing the first A terminal either joins the other A (creating \`BBBB\`) or joins one B (creating one of the two *different* pair patterns). In every case, at least one distinct orbit type appears.

Thus \`2 <= |Col4(B)/S3| <= 4\` whenever B is colourable.

### Lemma 3 — eleven explicit representatives

There are at most \`C(4,2)+C(4,3)+C(4,4)=11\` possible sets of 2, 3 or 4 orbit types. All eleven are realized by permuting the ordered semiedges of these five **simple connected** templates (edge endpoints are 0-based, each listed port root gets one semiedge):

| Template | Internal vertices | Ordered roots | Realized orbit types |
| --- | ---: | --- | --- |
| FOUR_CYCLE_THREE_WITH_1111 | 4 | (0,1,2,3) | 1111,1122,1212 |
| SIX_VERTEX_HETERO_TWO | 6 | (1,2,4,5) | 1212,1221 |
| SIX_VERTEX_THREE_WITHOUT_1111 | 6 | (1,2,3,5) | 1122,1212,1221 |
| PETERSEN_MINUS_ADJACENT_TWO_ISO | 8 | (0,2,3,4) | 1111,1221 |
| EIGHT_VERTEX_ALL_FOUR | 8 | (0,1,2,3) | 1111,1122,1212,1221 |

Full ordinary edge lists, precise permutations, and machine checks are in [the executable atlas](../experiments/r5_universal_four_cut_11_signature_substitution.py). The first graph is a 4-cycle, and the fourth is the 4-pole obtained by deleting two adjacent vertices of the Petersen graph. Reordering the four labelled semiedges freely permutes the three distinct two-pair types while fixing \`1111\`. Thus the representatives cover three pairs containing \`1111\`, three pairs excluding it, three triples containing it, one triple excluding it, and the full set — all eleven subsets.

**Conclusion:** For every colourable cubic 4-pole B, some simple connected 4-pole B* with exactly four distinct semiedge roots and at most eight internal vertices satisfies \`Col4(B*)=Col4(B)\`.

### Theorem 4 — all-size port-free 4-cut semantic substitution

Let M be a connected simple cubic sixpole, and B a connected internal vertex block disjoint from M's six labelled semiedges, separated from the rest by exactly four ordinary edges. Assume B is properly 3-edge-colourable. Replace B and its incident four cut edges with the representative B* from Lemma 3, reconnecting to the same four **ordered** outside endpoints.

Then

\`Col6(M) = Col6(M[B -> B*])\`.

**Proof.** In every proper colouring of M, the ordered four interface colours lie in \`Col4(B)\`, and hence extend to B*. Conversely, every proper colouring of the quotient induces an interface tuple in \`Col4(B*)=Col4(B)\`, and therefore extends to B. The outside colouring and the six ordered outer semiedge colours remain unchanged in both directions. The new block is connected and simple, its vertices are fresh, and its four port roots are distinct. Consequently, the new sixpole stays connected and simple even when two old outside cut-edge endpoints coincide. All vertices remain cubic by construction. This proves exact **set equality**; internal colouring multiplicities are not asserted to match. □

### Corollary 5 — minimal Exact-One 6-poles exclude large internal 4-cuts

If a colourable sixpole M is minimum order in its exact \`100,010,001\` pair-equality signature class, it has no port-free connected four-edge-cut block with ten or more vertices. Indeed, substituting B* yields a strictly smaller sixpole with the identical six-port colour set. In particular, for an 18-vertex candidate with such a block, the quotient has at most 16 vertices, which is inside the separately finite-excluded range of CI [#38408523974](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38408523974). A hypothetical exact-one candidate is colourable by definition, so its internal blocks are colourable; the structural filter does not need to decide arbitrary block colourability.

The cut detector runs in \`O(m^4(n+m))\` by checking all 4-edge sets, deleting them, taking connected components, and retaining components free of the six external ports with all four deleted edges on their boundary. It does **not** colour the graph or claim to decide arbitrary SCL.

### Reproducible finite regression facts

* The 11 catalogue entries all glue into legal simple connected sixpoles.
* Replacing a 12-vertex 4-pole obtained by two diamond inflations with its 4-vertex core reduces an 18-vertex example to ten vertices, preserving all 87 six-port physical boundary states.
* In the existing constructed n=18 nested diamond/triangle example, the graph-only detector finds 5 distinct port-free 4-cuts, all with 10-vertex blocks. Each has a 6-vertex representative, giving a 14-vertex quotient. Independently enumerated physical signatures: 63 before and 63 after, exactly equal for each of the five cuts.

The new CI workflow is [R5 Kempe Coupled Involutions and Four-Cut Atlas](../.github/workflows/r5-fourcut-colour-atlas.yml). **Do not record CI PASS until its job conclusion has actually been checked.**

## Critical limitation

The theorem is **semantic**: the colour relation of a large 4-pole is one of eleven options, but computing which one for an arbitrary input is not shown polynomial-time. There is no generally constructed PC-degree-1 variable substitution to the smaller template and no polynomially bounded PC back-simulation. This result neither proves an all-size absence of exact-one sixpoles nor yields a uniform polynomial-time solver for NP-complete native SCL.

## Literature context

* [Kempe-closed colour sets in cubic poles — Midsummer Combinatorial Workshop](https://kam.mff.cuni.cz/kamserie/clanky/2009/s916.pdf), discussion pp. 52–55 of 6-pole colour sets and the realizability question.
* [Colour-open 4-poles, Electronic Journal of Combinatorics discussion](https://doczz.net/doc/4924868/this-pdf-file---the-electronic-journal-of-combinatorics), Section 3, 4-pole colouring types and Kempe restrictions.

**Next open theorem:** characterize the global compatibility of all three colour-class involutions in a single 6-pole; the abstract boundary-only Kempe model is insufficient. Search either for a real exact-one sixpole at n>=18 or for a universal realizability obstruction involving cross-colour path geometry.
