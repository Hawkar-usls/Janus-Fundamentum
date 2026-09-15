# 2026-09-15 — Factorized feedback-interface portfolio PASS

Authority: `SCOPED_THEOREM_AND_IMPLEMENTATION_CHECK__NO_GLOBAL_PROMOTION`

## Parent

The preceding wide-interface gate established:

- unrestricted downstream contracts can force `2^|B|` exact classes;
- a strict affine-syndrome subclass admits exact polynomial quotient transfer.

Parent result head: `3df50dcb6ba8a9279b419d00661e837f529033a3`.

## Anti-loop reuse

Instead of inventing a new generic compressor, the successor reused the already sealed 2026-09-13 mechanism:

`TRUMP_EXACT_TYPED_INTERFACE_BASIS_FIXPOINT`

which had established that exactly disconnected typed OPEN cores can remain a factorized portfolio without Cartesian-product materialization.

## New theorem

For a canonical feedback interface `B`, construct the complete frozen downstream dependency hypergraph `H_B` from every transfer, message, and reconstruction scope.

If `H_B` decomposes into components `B_1,...,B_t`, every exact downstream obligation is component-local, and every component has a separately sealed exact polynomial local carrier, then exact transfer/reconstruction is represented as the additive portfolio

`[Q_1,...,Q_t]`

rather than the Cartesian product `Q_1 x ... x Q_t`.

Exactness follows from disjoint variable domains and complete scope coverage. Local exact witnesses union consistently. A replayable local exact conflict certifies global conflict. Any transfer or reconstruction relation spanning two blocks is itself a dependency edge and forces a component merge.

## Frozen lineage

- preregistration: `8235a16f956f388eb79c0f15961e22db7c088558`
- candidate: `c2d76540d3828e994983f9095d833d9511209233`
- independent checker: `fec844f00479490166f2063bc6bf242962cb39ed`
- workflow/head at execution: `46bd0f84b598cd4ede0978bfd5dbc3f3bf088f82`
- theorem note: `63da24a1a709853b9d88ad16345cb66e681a8d6c`
- result seal: `b4e26b71ad0f0d1aa69ee456efe0439cea48f28f`
- Actions run: `34910238642`
- job: `104195887552`

## Checker result

Verdict:

`PASS_SCOPED_FACTORIZED_FEEDBACK_INTERFACE_PORTFOLIO`

All independent checks passed.

Important controls:

- 32 disconnected components remained 32 disjoint local records;
- portfolio storage was additive;
- `cartesian_products_materialized = 0`;
- global raw `2^|B|` enumeration = 0;
- mixed raw-log-width + sealed affine-syndrome components reconstructed one exact witness;
- one exact local UNSAT component propagated global UNSAT;
- transfer cross-coupling merged former blocks and failed closed;
- reconstruction cross-coupling also merged former blocks and failed closed;
- unknown connected wide core returned `OPEN_UNSUPPORTED_LOCAL_CARRIER`.

Regression checks remained green for Trinity Sovereign, sealed unicyclic transfer, canonical logarithmic feedback-interface transfer, and affine wide-interface quotient.

## Complexity

`size(Q) = O(|H_B| + SUM_j size(Q_j))`

and

`T_total = T_build(H_B) + SUM_j T_local,j + poly(glue,replay)`.

For raw local carriers, `|B_j| <= floor(log2 L)` implies at most `L` local assignments. Affine local carriers inherit polynomial GF(2) lifecycle bounds. The formal product of local state counts may be exponential but is never materialized.

## Firewalls

- `P_VS_NP = OPEN`
- `GENERAL_SAT_IN_P = NOT_PROVED`
- universal wide-interface compression remains false for unrestricted downstream query contracts
- no global APMA frontier promotion

## Remaining exact open surface

`CONNECTED_WIDE_FEEDBACK_INTERFACE_OUTSIDE_RAW_LOG_AND_AFFINE_SYNDROME_CARRIERS`

Before inventing a new carrier, run a full anti-loop harvest over earlier exact typed-congruence, conditional-multirow, reachable-domain-guard, and query-specific quotient lineages.
