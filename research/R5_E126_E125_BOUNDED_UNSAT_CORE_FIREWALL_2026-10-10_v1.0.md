# R5 E126 — E125 Bounded-UNSAT-Core Firewall

Date: 2026-10-10

Status:
E125_SCALABLE_HIGH_WIDTH_FAMILY_ROUTED_BY_CONSTANT_UNSAT_CORE

P_VS_NP = OPEN.

## 1. Purpose

E125 constructs an explicit connected square+cubic+linear family M_t with

    n = 63 t^2,
    nullity_Q(M_t) >= 13 t^2 = Omega(n),
    raw Levi treewidth >= t = Omega(sqrt(n)),
    Exact-One UNSAT.

Those properties are correct.

However the E125 UNSAT proof itself exposes a stronger polynomial terminal that
must be applied before any late E18/KLOC/normal-span/branchwidth audit.

Every left block retains the same 62 checks of the frozen E64 q=63 UNSAT
carrier, deleting only one check c0.

Those 62 checks are already UNSAT by themselves.

Therefore every E125 member contains t^2 constant-size UNSAT subinstances.

E125 is consequently not a scalable post-router hard family.

## 2. The 62-check core is UNSAT

Let R be the E64 q=63 carrier and delete one check c0.

Suppose a Boolean assignment x to the 63 base variables satisfied all other
62 Exact-One checks.

Let s be the selected-variable count on c0. Since every variable occurs in
exactly three base checks,

    62 = 3|x| - s.

Hence

    s = 3|x| - 62
      == 1 (mod 3).

Because c0 has three variables,

    s in {0,1,2,3}.

Therefore

    s=1.

So x also satisfies c0.

But E64 exactly certifies that the full q=63 carrier has no Exact-One
assignment.

Contradiction.

Thus the 62 retained checks alone form an UNSAT core on 63 variables.

## 3. E125 contains the core verbatim

In E125, for every toroidal left block h:

* all 63 original variables of that block remain;
* exactly the original check c0 is removed;
* all other 62 E64 checks are retained without modification;
* the new cross-checks only add constraints involving the three freed c0 ports.

Therefore restricting M_t to those 63 variables and the 62 retained local
checks yields exactly the fixed UNSAT core above.

Adding cross-checks cannot restore satisfiability to an already UNSAT
subformula.

Hence E125 UNSAT is witnessed locally inside every block.

## 4. Polynomial bounded-core terminal

For any fixed constant B, the following is polynomial-time:

    search all variable/check subsets of size <= B
    and test whether the induced/restricted subformula is one of a fixed
    finite library of certified UNSAT cores.

For the E125 construction one may take B=63 and the frozen E64-one-check core.

Even a naive O(n^63) recognizer is polynomial in the complexity-theoretic
sense. More practically, E125 exposes its block partition explicitly, making
recognition linear in the constructed family representation.

Therefore growing raw treewidth and linear nullity do not make E125 a hard
benchmark: a constant UNSAT witness is present independently of global width.

## 5. Consequence for benchmark design

A genuine SCALABLE_POST_ROUTER_UNSAT family must now satisfy an additional
anti-loop requirement:

    NO_BOUNDED_UNSAT_CORE.

More strongly, the minimum UNSAT-core size should grow with n, or at least no
fixed finite core family should certify every member.

This requirement is independent of:

* rational nullity;
* raw Levi treewidth;
* E18/KLOC cleanliness;
* branchwidth of a chosen algebraic representation.

Without it, one can manufacture arbitrarily wide connected UNSAT instances by
wiring together constant hard blocks while retaining a local contradiction.

## 6. Updated scalable benchmark target

The admissible target is now:

    SCALABLE_POST_ROUTER_UNSAT

with all of:

    connected square+cubic+linear,
    3|n,
    effective nullity beyond O(log n),
    E18 projective-clean,
    KLOC3-clean,
    no cube-root/rainbow-Z3 SAT certificate,
    outside admitted normal-span/component/branchwidth terminals,
    NO bounded-size UNSAT core,
    exact UNSAT.

E125 fails the bounded-core gate before the later filters need to be tested.

## Claim boundary

E125_SQUARE_CUBIC_LINEAR_CONNECTED = PRESERVED.
E125_NULLITY_OMEGA_N = PRESERVED.
E125_RAW_TREEWIDTH_OMEGA_SQRT_N = PRESERVED.
E125_HAS_62_CHECK_UNSAT_CORE_PER_BLOCK = PROVED.
E125_SCALABLE_POST_ROUTER_HARD = REFUTED.
NO_BOUNDED_UNSAT_CORE = NEW_REQUIRED_BENCHMARK_GATE.
SCALABLE_POST_ROUTER_UNSAT = OPEN.
GLOBAL_SYMBOLIC_SUPPORT_CONSTRUCTION = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
