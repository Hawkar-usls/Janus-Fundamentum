# R5 — Synchronous phase locking as an exact Klein-four boundary law

**Date:** 2026-10-14 (Kyiv)  
**Research branch:** research/r5-kempe-coupled-involutions-20261013  
**Executable:** [r5_exactone_synchronous_phase_lock_rank1_gate.py](../experiments/r5_exactone_synchronous_phase_lock_rank1_gate.py).

## Epistemic boundary

"Синхронная физика" is used here as a **discovery analogy**: physical oscillator phase synchronization suggests testing shared phase differences and higher-order coupling. The formal claims below depend solely on finite graph theory and binary linear algebra, NOT on the existence of a new physical effect. This preserves the JANUS `DISCOVERY_PROVENANCE != PROOF_DEPENDENCY` rule.

In a properly coloured cubic graph, interpret physical 3-edge colours 0,1,2 as the three nonzero elements 01,10,11 of the Klein four vector space `F2^2`. This is the standard nowhere-zero flow / parity lemma, not a new physical theory. For six physical outer semiedges, fix the actual n28 logical port index pairs `A=(0,5), B=(1,4), C=(2,3)`.

## All-size theorem: Exact-One is a nonzero rank-one phase-lock condition

Write `d_A = code(c0) XOR code(c5)`, and likewise `d_B, d_C`. Summing Kirchhoff equations over every internal cubic vertex gives

    d_A XOR d_B XOR d_C = 0.

Each equality bit is 1 exactly when its corresponding d is zero. Over F2^2, `d_C = d_A XOR d_B`. If `d_A,d_B` are linearly independent, then `d_A,d_B,d_C` are the THREE distinct nonzero values, and the Boolean bits are 000. If both are zero then the bits are 111. Otherwise, the two vectors span a nonzero rank-one subspace, and exactly ONE of `d_A,d_B,d_C` is zero. This proves the identity

    Exact-One ⇔ rank_F2([d_A,d_B,d_C]) = 1
              ⇔ det_F2(d_A,d_B)=0 and (d_A,d_B)≠(0,0).

The determinant is `a0*b1 XOR a1*b0`, in binary coordinates. The second nonzero condition is ESSENTIAL: omitting it admits forbidden bit 111.

This is a *boundary recognition predicate*, NOT a constructive graph-realization theorem and NOT an algorithm to find a proper full internal colouring.

## Necessary four-body correlation: a strict projection theorem

There are exactly **183** ordered external three-colour tuples satisfying the cubic parity law (each colour appears an even number of times). Their Boolean equality bit histogram is

    100:36, 010:36, 001:36, 000:48, 111:27.

The exact `GOOD` relation has 108 tuples; 75 parity-legal tuples are forbidden.

For **EVERY** subset of physical port indices of size 1, 2, or 3, the coordinate projection of the 108-state GOOD relation is IDENTICAL to the corresponding coordinate projection of the entire 183-state parity relation. Therefore NO conjunction of purely local constraints on at most three of these six physical port coordinates, even together with global parity, can distinguish exact GOOD from the 75 forbidden parity-compatible tuples. Auxiliaries or hidden globally shared variables may realize effective four-body interactions, so they are NOT excluded by this lower-bound statement.

A single four-coordinate projection onto two complete logical pairs, e.g. the physical port indices `(0,5,1,4)`, DOES separate all 75 forbidden tuples when combined with cubic parity. That 4-port projected relation has **48** ordered colour-tuples; it is an exact realization-level specification of a potential four-body synchronization gate, NOT automatically the boundary relation of an isolated cubic FOURPOLE (an isolated fourpole itself obeys the four-semiedge parity constraint and cannot realize all 48).

## Precise phase characterization of the physical bridgeless n28 TWO-bit seed

The independently complete 39-ordinary-edge colouring enumeration of the real n28 bridgeless 6pole yields exactly 72 physical tuples, each with two proper full colouring extensions, and bits exactly 100:36,010:36. That relation is mathematically identical to the 183-state parity relation intersected with THREE low-arity boundary restrictions:

    c2 != c3,
    not all_distinct(c0,c2,c5),
    not all_distinct(c0,c3,c5).

The two triple conditions enforce synchronization of C's port colours against the A pair. Given `c2!=c3`, if A is unequal, both C colours must be those two A colours in opposite order, and parity forces B equal; if A is equal, parity and `c2!=c3` force B unequal. This proves an EXACT 72-state relation identity, **not** a unique presentation of the physical graph.

A real graph-cut witness explains the permanently missing bit 001: ordinary two-edge cut `{(7,21),(8,27)}` isolates the 10-vertex bridgefree B FOURPOLE with physical semiedge roots `(6,9,7,8)`, ordered as `(C_first,C_second,cut_first,cut_second)`. Its genuine ordered 4-port signature is exactly `{ABAB,ABBA}`, i.e. C's two physical colours ALWAYS differ. Kirchhoff on the fourpole relates the difference of C's two colours to that of the two connecting edge colours. No time synchronization or Kempe switching performed on the UNCHANGED graph can realize a boundary C-zero state: it is literally absent from the correct entire physical colouring support.

## Exact quantitative obstruction to phase unlock in fixed four-block K4-minus-edge wiring

Original fourpole signature class indices (11 classes in the proven R5 atlas, in combinations-of-four-orbits ordering) are A=4, B=5, C=3, D=3. The specific five connecting edges and six external port order are

    A[2]=C[1], A[3]=D[1],
    B[2]=C[2], B[3]=D[2], C[3]=D[3];
    outside=A[:2]+B[:2]+C[0]+D[0];
    logical physical pairs=((0,5),(1,4),(2,3)).

The existing B=5, with orbit classes {ABAB,ABBA}, has exactly GOOD bits 100/010, 36 each. Expanding B while holding A,C,D fixed has these exact COMPLETE physical relation histograms:

| B signature class | 100 | 010 | 001 | forbidden 000 | forbidden 111 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 original | 36 | 36 | 0 | 0 | 0 |
| 8 add AAAA | 36 | 36 | 18 | 0 | 9 |
| 9 add AABB | 36 | 36 | 18 | 0 | 18 |
| 10 add both | 36 | 36 | 18 | 0 | 27 |

Next, allow ALL FOUR constituent fourpoles to change among ALL 11 physically realizable full signatures, while keeping the exact K4-minus-edge wiring and logical pairs unchanged. An independently built exact S3-orbit relation engine groups the 3^11=177,147 joint assignments of five connector colours and six external colours into **92 distinct local orbit combinations**. It then checks all **11^4=14,641** fourpole class choices using 729-bit exact physical support masks.

Exactly **439** assignments realize all 108 GOOD sixport tuples. Among these the MINIMUM number of additional physically realizable forbidden tuples is **42**, attained exactly by two class assignments:

    (A,B,C,D)=(4,10,6,7) and (4,10,7,6).

Each has complete physical relation histogram `100:36,010:36,001:36,000:24,111:18` — 150 total external states. Thus for this FIXED fourblock wiring and logical pairing,

    all 108 GOOD states present => at least 42 forbidden physical states.

This is an exact lower bound over **all allowed internal fourpole sizes of this wiring**, not just small graph order. It does not exclude physical higher-width couplings, other block skeletons or an unreducible cubic 6pole.

## Physics literature and next lawful test

Higher-order oscillator Ising machines have been studied as heuristic optimizers for higher-order SAT penalties (e.g. *Efficient optimization with higher-order Ising machines*, Nature Communications 2023, https://www.nature.com/articles/s41467-023-41214-9). This is motivation for testing **four-body phase correlations**, not proof that an oscillator simulation implements cubic 3-edge-colouring correctly, has exact dynamics, or can decide an NP-complete input in polynomial time.

Next experiment: a physical FOUR-BODY synchronization hub in a seven-fourpole higher-connectivity coupling network or a nondecomposable sixpole; require a full proper 3-edge-colouring witness for every newly allowed physical state. The desired complete three-bit 108-state gadget is still OPEN, and universal polynomial SolveLinearCubicXSAT remains NOT CONSTRUCTED. P versus NP is OPEN.

## Provenance

The local independent exhaustive colouring of n28 was replayed in this conversation: **72 distinct physical states, 144 full proper colourings, 36 each bits 100/010**. Local GF4 / exact boundary-projection 729-tuple algebra and full 14,641-class fixed fourblock mask computations were separately replayed. Script committed on research branch; **independent GitHub Actions SUCCESS remains unverified**.