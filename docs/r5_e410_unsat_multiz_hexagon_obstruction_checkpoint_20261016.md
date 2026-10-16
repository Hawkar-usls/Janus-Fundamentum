# R5 E4.10 — UNIVERSAL TERNARY COVER INHERITANCE, N90 UNSAT MULTI_Z, HEXAGON 0=1 OBSTRUCTION
**Scientific date:** 2026-10-16, Europe/Kyiv.
**Parent:** stacked successor to [Draft PR #533](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/533), research HEAD `de2578e3db3305ae9333606553a1fddf488c32d2` at this new branch's creation. Main has NOT been modified/merged. Historical source: E4.8 frozen repaired connected legal UNSAT SCL45, with exactly two nonzero feasible z directions, each with one integer ternary y; full source GF2 kernel dimension6, independently complete 64-word UNSAT proof. E4.9 gave exact joint cycle space rank19 and an SAT-compatible Ramanujan-NEW signing, but bad source old spectrum and source cut.

## E4.10.A All-n theorem: ternary witnesses survive graph covering

For an arbitrary legal square cubic 3-regular Exact-One incidence matrix A of order n and a ternary integer vector `y∈{0,1,2}^n` satisfying `Ay=2*1`, take ANY graph covering `Atilde` of degree p (in particular a 2-lift), with each lifted variable j_sheet assigned the SAME ternary y_j. Every lifted row is incident to exactly one copy of each of its original three variables; therefore its integer sum remains 2. Hence

`Ay=2*1 ⇒ Atilde * (y repeated p times)=2*1.`

If two source y witnesses have distinct parity vectors `z1≠z2`, their repetitions yield distinct nonzero vectors of `ker_GF2(Atilde)`, so

`|Z(A)|>=2 ⇒ |Z(Atilde)|>=2`

for ANY graph cover. This does NOT imply SAT or UNSAT of Atilde: covers of UNSAT sources may be SAT, as established previously.

## E4.10.B All-n finite 2-lift hexagon-parity obstruction

For a simple cycle gamma of length l in a source bipartite incidence graph, voltage parity `Σ_(edge e∈gamma) sigma_e mod2` determines its lift:
- EVEN parity: two distinct simple lifted cycles of length l;
- ODD parity: one simple lifted cycle of length 2l.

Therefore girth of any graph 2-lift can exceed6 only if **EVERY** simple base 6-cycle has odd voltage parity.

The source C45 (legal linear cubic, incidence girth6) has 26 simple cycles of length6. Complete deterministic enumeration constructs the corresponding 135-dimensional GF2 edge-incidence masks. Their required 26 linear equations `mask_gamma · sigma=1` have GF2 rank22 but augmented rank23, hence are INCONSISTENT.

More importantly, elimination tracking constructs an explicit, independently replayable **THREE-HEXAGON** witness. A set of THREE distinct original source simple hexagon masks `m8,m12,m13` has

`m8 XOR m12 XOR m13=0`.

Therefore the three requested odd-voltage equations would imply `0=1 XOR 1 XOR 1=1`. At least one of these source 6-cycles stays even-voltage under EVERY signing and lifts to a simple 6-cycle. As a graph cover cannot have smaller girth than source, we conclude:

`EVERY 2-lift of THIS frozen C45 source has EXACT incidence girth6.`

This is a **FINITE SOURCE-SCOPED THEOREM**, not a prohibition on high girth for other legal SCL source families or more general graph transformations.

Exact 135-bit XOR certificate (each mask represents exactly one independently checked 6-cycle on the frozen parent and their XOR is zero):

```text
m8:  59429886597890459256674582528
m12: 1901489500757814766823270252544
m13: 1960911529337877730990309244928
m8 XOR m12 XOR m13 = 0
3 required odd RHS bits XOR = 1
```

Stronger attempted constraints also inconsistent:
- girth8 (require all 26 base 6-cycles odd): rank22, contradiction with3 hexagons;
- girth10 (26 hexagons+69 8-cycles =95 conditions): rank39, explicit 3-cycle contradiction;
- girth12 (plus106 10-cycles =201 conditions): rank46, explicit 9-cycle contradiction.

For a base with girth6, there are no other nonbacktracking closed walks of length less than12 outside simple cycles: a non-simple reduced closed walk must contain at least two simple cycles, requiring ≥12 total edges. In any case the hexagon proof ALONE rules out girth≥8; there is no need to assume the stronger enumeration's completeness to prove the final no-girth8 statement.

## E4.10.C Construct connected n90 UNSAT MULTI_Z despite short-cycle impossibility

To establish that size n≥63 and MULTI_Z can coexist on a larger certified UNSAT source, we select a completely explicit incidence-voltage signing of the frozen C45. Since the COMPLETE E4.8 base-only audit establishes `Z(C45)={z1,z2}`, any SAT 2-lift must have one of these two sheet-XOR directions. We directly check that the selected sigma violates **at least one fundamental cycle equation for EACH z**; thus neither z could support a Boolean exact-one 2-lift witness. This is an exact algebraic UNSAT certificate relying only on the complete E4.8 source `Z(C45)` certificate.

Independently, exact GF2 rowspace enumeration on the NEW 90×90 source constructs rank83/nullity7 and exhausts ALL `2^7=128` parity words: **ZERO** Exact-One solutions. It is legal square/cubic/linear and its 180-vertex incidence graph is connected.

The two original ternary source witnesses y_i are now literally repeated on both sheets; all ninety integer source rows are independently checked to sum2. Two physical nonzero z parity vectors in the new GF2 kernel are:

```text
zA_lift = 593501514037282183362403176
zB_lift = 1033550512377019709900217192
```

Hence the new source satisfies `|Z(C90)|>=2` (a LOWER bound, not a claim that every nonzero 127-word kernel direction has been counted).

Direct BFS confirms incidence girth EXACTLY6, matching the source-level no-girth8 theorem. The original parent C45 has a four-edge cyclic cut with an 18-vertex smaller side; the graph 2-lift inherits an EIGHT-edge cut with a **36-vertex** smaller side among180 vertices. Its conductance satisfies the exact upper bound `8/(3*36)=2/27`, so n90 is **not** a high-expansion / source old-spectrum improvement and is not an asymptotic hardness witness.

## E4.10.D Independent permanent frozen instance and clean-room replay

The fully explicit source is COMMITTED as:

`experiments/r5_e410_frozen_unsat_multi_z_20261016.json`.

It contains all ninety row triples (n90), signed C45→C90 voltage mask, two source-to-lift ternary parity witnesses, three original source hexagon masks, and the original expected rank/girth statistics. No generation randomness is needed to replay. CI regenerates a candidate fixture and checks equality against this immutable GitHub file, failing on `E410_FROZEN_SOURCE_DRIFT`.

`experiments/r5_e410_cleanroom_lifted_unsat_20261016.py` uses **ONLY standard library** and imports NO prior JANUS research modules; independently:
1. reconstructs every lifted row from the frozen C45 source and voltage, byte-for-byte compared against the frozen C90 row triples;
2. validates source SCL legality (degree3, pairwise linearity), graph connectivity and exact girth by independent BFS;
3. reconstructs every one of THREE certified hexagon edge masks on parent C45, checks each is a single connected simple 6-cycle, and independently computes their XOR is zero and odd RHS parity;
4. performs fresh HIGH-pivot GF2 elimination on C90 (producer uses earlier low-pivot implementation), gets rank83/nullity7 and enumerates all128 GF2 parity words, proving UNSAT;
5. lifts BOTH ternary integer Ay=2 witnesses, checks all90 row sums and two different nonzero parity z;
6. independently validates inherited 8-edge cut and conductance upper bound2/27.

Full source and numerical proof certificate are emitted as JSON in CI; raw certificate artifacts have explicit 90-day retention, while frozen source and scripts persist in GitHub.

## R5 scientific ledger

| Statement | Authority |
|---|---|
| Every graph cover preserves any supplied integer ternary Ay=2 witness | PROVED ALL n |
| A multi-z base gives at least two distinct ternary directions in every cover | PROVED ALL n |
| UNSAT source automatically implies UNSAT of any cover | **FALSE; NOT CLAIMED** |
| All simple base hexagons can be made odd in frozen C45 | NO — explicit GF2 0=1 from3 hexagons |
| Every 2-lift of frozen C45 must have incidence girth exactly6 | PROVED FOR FROZEN SOURCE, finite witness |
| n90 connected legal cubic linear base is UNSAT | CLEAN-ROOM CI VERIFIED, 128-word complete proof |
| n90 admits at least two distinct z with Ay=2 ternary witnesses | CLEAN-ROOM CI VERIFIED |
| n90 has girth≥10/12 | FALSE for this family |
| n90 source conductance at alpha≤0.2 >2/27 | NOT POSSIBLE; inherited cut upper bound2/27 |
| n90 high expansion or large balanced separator | NOT PROVED |
| Same n90 SAT/UNSAT branch-stable spectral twins | NOT CONSTRUCTED |
| Generic uniform polynomial-time SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |

## Reproduction

```bash
python3 experiments/r5_e410_girth_lifted_unsat_multi_z_20261016.py --fixture experiments/r5_e48_frozen_repaired_multi_z_20261016.json --samples 96 > e410_lifted_source_certificate.json
python3 experiments/r5_e410_cleanroom_lifted_unsat_20261016.py --fixture experiments/r5_e410_frozen_unsat_multi_z_20261016.json --parent experiments/r5_e48_frozen_repaired_multi_z_20261016.json > e410_cleanroom_certificate.json
```

Workflow: `.github/workflows/r5-e410-lifted-multi-z.yml`, with two-stage verification and immutable-fixture check.

## Next scientifically admissible frontier E4.11

**Replace the source-hexagon contradiction at the graph-construction level.** One signed 2-lift of this frozen C45 can NEVER give girth≥8 (specific three-cycle witness), so further searching such voltage signings is mathematically wasted. Construct a qualitatively new legal connected UNSAT source n≥63 with `Z(A)>=2` via source-level rewrites or a different parent without contradictory odd-hexagon equations; independently verify exact UNSAT using proof-carrying certificates (GF2 enumeration when small, LRAT verified where large). Only then target girth≥10 or12, balanced expansion and the branch-depth1 spectral twins. Optimizing signed NEW eigenvalues without improving source OLD spectrum cannot close that gate.

