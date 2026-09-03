# JANUS TRUMP R44Y — Legend characterization and proof-search split

## Theorem A — Legend is equivalent to `P = NP`

Let `LEGEND` denote the frozen `TRUMP_UNIVERSAL_PROOF_CARRYING_DECOMPOSITION_LEMMA`: there exist fixed constants `c,d` and one deterministic answer-blind constructor `D` such that every 3-CNF input of encoded size `N` is handled exactly; every charged macrostep uses at most polynomial work/state in the original `N`; a discrete rank in `{0,...,ceil(N^d)}` decreases by at least one per nonterminal macrostep; and the final result is polynomial-time replayable against the original formula.

Then

`LEGEND <=> 3SAT in P <=> P = NP`.

### `LEGEND => P = NP`

By L5 there are at most `ceil(N^d)` nonterminal macrosteps. By L3 each macrostep, including discovery, compilation, proof generation and verification, costs at most `N^c` up to one fixed polynomial exponent. L4 excludes hidden superpolynomial live state. Hence the complete deterministic run has polynomial total cost. L1 makes it total on every 3-CNF, and L2 makes every terminal answer exact. Thus `3SAT in P`. Since 3SAT is NP-complete, `P = NP`.

L6 is stronger than what is needed merely to decide 3SAT: it adds an independently replayable end-to-end result and therefore strengthens reproducibility without weakening the implication.

### `P = NP => LEGEND`

Assume `P = NP`. Then there exists a correct deterministic polynomial-time 3SAT decider `A`.

For a satisfiable formula, standard SAT self-reducibility recovers a full satisfying assignment by fixing variables one at a time and querying `A`; this uses only polynomially many polynomial-time calls.

For an unsatisfiable formula, run `A` to rejection. Because `A` is deterministic and polynomial-time, its complete computation history has polynomial length. A separately specified verifier can check, in polynomial time, that the transcript starts from the encoded input, that every adjacent configuration obeys the fixed transition relation of `A`, and that the final configuration is rejecting. Soundness of this replay relies only on the fixed mathematical correctness of `A`, which is part of the assumed `P=NP` witness; the verifier does not need to rediscover the SAT answer.

Define `D` to execute this polynomial procedure and emit a terminal result directly. Its live state, discovery/work and returned witness/transcript are polynomial. Set `Phi_F(start)=1` and `Phi_F(terminal)=0`. Therefore L1--L6 all hold.

So the Legend lemma is a characterization of the final complexity-class claim, not a presently known weaker stepping-stone.

## Theorem B — universal short UNSAT evidence already reaches `NP = coNP`

Suppose one total exact proof-carrying constructor has the following restricted property on every UNSAT 3-CNF: it terminates and emits a certificate of polynomial size that a deterministic polynomial-time verifier accepts exactly for unsatisfiable inputs.

Then `UNSAT_3CNF in NP`. Since `UNSAT_3CNF` is coNP-complete, `coNP subseteq NP`; taking complements gives `NP subseteq coNP`, hence `NP = coNP`.

This is the classical proof-complexity boundary isolated by Cook and Reckhow: a polynomially bounded propositional proof system exists iff `NP = coNP`.

Reference: Stephen A. Cook and Robert A. Reckhow, *The relative efficiency of propositional proof systems*, Journal of Symbolic Logic 44(1), 1979, DOI `10.2307/2273702`.

The crucial separation for TRUMP is therefore

`POLYNOMIAL CERTIFICATE EXISTENCE != DETERMINISTIC POLYNOMIAL CERTIFICATE DISCOVERY`.

A short proof may exist without a deterministic polynomial-time method for finding it. The proof-search/discovery cost must remain charged explicitly.

## Consequence for the six Legend obligations

The six obligations remain a useful audit decomposition, but they are not six independent mini-problems whose separate finite progress can be added until `P=NP` appears.

In particular:

- The frozen L5 rank is a sufficient discrete certificate of a polynomial macrostep bound. Conversely, once a deterministic terminating trajectory is already known to have polynomial length, an abstract `remaining steps` rank exists; however, if TRUMP wants to compute or verify that rank operationally, that work must be charged under L3. Thus the rank is not free computational power.
- L1/L2/L4/L5/L6 on the universal UNSAT side already demand a proof-size/verification phenomenon at the `NP=coNP` frontier.
- L3 is the uniform discovery requirement: existentially short evidence does not discharge it.
- L1--L6 for one fixed constructor are collectively equivalent to the original `P=NP` target.

Therefore the next admissible mathematical attack is not another representation heuristic. It is a theorem or countertheorem about a fixed proof language and its deterministic discovery complexity.

Scientific boundary: `P_VS_NP = OPEN`.
