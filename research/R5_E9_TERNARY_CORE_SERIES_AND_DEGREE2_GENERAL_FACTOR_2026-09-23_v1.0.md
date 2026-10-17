# R5 E9 — Series Contraction and Degree-2 Ternary Repair Core

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_CONTRACTION + SOURCE_BOUND_GENERAL_FACTOR_POLY_ISLAND__NO_D1_PROMOTION

Parent: R5_E9_TERNARY_REPAIR_CORE_ACTION_GATE_V1

Checker: experiments/r5_e9_ternary_core_series_and_degree2_checker.py

## 1. Compact complement-pair relation

For a bit-pattern t in F2^k define

CP_t := {0,1}^k \ {t, t XOR 1^k}.

Every model-relative NAE repair factor is of this form after ordering its coordinates:

Q_e = CP_t

for the appropriate local pattern t determined by the known model y.

Thus translated NAE is exactly a complement-pair exclusion relation.

## 2. Exact series-composition theorem

Let R=CP_t have scope {x} union A and S=CP_s have scope {x} union B, with A and B disjoint.

Write t=(t_x,t_A) and s=(s_x,s_B).

Define delta=t_x XOR s_x.

Define the boundary pattern

u := ( t_A , s_B XOR ((1 XOR delta) * 1_B) ).

Then:

exists x [ CP_t(x,A) AND CP_s(x,B) ]

is exactly

CP_u(A,B).

### Proof

For a fixed assignment a to A, CP_t forbids at most one value of x.
It forbids x=t_x when a=t_A, forbids x=1-t_x when a=not t_A, and forbids no x otherwise.

The same holds for CP_s.

The existential over x fails iff the two factors each forbid one value and these forbidden x-values are opposite.
There are exactly two such boundary assignments, and they are complements of one another.
The first is u as defined above and the second is u XOR 1.

Hence the projected relation excludes exactly one complementary pair.

QED.

## 3. Algorithmic consequence

A repair variable of factor-degree exactly two can be eliminated without enumerating the truth table of the enlarged factor, provided its two current compact factors intersect only in that variable.

The replacement factor is another CP relation represented by:

- its scope;
- one forbidden pattern u.

Representation size is linear in the resulting scope.

Reconstruction is polynomial: for a satisfying boundary assignment, test x=0 and x=1 against the two parent CP factors and choose the first valid value.

Thus this is an exact proof-carrying contraction with:

- one repair variable removed;
- one factor removed;
- no selector;
- no exponential table materialization.

## 4. Why series contraction is stronger than leaf projection

Leaf projection treats factor-degree <=1 variables.

Series contraction handles factor-degree 2 variables whenever the two incident compact factors have adhesion exactly one at the contracted variable.

Repeated application can collapse long chains of translated-NAE interaction into one higher-arity CP factor while retaining O(scope) representation.

The process stops only when:

- every remaining variable has factor-degree >=3, or
- a degree-2 variable joins two factors that already share additional live variables, creating a genuinely cyclic/parallel interface.

Thus raw arity growth is not itself an obstruction.

## 5. Pure degree-2 ternary core as General Factor

Now consider a pure ternary repair core in which:

- every live factor is an original translated NAE3 factor;
- every repair variable occurs in exactly two ternary factors;
- only unary pivot/protected constraints are added.

Construct the dual graph G:

- one graph vertex for each ternary factor;
- one graph edge e_v for each repair variable v, joining its two incident factors.

Because every ternary factor has arity three, G is subcubic; if every variable has degree exactly two and every factor remains ternary, each factor vertex has degree three before forced-edge deletion.

Change coordinates from repair bits h to repaired model bits

z_v = y_v XOR h_v.

At one factor f, the NAE condition says its three incident z-edges are not all equal.

Let S be the subset of dual edges with z_v=1.

Then exactly:

1 <= deg_S(f) <= 2.

Pivot/protected constraints on h become forced included/excluded dual edges according to their y-values.

After accounting for forced edges, every factor vertex has an interval of feasible remaining degrees.

Therefore repair-mask existence is an instance of General Factor with interval degree sets.

## 6. Polynomial solvability

Cornuejols' General Factor theorem gives polynomial-time solvability whenever every degree set has max-gap at most one; interval degree sets are a standard special case.

Modern summaries state the same boundary explicitly and also connect symmetric Boolean edge-CSPs with graph-factor problems.

References:

- Cornuejols, General factors of graphs, J. Combin. Theory B 45 (1988).
- Marx, Sankar, Schepper, Degrees and Gaps: Tight Complexity Results of General Factor Problems Parameterized by Treewidth and Cutwidth, 2021.
- Shao, Zivny, A Strongly Polynomial-Time Algorithm for Weighted General Factors with Three Feasible Degrees, 2023/2024.

Hence:

PURE TERNARY REPAIR CORE
+ every repair variable factor-degree <=2
= POLYNOMIAL EXACT SELECTOR SYNTHESIS.

Given the selected dual-edge set S, recover z, then h=z XOR y, then synthesize the escape selector using the already proved mask-to-selector theorem.

## 7. Exact positive island

### Theorem D2RC-1

For a repair instance whose genuine ternary core has no binary coupling factors and in which every repair variable occurs in at most two ternary factors, protected-set-avoiding repair-mask existence and construction are polynomial.

Degree <=1 variables are handled by exact leaf projection.
After that, the degree-2 pure core reduces to interval General Factor as above.

This theorem permits arbitrary cycles in the dual graph.

Therefore:

CYCLE != HARDNESS

and more strongly:

PURE TERNARY FANOUT <=2 != HARDNESS.

## 8. Mixed-core kernelization

Before invoking a new ternary-core action, apply:

1. translation quotient;
2. leaf projection;
3. compact CP series contractions on degree-2 adhesion-one interfaces;
4. solve any separated pure degree-2 ternary components by General Factor;
5. binary-core / 2-SAT extraction where available.

Only the remaining fanout/parallel-interface core is passed to the new action layer.

## 9. Hard benchmark

Connected DDD linear 4-regular NAE3 remains unaffected:

- every variable occurs in four ternary factors;
- no leaf variable exists;
- no degree-2 series variable exists;
- the global complement translation has already been quotiented;
- chi_min(x)=+4 initially.

So DDD4 remains a clean hard-control core.

## 10. Sharpened frontier

The missing motif is not ternary arity alone and not cyclicity alone.

After all current polynomial contractions, the next genuinely new obstruction must involve at least one of:

- repair-variable fanout >=3;
- multi-variable / parallel interfaces between compact factors;
- protected-set interaction that survives the degree-2 General-Factor island.

Freeze:

R5_E9_HIGH_FANOUT_TERNARY_CORE_BREAKER_GATE_V1

Target:

on the reduced ternary repair core, synthesize a polynomial exact action that removes/fixes at least one Boolean dimension or lowers ternary fanout so that leaf/series/General-Factor/2-SAT cascades resume.

## 11. Ceiling

LEAF PROJECTION = PASS
CP SERIES CONTRACTION = PASS
PURE TERNARY FANOUT <=2 = P VIA GENERAL FACTOR
DDD4 = SURVIVES
HIGH-FANOUT TERNARY CORE BREAKER = OPEN
D1 = EMPTY
P_VS_NP = OPEN
