# R5 — Exact d(J5)=3; certified third-ply attempt on J7; eight-state colour-transfer compression

Date: 2026-10-12 (Europe/Kyiv). Research PR #516 remains DRAFT. Main unchanged.

## Source ancestry, CI, authority

Original checkpoint: `c3db026fc1909d49d090ac8326aa2946f2db0187`.
Earlier exact orbit-complete depth-two barrier:
https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38291137567
both J5/J7 SUCCESS. It proves that the **EXACT** frozen two-ply expert,
including all original source variables via four independently checked
S3+flower edge orbits, returns UNKNOWN for J5 and J7.

New source-replayed third-ply code:
`experiments/r5_universal_flower_three_ply_certified_saturation.py`.
CI: https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38292987243
Four separate matrix jobs correspond to J5/J7 x0=0/1. The branch
proofs rely ONLY on the existing `certified_failed_literal_closure`
and its independent source verifier. On a successful branch proof,
each forced pin is justified by a stored conditional UNSAT proof;
termination is by a source-proof-checked BASE_UNSAT or by two checked
child proofs under complementary Boolean values. Every accepted
SAT witness is checked against the ORIGINAL formula; UNKNOWN
is NEVER an UNSAT verdict. A tampered retained proof is rejected.

**Verified at time of memo write**: J5 x0=0 SUCCESS with UNSAT, 70
inner one-ply calls, 6 outer rounds, 5 FORCE events and terminal
refutation; J5 x0=1 SUCCESS with UNSAT, 61 inner calls, 7 rounds,
6 FORCE events and terminal refutation. Both have independent
negative-fake proofs rejected. Together they discharge x0 and
prove ORIGINAL J5/SCL90 UNSAT in our fixed three-ply proof system.
The precise hierarchy is d=1 Boolean/GF2 closure, d=2 full two-ply
lookahead over all variables, d=3 two nested literal choices followed
by one-ply closure with polynomial forced-pin restarts.

**Conclusion: minimal d(J5)=3 FOR THIS EXACT EXPLICIT HIERARCHY.**
This is NOT a lower bound for other proof systems and is not a
universal all-SCL polynomial algorithm.

J7 branch jobs have to be inspected after the ongoing independent
CI completes. Until then d(J7) has a proven lower bound d>=3 from
the full depth-two barrier but no claimed exact value here.
Do NOT turn job IN_PROGRESS into SUCCESS.

Conservative fixed-depth runtime estimate: one-ply source and
certified replay O(n^8) bit operations (prior audit); for each
conditional outer case, <= n accepted pins and <= 2n candidate
conditioned child calls in each round, so O(n^10) bit work before
bookkeeping/replay overhead, conservatively O(n^12).
Depth remains EXACTLY 3 regardless of n. A proof-carrying
conditional refutation tree can be stored as an event DAG of
FORCE and final DOUBLE_UNSAT nodes referencing existing source
proofs; inconclusive child probes need not be retained to certify
SAT or UNSAT. Proof size remains polynomial for fixed depth.

## NEW: independently authenticated proof compression on the ENTIRE flower family

Program:
`experiments/r5_universal_flower_27state_transfer_unsat_certificate.py`
Workflow:
`.github/workflows/r5-flower-27state-transfer-certificate.yml`
Initial exact CI #38293154138 SUCCESS; strengthened 8-state
quotient CI #38293344030 SUCCESS. Subsequent source-colour
automorphism tests require their own CI confirmation.

Let the colour alphabet be C={0,1,2}. At each block i let
L_i=(l_b,l_c,l_d) be the three incoming edge colours and
R_i=(r_b,r_c,r_d) outgoing edge colours. The three local spoke
colours p=(p_b,p_c,p_d) must be a permutation of C because the
cubic central vertex has one spoke of each colour. Each outside
vertex demands (l_j,p_j,r_j) be a permutation of C. Therefore
the exact local transition predicate is

  T(L,R) = EXISTS p in S3: for j=b,c,d, {l_j,p_j,r_j}=C.

It is a constant-size 27x27 Boolean matrix with 48 allowed
entries among 729, enumerated by an independent verifier. The
flower seam twists c and d, so a global 3-edge-colouring exists
iff there is a Boolean matrix path from s to t of length k
with s=twist(t), twist(b,c,d)=(b,d,c).

**Eight-state live quotient theorem**, independently checked
over ALL 729 ordered state pairs:
- Three equal inputs: no outgoing transition.
- Six all-distinct states: a transition preserves permutation
  parity D+ or D-. The twist REVERSES parity.
- Eighteen two-equal states: label by (singleton colour u,
  repeated colour r), u!=r. A transition preserves u while
  switching repeated r to the unique third colour different
  from u and r. The twist preserves both u and r.
Thus among 27 states exactly eight quotient classes are live:
D+, D-, and six ordered pairs E_(u,r). After odd k E flips
its r label an odd number of times, so no twisted closing;
D cannot ever satisfy twisted closing. Therefore for ALL
odd k>=5, there is NO proper 3-edge-colouring of Jk.
This is a finite local certificate plus symbolic induction,
NOT extrapolation from five finite k tests.

The authenticated negative expert validates exact input equality
to the complete original Holyer SCL make_scl(flower(k)), and
checks the 27-state transfer and 8-state quotient. It explicitly
rejects altered source equations. Historical check source n:
J5=90, J7=126, J9=162, J11=198, J13=234. Positive transfer
controls on even lengths 2,4,6,8 were checked (not disguised
as Jk graph constructors for forbidden small/other k).

Worst-case bit work for authenticated canonical flower inputs
is O(n) source validation plus O(k*27^3) Boolean dynamic
programming; 27 is independent of k. The symbolic quotient
proves the odd-length impossibility for arbitrary k, and
the finite automaton serves as an independently checkable
local arithmetic/colour proof.
**This is a REAL polynomial proof compression for an infinite
family, not the arbitrary all-SCL theorem.** The current
authenticator handles exact canonical flower source labelling;
no generic unproven polynomial graph-isomorphism-based
recognizer is invoked.

## Source-preserving S3 branch-discharge compression

An exact Holyer original formula has a global action of
all six colour permutations. The verifier checks each
permutation maps every source row bijectively to a source
row and maps original edge variables appropriately.
Every SAT witness chooses exactly one colour per edge.
Therefore if `F & X_(e,0)=1` has a verified UNSAT
certificate, any alleged witness W for F could be colour-
permuted into a witness with `X_(e,0)=1`, contradiction.
A single 1-pinned conditional UNSAT proof suffices to refute
the entire authenticated Holyer formula; the two
other edge-colour cases are obtained by an explicit
certificate-preserving group action, rather than repeated
source search. This is a valid proof-compression rule, NOT
an assumption that zero-valued bit cases are themselves
consequences. Authentication of S3 closure is essential.

For arbitrary SCL inputs without this checked symmetry,
both branches of an outer Boolean variable must still
be discharged individually.

## General compression theorem gate remains OPEN

For a general bounded-width boundary DP with separator
width w, a naive exact signature table has up to 2^w
Boolean boundary states (or 3^w for three edge colours).
Its work is polynomial **when** a source-preserving decomposition
with w=O(log n) is supplied or constructed in polynomial time,
but this condition has NOT been established for all SCL.
A constant interface does NOT bound internal atomic solving:
the repository already contains an NP-hard connected/atomic
Tanner reduction, and a two-port atomic interior hardness
graft. No general polynomial-size source-verified
proof compression has been built.

Related external theory: Atserias–Dalmau on resolution
width and pebble games; Ben-Sasson–Wigderson on
resolution size/width; Amarilli et al. on exponential
in treewidth lower bounds for structured knowledge compilation.
Such results do not prove P!=NP and cannot establish
an arbitrary-SCL lower bound by citation alone.

Scientific gates:
```
J5_MIN_DEPTH_EXACT_IN_SATURATING_HIERARCHY = 3 PROVED
J7_MIN_DEPTH = >=3 (check in-flight dedicated third-ply CI)
ISAACS_FLOWER_ODD_8STATE_AUTHENTICATED_UNSAT = PROVED
COLOUR_SYMMETRY_SOURCE_AUTOMORPHISM = CHECK IN CI
FLOWER_BOUNDARY_COMPRESSION = CERTIFIED_INFINITE_FAMILY
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED
P_VS_NP = OPEN
```
