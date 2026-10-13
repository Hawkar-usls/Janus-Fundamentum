# R5 — All six published 20-vertex nontrivial snarks, 120 induced claw deletions, 1,800 physically exact pair interfaces

Scientific date: 2026-10-13 (Europe/Kyiv). PR #516 DRAFT.
Ultimate target unchanged: one sound, complete uniform bit-polynomial
`SolveLinearCubicXSAT` for ALL legal square/cubic/linear positive
Exact-One sources with source SAT witness or UNSAT. NOT CONSTRUCTED;
P versus NP remains OPEN.

## Source/provenance

Six **published** 20-vertex nontrivial snarks S1..S6 are taken from:
A. D. Forbes, *Snark Designs*, arXiv:1207.3032v2
https://oro.open.ac.uk/56584/1/1207.3032.pdf
section 4, pp. 14–15 of PDF (1-indexed print numbering),
full published 1-based EDGE SETS S1..S6.
These edge sets are transcribed into
`experiments/r5_universal_forbes_six_20_snarks_claw_exactone.py`
and normalized to 0-based vertex labels with independent assertions
on edges, degree, girth and source 3-edge-uncolourability.

This is distinct from an exhaustive list of ALL connected 20-vertex
cubic non-3-edge-colourable graphs. Forbes explicitly describes
these six as the **nontrivial** snarks. All simple 20-vertex class-II
graphs may include reducible / trivial cases, e.g. graphs with
short cycles or insufficient cyclic connectivity. Even the
exhaustiveness of the six nontrivial snarks is a literature theorem,
not inferred from a single J5 test.

## Exact source experiment

For each S_i (20 vertices, 30 edges), assert:
- simple 3-regular vertex degree 3, connected via cubic source;
- girth >=5;
- ZERO genuine proper 3-edge colourings by complete DFS over
  30 original source edges, no assumed/snark-only declaration.

For each of all 20 possible centre vertices v (all neighbours
pairwise nonadjacent by girth>=5):
1. Remove the induced centre-plus-three-neighbours claw
   `C_v={v} union N(v)` with all incident edges.
2. The 16-vertex remnant M_v has exactly 21 original edges and
   six physical semiedges, one each incident to six distinct
   remaining vertices. Assert all six physical port roots distinct
   (girth>=5).
3. Exhaust ALL complete proper 3-edge colourings of the remnant,
   with no colour normalization/anchoring and full semiedge colour
   tuples, deduplicating equal boundary physical signatures.
4. For each of 15 partitions of six physical ports into 3 pairs,
   construct EXACT projected Boolean relation
   `t_i=[same actual physical 3-edge colour at both ports]`.
   The target EXPOSED `ExactOne` is EXACTLY `{100,010,001}`.
5. Re-gluing the canonical STAR6 along the original claw's
   natural 3 paired port labels reconstructs the original
   non-colourable S_i, so these NATURAL pairings exclude 000;
   assert this source property independently for EACH of 120 claws.
6. For every possible `no_000` four-pattern interface
   `{100,010,001,111}`, record a real full six-port physical
   witness carrying 111 and check that direct pairwise colour
   equality allows the MATCH3 completion.

## CI-authoritative results

Workflow:
`.github/workflows/r5-forbes-six-20snarks-claws.yml`

[Run #38414354891](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38414354891)
SUCCESS on
`db46f575f2d93dc033984fd620797e1bf8f0ff94`.
The independently computed per-source values are:

| source | claws | interfaces | source full internal colourings across claws | distinct full physical boundary tuples (summed across claws) | bit relations |
|---|---:|---:|---:|---:|---|
| S1 (flower J5) | 20 | 300 | 5280 | 2160 | 270 full-five, 30 `{100,010,001,111}` |
| S2 | 20 | 300 | 3864 | 1530 | 268 full-five, 20 `{100,010,001,111}`, 12 more restricted patterns |
| S3 | 20 | 300 | 3294 | 1512 | 266 full-five, 25 `{100,010,001,111}`, 9 more restricted |
| S4 | 20 | 300 | 3720 | 1674 | 268 full-five, 23 `{100,010,001,111}`, 9 more restricted |
| S5 | 20 | 300 | 3780 | 1440 | 264 full-five, 20 `{100,010,001,111}`, 16 more restricted |
| S6 | 20 | 300 | 3768 | 1647 | 268 full-five, 23 `{100,010,001,111}`, 9 more restricted |
| TOTAL | **120** | **1800** | **23706** | **9963** | **ZERO ExactOne** |

Every S_i is source-uncolourable (not merely literature-labelled)
and every induced claw fragment admits a proper internal colouring.
The all-five Boolean relation is `{000,100,010,001,111}`.
A smaller proper subset of those five patterns cannot be inferred
to be `ExactOne` from its size alone. EXACT physical colours and
bit tuple support are enumerated for each of all 1,800 interfaces.
All source-specific relations are logged in GitHub CI.

Independent source construction control:
`experiments/r5_universal_j5_20vertex_snark_star_deletion_sixpole.py`,
CI [#38413695452](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38413695452)
SUCCESS. It constructs Isaacs' J5 directly using 5 stars,
one 5-cycle and one 10-cycle, independently of Forbes' 1-based
S1 edge list, and reproduces S1's 270 full-five / 30 no000
but 111-present / 0 exactone result.

## The useful all-size theorem still stands

For ANY cubic sixpole M:
`R(M)=EXACTONE`
iff ALL THREE original single-pair closures are SAT,
the physical 6-wire STAR6 closure is UNSAT (excludes 000),
and the direct all-3-pair MATCH3 completion is UNSAT (excludes 111).
Cubic colour parity already excludes exactly-two-true states.
This is a graph SAT/UNSAT semantic theorem, not a PC proof-degree
transfer or a construction.

If we reconstruct the STAR6 closure from a hypothetical simple
16-vertex sixpole, we get a simple 20-vertex cubic graph and a
legal Holyer positive Exact-One SCL90. The six published
20-vertex NONTRIVIAL snarks cannot serve as that H(M) in any
induced 4-vertex-star deletion / 3-pair interface.

**IMPORTANT** The 6-snarK result does NOT exclude a target
M with 16 vertices whose STAR closure H(M) is a different,
TRIVIAL 20-vertex class-II cubic graph (or any n>=18).
It also does not prove an unbounded native GF(3) PC degree
lower bound. Native source PC Boolean equality decoder degree<=4
was previously proved, but a global original-generator transfer
with uniform k,C is NOT CONSTRUCTED.

A separate unbounded 16-vertex *all interior graph* nauty
workflow #38408523974 was ACTIVE as of this checkpoint.
No claim is made on its outcome until its final CI state,
artifacts, and logs are verified.

## Epistemic gates

- FORBES_SIX_PUBLISHED_S20_CUBIC_NONCOLOURABLE = VERIFIED_EXACT_CI
- ALL_SIX_INDUCED_CLAW_REMNANTS_120 = EXHAUSTED_EXACT_CI
- ALL_1800_FULL_PHYSICAL_PAIRINGS_ONEHOT = ZERO_CI_CERTIFIED
- J5_INDEPENDENT_STAR_CONSTRUCTION = VERIFIED_CI
- ALL_TRIVIAL_20_VERTEX_NONCOLOURABLE_CUBICS = NOT_CLASSIFIED
- N16_UNRESTRICTED_OPEN_SIXPOLE = AWAITING_OTHER_CI
- GENUINE_EXPOSED_EXACTONE = NOT_CONSTRUCTED
- GLOBAL_SOURCE_GF3_PC_BACKSIM = NOT_CONSTRUCTED
- UNBOUNDED_NATIVE_GF3_PC_DEGREE = OPEN
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN
