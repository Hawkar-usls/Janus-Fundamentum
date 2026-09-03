# JANUS TRUMP R44BI — shared unit-disabled hubs conserve maximum deficiency

R44BF covered private forced auxiliaries. R44BI allows the same fresh auxiliary to be shared across arbitrarily many clauses.

Let `F={C_i}` be a CNF on original variables `X`. Introduce a fresh set `Y`. For each clause choose any set of hub literals `Y_i`, with each auxiliary used in one consistent polarity across padded clauses, and replace

`C_i` by `P_i = C_i ∪ Y_i`.

For each fresh auxiliary `y` that occurs, add one unit clause forcing `y` to the value that makes its padded literal false.

The forcing units make all padded literals false, so the transformed CNF is logically equivalent to `F` after forgetting the fixed auxiliaries.

## Maximum-deficiency theorem

Take any selected transformed subformula `Q`.

Let:
- `A` = selected padded original clauses;
- `U` = fresh variables whose forcing unit is selected;
- `Y(A)` = fresh variables appearing in the selected padded clauses.

Then the selected clause count is `|A|+|U|`, and its variables are the disjoint union of original variables `Var_F(A)` and fresh variables `Y(A)∪U`. Hence

`delta(Q)=|A|+|U|-|Var_F(A)|-|Y(A)∪U|`

`=delta_F(A)+|U|-|Y(A)∪U|`

`<=delta_F(A)`

`<=delta*(F)`.

Thus `delta*(T_hub(F))<=delta*(F)`.

For equality, choose an original sub-clause-set `A0` attaining `delta*(F)`. Select its padded copies and select exactly the forcing units for every hub in `Y(A0)`. Then `U=Y(A0)`, so the fresh-variable and unit-clause counts cancel:

`delta(Q)=delta_F(A0)=delta*(F)`.

Therefore

`boxed(delta*(T_hub(F))=delta*(F))`.

## R44BD consequence

Arbitrary nonlocal sharing of a fresh hub among many clauses does not by itself lower maximum deficiency if exactness is enforced only by fixing that hub to its disabling value. The private padding theorem R44BF is the one-clause-per-hub special case.

The barrier does **not** cover genuinely functional shared auxiliaries whose values depend on original variables through non-unit constraints. Those remain a different operator class and require a separate theorem.

`SHARED_HUB != FREE_MAXDEF_CREDIT_WHEN_UNIT_DISABLED`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
