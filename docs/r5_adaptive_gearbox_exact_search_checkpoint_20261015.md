# R5: JANUS adaptive exact search gearbox (2026-10-15)
**Scientific classification:** IMPLEMENTED EXACT ENUMERATION; adaptive heuristics; `P vs NP` OPEN.

## Why this mechanism exists
The user asked for an automatic transmission: when a strong method consumes
more effort than its pruning benefit justifies, drop to cheaper methods
**without dropping any logical cases**. This is different from claiming
universal polynomial elimination. For worst-case NP-complete cubic
3-edge-colouring, the fallback DFS remains exponential. This checkpoint
deliberately treats "speed" as a measured, falsifiable *finite algorithm*,
not a proof of P=NP.

## Frozen artifact and provenance
- Repository: `Hawkar-usls/Janus-Fundamentum`.
- Research branch: `research/r5-tutte-deficit-local-trap-20261014`;
  PR [#518](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/518)
  remains a draft, issue [#519](https://github.com/Hawkar-usls/Janus-Fundamentum/issues/519) remains OPEN.
- Verified branch baseline at research start:
  `f5f95c586e5a8cf00dbe8929cd4fffe5283dfe33`;
  [CI SUCCESS 38648503598](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38648503598).
- Source `experiments/r5_adaptive_gearbox_exact_coloring_20261015.py`.
- Python >=3.11 standard library; deterministic MRV choices; JSON reports;
  optional node budget and resumable, graph-hash-validated frontier.
- Tests invoke the executable on all frozen K4/K3,3/Petersen/n10/n12
  controls plus a disconnected K4+K4 graph.
- Not merged to `main`.

## What the gears actually do
Every edge e has a nonempty domain `D_e subset {0,1,2}`, stored as
a three-bit mask. An exact proper three-edge coloring is precisely
a singleton choice for all edges such that the three incident edges
at every cubic vertex use all three colors.

**Gear 0 FAST.** Enforce generalized arc consistency at each cubic
vertex. The only six possible tuples are permutations of (0,1,2);
remove an edge color iff it participates in NONE of these locally
permitted tuples. This is exact necessary propagation.

**Gear 1 BALANCED.** In addition, precompute true graph two-edge cuts
and enforce that both crossing edges carry the SAME color. This follows
from the parity lemma: for any cut delta(S) and color c, the number
of c-colored crossing edges is congruent to |S| (mod 2).
Every proper three-edge coloring must obey each enforced equality.

**Gear 2 PRECISION.** Add exact all-different propagation at true
three-edge cuts (the parity lemma requires each color exactly once)
and bounded *failed-literal* lookahead. Probe a few candidate colors
by propagating with gear 1; remove a color only if this creates a
logical contradiction. The probes are capped per node so the
lookahead cost cannot silently turn into an unbounded recursion.

**Bridge pre-check.** A cubic graph with a bridge cannot be
properly three-edge colored: a one-edge cut must contain an odd
number of edges of EACH of three colors. Such an UNSAT result is
a valid structural theorem, not an incomplete search verdict.

**Gear change.** Every configurable number of explored DFS nodes,
compare the number and cost of lookahead probes and failed-literal
discoveries, the two-cut equality checks, and contradiction count.
Drop from gear 2 to 1 when expensive probes yield no failed colors;
from 1 to 0 when no two-cut constraints exist or they add evaluation
overhead without contradictions; increase from 0 to 1 when many
frontier nodes die. Switching modifies *only* filtering strength on
the next popped search node. A mode cannot discard or skip a branch.
Diagnostic trace includes node number, old/new gear and reason.

## Theorem 1: sound and complete for finished runs
Assume a finite simple 3-regular graph G. The algorithm begins with
the full domain for every edge. At each DFS node it applies only
conditions that EVERY genuine 3-edge-coloring must satisfy:
- vertexwise all-different;
- parity of true 2-edge cuts (color equality);
- parity of true 3-edge cuts (all-different);
- failed-literal elimination after a valid necessary-consistency
  contradiction.
It then branches on every color remaining in an unresolved edge
domain. The children partition all full colorings consistent with
that parent. Therefore a feasible complete coloring always survives
some node if one exists, regardless of changes in propagation gear.

When it returns SAT, it independently verifies all incident colors
at all vertices. When it returns UNSAT after exhausting the DFS
frontier, no coloring remains, by induction over the complete
branching tree. If it returns UNSAT on a bridge, the parity lemma
provides its universal certificate. The proof does not depend on
the completeness of enumerating graph cuts: omitted cuts weaken
pruning, never invalidate correctness. Cubic disconnected graphs
are also accepted; proper edge colorings compose across components.

**Conditional caveat:** these are ordinary correctness proofs for
finite terminating enumeration. They are *not* polynomial-time proofs.

## Theorem 2: exact checkpoint/resume and UNKNOWN verdict
When `max_nodes` cuts off exploration with a nonempty frontier,
the only legal verdict is `UNKNOWN_RESOURCE_LIMIT`. The JSON
checkpoint includes: input graph SHA256 fingerprint, every pending
edge-domain state in LIFO order, current gear, immutable
precomputation budget and telemetry. Resume validates the graph
hash and reuses precisely the same pending frontier and counters.
Hence repeated bounded runs preserve exact completeness. No
`UNSAT` is inferred from budget exhaustion, stalled propagation,
or lack of heuristic progress.

The checkpoint is an *execution-state witness*, not a compact
polynomial UNSAT certificate. Frontier size may itself grow
exponentially. This is expected, and stored honestly.

## Concrete reproducibility
From repo root:

```bash
python3 experiments/r5_adaptive_gearbox_exact_coloring_20261015.py --self-test

# SAT and UNSAT reference runs:
python3 experiments/r5_adaptive_gearbox_exact_coloring_20261015.py --fixture SAT_Hall10
python3 experiments/r5_adaptive_gearbox_exact_coloring_20261015.py --fixture Petersen

# Compare exact same solver with cheap versus precision gear:
python3 experiments/r5_adaptive_gearbox_exact_coloring_20261015.py --fixture Petersen --gear 0 --fixed-gear
python3 experiments/r5_adaptive_gearbox_exact_coloring_20261015.py --fixture Petersen --gear 2 --fixed-gear

# Persist an incomplete computation instead of inventing an UNSAT result:
python3 experiments/r5_adaptive_gearbox_exact_coloring_20261015.py --fixture Petersen --max-nodes 1 --checkpoint /tmp/gearbox_frontier.json
python3 experiments/r5_adaptive_gearbox_exact_coloring_20261015.py --fixture Petersen --resume /tmp/gearbox_frontier.json

# User-supplied graph:
python3 experiments/r5_adaptive_gearbox_exact_coloring_20261015.py --graph graph.json
```

Custom graph file: `{"n":10,"edges":[[0,1],...]}`, with 0-based
vertices and a simple cubic edge list (all degrees exactly three).
Disconnected graphs are allowed.

An equivalent SAT assignment for the Holyer embedding of cubic
3-edge-coloring can be recovered from `edge_colors`: set exactly
`x_(edge,color)=1` for the indicated edge color and all other
color indicators to zero. This covers the Holyer-embedded NP-complete
legal square/cubic/linear Exact-One subclass but does NOT automatically
solve arbitrary SCL instances that have not been reduced to this
graph form. Do not infer a universal solver for all SCL inputs.

## Complexity and restrictions
For n vertices, m=3n/2 edge variables have three values each; a
naive bound is `3^m` leaves (actual branching propagates heavily).
Cut precomputation checks all O(m^2) pairs and at most the
configurable `cut_budget` triples; each checked cut uses BFS over
the graph. If a cut budget truncates 3-cut enumeration, the solver
still remains sound and complete: only optional deductions are
dropped. Each per-node domain-propagation loop eliminates a color
at least once per nontrivial iteration, so a propagation pass is
polynomial in n; bounded failed-literal lookahead is polynomial
per node. The **number of nodes** has no known uniform polynomial
bound, even after transmission changes.

The rate of mode shifts and their relative efficiency are *heuristics*,
not guarantees that the selected gear always beats a fixed gear.
The JSON reports permit comparing node counts, probe counts and
constraint evaluations on the same frozen fixtures.

## Verified operational results (GitHub Actions 2026-10-15)
CI [run 38652483021](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38652483021)
completed SUCCESS at source commit `c9b8d03d36b7386809819b659c9ae93a983384a3`.
The workflow ran every previous R5 theorem checker plus the gearbox
self-test with all three fixed gears, adaptive policy and exact resume.

| Fixture | n | Expected | FAST nodes | PRECISION nodes | AUTO nodes |
| --- | ---: | --- | ---: | ---: | ---: |
| K4 | 4 | SAT | 3 | 3 | 3 |
| K3,3 | 6 | SAT | 4 | 4 | 4 |
| Petersen | 10 | UNSAT | 22 | 10 | 10 |
| SAT Hall trap | 10 | SAT | 4 | 4 | 4 |
| SAT imbalance trap | 12 | SAT | 4 | 4 | 4 |
| K4 x 2 (disconnected) | 8 | SAT | 5 | 5 | 5 |
| Bridge10 | 10 | UNSAT | 0 | 0 | 0 |
| Circulant bipartite | 20 | SAT | 7 | 7 | 7 |
| Circulant bipartite | 60 | SAT | 7 | 7 | 7 |
| K4 x 10 (disconnected) | 40 | SAT | 21 | 21 | 21 |

**Actual gear-shift trace:** On K4 x 10, automatic gearbox
changed PRECISION(2) -> BALANCED(1) at visited node **8** after
probes failed to eliminate any candidates; BALANCED(1) -> FAST(0)
at visited node **12**, because there were no two-edge-cut equality
constraints. A full PRECISION run performed **100** literal probes;
the AUTO run performed **40** probes and visited the same 21 nodes.
This is a real reduction in one category of work, not a wall-clock
benchmark and not evidence of asymptotic improvement.

**When strong gear is valuable:** On Petersen, fixed/automatic
PRECISION explored 10 nodes; FAST explored 22. Both returned UNSAT
and the adaptive controller avoided premature downshift.

**Resume:** Petersen with a one-node budget returned
UNKNOWN_RESOURCE_LIMIT, persisted frontier, resumed to UNSAT,
and matched the uninterrupted visit count exactly.

**Holyer source verification:** Every SAT witness additionally
reconstructs and verifies square + cubic + linear positive exact-one
incidence rows: 3m variables and rows, exactly three variables per
row and three occurrences per variable, at most one variable shared
by any two rows, with exactly one true literal in every row.

**Caveat:** finite pass rates are not all-n convergence bounds;
switch policies may lose to either fixed gear on other inputs.
Worst-case search remains exponential. No universal polynomial
`SolveLinearCubicXSAT` was constructed.

## Next research gate
Benchmark all three fixed gears versus adaptive on connected
Holyer-derived hard graphs with fixed time/node caps. Evaluate
per-gate decision cost and failed-literal hit rate; tune only on
training controls, freeze policy, and test on blind graphs. For
any claimed universal solver require deterministic polynomial
upper bounds on visited states **and** all intermediate work,
without heuristics, timeouts or hidden exponential cut generation.

State: EXACT EXPONENTIAL SOLVER IMPLEMENTED; POLYNOMIAL
`GlobalCutImprove` NOT CONSTRUCTED; `SolveLinearCubicXSAT`
NOT CONSTRUCTED; `P vs NP` OPEN.
