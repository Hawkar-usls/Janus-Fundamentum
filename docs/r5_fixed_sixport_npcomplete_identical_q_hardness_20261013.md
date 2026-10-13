# R5 — NP-complete fixed physical six-port entry at an IDENTICAL linear trace Q

Date: 2026-10-13.  
Research branch: research/r5-kempe-coupled-involutions-20261013.  
Executable: [r5_kempe_fixed_sixport_npcomplete_gadget_gate.py](../experiments/r5_kempe_fixed_sixport_npcomplete_gadget_gate.py).

**Main scientific verdict:** Computing even one specified admissible physical boundary value of a cubic sixpole's nonlinear edge-colouring signature is NP-complete. This remains true if ALL instances have exactly the same labelled six-edge Klein-four flow trace Q, equal to that of the bare six-cycle C6. The result is a hardness barrier, NOT a proof P≠NP and NOT a construction of a polynomial universal SCL solver.

## Theorem (fixed-six-port membership)

Fix six distinct ordered semiedges, paired (0,1),(2,3),(4,5), and the single predetermined physical colour tuple

    s* = (0,0,1,2,2,1),  bits(s*) = 100.

Define FIXED-SIXPOLE-COLOUR-MEMBERSHIP:
Input: a connected SIMPLE cubic sixpole M, each of whose six semiedges has a distinct root.
Question: is there a full proper 3-edge-colouring of M whose exact ordered six semiedge colours equal s*?

Then this problem is NP-COMPLETE, even restricted to sixpoles whose canonical marked six-edge linear trace Q_M is exactly the same labelled six-cycle as Q_C6.

### Reduction from cubic 3-edge-colourability

Holyer's 1981 theorem proves NP-completeness of deciding whether a cubic graph admits a proper 3-edge-colouring:
Ian Holyer, "The NP-Completeness of Edge-Coloring", SIAM Journal on Computing 10(4):718-720 (1981), https://doi.org/10.1137/0210055.

Let G=(V,E) be a connected simple cubic graph; choose in polynomial time an ordinary edge uv belonging to a cycle, so G-uv is connected (a connected cubic graph always has a cycle). Take a disjoint C6, with vertices 0..5, ordinary cycle edges e_i=(i,i+1 mod 6), plus one dangling **physical** semiedge at each vertex. Delete edge e_0=(0,1) from the cycle, delete uv from G, and insert ordinary edges u0, v1 between the two pieces. Call the resulting connected simple cubic sixpole M_G. The original six ordered semiedges at cycle vertices 0..5 are unchanged; M_G has |V(G)|+6 vertices and (3|V(M_G)|-6)/2 ordinary edges.

**Interface lemma.** In any proper 3-edge-colouring of M_G, the two connector edges u0 and v1 must have the same colour a. Proof: sum the vertex Kirchhoff equations over all vertices originally from G; each interior G-edge appears twice, so the xor over F2^2 of the two connector labels vanishes. All three colours map to distinct nonzero F2^2 values, hence both connectors have the same colour. This holds regardless of G-uv connectivity. The common colour may be reinstated on deleted edge uv, yielding a full proper edge-colouring of G.

**Pinned C6 lemma.** With external physical s*=(0,0,1,2,2,1), the C6-path fragment with its two connector colours equal a has exactly ONE proper colouring of its five remaining ordinary cycle edges, and it requires a=1. Index the five remaining cycle edges e1..e5 in cyclic order. The UNIQUE assignment is

    (e1,e2,e3,e4,e5)=(2,0,1,0,2);
    a=1.

This is certified by enumerating all 3*3^5=729 assignments. Equivalently, the complete six-cycle C6 with physical tuple s* has a unique full edge colouring with deleted e0 colour 1.

If G is 3-edge-colourable, relabel its three colours so deleted edge uv has colour 1, glue the unique C6-path assignment, and obtain a proper full colouring of M_G with physical tuple s*. Conversely, any such colouring of M_G restricts on G and closes back to a proper G-colouring. Therefore

    s* in Col6(M_G) <=> G admits a proper edge-3-colouring.

Checking a proposed full edge-colouring is polynomial. Holyer's NP-completeness transfers by the polynomial explicit reduction. Hence FIXED-SIXPOLE-COLOUR-MEMBERSHIP is NP-complete.

### Stronger all-or-nothing physical signature

The two-edge G-uv multipole has exactly these possibilities for its **two** physical connector colours:
* if G is properly 3-edge-colourable: exactly {(0,0),(1,1),(2,2)} (the parity lemma forces equality, and S3 colour relabelling gives all three);
* otherwise: the EMPTY relation.

Attaching this two-pole in place of the C6 cycle edge e0 therefore yields

    Col6(M_G) = Col6(C6) if G is 3-edge-colourable;
                EMPTY otherwise.

Independent finite colour enumeration finds exactly 63 **distinct ordered physical** boundary tuples for C6 (there are 66 full internal C6 3-edge-colourings, because some port tuples have multiple extensions).

**Counting refinement:** With s* pinned, the C6-path fragment has exactly one internal extension, and the connectors are forced colour 1. Thus

    #full_3EC(M_G | s*) = #full_3EC(G with uv coloured 1)
                       = #full_3EC(G) / 3.

The factor 1/3 follows from the free transitive S3 permutation of three colours on the colour of any fixed ordinary edge. This count equality is unconditional; do not assert a separate #P-completeness theorem without citing a suitable source.

### Same Q for every input, including NO instances

The six-edge trace construction from the previous R5 theorem splits each of the six physical C6 port-root vertices into two stubs joined by six marked edges, deletes these marked edges, and contracts the components of the remaining ordinary graph. Because chosen uv belongs to a cycle, the entire G-uv fragment remains connected, and serves as one replacement connection between the two stubs formerly joined by C6 edge 01. All five other C6 cycle edges are unchanged connections between marked port stubs.

Thus the contracted marked six-edge graph Q_M is literally the same labelled six-cycle Q_C6 for **every** input connected cubic G, irrespective of 3-edge-colourability. Consequently

    Q_M = Q_C6,   r_s(M)=r_s(C6) for ALL 729 port tuples s,

and the entire NP-complete yes/no signal exists strictly in the nonlinear nowhere-zero edge-colouring relation. Even deciding whether the sixpole colour set is EMPTY is NP-hard under fixed Q.

### Corollary: port-free 2-pole contraction needs an NP-hard side condition

The G-uv fragment is a connected port-free interior 2-pole of M_G, linked by exactly two ordinary edges. If G is colourable, replacing that fragment by one edge preserves the full ordered physical six-port signature. If G is NOT colourable, the fragment has EMPTY boundary relation and replacement creates the colourable C6, improperly changing UNSAT to SAT.

Thus the old universal 2-cut replacement theorem is correct **only under its explicit colourability premise**. There is no justified unconditional polynomial-time "shrink every 2-cut" preprocessing algorithm, unless it can decide the NP-complete 2-pole-colourability gate (in particular, if P=NP this barrier could be overcome).

The globally GOOD-only Exact-One-gadget minimality argument is *not contradicted* by this issue: under its hypothetical nonempty colour relation, every block in a realised full colouring is colourable. The no-go conjecture for irreducible 6poles remains OPEN.

## Finite reproducer

The standalone script implements the splice construction, independently enumerates all proper 3-edge-colourings of the source and pinned output and independently enumerates all *unfixed-port* physical tuples. It checks the exact trace Q agreement:

Source G        full 3EC(G)   G edge1  M pinned s*  |Col6(M)|  full 3EC(M)
K4                       6         2           2         63            132
Triangular prism         6         2           2         63            132
Cube Q3                 24         8           8         63            528
Petersen graph           0         0           0          0              0

All constructed M_G are connected and simple, have six **distinct** semiedge roots, and share the *same ordered six-edge* Q as C6. These controls cover nontrivial YES/NO behaviour; the NP-completeness follows from the **all-size reduction plus Holyer**, not from the four finite examples.

## Alignment with native square/cubic/linear SCL

The existing independent source-level bridge [r5_universal_cubic_edgecolor_direct_scl_bridge.py](../experiments/r5_universal_cubic_edgecolor_direct_scl_bridge.py) constructs, from any simple cubic G, variables x_(e,c) for each ordinary source edge e and colour c∈{0,1,2}. It uses one Exact-One row for each edge e over its three colours and one Exact-One row for each source vertex v and colour c over the three edges incident to v.

For N source vertices and M=3N/2 edges, the construction has 3M variables and M+3N=3M rows. Every row has exactly three positive variables; each variable occurs in exactly three rows (its edge row and both endpoint-colour rows); distinct rows share at most one variable because G is simple. These are exactly the native JANUS SCL promises: square incidence, cubic row and column degrees, and linear intersections. Full proper 3-edge-colourings of G correspond bijectively to SAT witnesses of this native SCL instance.

The new executable rechecks these three-degree/linearity constraints independently for each of the K4, prism, cube and Petersen controls, with respectively 18, 27, 36 and 45 native rows and columns. This does NOT map every sixpole to an arbitrary native SCL input by itself; it demonstrates that the same NP-hard SOURCE G feeds both legally promised constructions.

An abstract polynomial-time algorithm computing the **complete exact physical six-port colour support for arbitrary cubic sixpoles** is therefore equivalent (in decision power) to P=NP: its one pinned entry suffices to decide cubic 3-edge-colourability and hence SAT; conversely, P=NP allows 729 individual NP membership tests to compute the whole finite support polynomially. This is an equivalence of *hypothetical algorithms*, not an achieved algorithm.

## Open scientific gates and next action

- FIXED-SIXPOLE-SIGNATURE-ENTRY: NP-COMPLETE (polynomial reduction proved).
- FIXED-Q-CYCLE SIXPOLE membership: NP-COMPLETE (same proof).
- ALL-N EXACT-ONE SIXPOLE NO-GO: OPEN.
- Polynomial construction/compression of nonlinear physical signature for arbitrary internal cubic core: NOT CONSTRUCTED.
- Native PC-degree lower bound for LEGAL SCL: OPEN.
- Universal SolveLinearCubicXSAT: NOT CONSTRUCTED.
- P vs NP: OPEN.

**Next attack:** avoid assuming constant-size boundary support yields a polynomial algorithm. Try to find an exact structural identity for the specific GOOD-only Exact-One **promise**, or an actual gadget, that does NOT require solving arbitrary two-pole colourability. Such a result must be stronger than generic six-port tensor tabulation, now proved NP-hard even at an identical six-edge trace.

CI evidence: source and regression workflow committed; do not label CI success until a completed workflow job result is retrieved.
