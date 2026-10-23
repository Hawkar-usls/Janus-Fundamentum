# BABEL-31 — fully automatic bounded-frontier factor-graph SAT/#SAT dynamic programming

**2026-10-23 — research-only stacked on BABEL-30 Draft PR #556, head \`567450a8acce3d90244db755df97ab92bef2ed4e\`.** This is a standard finite-domain separator DP applied to the exact-one incidence graph, not a claim of historical mathematical novelty or universal polynomial-time SAT. No TRUMP v3.23 scientific authority or mainline change.

## Why BABEL-30 needed this successor

BABEL-30 restores components after ONE incidence exchange and passes a two-state equality message. BABEL-29 proves two incidence swaps can create new solutions from punctured assignments that violate two original rows; composing separate two-state single-swap filters is invalid. On the certified connected SCL54 double-swap fixture BABEL-30 consequently returns \`UNKNOWN_NOT_ADMITTED\`. BABEL-31 bypasses row-restoration and instead represents **every actual crossing row-variable incidence** by a Boolean boundary port. Multiple edited rows and simultaneous imports are treated exactly, without presuming original-component SAT.

## 1. General all-n incidence-graph decomposition theorem

Let F be ANY legal positive Exact-One 3-SAT system (in particular any legal square cubic linear SCL). Its factor graph G is bipartite: clause vertices r, variable vertices v, one incidence edge e=(r,v) for each original occurrence.

A **certificate of admitted decomposition** is a binary tree of disjoint vertex sets, with root all vertices, leaves at most W vertices, and EACH subtree S having an incidence boundary

    ∂S = { e=(r,v) : exactly one endpoint belongs to S }

of at most B edges. Every internal node is the disjoint union S=A ⊔ C of its two children, and their edges and vertex sets are independently checkable against the original graph. The total number of leaf nodes is ≤2n (each contains at least one factor-graph vertex); each leaf has at most W internal vertices and ≤B boundary edges.

For each subtree S define a table T_S mapping a bit vector indexed by its ordered boundary edges ∂S to a nonnegative INTEGER count, plus one representative witness for every positive entry. An entry counts the assignments to all variable vertices within S, with each boundary edge e carrying a fixed port bit, such that **every clause vertex within S** satisfies exact-one. For e=(r,v) with r∈S,v∉S the bit is the externally supplied value of variable v; for r∉S,v∈S the bit must equal the assigned value of the internal variable v.

- **Leaf:** enumerate assignments of its at-most-W variable vertices plus one independent outside-variable port bit for each boundary incidence with row inside S. Therefore at most W+B Boolean symbols. Enforce every original clause whose row node lies in S, produce exact boundary signature and internal-variable witness. This costs O(2^(W+B) poly(W+B)) or less by full exact-one DPLL.
- **Merge:** the common boundary-edge indices of A and C are precisely their crossing edges, and every such edge must carry the SAME bit in both child tables. Join on these equalities, multiply counts, and project to ∂S. For every parent signature τ,

    T_S(τ) = sum_(α,β compatible and restrict to τ) T_A(α) T_C(β).

  Representative witnesses concatenate disjoint internal-variable assignments; no witness is claimed for a zero count.

**Exactness proof (all n, both directions):** Every global assignment induces one bit per cut incidence and a unique pair of child boundary signatures; child row clauses and bit equalities are necessary. Conversely, matching child table witnesses assign disjoint variable vertex sets and each cut incidence has equal bits at row and variable endpoints; every original row in A or C is therefore exactly satisfied. This is a bijection at the level of assignment sets, so the recurrence computes **#SAT** exactly, not just satisfiability. Induction to root (∂root=empty) proves the final count. If positive, its stored representative is a true full Boolean SAT model, and the solver **rechecks every original row** before reporting SAT. If zero, and leaves have been exhaustively enumerated and the complete tree verified, UNSAT is sound.

**Total bit-complexity, including all intermediate tables and model reconstruction:**

    T ≤ poly(n,W,B) * ( 2^(W+B) + 2^(2B) ),

given an already discovered admissible tree. Every count ≤2^n, so integers have O(n) bits; witnesses are n-bit masks. For FIXED W,B, this is polynomial. The claim is conditional on a successful decomposition; we do NOT assert that all SCL admit one.

## 2. Automatic discovery, WITHOUT source construction receipts

BABEL-31 uses an internal bounded edge-capacity maxflow procedure (unit incidence capacities) to test candidate separating pairs of anchored clause neighborhoods. Terminal anchor-cluster arcs have capacity >B; each successful mincut of capacity ≤B yields an exact vertex partition. The partition is accepted only after independent checks that:

1. both induced sides are connected and nonempty;
2. each side's boundary **against the ORIGINAL full input graph** is ≤B — not merely its interface with the sibling. This prevents hidden growth of ancestor boundary states;
3. every separated original incidence and ordered signature is explicitly accounted for.

The deterministic candidate policy uses a fixed number of row anchors and graph-distance-distant opposing anchors, with exact maxflow for each candidate; this runs in polynomial time, but is a **discovery heuristic, NOT an exhaustive search over all possible decompositions**. On failure to construct a verified bounded-frontier tree, the solver returns \`UNKNOWN_NOT_ADMITTED\` instead of a false SAT/UNSAT claim.

Discovery complexity is polynomial on **every** input for fixed B (even rejected inputs). The maxflow is capped at B+1 units and never relies on floating point. It is not a guarantee that every graph with SOME bounded decomposition will be recognized by this particular candidate policy.

The independent verifier tests seven seeded row/variable permutations of the hard SCL54 fixture to ensure raw physical input labels, block order and compiler provenance are not prerequisites to the test.

## 3. Frozen regression receipts

The self-contained exact checker \`experiments/babel31/bounded_frontier_factor_dp.py\` tests (B=4,W=54):

- BABEL-29 **connected SCL54 double cross-splice**: two SAT solutions, previously UNKNOWN in BABEL-30. Discovers a four-incidence-edge cut and produces a physical SAT model.
- BABEL-29 connected SCL54 double straight-splice: exactly one SAT model.
- BABEL-28 single-splice compatible/incompatible SCL54: counts 1 and 0 respectively.
- BABEL-27 connected chain C3/C5/C9/C20: counts 1 at n=81,135,243,540 with fully reconstructed models.
- Seven deterministic independent row and variable relabelings of the double cross-splice: each must return SAT count2.
- Local Fano7 UNSAT and Affine9 three-SAT controls (direct finite DPLL).

A separate \`experiments/babel31/independent_parity_oracle.py\` reconstructs the small controls without relying on producer labels, computes GF2 rank/kernel and counts SAT directly by all parity words when the kernel is small, and checks output witness against the original formula. For the large family, all-n dynamic programming induction is the theorem; no exponential full-cube oracle is claimed.

## 4. Required frontier

A finite W and B are NOT guaranteed for all connected SCL. The candidate maxflow policy can miss suitable decompositions. High-width systems may require exponentially many interface signatures. No theorem here bounds total state history for arbitrary connected inputs, or constructs a different universal exact carrier.

\`\`\`
BABEL31_BOUNDARY_TABLE_SEMANTIC_BIJECTION = PROVED_ALL_N
BABEL31_EXACT_INTEGER_COUNT_AND_WITNESS_ON_ADMITTED_DECOMPOSITIONS = PROVED_ALL_N
BABEL31_AUTOMATIC_CUT_DISCOVERY = POLYNOMIAL_SOUND_NOT_UNIVERSALLY_COMPLETE
BABEL31_BOUNDED_W_B_SUBCLASS_IN_P = PROVED
BABEL31_BABEL29_DOUBLE_SPLICE_UNKNOWN = TARGETED_FOR_CI_VERIFICATION
BABEL31_ARBITRARY_CONNECTED_SCL_BOUNDED_DECOMPOSITION = NOT_PROVED
BABEL31_UNIVERSAL_SolveLinearCubicXSAT = NOT_PROVED
P_VS_NP = OPEN
\`\`\`

No scientific result shall be promoted until exact-head independent CI PASS.


## 5. Full proof-carrying exact boundary receipts: separately replayed

The solver now emits a typed JSON-compatible \`BABEL31/EXACT-BOUNDARY-TABLE-TREE/v1\` receipt with the exact original factor-graph vertex subset and ordered boundary edge IDs of EVERY tree node, plus an exact integer count and physical representative assignment for EACH positive boundary signature. A merge node carries both child receipts and its projected table. For fixed B every table contains at most 2^B entries; the full receipt size including explicit vertex sets at each node is polynomial (a conservative O(n^2+ n 2^B * n) bits bound suffices).

An independent verifier, \`experiments/babel31/independent_receipt_replay.py\`, takes ONLY the original incidence rows, the claimed full table receipt and final result. It does **not** call the cut finder, the producer's variable-first Exact-One DPLL or its table join. It verifies each subtree partition and its boundary against the ORIGINAL incidence graph. To reconstruct leaf tables, it instead branches on which of the three literals in each owned clause is the UNIQUE true literal, enforcing equality for shared local variables. It then independently sums the counts of every leaf boundary signature. Every internal merge is checked by an independently implemented integer product-and-sum over matching edge-port bits. It verifies that each representative model obeys every original row owned by the node, with boundary port values substituted, and verifies the final physical SAT assignment against all original clauses.

**Certificate completeness caveat:** A positive SAT witness alone proves SAT. For an UNSAT receipt, the independent full enumeration of each leaf and verification of EVERY merge is what establishes complete zero counting; absence of a witness without those checks would be insufficient. The verifier's row-choice search is bounded by \`3^W 2^(W+B)\` in the deliberately conservative worst case, hence polynomial for fixed W,B and independent of the full input's 2^n possibilities. This verification cost must be included in any end-to-end proof-carrier claim.

### Exact-head CI evidence

On HEAD \`6c8bc2fa170bf8370048341c8152fed64ac5c65e\`:
- [GitHub Actions pull-request run #39944259643](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39944259643): **COMPLETED SUCCESS**.
- [GitHub Actions push run #39944255232](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39944255232): **COMPLETED SUCCESS**.
- The independent checker recomputes full GF2 parity counts on small SCL controls and independently verifies EVERY complete boundary-table receipt, including connected SCL540.
- BABEL29 double-cross SCL54 changes from BABEL30 \`UNKNOWN\` to **SAT count2**; double-straight has SAT count1. Original single-splice UNSAT control count0. Seven label permutations pass. A forced frontier0 nonadmission remains \`UNKNOWN_NOT_ADMITTED\`.
- Large t-chain cases are not exhaustively enumerated over GF2; their counts instead carry a verified complete bounded-frontier decomposition, exhaustive leaf counts and exact integer composition. Their returned physical SAT models are independently replayed against all original rows.

\`\`\`
BABEL31_FULL_BOUNDARY_TABLE_RECEIPT = VERIFIED_EXACT
BABEL31_INDEPENDENT_REPLAY_OF_ALL_LEAF_AND_MERGE_TABLES = CI_PASS
BABEL31_UNSAT_COMPLETE_COUNT_ON_ADMITTED = PROOF_CARRYING_PASS
BABEL31_UNIVERSAL_SAT_COMPLETENESS = NOT_PROVED
P_VS_NP = OPEN
\`\`\`


## 6. Extension to a real SIX-edge / three-incidence-swap interface

The exact factor-graph recurrence holds at ANY certified finite frontier size B, not only B=4. A new frozen legal connected SCL54 control has **THREE** cross-splices between the same two original SCL27 regions: start from BABEL29's double-cross instance, then exchange original U row0 variable0 with the other U row0 variable0 (offset27). Both preserved partial models have zero at these added two literals. The resulting joined input has **exactly TWO SAT assignments**, confirmed independently by exhaustive GF2 enumeration (small control only).

At frontier budget B=6, the old radius-one source/sink anchor policy could prefer a trivial 4-vertex star separated by six edges, which did not lead to W=54 leaves. The candidate finder now **uses radius-two anchor neighborhoods whenever B>=6**; every successful cut is still checked against ALL original incidence edges, the full subtree frontier budget and the independent receipt checker. For the three-swap SCL54 it finds the intended six-edge 54+54 factor-graph split, computes exactly TWO assignments, returns a physical witness and produces an independently replayed full table certificate.

Three deterministic row-and-variable permutations of this control also pass at B=6. This is a useful increased admitted width, NOT a proof that arbitrary 6-edge-cut decompositions will always be discovered.

[GitHub Actions #39944817685](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/39944817685): SUCCESS on head \`2ef9b35e729b8ad4374dc6f0e32a4051c2fa66ec\` with independently computed full GF2 count, full tree-table proof receipt and physical SAT witness recheck.

\`\`\`
BABEL31_DOUBLE_SPLICE_B4_PREVIOUS_UNKNOWN = SAT_COUNT_2_VERIFIED
BABEL31_TRIPLE_SPLICE_B6_AUTOMATIC_ADMISSION = SAT_COUNT_2_VERIFIED
BABEL31_INDEPENDENT_RECEIPT_ON_ALL_ADMITTED_CONTROLS = PASS
BABEL31_UNIVERSAL_COMPLETENESS = OPEN
P_VS_NP = OPEN
\`\`\`
