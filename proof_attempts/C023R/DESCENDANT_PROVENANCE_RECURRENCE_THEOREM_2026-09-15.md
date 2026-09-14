# C023R P1 — exact descendant provenance recurrence theorem

Date: 2026-09-15
Authority: `HQ_SYMBOLIC_LEMMA__NO_SCIENTIFIC_PROMOTION`

Parent preregistration:

`DESCENDANT_DERIVED_CLAUSE_FINGERPRINT_PROPAGATION_PREREG_v1.0.md`

## Frozen transition facts used

At every historical Policy-0A state:

1. exhaustive pre-unit propagation simplifies the incoming CNF;
2. the resulting canonical CNF is the cache key;
3. `resolution_trace` indexes the clauses present at pass entry;
4. every recorded addition is a legal resolvent of two clauses from that fixed entry index;
5. newly added clauses are stored but are not inserted into the parent index during the same pass;
6. post-unit propagation only simplifies/removes clauses;
7. branch restriction only simplifies/removes clauses before the recursive child call;
8. canonicalization may deduplicate byte-identical clauses.

## Witness-provenance object

Because canonicalization can merge byte-identical clauses that admit different derivations, do **not** assign a unique historical provenance to a stored clause.

Instead, a provenance witness for a clause `C` is any finite binary derivation DAG/tree satisfying:

- each leaf is one original root-CNF clause;
- unary edges are restrictions/simplifications under assignments and do not count as Resolution merge layers;
- every binary internal node is one recorded legal Resolution inference;
- the root witness, after applying the assignments on its execution ancestry, yields the stored canonical clause `C`.

Define `merge_height(P)` recursively:

- root source clause: `0`;
- restriction/simplification: unchanged;
- Resolution of witnesses `P1,P2`: `1 + max(merge_height(P1), merge_height(P2))`.

If canonicalization deduplicates several equal clauses, any one valid witness may be retained for the existential bound below.

## Lemma 1 — restriction and unit propagation do not increase merge height

Let stored clause `C` have witness `P`. Restrict by one assignment.

- if the assignment satisfies `C`, the clause disappears and no descendant witness is needed;
- if the assignment falsifies one literal, delete that literal from the residual representation while retaining the same root derivation witness under the extended assignment;
- if the assignment does not occur in `C`, retain `C` and `P` unchanged.

Repeated exhaustive unit propagation is a sequence of these restrictions. Therefore every surviving clause after pre-UP or post-UP has a witness whose merge height is no larger than before propagation.

Canonical deduplication cannot invalidate the existential statement: if several surviving copies canonicalize to the same byte clause, retain any one of their witnesses.

## Lemma 2 — one local Resolution pass adds at most one merge layer

Let the pass-entry canonical CNF be `K`, and suppose every clause `C in K` has some provenance witness of merge height at most `h`.

Every recorded new resolvent `R` is produced from two clauses `C1,C2` in the fixed pass-entry index. Choose witnesses `P1,P2` with heights at most `h`. The legal recorded Resolution event itself gives a witness

`P_R = Resolve(P1,P2,pivot)`

with

`merge_height(P_R) <= h+1`.

Crucially, newly added resolvents are not re-indexed during the same pass. Therefore no recorded addition in that pass can use an `h+1` addition as a parent and create an `h+2` witness in the same search state.

Existing clauses retain height at most `h`; duplicate new clauses may retain either an older witness or the new witness. Hence every clause in the saturated pass output admits a witness of merge height at most `h+1`.

## Theorem — descendant recurrence

Let `K_d` be any cache key reached after `d` visited nonterminal local-Resolution states on one root-to-key execution ancestry, counting the root state as the first pass when applicable.

Every clause in `K_d` admits a root-CNF provenance witness of merge height at most `d`.

Proof: induction on visited local-Resolution states. Root source clauses have height zero before the first pass. Lemma 2 increases the bound by at most one at the pass; Lemma 1 shows all subsequent post-UP, branch restriction and next pre-UP steps do not increase it. Repeat. QED.

## Corollary — source-leaf count bound for one witness

A binary derivation tree of merge height `d` has at most `2^d` leaves. Therefore every descendant stored clause admits at least one derivation witness using at most `2^d` root-clause leaves (and hence at most `2^d` source vertex-factor identities).

This corollary is only an upper bound on one possible derivation witness. It is **not** a lower bound on information retained by the clause and not a bound on the number of historical contexts mapping to the same cache key.

## Red-team / limitation

The theorem does **not** prove the desired fingerprint claim:

- search depth can be linear in the lifted variable count;
- `2^d` can therefore be exponential;
- narrow clauses can have deep provenance through cancellations;
- canonical dedup can hide multiple derivations behind one byte-identical clause.

Thus

`PROVENANCE_MERGE_HEIGHT <= SEARCH_PASSES`

does not imply

`CACHE_FIBER <= 2^{o(L)}`.

## P1 verdict

`PASS_EXACT_PROVENANCE_RECURRENCE__INSUFFICIENT_ALONE_FOR_FINGERPRINT_BOUND`

## Next preregistered obligation

Proceed to `P2 — exact influence condition`: identify an explicit frozen-transition clause/key distinction caused by one collision-history bit, or construct an exact bounded-radius collision cell in which inherited resolvents fail to distinguish that bit.

No finite asymptotic run is authorized by this lemma.
