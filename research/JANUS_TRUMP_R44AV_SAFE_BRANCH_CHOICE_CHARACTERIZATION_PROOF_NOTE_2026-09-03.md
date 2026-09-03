# JANUS TRUMP R44AV — universal exact safe branch choice is the final frontier

Let `C(F,v)` be deterministic and polynomial-time. For every nonterminal 3CNF `F` and remaining variable `v`, suppose it returns `epsilon in {0,1}` such that

`SAT(F) iff SAT(F[v=epsilon])`.

Apply `C` repeatedly, simplifying after each assignment. Each step removes at least one variable and preserves satisfiability exactly. Hence after at most `n` steps we reach a variable-free formula whose truth value is trivial to read. Polynomial work per step times at most `n` steps gives a polynomial-time 3SAT decider. Therefore such a universal chooser implies `P=NP`.

Conversely, if `P=NP`, SAT of each cofactor can be tested in polynomial time. Choose a satisfiable cofactor whenever the parent is satisfiable; if the parent is unsatisfiable, either child is unsatisfiable and either value is safe. Thus a polynomial exact chooser exists.

So the characterization is:

`UNIVERSAL_POLYTIME_EXACT_SAFE_BRANCH_CHOICE <=> 3SAT in P <=> P=NP`.

This does not ban partial certified chooser rules. It only forbids treating partial coverage as a smaller proof of the universal property.

Firewalls:
- `SAFE_CHOICE_ON_A_CLASS != UNIVERSAL_SAFE_CHOICE`
- `HEURISTIC_BRANCHING != EXACT_BRANCHING`
- `BRANCH_SCORE != SAT_PRESERVING_CERTIFICATE`
- `P_VS_NP=OPEN`.
