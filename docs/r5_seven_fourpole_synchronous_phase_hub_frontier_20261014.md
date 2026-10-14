# R5 — Seven-fourpole synchronous phase hub: four high-connectivity skeletons

Date: 2026-10-14 (Kyiv). Research branch: research/r5-kempe-coupled-involutions-20261013.

**Reproducer:** [r5_exactone_seven_fourpole_synchronous_hub_frontier.py](../experiments/r5_exactone_seven_fourpole_synchronous_hub_frontier.py). Formal phase law: [r5_synchronous_phase_lock_exactone_fourbody_checkpoint_20261014.md](r5_synchronous_phase_lock_exactone_fourbody_checkpoint_20261014.md).

## Why the central hub is different from previous unsuccessful grammars

Seven genuine connected cubic fourpoles joined through exactly eleven edges leave six physical outer semiedges. If the interblock skeleton is SIMPLE and **3-edge-connected**, its total degree is 22 and every block has degree at least 3, so exactly one block has interblock degree 4 and the other six have degree 3. The unique degree-four block has no external physical semiedge and acts as a possible common FOUR-wire synchronization hub. Each of the other six blocks exposes one physical port.

This is a DISCOVERY CONSTRUCTION inspired by coupled phase synchronization, not a claim of a new physical law. All checks rely exclusively on proper 3-edge-colouring and the Klein-four conservation equation.

## Exact exhaustive skeleton census

Independently enumerate all C(21,11)=352,716 simple labelled 7-vertex / 11-edge skeletons. Exactly **5,670** have the mandatory ordinary degree sequence `(3,3,3,3,3,3,4)`. Those 5,670 split exhaustively into **four** nonisomorphic 3-edge-connected skeletons, with labelled permutation orbit sizes

    2520, 1260, 1260, 630.

Every candidate passes the explicit minimum-edge-cut >=3 test; all four representatives are hard-coded as explicit ordinary edge lists in the standalone verifier. The graph-isomorphism completeness is checked by generating the full orbit of each representative under 7! vertex label permutations and proving the four orbits are disjoint with union size 5,670. No external graph atlas or statistical assumption is required.

## Exact Klein-four phase interface data

For each of the four skeletons independently enumerate **all 3^11=177,147 colour assignments** of its ordinary interblock edges. For a terminal 3-interface block, the missing single external port colour is uniquely fixed as the xor of the three nonzero Klein-four interface colours, and the assignment is discarded if this xor is zero. For the internal 4-interface hub, its four interface colours must xor to zero. The remaining local ordered 4-port pattern must belong to one of AAAA/AABB/ABAB/ABBA. Group every proper choice by the seven local orbit IDs, and record its exact 729-bit external colour support.

| High-connectivity skeleton ID | Local orbit patterns | Proper interblock colour assignments |
| ---: | ---: | ---: |
| 0 | 1,328 | 10,479 |
| 1 | 1,400 | 10,371 |
| 2 | 1,379 | 10,413 |
| 3 | 1,272 | 10,551 |

The exact orbit records are valid for arbitrary internal sizes of their fourpole blocks, as long as each block's full ordered colour relation is from the proved 11-class fourpole atlas.

## Exploratory synchronous-selector screening — NO proof of nonexistence

Sample with deterministic random seed 20261014 exactly **500** independent 11-class assignments for each of all **15 logical pairings** for each of the four skeletons (30,000 sampled class/pairing combinations). Every sampled assignment's COMPLETE external 3-colour relation is computed EXACTLY from the precomputed orbit records; only selection of assignments is heuristic.

Score = number of forbidden physically possible external tuples + 4 times (108 minus number of allowed GOOD tuples). The best sampled candidates on skeleton IDs 0,1,2,3 score **51,42,45,42**, respectively. Each sampled best covers **all 108 allowed** external states but also produces respectively **51,42,45,42 forbidden** states. These are actual exact evaluations of selected abstract fourpole-class compositions, NOT evidence that no better seven-block class assignment or full 108-state physical graph exists.

**No full three-bit exact-one sixpole is constructed or excluded** by the sample. This seven-block grammar has 11^7 possibilities per pairing; the current finite sampled checks do NOT exhaust them.

## Next strong mathematical gate

Replace heuristic sampling with a formal SAT/UNSAT certificate over seven 4-bit orbit inclusion masks, nonlinear BAD witness clauses and three simultaneously realisable GOOD witnesses. If SAT, build a single genuine cubic physical seven-block multipole from physical 11-class representatives, ensure the six distinct physical roots and no forbidden proper 3-edge-colourings, then independently enumerate all 108 outer physical tuples. If UNSAT, produce a checkable proof of uncolourability of the grammar (not an informal search timeout).

The general Exact-One 108-state cubic sixpole remains OPEN. The verified n28 bridgeless GOOD-only two-bit seed remains intact. General deterministic polynomial SolveLinearCubicXSAT is NOT CONSTRUCTED; P vs NP remains OPEN. CI for these new files remains UNVERIFIED pending actual completed GitHub Actions run.
