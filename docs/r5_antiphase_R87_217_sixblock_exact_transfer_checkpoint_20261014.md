# R5 — Anti-phase two-channel transfer reduced to an exact 87-state sixpole signature

Date: 2026-10-14 (Europe/Kyiv). Branch `research/r5-kempe-coupled-involutions-20261013`.

**Standalone tools:** [full 217-isotype multigraph catalogue](../experiments/r5_sixblock_217_loopless_catalogue_for_antiphase.cpp); [exact physical R87 transfer and first-stage universal necessary filter](../experiments/r5_exactone_antiphase_mandatory_R87_217_envelope.py); [second-stage exact 11-physical-fourpole-class solver with SAT positive control](../experiments/r5_exactone_antiphase_R87_fixed_fourpole_class_csp.py).

## 1. Scientific question and result boundary

Starting with any connected, physically colourable cubic FOURPOLE `H` exposing two logical outer semiedges x,y and two linking semiedges a,b, we ask whether connecting `H` to a physical sixpole `R` can realize **exactly** the 108 parity-legal GOOD physical sixport tuples, with equality bits 100/010/001 and none forbidden.

Assume `x` and `y` belong to DIFFERENT logical pairs, and `H` has the actual physically realizable full fourport signature **{AABB,ABAB}** (the alternate {AABB,ABBA} is handled by exchanging x and y). This is the only nontrivial anti-phase 2+4 cut class surviving the earlier fourpole interface reduction; identity/swap alternatives can already be excluded by the sixblock full GOOD no-go.

**NEW EXACT THEOREM:** A full 108-state physical relation after composing `H` with the right sixpole `R` exists **IF AND ONLY IF** the ordered physical sixport signature of `R` equals a PARTICULAR **87-state set `R87`** defined explicitly below. This is a conditional exact RELATION IDENTITY: it does not itself construct a physical right sixpole realizing `R87`.

**NEW COMPLETE FIRST-STAGE NEGATIVE:** Across all 217 connected loopless six-fourpole/nine-join multigraph skeleton types, and all 15 choices of the two linking ports and 24 assignments of the remaining four right ports, **57,504 / 78,120** labelled port arrangements cannot possibly realize `R87`, even if different physical local orbit types are allowed to be selected independently for different target states. **114 / 217** skeleton isomorphism types are excluded for EVERY assignment of ports by this necessary filter. The remaining **20,616** placements (in 103 isomorphism types) are ***NOT*** proved SAT or UNSAT; they require consistent complete fourpole classes.

This constitutes substantive provable progress, **NOT a complete 217-skeleton class-coupling no-go**. We do not claim that a full physical Exact-One gadget has been found.

## 2. Exact anti-phase transfer law

Fix the left `H` fourport order `(x,y,a,b)`. Its complete correct proper three-edge-colour relation `{AABB,ABAB}` is given by:

- If `a≠b`, precisely `x=a,y=b`;
- If `a=b`, precisely `x=y≠a`, with either of the two remaining common colours permitted.

In the final sixpole, order the physical outer ports as `(x,u,y,v,w,z)`, with logical pairs `(x,u),(y,v),(w,z)`. In the right sixpole `R), whose TWO connection semiedges meet `H`, order its six physical ports as `(u,v,w,z,a,b)`.

Let `T108` denote the complete 108-state set of sixport colour assignments with all three colour counts even and exactly one of the three logical port pairs equal.

For a right sixport tuple `r=(u,v,w,z,a,b)`, define `F(r)` as the set of full final sixport tuples `(x,u,y,v,w,z)` for ALL `(x,y,a,b)` physically allowed in `H`.

Define

    R87 = { r in {0,1,2}^6 :
                r satisfies the sixport Klein-four parity law,
                F(r) is nonempty, and F(r) is a subset of T108 }.

Exhaustively enumerate ALL 729 possible right tuples and the 12 physically allowed `H` tuples. The exact result is:

| Property | Integer |
| --- | ---: |
| Physically safe right tuples | **87** |
| Right tuples with a=b | 21 |
| Right tuples with a≠b | 66 |
| Physical S3 colour-permutation orbits of R87 | 15 |
| Union of all F(r) with r in R87 | Exactly all 108 T108 tuples |
| Total cardinality of these F(r) sets | 108 |
| Full final tuples with more than one right origin | **0** |

Because EVERY one of the 108 `T108` tuples has EXACTLY ONE right origin, **all** 87 safe right tuples are necessary: omitting even one makes at least one of the 108 GOOD tuples unavailable. Conversely adding any other physically admissible right tuple produces at least one forbidden final tuple. Hence composition with this H gives all GOOD and no BAD **IF AND ONLY IF** the right sixpole's complete physical ordered port relation is EXACTLY R87.

This avoids the earlier ineffective strategy of demanding that the right remainder itself realize full GOOD under some pairing. `R87` is a genuinely different exact sixport relation and cannot be replaced by a mere Boolean truth support target.

## 3. Isomorphism-complete sixblock loopless multigraph catalogue

Delete the degree-two anti-phase H constituent from a seven-fourpole / eleven-join connected loopless multigraph. If this deletion leaves a connected right remainder (true whenever the whole skeleton is 2-edge-connected), it has exactly six fourpole constituents and nine ordinary interblock links, allowing parallel joins, and exposes six physical semiedges.

The independent C++ catalogue generator enumerates all labelled 9-link multisets among C(6,2)=15 distinct block pairs with degree ≤4 and connectedness, retaining parallel edges. It identifies isomorphism types under all six-block label permutations:

    110,170 connected labelled edge multisets
    217 distinct unlabelled loopless multigraph skeletons.

The exported representative list is deterministic (lexicographic canonical multiplicity encoding) and is fed as data to BOTH Python checkers, so the exact sample skeleton indices are reproducible.

For each skeleton, assign the TWO right linking ports `a,b` to any distinct positions of its SIX physical semiedges (15 choices), and map the other four external physical semiedges to `u,v,w,z` in ALL 24 orders. There are `217×15×24=78,120` port arrangements. This even covers some assignments not extendable to the original sevenblock degree restrictions, which is safe for an impossibility filter.

## 4. Complete first-stage physical SAFE-orbit envelope

For each right skeleton and for EACH assignment of all `3^9=19,683` physical colours to its nine linking edges, independently determine every compatible local FOURPOLE parity pattern `AAAA,AABB,ABAB,ABBA`. Group by six-vector of these local orbit IDs, recording its COMPLETE **729-bit** sixport outer-colour support.

For any proposed `R87` target, call a six-local-orbit vector SAFE only if its **complete** external sixport support lies inside the desired 87-state set. A physically realizable connected cubic fourpole may have one of the proven eleven entire two-to-four-orbit boundary signatures. Any composite exactly realizing R87 may only enable SAFE local six-orbit vectors. Therefore a NECESSARY condition is that the union of the external supports of **all** individually SAFE local six-orbit vectors covers all 87 physical states of R87.

This test is deliberately **overpermissive**: it lets the orbit set of an individual constituent fourpole vary independently between different boundary states, which a real constituent cannot do. Hence an *excluded* placement is definitely impossible, but a placement passing this test is not automatically achievable.

The independently executed exact audit and deterministic committed regression confirm:

| Necessary-filter result | Count |
| --- | ---: |
| Skeleton types | 217 |
| Attachment and ordering checks | **78,120** |
| Impossible even under maximally permissive safe envelope | **57,504** |
| Pass necessary envelope, requires class consistency check | **20,616** |
| Skeletons impossible for all 360 placements | **114** |
| Skeletons passing the envelope for all 360 placements | 24 |

A total of 103 skeleton types have at least one not-yet-excluded placement. These raw placements have port relabeling redundancies; they are counts of checked assignments, not physical nonisomorphic gadget counts.

## 5. Second-stage actual 11-fourpole-class consistency

The companion exact Python solver fixes each right constituent to ONE of the 11 legitimate connected physical fourpole signature classes. For every local six-orbit vector, it records whether the full sixport support contains a forbidden state. For each six-tuple of chosen physical signature masks it requires:

1. There is **NO** locally compatible forbidden six-orbit vector.
2. The compatible SAFE vectors together cover each of the **15 S3 orbit classes** of the required R87 relation, equivalent to all 87 states because every class is global-colour-name symmetric.

It searches all possible choices of the six masks, applying sound monotone early pruning whenever some required physical orbit has lost all possible SAFE witness vectors. This is a COMPLETE SAT/UNSAT decision for ONE fixed (skeleton,cut,port assignment) case, and has an independent positive synthetic SAT fixture.

A finite exact second-stage regression verifies the following genuinely nontrivial first-stage survivor configurations are nevertheless UNSAT:

| Canonical right skeleton ID | Cut positions | Other-port assignment | Leaf configurations checked | Physical fixed-class result |
| ---: | --- | --- | ---: | --- |
| 51 | (0,2) | (0,1,2,3) | 4,140 | UNSAT |
| 52 | (0,2) | (0,1,2,3) | 17,424 | UNSAT |
| 100 | (0,2) | (0,1,2,3) | 17,409 | UNSAT |
| 200 | (0,2) | (0,1,2,3) | 18,339 | UNSAT |

In each sample zero fixed-class assignments survive without forbidden proper colourings after meeting every required R87 orbit. A separate independent SciPy/HiGHS integer model reproduced UNSAT for these representative cases, but the SciPy optimization outputs are supplementary; the committed pure-Python exhaustive mask verifier is the reproducibility anchor.

**Crucial:** These four fully checked placements do not discharge the other 20,612 necessary-filter survivors. A full-architecture UNSAT declaration requires checking the entire remaining fixed-mask CSP after symmetry reduction, producing complete per-orbit counters, or constructing a positive legally physical right sixpole and final H composition.

## 6. The next decisive check

Use the frozen R87 15-orbit exact target (rather than good/bad-only truth bits) with the 217 atlas, apply within-block semiedge permutation and full block-multigraph automorphism symmetries, then perform exact **fixed 11-class** compatibility for all remaining physically distinct port placements. If SAT, choose concrete representative fourpoles from the published 11-class physical catalogue, construct a single connected simple cubic sixpole with six distinct roots, glue the anti-phase H, and FULLY enumerate every internal proper edge-colouring to check the required **108** external tuples and **ZERO** forbidden ones. If UNSAT, emit complete replayable proof counters and exact grammar boundary.

**Epistemic state:** Right R87 mathematically necessary/sufficient for the anti-phase join: PROVED. Complete first-stage all-217 envelope: VERIFIED (57,504 placements and 114 isotypes impossible). Fixed-class four sample UNSAT: VERIFIED. All remaining sixblock 217 fixed-class placements: **OPEN**. Full threebit cubic physical Exact-One gadget: OPEN. Native polynomial-time `SolveLinearCubicXSAT`: NOT CONSTRUCTED. `P) vs `NP`: OPEN.

Provenance: exact Python calculations and independent C++ sixblock generator executed in the current research session; all three source files, this checkpoint and CI entry committed to research branch. A completed successful GitHub Actions CI result is **not independently verified**.
