# R5 Universal Solver Integrated Anti-Loop Checkpoint v1.1

Date: 2026-10-10

Status:
INTEGRATED_SUCCESSOR_FRONTIER__E123_REPLAYED__NO_UNIVERSAL_POLYNOMIAL_SOLVER_YET

P_VS_NP = OPEN.

## 1. Goal

The only final goal on this line remains a deterministic polynomial-time

    SolveLinearCubicXSAT(F)

for every positive square+cubic+linear Exact-One instance, returning either a
SAT witness or UNSAT with proved soundness, completeness and total polynomial
runtime.

Parameterized/FPT terminals, finite controls, bounded-width sectors,
representation-only results and randomized reductions remain useful routers but
are not the final theorem.

## 2. Repository authority and synchronization

Canonical default-branch authority at the start of this successor cycle:

    main = 18c2a9a5dca8bf57d422a1397758027dd9a2c0ed.

PR #515 branch:

    research/parity-isolation-trade-checkpoint-20261009.

The branch had been based on

    e7d6790d533f9acd3c4fe7f2439542dfbfa3361c

while main had one later non-mathematical Physarius-registry commit.

The exact current main registry blob was copied into the branch and main was
merged without rewriting the 37 scientific commits:

    registry sync commit
      17366b3f773db5880b036917353f0404fd929df7

    merge-main commit
      7c1bce0cf8f8854df864495fc7247b7b584dea62.

After synchronization GitHub comparison reported:

    behind main = 0
    merge base  = 18c2a9a5dca8bf57d422a1397758027dd9a2c0ed.

Thus all results below are successor work on top of the current main authority,
not an obsolete fork.

## 3. Unified executable replay

The branch extends

    .github/workflows/r5-frontier-verification.yml

to run on pull requests and replay both:

1. the canonical main chain
   E17, E53, E61 through E119; and
2. the executable PR #515 successor checks.

Workflow-extension commits:

    c611592438c08a6d298e07af8039c401d2945875
      add PR515 successor checks;

    12fd46b619065df1363a7ce3ec37eb91ae364acd
      add E122;

    db98961836958a1f2fbe667c6039e85736125e92
      add E123.

Integrated replay evidence:

    run 38010903142
      SUCCESS
      canonical E17/E53/E61-E119 + successor checks through E121;

    run 38011153694
      SUCCESS
      same integrated chain + E122;

    run 38011541158
      SUCCESS
      final integrated chain + E123.

The final run completed every step successfully, including:

    E118 universal hardness replay,
    E119 perfect-conflict terminal,
    deterministic canonical-twist matroid-intersection gluing,
    q8 delta-junction firewall,
    one-check boundary / pin-XOR frontier,
    SAT-admissible one-check redundancy,
    fixed-point affine-closure firewall,
    E79 characteristic-2/3 holographic firewall,
    E120 corrected row-aligned control,
    cube-root/rainbow-Z3 SAT terminal,
    E121,
    E122,
    E123,
    parity trade smooth-count replay,
    fixed-M trade-span replay,
    Hall-tight DM trade replay.

The same scientific head also passed

    Validate JANUS registry
      run 38011541147
      SUCCESS.

Therefore E120-E123 and the new successor terminals are no longer isolated
notes: they have been replayed in one CI run together with the canonical
E61-E119 chain.

## 4. Stable exact problem formulations

For every square+cubic carrier A,

    A x = 1, x in {0,1}^n

is equivalent under y=3x-1 to

    y in ker_Q(A) intersect {-1,2}^n.

The binary endpoint formulation remains:

    SAT
      iff
    max_{k in ker_F2(A)} |k| = 2n/3.

The full target class is NP-complete by the E118 same-class hardness bridge.
Therefore a deterministic polynomial solver for all instances would imply

    P = NP.

No such solver is currently established.

## 5. SAT-admissible arithmetic and one-check boundary theorem

Every satisfying assignment selects n/3 variables, so

    SAT => 3 divides n.

Assume 3|n and delete any one check c.

If s is the selected boundary weight on the three deleted incidences, counting
incidences in the other n-1 checks gives

    n-1 = 3|Y| - s.

Thus s=1.

Consequences:

* every local satisfying extension of the n-1-check module already satisfies
  the deleted check;
* its exact three-port relation is either empty or a subset of the three
  singleton states;
* every nonempty such relation is a rank-1 matroid;
* its boundary relation is nonempty iff the original instance is SAT.

Hence static decomposition EXISTENCE on the SAT-admissible layer is not the
universal blocker.

The exact algorithmic object is

    SUPPORT_c
      = { incident port e : some global solution selects e }.

Computing this exact three-bit mask in polynomial time is already sufficient,
via self-reduction, for the desired universal solver.

## 6. Static delta lane: randomness removed, universality not obtained

E83 canonical variable-side twisting converts any exact delta boundary module
to an ordinary matroid basis family.

For a static represented-delta partition, equality of the two copies of each
cut incidence becomes exactly-one selection in a partition-matroid block.

Therefore global consistency is ordinary matroid intersection between:

    direct sum of the twisted module matroids

and

    one partition matroid on duplicated cut incidences.

This is deterministic polynomial time once the represented static modules are
constructible.

Thus randomized E78 delta-sum representation and structured Pfaffian PIT are
not the preferred blocker on this static lane.

However q8 and the later recursive-delta firewalls still show that arbitrary
raw interfaces do not remain delta under unrestricted bottom-up composition.
Moreover q8 itself is outside the SAT-admissible 3|n layer, so it is a
representation firewall rather than the final solver obstruction.

## 7. Pin / propagate / affine closure

For one candidate port of c:

1. pin the chosen variable to 1 and the other two to 0;
2. unit-propagate Exact-One constraints;
3. convert every two-unknown residual clause to x_u xor x_v = 1;
4. contract every XOR component;
5. substitute affine literals;
6. exactly simplify every repeated-component ternary constraint;
7. iterate to fixed point.

At fixed point every surviving ternary constraint uses three distinct quotient
bits.

This is an exact polynomial local reduction.

But the quotient is not forced into a known easy low-determinant class. A
frozen q=30 SAT control has minors of determinant 2 and -5 after complete
closure. Therefore neither universal TU nor universal bimodularity follows.

A universal constant-factor shrink after one pin is also not established.

## 8. Matchgate / holographic and compatibility anti-loops

The following shortcuts are closed:

* local support-preserving Pfaffian/matchgate compilation through the primitive
  Equality_3 atom;
* one universal invertible 2x2 holographic basis in characteristics !=2,3
  by E79;
* the remaining characteristic-2 and characteristic-3 cases by complete
  successor replay;
* chordality/perfectness of the fixed-M trade compatibility graph;
* perfectness restored merely by restricting to zero-circulation minimum-face
  trades.

Thus no universal solver should return to these routes without a genuinely new
global representation theorem.

## 9. Cube-root / rainbow-Z3 positive terminal

If ker(A) contains a full-support vector z with

    z_j in lambda {1, omega, omega^2}

for one common nonzero scalar lambda and primitive cube root omega, then every
three-entry row must contain the three distinct phases.

Each phase class is therefore an Exact-One witness.

Hence

    COMMON-SCALE CUBE-ROOT KERNEL VECTOR => SAT

is a proved global terminal that requires no commuting P,Q hypothesis.

The universal difficulty is construction/existence, not witness recovery.

## 10. E120: row-aligned three-port shortcut refuted, then narrowed

E120 gives a q=15 UNSAT instance whose rational kernel projection onto every
SOURCE ROW is the full row-sum-zero plane, so every row locally admits all
three Exact-One corners.

But anti-loop replay found:

* rational nullity only two; and
* arbitrary-coordinate KLOC3 already catches the carrier on coordinates
  {0,1,11}.

Therefore E120 is retained only as a negative control against row-aligned local
three-port reasoning.

It is not a post-router hard core.

## 11. E121: KLOC3 cleanliness alone is insufficient

E121 is a connected q=36 square/cubic/linear UNSAT cyclic 3-lift with:

    3|n,
    d_Q=3,
    every KLOC1/KLOC2/KLOC3 coordinate subset clean.

But it has 57 E18 projectively proportional coordinate pairs, all exact
equalities, so E18 legitimately quotients the lift-level camouflage.

Therefore

    KLOC3 clean => SAT

is false.

## 12. E122: post-E18 + KLOC3 cleanliness still does not imply SAT

E122 modifies the q36 cyclic lift and proves:

    connected square/cubic/linear,
    3|n,
    d_Q=3,
    zero E18 proportional coordinate-row pairs,
    all KLOC1/KLOC2/KLOC3 coordinate subsets clean,
    Exact-One UNSAT.

Its GF(2) kernel weights are

    [0,12,20,20,20,20,20,20]

with

    20 < 24 = 2n/3.

Thus

    post-E18 clean + KLOC3 clean => SAT

is false.

But d_Q=3, so the existing O(2^d poly(n)) small-nullity terminal solves E122.
It is a structural counterexample, not the desired asymptotic hard family.

## 13. E123: repository-wide anti-loop recovers a stronger old carrier

A full repository audit showed that the old E64 Tutte-12 / GH(2,2) q63 UNSAT
carrier was already a much stronger candidate. The later E18/KLOC filters had
simply never been cross-applied to it.

E123 replays the frozen E64 carrier and proves:

    q=63,
    connected square/cubic/linear,
    girth 12,
    3|63,
    rank_Q=49,
    d_Q=14,
    Exact-One UNSAT,
    zero rational-kernel coordinate rows,
    zero E18 projectively proportional pairs,
    every KLOC1/KLOC2/KLOC3 subset alphabet-compatible.

Among all

    C(63,3)=39711

coordinate triples, exactly 63 projected triples have rank two instead of
three; all 63 still intersect {-1,2}^3.

E123 therefore closes the finite EXISTENCE question:

    strong post-E18 + KLOC3-clean UNSAT instances exist.

This carrier predates E122 in main and demonstrates why cross-frontier
anti-loop auditing is mandatory.

## 14. What E123 does not establish

E123 is one finite q=63 carrier.

Although d_Q=14 is nontrivial, one finite point cannot prove

    d_eff = omega(log n)

or defeat every admitted parameterized router asymptotically.

Thus the benchmark target is no longer existence of a finite post-E18/KLOC3
counterexample.

The remaining benchmark target is:

    SCALABLE_POST_ROUTER_UNSAT

requiring a scalable family with:

* connected square/cubic/linear structure;
* 3|n;
* no E18 zero/proportional collapse after exact quotienting;
* KLOC3-cleanliness;
* no cube-root/rainbow-Z3 SAT terminal;
* effective nullity beyond O(log n), or another proved escape from the
  small-nullity terminal;
* no admitted low normal-span rank / component / branchwidth / small-separator
  terminal;
* exact UNSAT evidence.

A finite q63 fixture is a mandatory negative control, not an asymptotic lower
bound.

## 15. Relation to older general-SAT firewalls

The separate general-SAT universal-closure branches already show that naive
explicit separator-state / factor-table contraction can hide exponential
continuation relations, and that polynomial unions of affine subspaces are not
a universal grammar.

Therefore any Exact-One successor must remain genuinely symbolic.

No proposed support-construction theorem may obtain polynomiality by silently
materializing exponentially many boundary states.

## 16. Current single algorithmic theorem target

The strongest active theorem target remains:

    GLOBAL SYMBOLIC SUPPORT CONSTRUCTION THEOREM

Input:
    square+cubic+linear Exact-One F with 3|n
    and one check c.

Output in deterministic polynomial time:
    exact three-bit SUPPORT_c.

Allowed internal reductions include:

    E18 projective closure,
    fixed-point affine/XOR closure,
    all admitted R5 polynomial terminals,
    global symbolic invariants.

Forbidden hidden costs include:

    explicit exponential continuation tables,
    unrestricted Boolean branching,
    unproved constant-factor shrink,
    bounded-width assumptions without a universal router,
    treating finite benchmark survival as asymptotic evidence.

If SUPPORT_c is polynomially constructible for every input, repeated support
queries reconstruct a full witness, and an empty mask certifies UNSAT.

## 17. Current claim boundary

MAIN_AUTHORITY_BASE
  = 18c2a9a5dca8bf57d422a1397758027dd9a2c0ed.

PR515_MAIN_SYNCHRONIZED
  = YES.

FINAL_INTEGRATED_SUCCESSOR_REPLAY
  = run 38011541158 / SUCCESS.

FINAL_REGISTRY_VALIDATION
  = run 38011541147 / SUCCESS.

ONE_CHECK_BOUNDARY_RANK1_MATROID
  = PROVED.

STATIC_REPRESENTED_DELTA_GLUING_RANDOMNESS
  = REMOVED.

FIXED_POINT_AFFINE_CLOSURE
  = PROVED LOCAL REDUCTION.

UNIFORM_HOLOGRAPHIC_BASIS
  = REFUTED IN ALL CHARACTERISTICS.

CUBE_ROOT_RAINBOW_Z3_TERMINAL
  = PROVED.

E120_ROW_ALIGNED_RELAXATION
  = REFUTED / NARROWED.

E121_KLOC3_ONLY_SAT_IMPLICATION
  = REFUTED.

E122_POST_E18_PLUS_KLOC3_SAT_IMPLICATION
  = REFUTED.

E123_STRONG_FINITE_POST_ROUTER_UNSAT
  = PROVED AND INTEGRATED-REPLAYED.

SCALABLE_POST_ROUTER_UNSAT_FAMILY
  = OPEN.

GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION
  = OPEN.

UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER
  = NOT_CONSTRUCTED.

P_VS_NP
  = OPEN.
