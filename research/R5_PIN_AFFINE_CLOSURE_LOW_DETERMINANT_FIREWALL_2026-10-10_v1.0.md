# R5 — Pin/Propagate/Affine-Closure Quotient and Low-Determinant Firewall

Date: 2026-10-10

Status:
AFFINE_CLOSURE_STRENGTHENED
+ TU/BIMODULAR QUOTIENT SHORTCUT REFUTED
+ CONSTANT-FACTOR SHRINK THEOREM OPEN

P_VS_NP = OPEN.

## 1. Starting point

R5_ONE_CHECK_BOUNDARY_MATROID_PIN_XOR_FRONTIER proved that for 3|n,
pinning one of the three states at a check, followed by Exact-One unit
propagation, is a natural direct attempt to construct the hidden one-check
three-port support matroid.

A frozen SAT q=18 control showed raw unit propagation is incomplete but its
binary residual clauses x_u+x_v=1 collapse by XOR-component contraction.

This note strengthens that reduction to a fixed-point affine closure and tests
two proposed polynomial terminals on the resulting quotient.

## 2. Fixed-point affine closure

Repeat until stable:

1. Exact-One unit propagation.
2. Every residual clause with exactly two unknown variables becomes
       x_u xor x_v = 1.
3. Contract each consistent XOR component to one representative bit t_C;
   every original variable in the component is t_C xor p_v.
4. Substitute these affine literals into every residual ternary Exact-One
   clause.
5. If one ternary clause uses the same component more than once, simplify it
   exactly by its Boolean truth table.

The last step is essential.

For an Exact-One constraint on three affine literals, if at most two distinct
component bits occur, exhaustive evaluation over at most four assignments
either:
* gives contradiction; or
* forces at least one component bit.

Those forced values are propagated back to all original variables and the
closure repeats.

At a fixed point, every surviving ternary clause contains THREE DISTINCT XOR
component representatives.

## 3. Repair of a false TU obstruction

A q=21 planted SAT control initially produced a quotient matrix row with a
coefficient -2 and therefore a 1x1 determinant -2.

That was not a genuine obstruction. Its ternary clause used one XOR component
twice. Exact Boolean simplification forces quotient bits, and a second affine
closure round solves the entire branch:

    14 unknown original variables
      -> 2 XOR components
      -> repeated-component simplification
      -> 0 unknown variables.

Therefore determinant tests must be applied only AFTER fixed-point affine
closure.

## 4. Frozen proper q=30 SAT counterexample

The following 30x30 source is specified by column supports:

    (9,15,23)
    (1,2,22)
    (13,20,27)
    (4,24,25)
    (5,6,28)
    (0,7,19)
    (11,17,29)
    (14,21,26)
    (3,10,18)
    (8,12,16)
    (2,11,19)
    (9,14,19)
    (12,18,25)
    (4,15,22)
    (10,15,28)
    (1,17,24)
    (5,8,21)
    (1,16,29)
    (0,5,17)
    (4,8,20)
    (6,18,27)
    (3,20,26)
    (2,6,10)
    (23,25,26)
    (7,9,29)
    (14,22,28)
    (3,12,23)
    (7,11,13)
    (13,21,24)
    (0,16,27)

It is:
* square;
* row-degree 3 and column-degree 3;
* linear/C4-free;
* connected.

The planted Exact-One witness is

    {0,1,2,3,4,5,6,7,8,9}.

At check 26 the incident variables are

    {7,21,23},

and the planted state selects variable 7.

After pinning that state and running the COMPLETE affine closure above, the
branch remains nontrivial:

    original unknown variables = 23
    XOR quotient components    = 11
    proper ternary clauses      = 15
    repeated-component clauses  = 0.

Thus every surviving ternary clause genuinely uses three distinct quotient
bits.

## 5. Signed quotient matrix

Write every affine literal as

    t_C xor p.

For one proper ternary clause, ExactOne(l1,l2,l3)=1 becomes an integer equation

    sum_C a_C t_C = b,

where exactly three distinct columns are nonzero and each coefficient is +1 or
-1.

On the frozen q=30 quotient the resulting matrix contains the 2x2 minor

    [  1   1 ]
    [ -1   1 ]

with determinant 2.

Therefore the fixed-point quotient is NOT universally totally unimodular.

More strongly, it contains the 4x4 minor

    [ -1 -1  0  1 ]
    [  0 -1  0 -1 ]
    [ -1  1 -1  0 ]
    [  1  0 -1  0 ]

whose determinant is

    -5.

Hence the quotient is not universally bimodular and not in any
subdeterminant-<=2 shortcut class.

This is distinct from the E33 TU-kernel terminal: E33 remains valid whenever a
TU kernel certificate exists. The present result says the new affine quotient
does not automatically manufacture such a low-determinant representation.

## 6. Shrink observations, not theorem

Random planted square/cubic/linear controls were used only as stress tests.

After fixed-point affine closure, examples with increasing n can retain a
large quotient. In one tested n=180 carrier, even the best check under the
minimax score over its three pin branches retained a branch with 150 quotient
bits.

This is OBSERVATION only. It is not a constructed asymptotic counterfamily.

Therefore the proposed universal implication

    one check pin
      => constant-factor quotient shrink

is NOT PROVED and currently lacks supporting evidence.

No recurrence 3T(alpha n)+poly(n) may be claimed without a genuine uniform
alpha<1 theorem.

## 7. Surviving target

The correct reduced object after affine closure is a sparse signed
Exact-One quotient:

* Boolean component variables;
* each surviving constraint is Exact-One on three DISTINCT affine literals;
* each row has three +/-1 coefficients after moving constants to the RHS.

The next admissible algorithmic question is not TU.

It is whether the quotient has an additional GLOBAL invariant inherited from
the original square/cubic/linear carrier that permits:
* polynomial separator construction;
* bounded-state decomposition;
* determinant/Pfaffian cancellation unavailable to arbitrary signed
  1-in-3 systems; or
* a monotone potential proving polynomial total recursion.

## Claim boundary

FIXED_POINT_AFFINE_CLOSURE = PROVED CORRECT LOCAL REDUCTION.
PRE_CLOSURE_DET2_FIREWALL = INVALIDATED_BY_BOOLEAN_SIMPLIFICATION.
POST_CLOSURE_TU = REFUTED.
POST_CLOSURE_BIMODULAR = REFUTED.
CONSTANT_FACTOR_SHRINK = OPEN.
UNIVERSAL_POLYNOMIAL_EXACTONE_SOLVER = NOT_CONSTRUCTED.
P_VS_NP = OPEN.
