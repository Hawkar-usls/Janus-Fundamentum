# R5 — All-size six-port Kempe saturation-or-forbidden theorem

Date: 2026-10-13.  
Repository branch: `research/r5-kempe-coupled-involutions-20261013`.  
Executable: [r5_kempe_sixpole_saturation_or_forbidden_gate.py](../experiments/r5_kempe_sixpole_saturation_or_forbidden_gate.py).

## Formal statement

Let M be a properly 3-edge-coloured cubic six-pole with six ordered physical dangling half-edges paired as (1,2), (3,4), (5,6). Colours are 0,1,2. For an ordered boundary tuple s write

`bit(s)=( [s1=s2], [s3=s4], [s5=s6] )`.

Let G={100,010,001}. The result does **not** require all colourings of M to remain in G.

**Constructive dichotomy.** Given an actual full proper 3-edge-colouring of M with boundary state s and bit(s) in G, an algorithm linear in the size of M produces either:

1. a proper 3-edge-colouring with boundary bit outside G, reachable from the starting colouring through **at most six** Kempe-path interchanges; or
2. 36 explicit proper 3-edge-colourings whose ordered boundary tuples are precisely the 36 parity-legal physical tuples with bit(s), each reachable from the input witness by **at most four** Kempe-path interchanges.

Outcome (2) is NOT a certificate that there are no forbidden states elsewhere.

**Corollary — saturation and fibre-uniformity.** If the **global** boundary relation of M satisfies Bits(M) subset G, then for every realised b in G:
* exactly all 36 physical boundary tuples of bit b appear;
* the number `m_b` of full proper edge-colourings extending any one of these tuples is independent of the chosen tuple;
* the total number of proper full edge-colourings is `36 * sum_{b in Bits(M)} m_b`.

In particular a hypothetical exact open six-port Exact-One gadget must realise exactly 108 distinct physical boundary tuples and its total number of proper colourings is divisible by 36, with strictly positive `m_100,m_010,m_001`.

The theorem assumes a full colouring witness for the constructive algorithm. Finding such a witness for arbitrary input, testing the global GOOD-only property, and solving native SCL remain unresolved.

## Finite matching lemma — independently recomputed

The cubic parity lemma restricts any 6-port boundary to three even colour multiplicities. Exactly 108 of the 183 parity-legal six-port tuples have a bit in G: 36 of multiplicity type 2+2+2 and 72 of type 4+2.

For each tuple s and each unordered colour pair (a,b), consider all perfect matchings on the ports bearing either a or b; these are the possible terminal pairings of (a,b)-Kempe paths in a full proper edge-colouring. Call a matching GOOD-compatible if flipping **any subset** of its paired paths leaves the resulting tuple with bit in G. This is the correct condition because disjoint bicolour paths may all be independently interchanged.

There are 324 choices (s,{a,b}):
* At each of the 36 balanced 2+2+2 states all three colour pairs have **one** GOOD-compatible terminal matching.
* At each of the 72 unbalanced 4+2 states, the two colour pairs involving the **absent** third colour have **one** GOOD-compatible matching; the pair of two colours actually present has **five** GOOD-compatible matchings, and must NOT be assumed uniquely forced.

Thus 252 of 324 choices force a unique matching. Use **only** those 252 choices. Switching a single path of a forced matching produces 432 directed moves on the 108 boundary states. An exact finite audit establishes:
* every move is reversible and its matching is again unique at the destination for the same colour pair;
* the moves form three separate connected 36-state components, one per bit;
* each component has exact graph diameter 4 (36 balanced roots have eccentricity 3; 72 unbalanced roots have eccentricity 4);
* every path of length <=4 in this graph is liftable to an actual sequence of Kempe-path interchanges **unless** an actual observed terminal matching deviates from the unique GOOD-compatible matching.

This finite combinatorial lemma is verified in executable source with exhaustive enumeration of all 108 states and 324 cases; no graph-order-dependent enumeration is involved.

## Proof of the constructive dichotomy

Fix input colouring c at boundary state s, bit b in G. Using the finite 108-state graph, compute shortest routes from s to all 36 tuples of bit b. Every such route has length <=4.

To lift one route, inspect the actual (a,b)-Kempe path pairing for the colour pair specified by the next forced transition:

* **Correct pairing:** interchange the unique path with the route's specified endpoints. The resulting full colouring is proper and has the next prescribed boundary tuple. Continue.
* **Incorrect pairing:** because the finite matching lemma found exactly ONE matching for which *all subset switches* are GOOD, there is a subset of the actual terminal paths (at most three paths) whose interchanges produce a forbidden boundary tuple. Exhaustively inspect at most 2^3 subsets and output the corresponding full proper colouring. If this failure happens at the i-th intended transition, there were at most i-1<=3 previous switches, so total at most 3+3=6.

All terminal-path components are disjoint and switching one of them does not change the other (a,b)-components, so the selected subset can be switched sequentially. The algorithm performs O(1) graph traversals of size O(|V|+|E|); total runtime is linear in the full six-pole size. The other branch returns all 36 witnesses within at most four flips.

## Proof of fibre-uniformity

Assume no full colouring has forbidden bit. Every state-colour-pair that is unique in the finite table must be realised by its prescribed actual terminal matching in **every** full colouring with that boundary state, otherwise switching a subset produces a forbidden colouring, contradiction.

For any forced transition s --(a,b;u,v)--> t, flip the unique (a,b)-Kempe path joining ports u,v. This defines a map from full-colouring fibre `C_s` to `C_t`. The same path is preserved as a connected bicoloured component by colour interchange. The finite lemma establishes that the same terminal pairing is also forced at t, so the flip is a two-sided inverse for **every** colouring of `C_t`. It is therefore a bijection.

All 36 vertices of a given bit are connected by these reversible forced moves; hence their fibres are bijective and all have common cardinality m_b. This proves the saturation claim and the counting identity.

## Provenance and limitations

Independent local combinatorial evaluation established 108 GOOD states, 252 forced matching choices, 432 forced directed moves, three connected components of 36, and eccentricity histogram {3:36,4:72}. On the pre-existing properly coloured simple connected eight-vertex sixpole, a forbidden `000` witness is obtained after three Kempe-path flips.

This proof concerns colourability witnesses, boundary relations and Kempe moves. It does **not** establish absence of any exact-one gadget, Polynomial Calculus degree lower bounds, or a general polynomial algorithm for `SolveLinearCubicXSAT`. P vs NP remains OPEN.

**CI provenance:** never mark a GitHub Actions PASS until the run/job logs are independently verified; script was committed and wired into `.github/workflows/r5-fourcut-colour-atlas.yml`, with CI conclusion unverified at authorship.
