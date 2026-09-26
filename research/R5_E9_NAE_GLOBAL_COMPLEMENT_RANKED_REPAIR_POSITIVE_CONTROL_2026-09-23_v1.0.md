# R5 E9 — NAE Global-Complement Ranked Repair Positive Control

Date: 2026-09-23

Status: exact JANUS-derived positive control for ranked witness repair.

Scientific boundary: D1=EMPTY; P_VS_NP=OPEN.

## 1. Setting

Let F be a constant-free NAE-CNF: each constraint requires that its literal truth values are not all equal.
Literal polarities may be arbitrary.

For an assignment y, let bar(y) be the assignment obtained by complementing every variable.

Complementing every variable flips the truth value of every literal, regardless of literal polarity.
NAE is invariant under global truth-value complementation.

Therefore:

y models F  iff  bar(y) models F.

## 2. Ranked repair theorem

Choose any live variable x and canonical condition C_x := (x=0).

Define the structural transformer

mu(y) = bar(y).

Define rank

rho_x(y) = y_x in {0,1}.

If y models F and violates C_x, then y_x=1.
Global complementation gives mu(y) models F and mu(y)_x=0.
Hence

rho_x(mu(y)) = 0 < 1 = rho_x(y).

By the ranked-repair minimal-model argument:

SAT(F) iff SAT(F and not x).

No resolvent is generated.

## 3. Expansion-charge significance

For linear 4-regular positive NAE3, the exact normalized local charge is

chi_min(x)=4

for every variable initially.

Nevertheless the complement repair fixes one chosen variable exactly without materializing any of the Cartesian Davis-Putnam resolvents.

Therefore positive resolution-expansion charge is not itself a hardness invariant.
It is the price of explicit CNF projection when no stronger witness-repair theorem is used.

This is the first exact positive control for the active program:

DESTROY POSITIVE EXPANSION CHARGE WITHOUT PAYING THE RESOLVENT PRODUCT = PASS on constant-free NAE via global complement symmetry.

## 4. How much progress is guaranteed

If the NAE incidence structure has k variable-connected components, each component can be complemented independently.
Thus one pivot variable per component can be fixed canonically.

For a connected NAE survivor this guarantees only one Boolean-dimension reduction.
After fixing the pivot, the residual formula no longer has the unrestricted componentwise complement symmetry in general.

Hence this is a real contraction module, not a polynomial algorithm for the hard NAE family.

## 5. Algorithmic contract

Synthesis: choose the lexicographically first live variable in each NAE component.
Transformer: complement all variables in that component.
Rank: value of the chosen pivot variable.
Verification: syntactically verify every constraint is NAE and the chosen variables form complete connected components.
Construction/reconstruction/runtime: polynomial.

## 6. New lesson for WDR

The charge-repair gate should search for structural actions that act on entire witness space before Shannon distribution.

Natural candidate families now include:
- explicit involutive symmetries;
- tractable affine kernel actions;
- autarky-like component repairs;
- ranked substitutions that strictly decrease a canonical objective.

## 7. Ceiling

NAE GLOBAL-COMPLEMENT RANKED REPAIR = PASS
POSITIVE CHARGE CAN BE DESTROYED STRUCTURALLY = YES
REPEATED UNIVERSAL DIMENSION ELIMINATION = NOT PROVED
WDR EXPANSION-CHARGE REPAIR GATE = OPEN
D1 = EMPTY
P_VS_NP = OPEN
