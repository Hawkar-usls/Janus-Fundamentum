# R5 E10A — Two-Row Graph-Lift Distinguished-f Source Audit

Date: 2026-09-24

Authority:
`SOURCE_AUDIT_ONLY__PASS_SCOPED_GAP_CONFIRMED`

Governance parent:
`JANUS_GLOBAL_PREMATH_NO_DUPLICATION_GATE_2026-09-24_v1.0`

Strategic parent:
`R5_E10A_FIRST_NON_GRAPH_LIFT_DISTINGUISHED_F_GATE_V1`

## G0 — exact frozen representation

This audit intentionally separates **row-lift dimension** from additive
perturbation rank.

The input representation is literally

```
A =
[ B_G ]
[ S   ],
```

where:

- `B_G` is a reduced binary vertex-edge incidence matrix of an undirected
  multigraph `G`;
- `S in GF(2)^(2 x E)` consists of exactly two signature rows;
- every element is therefore an edge `e=ab` carrying a label
  `lambda(e) in GF(2)^2`.

For a distinguished element `f=uv`, a set `J subseteq E-{f}` spans `f`
exactly when

```
boundary(J) = {u,v}
and
sum_{e in J} lambda(e) = lambda(f) in GF(2)^2.
```

Thus shortest-`f` is the minimum-cardinality `{u,v}`-join with a prescribed
`GF(2)^2` label, plus one for `f`.

This is the exact two-signature-row graph-lift object. It is **not**
`I(G)+P, rank(P)<=2`.

## G1 — internal anti-duplication

Fundamentum searches included:

- parity T-join;
- two parity constraints;
- group-labelled / group-labeled T-join;
- homology T-join;
- rank-k graphic lift;
- GF(2)^2;
- cycle labels;
- Space Cover;
- exact / parity matching.

No earlier artifact closing this exact two-row graph-lift distinguished-`f`
problem was located.

The following parents remain source-bound and must not be repeated:

- ordinary graphic shortest-`f`;
- one-row even-cycle / parity T-join;
- full trellis/min-plus conditional syndrome tables;
- additive rank-2 perturbed-graphic Space Cover (PA-0004).

## G2 — canonical external names

Primary canonical language:

- minimum-weight `T`-join with a prescribed finite-abelian-group label;
- group-constrained circulation;
- graphic rank-`k` lift / group-labeled graph lift;
- parity/congruency-constrained combinatorial optimization.

The exact group here is

```
Gamma = GF(2)^2.
```

Walsh's rank-`k` lift work supplies source context for higher-rank lifts of
graphic matroids and their relation to group-labeled graphs. It is structural
background, not by itself a shortest-`f` algorithm.

## G3 — source exhaustion

### S1 — rank-one baseline

For one signature row, the problem is the source-bound even-cycle lane:
minimum distinguished circuit reduces to a `{u,v}`-join with one prescribed
parity. Cook–Espinoza–Goycoolea give a polynomial algorithm for minimum-weight
odd/even `T`-join with nonnegative weights. Therefore row-lift dimension one
is already a deterministic polynomial terminal.

### S2 — finite-group constrained TU / circulation

Nägele–Santiago–Zenklusen and subsequent group-constrained extensions formulate
Group-Constrained Circulation:

```
minimum-cost integral circulation
subject to
sum_a eta(a) x_a = g in a finite abelian group.
```

For network-matrix GCTU with a finite abelian group and unary encoded objectives,
the cited source gives a strongly polynomial **randomized** algorithm. The
randomization is inherited from exact-length circulation / exact-cost perfect
matching machinery.

Consequently, once the two-row distinguished-`f` problem is represented as a
`GF(2)^2`-constrained `{u,v}`-join / circulation, there is a source-backed
randomized-polynomial route.

For every fixed number `r` of signature rows, the same mechanism uses a fixed
finite group `GF(2)^r` (plus standard flow bookkeeping) and therefore gives a
fixed-`r` randomized-polynomial lane.

This does **not** establish deterministic P.

### S3 — exact matching derandomization firewall

Exact Matching has had a randomized polynomial algorithm since the
Mulmuley–Vazirani–Vazirani line, while a deterministic polynomial algorithm
remains open. Current 2023–2026 work continues to state that derandomization is
open and supplies deterministic algorithms only for restricted classes or
relaxations.

This source fact explains why the group-constrained circulation theorem is
randomized. It does **not** prove that the present two-row T-join subclass is
equivalent to Exact Matching, and JANUS must not claim such an equivalence
without a reduction.

### S4 — group-labelled shortest path is not enough

Iwata–Yamaguchi give a deterministic strongly polynomial shortest non-zero path
algorithm for finite abelian group-labeled graphs.

A `{u,v}`-join with a prescribed total group label may contain Eulerian cycle
components in addition to the terminal path. Therefore the path theorem alone
does not close the group-constrained T-join problem.

### S5 — one-parity T-join caution

Schlotter–Sebő further emphasize that path and T-join parity problems have
different complexity behavior. This reinforces the firewall against replacing
the T-join by a path without a proof.


### S6 — 2026 bipartite Exact Matching candidate: quarantine, not authority

Yuefeng Du,
*Bipartite Exact Matching in P*,
arXiv:2604.01571 (2026), currently a CoRR/arXiv preprint.

The paper claims a deterministic \`O(n^6)\` algorithm for Exact Matching on
bipartite graphs.

This is potentially dominating for the present JANUS route because a
witness-preserving reduction

\`\`\`
bounded-capacity exact-length circulation
-> bipartite b-factor of exact weight
-> bipartite exact-weight perfect matching
-> bipartite red/blue Exact Matching
\`\`\`

would turn the existing randomized GCC lane into a deterministic lane.

However, the source is **not promoted to authority in this audit**.

The abstract says that the entire proof has been formally verified in Lean 4,
but Appendix A explicitly describes the formalization as partial: the top-level
brace certification theorem remains conditional on eight structural hypotheses,
including graph-to-algebra bridge obligations and the imported McCuaig
classification linkage.  Thus the machine-checking statement is materially
weaker than a fully closed end-to-end formal proof.

As of this audit, the work is an arXiv/CoRR preprint and an independent proof
tracker lists it as a candidate not yet independently examined.

JANUS classification:

\`\`\`
DU-2026 BIPARTITE EXACT MATCHING IN P
=
EXTERNAL_CANDIDATE_UNVERIFIED

USE
=
CONDITIONAL DONOR / FUTURE PROMOTION TARGET

NOT
=
SOURCE-BOUND DETERMINISTIC TERMINAL
\`\`\`

No P-vs-NP or deterministic-JANUS claim may depend on this source until the
missing verification/acceptance layer is resolved.

### S7 — standard exact-matching transfer pieces

Two standard transformations were source-checked because they are needed to
decide whether Du's claimed theorem, if later validated, would dominate this
frontier.

1. **Bipartite b-factor to bipartite perfect matching.**
   Standard b-factor gadgets replace each original vertex/edge by copy/peripheral
   vertices so that perfect matchings correspond exactly to b-factors.  When the
   starting b-factor graph is bipartite, the gadget can retain a bipartition.

2. **Polynomially bounded exact-weight perfect matching to red/blue Exact
   Matching.**
   Gurjar--Korwar--Messner--Thierauf record the standard logspace equivalence:
   after making weights positive, an edge of weight \`w\` is replaced by an odd
   alternating red/blue path with \`w\` red and \`w-1\` blue edges.  Polynomial
   weights give polynomial expansion.  For a bipartite starting graph, replacing
   an edge joining opposite sides by an odd path preserves bipartiteness.

These facts do not yet provide a deterministic solver.  They authorize the next
JANUS brick to prove/check the remaining exact bridge from the bounded-capacity
exact-length circulation produced by GCC to an exact-weight **bipartite**
b-factor, including cost and witness preservation.


## G4 — collision matrix

| JANUS object | External object | Classification | Action |
| --- | --- | --- | --- |
| one signature row | even-cycle / signed-graph matroid | STRONGER_KNOWN_RESULT | deterministic poly terminal |
| two signature rows | GF(2)^2-labelled T-join | EXACT_LANGUAGE_COLLISION | use canonical language |
| fixed-r signature rows | finite-group-labelled graphic lift | KNOWN_STRUCTURAL_DONOR | source-bind Walsh |
| group-constrained circulation | GCTU/GCC | STRONGER_KNOWN_RANDOMIZED_RESULT | randomized terminal only |
| generic deterministic exact-matching derandomization | Exact Matching | OPEN_EXTERNAL_BARRIER | do not assume |
| shortest non-zero group-labelled path | path donor | KNOWN_DONOR_ONLY | does not replace T-join |
| additive rank-2 perturbed graphic | I(G)+P | DIFFERENT_REPRESENTATION | PA-0004 reserve, do not conflate |
| Du-2026 bipartite Exact Matching in P | recent arXiv/CoRR claim with partial Lean formalization | EXTERNAL_CANDIDATE_UNVERIFIED | conditional donor only; no theorem promotion |
| bounded-capacity XLC -> bipartite exact-weight matching transfer | standard b-factor / exact-weight components plus one JANUS bridge obligation | SCOPED_GAP_SURVIVES | prove exact circulation-to-b-factor bridge |
| deterministic two-row distinguished-f solve | no authoritative closure located | SCOPED_GAP_SURVIVES | new math only here |

## Audit decision

```
ROW-LIFT r=0
=
DETERMINISTIC P

ROW-LIFT r=1
=
DETERMINISTIC P

FIXED ROW-LIFT r>=2
=
SOURCE-BACKED RANDOMIZED POLY
VIA FINITE-GROUP CIRCULATION

DETERMINISTIC r=2
=
NO CLOSURE LOCATED

ADDITIVE PERTURBATION RANK
!=
ROW-LIFT DIMENSION
```

Decision:

```
PASS_SCOPED_GAP_CONFIRMED
```

New mathematics is authorized only inside:

```
R5_E10A_TWO_ROW_GRAPH_LIFT_DETERMINISTIC_DISTINGUISHED_F_GATE_V1
```

The first allowed brick is deliberately narrow:

1. prove the exact two-row distinguished-`f` to finite-group-circulation bridge
   with polynomial witness reconstruction;
2. source-bind the resulting randomized solver;
3. first test the exact transfer `bounded-capacity XLC -> bipartite exact-weight matching`;
4. treat Du-2026 only as a conditional endpoint until independently validated;
5. continue seeking an unconditional **deterministic** special algorithm or contraction
   for this `GF(2)^2` T-join subclass, without full trellis/min-plus tables.

A randomized solver is useful as a control and terminal for RP-style experiments,
but it does not satisfy JANUS's deterministic `P` contract.


### S8 — exact-label shortest-path re-audit

The zero-sum correction-cycle compression exposed a smaller primitive, so the
source audit was reopened before any path theorem was attempted.

Yamaguchi's weighted-linear-matroid-parity line gives deterministic polynomial
algorithms for **shortest non-zero** paths for finitely generated abelian groups.
For \`GF(2)^2\`, "non-zero" minimizes over three labels and therefore does not
isolate one prescribed label.

Kawase--Kobayashi--Yamaguchi distinguish explicitly between finding an s-t path
of prescribed label alpha and finding a path whose label is not alpha. They
report Huynh's polynomial-time solvability of the **feasibility** version of the
prescribed-label problem for any fixed finite abelian group. This does not
optimize path length.

Bentert--Drange--Fomin--Golovach--Korhonen (ICALP 2024) define
**Xor-Constrained Shortest Path** exactly as a shortest simple s-t path whose
edge-label XOR equals a prescribed vector \`c in GF(2)^d\`. Their Theorem 2
gives a one-sided-error randomized algorithm in
\`2^(d+p)(n+m)^O(1)\` time. With \`d=2,p=0\`, this is exactly the path primitive
exposed by the JANUS two-row lift. The paper itself explains that earlier
group-labelled shortest-path work handles non-zero labels, while their
application needs one specific group element.

Yamaguchi's non-returning A-path / label-set-at-most-four theorem was also
checked. There \`|Omega|<=4\` is the size of a terminal-state label set in a
different non-returning A-path model; it is not the prescribed-sum shortest-path
objective here.

Therefore:

\`\`\`
DETERMINISTIC SHORTEST NON-ZERO
= SOURCE-BOUND, ADJACENT ONLY

FIXED-GROUP PRESCRIBED-LABEL FEASIBILITY
= SOURCE-BOUND, NO LENGTH OPTIMIZATION

PRESCRIBED-LABEL SHORTEST SIMPLE PATH IN GF(2)^2
= EXACT LANGUAGE COLLISION WITH XOR-CONSTRAINED SHORTEST PATH

KNOWN ALGORITHM
= RANDOMIZED POLYNOMIAL

DETERMINISTIC POLYNOMIAL CLOSURE
= NOT LOCATED IN THIS RE-AUDIT
\`\`\`

This is a scoped source-audit conclusion, not an absolute novelty claim.


### S9 — top-plateau / optimal-face parity re-audit

The pairwise-parity collapse exposed a new exact residual, so PA-0005 was reopened before attempting a theorem.

The source-bound one-bit parity/odd-path machinery reduces the unit-positive pair-class path optimum to a minimum-weight perfect matching in a generally non-bipartite auxiliary graph. El Maalouly--Steiner--Wulf prove deterministic polynomial Correct Parity Matching (CPM) for general graphs via Lovasz' linear hull, and deterministic polynomial Bounded Correct Parity Matching (BCPM) for bipartite graphs. Their paper explicitly leaves general-graph BCPM open; Murakami--Yamaguchi retain this boundary and give FPT progress via odd-cycle-transversal.

A tempting allowed-edge shortcut is source-valid only in the bipartite minimum-weight face: there the Birkhoff polytope has no blossom inequalities, so every perfect matching using only edges that occur in some optimum is again optimal. In general graphs Edmonds' odd-cut/blossom constraints remain part of the face, so deleting non-optimal edges alone is not an exact representation of the optimum family.

No located source closes the narrower object:

```
parity feasibility among minimum-weight
perfect matchings of a general graph,
with the minimum face represented by
tight edges + laminar positive blossoms.
```

This does not claim novelty of matching-face or blossom theory. It confirms only that the JANUS top-plateau reduction may target this narrower optimal-face parity object instead of general BCPM.
