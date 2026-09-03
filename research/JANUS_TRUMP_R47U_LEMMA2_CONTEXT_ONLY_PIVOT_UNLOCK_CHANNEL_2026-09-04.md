# JANUS TRUMP R47U — Lemma 2: Context-Only Pivot Unlock Channel

Status: **SYMBOLIC IDENTITY + SEALED FINITE WITNESS; NOT A SERIAL FAMILY THEOREM**

## Exact-DP decomposition

For a formula `F` and pivot `v`, write

- `P_v(F)` for clauses containing `v`,
- `N_v(F)` for clauses containing `-v`,
- `B_v(F)` for all clauses containing neither polarity of `v`,
- `R_v(F)` for the canonical set of all non-tautological exact-DP resolvents from `P_v(F) x N_v(F)`.

The forced exact-DP state before later normalization is

`D_v(F) = SubMin(Canonical(B_v(F) union R_v(F)))`.

## Identity

Let `F` and `G` be two states with

`P_v(F)=P_v(G)` and `N_v(F)=N_v(G)`.

Then automatically

`R_v(F)=R_v(G)`.

Therefore every difference between `D_v(F)` and `D_v(G)` is caused exclusively by the changed background context

`B_v(F) != B_v(G)`

and its interactions with the same fixed resolvent set under canonicalization/subsumption.

In particular, a predecessor macro can change whether pivot `v` eventually becomes accepted **without changing v's own parents, polarity counts, parent-pair product, or resolvent set**.

This is the **context-only unlock channel**.

## R47T sealed witness

For the R47K residual

`hash = 9a84c02f1570e752ac0c017037b8a4a40c2599b53faf51bcd6d957f40aa81dde`

with `CLV=[77,206,22]`, the certified sequence `(11,20)` exhibits exactly this channel.

Before eliminating 11, pivot 20 has:

- `p=8`, `n=2`, `p*n=16`,
- 15 distinct non-tautological resolvents,
- forced-DP `CLV=[81,226,21]`,
- normalized final `CLV=[77,208,21]`, not accepted.

After the certified nonaccepted v11 layer reaches `G1=[77,210,21]`, pivot 20 still has:

- `p=8`, `n=2`, `p*n=16`,
- exactly the same 15 resolvents,
- exactly the same parent set,
- exactly the same resolvent set,

but its forced-DP state is now `CLV=[80,227,20]` and normalization reaches `[76,209,20]`, accepted.

The measured delta is:

- parent-pair product: 0,
- distinct resolvents: 0,
- forced-DP clauses: -1,
- forced-DP literals: +1,
- normalized final clauses: -1,
- normalized final literals: +1.

The successful path contains an explicit RUP event `C:80 -> 76`, with six removed clauses and two added strengthened clauses.

Thus the local unlock cannot be explained by lower v20 occurrence degree, fewer v20 parent pairs, or fewer v20 resolvents. It is a background-context effect.

## Consequence for serial amplification

A candidate serial gadget does not need stage `i` to rewrite the parent set of stage `i+1`. It may instead preserve the next pivot's local resolution generator while changing a small background clause interface that controls whether the fixed resolvent set is absorbed/subsumed/strengthened enough to cross the acceptance threshold.

This suggests a possible chained architecture:

`LOCK_i context --DP_i+closure--> UNLOCK_{i+1} context`

with each next pivot's own parent/resolvent skeleton held invariant.

Such an architecture is attractive for R47U Lemma 1 because a lock rank may be encoded by which contextual interfaces have been rewritten, while bypass resistance would require proving that one macro layer cannot rewrite more than one interface.

## Critical missing theorem

The finite R47T witness does **not** prove that context-only unlocks compose serially.

A real amplification construction must still prove:

1. context interfaces can be concatenated with only polynomial size growth;
2. stage `i` changes the interface for stage `i+1` but not for stages `i+2,...`;
3. arbitrary alternate pivots cannot skip an interface;
4. normalization closure cannot propagate through multiple interfaces in one layer;
5. the pre-macro stack preserves the intended chain and reachability;
6. terminal/strict-CLV acceptance remains impossible before the required final stage.

Conversely, if normalization necessarily propagates a context rewrite through arbitrarily many such interfaces in one layer, that is evidence toward a structural-collapse theorem rather than serial amplification.

## Next killer test

Construct or falsify a **three-stage contextual chain** in which:

- stage A is nonaccepted but rewrites only interface AB;
- B is nonaccepted before A;
- after A, B executes but remains nonaccepted relative to the original macro input while rewriting only interface BC;
- C is nonaccepted before A,B and becomes accepted only after the ordered composition A->B;
- exhaustive depth `<3` replay confirms no bypass sequence.

A success is only a finite `d(F)>=3` witness unless accompanied by a scalable lock-rank construction.
A systematic failure caused by closure crossing multiple interfaces becomes a candidate collapse mechanism.

## Firewalls

`SERIAL_CONTEXT_CHAIN_EXISTS = NOT_PROVED`

`UNIVERSAL_CONSTANT_K_EXISTS = NOT_PROVED`

`O4_UNIVERSAL_COVERAGE = OPEN`

`SAT_IN_P = NOT_PROVED`

`P_EQ_NP = NOT_PROVED`

`P_NE_NP = NOT_PROVED`

`P_VS_NP = OPEN`

`TRUMP_finished = false`
