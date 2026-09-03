# JANUS TRUMP R44BF — private forced auxiliaries conserve maximum deficiency

For every clause `C_i` of a CNF `F`, introduce a private fresh variable `y_i` and replace `C_i` by

`(C_i ∨ y_i) ∧ (¬y_i)`.

Call the resulting CNF `T(F)`. The transformation is logically exact after eliminating the private variables because each unit clause forces `y_i=0`.

We prove

`boxed(delta*(T(F)) = delta*(F))`.

Take an arbitrary selected sub-clause-set `Q⊆T(F)`. Classify each original clause index `i` according to which members of its transformed pair occur in `Q`:

- `B`: both `(C_i∨y_i)` and `(¬y_i)`;
- `P`: padded clause only;
- `U`: unit clause only;
- neither.

Then

`|Q| = 2|B| + |P| + |U|`.

Because all `y_i` are private, the selected private-variable count is

`|B|+|P|+|U|`.

The selected original variables are exactly those occurring in clauses indexed by `B∪P`. Hence

`delta(Q)`
`= 2|B|+|P|+|U| - (|B|+|P|+|U|) - |Var(B∪P)|`
`= |B| - |Var(B∪P)|`
`<= |B| - |Var(B)|`
`<= delta*(F)`.

Thus `delta*(T(F))<=delta*(F)`.

For the reverse inequality, choose an original sub-clause-set `B0⊆F` attaining `delta*(F)`. In `T(F)`, select both transformed clauses for each index in `B0`. The selected subformula has exactly `2|B0|` clauses and `|Var(B0)|+|B0|` variables, so its deficiency is

`2|B0|-(|Var(B0)|+|B0|)=|B0|-|Var(B0)|=delta*(F)`.

Therefore equality holds.

## R44BE consequence

The disjoint-copy selector merge from R44BE has maximum deficiency `a+b-1`. Applying the private forced-literal padding above to every selector-guarded clause leaves maximum deficiency exactly `a+b-1`. Therefore the obvious attempt to compensate branch deficiency by donating one private forced variable per clause does not help.

This is not a theorem against every auxiliary extension. Shared auxiliaries or stronger nonlocal gadgets are outside scope and require independent analysis.

`FRESH_VARIABLE_COUNT != FREE_MAXDEF_CREDIT`.

`TRUMP_finished=false`.

`SAT_IN_P=NOT_PROVED`.

`P_VS_NP=OPEN`.
