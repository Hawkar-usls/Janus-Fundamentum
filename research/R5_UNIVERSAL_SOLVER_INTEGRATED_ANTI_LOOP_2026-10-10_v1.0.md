# R5 Universal Solver Integrated Anti-Loop Checkpoint

Date: 2026-10-10

Status:
INTEGRATED_FRONTIER__NO_UNIVERSAL_POLYNOMIAL_SOLVER_YET

P_VS_NP = OPEN.

## 1. Goal

The only promoted end goal remains a deterministic polynomial-time

    SolveLinearCubicXSAT(F)

for every positive square+cubic+linear Exact-One instance, returning either a
SAT witness or UNSAT with soundness, completeness and polynomial runtime.

Partial terminals, bounded parameters, finite controls and randomized
reductions are not the final goal.

## 2. Repository routes checked before continuing

This checkpoint explicitly cross-checks the active 2026-10-10 parity/one-check
work against older Fundamentum lines so they are not rediscovered under new
names.

### E60 permutation normal form

Every simple square cubic carrier admits

    A = I + P + Q

after a polynomial 3-edge-coloring of its bipartite incidence graph.

E60 already proves that this is a normal form for the FULL class. Alternating
P/Q cycles are not independent because the I matching couples them.

Therefore merely returning to permutation cycles is not a new universal route.

### E74/E79 matching/Pfaffian local route

Local support-preserving matchgate/projected-linear compilation is blocked by
the non-delta Equality_3 atom. E79 additionally blocks a single universal
holographic basis.

Therefore no new local Pfaffian gadget search is authorized without genuinely
global cancellation.

### E78/E83 static delta route

A new 2026-10-10 theorem strengthens this lane:

after the E83 canonical variable-side twist, every exact delta boundary module
is an ordinary matroid basis family and equality across each Tanner cut edge
becomes exactly-one across the two duplicated edge copies.

Hence any constructible static represented-delta partition is solved
DETERMINISTICALLY by ordinary matroid intersection against a partition matroid.

Randomized delta-sum construction / structured Pfaffian PIT is therefore not
the preferred blocker on the static-partition lane.

### E81 q=8 qualification

E81 remains a valid representation counterexample: q=8 has no static partition
into nonempty exact delta modules.

But SAT in the square cubic class requires

    3 | n,

since every solution selects n/3 variables.

Thus q=8 is rejected by the mandatory divisibility precheck and is not by
itself a universal-solver counterexample after that precheck.

### PR #489 adaptive symbolic-elimination firewalls

The GENERAL-SAT universal-closure branch already proves:

* explicit exact adaptive contraction trees can require
  2^(Omega(n/log n)) bond states via high-branchwidth linear-code
  continuation relations;
* polynomial unions of affine subspaces are not a universal grammar;
* ordinary exact tabular factor elimination is killed by expander/treewidth
  families;
* projection/semantic collision count is not a monotone termination measure.

Therefore the current Exact-One attack must remain a compact SYMBOLIC method.
No proposed separator DP may silently materialize exponential continuation
tables.

### Stage6B.4 deletion-qHorn exact-distance descent

Frozen branch:
    research/general-sat-universal-coverage-map-2026-09-19

Round 1:
    workflow commit c6edcd22107debeeb00bf2b690bc05a101f748a8
    run 35461153243
    conclusion SUCCESS
    13/13 midpoint queries = proof-producing UNSAT
    every lower bound verified by VeriPB and secondarily by CakePB.

Round 2:
    workflow commit cedca801b0292ccc085424a694c2aba92828f974
    run 35461823191
    conclusion SUCCESS
    again 13/13 midpoint queries = UNSAT.

Certified open brackets after Round 2 are:

    index 1 : [18,24]
    index 2 : [23,31]
    index 3 : [18,25]
    index 4 : [21,28]
    index 5 : [15,21]
    index 6 : [19,26]
    index 7 : [16,22]
    index 9 : [23,31]
    index 10: [23,31]
    index 11: [23,31]
    index 12: [23,31]
    index 13: [23,31]
    index 14: [23,31]

No exact distance was closed in these two rounds.

This is finite proof-carrying evidence of substantial qHorn deletion distance.
It is NOT an asymptotic lower bound and NOT a complexity theorem.

## 3. New one-check theorem

For n divisible by three, delete ANY one check c and retain every variable plus
the other n-1 checks.

If s is the selected boundary weight on the three incidences of c, exact
incidence counting gives

    3|Y| - s = n-1.

Since s is in {0,1,2,3} and n=0 mod 3,

    s=1.

Therefore the exact three-port boundary relation is either empty or a rank-1
matroid on the three ports.

Moreover s=1 satisfies the deleted check itself, so

    original F is SAT
    iff
    the one-check-deleted boundary relation is nonempty.

Thus static decomposition EXISTENCE on the admissible layer is trivial.

The true problem is CONSTRUCTION of its three-bit nonloop mask:

    SUPPORT_c =
      {e incident with c : a global solution selecting e exists}.

Polynomial construction of SUPPORT_c is equivalent to the desired solver up to
ordinary self-reduction.

## 4. Direct support-construction attack

The current exact reduction is:

    pin one of the three check states
      -> Exact-One unit propagation
      -> x_u xor x_v = 1 contraction
      -> Boolean simplification of repeated XOR-component occurrences
      -> repeat to fixed point.

At fixed point every surviving ternary constraint is Exact-One on THREE
DISTINCT affine quotient literals.

This repair is important: pre-fixed-point coefficients +/-2 are artifacts that
can encode further forced Boolean propagation.

## 5. Low-determinant shortcut is closed

A frozen satisfiable q=30 square/cubic/linear carrier survives full affine
closure with:

    23 unknown original variables
    11 XOR quotient variables
    15 proper signed ternary constraints.

Its signed quotient matrix has a 2x2 determinant 2 and a 4x4 determinant -5.

Therefore the post-closure quotient is not automatically:

    totally unimodular;
    bimodular;
    bounded by Delta<=2.

E33's independent TU-kernel terminal remains valid when its premise happens to
hold; affine closure simply does not force that premise.

## 6. Local constant-factor shrink is not established

Random planted stress controls show that a one-check pin can leave a quotient
whose size is a large fraction of n. In one n=180 control, even the check with
the best minimax score over its three pin branches retained a branch with 150
quotient variables.

This is OBSERVATION only, not an asymptotic counterfamily.

Combined with the PR #489 explicit-bond firewall, it is enough to reject any
claim that current evidence proves a polynomial recursion by local shrink or
small separator states.

## 7. Exact inherited quotient invariant

For each XOR component C, write every original variable as

    x_v = t_C xor p_v

and define its signed charge

    chi_C = # {v in C : p_v=0} - # {v in C : p_v=1}.

After fixed-point affine closure, let M be the signed matrix of proper ternary
quotient equations.

Every unknown original variable still participates in exactly three unresolved
clauses. Every eliminated binary clause connects opposite parities and
cancels one positive and one negative contribution.

Therefore the sum of entries in quotient column C is exactly

    sum_rows M[row,C] = 3 chi_C.

This is a genuine inherited conservation law.

It is not yet a solver: it is a linear combination of the surviving equations
and by itself supplies no new independent constraint. It is retained because a
future global representation must preserve it.

## 8. External complexity sanity check

Perfect matching is NP-complete already for important 3-uniform regular
hypergraph families, and perfect matching in linear 3-uniform hypergraphs is
also a standard NP-complete restriction.

Thus no literature-based generic hypergraph-matching shortcut was found that
would make the target easy without exploiting additional source-specific
structure.

Likewise, polynomial algorithms for bimodular integer programs do not apply
after the explicit determinant-5 quotient certificate.

## 9. Single surviving target

Do NOT return to:

    raw I+P+Q cycle DP;
    local matchgate gadgets;
    perfect/chordal trade compatibility;
    zero-circulation compatibility perfectness;
    static-delta randomized PIT;
    TU/bimodular quotient;
    explicit separator-state contraction;
    unproved constant-factor pin shrink;
    bounded deletion-qHorn as though the parameter were already small.

The active target is:

    GLOBAL SYMBOLIC SUPPORT CONSTRUCTION THEOREM

Input:
    a square+cubic+linear Exact-One carrier F with 3|n
    and one check c.

Output in polynomial time:
    the exact three-bit SUPPORT_c mask.

Allowed internal reductions include affine closure, but the algorithm must
compress the surviving signed ternary hard core symbolically without explicit
exponential continuation states and without assuming a bounded qHorn distance,
bounded treewidth, TU representation or local shrink.

If this theorem is proved, repeated support queries reconstruct a full witness;
if every support bit is absent, UNSAT is certified.

## 9A. Successor replay authority update

The branch has now been reconciled with current main and the unified
`R5 Frontier Verification` workflow has been extended through the executable
PR #515 successor checks.

On branch HEAD `db98961836958a1f2fbe667c6039e85736125e92`:

* `R5 Frontier Verification` run `38011541158` = SUCCESS;
* `Validate JANUS registry` run `38011541147` = SUCCESS.

The replay includes the canonical E17/E53/E61--E119 chain plus the branch
checkers for canonical-twist matroid gluing, q8 delta-junction recursion,
one-check support reduction, affine closure, the characteristic-2/3 E79
firewall, E120, the cube-root/rainbow-Z3 terminal, E121, the parity-trade
normal forms, and the later E122/E123 rebinding.

Therefore the branch is now a replayed scientific successor of E119 rather
than an unintegrated note stack. It remains a draft PR and is not merged into
main.

## 9B. E122/E123 benchmark correction

E122 proves the finite implication

    3|n + E18-projective-clean + KLOC3-clean => SAT

is false already at q=36.

Its carrier is connected square/cubic/linear, has no zero/proportional rational
kernel-coordinate rows, every coordinate subset of size at most three is
alphabet-compatible, and is Exact-One UNSAT. But its rational nullity is only
3, so the existing small-nullity terminal still solves it.

E123 then rebinds the older E64 Tutte-12 q=63 carrier through the later E18 and
KLOC3 filters:

    q = 63,
    rank_Q = 49,
    nullity_Q = 14,
    E18 zero/proportional rows = none,
    all KLOC1/KLOC2/KLOC3 subsets clean,
    Exact-One UNSAT.

This is the strongest current finite post-E18/KLOC3 negative control, but one
finite q=63 point does not establish superlogarithmic effective nullity
asymptotically.

Hence the benchmark target is now sharpened to

    SCALABLE_POST_ROUTER_UNSAT

requiring a family with effective nullity escaping O(log n) and avoiding every
already-admitted low-rank/component/branchwidth terminal.

The theorem target remains unchanged:

    GLOBAL SYMBOLIC SUPPORT CONSTRUCTION.

## 9C. New anti-loop for scalable lift searches

Cyclic voltage lifts admit a character decomposition: the lifted matrix
decomposes into base-size character blocks obtained by evaluating the voltage
matrix at roots of unity. This is standard voltage-lift algebra and is already
used concretely in E121/E122.

Therefore a scalable high-nullity lift family cannot be justified merely by
observing one singular twisted block at order 3. It needs a uniform algebraic
mechanism, such as a Laurent-polynomial kernel relation that forces singularity
for an unbounded set of characters, together with an independent UNSAT
certificate that survives the lift.

Conversely, phase-engineering a common-scale cube-root kernel mode is forbidden
as an UNSAT construction by the rainbow-Z3 terminal: such a mode immediately
constructs Exact-One witnesses.


## Claim boundary

ONE_CHECK_BOUNDARY_RANK1_MATROID = PROVED.
STATIC_DELTA_GLUING_RANDOMNESS = REMOVED.
AFFINE_CLOSURE = PROVED LOCAL REDUCTION.
POST_CLOSURE_TU = REFUTED.
POST_CLOSURE_BIMODULAR = REFUTED.
STAGE6B4_ROUND1_AND_ROUND2 = PROOF_CARRYING_FINITE_NEGATIVE_EVIDENCE.
GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION = OPEN.
SCALABLE_POST_ROUTER_UNSAT = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
