# JANUS TRUMP R44BD — maxdef descent-preserving OR-merge interface

Szeider's maximum-deficiency SAT algorithm gives a polynomial reduction to a `delta*`-critical formula `G` such that for every remaining variable `x` and both truth values `epsilon`,

`delta*(G[x=epsilon]) <= delta*(G)-1`.

Thus the rank already exists branchwise. The exponential `2^k` factor comes from preserving the SAT disjunction of both children.

Let `k=delta*(G)`, `G0=G[x=0]`, `G1=G[x=1]`.

The frozen target is one deterministic operator `M(G0,G1)` satisfying all of:

1. `SAT(M) iff SAT(G0) or SAT(G1)`;
2. `delta*(M)<=k-1`;
3. construction work polynomial in original input size with exponent independent of `k`;
4. polynomial live state and metadata;
5. polynomial witness/certificate lifting to the parent;
6. closure under the same polynomial normalization used before the next macrostep.

If such an operator exists universally, then maximum deficiency falls by at least one per merged macrostep. Since `delta*` is a nonnegative integer bounded by the number of clauses, there are at most `N` such steps. Together with polynomial per-step work/state this yields a polynomial SAT decider, hence `P=NP`.

This is why the target is not a minor lemma: it is a precise Legend witness interface.

Already-failed natural merges remain excluded:

- selector merge: exact OR but the binary choice is reified rather than discharged;
- ordinary CNF Davis-Putnam merge: exact but can rebound `delta*` (R44AS-RANK);
- auxiliary-free CNF projection: parity gives exponential CNF size;
- quantifier-prefix hiding: small syntax but SAT remains in the terminal evaluator.

Status:

`TARGET_FROZEN__NOT_PROVED`

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.
