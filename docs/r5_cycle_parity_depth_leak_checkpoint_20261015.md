# R5 E4.5 — CYCLE_PARITY_CERTIFICATE + DEPTH_ONE_SPECTRAL_LEAKAGE
**Date:** 2026-10-15.
**Provenance:** independently audited user-proposed moment-leak theorem, 2-lift
kernel exact sequence and cycle-obstruction mechanism against the actual
E4.4 GitHub implementations. Derived and checked new correction:
multiple ternary y with the SAME fixed nonzero z give the SAME voltage
cycle system and a single affine SAT locus (not a union); a union may
arise from several distinct nonzero z when dim ker H>1.
**Parent:** stacked [PR #528](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/528),
head `df63eaa1ce57f3de82244bfbb3d49906604d720c`.
**Main at beginning:** `62a6aa5703bfb9120b3e278b84d2acd993d37133`;
not merged/modified here.

## E4.5.A Exact 2-cover kernel sequence (ALL n)

Let a connected legal square/cubic/linear SCL base A have r=rank_GF2(A),
d=n−r, full right kernel basis K and full left kernel basis L.
A graph two-cover specified by source edge incidences A0+A1=A
has
`Atilde=[[A0,A1],[A1,A0]]`, with
`rank Atilde = 2r + rank H`, `H=L^T A0 K` (E4.4).
Under invertible linear coordinate changes, a lift kernel
element maps to
`z=x^(0)+x^(1) ∈ ker A`, satisfying H z=0,
while the fiber over z is an affine copy of ker A.
This gives an exact short sequence of GF2 vector spaces:

`0 -> ker A -> ker Atilde -> ker(H acting on ker A) -> 0`.

In coordinates via K, H is a d×d matrix. The last kernel
is represented by vectors `K*c` with `H*c=0`;
it does NOT mean that arbitrary n-dimensional kernel vectors
are inserted uncoordinated into the d×d matrix.

When the connected base is UNSAT, a lift SAT witness cannot
have z=0: x^(0)=x^(1) would force a valid original SAT witness.
Thus if dim ker H=1, ALL SAT lift witnesses in a fixed-H fiber
have the SAME nonzero sheet-XOR `z_star`.

## E4.5.B Integer y, cubic support graph, exact cyclic criterion (ALL n)

For a fixed nonzero `z∈ker A`, define

`Y_z={y∈{0,1,2}^n: Ay=2*1 (over integers), y mod2=z}`.

Each source row intersects support(z) in either 0 or 2
columns. With exactly two selected support columns j,k,
the row must have y_j=y_k=1, y_third=0. With zero
support columns, its row y-values must be a permutation
of (2,0,0). The former rows define a simple cubic
graph G_z on the support(z): 3 incidences per source
column and no pair repeats (linearity of SCL).

Let `sigma_(i,j)` be voltage of original row incidence
(i,j) and `lambda_j` the selected sheet when y_j=1.
A lifted pair of rows for i is Exact-One iff

`lambda_j + lambda_k = 1 + sigma_(i,j)+sigma_(i,k) mod2`

for each G_z edge e=(j,k;i). The equations are consistent
iff for EVERY graph cycle gamma:

`sum_{e=(j,k;i) in gamma} (1+sigma_(i,j)+sigma_(i,k))=0 mod2`.

It suffices to impose a fundamental cycle basis; one can
find this using a spanning forest in polynomial time.
With c graph components, every consistent system has
exactly 2^c sheet-label assignments. The equations
depend on z and sigma ONLY, not on the particular y∈Y_z.

**Sharper than the initial proposal:** even when |Y_z|>1,
the SAT voltage locus for this FIXED z is still ONE
(possibly empty) affine GF2 subspace; when compatible,
the exact number of SAT lifted assignments with this z is

`|Y_z|*2^c`.

If dim ker H=1 and base is UNSAT, z_star is the ONLY
possible nonzero sheet-XOR, so the FULL SAT locus in
the fixed-H gauge quotient is either empty or one
affine GF2 subspace, irrespective of |Y_z|. The
cardinality of Y_z controls the multiplicity of
SAT solutions, not the affine shape of the locus.

**If dim ker H>1**, distinct nonzero z may each
contribute a different affine voltage locus. The
union need not itself be an affine subspace.
This is the correct general caveat.

Gauge edge flips (sheet relabelings at row/column
vertices) preserve the cycle equations. Restricting
these linear conditions to a non-gauge basis of
ker Phi / gauge yields a GF2 matrix Psi whose kernel
is precisely the compatible orbit-index set when
sigma0 is already SAT. Its codimension is rank Psi.

## E4.5.C Frozen full-rank cycle certificate (CI VERIFIED)

Source: `experiments/r5_cycle_parity_certificate_20261015.py`.
It REBUILDS the original connected UNSAT SCL36 source
from frozen seed, 64-word finite UNSAT proof, ternary y
witness and signs of the SAT cover. It INDEPENDENTLY:
1. Constructs actual obstruction `H=L^T A0 K` from
   incidence voltage bits; verifies rank(H)=5 and
   computes its one-dimensional right kernel.
2. Converts the unique nonzero H-kernel coordinate
   to physical `z_star∈ker A` and checks all base
   parity rows directly. Result `|z_star|=20`.
3. Builds simple cubic G_z with 20 vertices, 30
   edges, 1 connected component. Counts 11
   fundamental cycles (30−20+1).
4. Forms all 11 parity equations in incidence-voltage
   bits; pulls them back to the exact 11-dimensional
   quotient basis, obtaining **rank(Psi)=5**.
5. The source SAT cover was exhaustively verified
   to have exactly TWO witnesses, so because G_z
   has c=1 and every feasible y yields exactly2,
   `|Y_z|=1` is **proved** from this independent
   exact count, not guessed from the solver's first y.
6. Predicts `2^(11-5)=64` SAT classes and 1984
   UNSAT classes. Reruns a SEPARATE exact 128-word
   GF2-affine SAT oracle for ALL 2048 quotient classes:
   **0 disagreements.** Every one of the 64 SAT
   covers has EXACTLY 2 witnesses. The other
   1984 have EXACTLY 0.

This upgrades the prior finite exhaustive classification
to a short algebraic prediction using FIVE independent
cycle conditions. Computing |Y_z| may remain hard in
general; this frozen certificate does NOT imply a
polynomial SAT algorithm for arbitrary square/cubic
linear Exact-One source A.

Raw JSON includes original y, z_star, fundamental
cycle incidence masks, all 11 Psi row vectors,
rank evidence, and exact full-orbit check counts,
with no lossy float encoding of large GF2 masks.

## E4.5.D All-n depth-h moment leakage theorem

For ANY binary family C⊆{0,1}^m (linearity not required),
its binomial weight moment is
`M_q(C)=sum_{x∈C}binom(|x|,q)`.
Fix a subset I of h distinct coordinates to ones and
delete them, giving `C_(I,1)^-I`.
Double count pairs (word, h-subset among its ones):

`sum_{|I|=h} M_q(C_(I,1)^-I)
 = binom(q+h,h) * M_(q+h)(C)`.

Because each word of weight w contributes
`binom(w,h) binom(w-h,q)=
  binom(q+h,h)binom(w,q+h)`.

At h=1, q=2:

`sum_i M_2(C_(i,1)^-i)=3 M_3(C)`.

This is an exact all-n theorem about binomial
moments, NOT power moments. A sequence of all
value-labeled depth-h child moment profiles
of degree≤k therefore reveals the root
moment degree k+h.

**Additional all-n observation:** the ACTUAL E4.2
unlabeled all-variable branch grammar retains the
free **kernel-complement parity** of each child.
At a parent with fixed-Z parity p, the child
x_i=1 has parity p while x_i=0 has parity
p XOR 1. Thus even an unordered child pair
can recover which child is the x_i=1 branch.
Inductively, a full unordered multiset of all
such parity-tagged branch pairs at depth h
still reveals the sum of the all-ones h-subsets.
Therefore the depth-h necessary root-moment
condition also holds for THIS SPECIFIC
parity-tagged unlabeled grammar. It need
NOT hold for arbitrary feature representations
that erase parity/value tags, nor for only one
chosen branch per parent.

## E4.5.E Explicit degree2 SCL72 spectral-twin leakage

Source: `experiments/r5_branch_moment_leakage_20261015.py`.
Frozen matched root orbit classes 0 (SAT2) and
13 (UNSAT0) from E4.4 have equal rank65,
nullity7, B0..B2 and A4/A6/A8/A10. It
independently enumerates the 128 parity-solution
x=1+ker A words on each cover; computes
moments M0..4 by direct combinatorics, signed
D0..4 by inverse Krawtchouk, and root
B0..4 by complete kernel histogram.
Checks `D_s=(-1)^s B_s` exactly.

At m=72, d=7, for two instances with
matching B0..B2, signed-Pless implies

`Delta M3 = 16 * Delta B3`.
Combined with the h1 identity:

`Delta sum_(i=1)^72 M2(C_(i,1)^-i) =
   48 * Delta B3`.

The exact regression obtains (SAT minus UNSAT):

`Delta B3=-16`;
`observed Delta child-summed M2=-768`;
`predicted 48*(-16)=-768`.

It also checks all 6 combinations h∈{1,2},
q∈{0,1,2} separately by enumerating the
selected coordinate sets. The value-labeled
child sum is independently reconstructed
from UNLABELED child pairs that retain the
free-coset parity tags; the recovered total
is exactly the same. This demonstrates
which interface information makes the
higher-moment leak observable.

The full E4.4 2048-class fixed-Phi orbit is
RECHECKED and has NO opposite-status pair
matching B0..B3 and root anchors. Therefore,
by the all-n leakage theorem, **NO opposite
SAT/UNSAT depth1 twin exists in this orbit
for the specified ALL-BRANCH parity-tagged
degree2 signed-affine grammar**. This finite
conclusion does not constrain a new base,
a different rank fiber, or a weaker grammar
that discards parity/value information.

## Reproduction

```bash
python3 experiments/r5_cycle_parity_certificate_20261015.py --self-test
python3 experiments/r5_branch_moment_leakage_20261015.py --self-test
```

Workflow: `.github/workflows/r5-cycle-parity-depth-leak.yml`
does independently rerun the 2048-class 128-word
exact SAT classifications via cycle constraints,
and exact moment leakage tests and full 2048
k3-bucket prescreen. Both resulting JSON
certificates are uploaded as GitHub Actions
artifacts with explicit retention time
(90 days); the scripts and this mathematical
checkpoint remain permanently versioned
in the branch.

## Strict provenance-aware gates
| Gate | Verdict |
|---|---|
| Fixed-z cycle parity iff existential SAT sign constraint | PROVED ALL n |
| Fixed-z SAT-voltage locus affine regardless of Y_z multiplicity | PROVED ALL n |
| Multiple nonzero z may give non-affine union | GENERAL CAUTION |
| One-dimensional ker H for frozen base | VERIFIED |
| Unique nonzero z_star of weight20 | VERIFIED |
| G_z connected (20 vertices, 30 edges, 11 cycles) | VERIFIED |
| Psi rank5 over GF2 | VERIFIED |
| Exact 64 SAT/1984 UNSAT predictions over 2048 classes | CI VERIFIED / ZERO MISMATCH |
| Every SAT cover has exactly2 witnesses | CI VERIFIED / PROVED for frozen orbit |
| Depth-h all-ones binomial-moment identity | PROVED ALL n |
| Parity-tagged unlabeled full branch profile retains leakage | PROVED FOR SPECIFIED GRAMMAR |
| Explicit n72 pair Delta child sum =48 Delta B3=-768 | CI VERIFIED |
| Opposite-status root B0..3 match in fixed orbit | NOT FOUND in exhaustive 2048 |
| Opposite-status depth1 twin within same full grammar/fixed orbit | RULED OUT FOR THAT FINITE ORBIT |
| New base with matched B0..3 and depth1 signatures | OPEN |
| Uniform polynomial SAT solver for arbitrary SCL | NOT CONSTRUCTED |
| P vs NP | OPEN |

Next legal research gate: select another connected UNSAT
base with ternary Ay=2 witness and nontrivial
fixed-Phi gauge quotient; derive its Psi row
rank before expensive enumeration. Seek
opposite-status cover pairs with matching
B0..B3, A4..A10, and actual parity-tagged
depth1 profiles. Enforce independently certified
UNSAT and direct SAT witness, and do not
confuse a finite feature-grammar obstruction
with a universal lower bound or P=NP solution.
