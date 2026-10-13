# R5 — REAL GOOD-only physical connected double cover and nontrivial five-step Kempe holonomy

Date: 2026-10-14 (Kyiv).  
Research branch: research/r5-kempe-coupled-involutions-20261013.  
Executable: [r5_kempe_n14_goodonly_connected_double_cover.py](../experiments/r5_kempe_n14_goodonly_connected_double_cover.py).

## Why this is a stronger checkpoint

The previously constructed 8-vertex examples displayed actual nontrivial five-step closed-boundary Kempe loops, but also allowed forbidden equality-bit states 000 and 111. The previous 36-vertex boundary F22/Kempe square complex permitted an ABSTRACT connected two-sheet cover, with no physical GOOD-only realization known.

**New result:** a real simple connected cubic **14-vertex** sixpole with physical full colour relation contained in GOOD={100,010,001} realizes a **connected degree-two covering** of the compulsory 36-state boundary Kempe transition graph, with nontrivial five-step holonomy. Thus the obstruction "global GOOD-only automatically forces trivial Kempe monodromy" is FALSE, even for real cubic graphs with six DISTINCT physical semiedge roots. Any eventual universal argument must use properties stronger than GOOD-only+15 same-pair commuting-square identities+trivial monodromy.

**Critical limit:** the physical graph realizes ONLY truth bit 001, not all three GOOD bits. It is **NOT** the requested 108-state three-input Exact-One gadget. The full universal sixpole question and general JANUS polynomial solver remain OPEN.

## Full physical graph certificate

Let the cubic 6-pole have internal vertices 0 through 13 and the following **18 ordinary edges in canonical sorted order**:

    e00=(0,1),  e01=(0,2),   e02=(0,3),
    e03=(1,2),  e04=(2,6),   e05=(3,4),
    e06=(3,5),  e07=(4,5),   e08=(6,7),
    e09=(6,11), e10=(7,8),   e11=(7,12),
    e12=(8,13), e13=(9,11),  e14=(9,12),
    e15=(10,12),e16=(10,13), e17=(11,13).

The ordered physical dangling semiedge roots are

    (1,4,5,8,9,10).

They are six **distinct** vertices. Under the ordered logical equality pairs

    ((port0,port5),(port1,port2),(port3,port4)),

the entire physical three-edge-colouring boundary relation consists of exactly **36 distinct** physical tuples, and every one has equality bit **001**.

The graph is simple (18 different unordered ordinary edges), connected, and cubic when semiedges are counted. It is obtained by joining the 6-vertex HETERO_TWO fourpole and the 8-vertex PETERSEN_MINUS_ADJACENT_TWO_ISO fourpole by one ordinary edge (2,6).

## Theorem (finite physical 2-sheet Kempe covering)

Independently enumerate every internal proper 3-edge-colouring by depth-first search with adjacent-edge colour conflicts forbidden. Given any complete assignment, the missing colour at each one-semiedge root uniquely determines its physical external port colour. The **entire** exhaustive list has 72 complete proper colourings. Partitioned by exact ordered physical six-port colour tuple, the 72 entries form **36 fibres of size exactly two**.

From the earlier parity and Kempe matching lemma, at each allowed physical tuple and unordered two-colour pair, the number of GOOD-safe endpoint perfect matchings is either one or five. Use **only** cases with UNIQUE GOOD-safe matching; any true GOOD-only physical colouring must realize that unique matching.

The resulting 36-boundary-state transition graph has 72 undirected base edges. For each of the 72 complete proper colourings, compute *actual internal (a,b) alternating path components on the SAME physical graph* and switch one component at a time. The machine-independent exact checks assert:

1. The real pairings coincide with the uniquely forced GOOD-safe boundary pairings.
2. For every one of the 72 base edges, each of its two source-fibre colourings has exactly one uniquely determined genuine path-flip lift. Every flip is self-inverse on full edge-colour assignments.
3. The full lift is a graph with exactly 72 vertices and 144 undirected forced-path edges, and it has **ONE connected component of size 72**.
4. All **15 compulsory same-colour path-commutation squares** on the 36-state base lift to genuine commuting squares of the **complete internal** colouring: switching two disjoint paths in either order yields the identical fourth corner on both sheets.

Therefore this is an ACTUAL genuine two-sheeted graph covering, and its monodromy on the 2-element fibre has nontrivial image C2. It is not merely an abstract matching or hypothetical cover.

## Shortest genuine nontrivial closed-boundary path: length FIVE

An independent breadth-first shortest-path computation in the connected 72-vertex physical Kempe graph finds that for **EVERY one of the 36 external port tuples**, the two different complete internal colourings over that tuple are connected by a shortest forced-path sequence of **exactly five** switches.

One explicit all-physical witness begins with

    six physical port colours:
    (1,1,0,2,2,0),

and has the following 18 internal edge colours in the canonical edge order above:

    BEFORE:
    (0,1,2,2,0,0,1,2,1,2,0,2,1,1,0,1,2,0)

Apply these five ACTUAL Kempe-path switches, where the second column identifies the colour pair and the third the actual two physical semiedge endpoint indices:

    step  colour pair   physical path endpoints  boundary AFTER
     1     (0,1)             (0,5)              (0,1,0,2,2,1)
     2     (0,1)             (1,2)              (0,0,1,2,2,1)
     3     (1,2)             (2,5)              (0,0,2,2,2,2)
     4     (0,1)             (0,1)              (1,1,2,2,2,2)
     5     (0,2)             (2,5)              (1,1,0,2,2,0)

Every intermediate physical sixport tuple still has truth bit 001 relative to ((0,5),(1,2),(3,4)). The final physical tuple is exactly the initial tuple; the complete internal colouring is instead

    AFTER:
    (0,1,2,2,0,0,1,2,2,1,1,0,0,0,1,2,1,2).

Ten of the eighteen ordinary edge colours have changed. The entire five-step path is replayed from the SAME physical graph and checked to be fully proper after each path flip. The remaining 35 port fibres likewise have a nontrivial five-step loop.

## Scientific interpretation

This construction proves a clear physical POSSIBILITY, not an impossibility:

    A physically realizable GOOD-only sixpole MAY have
    exactly one nonempty bit fibre and nontrivial C2 monodromy.

Consequently no universal proof may assert either that GOOD-only alone implies three nonempty truth bits or that physical joint three-colour matching geometry alone forces all good-only Kempe monodromies to be trivial. The genuine full three-bit 108-state gadget is still entirely unresolved.

Next decisive research gate: whether all three 36-state physical fibres can coexist in one connected simple cubic sixpole without ANY forbidden tuple, with compatible internal cross-colour path updates. Merely gluing or taking the abstract disjoint union of three one-bit witnesses is NOT enough; a genuine connected cubic graph and full physical colour census are required.

This remains a specialised gadget research result. The universal polynomial native SolveLinearCubicXSAT is NOT CONSTRUCTED; P versus NP is OPEN.

CI provenance: source committed, verification workflow wired separately; do not claim CI SUCCESS until a completed run is independently observed.
