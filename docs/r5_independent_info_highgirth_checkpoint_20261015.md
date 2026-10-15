# R5 E4.3 — INFORMATIONALLY_INDEPENDENT_BRANCH_TWINS
**Date:** 2026-10-15.
**Scientific objective:** Distinguish mathematically independent discriminants from redundant but independently computed proof checks; measure bounded branch cost; use high-girth and balanced-separator controls; attempt feature-preserving parity twists without inventing a SAT/UNSAT counterexample.

**Parent provenance:** User-provided detailed audit in `Вставленный текст(20261015-112828).txt`; independent implementation and finite regressions in new stacked Draft PR based on [PR #526](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/526). Parent HEAD at read `2830cfcbe5e3674c152fa8a3a59ac2c050d60cab`; main initially `eda3c2b53dc917b3240d3ae5f87c73f4e3ab6957` and NOT modified.

## E4.3 Theorem A: low signed MacWilliams ↔ low binomial moments (ALL n)

For any consistent Boolean cube x_Z=0, x_O=1 of legal square/cubic/linear SCL, the free kernel-complement code is an affine coset v0+L on m coordinates, with d=dim L, r=m−d, rowspace signed spectrum

`D_s = sum_{u in L^perp, |u|=s} (-1)^{u·v0}`.

Let `C_j = #{v in v0+L : |v|=j}` and binomial moments
`M_q = Σ_j C_j binom(j,q)`. The affine weight enumerator is

`W(z)=Σ_j C_j z^j=2^(-r)Σ_s D_s(1+z)^(m-s)(1−z)^s`.

Since `M_q=[(z-1)^q]W(z)`, expand at z=1 and obtain

`M_q=2^(d−q)Σ_(s=0)^q (−1)^s binom(m−s,q−s)D_s`.

This transform is UPPER TRIANGULAR in s with nonzero
diagonal `2^(d−q)(−1)^q` at q=s. Therefore for known m,d:

`(M0,...,Mk) ↔ (D0,...,Dk)`

and each side can be exactly reconstructed from the other using rational arithmetic. These are two independently COMPUTABLE views of the same fixed-degree information, not two independent discriminating channels, when k is at least the moment degree.

**Additional informational nuance:** retaining separately P_s and M_s, with D_s=P_s−M_s and B_s=P_s+M_s, may carry information unavailable from the signed D_s alone. Kernel A4,A6, etc. can also be independent of the low signed spectrum (as demonstrated by the frozen connected n36 seeds0 and13).

## E4.3 Theorem B: audit identities are redundant for full LP but essential as cross-checks

For the same cube c=A_Z1, m free coords, r=rank A_T:
- d=m−r;
- C0=[c=0], C_m=[A_T*1_T=c];
- sum_s D_s=2^r C0;
- sum_s (−1)^s D_s=2^r C_m;
- D_m=(−1)^|Z|;
- D_(m−s)=(−1)^|Z|D_s;
- P_(m−s),M_(m−s) are equal to P_s,M_s when |Z| even, swapped when odd; B_(m−s)=B_s.

Full, sound E4.1 affine MacWilliams with exact C0/C_m already implies corresponding endpoint sums. Accordingly these are independent AUDIT CHECKS, not stricter inequalities when the complete LP already includes their source identities.

**Implemented verifier:** `experiments/r5_discriminant_audit_split_20261015.py` computes fixed low D_s via restricted-rowspace membership/character, M_q via independent GF2 rank queries and compares both triangular transformations. The small finite oracle enumerates all 2^d affine words solely in regression, derives full D by inverse Krawtchouk and independently derives all B via a second homogeneous histogram; every P/M complementary swap and both endpoint sums are checked. For arbitrary n no 2^d enumeration is required to obtain low k moments/spectrum.

**Core/audit split:**
- Discriminant core `(m,r,parity,C0,target,P_s,M_s for s≤k, optional independent A4,A6 anchors)`.
- Audit layer `(d,moment M0..Mk recomputed, signed endpoint sums, D_m, consistency tags, LP optimum when mathematically determined by full LP input)`.
The audit layer is an independent implementation witness, NOT a new dimension of discriminatory power. If moments degree exceeds signed spectral k, the extra moments must return to core; the current implemented paired test uses the same k.

### Finite exact controls

CI: AffinePlane9, HolyerK4, connected SCL36 seed0 and seed13, each at root and four partial assignments. Low signed coefficients degree3 and moments degree3 match exactly, are invertible both ways, and the complete tiny oracle checks both endpoint sums and full P/M complement symmetry.

Frozen connected n36 seed0 and13:
- identical signed-low degree2 / binomial moment degree2, and matching core **WITHOUT** kernel anchors;
- different exact A6 coefficients: (A4,A6)=(0,3) versus (0,2);
- therefore the extended `core+anchors` correctly separates the pair. They remain both SAT, true #SAT2 vs3. This does NOT demonstrate SAT/UNSAT indistinguishability.

## E4.3 Theorem C: exact number of depth-h partial cubes

For m originally free variables, the number of DISTINCT partial cubes with at most h fixed coordinates is

`Q_h(m)=Σ_(i=0)^h 2^i binom(m,i)`.

Fixed h ⇒ `O(m^h)`. When h grows like log(m), this simple enumerating scheme has quasipolynomial size `exp(O(log²m))`; at h=m exactly `Q_m(m)=3^m`. This is a bound on **the complete materialized family**, NOT a proven lower bound on more compressed algorithms and NOT necessarily the number visited by a clever solver.

For m=36:
```text
h0: 1
h1: 73
h2: 2,593
h3: 59,713
h4: 1,002,193.
```
This exposes why growing branch depth cannot be called uniformly polynomial merely because fixed depths are.

## E4.3 Theorem D: girth and balanced separators (ALL n)

The original 3-regular bipartite incidence graph B_A has n row vertices and n column vertices. For girth(B_A)>=12, degree3 even-girth Moore bound gives

`2n>=2*(1+2+4+8+16+32)=126`, i.e. **n>=63**.

Every nonzero selected kernel support is a simple cubic graph G_v; its cycles of length l correspond to incidence cycles length 2l. Therefore if girth(B_A)>=12, girth(G_v)>=6. The degree3 Moore bound in a cubic graph of girth6 gives |support(v)|>=14, hence

`A4=A6=A8=A10=A12=0`.

This vanishing applies to the full kernel AND each compatible partial cube. Verification of girth>=12 uses deterministic BFS to depth5 from each incidence vertex, O(n) sparse RAM operations because degree3 and depth fixed.

**Crucial separator correction:** every cubic graph on sufficiently many vertices has a 3-vertex LOCAL separator: removing the neighbors of one vertex isolates that vertex. Thus an adversarial input cannot literally demand the absence of ALL small separators. Meaningful targets should impose **BALANCED** separator / expansion constraints, e.g. no separator of size k separating both sides of size≥0.25N. The exact finite checker only certifies presence/absence of balanced separator size 0,1,2; size≥3 is NOT excluded.

### Verified connected SCL72 FAILS both desired hardness filters

SCL72 from four-K4 witness-preserving swaps is legal connected, GF2 nullity d21, and has a verified SAT witness. It FAILS girth>=12 due to a short incidence cycle. More decisively, exact balanced-25%-separator search found a separator of just two incidence vertices [16,107], splitting the other 142 vertices into two components of sizes **36 and 106**. Therefore this source is NOT a proven separator-resistant/hard SCL; it is a useful NEGATIVE CONTROL. Its exact SAT count was not computed in this experiment.

## E4.3 experiment: feature-preserving local parity-twists

`experiments/r5_information_twins_20261015.py`

Instead of blindly hoping random SCLs collide, start from frozen legal connected SAT n36 seeds0 and13, and attempt local legal incidence 2-switch combinations of lengths 1,2,3. Retain a candidate ONLY if the entire independent core
`(m,r,parity,C0,target,P/M_signed low degree2,A4,A6)`
remains exactly unchanged. Only retained candidates use complete exact GF2 affine enumeration for SAT/UNSAT; if an opposite-status root twin appears, compare all singleton branches under a variable-renaming-invariant unordered-multiset signature with the same core+anchors. An UNSAT verdict requires complete finite enumeration; no timeout converts to UNSAT.

**Finite recorded result:** 72 trials each, 144 total:
```text
seed0: true SAT count 2; 71 rejected nullity change;
       1 more rejected after discriminant; 0 admitted.
seed13: true SAT count 3; 70 rejected nullity change;
        2 admitted after full core+anchor matching; both SAT.
Opposite SAT/UNSAT core twin: NOT FOUND.
Depth1 opposite SAT/UNSAT twin: NOT TESTED, no root pair.
```
Including 2/3-switch compositions did NOT change this result on the frozen seeded trials. It is a concrete negative outcome for THIS generator budget, NOT a proof that invariant-preserving parity twists do not exist. This reveals the dominant selection bottleneck: preserving GF2 nullity.

## Scientific status
| Gate | Result |
|---|---|
| Signed affine Pless triangular moment equivalence | **PROVED ALL n** |
| Independent information-vs-audit split | **PROVED for matched degrees; CI** |
| Endpoint alternating sum and P/M complement | **PROVED; FINITE CI** |
| Full finite oracle and independent GF2-rank checks | **CI PASS** |
| Exact Q_h(m) combinatorial family size | **PROVED** |
| Girth12 n>=63 and A4..A12=0 | **PROVED ALL n** |
| Small balanced separator discovered on connected n72 | **EXACT FINITE NEGATIVE CONTROL** |
| Local rank/core-preserving parity twist SAT→UNSAT | **NOT FOUND in 144 finite trials** |
| All-n explicit girth12 + expansion resistant legal SCL with certified SAT/UNSAT | **NOT CONSTRUCTED** |
| Universal polynomial bound on branch depth/coverage | **NOT PROVED** |
| `SolveLinearCubicXSAT` | **NOT CONSTRUCTED** |
| P vs NP | **OPEN** |

**Next defensible research step:** construct nontrivial rank-preserving *global* parity-twist gadgets, preferably structured on n≥63 incidence girth12 with measured BALANCED expansion, and generate opposite-status pairs with matching independent k-degree discriminants and independent UNSAT proofs. If k is fixed and finite, a collision is a lower bound ONLY on that specified feature grammar, not on all exact SCL algorithms. The current exact Fraction simplex also still lacks a proven polynomial pivot bound.
