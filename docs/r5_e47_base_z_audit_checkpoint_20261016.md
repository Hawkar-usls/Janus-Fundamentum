# JANUS Fundamentum R5 E4.7 — COMPLETE_BASE_Z_AUDIT + RATIONAL_NULLITY_FILTER
**Date:** 2026-10-16 (Europe/Kyiv; CI events 2026-10-15 UTC).
**Source provenance:** User proposed the two general base-level filters and asked for complete frozen SCL36 all-63-direction audit, rational rank/nullity, followed by a search for legal connected multi-z-capable UNSAT bases. We independently read Draft [PR #530](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/530), actual HEAD `879e0bbf3d1530017ee9cea3931409c632d6f437`, and the complete frozen declarative fixture. At start `main` pointed at `2ef3f81158bf9ef6077bcf4fb1e8ba7f0d2d5434`. This is a *stacked research PR*; main is not updated.

## General theorem E4.7.A — BASE_Z_AUDIT is independent of two-lift voltages (PROVED ALL n)

For legal square/cubic/linear SCL incidence A define, for each z in ker_GF2(A),
`Y_z={y∈{0,1,2}^n : A*y=2*1 (over Z), y mod2=z}`,
and the finite set

`Z(A)={0≠z∈ker_GF2(A) : |Y_z|>0}`.

By definition **Z(A) depends only on original A**. Two-lift incidence signs/voltages sigma choose which z lie in ker(H_sigma) and which fixed-z graph-cycle equations are compatible, but cannot create a new y in Y_z. Every SAT witness of a graph two-cover of a CONNECTED UNSAT base has some nonzero z∈Z(A) (z=0 would descend to a SAT base witness). Thus:

`|Z(A)|<=1 ⇒ no legal graph two-lift of this base can have two DISTINCT contributing nonzero sheet-XOR directions`.

If `Z(A)=empty`, NO SAT two-lift of this connected UNSAT base can exist, regardless of voltages. If `Z(A)` contains one direction, only that direction can contribute, even when a particular obstruction H has a higher-dimensional kernel. This is an ALL-COVERS prohibition on MULTI_Z for the fixed base, not an all-n solver.

For every z, `|z|` is even and `3|z|=2|R2|<=2n`, so `p=n/3-|z|/2>=0` for all valid source-kernel words. E4.6 proved `|Y_z|` exactly equals the number of clean-column exact covers of the R0 row set.

## General theorem E4.7.B — rational nullity necessary for multiple ternary y (PROVED ALL n)

For every SCL A, `A*1=3*1`. If an UNSAT base has a ternary y with integer `Ay=2*1`, then `u=y−(2/3)*1∈ker_Q(A)`.

On an UNSAT base, every ternary y must have AT LEAST ONE of each value 0,1,2:
- if no 2, y is Boolean and x=1−y is an Exact-One SAT base witness;
- if no 1, x=y/2 is Boolean Exact-One SAT base witness;
- if no 0, `sum(y)>=n` contradicts `sum(y)=2n/3`.

Suppose two distinct y,y' have dependent u,u'. Then
`y'=(2/3)*1+lambda*(y−(2/3)*1)`.
The coordinates where y is 0 restrict lambda to `{1,−1/2,−2}`;
the coordinates where y is 1 restrict lambda to `{−2,1,4}`;
and those where y is 2 restrict lambda to `{−1/2,1/4,1}`.
Their intersection is exactly `{1}`, forcing y'=y — contradiction.
So any TWO distinct ternary y on an UNSAT base yield independent rational kernel directions. Therefore

`|{ternary y : A*y=2*1}|>=2 ⇒ dim ker_Q(A)>=2`.

In particular, `|Z(A)|>=2 ⇒ rank_Q(A)<=n−2`.
This is only NECESSARY, never sufficient. Rational rank can be screened by a finite-field rank lower bound: `rank_(mod p)(A)<=rank_Q(A)` for every prime p. Hence if `rank_(mod p)>=n−1`, the base is decisively excluded for MULTI_Z without any rational elimination or Y_z work.

## Complete independent 63-direction certificate: frozen connected UNSAT SCL36

The original E4.6 frozen fixture is permanently versioned as
[exact rows and voltages](https://github.com/Hawkar-usls/Janus-Fundamentum/blob/research/r5-e47-base-z-audit-20261016/experiments/r5_e46_frozen_fixture_20261016.json).
Source SHA256 from fixture:
`9fde1e8f629b75e75a242111a68448b2db4eb47789054fd15d9603fd14788229`.

File `experiments/r5_e47_base_z_rational_audit_20261016.py` is a new standalone Python-STDLIB-ONLY verifier with NO imports from research modules:
1. Validates all n36 row/column degrees3 and pairwise intersections≤1.
2. Computes GF2 rowspace via its own independent LOW-pivot row-reduced echelon, obtains exact rank30/nullity6; enumerates **all 2^6−1=63** nonzero kernel vectors and rechecks Av=0 for each.
3. For each z, constructs R0/R2, p(z), all clean outside columns and all exact ternary solutions Y_z in TWO ALGORITHMICALLY DISTINCT ways:
   - (i) first uncovered-row recursive exact-cover DFS, checking each terminal integer Ay=2/y mod2=z;
   - (ii) independent squarefree multilinear mask-product DP: product of (1+three-row monomial) for each clean column, modulo squared row variables; coefficient at the full R0 row monomial counts exact covers.
   The two counts agree for every one of 63 z, no resource-limit UNKNOWN.
4. Exactly ONE relevant direction, `Z(A)={32055778152}` (weight20), and EXACTLY ONE y for that direction; two columns with y=2 are source indices **1 and16** (zero-indexed), covering R0 rows [0,3,4,9,15,22]. The y histogram is 20 coordinates=1, two=2 and14=0.
5. Remaining **62** directions satisfy Y_z=empty. This is a COMPLETE FINITE certificate for the fixed base, not a random sample. Consequently MULTI_Z impossible for EVERY legal two-cover of this base, including all arbitrary voltages and ANY obstruction rank; the earlier scan over 32 rank4 H matrices was a strict subset of this stronger result.
6. Emits full per-z JSON records (64-bit exact decimal z, weight, p, R0, clean columns, solutions, DFS nodes, DP states) and computes stable table SHA256:
`7153b32b654ff901184c31c50ab68e7737bed4513682100fe244c7499f8fe223`.

**Independent exact rational rank:**
- Fraction-based full rational RREF yields `rank_Q(A)=33, nullity_Q(A)=3`;
- produces THREE explicitly independently verified rational kernel basis vectors;
- selects 33 original source rows and 33 columns from pivots and independently computes their 33×33 integer determinant with fraction-free Bareiss elimination: **−96**, a nonzero lower-bound rank certificate; the three rational kernel vectors give the rank upper bound33. Thus equality rank33 is proven by two separate certificate forms.

The rational filter does NOT exclude this original UNSAT base: nullity_Q=3>=2. It is the complete discrete `Z(A)` certificate, not rational rank, which proves all-two-covers MULTI_Z impossible here.

## First reproducible search for a NEW multi-z-capable base

Script `experiments/r5_e47_find_multi_z_base_20261016.py` generates exactly 96 seeded legal connected SCL36 sources using the existing source-level degree/linearity-preserving incidence switches, independently checks SAT/UNSAT with full GF2-affine enumeration, and applies `rank_mod65521>=34` as a rigorous negative test for the necessary `rank_Q<=34` criterion. If modular rank is at most33, it computes exact rational rank. Only then it enumerates full GF2 kernel and complete Y_z for candidate UNSAT bases.

CI observed:
```text
generated legal connected n36: 96
exact SAT: 17
exact UNSAT: 79
UNSAT rejected mod prime rank >=35: 66
UNSAT rejected mod prime rank ==34: 12
UNSAT passing rational nullity>=2: 1
that one fully enumerated for Z(A): 1
Z(A) size of that candidate: 0
found legal connected multi-z UNSAT source: NONE
```

For this single rational-eligible source Z(A)=empty, so NO SAT graph two-cover is possible from it, not merely no MULTI_Z. These are **FINITE NEGATIVE** outcomes for the frozen 96-source generator and seed. They do NOT establish an all-n impossibility, a lower bound for SAT, or completeness of source-graph construction.

The exact integer/z certificates for the rare candidate appear in the uploaded JSON CI artifact; no new SAT 2-cover is claimed.

## Scientific status

| Statement | Gate |
|---|---|
| Z(A) depends only on A, not two-cover voltages | PROVED ALL n |
| |Z(A)|<=1 forbids multi-direction SAT on any 2-lift of fixed UNSAT base | PROVED ALL n |
| Two ternary y on UNSAT base force Q-nullity>=2 | PROVED ALL n |
| Prime-field rank≥n−1 soundly rejects MULTI_Z candidates | PROVED ALL n |
| Frozen base GF2 dimension6 all63 exact Y_z verified twice | CI PASS |
| Frozen Z(A) singleton, multi-z impossible across ALL covers | FINITE PROOF-CARRYING CERTIFICATE |
| Frozen rank_Q33/nullity3, 33×33 nonzero det −96 | EXACT CERTIFICATE |
| Bounded 96-source UNSAT scout | 79 UNSAT, 78 rejected by rational filter, one with Z(A)=empty |
| Connected UNSAT source with >=2 eligible z and joint affine cycle loci | NOT FOUND |
| Opposite SAT/UNSAT full depth1-degree2 spectral+anchors twins | OPEN |
| Polynomial construction of complete Z(A) for arbitrary GF2 d | NOT PROVED |
| Uniform polynomial-time SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |

## Reproduce
```bash
python3 experiments/r5_e47_base_z_rational_audit_20261016.py --fixture experiments/r5_e46_frozen_fixture_20261016.json > e47_base_z_certificate.json
python3 experiments/r5_e47_find_multi_z_base_20261016.py --trials 96 > e47_connected_multi_z_scout.json
```
Workflow: `.github/workflows/r5-e47-base-z-audit.yml`.
Complete per-z and searched-base JSON certificates are uploaded as
GitHub Actions artifacts with 90-day retention; scripts and proof
checkpoint remain versioned in GitHub.

**Next admissible Gate E4.8:** Rather than mere random voltage switches on one frozen base, create or find a legal CONNECTED UNSAT source with `|Z(A)|>=2` and `nullity_Q>=2`, with independent exact UNSAT proof. Only then build voltage systems such that multiple z directions actually lie in ker H and have compatible cycle parity in one chosen 2-lift. Compare full root `B0..B3,A4..A10` before attempting parity-tagged depth1 profiles. Include balanced expansion and girth separately; neither follows from Z(A). Do not confuse this finite structural frontier with an all-n polynomial SAT theorem.
