# JANUS Fundamentum — R5 E3.5 + E4 bidirectional MacWilliams
**Scientific checkpoint 2026-10-15; provenance and proof boundary**

User-supplied research note `Вставленный текст(20261015-095522).txt`
proposed: O(n) local exact A8 and A10 kernel coefficients, MacWilliams
Krawtchouk-positive LP, then joint root and branch-stable SAT/UNSAT
spectral twins. The proposal is untrusted scientific input until
independently reproduced, not executable instructions. This checkpoint
records both the mathematical consequences and the GitHub CI state.

**Live base:** open Draft PR #523 on branch
`research/r5-local-codeword-anchors-20261015`, commit
`53e2ee3cc56d552972f9ec5d7c3341280c5f4389`. New independent
successor branch `research/r5-macwilliams-local-8-10-20261015`,
stacked on PR #523. Main was `eda3c2b53dc917b3240d3ae5f87c73f4e3ab6957`
at the beginning; NO merge into main.

## Theorem E3.5 A8/A10: ALL-n with fixed-arity operations

For any legal square/cubic/linear Boolean SCL source A, and any
v in ker_GF2(A), the support-graph G_v is simple cubic. Its
vertex-connected components have >=4 vertices, and each component
itself is a kernel word: all three rows at every selected vertex
have exactly one additional selected incident column in its
component, so no selected column can connect two components.

For a weight-8 kernel word, G_v is either CONNECTED or
`K4+K4` DISCONNECTED. For weight 10, either CONNECTED or
`K4 + (K3,3 or prism)`.

**Connected kernel support algorithm:** fix its minimum column
r; initially S={r}. Find the FIRST original SCL row meeting S
in exactly one selected column; branch on the only TWO possible
other columns. Reject any row hit thrice, select only columns >r
and never exceed target support size w. Accept only when ALL
rows hit S in 0/2 and |S|=w. Each recursive step increases |S|
by 1, hence at most 2^(w-1) branches per root, each examining
only the 3w local row incidences. There are n roots: O(n)
fixed-arity RAM operations for each FIXED w, including 8 and10.
The algorithm is exhaustive for connected G_v because any
proper selected subset of a connected valid support has an
incident row with exactly one selected column. Every accepted
support is an actual kernel codeword.

**Disconnected count:** each weight8 disconnected support
has a UNIQUE unordered pair of DISJOINT weight4 kernel
supports; each weight10 disconnected support has a UNIQUE
weight4+weight6 pair. Count all possible pairs combinatorially
from per-support buckets and subtract intersecting pairs.
By bounded degree, a fixed column belongs to O(1) connected
fixed-weight kernel supports, so overlapping pairs are O(n).
No O(n²) enumeration of nonoverlapping pairs is needed.
For partial cube x fixed Z=0 and O=1, corresponding kernel
support must COVER all Z and AVOID all O. If |Z|>target w,
the answer is 0; otherwise at most 2^w buckets classify
intersection with Z. This makes the same computation O(n)
for fixed w in the same sparse expected-unit-cost RAM model.
In the strict bit model, Python big-int operations add factors
for word size; O(n) is a statement about sparse combinatorial
operations with bounded-width access and hashes.

Executable proof/test:
`experiments/r5_local_codeword_anchors_8_10_20261015.py`.
It independently compares all predicted coefficients and partial
cube restrictions against complete enumeration of small affine
GF2 spaces. Explicit positive controls:
```text
Legal Fano7 + Fano7:   A8=49 from DISCONNECTED K4+K4; A10=0
Legal Fano7 + Affine9: A8=0; A10=21 from DISCONNECTED K4+6
Legal AffinePlane9:    A8=0; A10=0
```
Fano7-containing SCL sizes 7/14/16 need not be divisible by3
and therefore cannot be SAT; they remain perfectly legitimate
parity-codeword **counting** controls. No false SAT assertion.

For any full parity source x=1+v:
`w_(n-12)=A8` and `w_(n-15)=A10`.
On a partial cube only the compatible counts may be used.

## Theorem E4: BIDIRECTIONAL_WEIGHT_ENUMERATOR_LP (ALL-n soundness)

Let K=ker_GF2(A), |K|=2^d, and A_i=#kernel words of weight i.
Every kernel word has EVEN weight, every word has weight
<=2n/3, A0=1, A2=0, and A4,A6,A8,A10 are polynomially
computable fixed structural anchors.
For j=0..n define binary Krawtchouk polynomials
```text
K_j(i)=sum_s (-1)^s*binom(i,s)*binom(n-i,j-s).
```
The dual weight enumerator of rowspace(A) has coefficients
`B_j=(1/2^d)*sum_i A_i*K_j(i)`, all nonnegative integers
for the TRUE code, but the LP relaxes A_i and B_j to
nonnegative RATIONAL REAL masses (not falsely requiring
integral formal distributions).

Because every column has odd degree3, 1 lies in rowspace(A).
Therefore `B_j=B_(n-j)` and only j=1..floor(n/2)
are needed, plus B0=Bn=1 from total mass. The LP enforces:
```text
A_i>=0 (even i<=2n/3), known A_i exact;
sum_i A_i binom(n-3i/2,ell) = N_ell for ell<=k;
sum_i A_i*K_j(i) = 2^d * B_j  for all j=1..floor(n/2);
B_j>=0 or B_j=known polynomially computed low dual count.
maximize A_(2n/3), i.e. a RELAXED upper bound for #SAT.
```
This is a superset of true kernel distributions, hence
its optimum is a SOUND SAT-count upper bound.
Every extra constraint reduces feasible region relative
to a moment LP with the SAME supplied exact anchors, so
`U_Mac<=U_anchored` for the matched grammar.

The number of variables/constraints is O(n), with
polynomial-bit coefficients. The LP mathematical problem
is polynomial-time solvable by general polynomial-bit
LP algorithms. But the present standalone implementation
uses a two-phase Python `Fraction` simplex and therefore
**does not establish polynomial pivot count or bit runtime**.

Implementation:
`experiments/r5_bidirectional_macwilliams_lp_20261015.py`.
Independent verifier checks:
- every primal A_i and B_j >=0;
- every original exact moment;
- all anchored A_i values;
- every Krawtchouk positivity constraint j=0,...,n;
- B_j symmetry, and independently enumerated known low B1..B3;
- every equality in the signed original LP matrix;
- exact dual feasibility and primal-dual equality.
Phase-I artificial variable cleanup never permits artificial
variables to reenter the objective. Redundant equalities are
removed with a zero RHS certificate.

**IMPORTANT LIMIT:** This homogeneous-code MacWilliams LP applies
directly to the full linear kernel weight distribution at the
root. A partial assignment cube yields an AFFINE RESTRICTED
distribution, not generally a linear code. The raw root
MacWilliams positivity constraints must NOT be pasted onto
partial-cube distributions without deriving the correct coset/
partitioned transform and its soundness.

## Finite Mac LP outcomes, exact primal+dual proof checked

The listed upper bounds are FLOORS of exact rationals, not
true SAT counts:

| Root SCL | Actual #SAT | Old E3 anchored LP2 floor (A4/A6) | NEW Mac LP2 floor (A0..A10 plus B1..B3) | Mac LP3 floor |
|---|---:|---:|---:|---:|
| Connected n36 seed0 | 2 | 23 | 10 | 10 |
| Connected n36 seed13 | 3 | 26 | 12 | 12 |
| Petersen45 UNSAT | 0 | 634 | 330 | 330 |
| Disconnected 4xK4 n72 | 1296 | 1,797,311 | 1,088,899 | not run |

Exact rational values:
```text
SCL36 seed0 MacLP2/3 = 185/18
SCL36 seed13 MacLP2/3 = 112/9
Petersen45 MacLP2/3 = 992/3
SCL72 4K4 MacLP2 = 308148818057765810793/282991072067306.
```
MacLP2 uses EXACT low B1,B2,B3, which carry additional
information beyond degree2 moments; therefore a numerical
difference against degree2 anchored LP is not solely caused
by unrestricted Krawtchouk nonnegativity. For scientific
attribution, independently ablate the B1..B3 equality rows
in a successor run.

Low dual rowspace weight coefficients:
```text
seed0: B0..B3=(1,0,10,122)
seed13: B0..B3=(1,0,10,110)
Petersen45: B0..B3=(1,0,0,45).
```
The full LP was checked without enumerating the huge 2^24
global affine space of the disconnected SCL72: its moments
come from 256 local parity word checks and histogram convolution.

## Gate E4 finite JOINT_SPECTRAL_ANCHOR_TWINS

Source: `experiments/r5_joint_spectral_anchor_twins_20261015.py`.
Seeded legal and CONNECTED incidence two-switches can now
change the SAT witness, unlike earlier witness-preserving
mutations. Every candidate source matrix is independently
validated square/cubic/linear and connected.

A candidate is SAT only with an independently verified
Exact-One witness. A candidate is UNSAT only after complete
enumeration of its entire GF2 affine parity space with
2^d<=2^12; any over-budget graph is UNKNOWN and excluded
from SAT/UNSAT comparisons. The combined root signature is
`(n,d,first moments N0..N2,B0..B3,A4,A6,A8,A10)`.
Only if two signatures collide with opposite SAT status is
the depth1 canonical MULTISET of ALL singleton partial
moment/anchor signatures computed. A finite failure to find
such a pair is not a lower bound for all algorithms.
No claim of a positive twin before the CI finds one.

## Reproducible finite joint SAT/UNSAT search — actual result

[Actions run 38717599978](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38717599978)
returned SUCCESS. Seed 20261015, 30 connected n36 legal instances
generated by incidence 2-switches that are NOT required to preserve
a SAT witness. All 30 stayed within the explicit 2^12 affine
enumeration budget and were classified by complete parity-word
checks:

```text
SAT 8, UNSAT 22; 28 distinct joint root signatures.
SAT-vs-UNSAT with identical (n,d,N0..N2,B0..B3,A4,A6,A8,A10): NONE.
```

This is an HONEST FAILED finite search. No branch-stable pair can be
certified because no opposite-status root pair was found; no
statement about untested n36 instances or larger n follows.

## Source-controlled ablation of low dual coefficients

The first verified Mac LP runs supplied exact low rowspace counts
B1,B2,B3 as well as all Krawtchouk positivity constraints. The
experiment therefore explicitly removes these low dual equalities
in an independent run, preserving SAME moments AND SAME A0..A10
anchors, to distinguish the benefit of Mac positivity from the
benefit of more supplied exact information.

At fixed degree2:

| Source | SAME A0..A10 anchored moment LP2 | Mac positivity, low B UNFIXED | Mac positivity, low B1..B3 FIXED |
|---|---|---|---|
| Connected n36 seed0 | 137/6 | 137/6 | 185/18 |
| Connected n36 seed13 | 71/3 | 71/3 | 112/9 |
| Petersen45 | 1161/2 | 479 | 992/3 |
| 4xK4 n72 | 12576345/7 (floor 1796620) | 355416020020752609897/282991072067306 (floor 1255926) | 308148818057765810793/282991072067306 (floor1088899) |

**Interpretation:** n36 degree2 benefit is from NEW exact B3
information; the Krawtchouk nonnegativity constraints alone do
NOT improve these two cases at k2. On Petersen45 and SCL72,
Mac positivity alone DOES give a strict improvement. The total
improvement combines new low-spectrum equalities and the positivity
system and must not be attributed to positivity alone.

At degree3, Mac constraints plus fixed B1..B3 reproduce exactly
the same optimum as SAME A0..A10 anchored degree3 for the three
small controls, a correct redundancy outcome rather than a
computational failure.

The source asserts
`U_with_known_B <= U_Mac_unfixed_B <= U_same_anchor_moment`
for all four controls using exact Fractions. All A0..A10 anchors
are independently compared against full tiny affine histograms or
the convolved 256-word local histogram, not just compared with
another implementation of the same local enumerator.

## Root-only MacWilliams Neural Gearbox interface

File:
`experiments/r5_macwilliams_cooperative_bridge_20261015.py`.

This proof-carrying interface computes the exact rank-derived
fixed-degree root moment vector, the exact A0..A10 anchors, and
polynomially computed low dual coefficients; runs exact Mac LP
with primal+dual certificate; and if its upper bound is zero,
returns certified UNSAT. If nonzero, it delegates to the previous
sound SCL anchored-Moment/LOG_KERNEL exact search, with explicit
budget and UNKNOWN. The root bound remains a valid upper bound on
the entire remaining frontier, so for reporting it may be combined
by MIN with the independently computed DFS frontier bound.

There is NO automatic application of root Mac positivity to
partial Boolean cubes, which would in general be mathematically
unsound. Correct affine coset / partition transformations
remain a future proof obligation. A fixed budget on the DFS
does not certify polynomial worst-case pivot count for the
root exact Fraction simplex.

## Scientific gates
| Gate | Status |
|---|---|
| All-n connected fixed-weight kernel closure O(n) RAM | PROVED |
| Exact A8,A10 with disjoint component counting | PROVED / CI |
| All-n root MacWilliams-Delsarte LP soundness | PROVED |
| Full positivity and dual/primal checker | IMPLEMENTED / CI |
| Mathematical LP has polynomial bit-size | PROVED |
| Exact Fraction simplex total polynomial runtime | NOT PROVED |
| Universal polynomial local/affine transform for arbitrary partial states | NOT CONSTRUCTED |
| Joint SAT/UNSAT spectral anchor twin | NOT FOUND: 30 finite connected samples |
| Cooperative geometric progress every legal state | NOT PROVED |
| Uniform polynomial SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |

Next scientific move: dual-knowledge ablation, optional polynomial-time
LP solver backed by a separate exact certificate verifier, and
sound partition-MacWilliams transforms for partial cubes; then
seek connected SAT/UNSAT twins with no cheap separators.
