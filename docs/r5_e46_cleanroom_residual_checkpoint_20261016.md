# R5 E4.6 — CLEAN_ROOM_VERIFY + RESIDUAL_YZ_EXACT_COVER + MULTI_Z_SCOUT
**Date:** 2026-10-16 local Europe/Kyiv; frozen CI events on 2026-10-15 UTC.
**Provenance:** User's uploaded mathematical E4.5 audit proposes a directly verifiable residual ternary-to-exact-cover reduction, an independent clean-room verifier, and adversarial multi-`z` voltage families. We implemented those as separate experimental gates. Parent stacked [Draft PR #529](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/529) HEAD `d44341c3e1224ad08442c8d4159c06c2b3e119b0` independently verified before branch. GitHub main at audit start `8be760f090a5c0c678c8fdfc46f48e49704b060c`; main NOT changed by this research branch.

## Gate E4.6-A: all-n theorem, fixed-`z` residual exact cover

Let A be any legal n×n square cubic linear SCL incidence matrix, z∈ker_GF2(A), S=supp(z), and `Y_z={y∈{0,1,2}^n : Ay=2*1 (over integers), y mod2=z}`. Every source row meets S in zero or two columns. Let R0 and R2 denote the sets of these row types. Counting column incidences gives `|R2|=3|z|/2` and `|R0|=n−3|z|/2`. Thus |z| is even.

For every y in Y_z, y_j=1 on S; for outside columns y_j∈{0,2}. Every R2 row already has 1+1=2, forcing its outside column to0. Define the CLEAN set
`J0={j∉S: all three row incidences of j are in R0}`.
A column y_j=2 can occur only in J0. Every R0 row must be covered by exactly one such column. This establishes a BIJECTION

`Y_z ↔ {exact covers of R0 by complete three-row neighborhoods of clean columns j∈J0}`.

Exactly `p=|R0|/3=n/3−|z|/2` columns with y_j=2 are selected. For fixed z the branching search picks an uncovered R0 row and tries its at most THREE clean columns, yielding `O(3^p poly(n))` worst-case work, with exact easy independent verification of every found y. This is a parameterized bound; p can grow linearly in n and it is NOT an all-n polynomial SCL SAT algorithm. A node-budget exhaustion returns `UNKNOWN_RESOURCE_LIMIT` rather than UNSAT.

### Direct finite certificate of uniqueness

Frozen source: exact E4.5 connected UNSAT SCL36 with original source SHA256
`9fde1e8f629b75e75a242111a68448b2db4eb47789054fd15d9603fd14788229`.
Its unique nonzero 2-lift sheet-XOR `z_star=32055778152` has weight20. It partitions 36 source rows into:
- `R2`: 30 source rows with 2 support columns;
- `R0`: **six rows** with IDs **0,3,4,9,15,22** (0-indexed).

The CLEAN outside source columns are **1 and16**, with disjoint row-neighborhoods:
- column1 covers rows0,3,4;
- column16 covers rows9,15,22.

Thus there is exactly ONE residual exact cover: `{1,16}`, with exactly two columns assigned y_j=2. Its extension y_j=1 on supp(z), y_j=2 at columns1,16 and y=0 elsewhere directly satisfies every original integer row sum2, as well as y mod2=z. This proves **|Y_z|=1 without any 72-variable GF2 parity-oracle count**.

Two independent finite algorithms agree:
1. exact uncovered-row branching using at most three available clean columns per row;
2. direct enumerate all pairs of clean columns and check ALL base row integer sums.

Script: `experiments/r5_residual_yz_exact_cover_20261016.py`.
Formal proof of all-n bijection does not rely on this numerical test.

## Gate E4.6-B: actual clean-room E4.5 verifier

Frozen numerical proof fixture is committed as
`experiments/r5_e46_frozen_fixture_20261016.json`.
It contains only 36 legal base row triples, the fixed SAT voltage
bit mask on the 108 row-column incidences, all **11** nongauge
`ker Phi/gauge` generator bit masks, and z_star, exact ternary
y and direct SAT witness (plus expected test values).

The fixture was initially exported by
`experiments/r5_e46_export_fixture_20261016.py` from the
existing JANUS E4.5 module on a frozen revision. It is now
VERSIONED IMMUTABLY in GitHub; CI recomputes a candidate
and FAILS if it differs from that committed fixture
(`FROZEN_INSTANCE_DRIFT`) instead of silently rewriting it.

**The actual verifier**
`experiments/r5_e46_clean_room_verify_20261016.py` does NOT
import the exporter, the original E4.4/E4.5 code, or any other
JANUS/research module. Only Python stdlib modules are imported.
It implements its OWN LOW-pivot full RREF and kernel, GF2 transpose,
row/column gauge, edge-image Phi, signed 2-lift construction,
cycle-space basis and independent COMPLETE 2^d integer Exact-One
oracle. The proof fixture is model data, not trusted code.

It independently proves, from those frozen numbers:
- base legal cubic linear, rank30, nullity6; UNSAT by ALL64 affine parity words;
- left/right kernel dimension6, Phi rank26, row/column gauge rank71;
- 11 supplied nongauge quotient generators lie in kerPhi,
  and gauge+generators have rank82 = 108−26, hence they span
  the ENTIRE fixed obstruction fiber quotient;
- the 6×6 fixed obstruction H has rank5, unique nonzero z_star
  of weight20;
- directly enumerated residual Y_z has exactly one solution,
  choosing clean columns1 and16;
- G_z has20 vertices,30 edges,1 component,11 fundamental cycles;
  pulled-back 11-coordinate Psi has rank5;
- exactly 2^(11−5)=64 predicted SAT classes;
- on each of ALL2048 quotient classes the verifier builds an
  explicit legal 72×72 2-lift, independently rebuilds its
  affine code using LOW-pivot GF2 elimination, enumerates
  ALL128 codewords and checks integer Exact-One rows.
- EXACT result: **64 SAT,1984 UNSAT**, SAT witness count2
  for EACH SAT cover, zero for each UNSAT cover, **zero
  prediction disagreements**.

This is independent code for verification, **not an
independent derivation of the original instance**; the
frozen fixture originated from JANUS and the verifier
does not independently prove the user's choice of
research instance. A clean-room computation on the
same frozen input eliminates large classes of common
algorithmic bugs but does not make the input source
independent. All claims remain finite/certificate-scoped.

The proof checker is deliberately exhaustive over a
single 2048-class orbit and therefore does NOT prove an
all-n polynomial-time SAT algorithm.

## Gate E4.6-C: multi-z feasibility experiment (bounded negative)

To test the next potential obstruction, vary one or two
row-column incidence voltages starting from the E4.5 SAT
cover, searching for H of rank4 rather than5 (right
kernel dimension2 and THREE nonzero physical z values).
For each candidate z, run the exact residual Y_z
calculator with an explicit resource cap. This distinguishes
the number of admissible sheet-XOR directions from the
number actually supporting valid ternary y.

**Reproducible finite CI outcome:**
- Scanned first **187** one/two-edge flip candidates in a
  deterministic order until **32** rank4 H matrices found.
- Four rank4 H matrices had **ZERO** relevant z with
  Y_z nonempty.
- Twenty-eight rank4 H matrices had exactly **ONE**
  relevant z with Y_z nonempty.
- **Zero** had two or three relevant z in that bounded
  collection. No residual search reached UNKNOWN.
- Concrete example: flip the FIRST source edge.
  H rank4, kerH dimension2, z candidates:
  `55257881971` weight20/p2/Ycount0,
  `32055778152` weight20/p2/Ycount1,
  `50114332187` weight16/p4/Ycount0.

This is a FINITE NEGATIVE result for this source,
voltage-flip grammar and budget, NOT a theorem that
dim kerH≥2 cannot produce multiple relevant z.
Constructing two or more z with Y_z nonempty is a
necessary precursor to genuine overlap/competition of
multiple affine cycle-SAT regions. It is NOT by itself
evidence of high-girth, expansion resistance, or
depth1 SAT/UNSAT indistinguishability.

Script:
`experiments/r5_multi_z_rank4_frontier_20261016.py`.

## Conditional general exact decomposition for UNSAT connected base

For arbitrary connected UNSAT source A, any 2-lift
specified by voltage sigma has obstruction H_sigma.
Every SAT solution has nonzero sheet-XOR z=Kc with
0≠c∈ker H_sigma. For each z,
`Y_z` and G_z depend ONLY on A,z, and consistency of
its cycle-parity system depends on sigma. Different z
index disjoint lifted SAT witnesses, so

`#SAT(tilde A_sigma)
= Σ_{0≠c∈ker H_sigma}
   |Y_{Kc}| · 2^{c(G_{Kc})} ·
   1_{cycle equations satisfied for sigma,Kc}`.

For every z, the residual exact-cover search costs
`O(3^{p(z)} poly(n))` where `p(z)=n/3−|z|/2`.
Enumerating every nonzero kerH_sigma vector gives a
VALID parameterized exact decision/counting algorithm
with worst-case

`poly(n) · Σ_{0≠c∈ker H_sigma}3^{p(Kc)}`

(and polynomial cycle computations per term) provided
the oracle is allowed to finish, but NO universal
polynomial bound because dimkerH and p can grow.

If several z have Y_z nonempty, each contributes one
affine voltage locus when sigma varies inside a chosen
linear voltage family. The union may fail to be affine.
This does not establish a difficult SAT instance or
lower bound for all polynomial algorithms.

## Scientific status

| Statement | Gate |
|---|---|
| Fixed-z residual Yz ↔ exact cover of R0 by clean triples | PROVED ALL n |
| Parameter p=n/3−|z|/2, O(3^p poly n) | PROVED parameterized bound, not P |
| Frozen E4.5 z_star exact residual Y=1 via six rows | INDEPENDENT CI VERIFIED |
| Frozen committed immutable JSON instance | FROZEN / DRIFT CHECK |
| No-research-import LOW-pivot GF2/cycles/full 2048 oracle | CI VERIFIED |
| 64 SAT,1984 UNSAT, rankPsi5, zero mismatches | CI VERIFIED AGAIN |
| Multi-z H rank4, 3 possible z per H | EXACT algebra / CI |
| Two or more Yz-relevant z in 32 sampled rank4 H | NOT FOUND |
| SAT/UNSAT twins at depth1, B0..B3 with same anchors | OPEN |
| High-girth/expander adversarial inputs | OPEN |
| Uniform polynomial SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |

## Reproduce

```bash
python3 experiments/r5_residual_yz_exact_cover_20261016.py --self-test
python3 experiments/r5_e46_export_fixture_20261016.py > generated_candidate.json
python3 -c 'import json; assert json.load(open("generated_candidate.json"))==json.load(open("experiments/r5_e46_frozen_fixture_20261016.json"))'
python3 experiments/r5_e46_clean_room_verify_20261016.py --fixture experiments/r5_e46_frozen_fixture_20261016.json
python3 experiments/r5_multi_z_rank4_frontier_20261016.py --self-test
```

CI:
`.github/workflows/r5-e46-cleanroom-residual.yml`.
Certificates uploaded as workflow artifacts with
90-day retention; code, source fixture and checkpoint
are persistent GitHub files.

**Next admissible mathematical construction:** build an
UNSAT legal connected base with at least TWO *distinct
nonzero* z from kerH for which the residual Y_z exact
cover is independently nonempty. Then derive the
different cycle-parity affine loci and their overlap,
and search opposite SAT/UNSAT voltage pairs matching
B0..B3, A4..A10 and the full degree2 depth1
parity-tagged affine branch signature. Use direct SAT
witnesses and complete/certificate UNSAT, never
resource exhaustion as negative evidence.
