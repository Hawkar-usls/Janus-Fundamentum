# R5 THEOREM: Original SCL90 J5 is UNSAT but has NO GF(3) degree-three Boolean polynomial-calculus refutation

Date: 2026-10-13 (Europe/Kyiv). Research PR #516 DRAFT; main untouched.

## Precise scientific outcome

The proposal that every UNSAT original square/cubic/linear positive Exact-One 3-SAT (SCL) source F has a degree-three GF3 Nullstellensatz/Boolean-polynomial-calculus refutation is **FALSE**. This is an unconditional counterexample to one restricted algebraic proof system, NOT a proof of P!=NP and NOT a lower bound against arbitrary polynomial algorithms. P vs NP remains OPEN.

Let F be the exact native source make_scl(flower(5)), with 90 variables, 90 Exact-One3 rows, three occurrences per column, and no pair of original rows sharing more than one variable. Each original row C_i induces E_i(x)=sum_(v in C_i) x_v - 1 over F3, reduced modulo the original Boolean equations x_v²=x_v. The proposed degree-d refutation space V_d(F) is the GF3 span of all multilinear reductions E_i*x_M with original source row i and squarefree monomials M of size at most d-1.

**Claim proven:** F UNSAT, but 1 is NOT in V_3(F). Thus the minimal degree for the specific source J5 SCL90 is at least FOUR (whether degree4 suffices is NOT proved).

## Certificate A: independently ORIGINAL-SOURCE UNSAT

The 20-vertex Isaacs flower snark J5 is encoded by the direct source-legal cubic graph 3-edge-colouring bridge: each graph edge e contributes three Boolean variables (edge e, colour c) and one Exact-One clause among its colours; each graph vertex contributes one Exact-One clause for each of three colours. This produces exactly 90 square/cubic/linear positive Exact-One source variables and rows. It has an explicit witness bijection with 3-edge colourings.

The old independently source-authenticated 27-state transfer and exact 8-state obstruction prove that NO odd Isaacs flower can be properly 3-edge-coloured. The existing function verify_authenticated_flower_unsat checks that the source is EXACTLY the native flower(5) Holyer image AND verifies the transfer contradiction. The direct exhaustive 3-edge-colouring checker separately returns UNSAT for J5. This truth certificate does not depend on the degree-three polynomial-calculus solver.

## Certificate B1: full exact 121,576-dimensional GF3 row-space plus independent dual check

There are exactly N3 = 1+90+C(90,2)+C(90,3) = 121,576 squarefree monomials of degree <=3. There are exactly 90*(1+90+C(90,2)) = 368,640 allowed original source generators E_i*x_M with |M|<=2.

A full exact sparse GF3 Gaussian elimination computed:
- native source GF3 degree3 row-space rank: 121,275
- status: NO DEGREE3 REFUTATION, verified via dual
- independent F3 dual y support: 54,735 nonzero coordinates
- exact sparse elimination cell updates: 464,719,115
- original dual checks: y(1)=1, y(E_i*x_M)=0 for ALL 368,640 generators

An independent checker reconstructs the original source polynomial generators from row IDs and multiplier sets and verifies every equality over GF3. No floating arithmetic or extrapolation.

**Authoritative CI:** https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38331387342 (SUCCESS), source SHA 254679fa079e8dd0c679deaca5eb613564acfe0d.
Source: experiments/r5_universal_flower_snark_gf3_degree3_dual_attack.py.

Provenance: first failed CI #38331153843 was only an incorrect harness assumption n=9k (true is 18k). Corrected CI #38331203838 returned UNKNOWN_RESOURCE_LIMIT after the originally configured 100M-update guard (rank120819), without a false scientific conclusion. Raising the guard to 500M yielded the exhaustive fully certified SUCCESS #38331387342.

## Certificate B2: independent symmetry-compressed exact dual plus full original source replay

There is a SOURCE-ROW-VERIFIED automorphism group G=C10 x C2 of order20 on flower J5's native Holyer source. The first factor rotates the TWISTED 2k-cycle of c/d lanes (which interchanges c/d at the seam) and simultaneously rotates the petal centre/b vertices modulo k. The second swaps original colours 0 and 1 globally. Every original source row is checked to map to another original source row.

Because 20 is invertible in F3, any source-valid degree-three dual y can be averaged over G while preserving y(1)=1 and annihilation of ALL source row-monomial products. Consequently an invariant dual exists if and only if an ordinary original degree-three dual exists. This is a general finite group averaging lemma; it is valid only because the group order is not divisible by the field characteristic.

The independently implemented orbit-linear algebra has:
- original degree<=3 monomials: 121,576
- invariant monomial orbits: 6,656
- source row orbits: 10
- representative row*multiplier equations: 40,960
- compressed exact GF3 rowspace rank: 6,639
- result: a G-invariant F3 dual exists
- full expanded dual nonzero support: 46,266
- ALL 368,640 ORIGINAL generators independently checked over F3
- deliberate forged dual coefficient independently REJECTED

**Authoritative CI:** https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38332355302 (SUCCESS), source SHA 39d2ae8eb8c3095df59f6bc2ec94c1bc1117d2e2.
Source: experiments/r5_universal_flower_j5_gf3_degree3_symmetry_dual.py.
Workflow: .github/workflows/r5-flower-j5-degree3-orbit-dual.yml.

The two dual supports, 54,735 and 46,266, differ because duals are not unique; each is independently source-verified. The invariant method is substantially faster and reconstructs the actual native degree-three dual without depending on the full original Gaussian elimination.

Provenance: the first symmetry implementation tried an UNTWiSTED five-petal rotation and was correctly REJECTED by source-automorphism replay (CI #38332196211 FAILED); the corrected twisted rotation passed the original source test but an ordinary harness typo key/keys caused CI #38332273480 FAILED. CI #38332355302 fixed this and passed ALL source checks. Those failures were coding faults, not contrary scientific proofs.

## Elementary proof of actual refutation lower bound

Take EITHER independently source-verified dual y. Assume a degree-three refutation existed:
  1 = sum over original rows i and monomials |M|<=2 of c_(i,M) multilinear(E_i*x_M).

By F3-linearity, applying y gives
  1 = y(1) = sum c_(i,M) y(E_i*x_M) = 0,
contradicting the field identity 1 != 0. Hence no degree-three refutation exists in the original native Boolean GF3 proof system. Certificate A independently proves F UNSAT.

Therefore a fully legal ORIGINAL SCL with UNSAT but no V3 refutation EXISTS. This precisely refutes the claimed universal degree-three completeness hypothesis.

## What remains OPEN

This discovery INVALIDATES the earlier conditional n^10 universal candidate when its missing V3-completeness premise is taken as true. It does NOT refute a degree4/5/etc universal theorem, or prove that degrees must grow with n; it does NOT rule out other implicit polynomial LoopZeroTest algorithms. The conditional source preserving pin compiler and witness self-reduction remain correct.

Next admissible proof goal: determine whether degree4 suffices for this exact J5 or construct native SCL families requiring degree that grows without bound. Published PC lower bounds on OTHER graph-colouring and Tseitin encodings cannot be transplanted into the native square/cubic/linear SCL source without an explicit GF3 low-degree-back-simulation reduction.

GATES:
- NATIVE_J5_SCL90_SOURCE_UNSAT = PROVED
- ORIGINAL_GF3_DEGREE3_GAUSSIAN_NO_REFUTATION = PROVED
- ORIGINAL_GF3_DEGREE3_DUAL_54735 = CI_SUCCESS
- SOURCE_VERIFIED_TWISTED_AUTOMORPHISM_C10xC2 = PROVED
- INVARIANT_ORBIT_DEGREE3_DUAL_46266 = CI_SUCCESS
- ALL_368640_ORIGINAL_GENERATORS_REPLAYED = PROVED
- UNIVERSAL_ALL_SCL_DEGREE3_COMPLETENESS = REFUTED
- J5_MINIMUM_GF3_SOURCE_PROOF_DEGREE >=4 = PROVED
- J5_DEGREE4_SUFFICIENCY = OPEN
- UNIVERSAL_ANY_FIXED_DEGREE = OPEN
- GENERAL_POLY_LOOPZERO = NOT_CONSTRUCTED
- SolveLinearCubicXSAT = NOT_CONSTRUCTED
- P_VS_NP = OPEN


## Frozen certificate without Gaussian elimination — independent third proof mode

The second symmetry-invariant J5 dual has now been frozen as actual immutable-by-commit source data, separate from all algorithms which DISCOVERED it:

- Path: research/certificates/R5_J5_SCL90_GF3_V3_ORBIT_DUAL_2026-10-13.b64z
- Content: 1452 Base64 characters encoding zlib-compressed 6656 GF3 moment orbit bytes.
- SHA256 of DECOMPRESSED 6656-byte orbit vector:
  f2944e1a4fb474ebaac3aa2fcc19689139d1bee256f3f01af1f4ecebfd7c1edd
- Standalone code: experiments/r5_j5_degree3_frozen_dual_standalone_source_verifier.py
- Independent CI: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38332775987 — SUCCESS.

This standalone source verifier does NOT perform Gaussian elimination or invoke the degree-three dual GENERATOR. It:
1. rechecks the exact native J5 source SCL90 and original 27-state UNSAT transfer;
2. decodes the frozen 6656-entry moment-orbit byte string, checks its SHA256 and exact source symmetries;
3. expands all 121576 multilinear moments and checks the exact F3 linear relation for **every one of the 368640 original clause×monomial degree-three generators**;
4. rejects a deliberately corrupted witness.

Thus the fixed certificate is an independently verifiable actual finite mathematical WITNESS of nonmembership 1 outside V3(F), not merely a numerical rank statistic or code which promises to construct a dual. The original SCL source is independently UNSAT; the elementary 1=y(1)=0 contradiction completes the theorem.

The FALSE universality of GF3 degree3 now has independently checkable code, frozen small data, hash and completed CI.
