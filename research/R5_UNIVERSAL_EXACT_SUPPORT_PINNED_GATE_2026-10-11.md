# PR515 — ExactSupport(A, π): Executable Pinned Decision Gate with Honest Complexity Boundary

Date: 2026-10-11.
Repository: Hawkar-usls/Janus-Fundamentum.
Previous authority: e1e1620202cf16fc6ed24768c7e8baf161b441b8, R5 #38117654891 SUCCESS, registry #38117654881 SUCCESS.

**Canonical goal:** deterministic worst-case n^O(1)
`ExactSupport(A,pi)` for every square cubic linear (C4-free)
positive Exact-One incidence matrix, including SAT with witness
and UNSAT, and for every consistent partial Boolean assignment pi.

**Checkpoint result: runnable exact decision API + pinned self-reduction,
safe polynomial negative certificates, and bounded UNKNOWN semantics.
There is NO proven all-input polynomial bit runtime for the full
decision. P_VS_NP=OPEN.**

## I. Semantics and construction

For a Boolean assignment x, let
    F_A(x) = AND_{rows i} [sum_{j:A_ij=1} x_j = 1].

`ExactSupport(A,pi)` returns:
  SAT and a concrete x in {0,1}^n with F_A(x)=true,
      x agreeing with pi;
  UNSAT only after a fully exact negative inference
      (propagation, GF2, top-weight capacity, MOD4 exclusion)
      or an exhaustively completed exact branching proof;
  UNKNOWN if a caller-specified branch resource guard interrupts.

With NO guard, this is a TOTAL exact decision algorithm.
Its worst-case bit complexity is exponential, not polynomial.

The implementation is:
    experiments/r5_universal_exact_support_pinned_oracle_attack.py

It validates the full square+cubic+linear promise, rejects 3∤n,
normalizes pinned inputs, computes a GF2 kernel basis once,
then performs a standard complete exact-cover branch search.

### Polynomial-time exact negative filters

1. **Exact-One propagation.** If one member of a clause is 1,
   force all other members to 0. If no 1 and only one undecided
   member remains, force it to 1. More than one 1 or no possible
   1 is a sound contradiction. Each propagation assigns
   previously unknown variables at most once.

2. **Pinned affine GF2 consistency.** Every genuine model has
   x=1+k with k in K=ker_F2(A), so x pins translate to k pins
   k_j=1-x_j. GF2 elimination yields an empty affine coset
   or a particular word k0 and translation basis b_i.
   Inconsistency soundly proves UNSAT for that slice.

3. **New explicit top-weight capacity bound.** Let
       U = supp(k0) UNION supp(b_1) UNION ... UNION supp(b_r).
   Every affine pinned word k is supported within U.
   An Exact-One model requires |k|=2n/3. Therefore
       |U| < 2n/3  => pinned ExactSupport(A,pi)=FALSE.
   This is an exact all-input polynomial test (bitset OR +
   Gaussian elimination), not a sufficient SAT condition.
   The filter does NOT assert that this union bound is tight.
   In particular if K={0} it immediately detects UNSAT.

4. **Quadratic Gauss residue obstruction.** On the pinned
   affine coset, polynomial GF2 quadratic Gauss elimination
   calculates exactly the number of k with
       wt(k)/2 == n/3 (mod 2).
   If zero, there is no valid top-weight k. If positive,
   it is only an OPEN/feasible parity residue: q90 E118
   negative controls already show a false-positive. The
   algorithm *never* returns SAT based on this alone.

These filters are polynomial in n for each invocation.
They can be used only at the root, or also at any chosen
bounded recursion depth; repeated oracle calls on an
exponential branch tree do NOT become polynomial globally.

### Complete exact clause branching

After propagation, pick an unsatisfied Exact-One clause
whose remaining unfixed coordinates are at minimum 2 or 3.
For EACH free member j, branch on the unique-one assignment
    x_j=1, x_other-free=0.
The branches are disjoint and exhaust every completion
of that clause. For k free members this sets all k
previously unassigned bits. Thus a crude worst-case
recurrence is
    T(n) <= max(2*T(n-2),3*T(n-3)) + poly(n),
hence T(n)=O(3^(n/3)*poly(n)) by induction
(the 3-state case dominates the 2-state case).
A branch ends with a genuine SAT witness or a sound
contradiction; an exhausted tree proves UNSAT.

**Not a new complexity theorem:** branching on an exact-cover
clause and the O(3^(n/3)) upper bound are classical Algorithm-X
style techniques (David Eppstein, "Analyzing Algorithm X", 2008:
https://11011110.github.io/blog/2008/01/10/analyzing-algorithm-x.html).
This checkpoint's contribution is the callable pinned decision
interface, strict UNKNOWN semantics, integration of all-input
polynomial negative filters, and verified witness extraction.
Do NOT promote this known branching bound as P=NP progress.

The solver returns the FIRST verified SAT model in fixed
deterministic branch order, or UNSAT only after the full tree
has been explored. This completes the decision algorithm,
BUT DOES NOT satisfy the polynomial-time goal.

A configurable `max_nodes` guard counts decisions,
and on exhaustion the caller receives UNKNOWN, never a
speculative UNSAT. A zero-decision budget may still return
UNSAT if exact polynomial preprocessing succeeds (e.g.
E123 MOD4 obstruction).

## II. Explicit pinned witness self-reduction

The user-requested interface `RecoverWitnessFromSupport(A)`
implements the standard deterministic pinned self-reduction:

  1. Query support at no pins: if false, UNSAT.
  2. For j=0,...,n-1, query pinned support after
     tentatively setting x_j=0.
     If SAT, keep x_j=0; if UNSAT, set x_j=1.
  3. Verify the final Boolean x satisfies Ax=1.

This makes <=n+2 support calls, with O(n)-bit pins.
If a TRUE worst-case polynomial ExactSupport existed,
this protocol would immediately be a worst-case polynomial
sound+complete solver with a witness and hence P=NP
through E118's exact-class NP-hardness bridge.

Here the support implementation is exact but exponential,
so n+2 calls are not polynomial globally. A direct SAT
witness is already returned from the complete branch tree,
so self-reduction is primarily an independent semantic test.

## III. Distinguish proof / certificate / observation

PROVED for every input from code + mathematical argument:
    UNSAT filters are SOUND, a SAT witness is independently checked,
    exact clause branching is exhaustive, a resource guard
    returns UNKNOWN, and self-reduction is logically valid.
    Runtime without guard O(3^(n/3)*poly(n)).
    Each GF2 and quadratic-Gauss filter call is polynomial.

FINITE exact controls (not universal polynomial proof):
    E61 SAT12 and UNSAT12;
    SAT12 pinned splits and explicit witness self-reduction;
    contradictory pins -> UNSAT;
    zero-node guard -> UNKNOWN on still unresolved SAT12;
    E123 Tutte-12 UNSAT63 -> polynomial MOD4 certificate;
    E118 connected negative q90 -> root MOD4 does NOT solve it;
    E118 positive/negative q90 -> exact branch solver
        provides verified SAT/UNSAT on bounded finite fixtures
        if that CI check terminates within resource budget;
    - six independently generated frozen legal n12 SCL
      matrices; for each the complete fixed finite family
      of 495 four-column choices is enumerated as an
      independent oracle, and seven pinned variants
      are compared with ExactSupport (42 exact comparisons).
      This is finite testing, not a global complexity theorem.

COUNTEREXAMPLE/limitation:
    Prior E118 tests show all 270 first-check pins of
    an UNSAT90 survive quadratic-Gauss MOD4, so polynomial
    negative filtering alone is not complete.
    Prior toroidal legal SCL family gives primal
    treewidth Omega(sqrt(n)) and refutes polynomial
    dense min-plus table bounds.
    Hence arbitrary branching/width shortcuts are
    not allowed as the claimed final construction.

## IV. The ONE remaining mathematical gate

To meet the actual user demand, replace exponential
residual `visit(partial)` with a deterministic algorithm
or certified data structure of size n^C such that:

  - every input and arbitrary pi receives SAT+verifiable
    witness or a mathematically sound UNSAT verdict;
  - each update/query and complete evaluation costs
    n^C BIT operations for an input-independent C;
  - no exponential materialization of residual states,
    polynomial-space circuit with exponential evaluation,
    NP-hard oracle invocation, unproved compressed
    tensor contraction, or heuristic search hidden
    behind the ExactSupport name.

A purely syntactic API with an exact exponential backend
is an ENGINEERING CHECKPOINT, not progress on the global
polynomial-time theorem. The gate stays LOCKED.

## Scientific status

PINNED_EXACT_SUPPORT_API = IMPLEMENTED.
ALL_INPUT_PROOF_SOUNDNESS = PROVED.
ALL_INPUT_PROOF_COMPLETENESS_WITHOUT_GUARD = PROVED.
PINNED_GAUSS_NEGATIVE_CERTIFICATE = PROVED_POLYNOMIAL.
AFFINE_TOP_WEIGHT_UNION_CAPACITY_NEGATIVE_CERTIFICATE = PROVED_POLYNOMIAL.
RESOURCE_GUARD_UNKNOWN_SEMANTICS = PROVED.
PINNED_WITNESS_SELF_REDUCTION = PROVED_CONDITIONALLY_ON_SUPPORT.
COMPLETE_SUPPORT_WORST_CASE_BIT_RUNTIME = EXPONENTIAL_BOUND.
UNIVERSAL_POLYNOMIAL_EXACT_SUPPORT = OPEN.
UNIVERSAL_POLYNOMIAL_SolveLinearCubicXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
