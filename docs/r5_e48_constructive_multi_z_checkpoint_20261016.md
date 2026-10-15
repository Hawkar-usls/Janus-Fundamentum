# R5 E4.8 — CONSTRUCTIVE CONNECTED MULTI_Z via cross-component incidence switches
**Date:** 2026-10-16 (Europe/Kyiv; Actions events late 2026-10-15 UTC).
**Scientific objective:** Explicit certified legal connected UNSAT square+cubic+linear SCL sources with at least 2 distinct nonzero z satisfying integer Ay=2; construct one graph 2-cover admitting multiple different z SAT witnesses; independently remove the trivial 2-edge-cut obstruction where possible. This is a STACKED Draft PR successor to E4.7 [PR #531](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/531). Parent research HEAD `69fe7b98558e832f2bcd6eb8c737511d63b97d12`; main at investigation start `2ef3f81158bf9ef6077bcf4fb1e8ba7f0d2d5434`. Main NOT modified.

## All-n theorem E4.8.A: source cross-switch preserves UNSAT and creates MULTI_Z

Let A be a legal CONNECTED square/cubic/linear UNSAT SCL incidence matrix of order nA divisible by3 with a CERTIFIED integer ternary witness `yA∈{0,1,2}^nA`, `AyA=2·1`. Let B be a legal CONNECTED SAT SCL of order nB, with at least two distinct Boolean Exact-One witnesses `x1,x2` that share `x1[b]=x2[b]=t∈{0,1}` at some source B column b. Suppose A has an original column a with `yA[a]=1−t`; let A row r contain a and B row s contain b.

Take the DISJOINT incidence matrix A⊕B, shift B column indices by nA, and swap two EXISTING source edges

`(r,a),(nA+s,nA+b) ⇒ (r,nA+b),(nA+s,a)`.

The result C has nA+nB rows and columns, every row and column degree3, and is linear (any row-pair/column-pair has at most one shared incidence). The switch connects the components since both original deleted edges lie on cycles: every edge of a 3-regular bipartite graph lies on an even cycle by its decomposition into perfect matchings. Hence both original components remain connected after removing their chosen edges, and the two crossedges connect them.

**All-n UNSAT proof, WITHOUT searching C:** If C had an integer Exact-One Boolean solution x, summing only the nA rows originally belonging to A would give
`nA = 3*sum_(j in VA)x_j − x_a + x_(nA+b)`.
Since nA≡0 mod3, `x_a=x_(nA+b) mod3`; as the values are Boolean, they are exactly equal. Undoing the switch then leaves the two affected row sums unchanged, so x restricted to VA would solve A. Contradiction. Thus **C is UNSAT**.

For each SAT solution `x_i` of B with the fixed common value t, define integer
`y_i=(yA,1−x_i)`. Since `B·1=3·1` and `Bx_i=1`, we have `B(1−x_i)=2·1`. The two switched columns have equal `yA[a]=1−t`, so each row sum remains2 after switching, hence `C y_i=2·1` over integers. The parity words `z_i=y_i mod2` are nonzero, distinct whenever x_i differ, and `z_i∈Z(C)`. Thus `|Z(C)|>=number of distinct chosen SAT witnesses of B with common b,t`.

**Structural firewall:** This ONE cross-switch creates an EXPLICIT 2-edge cut separating the two original vertex sets of the incidence graph. It establishes existence of connected UNSAT multi-z sources but not high-girth, high expansion or SAT/UNSAT spectral twins.

## All-n theorem E4.8.B: compatible ternary witnesses ⇒ one simultaneous 2-cover by solving GF(2)

For each claimed ternary `y_i` and each source variable j with `y_i[j]=1`, introduce selected sheet label `lambda_(i,j)∈GF2`. Let `sigma_(r,j)` be a binary voltage on every legal source incidence (3n bits).

Every row of each y_i is one of patterns (2,0,0) or (1,1,0). Rows of the first type are automatically exact-one in both lifted row copies. For a row of second type, with unit-value variables j,k, the EXACT requirement is the linear equation

`lambda_(i,j)+lambda_(i,k)+sigma_(r,j)+sigma_(r,k)=1 mod2`.

For a fixed finite list of integer ternary witnesses, existence of one simultaneous SAT 2-lift realizing ALL of them is EQUIVALENT to consistency of the collected GF2 linear system, and a Gaussian solution explicitly CONSTRUCTS all lifted Boolean witnesses. It is NOT automatic from `|Z(C)|>=2`. Given the y_i, this feasibility and construction are polynomial; finding the y_i in arbitrary instances is NOT proven polynomial.

For each nonzero sheet-XOR z_i the sheet-swapped Boolean lifted solution is distinct and has the SAME z_i. The test constructs and independently validates both solutions. Thus two distinct z each realized gives ≥4 SAT lifted solutions, three gives ≥6.

## Positive control E4.8.C: A=SCL36 UNSAT, B=AffinePlane9 SAT ⇒ SCL45

Use frozen E4.6/E4.7 legal connected UNSAT source n36 SHA256
`9fde1e8f629b75e75a242111a68448b2db4eb47789054fd15d9603fd14788229`,
with exact 64-word GF2 UNSAT oracle and unique yA
(20 ones, two twos in columns1,16, 14 zeros).
Use the actual JANUS `AffinePlane9_SAT` fixture, independently enumerating its THREE exact SAT witnesses.

Pigeonhole yields a pair with the same x_b=t; the generator uses deterministic first largest bucket and compatible A column/rows, then performs ONE cross-switch and checks all degrees, linearity and bipartite connectivity.

**Actual exact CI:**
- C order45, legal, connected, UNSAT.
- Independently FULL enumeration of all **128** GF2 parity words (nullity7): exact SAT count0.
- Exact rational nullity4.
- Two independently constructed integer ternary witnesses with TWO distinct physical parity z.
- Full enumeration of all 127 nonzero base kernel directions yields `|Z(C)|=2`, not merely lower bound2.
- Joint row-incidence-voltage GF2 system is CONSISTENT, and direct rowwise lifted Exact-One checks verify both nonzero z realized by one SAME SAT cover SCL90.
- Independent finite full lifted GF2 oracle: rank81/nullity9, all **512** parity words, exactly **4** valid SAT assignments; two per z.
- The initial two-crossedge source has the expected 2-edge cut. It is a positive proof-of-concept, NOT a source hardness witness.

## Stronger positive control E4.8.D: A=SCL36 UNSAT, B=Holyer-K4 SAT ⇒ SCL54

Use actual JANUS Holyer-K4 source fixture, independently enumeration yields SIX exact SAT witnesses. A deterministic selected column/value class contains FOUR distinct witnesses, all with a common bit; construct four distinct ternary `y_i` and parity `z_i` by the same all-n theorem.

**Actual exact CI:**
- C order54 legal connected, UNSAT.
- FULL **2048** GF2 parity words independently exhaust source (nullity11), exact SAT count0.
- rational nullity6.
- **4** distinct z explicitly constructed, while FULL kernel+residual Exact Cover source audit finds **8** nonzero `z` with `Y_z
e empty`.
- One GF2 voltage solution of joint equations is found for the first three distinct z, and independently verified integer row-sum lifted SAT witnesses AND their sheet swaps give at least **SIX** valid SAT assignments of one SCL108 2-cover. FULL SCL108 SAT count is NOT claimed by this gate.
- A low-edge separator remains by design; no expansion/hardness claim.

## NEW stronger E4.8.E: remove all 1- and 2-edge cuts from SCL45

Starting from the first n45 bridge, make a SECOND legal cross-component 2-switch, with its two switched variable values equal in BOTH frozen integer ternary witnesses. This GUARANTEES preservation of those y witnesses by direct row-sum equality, but does **NOT** preserve source UNSAT as an all-n theorem; the only sound way to claim it for the resulting source is an independent exact UNSAT certificate.

Deterministic restricted scan of disjoint original source rows with value compatibility: the VERY FIRST candidate passed all tests. Second cross-switch uses zero-indexed source row/column edge pairs:
`(2,9)` from source A side and `(39,43)` from source B side, replacing them with cross incidences. Actual exact results:

- Source n45 remains legal cubic linear and connected.
- GF2 rank39/nullity6; exhaustive ALL64 GF2 parity words certify **UNSAT**.
- Rational rank42/nullity3 by exact Fraction elimination.
- Complete source kernel Y_z audit: ALL63 nonzero z checked, exactly **TWO** relevant z, each with **ONE** integer ternary Y witness and the SAME y=2 source columns `{1,16}`. Physical z in frozen fixture:
  `16868327578472` and `29375272344424`.
- Every one of the `binom(135,2)=9045` pairs of distinct source incidence EDGES was independently checked by a standard-library clean-room BFS that removes both edges and recomputes graph components. NO edge cut of size1 or2; the source is **3-edge-connected** in the graph-theoretic sense.
- Additionally, a separate complete balanced 25%-fraction vertex-separator tester found NO separator of vertex size≤2. Vertex separator sizes≥3 NOT CHECKED.
- One joint GF2 voltage sign solution constructs an **SCL90** cover with all four SAT witnesses (two for each z). Exact complete GF2 oracle rank81/nullity9, all512 parity words checked, **SAT count exactly4**.
- The C45 signed cover and its two z remain unchanged by reconstructing source from committed numbers; no reliance on random seeds at verification time.

**Important hard-gate limitations:** source n45 is BELOW the proven Moore threshold n≥63 for girth≥12 cubic bipartite incidence graphs, so it CANNOT satisfy that high-girth target. No proof of expansion, balanced separator size≥3, universal running-time lower bound, or a degree2 depth1 SAT/UNSAT spectral twin.

## Independent frozen clean-room verification

`experiments/r5_e48_frozen_repaired_multi_z_20261016.json` commits actual rows of the repaired source C45, a fixed 135-edge voltage sign mask for its SAT 2-cover, explicit source parity z and two lifted SAT witness bitstrings, plus frozen expected counts and source SHA256
`79d48f357fe9bffd32734ea44df33ab50e46cfb345859da7384a5c3d136626d0`.

Workflow derives a candidate fixture using the JANUS construction and FAILS on `E48_FROZEN_REPAIRED_SOURCE_DRIFT` if it differs from the COMMITTED original fixture; it never silently replaces it.

`experiments/r5_e48_cleanroom_repaired_verify_20261016.py` is standard-library-only and imports NO research project modules. It implements:
- independent HIGH-pivot GF2 elimination and full kernel enumeration (producer used LOW-pivot GF2);
- rational Fraction-based Gaussian elimination;
- complete all63 source residual Y_z exact covers;
- complete EXHAUSTIVE all 9045 edge-pair deletions with BFS (producer used independent Tarjan lowlink);
- reconstruct signed 2-lift from frozen source row triples+135-bit voltage, independently check full legal SCL90;
- enumerate ALL512 lifted GF2 parity candidates, verify exact integer SAT count4;
- independently compute layer-XOR for each exact SAT witness, showing multiplicity exactly2 for each of the TWO source z.

All checks passed CI. This clean-room computation independently verifies mathematical facts about the shared frozen instance; it does not claim the fixture was independently *discovered*.

## Reproduce

```bash
python3 experiments/r5_e48_connected_multi_z_bridge_20261016.py --self-test > e48_bridge_certificate.json
python3 experiments/r5_e48_bridge_cut_repair_20261016.py --limit 400 > e48_cut_repair_certificate.json
python3 experiments/r5_e48_cleanroom_repaired_verify_20261016.py --fixture experiments/r5_e48_frozen_repaired_multi_z_20261016.json > e48_cleanroom_repaired_certificate.json
```

Workflow `.github/workflows/r5-e48-connected-multi-z.yml` runs the tests, checks fixture drift, and uploads the machine-readable JSON certificates (90-day retention). Code, fixtures and this report remain versioned in GitHub.

## Proof-vs-experiment ledger

| Gate | Status |
|---|---|
| One cross-component 2-switch preserves legal connected SCL | PROVED all n under assumptions |
| One cross-switch keeps source UNSAT via mod3 argument | PROVED all n under assumptions |
| Matching yA[a]=1−xB[b] produces distinct Y_z directions | PROVED all n under assumptions |
| Simultaneous SAT 2-cover from consistent GF2 voltage constraints | PROVED all n conditional; constructive |
| E4.8 initial connected SCL45 full Z=2, UNSAT and SAT 2-cover exact4 | CI VERIFIED |
| E4.8 initial connected SCL54 full Z=8, UNSAT; ≥6 lifted SAT | CI VERIFIED |
| Second cross switch preserves UNSAT in ALL n automatically | **NOT PROVED, NOT CLAIMED** |
| Frozen repaired 3-edge-connected UNSAT SCL45 full Z=2 | EXACT CLEAN-ROOM CI VERIFIED |
| Repaired SCL90 exact SAT count4 with both z active | EXACT CLEAN-ROOM CI VERIFIED |
| No balanced 25%-vertex separator k≤2 after repair | FINITE EXHAUSTIVE CI VERIFIED |
| No high-girth, expansion or large balanced separator (>2) | OPEN |
| Opposite SAT/UNSAT signed 2-lift pair matching B0..3 and full depth1 profile | NOT CONSTRUCTED |
| All-n polynomial SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P versus NP | OPEN |

**Next targeted Gate E4.9:** characterize **NONTRIVIAL balanced vertex separators of size3 and higher**, explicit girth and expansion; then seek multi-z-preserving structural rewrites on sources n≥63, with exact UNSAT certificates and verifiable joint SAT 2-lifts. Avoid treating 3-edge-connectivity as a hardness theorem. Independently test any SAT/UNSAT cover twins for full truncated B0..B3 + local A4..A10 + depth1 affine signatures, and retain UNKNOWN for incomplete or resource-limited checks.
