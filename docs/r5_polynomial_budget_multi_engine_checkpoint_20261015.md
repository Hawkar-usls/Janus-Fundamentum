# R5 Polynomial-guarded multi-engine JANUS Gearbox — proof & checkpoint
Scientific date 2026-10-15. Branch: `research/r5-tutte-deficit-local-trap-20261014`.
Source: `experiments/r5_polynomial_budget_multi_engine_20261015.py`.
Continuing draft PR #518 / open issue #519. Original working baseline
`66436cd26f866aada74a8b1c257e263b6973e3d6` with passing CI
`38652556233`. Current main was
`a278d68534cbc9eba6fadbf4ff26182c03c792a2` at verification.

## User goal and crucial logical distinction
The earlier adaptive gearbox changed local pruning tiers according to fixed
test thresholds (8 nodes, 12 probes), but these thresholds did NOT bound the
total number of visited search states. New requirement: (1) polynomially
bounded **time per invocation**, (2) automatic scheduling of multiple
independent exact search algorithms using measured reduction in remaining
search-space upper bounds, (3) exact persistence of unfinished alternatives.

**Theorem A (budget):** The new invocation visits at most
`B(n)=4n^2` total search nodes over **both** engines, regardless of
`--max-nodes` (the command-line value is clamped to B(n)).
An engine quantum visits at most 8 nodes. Each DFS expansion and
propagation is polynomial in the n-vertex graph size (max-three-cut
precomputation restricted to min(256,n^2) triple candidates; all pair
cuts enumerated in O(n^2) choices with polynomial BFS validation).
Checkpoint frontiers each have O(n) stack states, O(n) words per state.
Retained history is capped to 64 entries; global counters use O(n) bits
because each complete search tree has at most 3^O(n) nodes.
The per-invocation algorithm, including built-in preprocessing,
scheduling and checkpoint serialization produced by this implementation,
therefore has a uniform n^O(1) bound on computation and output size
for valid self-produced checkpoints.

**CRITICAL:** This is a *total polynomial-time SAT/UNSAT/UNKNOWN*
procedure, NOT a polynomial-time SAT/UNSAT decision procedure.
After B(n) nodes it returns `UNKNOWN_RESOURCE_LIMIT` if both
unexplored frontiers remain. Multiple resumes may use exponentially many
total nodes and total time. A polynomial controller does NOT solve an
NP-complete problem in polynomial time by changing gears.

## Two genuinely independent exhaustive proof paths
**EDGE_DOMAINS**: the existing precise edge-color-constraint solver
(`r5_adaptive_gearbox_exact_coloring_20261015.py`) supplies
all-different propagation, optional 2-cut equalities and 3-cut parity,
bounded failed-literal probes and exact branching over all remaining
edge-color values. Gear 2/1/0 logic is inherited, with full pending
DFS frontier retained.

**MATCHING_EVEN_FACTOR**: entirely different representation.
Select one unmatched vertex (fewest unused incident edges), branch on
every edge to another unmatched vertex, and recursively enumerate
perfect matchings **exactly once each**. At a complete perfect
matching M, remove its edges. The complementary 2-factor consists
of cycles; two-color its edges by traversing alternating adjacency
constraints. If a residual odd cycle makes alternating impossible,
reject M. Otherwise use M as color 0 and alternate colors 1 and 2
on the residual cycles. This gives a checked proper 3-edge-coloring.

**Theorem B (soundness/completeness):** Each engine individually is
a sound and complete finite backtracking solver. A SAT verdict is
returned only after independent row-wise 3-edge-coloring and Holyer
Exact-One witness checks. Either engine exhausting its own frontier
without SAT proves UNSAT: its search tree has enumerated every coloring
(or respectively every perfect matching). Bridge precheck is also
sound by the cubic parity lemma. Switching between engines never
removes or replaces a pending state from either frontier. Therefore:
- `SAT` with explicit independently verified witness is sound;
- `UNSAT` after a complete frontier or certified bridge is sound;
- `UNKNOWN_RESOURCE_LIMIT` loses no pending DFS alternatives;
- resumption validates graph SHA256 and state format, retains both
  stacks and algorithm policy, and continues exploration exactly
  from the saved frontiers.

## A mathematically valid remaining-search metric
The user asked to measure how quickly engines SHRINK their remaining
space, not just elapsed work. For each engine define an easy-to-compute
upper bound on the raw number of candidate completions of its frontier.

EDGE: for each pending domain state `D=(D_e)`, let
```text
U_edge(D)=product over edges e of |D_e|.
Mass_edge = sum over pending D of U_edge(D).
```
Each branch fixes one color on one edge, partitioning the parent's
raw Cartesian product exactly; sound propagation may only shrink
domains. Hence Mass_edge is MONOTONE NONINCREASING under each full
search node expansion. It upper-bounds unprocessed complete
edge-color assignments, not the number of SAT witnesses.

MATCHING: for each partial matching state M with r unmatched
vertices, any deterministic pivot has at most 3 admissible choices.
There can therefore be no more than `3^(r/2)` completions of
this partial state. Define
```text
Mass_matching = sum over pending M of 3^(unmatched(M)/2).
```
At each pivot with q<=3 choices, the combined child mass is
q*3^((r-2)/2) <= 3^(r/2); failed or terminal nodes can only
reduce it. Thus Mass_matching is MONOTONE NONINCREASING.

These upper bounds are different mathematical quantities for
different algorithms and MUST NOT be directly compared as
solution counts. Scheduling computes log2 reduction of each
engine's OWN mass per quantum, divides by a measured *work proxy*
(local factor checks / probe counts, or matching branches), and
uses exponentially smoothed scores with mandatory fairness
(every live engine gets at least one quantum per three rounds).
Metric calculations on huge values use integers of O(n) bits,
with logarithms used only to rank engines, never to decide SAT.

The checker ASSERTS monotone nonincrease of each actual per-engine
raw-assignment upper bound after every quantum. Future failure of
this assertion would be a proof-model discrepancy, not permission
to silently weaken the invariant.

**Theorem C (fair progress):** A scheduler quantum visits >=1
node and <=8 nodes; every still-live independent engine is sampled
at least once per <=3 scheduling rounds. Thus if one repeatedly
invokes resume without a cumulative time bound, an entire finite
exhaustive tree is eventually explored, yielding SAT or UNSAT.
This is only asymptotic *eventual termination*, potentially
exponential in n.

## Preliminary frozen CI results
Initial CI for the new tester failed because bridge-based
UNSAT returned before normal statistics existed; fixed by
producing a uniform `finished(...)` report. The failure is
retained in workflow history as a regression provenance record.

At corrected code commit `87d29cf1278a110f56fefcb7d51c022c4cd9e03b`,
[run 38653883167](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38653883167)
completed SUCCESS on all previous R5 checkers and the multi-engine
self-test:

| Frozen control | Status | Winning proof path | Total nodes / call |
| --- | --- | --- | ---: |
| K4 | SAT | Edge-domain | 4 |
| K3,3 | SAT | Edge-domain | 7 |
| Petersen | UNSAT | independent search exhaustion | 26 |
| Connected n10 SAT Hall trap | SAT | Edge-domain | 8 |
| Connected n12 SAT imbalance trap | SAT | Edge-domain | 10 |
| K4 x 2, disconnected | SAT | Matching-even-factor | 9 |
| K4 x 10, disconnected | SAT | Matching-even-factor | 37 |
| Connected bipartite n20 | SAT | Edge-domain | 17 |
| Connected bipartite n60 | SAT | Edge-domain | 7 |
| Cubic graph with bridge, n10 | UNSAT | bridge parity | 0 |

Test also checks a one-node budget returns UNKNOWN,
a second one-node resume preserves UNKNOWN, and a third resumed
run reaches the correct Petersen UNSAT. Wrong-graph checkpoint
is rejected. A request for `10^100` nodes is clamped at B(10)=400;
a request for zero nodes returns UNKNOWN, not fabricated UNSAT.

With two independent engines, total visited nodes may exceed the
previous single-engine baseline on easy instances: duplicate work
is an explicit throughput tradeoff, not an algorithmic speed claim.
Measured reductions are *upper-bound signals*, not a certified
fraction of actual unsolved instances.

## Reproduce
```bash
python3 experiments/r5_polynomial_budget_multi_engine_20261015.py --self-test
python3 experiments/r5_polynomial_budget_multi_engine_20261015.py --fixture Petersen
python3 experiments/r5_polynomial_budget_multi_engine_20261015.py --fixture Petersen --max-nodes 1 --checkpoint /tmp/janus_dual.json
python3 experiments/r5_polynomial_budget_multi_engine_20261015.py --fixture Petersen --resume /tmp/janus_dual.json --checkpoint /tmp/janus_dual.json
python3 experiments/r5_polynomial_budget_multi_engine_20261015.py --fixture K4x10
```
Custom graphs: `--graph /path/to/graph.json`, with keys `n` and
`edges`, 0-based simple cubic undirected vertices.

## Research gates, no false promotions
- Strict polynomial per-invocation budget with SAT/UNSAT/UNKNOWN: PROVED.
- Two independently complete exact search algorithms: IMPLEMENTED.
- Both engine frontiers preserved across interruption: TESTED.
- Upper-bound shrinkage monotone, polynomial metric computation: PROVED.
- Quantitative true runtime speedup in microseconds/seconds: NOT TESTED.
- All-user-input SCL (non-Holyer class) integration: NOT CONSTRUCTED.
- Uniform polynomial-time total SAT/UNSAT solver: NOT CONSTRUCTED.
- GlobalCutImprove with guaranteed polynomial decision: OPEN.
- P versus NP: OPEN.

Next scientifically meaningful work: freeze this controller;
run blind, provenance-tagged cubic/Holyer-hard benchmarks of
increasing sizes, compare cost per decisive SAT/UNSAT and upper-bound
reduction against both fixed engines, test repeated checkpoint
and rescue paths, and DO NOT overfit to Petersen/K4 controls.
