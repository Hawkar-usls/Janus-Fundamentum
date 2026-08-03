# C048 — Proof-carrying affine-subspace layout discovery

## Status

```text
C048 = IMPLEMENTED / DRAFT / REVIEW_PENDING
P_VS_NP = OPEN
```

C047 gives an exact offset-aware affine-functional trellis for one charged factor order. C048 adds a deterministic assignment-independent layout portfolio, freezes the complete candidate manifest before any trellis result is visible, runs exactly one bounded C047-style probe per unique order, and selects only a replayable SAT/UNSAT terminal.

## Input and cut width

Each forbidden factor is an affine subspace

\[
U_i=\{x:n\cdot x=\beta_i(n)\text{ for all }n\in N_i\}.
\]

For an order \(\pi\), define

\[
P_t=\sum_{j\le t}N_{\pi(j)},\qquad
S_t=\sum_{j>t}N_{\pi(j)},\qquad
B_t=P_t\cap S_t.
\]

The exact C047 probe has at most \(2^{\dim B_t}\) states at cut \(t\). C048 computes every \(B_t\) by RREF and records the complete width vector before accepting a candidate.

## Frozen constructors

The current fixed portfolio is:

```text
PARALLEL_BLOCKS_FIRST_OCCURRENCE
REVERSE_PARALLEL_BLOCKS
GREEDY_MIN_FRONTIER
GREEDY_MAX_PREFIX_OVERLAP
```

`GREEDY_MIN_FRONTIER` repeatedly chooses the remaining factor minimizing

\[
\dim\bigl((P+N_i)\cap \sum_{j\ne i}N_j\bigr),
\]

with a complete deterministic tie-break. `GREEDY_MAX_PREFIX_OVERLAP` first prefers the largest overlap with the current prefix and then minimizes the next frontier.

The constructors use only the normalized affine factors and their normal spaces. They do not inspect SAT witnesses, UNSAT terminals, branch assignments, or probe outcomes. Duplicate orders are removed before probing. The frozen manifest contains every order, exact cut widths, constructor aliases, discovery ledger, and one digest binding the entire candidate set.

## Selector theorem

For a fixed polynomial portfolio \(\mathcal P\), fixed C047 width/work/certificate capabilities, and charged polynomial discovery,

\[
T_{C048}(I)=\operatorname{poly}(|I|)+
\sum_{\pi\in\mathcal P}T_{C047}(I,\pi).
\]

Every unique candidate receives exactly one full offset-aware trellis probe. A candidate is selectable only if the probe returns replayable SAT or UNSAT. Successful candidates are ordered by

```text
(max_cut_width, total_cut_width, probe_work, layout_digest)
```

and the least tuple is selected. If all probes refuse, C048 returns `OPEN_PORTFOLIO_EXHAUSTED`.

This proves sound polynomial selection for the fixed portfolio. It does not prove that the portfolio contains a bounded-width order whenever one exists.

## Strict extension over C047

For \(d\ge3\), use ambient dimension \(d+1\), let \(z=e_{d+1}\), and define one-dimensional normal spaces

\[
a_i=e_i,\qquad b_i=e_i+z.
\]

The input order is

\[
a_1,\ldots,a_d,b_1,\ldots,b_d.
\]

At the middle cut,

\[
\dim(\operatorname{span}\{a_i\}\cap
\operatorname{span}\{b_i\})=d-1.
\]

Thus the C047 first-occurrence order has width \(d-1\). The greedy frontier constructor deterministically produces

\[
a_1,b_1,a_2,b_2,\ldots,a_d,b_d,
\]

whose maximum width is at most two. For the frozen control with \(d=20\):

```text
C047 baseline, cap 2 -> OPEN_CUT_WIDTH
exact baseline maximum width -> 19
C048 GREEDY_MIN_FRONTIER -> SAT
selected maximum width -> 2
```

The witness is checked against every original affine factor. This is a strict constructive layout-discovery extension, not a universal approximation theorem.

## Independent verification

The verifier does not import or call the C048 selector or order-probe producer. It independently:

1. normalizes the input factors;
2. reconstructs the frozen candidate manifest;
3. recomputes every cut space and width;
4. replays every offset-aware trellis transition from low-level GF(2) primitives;
5. rebuilds the deterministic selection tuple;
6. reproduces discovery and certificate refusals;
7. checks the selector fixed-point byte accounting and integrity digest.

## Exact boundaries

The 24-variable NAND3 pressure image remains:

```text
OPEN_PORTFOLIO_EXHAUSTED
```

Every unique frozen layout exceeds the fixed width capability. This is evidence only that the present constructors are incomplete. It is not a pathwidth lower bound, not a lower bound against branch decompositions, and not evidence for `P != NP`.

## Surviving gate

```text
POLYNOMIAL_LAYOUT_PORTFOLIO_COMPLETENESS
OR
FIXED_WIDTH_BRANCH_DECOMPOSITION_DISCOVERY
```

The next construction must either prove completeness of a polynomial candidate family on a substantially broader class, or implement a charged fixed-width branch-decomposition algorithm with offset-aware C047 messages.
