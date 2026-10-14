# R5 — JANUS Cooperative Universal Progress: SCL-native exact merge and frozen stall
**Date:** 2026-10-15  
**Status:** Exact finite experiment with separately verified local transitions; universal polynomial cooperative coverage NOT PROVED.

## Source of request and provenance
User supplied a mathematical proposal on Cooperative Universal Progress (also in the conversation attachment `Вставленный текст(20261014-234317).txt`). This checkpoint distinguishes statements in that proposal from independently checked finite computations and the new executable model.

- Repository: `Hawkar-usls/Janus-Fundamentum`.
- Existing R5 draft PR [#518](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/518), head `5b434b3b994cb0addd3e706e1a6118fe683d8455` before this work. Existing [issue #519](https://github.com/Hawkar-usls/Janus-Fundamentum/issues/519).
- **Successor research branch**: `research/r5-cooperative-coverage-20261015`, branching from that exact R5 head. Separate dependent PR to the R5 research branch; does NOT overwrite `main`.
- Source: `experiments/r5_cooperative_scl_coverage_20261015.py`.
- Seeded adversarial generator: `experiments/r5_cooperative_coverage_breaker_20261015.py`.
- Tests triggered by `.github/workflows/r5-tutte-deficit-local-trap.yml` (includes all prior R5 regression steps).

## 1. Mathematical contract for the shared FRONTIER_BOUND
Input: a **legal** n-by-n incidence family of positive Exact-One clauses, n
variables, three distinct variables per clause, each variable occurring
exactly three times, and any two different clauses overlapping in at most
one variable. No graph-edge-colorability encoding is assumed.

The source implies all true solutions have exactly n/3 true variables.
If `n % 3 != 0`, immediate UNSAT by `3|x|=n`.

Every Exact-One solution also satisfies `Ax=1 mod 2`. For a partial
assignment cube C=(Z,O) of variables fixed zero/one, define:
- `W(C)=binom(n-|Z|-|O|, n/3-|O|)` (zero outside its feasible range).
- `P(C)=0` if the residual GF(2) affine system is inconsistent; otherwise
  `P(C)=2^d`, where d is its free dimension, computed by exact Gaussian
  elimination on the fixed cube.
- `U(C)=min(W(C),P(C))`.
- For an actual DFS frontier of **disjoint** cubes, define
  `U(K)=sum_{C in frontier} U(C)`.

Let `C(K)` denote the union, over frontier cubes, of assignments that
satisfy BOTH original global necessary conditions (Hamming weight n/3
and linear GF(2) parity). Then:
```text
Sol(F) subseteq C(K),    |C(K)| <= U(K).
```
Each expert update maintains `Sol(F) subseteq C(K)` by preserving all
Exact-One solutions. Hence this is a valid *integer upper bound on the
candidate intersection*, NOT the number of all Boolean assignments in
the cube. Mixing those notions is unsound.

The two counts W and P alone do not count their intersection exactly;
using their minimum is only an upper bound. For the n=9 regression,
W=84, P=4, U=4, while the exact intersection has THREE candidates.
No intersection counting tractability is assumed in high dimensions.

## 2. Sound local expert grammar and verifier
The shared representation is a DFS stack of Boolean cubes.
The checker `verify_progress(rows, old_cube, replacement, proof)`
does not trust an update's claimed progress. For allowed proof opcodes
it independently recomputes the source exact-one or GF(2) consequences,
or checks that BRANCH children form the exact disjoint x_v=0/x_v=1
partition. It recomputes U for all affected cubes and rejects any
increase. A progress-power c certificate is accepted only if
```text
U_new * n^c <= (n^c-1) * U_old.
```
This avoids floating-point rounding of fractional progress.

Expert forms:
- `EXACT_ONE`: unit consequences and integer clause contradiction.
- `WEIGHT`: global weight contradiction and forced remaining values.
  Implemented in the same deterministic local consequence pass.
- `GF2`: exact Gaussian affine inconsistency; also derivation of
  globally forced variable coordinates via nullspace basis.
- `SMALL_KERNEL`: if affine dimension d<=8 (a FIXED constant),
  enumerate all 2^d parity candidates; accept a SAT witness only after
  independent whole-matrix Exact-One check. Reject a cube only when
  every affine candidate was checked. If d>8, DECLINE.
- `BRANCH`: exhaustive splitting on any unset Boolean variable when
  the other experts decline. It preserves completeness, but can
  leave the certified FRONTIER_BOUND unchanged.

SAT witness validation is polynomial and direct. Individual rewrite
verification is polynomial in n, and bounded SMALL_KERNEL proofs
cost at most 256 candidates times polynomial clause verification.
The finite UNSAT search is logically sound by exhaustive branching;
the current 32-entry recent-event diagnostics are NOT a complete
externally replayable UNSAT proof of potentially exponential length.
Do not claim general polynomial-size UNSAT certificates.

The solver limits each invocation to <=4n^2 search nodes, returning
`UNKNOWN_RESOURCE_LIMIT` if a frontier remains. Resumption verifies
the input SHA256; total cumulative search may be exponential.
This is the same **polynomial-per-invocation ≠ polynomial decision**
firewall already applied to the two-engine Gearbox.

## 3. Analytic all-n theorem: conditional cooperative progress
If there are <=n^a uniformly constructible experts, every attempted
step and its verification/merge costs <=n^b, and for every reachable
nonterminal state some expert terminates or gives a sound and checked
`U_new <= (1-1/n^c)*U_old` with polynomial-size state, then running
every expert for its full budget per cooperative round yields a
deterministic n^O(1) SAT/UNSAT solver.

Proof: `U0<=2^n`, so after q successful rounds
`Uq<=2^n exp(-q/n^c)`. If q>n^c(n ln 2+1), `Uq<1`;
as nonnegative integer Uq is zero. Then no remaining solution is
possible (or SAT returned earlier). Number of experts * rounds *
attempt cost <=O(n^{a+b+c+1}), ignoring constant factors and assuming
all memory/merge work is included in b.

The **universal progress premise has NOT been established**. A
polynomial-size checker, short representation, and fair scheduler do
not imply it. In particular, a legal finite stall of the current
restricted expert grammar is found below.

## 4. Reproduced 9x9 affine-plane example
Enumerate the nine points of F3^2 and take three families of three
parallel lines: x=c, y=c, y-x=c for c=0,1,2. This gives precisely
nine 3-element rows and columns, with row intersections <=1.

Exact independent brute-force weight oracle:
- n=9, possible weight-three vectors = binom(9,3)=84.
- GF(2) rank = 7, affine parity dimension = 2; exactly four vectors
  satisfy `Ax=1 mod 2`.
- Three parity vectors have weight three and are actual Exact-One
  SAT witnesses; the fourth is `x=111111111`, satisfying parity
  but NOT integer Exact-One (every clause has sum three).
- The bounded affine expert independently finds SAT in one popped
  node and verifies the complete witness.

This demonstrates *actual exchange* of exact GF(2) basis, integer
weight condition and Exact-One validation, not only portfolio
scheduling.

## 5. Frozen finite negative: Holyer-Petersen45 stalls with this U
For the cubic Petersen graph, Holyer's edge-color embedding produces
n=45 legal SCL variables and clauses (each source variable x_(e,c)
is in one edge clause and two vertex-color clauses).
The exact root GF(2) affine dimension is **12**, so
`U_root=2^12=4096` (weight-bound is larger).

Certified initial-state observations:
- All Exact-One clauses have three unset variables: no local unit
  derivation or contradiction.
- GF(2) basis has no individually forced variable at the root.
- SMALL_KERNEL with fixed d<=8 DECLINES.
- **For every one of the 45 possible Boolean splitting variables v**,
  `U(x_v=0)+U(x_v=1)=4096=U_root`.

Therefore no named propagation expert or any 1-variable BRANCH
provides the required fractional reduction of **this specified U**
at the root, for any c>=1. This is an EXACT FINITE COUNTEREXAMPLE to
the **specified restricted expert family and selected potential**,
not to all possible experts or polynomials. The branch step still
partitions candidates soundly; its absence of strict U progress
does NOT mean the algorithm cannot continue searching.

At node budget three, both the first call and resumed call return
UNKNOWN_RESOURCE_LIMIT, with hash-protected exact frontier. No
UNSAT is inferred from budget exhaustion.

## 6. Seeded Coverage Breaker
The generator builds all-legal SCL directly from the union of three
permutation matchings in a bipartite clause-variable incidence graph.
It rejects every invalid triple/overlap; all retained output matrices
are explicitly validated.

Frozen self-test uses n=12, seed 20261015, two samples and two-node
budgets. The legal matrices were found after a combined 11936
rejection-sampling attempts:
- `76bc78a8d155c1a1d49110c3104236632a5d1705c7b7b13531df09b8e7825d3c`:
  UNSAT, U0=1, Uend=0;
- `ef8f79f0b9f4a0ef8286c59dee56d2f33bbc3a7e7dacd5ff9c6e8885120e9418`:
  UNSAT, U0=1, Uend=0.

These are EASY instances for the parity expert; the fact that the
generator finds legal n12 inputs does not constitute a hard-input
distribution. The frozen Holyer-Petersen45 is the meaningful
adversarial example for the current U and grammar.

Use:
```bash
python3 experiments/r5_cooperative_scl_coverage_20261015.py --self-test
python3 experiments/r5_cooperative_scl_coverage_20261015.py --fixture AffinePlane9_SAT
python3 experiments/r5_cooperative_scl_coverage_20261015.py --fixture Regular12_UNSAT
python3 experiments/r5_cooperative_scl_coverage_20261015.py --fixture HolyerPetersen_UNSAT --node-budget 3 --checkpoint /tmp/cooperative.json
python3 experiments/r5_cooperative_scl_coverage_20261015.py --fixture HolyerPetersen_UNSAT --node-budget 3 --resume /tmp/cooperative.json --checkpoint /tmp/cooperative.json
python3 experiments/r5_cooperative_coverage_breaker_20261015.py --self-test
```

The finite tests include Fano7 immediate UNSAT via n mod 3, a legal
n12 integer Exact-One UNSAT despite GF(2) consistency, and Holyer K4
SAT. Independent exact brute force validates n<=18 non-Petersen
fixtures. No appeal to an unverified dataset or GPT-supplied result
as a certificate.

## 7. Next research gate
The current root Petersen stall shows the weakness of
`U(C)=min(weight_count,parity_count)` under single-variable branching:
an exact split partitions both counts, preserving their sum. To obtain
universal fractional progress, a next expert would require a NEW,
certified, polynomially computed bound using correlations among
parity, Hamming weight and integer Exact-One constraints, or exact
operations on more global partition signatures.

A tighter estimate that reduces U without excluding actual
assignments is legitimate ONLY if independently certified as a new
upper bound on |C(K)|. A heuristic estimate of "likely remaining
solutions" is NOT a certificate.

If a new expert only reshuffles the frontier or decreases a proxy
that is not a proved upper bound, do not promote it to progress.

| Gate | Status |
| --- | --- |
| Conditional cooperative progress theorem | PROVED under explicit premises |
| Native SCL legal-input validator | IMPLEMENTED |
| Independently verified local expert merge | IMPLEMENTED |
| Exact weight/GF(2) common frontier upper bound | PROVED all n |
| 9x9 84→4 parity states→3 actual witnesses | VERIFIED finite |
| Holyer-Petersen45 no single-variable U shrink | FINITE FROZEN COUNTEREXAMPLE |
| Seeded legal SCL Coverage Breaker | IMPLEMENTED, easy n12 controls |
| Polynomial universal progress for all states | NOT PROVED |
| Uniform polynomial SolveLinearCubicXSAT | NOT CONSTRUCTED |
| P vs NP | OPEN |
