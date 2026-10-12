# R5 — Connected SCL UNSAT with global n divisible by 3, unbounded girth, and matched SAT/UNSAT controls

Date: 2026-10-13 (Europe/Kyiv). Branch `research/r5-cubic-flow-smith-pair-20261011`; PR #516 remains DRAFT, main untouched.

## Absolute scientific contract

The goal is ONE uniform worst-case polynomial-bit-time, sound+complete `SolveLinearCubicXSAT` on EVERY original square, cubic, linear, monotone Exact-One source, returning ORIGINAL SAT witness or sound UNSAT. A compact Holant/signature encoding, a fixed special-source solver, and a restricted proof-system NO-GO do NOT meet the goal.

`SolveLinearCubicXSAT=NOT_CONSTRUCTED`; `P_VS_NP=OPEN`.

This checkpoint proves an explicit infinite adversarial family and certifies a same-size SAT/UNSAT pair. It refutes ONLY global n%3 plus fixed-length generalized-loop truncation, not all polynomial algorithms. The source is original SCL with the SAME 3-ones-per-row/column and C4-free legality; no partial pins or nonstandard clauses are assumed.

## 1. An exact universal boundary-charge congruence

Let F be ANY legal square, cubic, linear positive Exact-One source with m original rows and variables, choose one original Tanner incidence `row r -- variable v`, and cut that edge into independent dangling values:
- `a` is the source Exact-One row's external incoming value;
- `b=x_v` is the original variable node's external bit, still repeated on its other two source edges.

All other original source rows retain Exact-One and all other incidence connections retain Equality. For any valid open-block assignment, summing m original row equations gives

```
m = 3 Σ_(source original variables u) x_u - b + a.
Therefore a-b ≡ m (mod 3).
```

The formula is an EXACT original-source count, not a belief-propagation approximation, a probabilistic certificate or an assumed transfer function.

Because a,b∈{0,1}, when `m≡1 mod3` it forces `(a,b)=(1,0)`; when `m≡2 mod3`, it forces `(a,b)=(0,1)`. This is a NECESSARY condition, not always sufficient for an actual open assignment.

More generally, if k≥2 disjoint open SCL blocks of nonzero residues are cyclically joined `row_i→variable_(i+1)`, then `a_i=b_(i+1)` forces their residue sequence to alternate `1,2,1,2,...`. If the sequence is not alternating (e.g. three identical residues), the joined ORIGINAL LEGAL SCL is UNSAT, even when total `n=Σm_i` is divisible by3. Alternating residues only pass the arithmetic gate; open-block feasibility still needs proof.

This small finite boundary-charge algebra can detect these sources in polynomial time GIVEN their component decomposition. **It is not a universal polynomial SCL solver, and this family is not being presented as computationally hard for every possible algorithm.**

## 2. All-input source-valid cyclic three-copy construction

Start from a connected legal m-row/source-variable SCL F with m mod3 ∈{1,2} and bipartite original Tanner girth g≥6 (the last is true for all legal linear sources).

Take THREE vertex-disjoint copies, each of size m, choose the same original cut incidence `(r,v)` in each, delete the three cut edges, and replace each by a cyclic incidence `row_(r,i)→variable_(v,i+1 mod3)`.

SOURCE-LEGALITY:
- each source row loses exactly one old variable and gains exactly one new variable;
- each original variable node loses exactly one incident source row and gains exactly one;
- every original row/column still has degree 3, all original rows remain triples;
- there cannot be a C4 crossing the component interface, because each unordered pair of the three previously disjoint components has only one new cross edge and any inter-component cycle uses all THREE cross edges;
- graph is connected whenever the original Tanner is connected. **Every connected 3-regular bipartite graph is bridgeless:** if a Tanner edge were a bridge, considering one side with R row-nodes and C variable-nodes, incidence-degree counting would give \`3(R-C)=+1\` or \`-1\`, impossible over integers. Therefore removing the chosen incidence leaves each original Tanner copy connected, and the three cross incidences connect these copies in a cycle.

New size n=3m is ALWAYS divisible by3. Nonetheless each block's congruence forces all (a_i,b_i) identical as (1,0) OR (0,1), and the 3-cycle requires a_i=b_(i+1), contradiction. Hence joined source UNSAT with a short original-source arithmetic certificate even though 3|n. This source proof does NOT infer UNSAT merely because a CI enumerator returned zero.

GIRTH: every cycle that lies in one original component has length≥g. A cycle using the cross connections uses all 3 of them and a path inside each cut component from the former row endpoint to the former variable endpoint. Such a path has length≥g−1, otherwise restoring the original edge creates a cycle shorter than g. Hence any new cross-component cycle has length at least `3+3(g-1)=3g`. Therefore joined Tanner girth≥g, and the source remains C4-free.

The connectivity proof is fully all-source for every CONNECTED legal SCL input: 3-regular bipartite Tanner graphs have no bridges, as shown by the one-edge-cut degree divisibility argument. In the explicit tower, connectivity is additionally source-verified for finite controls.

## 3. Infinite HIGH-GIRTH, 3|n, connected source UNSAT family

Earlier R5 tower theorem is exact: start from original Fano7 SCL with Tanner girth6 and m0=7; on each connected cubic bipartite source H_j, take spanning-tree chord-basis voltage cover over `(F2)^(m_j+1)`. The lift has `m_(j+1)=m_j 2^(m_j+1)`, stays original legal cubic/bipartite/C4-free, is connected, and girth STRICTLY grows because every simple base cycle has a nonzero independent chord voltage.

Every m_j equals 7 times a power of two, hence never divisible by3. Take THREE copies at EVERY tower level and cyclically join as above. The connected joined sources have

```
n_j = 3m_j ≡0 (mod3),
#SAT(F_j)=0,
girth(Tanner(F_j)) ≥ girth(H_j) → infinity.
```

Previous independent theorem: contracting ANY source-valid Tanner perfect matching to quartic T4 cells gives graph Q_j with `girth(Q_j) ≥ girth(Tanner(F_j))/2`, so quotient girth also goes to infinity.

The exact unpinned generalized-loop tensor has local moments of selected-degree 1 and 4 zero; every nonempty selected-edge subgraph contributing to the loop sum must have occupied degrees 2 or3, hence CONTAINS a cycle. Fix any integer L independent of source size. Choose j with girth(Q_j)>L. Then all nonempty generalized-loop terms of ≤L selected edges vanish. The truncated correction equals 1 (empty subset); exact source Holant and exact normalized correction equal 0 by original-source UNSAT. Therefore:

```
FOR ANY FIXED L,
SOME CONNECTED LEGAL SCL SOURCE WITH 3|n, UNSAT
SATISFIES LoopTrunc_≤L = 1 AND LoopExact=0.
```

Thus a GLOBAL size-divisibility check `3|n`, followed by ANY fixed-edge-count loop truncation, is not a sound+complete all-SCL decision algorithm.

Important SCOPE: source-aware polynomial decomposition or modular-cut algorithms can reject these specific examples, and a growing-L or non-flat implicit exact algorithm remains possible. Nothing here implies P!=NP or exponential time for all algorithms.

## 4. Independent controls and correct CI provenance

Source:
`experiments/r5_universal_triple_fano_connected_divisible_high_girth_unsat.py`.
Workflow:
`.github/workflows/r5-connected-fano-divisible-high-girth.yml`.

CI [#38322755341 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38322755341):
- three base Fano7 copies cyclically joined => connected legal SCL21 with n mod3=0, independently original-source UNSAT via boundary-charge contradiction and finite exact Boolean count0; Tanner girth6;
- first 256-sheet Fano binary homology cover has m=1792, original Fano-cover Tanner girth>9;
- joining THREE covers yields connected legal SCL5376, n mod3=0, original-source block charge UNSAT certificate, Tanner girth>9;
- independently source-audited matched quartic Q has no cycle of length≤5, so exact loop correction=0 but truncated loop correction through 5 selected edges=1;
- forged source rows rejected.

The matching quotient was constructed and original incidence source replayed at n=5376 without computing the exponentially large full partition.

Second adversarial control, [#38322908815 SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38322908815):
a SECOND independent connected legal SCL21 is obtained from the EXACT open-gadget source G10 and G11 of earlier R5 pin-compiler theorem. G10 has one nonzero boundary state (a,b)=(1,0), multiplicity1; G11 has one nonzero boundary state (a,b)=(0,1), multiplicity2. Delete each cut edge and SWAP cross attachments `W10→V11, W11→V10`; both required border equalities hold, giving EXACTLY 2 original SAT witnesses; every source row of the transformed SCL21 is independently replayed and direct exhaustive original 2^21 Boolean counting confirms 2.

Thus we have independently source-verified, connected, cubic, C4-free, SAME-SIZE, SAME n%3, girth≥6 SCL21 sources with

```
SCL21 SAT : original #SAT = 2;
SCL21 UNSAT: original #SAT = 0.
```

Both have the SAME positive universal homogeneous Bethe value `Z_B=(16/27)^7`, and the same local 1/3-consistent pseudodistribution by previous all-SCL theorem. Local statistics and total size do not decide their source truth. This finite distinction does not by itself establish a hardness result against any specific stronger global algorithm.

## 5. Current gate and next positive theorem

COMPLETED:
- Connected source-legal unbounded-girth UNSAT tower WITH global n divisible3;
- explicit nontrivial boundary-charge explanation of UNSAT independent of the n mod3 check;
- arbitrary fixed selected-edge loop cutoff contradicted;
- same-size source SAT21/UNSAT21 adversarial pair;
- independently checked non-Holyer finite controls from prior checkpoints continue to apply;
- existing all-SCL constant-size pin compiler still proves search-to-decision for a *hypothetical* universal unmarked zero oracle.

MISSING:
- Uniform worst-case polynomial-bit-time exact `LoopZeroTest` for EVERY ORIGINAL legal SCL, not merely a fixed-depth loop rule or a boundary-charge subclass;
- polynomial-time bit-complexity and original-source soundness/completeness for any proposed non-flat implicit signature algebra;
- ultimately a universal SAT-witness/UNSAT-sound `SolveLinearCubicXSAT`. P vs NP OPEN.

```
CONNECTED_UNSAT_N_DIVISIBLE3_UNBOUNDED_GIRTH = PROVED
ORIGINAL_SOURCE_BLOCK_CUT_CHARGE_CONTRADICTION = PROVED
EVERY_FIXED_LENGTH_LOOP_TRUNCATION_WITH_NMOD3_TEST = REFUTED
MATCHED_N21_SAT2_VS_UNSAT0_ORIGINAL_SOURCE_CONTROL = CI_SUCCESS
EXACT_GLOBAL_POLYNOMIAL_LOOPZERO = NOT_CONSTRUCTED
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
