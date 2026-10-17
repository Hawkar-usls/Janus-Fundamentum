# R5 E9 — Mandatory-Pivot Conditioning and Activated Pair-Glue Normal Form

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_NORMAL_FORM__SOURCE_BOUND_HARD_FIBER__NO_D1_PROMOTION

Parents:
- R5_E9_SINGLE_PIVOT_PIN_ACTIVATION_HARD_CORE_2026-09-23_v1.0
- R5_E9_PIVOT_ACTIVATED_INTERFACE_CONTRACTION_GATE_V1

Checker: experiments/r5_e9_pivot_activated_fiber_normal_form.py

## 1. Critical scope correction

The single-pivot selector problem does not ask whether the whole activation gadget has any model.
A supplied base model already proves that.

It asks for a model in the constrained fiber

h_p = 1,
h_A = 0.

Therefore the activation bit is not a free choice available to a quotient.
It is fixed by the query before the hard search begins.

Any sound collective contraction must preserve the p=1 fiber specifically.
Merging the easy p=0 and hard p=1 modes merely because the whole formula is satisfiable would destroy the target property.

## 2. Signal-tree contraction in repair coordinates

Every signal-tree wire is an exact NAE2 / disequality constraint in absolute coloring coordinates.

Let y be the supplied base coloring and h the repair mask, z=y XOR h.
Because both y and z satisfy the same wire disequality, for every wire edge uv:

y_u XOR y_v = 1
and
z_u XOR z_v = 1.

Subtracting over F2 gives

h_u = h_v.

The signal tree is connected to the pivot.
Hence under the mandatory condition h_p=1:

h_v=1

for every signal vertex v in that tree.

So every signal leaf flips from its base value r_i to 1-r_i deterministically.

The entire bounded-degree distributor is therefore polynomially contractible after pivot conditioning.

## 3. Compact gated PIX relation

For one activation interface let q0=r and q1=r XOR a, where a is the activation bit.
Project the PIX internals a,b,c,d.

Let

e(x,y) := 1 XOR x XOR y,

so e=1 exactly when x=y.

The projected relation is exactly:

G_r(a,x,y)
iff
a*e = 0
and
e*(x XOR r) = 0.

Equivalent mode description:

- a=0: allow x!=y and the single equal state x=y=r;
- a=1: require x!=y.

The checker exhaustively verifies this identity for both r values.

## 4. Mandatory activated fiber

The selector question fixes a=1.

Then the second factor becomes irrelevant because a*e=0 forces e=0.
Thus:

G_r(1,x,y)
iff
x XOR y = 1,

independent of r.

Therefore, after conditioning h_p=1 and contracting the signal distributor plus PIX internals, the whole target becomes:

B(X)
AND
AND_i NAE2(x_i,y_i),

where B=D2 union D3 is the easy pure-ternary fanout-2 base layer.

This is exactly the hard mixed source interface of Darmann-Doecker-Dorn Theorem 4.3.

## 5. Defect-syndrome normal form

Define one pair-defect bit per D1 pair:

e_i := 1 XOR x_i XOR y_i.

Then the activated target is:

B(X)
AND
E(X)=0,

where

E(X)=(e_1,...,e_m).

The known base model beta merely gives one known point E(beta) in the syndrome image.

The hard question is:

0 in E(Mod(B)) ?

Thus the shared-pivot problem is equivalently a zero-syndrome membership problem for the image of an easy fanout-2 model space under a fixed affine pair map.

## 6. Exact pair-glue contraction

In the activated fiber, every pair constraint is

y_i = 1 XOR x_i.

Substitute one representative variable t_i for each pair:

x_i=t_i,
y_i=1 XOR t_i.

This removes every D1 pair factor and one Boolean dimension per pair with trivial witness reconstruction.

For the NP-hard source family produced in the proof of DDD Theorem 4.3, this substitution reconstructs the signed degree-4 NAE-3SAT instance before the plus/minus variable split.

Each representative t_i inherits the two ternary occurrences of x_i and the two ternary occurrences of y_i, hence four ternary occurrences.

So:

PAIR INTERFACES = 0 after contraction,
but
EFFECTIVE VARIABLE FANOUT = 4.

The hardness has migrated from a binary glue layer into a higher-occurrence signed ternary core.

## 7. Consequence for the proposed collective-pivot quotient

The common pivot is a useful bounded-degree hardness distributor, but after the mandatory p=1 conditioning it is no longer the remaining degree of freedom.

A direct attempt to 'quotient the shared cause before activation' is unsound unless it preserves the p=1 fiber.

The obvious exact collective quotient already exists:

condition pivot
-> contract signal tree
-> project PIX internals
-> substitute pair disequalities.

It is polynomial and removes many auxiliary variables.

But its output is the known hard degree-4 NAE core.

Therefore this route is a representation contraction, not yet an algorithmic contraction.

## 8. Strong lesson for potentials

Counting only:
- number of activation interfaces;
- signal-tree size;
- auxiliary variables;
- or raw Boolean dimensions

is insufficient as a scientific progress measure.

All of these can decrease dramatically while the exact hard core is merely recomposed into degree-4 variables.

A future universal potential must charge both:

- explicit interface/glue complexity;
and
- complexity migrated into merged-variable incidence / residual interaction.

## 9. New active object

Freeze:

R5_E9_PAIR_DEFECT_SYNDROME_IMAGE_GATE_V1

Input:
- a fanout-2 ternary NAE base B with a polynomially supplied model beta;
- a partition of its variables into D1 pairs;
- affine defect map E_i=1 XOR x_i XOR y_i.

Question:

Can the zero-syndrome membership problem

0 in E(Mod(B))

be represented and solved by a polynomial witness-preserving quotient that is not merely the pair substitution back into the degree-4 hard core?

Equivalent graph form:

- B is an interval-General-Factor / {1,2}-degree problem on the dual cubic graph;
- each D1 pair couples two base edges and demands exactly one selected edge;
- the pair layer is the only obstruction absent from the easy base.

Candidate future currencies must act on this image/coupling collectively rather than on the already-contractible pivot distributor.

## 10. Ceiling

SINGLE-PIVOT HARDNESS REDUCTION = AUDITED
MANDATORY PIVOT CONDITIONING = EXACT
SIGNAL DISTRIBUTOR = POLY CONTRACTIBLE
PIX FAMILY = EXACT GATED NORMAL FORM
ACTIVATED FIBER = D2+D3 PLUS D1 DISEQUALITIES
DIRECT PAIR GLUE = EXACT BUT RECONSTRUCTS HARD DEGREE-4 CORE
PAIR-DEFECT SYNDROME IMAGE = ACTIVE FRONTIER
D1 = EMPTY
P_VS_NP = OPEN
