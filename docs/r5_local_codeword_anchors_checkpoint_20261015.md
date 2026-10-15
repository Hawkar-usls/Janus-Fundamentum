# R5 — Gate E3 LOCAL_CODEWORD_ANCHORS / ANCHORED_MOMENT_LP
**Scientific date: 2026-10-15.**
**Provenance:** Derived from the user-provided mathematical proposal to use simple-cubic support graphs of kernel words and local Pasch/6-vertex configurations, then independently implemented and CI verified. Stacked successor to draft [PR #522](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/522) at frozen base HEAD `26a15cac2e1c3351b9ed1c9cf2934ddb11b7e01e`. Current main at initial read `eda3c2b53dc917b3240d3ae5f87c73f4e3ab6957`, left unchanged.

## Theorem E3.1 — support graph of a parity-kernel word (ALL n)

Let A be a legal linear/cubic square SCL incidence matrix: every
row and column has exactly 3 ones; two columns meet in <=1 row.
For a nonzero v in ker_GF2(A), let S=supp(v). Since every row meets
S in 0 or 2 columns, the graph G_v with vertex set S and an edge
for every original row meeting S in two columns has degree 3 at
each vertex. If two selected columns shared two rows, the source
would violate linearity. Thus G_v is SIMPLE and CUBIC.

The sum of all kernel parity equations implies |S| is even:
0=1^T Av=(1^T A)v=1^T v (mod 2). Hence:
- |S|=2 cannot occur (simple cubic min four vertices).
- |S|=4 forces G_v=K4, the Pasch support configuration.
- |S|=6 forces a CONNECTED simple cubic graph on six vertices:
  two cubic components would require >=8 vertices. The only
  six-vertex simple cubic graph types are K3,3 and the triangular
  prism. Independent verifier checks that the support graph has
  every vertex degree 3 and 0 or 2 triangles respectively.

Denote `A_w=# {v in ker_GF2(A):|v|=w}`. The parity solution
space is exactly `C=1+ker_GF2(A)`. For each `x=1+v`:
`t(x)=n-(3/2)|v|`, where t=#source rows evaluating to 111.
Therefore `w_n=1, w_(n-3)=0, w_(n-6)=A4,
w_(n-9)=A6`.

This equality holds for FULL parity space; under a partial
Boolean x-cube (Z bits fixed0, O bits fixed1), the respective
kernel word v must obey `Z subset supp(v)` and
`supp(v) cap O=empty`. Consequently
`w_n(C)=1 iff Z is empty`; `w_(n-3)(C)=0`;
and the other anchors are EXACT COUNTS of locally enumerated
A4 and A6 wordsets passing the fixed-bit filter. The data
are NOT inherited indiscriminately from the root.

## Theorem E3.2 — linear candidate counting (ALL n, fixed weights)

Define H the graph of intersections of source columns. From degree
3 and source linearity, every column has exactly 6 distinct
neighbors in H. Every kernel support S is a 3-regular graph G_v
inside H.

- To enumerate A4, for each of n roots v enumerate at most
  C(6,3)=20 neighbor triples and keep those with minimal vertex
  v. Validate each 4-word locally. O(n) candidates.
- To enumerate A6, every G_v is CONNECTED. Enumerate connected
  size-6 subsets of H by expanding from their smallest vertex,
  never adding a smaller vertex. With |H|-degree=6 and fixed
  subset size, each root generates at most a CONSTANT number
  of distinct partial connected sets. Check each candidate's
  parity. Thus O(n) candidates and O(n) local checks.

The implementation uses a sparse O(n) *expected* RAM validator
over the n constant-length source rows: column-degree counts and
a hash set of the 3 source-variable pairs per row detect exactly
the forbidden double intersections. For each candidate v, only
the 3*|v| incident rows are examined to verify Av=0, rather
than re-scanning all n rows. This prevents hidden O(n^2) work
in the local kernel check. Python packed big-integer bit tests
and hashing have implementation-level bit costs; the strict
O(n) claim is for fixed-arity combinatorial operations in a
standard unit-cost RAM / expected O(1) hash model, not for every
Python machine-bit instruction in the worst case.

Independent finite CI oracle enumerates all affine parity
states on AffinePlane9, Holyer-K4, K4x2, Petersen45 (d12),
and both connected n36 Gate-D twins (d7). At each control
it checks exact local counts against full affine enumeration.
Four partial cubes including fixed0/fixed1 conditions are
independently rechecked on each twin.

## Theorem E3.3 — girth anchors (ALL n)

In the bipartite row-column incidence graph B_A each G_v
cycle of length ell maps to an incidence cycle of length 2ell
(with distinct rows and columns, by source linearity). If
`girth(B_A)>=10`, every G_v has girth >=5.
A simple cubic graph with girth >=5 has >=1+3+6=10 vertices
(Moore BFS bound), so **A4=A6=A8=0** on the full source and
in every restricted cube. Hence fixed masses w_(n-6),
w_(n-9),w_(n-12) are zero. The program computes this
sufficient condition by BFS limited to depth 4 in the
bounded-degree incidence graph, visiting O(1) vertices per
root and thus O(n) RAM operations. A FALSE girth test does
not imply any anchor is nonzero.

Current two connected Gate-D twins do NOT have girth>=10;
the CI does not misapply a girth-zero anchor to either.

## Theorem E3.4 — rational anchored LP

Given exact binomial moments
`N_j=sum_{Ax=1 mod2} binom(t(x),j)` for j<=k,
and any finite anchored map t→known exact integer mass w_t,
remove these masses from each moment constraint:
```text
R_j = N_j - sum_{a anchored} w_a * binom(a,j).
```
Primal: maximize unknown `w_0` over NONANCHORED support
t in {0,3,...,n}, subject to
`sum_unanchored w_t binom(t,j)=R_j`, w_t>=0.
Dual: minimize `sum_j lambda_j R_j` with
`q(t)=sum_j lambda_j binom(t,j)>=1[t=0]`
only on NONANCHORED t. Anchors are already fixed exactly.
Both sides use Fraction arithmetic. Before acceptance,
the checker verifies nonnegative primal masses, original
moment equalities *including all anchors*, every dual
inequality, complementary slackness, and exact equality
of primal and dual objectives. This is a certified optimal
degree-k bound for the given moments and anchors.

Fixed k<=5 is polynomial *provided moments are obtained
in polynomial time*. The all-n fixed-degree rank restriction
method from PR #521 computes degree-k binomial moments in
O(n^k poly(n)) for fixed k. The current finite numeric
regressions for k4/5 use d<=12 finite affine enumeration,
or certified convolution of small components, rather than
pretending that 2^d enumeration is polynomial for all SCL.

## Independent manual Gate-D certificate, k=2

For each connected n36 twin the raw binomial moments are
N0=128, N1=1152, N2=6624 (raw power M2=14400).
Removing the known t36 state leaves
R0=127, R1=1116, R2=5994 in the binomial basis.
The rational polynomial
`q(t)=(1-t/9)(1-t/12)` is >=1[t=0]
on the remaining grid (w33=0).
Its exact objective is **94/3**, matching a formal primal
nonnegative mass distribution:
```text
 t=0:94/3, t=9:32/3, t=12:85, t=36:1.
```
This proves ANCHORED_LP2 optimum = 94/3 (floor31).
A full independent rational simplex reproduces it in CI.

Since q(30)=7/2 and q(27)=5/2,
for each pair instance there is an additional valid bound:
```text
6*#SAT+21*A4+15*A6<=188.
```
This inequality is a feasible q certificate, and is
NOT generally claimed to be the OPTIMUM when A4/A6 are
fixed. The optimal LP independently recomputes the bound.

## Exact first experiment: both connected SCL-36 spectral twins

Construction: connected legal n36 source from prior PR #522
using the frozen witness-preserving row-column swaps
with seed 0 and seed 13. Independent local-versus-affine
counts in GitHub Actions:
```text
                          seed0             seed13
GF(2) nullity             7                 7
raw binomial N0,N1,N2     128,1152,6624      identical
signed dual spectrum k2  (1,0,10)          identical
A4                        0                 0
A6                        3                 2
girth(B)>=10?             NO                NO
true SAT count            2                 3
manual anchored q bound  23                26
```

The weight-6 anchor A6 SEPARATES the previously
indistinguishable LOW-MOMENT pair. Thus this pair is
NOT a spectral twin for the joint (moment2, A4/A6)
representation. This does NOT produce a SAT/UNSAT
indistinguishability pair: both are SAT.

Fully optimal rational LP integer bounds after all E3
anchors (w_n=1,w_(n-3)=0,A4,A6):

| k | seed0 exact LP | floor | seed13 exact LP | floor |
|---|---|---:|---|---:|
|2|143/6|23|79/3|26|
|3|267/16|16|143/8|17|
|4|293/45|6|407/45|9|
|5|109/20|5|25/4|6|

Old UNANCHORED degree2 LP was 176/5 (floor35)
for both; the anchored degree2 LP with only w_n,w_(n-3)
was 94/3 (floor31) for both.

## Independent Petersen45 and DISCONNECTED SCL72 controls

| k | Petersen45 old LP | E3 anchored LP | SCL72 old LP | E3 anchored LP |
|---|---|---|---|---|
|2|640|1269/2 (floor634)|12582912/7|12581181/7 (floor1797311)|
|3|480|420 (floor420)|1310720|42467799/35 (floor1213365)|
|4|1352/7|1275/7 (floor182)|1835008/5|1832059/5 (floor366411)|
|5|3088/21|8640/77 (floor112)|6569984/25|5901843/25 (floor236073)|

Petersen45: A4=0 and A6=0, known w_n and w_(n-3)
are still useful and anchored LP benefits at higher k.
SCL72 consists of four independent Holyer-K4 blocks
and has A4=0,A6=48; its true SAT count=1296.
Its global histogram/moments are computed by independent
component convolution from 256 local affine checks,
not 2^24 global checks.

## Gate E3 installed in the actual cooperative SCL solver

Modified existing
`experiments/r5_moment_cooperative_solver_20261015.py` on the
successor research branch only. Optional `--anchored-moments`
enables local all-n A4/A6 enumeration and exact rational LP
degree<=3 on each reachable Boolean cube.
Each time the solver computes and checks the exact partial
anchors, independently obtains fixed-degree GF(2) moments,
and uses the tighter of previous moment and anchored LP
integer bounds. On zero bound a cube is discarded only
after the mathematical certificate. Otherwise valid
local propagation, bounded LOG_KERNEL or exact branching
preserves all true SAT solutions. A one-invocation node
cap retains UNKNOWN + exact DFS checkpoint. Saved policy
flag is validated at resume.

Frozen one-node integrated CI:
```text
connected SCL36 seed0: certified U3 root16 -> frontier15, UNKNOWN.
connected SCL36 seed13: certified U3 root17 -> frontier16, UNKNOWN.
Petersen45: certified U3 root420, UNKNOWN with cap c1.
```
The one-unit decrease in n36 is NOT the fractional c1
geometric progress guarantee. No artificial UNSAT
claim is made from an unfinished search.

## Strict gate ledger
- Parity-kernel word support is a simple cubic graph: PROVED ALL n.
- Weight4 K4/Pasch; weight6 K3,3/prism: PROVED ALL n.
- O(n) fixed-weight local enumeration under sparse RAM model: PROVED.
- Incidence girth>=10 forbids weights4/6/8: PROVED.
- Exact partial anchor filtering: PROVED, CI FINITE VERIFIED.
- Manual 94/3 exact primal-dual optimum: PROVED / CI VERIFIED.
- E3 anchored degree2..5 root LP optimality on four controls: CI VERIFIED.
- E3 integrated cooperative root + one split: CI VERIFIED.
- Anchored SAT/UNSAT spectral twins with same input data: NOT FOUND.
- Universal geometric progress and all-n deterministic polynomial SAT/UNSAT: NOT PROVED.
- `SolveLinearCubicXSAT`: NOT CONSTRUCTED.
- P versus NP: OPEN.

Next: search legal CONNECTED SAT-vs-UNSAT instances that share
n, affine dimension, low signed rowspace spectra and
the exact A4/A6 anchors; require independent UNSAT proof.
A match would show a finite decision indistinguishability
for THIS fixed (moment,anchor) representation. Also test
anchored LP on all successor cubes and higher-order
component signatures without hiding exponential work.
