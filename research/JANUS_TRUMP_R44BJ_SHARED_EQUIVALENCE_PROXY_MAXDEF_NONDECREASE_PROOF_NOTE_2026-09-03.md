# JANUS TRUMP R44BJ — shared equivalence proxies cannot lower maximum deficiency

Choose an original variable `x` and a fresh auxiliary `y`. Redirect any chosen subset of occurrences of `x` / `¬x` to `y` / `¬y` with the same polarity, and add

`(¬x ∨ y) ∧ (x ∨ ¬y)`.

These two clauses force `y=x`, so existentially forgetting `y` recovers exactly the original Boolean function.

Let `A` be an original sub-clause-set attaining `delta*(F)`, and let `A'` be its transformed redirected copy.

If `x` does not occur in `A`, then `A'` itself still witnesses deficiency `delta*(F)`, so maximum deficiency cannot decrease.

Assume `x` occurs in `A`.

There are three cases.

1. **Both x and y occur in A'.**  Then `A'` has one more variable than `A`, so `delta(A')=delta(A)-1`. Adding both equivalence clauses adds two clauses and no new variables, giving deficiency `delta(A)+1`.

2. **Only y occurs in A'.**  All occurrences of x in A were redirected. The variable count of `A'` equals that of `A`; the two equivalence clauses add x plus two clauses, again giving `delta(A)+1`.

3. **Only x occurs in A'.**  None of A's x-occurrences was redirected. The two equivalence clauses add y plus two clauses, again giving `delta(A)+1`.

Hence

`delta*(T_equiv(F)) >= delta*(F)`

for all F, and if some maximum-deficiency witness contains the proxied variable x, then

`delta*(T_equiv(F)) >= delta*(F)+1`.

Thus a globally shared functional **copy** variable cannot supply R44BD maximum-deficiency descent. The constraint enforcing exactness returns at least all apparent matching credit and may add debt.

This does not cover genuinely multi-input functional auxiliaries such as `y <-> (a AND b)`, `y <-> (a OR b)`, or XOR definitions. Those are the next distinct operator class.

`SHARED_FUNCTIONAL_COPY != MAXDEF_CREDIT`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
