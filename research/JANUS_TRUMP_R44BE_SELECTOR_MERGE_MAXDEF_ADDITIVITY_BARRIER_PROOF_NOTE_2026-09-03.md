# JANUS TRUMP R44BE — selector merge maximum-deficiency additivity barrier

R44BD requires an exact OR-merge that preserves branchwise maximum-deficiency descent. R44BE fixes one natural operator class and refutes it exactly.

## 1. Fixed operator

Let `A` and `B` be CNF formulas on disjoint variable sets and let `s` be fresh. Define

`Sel(A,B;s) = { {s} ∪ C : C∈A } ∪ { {¬s} ∪ D : D∈B }`.

This has exact OR semantics:

`SAT(Sel(A,B;s)) iff SAT(A) or SAT(B)`.

Indeed, `s=0` activates `A` and satisfies the guarded `B` side; `s=1` does the converse.

## 2. Exact maximum-deficiency formula

Put

`a=delta*(A)>=1`, `b=delta*(B)>=1`.

Any subformula `H` of `Sel` is determined by subformulas `A'⊆A`, `B'⊆B`.

If `A'` is nonempty and `B'` empty, the fresh selector occurs in `H`, so

`delta(H)=|A'|-(|var(A')|+1)=delta(A')-1<=a-1`.

The symmetric one-sided bound is `<=b-1`.

If both sides are nonempty, the branch variable sets are disjoint and the only shared variable is `s`. Hence

`delta(H)=|A'|+|B'|-(|var(A')|+|var(B')|+1)`

`=delta(A')+delta(B')-1`

`<=a+b-1`.

Choose nonempty witnesses `A*`, `B*` attaining `delta*(A)=a` and `delta*(B)=b`. Their guarded union attains `a+b-1`. Since `a,b>=1`, this value dominates the one-sided cases and the empty subformula.

Therefore

`delta*(Sel(A,B;s)) = a+b-1`.

So the selector is a succinct exact OR representation, but it **adds the two branch maximum-deficiency debts**.

## 3. Infinite reachable critical family

Define the rank-two base

`C2(x,y) = {(x∨y),(x∨¬y),(¬x∨y),(¬x∨¬y)}`.

It is minimally unsatisfiable, has two variables and four clauses, and `delta*(C2)=2`. Assigning either variable either truth value leaves the contradictory unit pair on the other variable, which has maximum deficiency 1. Thus `C2` is `delta*`-critical of rank 2.

Let `F_2=C2`. For every `r>=2`, define recursively

`F_{r+1}=Sel(F_r,C2;s_r)`

using a fresh selector and a fresh variable-disjoint copy of `C2`.

By the additivity theorem,

`delta*(F_{r+1})=delta*(F_r)+2-1=r+1`.

Criticality follows inductively:

- assigning the top selector leaves rank `r` or rank `2`, both at most `r=(r+1)-1`;
- assigning a variable in the `F_r` side lowers that side to rank at most `r-1`, after which guarded composition with `C2` has rank at most `(r-1)+2-1=r`;
- assigning a variable in the `C2` side lowers that side to rank `1`, after which the guarded composition has rank at most `r+1-1=r`.

Hence every `F_r` is `delta*`-critical.

## 4. Direct failure of R44BD M2

At the top selector of critical parent `F_{r+1}`, let

`G0=F_r`, `G1=C2`.

The parent rank is

`k=r+1`.

Both children are nonterminal and satisfy

`delta*(G0)=r<=k-1`,

`delta*(G1)=2<=k-1`.

Thus this is an actual R44BD merge situation.

Applying the fixed selector-guard merge to these children gives

`delta*(Sel(G0,G1)) = r+2-1 = r+1 = k`,

not `<=k-1`.

Therefore the fixed class

`FRESH_SELECTOR_DISJOINT_BRANCH_GUARD_MERGE`

cannot satisfy R44BD M2 universally.

## Scope

This theorem does not refute all conceivable OR-merges. In particular it does not rule out a selector followed by a genuinely new exact rank-reducing normalization, a non-CNF merge language, or an operator exploiting special sibling relations. Those require separate proofs.

The exact conclusion is only:

`EXACT_SELECTOR_OR != MAXDEF_DESCENT_PRESERVING_OR`.

Status remains:

`TRUMP_finished=false`

`SAT_IN_P=NOT_PROVED`

`P_VS_NP=OPEN`.
