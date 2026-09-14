# C023R theorem note — expander boundary / stifling / residual-width tradeoff

Authority: `HQ_SYMBOLIC_THEOREM_NOTE__NO_GLOBAL_PROMOTION`

## Setting

Let `Q` be a nonempty connected proper vertex set in a simple graph carrying MAJ3-lifted Tseitin constraints. Let `delta(Q)` be the set of edges with exactly one endpoint in `Q`. For each edge `e`, let `z_e` be its three MAJ3 coordinates and let `g(z_e)=MAJ3(z_e)`.

## Lemma 1 — exact boundary projection of a connected region

Conjoin the Tseitin vertex equations for vertices in `Q` and existentially quantify all internal edge blocks.

XORing the vertex equations cancels every internal edge output twice and gives the necessary boundary equation

`XOR_{e in delta(Q)} g(z_e) = c_Q`,

where `c_Q` is the XOR of charges in `Q`.

This equation is also sufficient for boundary extendibility. Fix any boundary gadget-output vector satisfying the displayed parity equation. The remaining internal edge-output equations form a GF(2) incidence system on the connected internal graph induced by `Q`. Its incidence matrix has rank `|Q|-1`; the only consistency condition is that the right-hand side has even total parity, exactly the displayed boundary equation. Hence internal edge outputs exist. Each internal output bit has a nonempty MAJ3 fibre, so internal gadget coordinates can be chosen as well.

Therefore the exact existential projection onto boundary gadget coordinates is precisely

`R_Q = { z_delta : XOR_e MAJ3(z_e) = c_Q }`.

## Lemma 2 — minimum forcing cost of a restricted boundary parity

Let `alpha` be any partial assignment to boundary gadget coordinates. For each boundary block `e`, call its residual MAJ3 output **forced** when every completion of the remaining block coordinates has the same MAJ3 value; otherwise call it **flexible**.

Let `U_alpha` be the set of flexible boundary blocks.

Consider any clause `C` over currently unassigned boundary coordinates that is an implicate of the restricted relation `R_Q | alpha`. Falsifying `C` gives an additional partial assignment `beta`.

If some boundary block remains output-flexible under `alpha union beta`, then because blocks are independent one can choose that block's output to repair the single parity equation after choosing arbitrary extensions of all other flexible blocks. Hence `alpha union beta` would still have a satisfying extension, contradicting that `C` is an implicate.

Therefore falsifying any implicate must force every previously flexible boundary block. Assigning one remaining coordinate can force at most the block containing that coordinate, so

`width(C) >= |U_alpha|`.

Equivalently, any boundary-only implicate of width `W` implies

`|U_alpha| <= W`.

## Lemma 3 — forced MAJ3 output costs at least two assigned coordinates

With zero assigned coordinates, MAJ3 can output both values. With exactly one assigned coordinate, the two unassigned coordinates still admit completions of both outputs. Therefore a block whose output is already forced by `alpha` contains at least two assigned coordinates (necessarily enough to stifle the block; two equal bits are the minimal case).

Since at least `|delta(Q)|-W` boundary blocks are already forced whenever a boundary-only implicate of width `W` exists,

`|alpha restricted to boundary coordinates| >= 2 ( |delta(Q)| - W )`.

This is an exact history charge, not a probabilistic statement.

## Corollary 1 — q=4 Ramanujan expansion charge

For the frozen 5-regular q=4 Morgenstern family, the registered spectral binding gives Laplacian gap at least 1. For every `Q` with `|Q| <= N/2`, Rayleigh's cut bound gives

`|delta(Q)| >= |Q|(N-|Q|)/N >= |Q|/2`.

Combining with Lemma 3:

`|alpha_boundary| >= |Q| - 2W`,

or equivalently

`|Q| <= |alpha_boundary| + 2W`.

Thus a narrow boundary-only reason with large connected provenance is possible only after the execution history has already assigned linearly many boundary gadget coordinates.

## Exact forcing-cost refinement

For a boundary block `e` and target output `b`, define `kappa_e^alpha(b)` as the minimum number of additional unassigned block coordinates that must be fixed so that every completion has MAJ3 output `b`, with infinity if `b` is impossible from the current restriction.

Then the exact minimum width of a boundary implicate of `R_Q|alpha` is

`min_{y : XOR y != c_Q'} sum_e kappa_e^alpha(y_e)`,

where `c_Q'` is the parity target after already-forced outputs are absorbed. The lower bound `width >= |U_alpha|` is its coarse consequence because every flexible block has forcing cost at least 1.

## Claim boundary

This theorem applies to clauses whose semantic consequence is considered after projecting a connected source region onto its boundary blocks. It does not assert that every historical inherited clause is boundary-only, nor that provenance can be reconstructed from a cache key.

It therefore does not yet prove near-injective cache history or a cache lower bound.

## Next missing link

`C023R_HISTORY_CHARGE_TO_CACHE_FIBER_INJECTIVITY`

The remaining question is whether the linearly many boundary assignments charged above are themselves recoverable (up to `o(L)` ambiguity) from the exact historical key / inherited-clause basis, or whether many different stifling assignments can erase to the same byte-identical key. The latter would seed the serial-diamond falsifier route.