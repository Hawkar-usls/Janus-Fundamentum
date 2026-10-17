# R5 E9 — Boolean Torsion Slice Two-State Threshold

Date: 2026-09-23

Authority: JANUS_DERIVED_EXACT_POSITIVE_ISLAND + SHARP THREE-STATE BARRIER__NO_D1_PROMOTION

Parent: R5_E9_BOOLEAN_SLICE_OF_TORSION_GATE_V1

Checker: experiments/r5_e9_boolean_slice_two_state_threshold.py

## 1. Problem

After Smith reduction, each interaction block contributes a Boolean side-code relation C_B on its row-side bits.

The previous Z3 theorem shows that generic composition of arbitrary such relations is already NP-complete.

We therefore ask for the strongest unconditional composition class visible directly from the cardinality/shape of the surviving Boolean slice.

## 2. Any relation with at most two tuples is bijunctive

Let R subseteq {0,1}^k with |R|<=2.

If |R|<=1 the claim is trivial.
Suppose R={u,v}.

Take any three tuples a,b,c in R.
At least two of them are equal.
The coordinatewise majority of a,b,c is exactly that repeated tuple.

Hence R is closed under majority.

Therefore every at-most-two-tuple Boolean relation is bijunctive.

This already places every fixed two-state side slice inside Schaefer's 2-SAT tractable class.

## 3. Direct compilation theorem

The result is stronger than a fixed-language observation because JANUS blocks may have different arities and different two-word relations.

For a block j with side relation

C_j={u^j,v^j},

introduce one local selector bit t_j:

t_j=0 selects u^j,
t_j=1 selects v^j.

For every coordinate i of the block, the global side bit s_i is then one of:

- constant 0;
- constant 1;
- t_j;
- not t_j.

Now consider a side coordinate shared by two blocks j,k.
Equality of their representations yields a Boolean constraint on (t_j,t_k).

Every Boolean binary relation can be written as 2-CNF by adding one 2-clause for each forbidden pair.

Coordinates occurring in only one block impose no coupling.
Unary restrictions become unit clauses.

Therefore the composition of an arbitrary family of explicitly represented <=2-state Boolean side slices reduces in polynomial time to 2-SAT.

Witness reconstruction is immediate from the selector assignment.

### Theorem BTS-1

Arbitrary composition of polynomially many Boolean side-code blocks, each having at most two surviving side words, is exactly polynomial-time solvable with polynomial witness reconstruction.

No common torsion modulus, common arity, or common pair of words is required.

## 4. Determinant-13 block as an instance

The frozen det-13 side slice is

{000010,111101}.

So it falls exactly into BTS-1.

Its tractability does not require treating Z13 specially.

The SNF stage compresses the block to two side states; after that the generic two-state compiler takes over.

## 5. Sharpness at three states

Three tuples already suffice to leave the universal two-state tractable island.

Consider

R_1/3={100,010,001}.

This is the Boolean slice of

s1+s2+s3 = 1 mod 3.

Repeated constraints of this relation are Positive 1-in-3-SAT, which is NP-complete.

R_1/3 also visibly fails majority closure:

maj(100,010,001)=000 notin R_1/3.

Thus there is a sharp cardinality threshold for unrestricted side-block composition:

<=2 states : always P;
3 states   : already enough for NP-complete composition.

## 6. Important correction: blockwise tractability is not enough

Even when every block relation individually belongs to some Schaefer tractable class, generic composition is only automatically safe when the active relation family shares a common tractable polymorphism/algorithmic class.

For example:

OR3 is dual-Horn;
NAND3 is Horn;

but allowing both on the same scope expresses NAE3:

OR3(x,y,z) AND NAND3(x,y,z)
iff
NAE3(x,y,z).

General positive NAE3 satisfiability is NP-complete.

So the authoritative side-code compiler must maintain a GLOBAL common-polymorphism ledger rather than assigning each block an unrelated local label.

## 7. Global ledger

For the active side-code family Gamma maintain the full six-way Schaefer ledger:

- 0-valid: every active relation contains the all-zero tuple;
- 1-valid: every active relation contains the all-one tuple;
- AND       -> Horn;
- OR        -> dual-Horn;
- majority  -> bijunctive / 2-SAT;
- ternary XOR/minority -> affine.

If the interface model does not freely add constants, a globally 0-valid language is solved by the all-zero assignment and a globally 1-valid language by the all-one assignment.

If constants 0 and 1 are explicitly admitted as free relations, use the corresponding constants-version of Schaefer's theorem; in that setting the two validity lanes are not independent generic escape hatches.

If at least one admissible global lane remains, use the corresponding polynomial engine.

If no common operation remains, Schaefer gives no generic polynomial composition theorem; the system must be contracted before unrestricted composition.

Two-state blocks automatically preserve majority, so a family consisting only of <=2-state blocks always stays in the bijunctive lane.

## 8. New active gate

Freeze:

R5_E9_THREE_STATE_BOOLEAN_SLICE_BREAKER_GATE_V1

Input:

a torsion side-code interaction after all <=2-state blocks have been compiled away and after maximal common-polymorphism composition.

Target:

find a polynomial witness-preserving contraction that eliminates, merges, or transforms every genuinely non-Schaefer >=3-state side interaction before it can compose as an NP-complete Boolean CSP.

Primary frozen hard atom:

R_1/3={100,010,001}.

Any proposed universal contraction must explain this exact three-state relation.

## 9. Ceiling

<=2 SIDE STATES = UNIVERSALLY POLY COMPOSABLE
DET13 BLOCK = INSIDE TWO-STATE ISLAND
3 SIDE STATES = SHARP ENOUGH FOR 1-IN-3 HARDNESS
BLOCKWISE SCHAEFER LABELS = INSUFFICIENT WITHOUT COMMON GLOBAL POLYMORPHISM
THREE-STATE / NON-SCHAEFER SLICE BREAKER = OPEN
D1 = EMPTY
P_VS_NP = OPEN
