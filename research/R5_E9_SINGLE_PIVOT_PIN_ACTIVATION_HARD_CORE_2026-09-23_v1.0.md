# R5 E9 — Single-Pivot Pin Activation and Escape-Selector Hard Core

**Date:** 2026-09-23  
**Status:** exact JANUS-derived reduction.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.  
**Complexity interpretation:** this identifies an NP-complete restricted subproblem inside the current selector gate; it is not a P≠NP claim.

## 1. Starting source problem

Use Darmann–Döcker–Dorn Theorem 4.3:

Positive Linear 3-Disjoint NAE-(2,3)-SAT-E3 is NP-complete even when every variable appears in exactly one 2-clause.

Write the source clause layers as:

- D1: a partition into NAE2 clauses;
- D2,D3: partitions into positive NAE3 clauses.

Every source variable therefore appears:

- once in D1;
- once in D2;
- once in D3.

## 2. The PIX gadget has three useful modes

Use the six-edge gadget from the previous artifact with external x,y, internal a,b,c,d and control vertices q0,q1.

Its projected relation on (x,y) is:

### Opposite controls

If q0 != q1:

[
R_{xy}={01,10},
]

i.e. exact NAE2 / XOR.

### Equal controls 00

If q0=q1=0:

[
R_{xy}={00,01,10},
]

i.e. the single forbidden pair is 11.

### Equal controls 11

If q0=q1=1:

[
R_{xy}={01,10,11},
]

i.e. the single forbidden pair is 00.

Thus changing one control from equality to inequality **activates** an exact XOR interface.

## 3. Construct an easy base assignment before activation

Delete D1 from the source formula.

The remaining D2 union D3 instance has pure ternary variable fanout two.

By the already established fanout<=2 / General-Factor polynomial island, construct a NAE model

[
eta
]

of D2 union D3.

For every source pair {x,y} in D1 choose one bit r_{xy}:

[
r_{xy}=
egin{cases}
1,&eta(x)=eta(y)=1,\
0,&	ext{otherwise}.
end{cases}
]

Then beta(x),beta(y) is accepted by the equal-control PIX relation with

[
q0=q1=r_{xy}.
]

Indeed:

- r=0 only forbids 11;
- r=1 only forbids 00.

So every hard D1 interface has a deliberately relaxed base mode compatible with beta.

## 4. Bounded-degree one-pivot signal distributor

Create one pivot p and set its value in the supplied base model to

[
p=0.
]

We need one dynamic leaf signal s_i for each source 2-clause i, with base value

[
s_i=r_i.
]

Build a rooted binary tree / caterpillar of signal variables with maximum abstract degree 3.

Replace every tree edge (u,v) by one PIX gadget in **wire mode**, using two fresh protected control vertices fixed to opposite values 0 and 1.

Therefore every tree edge enforces

[
u
e v.
]

If a leaf path initially has the wrong parity for desired r_i, subdivide its terminal tree edge once.

Hence we can realize every prescribed base leaf bit r_i while maintaining maximum signal-tree degree 3.

Because every tree edge is disequality, changing only the root value from 0 to 1 forces **every signal bit to complement**:

[
s_i(p=1)=1-r_i.
]

No search is involved.

## 5. Activate every hard source 2-clause from the single pivot

For source D1 clause NAE2(x_i,y_i):

- instantiate one activation PIX gadget with external x_i,y_i;
- its first control q0_i is protected at value r_i;
- its second control q1_i is the dynamic leaf signal s_i.

### Base state p=0

Then

[
q0_i=q1_i=r_i.
]

By construction beta(x_i),beta(y_i) is accepted by the relaxed equal-control PIX relation.

Thus the supplied base coloring extends through every activation gadget.

### Target state p=1

The signal tree forces

[
q1_i=1-r_i,
]

while protected q0_i remains r_i.

The controls are now opposite, so PIX enforces exactly

[
x_i
e y_i.
]

Therefore all source D1 clauses are activated simultaneously.

The original D2,D3 ternary clauses are present unchanged.

Hence a model with p=1 and all protected variables unchanged exists iff the original NP-hard mixed NAE-(2,3) instance is satisfiable.

## 6. Supplied base model is polynomially constructible

The reduction supplies a full known model y with p=0.

Construction:

1. solve D2 union D3 by the polynomial pure-fanout<=2 General-Factor algorithm to obtain beta;
2. choose r_i from beta as above;
3. assign every signal-tree vertex according to root p=0 and edge disequalities;
4. extend every wire PIX gadget by a constant-size lookup;
5. extend every relaxed activation PIX gadget by a constant-size lookup.

Thus the target instance includes the known model required by the JANUS repair formulation.

## 7. Degree audit

### Original source variables

Each source x appeared in exactly:
- one D1 clause;
- one D2 clause;
- one D3 clause.

The D1 occurrence is replaced by exactly one external occurrence in its activation PIX gadget.

Therefore source-variable degree remains exactly 3.

### Activation gadget

- internal a,b,c,d: degree 3;
- protected q0_i: degree 2;
- dynamic q1_i=s_i: degree 2 inside PIX plus one signal-tree wire = degree 3.

### Signal distributor

Every tree signal participates in at most three abstract tree edges.

Each abstract edge contributes one external occurrence in its PIX wire gadget.

Therefore internal signal degree <=3.

The pivot root has degree <=2.

Every private protected control inside a wire PIX has degree 2.

Thus the whole output has maximum vertex degree 3.

## 8. Linearity audit

Every PIX gadget is internally linear.

All internal/control vertices are fresh except designated external signal/source vertices.

Two gadgets sharing a signal intersect only in that signal.

An activation gadget intersects the original source ternary formula only in its single external source variable on each external edge.

The source formula is linear.

Therefore the entire constructed 3-uniform hypergraph remains linear.

## 9. Exact reduction theorem

### Theorem SPA-1

The following problem is NP-complete:

Input:
- a linear 3-uniform positive NAE hypergraph H of maximum degree 3;
- a supplied NAE coloring y of H;
- a protected set A;
- one pivot p not in A.

Question:
does there exist another NAE coloring z such that

[
z_a=y_aquadorall ain A
]

and

[
z_p
e y_p?
]

Membership in NP is immediate.

NP-hardness is the reduction above from DDD Theorem 4.3.

## 10. Consequence for the JANUS repair-mask problem

Put

[
h=yoplus z.
]

Then SPA-1 is exactly:

find a valid repair mask h such that

[
h_p=1,qquad h_A=0.
]

Therefore single-pivot protected repair existence is already NP-complete on:

- linear;
- 3-uniform;
- positive NAE;
- maximum degree 3;
- supplied known model.

This is precisely the structural domain of the current escape-selector work.

## 11. Consequence for monotone escape selectors

The previously proved selector completeness theorem gives:

[
exists	ext{ valid repair mask avoiding A}
iff
existssigma: Closure_sigma(p)cap A=emptyset.
]

A selector sigma is polynomial-size and its monotone closure is polynomially checkable.

Hence:

### Corollary SPA-2

ESCAPE-SELECTOR EXISTENCE is NP-complete already for linear 3-uniform maximum-degree-3 NAE repair instances with a supplied model, protected set, and one pivot.

This does NOT say no polynomial selector-synthesis algorithm exists.

Such an algorithm would be a polynomial algorithm for an NP-complete problem and therefore would directly imply P=NP.

That is exactly the global JANUS target, not a contradiction.

## 12. Strategic correction

The previous proposed comparison

fanout 3 selector = easy
vs
fanout 4 selector = hard

is false.

Correct picture:

UNPINNED NAE3 decision with max degree 3
=
P,

but

SINGLE-PIVOT PROTECTED ALTERNATIVE-MODEL / ESCAPE SELECTOR
with max degree 3
=
NP-COMPLETE.

The extra power comes from **pin-activated binary/parity interfaces**, not from a fourth incidence.

## 13. New exact hard motif

The reduction exposes a minimal hard architecture:

[
	ext{known easy base model}
]

[
+ 	ext{one pivot signal}
]

[
+ 	ext{bounded-degree XOR distribution tree}
]

[
+ 	ext{protected controls}
]

[
+ 	ext{PIX equal->opposite activation}
]

[
Longrightarrow
]

[
	ext{simultaneous activation of an NP-hard NAE2 interface layer}.
]

This is a much sharper target than generic high fanout.

## 14. New active gate

### R5_E9_PIVOT_ACTIVATED_INTERFACE_CONTRACTION_GATE_V1

The current missing mechanism is now:

> Given a WDR-normal instance whose single pivot activates many binary/parity interfaces through a bounded-degree repair network, find a polynomial witness-preserving quotient that contracts the **shared activation signal** without enumerating the exponentially many downstream model choices.

The next action should target the common pivot-controlled interface family as one grouped object.

Candidate angles:
- quotient all interfaces by the shared activation bit before they materialize;
- find a rank on activation-front propagation rather than individual assignments;
- derive a compact algebra for equal-control vs opposite-control PIX states;
- exploit the fact that every hard interface changes mode under the same one-bit global event.

D1 = EMPTY.
P_VS_NP = OPEN.
