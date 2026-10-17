# R5 — Constructive Max-Plus E118 Phase Contraction: Exact Solver and Missing Width Theorem

Date: 2026-10-11; research branch PR #515.

**Scientific status:** A mathematically exact, sound-and-complete
deterministic elimination solver WITH witness reconstruction now has
an executable implementation. Its worst-case bound is
`2^w poly(n)` for induced width `w`; NO universal polynomial
upper bound on `w` is proved. Thus the user-requested
`SolveLinearCubicXSAT` with worst-case `n^{O(1)}` is
**NOT CONSTRUCTED**. `P_VS_NP=OPEN`.

This attack avoids evaluating the entire cyclotomic phase;
it computes exactly the maximum attainable exponent of its
NONNEGATIVE formal weight polynomial, and shows that the
top exponent test is equivalent to Exact-One SAT.

## 1. From the E118 exact local phase to a MAX-PLUS sum

As previously proved in the Hall-matched E118 port normal form,
each 3-regular cubic source with s variable/check pairs admits a
polynomially constructible perfect matching of clauses to owners v.

For each owner v let {a,b} be the two non-owner variables in
the matched clause, and put
    p_v = 1-x_v,
    q_v = p_a XOR p_b.

The exact local phase matrix, with alpha a formal square root
of the half-weight variable z, is

            q=0                 q=1
    p=0     1+alpha^6           2 alpha^5
    p=1     alpha^4+alpha^6     2 alpha^7.

All coefficients are NONNEGATIVE INTEGERS. Hence the highest
degree in a product equals the sum of the highest degrees and
the highest degree in the sum equals the maximum of those degrees.
This is *exact tropicalization* (MAX-PLUS), without cancellation.

The local maximal contribution is

    m(p,q) = 6 - q + 2 p q.

For a source x in {0,1}^s define
    E(x) = sum_v m(p_v,q_v).

The top target-kernel degree is exactly
    max_{x in {0,1}^s} E(x),
no approximation and no branch on the E118 internal flip variables.

## 2. A global clause-count identity independent of Hall matching

Introduce Ising spins sigma_v=2x_v-1=(-1)^p_v.
Then q_v=(1-sigma_a sigma_b)/2 and 2p_v-1=-sigma_v.
The above contribution becomes

    m(p_v,q_v)
     = 6 - (sigma_v/2)
         + (sigma_v sigma_a sigma_b)/2.

Sum over ALL matched source clauses. Every source variable
appears as an owner EXACTLY ONCE. Let t_j(x) denote the
number of source clauses with exactly j selected x-variables.

Because `sigma_v sigma_a sigma_b` is +1 when clause
occupancy is odd and -1 when even, and because
`sum_v sigma_v = 2|x|-s`, we get

    E(x) = 7s - (t_0+t_2) - |x|.

This expression is INDEPENDENT of the chosen Hall matching:
all matching choices give the same highest attainable
global E118 kernel weight for any fixed source assignment x.

By cubicity of the SOURCE,
    3 |x| = t_1 + 2 t_2 + 3 t_3,
and by the number of source clauses,
    s = t_0 + t_1 + t_2 + t_3.

Assume 3|s, since otherwise the source and its E118
10s-variable target cannot be Exact-One SAT by counting.
Elementary substitution gives

    20s/3 - E(x)
      = (2/3)*(t_0 + 2*t_2 + t_3).          (1)

The nonnegative integer

    B(x)=t_0+2*t_2+t_3

is automatically divisible by THREE (a cubicity congruence),
and the exact target weight gap is 2 B(x)/3.

So for ANY 3-regular cubic source:

    MAX_TARGET_KERNEL_WEIGHT
      = 20s/3 - 2*min_x B(x)/3.

Moreover:

    B(x)=0
     iff t_0=t_2=t_3=0
     iff EVERY source clause has exactly one selected variable
     iff source SAT.

If the source is UNSAT, the minimum B is a positive
multiple of 3, and the highest possible kernel weight falls
at least TWO below the genuine Exact-One top shell.
The associated target remains UNSAT. This is an ALL-SOURCE
exact max-degree identity, not a new polynomial algorithm.

For n=9 cyclic source instances:
    offsets(1,2): min B=0, max kernel weight=60, SAT;
    offsets(1,6): min B=3, max kernel weight=58, UNSAT.
This agrees with the frozen E118 full coefficient histograms.

**Anti-duplicate:** E65 proves quantization of defects for
all square cubic parity solutions. The present identity is
its E118-gadget/MAX-PLUS source translation via Hall port
normal form, not a discovery that exact-one defects are
quantized or that the source class is NP-hard.

## 3. A constructive exact min-sum elimination with witness

Define the three-bit local violation cost

      phi(number of ones) = (1,0,2,1)
      for #ones=0,1,2,3.

Then B(x) is simply sum of phi over the source clauses.
For any square/cubic/linear incidence A with 3|n
(and, in fact, any three-uniform source), minimizing this
nonnegative sum solves Exact-One SAT EXACTLY:

    min B=0 -> SAT, return a minimizer x;
    min B>0 -> UNSAT.

We supply a concrete deterministic min-sum variable
eliminator:

1. Initialize factor F_c on every 3-variable source
   clause c with integer values phi(#ones).
2. Compute a deterministic min-fill order of the primal
   3-hyperedge graph.
3. For variable v gather all current factors containing v,
   form their scope union S, and compute for every
   assignment to S-{v} the exact min of the two v-states.
   Store an argmin backpointer.
4. Continue until all variables are eliminated.
5. Sum final scalar costs, reverse all backpointers,
   reconstruct x; independently re-evaluate B(x).
6. If minimum=0 independently verify Ax=1 with an actual
   binary witness and return SAT; otherwise return UNSAT.

This uses no SAT/UNSAT heuristic classification.
Both soundness and completeness hold for **EVERY input**.

Let w be the observed induced width of the chosen
elimination order (largest number of non-eliminated
variables in a union scope at an elimination step).
Then each intermediate factor has at most 2^w entries,
and one step considers at most 2^(w+1) valuations.

With n factors and polynomial-order elimination overhead,

    time = O(2^(w+1) poly(n)) bit operations,
    memory = O(n 2^w) polylog(n) bits.

Integer values are between zero and 2n, so arithmetic
has O(log n) bits; no hidden huge precision.
Backpointer reconstruction costs O(nw).

The program has an optional `max_width` *resource guard*,
and if the width exceeds it, raises an exception;
it NEVER guesses UNSAT when an exact computation is
unavailable. With no guard, the procedure is complete
but can be exponential.

**Critical scientific ceiling:** neither min-fill nor the
2-factor owner permutation has a proved w=O(log n)
or a proved globally polynomial intermediate-width
bound on all NP-complete 3-uniform cubic sources.
Consequently this is a genuine implemented EXACT
solver, but NOT the requested universal POLYNOMIAL solver.

### Exact SCL-width obstruction to an all-input polynomial factor-table bound

A prior independent Fundamentum theorem, audited against the
2025 Kettani constant-treewidth claim, gives the explicit family
of legal square+cubic+linear SAT carriers for every L divisible
by 3, L>=9:

    x_(i,j) + x_(i+1,j) + x_(i,j+1) = 1
    on the L-by-L toroidal grid.

Every such formula has n=L^2 variables/clauses and its primal
conflict graph contains the ordinary L-by-L grid. The
cross-bramble/Helly argument gives

    treewidth(primal) >= L-1 = sqrt(n)-1.

The width of ANY elimination order using explicit dense
binary factors on that graph is at least its treewidth;
therefore the maximum factor-table scope has at least
sqrt(n)-1 other variables and requires at least

    2^(sqrt(n)-1)

entries on those instances. This rules out deriving an
n^O(1) worst-case bound from explicit table-based min-sum
elimination, even with the best elimination ordering.
It is a LOWER BOUND ONLY FOR THIS REPRESENTATION/ALGORITHM,
not a general SAT algorithm lower bound.

The toroidal family is actually SAT with exactly three
simple periodic models, so it is an especially clear
illustration that large explicit factor tables may be
avoidable by a **different symbolic representation**.
The width theorem alone cannot prove P!=NP or that
every solver must be exponential.

The min-fill code checks its measured width on L=9,12,15
while NOT allocating any exponential factor table there.

Nothing in this note proves `P=NP`.

## 4. Why ordinary source defect minimization does not evade hardness

The E118 reduction maps an arbitrary NP-complete 3-regular
monotone cubic 1-in-3-SAT source to the legally linear,
cubic and square target.

The global optimum B(x) is exactly zero iff the source
is satisfiable. Computing this optimum, or merely testing
whether it is zero, is therefore NP-hard on the source
family. It is mathematically impossible to treat the
local tropicalization formula alone as an algorithm for
that optimum: it removes complex arithmetic, not the
NP-hard source interaction.

A proof that all eliminations and caches needed to
compute this exact minimum always require only
n^C bit operations would be a genuine P=NP proof.
That missing bound remains OPEN.

## 5. Exact executable tests

    python experiments/r5_universal_e118_tropical_defect_variable_elimination.py

Tests include:

- E61 legal SCL SAT12 and UNSAT12, returned status,
  reconstructed SAT Boolean witness and defect;
- E118 cyclic source q9 offsets (1,2) SAT and (1,6)
  UNSAT, independently certified by complete 2^9
  model list (fixture only);
- source assignment-by-assignment test of the Hall
  phase maximum formula, the global clause-count
  identity, 3-divisibility and quantified gap;
- exact min-plus factor elimination with checked
  argmin reconstruction and measured induced width;
- independent SAT witness lifting through the E118 90-variable
  reduction gadget and a full exact-one target verification;
- legal toroidal SCL SAT carriers L=9,12,15 whose
  min-fill order has induced width >=L-1, without
  running an exponential table computation.

Full R5 verifies the runnable checkpoint; do not
treat success of finite tests as proof of n^O(1).

## Gate ledger

E118_LOCAL_PHASE_MAX_PLUS_EXACT = PROVED_ALL_SOURCES.
E118_DEFECT_EQUALS_(2/3)_WEIGHTED_CLAUSE_VIOLATIONS = PROVED_ALL_SOURCES.
E118_SAT_IFF_MAX_KERNEL_WEIGHT_TOP = PREDECESSOR_AND_PROVED.
E118_UNSAT_MAX_WEIGHT_GAP_GE_TWO = PROVED_FOR_3_DIVIDES_S.
MIN_SUM_FACTOR_ELIMINATION_SOUND_COMPLETE = PROVED_ALL_INPUTS.
MIN_SUM_FACTOR_ELIMINATION_RUNTIME = O(2^w * poly(n)).
UNIFORM_WORST_CASE_W_LE_O_LOG_N = REFUTED_FOR_EXPLICIT_TABLE_ELIMINATION.
LEGAL_SCL_TOROIDAL_PRIMAL_TW_GE_SQRT_N_MINUS_ONE = PREDECESSOR_PROVED.
GLOBAL_POLYNOMIAL_TROPICAL_CONTRACTION = OPEN.
UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
