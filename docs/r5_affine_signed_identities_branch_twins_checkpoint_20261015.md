# R5 E4.1a / E4.2 — AFFINE_SIGNED_SPECTRUM_IDENTITIES + BRANCH_STABLE_SPECTRAL_TWINS
**Date:** 2026-10-15.
**Provenance:** user's explicit scientific proposals for three affine signed spectrum equalities and an isomorphism-invariant bounded-depth spectral-twin experiment. This checkpoint is a STACKED Draft PR successor to existing [PR #525](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/525). Read GitHub parent HEAD `ad31b236c3e54932664e471e3d6aa32f99d20cc4`; main at start `eda3c2b53dc917b3240d3ae5f87c73f4e3ab6957`, unchanged.

## E4.1a three global identities (PROVED for every consistent legal cube)

For legal square/cubic/linear SCL A, fixed x_Z=0 and x_O=1,
let free T=[n]\\(Z∪O), m=|T|, a=1_Z and c=A_Z 1 over GF(2).
The kernel v=1+x has fixed v_Z=1, v_O=0 and free coset
v0+L solving A_T v_T=c with L=ker_GF2(A_T), R_T=L^perp,
r=rank_GF2(A_T). Define the signed rowspace coefficients

`D_s = Σ_{u ∈ R_T, |u|=s} (-1)^{u·v0}`.

**Theorem A: Parity.** Since every ORIGINAL column of A has
three ones, `1_n^T A_T=1_T^T` mod2. Consequently

`|v_T| mod2 = 1_n^T A_T v_T = 1_n^T c = |Z| mod2`.

This holds for every affine continuation. Hence C_j=0 when
j%2 differs from |Z|%2. It implies all free homogeneous
kernel words have even weight, and
`D_(m-s)=(-1)^|Z|D_s` because 1_T∈R_T.

**Theorem B: Coset representative invariance.** If v0' is
another solution to A_T v=c, then v0'−v0∈ker A_T=L.
For any u∈R_T=L^perp, u·(v0'−v0)=0. Hence D_s(v0')=D_s(v0)
for EVERY s. In particular two Gaussian solvers may
choose different particular vectors but MUST derive
identical signed spectra.

**Theorem C: Character-sum and homogeneous-RHS identity.**

`Σ_s D_s = Σ_{u ∈ R_T}(-1)^{u·v0}
           = 2^r · [v0∈L]
           = 2^r · [c=0].`

It is mathematically valid on all consistent cubes,
including those with a nonzero particular Gaussian v0
despite c=0 (an implementation must check the RHS,
NOT assume v0=0). For c≠0, the sum must equal ZERO.
For |Z| odd, paired antisymmetry also implies
`D_(m/2)=0` when m even.

**Important redundancy firewall:** Full, correct E4.1
affine MacWilliams LP with its j=0 transform and known
C0 = [c=0] ALREADY IMPLIES
`Σ_s D_s=2^r C0`.
Therefore adding this equation does NOT strictly tighten
that full LP. It is a valuable INDEPENDENT AUDIT check:
detects incorrect signs, wrong coset/RHS, misapplied
homogeneous anchors, or a corrupted certificate.

## E4.1a exact independent finite codeword tests

`experiments/r5_affine_signed_spectrum_identities_20261015.py`
uses a polynomial-input GF2 procedure for fixed low signed
weights and ALSO an independent tiny exhaustive-affine oracle.
The latter directly constructs the complete distribution
C_j, derives EVERY D_s through inverse Krawtchouk, and
asserts all signed sums, complementary symmetry, parity
support, D_m sign, representative invariance and
homogeneity C0. This independent full enumeration is a
FINITE ORACLE ONLY and must not be counted as a polynomial
method for arbitrary n.

Frozen controls: AffinePlane9 n9, HolyerK4 n18, and
CONNECTED SCL36 seeds0/13 (both GF2 nullity7).
For every control root, x0=0, x0=1, x0=x2=0,
and x0=x2=1 are tested with all identity checks PASS.

Examples for the x0=0 branch:
| Source | ΣD_s | D_m | negative signed coefficients |
|---|---:|---:|---:|
| AffinePlane9 | 0 | -1 | 4 |
| HolyerK4 | 0 | -1 | 8 |
| Connected SCL36 seed0 | 0 | -1 | 17 |
| Connected SCL36 seed13 | 0 | -1 | 17 |

On x0=1 of these controls the RHS is homogeneous,
C0=1, D_m=+1 and ΣD_s=2^r.
Original CI was GREEN [run 38724315790](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38724315790).

## E4.2 isomorphism-invariant truncated affine branch signatures

`experiments/r5_branch_stable_spectral_twins_20261015.py`

For each affine Boolean cube C, define a BASE signature
S0(C) using:
- consistency of restricted GF2 equations;
- m,r,d, parity of its free coset and exact C0;
- the independently verified expected character-sum
  ΣD_s and complement sign D_m;
- fixed low positive/negative rowspace spectra P_s,M_s;
- first fixed-degree affine binomial moments;
- target weight feasibility;
- OPTIONAL independently verified exact rational affine
  MacWilliams LP optimum (only used where explicitly enabled).

To avoid a non-invariant choice of one numbered variable,
recursively define

`S_h(C) =
 (S0(C),
  SORTED_MULTISET_v { SORTED_PAIR(
     S_(h-1)(C[v=0]),S_(h-1)(C[v=1]) ) })`.

The multiset runs over ALL currently free variables v.
Under any simultaneous relabeling of original variables
and rows, the pair corresponding to v relabels to the
pair for its image, so the entire root signature agrees.
This is a rigorous ISOMORPHISM-INVARIANT FEATURE, not a
complete incidence-graph isomorphism/canonical-labeling
algorithm. Different nonisomorphic sources may still
share the signature (that's the POINT of twin search).

For fixed integer h and fixed moment/low-spectrum degree
the number of distinct requested cubes is n^O(h),
though the materialized signature can be large; if h
grows with n there is NO proven uniform polynomial cap.
The current Fraction simplex implementation has NO
general polynomial worst-case pivot bound.

**Permutation tests independently checked:**
- AffinePlane9: all singleton branch S1 includes exact
  rational signed affine LP; same after a nontrivial
  variable and row permutation. S2 uses low spectral
  profile without LP; also permutation invariant.
- HolyerK4: S1/S2 low spectral signatures invariant
  on ALL variable branches; exact rational LP root
  and an independently mapped singleton child also
  invariant (not all n18 child LPs; this is recorded).
- This is not proof of complete indistinguishability
  under arbitrary branching strategies, not a
  polynomial-time graph isomorphism algorithm.

## E4.2 finite connected SAT/UNSAT root prescreen

The existing parent E4 finite root signature
`(n,d,N0..N2,B0..B3,A4,A6,A8,A10)`
is stricter than just degree2 affine moments.
The new test builds 36 legal CONNECTED n36 instances
by reproducible degree-preserving incidence 2-switches.
Every result was independently checked via complete
GF2-affine enumeration with at most 2^12 words:

```text
exact classified: 36
SAT: 10
UNSAT: 26
distinct root signatures: 32
same-status repeated signatures: 4
opposite SAT/UNSAT with SAME root signature: NONE.
GF2 nullity distribution:
d0:3, d1:4, d2:7, d3:7, d4:1, d5:4, d6:5, d7:5.
```

Because no opposite-status root twin was found,
there is NO scientific basis to declare a DEPTH1/2
opposite-status twin, nor a "branch-stable" obstruction.
The permutation tests are POSITIVE REPRODUCIBILITY
CONTROLS, not SAT/UNSAT twin claims.

**Higher-nullity connected SAT control:** independent
source two-switch construction from four K4 blocks gives
connected n72 with GF2 nullity d=21 (2,097,152
parity words). A SAT witness is directly checked, so
SAT is established without enumerating all words.
The full exact solution count is NOT COMPUTED by
this E4.2 search, and a missing/timeout witness would
NOT be an UNSAT proof. The construction has obvious
small separators; no structural hardness claim.

## Safe cooperative-bound update

Modified
`experiments/r5_affine_macwilliams_cooperative_20261015.py`
to retain exact proven upper-bound semantics on a
partition of cubes:

`Q(C)=Q(C0)+Q(C1)` exactly;

`U_after=MIN(U_before,U(C0)+U(C1))` is a valid bound
even when children use distinct spectral LPs and their
raw summed bounds fail monotonicity.
A "certified_shrink" is issued ONLY when U_after<U_before.

Finite HolyerK4 CI reproduces root 10→5+5,
so U_after=10, NO shrink; on restricted x0=0
state 5→4, an actual one-unit removal of
BOUND EXCESS, not removal of a SAT solution.

## Reproduction
```bash
python3 experiments/r5_affine_signed_spectrum_identities_20261015.py --self-test
python3 experiments/r5_branch_stable_spectral_twins_20261015.py --self-test
python3 experiments/r5_affine_macwilliams_cooperative_20261015.py --self-test
```
Workflow:
`.github/workflows/r5-affine-signed-identities-branch-twins.yml`.

## Scientific gate ledger
| Topic | Gate |
|---|---|
| All-n parity, rep-invariance, sign character sum, complement symmetry | PROVED |
| Full E4.1 LP strengthened by redundant sum equation | NO; strictly redundant |
| Independent finite full-spectrum oracle regression | CI PASS |
| Permutation-invariant all-split h1/h2 truncated signatures | PROVED and CI |
| Finite 36 connected n36 exact classification | CI: 10 SAT 26 UNSAT |
| Opposite SAT/UNSAT same root truncated signature | NOT FOUND |
| Branch-stable opposite SAT/UNSAT same h1/h2 | NOT ESTABLISHED |
| Connected n72 d21 SAT positive control | WITNESS VERIFIED, exact count unknown |
| All-n fixed-depth feature construction | n^O(h) structural calls, LP pivot issue unresolved |
| Growing h and universal poly geometric progress | NOT PROVED |
| Complete polynomial SCL SAT/UNSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |

**Next substantive proof obligation:** seek opposite-status
root twins that survive an ISOMORPHISM-INVARIANT depth1 test,
and/or prove genuine obstruction for a specified fixed
spectral grammar, preferably with large d and verified
nontrivial incidence separators. Avoid inferring universal
hardness from a negative bounded search.
