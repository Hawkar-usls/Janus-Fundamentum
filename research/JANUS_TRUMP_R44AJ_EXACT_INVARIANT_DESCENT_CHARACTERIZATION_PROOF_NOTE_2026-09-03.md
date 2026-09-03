# JANUS TRUMP R44AJ — Exact invariant descent characterization

## Frozen machine

For an input 3CNF `F` of encoded size `N`, suppose there is a deterministic transition `T` on exact decision states with:

1. polynomial charged transition cost;
2. polynomial state size;
3. exact SAT-status preservation on nonterminal transitions;
4. an integer rank `rho` bounded by a fixed polynomial `p(N)`;
5. strict decrease `rho(T(S)) <= rho(S)-1` on every nonterminal transition;
6. polynomial-time recognizable/verifiable SAT/UNSAT terminal states;
7. all work for computing/updating `T`, state and rank included in the charge.

## Forward direction

At most `p(N)` nonterminal transitions occur. Every transition costs polynomial time and manipulates only polynomial-size state. Hence the full trajectory reaches a correct terminal SAT/UNSAT verdict in polynomial total time. Thus `3SAT in P`, and NP-completeness of 3SAT gives `P=NP`.

## Reverse direction

Assume `P=NP`. Then a deterministic polynomial-time 3SAT decider `A` exists. Define one transition `T(F)` to run `A(F)` and return the corresponding terminal verdict. Give the initial state rank `1` and terminal states rank `0`. The transition cost and state size are polynomial, exactness is immediate, and strict descent occurs in one step.

Therefore the frozen universal exact invariant-descent machine exists iff `P=NP`.

## Meaning for TRUMP

Searching for such an invariant is legitimate, but it is the final problem rather than an easier surrogate. A candidate gets no theorem authority from finite successes, partial reduction power, or an abstract rank whose maintenance cost is not proved polynomial.

Seals:

- `EXACT_INVARIANT != UNIVERSAL_DESCENT`
- `RANK_EXISTS != RANK_POLYTIME_MAINTAINABLE`
- `POLY_STEP_COST + POLY_STEP_COUNT + EXACTNESS => POLY_TOTAL_DECIDER`
- `FINITE_SUCCESS != UNIVERSAL_DESCENT`
- `NO_COUNTEREXAMPLE_FOUND != PROOF`

Scientific status: `P_VS_NP=OPEN`.
