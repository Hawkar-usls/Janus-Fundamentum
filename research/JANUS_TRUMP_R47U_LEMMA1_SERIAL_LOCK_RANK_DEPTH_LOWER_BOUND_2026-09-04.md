# JANUS TRUMP R47U — Lemma 1: Serial Lock-Rank Depth Lower Bound

Status: **SYMBOLIC ABSTRACT LEMMA — DOES NOT YET CONSTRUCT A CNF FAMILY**

## Setup

Fix a macro input residual state `F0` and the frozen one-layer operator

`T_v(F) := NORMALIZATION_CLOSURE(EXACT_DP_v(F))`

for every legal pivot `v` in state `F`.

A finite ordered pivot sequence `sigma=(v1,...,vt)` is *accepted relative to F0* iff its independently replayed composition reaches a semantic terminal or its final canonical state has

`CLV(T_sigma(F0)) < CLV(F0)`.

Let `d(F0)` be the minimum accepted sequence length, with infinity if no finite accepted sequence exists.

## Lemma

Let `k>=1`. Suppose there exists an integer-valued lock rank

`lambda : S -> {0,1,...,k}`

defined on every state `S` reachable from `F0` by fewer than `k` frozen macro layers, satisfying all of:

1. **Initial lock**: `lambda(F0)=0`.
2. **One-stage unlock bound**: for every such reachable state `F` with `lambda(F)<k` and every legal pivot `v`, if `G=T_v(F)` is nonterminal, then
   `lambda(G) <= lambda(F)+1`.
3. **No early acceptance**: every state `F` with `lambda(F)<k` reachable from `F0` by fewer than `k` layers is nonterminal and obeys
   `CLV(F) >= CLV(F0)`.
4. **Certificate locality**: predicates witnessing `lambda(F)=i`, the one-stage unlock bound, and no-early-acceptance are checkable without a SAT oracle, truth labels, advice, or exhaustive enumeration of all pivot sequences.

Then

`d(F0) >= k`.

### Proof

Consider any ordered legal pivot sequence of length `t<k`.
By Initial lock and repeated application of the One-stage unlock bound,

`lambda(T_sigma(F0)) <= t < k`.

Therefore No early acceptance applies to the final state: it is nonterminal and its CLV is not strictly below `CLV(F0)`. Hence the sequence is not accepted. Since the sequence was arbitrary, no sequence of length `<k` is accepted, so `d(F0)>=k`. QED.

## Why this matters

This converts a potentially exponential lower-bound obligation

`FOR ALL sigma with |sigma|<k: sigma is not accepted`

into a structural invariant proof. A genuine serial-amplification family may therefore be proved by constructing `F_k` together with a polynomial-size lock-rank certificate, rather than enumerating `V^1+...+V^(k-1)` sequences.

## Family corollary

If for every `k` there is a canonical 3-CNF source `I_k` of size `poly(k)` whose frozen pre-macro route reaches residual `F_k`, and `F_k` admits the above lock-rank invariant with parameter `k`, then

`d(F_k) >= k`.

Thus the universal **fixed-constant-K** coverage route for the frozen explicit-depth grammar is false.

This does **not** by itself prove:

- superpolynomial complexity,
- failure of every compressed polynomial discovery representation,
- `SAT notin P`,
- `P != NP`.

R47U Route C remains open: an unbounded raw depth can still coexist with a polynomial compressed representation/discovery theorem.

## Construction obligations for a real CNF family

A proposed `F_k` must provide all of:

- polynomial source size and canonical 3-CNF encoding;
- canonical reachability to the claimed residual;
- a machine-checkable definition of `lambda` from formula structure;
- proof that **every** legal pivot advances the lock rank by at most one;
- proof that alternate pivot orders cannot bypass locked stages;
- proof that R33/affine/RUP/normalization closure cannot unlock multiple stages at once;
- proof that terminal/strict-CLV descent cannot occur before the final required stage;
- polynomial verification of all family certificates.

The current R47K/R47L pair `(11,20)` is evidence that a one-step unlock relation can exist, but it is not yet a scalable serial lock construction.

## Dual structural-collapse target

The same language exposes the opposite theorem route. If every reachable residual has a structurally defined unlocking dependency system whose longest necessary causal chain is bounded by one absolute constant `K`, and a certified sequence following that chain can be discovered in polynomial time, then `d(F)<=K` universally for the frozen grammar.

Therefore the next symbolic question is not "try depth 3". It is:

> Can reachable residual CNFs realize arbitrarily long bypass-resistant unlock chains, or does the frozen reduction/normalization stack force their causal diameter to collapse to a universal constant?

## Firewalls

`UNBOUNDED_DEPTH_FAMILY_EXISTS = NOT_PROVED`

`UNIVERSAL_CONSTANT_K_EXISTS = NOT_PROVED`

`O4_UNIVERSAL_COVERAGE = OPEN`

`SAT_IN_P = NOT_PROVED`

`P_EQ_NP = NOT_PROVED`

`P_NE_NP = NOT_PROVED`

`P_VS_NP = OPEN`

`TRUMP_finished = false`
