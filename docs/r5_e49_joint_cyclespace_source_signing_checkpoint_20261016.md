# JANUS Fundamentum · R5 E4.9 — JOINT_CYCLESPACE_GEOMETRY + SOURCE_STRUCTURAL_PROFILE + CONSTRAINED_SIGNING

**Scientific date:** 2026-10-16 (Kyiv).
**Provenance:** started from user's independent E4.8 audit, including the proposed exact 19-rank joint cycle constraints, 27-dimensional switching family, 4-edge modular seam and poor old source spectrum. These were NOT adopted as assertions alone: this gate reconstructs the actual frozen E4.8 source from its 45 committed row triples, re-derives every cycle and all 3-edge cuts, numerically searches *within the compatible family* and verifies a winning signing via two independent exact rational-inertia algorithms.

**Parent:** E4.8 [Draft PR #532](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/532), actual SHA `719c0bf3544226c03a8521fdc89fc38397450ed4`, still unmerged. E4.9 stacks on that research branch; `main` not changed.

## E4.9.1 — ALL-n JOINT_CYCLESPACE THEOREM

Let A be legal n×n SCL incidence. For any **nonzero** z in ker_GF2 A with ternary integer feasible Y_z nonempty, the support graph G_z has vertices supp(z), and each row meeting supp(z) twice supplies one graph edge connecting the two selected columns. By legal SCL linearity, it is SIMPLE; each source column has exactly three incident edges in G_z, hence it is 3-regular. With c_z components:

`|E(G_z)|=3|z|/2,quad beta(G_z)=|E|-|V|+c_z=|z|/2+c_z.`

The voltage compatibility constraints from each graph cycle gamma are

`Σ_(e=(j,k;i)∈gamma) [1+sigma_(i,j)+sigma_(i,k)]=0 mod2`.

Each G_z graph edge maps to a *unique pair* of original incidence edges. Thus the linear map from G_z edge 1-chains into the source incidence edge space is injective: independent graph cycles yield independent linear voltage equations. Consequently, **on the full 3n-dimensional edge voltage space** the rank of the fixed-z constraints is EXACTLY `beta(G_z)`; because every constraint is an incidence cycle it vanishes on gauge changes `sigma_(i,j)→sigma_(i,j)+p_i+q_j`, and the same codimension remains in the connected source's switching quotient.

For multiple feasible nonzero z in a set Y, let W_Y be the GF2 span of all incidence cycle masks from their G_z. The joint rank is

`kappa(Y)=dim_GF2(W_Y)`,

not the sum of individual beta ranks. When compatible, the affine signing family modulo gauge has dimension

`(3n-(2n-1))-kappa(Y)=n+1-kappa(Y)`

for any connected square cubic SCL source, provided every requested z is ternary feasible. For a general connected incidence graph with V vertices and E edges, the corresponding formula is `E−V+1−kappa(Y)`. The affine solution set could be empty; compatibility itself must be checked.

These formulas concern **signings realizing specified already-known ternary witnesses**, not universal polynomial computation of Z(A), SAT/UNSAT or P=NP.

### Frozen repaired SCL45 exact certificate

Source:
`experiments/r5_e48_frozen_repaired_multi_z_20261016.json`.
Canonical source SHA256:
`79d48f357fe9bffd32734ea44df33ab50e46cfb345859da7384a5c3d136626d0`.

Exactly two relevant z, each weight26, and their G_z have 26 vertices,39 edges,1 component and **beta=14** each.

File `experiments/r5_e49_joint_cyclespace_20261016.py` reads this frozen source; independently BFS-constructs each G_z spanning tree, computes its 14 fundamental cycle source-voltage masks and their parity RHS, checks each cycle against the already-certified original signed SAT 2-lift, and Gaussian-ranks all masks. Result:

```text
rank(W_z1)=14
rank(W_z2)=14
rank(W_z1 + W_z2)=kappa=19
dim(W_z1 ∩ W_z2)=14+14-19=9
source cycle space E−V+1=135−90+1=46
gauge bit subspace dim=89
full compatible incidence voltage affine dimension=135−19=116
compatible switching quotient dimension=116−89=27
compatible switching class count=2^27=134217728
```

The checker independently builds 45 row and45 column gauge generators, verifies their rank89, proves every 14+14 cycle mask annihilates gauge, derives an explicit **27-element linearly independent nongauge basis** for the compatible voltage solution space (stored as exact decimal bit strings in the JSON certificate), and verifies each generator still directly admits integer Exact-One lifted witnesses for **BOTH** physical z. This makes the 27-dimensional result a CONSTRUCTIVE finite GF2 certificate.

The 2^27 signings were **not exhaustively searched**; 2^27 is an exact affine-family cardinality, not an empirical sample size.

## E4.9.2 — SOURCE_STRUCTURAL_PROFILE

File `experiments/r5_e49_structural_profile_20261016.py` independently builds Γ as 90 vertices and135 incidence edges. It computes girth by BFS from every vertex: **girth=6**.

To completely classify **all 3-edge cuts**, rather than BFS-reconstruct 400995 triples separately, the verifier deletes each of 9045 edge pairs and finds *all bridges remaining* by exact Tarjan lowlink DFS. ANY 3-edge cut necessarily appears as one such pair plus a bridge. It finds exactly **90** such 3-edge cut triples, and verifies they coincide with the 90 cubic vertex stars. Each removal isolates exactly one vertex. Hence there is NO NONTRIVIAL / CYCLIC cut of size3. The previous independent clean-room gate ruled out all size1/2 cuts.

Four specific cross-incidences (source row, original source column indices) remain:
`(1,36),(2,43),(36,3),(39,9)`.
Deleting these FOUR edges divides the incidence graph into CONNECTED vertex sets of cardinalities72 and18, BOTH containing cycles. Thus cyclic edge connectivity for this frozen graph is EXACTLY

`lambda_cyclic(Γ)=4`.

The smaller component's volume in the cubic graph is 3×18=54; there are4 boundary edges, so its exact edge conductance is

`4/54=2/27≈0.074074074`.

For the prescribed `Phi_alpha=min_{alpha*|V|<=|S|<=|V|/2} |∂S|/vol(S)`, the explicit 20%-side cut gives a valid **UPPER BOUND** `Phi_alpha <= 2/27` when `alpha<=0.20`. It gives **NO** bound by that same cut for `alpha=0.25`, and its conductance was not independently proved globally optimal.

A separate bounded balanced-vertex-separator exhaustive algorithm found no 25%-balanced vertex separator of size1 or2. A user audit had reported k<=4 from a larger finite enumeration, but this gate has **NOT** rerun 3/4 vertex removals and does NOT claim that result as independently CI-verified.

**Why signings cannot fix the seam:** every graph 2-lift inherits the source's OLD eigenvalues and preimages of source cuts have identical conductance ratios. Improving NEW eigenvalues cannot remove source cut structure.

## E4.9.3 — CONSTRAINED_SIGNING: ACTUAL NEW SPECTRAL WITNESS

The classic bipartite 2-lift decomposition says the spectrum of the 2-lift is the union of the OLD source adjacency spectrum and the NEW signed adjacency spectrum.

For SCL incidence B (n×n) and source bipartite graph adjacency `[[0,B],[B^T,0]]`, the eigenvalues are `±singular_values(B)`. Under source-edge sign sigma, the NEW eigenvalues are `±singular_values(B_sigma)`.

The research script `experiments/r5_e49_constrained_signing_20261016.py` starts from the original certified compatible sigma, generates exactly 27 independent nongauge-compatible basis deltas, samples 400 deterministic pseudorandom bit combinations (seed20261016), and does a bounded one-bit-neighbor descent using NumPy SVD as a HEURISTIC ONLY.

Frozen best:
```text
source old lambda2 numerical             2.904907260618564
baseline signed new max |lambda|         2.916567666011535
best observed signed new max |lambda|    2.6690667160012045
best quotient bit-code                  121461366
best signed incidence voltage mask      13122370207647014411045975447177946768522
```

The script builds integral Gram `B B^T` and `B_sigma B_sigma^T` (45×45). It then INDEPENDENTLY certifies singular-value counts above strict rational thresholds by exact `fractions.Fraction` LDL inertia of `q² I − G`, not by trusting floating SVD:

```text
source λ2 ∈ (29049/10000, 29050/10000) = (2.9049,2.9050)
best new signed radius ∈ (2668/1000, 2671/1000) = (2.668,2.671)
```

It verifies `(2671/1000)^2 < 8` and `(29049/10000)^2 > 8` as EXACT integer inequalities.

Therefore, for THIS explicit frozen signing:

`||A_sigma|| < 2.671 < 2sqrt2`

and it preserves both independent feasible z in ONE 2-lift (explicit integer lifted witnesses checked again). This is an ACTUAL **Ramanujan NEW spectral bound** for a signing CONSTRAINED to JANUS's joint-SAT affine family, not merely an unconstrained Bilu–Linial signing.

However, the source itself has `lambda2(source)>2.9049>2sqrt2`. Because every 2-lift inherits OLD eigenvalues, no signing can make this particular source's full 2-lift a Ramanujan graph in the usual cubic bipartite spectral sense.

**Global optimization is NOT claimed**: 400 sampled non-gauge combinations plus local improvements do not minimize over all 134217728 classes, nor do they prove a universal constrained-signing theorem.

### Independent exact spectral replay, frozen witness

The explicit candidate is frozen in `experiments/r5_e49_frozen_constrained_signing_20261016.json` (not silently recomputed). The separate standard-library-only script `experiments/r5_e49_signed_spectral_cleanroom_20261016.py` imports NO JANUS code and NO NumPy. From frozen rows and voltage bits it rebuilds both integral 45×45 Gram matrices, uses a different exact Fraction symmetric-Schur inertia code, independently reconstructs exact-one Boolean 2-lift solutions for EACH z (including their sheet swaps), checks all integer lifted row sums, and repeats the two rational intervals and strict `2sqrt2` comparisons.

Thus the numerical best signing is **independently proof-carrying** even if a future heuristic search chooses a different winner. The checker certifies AT LEAST4 lifted SAT witnesses; it does NOT yet claim a complete SAT count for this new signing (the original E4.8 frozen signed lift has exactly4 via a separate complete oracle).

### Literature alignment and boundaries

- Zhiqiang Xu, *A deterministic algorithm for signing bipartite graphs at the Ramanujan bound* (2026-10-07), [arXiv:2610.09972](https://arxiv.org/abs/2610.09972), reports deterministic polynomial full-space bipartite signing `||A_sigma||<2sqrt(Delta−1)`. This is a RECENT PREPRINT and does not establish the same bound **within a JANUS fixed affine parity family**.
- Vaibhav Suvagiya, *Parity families and signed spectra* (revised 2026-09), [arXiv:2607.17343](https://arxiv.org/abs/2607.17343), studies affine GF2 cycle-signing constraints and near-Ramanujan transfer, including bounded-codimension assumptions in relevant regimes. E4.9's `kappa(Y)=19` on n45 is not bounded uniformly when n grows; no such theorem is automatically applicable.
- The source old/new spectral decomposition is the standard Bilu–Linial 2-lift identity, used in Marcus–Spielman–Srivastava bipartite interlacing families. These theorems neither remove the frozen C45 four-edge cut nor prove arbitrary finite-dimensional affine constrained minimization.

## SCIENTIFIC GATE LEDGER

| Subgate | Verdict |
|---|---|
| Individual `beta(G_z)=|z|/2+c_z` cycle rank and codim | PROVED ALL n |
| Joint `kappa(Y)` = span rank and quotient dim `E−V+1−kappa` | PROVED ALL n (when affine system compatible) |
| Frozen kappa(z1)=14,kappa(z2)=14,joint kappa=19, overlap9 | EXACT CI VERIFIED |
| 27 nongauge generators and 134217728 compatible switching classes | EXACT CI VERIFIED |
| Frozen source incidence girth6 | EXACT CI VERIFIED |
| All 90 size3 cuts are trivial vertex stars | EXACT CI VERIFIED |
| Cyclic edge connectivity exactly4 | EXACT CI VERIFIED |
| Explicit cut bound `Phi_alpha<=2/27` for alpha<=0.2 | EXACT CI VERIFIED |
| Global `Phi_alpha` minima and alpha=0.25 upper | NOT COMPUTED |
| Source old λ2 strict interval (2.9049,2.9050) | EXACT RATIONAL INERTIA CI VERIFIED |
| One JANUS-constrained signing with new spectral norm <2sqrt2 | EXACT RATIONAL INERTIA + INDEPENDENT CLEAN-ROOM CI VERIFIED |
| Best new signing exact SAT count 4, two per source z | INDEPENDENT FULL GF(2) ORACLE CI VERIFIED |
| Global optimum over all 2^27 | NOT PROVED |
| Uniform constrained signing theorem | NOT PROVED |
| New n>=63 legal connected UNSAT source with joint MULTI_Z and high girth | **NOT CONSTRUCTED** |
| Independent LRAT certificates for unbounded GF2 nullity | NOT YET IMPLEMENTED |
| Depth1 opposite-status spectral+anchor S1 twins | NOT CONSTRUCTED |
| Universal polynomial time SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P versus NP | OPEN |

## E4.9.D — exact SAT count is CONSTANT across the full 27-dimensional compatible signing family

The E4.8 frozen source C45 has been FULLY audited: it is UNSAT, and
`Z(C)={z1,z2}` contains exactly TWO nonzero parity sheet-XOR
directions. Each fixed-z residual exact cover yields
`|Y_z1|=|Y_z2|=1`. Both support graphs `G_z1,G_z2` are connected,
so `c_z1=c_z2=1`.

For EVERY incidence voltage sigma that satisfies the 19
independent joint parity constraints (equivalently, EVERY one
of the 2^27 compatible gauge-quotient classes), E4.5's ALL-n
signed two-lift counting identity gives

```text
#SAT(lift_sigma(C45))
= sum_{z in Z(C45)} |Y_z| * 2^{c_z} * 1[cycle_z(sigma) holds]
= 1*2 + 1*2
= 4.
```

No other 90-var Exact-One solutions can exist:
the source C45 is UNSAT, hence sheet-XOR zero is
impossible; Z(C45) was FULLY enumerated and has
no third admissible direction. Therefore the ENTIRE
27-dimensional affine family—not merely the one
selected good signing—has **exactly four SAT witnesses
per graph 2-lift**, two for each z. This claim is
conditional on the frozen exact source certificate;
it is not an all-n constant-count theorem for
arbitrary SCL instances.

A newly extended **independent stdlib-only verifier**
`experiments/r5_e49_signed_spectral_cleanroom_20261016.py`
now reconstructs the winning 90×90 signed two-cover,
computes its ACTUAL GF2 rank/nullity using a separate
HIGH-pivot elimination, enumerates every one of its
`2^d` parity words, and checks that EXACTLY the four
constructed signed Exact-One words survive (two per z).
CRITICAL scientific repair: unlike the ORIGINAL frozen
2-lift, the newly optimized signing is NOT assumed
to retain rank81/nullity9. Its rank is recomputed
from the new matrix; the old rank was never protected
by the cycle parity constraints alone. The numerical
spectral certificate did not depend on this correction.

This adds an independent finite count certificate
to the exact cycle-theoretic deduction, not a uniform
polynomial-time all-SCL solver.

## Reproduction

```bash
python3 experiments/r5_e49_joint_cyclespace_20261016.py --fixture experiments/r5_e48_frozen_repaired_multi_z_20261016.json > e49_joint_cycle_certificate.json
python3 experiments/r5_e49_structural_profile_20261016.py --fixture experiments/r5_e48_frozen_repaired_multi_z_20261016.json > e49_structural_certificate.json
python3 experiments/r5_e49_constrained_signing_20261016.py --fixture experiments/r5_e48_frozen_repaired_multi_z_20261016.json --samples 400 > e49_constrained_signing_certificate.json
python3 experiments/r5_e49_signed_spectral_cleanroom_20261016.py --fixture experiments/r5_e48_frozen_repaired_multi_z_20261016.json --signing experiments/r5_e49_frozen_constrained_signing_20261016.json > e49_cleanroom_signed_spectrum.json
```

Workflow `.github/workflows/r5-e49-cyclespace-structure.yml` runs these four and uploads four proof JSON certificates with explicit 90-day retention. Source scripts, numerical frozen signed witness and theorem checkpoint are committed permanently.

## Next E4.10 / E4.9 N63 structural challenge

The E4.8 source is now fully explained; it should not be over-sold as hard. Seek a *NEW* connected legal UNSAT source `n>=63`, girth10 (or12), `|Z(A)|>=2` with at least two compatible SAT directions in one two-cover, and record `kappa(Y)` and `dim F_Y`. The cubic bipartite girth12 Moore tree needs 126 incidence vertices, i.e. n>=63; scanning n45 cannot test girth12. Require certified small-cut/expansion metrics by explicit separators, sound lower bounds or exact computations, not inferred from “no 2-cut”. For larger source d, accept independent externally verifiable UNSAT certificates (LRAT or similarly checkable formats), not timeouts or uncontrolled parity enumeration. Only on such controls pursue opposite-status SAT/UNSAT twins matching root B0..3, A4..10 and all parity-tagged depth1 signed-affine child signatures.

The spectral gate's definitive lesson is that even a **successful constrained near-Ramanujan NEW signing** does not cure **source OLD eigenvalues and cuts**. Therefore high-girth/expansion and proof-carrying source construction are the next scientific bottleneck, not repeating SCL45 voltage search.
