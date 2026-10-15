# R5 / JANUS: fixed-degree moment expert, exact certificates, and LOG_KERNEL
2026-10-15. **All-n statements and CI-finite statements separated.**

## Origin / provenance

This result implements and independently tests the user-supplied research text
`Вставленный текст(20261015-070729).txt` (1132 lines), which first supplied
the parity+weight sufficiency argument and degree-1/2/3 dual candidates,
including 45-vertex SCL Petersen conjectured numbers.

Repository `Hawkar-usls/Janus-Fundamentum`.
Base (stacked) previous research `research/r5-cooperative-coverage-20261015`,
head `85a92975b63c48ee72bb266d1fb883c370aa249f` (PR #520, CI PASS).
New branch `research/r5-moment-hierarchy-20261015`, dependent on PR #520;
do **not** merge directly to main until all preceding dependencies reviewed.

Executable artifacts:
- `experiments/r5_fixed_degree_moment_expert_20261015.py`: polynomial
  GF(2) restriction query moment counts, exact Fraction dual certificates,
  Petersen all-45-split replay and independent 4096-word histogram control,
  and `LOG_KERNEL`.
- `experiments/r5_moment_cooperative_solver_20261015.py`: actual
  SCL-native cooperative exact solver with moment bound, local Exact-One,
  GF(2), parameter-limited affine full enumeration and exact DFS/checkpoint.
- `.github/workflows/r5-moment-hierarchy.yml`: independent CI
  with both modules + prior cooperative tests.

## Theorem 1 (all-n, exact, no linearity needed)
Let A be n-by-n 0/1 with every row and column having exactly
three ones; x is Boolean. Then
```
Ax = 1 over the integers   <=>   (Ax = 1 mod 2 AND |x|=n/3).
```
Proof: parity forces each row's integer sum to be 1 or 3. Column
regularity gives sum_i (Ax)_i = 3|x|. If |x|=n/3, total n with n
positive odd row sums implies all are 1. Conversely, exact-one
gives parity and |x|=n/3.

For any parity state x, let t(x)=#rows whose integer sum is 3.
Then `3|x|=n+2t(x)`, hence if 3 divides n, t is a multiple
of 3. Furthermore `t=0 iff x is an exact SAT solution`.

Thus the set of candidates satisfying parity AND weight is ALREADY
the exact SAT solution set. The old bound min(weight count, GF(2)
affine count) is loose because it is the min of TWO SUPerset sizes,
not because those conditions fail to imply Exact-One.

## Theorem 2 (all-n, fixed-degree polynomial moment counts)
For fixed cube C=(Z,O), let S_C={x consistent with C: Ax=1 mod2},
an affine GF(2) space of size 2^d or empty.

Define indicators I_i(x)=1 if clause i evaluates to 111, and
`t(x)=sum_i I_i(x)`.
For any j>=0, the *raw binomial moment*
```
N_j(C) = sum_{x in S_C} binom(t(x),j)
       = sum_{R subseteq [n], |R|=j}
          #(x in S_C : all variables in union of clauses R are 1).
```
The count for each R is an exact GF(2) rank/consistency check:
fix at most 3j variable bits to 1; if compatible, number of affine
seeds is `2^(d-rank)`, else zero. The implementation computes this
from the precomputed affine basis using bit-vector elimination.

For every FIXED degree r<=3, compute N_0,...,N_r with
O(n^r) rank checks (each polynomial) and polynomial-size integers.
This is ALL-n polynomial for each fixed r, not when r grows with n.

## Theorem 3 (all-n, proof-carrying rational dual)
For any exact rational coefficients lambda_0,...,lambda_r define
`q(t)=sum_j lambda_j*binom(t,j)`.
Suppose
```
q(0)>=1, and q(t)>=0 for every t in {3,6,...,n}.
```
Then pointwise `1[t=0] <= q(t)` on the *entire legitimate support*,
so the true number Q(C) of exact SCL SAT assignments in C satisfies
```
Q(C) <= sum_{j=0}^r lambda_j * N_j(C).
```
Take FLOOR of the nonnegative rational bound and minimum with
the old integer bound. All arithmetic is exact Python
`fractions.Fraction`; the verifier independently rechecks the
affine moments, coefficient list and each permitted support point.

For any input cube C, `U_r(C)` is therefore a mathematically
certified integer upper bound on the ACTUAL SAT solution count.
For disjoint cubes, the sum bounds their union. The certificate
does NOT have to enumerate the solutions.

Finite candidate duals currently installed:
```
q1(t)=1 - t/n                          (legal for n>=3)
q2(t)=(t-12)*(t-15)/180
      =1 - 13/90*t + 1/90*C(t,2)
q3(t)=1 -331/2025*t +23/1350*C(t,2) -1/1350*C(t,3)
qchild0(t)=1 -247/1215*t +7/270*C(t,2) -1/810*C(t,3)
```
These particular q2/q3/qchild0 are finite empirical *candidates*.
The verifier always checks positivity for the CURRENT n.
For example q3 may be invalid for large n because its negative
cubic term dominates at large t; it is never silently used outside
a verified support. This is essential for all-n soundness.

## Exact finite regressions — affine plane order 3
n=9, GF(2) rank 7, 4 parity words, 84 weight-three words,
three actual SAT witnesses.

Root raw moments N0=4, N1=9; q1=1-t/9 gives exactly
`U1=floor(4-9/9)=3`. The independent whole-solution validator
rechecks this finite fact.

## Exact finite regressions — Petersen / Holyer 45x45
n=45, affine GF(2) dimension 12, 4096 parity words.

The complete histogram of t among all 4096 words, independently
enumerated only in the CI FINITE ORACLE, is:
```
t:     3   6   9    12  15  18  21  27  30  45
count: 270 540 1350 720 684 240 225 30  36  1
```
No t=0 parity word exists, hence Petersen UNSAT. The 4096-word
exhaustive check here is NOT the polynomial moment algorithm.
The two independent computations match raw moments
```
N0=4096, N1=46080, N2=288000, N3=1337280.
M1=N1/N0=45/4
M2=N2/N0=1125/16
M3=N3/N0=20895/64
```
All these quantities are independently verified in CI; the rank
oracle does not read the enumerated histogram.

The exact rational duals then give:
```
Old U = 4096.
Degree 1: q1   U1=3072.
Degree 2: q2   U2=640.
Degree 3: q3   U3=480.
```
For EVERY source variable v in 0,...,44:
```
  C(v=0): d=11, N=(2048,21504,124032,523264)
          qchild0 bound=11072/45; floor=246.
  C(v=1): d=11, N=(2048,24576,163968,814016)
          q3 bound=5536/25; floor=221.
  sum child bounds=467.
```
Check c=1 geometric threshold exactly as integers:
```
467*45 = 21015 < 21120 = 480*44.
```
The old U=4096 had no improvement under ANY singleton branch,
whereas degree-3 moment U has a strict certified decrease for
ALL 45 singleton branches of this ONE finite Petersen root.

Important: the third-degree candidate q3 being useful at the
Petersen root does NOT establish the same progress on all
descendants, all SCL instances or all n. This finite fact is a
verified correction to the prior Petersen-stall, not P=NP.

## LOG_KERNEL — all-n bounded polynomial expert
For fixed c in {0,1,2,3}, if a cube's affine GF(2) solution space
has dimension d with `2^d<=n^c`, enumerate each of the 2^d
parity words, and verify the exact SAT witness condition.
This costs <=n^c poly(n), hence polynomial for fixed c.
Otherwise the expert returns DECLINE.

On Petersen n=45 d=12: 2^d=4096<45^3=91125.
Therefore c=3 expert exhaustively scans all 4096 parity words,
finds none of weight 15, and **certifies UNSAT** for this finite
Holyer-Petersen instance. For c=1 (cap 45) it declines.

This finite acceptance is not a universal polynomial SAT solver:
there exist legitimate SCL families with affine nullity Theta(n).

## Integrated cooperative exact solver
In `r5_moment_cooperative_solver_20261015.py`, each DFS step:
1. recomputes a certified degree<=3 moment U(C);
2. discards C only if U(C)=0;
3. applies locally rechecked Exact-One and GF(2) forced assignments;
4. runs LOG_KERNEL under the explicitly fixed n^c budget;
5. if all experts decline, splits one variable into two disjoint cubes,
   recomputes both independently certified bounds and verifies
   `U(children)<=U(parent)`.
Each SAT response is independently Exact-One-verified; each UNSAT
response requires proof that every pending cube has been exhausted
(or log-kernel/exact proof). At a per-run maximum of 4n² DFS nodes,
it may return `UNKNOWN_RESOURCE_LIMIT`, never fabricated UNSAT.
Checkpoint includes original matrix checksum, proof policy and stack.

Important resource note: the fixed-degree moment calculation costs
O(n^3 poly(n)) PER searched cube; per-run total is polynomial in n
because node count is capped, but cumulative repeated resumed
runs can still be exponential. Recent-event log is not a complete
external UNSAT proof when exhaustive tree grows huge.

Integrated finite tests:
- affine plane9: U1=3, SAT witness verified;
- Petersen45 with c=1: one-node budget -> UNKNOWN with U3 480->467,
  both children retained;
- Petersen45 with c=3: exact UNSAT after scanning 4096 parity states;
- saved wrong-matrix checkpoint rejected; genuine resume advances.

## Successor Coverage Breaker: exact n72 finite root stall for current certificates

File: `experiments/r5_moment_coverage_breaker_20261015.py`.
Input: a disconnected cubic graph containing **four independent
copies of K4**, encoded into 72-variable *legal* square/cubic/linear
positive Exact-One via the standard Holyer encoding. This graph is SAT,
but the current restricted expert family can still show shallow
non-progress in its particular potential.

GF(2) affine dimension d=24, hence there are `2^24=16,777,216`
parity words at the root; `72^3=373,248`. The polynomial
`LOG_KERNEL(c=3)` correctly returns `DECLINE`.

Moment degree is capped at 3, but our **current dual template library**
contains q1, q2, Petersen-specific q3 and qchild0. For n=72 the
Petersen-specific cubics fail the *all-support nonnegativity check*
and MUST be rejected, rather than unsoundly extrapolated. The remaining
valid templates give
```text
U(root) = 5,452,595
For EACH v=0..71:
U(v=0)=2,254,438
U(v=1)=3,198,156
U(children)=5,452,594.
```
Thus each individual variable split reduces U by exactly one count,
and violates the geometric c=1 requirement:
`U(children)*72 > U(root)*71`.

All 72 splits were **independently replayed** using GF(2)-restriction
moment rank checks (fixed degree 3) in GitHub Actions:
[CI SUCCESS run 38698911282](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38698911282)
at commit `ca2ed25cb4ce70971cfb45f7c32cdbb2b8a4f565`.

**Limits:**
1. This example is DISCONNECTED, not a hard connected source.
2. These are finite failures of **the current finite set of permitted
   dual certificates**, not a lower bound on every possible
   degree-3 dual LP or another polynomial expert.
3. The input is SAT, so a branch can still reach a witness; no
   universal UNSAT barrier is proved.
4. A monotone bound dropping by just one is not the multiplicative
   progress required for the conditional Cooperative Progress theorem.

New gate: generate new degree-3 duals valid for all t=0,3,...,72
using a separate polynomial LP / small exact-rational dual finder,
and recheck whether ANY new certificate eliminates the n72 stall;
then seek harder connected SCL examples with d>c log n.

## Proof boundary / next test
Required next step is to find a legal SCL instance with large affine
nullity `2^d>n^c`, root U_r>0 and NO progress under small-degree
moment + local propagation, and freeze all structural data with
strict accounting for number of rank queries and coefficient bits.

Do not confuse the exact 45-singleton Petersen fact with all-n progress.
A solver completing in polynomial time on finitely many controls does
not establish the universal quantifier.

| Gate | Status |
| --- | --- |
| Parity + cardinality iff Exact-One | PROVED ALL n |
| t multiple of 3 among legal parity states | PROVED ALL n |
| Fixed-degree exact binomial moments by GF2 restrictions | PROVED ALL n |
| Verifiable rational polynomial upper bounds | PROVED ALL n |
| AffinePlane9 U1=3 | CI VERIFIED |
| Petersen45 4096→3072→640→480 | CI VERIFIED |
| Petersen 45 singleton splits U3 480→467 | CI VERIFIED FINITE |
| Petersen c3 LOG_KERNEL UNSAT | CI VERIFIED FINITE |
| Universal per-state geometric progress | NOT PROVED |
| Uniform polynomial SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |
