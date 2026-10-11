# PR515 — Exact Primitive Phase Elimination: Scalar-Closure Firewall and Projected-Walsh Construction

Date: 2026-10-11.
Repository: Hawkar-usls/Janus-Fundamentum.
Branch: research/parity-isolation-trade-checkpoint-20261009.
Parent: E61/E65 top-weight theorem, E118 NP-hardness bridge,
E123 negative, PR515 single-primitive-phase exact coefficient theorem.

**Verdict: a new exact constructive ONE-STEP formula and a
basis-independent finite no-go for SCALAR one-phase closure.
A worst-case all-input polynomial recursive evaluation theorem
has NOT been proved; universal SolveLinearCubicXSAT NOT CONSTRUCTED.
P_VS_NP OPEN.**

## I. Exact sum of ONE kernel direction

Let K=ker_F2(A) for a square+cubic+linear n x n
incidence matrix, n=3m, and Q the least power of 2 >2m.
Let zeta be primitive Q-th root. Every k in K has
even Hamming weight at most 2m.

Fix ANY nonzero v in K and choose ANY complement L such that
K=<v> direct_sum L. For each u in L,

    Delta_v(u) = (wt(u+v)-wt(u))/2
               = wt(v)/2 - wt(u AND v),

with XOR addition in F2 and ordinary intersection weight.

The sum of the two possible v-states is exactly

    F_v(u) = zeta^(wt(u)/2) * (1+zeta^Delta_v(u)).

For Boolean pins, first solve their affine F2 constraints,
obtaining k0+Kprime. The same formula applies with
u replaced by k0+u; Delta_v(u) remains the same weight
difference, which is integral because v has even weight.

The mathematical question is whether the eliminated factor can
be represented as a scalar constant times one new phase of
unit modulus:

    F_v(u) ?= C * zeta^P(u).

A NECESSARY condition is constant |1+zeta^Delta_v(u)|.

Since

    |1+zeta^a|^2 = 2+2cos(2*pi*a/Q),

the modulus equality for two INTEGER exponents a,b holds
if and only if a==+b or a==-b (mod Q).

At u=0 we have Delta_v(0)=wt(v)/2=:a.
Given any u in K not in {0,v}, we have

    Delta_v(u+v) = -Delta_v(u).

For ANY complementary subspace L, exactly one of u,u+v
belongs to L, and these two have the SAME modulus. Thus if

    wt(v)/2 - wt(u AND v) not congruent to +/-wt(v)/2 mod Q,

then NO choice of complement L allows single-phase scalar
closure when eliminating v.

## II. Strong finite theorem: ALL first directions obstructed

For each q63 and q90 fixture, freeze the canonical GF2 RREF
basis, then enumerate all nonzero directions v in the ENTIRE
kernel (not just basis directions). For each v test its at
most 18 canonical basis words u, excluding u=v, to find a
witness satisfying the inequality above. This finite exact
test is independent of the chosen elimination direction
or how that direction is extended to a basis.

Exact outputs:

    E123 UNSAT R63 (kernel dim14):
        16,383 / 16,383 directions obstructed;
        minimum violating basis witnesses per v = 13.

    E65 SAT R63^T (kernel dim14):
        16,383 / 16,383 directions obstructed;
        minimum violating basis witnesses per v = 13.

    E118 UNSAT90 (kernel dim18):
        262,143 / 262,143 directions obstructed;
        minimum violating basis witnesses per v = 2.

    E118 SAT90 (kernel dim18):
        262,143 / 262,143 directions obstructed;
        minimum violating basis witnesses per v = 2.

This disproves **SCALAR SINGLE-PHASE CLOSURE under ANY
first elimination basis** even on legal SAT instances.
The exhaustive finite check is used as a proof certificate;
it is not a universal algorithm and makes NO claim of
a general exponential lower bound on clever multi-phase
or circuit-based representations.

Runnable certificate:
    python experiments/r5_universal_primitive_phase_one_step_closure_firewall.py

## III. Constructive successor: exact projected-Walsh one-step elimination

Instead of demanding one phase, allow a finite sum of
Walsh-character-shifted phases. Fix a GF2 kernel basis
b_0,...,b_(d-1) and choose pivot v=b_p.
Let t in F2^(d-1) parameterize the remaining basis words:

    u(t)=XOR_{j!=p} t_j b_j.

Only coordinates in supp(v) matter to

    Delta_v(u(t)) = wt(v)/2
                     - sum_{i in supp(v)} (u(t))_i.

Each (u(t))_i is a binary LINEAR FORM in t. Collect these
forms as rows of a GF2 matrix T_v of dimensions
wt(v) x (d-1), and let

    r_v = rank_F2(T_v) <= min(wt(v), d-1).

Choose independent row forms h_1(t),...,h_(r_v)(t)
spanning all rows of T_v. Then there is a function

    g_v : F2^(r_v) -> Z[zeta]

such that

    1+zeta^Delta_v(u(t))
         = g_v(h_1(t),...,h_r(t)).

Its EXACT Walsh expansion is

    g_v(y) = 2^(-r_v) *
             sum_{s in F2^(r_v)}
                 (sum_{a in F2^(r_v)}
                    (-1)^(s dot a)g_v(a))*(-1)^(s dot y).

The Fourier/Walsh coefficients lie in Z[zeta].
For primitive Q=2^q, the integral basis
1,zeta,...,zeta^(Q/2-1) has O(n) coordinates, and each
coefficient is an exact integer sum of <=2^r terms;
there is NO floating-point error and each coordinate
has O(r+1) bits.

Each Walsh character of the remaining binary parameters
is itself a phase:

    (-1)^(s dot h(t)) = zeta^[(Q/2)*(s dot h(t))],

so every term in the expansion becomes an ordinary
cyclotomic phase with an added Boolean-linear exponent.
Thus the constructive formula is a valid, exact,
basis-preserving generalized phase elimination step.

One-step complexity:

    poly(n,Q) * (r_v+1) * 2^(r_v)

bit operations (for an explicit dense Walsh transform).
This is polynomial for that step if r_v=O(log n).
HOWEVER r_v can be linear in n, and recursively
eliminating ALL variables can multiply the number
of branches. No uniform worst-case polynomial bound
is presently proved. The fact that a short phase formula
can be written is not a computational shortcut.

## IV. Exact replay on both hard SAT/UNSAT pairs

Using the FIRST pivot of the canonical GF2 RREF basis
(expressed in the checker in this exact fixed order):

    E123 UNSAT R63       d=14, wt(v)=16, r_v=12:
        4096 nonzero Walsh characters out of 4096.

    E65 SAT R63^T        d=14, wt(v)=14, r_v=12:
        4096 nonzero Walsh characters out of 4096.

    E118 UNSAT90         d=18, wt(v)= 6, r_v= 2:
        4 nonzero Walsh characters out of 4.

    E118 SAT90           d=18, wt(v)= 6, r_v= 2:
        4 nonzero Walsh characters out of 4.

The exact routine derives independent coordinate forms
on supp(v) by F2 elimination, constructs the phase
factor as Q/2-coordinate INTEGER vectors, performs a
multidimensional Walsh transform, and checks the
inverse transform W(W(g))=2^r*g coefficient-by-coefficient.
No complex floating-point representation is involved.

Runnable certificate:
    python experiments/r5_universal_projected_walsh_phase_elimination_attack.py

Important distinction:

- The E118 first step has 4 branches, so ruling out one-phase
  closure does NOT rule out an efficient multiple-phase
  contraction. This is genuine compression of the single step.
- The E123 canonical first step already has 4096 branches
  with no cancellations. Choosing ANOTHER elimination
  direction/complement might be cheaper; we make no
  universal lower-bound claim from this chosen pivot.
- The q90 source E118 family is NP-hard as the source
  varies. Finding a universal schedule/representation
  where the exact total contraction stays polynomial
  would itself solve an NP-complete problem. Such a
  schedule theorem cannot be assumed from cheap first
  elimination on two fixed finite controls.

## IV-A. GENERAL E118 proof: the six-bit gadget flip ALWAYS has a 2-bit interface

This is a symbolic theorem for the WHOLE E118 occurrence-splitting
reduction family, not a statement inferred from the two q90 examples.

Let one E118 equality gadget have external ports x,y,z and
internal variables a,b,c,d,e,f,g. Over F2 its nine homogeneous
parity equations are equivalent to the exact parametrization

    x=y=p,       z=g=q,        f=t,
    a=c=p XOR q XOR t,
    b=e=p XOR t,
    d=q XOR t.

The checker tests this against **all** 2^10 Boolean local
assignments, with precisely 2^3=8 homogeneous solutions.

Changing t from 0 to 1 while holding p,q fixed flips exactly
the SIX internal coordinates a,b,c,d,e,f, and leaves
x,y,z,g unchanged. Consequently the vector

    v_g := e_a+e_b+e_c+e_d+e_e+e_f

is a weight-6 word in the GF2 kernel of every E118 target,
independently of the source formula. The local flip
is zero on all source-clause rows, so flips associated
with distinct variable gadgets are independent:
their supports are disjoint and all lie in the global kernel.

Gauge-fix the unique representative of each coset of these
flip directions by setting the local f coordinate t=0.
The other six coordinates are then

    (a,b,c,d,e,f) =
      (p XOR q, p, p XOR q, q, p, 0).

The intersection weight between the gauge representative and v_g is

    |u AND v_g| = 2*(p XOR q) + 2*p + q.

Thus the eliminated factor is EXACTLY the four-value table

    (p,q)=(0,0): 1+zeta^3;
    (p,q)=(1,0): 1+zeta^(-1);
    (p,q)=(0,1): 2;
    (p,q)=(1,1): 2.

This is a function of AT MOST TWO Boolean linear forms.
Hence the projected-Walsh elimination from Section III
has at most 2^2=FOUR terms for each E118 gadget, for
**every possible source formula and input size**. At
any primitive power-of-two root with Q>=16,
all four Walsh numerators are nonzero:

    W_00 = 6+zeta^3+zeta^(-1),
    W_10 = zeta^3-zeta^(-1),
    W_01 = zeta^3+zeta^(-1)-2,
    W_11 = zeta^3-zeta^(-1),

where Walsh indices are ordered as (p,q). The local
coefficients are computed in exact integral coordinates
with four one-line sums.

**Important limit:** after removing ALL source-variable
gadget flips, the remaining gauge-fixed parity system
still contains the source clauses and globally couples
the p,q port variables. E118 SAT equivalence and the
known extension factor 2^(2n_source/3) show that a
general sound/complete polynomial exact-contraction
algorithm for this remaining network would solve the
NP-complete source problem. The existence of a uniform
FOUR-term local rule does not imply such a global theorem.

Companion executable:
    python experiments/r5_universal_e118_gadget_local_four_phase_lemma.py

This result is new only as a **phase-elimination
interpretation of E118's already-proved equality gadget**.
It neither rediscovers the E118 reduction nor claims
a global solver. The value is an exact explanation
of why the q90 first step compresses to four terms,
and where the difficult interaction survives.

## V. The next precise universal obligation

A true universal recursive evaluator needs an EXPLICIT
representation and a provable all-input invariant bounding

    TOTAL BIT COST of all materialized phase branches,
    Walsh coefficients, cancellations, reductions, and
    final number of arithmetic operations by n^C

for an input-independent constant C. It must also compute
the coefficient of the primitive root at degree m and
support arbitrary partial Boolean pins without
exponential overhead.

An exact universally polynomial alternative could use
a compressed (factored or shared DAG/tensor) representation,
not an explicit flat sum of Walsh characters. In that case,
the proof must bound the DAG's contraction/evaluation cost,
not just its initial construction size.

The present attack establishes ONE sound exact elimination
rule and an exact finite obstruction to scalar closure.
It does NOT establish any universal poly bound; neither a
subclass result nor a finite instance is promoted to
a P=NP proof.

## Claim ledger

ONE_DIRECTION_EXACT_PHASE_ELIMINATION = PROVED.
SCALAR_SINGLE_PHASE_CLOSURE_ON_E118_E123 = REFUTED_FOR_EVERY_DIRECTION.
PROJECTED_WALSH_SPECTRAL_IDENTITY = PROVED.
PROJECTED_ONE_STEP_COMPLEXITY = O(2^r * poly(n)).
E118_ALL_SOURCE_LOCAL_GADGET_FLIP_WEIGHT_SIX = PROVED.
E118_ALL_SOURCE_LOCAL_PROJECTED_PHASE_RANK_LE_TWO = PROVED.
E118_LOCAL_GADGET_FOUR_WALSH_TERMS = PROVED.
E118_POST_GAUGE_GLOBAL_SOURCE_COUPLING = NP_HARD_PREDECESSOR.
E118_FIRST_PIVOT_EXACT_BRANCH_COUNT = 4.
E123_FIRST_PIVOT_EXACT_BRANCH_COUNT = 4096.
GLOBAL_RECURSIVE_POLYNOMIAL_BRANCH_BOUND = OPEN.
UNIVERSAL_POLY_PRIMITIVE_PHASE_EVALUATOR = NOT_CONSTRUCTED.
UNIVERSAL_POLY_SOLVELINEARCUBICXSAT = NOT_CONSTRUCTED.
P_VS_NP = OPEN.

External context (not proof of an SCL lower bound):
Greene (1976) binary linear-code weight enumerators and Tutte
polynomial, DOI 10.1002/sapm1976552119.
Classical simulation of degree-3 IQP circuits requires
handling high-order exponential sums; PRX Quantum 6, 010337
(2025), DOI 10.1103/PRXQuantum.6.010337.
The latter's general hardness results must not be imported
unconditionally to this special structured incidence family.
