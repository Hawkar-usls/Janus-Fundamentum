# R5 E9 — Fanout-3 Scope Correction and Pin-Activated XOR Interface

**Date:** 2026-09-23  
**Status:** exact JANUS-derived reduction + source-scope correction.  
**Scientific boundary:** D1=EMPTY; P_VS_NP=OPEN.

## 1. Scope correction: ordinary fanout-3 NAE decision is not the selector problem

Darmann–Döcker–Dorn prove that Positive Linear k-Disjoint NAE-3-SAT-Ek is in P for k=3 and NP-complete for each fixed k>=4.

For k=3 their proof invokes Filho's more general result that Positive NAE-r-SAT-Er is in P.

Filho's algorithm is an **unprecolored 2-colorability decision algorithm**:
a non-2-colorable instance contains a minimal non-2-colorable subhypergraph; edge-size/degree counting forces such an obstruction to be a square condenser; square condensers can be recognized in polynomial time.

This does not solve the JANUS escape-selector problem.

After the repair coordinate change z=y xor h, JANUS asks for a second coloring satisfying pins:

- protected a: z_a=y_a,
- pivot p: z_p=1-y_p.

That is a precoloring-extension / alternative-model question, not ordinary bicolorability.

Indeed, in the k=3 3-disjoint subclass Darmann–Döcker–Dorn explicitly note that whether NO-instances even exist is open, while their P statement still follows from Filho's general decision theorem.

Therefore:

UNPINNED FANOUT-3 IN P
!=
PINNED ESCAPE-SELECTOR FANOUT-3 IN P.

The previous plan to use fanout 3 as an automatic positive selector control is invalid.

## 2. One pin converts NAE3 to a singleton-exclusion binary relation

For Boolean x,y:

[
NAE(x,y,0)iff xlor y,
]

and

[
NAE(x,y,1)iff 
eg xlor
eg y.
]

Thus fixing one coordinate of a ternary NAE factor creates an ordinary binary clause forbidding exactly one assignment.

Call such a binary relation SE (singleton exclusion).

This is precisely the kind of 2-clause interaction that Darmann–Döcker–Dorn identify as lowering the unpinned degree-hardness threshold: Positive Linear NAE-(2,3)-SAT-E3 is NP-complete even with exactly one 2-clause per variable.

## 3. Exact pin-activated XOR gadget

Let x,y be external variables.

Introduce fresh internal variables a,b,c,d and two fresh precolored vertices

[
q_0=0,qquad q_1=1.
]

Add six positive 3-uniform NAE edges:

[
egin{aligned}
E_1&=NAE(x,a,b),\
E_2&=NAE(y,c,d),\
E_3&=NAE(a,c,q_0),\
E_4&=NAE(a,d,q_1),\
E_5&=NAE(b,c,q_1),\
E_6&=NAE(b,d,q_0).
end{aligned}
]

The four pinned internal edges become

[
(alor c)
land
(
eg alor
eg d)
land
(
eg blor
eg c)
land
(blor d).
]

### Lemma PIX-1

These four binary constraints have exactly two assignments:

[
(a,b,c,d)=(0,0,1,1)
]

and

[
(a,b,c,d)=(1,1,0,0).
]

### Proof

If a=0, then a∨c forces c=1; ¬b∨¬c forces b=0; b∨d forces d=1.

If a=1, then ¬a∨¬d forces d=0; b∨d forces b=1; ¬b∨¬c forces c=0.

Thus always

[
a=b,qquad c=d=
eg a.
]

∎

Now E1 becomes NAE(x,a,a), hence x=¬a.

E2 becomes NAE(y,¬a,¬a), hence y=a.

Therefore:

### Theorem PIX-2

With q0=0 and q1=1,

[
exists a,b,c,d; igwedge_{i=1}^6 E_i
iff
x
e y.
]

So six linear 3-uniform NAE factors plus two pins realize an exact NAE2/XOR interface.

## 4. Structural audit

Inside the gadget:

- deg(x)=deg(y)=1;
- deg(a)=deg(b)=deg(c)=deg(d)=3;
- deg(q0)=deg(q1)=2;
- every pair of distinct hyperedges intersects in at most one vertex.

Thus the gadget is linear and has maximum degree 3.

Fresh internals and fresh q0,q1 per replacement preserve linearity when inserted into a larger linear formula.

Most importantly, replacing one source NAE2(x,y) consumes exactly one occurrence of x and one occurrence of y, so it preserves the source variables' occurrence count.

## 5. Derived precoloring-extension hardness at max degree 3

Source theorem:
Darmann–Döcker–Dorn Theorem 4.3 gives NP-completeness of Positive Linear 3-Disjoint NAE-(2,3)-SAT-E3 even when every variable appears in exactly one 2-clause.

Replace every 2-clause NAE(x,y) by the PIX gadget above, with fresh q0,q1 precolored 0 and 1.

Then:

- every constraint is a positive NAE3 edge;
- the resulting hypergraph is 3-uniform and linear;
- every original variable still has degree exactly 3;
- every new uncolored internal variable has degree 3;
- every precolored q-vertex has degree 2;
- the precoloring extends iff the source mixed NAE-(2,3) instance is satisfiable.

Therefore:

### Corollary PIX-3

2-PRECOLORING EXTENSION is NP-complete on linear 3-uniform hypergraphs of maximum degree 3.

This is a derived reduction; no novelty claim is made absent a dedicated prior-art audit.

## 6. Stronger input promise: the unprecolored hypergraph is bicolorable

The hard source in Theorem 4.3 has exactly one 2-clause per variable.
After deleting that 2-clause layer, each original variable occurs in two remaining 3-clause layers.

The k=2 positive 3-disjoint NAE3 instance is always bicolorable.

Furthermore, if q0,q1 in PIX are left unpinned, direct exhaustive evaluation shows that the gadget projects to the universal relation on (x,y): every one of 00,01,10,11 has an extension.

Hence the transformed pure 3-uniform hypergraph without its precoloring is guaranteed bicolorable.

A coloring can be constructed using the already available polynomial fanout<=2 / General-Factor machinery on the source 3-clause layers and then extending each free-pin gadget locally.

Thus the hardness comes from the **extension/pin interface**, not from deciding whether the underlying hypergraph has any model.

## 7. Exact new structural motif

The six-edge gadget exposes the missing interaction:

[
	ext{PINNED TERNARY FACTORS}
	o
	ext{SE binary clauses}
	o
	ext{alternating SE cycle}
	o
	ext{parity / XOR interface}.
]

So the important transition is not simply fanout 3 -> 4.

Protected pins can activate a rigid binary parity channel while all repair-variable degrees stay at most 3.

This explains why the pure-fanout<=2 General-Factor island and ordinary fanout-3 bicolorability do not settle the JANUS selector problem.

## 8. Important ceiling: this is not yet single-pivot hardness

PIX-3 proves hardness for **arbitrary precoloring extension** with many precolored q-vertices.

The current monotone escape-selector gate is more specialized:

- one forced flipped pivot p;
- protected set A forced to remain at their values in a supplied model y.

We have not yet shown that the many hard pin requirements of PIX-3 can be activated from one pivot while preserving the linear 3-uniform maximum-degree-3 budget.

Therefore do NOT claim:

SINGLE-PIVOT ESCAPE SELECTOR AT FANOUT 3 = NP-HARD.

That remains open in the JANUS analysis.

## 9. New killer gate

### R5_E9_SINGLE_PIVOT_PIN_ACTIVATION_GATE_V1

Input target:
a linear 3-uniform repair instance with a supplied model y, protected set A, and one pivot p.

Question:

Can the pin-activated parity interface above be activated/distributed from the single condition

[
h_p=1,qquad h_A=0
]

using only polynomial-size linear 3-uniform max-degree-3 structure?

Two scientifically useful outcomes:

### PASS-GADGET

Construct such a one-pivot activation gadget.

Then the single-pivot selector problem already contains the hard mixed NAE-(2,3) interface at fanout 3.

The universal JANUS algorithm must solve this exact core.

### FAIL-THEOREM

Prove a structural invariant preventing one-pivot activation under the degree/linearity budget.

Then that invariant becomes a new contraction/repair law unavailable to arbitrary precoloring extension.

## 10. Updated frontier

DO NOT use as the primary contrast:

fanout 3 selector = P
vs
fanout 4 selector = hard.

Correct contrast:

UNPINNED fanout 3 bicolorability
=
P,

but

PIN-ACTIVATED binary/parity interfaces
already exist at max degree 3.

The next exact missing object is the gap between

MULTI-PIN ACTIVATION
and
SINGLE-PIVOT + PROTECTED-SET ACTIVATION.

D1 = EMPTY.
P_VS_NP = OPEN.
