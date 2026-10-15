# R5 E4.1 — AFFINE_MACWILLIAMS_SOUNDNESS

**Date:** 2026-10-15. Proof-carrying successor to E3.5/E4, not a universal solver.
**Repo:** Hawkar-usls/Janus-Fundamentum
**Base:** draft PR #524 branch `research/r5-macwilliams-local-8-10-20261015`,
at verified HEAD `18013c4aae599804a106ddee025168f3a97d9255`.
**New branch:** `research/r5-affine-macwilliams-soundness-20261015`
(stack on #524; main unchanged).
**Input scientific proposal:** user's mathematical statement of the exact
coset signed-MacWilliams formula and need for a proof-preserving branch
expert. The mathematical reasoning below is independently checked by
the exhaustive finite code/coset controls described later.

## E4.1 Theorem A — exact coset MacWilliams (ALL n)

Let A be a legal square/cubic/linear SCL input with n columns and
rows, and let partial Boolean cube be x_Z=0, x_O=1,
Z∩O=∅. Set v=1+x, hence fixed v_Z=1 and v_O=0.
Let T=[n]\(Z∪O) and a=indicator(Z).
The free v_T must solve

`A_T v_T = A_Z 1 (mod 2)`.

If inconsistent this cube has no SAT assignments. Otherwise choose
ANY particular v0 and let L=ker_GF2(A_T), m=|T|,
d=dim L, r=rank(A_T)=m-d and R_T=row_GF2(A_T)=L^perp.

For every s=0,...,m define the SIGNED rowspace coefficient

`D_s=sum_{u in R_T, |u|=s}(-1)^(u⋅v0)`.

For every j=0,...,m, let C_j be the number of free affine
continuations of weight j. Krawtchouk inversion gives EXACTLY

`C_j = 2^(-r) * sum_s D_s*K_j(s;m)`,

where
`K_j(s;m)=sum_{h}(-1)^h binom(s,h)binom(m-s,j-h)`.

The full original kernel v has fixed weight |Z| plus free
weight j, so (for n%3=0),

`#SAT(A|cube)=C_(2n/3-|Z|)`.

The identity is exact, not a relaxation. It is equivalent to
the affine weight-enumerator transform / Fourier character
orthogonality.

### Soundness subtleties

1. **Signed D_s can be negative.** An all-n counterexample to
   copying the root D_s>=0 constraint to children is the finite
   AffinePlane9 cube x0=0, for which (D0,D1,D2,D3)
   =(1,-2,-2,6) and D8=-1.
2. **1_T belongs to R_T** because the XOR of all original
   rows restricted to T is 1_T (each original source column
   degree three). Consequently,
   `D_(m-s)=(-1)^|v0| D_s`. Equivalently the dual unsigned
   row spectrum B_s is symmetric; when |v0| odd the positive
   and negative signed components swap under complement.
3. **Homogeneous right-hand-side test:** C0=1 iff
   `A_Z*1=0`, otherwise C0=0. It is WRONG to test whether
   the *arbitrarily chosen* Gaussian particular v0=0; even
   homogeneous cosets may have a nonzero chosen v0.
4. Every homogeneous kernel word has EVEN weight because
   1_T∈R_T, so every affine continuation has a fixed
   parity |v0|. Any target weight of opposite parity is
   rejected immediately.
5. The free dimension d can be linear in n, so enumeration
   of 2^d is used only by the tiny finite CI oracle and
   never masquerades as an all-n polynomial expert.

## E4.1 Theorem B — sound affine two-sided LP (ALL n)

We distinguish TWO distributions:
- H_i≥0 counts kernel words of weight i in L (even i only).
- C_j≥0 counts coset words of weight j in v0+L (j has
  parity |v0|).
- P_s,M_s≥0 are formal rowspace counts with positive/negative
  character respectively.

Let |L|=2^d. For every s=0,...,m enforce

`sum_i H_i K_s(i;m)=2^d(P_s+M_s)`
`sum_j C_j K_s(j;m)=2^d(P_s-M_s)`.

Also enforce homogeneous H0=1, both total masses=2^d,
the first k EXACT affine binomial weight moments for C,
and exact low signed spectral counts P_s,M_s obtained
by enumerating support subsets |u|≤3 and checking
u∈R_T and sign (-1)^(u⋅v0).

P0=1,M0=0; at s=m the coefficients are determined by
parity |v0|. For a homogeneous free RHS C0=1,
otherwise C0=0. Because the true distributions are
feasible, maximizing target C_j gives a SOUND
upper bound on SAT continuations.

The LP has O(m) variables and O(m) constraints, exact
Krawtchouk coefficients with polynomial-bit integers.
It is a polynomial-size rational LP. Its mathematical
optimum is polynomial-time computable via general LP
algorithms; however the current implementation's exact
Fraction simplex has no established polynomial pivot
bound. Additionally, a polynomially generated local
moments/low-row-spectra proof does not imply universally
polynomial search completion on arbitrary SCL.

### Polynomial moment/low spectra construction for fixed degree

For a fixed k, compute
`sum_{v∈v0+L}binom(|v|,j)` by summing over the O(m^j)
subsets of free coordinates and counting affine seeds
with these coordinates =1 via exact GF2 rank checks.
Signed P_s/M_s for fixed s≤k are obtained by enumerating
O(m^s) sparse support vectors u, testing u⊥L and their
sign u⋅v0. No enumeration of 2^d needed for these inputs.

**Verifier:** exact primal masses, true affine moments,
every Krawtchouk equation s=0..m (not just low s),
nonnegative P/M, exact signed low weights, equality of
rational primal and dual objectives, and dual feasibility
for every LP variable, independently recomputed from
Gaussian bases and exact constraints.

## Implementation and finite CI oracle

- `experiments/r5_affine_macwilliams_soundness_20261015.py`
  computes partial-cube affine parameters and fixed-degree
  moments via GF2 restriction rank checks, plus exact
  signed low dual spectrum; implements exact LP and
  independent primal/dual checks.
- A DIFFERENT method `enumerate_affine_oracle` lists
  all 2^d words on tiny frozen controls ONLY, builds
  histogram C_j and independently obtains every D_s
  using inverse Krawtchouk; verifies all j and the
  sign/complement symmetry.
- Initial CI failures are retained in Actions history:
  a same-pass inverse-symmetry check referenced a
  future index; then a malformed newline in its patch;
  then the WRONG test `v0==0` for homogeneous
  restricted RHS incorrectly anchored C0 and generated
  infeasibility. These are corrected, NOT hidden.
- CI SUCCESS on final tests at
  [run 38720406774](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38720406774).

Exact finite LP degree2:
| Control | Cube x | True continuations | affine LP2 floor | negative D | D_m |
|---|---|---:|---:|---|---:|
| AffinePlane9 n9 | none | 3 | 3 | no | +1 |
| AffinePlane9 n9 | x0=0 | 2 | 2 | YES | -1 |
| AffinePlane9 n9 | x0=1 | 1 | 1 | no | +1 |
| HolyerK4 n18 | none | 6 | 10 | no | +1 |
| HolyerK4 n18 | x0=0 | 4 | 5 | YES | -1 |
| HolyerK4 n18 | x0=1 | 2 | 5 | no | +1 |

In addition the test checks the constrained x0=x2=0
cube on each source (and independently verifies true
counts / affine low spectrum). Full signed D spectrum
is used only in the independent finite oracle, NOT by
the polynomial-input LP.

## E4.1 Cooperative Neural Gearbox — actual descendants

- `experiments/r5_affine_macwilliams_cooperative_20261015.py`
  invokes the verified E4.1 LP independently on EVERY
  source cube when m>=4 and target weight feasible;
  tiny cases with <=3 free bits use exact <=8-word
  checks. It NEVER inherits a root D_s>=0 assumption
  or a root-unsigned spectrum as child constraints.
- A certified LP upper bound zero can PRUNE a cube,
  but a positive bound alone never establishes SAT.
- Every binary branch is an exact partition, local
  propagation rechecked from current immutable state;
  children receive NEW independently valid LP bounds.
  A measured decrease is marked only on numeric proof,
  not by calling the operation itself "progress".
- Bounded DFS and proof-policy SHA256 guard return
  UNKNOWN_RESOURCE_LIMIT with resumable frontier.
  A resource exhaustion is NOT UNSAT.
- Frozen HolyerK4 root: U_LP2 10→(5+5)=10
  (NO geometric progress); its x0=0 branch
  admits another certified split U_LP2 5→4
  (positive finite progress, NOT universal).
  The actual solution counts are 6 total, 4 in x0=0,
  and 2 in x0=1. [Integration CI SUCCESS](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38720647794).

## E4.2 / E4.3 pending

- A full rowspace spectrum determines full kernel
  weight enumerator exactly by MacWilliams, hence
  exact SAT count. Opposite SAT-status twins CAN
  share only TRUNCATED or otherwise incomplete
  supplied spectral/moment features.
- Existing seeded 30 connected n36 examples from
  PR #524: SAT 8, UNSAT 22, and 28 distinct joint
  root signatures; no matching opposite-status pair.
  This successor does NOT invent such a pair.
- A branch-stable twin needs canonical depth-1 (and
  higher) signatures re-evaluated on each restricted
  affine subsystem; correct matching must account for
  variable permutations, without presuming canonical
  labels.
- To claim structural hardness, separately measure
  girth/separators, low treewidth and locally
  enumeratable affine components. Connectivity alone
  is not an adequate difficulty certificate.

## Status
| Gate | Result |
|---|---|
| Exact affine MacWilliams formula | PROVED ALL n |
| Signed complement symmetry and potential D<0 | PROVED / FINITE CI |
| Fixed-k moments and signed low spectrum via rank queries | PROVED polynomial fixed k |
| Sound two-sided positive/negative LP on child coset | PROVED |
| Independently checked Fraction simplex primal/dual certificate | CI VERIFIED |
| Child-by-child proof-carrying exact DFS integration | CI VERIFIED |
| General polynomial total time for implemented Fraction simplex | NOT PROVED |
| Universal fractional progress / SAT-vs-UNSAT all legal SCL | NOT PROVED |
| Branch-stable SAT/UNSAT spectral twins | NOT FOUND |
| `SolveLinearCubicXSAT` deterministic n^O(1) | NOT CONSTRUCTED |
| P vs NP | OPEN |
