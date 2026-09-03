# JANUS TRUMP R44AR — Quantifier hiding is not terminal computation

Let `F(x_1,...,x_n)` be a 3-CNF. Define a sequence of exact states

`S_i := exists x_1 ... exists x_i . F`.

Represent each state by retaining the original matrix `F` plus the list of variables moved to the existential prefix.

For every `i`, `S_i` is satisfiable iff `F` is satisfiable. Updating `S_i -> S_{i+1}` is polynomial and the representation remains `O(|F|+n)`. The rank

`rho(S_i)=n-i`

strictly decreases by one and has polynomial height.

However, after `n` steps the terminal state is

`S_n = exists x_1 ... exists x_n . F`.

This is a closed Boolean formula whose truth is exactly the original SAT question. Nothing about prefix construction evaluates it. Thus the unresolved computation has only been moved from free-variable syntax into the terminal evaluator.

This candidate deliberately demonstrates why the Legend ledger needs polynomial terminal recognition/replay in addition to exactness, polynomial state, and strict rank descent.

Seals:

- `QUANTIFIED_AWAY_SYNTACTICALLY != COMPUTATION_DISCHARGED`
- `FREE_VARIABLE_COUNT != UNRESOLVED_COMPLEXITY`
- `STRICT_SYNTACTIC_DESCENT != STRICT_COMPUTATIONAL_DESCENT`
- `SMALL_EXACT_STATE != EASY_TERMINAL_EVALUATION`
- `E6_CANNOT_BE_HIDDEN_IN_THE_TERMINAL_EVALUATOR`

Scientific status: `TRUMP_finished=false`; `SAT_IN_P=NOT_PROVED`; `P_VS_NP=OPEN`.
