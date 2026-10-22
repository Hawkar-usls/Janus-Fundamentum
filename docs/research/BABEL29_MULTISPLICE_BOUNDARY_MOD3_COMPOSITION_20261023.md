# BABEL-29 — exact all-r multi-splice boundary transfer, mod-3 conservation and a NEW connected SAT control

**23 October 2026.** This is a research-only successor to BABEL-28, PR #554, head \`97d99a6856e7b3fc0d893d6aa16466fe663bae58\`. No changes to \`main\`; TRUMP v3.23 authority is not modified. Scope is an **exact conditional composition theorem**, not a general polynomial SAT algorithm or a novel complexity-class resolution. This is a standard constraint-relation dynamic programming construction specialized to SCL; historical priority is NOT claimed.

## Frozen provenance and scope

Mandatory context anchor: \`START_HERE_TRUMP_CONTEXT.md\`; \`registry/TRUMP_CURRENT_STATE_2026-09-16_v3.23.json\` blob \`70e8b78fedd05bedb2e2324846d83c6fceea434d\`; v3.23 manifest overlay blob \`72af54233ebb2427894192c9904e179ece6c30ed\` [if source checksum differs, use the actual existing manifest blob; this text is NOT an authority pointer]. Earlier BABEL-28 proved a **two-state** rule for exactly ONE incidence exchange on each side, using redundancy of a single removed row. It does not authorize coordinatewise equality of interface bits for two or more exchanges.

## 1. General all-r exact boundary transfer theorem

Let L,R be any vertex-disjoint positive Exact-One systems on disjoint original Boolean variable sets, with disjoint selected rows

    r_1,...,r_r of L,    s_1,...,s_r of R,

and an occurrence a_i∈r_i and b_i∈s_i for each i. Remove a_i from r_i and b_i from s_i and replace them by b_i and a_i respectively, preserving the row index of each modified row. (The incidence splice is one-to-one and all selected rows are distinct within their respective side.) Check that the resulting incidence structure is legal square/3regular/linear if that property is needed; the logical counting identity below holds whenever the operation is defined even if a structural restriction fails.

For a Boolean assignment x_L satisfying **all unmodified rows of L**, put

    a_i=x_L(a_i) ∈ {0,1},
    l_i=sum_(j∈r_i\{a_i}) x_L(j) ∈ {0,1,2},
    beta_i=1-l_i.

The import requirement beta_i must be a Boolean bit to permit satisfaction of new row r_i. Thus punctured assignments with any l_i=2 are discarded. Define the EXACT boundary table (nonnegative integer entries)

    T_L(a,b) := # { x_L : all unmodified L rows have Exact-One,
                              x_L(a_i)=a_i for all i,
                              1-l_i=b_i∈{0,1} for all i }.

Define T_R(b,a) analogously, with b_i exported from R and a_i its desired imported bits. Then the entire joined system J has an **exact, bijective disjoint partition** by interface signatures:

    SAT(J) = disjoint union_(a,b∈{0,1}^r)
             [ P_L(a,b) × P_R(b,a) ],

and its number of models is

    #SAT(J) = sum_(a,b) T_L(a,b) * T_R(b,a).             (1)

No completeness assumptions on the punctured components are needed; both sides may be SAT or UNSAT in their ORIGINAL unpunctured form. If each nonzero entry also carries one verified physical witness, the construction is explicit in both directions.

**All-n proof**: any joined SAT model restricts to assignments satisfying all untouched rows, and each swapped row enforces beta_i=b_i on L and alpha_i=a_i on R. Hence restrictions belong to precisely one table entry on each side. Conversely any selected pair of table assignments satisfies every unmodified row and, from beta_i=b_i and alpha_i=a_i, every modified row. The map that joins assignments is inverse to restriction and is injective, so (1) is exact. Nothing exponential is hidden in this semantic equality; HOWEVER discovering all table entries can be NP-hard.

**Complexity**: a table has ≤4^r entries (a,b each r bits). Constructing the join/count from already *certified* tables requires O(4^r poly(|input|+receipt_bytes)) bit time (the count integers are ≤2^n). For fixed r, and for r=O(log n) when **all available interface tables have polynomial descriptions and can be produced in polynomial time**, the join is polynomial. There is NO claim that all arbitrary connected SCL can be recursively decomposed with globally polynomial boundary widths or polynomial local table construction. Carrying many ancestor boundaries may multiply states exponentially; account for TOTAL interface history.

## 2. New all-n mod-3 conservation theorem

Assume now that L and R each are SQUARE, 3-regular Exact-One systems, and n_L and n_R are divisible by3. Take any table-admitted local partial assignment of L, satisfying every unmodified row; the total count over ORIGINAL rows equals 3|x_L|, but the removed row r_i contains one export bit a_i and two retained bits l_i=1-b_i. Thus

    3|x_L|
       = (n_L-r) + sum_i (l_i+a_i)
       = n_L + sum_i(a_i-b_i).

As n_L≡0 mod3, **every nonzero T_L(a,b)** must obey

    |a|_1 - |b|_1 ≡ 0 (mod3).                           (2)

Likewise T_R(b,a) satisfies the same condition with opposite sign. This is a necessary filter before any table multiplication. It is NOT sufficient for an arbitrary punctured assignment to exist.

There are exactly

    N_r = (4^r + 2)/3

Boolean interface pairs (a,b) passing (2), for each integer r>=1. Proof via the cube-root-of-unity filter \`(1/3)sum_(j=0)^2 (1+ω^j)^r(1+ω^{-j})^r\`; \`|(1+ω)|^2=1\`. Equivalently, an elementary 3-residue walk recurrence yields the same count. So the universal necessary mod3 interface budget is **2, 6, 22, 86, ...** for r=1,2,3,4.

- At r=1, \`|a|-|b|∈{-1,0,1}\`, so (2) forces a=b and exactly two possibilities. BABEL-28's two-state identity is recovered exactly. The single-row redundancy lemma also forces original satisfaction separately.
- At r=2, \`|a|-|b|∈[-2,2]\`, so (2) forces \`|a|=|b|\`, which allows **six**, not merely two or four, compatible pairs. Crucially **a=(1,0), b=(0,1)** is permitted: opposite defects can compensate. Therefore the single-swap equality must NOT be imposed coordinatewise when two rows are punctured.

## 3. A FROZEN connected SCL54 where the missing six-state behavior is REAL

Take two disjoint copies of the existing BABEL-24 connected legal SCL27 with SHA256

    9c4fbe64849c319f927583646d7a6d71ced4c1b9cfefec05c0446cdefbf2b9ed.

Each original has EXACTLY ONE SAT model, true variable indices (relative to its component)

    (2,3,7,9,13,17,19,23,24).

On left L choose **two distinct modified rows** r=(11,22) and exported variables a=(22,25). On right R select modified rows s=(22,11), with relative exports b=(25,22). Perform the two cross swaps (global coordinates of R are offset+27):

    L row11: variable22  <->  R row22: variable25
    L row22: variable25  <->  R row11: variable22.

**Theorem for this exact frozen fixture.** The resulting system is connected, legal square/3-uniform/3-regular/linear SCL54, with d=6 and **EXACTLY TWO** SAT solutions, not one. The first is the concatenated old unique models. The second consists of two physical copies of the punctured **alternative** assignment with one indices

    (2,3,7,9,13,17,18,22,26).

The second assignment satisfies all 25 untouched rows of U but violates the two ORIGINAL removed rows with original row counts (2,0). Thus it was not a true SAT model of either original U! But the cross swaps swap the two interface deficits and make every joined row Exact-One.

Explicit nonzero punctured boundary table entries, in the **row order specified above**:

    T_L(00,00)=1   original U model
    T_L(10,01)=1   alternative U punctured model
    T_R(00,00)=1   original U model
    T_R(01,10)=1   alternative U punctured model

and ALL other entries vanish. The exact composition formula (1) gives

    #SAT(J) = 1*1 + 1*1 = 2.

This is a **minimal semantic counterexample** to naïvely composing two single-edge BABEL-28 filters without allowing a temporary two-row defect exchange. It does not contradict any established BABEL-28 theorem; the earlier theorem explicitly applied to r=1.

The independent checker exhaustively enumerates **the 27-variable punctured systems by full DPLL coverage with propagation**, recomputes both four-index interface boundary tables, validates the SCL54 incidence and inverse restores U×U, computes the exact binary parity kernel d=6, and enumerates all 64 parity words for an entirely independent check of the two actual joined solutions. The producer and checker do not use existing BABEL source code.

## 4. Programmatic verifier and remaining frontier

\`experiments/babel29/multisplice_boundary_transfer.py\` replays r1 and r2, including both matching and mismatching r1 controls from BABEL-28, the r2 connected 2-model witness, the mod3 N_r state counts for r1..4, and a second r2 straight-routing control. Exact rational/integer/Boolean only, no Monte Carlo, no modular-only inference.

\`\`\`
BABEL29_ALL_R_EXACT_TABLE_COMPOSITION = PROVED
BABEL29_ALL_R_MOD3_BALANCE = PROVED (n_i divisible by3)
BABEL29_ADMISSIBLE_STATE_COUNT = (4^r+2)/3
BABEL29_CONNECTED_SCL54_TWO_SAT_CROSS_DEFECT = PROVED_FINITE_EXACT
BABEL29_ARBITRARY_CONNECTED_SCL_POLY_SEPARATOR_DECOMPOSITION = OPEN
BABEL29_POLY_DISCOVERY_OF_ALL_LOCAL_TABLES = OPEN
UNIVERSAL_SolveLinearCubicXSAT = NOT_PROVED
P_VS_NP = OPEN
\`\`\`

BABEL-20 has 20/20 **POSITIVE** exact rational FULL-M2 certificates despite noncover labels for its restricted transfer route (PR #543), so \`UNSAT_FOURIER_M2_COMPLETENESS=OPEN\`, not DISPROVED. This status correction is carried forward to prevent confusion.
