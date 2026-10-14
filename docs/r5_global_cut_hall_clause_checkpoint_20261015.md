# R5 checkpoint: global Hall-cut certificates and cutspace-compatible matching exchange
**Date:** 2026-10-15 · **Scope:** universal mathematical identities; finite exact regression, no universal polynomial solver.

## Provenance and prior state
- Continuing draft [PR #518](https://github.com/Hawkar-usls/Janus-Fundamentum/pull/518) and open [issue #519](https://github.com/Hawkar-usls/Janus-Fundamentum/issues/519).
- Previous commit before this research pass: `ab4e7c49291a3e26e48eb520649ff860bed81931` on `research/r5-tutte-deficit-local-trap-20261014`; prior combined CI success [run 38637026907](https://github.com/Hawkar-usls/Janus-Fundamentum/actions/runs/38637026907).
- Previous verified controls: n=10 connected bridgeless SAT balanced Hall obstacle (`s=551, Delta=2, X={3}, N_R(X)=empty`), n=12 connected bridgeless SAT pure imbalance trap (`s=1246, Delta=4`, strict-improvement Hamming radius >=5), Petersen UNSAT.
- Newly added executable: `experiments/r5_global_cut_hall_clause_20261015.py`.
- All statements below flagged THEOREM have elementary **all-n proofs**. Counts/test outputs are **finite controls**, not all-n complexity results.

## Definitions
Let `G=(V,E)` be a finite simple cubic graph. For binary vertex labeling `s`,
`M_s={uv in E:s(u)=s(v)}`. `s` is *admissible* if `M_s` is a matching.
Let `U_s=V\\V(M_s)`, `R_s=G[U_s]`, and `Delta(s)=|U_s|-2 nu(R_s)`.
The residual graph is bipartite. `Delta(s)` is always a **nonnegative even
integer**, since a cubic graph has an even number of vertices and removed
endpoints come in pairs. A zero-deficit admissible labeling is equivalent
to proper three-edge colorability of G.

## Theorem 1 — Hall-cut obstruction clause (global, all n)
Fix any admissible s. Let `X subseteq U_s` be contained in *one*
side of the residual bipartition, and suppose
```text
h_X = |X|-|N_{R_s}(X)| > 0.
```
Let `S=N_G[X] = X union N_G(X)` be the closed neighbourhood in the
**original** G. Let `Star(S)={uv in E : u in S or v in S}`.

Then for **every** F subset V such that s' = s XOR 1_F is admissible
and Delta(s')=0, the switching cut C=delta_G(F) satisfies
```text
C cap Star(S) != empty.
```
Equivalently in binary edge-change indicators `t_e=1[e in C]`,
```text
sum_{e in Star(S)} t_e >= 1.
```

*Proof.* Suppose C avoids Star(S). For every v in S, every incident
edge has exactly the same endpoint-equality status under s and s'.
Thus each vertex in X, and each original neighbour of X, retains its
membership in `U_s` versus `V\\U_s`. Moreover G is unchanged.
Therefore X is still an independent subset of `U_{s'}` with exactly
the same neighbours in `R_{s'}`, namely `N_{R_s}(X)`. Every matching
covering all vertices of X would have to match them to distinct
neighbours outside X; since there are fewer such neighbours than
vertices in X, this is impossible. In particular `R_{s'}` has no
perfect matching, contradicting Delta(s')=0. QED.

**Scope warning:** This clause is necessary for reaching **zero
deficit**, NOT for every strict improvement from an arbitrary
Delta(s)>0. Because Delta is even, at Delta(s)=2 every strict descent
does reach zero, so the clause also blocks all strictly improving
transitions from a Delta=2 Hall state. At higher starting deficiency,
an improvement to a still-positive deficiency may preserve a particular
Hall violation.

**Complement invariance:** The cut C is unchanged when F is replaced
by V\\F. Thus this clause blocks the ineffective all-vertex complement
as well as identity (both C=empty) without excluding any valid SAT
terminal.

**Polynomial fixed-state separation:** Find a maximum bipartite
matching in R_s. Start alternating-path search from unmatched vertices
of the smaller bipartition and collect reachable vertices X there.
The reachable neighbours are N_R(X); Hall's equality gives
`|X|-|N_R(X)|=|U_min|-nu(R_s)`. The executable independently
implements elementary augmenting paths and alternating reachability
at O(n|E|), without enumerating subsets. THIS DOES NOT solve the
global search over future s' or F.

## Theorem 2 — exact cutspace-compatible matching correspondence
Fix admissible s on **connected** G and M=M_s. For every matching M'
in G, there exists an admissible vertex labelling s' with M_{s'}=M'
iff
```text
C = M symmetric_difference M' belongs to the binary cut space of G.
```
For every qualifying M' there are precisely **two** corresponding s':
they are global complements.

*Proof.* If M'=M_{s'}, the cut-switch identity gives
`M symmetric_difference M'=delta_G({v:s(v) != s'(v)})`.
Conversely, if C=delta_G(F), use s'=s XOR 1_F: its monochromatic set
is M symmetric_difference C=M', a matching. In a connected graph,
two vertex subsets have the same cut iff they are identical or
complements, so these are precisely the two labelings. QED.

Cutspace membership has a **polynomial certificate**. Choose a spanning
tree T and for each non-tree edge e form its fundamental cycle Z_e.
Then C is a cut iff
```text
|C cap Z_e| is even for all e outside T.
```
There are exactly `|E|-|V|+1` such conditions in connected G;
for cubic G this equals `|V|/2+1`. After they hold, recover F up
to complement by propagating endpoint XOR constraints on T.

Because both M and M' are matchings, their symmetric difference
C consists of disjoint alternating paths and even alternating cycles.
At the endpoints of an alternating path, a newly added edge can only
terminate at a vertex free in M. Thus a potential universal global
step is precisely the search for **cutspace-compatible alternating
matching exchanges** with improved residual matching deficiency.

Although each candidate is checkable in polynomial time, finding one
with smaller Delta on every SAT input is still the unresolved
NP-hard global search.

## Theorem 3 — universal cut-size Lipschitz bound
For any two admissible s,s' with F={v:s(v)!=s'(v)}, C=delta_G(F),
```text
abs(Delta(s')-Delta(s)) <= 2 |C|.
```
*Proof.* By the cut-switch law, M_{s'}=M_s symmetric_difference C.
The set of vertices incident with the changed matching edges has
size at most 2|C|. All other vertices have exactly the same status
in U_s and U_{s'}, so `|U_s symmetric_difference U_{s'}| <= 2|C|`.
The function `D(U)=|U|-2 nu(G[U])` changes in absolute value by
at most 1 when one vertex is added or removed: the maximum matching
size changes by 0 or 1. Telescope over changed vertices. QED.

Consequence: a zero-deficit target must switch at least
`Delta(s)/2` **edges in its cut**; the number of flipped vertices
alone does not imply this bound.

## Theorem 4 — exact balance constraint on terminal flip sets
For a zero-deficit s', the original two label classes must end up
equal in size. If `a=|F cap V_0|` and `b=|F cap V_1|`, then
```text
a-b = (|V_0|-|V_1|)/2.
```
This is immediate by equating `|V_0|-a+b` and `|V_1|-b+a`.
It is a necessary global cardinality equation, not a guarantee that
Hall deficiency vanishes.

## A necessary Hall clause is not sufficient (explicit adversarial control)
For the balanced Hall-obstructed SAT start `s=551` on the n=10 fixture
(`Delta(s)=2`, witness X={3}), choose the alternative admissible
balanced mask `s'=682`. Then the cut C=delta_G({v:s(v)!=s'(v)})
contains 6 edges, **4** of which meet `Star(N_G[X])`. The exact
Hall-cut inequality and terminal balance equation are satisfied, and
`M_{s'}` is a matching — but **`Delta(s')=2`**, so no improvement
occurred. This is a finite counterexample to the sufficiency of the
combined necessary constraints. They are sound search filters only.
The exact checker explicitly asserts this false-positive control.

## Reproducible finite controls
Run from repository root:
```bash
python3 experiments/r5_tutte_deficit_local_trap_20261014.py
python3 experiments/r5_tutte_hall_decomposition_20261014.py
python3 experiments/r5_global_cut_hall_clause_20261015.py
```
The new checker uses a polynomial bipartite matching and Hall witness
routine on each **fixed** admissible labeling; for each finite graph it
exhaustively enumerates all admissible labelings and all their pairs.
Controls: K4, K3,3, Petersen, connected SAT n=10, connected SAT n=12.

Frozen checks on n=10: 16 admissible labelings (12 terminal zero);
4 positive-Hall states times 12 terminal states = 48 cut-clause
assertions; anchored at s=551, Hall X={3}, N_R(X)=empty, and minimum
Hamming / cut size of zero descendants are respectively 2 and 4.
Frozen n=12: 10 admissible labelings, 8 terminal zero; anchored
at s=1246, minimum Hamming 5 and cut size 5 to a zero descendant.
The script also validates cut exchange, alternating matching
structure, balance and Lipschitz for all tested admissible pairs.

The finite verifier is EXPONENTIAL in n (enumeration of labellings);
these checks provide only replayable finite controls for the all-n proofs.

## Literature context (not proof of the universal algorithm)
- Aslanyan et al., *On disjoint matchings in cubic graphs: maximum 2- and
  3-edge-colorable subgraphs*, 2009/2014, https://arxiv.org/abs/0909.2767 .
- Edwards, Sanders, Seymour, Thomas, *Three-edge-colouring doublecross
  cubic graphs*, 2016, https://arxiv.org/abs/1411.4352 .
- Inoue et al., *Three-edge-coloring apex cubic graphs*, 2026, arXiv
  2608.22870; describes a polynomial constructive algorithm for a
  restricted class, **not** a universal Holyer-hard solution.

## Next rigorous gate
Develop a deterministic `GlobalCutImprove` algorithm that, on *all*
legal connected cubic graphs and every admissible positive-Delta s,
finds a lower-Delta admissible s' whenever the graph is 3-edge-colourable,
with a uniform O(n^C) runtime. It may incorporate polynomially
separated Hall cut clauses, cutspace parity, alternating exchanges,
and balance, but must prove a uniform bound on **total iterations,
search complexity and intermediate representation size**.

Petersen (UNSAT) may be stopped only with a correct decision; the n=10
balanced Hall SAT case and n=12 imbalance SAT trap must not be
incorrectly declared UNSAT. No number of finite controls proves all-n
tractability. `GlobalCutImprove`: NOT CONSTRUCTED.
`SolveLinearCubicXSAT`: NOT CONSTRUCTED. `P vs NP`: OPEN.
