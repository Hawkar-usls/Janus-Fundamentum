# R5 — Quantitative global Hall repair and polynomial-search equivalence
Scientific date: 2026-10-15. Source: follow-up of draft PR #518 and open issue #519.

## Scientific provenance
Base for this pass: research/r5-tutte-deficit-local-trap-20261014 at 87ef46b69c81ddc07919325f595157320807303c; combined CI SUCCESS run 38642824082. All-n proofs below are algebraic; finite regression is exactly replayed by experiments/r5_global_quantitative_hall_repair_20261015.py. This file does not certify a universal polynomial algorithm. P vs NP remains OPEN.

## Definitions
G=(V,E) simple cubic; s a binary vertex labeling. M_s={uv in E:s(u)=s(v)} is a matching (admissibility). U_s=V without endpoints of M_s; R_s=G[U_s]. Delta(s)=|U_s|-2nu(R_s). Let X subset U_s lie entirely in one bipartition side of R_s, and let h_X=|X|-|N_{R_s}(X)|>0. Let W_X=N_G(X) setminus U_s. Thus W_X are the original G-neighbors of X that are not initially exposed in the residual matching graph.

For a target admissible s', let C=delta_G({v:s(v)!=s'(v)})=M_s symmetric_difference M_{s'}. Let E_star(X)={uv in E:u in X or v in X}. Since X subset U_s and all vertices of X share the same label, X is independent and no edge of M_s touches X.

## Theorem A — membership repair capacity (valid on every cubic G)
For every admissible target s' with Delta(s')=0, define
  r_X=|X setminus U_{s'}|,
  a_X=|(N_G(X) setminus U_s) intersect U_{s'}|.
Then
  r_X + a_X >= h_X.
Proof: X'=X intersect U_{s'} has |X|-r_X elements. A perfect matching of R_{s'} must match all of X' into distinct vertices of N_G(X) intersect U_{s'}. There are at most |N_{R_s}(X)|+a_X such neighbors. Subtract. QED.

This is a necessary bound on actual repair of the deficient neighborhood. It says nothing about how to efficiently locate a suitable target.

## Theorem B — weighted exact cut capacity (valid on every cubic G)
Write C=M_s symmetric_difference M_{s'}. Then for every admissible s' (even with Delta(s')>0) we have the unconditional upper bound
  r_X + a_X <= |C intersect E_star(X)|
              + sum_{e in C intersect M_s} |e intersect W_X|.
Consequently every zero-deficit target satisfies:
  |C intersect E_star(X)|
  + sum_{e in C intersect M_s} |e intersect W_X| >= h_X.

Proof. If x in X stops being exposed, some formerly absent monochromatic edge e incident with x appears in M_{s'}. Because no M_s edge touches X, this e is in C intersect E_star(X). Distinct x cannot share an edge because X is independent, hence r_X is at most the first term. If w in W_X becomes exposed, its incident old M_s edge e is absent from M_{s'} and hence e lies in C intersect M_s. Each such e can have up to two endpoints in W_X; the weight |e intersect W_X| exactly upper-bounds the number of newly exposed W_X vertices covered by that old edge. Adding gives the inequality. QED.

This sharpens the old unweighted clause C intersect E_G(N_G[X]) != empty. It omits irrelevant cut edges and enforces a numerical repair budget. It remains necessary, not sufficient. Multiple source Hall witnesses each give a valid inequality on any zero-deficit target.

Notice that checking the inequalities for a proposed C costs polynomial time, and a violated Hall witness X can be found by a polynomial-time bipartite matching on **fixed** s. Nothing proves polynomial-time simultaneous construction of C over the exponentially large cut space.

## Theorem C — uniform global-improvement operator would solve P vs NP
Assume a deterministic algorithm `GlobalCutImprove(G,s)` with one universal polynomial bound in n on *every input*, which for every connected simple cubic G and admissible s:
  (i) returns another admissible s' with Delta(s')<Delta(s) if G is SAT and Delta(s)>0; or
  (ii) correctly reports UNSAT when G has no proper 3-edge-coloring.
On inputs with Delta(s)=0, return s.

Then P=NP.

Proof. First construct some admissible s in polynomial time: begin with any vertex bicoloring; whenever a vertex has at least two same-colored neighbors, flip it. Since degree is three, this flip increases the number of cross edges by at least one. There are at most |E| such improving flips, so this process stops with at most one monochromatic edge incident to each vertex, i.e. admissible s. At each later step compute Delta(s) by maximum bipartite matching (polynomial time). If Delta=0 produce a 3-edge-coloring; otherwise apply GlobalCutImprove. If G SAT, Delta decreases by an even positive integer and is initially <=n; thus in <=n/2 calls Delta reaches zero. If G UNSAT, the postulated algorithm returns the correct UNSAT decision in polynomial time. Hence 3-edge-coloring cubic graphs belongs to P, implying P=NP via Holyer's NP-completeness.

Conversely, if P=NP, a standard self-reduction recovers a witness for the NP relation "G has a 3-edge-coloring" in polynomial time (or decides UNSAT). Convert the found coloring into a balanced admissible s' with Delta(s')=0, so a GlobalCutImprove procedure with the above contract exists. Thus this **fully total deterministic polynomial global-improvement contract is equivalent to P=NP**. This is a conditional equivalence, not a proof of either direction's conjectured polynomial construction.

The argument requires total polynomial halting and a correct answer on UNSAT graphs; a *SAT-only promise* subroutine with no behavior specified on UNSAT does NOT automatically give an NP decision algorithm.

## Finite regression and falsification boundary
Run from repository root:
  python3 experiments/r5_global_quantitative_hall_repair_20261015.py

The checker exhaustively enumerates all admissible s on five frozen small cubic graphs (K4, K3,3, Petersen, a n=10 connected SAT Hall trap, n=12 connected SAT imbalance trap). It enumerates **every** Hall-deficient subset X in both residual bipartition sides, not just a selected witness, and checks the unconditional cut-capacity upper bound on all admissible pairs and the quantitative Hall-repair inequality on every zero-deficit target. The test runtime is exponential in n; this is for finite falsification and provenance only.

For the n=10 SAT fixture, source mask 551 has X={3}, h_X=1. Source mask 551 -> target 682 is an admissible balanced move hitting the Hall star but keeps Delta=2. Therefore the weighted cut inequality and exact cutspace/matching constraints are also only necessary. No claim of closure follows.

## Required next theorem or counterexample
The research objective remains a deterministic polynomial-time **search**, not short static necessary inequalities: given arbitrary G,s as above, find a cut C satisfying cutspace membership, terminal balance, matching admissibility, and all dynamic Hall demands such that Delta strictly decreases; or return a sound UNSAT result. Prove bound O(n^C) on total candidate-generation, constraint handling, updates and iterations for a universal constant C. Any claimed algorithm must run on both SAT fixtures and Petersen; isolated subclass, bounded-n scan, oracle assumption or syntactic formula is not closure.

Ledger:
- Hall membership bound: PROVED all n.
- Weighted cut repair bound: PROVED all n.
- Polynomial construction of fixed-s Hall witness: PROVED (previous PR checkpoint).
- Total polynomial GlobalCutImprove iff P=NP: PROVED conditional equivalence.
- Uniform polynomial GlobalCutImprove: NOT CONSTRUCTED.
- NonzeroSqFreeDet: NOT CONSTRUCTED.
- SolveLinearCubicXSAT: NOT CONSTRUCTED.
- P vs NP: OPEN.
